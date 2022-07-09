import sys
import os
import copy
import logging
from typing import (Any, Dict, Optional)

from utils import utils
from utils.log import Log

users_directory = utils.get_dir_or_create(os.path.join("users"))
banned_users_yaml_file = os.path.join(users_directory, "banned_users.yaml")


class User():
    def __init__(self, chatid: str, application_logfilehandler: str, UsersManager):
        self.logger = Log(
            name=f"user:{chatid}",
            stream_handle=sys.stdout,
            log_level=logging.INFO
        )

        self.chatid = chatid
        self.data = None
        self.is_banned = False
        self.user_manager = UsersManager
        self.answered_callback_queries = []

        self.directory = os.path.join(users_directory, chatid)
        user_exists = os.path.isdir(self.directory)
        self.directory = utils.get_dir_or_create(self.directory)

        self.log_file = os.path.join(self.directory, f"{self.chatid}.log")
        self.logger.add_filehandle(self.log_file)

        if user_exists:
            self.yaml_file = self.load_user_from_file()
        else:
            self.yaml_file = self.create_new_user()

        self.save_user_to_file()
        if UsersManager.log_user_logs_to_app_logs:
            self.logger.add_filehandler(application_logfilehandler)

    def create_new_user(self) -> None:
        self.logger.info("CREATING_NEW_USER",
                         f"User:{self.chatid} is a new user. Creating their files...")

        user_data = copy.deepcopy(self.user_manager.data_fields)
        self.data = user_data

        return os.path.join(self.directory, f"{self.chatid}.yaml")

    def update_user_data_from_file(self, user_data: Dict[str, Any]) -> Dict:
        # TODO Update outdated user data with new data fields (user_manager.data_fields)
        return user_data

    def load_user_from_file(self) -> None:
        self.logger.info(False, "\n")
        self.logger.info(
            "NEW_SESSION", f"User:{self.chatid} is starting a new session and resuming their progress...")

        user_yaml_file = os.path.join(self.directory, f"{self.chatid}.yaml")
        user_yaml_file_exists = os.path.isfile(user_yaml_file)

        user_data = utils.load_yaml_file(
            user_yaml_file, self.logger) if user_yaml_file_exists else None

        if not (user_yaml_file_exists and user_data):
            if not user_yaml_file_exists:
                self.logger.error(
                    "USERDATA_MISSING", f"User:{self.chatid} userdata is missing. Creating a new one...")
            else:
                self.logger.error(
                    "USERDATA_CORRUPTED", f"User:{self.chatid} userdata is corrupted! Resetting his/her state...")

            # Create new user since their old data could not be found / loaded
            return self.create_new_user()
        else:
            # Update their saved data in case of format changes
            self.data = self.update_user_data_from_file(user_data)
            self.logger.info("LOADED_USER_FROM_FILE",
                             f"Loaded User:{self.chatid} from file.")

            return user_yaml_file

    def save_user_to_file(self) -> None:
        if not utils.dump_to_yaml_file(
                self.data, self.yaml_file, self.logger):
            self.logger.error("USERDATA_FAILED_TO_SAVE",
                              f"User:{self.chatid} userdata has failed to be saved. Trying again later...")

    def update_user_data(self, data_label: str, data_value: Any) -> None:
        self.data.update({data_label: data_value})
        self.save_user_to_file()

    def reset_user(self) -> None:
        self.create_new_user()
        self.save_user_to_file()


class UserManager(object):
    def new(self, chatid: str) -> User:
        # self.update_banned_list()
        if chatid not in self.users:
            self.logger.info("CREATING_USER_CLASS",
                             f"Creating UserClass for User:{chatid}.")
            user = User(chatid, self.application_logfilehandler, self)

            if chatid in self.banned_users:
                user.is_banned = True

            self.users.update({chatid: user})
            return user
        else:
            self.logger.info("USING_CACHED_USER_CLASS",
                             f"Using cached UserClass for User:{chatid}.")
            return self.users.get(chatid)

    def get_from_chatid(self, chatid: str) -> Optional[User]:
        return self.users.get(chatid)

    def update_banned_list(self) -> None:
        banned_users = utils.load_yaml_file(
            banned_users_yaml_file, self.logger) if os.path.isfile(banned_users_yaml_file) else False
        if banned_users:
            self.banned_users = banned_users

            for chatid in banned_users:
                user: User = self.get_from_chatid(chatid)
                if user:
                    user.is_banned = True
                    # user.reset_user()

    def ban_user(self, chatid: str) -> None:
        self.update_banned_list()

        user: User = self.get_from_chatid(chatid)
        if user:
            # user.reset_user()
            user.is_banned = True

        self.banned_users.append(chatid)
        utils.dump_to_yaml_file(
            self.banned_users, banned_users_yaml_file, self.logger)

    def unban_user(self, chatid: str) -> None:
        self.update_banned_list()

        if chatid in self.banned_users:
            self.banned_users.remove(chatid)
            utils.dump_to_yaml_file(
                self.banned_users, banned_users_yaml_file, self.logger)
            self.update_banned_list()

            user: User = self.get_from_chatid(chatid)
            if user:
                user.is_banned = False
            # self.new(chatid)

    def add_data_field(self, key: str, value: Any):
        self.data_fields.update({key: copy.deepcopy(value)})

    def init(self, logger: Log, log_user_logs_to_app_logs: bool = False) -> None:
        self.application_logfilehandler = logger.file_handlers[0]
        self.logger = logger
        self.users = {}
        self.data_fields = {}
        self.banned_users = []
        self.log_user_logs_to_app_logs = log_user_logs_to_app_logs

        self.update_banned_list()

    def load_users_from_file(self):
        for chatid in os.listdir(users_directory):
            if os.path.isdir(os.path.join(users_directory, chatid)):
                self.new(chatid)

    def __new__(cls, *_):
        if not hasattr(cls, "instance"):
            cls.instance = super(UserManager, cls).__new__(cls)
        return cls.instance
