class TradeInstruction:
    def __init__(self, product: str, amount: int, direction: str = "buy"):
        self.product = product
        self.amount = amount
        assert direction in ({'buy', 'sell'})
        self.direction = direction


class TradeRecord:
    def __init__(self, trade_instruction: TradeInstruction, trade_id: str, units: float, time: str):
        self.trade_id = trade_id
        self.product = trade_instruction.product
        self.cost = trade_instruction.amount
        self.time = time
        self.direction = trade_instruction.direction.upper()
        self.units = units

    def json(self):
        return {
            "trade_id": self.trade_id,
            "product": self.product,
            "cost": self.cost,
            "units": self.units,
            "time": self.time,
            "direction": self.direction
        }

