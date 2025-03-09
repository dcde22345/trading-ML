import talib
import numpy as np

from datetime import datetime

from ..backtesting import BackTesting
from ..position import Position

class test_MACD_SAR_EMA200(BackTesting):
    def __init__(self, init_balance: float, quantity: int, parymid: int):
        super().__init__(init_balance, quantity, parymid)

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
                self._trading_strategy(long_condition=long_condition, short_condition=short_condition, close_price=close_price, date=date, sar=sar, risk_reward=risk_reward)


    # 先以parymid = 1的方法實作
    def _trading_strategy(self, long_condition:bool, short_condition: bool, date: datetime, close_price:float, sar: float,risk_reward: float):
        """基於MACD + SAR + EMA200的交易策略"""

        # 檢查是否有空頭倉位，如果有就平倉
        if long_condition:
            # 是否有position
            for holding_position in self.holding_positions:
                # position.condition是否為short
                if holding_position.condition == True:
                    # 如果是`的話作平倉
                    position_pnl = holding_position.test_close_position(close_price, date)
                    # 計算pnl
                    self.balance += position_pnl

                # 紀錄trading_log
                self.trading_log.append({"id": holding_position.position_id, "type": "close_short", "price": close_price, "pnl": position_pnl})

            # 檢查目前的positions是否小於parymid
            if len(self.holding_positions) < self.parymid:
                # 進行開倉
                self.position_id += 1

                # 建立新的position
                new_position = Position(position_id=self.position_id, condition=True) # condition: True(long) or False(short)
                new_position.test_open_position(price=close_price, quantity=self.quantity, date=date)

                # 計算balance, position_size
                self.balance -= (close_price * self.quantity)

                # 記錄到trading_log
                self.trading_log.append({"id": new_position.position_id,"type": "open_long", "price": close_price, "pnl": None})
                # 將目前的position加入positions
                self.holding_positions.append(new_position)

            # 出場邏輯
            stop_loss = sar
            stop_profit = close_price + ((close_price - sar) * risk_reward)

            # 要獲取時間顆粒度更小的price來做資訊