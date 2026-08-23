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

# Official KSE-100 Index Constituents (100 Companies Mapping)
KSE_100_DICT = {
    # Banks & Financials (13)
    "ABL": "Allied Bank Limited",
    "AKBL": "Askari Bank Limited",
    "BAFL": "Bank Alfalah Limited",
    "BAHL": "Bank AL Habib Limited",
    "BOP": "The Bank of Punjab",
    "FABL": "Faysal Bank Limited",
    "HBL": "Habib Bank Limited",
    "HMB": "Habib Metropolitan Bank Limited",
    "MCB": "MCB Bank Limited",
    "MEBL": "Meezan Bank Limited",
    "NBP": "National Bank of Pakistan",
    "SCBPL": "Standard Chartered Bank (Pakistan) Limited",
    "UBL": "United Bank Limited",
    
    # Oil & Gas / Exploration / Marketing (11)
    "APL": "Attock Petroleum Limited",
    "ATRL": "Attock Refinery Limited",
    "CNERGY": "Cnergyico PK Limited",
    "MARI": "Mari Petroleum Company Limited",
    "OGDC": "Oil & Gas Development Company Limited",
    "POL": "Pakistan Oilfields Limited",
    "PPL": "Pakistan Petroleum Limited",
    "PSO": "Pakistan State Oil Company Limited",
    "SHEL": "Shell Pakistan Limited",
    "SNGP": "Sui Northern Gas Pipelines Limited",
    "SSGC": "Sui Southern Gas Company Limited",
    
    # Chemicals, Fertilizers & Petrochemicals (11)
    "AGP": "AGP Limited",
    "COLG": "Colgate-Palmolive (Pakistan) Limited",
    "CPHL": "Citi Pharma Limited",
    "EFERT": "Engro Fertilizers Limited",
    "ENGRO": "Engro Corporation Limited",
    "EPCL": "Engro Polymer & Chemicals Limited",
    "FATIMA": "Fatima Fertilizer Company Limited",
    "FFBL": "Fauji Fertilizer Bin Qasim Limited",
    "FFC": "Fauji Fertilizer Company Limited",
    "ICI": "Lucky Core Industries Limited",
    "LOTCHEM": "Lotte Chemical Pakistan Limited",
    
    # Cement & Building Materials (9)
    "BWCL": "Bestway Cement Limited",
    "CHCC": "Cherat Cement Company Limited",
    "DGKC": "D.G. Khan Cement Company Limited",
    "FCCL": "Fauji Cement Company Limited",
    "KOHC": "Kohat Cement Company Limited",
    "LUCK": "Lucky Cement Limited",
    "MLCF": "Maple Leaf Cement Factory Limited",
    "PIOC": "Pioneer Cement Limited",
    "POWER": "Power Cement Limited",
    
    # Technology & Telecom (7)
    "AIRLINK": "Air Link Communication Limited",
    "AVN": "Avanceon Limited",
    "OCTOPUS": "Octopus Digital Limited",
    "PTC": "Pakistan Telecommunication Company Limited",
    "SYS": "Systems Limited",
    "TELE": "Telecard Limited",
    "TRG": "TRG Pakistan Limited",
    
    # Power & Energy (5)
    "HUBC": "The Hub Power Company Limited",
    "KAPCO": "Kot Addu Power Company Limited",
    "KEL": "K-Electric Limited",
    "NPL": "Nishat Power Limited",
    "SPWL": "Saif Power Limited",
    
    # Food, Personal Care & Pharmaceuticals (14)
    "ABOT": "Abbott Laboratories (Pakistan) Limited",
    "FFL": "Fauji Foods Limited",
    "FML": "FrieslandCampina Engro Pakistan Limited",
    "GLAXO": "GlaxoSmithKline Pakistan Limited",
    "HALEON": "Haleon Pakistan Limited",
    "HINL": "Highnoon Laboratories Limited",
    "NATF": "National Foods Limited",
    "NESTLE": "Nestlé Pakistan Limited",
    "RMPL": "Rafhan Maize Products Company Limited",
    "SEARL": "The Searle Company Limited",
    "SHFA": "Shifa International Hospitals Limited",
    "UNITY": "Unity Foods Limited",
    "UPFL": "Unilever Pakistan Foods Limited",
    "JDWS": "JDW Sugar Mills Limited",
    
    # Autos, Engineering & Industrial (11)
    "ATLH": "Atlas Honda Limited",
    "GAL": "Ghandhara Automobiles Limited",
    "GHGL": "Ghani Glass Limited",
    "INDU": "Indus Motor Company Limited",
    "INIL": "International Industries Limited",
    "ISL": "International Steels Limited",
    "MTL": "Millat Tractors Limited",
    "PAEL": "Pak Elektron Limited",
    "SAZEW": "Sazgar Engineering Works Limited",
    "SRVI": "Service Industries Limited",
    "TGL": "Tariq Glass Industries Limited",
    "THALL": "Thal Limited",
    
    # Textiles & Paper/Packaging (10)
    "BNWM": "Bannu Woollen Mills Limited",
    "GADT": "Gadoon Textile Mills Limited",
    "GATM": "Gul Ahmed Textile Mills Limited",
    "ILP": "Interloop Limited",
    "KTML": "Kohinoor Textile Mills Limited",
    "NCL": "Nishat Chunian Limited",
    "NML": "Nishat Mills Limited",
    "PABC": "Pakistan Aluminium Beverage Cans Limited",
    "PKGS": "Packages Limited",
    "IBFL": "Ibrahim Fibres Limited",
    
    # Real Estate, REITs, Services & Investment (9)
    "AHCL": "Arif Habib Corporation Limited",
    "AICL": "Adamjee Insurance Company Limited",
    "DCR": "Dolmen City REIT",
    "MHAM": "Murree Brewery Company Limited",
    "PAKT": "Pakistan Tobacco Company Limited",
    "PIBTL": "Pakistan International Bulk Terminal Limited",
    "PSX": "Pakistan Stock Exchange Limited",
    "TPLP": "TPL Properties Limited",
    "TPLRF1": "TPL REIT Fund I"
}

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@st.cache_data(ttl=45)
def fetch_kse100_prices():
    """
    Fetches prices for 100 KSE-100 scrips with company names and sequential numbering.
    """
    parsed_list = []
    symbols = list(KSE_100_DICT.keys())
    symbol_chunks = list(chunk_list(symbols, 25))

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
                            "Company Name": KSE_100_DICT.get(sym, sym),
                            "Symbol": sym,
                            "Price (PKR)": round(float(price), 2),
                            "Status": "Active"
                        })
                    else:
                        parsed_list.append({
                            "Company Name": KSE_100_DICT.get(sym, sym),
                            "Symbol": sym,
                            "Price (PKR)": "N/A",
                            "Status": "No Data"
                        })
        except Exception:
            for sym in chunk:
                parsed_list.append({
                    "Company Name": KSE_100_DICT.get(sym, sym),
                    "Symbol": sym,
                    "Price (PKR)": "N/A",
                    "Status": "Error"
                })

    df = pd.DataFrame(parsed_list)
    
    # Insert S.No as the first column starting from 1
    if not df.empty:
        df.insert(0, "S.No", range(1, len(df) + 1))
        
    return df

# --- App Interface ---
with st.spinner("Retrieving KSE-100 Index constituents data..."):
    df = fetch_kse100_prices()

if not df.empty:
    valid_df = df[df["Status"] == "Active"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("KSE-100 Constituents", len(df))
    col2.metric("Active Feeds", len(valid_df))
    col3.metric("Auto-Refresh Cycle", f"#{count}")

    search_query = st.text_input("🔍 Filter by Company Name or Symbol", "")
    if search_query:
        df = df[
            df["Symbol"].str.contains(search_query.upper(), na=False) |
            df["Company Name"].str.contains(search_query, case=False, na=False)
        ]

    st.markdown("### KSE-100 Index Scrips Watchlist")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "S.No": st.column_config.NumberColumn(format="%d"),
            "Company Name": st.column_config.TextColumn("Company Name"),
            "Symbol": st.column_config.TextColumn("Symbol"),
            "Price (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
        }
    )
else:
    st.error("Market feed server timed out. Please refresh.")
