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

# --- Auto Refresh Setup (60 seconds) ---
count = st_autorefresh(interval=60000, limit=None, key="psx_refresh_counter")

st.title("📈 PSX KSE-100 Live Market Board")
st.caption(f"Last Refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

@st.cache_data(ttl=300)
def get_all_kse100_symbols():
    """
    Dynamically fetches all constituent scrips in the KSE-100 index directly from PSX DPS.
    """
    url = "https://dps.psx.com.pk/indices/KSE100"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            symbols = []
            # Scrape symbols from the PSX KSE100 constituents table
            table = soup.find("table")
            if table:
                for row in table.find_all("tr")[1:]:
                    cols = row.find_all("td")
                    if cols:
                        sym = cols[0].text.strip().split('.')[0]  # Strip any .XD suffix
                        if sym and sym not in symbols:
                            symbols.append(sym)
            if len(symbols) >= 50:
                return symbols
    except Exception:
        pass
    
    # Fallback complete KSE-100 list if dynamic fetch encounters a block
    return [
        "ABL", "ABOT", "AGP", "AHCL", "AICL", "AIRLINK", "AKBL", "APL", "ATLH", "ATRL", 
        "BAFL", "BAHL", "BNWM", "BOP", "BWCL", "CHCC", "CNERGY", "COLG", "CPHL", "DCR", 
        "DGKC", "EFERT", "ENGRO", "FABL", "FATIMA", "FCCL", "FFBL", "FFC", "FML", "GADT", 
        "GAL", "GATM", "GHGL", "GLAXO", "HALEON", "HBL", "HMB", "HUBC", "ILP", "INIL", 
        "ISL", "JDWS", "KAPCO", "KEL", "KOHC", "KTML", "LCI", "LOTCHEM", "LUCK", "MARI", 
        "MCB", "MEBL", "MHAM", "MLCF", "MUREB", "NATF", "NBP", "NCL", "NESTLE", "NML", 
        "NPL", "OGDC", "PABC", "PAEL", "PAKT", "PIBTL", "PIOC", "PKGS", "POL", "PPL", 
        "PSMC", "PSO", "PTC", "RMPL", "SAZEW", "SCBPL", "SHEL", "SHFA", "SNGP", "SPWL", 
        "SRVI", "SSGC", "SYS", "TGL", "THALL", "TPLP", "TRG", "UBL", "UNITY", "UPFL"
    ]

@st.cache_data(ttl=45)
def fetch_psx_stock_data(symbol):
    """
    Fetches real-time price and 52-week range details for a stock scrip.
    """
    url = f"https://dps.psx.com.pk/company/{symbol}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Latest Price
            latest_price = None
            price_elem = soup.find("div", class_="quote__close") or soup.find("div", class_="stats_value")
            if price_elem:
                raw_text = price_elem.text.strip().replace("Rs.", "").replace(",", "").strip()
                try:
                    latest_price = float(raw_text)
                except ValueError:
                    latest_price = None
            
            # 2. 52-Week High & Low
            high_52, low_52 = None, None
            for item in soup.find_all(["div", "tr"]):
                text = item.text.lower()
                if "52 week high" in text or "52w high" in text:
                    val_elem = item.find("div", class_="stats_value") or item.find("td")
                    if val_elem:
                        try:
                            high_52 = float(val_elem.text.strip().replace("Rs.", "").replace(",", ""))
                        except ValueError:
                            pass
                elif "52 week low" in text or "52w low" in text:
                    val_elem = item.find("div", class_="stats_value") or item.find("td")
                    if val_elem:
                        try:
                            low_52 = float(val_elem.text.strip().replace("Rs.", "").replace(",", ""))
                        except ValueError:
                            pass

            return {
                "Symbol": symbol,
                "Latest Price (PKR)": latest_price if latest_price is not None else "N/A",
                "52W High (PKR)": high_52 if high_52 is not None else "N/A",
                "52W Low (PKR)": low_52 if low_52 is not None else "N/A"
            }
    except Exception:
        pass
    
    return {"Symbol": symbol, "Latest Price (PKR)": "N/A", "52W High (PKR)": "N/A", "52W Low (PKR)": "N/A"}

# --- Main App Execution ---
all_symbols = get_all_kse100_symbols()

with st.spinner(f"Fetching live data for {len(all_symbols)} KSE-100 companies..."):
    data_list = [fetch_psx_stock_data(sym) for sym in all_symbols]
    df = pd.DataFrame(data_list)

# --- Metric Cards ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Scrips Loaded", len(df))
col2.metric("Market Refresh Rate", "1 Minute Auto-Update")
col3.metric("Refresh Cycle Count", f"#{count}")

# --- Interactive Filter & Display ---
search_query = st.text_input("🔍 Search Company Symbol", "")
if search_query:
    df = df[df["Symbol"].str.contains(search_query.upper(), na=False)]

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
