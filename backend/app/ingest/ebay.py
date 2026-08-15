import httpx, logging
from app.core.config import settings
from datetime import datetime, timedelta, timezone

TOKEN_EXPIRY_MARGIN_SECONDS = 60
FILTER_DEFAULT = "buyingOptions:{AUCTION|FIXED_PRICE|BEST_OFFER}"
SORT_DEFAULT = "newlyListed"
CAP = 5000

logger = logging.getLogger(__name__)

class EbayError(Exception):
    pass

def next_quota_reset(now):

    current_reset_time = (now).replace(
    hour=7, minute=0, second=0, microsecond=0)

    if(now > current_reset_time):
        next_reset_time = (now + timedelta(days=1)).replace(
    hour=7, minute=0, second=0, microsecond=0)
        return next_reset_time
    else:
        return current_reset_time

class EbayClient:
    def __init__(self):

        self._client = httpx.Client()
        self.token = None
        self.token_expires_at = None
        self.count = 0
        self.count_expires_at = next_quota_reset(datetime.now(timezone.utc))

    def refresh_token(self):
        now = datetime.now(timezone.utc)
        if self.token and now < self.token_expires_at:
            return self.token
        else:
            response = self._client.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                auth=(settings.ebay_client_id, settings.ebay_client_secret),
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
            )

            if response.status_code != 200:
                raise EbayError(
                    f"token request failed: {response.status_code}, {response.text}"
                )

            data = response.json()

            self.token = data["access_token"]
            self.token_expires_at = now + timedelta(
                seconds=data["expires_in"] - TOKEN_EXPIRY_MARGIN_SECONDS
            )

            return self.token
        
    def search(self, query, sort=SORT_DEFAULT, filter=FILTER_DEFAULT, limit=200):
    
        params = {
            "q": query,
            "sort": sort,
            "filter": filter,
            "limit": limit,
        }
    
        return self._request(params=params)

    def _request(self, allow_retry=True, params=None):

        token = self.refresh_token()

        if self.count >= CAP:
            raise EbayError(f"API call manual cap reached.")

        response = self._client.get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            headers={
                "Authorization": f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            },
            params=params,
        )

        now = datetime.now(timezone.utc)

        if(now > self.count_expires_at):
            self.count = 0
            self.count_expires_at = self.next_quota_reset(now)

        self.count += 1

        if response.status_code == 401 and allow_retry:
            self.token = None
            return self._request(allow_retry=False, params=params)
        
        elif response.status_code == 429:
            raise EbayError(f"Rate limit reached: {response.status_code}, {response.text}")

        elif response.status_code != 200:
            raise EbayError(f"request failed: {response.status_code}, {response.text}")

        return response.json()

    def close(self):
        self._client.close()
