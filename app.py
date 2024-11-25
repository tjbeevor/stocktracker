import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="ASX Mining Stocks Tracker",
    page_icon="⛏️",
    layout="wide"
)

# List of major ASX mining stocks with their tickers
MINING_STOCKS = {
    'BHP Group': 'BHP.AX',
    'Rio Tinto': 'RIO.AX',
    'Fortescue Metals': 'FMG.AX',
    'Northern Star': 'NST.AX',
    'Evolution Mining': 'EVN.AX',
    'Mineral Resources': 'MIN.AX',
    'South32': 'S32.AX',
    'Newcrest Mining': 'NCM.AX',
    'Pilbara Minerals': 'PLS.AX',
    'Lynas Rare Earths': 'LYC.AX'
}

def load_stock_data(ticker, period='1y'):
    """Load stock data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            st.warning(f"No data available for {ticker}")
            return None
        return hist
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None

def create_stock_chart(data, company_name):
    """Create a candlestick chart using plotly"""
    if data is None or data.empty:
        return None
        
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])])
    
    fig.update_layout(
        title=f'{company_name} Stock Price',
        yaxis_title='Price (AUD)',
        xaxis_title='Date',
        template='plotly_dark'
    )
    return fig

def get_safe_value(data, column, index=-1, default="N/A"):
    """Safely get value from DataFrame with fallback"""
    if data is None or data.empty:
        return default
    try:
        return data[column][index]
    except:
        return default

def calculate_daily_change(data):
    """Safely calculate daily change percentage"""
    if data is None or data.empty or len(data) < 2:
        return "N/A"
    try:
        change = ((data['Close'][-1] - data['Close'][-2]) / data['Close'][-2]) * 100
        return f"{change:.2f}%"
    except:
        return "N/A"

def main():
    st.title("ASX Mining Stocks Tracker")
    st.markdown("Track and analyze major mining stocks listed on the Australian Securities Exchange (ASX)")
    
    # Sidebar
    st.sidebar.header("Settings")
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks to Track",
        list(MINING_STOCKS.keys()),
        default=list(MINING_STOCKS.keys())[:3]
    )
    
    time_period = st.sidebar.selectbox(
        "Select Time Period",
        ['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        index=3
    )
    
    # Main content
    if selected_stocks:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Charts", "Summary"])
        
        with tab1:
            # Display charts
            for company in selected_stocks:
                ticker = MINING_STOCKS[company]
                data = load_stock_data(ticker, time_period)
                
                if data is not None and not data.empty:
                    # Create and display chart
                    fig = create_stock_chart(data, company)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Display key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        current_price = get_safe_value(data, 'Close')
                        if current_price != "N/A":
                            current_price = f"${current_price:.2f}"
                        st.metric("Current Price", current_price)
                    with col2:
                        st.metric("Daily Change", calculate_daily_change(data))
                    with col3:
                        volume = get_safe_value(data, 'Volume')
                        if volume != "N/A":
                            volume = f"{volume:,.0f}"
                        st.metric("Volume", volume)
                    with col4:
                        high = get_safe_value(data, 'High', default=0)
                        if high != "N/A":
                            high = f"${data['High'].max():.2f}"
                        st.metric("52W High", high)
        
        with tab2:
            # Create summary table
            summary_data = []
            for company in selected_stocks:
                ticker = MINING_STOCKS[company]
                data = load_stock_data(ticker, time_period)
                
                if data is not None:
                    current_price = get_safe_value(data, 'Close')
                    if current_price != "N/A":
                        current_price = f"${current_price:.2f}"
                    
                    year_high = get_safe_value(data, 'High', default=0)
                    if year_high != "N/A":
                        year_high = f"${data['High'].max():.2f}"
                    
                    year_low = get_safe_value(data, 'Low', default=0)
                    if year_low != "N/A":
                        year_low = f"${data['Low'].min():.2f}"
                    
                    volume = get_safe_value(data, 'Volume')
                    if volume != "N/A":
                        volume = f"{volume:,.0f}"
                    
                    summary_data.append({
                        'Company': company,
                        'Ticker': ticker,
                        'Current Price': current_price,
                        'Daily Change %': calculate_daily_change(data),
                        'Volume': volume,
                        'Year High': year_high,
                        'Year Low': year_low
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
            else:
                st.warning("No data available for the selected stocks")

if __name__ == "__main__":
    main()
