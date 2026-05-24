from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from src.chatapp.keyboards.buyer_menu import get_buyer_menu_keyboard
from src.chatapp.keyboards.seller_menu import get_seller_menu_keyboard
from src.chatapp.dependency_injection.dependency_injection import get_bot_deps
from src.domain.config.support import format_support_text


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show appropriate help based on current role"""
    chat_id = str(update.effective_user.id)
    
    # Check stored current role first
    current_role = context.user_data.get("current_role")
    
    if current_role == "buyer":
        await show_buyer_help(update, context)
        return
    elif current_role == "seller":
        await show_seller_help(update, context)
        return
    
    # Fallback: check database if no role stored yet
    async with get_bot_deps() as deps:
        buyer_service = deps["buyer_service"]
        seller_service = deps["seller_service"]
        
        buyer = await buyer_service.get_buyer_by_chat_id(chat_id)
        seller = await seller_service.get_seller_by_chat_id(chat_id)
    
    if buyer and not seller:
        context.user_data["current_role"] = "buyer"
        await show_buyer_help(update, context)
    elif seller and not buyer:
        context.user_data["current_role"] = "seller"
        await show_seller_help(update, context)
    elif buyer and seller:
        # Default to seller if both exist and no role stored
        context.user_data["current_role"] = "seller"
        await show_seller_help(update, context)
    else:
        await update.message.reply_text("⚠️ Please register first. Use /start.")


async def show_buyer_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
📖 **How Radar Works for Buyers**

**Create Requests:**
Tell us what you're looking for — a car or a property. Set your criteria like price range, location, features, and more.

**Get Matched:**
When a seller lists something that matches your criteria, we'll notify you instantly.

**Contact Sellers:**
View match details and contact sellers directly via Telegram.

**Manage Requests:**
- Free plan: 3 active requests
- Premium plan: 10 active requests
- Delete old requests to add new ones

**Commands:**
🚗 Request a Car - Search for cars
🏠 Request Real Estate - Search for properties
📄 My Requests - Manage your requests
❓ Help - Show this message

**Tips:**
✓ Be specific with your criteria for better matches
✓ Check your matches regularly
✓ Contact sellers quickly - good deals go fast!

{format_support_text()}
"""

    await update.message.reply_text(
        help_text,
        reply_markup=get_buyer_menu_keyboard(),
    )


async def show_seller_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
📖 **How Radar Works for Sellers**

**List Your Cars & Properties:**
Post your cars or real estate with photos, price, details, and location. Buyers searching for matching listings get notified instantly.

**Get Matched Automatically:**
When your listing matches a buyer's search criteria, they receive a notification and can contact you directly.

**Manage Your Listings:**
- Free plan: 5 active listings
- Premium plan: 50 active listings
- Delete sold items anytime
- Update contact info in Settings

**How Buyers Contact You:**
Buyers see your Telegram handle and phone number when interested. They can message you directly via Telegram or call.

**Tips for Success:**
✓ Add clear photos (up to 10 per listing)
✓ Price competitively for your market
✓ Keep your contact info up to date
✓ Respond to buyer inquiries quickly
✓ Delete listings once sold or rented

**Commands:**
🚗 Post a Car - Add a car listing
🏠 Post Real Estate - Add a property listing
📋 My Listings - View and manage your listings
⚙️ Settings - Update phone/website
❓ Help - Show this message

{format_support_text()}
"""

    await update.message.reply_text(
        help_text,
        reply_markup=get_seller_menu_keyboard(),
    )
    
def get_help_handler():
    return MessageHandler(filters.Regex("^❓ Help$"), show_help)