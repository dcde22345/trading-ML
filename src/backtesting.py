import MetaTrader5 as mt5
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import talib

from tqdm import tqdm
from IPython.display import display
from abc import abstractmethod

from .position import Position

model_path = "../models"

class BackTesting:
    def __init__(self, init_balance: float):
        self.balance: float = init_balance
        self.trading_log: list[dict] = []
        self.positions: list[Position] = []

    def run(self, symbol, timeframe, start_date, end_date):
        data = self._get_historical_data(symbol, timeframe, start_date, end_date)
        model = self._load_model(symbol=symbol)
        # 如果data和model都不為空
        if data is not None and model is not None:
                self._simulate(data=data, model=model)
                print(f"最終資金: {self.balance}")
                
                # 轉換交易日誌為 DataFrame
                trade_df = pd.DataFrame(self.trading_log)
                if not trade_df.empty:
                    
                    display(name="回測交易結果", dataframe=trade_df)

                    # 繪製回測績效
                    trade_df['cum_profit'] = trade_df['profit'].cumsum()
                    plt.figure(figsize=(10, 5))
                    plt.plot(trade_df.index, trade_df['cum_profit'], marker='o', linestyle='-')
                    plt.title("回測績效")
                    plt.xlabel("交易次數")
                    plt.ylabel("累積盈利")
                    plt.grid()
                    plt.show()


    
    def _get_historical_data(self, symbol, timeframe, start_date, end_date):
        # 初始化 MT5
        if not mt5.initialize(path="C:\\MT5\\terminal64.exe"):
            print("MT5 初始化失敗")
            quit()

        """獲取歷史數據"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    
        rates = mt5.copy_rates_range(symbol, timeframe, start, end)
        
        if rates is None:
            print("無法獲取歷史數據")
            return None
    
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    @abstractmethod         
    def _simulate(self):        
        return NotImplemented
    
    @ abstractmethod
    def _trading_strategy(self):
        return NotImplemented