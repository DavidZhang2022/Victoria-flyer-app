from app.core.categories import CATEGORIES

def classify_product(raw_name: str) -> str:
    if not raw_name:
        return "Other"

    name = raw_name.lower()

    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in name:
                return category

    return "Other"
