import talib
import numpy as np

from datetime import datetime

from ..backtesting import BackTesting
from ..position import Position

class test_MACD_SAR_EMA200(BackTesting):
    def __init__(self, init_balance: float, quantity: float):
        super().__init__(init_balance, quantity)

    def _simulate(self, historical_data):
        """執行回測"""
        for i in range(200, len(historical_data)):  # 從第200根K線開始（避免EMA不足）
            date = historical_data['time'].iloc[i]
            close_price = historical_data['close'].iloc[i]
            ema_length = 200
            macd_fast = 12
            macd_slow = 26
            macd_signal = 9
            sar_start = 0.02
            sar_step = 0.02
            sar_max = 0.2
            risk_reward = 1.0  # 風險報酬 1:1

            # 計算技術指標
            ema200 = talib.EMA(historical_data['close'], timeperiod=ema_length).iloc[i]
            macd, macd_signal, _ = talib.MACD(historical_data['close'], fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal)
            sar = talib.SAR(historical_data['high'], historical_data['low'], acceleration=sar_start, maximum=sar_max).iloc[i]

            macd_line = macd.iloc[i]
            signal_line = macd_signal.iloc[i]

            long_condition = close_price > ema200 and sar < close_price and macd_line > signal_line
            short_condition = close_price < ema200 and sar > close_price and macd_line < signal_line


            if self.balance > 0:
                self._trading_strategy(long_condition=long_condition, short_condition=short_condition, close_price=close_price, date=date, index=i)


    # 先以parymid = 1的方法實作
    def _trading_strategy(self, long_condition:bool, short_condition: bool, date: datetime, close_price:float, index: int):
        """基於MACD + SAR + EMA200的交易策略"""

        # 檢查是否有空頭倉位，如果有就平倉
        if long_condition:
            # 是否有position
            # position.condition是否為short
            if self.holding_positions[-1].condition is False:
                # 如果是的話作平倉
                # 計算pnl
                position_pnl = self.holding_positions[-1].test_close_position(close_price, date)
                self.balance += position_pnl
                self.pnl += position_pnl

                # 紀錄trading_log
                self.trading_log.append({"id": self.position_id, "type": "close_short", "price": close_price, "pnl": position_pnl})

            # 進行開倉
                # position_id加一
                self.position_id += 1
                # position_size加1
                self.position_size += 1

                # 建立新的position
                new_position = Position(position_id=self.position_id, condition=True) # condition: True(long) or False(short)
                new_position.test_open_position(price=close_price, quantity=self.quantity, date=date)

                # 計算balance, position_size
                self.balance -= (close_price * self.quantity)
                self.position_size += 1

                # 記錄到trading_log
                self.trading_log.append({"id": self.position_id,"type": "long", "price": close_price, "profit": 0})

                # 將目前的position加入positions
                self.holding_positions.append(new_position)

        # 如果是空頭狀態的話
        if short_condition:
            # 檢查是否有position
            # 檢查position是否為True
            if self.holding_positions and self.holding_positions[-1].type is True:  # 檢查是否有多頭倉位
                # 閉倉並計算profit
                position_pnl = self.holding_positions[-1].test_close_position(close_price, date).pnl
                self.balance += position_pnl
                self.pnl += position_pnl

                # 紀錄到trading_log
                self.trading_log.append({"type": "close_long", "price": close_price, "pnl": position_pnl})
            
            # 如果是空倉
            if not self.holding_positions or self.holding_positions[-1].type is True:
                position_size = self.balance / close_price
                new_position = Position(index, index, False, close_price, position_size, date)
                new_position.open_position(True, close_price, date)
                self.balance -= position_size * close_price
                self.holding_positions.append(new_position)
                self.trading_log.append({"type": "short", "price": close_price, "profit": 0})