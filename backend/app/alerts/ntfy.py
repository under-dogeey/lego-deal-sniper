import httpx, logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def send_message(text, click_url=None):

    ntfy_topic = settings.ntfy_topic

    if not ntfy_topic:
        logger.debug("ntfy send failed: invalid ntfy topic")
        return False
    
    ntfy_url = f"https://ntfy.sh/{ntfy_topic}"

    timeout = httpx.Timeout(5.0)

    if click_url is None:
        response = httpx.post(ntfy_url, content=text, timeout=timeout)
    else:
        response = httpx.post(ntfy_url, content=text, timeout=timeout, headers={"Click": click_url})

    if response.status_code == 200:
        return True
    else:
        logger.error(f"ntfy send failed: {response.status_code} {response.text}")
        return False