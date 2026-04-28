from .moving_average import MovingAverageCrossStrategy
from .breakout import BreakoutStrategy
from .single_stock_research import SingleStockResearchSignalStrategy

STRATEGIES = {
    "ma_cross": MovingAverageCrossStrategy,
    "breakout": BreakoutStrategy,
    "single_stock_research": SingleStockResearchSignalStrategy,
}
