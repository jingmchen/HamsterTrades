# Settings default for PyHamster

from typing import Final
from ..configuration import LogLevel

class SettingsDefault:
    """Settings defaults"""
    class LoggingSection:
        log_level:Final[LogLevel] = LogLevel.INFO
        retained_days:Final[int] = 7