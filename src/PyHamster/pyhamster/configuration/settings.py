# Values initialized from settings.json

from dataclasses import dataclass
from ..base import KeyEnum

class LogLevel(KeyEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LoggingSection:
    log_level:LogLevel
    retained_days:int

@dataclass
class Settings:
    logging:LoggingSection