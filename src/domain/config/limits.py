import os
from typing import Dict


def get_request_limits() -> Dict[str, int]:
    """Get request limits from environment variables"""
    return {
        "free": int(os.getenv("MAX_REQUESTS_FREE", "3")),
        "basic": int(os.getenv("MAX_REQUESTS_BASIC", "5")),
        "premium": int(os.getenv("MAX_REQUESTS_PREMIUM", "10")),
        "enterprise": int(os.getenv("MAX_REQUESTS_ENTERPRISE", "999")),
    }


DEFAULT_PLAN = "free"


def get_max_requests_for_buyer(payment_info: dict) -> int:
    """
    Get max requests for a buyer based on their payment plan.
    Defaults to 'free' plan if no payment info exists.
    
    Args:
        payment_info: Buyer's payment JSONB field (dict)
        
    Returns:
        Maximum number of active requests allowed
    """
    limits = get_request_limits()
    
    
    if not payment_info:
        return limits[DEFAULT_PLAN]
    
    plan = payment_info.get("plan", DEFAULT_PLAN)
    
    return limits.get(plan, limits[DEFAULT_PLAN])

def get_listing_limits() -> Dict[str, int]:
    """Get listing limits from environment variables"""
    return {
        "free": int(os.getenv("MAX_LISTINGS_FREE", "5")),
        "basic": int(os.getenv("MAX_LISTINGS_BASIC", "15")),
        "premium": int(os.getenv("MAX_LISTINGS_PREMIUM", "50")),
        "enterprise": int(os.getenv("MAX_LISTINGS_ENTERPRISE", "999")),
    }


def get_max_listings_for_seller(payment_info: dict) -> int:
    """Get max listings for a seller based on their payment plan."""
    limits = get_listing_limits()

    if not payment_info:
        return limits[DEFAULT_PLAN]

    plan = payment_info.get("plan", DEFAULT_PLAN)
    return limits.get(plan, limits[DEFAULT_PLAN])