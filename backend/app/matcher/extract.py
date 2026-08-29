import re

PATTERN = re.compile(r"\b(\d{3,7})(?:-(\d))?\b")
KILL_WORDS = ("pcs", "pieces", "pc", "bricks", "lb", "lbs", "kg") 

def extract_set_numbers(title) -> list[str]:

    set_numbers = []

    title = title.lower()

    for match in PATTERN.finditer(title):
        after = title[match.end():].strip()
        before = title[:match.start()].strip()

        if after.startswith(KILL_WORDS):
            continue

        if before.endswith("$"):
            continue

        set_numbers.append(match.group(1))

    return set_numbers