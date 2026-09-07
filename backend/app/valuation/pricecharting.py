import httpx, logging, json
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://www.pricecharting.com"
CSV_PATH = "/" #unverified until subscribed to pricecharting

def download_csv(today, target_dir):

    token = settings.pricecharting_token

    if not token:
        logger.debug("no token found")
        return None
    
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / f"{today}.csv"
    url = BASE_URL + CSV_PATH

    response = httpx.get(url=url, params={"t": token}, timeout=httpx.Timeout(60.0))

    response.raise_for_status()

    file_path.write_bytes(response.content)

    return file_path
        
