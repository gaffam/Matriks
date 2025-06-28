"""Simple product recommendation based on project info."""
from typing import Dict

BRAND_RULES = [
    {"location": "bursa", "type": "fabrika", "brand": "X"},
    {"location": "urfa", "type": "avm", "brand": "Y"},
]

def recommend_brand(info: Dict[str, str]) -> str:
    loc = info.get("location", "").lower()
    typ = info.get("type", "").lower()
    for rule in BRAND_RULES:
        if rule["location"] in loc and rule["type"] in typ:
            return rule["brand"]
    # default brand
    return "X"
