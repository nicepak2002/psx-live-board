import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="PSX KSE-100 Live Board",
    page_icon="📈",
    layout="wide"
)

# --- Auto Refresh Setup (60 seconds = 1 minute) ---
count = st_autorefresh(interval=60000, limit=None, key="psx_refresh_counter")

st.title("📈 PSX KSE-100 Live Market Board")
st.caption(f"Last Refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

@st.cache_data(ttl=30)
def fetch_all_kse100_fast():
    """
    Fetches ALL KSE-100 stock prices in a SINGLE request (under 2 seconds).
    """
    url = "https://dps.psx.com.pk/indices/KSE100"
    data = []
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table")
            
            if table:
                rows = table.find_all("tr")
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        # Extract symbol name and current price
                        symbol = cols[0].text.strip().split('.')[0]
                        price_text = cols[1].text.strip().replace("Rs.", "").replace(",", "")
                        
                        try:
                            price = float(price_text)
                        except ValueError:
                            price = "N/A"
                            
                        data.append({
                            "Symbol": symbol,
                            "Latest Price (PKR)": price
                        })
    except Exception:
        pass
        
    return pd.DataFrame(data)

# --- Fetch Data instantly ---
with st.spinner("Fetching PSX market data in seconds..."):
    df = fetch_all_kse100_fast()

# If data returns empty (outside market hours or structure check), display fallback UI
if df.empty:
    st.warning("Unable to reach PSX live feed directly. Retrying on next cycle.")

# --- Summary Cards ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Scrips Loaded", len(df))
col2.metric("Market Refresh Rate", "1 Minute Auto-Update")
col3.metric("Refresh Cycle Count", f"#{count}")

# --- Search Filter & Display Table ---
search_query = st.text_input("🔍 Search Company Symbol", "")
if search_query and not df.empty:
    df = df[df["Symbol"].str.contains(search_query.upper(), na=False)]

st.markdown("### Stock Overview")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Latest Price (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
    }
)
