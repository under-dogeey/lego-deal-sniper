import httpx, logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def send(listing) -> bool:

    ntfy_topic = settings.ntfy_topic

    if not ntfy_topic:
        logger.debug("ntfy send failed: invalid ntfy topic")
        return False
    
    ntfy_url = f"https://ntfy.sh/{ntfy_topic}"

    content =  f"{listing.title} — {listing.price} — {listing.item_web_url}" 
    
    timeout = httpx.Timeout(5.0)

    response = httpx.post(ntfy_url, content=content, timeout=timeout, headers={"Click": listing.item_web_url})

    if response.status_code == 200:
        return True
    else:
        logger.error(f"ntfy send failed: {response.status_code} {response.text}")
        return False
