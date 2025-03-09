import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Diagram:
    def __init__(self, symbol: str,df: pd.DataFrame, trading_log: pd.DataFrame):
        self.symbol = symbol
        self.df = df
        self.trading_log = trading_log

    def result(self):
        # 取得df的close與時段
        close: pd.Series = self.df['close']
        time: pd.Series = self.df['time']
        long_condition_df: pd.DataFrame = self.trading_log[self.trading_log['condition'] == True]
        short_condition_df: pd.DataFrame = self.trading_log[self.trading_log['condition'] == False]

        # figure，x軸為時間，y軸為價格，標題為symbol
        plt.figure(figsize=(10, 5))
        plt.plot(time, close, linestyle='-')
        plt.title(f'{self.symbol}, {time.iloc[0]}-{time.iloc[-1]}')
        plt.xlabel("時間")
        plt.ylabel("價格")

        # 在有trainding的點上，long為藍色，short為紅色，這兩種顏色會有買和賣的標記
        # long標記點
        print(len(long_condition_df['entry_date']))
        print(len(long_condition_df['entry_price']))
        plt.scatter(long_condition_df['entry_date'], long_condition_df['entry_price'], color='blue', label='Long Entry', marker='^', s=100)
        plt.scatter(long_condition_df['close_date'], long_condition_df['close_price'], color='cyan', label="Long Exit", marker='v', s=100)

        # short標記點
        plt.scatter(short_condition_df['entry_date'], long_condition_df['entry_price'],  color='red', label="Short Entry", marker='^', s=100)
        plt.scatter(short_condition_df['close_date'], short_condition_df['close_price'], color='orange', label="Short Exit", marker='v', s=100)

        # # 轉換交易日誌為 DataFrame
        plt.show()




        # trade_df = pd.DataFrame(self.trading_log)
        # if not trade_df.empty:

        #     # 繪製回測績效
        #     trade_df['cum_profit'] = trade_df['profit'].cumsum()
        #     plt.figure(figsize=(10, 5))
        #     plt.plot(trade_df.index, trade_df['cum_profit'], marker='o', linestyle='-')
        #     plt.title("回測績效")
        #     plt.xlabel("交易次數")
        #     plt.ylabel("累積盈利")
        #     plt.grid()
        #     plt.show()

    def pnl(self):
        pass
            
    # 交易圖表
    # pnl圖表