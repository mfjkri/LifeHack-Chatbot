import sys
sys.path.append("src")

import os

from utils.utils import (load_yaml_file, dump_to_yaml_file)

users_directory = os.path.join("users")
banned_users_file = os.path.join(users_directory, "banned_users.yaml")
banned_users = load_yaml_file(banned_users_file) or []

if __name__ == "__main__":
    for chatid in os.listdir(users_directory):
        user_directory = os.path.join(users_directory, chatid)

        if os.path.isdir(user_directory) and chatid not in banned_users:
            banned_users.append(chatid)

    dump_to_yaml_file(banned_users, banned_users_file)
