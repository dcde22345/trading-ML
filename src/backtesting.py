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

from .strategy import Strategy


class BackTesting:
    def __init__(self, strategy: callable,init_balance: float = 10000, unit: float = 10, parymid: int = 1):
        self.strategy = strategy # 交易策略
        self.balance: float = init_balance
        self.trading_log: pd.DataFrame = None
        self.unit = unit
        self.parymid = parymid

    # 拿過去的data，並且在每一個K bar做一次stategy
    # return sharpe ratio, total pnl
    def simulate(self, symbol, timeframe: int, start_date: str, end_date: str, *args, **kwargs) -> list:
        trading_log_list = []
        historical_data = self._get_historical_data(symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date)
        
        # 利用strategy名稱獲得lookback長度
        lookback = Strategy.get_lookback(self.strategy.__name__)

        # 每次傳入lookback長的data
        for i in range(len(historical_data) - lookback):
            trading_info = self.strategy(df=historical_data.iloc[i:lookback + i, :], *args, **kwargs)
            trading_log_list.append(trading_info)
            
        # 將trading_log整理成df
        trading_log_list = np.concatenate(trading_log_list)

        # 轉換成df後分成entry_df和exit_df
        trading_log_df = pd.DataFrame(trading_log_list.tolist())
        
        entry_df = trading_log_df[trading_log_df['type'].str.contains('entry')].dropna(axis=1, how='all').set_index("position_id")
        exit_df = trading_log_df[trading_log_df['type'].str.contains('exit')].dropna(axis=1, how='all').set_index("position_id")

        # 進行合併
        trading_log_df = entry_df.join(exit_df, on=['position_id'], lsuffix="_entry", rsuffix="_exit")
        
        # 確認時間格式設定完成
        trading_log_df['entry_date'] = pd.to_datetime(trading_log_df['entry_date'])
        trading_log_df['close_date'] = pd.to_datetime(trading_log_df['close_date'])
        
        self.trading_log = trading_log_df

    def _get_historical_data(self, symbol, timeframe: int, start_date: str, end_date: str):
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