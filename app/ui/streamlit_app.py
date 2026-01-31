from __future__ import annotations
import requests
import streamlit as st
import pandas as pd

API_BASE = st.secrets.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Victoria Flyer Compare", layout="wide")
st.title("Victoria Flyer Compare (Flyer Deals)")

q = st.text_input("Search product (e.g., milk, chicken, apple):", value="milk")

col1, col2, col3 = st.columns(3)
days = col1.slider("Lookback days", 3, 30, 14)
limit = col2.slider("Max results", 20, 500, 200)
sort_mode = col3.selectbox("Sort", ["Cheapest unit price first", "Latest first"])


def to_professional_unit_price(unit_price, unit_price_label):
    """
    Convert internal unit price labels (e.g. $/100ml, $/100g) to professional ones ($/L, $/kg).
    Returns: (value_for_sort_and_display, label)
    """
    if unit_price is None:
        return None, ""

    try:
        v = float(unit_price)
    except Exception:
        return None, ""

    label = (unit_price_label or "").strip().lower()

    # $/100ml -> $/L
    if "/100ml" in label:
        return v * 10.0, "$/L"

    # $/100g -> $/kg
    if "/100g" in label:
        return v * 10.0, "$/kg"

    # already each or others
    if "/each" in label:
        return v, "$/each"

    # fallback: keep as is
    return v, unit_price_label or ""


if st.button("Search"):
    r = requests.get(
        f"{API_BASE}/offers/search",
        params={"q": q, "days": days, "limit": limit},
        timeout=30
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        st.warning("No results.")
        st.stop()

    df = pd.DataFrame(data)

    # --- NEW: professional unit price / label ---
    converted = df.apply(
        lambda row: to_professional_unit_price(row.get("unit_price"), row.get("unit_price_label")),
        axis=1
    )
    df["unit_price_pro"] = [x[0] for x in converted]
    df["unit_label_pro"] = [x[1] for x in converted]

    # round for nicer display
    df["unit_price_pro"] = df["unit_price_pro"].map(lambda x: None if x is None else round(float(x), 2))

    # --- sorting ---
    if sort_mode == "Cheapest unit price first":
        # put items without unit price (or not comparable) at the end
        df["unit_price_sort"] = df["unit_price_pro"].fillna(10**9)
        df = df.sort_values(["unit_price_sort", "price"], ascending=[True, True])
    else:
        df = df.sort_values(["fetched_at_utc"], ascending=[False])

    # --- columns to show ---
    show_cols = [
        "raw_name", "store_query", "merchant_name",
        "raw_price_text", "raw_quantity",
        "price",
        "unit_price_pro", "unit_label_pro",          # ✅ show professional unit price
        "raw_valid_from", "raw_valid_to",
        "image_url", "product_key"
    ]

    # if some columns don't exist (depending on API), filter safely
    show_cols = [c for c in show_cols if c in df.columns]

    st.dataframe(df[show_cols], use_container_width=True)

st.caption("Tip: start the API with `uvicorn app.api.main:app --reload`")
