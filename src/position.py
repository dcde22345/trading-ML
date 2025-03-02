from datetime import datetime

# type: True -> long, False -> short
class Position:
    def __init__(self, position_id: int, condition: bool):
        self.position_id = position_id
        self.condition = condition  # long (True) or short (False)
        self.entry_price = None
        self.quantity = None  # position size
        self.entry_date = None
        self.exit_price = None
        self.exit_date = None
        self.pnl = None

    def test_open_position(self, price: float, quantity: int,date: datetime):
        """建立新倉位"""
        self.entry_price = price
        self.entry_date = date
        self.quantity = quantity
        print(f"Position {self.position_id} opened at {self.entry_price} on {self.entry_date}")
        print("Condition not met, position not opened.")

    def test_close_position(self, price: float, date: datetime):
        """關閉倉位並計算 PnL"""
        self.exit_price = price
        self.exit_date = date

        if self.condition:  # Long position
            self.pnl = (self.exit_price - self.entry_price) * self.quantity
        else:  # Short position
            self.pnl = (self.entry_price - self.exit_price) * self.quantity

        print(f"Position {self.position_id} closed at {self.exit_price} on {self.exit_date}, PnL: {self.pnl}")
# 建倉
# 平倉
# 爆倉