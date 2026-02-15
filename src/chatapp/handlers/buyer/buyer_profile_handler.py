from uuid import UUID
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.infrastructure.utils.logs import app_log


def format_request_line(request, index: int) -> str:
    d = request.details
    colors = ", ".join(d.get("color", [])) if isinstance(d.get("color"), list) else d.get("color", "N/A")
    return (
        f"{index}️⃣ {d.get('make', 'N/A')} {d.get('model', 'N/A')} "
        f"— {d.get('year', 'N/A')} — {colors}"
    )


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        if not buyer:
            await update.message.reply_text(
                "⚠️ You need to register first. Use /start.",
            )
            return

        requests = await request_service.get_requests_by_buyer(buyer.id)

    if not requests:
        await update.message.reply_text(
            "📋 You have no active requests.",
            reply_markup=get_buyer_menu_keyboard(),
        )
        return

    # Build message text
    lines = ["📋 Your Car Requests:\n"]
    for i, r in enumerate(requests):
        lines.append(format_request_line(r, i + 1))

    # Build inline delete buttons
    keyboard = []
    for i, r in enumerate(requests):
        d = r.details
        label = f"❌ Delete {d.get('make', '')} {d.get('model', '')}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"delete_request:{r.id}")])

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    request_id = UUID(query.data.split(":")[1])

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete:{request_id}"),
            InlineKeyboardButton("❌ No, Keep", callback_data="cancel_delete"),
        ]
    ])

    await query.edit_message_text(
        "Are you sure you want to delete this request?",
        reply_markup=keyboard,
    )


async def handle_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    request_id = UUID(query.data.split(":")[1])

    try:
        async with get_bot_deps() as deps:
            request_service = deps["buyer_request_service"]
            await request_service.delete_requests([request_id])

        await query.edit_message_text("✅ Request deleted successfully.")

        # Refresh the profile view
        chat_id = str(update.effective_user.id)
        async with get_bot_deps() as deps:
            buyer_service = deps["buyer_service"]
            request_service = deps["buyer_request_service"]

            buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
            requests = await request_service.get_requests_by_buyer(buyer.id)

        if not requests:
            await query.message.reply_text(
                "📋 You have no more active requests.",
                reply_markup=get_buyer_menu_keyboard(),
            )
            return

        # Rebuild the list
        lines = ["📋 Your Car Requests:\n"]
        for i, r in enumerate(requests):
            lines.append(format_request_line(r, i + 1))

        keyboard = []
        for i, r in enumerate(requests):
            d = r.details
            label = f"❌ Delete {d.get('make', '')} {d.get('model', '')}"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"delete_request:{r.id}")])

        await query.message.reply_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        app_log.error(f"Error deleting request: {e}", exc_info=True)
        await query.edit_message_text("⚠️ Something went wrong. Please try again.")


async def handle_cancel_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()


def get_buyer_profile_handler():
    return [
        MessageHandler(filters.Regex("^👤 My Profile$"), show_profile),
        CallbackQueryHandler(handle_delete_callback, pattern="^delete_request:"),
        CallbackQueryHandler(handle_confirm_delete, pattern="^confirm_delete:"),
        CallbackQueryHandler(handle_cancel_delete, pattern="^cancel_delete$"),
    ]