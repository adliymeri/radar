from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    # Always send a new message with the main buyer menu
    await update.message.reply_text(
        "⬆️ Main Menu",
        reply_markup=get_buyer_menu_keyboard()
    )

    return ConversationHandler.END
