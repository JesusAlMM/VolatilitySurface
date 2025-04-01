import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import timedelta
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.interpolate import griddata
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import time

st.set_page_config(layout="wide")

if "vol_surface_history" not in st.session_state:
    st.session_state.vol_surface_history = []

def page_one():
    st.button("Recorded Graphs", on_click=lambda: st.session_state.update({"page": "page_2"}))
    st.title('Volatility & Greeks Explorer')
    
    def bs_call_price(S, K, T, r, sigma, q=0):
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        call_price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return call_price
    
    def calculate_greeks(S, K, T, r, sigma, q=0):
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
    
        delta = np.exp(-q * T) * norm.cdf(d1)
        gamma = np.exp(-q * T) * norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = (-S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2)
                 + q * S * np.exp(-q * T) * norm.cdf(d1))
        vega = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    
        return delta, gamma, theta, vega, rho
    
    def implied_volatility(price, S, K, T, r, q=0):
        if T <= 0 or price <= 0:
            return np.nan
    
        def objective_function(sigma):
            return bs_call_price(S, K, T, r, sigma, q) - price
    
        try:
            implied_vol = brentq(objective_function, 1e-6, 5)
        except (ValueError, RuntimeError):
            implied_vol = np.nan
        return implied_vol
            
    with st.sidebar:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 30px;">📈</span>
                <h2 style="margin: 0;">Black-Scholes Model</h2>
            </div>
            <div style="background-color: #1E1E1E; padding: 5px; border-radius: 5px; display: inline-block;">
           <span style="color: #7FFFD4; font-size: 14px;">Created by:</span>
           </div>
           <br><br>
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="30">
                <a href="https://www.linkedin.com/in/jesusamart" target="_blank" 
                   style="text-decoration: none; background-color: #1E1E1E; color: white; padding: 5px 5px; border-radius: 5px; font-weight: bold; font-size: 14px;">
                    Jesus A. Martínez
                </a>
            </div>
            <br>
        """, unsafe_allow_html=True)

    st.sidebar.header('Ticker Symbol')
    ticker_symbol = st.sidebar.text_input('Select Ticker', value='SPY', max_chars=10).upper()

    st.sidebar.header('Model Params')
    risk_free_rate = st.sidebar.number_input('Risk-Free Rate (%)', value=0.015, format="%.4f")
    dividend_yield = st.sidebar.number_input('Dividend Yield (%)', value=0.013, format="%.4f")
    y_axis_option = st.sidebar.selectbox('Select Y-axis:', ('Strike Price', 'Moneyness'))
    
    st.sidebar.header('Strike Price Filter Params')
    min_strike_pct = st.sidebar.number_input('Min Strike Price (% of Spot Price)', min_value=50.0, max_value=199.0, value=80.0, step=1.0, format="%.1f")
    max_strike_pct = st.sidebar.number_input('Max Strike Price (% of Spot Price)', min_value=51.0, max_value=200.0, value=120.0, step=1.0, format="%.1f")
    
    st.sidebar.header('Save interval (seconds)')
    save_interval = st.sidebar.number_input('Interval (in seconds)', min_value=1, value=60, step=1)
    
    if min_strike_pct >= max_strike_pct:
        st.sidebar.error('Minimum percentage must be less than maximum percentage.')
        st.stop()
    
    ticker = yf.Ticker(ticker_symbol)
    today = pd.Timestamp('today').normalize()
    
    try:
        expirations = ticker.options
        exp_dates = [pd.Timestamp(exp) for exp in expirations 
                     if pd.Timestamp(exp) > today + timedelta(days=7)]
    except Exception as e:
        st.error(f'Error fetching options for {ticker_symbol}: {e}')
        st.stop()
    
    if not exp_dates:
        st.error(f'No valid option expiration dates for {ticker_symbol}.')
        st.stop()
    
    option_data = []
    for exp_date in exp_dates:
        try:
            opt_chain = ticker.option_chain(exp_date.strftime('%Y-%m-%d'))
            calls = opt_chain.calls
        except Exception as e:
            st.warning(f'Error fetching options for {exp_date.date()}: {e}')
            continue
    
        calls = calls[(calls['bid'] > 0) & (calls['ask'] > 0)]
        for _, row in calls.iterrows():
            mid_price = (row['bid'] + row['ask']) / 2
            option_data.append({
                'expirationDate': exp_date,
                'strike': row['strike'],
                'mid': mid_price
            })
    
    if not option_data:
        st.error('No valid options data available.')
        st.stop()
    
    options_df = pd.DataFrame(option_data)
    spot_price = ticker.history(period='1d')['Close'].iloc[-1]
    options_df['daysToExpiration'] = (options_df['expirationDate'] - today).dt.days
    options_df['timeToExpiration'] = options_df['daysToExpiration'] / 365
    options_df = options_df[(options_df['strike'] >= spot_price * (min_strike_pct / 100)) &
                            (options_df['strike'] <= spot_price * (max_strike_pct / 100))]
    options_df = options_df[options_df['timeToExpiration'] > 0]
    with st.spinner('Calculating IV & greeks...'):
        options_df['impliedVolatility'] = options_df.apply(
            lambda row: implied_volatility(row['mid'], spot_price, row['strike'], row['timeToExpiration'], risk_free_rate, dividend_yield), axis=1
        )
        options_df.dropna(subset=['impliedVolatility'], inplace=True)
   
    col1, col2 = st.columns([3.5, 1.5])    
    with col1:    
        options_df['moneyness'] = options_df['strike'] / spot_price
    
        if y_axis_option == 'Strike Price':
            Y = options_df['strike'].values
            y_label = 'Strike Price'
        else:
            Y = options_df['moneyness'].values
            y_label = 'Moneyness'
            
        X = options_df['timeToExpiration']
        Z = options_df['impliedVolatility']
    
        ti = np.linspace(X.min(), X.max(), 50)
        ki = np.linspace(Y.min(), Y.max(), 50)
        T, K = np.meshgrid(ti, ki)
        Zi = griddata((X, Y), Z, (T, K), method='linear')
        Zi = np.ma.array(Zi, mask=np.isnan(Zi))
    
        fig = go.Figure(data=[go.Surface(
            x=T, y=K, z=Zi,
            colorscale='Spectral',
            colorbar_title=''
        )])
    
        fig.update_layout(
            scene=dict(
                xaxis_title='Time to Exp',
                yaxis_title=y_label,
                zaxis_title='Implied Vol'
            ),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=35, r=35, b=35, t=35)
        )
        
        click_data = plotly_events(fig, click_event=True, hover_event=False)
        
        if "last_save_time" not in st.session_state:
            st.session_state.last_save_time = time.time() 
        
        current_time = time.time()        
        elapsed_time = current_time - st.session_state.last_save_time
        
        if elapsed_time >= save_interval:
            st.session_state.vol_surface_history.append({
                "timestamp": pd.Timestamp.now(),
                "figure": fig
            })
            st.session_state.last_save_time = current_time
            st.success(f"Graph saved at {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning(f"There are {save_interval - elapsed_time:.0f} seconds remaining to save the graph.")
   
        img_bytes = fig.to_image(format="png")
        st.download_button(
            label="Download Graph",
            data=img_bytes,
            file_name="volatility_surface.png",
            mime="image/png"
        )
   
    with col2:
        if click_data:
            selected_time = click_data[0]['x']
            selected_strike = click_data[0]['y']
            implied_vol = griddata((X, Y), Z, (selected_time, selected_strike), method='linear')
    
            if implied_vol is None or np.isnan(implied_vol):
                st.warning("No volatility data available for the selected point.")
            else:
                delta, gamma, theta, vega, rho = calculate_greeks(
                    spot_price, selected_strike, selected_time, 
                    risk_free_rate, implied_vol, dividend_yield
                )
    
                col_symbol, col_name, col_value = st.columns([0.25, 1, 2])
    
                symbols = ["Δ", "Γ", "Θ", "V", "ρ"]
                names = ["Delta:", "Gamma:", "Theta:", "Vega:", "Rho:"]
                values = [f"{delta:.4f}", f"{gamma:.4f}", f"{theta:.4f}", f"{vega:.4f}", f"{rho:.4f}"]
    
                for symbol, name, value in zip(symbols, names, values):
                    col_symbol.write(f"**{symbol}**") 
                    col_name.write(name)              
                    col_value.write(value)            
        else:
            st.info("Click on the volatility surface plot to calculate Greeks for a specific option.")

def page_two():
    st.title("Recorded Graphs")
    st.button("Go back", on_click=lambda: st.session_state.update({"page": "page_1"}))

    if "gallery_index" not in st.session_state:
        st.session_state.gallery_index = 0

    if "vol_surface_history" in st.session_state and st.session_state.vol_surface_history:
        gallery_items = st.session_state.vol_surface_history[::-1] 

        current_item = gallery_items[st.session_state.gallery_index]
        st.write(f"**Graph saved:** {current_item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        st.markdown(
            """
            <style>
            .centered {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="centered">', unsafe_allow_html=True)
        st.plotly_chart(current_item["figure"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("🠸 Back"):
                if st.session_state.gallery_index > 0:
                    st.session_state.gallery_index -= 1
                else:
                    st.warning("This is the first graph.")
        with col3:
            if st.button("Next 🠺"):
                if st.session_state.gallery_index < len(gallery_items) - 1:
                    st.session_state.gallery_index += 1
                else:
                    st.warning("This is the last graph.")
    else:
        st.info("No graphs have been saved yet.")

if 'page' not in st.session_state:
    st.session_state.page = "page_1"

if st.session_state.page == "page_1":
    page_one()
elif st.session_state.page == "page_2":
    page_two()
