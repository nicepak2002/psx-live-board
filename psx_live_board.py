import streamlit as st
import pandas as pd
import yfinance as yf
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

st.title("📈 PSX KSE-100 Market Board")
st.caption(f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT")

# Core PSX Symbols
KSE_100_SYMBOLS = [
    "LUCK", "ENGRO", "HUBC", "OGDC", "PPL", "SYS", "MEBL", "FFC", 
    "HBL", "MCB", "UBL", "MARI", "EFERT", "TRG", "POL", "BAFL", 
    "CHCC", "DGKC", "PIOC", "CNERGY", "BOP", "KEL", "TPLP", "DOL",
    "ABL", "ABOT", "AGP", "AHCL", "AICL", "AIRLINK", "AKBL", "APL",
    "ATLH", "ATRL", "BAHL", "BWCL", "COLG", "CPHL", "FABL", "FATIMA", 
    "FCCL", "FFBL", "GADT", "GAL", "GATM", "GLAXO", "HALEON", "HMB", 
    "ILP", "INIL", "ISL", "KAPCO", "KOHC", "KTML", "LCI", "LOTCHEM", 
    "MLCF", "NBP", "NCL", "NESTLE", "NML", "NPL", "PABC", "PAEL", 
    "PAKT", "PIBTL", "PKGS", "PSO", "PTC", "RMPL", "SAZEW", "SHEL", 
    "SHFA", "SNGP", "SPWL", "SRVI", "SSGC", "TGL", "THALL", "UNITY"
]

@st.cache_data(ttl=45)
def fetch_psx_prices():
    """
    Fetches latest price (LTP) or previous close for PSX stocks via yfinance.
    Handles off-market hours smoothly without returning empty sets.
    """
    yf_tickers = [f"{sym}.KA" for sym in KSE_100_SYMBOLS]
    parsed_list = []

    try:
        # Download 5-day daily data to ensure data availability on weekends/holidays
        df_download = yf.download(yf_tickers, period="5d", interval="1d", progress=False)
        
        if not df_download.empty and 'Close' in df_download:
            close_prices = df_download['Close'].ffill().iloc[-1]  # Get most recent closing price
            
            for sym in KSE_100_SYMBOLS:
                ticker_key = f"{sym}.KA"
                price = close_prices.get(ticker_key, None)
                
                if pd.notna(price):
                    parsed_list.append({
                        "Symbol": sym,
                        "Price (PKR)": round(float(price), 2),
                        "Status": "Active"
                    })
                else:
                    parsed_list.append({"Symbol": sym, "Price (PKR)": "N/A", "Status": "No Data"})
                    
            return pd.DataFrame(parsed_list)
    except Exception:
        pass

    return pd.DataFrame()

# --- Application Rendering ---
with st.spinner("Retrieving PSX market data..."):
    df = fetch_psx_prices()

if not df.empty:
    valid_df = df[df["Price (PKR)"] != "N/A"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tracked Companies", len(df))
    col2.metric("Active Price Feeds", len(valid_df))
    col3.metric("Auto-Refresh Cycle", f"#{count}")

    search_query = st.text_input("🔍 Filter by Stock Symbol", "")
    if search_query:
        df = df[df["Symbol"].str.contains(search_query.upper(), na=False)]

    st.markdown("### Stock Price Watchlist")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Price (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
        }
    )
else:
    st.error("Market feed server timed out. Please click 'R' or refresh the page.")
