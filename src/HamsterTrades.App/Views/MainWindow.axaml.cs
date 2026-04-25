using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using HamsterTrades.App.ViewModels;

namespace HamsterTrades.App.Views;

public sealed partial class MainWindow : Window
{
    public MainWindow(MainWindowViewModel viewModel)
    {
        AvaloniaXamlLoader.Load(this);
        DataContext = viewModel;
    }
}