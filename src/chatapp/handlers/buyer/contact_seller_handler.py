from uuid import UUID
from telegram import Update, Bot
from telegram.ext import ContextTypes, CallbackQueryHandler
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.infrastructure.utils.logs import app_log


async def handle_contact_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Contact Seller' button click"""
    query = update.callback_query
    await query.answer()

    match_id = UUID(query.data.split(":")[1])

    async with get_bot_deps() as deps:
        matching_service = deps["matching_service"]  # changed
        buyer_service = deps["buyer_service"]
        seller_service = deps["seller_service"]

        # Mark match as contacted
        await matching_service.mark_as_contacted(match_id)  # changed

        # Get match details
        match = await matching_service.get_match_by_id(match_id)  # changed
        buyer = await buyer_service.get_buyer_by_id(match.buyer_id)
        seller = await seller_service.get_seller_by_id(match.seller_id)

        seller_handle = seller.details.get("telegram_handle", "N/A")
        seller_phone = seller.details.get("mobile_phone", "Not shared")

        message = (
            f"✅ Seller Contact Information:\n\n"
            f"📱 Telegram: @{seller_handle}\n"
            f"📞 Phone: {seller_phone}\n\n"
            f"Feel free to reach out directly!"
        )

        await query.edit_message_text(message)
        app_log.info(f"Match {match_id} marked as contacted")


def get_contact_seller_handler():
    return CallbackQueryHandler(handle_contact_seller, pattern="^contact_seller:")