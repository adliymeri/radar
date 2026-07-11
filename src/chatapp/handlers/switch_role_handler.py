from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps


async def switch_to_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        seller = await seller_service.get_seller_by_chat_id(chat_id)

    if seller:
        context.user_data["current_role"] = "seller"
        await update.message.reply_text(
            "Switched to Seller mode!",
            reply_markup=get_seller_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "You're not registered as a seller yet.\n"
            "Use /start to register as a seller."
        )


async def switch_to_buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)

    if buyer:
        context.user_data["current_role"] = "buyer"
        await update.message.reply_text(
            "Switched to Buyer mode!",
            reply_markup=get_buyer_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "You're not registered as a buyer yet.\n"
            "Use /start to register as a buyer."
        )


def get_switch_role_handlers():
    return [
        MessageHandler(filters.Regex("^🔄 Switch to Seller$"), switch_to_seller),
        MessageHandler(filters.Regex("^🔄 Switch to Buyer$"), switch_to_buyer),
    ]