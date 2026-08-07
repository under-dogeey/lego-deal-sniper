import json
from datetime import datetime
from pathlib import Path

def save_response(label, data):

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    target_dir = Path("data")
    target_dir.mkdir(parents=True, exist_ok=True)

    mapping = str.maketrans({" ": "_", "\"":"_"})
    label = label.translate(mapping)

    with open(target_dir / f"{label}_{timestamp}.json", 'x') as file:
        json.dump(data, file, indent=2)