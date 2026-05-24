from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.domain.config.limits import get_max_listings_for_seller
from src.chatapp.handlers.seller.seller_error_handler import error_exit
from src.chatapp.handlers.seller.seller_cancel_handler import cancel_handler
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.domain.models.real_estate_listing import RealEstateListing
from src.domain.models.listing import Listing
from src.domain.enums.real_estate_enums import PropertyType, ListingType, PropertyCondition
from src.domain.config.location_constants import CITIES, DISTRICTS
from src.infrastructure.utils.logs import app_log

(
    SELECT_PROPERTY_TYPE,
    SELECT_LISTING_TYPE,
    SELECT_CONDITION,
    SELECT_CITY,
    SELECT_DISTRICT,
    SELECT_ADDRESS,
    SELECT_AREA,
    SELECT_BEDROOMS,
    SELECT_BATHROOMS,
    SELECT_FLOOR,
    SELECT_PRICE,
    SELECT_PARKING,
    SELECT_ELEVATOR,
    SELECT_FURNISHED,
    SELECT_BALCONY,
    UPLOAD_PHOTOS,
    GET_LINK,
    GET_DESCRIPTION,
    CONFIRM,
) = range(19)


CANCEL_ROW = ["❌ Cancel"]


def with_cancel(keyboard: list) -> list:
    return keyboard + [CANCEL_ROW]


# ================= START =================

async def start_real_estate_listing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        listing_service = deps["listing_service"]

        seller = await seller_service.get_seller_by_chat_id(chat_id)
        if not seller:
            await update.message.reply_text("⚠️ You need to register first. Use /start.")
            return ConversationHandler.END

        max_listings = get_max_listings_for_seller(seller.payment)
        existing_listings = await listing_service.get_listings_by_seller(seller.id)

        if len(existing_listings) >= max_listings:
            plan = seller.payment.get("plan", "free") if seller.payment else "free"
            await update.message.reply_text(
                f"⚠️ You've reached the maximum of {max_listings} active listings for your {plan} plan.\n\n"
                f"Delete an existing listing from 📋 My Listings to add a new one, "
                f"or upgrade your plan for more listings.",
                reply_markup=get_seller_menu_keyboard()
            )
            return ConversationHandler.END

    context.user_data["listing"] = {}
    context.user_data["photos"] = []

    keyboard = with_cancel([[pt.value] for pt in PropertyType])
    await update.message.reply_text(
        "🏠 Let's post your property!\n\nWhat type of property?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return SELECT_PROPERTY_TYPE


# ================= PROPERTY TYPE =================

async def handle_property_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    valid_values = [pt.value for pt in PropertyType]
    if text not in valid_values:
        await update.message.reply_text("Please select from the list.")
        return SELECT_PROPERTY_TYPE

    context.user_data["listing"]["property_type"] = text

    keyboard = with_cancel([[lt.value] for lt in ListingType])
    await update.message.reply_text(
        "For sale or rent?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_LISTING_TYPE


# ================= LISTING TYPE =================

async def handle_listing_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    valid_values = [lt.value for lt in ListingType]
    if text not in valid_values:
        await update.message.reply_text("Please select from the list.")
        return SELECT_LISTING_TYPE

    context.user_data["listing"]["listing_type"] = text

    keyboard = with_cancel([[pc.value] for pc in PropertyCondition])
    await update.message.reply_text(
        "Property condition?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_CONDITION


# ================= CONDITION =================

async def handle_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    valid_values = [pc.value for pc in PropertyCondition]
    if text not in valid_values:
        await update.message.reply_text("Please select from the list.")
        return SELECT_CONDITION

    context.user_data["listing"]["condition"] = text

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

    context.user_data["listing"]["city"] = text

    districts = DISTRICTS.get(text, [])
    if not districts:
        context.user_data["listing"]["district"] = ""
        return await ask_address(update, context)

    keyboard = with_cancel([[d] for d in districts])
    await update.message.reply_text(
        f"Which district in {text}?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_DISTRICT


# ================= DISTRICT =================

async def handle_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    city = context.user_data["listing"]["city"]
    valid_districts = DISTRICTS.get(city, [])

    if text not in valid_districts:
        await update.message.reply_text("Please select a district from the list.")
        return SELECT_DISTRICT

    context.user_data["listing"]["district"] = text
    return await ask_address(update, context)


# ================= ADDRESS =================

async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Enter the full address:",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_ADDRESS


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) < 3:
        await update.message.reply_text("❌ Address is too short. Please enter a valid address:")
        return SELECT_ADDRESS

    context.user_data["listing"]["address"] = text

    await update.message.reply_text(
        "Enter the area in m²:",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_AREA


# ================= AREA =================

async def handle_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(",", "").replace(" ", "")
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g. 85):")
        return SELECT_AREA

    if value <= 0:
        await update.message.reply_text("❌ Area must be greater than 0. Try again:")
        return SELECT_AREA

    context.user_data["listing"]["area"] = value

    keyboard = with_cancel([
        ["1", "2", "3"],
        ["4", "5+"],
    ])
    await update.message.reply_text(
        "How many bedrooms?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_BEDROOMS


# ================= BEDROOMS =================

async def handle_bedrooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace("+", "")
    if not text.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_BEDROOMS

    value = int(text)
    if value <= 0:
        await update.message.reply_text("❌ Must be at least 1. Try again:")
        return SELECT_BEDROOMS

    context.user_data["listing"]["bedrooms"] = value

    keyboard = with_cancel([
        ["1", "2", "3+"],
    ])
    await update.message.reply_text(
        "How many bathrooms?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_BATHROOMS


# ================= BATHROOMS =================

async def handle_bathrooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace("+", "")
    if not text.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_BATHROOMS

    value = int(text)
    if value <= 0:
        await update.message.reply_text("❌ Must be at least 1. Try again:")
        return SELECT_BATHROOMS

    context.user_data["listing"]["bathrooms"] = value

    keyboard = with_cancel([
        ["0", "1", "2", "3"],
        ["4", "5", "6", "7+"],
    ])
    await update.message.reply_text(
        "Which floor?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_FLOOR


# ================= FLOOR =================

async def handle_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace("+", "")
    if not text.isdigit():
        await update.message.reply_text("❌ Please select from the list or enter a number:")
        return SELECT_FLOOR

    context.user_data["listing"]["floor"] = int(text)

    await update.message.reply_text(
        "Enter the price (€):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_PRICE


# ================= PRICE =================

async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(",", "").replace(" ", "")
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g. 95000):")
        return SELECT_PRICE

    if value <= 0:
        await update.message.reply_text("❌ Price must be greater than 0. Try again:")
        return SELECT_PRICE

    context.user_data["listing"]["price"] = value
    return await ask_parking(update, context)


# ================= BOOLEAN FILTERS =================

async def ask_parking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = with_cancel([["✅ Yes", "❌ No"]])
    await update.message.reply_text(
        "🅿️ Does it have parking?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_PARKING


async def handle_parking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "✅ Yes":
        context.user_data["listing"]["parking"] = True
    elif text == "❌ No":
        context.user_data["listing"]["parking"] = False
    else:
        await update.message.reply_text("Please select Yes or No.")
        return SELECT_PARKING
    return await ask_elevator(update, context)


async def ask_elevator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = with_cancel([["✅ Yes", "❌ No"]])
    await update.message.reply_text(
        "🛗 Does it have an elevator?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_ELEVATOR


async def handle_elevator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "✅ Yes":
        context.user_data["listing"]["elevator"] = True
    elif text == "❌ No":
        context.user_data["listing"]["elevator"] = False
    else:
        await update.message.reply_text("Please select Yes or No.")
        return SELECT_ELEVATOR
    return await ask_furnished(update, context)


async def ask_furnished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = with_cancel([["✅ Yes", "❌ No"]])
    await update.message.reply_text(
        "🛋 Is it furnished?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_FURNISHED


async def handle_furnished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "✅ Yes":
        context.user_data["listing"]["furnished"] = True
    elif text == "❌ No":
        context.user_data["listing"]["furnished"] = False
    else:
        await update.message.reply_text("Please select Yes or No.")
        return SELECT_FURNISHED
    return await ask_balcony(update, context)


async def ask_balcony(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = with_cancel([["✅ Yes", "❌ No"]])
    await update.message.reply_text(
        "🏞 Does it have a balcony?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_BALCONY


async def handle_balcony(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "✅ Yes":
        context.user_data["listing"]["balcony"] = True
    elif text == "❌ No":
        context.user_data["listing"]["balcony"] = False
    else:
        await update.message.reply_text("Please select Yes or No.")
        return SELECT_BALCONY

    await update.message.reply_text(
        "📸 Send photos of the property one by one.\nPress Done when finished:",
        reply_markup=ReplyKeyboardMarkup([["✔️ Done", "❌ Cancel"]], resize_keyboard=True, is_persistent=True),
    )
    return UPLOAD_PHOTOS


# ================= PHOTOS =================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        context.user_data["photos"].append(file_id)
        count = len(context.user_data["photos"])
        await update.message.reply_text(
            f"📸 Photo {count} added. Send another or press Done:",
            reply_markup=ReplyKeyboardMarkup([["✔️ Done", "❌ Cancel"]], resize_keyboard=True, is_persistent=True),
        )
        return UPLOAD_PHOTOS

    if update.message.text == "✔️ Done":
        if not context.user_data["photos"]:
            await update.message.reply_text("Please send at least one photo:")
            return UPLOAD_PHOTOS

        context.user_data["listing"]["photos"] = context.user_data.pop("photos")

        await update.message.reply_text(
            "Do you have a listing link? Send it or press Skip:",
            reply_markup=ReplyKeyboardMarkup([["⏭ Skip", "❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
        )
        return GET_LINK

    await update.message.reply_text("Please send a photo or press Done:")
    return UPLOAD_PHOTOS


# ================= LINK =================

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["listing"]["link"] = None if text == "⏭ Skip" else text

    await update.message.reply_text(
        "Add a description? Send it or press Skip:",
        reply_markup=ReplyKeyboardMarkup([["⏭ Skip", "❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return GET_DESCRIPTION


# ================= DESCRIPTION =================

async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["listing"]["description"] = None if text == "⏭ Skip" else text

    data = context.user_data["listing"]
    photo_count = len(data.get("photos", []))

    features = []
    if data["parking"]:
        features.append("🅿️ Parking")
    if data["elevator"]:
        features.append("🛗 Elevator")
    if data["furnished"]:
        features.append("🛋 Furnished")
    if data["balcony"]:
        features.append("🏞 Balcony")

    summary = (
        f"🏠 {data['property_type']} — {data['listing_type']}\n"
        f"🏗 {data['condition']}\n"
        f"📍 {data['district']}, {data['city']}\n"
        f"📫 {data['address']}\n"
        f"📐 {data['area']:.0f} m²\n"
        f"🛏 {data['bedrooms']} bedrooms | 🚿 {data['bathrooms']} bathrooms\n"
        f"🏢 Floor {data['floor']}\n"
        f"💶 €{data['price']:,.0f}\n"
        f"{'✅ ' + ', '.join(features) if features else '❌ No features'}\n"
        f"📸 {photo_count} photo(s)\n"
        f"🔗 {data.get('link') or 'No link'}\n"
        f"📝 {data.get('description') or 'No description'}"
    )

    await update.message.reply_text(
        f"Please confirm your listing:\n\n{summary}",
        reply_markup=ReplyKeyboardMarkup(
            [["✅ Confirm", "❌ Cancel"]],
            resize_keyboard=True,
            is_persistent=True,
        ),
    )
    return CONFIRM


# ================= CONFIRM =================

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "Cancel" in update.message.text:
        return await cancel_handler(update, context)

    try:
        data = context.user_data["listing"]
        chat_id = str(update.effective_user.id)

        async with get_bot_deps() as deps:
            seller_service = deps["seller_service"]
            listing_service = deps["listing_service"]
            real_estate_listing_service = deps["real_estate_listing_service"]

            seller = await seller_service.get_seller_by_chat_id(chat_id)
            if not seller:
                await update.message.reply_text(
                    "⚠️ You need to register first. Use /start.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                return ConversationHandler.END

            new_listing = Listing(
                seller_id=seller.id,
                type="real_estate",
            )
            created_listing = await listing_service.create_listing(new_listing)

            new_real_estate_listing = RealEstateListing(
                listing_id=created_listing.id,
                property_type=data["property_type"],
                listing_type=data["listing_type"],
                condition=data["condition"],
                city=data["city"],
                district=data["district"],
                address=data["address"],
                area=data["area"],
                bedrooms=data["bedrooms"],
                bathrooms=data["bathrooms"],
                floor=data["floor"],
                price=data["price"],
                parking=data["parking"],
                elevator=data["elevator"],
                furnished=data["furnished"],
                balcony=data["balcony"],
                photos=data["photos"],
                link=data.get("link"),
                description=data.get("description"),
            )
            await real_estate_listing_service.create_listing(new_real_estate_listing)

        context.user_data.clear()
        await update.message.reply_text(
            "✅ Your property listing has been posted!",
            reply_markup=get_seller_menu_keyboard(),
        )
        return ConversationHandler.END

    except Exception as e:
        app_log.error(f"Error posting real estate listing: {e}", exc_info=True)
        return await error_exit(update, context)


# ================= CONVERSATION =================

def get_seller_real_estate_listing_conv():
    cancel_filter = filters.Regex("^❌ Cancel$")
    done_filter = filters.Regex("^✔️ Done$")

    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏠 Post Real Estate$"), start_real_estate_listing)],
        states={
            SELECT_PROPERTY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_property_type)],
            SELECT_LISTING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_listing_type)],
            SELECT_CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_condition)],
            SELECT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_city)],
            SELECT_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_district)],
            SELECT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_address)],
            SELECT_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_area)],
            SELECT_BEDROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_bedrooms)],
            SELECT_BATHROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_bathrooms)],
            SELECT_FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_floor)],
            SELECT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_price)],
            SELECT_PARKING: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_parking)],
            SELECT_ELEVATOR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_elevator)],
            SELECT_FURNISHED: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_furnished)],
            SELECT_BALCONY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_balcony)],
            UPLOAD_PHOTOS: [
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(done_filter, handle_photo),
            ],
            GET_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_link)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_description)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirm)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            MessageHandler(cancel_filter, cancel_handler),
        ],
        persistent=True,
        name="real_estate_listing",
    )