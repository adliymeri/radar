from telegram import ReplyKeyboardMarkup

def get_buyer_menu_keyboard(is_paused: bool = False):
    matching_button = "▶️ Resume Matching" if is_paused else "⏸ Pause Matching"

    keyboard = [
        ["🚗 Request a Car", "🏠 Request Real Estate"],
        ["📄 My Requests", matching_button],
        ["❓ Help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)