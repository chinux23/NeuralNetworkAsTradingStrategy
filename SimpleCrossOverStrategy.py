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
    params["stop_ratio"] = OptimizeParam("stop", 9.7, 0.1, 12, 0.1)
    params["short_ratio"] = OptimizeParam("shortPeriod", 0.19, 0.1, 0.5, 0.01)
    params["longPeriod"] = OptimizeParam("longPeriod", 24, 20, 60, 1)
    params["threshold_multiplier"] = OptimizeParam("threshold_multiplier", 1.1, 0.1, 4, 0.1)
    params["linreg_lookback"] = OptimizeParam("linreg_lookback", 46, 10, 60, 1)
    params["linreg_slope_coeff"] = OptimizeParam("slope coeff", 0.15, 0.05, 0.5, 0.05)
    params["cond3_coeff"] = OptimizeParam("cond3_coeff", 1.75, 1, 4, 0.25)


    def __init__(self, dataframe, params=None):
        super().__init__(dataframe, params)

    def strategy(self):

        """
        策略的逻辑
        """

        recentATR = ATR(self.C, self.H, self.L, 100, False)
        threshold = self.optimize("threshold_multiplier") * recentATR
        linreg_slope_coeff = self.optimize("linreg_slope_coeff")
        linreg_lookback = int(self.optimize("linreg_lookback"))
        long_period = int(self.optimize("longPeriod"))

        short_period = int(self.optimize("short_ratio") * long_period)
        short_line = MA(self.C, short_period)
        long_line = MA(self.C, self.optimize("longPeriod"))

        close_slope = LinRegSlope(self.C, short_period)
        short_slope = LinRegSlope(short_line, linreg_lookback)

        # Long logic
        bcond1_1 = (self.C > long_line) & (self.C > short_line)
        bcond1_2 = long_line < short_line
        bcond1_3 = abs(short_line - long_line) > threshold
        bcond1 = bcond1_1 & bcond1_2 & bcond1_3
        bcond2 = LinRegSlope(self.C, short_period) > linreg_slope_coeff * self.optimize("cond3_coeff") * recentATR
        bcond3 = short_slope > linreg_slope_coeff * recentATR
        BSIG = bcond1 & bcond2 & bcond3

        # Short logic
        scond1_1 = (self.C < long_line) & (self.C < short_line)
        scond1_2 = long_line > short_line
        scond1_3 = abs(short_line - long_line) > threshold
        scond1 = scond1_1 & scond1_2 & scond1_3
        scond2 = LinRegSlope(self.C, short_period) < (-1) * linreg_slope_coeff * self.optimize("cond3_coeff") * recentATR
        scond3 = short_slope < (-1) * linreg_slope_coeff * recentATR
        SSIG = scond1 & scond2 & scond3

        self.BUY = BSIG
        self.SHORT = SSIG

        sigs = MoveStop(self.C, self.BUY, self.SHORT, self.SELL | self.COVER, 100)
        return sigs.values
