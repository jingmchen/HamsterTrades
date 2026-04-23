# Loads and validates settings.json into settings.py class

import json
from enum import Enum
from typing import TypeVar
from functools import lru_cache
from ..core import Constants, Keys, MissingKeyError, MissingSectionError
from ..configuration import Settings, SettingsDefault, LoggingSection, LogLevel
from ..utils import Logger

E = TypeVar("E", bound=Enum)

class SettingsProvider:
    """Provides `settings` class from settings.json"""

    def __init__(self) -> None:
        self._logger = Logger.for_context(SettingsProvider)

    @lru_cache
    def load_settings(self) -> Settings:
        settings_path = Constants.File.Path.SETTINGS

        if not settings_path.exists():
            raise FileNotFoundError(f"Settings file not found at: {Constants.File.Path.SETTINGS}.")
        
        with settings_path.open(encoding="utf-8") as f:
            raw = json.load(f)
        
        for section in (Keys.Settings.LoggingSection.TITLE, Keys.Settings.ThemeSection.TITLE):
            if section not in raw:
                raise MissingSectionError(section)
        
        return Settings(
            logging=self._load_logging_section(raw[Keys.Settings.LoggingSection.TITLE])
        )

    def _load_logging_section(self, data:dict) -> LoggingSection:
        for key in (Keys.Settings.LoggingSection.LOG_LEVEL, Keys.Settings.LoggingSection.RETAINED_DAYS):
            if key not in data:
                raise MissingKeyError(f"{Keys.Settings.LoggingSection.TITLE}.{key}")
        
        return LoggingSection(
            log_level=self._parse_enum(
                enum=LogLevel,
                key=Keys.Settings.LoggingSection.LOG_LEVEL,
                value=data[Keys.Settings.LoggingSection.LOG_LEVEL],
                defaultvalue=SettingsDefault.LoggingSection.log_level
            ),
            retained_days=self._validate_values(
                key=Keys.Settings.LoggingSection.RETAINED_DAYS,
                value=data[Keys.Settings.LoggingSection.RETAINED_DAYS],
                min_limit=0,
                defaultvalue=SettingsDefault.LoggingSection.retained_days
            )
        )
    
    def _validate_values(self, *, key:str, value:str|int, min_limit:str|int = None, max_limit:str|int = None, defaultvalue:str|int) -> str:
        try:
            num_value = float(value)

            if (min_limit is not None and num_value < float(min_limit)) or (max_limit is not None and num_value > float(max_limit)):
                self._logger.warning(
                    f"Key value for key: '{key}' is invalid. Reverting to default: '{defaultvalue}'"
                )
                return defaultvalue
        except ValueError:
            self._logger.warning(
                    f"Key value for key: '{key}' is not a number. Reverting to default: '{defaultvalue}'"
                )
            return defaultvalue
        
        return value
    
    def _parse_enum(self, *, enum:type[E], key:str, value:str|int, defaultvalue:E) -> E:
        match = next(
            (member for member in enum if member.name.casefold() == value.casefold()),
            None
        )
        
        if match is None:
            self._logger.warning(
                f"Unable to parse key '{key}' value: '{value}'. Reverting to default: {defaultvalue}"
            )
            return defaultvalue
        
        return match
