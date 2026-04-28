from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import csv


@dataclass
class PaperOrder:
    symbol: str
    side: str
    qty: int
    price: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    note: str = ""


@dataclass
class PaperAccount:
    cash: float = 1_000_000.0
    positions: dict[str, int] = field(default_factory=dict)
    orders: list[PaperOrder] = field(default_factory=list)

    def submit_order(self, symbol: str, side: str, qty: int, price: float) -> PaperOrder:
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if qty <= 0 or price <= 0:
            raise ValueError("qty and price must be positive")
        cost = qty * price
        if side == "BUY":
            if cost > self.cash:
                raise ValueError("paper account has insufficient cash")
            self.cash -= cost
            self.positions[symbol] = self.positions.get(symbol, 0) + qty
        else:
            if self.positions.get(symbol, 0) < qty:
                raise ValueError("paper account has insufficient position")
            self.cash += cost
            self.positions[symbol] -= qty
        order = PaperOrder(symbol=symbol, side=side, qty=qty, price=price)
        self.orders.append(order)
        return order

    def export_log(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["timestamp", "symbol", "side", "qty", "price", "cash_after", "position_after", "note"],
            )
            writer.writeheader()
            running_positions: dict[str, int] = {}
            running_cash = 1_000_000.0
            for order in self.orders:
                if order.side == "BUY":
                    running_cash -= order.qty * order.price
                    running_positions[order.symbol] = running_positions.get(order.symbol, 0) + order.qty
                else:
                    running_cash += order.qty * order.price
                    running_positions[order.symbol] = running_positions.get(order.symbol, 0) - order.qty
                writer.writerow(
                    {
                        "timestamp": order.timestamp,
                        "symbol": order.symbol,
                        "side": order.side,
                        "qty": order.qty,
                        "price": order.price,
                        "cash_after": round(running_cash, 2),
                        "position_after": running_positions.get(order.symbol, 0),
                        "note": order.note,
                    }
                )
        return output_path
