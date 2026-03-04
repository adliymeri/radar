from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.infrastructure.utils.logs import app_log


async def pause_matching(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        if not buyer:
            await update.message.reply_text("⚠️ You need to register first.")
            return

        # Pause all active requests
        requests = await request_service.get_requests_by_buyer(buyer.id)
        for request in requests:
            if request.status == "active":
                request.status = "paused"
                await request_service.update_request(request)

        # Detect overall paused status
        paused = await is_matching_paused(request_service, buyer.id)

        await update.message.reply_text(
            "⏸ Matching paused. You won't receive new match notifications.",
            reply_markup=get_buyer_menu_keyboard(is_paused=paused),
        )


async def resume_matching(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        if not buyer:
            await update.message.reply_text("⚠️ You need to register first.")
            return

        # Resume all paused requests
        requests = await request_service.get_requests_by_buyer(buyer.id)
        for request in requests:
            if request.status == "paused":
                request.status = "active"
                await request_service.update_request(request)

        # Detect overall paused status
        paused = await is_matching_paused(request_service, buyer.id)

        await update.message.reply_text(
            "▶️ Matching resumed. You'll receive new match notifications.",
            reply_markup=get_buyer_menu_keyboard(is_paused=paused),
        )


def get_pause_resume_handlers():
    return [
        MessageHandler(filters.Regex("^⏸ Pause Matching$"), pause_matching),
        MessageHandler(filters.Regex("^▶️ Resume Matching$"), resume_matching),
    ]

async def is_matching_paused(request_service, buyer_id: str) -> bool:
    requests = await request_service.get_requests_by_buyer(buyer_id)
    if not requests:
        return False  # No requests, treat as not paused
    # Return True if all requests are paused
    return all(r.status == "paused" for r in requests)