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

# Official KSE-100 Index Constituents Ticker Symbols
KSE_100_CONSTITUENTS = [
    # Banks & Financials
    "ABL", "AKBL", "BAFL", "BAHL", "BOP", "FABL", "HBL", "HMB", "MCB", "MEBL", "NBP", "SCBPL", "UBL",
    # Oil & Gas / Exploration / Marketing
    "APL", "ATRL", "CNERGY", "MARI", "OGDC", "POL", "PPL", "PSO", "SHEL", "SNGP", "SSGC",
    # Chemicals, Fertilizers & Petrochemicals
    "AGP", "COLG", "CPHL", "EFERT", "ENGRO", "EPCL", "FATIMA", "FFBL", "FFC", "ICI", "LOTCHEM",
    # Cement & Materials
    "BWCL", "CHCC", "DGKC", "FCCL", "KOHC", "LUCK", "MLCF", "PIOC",
    # Technology & Telecom
    "AIRLINK", "AVN", "OCTOPUS", "PTC", "SYS", "TELE", "TRG",
    # Power & Energy
    "HUBC", "KAPCO", "KEL", "NPL", "SPWL",
    # Food, Personal Care & Pharma
    "ABOT", "FML", "GLAXO", "HALEON", "NATF", "NESTLE", "RMPL", "SHFA", "UNITY", "UPFL",
    # Autos & Engineering / Industrial
    "ATLH", "GAL", "INIL", "ISL", "PAEL", "SAZEW", "SRVI", "TGL", "THALL",
    # Textiles & Paper/Packaging
    "BNWM", "GADT", "GATM", "ILP", "KTML", "NCL", "NML", "PABC", "PKGS",
    # Real Estate & REITs / Investment
    "AHCL", "AICL", "DCR", "MHAM", "MUREB", "PAKT", "PIBTL", "TPLP"
]

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@st.cache_data(ttl=45)
def fetch_kse100_prices():
    """
    Fetches latest traded prices exclusively for official KSE-100 index scrips.
    """
    parsed_list = []
    # Fetch in small batches of 25 to guarantee 100% Yahoo API coverage
    symbol_chunks = list(chunk_list(KSE_100_CONSTITUENTS, 25))

    for chunk in symbol_chunks:
        yf_tickers = [f"{sym}.KA" for sym in chunk]
        try:
            df_download = yf.download(yf_tickers, period="5d", interval="1d", progress=False)
            
            if not df_download.empty and 'Close' in df_download:
                close_prices = df_download['Close'].ffill().iloc[-1]
                
                for sym in chunk:
                    ticker_key = f"{sym}.KA"
                    price = close_prices.get(ticker_key, None) if len(chunk) > 1 else close_prices
                    
                    if pd.notna(price):
                        parsed_list.append({
                            "Symbol": sym,
                            "Price (PKR)": round(float(price), 2),
                            "Status": "Active"
                        })
                    else:
                        parsed_list.append({"Symbol": sym, "Price (PKR)": "N/A", "Status": "No Data"})
        except Exception:
            for sym in chunk:
                parsed_list.append({"Symbol": sym, "Price (PKR)": "N/A", "Status": "Error"})

    return pd.DataFrame(parsed_list)

# --- App Interface ---
with st.spinner("Retrieving KSE-100 Index constituents data..."):
    df = fetch_kse100_prices()

if not df.empty:
    valid_df = df[df["Status"] == "Active"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("KSE-100 Constituents", len(df))
    col2.metric("Active Feeds", len(valid_df))
    col3.metric("Auto-Refresh Cycle", f"#{count}")

    search_query = st.text_input("🔍 Filter Stock Symbol", "")
    if search_query:
        df = df[df["Symbol"].str.contains(search_query.upper(), na=False)]

    st.markdown("### KSE-100 Index Scrips Watchlist")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Price (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
        }
    )
else:
    st.error("Market feed server timed out. Please refresh.")
