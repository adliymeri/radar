from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from src.chatapp.handlers.seller.seller_error_handler import error_exit
from src.chatapp.handlers.seller.seller_cancel_handler import cancel_handler
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.domain.models.car_listing import CarListing
from src.domain.models.listing import Listing
from src.domain.enums.car_enums import (
    CarBrand, CAR_MODELS, Color, Transmission,
    FuelType, Drivetrain, get_years
)
from src.infrastructure.utils.logs import app_log

(
    SELECT_MAKE,
    SELECT_MODEL,
    SELECT_YEAR,
    SELECT_PRICE,
    SELECT_MILEAGE,
    SELECT_COLOR,
    SELECT_TRANSMISSION,
    SELECT_FUEL,
    SELECT_DRIVETRAIN,
    SELECT_LOCATION,
    UPLOAD_PHOTOS,
    GET_LINK,
    GET_DESCRIPTION,
    CONFIRM,
) = range(14)


CANCEL_ROW = ["❌ Cancel"]


def with_cancel(keyboard: list) -> list:
    return keyboard + [CANCEL_ROW]


# ================= START =================

async def start_car_listing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"] = {}
    context.user_data["photos"] = []

    keyboard = with_cancel([[b.value] for b in CarBrand])
    await update.message.reply_text(
        "🚗 Let's post your car!\n\nChoose the brand:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
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

    context.user_data["listing"]["make"] = brand
    keyboard = with_cancel([[m] for m in models])
    await update.message.reply_text(
        "Select model:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_MODEL


# ================= MODEL =================

async def handle_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"]["model"] = update.message.text

    years = get_years()
    keyboard = with_cancel([list(map(str, years[i:i+4])) for i in range(0, len(years), 4)])
    await update.message.reply_text(
        "Select year:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_YEAR


# ================= YEAR =================

async def handle_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["listing"]["year"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please select a valid year from the list.")
        return SELECT_YEAR

    await update.message.reply_text(
        "Enter the price (€):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True, is_persistent=True),
    )
    return SELECT_PRICE


# ================= PRICE =================

async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["listing"]["price"] = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number (e.g. 15000):")
        return SELECT_PRICE

    await update.message.reply_text(
        "Mileage (km):",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True),
    )
    return SELECT_MILEAGE


# ================= MILEAGE =================

async def handle_mileage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["listing"]["mileage"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number (e.g. 50000):")
        return SELECT_MILEAGE

    keyboard = with_cancel([[c.value] for c in Color])
    await update.message.reply_text(
        "Choose color:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return SELECT_COLOR


# ================= COLOR (single select) =================

async def handle_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"]["color"] = [update.message.text]  # store as array with one item

    keyboard = with_cancel([[t.value] for t in Transmission])
    await update.message.reply_text(
        "Transmission:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_TRANSMISSION


# ================= TRANSMISSION =================

async def handle_transmission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"]["transmission"] = update.message.text

    keyboard = with_cancel([[f.value] for f in FuelType])
    await update.message.reply_text(
        "Fuel type:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_FUEL


# ================= FUEL =================

async def handle_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"]["fuel_type"] = update.message.text

    keyboard = with_cancel([[d.value] for d in Drivetrain])
    await update.message.reply_text(
        "Drivetrain:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True),
    )
    return SELECT_DRIVETRAIN


# ================= DRIVETRAIN =================

async def handle_drivetrain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"]["drivetrain"] = update.message.text

    await update.message.reply_text(
        "Where is the car located?",
        reply_markup=ReplyKeyboardMarkup([CANCEL_ROW], resize_keyboard=True),
    )
    return SELECT_LOCATION


# ================= LOCATION =================

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["listing"]["location"] = update.message.text.strip()

    await update.message.reply_text(
        "📸 Send photos of the car one by one.\nPress Done when finished:",
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

    summary = (
        f"🚗 {data['make']} {data['model']} ({data['year']})\n"
        f"💶 €{data['price']:,.0f}\n"
        f"🛣 {data['mileage']:,} km\n"
        f"🎨 {', '.join(data['color'])}\n"
        f"⚙️ {data['transmission']} | {data['fuel_type']} | {data['drivetrain']}\n"
        f"📍 {data['location']}\n"
        f"📸 {photo_count} photo(s)\n"
        f"🔗 {data.get('link') or 'No link'}\n"
        f"📝 {data.get('description') or 'No description'}"
    )

    await update.message.reply_text(
        f"Please confirm your listing:\n\n{summary}",
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
        data = context.user_data["listing"]
        chat_id = str(update.effective_user.id)

        async with get_bot_deps() as deps:
            seller_service = deps["seller_service"]
            listing_service = deps["listing_service"]
            car_listing_service = deps["car_listing_service"]

            seller = await seller_service.get_seller_by_chat_id(chat_id)
            if not seller:
                await update.message.reply_text(
                    "⚠️ You need to register first. Use /start.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                return ConversationHandler.END

            new_listing = Listing(
                seller_id=seller.id,
                type="car",
            )
            created_listing = await listing_service.create_listing(new_listing)

            new_car_listing = CarListing(
                listing_id=created_listing.id,
                make=data["make"],
                model=data["model"],
                year=data["year"],
                price=data["price"],
                mileage=data["mileage"],
                color=data["color"],
                transmission=data["transmission"],
                fuel_type=data["fuel_type"],
                drivetrain=data["drivetrain"],
                location=data["location"],
                photos=data["photos"],
                link=data.get("link"),
                description=data.get("description"),
            )
            await car_listing_service.create_car_listing(new_car_listing)

        context.user_data.clear()
        await update.message.reply_text(
            "✅ Your car listing has been posted!",
            reply_markup=get_seller_menu_keyboard(),
        )
        return ConversationHandler.END

    except Exception as e:
        app_log.error(f"Error posting car listing: {e}", exc_info=True)
        return await error_exit(update, context)


# ================= CONVERSATION =================

def get_seller_car_listing_conv():
    cancel_filter = filters.Regex("^❌ Cancel$")
    done_filter = filters.Regex("^✔️ Done$")

    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🚗 Post a Car$"), start_car_listing)],
        states={
            SELECT_MAKE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_make)],
            SELECT_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_model)],
            SELECT_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_year)],
            SELECT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_price)],
            SELECT_MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_mileage)],
            SELECT_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_color)],
            SELECT_TRANSMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_transmission)],
            SELECT_FUEL: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_fuel)],
            SELECT_DRIVETRAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_drivetrain)],
            SELECT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, handle_location)],
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
    )