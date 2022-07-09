import shutil
import os
import yaml
import re
from typing import (Any, List, Dict, Tuple, Union)
from datetime import (date, datetime)


class DEFAULT_LOG:
    def info(*args: Any) -> None:
        print("[INFO]", concat_tuple(args))

    def debug(*args: Any) -> None:
        print("[DEBUG]", concat_tuple(args))

    def error(*args: Any) -> None:
        print("[ERROR]", concat_tuple(args))

    def warn(*args: Any) -> None:
        print("[WARN]", concat_tuple(args))


def get_dir_or_create(dir_path: str) -> str:
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    return os.path.join(dir_path)


def load_yaml_file(file_path: str, log=DEFAULT_LOG) -> Union[Any, bool]:
    if not os.path.isfile(file_path):
        raise Exception(f"No file found at {file_path}")
    with open(file_path, 'r') as stream:
        config = {}
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exception:
            log.error(False, exception)
            config = False
        return config


def dump_to_yaml_file(data: Dict[str, Any], file_path: str, log=DEFAULT_LOG) -> bool:
    with open(file_path, 'w') as file:
        write_status = True
        try:
            yaml.dump(data, file)
        except yaml.YAMLError as exception:
            log.error(False, exception)
            write_status = False
        return write_status


def create_template_from(target_template: str, destination: str) -> Union[bool, str]:
    if os.path.exists(target_template):
        shutil.copyfile(target_template, destination)
        return destination
    return False


def init_config_with_default(config: Dict[str, Any], default_config: Dict[str, Any]) -> Dict:
    for configValue, configType in enumerate(default_config):
        if not check_key_existence_in_dict(config, configType):
            config[configType] = configValue
    return config


def check_key_value_pair_exist_in_dict(dic: Dict[str, Any], key: Any, value: Any) -> bool:
    try:
        return dic[key] == value
    except KeyError:
        return False


def check_key_existence_in_dict(dic: Dict[str, Any], key: Any) -> bool:
    try:
        _ = dic[key]
        return True
    except KeyError:
        return False


def concat_tuple(ouput_tuple: Tuple) -> str:
    result = ""
    for m in ouput_tuple:
        result += str(m) + ' '

    return result


def clear_directory(directory: str, log=DEFAULT_LOG) -> None:
    if not os.path.isdir(directory):
        return log.error(False, f"Directory: {os.path.join(directory)} does not exist.")

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            log.error(False, "Failed to delete %s. Reason: %s" %
                      (file_path, e))


def remove_files(files: List[str], log=DEFAULT_LOG) -> None:
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                log.error(False, "Failed to delete %s. Reason %s" %
                          (str(file), e))


date_formatter = {
    "dd/mm/yyyy": "%d/%m/%Y",
    "dd-mm-yyyy": "%d-%m-%Y",
    "ddmmyyyy": "%d%m%Y",
    "mm/dd/yyyy": "%m/%d/%y",
    "mm dd, yyyy": "%B %d, %Y",
    "mm-dd-yyyy": "%b-%d-%Y",

    "dd/mm/yyyy hh:mm:ss": "%d/%m/%Y %H:%M:%S",
    "dd-mm-yyyy hh:mm:ss": "%d-%m-%Y %H:%M:%S",
    "dd-mm-yyyy hhmmss": "%d-%m-%Y %H%M%S",
    "dd-mm-yyyy hhmm": "%d-%m-%Y %H%M",
    "ddmmyyyy hhmmss": "%d%m%Y %H%M%S",
}


def get_date_formatter(format_option: str, default_format_option: str) -> str:
    if check_key_existence_in_dict(date_formatter, format_option):
        return date_formatter[format_option]
    else:
        return date_formatter[default_format_option]


def get_date_now(format_option: str = "dd-mm-yyyy") -> str:
    date_format = get_date_formatter(format_option, "dd-mm-yyyy")
    today = date.today()
    return today.strftime(date_format)


def get_datetime_now(format_option: str = "ddmmyyyy hhmmss") -> str:
    datetime_format = get_date_formatter(format_option, "ddmmyyyy hhmmss")
    now = datetime.now()
    return now.strftime(datetime_format)


def convert_to_datetime(date_str: str, time_str: str = None):
    if time_str:
        time_str = time_str.split(' ')[0]
        return datetime.datetime.strptime(f'{date_str} | {time_str}', '%d/%b/%Y | %H:%M')
    else:
        return datetime.datetime.strptime(date_str, "%d/%b/%Y")


def format_input_str(input_str: str, alphanumeric: bool = True, whitelist_chars: str = "") -> str:
    return "".join(char for char in input_str if (alphanumeric and char.isalnum()) or whitelist_chars.find(char) > -1)


def check_if_valid_email_format(email_str: str) -> Union[str, bool]:
    if(re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email_str)):
        return email_str
    else:
        return False
