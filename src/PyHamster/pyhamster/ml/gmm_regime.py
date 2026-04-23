# Gaussian Mixed Model (GMM) for regime prediction in PyHamster

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Dict
from . import GMM_RegimeMap, GMM_Regime_Options
from ..core import Keys
from ..utils import Logger

class GMM_Regime:
    """
    GMM Regime Detection with STRICT walk-forward validation.
    
    For each prediction window:
    
    1. TRAIN SCALER: Fit StandardScaler on expanding training window
       → Learn mean/std of features from past data only
    
    2. TRAIN GMM: Fit GaussianMixture on normalized training features
       → Learn cluster centers and covariances from past data
    
    3. CREATE REGIME MAPPING: Analyze forward returns in training period
       → Determine which cluster = Bearish, Neutral, Bullish
       → CRITICAL: Use only training period forward returns
       → ROBUST: Handle underpopulated clusters (min sample threshold)
    
    4. FREEZE MODELS: Lock scaler, GMM, and regime mapping
    
    5. PREDICT: Use frozen models to predict regime for next period
    
    6. REFIT: After N days, repeat process with expanded training set
    
    This ensures predictions at time T use ONLY information available at T-1.
    """
    
    def __init__(
            self,
            *,
            options:GMM_Regime_Options|None = None
    ) -> None:
        self._logger = Logger.for_context(GMM_Regime)
        self.options = options or GMM_Regime_Options()
        self.previous_mapping = None  # Store last valid mapping for fallback
        
    def create_regime_mapping(
            self,
            *,
            X_train:np.ndarray,
            gmm_model:GaussianMixture,
            returns_fw:np.ndarray,
            train_end_date:pd.Timestamp
    ) -> GMM_RegimeMap:
        """
        Create regime mapping with robust cluster handling.
        
        Args:
            X_train (np.ndarray): Training features
            gmm_model (GaussianMixture): Fitted GMM model
            returns_fw (np.ndarray): Forward returns (already shifted)
            train_end_date (pd.Timestamp): End date of training period
        
        Returns:
            RegimeMap object with cluster -> regime mapping
        """
        # Predict clusters for training period
        #       - Assign each row in X_train to a cluster
        #       - Number of clusters depend on the number of Gaussian components (GMM_N_COMPONENTS)
        #       - Example outputs: [0, 0, 1, 1, 0, 2, 2, ...]
        clusters_all = gmm_model.predict(X_train)
        
        # CLEAN SLICING: Remove last observation from both arrays
        #       - Perform clean slicing on returns_fw as well to ensure it aligns with clusters_train
        clusters_train = clusters_all[:-1]
        returns_train = returns_fw[:-1]
        
        cluster_returns = {} # mean forward return per cluster
        cluster_counts = {} # number of samples per cluster
        
        # Loop over all possible GMM clusters
        for cluster_id in range(self.options.GMM_N_COMPONENTS):
            # Mask select samples that belong to the current cluster
            #       Example outputs: [False, True, False, True, ...]
            mask = clusters_train == cluster_id

            # Count how many samples fall into the current cluster
            count = mask.sum()
            cluster_counts[cluster_id] = count
            
            if count >= self.options.MIN_CLUSTER_SAMPLES:
                # Sufficient samples: calculate mean return
                cluster_returns[cluster_id] = returns_train[mask].mean()
            else:
                # Insufficient samples: use NaN (not 0.0)
                # This signals that the cluster is unreliable
                cluster_returns[cluster_id] = np.nan
        
        # Check if mapping is valid (all clusters have sufficient samples)
        valid_clusters = [cid for cid, ret in cluster_returns.items() if not np.isnan(ret)]
        is_valid = len(valid_clusters) == self.options.GMM_N_COMPONENTS
        
        if is_valid:
            # Sort by returns to assign regime labels
            sorted_clusters = sorted(cluster_returns.items(), key=lambda x: x[1])
            cluster_to_regime = {
                sorted_clusters[0][0]: Keys.Regime.BEARISH,
                sorted_clusters[1][0]: Keys.Regime.NEUTRAL,
                sorted_clusters[2][0]: Keys.Regime.BULLISH
            }
            
            self._logger.info(f"✓ Valid regime mapping created:")
            for cluster_id, regime in cluster_to_regime.items():
                self._logger.info(f"  Cluster {cluster_id} → {regime}: "
                      f"{cluster_counts[cluster_id]} obs, "
                      f"avg forward return: {cluster_returns[cluster_id]:.6f}")
        else:
            # Invalid mapping: try to use previous valid mapping
            if self.previous_mapping is not None and self.previous_mapping.is_valid:
                self._logger.info(f"⚠ Some clusters underpopulated, using previous fold's mapping")
                cluster_to_regime = self.previous_mapping.cluster_to_regime
                self._logger.info(f"  Carried forward mapping from {self.previous_mapping.training_end_date.date()}")
            else:
                # No previous mapping available: assign default ordering
                self._logger.info(f"⚠ Some clusters underpopulated and no previous mapping available")
                self._logger.info(f"  Using default cluster→regime assignment (0→Bearish, 1→Neutral, 2→Bullish)")
                cluster_to_regime = {
                    0: Keys.Regime.BEARISH,
                    1: Keys.Regime.NEUTRAL,
                    2: Keys.Regime.BULLISH
                }
            
            # Show which clusters are problematic
            for cluster_id, count in cluster_counts.items():
                status = "OK" if count >= self.options.MIN_CLUSTER_SAMPLES else "UNDERPOPULATED"
                ret_str = f"{cluster_returns[cluster_id]:.6f}" if not np.isnan(cluster_returns[cluster_id]) else "NaN"
                self._logger.info(f"  Cluster {cluster_id}: {count} obs, return: {ret_str} [{status}]")
        
        mapping = GMM_RegimeMap(
            cluster_to_regime=cluster_to_regime,
            mean_returns=cluster_returns,
            cluster_counts=cluster_counts,
            training_end_date=train_end_date,
            is_valid=is_valid
        )
        
        # Update previous mapping if current is valid
        if is_valid:
            self.previous_mapping = mapping
        
        return mapping
        
    def walk_forward_predict(self, data:pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Perform walk-forward regime prediction with NO look-ahead bias.
        
        Args:
            data (pd.DataFrame): DataFrame with features
        
        Returns:
            Tuple of:
            - df_clean: DataFrame with regime predictions
            - folds_executed: List of dictionaries with fold metadata for validation
        """
        self._logger.info("Starting GMM Regime Detection...")
        
        # ===== DATA CLEANING =====
        # Drop rows where features are NaN (e.g., initial period before windows fill)
        data_clean = data.dropna(subset=self.options.FEATURES).copy().reset_index()
        self._logger.info(f"Total observations after cleaning: {len(data_clean)}")
        
        # Initialize result columns
        data_clean[Keys.Data.Regime.GMM_CLUSTER] = np.nan  # GMM cluster ID (0, 1, 2, ...)
        data_clean[Keys.Data.Regime.GMM_LABEL] = None      # GMM cluster Label
        
        # ===== WALK-FORWARD SETUP =====
        min_train = self.options.MIN_TRAINING_DAYS
        refit_freq = self.options.REFIT_FREQUENCY
        
        self._logger.info(f"Walk-forward configuration:\n"
                    f"• Minimum training: {min_train} days\n"
                    f"• Refit frequency: {refit_freq} days\n"
                    f"• Min cluster samples: {self.options.MIN_CLUSTER_SAMPLES}\n"
                    f"• Total predictions needed: {len(data_clean) - min_train}")
        
        # Track all folds for validation
        folds_executed = []
        
        # Initialize model objects
        last_refit_idx = min_train
        scaler = None
        gmm_model = None
        regime_mapping = None
        
        fold_num = 0
        
        # ===== MAIN WALK-FORWARD LOOP =====
        for i in range(min_train, len(data_clean)):
            days_since_refit = i - last_refit_idx
            
            # ===== CHECK IF REFIT NEEDED =====
            if (scaler is None) or (days_since_refit >= refit_freq):
                fold_num += 1
                train_start = 0           # Expanding window: always start from beginning
                train_end = i             # End at current position
                
                self._logger.info(f"{'='*80}")
                self._logger.info(f"FOLD {fold_num}: Refitting models")
                self._logger.info(f"{'='*80}")
                self._logger.info(f"Training window: index {train_start} to {train_end-1}")
                self._logger.info(f"Training dates: {data_clean.loc[train_start, Keys.Data.Market.DATE].date()} to "
                      f"{data_clean.loc[train_end-1, Keys.Data.Market.DATE].date()}")
                self._logger.info(f"Training size: {train_end - train_start} days")
                
                # ===== STEP 1: FIT SCALER =====
                # Extract raw features from training window
                X_train_raw = data_clean.loc[train_start:train_end-1, self.options.FEATURES].values
                
                # Fit StandardScaler: learns mean and std from training data
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train_raw)
                
                self._logger.info(f"✓ Scaler fitted on {len(X_train_scaled)} training observations")
                
                # ===== STEP 2: FIT GMM =====
                # GaussianMixture finds K clusters in feature space
                gmm_model = GaussianMixture(
                    n_components=self.options.GMM_N_COMPONENTS,
                    covariance_type=self.options.GMM_COVARIANCE_TYPE,
                    max_iter=self.options.GMM_MAX_ITER,
                    n_init=self.options.GMM_N_INIT,
                    random_state=self.options.GMM_RANDOM_STATE
                )
                gmm_model.fit(X_train_scaled)
                
                self._logger.info(f"✓ GMM fitted (converged: {gmm_model.converged_})")
                
                # ===== STEP 3: CREATE REGIME MAPPING =====
                # Get forward returns for training period
                returns_forward_train = data_clean.loc[train_start:train_end-1, Keys.Data.Indicator.RETURNS_OO].shift(-1).values
                
                # Create mapping with robust cluster handling
                regime_mapping = self.create_regime_mapping(
                    X_train_scaled, 
                    gmm_model, 
                    returns_forward_train,
                    data_clean.loc[train_end-1, Keys.Data.Market.DATE]
                )
                
                # Update refit tracker
                last_refit_idx = i
                
                # ===== STORE FOLD METADATA =====
                folds_executed.append({
                    'fold': fold_num,
                    'train_start': train_start,
                    'train_end': train_end,
                    'train_start_date': data_clean.loc[train_start, Keys.Data.Market.DATE],
                    'train_end_date': data_clean.loc[train_end-1, Keys.Data.Market.DATE],
                    'regime_mapping': regime_mapping.cluster_to_regime.copy(),
                    'mean_returns': regime_mapping.mean_returns.copy(),
                    'cluster_counts': regime_mapping.cluster_counts.copy(),
                    'is_valid': regime_mapping.is_valid
                })
            
            # ===== STEP 4: PREDICT CURRENT OBSERVATION =====
            # Use FROZEN models (scaler, GMM, mapping) to predict regime
            
            # Extract current observation features
            X_current_raw = data_clean.loc[i:i, self.options.FEATURES].values
            
            # Transform using frozen scaler
            X_current_scaled = scaler.transform(X_current_raw)
            
            # Predict cluster using frozen GMM
            cluster_pred = gmm_model.predict(X_current_scaled)[0]
            
            # Map to regime using frozen mapping
            regime_pred = regime_mapping.cluster_to_regime[cluster_pred]
            
            # Store predictions
            data_clean.loc[i, Keys.Data.Regime.GMM_CLUSTER] = cluster_pred
            data_clean.loc[i, Keys.Data.Regime.GMM_LABEL] = regime_pred
        
        # ===== VALIDATION SUMMARY =====
        self._logger.info(f"WALK-FORWARD COMPLETED")
        self._logger.info(f"Total folds executed: {len(folds_executed)}")
        valid_folds = sum(1 for f in folds_executed if f['is_valid'])
        self._logger.info(f"Valid folds (all clusters sufficiently populated): {valid_folds}/{len(folds_executed)}")
        self._logger.info(f"Predictions generated: {data_clean[Keys.Data.Regime.GMM_LABEL].notna().sum()}")
        
        # Show final regime distribution
        regime_counts = data_clean[Keys.Data.Regime.GMM_LABEL].value_counts()
        self._logger.info(f"Final regime distribution:")
        for regime in [Keys.Regime.BEARISH, Keys.Regime.NEUTRAL, Keys.Regime.BULLISH]:
            count = regime_counts.get(regime, 0)
            pct = count / len(data_clean) * 100 if len(data_clean) > 0 else 0
            self._logger.info(f"   {regime}: {count} days ({pct:.1f}%)")
        
        return data_clean, folds_executed