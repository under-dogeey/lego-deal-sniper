import json
from pathlib import Path

def create_fixtures():
    data_dir = Path("C:/Users/Robert Trinh/legodealsniper/backend/data")
    file_path = data_dir / "positive" / "unsorted_lego_20260815_161612.json"
    out_path = Path(__file__).parent / "skeletons.jsonl"  

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    fixtures = []
            
    for item in data["itemSummaries"]:

        obj = {"id": item["itemId"], "source": "ebay", "title": item["title"], "description_snippet": None, "structured_fields": {"category_id": item["leafCategoryIds"][0]}, "expected": {"outcome": "", "set_numbers": []}, "notes": ""}

        epid = item.get("epid") 
        if epid is not None:
            obj["structured_fields"]["epid"] = epid

        condition = item.get("condition") 
        if condition is not None:
            obj["structured_fields"]["condition"] = condition

        price = item.get("price", {}).get("value")
        if price is not None:
            obj["structured_fields"]["price"] = price

        fixtures.append(obj) 

    with open(out_path, "w", encoding="utf-8") as file:
        for fixture in fixtures:
            file.write(json.dumps(fixture, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    create_fixtures()