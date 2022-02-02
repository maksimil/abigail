"""
Logger module
"""
import datetime

# foreground colors
FBLACK = "30"
FRED = "31"
FGREEN = "32"
FYELLOW = "33"
FBLUE = "34"
FMAGENTA = "35"
FCYAN = "36"
FWHITE = "37"

# background colors
BBLACK = "40"
BRED = "41"
BGREEN = "42"
BYELLOW = "43"
BBLUE = "44"
BMAGENTA = "45"
BCYAN = "46"
BWHITE = "47"

# tags
INFO = ["INFO", FBLUE]
WARN = ["WARN", FYELLOW]
ERROR = ["ERROR", FRED]


def _logmessage(tags, message):
    message = str(message)
    tag = ""
    for (tagname, color) in tags:
        tag += f"\x1b[{color}m[{tagname}]\x1b[0m"
    timestamp = datetime.datetime.now().isoformat(" ", timespec="seconds")
    return f"[{timestamp}]{tag}{_inline_text(message)}"


def _log(tags, message):
    print(_logmessage(tags, message))


def _inline_text(text):
    """
    Inlines text for terminal output
    """
    return f"\x1b[{BWHITE};{FBLACK}m\\n\x1b[0m".join(text.splitlines())


class Logger:
    """
    Logger class for module prefix
    """

    def __init__(self, mod):
        self._mod = mod

    def info(self, message):
        """
        Logs with [INFO]
        """
        self.log([INFO], message)

    def error(self, message):
        """
        Logs with [ERROR]
        """
        self.log([ERROR], message)

    def warn(self, message):
        """
        Logs with [WARN]
        """
        self.log([WARN], message)

    def log(self, tags, message):
        """
        Logs with [tag]
        """
        _log([self._mod, *tags], message)
