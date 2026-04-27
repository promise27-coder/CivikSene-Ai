import re
from collections import Counter


CATEGORY_TERMS = {
    "Roads": {
        "road": 3,
        "roads": 3,
        "pothole": 4,
        "potholes": 4,
        "street": 2,
        "bridge": 3,
        "footpath": 3,
        "sidewalk": 3,
        "crack": 2,
        "broken": 2,
        "damage": 2,
        "damaged": 2,
        "raste": 3,
        "rasta": 3,
    },
    "Sanitation": {
        "garbage": 4,
        "trash": 4,
        "waste": 3,
        "dirty": 2,
        "sewage": 4,
        "drainage": 4,
        "drain": 3,
        "gutter": 4,
        "overflow": 3,
        "overflowing": 3,
        "cleaning": 2,
        "kachra": 4,
        "gatar": 4,
    },
    "Electricity": {
        "electricity": 4,
        "power": 4,
        "light": 3,
        "lights": 3,
        "streetlight": 4,
        "streetlights": 4,
        "wire": 3,
        "wires": 3,
        "pole": 3,
        "outage": 4,
        "spark": 4,
        "transformer": 4,
        "bijli": 4,
    },
    "Water Supply": {
        "water": 4,
        "pipeline": 4,
        "pipe": 3,
        "leak": 3,
        "leakage": 4,
        "tap": 3,
        "supply": 2,
        "drinking": 3,
        "paani": 4,
        "pani": 4,
    },
    "Traffic": {
        "traffic": 4,
        "signal": 3,
        "parking": 3,
        "jam": 3,
        "vehicle": 2,
        "vehicles": 2,
        "congestion": 4,
        "zebra": 2,
    },
    "Public Safety": {
        "accident": 4,
        "danger": 3,
        "dangerous": 4,
        "fire": 4,
        "crime": 4,
        "injury": 4,
        "emergency": 4,
        "unsafe": 4,
    },
}

PHRASE_TERMS = {
    "street light": ("Electricity", 5),
    "street lights": ("Electricity", 5),
    "power cut": ("Electricity", 5),
    "open drain": ("Sanitation", 5),
    "garbage collection": ("Sanitation", 5),
    "water leakage": ("Water Supply", 5),
    "water supply": ("Water Supply", 5),
    "broken road": ("Roads", 5),
    "traffic signal": ("Traffic", 5),
}

HIGH_PRIORITY_TERMS = {
    "accident",
    "accidents",
    "blast",
    "burn",
    "burning",
    "collapse",
    "collapsed",
    "danger",
    "dangerous",
    "dead",
    "death",
    "emergency",
    "electrocution",
    "explosion",
    "fire",
    "flood",
    "flooding",
    "hazard",
    "hazardous",
    "injured",
    "injury",
    "shock",
    "spark",
    "sparking",
    "unsafe",
    "urgent",
}

HIGH_PRIORITY_PHRASES = {
    "building collapse",
    "electric shock",
    "fallen pole",
    "gas leak",
    "live wire",
    "major fire",
    "open manhole",
    "road accident",
    "severe waterlogging",
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", text)


def classify_complaint(description: str) -> str:
    normalized = _normalize_text(description or "")
    if not normalized:
        return "General"

    scores = {category: 0 for category in CATEGORY_TERMS}

    for phrase, (category, score) in PHRASE_TERMS.items():
        if phrase in normalized:
            scores[category] += score

    token_counts = Counter(_tokenize(normalized))
    for category, weighted_terms in CATEGORY_TERMS.items():
        for token, count in token_counts.items():
            scores[category] += weighted_terms.get(token, 0) * count

    best_category, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return "General"

    return best_category


def classify_priority(description: str) -> str:
    normalized = _normalize_text(description or "")
    if not normalized:
        return "Normal"

    for phrase in HIGH_PRIORITY_PHRASES:
        if phrase in normalized:
            return "High"

    tokens = set(_tokenize(normalized))
    if tokens.intersection(HIGH_PRIORITY_TERMS):
        return "High"

    return "Normal"
