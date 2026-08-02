# coreAgents/loggerAgent.py

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from coreAgents.pathAgent import PathAgent


class LoggerAgent:
    """
    Central logging agent for the framework.

    Creates one log file per execution
    and keeps only latest 30 execution log files.
    """

    MAX_LOG_FILES_TO_KEEP = 10

    LOG_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE_NAME = f"test_run_{LOG_TIMESTAMP}.log"
    LOG_FILE = PathAgent.LOGS_DIR / LOG_FILE_NAME

    LOG_LEVEL = getattr(
        logging,
        os.getenv("LOG_LEVEL", "DEBUG").upper(),
        logging.DEBUG,
    )

    FILE_HANDLER = None
    CONSOLE_HANDLER = None
    LOG_CLEANUP_DONE = False

    @classmethod
    def cleanup_old_logs(cls):
        """
        Keeps only latest 30 execution log files.
        Deletes older log files.
        """

        if cls.LOG_CLEANUP_DONE:
            return

        if not PathAgent.LOGS_DIR.exists():
            return

        log_files = [
            file
            for file in PathAgent.LOGS_DIR.iterdir()
            if file.is_file()
            and file.name.startswith("test_run_")
            and file.suffix == ".log"
        ]

        # Newest first
        log_files.sort(key=lambda file: file.stat().st_mtime, reverse=True)

        old_logs = log_files[cls.MAX_LOG_FILES_TO_KEEP:]

        for log_file in old_logs:
            try:
                log_file.unlink()
            except Exception:
                pass

        cls.LOG_CLEANUP_DONE = True

    @classmethod
    def get_file_handler(cls):
        """
        Creates file handler once.
        """

        if cls.FILE_HANDLER:
            return cls.FILE_HANDLER

        file_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        cls.FILE_HANDLER = RotatingFileHandler(
            cls.LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        cls.FILE_HANDLER.setLevel(cls.LOG_LEVEL)
        cls.FILE_HANDLER.setFormatter(file_formatter)

        cls.cleanup_old_logs()

        return cls.FILE_HANDLER

    @classmethod
    def get_console_handler(cls):
        """
        Creates console handler once.
        """

        if cls.CONSOLE_HANDLER:
            return cls.CONSOLE_HANDLER

        console_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )

        cls.CONSOLE_HANDLER = logging.StreamHandler()
        cls.CONSOLE_HANDLER.setLevel(logging.INFO)
        cls.CONSOLE_HANDLER.setFormatter(console_formatter)

        return cls.CONSOLE_HANDLER

    @classmethod
    def get_logger(cls, logger_name: str) -> logging.Logger:
        """
        Returns logger object.
        """

        logger = logging.getLogger(logger_name)

        if logger.handlers:
            return logger

        logger.setLevel(cls.LOG_LEVEL)
        logger.propagate = False

        logger.addHandler(cls.get_file_handler())
        logger.addHandler(cls.get_console_handler())

        return logger

    @classmethod
    def get_log_file(cls) -> Path:
        """
        Returns current execution log file path.
        """

        return cls.LOG_FILE

    @classmethod
    def get_log_file_name(cls) -> str:
        """
        Returns current execution log file name.
        """

        return cls.LOG_FILE_NAME