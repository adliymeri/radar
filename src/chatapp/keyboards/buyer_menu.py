from telegram import ReplyKeyboardMarkup

def get_buyer_menu_keyboard():
    keyboard = [
        ["🚗 Request a Car", "🏠 Request Real Estate"],
        ["👤 My Profile", "⏸ Pause Matching"],
        ["❓ Help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)