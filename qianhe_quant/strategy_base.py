from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class SignalFrame:
    data: pd.DataFrame
    signal_column: str = "signal"

    def validate(self) -> None:
        if self.signal_column not in self.data.columns:
            raise ValueError(f"Missing signal column: {self.signal_column}")
        allowed = {-1, 0, 1}
        actual = set(self.data[self.signal_column].dropna().astype(int).unique())
        if not actual.issubset(allowed):
            raise ValueError(f"Signal values must be in -1/0/1, got: {actual}")


class Strategy:
    name: str = "base"

    def generate_signals(self, df: pd.DataFrame) -> SignalFrame:
        raise NotImplementedError
