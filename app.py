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
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def create_stock_chart(data, company_name):
    """Create a candlestick chart using plotly"""
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
                
                # Create and display chart
                fig = create_stock_chart(data, company)
                st.plotly_chart(fig, use_container_width=True)
                
                # Display key metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Price", f"${data['Close'][-1]:.2f}")
                with col2:
                    change = ((data['Close'][-1] - data['Close'][-2]) / data['Close'][-2]) * 100
                    st.metric("Daily Change", f"{change:.2f}%")
                with col3:
                    st.metric("Volume", f"{data['Volume'][-1]:,.0f}")
                with col4:
                    st.metric("52W High", f"${data['High'].max():.2f}")
        
        with tab2:
            # Create summary table
            summary_data = []
            for company in selected_stocks:
                ticker = MINING_STOCKS[company]
                data = load_stock_data(ticker, time_period)
                
                summary_data.append({
                    'Company': company,
                    'Ticker': ticker,
                    'Current Price': f"${data['Close'][-1]:.2f}",
                    'Daily Change %': f"{((data['Close'][-1] - data['Close'][-2]) / data['Close'][-2] * 100):.2f}%",
                    'Volume': f"{data['Volume'][-1]:,.0f}",
                    'Year High': f"${data['High'].max():.2f}",
                    'Year Low': f"${data['Low'].min():.2f}"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)

if __name__ == "__main__":
    main()
