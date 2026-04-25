namespace HamsterTrades.Python.PythonRuntime;

public sealed class PythonRuntimeOptions
{
    public string? PythonDll {get; set;}
    public string? PythonHome {get; set;}
    public List<string> PythonPath {get; set;} = new();
    public string ModuleName {get; set;} = "pyhamster";
}