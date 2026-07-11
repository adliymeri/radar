from telegram import ReplyKeyboardMarkup

def get_seller_menu_keyboard():
    keyboard = [
        ["🚗 Post a Car", "🏠 Post Real Estate"],
        ["📋 My Listings"],
        ["⚙️ Settings", "❓ Help"],
        ["🔄 Switch to Buyer"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)