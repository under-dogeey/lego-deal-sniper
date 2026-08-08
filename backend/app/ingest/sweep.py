from app.ingest.ebay import EbayClient
from app.ingest.corpus import save_response

client = EbayClient()

query_strings = {
    "weight_language": ["lego pounds", "lego lbs", "bulk lego"],
    "amateur_vocabulary": ["legos lot", "mixed legos", "assorted legos"],
    "unsorted_admission": ["lego random", "lego mixed lot", "lego junk drawer", "unsorted lego"],
    "liquidation_context": ["lego estate"]
}

for group, queries in query_strings.items():
    for query in queries:
        result = client.search(query)
        save_response(query, result)
        print(f"{query}: {result['total']}")



client.close()
