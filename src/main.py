"""Main module with def main()"""
import os
import re
import datetime
from bot import ARGS, FUNC, KB, MESSAGE, PARSER, HIDDEN, Keyboard
import bot
import database
from database import Event, Homework
import log
import config

# Logger initialization
logger = log.Logger(["MAINBOT", log.FYELLOW])

# message configs
HELP = "help"
CMD = "cmd"


# Start command
def _cmd_start(_tb, message, _args):
    chatid = message.chat.id
    # adding user to the database
    database.add_user(chatid, False)
    return config.GREETING_MESSAGE, None


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


CMD_HELP = {
    CMD: "Справочник ⚙",
    HELP: "Выводит это сообщение",
    ARGS: {},
    FUNC: _cmd_help,
}


# Schedule lesson command
def _cmd_lessons_schedule(_tb, _message, _args):
    return config.LESSONS_SCHEDULE, None


CMD_LESSONS_SCHEDULE = {
    CMD: "Расписание уроков 🪧",
    HELP: "Показывает расписание уроков",
    ARGS: {},
    FUNC: _cmd_lessons_schedule,
}


# Schedule food_canteen command
def _cmd_food_сanteen_schedule(_tb, _message, _args):
    return config.FOOD_CANTEEN_SCHEDULE, None


CMD_FOOD_CANTEEN_SCHEDULE = {
    CMD: "Расписание столовой 🍻",
    HELP: "Показывает расписание еды в столовой",
    ARGS: {},
    FUNC: _cmd_food_сanteen_schedule,
}


# Calendar command
def _cmd_calendar(_tb, _message, _args):
    now = datetime.datetime.now()
    event_list = database.get_event_date({"$gte": now - datetime.timedelta(days=1)})

    if len(event_list) == 0:
        return (
            "Пока ничего не запланировано. Можно отдохнуть 🙃",
            None,
        )

    events_map = {}
    for event in event_list:
        if events_map.get(event.date) is None:
            events_map[event.date] = []
        events_map[event.date].append(event.text)

    res_message = ""
    times_list = list(events_map.keys())
    times_list.sort()

    for time in times_list:
        local_message = "".join(
            [
                f"<code>👉</code> {event}\n"
                for (order, event) in enumerate(events_map[time], 1)
            ]
        )
        datestring = time.strftime("%d.%m (%a)")
        res_message += f"<code><b>📌 {datestring}</b></code>\n{local_message}\n"

    return res_message, None


CMD_CALENDAR = {
    CMD: "Календарь 🗓",
    HELP: "Показывает список дат и прикрепленных к ним событий",
    ARGS: {},
    FUNC: _cmd_calendar,
}


# Add event command
def _cmd_add_event(tb, _message, args):
    date, _ = args["date"]
    text, _ = args["text"]
    event = Event(date=date, text=text)
    database.add_event(event)
    tb.send_all(database.get_user_list(), f'🗓 {date.strftime("%d.%m")} - {text}')
    return "Календарь обновлён 🗓", None


def _parse_date(message):
    try:
        text = message.text
        day, month, year = re.findall("^(.*)\\.(.*)\\.(.*)$", text)[0]

        date = datetime.datetime(int(year), int(month), int(day))

        if date < datetime.datetime.now() - datetime.timedelta(days=1):
            return None, "Дата слишком старая"

        return date, None

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


def _parse_text(message):
    if message.text is None:
        return None, "Поле не может быть пустым"
    return message.text, None


def _gen_cmd_add_event():
    return {
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
                PARSER: _parse_text,
            },
        },
        FUNC: _cmd_add_event,
    }


def _cmd_add_homework(_tb, _message, args):
    subject, _ = args["subject"]
    date, _ = args["date"]
    text, _ = args["text"]
    database.add_hw(Homework(subject=subject, text=text, date=date))
    return "Задание добавлено 📚", None


def _gen_cmd_add_homework():
    return {
        CMD: "Добавить дз 📚",
        HELP: "Добавляет дз",
        ARGS: {
            "date": {
                KB: gen_date_menu(2, 8),
                MESSAGE: "К какому сроку нужно сдать это дз?",
                PARSER: _parse_date,
            },
            "subject": {
                KB: config.SUBJECTS_MENU,
                MESSAGE: "Выберите предмет дз",
                PARSER: _parse_text,
            },
            "text": {
                KB: Keyboard(),
                MESSAGE: "Какое содержание дз?",
                PARSER: _parse_text,
            },
        },
        FUNC: _cmd_add_homework,
    }


HW_BTN_OLD = "Старое д/з"
HW_BTN_NEW = "Новое д/з"
HW_BTN_ALL = "Все д/з"


def _parse_date_hw(message):
    now = datetime.datetime.now()
    daydelta = datetime.timedelta(days=1)

    if message.text == HW_BTN_OLD:
        return (
            database.get_hw_date({"$gte": now - daydelta * 7, "$lte": now}),
            None,
        )

    elif message.text == HW_BTN_NEW:
        return database.get_hw_date({"$gte": now - daydelta}), None

    elif message.text == HW_BTN_ALL:
        return database.get_hw_date({"$gte": now - daydelta * 7}), None

    try:
        text = message.text
        day, month, year = re.findall("^(.*)\\.(.*)\\.(.*)$", text)[0]

        date = datetime.datetime(int(year), int(month), int(day))

        return database.get_hw_date({"$gte": date, "$lt": date + daydelta}), None

    except Exception as err:
        logger.warn(f"Handled: {err}")
        return None, "Пожалуйста выберите один из вариантов. Не надо вводить свой."


def gen_date_menu_hw():
    now = datetime.datetime.now()
    hw_list = database.get_hw_date({"$gte": now - datetime.timedelta(days=7)})

    ts = set()
    for hw in hw_list:
        ts.add(hw.date)

    ts = list(ts)
    ts.sort()
    ts = [t.strftime("%d.%m.%Y") for t in ts]
    kb = []

    for i in range(len(ts) // 2):
        kb.append(ts[2 * i : 2 * i + 2])

    if len(ts) % 2 != 0:
        kb.append([ts[-1]])

    return Keyboard([[HW_BTN_ALL], [HW_BTN_OLD, HW_BTN_NEW], *kb])


# Homework command
def _cmd_homework(_tb, _message, args):
    now = datetime.datetime.now()
    hw_list, _ = args["date"]

    if len(hw_list) == 0:
        return "Пока домашний заданий нет", None

    hw_map = {}
    for hw in hw_list:
        if hw_map.get(hw.date) is None:
            hw_map[hw.date] = []
        hw_map[hw.date].append(hw)

    res_message = ""
    times_list = list(hw_map.keys())
    times_list.sort()

    for time in times_list:
        hws = hw_map[time]
        hws.sort(key=lambda hw: hw.subject)

        local_message = "\n".join([format_hw(hw) for hw in hws])
        datestring = time.strftime("%d.%m (%a)")
        res_message += f"<code><b>📌 {datestring}</b></code>\n{local_message}\n\n"

    return res_message, None


def _gen_cmd_homework():
    return {
        CMD: "Домашнее задание 📚",
        HELP: "Показывает домашнее задание",
        ARGS: {
            "date": {
                KB: gen_date_menu_hw(),
                MESSAGE: "Выберите временной промежуток",
                PARSER: _parse_date_hw,
            },
        },
        FUNC: _cmd_homework,
    }


def format_hw(hw):
    """Formats homework statement"""
    text = hw.text
    lines = text.splitlines()

    if len(lines) > 1:
        text = "".join(["\n" + line for line in lines])

    return f"<code>📚 {hw.subject}</code>: {text}"


def _build_interface(cmds):
    return {item[CMD]: item for item in cmds}


def _interface(_tb, chatid):
    if database.is_teacher(chatid):
        return _build_interface(
            [
                CMD_CALENDAR,
                _gen_cmd_add_event(),
                _gen_cmd_homework(),
                _gen_cmd_add_homework(),
                CMD_LESSONS_SCHEDULE,
                CMD_FOOD_CANTEEN_SCHEDULE,
                CMD_HELP,
                CMD_START,
            ]
        )
    else:
        return _build_interface(
            [
                CMD_CALENDAR,
                _gen_cmd_homework(),
                CMD_LESSONS_SCHEDULE,
                CMD_FOOD_CANTEEN_SCHEDULE,
                CMD_START,
                CMD_HELP,
            ]
        )


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
