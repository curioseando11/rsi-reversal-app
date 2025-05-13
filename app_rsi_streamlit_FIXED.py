
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator

st.set_page_config(layout="centered")
st.title("Simulador de Estrategia RSI Reversal")

ticker = st.text_input("Símbolo de la acción (ej: AAPL, TSLA, NVDA)", value="AAPL")
start_date = st.date_input("Fecha de inicio", value=pd.to_datetime("2022-01-01"))
end_date = st.date_input("Fecha de fin", value=pd.to_datetime("2023-01-01"))
rsi_entry = st.slider("Comprar cuando RSI sea menor que:", min_value=5, max_value=50, value=30)
rsi_exit = st.slider("Vender cuando RSI sea mayor que:", min_value=10, max_value=90, value=50)
initial_capital = st.number_input("Capital inicial ($)", value=10000)

if st.button("Simular estrategia"):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.warning("No se encontraron datos para ese símbolo.")
        else:
            rsi = RSIIndicator(close=data["Close"]).rsi()
            data["RSI"] = rsi.fillna(0)

            capital = initial_capital
            position = 0
            historial = []
            for i in range(1, len(data)):
                rsi_val = data["RSI"].iloc[i]
                if position == 0 and rsi_val < rsi_entry:
                    buy_price = data["Close"].iloc[i]
                    position = capital / buy_price
                    capital = 0
                    historial.append((data.index[i], "BUY", buy_price))
                elif position > 0 and rsi_val > rsi_exit:
                    sell_price = data["Close"].iloc[i]
                    capital = position * sell_price
                    position = 0
                    historial.append((data.index[i], "SELL", sell_price))
            if position > 0:
                capital = position * data["Close"].iloc[-1]

            st.success(f"💵 Capital final: ${capital:,.2f}")
            
            # Mostrar gráfico
            fig, ax = plt.subplots(figsize=(12,5))
            ax.plot(data["Close"], label="Precio", color="blue")
            for fecha, tipo, precio in historial:
                if tipo == "BUY":
                    ax.plot(fecha, precio, marker="^", color="green", markersize=10)
                elif tipo == "SELL":
                    ax.plot(fecha, precio, marker="v", color="red", markersize=10)
            ax.set_title("Señales de Compra/Venta")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Precio")
            ax.grid(True)
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")
