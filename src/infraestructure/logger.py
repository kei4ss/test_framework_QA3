import logging
import logging.handlers
import os
from src.config.settings import settings
from src.config.logging_config import (
    ERROR_LOG_FILENAME, GENERAL_LOG_FILENAME, LOG_FORMAT, LOG_DATE_FORMAT,
    MAX_BYTES, BACKUP_COUNT,
    SensitiveDataFormatter
)


class Logger:
    __instance = None
    __initialized = False

    def __new__(cls, log_level: str = None, log_dir: str = None):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, log_level: str = None, log_dir: str = None):
        if self.__initialized:
            return

        resolved_level = (
            log_level
            or settings().global_config().get("log_level", "INFO")
        )
        resolved_dir = (
            log_dir
            or os.path.join(os.path.dirname(__file__), "../../logs")
        )

        numeric_level = getattr(logging, resolved_level.upper(), logging.INFO)

        os.makedirs(resolved_dir, exist_ok=True)

        self.__logger = logging.getLogger("SentinelaLogger")
        self.__logger.setLevel(numeric_level)

        if self.__logger.hasHandlers():
            self.__logger.handlers.clear()

        formatter = SensitiveDataFormatter(
            fmt=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        self.__logger.addHandler(console_handler)

        general_log_path = os.path.join(resolved_dir, GENERAL_LOG_FILENAME)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=general_log_path,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        self.__logger.addHandler(file_handler)

        error_log_path = os.path.join(resolved_dir, ERROR_LOG_FILENAME)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_log_path,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(formatter)
        self.__logger.addHandler(error_handler)

        self.__initialized = True
        self.__logger.info(
            "Logger inicializado | nível=%s | diretório=%s",
            resolved_level.upper(),
            resolved_dir
        )

    def debug(self, message: str, *args, **kwargs) -> None:
        self.__logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self.__logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self.__logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self.__logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self.__logger.critical(message, *args, **kwargs)

    def log_request(
        self,
        method: str,
        url: str,
        status_code: int,
        response_time: float
    ) -> None:
        log_message = (
            f"HTTP {method.upper()} {url} → {status_code} ({response_time:.3f}s)"
        )
        if status_code >= 400:
            self.error(log_message)
        else:
            self.info(log_message)

    def get_logger(self) -> logging.Logger:
        return self.__logger