import os


def get_support_info() -> dict:
    """Get support contact information from environment variables"""
    return {
        "email": os.getenv("SUPPORT_EMAIL", "support@example.com"),
        "phone": os.getenv("SUPPORT_PHONE", "+355 69 000 0000"),
        "telegram": os.getenv("SUPPORT_TELEGRAM", "@YourChannel"),
    }


def format_support_text() -> str:
    """Format support contact info for display"""
    support = get_support_info()
    return f"""
Need Help?
📧 Email: {support['email']}
📱 Phone: {support['phone']}
💬 Telegram: {support['telegram']}
"""