import httpx
import json
from app.core.config import settings

class BricksetError(Exception):
    pass

class BricksetClient:

    def __init__(self):
        self.api_key = settings.brickset_api_key
        self._client = httpx.Client()
            
    def get_themes(self):
        return self._request("getThemes")

    def get_sets(self, theme=None, year=None, updated_since=None, page_number=1, page_size=500):

        params = {
            "theme": theme,
            "year": year,
            "updatedSince": updated_since,
            "pageNumber": page_number,
            "pageSize": page_size
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self._request("getSets", params=params)
    
    def _request(self, brickset_function, params=None):
        response = self._client.get(f"https://brickset.com/api/v3.asmx/{brickset_function}", params = {"apiKey": self.api_key,
         "userHash": "",
         "params": json.dumps(params or {})})

        data = response.json()

        if data["status"] == 'error':
            raise BricksetError(data["message"])
        
        return data
    
    def close(self):
        
        self._client.close()