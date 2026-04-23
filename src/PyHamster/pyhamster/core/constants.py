# Constants for PyHamster
#   - Contains fixed values

from pathlib import Path
from ..base import KeyMeta, K, freeze
from ..core import Keys

class Constants(metaclass=KeyMeta):
    """Centralized location for all fixed values used."""

    class PackageInfo(metaclass=KeyMeta):
        PACKAGENAME:str = "PyHamster"
        ASSEMBLYNAME:str = "PyHamster"
        AUTHOR:str = "TJM"
        VERSION:str = "1.0.0"
    
    class Directory(metaclass=KeyMeta):

        class Name(metaclass=KeyMeta):
            PROJECT_ROOT:str = K("{PackageInfo.ASSEMBLYNAME}")
            LOGS:str = "logs"
        
        class Path(metaclass=KeyMeta):
            PROJECT_ROOT:Path = Path(__file__).parent.parent.parent.parent
            LOGS:Path = K(f"{PROJECT_ROOT}/{{Directory.Name.LOGS}}", cast=Path)
    
    class File(metaclass=KeyMeta):

        class Name(metaclass=KeyMeta):
            SETTINGS:str = "pysettings.json"
            LATEST_LOG:str = K("{AppInfo.ASSEMBLYNAME}-latest{File.Extension.LATEST_LOG}")
            ARCHIVED_LOG:str = K("{AppInfo.ASSEMBLYNAME}{File.Extension.ARCHIVED_LOG}")
        
        class Path(metaclass=KeyMeta):
            SETTINGS:Path = K("{Directory.Path.PROJECT_ROOT}/{File.Name.SETTINGS}", cast=Path)
            LATEST_LOG:Path = K("{Directory.Path.LOGS}/{File.Name.LATEST_LOG}", cast=Path)
            ARCHIVED_LOG:Path = K("{Directory.Path.LOGS}/{File.Name.ARCHIVED_LOG}", cast=Path)
        
        class Extension(metaclass=KeyMeta):
            LATEST_LOG:str = ".log"
            ARCHIVED_LOG:str = ".log"
    
    class Logger(metaclass=KeyMeta):
        VALID_LOG_LEVELS:tuple[str, ...] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        LOGFORMAT:str = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        DATEFORMAT:str = "%d-%b-%Y %H:%M:%S"
    
    class LogManager(metaclass=KeyMeta):
        ARCHIVED_LOG_DATEFORMAT:str = "%d-%m-%Y"
        MAX_ARCHIVES:int = 7
    
    class Query(metaclass=KeyMeta):
        YF_DATEFORMAT:str = "%Y-%m-%d"
        LOOKBACK_DAYS:int = 365

freeze(Constants, root=Constants)