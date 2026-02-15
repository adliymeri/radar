from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.infrastructure.utils.logs import app_log

async def error_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app_log.error("error_exit triggered", exc_info=True)
    context.user_data.clear()

    await update.message.reply_text(
        "⚠️ Something went wrong. Please try again.",
        reply_markup=get_buyer_menu_keyboard(),
    )

    return ConversationHandler.END