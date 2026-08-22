import httpx, logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def send(listing) -> bool:
    
    content = f"{listing.title} — {listing.price} — {listing.item_web_url}"

    return send_message(content)
    

def send_message(text):

    discord_web_url = settings.discord_webhook_url

    if not discord_web_url:
        logger.debug("discord send failed: invalid discord web url")
        return False
    
    timeout = httpx.Timeout(5.0)
    
    response = httpx.post(discord_web_url, json={"content": text}, timeout=timeout)

    if response.status_code == 204:
        return True
    else:
        logger.error(f"discord send failed: {response.status_code} {response.text}")
        return False