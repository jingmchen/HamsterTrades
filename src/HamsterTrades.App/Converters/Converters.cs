using System.Globalization;
using Avalonia;
using Avalonia.Data.Converters;

namespace HamsterTrades.App.Converters;

// Transforms data between ViewModel and View when types need reformatting

// All converters are static singletons to prevent unnecessary instance creations (Avalonia allocates a new converter instance every time a binding is evaluated)
// All converters are valid for static singletons as they are stateless
// - Convert() takes inputs and returns an output with no stored state between calls
// All converters have a private constructor to enforce singleton at compile time (prevent new Converter() elsewhere)

// For calling in .axaml files, declare in namespace: xmlns:conv="clr-namespace:SimplyDraft.App.Converters"
// For binding in .axaml files, call for example,
// <TextBlock Text="{Binding IsExpanded, Converter={x:Static conv:BoolToExpandIconConverter.Instance}}" />

/// <summary>Returns 0.4 opacity when true (cut items), 1.0 otherwise.</summary>
public sealed class BoolToOpacityConverter : IValueConverter
{
    public static readonly BoolToOpacityConverter Instance = new ();
    private BoolToOpacityConverter() {} // Enforce singleton at compile time
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not bool b) return AvaloniaProperty.UnsetValue;
        return b ? 0.4 : 1.0;
    }
    // One-way converter
    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) => throw new NotSupportedException();
}

/// <summary>Negates a boolean. Useful for IsEnabled/IsReadOnly pairs.</summary>
public sealed class InverseBoolConverter : IValueConverter
{
    public static readonly InverseBoolConverter Instance = new();
    private InverseBoolConverter() {}
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not bool b) return AvaloniaProperty.UnsetValue;
        return !b;
    }
    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not bool b) return AvaloniaProperty.UnsetValue;
        return !b;
    }
}

/// <summary>Returns "▸" or "▾" strings for IsExpanded property.</summary>
public sealed class BoolToExpandIconConverter : IValueConverter
{
    public static readonly BoolToExpandIconConverter Instance = new();
    private BoolToExpandIconConverter() {}
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not bool b) return AvaloniaProperty.UnsetValue;
        return b ? "▾" : "▸";
    }
    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) => throw new NotSupportedException();
}

/// <summary>Maps true/false to two string values supplied via parameter as "TrueVal|FalseVal".</summary>
public sealed class BoolToStringConverter : IValueConverter
{
    public static readonly BoolToStringConverter Instance = new();
    private BoolToStringConverter() {}
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not bool b) return AvaloniaProperty.UnsetValue;
        var parts = (parameter as string)?.Split('|');
        if (parts is {Length: 2}) return b ? parts[0] : parts[1];
        return b.ToString();
    }
    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) => throw new NotSupportedException();
}

/// <summary>
/// Collapses (IsVisible=false) when value is false/null.
/// Use InverseNullToVisibleConverter for the inverse.
/// </summary>
public sealed class BoolToVisibleConverter : IValueConverter
{
    public static readonly BoolToVisibleConverter Instance = new();
    private BoolToVisibleConverter() {}
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture) => value is true;
    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture) => value is true;
}