from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.domain.config.limits import get_max_requests_for_buyer
from src.chatapp.handlers.buyer.buyer_error_handler import error_exit
from src.chatapp.handlers.buyer.buyer_cancel_handler import cancel_handler
from src.domain.enums.car_enums import (
    CarBrand, CAR_MODELS, Transmission,
    FuelType, Drivetrain, get_years
)
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.domain.models.buyer_request import BuyerRequest


(
    SELECT_MAKE,
    SELECT_MODEL,
    SELECT_YEAR_MIN,
    SELECT_YEAR_MAX,
    SELECT_PRICE_MIN,
    SELECT_PRICE_MAX,
    SELECT_MILEAGE,
    SELECT_TRANSMISSION,
    SELECT_FUEL,
    SELECT_DRIVETRAIN,
    CONFIRM,
) = range(11)


CANCEL_ROW = ["❌ Cancel"]
DONE_ROW = ["✔️ Done", "❌ Cancel"]


def with_cancel(keyboard: list) -> list:
    return keyboard + [CANCEL_ROW]


def build_multi_select_keyboard(enum_class, selected: list, label: str = "") -> list:
    """Generic multi-select keyboard builder"""
    keyboard = []
    items = [item.value for item in enum_class]
    for i in range(0, len(items), 2):
        row = []
        for item in items[i:i+2]:
            prefix = "✅ " if item in selected else ""
            row.append(f"{prefix}{item}")
        keyboard.append(row)
    keyboard.append(DONE_ROW)
    return keyboard


# ================= START =================

async def start_car_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)
    
    # NEW: Check request limit before starting
    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        if not buyer:
            await update.message.reply_text("⚠️ You need to register first. Use /start.")
            return ConversationHandler.END

        # Get max requests based on buyer's payment plan
        max_requests = get_max_requests_for_buyer(buyer.payment)
        existing_requests = await request_service.get_requests_by_buyer(buyer.id)
        
        if len(existing_requests) >= max_requests:
            # Get plan name for message
            plan = buyer.payment.get("plan", "free") if buyer.payment else "free"
            
            await update.message.reply_text(
                f"⚠️ You've reached the maximum of {max_requests} active requests for your {plan} plan.\n\n"
                f"Delete an existing request from 📄 My Requests to add a new one, "
                f"or upgrade your plan for more requests.",
                reply_markup=get_buyer_menu_keyboard()
            )
            return ConversationHandler.END
    
    # Continue with existing flow
    context.user_data["request"] = {}
    keyboard = with_cancel([[b.value] for b in CarBrand])
    await update.message.reply_text(
        "🚗 Choose car brand:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MAKE



# ================= MAKE =================

async def handle_make(update: Update, context: ContextTypes.DEFAULT_TYPE):
    brand = update.message.text
    try:
        models = CAR_MODELS[CarBrand(brand)]
    except (ValueError, KeyError):
        await update.message.reply_text("Please select a valid brand from the list.")
        return SELECT_MAKE

    context.user_data["request"]["make"] = brand
    keyboard = with_cancel([[m] for m in models])
    await update.message.reply_text(
        "Select model:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MODEL


# ================= MODEL =================

async def handle_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["request"]["model"] = update.message.text

    years = get_years()
    keyboard = with_cancel([list(map(str, years[i:i+4])) for i in range(0, len(years), 4)])
    await update.message.reply_text(
        "Select minimum year:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_YEAR_MIN


# ================= YEAR MIN =================

async def handle_year_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        year_min = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please select a valid year from the list.")
        return SELECT_YEAR_MIN

    context.user_data["request"]["year_min"] = year_min

    # Generate years from year_min to current year
    all_years = get_years()
    filtered_years = [y for y in all_years if y >= year_min]
    keyboard = with_cancel([list(map(str, filtered_years[i:i+4])) for i in range(0, len(filtered_years), 4)])
    
    await update.message.reply_text(
        "Select maximum year:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_YEAR_MAX


# ================= YEAR MAX =================

async def handle_year_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        year_max = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please select a valid year from the list.")
        return SELECT_YEAR_MAX

    year_min = context.user_data["request"]["year_min"]
    if year_max < year_min:
        await update.message.reply_text(f"Max year must be >= min year ({year_min}). Try again:")
        return SELECT_YEAR_MAX

    context.user_data["request"]["year_max"] = year_max

    await update.message.reply_text(
        "Enter MIN price (€):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_PRICE_MIN


# ================= PRICE =================

async def handle_price_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number (e.g. 5000):")
        return SELECT_PRICE_MIN

    context.user_data["request"]["price_min"] = value
    await update.message.reply_text(
        "Enter MAX price (€):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True),
    )
    return SELECT_PRICE_MAX


async def handle_price_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number (e.g. 20000):")
        return SELECT_PRICE_MAX

    price_min = context.user_data["request"].get("price_min", 0)
    if value < price_min:
        await update.message.reply_text(
            f"Max price must be greater than min price (€{price_min:.0f}). Try again:"
        )
        return SELECT_PRICE_MAX

    context.user_data["request"]["price_max"] = value

    keyboard = [
        ["< 50,000 km", "< 100,000 km"],
        ["< 150,000 km", "< 200,000 km"],
        ["< 250,000 km", "250,000+ km"],
        ["✍️ Enter Custom Mileage"],
        CANCEL_ROW
    ]
    await update.message.reply_text(
        "Select maximum mileage:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MILEAGE


# ================= MILEAGE =================

async def handle_mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "✍️ Enter Custom Mileage":
        await update.message.reply_text(
            "Enter maximum mileage in km (whole numbers only, e.g. 153000):",
            reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True),
        )
        return SELECT_MILEAGE

    # Handle preset options
    mileage_map = {
        "< 50,000 km": 50000,
        "< 100,000 km": 100000,
        "< 150,000 km": 150000,
        "< 200,000 km": 200000,
        "< 250,000 km": 250000,
        "250,000+ km": 999999,  # effectively unlimited
    }

    if text in mileage_map:
        context.user_data["request"]["mileage"] = mileage_map[text]
    else:
        # Custom input validation
        # Remove common separators and validate
        cleaned = text.replace(",", "").replace(".", "").replace(" ", "").replace("k", "").replace("K", "")
        
        if not cleaned.isdigit():
            await update.message.reply_text(
                "❌ Invalid format. Enter whole numbers only (e.g. 153000):"
            )
            return SELECT_MILEAGE
        
        value = int(cleaned)
        if value <= 0:
            await update.message.reply_text("❌ Mileage must be greater than 0. Try again:")
            return SELECT_MILEAGE

        context.user_data["request"]["mileage"] = value

    # Start transmission multi-select
    context.user_data["selected_transmission"] = []
    keyboard = build_multi_select_keyboard(Transmission, [])
    await update.message.reply_text(
        "Select transmission type(s) (tap to toggle, then press Done):",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_TRANSMISSION


# ================= TRANSMISSION (multi-select) =================

async def handle_transmission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✔️ Done":
        selected = context.user_data.get("selected_transmission", [])
        if not selected:
            await update.message.reply_text("Please select at least one transmission type:")
            return SELECT_TRANSMISSION

        context.user_data["request"]["transmission"] = selected
        context.user_data.pop("selected_transmission", None)

        # Start fuel type multi-select
        context.user_data["selected_fuel"] = []
        keyboard = build_multi_select_keyboard(FuelType, [])
        await update.message.reply_text(
            "Select fuel type(s) (tap to toggle, then press Done):",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
        )
        return SELECT_FUEL

    clean = text.replace("✅ ", "")
    selected = context.user_data.setdefault("selected_transmission", [])

    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_multi_select_keyboard(Transmission, selected)
    selected_display = ", ".join(selected) if selected else "none"
    await update.message.reply_text(
        f"Selected: {selected_display}\nTap more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_TRANSMISSION


# ================= FUEL (multi-select) =================

async def handle_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✔️ Done":
        selected = context.user_data.get("selected_fuel", [])
        if not selected:
            await update.message.reply_text("Please select at least one fuel type:")
            return SELECT_FUEL

        context.user_data["request"]["fuel"] = selected
        context.user_data.pop("selected_fuel", None)

        # Start drivetrain multi-select
        context.user_data["selected_drivetrain"] = []
        keyboard = build_multi_select_keyboard(Drivetrain, [])
        await update.message.reply_text(
            "Select drivetrain(s) (tap to toggle, then press Done):",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
        )
        return SELECT_DRIVETRAIN

    clean = text.replace("✅ ", "")
    selected = context.user_data.setdefault("selected_fuel", [])

    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_multi_select_keyboard(FuelType, selected)
    selected_display = ", ".join(selected) if selected else "none"
    await update.message.reply_text(
        f"Selected: {selected_display}\nTap more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_FUEL


# ================= DRIVETRAIN (multi-select) =================

async def handle_drivetrain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✔️ Done":
        selected = context.user_data.get("selected_drivetrain", [])
        if not selected:
            await update.message.reply_text("Please select at least one drivetrain:")
            return SELECT_DRIVETRAIN

        context.user_data["request"]["drivetrain"] = selected
        context.user_data.pop("selected_drivetrain", None)

        # Build summary
        data = context.user_data["request"]
        summary = (
            f"🚗 {data['make']} {data['model']}\n"
            f"📅 {data['year_min']} — {data['year_max']}\n"
            f"💶 €{data['price_min']:,.0f} — €{data['price_max']:,.0f}\n"
            f"🛣 Max {data['mileage']:,} km\n"
            f"⚙️ Transmission: {', '.join(data['transmission'])}\n"
            f"⛽ Fuel: {', '.join(data['fuel'])}\n"
            f"🔧 Drivetrain: {', '.join(data['drivetrain'])}"
        )

        await update.message.reply_text(
            f"Confirm your request:\n\n{summary}",
            reply_markup=ReplyKeyboardMarkup(
                [["✅ Confirm", "❌ Cancel"]],
                resize_keyboard=True,
                is_persistent=True
            ),
        )
        return CONFIRM

    clean = text.replace("✅ ", "")
    selected = context.user_data.setdefault("selected_drivetrain", [])

    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_multi_select_keyboard(Drivetrain, selected)
    selected_display = ", ".join(selected) if selected else "none"
    await update.message.reply_text(
        f"Selected: {selected_display}\nTap more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_DRIVETRAIN


# ================= CONFIRM =================

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "Cancel" in update.message.text:
        return await cancel_handler(update, context)

    try:
        details = context.user_data["request"]
        chat_id = str(update.effective_user.id)

        async with get_bot_deps() as deps:
            buyer_service = deps["buyer_service"]
            request_service = deps["buyer_request_service"]

            buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
            if not buyer:
                await update.message.reply_text(
                    "⚠️ You need to register first. Use /start.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                return ConversationHandler.END

            request = BuyerRequest(
                buyer_id=buyer.id,
                type="car",
                details=details,
            )
            await request_service.create_request(request)

        context.user_data.clear()
        await update.message.reply_text(
            "✅ Request saved successfully!",
            reply_markup=get_buyer_menu_keyboard(),
        )
        return ConversationHandler.END

    except Exception as e:
        return await error_exit(update, context)


# ================= CONVERSATION =================

def get_car_request_conv():
    cancel_filter = filters.Regex("^❌ Cancel$")

    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🚗 Request a Car$"), start_car_request)],
        states={
            SELECT_MAKE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_make)],
            SELECT_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_model)],
            SELECT_YEAR_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_year_min)],
            SELECT_YEAR_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_year_max)],
            SELECT_PRICE_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_price_min)],
            SELECT_PRICE_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_price_max)],
            SELECT_MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_mileage)],
            SELECT_TRANSMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_transmission)],
            SELECT_FUEL: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_fuel)],
            SELECT_DRIVETRAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_drivetrain)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            MessageHandler(cancel_filter, cancel_handler),
        ],
        persistent=True,
        name="car_request",
    )