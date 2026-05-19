from uuid import UUID
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters
from src.domain.config.limits import get_max_requests_for_buyer
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.infrastructure.utils.logs import app_log


MATCHES_PER_PAGE = 20

def get_delete_label(request) -> str:
    d = request.details
    if request.type == "car":
        return f"❌ Delete {d.get('make', '')} {d.get('model', '')}"
    elif request.type == "real_estate":
        types = ", ".join(d.get("property_type", []))
        return f"❌ Delete {types} in {d.get('city', '')}"
    return "❌ Delete Request"

def format_request_line(request, index: int, match_count: int = 0) -> str:
    d = request.details
    match_indicator = f" ({match_count} matches)" if match_count > 0 else ""

    if request.type == "car":
        year_range = f"{d.get('year_min', 'N/A')} — {d.get('year_max', 'N/A')}"
        return (
            f"{index}️⃣ 🚗 {d.get('make', 'N/A')} {d.get('model', 'N/A')} "
            f"— {year_range}{match_indicator}"
        )
    elif request.type == "real_estate":
        price_range = f"€{d.get('min_price', 0):,.0f} — €{d.get('max_price', 0):,.0f}"
        property_types = ", ".join(d.get("property_type", ["N/A"]))
        city = d.get("city", "N/A")
        return (
            f"{index}️⃣ 🏠 {property_types} in {city} "
            f"— {price_range}{match_indicator}"
        )
    else:
        return f"{index}️⃣ Unknown request type{match_indicator}"


# ================= SHOW REQUESTS =================

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]
        matching_service = deps["matching_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        if not buyer:
            await update.message.reply_text("⚠️ You need to register first. Use /start.")
            return

        requests = await request_service.get_requests_by_buyer(buyer.id)
        
        # NEW: Get max requests for this buyer
        max_requests = get_max_requests_for_buyer(buyer.payment)

    if not requests:
        await update.message.reply_text(
            f"📄 You have no active requests (0/{max_requests}).",
            reply_markup=get_buyer_menu_keyboard(),
        )
        return

    # Get match counts for each request
    match_counts = {}
    async with get_bot_deps() as deps:
        matching_service = deps["matching_service"]
        for r in requests:
            count = await matching_service.count_matches_by_request(r.id)
            match_counts[str(r.id)] = count

    # Build message text - CHANGED: Show request count with limit
    lines = [f"📄 Your Requests ({len(requests)}/{max_requests}):\n"]
    for i, r in enumerate(requests):
        lines.append(format_request_line(r, i + 1, match_counts[str(r.id)]))

    # Build inline buttons - two buttons per request if there are matches
    keyboard = []
    for r in requests:
        d = r.details
        row = []
        
        # Delete button
        row.append(InlineKeyboardButton(
            get_delete_label(r),
            callback_data=f"delete_request:{r.id}"
        ))
        
        # Show Matches button (only if matches exist)
        count = match_counts[str(r.id)]
        if count > 0:
            row.append(InlineKeyboardButton(
                f"📨 Show Matches ({count})",
                callback_data=f"show_matches:{r.id}:0"
            ))
        
        keyboard.append(row)

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
# ================= DELETE REQUEST =================

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
            matching_service = deps["matching_service"]

            buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
            requests = await request_service.get_requests_by_buyer(buyer.id)
            
            # NEW: Get max requests
            max_requests = get_max_requests_for_buyer(buyer.payment)

        if not requests:
            await query.message.reply_text(
                f"📄 You have no more active requests (0/{max_requests}).",
                reply_markup=get_buyer_menu_keyboard(),
            )
            return

        # Get match counts
        match_counts = {}
        async with get_bot_deps() as deps:
            matching_service = deps["matching_service"]
            for r in requests:
                count = await matching_service.count_matches_by_request(r.id)
                match_counts[str(r.id)] = count

        # Rebuild the list - CHANGED: Show updated count
        lines = [f"📄 Your Requests ({len(requests)}/{max_requests}):\n"]
        for i, r in enumerate(requests):
            lines.append(format_request_line(r, i + 1, match_counts[str(r.id)]))

        keyboard = []
        for r in requests:
            d = r.details
            row = []
            row.append(InlineKeyboardButton(
                get_delete_label(r),
                callback_data=f"delete_request:{r.id}"
            ))
            count = match_counts[str(r.id)]
            if count > 0:
                row.append(InlineKeyboardButton(
                    f"📨 Show Matches ({count})",
                    callback_data=f"show_matches:{r.id}:0"
                ))
            keyboard.append(row)

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


# ================= SHOW MATCHES FOR REQUEST =================

async def handle_show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    request_id = UUID(parts[1])
    offset = int(parts[2])

    async with get_bot_deps() as deps:
        request_service = deps["buyer_request_service"]
        matching_service = deps["matching_service"]
        listing_service = deps["listing_service"]
        car_listing_service = deps["car_listing_service"]

        # Get request details
        buyer_request = await request_service.get_request_by_id(request_id)
        if not buyer_request:
            await query.edit_message_text("⚠️ Request not found.")
            return

        # Get total count and matches
        total_count = await matching_service.count_matches_by_request(request_id)
        matches = await matching_service.get_matches_by_request(
            request_id, 
            limit=MATCHES_PER_PAGE, 
            offset=offset
        )

    if not matches:
        await query.edit_message_text("No matches found for this request.")
        return

    # Build message
    d = buyer_request.details
    lines = [
        f"📨 Matches for: {d.get('make')} {d.get('model')} ({d.get('year_min')}-{d.get('year_max')})\n",
        f"Found {total_count} match(es):\n"
    ]

    # Fetch car listing details for all matches
    keyboard = []
    for i, match in enumerate(matches):
        async with get_bot_deps() as deps:
            car_listing_service = deps["car_listing_service"]
            car_listing = await car_listing_service.get_car_listing_by_id(match.listing_id)

        if not car_listing:
            continue

        # Build match summary
        status_icon = "✅" if match.status == "contacted" else "🔔"
        lines.append(
            f"{status_icon} {car_listing.make} {car_listing.model} ({car_listing.year}) — €{car_listing.price:,.0f}\n"
            f"   📍 {car_listing.location or 'N/A'} | {car_listing.mileage:,} km | {car_listing.transmission}"
        )

        # Add view button
        keyboard.append([InlineKeyboardButton(
            f"👁 View Match #{offset + i + 1}",
            callback_data=f"view_match:{match.id}"
        )])

    # Add pagination if needed
    pagination_row = []
    if offset > 0:
        pagination_row.append(InlineKeyboardButton(
            "⬅️ Previous",
            callback_data=f"show_matches:{request_id}:{offset - MATCHES_PER_PAGE}"
        ))
    if offset + MATCHES_PER_PAGE < total_count:
        pagination_row.append(InlineKeyboardButton(
            "➡️ Next",
            callback_data=f"show_matches:{request_id}:{offset + MATCHES_PER_PAGE}"
        ))
    if pagination_row:
        keyboard.append(pagination_row)

    # Back button
    keyboard.append([InlineKeyboardButton("🔙 Back to Requests", callback_data="back_to_requests")])

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ================= VIEW SINGLE MATCH DETAILS =================

async def handle_view_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match_id = UUID(query.data.split(":")[1])

    async with get_bot_deps() as deps:
        matching_service = deps["matching_service"]
        car_listing_service = deps["car_listing_service"]
        seller_service = deps["seller_service"]

        match = await matching_service.get_match_by_id(match_id)
        if not match:
            await query.edit_message_text("⚠️ Match not found.")
            return

        car_listing = await car_listing_service.get_car_listing_by_id(match.listing_id)
        seller = await seller_service.get_seller_by_id(match.seller_id)

    if not car_listing or not seller:
        await query.edit_message_text("⚠️ Listing details not available.")
        return

    # Build detailed message
    message_lines = [
        f"🚗 {car_listing.make} {car_listing.model} ({car_listing.year})",
        f"💶 €{car_listing.price:,.0f}",
        f"🛣 {car_listing.mileage:,} km",
        f"📍 {car_listing.location or 'Location not specified'}",
        f"⚙️ {car_listing.transmission} | {car_listing.fuel_type} | {car_listing.drivetrain}",
    ]

    if car_listing.description:
        desc = car_listing.description[:200] + "..." if len(car_listing.description) > 200 else car_listing.description
        message_lines.append(f"\n📝 {desc}")

    # If already contacted, show seller details directly
    if match.status == "contacted":
        seller_handle = seller.details.get("telegram_handle", "N/A")
        seller_phone = seller.details.get("mobile_phone", "Not shared")
        message_lines.extend([
            "\n✅ Seller Contact Information:",
            f"📱 Telegram: @{seller_handle}",
            f"📞 Phone: {seller_phone}"
        ])

    message = "\n".join(message_lines)

    # Build keyboard
    keyboard = []
    if match.status != "contacted":
        keyboard.append([InlineKeyboardButton("📞 Contact Seller", callback_data=f"contact_seller:{match_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Matches", callback_data=f"show_matches:{match.request_id}:0")])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    # Send photos if available (separate message because Telegram doesn't support photos + inline keyboard)
    if car_listing.photos and len(car_listing.photos) > 0:
        try:
            if len(car_listing.photos) == 1:
                # Single photo
                await query.message.reply_photo(photo=car_listing.photos[0])
            else:
                # Multiple photos - use media group (max 10)
                media_group = [InputMediaPhoto(media=photo_id) for photo_id in car_listing.photos[:10]]
                await query.message.reply_media_group(media=media_group)
        except Exception as e:
            app_log.error(f"Error sending photos: {e}")

# ================= CONTACT SELLER =================

async def handle_contact_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match_id = UUID(query.data.split(":")[1])

    async with get_bot_deps() as deps:
        matching_service = deps["matching_service"]
        seller_service = deps["seller_service"]
        car_listing_service = deps["car_listing_service"]

        # Mark as contacted
        await matching_service.mark_as_contacted(match_id)

        # Get details
        match = await matching_service.get_match_by_id(match_id)
        seller = await seller_service.get_seller_by_id(match.seller_id)
        car_listing = await car_listing_service.get_car_listing_by_id(match.listing_id)

    if not match or not seller or not car_listing:
        await query.edit_message_text("⚠️ Could not retrieve details.")
        return

    # Update message to show seller contact info
    seller_handle = seller.details.get("telegram_handle", "N/A")
    seller_phone = seller.details.get("mobile_phone", "Not shared")

    message_lines = [
        f"🚗 {car_listing.make} {car_listing.model} ({car_listing.year})",
        f"💶 €{car_listing.price:,.0f}",
        f"🛣 {car_listing.mileage:,} km",
        f"📍 {car_listing.location or 'Location not specified'}",
        f"⚙️ {car_listing.transmission} | {car_listing.fuel_type} | {car_listing.drivetrain}",
    ]

    if car_listing.description:
        desc = car_listing.description[:200] + "..." if len(car_listing.description) > 200 else car_listing.description
        message_lines.append(f"\n📝 {desc}")

    message_lines.extend([
        "\n✅ Seller Contact Information:",
        f"📱 Telegram: @{seller_handle}",
        f"📞 Phone: {seller_phone}",
        "\nFeel free to reach out directly!"
    ])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Matches", callback_data=f"show_matches:{match.request_id}:0")]
    ])

    await query.edit_message_text("\n".join(message_lines), reply_markup=keyboard)
    app_log.info(f"Match {match_id} marked as contacted")


# ================= BACK TO REQUESTS =================

# ================= BACK TO REQUESTS =================

async def handle_back_to_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Re-render the requests list
    chat_id = str(update.effective_user.id)

    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        request_service = deps["buyer_request_service"]
        matching_service = deps["matching_service"]

        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        requests = await request_service.get_requests_by_buyer(buyer.id)
        
        # NEW: Get max requests
        max_requests = get_max_requests_for_buyer(buyer.payment)

        # Get match counts
        match_counts = {}
        for r in requests:
            count = await matching_service.count_matches_by_request(r.id)
            match_counts[str(r.id)] = count

    # CHANGED: Show request count with limit
    lines = [f"📄 Your Requests ({len(requests)}/{max_requests}):\n"]
    for i, r in enumerate(requests):
        lines.append(format_request_line(r, i + 1, match_counts[str(r.id)]))

    keyboard = []
    for r in requests:
        d = r.details
        row = []
        row.append(InlineKeyboardButton(
            get_delete_label(r),
            callback_data=f"delete_request:{r.id}"
        ))
        count = match_counts[str(r.id)]
        if count > 0:
            row.append(InlineKeyboardButton(
                f"📨 Show Matches ({count})",
                callback_data=f"show_matches:{r.id}:0"
            ))
        keyboard.append(row)

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
# ================= HANDLER REGISTRATION =================

def get_buyer_profile_handler():
    return [
        MessageHandler(filters.Regex("^📄 My Requests$"), show_profile),
        CallbackQueryHandler(handle_delete_callback, pattern="^delete_request:"),
        CallbackQueryHandler(handle_confirm_delete, pattern="^confirm_delete:"),
        CallbackQueryHandler(handle_cancel_delete, pattern="^cancel_delete$"),
        CallbackQueryHandler(handle_show_matches, pattern="^show_matches:"),
        CallbackQueryHandler(handle_view_match, pattern="^view_match:"),
        CallbackQueryHandler(handle_contact_seller, pattern="^contact_seller:"),
        CallbackQueryHandler(handle_back_to_requests, pattern="^back_to_requests$"),
    ]