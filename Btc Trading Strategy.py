import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TradingStrategy:
    def __init__(self, data, initial_capital=1000, leverage=2, risk_per_trade=0.02):
        self.data = data
        self.capital = initial_capital
        self.leverage = leverage
        self.risk_per_trade = risk_per_trade
        self.trades = []
    
    def calculate_atr(self, window=14):
        high_low = self.data["High"] - self.data["Low"]
        high_close = abs(self.data["High"] - self.data["Close"].shift())
        low_close = abs(self.data["Low"] - self.data["Close"].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.data["ATR"] = true_range.rolling(window=window).mean()
    
    def run_strategy(self):
        self.calculate_atr()
        for idx, row in self.data.iterrows():
            if idx < 14 or pd.isna(row["ATR"]):  # Skip first 14 rows due to ATR calculation
                continue
            
            atr = row["ATR"]
            entry_price = row["Close"]
            stop_loss = atr * 1.4  # ATR 1.4x for stop loss
            take_profit = entry_price + (stop_loss * 5)  # 5:1 Risk-Reward Ratio
            position_size = (self.capital * self.risk_per_trade) / stop_loss
            
            # Simulate trade result
            self.capital += (take_profit - entry_price) * position_size
            self.trades.append({
                "entry": entry_price,
                "exit": take_profit,
                "profit": (take_profit - entry_price) * position_size
            })
        return self.capital, self.trades

# Load historical data
try:
    data = pd.read_csv("bitcoin_prices.csv")
    data["Time"] = pd.to_datetime(data["Time"])
    data = data.sort_values("Time")

    # Resample to 4H timeframe
    data_resampled = data.set_index("Time").resample("4H").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna().reset_index()

    # Execute strategy
    strategy = TradingStrategy(data_resampled)
    final_capital, trades = strategy.run_strategy()

    # Print results
    print(f"Final Capital: {final_capital} USDT")
    print(f"Total Trades: {len(trades)}")
except Exception as e:
    print(f"Error loading or processing data: {e}")
