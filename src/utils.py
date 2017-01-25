import logging
import os


# Logger Exceptions
class WrongLoggingLvl(Exception):
    def __init__(self, value):
        self.value = value + ": Logging Level not valid"

    def __str__(self):
        return repr(self.value)


class Logger:
    # Possible Log Level
    log_lvls = {
        "CRITICAL": 50,
        "ERROR": 40,
        "WARNING": 30,
        "INFO": 20,
        "DEBUG": 10,
        "NOTSET": 0
    }

    def __init__(self, logger_name, file_name=None, ch_lvl=0, file_lvl=0):
        # Check logging lvl, throws if invalid
        self.check_logging_lvl(ch_lvl)
        self.check_logging_lvl(file_lvl)

        # Init Logger
        self.logger = logging.getLogger(logger_name)

        # Console Handler
        ch_handler = logging.StreamHandler()
        ch_handler.setLevel(ch_lvl)
        ch_format = logging.Formatter("%(levelname)s - %(message)s")
        ch_handler.setFormatter(ch_format)
        self.logger.addHandler(ch_handler)

        # File Handler
        if file_name is not None:
            if not os.path.exists("log"):
                os.makedirs("log")
            file_handler = logging.FileHandler("log/" + file_name, "w",
                                               "utf-8")
            file_handler.setLevel(file_lvl)
            file_format = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def __del__(self):
        logging.shutdown()  # Don't log after this call!
        del (self.logger)

    def check_logging_lvl(self, lvl):
        if lvl not in self.log_lvls.keys() and lvl not in self.log_lvls.values(
        ):
            raise WrongLoggingLvl(lvl)
