from dataclasses import dataclass
from ..core import Keys

@dataclass
class GMM_Regime_Options:
    """Holds a group of input params for `GMM_Regime` class."""

    # -- Options for ML
    GMM_N_COMPONENTS:int = 3 # Number of regimes, BEARISH, NEUTRAL, BULLISH
    GMM_COVARIANCE_TYPE:str = "full" # Covariance type - 'full', 'tied', 'diag', 'spherical'
    GMM_MAX_ITER:int = 100 # Maximum iterations for EM algorithms
    GMM_N_INIT:int = 10 # Number of initializations
    GMM_RANDOM_STATE:int = 42 # For reproducibility

    # -- Options for backtesting
    FEATURES:list[str] = [
        Keys.Data.Indicator.YZ_VOL,
        Keys.Data.Indicator.SMA_CROSSOVER_NORM
    ]
    MIN_TRAINING_DAYS:int = 252
    REFIT_FREQUENCY:int = 63
    MIN_CLUSTER_SAMPLES:int = 10