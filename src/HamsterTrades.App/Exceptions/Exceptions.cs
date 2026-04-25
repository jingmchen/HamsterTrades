namespace HamsterTrades.App.Exceptions;

public enum ErrorCode
{
    // 1000 - Errors relating to configuration
    ConfigMissingKey = 1001,
    ConfigInvalidValue = 1002,
    ConfigMissingSection = 1003,

    // 2000 - Operational exception
    InvalidThreadState = 2001,

    // 9000 - Unhandled exceptions
    Unexpected = 9000
}

/// <summary>
/// Root of the application exception hiearchy.
/// </summary>
public class HamsterTradesException : Exception
{
    public ErrorCode ErrorCode {get;}

    public HamsterTradesException(ErrorCode errorCode, string message, Exception? inner = null) : base(message, inner)
    {
        ErrorCode = errorCode;
    }
}

/// <summary>
/// Exceptions relating to configuration
/// </summary>
public class ConfigException : HamsterTradesException
{
    public ConfigException(ErrorCode errorCode, string message, Exception? inner = null) : base(errorCode, message, inner) { }

    public static ConfigException MissingKey(string key)
    {
        return new ConfigException(
            errorCode: ErrorCode.ConfigMissingKey,
            message: $"Required configuration key '{key}' is missing."
        );
    }

    public static ConfigException InvalidValue(string key)
    {
        return new ConfigException(
            errorCode: ErrorCode.ConfigInvalidValue,
            message: $"Value for configuration key '{key}' is invalid or missing."
        );
    }

    public static ConfigException MissingSection(string section)
    {
        return new ConfigException(
            errorCode: ErrorCode.ConfigMissingSection,
            message: $"Required section '{section}' is missing in config."
        );
    }
}

public class OperationalException : HamsterTradesException
{
    public OperationalException(ErrorCode errorCode, string message, Exception? inner = null) : base(errorCode, message, inner) { }

    public static OperationalException InvalidThreadState(string thread)
    {
        return new OperationalException(
            errorCode: ErrorCode.InvalidThreadState,
            message: $"Operation not called on the proper thread: '{thread}'."
        );
    }
}