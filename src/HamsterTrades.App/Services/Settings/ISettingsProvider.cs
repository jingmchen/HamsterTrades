using HamsterTrades.App.Constants;

namespace HamsterTrades.App.Services.Settings;

public interface ISettingsProvider
{
    AppSettings Current {get;}
    void Save();
    void Reload();
}