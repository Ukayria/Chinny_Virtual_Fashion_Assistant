import os
import random
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(file))
PRICE_FILE = os.path.join(BASE_DIR, "data", "Fabric_Price.csv")

price_df = pd.read_csv(PRICE_FILE)

# build lookup (normalize)
price_lookup = {}
for _, row in price_df.iterrows():
    fabric = str(row["Fabric"]).strip().lower()
    ftype = str(row[price_df.columns[1]]).strip().lower().replace(" ", "")
    price_value = row[price_df.columns[-1]]
    try:
        price_value = int(price_value)
    except Exception:
        try:
            price_value = int(float(price_value))
        except Exception:
            price_value = None
    price_lookup[(fabric, ftype)] = price_value

def _normalize_type(t):
    if not t:
        return ""
    return t.strip().lower().replace(" ", "")

def get_price(fabric_list):
    total = 0
    details = []
    for fabric_item in fabric_list:
        parts = [p.strip() for p in fabric_item.split(",")]
        fab = parts[0].lower()
        typ = parts[1].lower() if len(parts) > 1 else ""
        key = (fab, _normalize_type(typ))
        price = price_lookup.get(key)
        if price is None:
            # fallback to fabric-only if single match exists
            matches = [v for (f, t), v in price_lookup.items() if f == fab and v is not None]
            price = matches[0] if len(matches) == 1 else None

        if price is not None:
            total += int(price)
            details.append(f"{parts[0]} ({parts[1] if len(parts)>1 else 'N/A'}) = ₦{int(price)} per yard")
        else:
            details.append(f"{parts[0]} ({parts[1] if len(parts)>1 else 'N/A'}) = Price Missing")
    return total, details

def prettify_name(filename):
    name = os.path.splitext(filename)[0]
    name = name.replace("_", " ").replace("-", " ").title()
    return name

def recommend_styles(body_shape, preference=None):
    base_folder = os.path.join("static", "styles")

    shape_mapping = {
        "Hourglass": "Wedding_occasion",
        "Pear": "Casual",
        "Rectangle": "Corporate_Office_wears",
        "Inverted Triangle": "Casual"
    }

    pref = (preference or "").strip().lower()
    if pref == "traditional":
        category_folder = "Wedding_occasion"
    elif pref == "casual":
        category_folder = "Casual"
    elif pref == "office":
        category_folder = "Corporate_Office_wears"
    else:
        category_folder = shape_mapping.get(body_shape, "Casual")

    folder_path = os.path.join(base_folder, category_folder)
    if not os.path.isdir(folder_path):
        # fallback gracefully
        category_folder = "Casual"
        folder_path = os.path.join(base_folder, category_folder)

    images = [f for f in os.listdir(folder_path) if not f.startswith(".")]
    if not images:
        return category_folder, []

    selected = random.sample(images, min(3, len(images)))

    fabric_map = {
        "Casual": {
            "casual_1": ["Crepe, Thick"],
            "casual_2": ["Crepe, Light"],
            "casual_3": ["Adire, High grade"],
            "casual_4": ["Adire, High grade"],
            "casual_5": ["Adire, High grade"],
            "casual_6": ["Crepe, Thick"],
            "casual_7": ["Crepe, Light"]
        },
        "Corporate_Office_wears": {
            "office_1": ["Crepe, Thick"],
            "office_2": ["Crepe, Thick"],
            "office_3": ["Crepe, Thick"],
            "office_4": ["Crepe, Thick"],
            "office_5": ["Crepe, Thick"],
            "office_6": ["Tweed, Thick"],
            "office_7": ["Crepe, Thick"]
        },
        "Wedding_occasion": {
            "occasion_1": ["Lace, Sample"],
            "occasion_2": ["Ankara, Low grade", "Crepe, Thick"],
            "occasion_3": ["Ankara, High grade"],
            "occasion_4": ["Lace, Beaded(mid)"],
            "occasion_5": ["Lace, Beaded(luxury)", "Crepe, Thick"],
            "occasion_6": ["Ankara, High grade"],
            "occasion_7": ["Lace, Beaded(luxury)"]
        }
    }

    results = []
    for img in selected:
        key_base = os.path.splitext(img)[0].lower().replace(" ", "").replace("-", "_")
        fabrics = fabric_map.get(category_folder, {}).get(key_base, ["Unknown, Unknown"])
        total_price, detail_list = get_price(fabrics)

        results.append({
            "image": os.path.join("static", "styles", category_folder, img).replace("\\", "/"),
            "name": prettify_name(img),
            "fabrics": fabrics,
            "price": int(total_price) if isinstance(total_price, (int, float)) else 0,
            "price_breakdown": detail_list
        })

    return category_folder, results

# add to bottom of recommend.py
from reward_model import score_texts as _score_texts

def score_recommendations(recs):
    """
    Accepts list of recommendation dicts (each with 'name' and 'fabrics' etc).
    If a trained reward model exists, scores and sorts recommendations.
    Otherwise returns recs unchanged.
    """
    if not recs:
        return recs

    texts = []
    for r in recs:
        # build a short text representation for ranking
        name = r.get("name", "")
        fabrics = ", ".join(r.get("fabrics", []))
        texts.append(f"{name} {fabrics}")

    scores = _score_texts(texts)
    if scores is None:
        return recs

    for r, s in zip(recs, scores):
        r["score"] = float(round(s, 3))
    recs.sort(key=lambda x: x.get("score", 0), reverse=True)
    return recs

