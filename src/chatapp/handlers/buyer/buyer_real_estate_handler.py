from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.domain.config.limits import get_max_requests_for_buyer
from src.chatapp.handlers.buyer.buyer_error_handler import error_exit
from src.chatapp.handlers.buyer.buyer_cancel_handler import cancel_handler
from src.domain.enums.real_estate_enums import PropertyType, ListingType, PropertyCondition
from src.domain.config.location_constants import CITIES, DISTRICTS
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.domain.models.buyer_request import BuyerRequest


(
    SELECT_PROPERTY_TYPE,
    SELECT_LISTING_TYPE,
    SELECT_CONDITION,
    SELECT_CITY,
    SELECT_DISTRICTS,
    SELECT_MIN_PRICE,
    SELECT_MAX_PRICE,
    SELECT_MIN_AREA,
    SELECT_MAX_AREA,
    SELECT_MIN_BEDROOMS,
    SELECT_MAX_BEDROOMS,
    SELECT_FEATURES,
    SELECT_MIN_FLOOR,
    SELECT_MAX_FLOOR,
    CONFIRM,
) = range(15)


CANCEL_ROW = ["❌ Cancel"]
DONE_ROW = ["✔️ Done", "❌ Cancel"]
SKIP_ROW = ["⏭ Skip"]
SKIP_CANCEL_ROW = ["⏭ Skip", "❌ Cancel"]


def with_cancel(keyboard: list) -> list:
    return keyboard + [CANCEL_ROW]


def build_multi_select_keyboard(items: list, selected: list) -> list:
    """Multi-select keyboard builder from a list of strings"""
    keyboard = []
    for i in range(0, len(items), 2):
        row = []
        for item in items[i:i+2]:
            prefix = "✅ " if item in selected else ""
            row.append(f"{prefix}{item}")
        keyboard.append(row)
    keyboard.append(DONE_ROW)
    return keyboard


def build_enum_multi_select_keyboard(enum_class, selected: list) -> list:
    """Multi-select keyboard builder from an enum"""
    items = [item.value for item in enum_class]
    return build_multi_select_keyboard(items, selected)


# ================= START =================

async def start_real_estate_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        if not buyer:
            await update.message.reply_text("⚠️ You need to register first. Use /start.")
            return ConversationHandler.END

        max_requests = get_max_requests_for_buyer(buyer.payment)
        existing_requests = await request_service.get_requests_by_buyer(buyer.id)

        if len(existing_requests) >= max_requests:
            plan = buyer.payment.get("plan", "free") if buyer.payment else "free"
            await update.message.reply_text(
                f"⚠️ You've reached the maximum of {max_requests} active requests for your {plan} plan.\n\n"
                f"Delete an existing request from 📄 My Requests to add a new one, "
                f"or upgrade your plan for more requests.",
                reply_markup=get_buyer_menu_keyboard()
            )
            return ConversationHandler.END

    context.user_data["request"] = {}

    # Start with property type multi-select
    context.user_data["selected_property_type"] = []
    keyboard = build_enum_multi_select_keyboard(PropertyType, [])
    await update.message.reply_text(
        "🏠 What type of property are you looking for?\n"
        "Select one or more, then press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_PROPERTY_TYPE


# ================= PROPERTY TYPE (multi-select) =================

async def handle_property_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "✔️ Done":
        selected = context.user_data.get("selected_property_type", [])
        if not selected:
            await update.message.reply_text("Please select at least one property type:")
            return SELECT_PROPERTY_TYPE

        context.user_data["request"]["property_type"] = selected
        context.user_data.pop("selected_property_type", None)

        # Move to listing type
        keyboard = with_cancel([[lt.value] for lt in ListingType])
        await update.message.reply_text(
            "Are you looking to buy or rent?",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
        )
        return SELECT_LISTING_TYPE

    clean = text.replace("✅ ", "")
    valid_values = [pt.value for pt in PropertyType]
    if clean not in valid_values:
        await update.message.reply_text("Please select from the list.")
        return SELECT_PROPERTY_TYPE

    selected = context.user_data.setdefault("selected_property_type", [])
    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_enum_multi_select_keyboard(PropertyType, selected)
    selected_display = ", ".join(selected) if selected else "none"
    await update.message.reply_text(
        f"Selected: {selected_display}\nTap more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_PROPERTY_TYPE


# ================= LISTING TYPE =================

async def handle_listing_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    valid_values = [lt.value for lt in ListingType]
    if text not in valid_values:
        await update.message.reply_text("Please select from the list.")
        return SELECT_LISTING_TYPE

    context.user_data["request"]["listing_type"] = text

    # Move to condition
    keyboard = with_cancel([[pc.value] for pc in PropertyCondition] + [SKIP_ROW])
    await update.message.reply_text(
        "Property condition?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_CONDITION


# ================= CONDITION =================

async def handle_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "⏭ Skip":
        context.user_data["request"]["condition"] = None
    else:
        valid_values = [pc.value for pc in PropertyCondition]
        if text not in valid_values:
            await update.message.reply_text("Please select from the list.")
            return SELECT_CONDITION
        context.user_data["request"]["condition"] = text

    # Move to city
    keyboard = with_cancel([[city] for city in CITIES])
    await update.message.reply_text(
        "Which city?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_CITY


# ================= CITY =================

async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in CITIES:
        await update.message.reply_text("Please select a city from the list.")
        return SELECT_CITY

    context.user_data["request"]["city"] = text

    # Move to districts
    districts = DISTRICTS.get(text, [])
    if not districts:
        context.user_data["request"]["districts"] = None
        return await ask_min_price(update, context)

    keyboard = []
    for i in range(0, len(districts), 2):
        keyboard.append(districts[i:i+2])
    keyboard.append(["✅ Multiple Districts"])
    keyboard.append(["⏭ Any District", "❌ Cancel"])

    await update.message.reply_text(
        f"Which district in {text}?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_DISTRICTS


# ================= DISTRICTS =================

async def handle_districts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    city = context.user_data["request"]["city"]
    valid_districts = DISTRICTS.get(city, [])

    if text == "✔️ Done":
        selected = context.user_data.get("selected_districts", [])
        if not selected:
            await update.message.reply_text("Please select at least one district:")
            return SELECT_DISTRICTS

        context.user_data["request"]["districts"] = selected
        context.user_data.pop("selected_districts", None)
        return await ask_min_price(update, context)

    if text == "⏭ Any District":
        context.user_data["request"]["districts"] = None
        context.user_data.pop("selected_districts", None)
        return await ask_min_price(update, context)

    clean = text.replace("✅ ", "")
    if clean not in valid_districts:
        await update.message.reply_text("Please select from the list.")
        return SELECT_DISTRICTS

    selected = context.user_data.setdefault("selected_districts", [])
    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_multi_select_keyboard(valid_districts, selected)
    keyboard.append(["⏭ Any District"])
    selected_display = ", ".join(selected) if selected else "none"
    await update.message.reply_text(
        f"Selected: {selected_display}\nTap more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_DISTRICTS


# ================= PRICE =================

async def ask_min_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Enter MIN price (€):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_MIN_PRICE


async def handle_min_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(",", "").replace(" ", "")
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g. 50000):")
        return SELECT_MIN_PRICE

    if value < 0:
        await update.message.reply_text("❌ Price cannot be negative. Try again:")
        return SELECT_MIN_PRICE

    context.user_data["request"]["min_price"] = value
    await update.message.reply_text(
        "Enter MAX price (€):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_MAX_PRICE


async def handle_max_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(",", "").replace(" ", "")
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g. 100000):")
        return SELECT_MAX_PRICE

    min_price = context.user_data["request"]["min_price"]
    if value < min_price:
        await update.message.reply_text(
            f"❌ Max price must be greater than min price (€{min_price:,.0f}). Try again:"
        )
        return SELECT_MAX_PRICE

    context.user_data["request"]["max_price"] = value
    return await ask_min_area(update, context)


# ================= AREA =================

async def ask_min_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Enter MIN area (m²) or skip:",
        reply_markup=ReplyKeyboardMarkup([SKIP_CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_MIN_AREA


async def handle_min_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "⏭ Skip":
        context.user_data["request"]["min_area"] = None
        context.user_data["request"]["max_area"] = None
        return await ask_min_bedrooms(update, context)

    cleaned = text.replace(",", "").replace(" ", "")
    try:
        value = float(cleaned)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g. 60):")
        return SELECT_MIN_AREA

    if value <= 0:
        await update.message.reply_text("❌ Area must be greater than 0. Try again:")
        return SELECT_MIN_AREA

    context.user_data["request"]["min_area"] = value
    await update.message.reply_text(
        "Enter MAX area (m²):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_MAX_AREA


async def handle_max_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(",", "").replace(" ", "")
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g. 120):")
        return SELECT_MAX_AREA

    min_area = context.user_data["request"]["min_area"]
    if value < min_area:
        await update.message.reply_text(
            f"❌ Max area must be greater than min area ({min_area:.0f} m²). Try again:"
        )
        return SELECT_MAX_AREA

    context.user_data["request"]["max_area"] = value
    return await ask_min_bedrooms(update, context)



# ================= BEDROOMS =================

async def ask_min_bedrooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["1", "2", "3"],
        ["4", "5+"],
        SKIP_CANCEL_ROW,
    ]
    await update.message.reply_text(
        "Minimum number of bedrooms?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MIN_BEDROOMS


async def handle_min_bedrooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "⏭ Skip":
        context.user_data["request"]["min_bedrooms"] = None
        context.user_data["request"]["max_bedrooms"] = None
        return await ask_features(update, context)

    cleaned = text.replace("+", "")
    if not cleaned.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_MIN_BEDROOMS

    value = int(cleaned)
    if value <= 0:
        await update.message.reply_text("❌ Must be at least 1. Try again:")
        return SELECT_MIN_BEDROOMS

    context.user_data["request"]["min_bedrooms"] = value

    keyboard = [
        ["1", "2", "3"],
        ["4", "5+"],
        CANCEL_ROW,
    ]
    await update.message.reply_text(
        "Maximum number of bedrooms?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MAX_BEDROOMS


async def handle_max_bedrooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    cleaned = text.replace("+", "")

    if not cleaned.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_MAX_BEDROOMS

    value = int(cleaned)
    min_bedrooms = context.user_data["request"]["min_bedrooms"]
    if value < min_bedrooms:
        await update.message.reply_text(
            f"❌ Max bedrooms must be >= min bedrooms ({min_bedrooms}). Try again:"
        )
        return SELECT_MAX_BEDROOMS

    context.user_data["request"]["max_bedrooms"] = value
    return await ask_features(update, context)


# ================= FEATURES (multi-select) =================

FEATURE_OPTIONS = ["🅿️ Parking", "🛗 Elevator", "🛋 Furnished", "🏞 Balcony"]
FEATURE_KEYS = {
    "🅿️ Parking": "parking",
    "🛗 Elevator": "elevator",
    "🛋 Furnished": "furnished",
    "🏞 Balcony": "balcony",
}


async def ask_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["selected_features"] = []
    keyboard = build_multi_select_keyboard(FEATURE_OPTIONS, [])
    keyboard.append(["⏭ Skip"])
    await update.message.reply_text(
        "Which features are important to you?\nSelect one or more, then press Done.\nOr skip if you don't care:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_FEATURES


async def handle_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "⏭ Skip":
        context.user_data["request"]["parking"] = None
        context.user_data["request"]["elevator"] = None
        context.user_data["request"]["furnished"] = None
        context.user_data["request"]["balcony"] = None
        context.user_data.pop("selected_features", None)
        return await ask_min_floor(update, context)

    if text == "✔️ Done":
        selected = context.user_data.get("selected_features", [])
        # Set selected features to True, unselected to None
        for label, key in FEATURE_KEYS.items():
            context.user_data["request"][key] = True if label in selected else None
        context.user_data.pop("selected_features", None)
        return await ask_min_floor(update, context)

    clean = text.replace("✅ ", "")
    if clean not in FEATURE_OPTIONS:
        await update.message.reply_text("Please select from the list.")
        return SELECT_FEATURES

    selected = context.user_data.setdefault("selected_features", [])
    if clean in selected:
        selected.remove(clean)
    else:
        selected.append(clean)

    keyboard = build_multi_select_keyboard(FEATURE_OPTIONS, selected)
    keyboard.append(["⏭ Skip"])
    selected_display = ", ".join(selected) if selected else "none"
    await update.message.reply_text(
        f"Selected: {selected_display}\nTap more or press Done:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True),
    )
    return SELECT_FEATURES
# ================= FLOOR =================

async def ask_min_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["0", "1", "2", "3"],
        ["4", "5", "6", "7+"],
        SKIP_CANCEL_ROW,
    ]
    await update.message.reply_text(
        "Minimum floor?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MIN_FLOOR


async def handle_min_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "⏭ Skip":
        context.user_data["request"]["min_floor"] = None
        context.user_data["request"]["max_floor"] = None
        return await show_confirm(update, context)

    cleaned = text.replace("+", "")
    if not cleaned.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_MIN_FLOOR

    context.user_data["request"]["min_floor"] = int(cleaned)

    keyboard = [
        ["0", "1", "2", "3"],
        ["4", "5", "6", "7+"],
        CANCEL_ROW,
    ]
    await update.message.reply_text(
        "Maximum floor?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MAX_FLOOR


async def handle_max_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    cleaned = text.replace("+", "")

    if not cleaned.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_MAX_FLOOR

    value = int(cleaned)
    min_floor = context.user_data["request"]["min_floor"]
    if value < min_floor:
        await update.message.reply_text(
            f"❌ Max floor must be >= min floor ({min_floor}). Try again:"
        )
        return SELECT_MAX_FLOOR

    context.user_data["request"]["max_floor"] = value
    return await show_confirm(update, context)


# ================= CONFIRM =================

async def show_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data["request"]

    summary = f"🏠 {', '.join(data['property_type'])} — {data['listing_type']}\n"

    if data.get("condition"):
        summary += f"🏗 {data['condition']}\n"

    summary += f"📍 {data['city']}"
    if data.get("districts"):
        summary += f" — {', '.join(data['districts'])}"
    summary += "\n"

    summary += f"💶 €{data['min_price']:,.0f} — €{data['max_price']:,.0f}\n"

    if data.get("min_area") is not None:
        summary += f"📐 {data['min_area']:.0f} — {data['max_area']:.0f} m²\n"

    if data.get("min_bedrooms") is not None:
        summary += f"🛏 {data['min_bedrooms']} — {data['max_bedrooms']} bedrooms\n"

    features = []
    if data.get("parking") is True:
        features.append("🅿️ Parking")
    if data.get("elevator") is True:
        features.append("🛗 Elevator")
    if data.get("furnished") is True:
        features.append("🛋 Furnished")
    if data.get("balcony") is True:
        features.append("🏞 Balcony")
    if features:
        summary += f"✅ {', '.join(features)}\n"

    if data.get("min_floor") is not None:
        summary += f"🏢 Floor {data['min_floor']} — {data['max_floor']}\n"

    await update.message.reply_text(
        f"Confirm your request:\n\n{summary}",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Confirm", "❌ Cancel"]],
            resize_keyboard=True,
            is_persistent=True,
        ),
    )
    return CONFIRM


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
                type="real_estate",
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

def get_real_estate_request_conv():
    cancel_filter = filters.Regex("^❌ Cancel$")

    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏠 Request Real Estate$"), start_real_estate_request)],
        states={
            SELECT_PROPERTY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_property_type)],
            SELECT_LISTING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_listing_type)],
            SELECT_CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_condition)],
            SELECT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_city)],
            SELECT_DISTRICTS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_districts)],
            SELECT_MIN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_min_price)],
            SELECT_MAX_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_max_price)],
            SELECT_MIN_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_min_area)],
            SELECT_MAX_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_max_area)],
            SELECT_MIN_BEDROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_min_bedrooms)],
            SELECT_MAX_BEDROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_max_bedrooms)],
            SELECT_FEATURES: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_features)],
            SELECT_MIN_FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_min_floor)],
            SELECT_MAX_FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_max_floor)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            MessageHandler(cancel_filter, cancel_handler),
        ],
        persistent=True,
        name="real_estate_request",
    )