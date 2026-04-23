# Keys for PyHamster
#   - Contain lookup values for indicators

from ..base import KeyEnum

class Keys:
    """Centralized location for all keys (lookup values)."""
    
    class Settings:
        class LoggingSection(KeyEnum):
            TITLE:str = "logging"
            LOG_LEVEL:str = "log_level"
            RETAINED_DAYS:str = "retained_days"

        class ThemeSection(KeyEnum):
            TITLE:str = "theme"
            THEME_MODE:str = "theme_mode"
            COLOR_MODE:str = "color_mode"
            FONT_FAMILY:str = "font_family"
            FONT_SIZE:str = "font_size"
        
        class WindowSection(KeyEnum):
            TITLE:str = "window"
            LENGTH:str = "length"
            WIDTH:str = "width"
            MIN_LENGTH:str = "min_length"
            MIN_WIDTH:str = "min_width"
    
    class Data:
        class Market(KeyEnum):
            DATE:str = "Date"
            OPEN:str = "Open"
            HIGH:str = "High"
            LOW:str = "Low"
            CLOSE:str = "Close"
            VOLUME:str = "Volume"
            DIVIDENDS:str = "Dividends"
            STOCK_SPLITS:str = "Stock Splits"
        
        class Indicator(KeyEnum):
            SMA:str = "SMA"
            EMA:str = "EMA"
            ATR:str = "ATR"
            ATR_PERCENTILE:str = "ATR_%"
            RSI:str = "RSI"
            ROC:str = "ROC"
            MOM:str = "MOM"
            CCI:str = "CCI"
            CHOP:str = "CHOP"
            WILLR:str = "WILLR"
            RETURNS_CC:str = "Returns_CC"
            RETURNS_OO:str = "Returns_OO"
            RETURNS_FW:str = "Returns_FW"
            HIST_VOL:str = "Historical_Vol"
            OBV:str = "OBV"
            VWAP:str = "VWAP"
            VOL_SMA:str = "VOL_SMA"
            VOL_RATIO:str = "VOL_RATIO"
            HIGHER_HIGH:str = "Higher_High"
            LOWER_LOW:str = "Lower_Low"
            HURST:str = "Hurst"
            YZ_VOL:str = "Yang-Zhang_Vol"
            SMA_CROSSOVER_NORM:str = "SMA_Cross_Norm"
            CHOCH:str = "CHoCH"

            def period(self, number:int) -> str:
                return f"{self.value}_{number}"
        
        class Regime(KeyEnum):
            GMM_CLUSTER:str = "GMM_Cluster"
            GMM_LABEL:str = "GMM_Label"
    
    class Regime(KeyEnum):
        BULLISH:str = "Bullish"
        BEARISH:str = "Bearish"
        NEUTRAL:str = "Neutral"

    class Query:
        class LiveData(KeyEnum):
            TICKER:str = "ticker"
            CURRENT_PRICE:str = "current_price"
            LAST_TRADE_TIME:str = "last_trade_time"
            HIGH:str = "high"
            LOW:str = "low"
            VOLUME:str = "volume"
    
    class Exporter:
        class ExcelVBAWriter(KeyEnum):
            MACRO_FILE_EXT:str = ".txt"