"""Main module with def main()"""
import time
import os
import re
import datetime
from bot import ARGS, FUNC, KB, MESSAGE, PARSER, HIDDEN, Keyboard
import bot
import database
from database import TIMESTAMP, TEXT, SUBJECT
import log

# Logger initialization
logger = log.Logger(["MAINBOT", log.FYELLOW])

# message configs
GREETING_MESSAGE = """Привет👋

Через меня вы будетe получать следующую полезную информацию:
📝Домашние задания
🕘Общие мероприятия (школьные концерты, сбор макулатуры и т.д.)
📆События в классе (даты экзаменов, контрольных, экскурсий и т.п)

Всё будет приходить прямо в этот чат

👇Нажте кнопку \"Календарь\" и увидишь, что запланировано на ближайшее будущее"
"""

HELP = "help"
CMD = "cmd"


# Start command
def _cmd_start(_tb, message, _args):
    chatid = message.chat.id
    # adding user to the database
    database.add_user(chatid, False)
    return GREETING_MESSAGE, None


CMD_START = {
    CMD: "/start",
    HIDDEN: True,
    ARGS: {},
    FUNC: _cmd_start,
}


# Help command
def _cmd_help(tb, message, _args):
    interf = _interface(tb, message.chat.id)
    docstring = ""
    for key, value in interf.items():
        if value.get(HELP):
            docstring += f"{key} - {value[HELP]}\n"
    return f"Как пользоваться? ⚙\n{docstring}", None


CMD_HELP = {CMD: "Справочник ⚙", HELP: "Выводит справку", ARGS: {}, FUNC: _cmd_help}


# Calendar command
def _cmd_calendar(_tb, _message, _args):
    now = datetime.datetime.now().timestamp()
    event_list = database.get_events_since(now - 60 * 60 * 24)

    if len(event_list) == 0:
        return (
            "Пока ничего не запланировано. Можно отдохнуть 🙃",
            None,
        )

    events_map = {}
    for event in event_list:
        if events_map.get(event[TIMESTAMP]) is None:
            events_map[event[TIMESTAMP]] = []
        events_map[event[TIMESTAMP]].append(event[TEXT])

    res_message = ""
    times_list = list(events_map.keys())
    times_list.sort()

    for time in times_list:
        local_message = "".join(
            [
                f"<code>{order}</code>: {event}\n"
                for (order, event) in enumerate(events_map[time], 1)
            ]
        )
        datestring = datetime.datetime.fromtimestamp(time).strftime("%d.%m (%a)")
        res_message += f"<b>📌 {datestring}</b>\n{local_message}\n"

    return res_message, None


CMD_CALENDAR = {
    CMD: "Календарь 🗓",
    HELP: "Показывает список дат и прикрепленных к ним событий",
    ARGS: {},
    FUNC: _cmd_calendar,
}


# Add event command
def _cmd_add_event(_tb, _message, args):
    date, _ = args["date"]
    text, _ = args["text"]
    database.add_event(text, date.timestamp())
    # tb.send_all(database.get_user_list(), f'{date.strftime("%d.%m")} - {text}')
    return "Календарь обновлён 🗓", None


def _parse_date(message):
    try:
        text = message.text
        day, month, year = re.findall("^(.*)\\.(.*)\\.(.*)$", text)[0]

        date = datetime.datetime(int(year), int(month), int(day))

        if date < datetime.datetime.now() - datetime.timedelta(days=1):
            return None, "Дата слишком старая"

        return datetime.datetime(int(year), int(month), int(day)), None

    except Exception as err:
        logger.warn(f"Handled: {err}")
        return None, "Пожалуйста отправляйте дату в формате дд.мм.гггг"


def gen_date_menu(cols, rows):
    """Generates menu for date"""
    now = datetime.datetime.now()
    dayspan = datetime.timedelta(days=1)
    return Keyboard(
        [
            [(now + dayspan * (cols * i + j)).strftime("%d.%m.%Y") for j in range(cols)]
            for i in range(rows)
        ]
    )


CMD_ADD_EVENT = {
    CMD: "Добавить событие 🗓",
    HELP: "Позволяет Вам добавить событие в календарь на конкретную дату.",
    ARGS: {
        "date": {
            KB: gen_date_menu(2, 8),
            MESSAGE: "Выберите дату",
            PARSER: _parse_date,
        },
        "text": {
            KB: Keyboard(),
            MESSAGE: "Напишите название события",
            PARSER: lambda message: (message.text, None),
        },
    },
    FUNC: _cmd_add_event,
}


def _cmd_add_homework(_tb, _message, args):
    subject, _ = args["subject"]
    date, _ = args["date"]
    text, _ = args["text"]
    database.add_hw(subject, date.timestamp(), text)
    # tb.send_all(
    #     database.get_user_list(), f'{date.strftime("%d.%m")} - {subject}: {text}'
    # )
    return "Задание добавлено 📚", None


CMD_ADD_HOMEWORK = {
    CMD: "Добавить дз 📚",
    HELP: "Добавляет дз",
    ARGS: {
        "date": {
            KB: gen_date_menu(2, 8),
            MESSAGE: "К какому сроку нужно сдать это дз?",
            PARSER: _parse_date,
        },
        "subject": {
            KB: Keyboard(),
            MESSAGE: "Напишите предмет дз",
            PARSER: lambda message: (message.text, None),
        },
        "text": {
            KB: Keyboard(),
            MESSAGE: "Какое содержание дз?",
            PARSER: lambda message: (message.text, None),
        },
    },
    FUNC: _cmd_add_homework,
}

# Homework command
def _cmd_homework(_tb, _message, _args):
    now = datetime.datetime.now().timestamp()
    hw_list = database.get_hw_since(now - 60 * 60 * 24)

    # logger.info(hw_list)

    if len(hw_list) == 0:
        return ("Пока домашний заданий нет", None)

    hw_map = {}
    for hw in hw_list:
        if hw_map.get(hw[TIMESTAMP]) is None:
            hw_map[hw[TIMESTAMP]] = []
        hw_map[hw[TIMESTAMP]].append(hw)

    res_message = ""
    times_list = list(hw_map.keys())
    times_list.sort()

    for time in times_list:
        hws = hw_map[time]
        hws.sort(key=lambda hw: hw[SUBJECT])

        local_message = "\n".join([format_hw(hw) for hw in hws])
        datestring = datetime.datetime.fromtimestamp(time).strftime("%d.%m (%a)")
        res_message += f"<b>📌 {datestring}</b>\n{local_message}\n\n"

    return res_message, None


def format_hw(hw):
    """Formats homework statement"""
    text = hw[TEXT]
    subject = hw[SUBJECT]

    if len(text.splitlines()) > 1:
        text = "".join(["\n" + line for line in text.splitlines()])

    return f"<code>{subject}</code>: {text}"


CMD_HOMEWORK = {
    CMD: "Домашнее задание 📚",
    HELP: "Показывает домашнее задание",
    ARGS: {},
    FUNC: _cmd_homework,
}


def _build_interface(cmds):
    return {item[CMD]: item for item in cmds}


def _interface(_tb, chatid):
    if database.is_teacher(chatid):
        return _build_interface(
            [
                CMD_CALENDAR,
                CMD_ADD_EVENT,
                CMD_HOMEWORK,
                CMD_ADD_HOMEWORK,
                CMD_HELP,
                CMD_START,
            ]
        )
    else:
        return _build_interface([CMD_CALENDAR, CMD_HOMEWORK, CMD_START, CMD_HELP])


def _main():
    # Database initialization
    database.init_db()

    logger.info("Initializing the bot")
    token = os.getenv("TELEGRAM_TOKEN")
    tb = bot.Bot(token, _interface)

    logger.info("Start polling")
    tb.start()


if __name__ == "__main__":
    _main()
