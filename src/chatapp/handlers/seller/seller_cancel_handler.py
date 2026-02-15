from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Cancelled.",
        reply_markup=get_seller_menu_keyboard(),
    )
    return ConversationHandler.END