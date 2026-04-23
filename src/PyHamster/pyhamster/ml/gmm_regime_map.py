import pandas as pd
from typing import Dict
from dataclasses import dataclass

@dataclass
class GMM_RegimeMap:
    cluster_to_regime:Dict[int, str] # Maps cluster ID → regime name
    mean_returns:Dict[int, float] # Mean forward returns per cluster
    cluster_counts:Dict[int, int] # Number of samples per cluster
    training_end_date:pd.Timestamp # Last date of training data used
    is_valid:bool # Whether mapping has sufficient samples