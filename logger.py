import datetime
import os
from os import listdir
from zipfile import ZipFile


class ChatColor:
    """
    Enum class for console colors
    """
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LogLevel:
    """
    Enum class for Log levels
    """
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3
    DEBUG = 4
    CUSTOM = 5

    @classmethod
    def to_string(cls, log_level: int) -> str:
        """
        :param log_level: the log level
        :return: the string representation of that log level
        """
        if log_level == LogLevel.INFO:
            return "INFO"

        if log_level == LogLevel.WARNING:
            return "WARNING"

        if log_level == LogLevel.ERROR:
            return "ERROR"

        if log_level == LogLevel.CRITICAL:
            return "CRITICAL"

        if log_level == LogLevel.DEBUG:
            return "DEBUG"

    @classmethod
    def to_color(cls, log_level: int) -> str:
        """
        :param log_level: the log level
        :return: the corresponding color of that log level
        """
        if log_level == LogLevel.INFO:
            return ChatColor.END

        if log_level == LogLevel.WARNING:
            return ChatColor.YELLOW

        if log_level == LogLevel.ERROR:
            return ChatColor.RED

        if log_level == LogLevel.CRITICAL:
            return ChatColor.BOLD + ChatColor.RED

        if log_level == LogLevel.DEBUG:
            return ChatColor.PINK


logger = None


def get_logger():
    """
    Don't create a logger instance yourself!
    use this function to retrieve one.

    :return: The logger instance
    """
    return logger


class Logger:
    """
    A custom logger class
    Also creates custom log files in /logs
    """
    def __init__(self):
        global logger

        self.path = os.path.dirname(__file__) + "/logs/"
        self.console_fmt = f"[{{0}} {{1}} {{2}}{ChatColor.END}]: {{3}} {{4}}{ChatColor.END}"
        self.file_fmt = "[{0} {1}]: {2}"
        self.file_dt_fmt = "%d-%m-%Y"
        logger = self

    def start_up(self) -> None:
        now = datetime.datetime.now()

        cleanup = False
        for f in listdir(self.path):
            if f == f"{now.strftime(self.file_dt_fmt)}.tendo.log":
                with open(self.path + f, "a+") as fh:
                    fh.write(f"\n{'=' * 10} < RESTART > {'=' * 10}\n")
                return
            elif f.endswith("tendo.log"):
                cleanup = True

        if cleanup:
            self.clean_up()

    def clean_up(self) -> None:
        """
        Cleans up the log files
        """
        now = datetime.datetime.now()

        for f in listdir(self.path):
            if f.endswith(".tendo.log") and not f == f"{now.strftime(self.file_dt_fmt)}.tendo.log":
                with ZipFile(self.path + f.replace(".tendo.log", ".log.zip"), "w") as new_zip:
                    new_zip.write(self.path + f)

                os.remove(self.path + f)

    def newline(self):
        """
        Prints a new line
        """
        print("\n")

        now = datetime.datetime.now()

        cleanup = False
        for f in listdir(self.path):
            if f == f"{now.strftime(self.file_dt_fmt)}.tendo.log":
                with open(self.path + f, "a+") as fh:
                    fh.write("\n")
                return
            elif f.endswith("tendo.log"):
                cleanup = True

        if cleanup:
            self.clean_up()

    def log(self, log_level: int, log_message: str) -> None:
        """
        Logs a message

        :param log_level: the log level
        :param log_message: the log message
        :return: None
        """
        now = datetime.datetime.now()
        string = self.console_fmt.format(  # noqa
            now.strftime("%d.%m.%y %H:%M:%S"),
            LogLevel.to_color(log_level),
            LogLevel.to_string(log_level),
            LogLevel.to_color(log_level),
            log_message
        )

        print(string)

        string = self.file_fmt.format(now.strftime("%d.%m.%Y %H:%M:%S"), LogLevel.to_string(log_level), log_message)  # noqa

        cleanup = False
        for f in listdir(self.path):
            if f == f"{now.strftime(self.file_dt_fmt)}.tendo.log":
                with open(self.path + f, "a+") as fh:
                    fh.write("\n" + string)
                return
            elif f.endswith("tendo.log"):
                cleanup = True

        if cleanup:
            self.clean_up()

        open(now.strftime(self.path + self.file_dt_fmt + ".tendo.log"), "w+").close()
        with open(now.strftime(self.path + self.file_dt_fmt + ".tendo.log"), "w") as fh:
            fh.write("\n" + string)

    def info(self, log_message: str) -> None:
        """
        Logs an info message
        Wrapper for log(LogLevel.INFO, log_message)

        :param log_message: The displayed log message
        :return: None
        """

        self.log(LogLevel.INFO, log_message)

    def warning(self, log_message: str) -> None:
        """
        Logs a warning message
        Wrapper for log(LogLevel.WARNING, log_message)

        :param log_message: The displayed log message
        :return: None
        """

        self.log(LogLevel.WARNING, log_message)

    def error(self, log_message: str, prevent_exception: bool = False) -> None:
        """
        Logs an error message
        Raises an exception unless prevent_exception is True
        Wrapper for log(LogLevel.ERROR, log_message)

        :param log_message: The displayed log message
        :param prevent_exception: Prevents the exception from being raised
        :return: None
        """

        self.log(LogLevel.ERROR, log_message)

        if not prevent_exception:
            raise Exception(log_message)

    def critical(self, log_message: str, prevent_exception: bool = False) -> None:
        """
        Logs a critical message
        Raises an exception unless prevent_exception is True
        Wrapper for log(LogLevel.CRITICAL, log_message)

        :param log_message: The displayed log message
        :param prevent_exception: Prevents the exception from being raised
        :return: None
        """

        self.log(LogLevel.CRITICAL, log_message)

        if not prevent_exception:
            raise Exception(log_message)

    def debug(self, log_message: str) -> None:
        """
        Logs a debug message
        Wrapper for log(LogLevel.DEBUG, log_message)

        :param log_message: The displayed log message
        :return: None
        """

        self.log(LogLevel.DEBUG, log_message)
