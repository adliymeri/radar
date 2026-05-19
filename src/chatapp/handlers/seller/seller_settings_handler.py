from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.infrastructure.utils.logs import app_log
import re

# States
EDIT_PHONE, EDIT_WEBSITE = range(2)


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current settings with edit options"""
    chat_id = str(update.effective_user.id)
    
    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        seller = await seller_service.get_seller_by_chat_id(chat_id)
    
    if not seller:
        await update.message.reply_text("⚠️ You need to register first. Use /start.")
        return
    
    phone = seller.details.get("mobile_phone", "Not set")
    website = seller.details.get("website", "Not set")
    telegram = seller.details.get("telegram_handle", "N/A")
    
    settings_text = f"""
⚙️ **Contact Settings**

**Phone:** {phone}
**Website:** {website}
**Telegram:** @{telegram} (automatic)

Tap below to update:
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Edit Phone Number", callback_data="edit_phone")],
        [InlineKeyboardButton("✏️ Edit Website", callback_data="edit_website")],
    ])
    
    await update.message.reply_text(
        settings_text,
        reply_markup=keyboard,
    )


# ================= EDIT PHONE =================

async def handle_edit_phone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Ask to share phone via contact button
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Share Phone Number", request_contact=True)], ["❌ Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    
    await query.edit_message_text("Please share your new phone number:")
    await query.message.reply_text(
        "Use the button below:",
        reply_markup=keyboard,
    )
    
    return EDIT_PHONE


async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    
    # Validate it's the user's own contact
    if not contact or contact.user_id != update.effective_user.id:
        await update.message.reply_text(
            "⚠️ Please use the button to share YOUR phone number.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📱 Share Phone Number", request_contact=True)], ["❌ Cancel"]],
                resize_keyboard=True,
            ),
        )
        return EDIT_PHONE
    
    new_phone = contact.phone_number
    chat_id = str(update.effective_user.id)
    
    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        seller = await seller_service.get_seller_by_chat_id(chat_id)
        
        # Add + prefix if missing
        seller.details["mobile_phone"] = f"+{new_phone}" if not new_phone.startswith("+") else new_phone
        await seller_service.update_seller(seller)
    
    await update.message.reply_text(
        f"✅ Phone number updated to: {seller.details['mobile_phone']}",
        reply_markup=get_seller_menu_keyboard(),
    )
    return ConversationHandler.END


async def invalid_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-contact messages during phone edit"""
    await update.message.reply_text(
        "⚠️ Please use the button to share your phone number.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Share Phone Number", request_contact=True)], ["❌ Cancel"]],
            resize_keyboard=True,
        ),
    )
    return EDIT_PHONE


# ================= EDIT WEBSITE =================

async def handle_edit_website_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = ReplyKeyboardMarkup(
        [["⏭ Skip"], ["❌ Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    
    await query.edit_message_text("Enter your website URL or press Skip to remove:")
    await query.message.reply_text(
        "Use the buttons or type a URL:",
        reply_markup=keyboard,
    )
    
    return EDIT_WEBSITE


async def handle_website_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Handle skip/remove
    if text == "⏭ Skip":
        new_website = None
    # Validate URL
    elif not re.match(r"^https?://", text):
        await update.message.reply_text(
            "⚠️ Please provide a valid URL (e.g., https://example.com) or press Skip:",
            reply_markup=ReplyKeyboardMarkup(
                [["⏭ Skip"], ["❌ Cancel"]],
                resize_keyboard=True,
            ),
        )
        return EDIT_WEBSITE
    else:
        new_website = text
    
    chat_id = str(update.effective_user.id)
    
    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        seller = await seller_service.get_seller_by_chat_id(chat_id)
        
        if new_website:
            seller.details["website"] = new_website
        else:
            seller.details.pop("website", None)
        
        await seller_service.update_seller(seller)
    
    message = f"✅ Website updated to: {new_website}" if new_website else "✅ Website removed"
    await update.message.reply_text(
        message,
        reply_markup=get_seller_menu_keyboard(),
    )
    return ConversationHandler.END


# ================= CANCEL =================

async def cancel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel settings edit"""
    await update.message.reply_text(
        "Settings update cancelled.",
        reply_markup=get_seller_menu_keyboard(),
    )
    return ConversationHandler.END


# ================= CONVERSATION HANDLER =================

def get_seller_settings_conv():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^⚙️ Settings$"), show_settings),
            CallbackQueryHandler(handle_edit_phone_callback, pattern="^edit_phone$"),
            CallbackQueryHandler(handle_edit_website_callback, pattern="^edit_website$"),
        ],
        states={
            EDIT_PHONE: [
                MessageHandler(filters.CONTACT, handle_phone_input),
                MessageHandler(filters.TEXT & ~filters.CONTACT, invalid_phone_input),
            ],
            EDIT_WEBSITE: [
                MessageHandler(filters.Regex("^⏭ Skip$"), handle_website_input),
                MessageHandler(filters.Regex("^https?://.+\\..+"), handle_website_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_website_input),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^❌ Cancel$"), cancel_settings),
        ],
        persistent=True,
        name="settings",
    )