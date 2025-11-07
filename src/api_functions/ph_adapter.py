# src/api_functions/ph_adapter.py
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def _gender_map(g: Optional[str]) -> Optional[str]:
    """
    API expects 'man' or 'lady'. Return None if unknown.
    """
    if not g: return None
    g = g.strip().lower()
    if g in {"male", "m"}: return "male"
    if g in {"female", "f"}: return "female"
    return None

def build_single_or_multi_display_body(
    result: Dict[str, Any],
    *,
    device_type: str,
    events: List[str],
    company_name: str,
    display_ids: List[int],
    purchase_intent: str,
    visitor_segments: List[str],
) -> Dict[str, Any]:
    """
    Use when you want to target one or more specific displays with 'display_ids'.
    """
    # Age and gender come from face detection (our variables)
    age = result.get("age")  # int or None
    gender = _gender_map(result.get("gender"))

    # Build API payload with config values and hardcoded defaults
    body: Dict[str, Any] = {
        # From config
        "device_type": device_type or "",
        "events": events or ["sales"],
        "company_name": company_name or "",
        "purchase_intent": purchase_intent or "",
        "display_ids": display_ids,
        "visitor_segments": visitor_segments or [],
        
        # From face detection (our variables)
        "age": age if isinstance(age, int) and age > 0 else None,
        "gender": gender,  # "man" | "lady" | None
        
        # Hardcoded values
        "first_name": "",  # Not available from face detection
        "visitor_type_id": None,  # Not available
        "reason_for_visit_id": None,  # Not available
        "product_type": "Electronics",  # Hardcoded
        "plan_types": ["Premium"],  # Hardcoded
        "plan_values": ["$100"],  # Hardcoded
        "page_views": ["Product Page"],  # Hardcoded
        "purchase_history": ["High Value"],  # Hardcoded
        "product_holdings": ["$80 Postpay"],  # Hardcoded
        "source": "DISPLAY",  # Hardcoded
    }
    return body

def build_all_store_body(
    result: Dict[str, Any],
    *,
    device_type: str,
    events: List[str],
    company_name: str,
    store_uuid: str,
    store_uuid_type: str,
    purchase_intent: str,
    visitor_segments: List[str],
) -> Dict[str, Any]:
    """
    Use when you want the store's targeting to decide displays via 'uuid'/'uuid_type'.
    """
    # Age and gender come from face detection (our variables)
    age = result.get("age")
    gender = _gender_map(result.get("gender"))

    body: Dict[str, Any] = {
        # From config
        "device_type": device_type or "",
        "events": events or ["sales"],
        "company_name": company_name or "",
        "purchase_intent": purchase_intent or "",
        "uuid": store_uuid,          # e.g. "UST-001"
        "uuid_type": store_uuid_type, # e.g. "STORE_CODE"
        "visitor_segments": visitor_segments or [],
        
        # From face detection (our variables)
        "age": age if isinstance(age, int) else None,
        "gender": gender,
        
        # Hardcoded values
        "first_name": "",  # Not available from face detection
        "visitor_type_id": None,  # Not available
        "reason_for_visit_id": None,  # Not available
        "product_type": "Electronics",  # Hardcoded
        "plan_types": ["Premium"],  # Hardcoded
        "plan_values": ["$100"],  # Hardcoded
        "page_views": ["Product Page"],  # Hardcoded
        "purchase_history": ["High Value"],  # Hardcoded
        "product_holdings": ["$80 Postpay"],  # Hardcoded
        "source": "DISPLAY",  # Hardcoded
        # Note: NO display_ids here per the spec's "ALL Store Displays" shape
    }
    return body

def send_visitor_data_to_api(
    result: Dict[str, Any],
    *,
    base_url: str,
    apikey: str,
    device_type: str = "",
    events: List[str] = None,
    company_name: str = "",
    display_ids: List[int] = None,
    store_uuid: str = None,
    store_uuid_type: str = None,
    purchase_intent: str = "",
    visitor_segments: List[str] = None,
    use_all_store_displays: bool = False,
    timeout: float = 5.0,
) -> bool:
    """
    Send visitor detection data to the API.
    
    Args:
        result: Detection result from face processing
        base_url: API base URL
        apikey: API key for authentication
        device_type: Device type identifier
        events: List of events (defaults to ["sales"])
        company_name: Company name
        display_ids: List of display IDs for targeting specific displays
        store_uuid: Store UUID for all-store targeting
        store_uuid_type: Type of store UUID (e.g., "STORE_CODE")
        use_all_store_displays: If True, target all store displays instead of specific ones
        timeout: Request timeout in seconds
        
    Returns:
        bool: True if API call was successful, False otherwise
    """
    from .http_producer import post_visitor_feed
    
    if events is None:
        events = ["sales"]
    if visitor_segments is None:
        visitor_segments = []
    
    try:
        if use_all_store_displays and store_uuid and store_uuid_type:
            # Use all store displays approach
            body = build_all_store_body(
                result,
                device_type=device_type,
                events=events,
                company_name=company_name,
                store_uuid=store_uuid,
                store_uuid_type=store_uuid_type,
                purchase_intent=purchase_intent,
                visitor_segments=visitor_segments
            )
            logger.info(f"Sending visitor data to all store displays (UUID: {store_uuid})")
        elif display_ids:
            # Use specific display targeting
            body = build_single_or_multi_display_body(
                result,
                device_type=device_type,
                events=events,
                company_name=company_name,
                display_ids=display_ids,
                purchase_intent=purchase_intent,
                visitor_segments=visitor_segments
            )
            logger.info(f"Sending visitor data to specific displays: {display_ids}")
        else:
            logger.error("Either display_ids or store_uuid must be provided")
            return False
        
        # Send to API
        success = post_visitor_feed(
            base_url=base_url,
            apikey=apikey,
            body=body,
            timeout=timeout
        )
        
        if success:
            logger.info("Successfully sent visitor data to API")
        else:
            logger.warning("Failed to send visitor data to API")
            
        return success
        
    except Exception as e:
        logger.debug(f"Error sending visitor data to API: {e}")
        return False
