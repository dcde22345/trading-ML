from datetime import datetime

# type: True -> long, False -> short
class Position:
    def __init__(self,backtesting: bool, position_id: int, condition: bool):
        # 基本資料
        self.backtesting = backtesting
        self.position_id = position_id
        self.condition = condition  # long (True) or short (False)

        # Position參數
        self.entry_price = None
        self.quantity = None  # position size
        self.entry_date = None
        self.exit_price = None
        self.exit_date = None
        self.sl = None
        self.sp = None
        self.pnl = None

    # 建立倉位並return 這個倉位的id, condition, entry_price, entry_date的資訊
    def open_position(self, price: float, quantity: int, date: datetime, sl: float, sp: float):
        """建立新倉位"""
        if self.backtesting:
            # 建立測試倉位
            self.entry_price = price
            self.entry_date = date
            self.quantity = quantity
            self.sl = price # 停損點
            self.sp = price # 停利點

            return {"type": f"entry {'long' if self.condition else 'short'}", "position_id": self.position_id,"condition": self.condition,"entry_price": self.entry_price,"entry_date": self.entry_date}
        else:
            # 建立真實倉位
            pass

    # 關閉倉位並且返回position的total pnl與基本資訊
    def close_position(self, price: float, date: datetime):
        """關閉倉位並計算 PnL"""
        if self.backtesting:
            # 關閉測試倉位
            self.exit_price = price
            self.exit_date = date
            
            if self.condition:  # Long position
                self.pnl = (self.exit_price - self.entry_price) * self.quantity
            else:  # Short position
                self.pnl = (self.entry_price - self.exit_price) * self.quantity
            return {"type": f"exit {'long' if self.condition else 'short'}", "position_id": self.position_id, "close_price": self.exit_price, "close_date": self.exit_date, "pnl": self.pnl}
        else:
            # 關閉真實倉位
            pass
# 建倉
# 平倉
# 爆倉