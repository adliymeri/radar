from uuid import UUID
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.infrastructure.utils.logs import app_log


def format_listing_line(listing, car_listing, index: int) -> str:
    """Format single listing for display"""
    return (
        f"{index}️⃣ {car_listing.make} {car_listing.model} ({car_listing.year}) "
        f"— €{car_listing.price:,.0f} | {car_listing.mileage:,} km"
    )


# ================= SHOW LISTINGS =================

async def show_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        listing_service = deps["listing_service"]
        car_listing_service = deps["car_listing_service"]

        seller = await seller_service.get_seller_by_chat_id(chat_id)
        if not seller:
            await update.message.reply_text("⚠️ You need to register first. Use /start.")
            return

        # Get all listings for this seller
        listings = await listing_service.get_listings_by_seller(seller.id)

    if not listings:
        await update.message.reply_text(
            "📋 You have no active listings.",
            reply_markup=get_seller_menu_keyboard(),
        )
        return

    # Fetch car details for each listing
    lines = [f"📋 Your Car Listings ({len(listings)}):\n"]
    keyboard = []
    
    for i, listing in enumerate(listings):
        async with get_bot_deps() as deps:
            car_listing_service = deps["car_listing_service"]
            car_listing = await car_listing_service.get_car_listing_by_id(listing.id)
        
        if not car_listing:
            continue
        
        lines.append(format_listing_line(listing, car_listing, i + 1))
        
        # CHANGED: Use seller_ prefix
        keyboard.append([
            InlineKeyboardButton(
                f"❌ Delete {car_listing.make} {car_listing.model}",
                callback_data=f"seller_delete_listing:{listing.id}"
            )
        ])

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ================= DELETE LISTING =================

async def handle_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    listing_id = UUID(query.data.split(":")[1])

    # CHANGED: Use seller_ prefix
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"seller_confirm_delete:{listing_id}"),
            InlineKeyboardButton("❌ No, Keep", callback_data="seller_cancel_delete"),
        ]
    ])

    await query.edit_message_text(
        "Are you sure you want to delete this listing?",
        reply_markup=keyboard,
    )


async def handle_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    listing_id = UUID(query.data.split(":")[1])

    try:
        async with get_bot_deps() as deps:
            listing_service = deps["listing_service"]
            await listing_service.delete_listing(listing_id)

        # Refresh the listings view
        chat_id = str(update.effective_user.id)
        async with get_bot_deps() as deps:
            seller_service = deps["seller_service"]
            listing_service = deps["listing_service"]
            car_listing_service = deps["car_listing_service"]

            seller = await seller_service.get_seller_by_chat_id(chat_id)
            listings = await listing_service.get_listings_by_seller(seller.id)

        if not listings:
            await query.edit_message_text(
                "✅ Listing deleted successfully.\n\n📋 You have no more active listings.",
            )
            return

        # Rebuild the list
        lines = [f"✅ Listing deleted successfully.\n\n📋 Your Car Listings ({len(listings)}):\n"]
        keyboard = []
        
        for i, listing in enumerate(listings):
            async with get_bot_deps() as deps:
                car_listing_service = deps["car_listing_service"]
                car_listing = await car_listing_service.get_car_listing_by_id(listing.id)
            
            if not car_listing:
                continue
            
            lines.append(format_listing_line(listing, car_listing, i + 1))
            
            # CHANGED: Use seller_ prefix
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ Delete {car_listing.make} {car_listing.model}",
                    callback_data=f"seller_delete_listing:{listing.id}"
                )
            ])

        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        app_log.error(f"Error deleting listing: {e}", exc_info=True)
        await query.edit_message_text("⚠️ Something went wrong. Please try again.")


async def handle_cancel_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()


# ================= HANDLER REGISTRATION =================

def get_seller_listings_handler():
    return [
        MessageHandler(filters.Regex("^📋 My Listings$"), show_listings),
        CallbackQueryHandler(handle_delete_callback, pattern="^seller_delete_listing:"),
        CallbackQueryHandler(handle_confirm_delete, pattern="^seller_confirm_delete:"),
        CallbackQueryHandler(handle_cancel_delete, pattern="^seller_cancel_delete$"),
    ]