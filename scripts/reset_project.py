import sys
sys.path.append("")

import shutil
from typing import Optional

import main


def reset_project(clear_all_logs: Optional[bool] = False,
                  log_file: Optional[str] = ""):
    if clear_all_logs:
        shutil.rmtree("logs")
    else:
        main.LOG_FILE = log_file

    main.FRESH_START = True
    main.setup()


if __name__ == "__main__":
    reset_project(True)
