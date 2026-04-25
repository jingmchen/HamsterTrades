using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using HamsterTrades.App.ViewModels;

namespace HamsterTrades.App.Views;

public partial class SettingsWindow: Window
{
    public SettingsWindow(SettingsViewModel viewModel)
    {
        AvaloniaXamlLoader.Load(this);
        DataContext = viewModel;
    }
}