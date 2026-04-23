# Exceptions for HamsterTrades

from enum import IntEnum

# -- ERROR CODES
class ErrorCode(IntEnum):
    # 1000 - Errors relating to configuration
    CONFIG_MISSING_KEY = 1001
    CONFIG_INVALID_VALUE = 1002
    CONFIG_MISSING_SECTION = 1003

    # 2000 - Operational exceptions - general
    INVALID_THREAD_STATE = 2001
    MISSING_DATA = 2002

    # 3000 - Operational exceptions for dataproviders
    QUERY_UNEXPECTED = 3001

    # 4000 - Operational exceptions for exporters
    EXCEL_WRITER_UNEXPECTED = 4001

    # 9000 - Unhandled exceptions
    UNEXPECTED = 9000

# -- ROOT EXCEPTIONS
class PyHamsterException(Exception):
    """Root of exception hierarchy."""
    def __init__(self, error_code:ErrorCode, message:str, inner:Exception|None = None):
        super().__init__(message)
        self.error_code = error_code
        self.inner = inner
    
    def __str__(self):
        return f"[{self.error_code.name} ({self.error_code})] {super().__str__()}"

class ConfigException(PyHamsterException):
    """Exceptions relating to configuration."""
    def __init__(self, error_code:ErrorCode, message:str, inner:Exception|None = None):
        super().__init__(error_code, message, inner)

class OperationalException(PyHamsterException):
    """Exceptions relating to operational errors."""
    def __init__(self, error_code:ErrorCode, message:str, inner:Exception|None = None):
        super().__init__(error_code, message, inner)

# -- CHILD EXCEPTIONS
class MissingKeyError(ConfigException):
    def __init__(self, key:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.CONFIG_MISSING_KEY,
            message=f"Required configuration key '{key}' is missing.",
            inner=inner
        )
        self.key = key

class InvalidValueError(ConfigException):
    def __init__(self, key:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.CONFIG_INVALID_VALUE,
            message=f"Value for configuration key '{key}' is invalid or missing.",
            inner=inner
        )
        self.key = key

class MissingSectionError(ConfigException):
    def __init__(self, section:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.CONFIG_MISSING_SECTION,
            message=f"Required section '{section}' is invalid or missing.",
            inner=inner
        )
        self.section = section

class InvalidThreadStateError(OperationalException):
    def __init__(self, message:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.INVALID_THREAD_STATE,
            message=message,
            inner=inner
        )

class MissingDataError(OperationalException):
    def __init__(self, message:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.MISSING_DATA,
            message=message,
            inner=inner
        )

class QueryUnexpectedError(OperationalException):
    def __init__(self, message:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.QUERY_UNEXPECTED,
            message=message,
            inner=inner
        )

class ExcelWriterUnexpectedError(OperationalException):
    def __init__(self, message:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.EXCEL_WRITER_UNEXPECTED,
            message=message,
            inner=inner
        )

class UnexpectedError(PyHamsterException):
    def __init__(self, message:str, inner:Exception|None = None):
        super().__init__(
            error_code=ErrorCode.UNEXPECTED,
            message=message,
            inner=inner
        )

