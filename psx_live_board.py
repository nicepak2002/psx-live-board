import streamlit as st
import pandas as pd
import requests
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

# Master KSE-100 Symbols List
KSE_100_SYMBOLS = set([
    "ABL", "ABOT", "AGP", "AHCL", "AICL", "AIRLINK", "AKBL", "APL", "ATLH", "ATRL", 
    "BAFL", "BAHL", "BNWM", "BOP", "BWCL", "CHCC", "CNERGY", "COLG", "CPHL", "DCR", 
    "DGKC", "EFERT", "ENGRO", "FABL", "FATIMA", "FCCL", "FFBL", "FFC", "FML", "GADT", 
    "GAL", "GATM", "GHGL", "GLAXO", "HALEON", "HBL", "HMB", "HUBC", "ILP", "INIL", 
    "ISL", "JDWS", "KAPCO", "KEL", "KOHC", "KTML", "LCI", "LOTCHEM", "LUCK", "MARI", 
    "MCB", "MEBL", "MHAM", "MLCF", "MUREB", "NATF", "NBP", "NCL", "NESTLE", "NML", 
    "NPL", "OGDC", "PABC", "PAEL", "PAKT", "PIBTL", "PIOC", "PKGS", "POL", "PPL", 
    "PSMC", "PSO", "PTC", "RMPL", "SAZEW", "SCBPL", "SHEL", "SHFA", "SNGP", "SPWL", 
    "SRVI", "SSGC", "SYS", "TGL", "THALL", "TPLP", "TRG", "UBL", "UNITY", "UPFL"
])

@st.cache_data(ttl=25)
def fetch_psx_data_fast():
    """
    Directly fetches live prices via the PSX Market Watch JSON endpoint in < 1 second.
    """
    url = "https://dps.psx.com.pk/market-watch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://dps.psx.com.pk/market-watch"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            
            # Extracts market stock list from JSON feed
            stocks = json_data.get("data", json_data) if isinstance(json_data, dict) else json_data
            
            parsed_list = []
            for item in stocks:
                symbol = item.get("symbol", "").split(".")[0]
                
                # Filter for KSE-100 constituents
                if symbol in KSE_100_SYMBOLS or not KSE_100_SYMBOLS:
                    price = item.get("current") or item.get("price") or item.get("close") or item.get("ldcp")
                    try:
                        price = float(price)
                    except (TypeError, ValueError):
                        price = None
                        
                    parsed_list.append({
                        "Symbol": symbol,
                        "Latest Price (PKR)": price
                    })
                    
            if parsed_list:
                df = pd.DataFrame(parsed_list).drop_duplicates(subset=["Symbol"])
                return df
    except Exception:
        pass

    # Fallback endpoint if main JSON feed is quiet
    try:
        alt_url = "https://dps.psx.com.pk/symbols"
        res = requests.get(alt_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            parsed_list = []
            for item in data:
                sym = item.get("symbol", "").split(".")[0]
                if sym in KSE_100_SYMBOLS:
                    parsed_list.append({
                        "Symbol": sym,
                        "Latest Price (PKR)": float(item.get("price", 0))
                    })
            return pd.DataFrame(parsed_list)
    except Exception:
        pass
        
    return pd.DataFrame()

# --- App Logic Execution ---
with st.spinner("Connecting to live PSX feed..."):
    df = fetch_psx_data_fast()

# --- Display Data or Handling ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total KSE-100 Scrips", len(df))
    col2.metric("Market Status", "LIVE (1m Refresh)")
    col3.metric("Cycle Counter", f"#{count}")

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
        }
    )
else:
    st.error("Market Feed Connecting... Next refresh in 60s (or click 'R' to retry).")
