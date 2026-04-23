# Logger for PyHamster

import sys
import logging
import inspect
from typing import Any
from ..core import Constants
from ..core import OperationalException

_logger_configured = False

def configure_logger(
    *,
    log_level:int = logging.INFO
) -> None:
    """Configure root logger for app. Called once during app startup."""

    # Validate directories
    log_dir = Constants.File.Path.LATEST_LOG
    log_dir.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt=Constants.Logger.LOGFORMAT,
        datefmt=Constants.Logger.DATEFORMAT
    )

    handlers:list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            filename=log_dir,
            encoding="utf-8"
        )
    ]

    root = logging.getLogger()
    root.handlers.clear()
    for h in handlers:
        h.setFormatter(formatter)
        root.addHandler(h)
    
    root.setLevel(level=log_level)

    global _logger_configured
    _logger_configured = True

class Logger:
    """
    Customized logger for TradingPenguin.

    Service Locator pattern - via `_logger = Logger.for_context(ClsName)`.
    """

    # Restrict instance to the listed attribute
    __slots__ = ("_log",)

    def __init__(self, stdlib_logger:logging.Logger) -> None:
        self._log = stdlib_logger
    
    @classmethod
    def for_context(cls, source:type|str|None = None) -> "Logger":
        if source is None: # Auto-detect source
            frame = inspect.stack()[1]
            name = frame[0].f_globals["__name__"]
        elif isinstance(source, type):
            name = f"{source.__module__}.{source.__qualname__}"
        else:
            name = source
        
        return cls(logging.getLogger(name))
    
    def _emit(self, level:str, msg:str, *args:Any) -> None:
        # Guard cannot be in for_context() due to Python initialization order
        if not _logger_configured:
            raise OperationalException("Logger is not configured. Call configure_logger() before using Logger.")
        getattr(self._log, level)(msg, *args)
        
    def debug(self, msg:str, *args:Any) -> None:
        self._emit("debug", msg, *args)

    def info(self, msg:str, *args:Any) -> None:
        self._emit("info", msg, *args)

    def warning(self, msg:str, *args:Any) -> None:
        self._emit("warning", msg, *args)

    def error(self, msg:str, *args:Any) -> None:
        self._emit("error", msg, *args)
    
    def critical(self, msg:str, *args:Any) -> None:
        self._emit("critical", msg, *args)

    def exception(self, msg:str, *args:Any) -> None:
        self._emit("exception", msg, *args)