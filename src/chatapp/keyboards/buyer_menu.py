from telegram import ReplyKeyboardMarkup

def get_buyer_menu_keyboard(is_paused: bool = False):
    """
    Build buyer menu keyboard. The matching button is dynamic:
      - "⏸ Pause Matching" if matching is active
      - "▶️ Resume Matching" if all requests are paused
    """
    matching_button = "▶️ Resume Matching" if is_paused else "⏸ Pause Matching"

    keyboard = [
        ["🚗 Request a Car", "🏠 Request Real Estate"],
        ["👤 My Profile", matching_button],
        ["❓ Help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)