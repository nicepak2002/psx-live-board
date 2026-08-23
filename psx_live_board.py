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

st.title("📈 PSX KSE-100 Live Market Board")
st.caption(f"Last Refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT")

# KSE-100 Ticker Symbols mapped to Yahoo Finance PSX format (.KA)
KSE_100_SYMBOLS = [
    "LUCK", "ENGRO", "HUBC", "OGDC", "PPL", "SYS", "MEBL", "FFC", 
    "HBL", "MCB", "UBL", "MARI", "EFERT", "TRG", "POL", "BAFL", 
    "CHCC", "DGKC", "PIOC", "CNERGY", "BOP", "KEL", "TPLP", "DOL",
    "ABL", "ABOT", "AGP", "AHCL", "AICL", "AIRLINK", "AKBL", "APL",
    "ATLH", "ATRL", "BAHL", "BWCL", "COLG", "CPHL", "DGKC", "FABL",
    "FATIMA", "FCCL", "FFBL", "GADT", "GAL", "GATM", "GLAXO", "HALEON",
    "HMB", "ILP", "INIL", "ISL", "KAPCO", "KOHC", "KTML", "LCI",
    "LOTCHEM", "MLCF", "NBP", "NCL", "NESTLE", "NML", "NPL", "PABC",
    "PAEL", "PAKT", "PIBTL", "PKGS", "PSO", "PTC", "RMPL", "SAZEW",
    "SHEL", "SHFA", "SNGP", "SPWL", "SRVI", "SSGC", "TGL", "THALL", "UNITY"
]

@st.cache_data(ttl=45)
def fetch_psx_via_yfinance():
    """
    Downloads bulk market data for all PSX stocks in a single request.
    """
    # Convert symbols to Yahoo Finance format (e.g., LUCK.KA)
    yf_tickers = [f"{sym}.KA" for sym in KSE_100_SYMBOLS]
    
    try:
        # Bulk download 1-day data for fast execution
        data = yf.download(yf_tickers, period="1d", interval="1m", progress=False)
        
        parsed_list = []
        if not data.empty and 'Close' in data:
            close_prices = data['Close'].iloc[-1]  # Get the latest closing/live price row
            
            for sym in KSE_100_SYMBOLS:
                ticker_key = f"{sym}.KA"
                price = close_prices.get(ticker_key, None)
                
                # Fallback check if single value or nan
                if pd.notna(price):
                    parsed_list.append({
                        "Symbol": sym,
                        "Latest Price (PKR)": round(float(price), 2)
                    })
                else:
                    parsed_list.append({"Symbol": sym, "Latest Price (PKR)": "N/A"})
                    
            return pd.DataFrame(parsed_list)
    except Exception:
        pass
        
    return pd.DataFrame()

# --- Application Logic ---
with st.spinner("Fetching live PSX prices..."):
    df = fetch_psx_via_yfinance()

if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scrips Tracked", len(df))
    col2.metric("Market Refresh Rate", "1 Minute Auto-Update")
    col3.metric("Cycle Count", f"#{count}")

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
    st.error("Connecting to server... If market is closed, data will reflect last traded price on next refresh.")
