#!/usr/bin/env python3
import sys

sys.path.append("src")

import logging
import os
import shutil

from bot import Bot
from user import UserManager
from utils import utils
from utils.log import Log
from stages.welcome import WelcomeStage


LOG_FILE = os.path.join("logs", f"main.log")

CONFIG = utils.load_yaml_file(os.path.join("config.yaml"))
assert CONFIG, "Failed to load config.yaml. Fatal error, please remedy."\
    "\n\nLikely an invalid format."

LIVE_MODE = CONFIG["RUNTIME"]["LIVE_MODE"]
FRESH_START = CONFIG["RUNTIME"]["FRESH_START"] if not LIVE_MODE else False
BOT_TOKEN = CONFIG["BOT_TOKENS"]["LIVE"] if LIVE_MODE else CONFIG["BOT_TOKENS"]["TEST"]


def main():

    setup()

    # Main application logger
    logger = Log(
        name=__name__,
        stream_handle=sys.stdout,
        file_handle=LOG_FILE,
        log_level=logging.DEBUG
    )

    user_manager = UserManager()
    user_manager.init(
        logger=logger,
        log_user_logs_to_app_logs=("LOG_USER_TO_APP_LOGS" in CONFIG
                                   and CONFIG["LOG_USER_TO_APP_LOGS"]))

    bot = Bot()
    bot.init(token=BOT_TOKEN,
             logger=logger,
             config=CONFIG)

    # Bot flow:
    STAGE_WELCOME = "welcome"
    STAGE_END = "end"

    # ------------------------------ Stage: welcome ------------------------------ #
    welcome_stage: WelcomeStage = WelcomeStage(
        stage_id=STAGE_WELCOME,
        next_stage_id=STAGE_END,
        bot=bot
    )
    welcome_stage.setup(
        interval=5
    )
    bot.set_first_stage(STAGE_WELCOME)
    # ---------------------------------------------------------------------------- #

    # -------------------------------- Stage: end -------------------------------- #
    bot.make_end_stage(
        stage_id=STAGE_END,
        goodbye_message="You have exited the conversation. \n\nUse /start to begin a new one.",
    )
    # ---------------------------------------------------------------------------- #

    # Start Bot
    logger.info(False, "")
    logger.info(False, "Initializing...")
    logger.info(False, "")

    bot.start(live_mode=LIVE_MODE)


def setup():
    """
    Creates the neccesary runtime directories if missing (logs).
    If FRESH_START is True, then it will clear existing files from last run (logs/* and users/*).

    :return: None
    """
    utils.get_dir_or_create(os.path.join("logs"))
    if FRESH_START:
        users_directory = os.path.join("users")

        for chatid in os.listdir(users_directory):
            user_directory = os.path.join(users_directory, chatid)
            if os.path.isdir(user_directory):
                shutil.rmtree(user_directory)

        if os.path.isfile(LOG_FILE):
            os.remove(LOG_FILE)


if __name__ == "__main__":
    main()
