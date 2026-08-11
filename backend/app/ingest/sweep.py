from app.ingest.ebay import EbayClient
from app.ingest.corpus import save_response

NEGATIVE_SIGNALS = {
    "weight_language": ["lego pounds", "lego lbs", "bulk lego"],
    "amateur_vocabulary": ["legos lot", "mixed legos", "assorted legos"],
    "unsorted_admission": ["lego random", "lego mixed lot", "lego junk drawer", "unsorted lego"],
    "liquidation_context": ["lego estate"]
}

def run_sweep(client, query_strings=NEGATIVE_SIGNALS):

    for queries in query_strings.values():
        for query in queries:
            result = client.search(query)
            save_response(query, result)
            print(f"{query}: {result['total']}")

if __name__ == "__main__":

    client = EbayClient()

    run_sweep(client)

    client.close()
