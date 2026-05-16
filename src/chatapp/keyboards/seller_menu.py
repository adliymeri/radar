from telegram import ReplyKeyboardMarkup

def get_seller_menu_keyboard():
    keyboard = [
        ["🚗 Post a Car"],
        ["📋 My Listings"],
        ["⚙️ Settings", "❓ Help"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)