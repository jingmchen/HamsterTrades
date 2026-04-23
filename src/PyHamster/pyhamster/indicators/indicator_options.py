# Options for Indicator class

from dataclasses import dataclass, field
from ..core import Keys

@dataclass
class IndicatorOptions:
    """Holds a group of input params for `Indicator` class."""

    # Required columns - else will throw an exception in Indicator class methods
    required_columns = [
        Keys.Data.Market.OPEN,
        Keys.Data.Market.HIGH,
        Keys.Data.Market.LOW,
        Keys.Data.Market.CLOSE,
        Keys.Data.Market.VOLUME
    ]

    # Period lists
    sma_periods:list[int] = field(default_factory=lambda: [20, 50, 200])
    ema_periods:list[int] = field(default_factory=lambda: [12, 20, 26, 50])
    atr_periods:list[int] = field(default_factory=lambda: [14, 50])
    rsi_periods:list[int] = field(default_factory=lambda: [14])
    mom_periods:list[int] = field(default_factory=lambda: [10])
    roc_periods:list[int] = field(default_factory=lambda: [10, 20, 50])
    willr_periods:list[int] = field(default_factory=lambda: [14])
    cci_periods:list[int] = field(default_factory=lambda: [20])
    chop_periods:list[int] = field(default_factory=lambda: [14])

    # ATR Percentile
    atr_percentile:int = 14
    atr_percentile_period:int = 252
    atr_percentile_jit_threshold:int = 10,000
    
    # BBands
    bbands_period:int = 20
    bbands_std:int = 2
    
    # Historical Volatility
    historical_volatility_period:int = 20

    # VOL SMA
    vol_sma_period:int=20

    # Change of Character
    choch_period:int = 20

    # Hurst Exponent
    hurst_period:int = 100
    hurst_method:str = "price"

    # Yang Zhang Volatility
    yz_period:int = 20

    # SMA Crossover Normalized
    sma_short:int = 20
    sma_long:int = 50