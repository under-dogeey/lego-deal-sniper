from app.db.models import LegoSet
from datetime import datetime

def clean(value) :
    return None if value in ("", "(Unnamed)", "{Not specified}") else value

def to_date(value):
    if value is None:
        return None

    return datetime.fromisoformat(value).date()

def to_lego_set(data: dict) -> LegoSet:
    return LegoSet(
        set_id = data["setID"],
        number = data["number"],
        number_variant = data["numberVariant"],
        name = data["name"],
        year = data["year"],
        theme = data["theme"],
        theme_group = clean(data.get("themeGroup")),
        subtheme = clean(data.get("subtheme")),
        category = clean(data.get("category")),
        released = data["released"],
        pieces = clean(data.get("pieces")),
        minifigs = clean(data.get("minifigs")),
        launch_date = to_date(data.get("launchDate")),
        exit_date = to_date(data.get("exitDate")),
        thumbnail_url = clean(data.get("image", {}).get("thumbnailURL")),
        image_url = clean(data.get("image", {}).get("imageURL")),
        owned_by = clean(data.get("collections", {}).get("ownedBy")),
        wanted_by = clean(data.get("collections", {}).get("wantedBy")),
        retail_price_us = clean(data.get("LEGOCom", {}).get("US", {}).get("retailPrice")),
        rating = clean(data.get("rating")),
        rating_count = clean(data.get("ratingCount")),
        weight_kg = clean(data.get("dimensions", {}).get("weight")),
        barcode_ean = clean(data.get("barcode", {}).get("EAN")),
        barcode_upc = clean(data.get("barcode", {}).get("UPC")),
        last_updated = datetime.fromisoformat(data["lastUpdated"])
    )

