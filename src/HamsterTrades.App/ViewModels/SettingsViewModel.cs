using Avalonia.Media;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using HamsterTrades.App.Services.Themes;

namespace HamsterTrades.App.ViewModels;

public sealed partial class SettingsViewModel : ObservableObject
{
    private readonly IThemeManager _themeManager;
    public List<AccentOption> Accents {get;}
    public IBrush AccentBrush => new SolidColorBrush(AccentToColor(_themeManager.CurrentAccent));
    public string CurrentAccent => _themeManager.CurrentAccent.ToString();

    public SettingsViewModel(IThemeManager themeManager)
    {
        _themeManager = themeManager;

        Accents = Enum.GetValues<AppAccent>()
            .Select(a => new AccentOption(a, a == _themeManager.CurrentAccent))
            .ToList();

        _themeManager.ThemeChanged += OnThemeChanged;
    }

    public bool IsLightTheme
    {
        get => _themeManager.CurrentTheme == AppTheme.Light;
        set {if (value) _themeManager.SetTheme(AppTheme.Light);}
    }

    public bool IsDarkTheme
    {
        get => _themeManager.CurrentTheme == AppTheme.Dark;
        set {if (value) _themeManager.SetTheme(AppTheme.Dark);}
    }

    public bool IsSystemTheme
    {
        get => _themeManager.FollowSystemTheme == true;
        set {if (value) _themeManager.ToggleSystemTheme(true);}
    }

    public bool FollowSystemTheme
    {
        get => _themeManager.FollowSystemTheme == true;
        set {if (value) _themeManager.ToggleSystemTheme(true);}
    }

    [RelayCommand]
    private void SelectAccent(AppAccent accent) => _themeManager.SetAccent(accent);

    public bool AutoSave
    {
        set => _themeManager.TogglePersistence(true);
    }

    public string StatusText =>
        $"ThemeManager initialized — {_themeManager.CurrentTheme} / {_themeManager.CurrentAccent}";
    
    private void OnThemeChanged(object? sender, ThemeChangedEventArgs e)
    {
        OnPropertyChanged(nameof(IsLightTheme));
        OnPropertyChanged(nameof(IsDarkTheme));
        OnPropertyChanged(nameof(IsSystemTheme));
        OnPropertyChanged(nameof(CurrentAccent));
        OnPropertyChanged(nameof(AccentBrush));
        OnPropertyChanged(nameof(StatusText));

        foreach (var a in Accents)
            a.IsSelected = a.Accent == e.Accent;
    }

    public static Color AccentToColor(AppAccent accent) => accent switch
    {
        AppAccent.Black => Color.Parse("#111111"),
        AppAccent.White => Color.Parse("#E5E5E5"),
        _ => Colors.Transparent
    };
}
public sealed partial class AccentOption(AppAccent accent, bool isSelected) : ObservableObject
{
    public AppAccent Accent     { get; } = accent;
    public string    Name       { get; } = accent.ToString();
    public IBrush    Color      { get; } = new SolidColorBrush(SettingsViewModel.AccentToColor(accent));

    [ObservableProperty]
    private bool _isSelected = isSelected;
}