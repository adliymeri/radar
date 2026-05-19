from telegram import Update
from telegram.ext import ContextTypes
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard


async def handle_lost_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ Session expired. Please start again from the menu.",
        reply_markup=get_buyer_menu_keyboard()
    )