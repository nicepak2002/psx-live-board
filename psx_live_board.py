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

# --- Auto Refresh Setup ---
# 60000 milliseconds = 1 minute
count = st_autorefresh(interval=60000, limit=None, key="psx_refresh_counter")

st.title("📈 PSX KSE-100 Live Market Board")
st.caption(f"Last Refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT")

# KSE-100 Scrips List
KSE_100_SYMBOLS = [
    "LUCK", "ENGRO", "HUBC", "OGDC", "PPL", "SYS", "MEBL", "FFC", 
    "HBL", "MCB", "UBL", "MARI", "EFERT", "TRG", "POL", "BAFL", 
    "CHCC", "DGKC", "PIOC", "CNERGY", "BOP", "KEL", "TPLP", "DOL"
]

@st.cache_data(ttl=50)  # Cache results for 50 seconds to keep performance smooth
def fetch_psx_stock_data(symbol):
    """
    Fetches stock details from the official PSX Data Portal.
    """
    url = f"https://dps.psx.com.pk/company/{symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract latest price / last traded price
            price_elem = soup.find("div", class_="quote__close")
            latest_price = price_elem.text.strip().replace("Rs.", "").replace(",", "") if price_elem else "N/A"
            
            # Extract 52-Week High & Low
            stats_keys = soup.find_all("div", class_="stats_label")
            stats_values = soup.find_all("div", class_="stats_value")
            
            high_52 = "N/A"
            low_52 = "N/A"
            
            for key, val in zip(stats_keys, stats_values):
                label_text = key.text.strip().lower()
                if "52 week high" in label_text or "52w high" in label_text:
                    high_52 = val.text.strip().replace("Rs.", "").replace(",", "")
                elif "52 week low" in label_text or "52w low" in label_text:
                    low_52 = val.text.strip().replace("Rs.", "").replace(",", "")
            
            return {
                "Symbol": symbol,
                "Latest Price (PKR)": float(latest_price) if latest_price != "N/A" else "N/A",
                "52W High (PKR)": float(high_52) if high_52 != "N/A" else "N/A",
                "52W Low (PKR)": float(low_52) if low_52 != "N/A" else "N/A"
            }
    except Exception:
        pass
    
    return {"Symbol": symbol, "Latest Price (PKR)": "N/A", "52W High (PKR)": "N/A", "52W Low (PKR)": "N/A"}

# --- Data Fetching ---
with st.spinner("Fetching PSX market data..."):
    data_list = []
    for sym in KSE_100_SYMBOLS:
        data_list.append(fetch_psx_stock_data(sym))
        
    df = pd.DataFrame(data_list)

# --- Summary Cards ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Scrips Tracked", len(df))
col2.metric("Market Refresh Rate", "1 Minute Auto-Update")
col3.metric("Refresh Cycle Count", f"#{count}")

# --- Display Data Table ---
st.markdown("### Stock Overview")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Latest Price (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
        "52W High (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
        "52W Low (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
    }
)
