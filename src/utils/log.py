import logging
from typing import (TextIO, Union, Any, Callable, Optional)

from utils import utils

FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")


class Log:

    def __init__(self, name: str, stream_handle: Optional[TextIO] = None, file_handle: Optional[str] = None, log_level: int = logging.INFO):
        logger = logging.getLogger(name)

        self.logger = logger
        self.name = name

        self.stream_handlers = []
        self.file_handlers = []

        if stream_handle:
            self.add_streamhandle(stream_handle)

        if file_handle:
            self.add_filehandle(file_handle)

        logger.setLevel(log_level)
        logger.debug("")
        logger.debug(f"Logger:{name} initialized")

    def quit(self):
        for stream_handler in self.stream_handlers:
            self.logger.removeHandler(stream_handler)

        for file_handler in self.file_handlers:
            self.logger.removeHandler(file_handler)

    def add_streamhandle(self, stream_handle: TextIO):
        stream_output = logging.StreamHandler(stream_handle)
        stream_output.setFormatter(FORMATTER)
        self.logger.addHandler(stream_output)
        self.stream_handlers.append(stream_output)

    def add_filehandle(self, file_handle: str):
        file_output = logging.FileHandler(file_handle)
        file_output.setFormatter(FORMATTER)
        self.logger.addHandler(file_output)
        self.file_handlers.append(file_output)

    def add_filehandler(self, file_handler: logging.FileHandler):
        self.logger.addHandler(file_handler)

    def _log(self, log_type: Callable, with_code: Union[bool, Any], *output: Any) -> None:
        if with_code:
            log_type("$CODE::" + with_code + " || " +
                     utils.concat_tuple(output))
        else:
            log_type(utils.concat_tuple(output))

    def info(self, with_code: Union[bool, Any], *output: Any) -> None:
        self._log(self.logger.info, with_code, *output)

    def debug(self, with_code: Union[bool, Any], *output: Any) -> None:
        self._log(self.logger.debug, with_code, *output)

    def error(self, with_code: Union[bool, Any], *output: Any) -> None:
        self._log(self.logger.error, with_code, *output)

    def warning(self, with_code: Union[bool, Any], *output: Any) -> None:
        self._log(self.logger.warning, with_code, *output)

    def info_if(self, condition: bool, *output: Any) -> None:
        if condition:
            self.info(*output)

    def debug_if(self, condition: bool, *output: Any) -> None:
        if condition:
            self.debug(*output)

    def error_if(self, condition: bool, *output: Any) -> None:
        if condition:
            self.error(*output)

    def warning_if(self, condition: bool, *output: Any) -> None:
        if condition:
            self.warning(*output)
