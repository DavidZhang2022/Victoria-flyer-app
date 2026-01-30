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

if st.button("Search"):
    r = requests.get(f"{API_BASE}/offers/search", params={"q": q, "days": days, "limit": limit}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        st.warning("No results.")
        st.stop()

    df = pd.DataFrame(data)

    if sort_mode == "Cheapest unit price first":
        df["unit_price_sort"] = df["unit_price"].fillna(10**9)
        df = df.sort_values(["unit_price_sort", "price"], ascending=[True, True])
    else:
        df = df.sort_values(["fetched_at_utc"], ascending=[False])

    show_cols = [
        "raw_name", "store_query", "merchant_name", "raw_price_text", "raw_quantity",
        "price", "unit_price", "unit_price_label",
        "raw_valid_from", "raw_valid_to",
        "image_url", "product_key"
    ]
    st.dataframe(df[show_cols], use_container_width=True)

st.caption("Tip: start the API with `uvicorn app.api.main:app --reload`")
