# Calculate all indicators for PyHamster

import numpy as np
import pandas as pd
import pandas_ta as ta
from hurst import compute_Hc
from numba import jit
from ..core import Keys, MissingDataError
from ..utils import Logger
from . import IndicatorOptions

class Indicator:
    """Single responsibility: Calculates all technical and statistical indicators."""

    def __init__(self, options:IndicatorOptions|None = IndicatorOptions) -> None:
        self._logger = Logger.for_context(Indicator)
        self.options = options or IndicatorOptions()
    
    def calculate_all_indicators(self, data:pd.DataFrame, ticker:str|None = None) -> pd.DataFrame:
        """
        Calculates all indicators and append to the DataFrame

        Args:
            data (pd.DataFrame): data containing OHLCV data
            ticker (str|None): ticker name
        
        Returns:
            pd.DataFrame: DataFrame appended with all indicators
        """

        data_result = data.copy() # Prevent accidental modification due to passed by ref

        # -- Validate
        missing = [c for c in self.options.required_columns if c not in data_result.columns]
        if missing:
            raise MissingDataError(f"DataFrame: '{data}' is missing data column: '{missing}'.")
        
        # -- Calculate technical indicators
        data_result = self.calculate_technical_indicators(data=data_result, ticker=ticker)

        # -- Calculate statistical indicators
        
        return data_result
    
    def calculate_technical_indicators(self, data:pd.DataFrame, ticker:str|None = None) -> pd.DataFrame:
        """
        Calculates all technical indicators and append to the DataFrame

        Args:
            data (pd.DataFrame): data containing OHLCV data
            ticker (str|None): ticker name
        
        Returns:
            pd.DataFrame: DataFrame appended with all technical indicators
        """

        self._logger.info(
            f"Calculating technical indicators"
            f"{f' for {ticker}' if ticker else ''}"
        )

        data_result = data.copy()

        # -- Simple Moving Averages
        for period in self.options.sma_periods:
            data_result[f"{Keys.Data.Indicator.SMA}_{period}"] = ta.sma(
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Exponential Moving Averages
        for period in self.options.ema_periods:
            data_result[f"{Keys.Data.Indicator.EMA}_{period}"] = ta.ema(
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Average True Ranges
        for period in self.options.atr_periods:
            data_result[f"{Keys.Data.Indicator.ATR}_{period}"] = ta.atr(
                high=data_result[Keys.Data.Market.HIGH],
                low=data_result[Keys.Data.Market.LOW],
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Average True Range Percentile
        data_result[Keys.Data.Indicator.ATR_PERCENTILE] = Indicator._calculate_atr_percentile(
            atr=data_result[Keys.Data.Indicator.ATR.period(self.options.atr_percentile)],
            period=self.options.atr_percentile_period,
            jit_threshold=self.options.atr_percentile_jit_threshold
        )

        # -- Relative Strength Index
        for period in self.options.rsi_periods:
            data_result[f"{Keys.Data.Indicator.RSI}_{period}"] = ta.rsi(
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Momentum
        for period in self.options.mom_periods:
            data_result[f"{Keys.Data.Indicator.MOM}_{period}"] = ta.mom(
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Rate of Change
        for period in self.options.roc_periods:
            data_result[f"{Keys.Data.Indicator.ROC}_{period}"] = ta.roc(
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Williams %R
        for period in self.options.willr_periods:
            data_result[f"{Keys.Data.Indicator.WILLR}_{period}"] = ta.willr(
                high=data_result[Keys.Data.Market.HIGH],
                low=data_result[Keys.Data.Market.LOW],
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )

        # -- Commodity Channel Index
        for period in self.options.cci_periods:
            data_result[f"{Keys.Data.Indicator.CCI}_{period}"] = ta.cci(
                high=data_result[Keys.Data.Market.HIGH],
                low=data_result[Keys.Data.Market.LOW],
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )
        
        # -- Choppiness Index
        for period in self.options.chop_periods:
            data_result[f"{Keys.Data.Indicator.CHOP}_{period}"] = ta.chop(
                high=data_result[Keys.Data.Market.HIGH],
                low=data_result[Keys.Data.Market.LOW],
                close=data_result[Keys.Data.Market.CLOSE],
                length=period
            )

        # -- Moving Average Convergence/Divergence
        macd = ta.macd(
            close=data_result[Keys.Data.Market.CLOSE]
        )
        if macd is not None:
            data_result = pd.concat([data_result, macd], axis=1)
        
        # -- Bollinger Bands
        bbands = ta.bbands(
            close=data_result[Keys.Data.Market.CLOSE],
            length=self.options.bbands_period,
            std=self.options.bbands_std
        )
        if bbands is not None:
            data_result = pd.concat([data_result, bbands], axis=1)
        
        # -- Stochastic Oscillator
        stoch = ta.stoch(
            high=data_result[Keys.Data.Market.HIGH],
            low=data_result[Keys.Data.Market.LOW],
            close=data_result[Keys.Data.Market.CLOSE]
        )
        if stoch is not None:
            data_result = pd.concat([data_result, stoch], axis=1)
        
        # -- Average Directional Index
        adx = ta.adx(
            high=data_result[Keys.Data.Market.HIGH],
            low=data_result[Keys.Data.Market.LOW],
            close=data_result[Keys.Data.Market.CLOSE]
        )
        if adx is not None:
            data_result = pd.concat([data_result, adx], axis=1)
        
        # -- On-Balance Volume
        data_result[Keys.Data.Indicator.OBV] = ta.obv(
            close=data_result[Keys.Data.Market.CLOSE],
            volume=data_result[Keys.Data.Market.VOLUME]
        )

        # -- Volume Weighted Average Price
        data_result[Keys.Data.Indicator.VWAP] = ta.vwap(
            high=data_result[Keys.Data.Market.HIGH],
            low=data_result[Keys.Data.Market.LOW],
            close=data_result[Keys.Data.Market.CLOSE],
            volume=data_result[Keys.Data.Market.VOLUME]
        )

        # -- Close-to-Close Returns
        data_result[Keys.Data.Indicator.RETURNS_CC] = data_result[Keys.Data.Market.CLOSE].pct_change()
        
        # -- Open-to-Open Returns
        data_result[Keys.Data.Indicator.RETURNS_OO] = data_result[Keys.Data.Market.OPEN].pct_change()

        # -- Forward Returns
        data_result[Keys.Data.Indicator.RETURNS_FW] = data_result[Keys.Data.Market.OPEN].shift(-1) / data_result[Keys.Data.Market.OPEN] - 1
        
        # -- Historical Volatility
        data_result[Keys.Data.Indicator.HIST_VOL] = Indicator._calculate_historical_volatility(
            returns=data_result[Keys.Data.Indicator.RETURNS_CC],
            period=self.options.historical_volatility_period
        )

        # -- Volume Indicators
        data_result[Keys.Data.Indicator.VOL_SMA] = data_result[Keys.Data.Market.VOLUME].rolling(window=self.options.vol_sma_period).mean()
        data_result[Keys.Data.Indicator.VOL_RATIO] = data_result[Keys.Data.Market.VOLUME] / data_result[Keys.Data.Indicator.VOL_SMA]

        # -- Market Structure
        data_result[Keys.Data.Indicator.HIGHER_HIGH] = (
            (data_result[Keys.Data.Market.HIGH] > data_result[Keys.Data.Market.HIGH].shift(1))
            & (data_result[Keys.Data.Market.HIGH].shift(1) > data_result[Keys.Data.Market.HIGH].shift(2))
        )
        data_result[Keys.Data.Indicator.LOWER_LOW] = (
            (data_result[Keys.Data.Market.LOW] < data_result[Keys.Data.Market.LOW].shift(1))
            & (data_result[Keys.Data.Market.LOW].shift(1) < data_result[Keys.Data.Market.LOW].shift(2))
        )

        # -- Change of Character
        data_result[Keys.Data.Indicator.CHOCH] = Indicator._detect_choch(
            data=data_result,
            period=self.options.choch_period
        )

        self._logger.info(
            f"✓ All technical indicators calculated successfully"
            f"{f' for {ticker}' if ticker else ''}"
        )

        return data_result
    
    def calculate_statistical_indicators(self, data:pd.DataFrame, ticker:str|None = None) -> pd.DataFrame:
        """
        Calculates all statistical indicators and join them to the DataFrame

        Args:
            data (pd.DataFrame): data containing OHLCV data
            ticker (str): ticker name
        
        Returns:
            pd.DataFrame: dataframe updated with statistical indicators
        """
        
        self._logger.info(
            f"Calculating statistical indicators"
            f"{f' for {ticker}' if ticker else ''}"
        )

        data_result = data.copy()

        # -- Hurst Exponent
        data_result[Keys.Data.Indicator.HURST] = Indicator._calculate_hurst_exponent(
            series=data_result[Keys.Data.Market.CLOSE],
            period=self.options.hurst_period,
            method=self.options.hurst_method
        )

        # Yang Zhang Volatility
        data_result[Keys.Data.Indicator.YZ_VOL] = Indicator._calculate_yang_zhang_volatility(
            data=data_result,
            period=self.options.yz_period
        )

        # SMA Crossover Normalized
        data_result[Keys.Data.Indicator.SMA_CROSSOVER_NORM] = Indicator._calculate_sma_crossover_normalized(
            close=data_result[Keys.Data.Market.CLOSE],
            short_window=self.options.sma_short,
            long_window=self.options.sma_long
        )

        self._logger.info(
            f"✓ All statistical indicators calculated successfully"
            f"{f' for {ticker}' if ticker else ''}"
        )

        return data_result

    @staticmethod
    def _calculate_atr_percentile(atr:pd.Series, period:int, jit_threshold:int = 10000) -> pd.Series:
        if len(atr) >= jit_threshold:
            return Indicator._calculate_atr_percentile_largedata(atr=atr, period=period)
        else:
            return Indicator._calculate_atr_percentile_smalldata(atr=atr, period=period)

    @staticmethod
    def _calculate_atr_percentile_smalldata(atr:pd.Series, period:int) -> pd.Series:
        """
        For small sets of data

        For each day, look back period days of ATR and calculate what percentile the current ATR is in.
            If the ATR is very high compared to the last year, the percentile will be close to 100.
            If it is low, close to 0.
            If we do not have enough data, just return NaN
        
        Args:
            atr (pd.Series)
        """

        values = atr.values
        n = len(values)
        result = np.full(n, np.nan)
        windows = np.lib.stride_tricks.sliding_window_view(values, period)
        current = windows[:, -1]
        result[period - 1:] = (windows <= current[:, None]).sum(axis=1) / period * 100
        return pd.Series(result, index=atr.index)

    @staticmethod
    def _calculate_atr_percentile_largedata(atr:pd.Series, period:int) -> pd.Series:
        """
        For large sets of data

        For each day, look back period days of ATR and calculate what percentile the current ATR is in.
            If the ATR is very high compared to the last year, the percentile will be close to 100.
            If it is low, close to 0.
            If we do not have enough data, just return NaN
        
        Args:
            atr (pd.Series)
        """

        @jit(nopython=True)
        def _percentile_loop(values, period):
            n = len(values)
            result = np.full(n, np.nan)

            for i in range(period - 1, n):
                window = values[i - period + 1 : i + 1]
                current = window[-1]
                result[i] = np.sum(window <= current) / period * 100
            
            return result
        
        return pd.Series(_percentile_loop(atr.values, period), index=atr.index)
    
    @staticmethod
    def _calculate_historical_volatility(returns:pd.Series, period:int) -> pd.Series:
        return returns.rolling(window=period).std() * np.sqrt(252)
    
    @staticmethod
    def _calculate_hurst_exponent(series:pd.Series, period:int, method:str="price") -> pd.Series:
        """
        Args:
            series (pd.Series): 'Price' or 'Returns' series
            period (int): Rolling window size
            method (str): "price" (default), "RS", "DFA", or "DSOD"
        
        Returns:
            pd.Series
                H = 0.5 - Random Walk (Market behavior: No memory, purely random (Efficient Market Hypothesis))
                H > 0.5 - Persistent/Trending (Market behavior: Positive autocorrelation, trends continue)
                H < 0.5 - Anti-persistent/Mean-reverting (Market behavior: Negative autocorrelation, trends reverse)
        """

        def __hurst_calc(ts):
            try:
                ts = ts.dropna()
                if len(ts) < 20:
                    return 0.5
                
                H, _, _ = compute_Hc(ts, kind=method, simplified=True)
                return H
            except:
                return 0.5
            
        # Calculate rolling Hurst exponent
        return series.rolling(window=period).apply(__hurst_calc, raw=False)
    
    @staticmethod
    def _calculate_yang_zhang_volatility(data:pd.DataFrame, period:int) -> pd.Series:
        """
        Calculate Yang-Zhang volatility estimator with non-negativity guard.
        
        The Yang-Zhang estimator is a range-based volatility measure that combines:
        - Overnight volatility: (Open[t] / Close[t-1])
        - Open-to-Close volatility: (Close[t] / Open[t])
        - High-Low range: Rogers-Satchell component
        
        Formula:
        σ²_YZ = σ²_overnight + k·σ²_open_close + (1-k)·σ²_RS
        
        where:
        - σ²_overnight = Var(ln(O[t]/C[t-1]))
        - σ²_open_close = Var(ln(C[t]/O[t]))
        - σ²_RS = Rogers-Satchell = E[ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O)]
        - k = weighting factor ≈ 0.34 (standard value)
        
        IMPROVEMENT: Added np.clip to ensure variance is non-negative before sqrt
        to handle edge cases where floating point errors could produce tiny negative values.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Must contain Open, High, Low, Close columns
        period : int
            Rolling window size for volatility estimation
        
        Returns:
        --------
        pd.Series : Annualized Yang-Zhang volatility (always non-negative)
        """

        # Overnight component: ln(Open[t] / Close[t-1])
        overnight = np.log(data[Keys.Data.Market.OPEN] / data[Keys.Data.Market.CLOSE].shift(1))
        overnight_var = overnight.rolling(window=period, min_periods=period).var()
        
        # Open-to-Close component: ln(Close[t] / Open[t])
        open_close = np.log(data[Keys.Data.Market.CLOSE] / data[Keys.Data.Market.OPEN])
        open_close_var = open_close.rolling(window=period, min_periods=period).var()
        
        # Rogers-Satchell component
        # RS = E[ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O)]
        high_close = np.log(data[Keys.Data.Market.HIGH] / data[Keys.Data.Market.CLOSE])
        high_open = np.log(data[Keys.Data.Market.HIGH] / data[Keys.Data.Market.OPEN])
        low_close = np.log(data[Keys.Data.Market.LOW] / data[Keys.Data.Market.CLOSE])
        low_open = np.log(data[Keys.Data.Market.LOW] / data[Keys.Data.Market.OPEN])
        
        rs_component = high_close * high_open + low_close * low_open
        rs_var = rs_component.rolling(window=period, min_periods=period).mean()
        
        # Combine components with k = 0.34 (standard weighting)
        k = 0.34
        yang_zhang_var = overnight_var + k * open_close_var + (1 - k) * rs_var
        
        # Clip variance to ensure non-negativity before sqrt to prevent tiny negative variances (e.g., -1e-16)
        yang_zhang_var_clipped = np.clip(yang_zhang_var, 0, np.inf)
        
        # Convert to annualized standard deviation
        yang_zhang_vol = np.sqrt(yang_zhang_var_clipped * 252)
        
        return yang_zhang_vol
    
    @staticmethod
    def _calculate_sma_crossover_normalized(close:pd.Series, short_window:int, long_window:int) -> pd.Series:
        """
        Calculate normalized SMA crossover signal.
        
        Instead of binary crossover (1/-1), we use continuous normalized difference:
        Signal = (SMA_short - SMA_long) / SMA_long
        
        This captures:
        - Positive values: Short MA above long MA (bullish momentum)
        - Negative values: Short MA below long MA (bearish momentum)
        - Magnitude: Strength of trend
        
        Normalization by SMA_long makes the signal scale-invariant (works across
        different price levels and assets).
        
        Parameters:
        -----------
        close : pd.Series
            Close prices
        short_window : int
            Short moving average window
        long_window : int
            Long moving average window
        
        Returns:
        --------
        pd.Series : Normalized crossover signal (continuous, typically in [-0.1, 0.1])
        """

        # Calculate moving averages with minimum periods = window (prevent incomplete averages at the start)
        sma_short = close.rolling(window=short_window, min_periods=short_window).mean()
        sma_long = close.rolling(window=long_window, min_periods=long_window).mean()
        
        # Normalized difference: percentage above/below long MA (Dividing by sma_long makes it scale-invariant)
        crossover_signal = (sma_short - sma_long) / sma_long
        
        return crossover_signal
    
    @staticmethod
    def _detect_choch(data:pd.DataFrame, period:int) -> pd.Series:
        """
        Args:
            data (pd.DataFrame): DataFrame containing data
            lookback (int): 
            
        Returns:
            pd.Series indicating:
                1 for bullish CHoCH
                -1 for bearish CHoCH
                0 for no change
        """

        high = data[Keys.Data.Market.HIGH]
        low = data[Keys.Data.Market.LOW]
        close = data[Keys.Data.Market.CLOSE]

        # Find swing highs and lows
        swing_high = high.rolling(window=period, center=True).max()
        swing_low = low.rolling(window=period, center=True).min()

        choch = pd.Series(0, index=data.index)

        for i in range(period, len(data)):
            # Bullish CHoCH: price breaks above previous swing high in a downtrend
            if close.iloc[i] > swing_high.iloc[i-1] and close.iloc[i-5:i].mean() < close.iloc[i-10:i-5].mean():
                choch.iloc[i] = 1
            # Bearish CHoCH: price breaks below previous swing low in an uptrend
            elif close.iloc[i] < swing_low.iloc[i-1] and close.iloc[i-5:i].mean() > close.iloc[i-10:i-5].mean():
                choch.iloc[i] = -1
        
        return choch