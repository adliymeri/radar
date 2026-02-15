from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.chatapp.handlers.buyer.buyer_error_handler import error_exit
from src.chatapp.handlers.buyer.buyer_cancel_handler import cancel_handler
from src.domain.enums.car_enums import (
    CarBrand, CAR_MODELS, Color, Transmission,
    FuelType, Drivetrain, get_years
)
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.domain.models.buyer_request import BuyerRequest


(
    SELECT_MAKE,
    SELECT_MODEL,
    SELECT_YEAR,
    SELECT_PRICE_MIN,
    SELECT_PRICE_MAX,
    SELECT_MILEAGE,
    SELECT_COLOR,
    SELECT_TRANSMISSION,
    SELECT_FUEL,
    SELECT_DRIVETRAIN,
    CONFIRM,
) = range(11)


CANCEL_ROW = ["❌ Cancel"]


def with_cancel(keyboard: list) -> list:
    return keyboard + [CANCEL_ROW]


# ================= START =================

async def start_car_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    return SELECT_YEAR


# ================= YEAR =================

async def handle_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["request"]["year"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please select a valid year from the list.")
        return SELECT_YEAR

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
    await update.message.reply_text(
        "Maximum mileage (km):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True),
    )
    return SELECT_MILEAGE


# ================= MILEAGE =================

async def handle_mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number (e.g. 100000):")
        return SELECT_MILEAGE

    context.user_data["request"]["mileage"] = value
    context.user_data["selected_colors"] = []
    keyboard = build_color_keyboard([])
    await update.message.reply_text(
        "Choose colors (select all that apply, then press Done):",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return SELECT_COLOR


# ================= COLOR (multi-select) =================

def build_color_keyboard(selected: list) -> list:
    keyboard = []
    colors = [c.value for c in Color]
    for i in range(0, len(colors), 2):
        row = []
        for color in colors[i:i+2]:
            label = f"✅ {color}" if color in selected else color
            row.append(label)
        keyboard.append(row)
    keyboard.append(["✔️ Done", "❌ Cancel"])
    return keyboard


async def handle_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✔️ Done":
        selected = context.user_data.get("selected_colors", [])
        if not selected:
            await update.message.reply_text("Please select at least one color:")
            return SELECT_COLOR

        context.user_data["request"]["color"] = selected
        context.user_data.pop("selected_colors", None)

        keyboard = with_cancel([[t.value] for t in Transmission])
        await update.message.reply_text(
            "Transmission:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
        )
        return SELECT_TRANSMISSION

    clean = text.replace("✅ ", "")
    selected = context.user_data.setdefault("selected_colors", [])

    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_color_keyboard(selected)
    await update.message.reply_text(
        f"Selected: {', '.join(selected) if selected else 'none'}\nSelect more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),  # fixed
    )
    return SELECT_COLOR


# ================= TRANSMISSION =================

async def handle_transmission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["request"]["transmission"] = update.message.text

    keyboard = with_cancel([[f.value] for f in FuelType])
    await update.message.reply_text(
        "Fuel type:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_FUEL


# ================= FUEL =================

async def handle_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["request"]["fuel"] = update.message.text

    keyboard = with_cancel([[d.value] for d in Drivetrain])
    await update.message.reply_text(
        "Drivetrain:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_DRIVETRAIN


# ================= DRIVETRAIN =================

async def handle_drivetrain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["request"]["drivetrain"] = update.message.text

    data = context.user_data["request"]

    summary = (
        f"🚗 {data['make']} {data['model']} ({data['year']})\n"
        f"💶 €{data['price_min']:,.0f} — €{data['price_max']:,.0f}\n"
        f"🛣 Max {data['mileage']:,} km\n"
        f"🎨 {', '.join(data['color'])}\n"
        f"⚙️ {data['transmission']} | {data['fuel']} | {data['drivetrain']}"
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
            SELECT_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_year)],
            SELECT_PRICE_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_price_min)],
            SELECT_PRICE_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_price_max)],
            SELECT_MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_mileage)],
            SELECT_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_color)],
            SELECT_TRANSMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_transmission)],
            SELECT_FUEL: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_fuel)],
            SELECT_DRIVETRAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_drivetrain)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            MessageHandler(cancel_filter, cancel_handler),
        ],
    )