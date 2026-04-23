# Log manager for PyHamster
#       - Handles responsibilities that should not be exposed in Logger cls

import shutil
from datetime import datetime, timedelta
from ..core import Constants

class LogManager:
    @staticmethod
    def archive_previous_logs() -> None:
        """
        Archives logs from previous app launches.

        Format:
        - `Assembly name` _ `Date` _ `Recursive numbering if duplicated` _ `.log`
        """

        latest_log = Constants.File.Path.LATEST_LOG

        if not latest_log.exists():
            return
        
        date = datetime.now().strftime(Constants.LogManager.ARCHIVED_LOG_DATEFORMAT)
        archived_log_base = Constants.File.Path.ARCHIVED_LOG
        archived_log = archived_log_base.with_stem(
            f"{archived_log_base.stem}-{date}"
        )

        # Recursive naming
        if archived_log.exists():
            i = 0

            while archived_log.exists():
                i += 1
                archived_log = archived_log_base.with_stem(
                    f"{archived_log_base.stem}-{date}-{i}"
                )
        
        shutil.copy2(latest_log, archived_log)
        latest_log.unlink()
    
    @staticmethod
    def clean_old_logs(retained_days:int = 7):
        """
        Cleans up old archived logs inside logs directory after a dictated number of days.
        """

        cutoff = datetime.now() - timedelta(days = retained_days)

        for filepath in Constants.Directory.Path.LOGS.iterdir():
            if filepath.suffix != Constants.File.Extension.ARCHIVED_LOG:
                continue

            created = datetime.fromtimestamp(filepath.stat().st_birthtime)

            if created < cutoff:
                filepath.unlink()