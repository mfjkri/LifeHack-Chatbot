from typing import Optional

from telegram import (CallbackQuery, ParseMode, Update)
from telegram.ext import (CallbackContext, Job, JobQueue)

from constants import (USERSTATE, MESSAGE_DIVIDER)
from utils import utils
from user import User
from stage import Stage


class WelcomeStage(Stage):
    def __init__(self, stage_id: str, next_stage_id: str, bot):
        super().__init__(stage_id, next_stage_id, bot)

    def setup(self, interval: Optional[int] = 60) -> None:
        self.interval = interval

        self.init_users_data()

        # self.states = {}
        self.bot.register_stage(self)

        self.WELCOME_DISCLAIMER_STAGE = self.bot.let_user_choose(
            stage_id="choose_welcome_disclaimer",
            choice_text="Would you like to start the bot?",
            choices=[
                {
                    "text": "Yes",
                    "callback": self.accept_disclaimer
                },
                {
                    "text": "No",
                    "callback": self.decline_disclaimer
                }
            ]
        )

    #

    def init_users_data(self) -> None:
        self.user_manager.add_data_field("is_bot_active", False)
        return super().init_users_data()

    def stage_entry(self, update: Update, context: CallbackContext) -> USERSTATE:
        return self.clear_job(update, context)

    def stage_exit(self, update: Update, context: CallbackContext) -> USERSTATE:
        return super().stage_exit(update, context)

    def clear_job(self, update: Update, context: CallbackContext) -> USERSTATE:
        user: User = context.user_data.get("user")

        current_job_queue: JobQueue = context.job_queue
        current_jobs = current_job_queue.get_jobs_by_name(user.chatid)
        for job in current_jobs:
            job.schedule_removal()

        return self.bot.proceed_next_stage(
            current_stage_id=self.stage_id,
            next_stage_id=self.WELCOME_DISCLAIMER_STAGE.stage_id,
            update=update, context=context
        )

    def accept_disclaimer(self, update: Update, context: CallbackContext) -> USERSTATE:
        query: CallbackQuery = update.callback_query
        query.answer()

        self.bot.edit_or_reply_message(
            update, context,
            "You have activated the bot.\n\n"
            "Use /start again to stop the bot."
        )

        user: User = context.user_data.get("user")

        context.job_queue.run_repeating(
            callback=self.do_me_interval,
            interval=self.interval,
            context=user.chatid,
            name=str(user.chatid))

        return -1
        # return self.stage_exit(update, context)

    def decline_disclaimer(self, update: Update, context: CallbackContext) -> USERSTATE:
        query: CallbackQuery = update.callback_query
        query.answer()
        return self.stage_exit(update, context)

    def do_me_interval(self, context: CallbackContext) -> None:
        job: Job = context.job

        context.bot.send_message(
            chat_id=job.context,
            text="The time now is "
            f"""<b>{utils.get_datetime_now("dd/mm/yyyy hh:mm:ss")}</b>""",
            parse_mode=ParseMode.HTML
        )
