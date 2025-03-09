import talib
import pandas as pd
import numpy as np

from datetime import datetime

from .position import Position

# 儲存多個Strategy
class Strategy:
    def __init__(self, unit: float = 100, backtesting: bool = True, parymid: int= 1):
        self.backtesting = backtesting # 預設為backtesting模式
        self.parymid = parymid
        self.position_list: list[Position] = []
        self.unit = unit
        self.sl = 0
        self.sp = 0
        self.position_id = 0

    # 取得lookback長度
    @staticmethod
    def get_lookback(strategy_name: str) -> int:
        if strategy_name == 'macd_sar_ema200':
            return 200
        
    # 先以parymid = 1的方法實作
    def macd_sar_ema200(self, df: pd.DataFrame) -> list:
        """基於MACD + SAR + EMA200的交易策略"""
        trade_info = []

        # 參數設定
        macd_fast = 12
        macd_slow = 26
        macd_signal = 9
        sar_acceleration = 0.02
        sar_max = 0.2
        ema_length = 200
        risk_award = 1
        
        # 產生len(df["close"])的值
        macd_line, signal_line, _ = talib.MACD(df['close'], fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal)
        sar = talib.SAR(high=df['high'], low=df['low'], acceleration=sar_acceleration, maximum=sar_max)
        ema_200 = talib.EMA(df['close'], timeperiod=ema_length)

        # 最新K bar資訊
        now_k = df.iloc[-1, :]
        
        # 最新的ema200
        now_ema_200 = ema_200.iloc[-1]

        # 最新的sar
        now_sar = sar.iloc[-1]

        # macd_line和signal_line
        bullish_market = (macd_line > signal_line).iloc[-1]

        long_condition = now_k['close'] < now_ema_200 and now_sar < now_k['close'] and bullish_market
        short_condition = now_k['close'] > now_ema_200 and now_sar > now_k['close'] and not bullish_market

        # 多頭市場的話
        # 檢查是否有空頭倉位，如果有就全部close掉，然後建立多倉倉位
        if long_condition:
            # 查看目前是否持有position
            if len(self.position_list) > 0:
                # 持有position的話，檢查裡面的單子，若有空單則close掉
                for position in self.position_list:
                    if position.condition == False: # 若空單的話則
                        trade_info.append(position.close_position(now_k['close'], now_k['time']))
                        self.position_list.pop() # pop 掉最後一個
            
            

            if len(self.position_list) < self.parymid:
                self.position_id += 1
                
                # 建立多倉倉位
                new_position = Position(backtesting=self.backtesting, position_id=self.position_id, condition=True)
                
                # 計算sp與sl
                sp = now_k['close'] + (now_k['close'] - now_sar) * risk_award
                sl = now_k['close'] - (now_k['close'] - now_sar) * risk_award

                open = new_position.open_position(now_k['close'], self.unit, now_k['time'], sl=sl, sp=sp)
                
                trade_info.append(open)
                self.position_list.append(new_position)

        # 空頭市場的話
        # 檢查是否有多頭倉位，如果有就全部 close 掉，然後建立空倉倉位
        if short_condition:
            # 查看目前是否持有 position
            if len(self.position_list) > 0:
                # 持有 position 的話，檢查裡面的單子，若有多單則 close 掉
                for position in self.position_list:
                    if position.condition == True:  # 多單條件為 True，需關閉
                        trade_info.append(position.close_position(now_k['close'], now_k['time']))
                        self.position_list.pop() # pop 掉最後一個

            if len(self.position_list) < self.parymid:
                self.position_id += 1 
                # 建立空倉倉位
                new_position = Position(backtesting=self.backtesting, position_id=self.position_id, condition=False)
                
                # 計算sp與sl
                sp = now_k['close'] - (now_sar - now_k['close']) * risk_award
                sl = now_k['close'] + (now_sar - now_k['close']) * risk_award

                open = new_position.open_position(now_k['close'], self.unit, now_k['time'], sl=sl, sp=sp)                

                # trade_info
                trade_info.append(open)
                self.position_list.append(new_position)

        # 如果目前的價錢超過sl或st價格，就賣掉
        for position in self.position_list:
            if position.condition and (now_k['close'] > position.sp or now_k['close'] < position.sl):
                trade_info.append(position.close_position(now_k['close'], now_k['time']))
                self.position_list.pop() # pop 掉最後一個
                
            if not position.condition and (now_k['close'] < position.sp or now_k['close'] > position.sl):
                trade_info.append(position.close_position(now_k['close'], now_k['time']))
                self.position_list.pop() # pop 掉最後一個

        # 回傳一天的trade_info
        return trade_info