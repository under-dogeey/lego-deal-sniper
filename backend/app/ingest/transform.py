from app.db.models import RawListing
from datetime import datetime, timezone
import copy

def to_datetime(value):
    if value is None:
        return None

    return datetime.fromisoformat(value)

def loop_images(data):
    
    images = []

    for image in data:
        images.append(image.get("imageUrl"))
    
    return images

def to_raw_listing(data: dict) -> RawListing:

  
    deep = copy.deepcopy(data)
    del deep["seller"]["username"]

    image_urls = [data["image"].get("imageUrl")] + loop_images(data.get("additionalImages", []))

    options = data.get("shippingOptions", [])

    if options:
        shipping_cost = options[0].get("shippingCost", {}).get("value")
    else:
        shipping_cost = None
            
    now = datetime.now(timezone.utc)

    return RawListing(
        source = 'ebay',
        source_listing_id = data["itemId"],
        title = data["title"],
        price = data.get("price", {}).get("value"),
        currency = data.get("price", {}).get("currency"),
        shipping_cost = shipping_cost,
        condition = data["condition"],
        condition_id = data.get("conditionId"),
        buying_options = data["buyingOptions"],
        epid = data.get("epid"),
        leaf_category_id = data["leafCategoryIds"][0],
        item_web_url = data["itemWebUrl"],
        image_urls = image_urls,
        seller_feedback_score = data["seller"].get("feedbackScore"),
        seller_feedback_percentage = data["seller"].get("feedbackPercentage"),
        item_creation_date = to_datetime(data["itemCreationDate"]),
        item_origin_date = to_datetime(data["itemOriginDate"]),
        bid_count = data.get("bidCount"),
        current_bid_price = data.get("currentBidPrice", {}).get("value"),
        item_end_date = to_datetime(data.get("itemEndDate")),
        is_pickup_only = "shippingOptions" not in data,
        distance_miles = data.get("distanceFromPickupLocation", {}).get("value"),
        first_seen = now,
        last_seen = now,
        ended_at = None,
        alerted_at = None,
        raw_json = deep
    )

#{
#  "itemId": "v1|398238964712|0",
#  "title": "LEGO 75930 - Jurassic World: Indoraptor Rampage at Lockwood Estate ",
#  "leafCategoryIds": ["19006"],
 # "categories": [
#    {"categoryId": "19006",  "categoryName": "LEGO (R) Complete Sets & Packs"},
#    {"categoryId": "220",    "categoryName": "Toys & Hobbies"},
#    {"categoryId": "183446", "categoryName": "Building Toys"},
#    {"categoryId": "183447", "categoryName": "LEGO (R) Building Toys"}
#  ],
#  "image":           {"imageUrl": "https://i.ebayimg.com/images/g/2eQAAeSwEIpqUXD4/s-l225.jpg"},
#  "thumbnailImages": [{"imageUrl": "https://i.ebayimg.com/images/g/2eQAAeSwEIpqUXD4/s-l1600.jpg"}],
#  "additionalImages": [ {"imageUrl": "…s-l225.jpg"}, …21 total… ],
#  "price":          {"value": "129.99", "currency": "USD"},
#  "currentBidPrice":{"value":  "99.99", "currency": "USD"},
#  "bidCount": 0,
#  "buyingOptions": ["FIXED_PRICE", "AUCTION"],
#  "condition": "Used",
#  "conditionId": "3000",
#  "shippingOptions": [
#    {
#      "shippingCostType": "FIXED",
#      "shippingCost": {"value": "14.99", "currency": "USD"},
#      "minEstimatedDeliveryDate": "2026-08-11T07:00:00.000Z",
#      "maxEstimatedDeliveryDate": "2026-08-14T07:00:00.000Z"
#    }
#  ],
#  "seller": {"username": "quas1115", "feedbackPercentage": "100.0", "feedbackScore": 479},
#  "epid": "25053412376",
#  "itemLocation": {"postalCode": "992**", "country": "US"},
#  "itemWebUrl": "https://www.ebay.com/itm/398238964712?_skw=lego+estate&hash=…",
#  "itemHref": "https://api.ebay.com/buy/browse/v1/item/v1%7C398238964712%7C0",
#  "legacyItemId": "398238964712",
#  "itemOriginDate":   "2026-07-11T18:24:01.000Z",
#  "itemCreationDate": "2026-08-01T18:24:36.000Z",
#  "itemEndDate":      "2026-08-08T18:24:36.000Z",
#  "adultOnly": false,
#  "availableCoupons": false,
#  "topRatedBuyingExperience": false,
#  "priorityListing": false,
#  "listingMarketplaceId": "EBAY_US"
#}