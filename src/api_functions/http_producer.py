# src/api_functions/http_producer.py
import logging
import requests
from typing import Dict, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

def post_visitor_feed(
    base_url: str,
    apikey: str,
    body: Dict[str, Any],
    timeout: float = 5.0,
) -> bool:
    """
    POST {base_url}/location-api/visitor/feed with JSON body and 'apikey' header.
    Returns True if 2xx.
    """
    if not base_url:
        logger.error("BASE_URL missing")
        return False
    if not apikey:
        logger.error("API_KEY missing")
        return False

    url = urljoin(base_url + "/", "location-api/visitor/feed")
    headers = {
        "Content-Type": "application/json",
        "apikey": apikey,
    }
    try:
        r = requests.post(url, json=body, headers=headers, timeout=timeout)
        if 200 <= r.status_code < 300:
            logger.info(f"[HTTP OK] {r.status_code}")
            return True
        logger.warning(f"[HTTP FAIL] {r.status_code} | {r.text[:500]}")
        return False
    except Exception as e:
        logger.exception(f"[HTTP EXC] {e}")
        return False
