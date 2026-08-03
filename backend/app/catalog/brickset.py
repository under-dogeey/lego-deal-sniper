import httpx
import json
import math
from app.core.config import settings

class BricksetError(Exception):
    pass

class BricksetClient:

    def __init__(self):
        self.api_key = settings.brickset_api_key
        self._client = httpx.Client()
            
    def get_themes(self):
        return self._request("getThemes")
    
    def get_years(self, theme=""):

        params = {
            "theme": theme
        }


        return self._request("getYears", params=params)

    def get_sets(self, theme=None, year=None, updated_since=None, page_size=500):

        first = self._fetch_page(1, theme=theme, year=year, updated_since=updated_since, page_size=page_size)

        all_sets = list(first["sets"])

        pages = math.ceil(first["matches"] / page_size)

        for page in range(2, pages + 1):

            all_sets.extend(self._fetch_page(page, theme=theme, year=year, updated_since=updated_since, page_size=page_size)["sets"]) 


        return all_sets
    
    def _request(self, brickset_function, params=None):

        query = {"apiKey": self.api_key}   
        if params:
            query.update(params)     

        response = self._client.get(f"https://brickset.com/api/v3.asmx/{brickset_function}", params = query)

        data = response.json()

        if data["status"] == 'error':
            raise BricksetError(data["message"])
        
        
        return data
    
    def _fetch_page(self, page_number, theme=None, year=None, updated_since=None, page_size=500):
        search = {
            "theme": theme,
            "year": year,
            "updatedSince": updated_since,
            "pageNumber": page_number,
            "pageSize": page_size,
            }
        
        search = {k: v for k, v in search.items() if v is not None}

        params = {
            "userHash": "",
            "params": json.dumps(search)

        }

        return self._request("getSets", params=params)
    
    def close(self):
        
        self._client.close()