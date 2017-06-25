"""
样本策略
"""

import dovahkiin as dk
from dovahkiin.strategy import StrategyBase
from dovahkiin.feature.Amibroker import *
from dovahkiin.feature.StrategyUtility import *
from dovahkiin.OptimizeParam import OptimizeParam


class CrossOver(StrategyBase):

    """
    样本策略，均线交叉
    """

    params = {}
    params["stop_ratio"] = OptimizeParam("stop", 10, 0.1, 12, 0.1)
    params["short_ratio"] = OptimizeParam("shortPeriod", 10, 2, 30, 1)
    params["longPeriod"] = OptimizeParam("longPeriod", 50, 20, 60, 1)
    params["threshold_multiplier"] = OptimizeParam("threshold_multiplier", 2, 0.1, 4, 0.1)
    params["linreg_lookback"] = OptimizeParam("linreg_lookback", 50, 10, 60, 1)
    params["cond3_coeff"] = OptimizeParam("cond3_coeff", 2, 1, 4, 0.25)


    def __init__(self, dataframe, params=None):
        super().__init__(dataframe, params)

    def strategy(self):

        """
        策略的逻辑
        """

        recentATR = ATR(self.C, self.H, self.L, 100, False)
        threshold = self.optimize("threshold_multiplier") * recentATR

        short_period = int(self.optimize("short_ratio") * self.optimize("longPeriod"))
        short_line = MA(self.C, short_period)
        long_line = MA(self.C, self.optimize("longPeriod"))

        close_slope = LinRegSlope(self.C, short_period)
        short_slope = LinRegSlope(short_line, self.optimize("linreg_lookback"))

        bcond1_1 = self.C > long_line and self.C > short_line
        bcond1_2 = long_line < short_line
        bcond1_3 = abs(short_line - long_line) > threshold
        bcond1 = bcond1_1 and bcond1_2 and bcond1_3

        

        sigs = MoveStop(self.C, self.BUY, self.SHORT, self.SELL | self.COVER, 100)
        return sigs.values
