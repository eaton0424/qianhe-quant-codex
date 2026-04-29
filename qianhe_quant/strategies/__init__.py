from .moving_average import MovingAverageCrossStrategy
from .breakout import BreakoutStrategy
from .single_stock_research import SingleStockResearchSignalStrategy
from .weekly_factor_rotation import WeeklyFactorRotationStrategy

STRATEGIES = {
    "ma_cross": MovingAverageCrossStrategy,
    "breakout": BreakoutStrategy,
    "single_stock_research": SingleStockResearchSignalStrategy,
    "weekly_factor_rotation": WeeklyFactorRotationStrategy,
}
