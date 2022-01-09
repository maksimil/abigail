INFO = ["[INFO]", "34"]
ERROR = ["[ERROR]", "31"]

BOT = ["[BOT]", "34"]
MESSAGE = ["[MESSAGE]", "32"]

DB = ["[DB]", "32"]


def logmessage(tags, message):
    tag = ""
    for (tagname, color) in tags:
        tag += f"\x1b[{color}m{tagname}\x1b[0m"
    return tag + message


def log(tags, message):
    """
    general logger funtion
    """
    print(logmessage(tags, message))


def bot_message(message):
    """
    logs the telebot message object
    """
    log([BOT, MESSAGE], f"{message.chat.username}[{message.chat.id}]> {message.text}")


def error(tag, message):
    log([tag, ERROR], message)


def info(tag, message):
    log([tag, INFO], message)
