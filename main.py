#!/usr/bin/env python3
import sys

sys.path.append("src")

import logging
import os
import shutil
from typing import (Union, Optional, Tuple)

from telegram import Update
from telegram.ext import (CallbackContext, JobQueue, Job)

from constants import USERSTATE
from bot import Bot
from user import (UserManager, User)
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
    STAGE_COLLECT_INTERVAL = "info_interval"
    STAGE_WELCOME = "welcome"
    STAGE_END = "end"

    # --------------------------- Stage: info_interval --------------------------- #
    def check_if_number(input_str: Union[str, bool]) -> Union[str, bool]:
        if input_str is True:
            return "any valid number"
        else:
            try:
                input_str = float(input_str)
            except:
                input_str = False

            return input_str

    bot.get_user_info(
        stage_id=STAGE_COLLECT_INTERVAL,
        next_stage_id=STAGE_WELCOME,
        data_label="Reminder Interval",
        input_formatter=check_if_number,
        additional_text="This is the interval of time between reminders sent by the bot.\nInterval is in <b>hours</b>.",
        use_last_saved=True,
        allow_update=True
    )
    bot.set_first_stage(STAGE_COLLECT_INTERVAL)
    # ---------------------------------------------------------------------------- #

    # ------------------------------ Stage: welcome ------------------------------ #
    welcome_stage: WelcomeStage = WelcomeStage(
        stage_id=STAGE_WELCOME,
        next_stage_id=STAGE_END,
        bot=bot
    )
    welcome_stage.setup(
        interval=6
    )
    # ---------------------------------------------------------------------------- #

    # -------------------------------- Stage: end -------------------------------- #
    bot.make_end_stage(
        stage_id=STAGE_END,
        goodbye_message="You have exited the conversation. \n\nUse /start to begin a new one.",
    )
    # ---------------------------------------------------------------------------- #

    # ------------------------------- Command: stop ------------------------------ #
    def stop_current_job(update: Update,
                         context: CallbackContext,
                         silent_stop: Optional[bool] = False) -> USERSTATE:
        user: User = context.user_data.get("user")

        if user:
            current_job_queue: JobQueue = context.job_queue
            current_jobs: Tuple[Job, ...] = current_job_queue.get_jobs_by_name(
                user.chatid)

            for job in current_jobs:
                job: Job
                job.schedule_removal()

            if not silent_stop:
                bot.edit_or_reply_message(
                    update, context,
                    "You have stopped the bot.\n\n"
                    "Use /start to start the bot again.",
                    reply_message=True
                )

        return bot.end_stage.stage_id

    bot.add_command_handler(
        command="stop",
        callback=stop_current_job,
        override_handler=True
    )
    # ---------------------------------------------------------------------------- #

    # ------------------------------ Command: start ------------------------------ #
    def start_overide(update: Update, context: CallbackContext) -> USERSTATE:
        stop_current_job(update, context, silent_stop=True)
        return bot.conversation_entry(update, context)

    bot.add_command_handler(
        command="start",
        callback=start_overide,
        add_as_fallback=True,
        override_handler=True
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
