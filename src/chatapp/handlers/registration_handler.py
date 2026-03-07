from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, filters
)
from uuid import UUID
import re

from src.domain.models.buyer import Buyer
from src.domain.models.seller import Seller
from src.domain.exceptions.buyer import BuyerAlreadyExistsError
from src.domain.exceptions.seller import SellerAlreadyExistsError
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.infrastructure.utils.logs import app_log

(
    CHOOSING_ROLE,
    GET_NAME,
    GET_SURNAME,
    GET_PHONE,
    GET_EMAIL,
    GET_SELLER_WEBSITE
) = range(6)


# ==================== START ====================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Register as Buyer", "Register as Seller"]]
    await update.message.reply_text(
        "Welcome to Radar! 📡\nPlease choose your role to begin:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True, is_persistent=True
        ),
    )
    return CHOOSING_ROLE


# ==================== ROLE ====================

async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice not in ["Register as Buyer", "Register as Seller"]:
        await update.message.reply_text("⚠️ Please use the buttons to choose your role.")
        return CHOOSING_ROLE

    context.user_data["role"] = "buyer" if choice == "Register as Buyer" else "seller"
    await update.message.reply_text(
        "What is your First Name?", reply_markup=ReplyKeyboardRemove()
    )
    return GET_NAME


# ==================== NAME ====================

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name.isalpha():
        await update.message.reply_text("⚠️ Name must contain only letters. Please try again:")
        return GET_NAME

    context.user_data["name"] = name
    await update.message.reply_text("Great! Now, your Surname?")
    return GET_SURNAME


# ==================== SURNAME ====================

async def handle_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surname = update.message.text.strip()
    if not surname.isalpha():
        await update.message.reply_text("⚠️ Surname must contain only letters. Please try again:")
        return GET_SURNAME

    context.user_data["surname"] = surname

    # Phone must be shared via button only
    keyboard = [[KeyboardButton("📱 Share Phone Number", request_contact=True)]]
    await update.message.reply_text(
        "Please share your phone number:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True
        ),
    )
    return GET_PHONE


# ==================== PHONE ====================

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if not contact or contact.user_id != update.effective_user.id:
        await update.message.reply_text("⚠️ Please use the button to share YOUR phone number.")
        return GET_PHONE

    context.user_data["phone"] = contact.phone_number
    await update.message.reply_text(
        "What is your Email Address?", reply_markup=ReplyKeyboardRemove()
    )
    return GET_EMAIL


# ==================== EMAIL ====================

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text("⚠️ Invalid email format. Please try again:")
        return GET_EMAIL

    context.user_data["email"] = email
    role = context.user_data.get("role")
    if role == "seller":
        keyboard = [["⏭ Skip"]]
        await update.message.reply_text(
            "Do you have a website? Send the URL or press Skip:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard, resize_keyboard=True, one_time_keyboard=True, is_persistent=True
            ),
        )
        return GET_SELLER_WEBSITE

    return await _finish_buyer_registration(update, context)


# ==================== SELLER WEBSITE ====================

async def handle_seller_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text != "⏭ Skip" and not re.match(r"^https?://", text):
        await update.message.reply_text("⚠️ Please provide a valid URL or press Skip:")
        return GET_SELLER_WEBSITE

    context.user_data["website"] = None if text == "⏭ Skip" else text
    return await _finish_seller_registration(update, context)


# ==================== FINISH ====================

async def _finish_buyer_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        new_buyer = Buyer(
            details={
                "name": data["name"],
                "surname": data["surname"],
                "email": data["email"],
                "mobile_phone": data.get("phone"),
                "chat_id": chat_id,
                "telegram_handle": update.effective_user.username or "N/A",
            }
        )
        try:
            await buyer_service.create_buyer(new_buyer)
            await update.message.reply_text(
                "✅ Registration complete! What would you like to do today?",
                reply_markup=get_buyer_menu_keyboard()
            )
        except BuyerAlreadyExistsError:
            await update.message.reply_text(
                "Welcome back! Choose an option below:",
                reply_markup=get_buyer_menu_keyboard()
            )
        except Exception as e:
            app_log.error(f"Buyer registration error: {e}", exc_info=True)
            await update.message.reply_text("❌ Failed to save. Please contact support.")

    context.user_data.clear()
    return ConversationHandler.END


async def _finish_seller_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        seller_service = deps["seller_service"]
        new_seller = Seller(
            details={
                "name": data["name"],
                "email": data["email"],
                "mobile_phone": data.get("phone"),
                "chat_id": chat_id,
                "telegram_handle": update.effective_user.username or "N/A",
                "website": data.get("website"),
            }
        )
        try:
            await seller_service.create_seller(new_seller)
            await update.message.reply_text(
                "✅ Registration complete! What would you like to do today?",
                reply_markup=get_seller_menu_keyboard()
            )
        except SellerAlreadyExistsError:
            await update.message.reply_text(
                "Welcome back! Choose an option below:",
                reply_markup=get_seller_menu_keyboard()
            )
        except Exception as e:
            app_log.error(f"Seller registration error: {e}", exc_info=True)
            await update.message.reply_text("❌ Failed to save. Please contact support.")

    context.user_data.clear()
    return ConversationHandler.END


# ==================== HELPER FOR INVALID INPUT ====================

async def invalid_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Please use the buttons to choose your role.")
    return CHOOSING_ROLE  # Stay in same state

async def invalid_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Please use the button to share your phone.")
    return GET_PHONE

async def invalid_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Please provide a valid URL or press Skip.")
    return GET_SELLER_WEBSITE


# ==================== CONVERSATION HANDLER ====================

def get_registration_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_cmd)],
        states={
            CHOOSING_ROLE: [
                MessageHandler(
                    filters.Regex("^(Register as Buyer|Register as Seller)$"),
                    choose_role
                ),
                MessageHandler(filters.TEXT & ~filters.COMMAND, invalid_role),  # Fixed
            ],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            GET_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_surname)],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, handle_phone),
                MessageHandler(filters.TEXT & ~filters.CONTACT, invalid_phone),  # Fixed
            ],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
            GET_SELLER_WEBSITE: [
                MessageHandler(filters.Regex("^⏭ Skip$"), handle_seller_website),
                MessageHandler(filters.Regex("^https?://.+\\..+"), handle_seller_website),  # Better regex
                MessageHandler(filters.TEXT & ~filters.COMMAND, invalid_website),  # Fixed
            ],
        },
        fallbacks=[
            CommandHandler("cancel", lambda u, c: ConversationHandler.END)
        ],
        allow_reentry=True
    )