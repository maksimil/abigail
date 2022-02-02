"""
Main module
"""
import traceback
import os
import re
import datetime
from bot import ARGS, FUNC, HELP, KB, MESSAGE, PARSER, gen_menu, empty_menu
import bot
import database
import log

# Logger initialization
logger = log.Logger(["MAINBOT", log.FYELLOW])

# message configs
CALENDAR_BTN = "Календарь📆"
NOTICES_BTN = "Список напоминаний📃"
ADD_EVENT_BTN = "Добавить событие✏️"
ADD_NOTICE_BTN = "Установить напоминание⏰"
HELP_BTN = "Справочник⚙"

GREETING_MESSAGE = """Привет, человек👋

Через меня ты будешь получать следующую полезную инфу:
📝Домашние задания
🕘Общие мероприятия (школьные концерты, сбор макулатуры и т.д.)
📆События в классе (даты экзаменов, контрольных, экскурсий и т.п)

Всё будет приходить прямо в этот чат

👇Нажми кнопку \"Календарь\" и увидишь, что запланировано на ближайшее будущее"
"""

ID_OF_THE_TEACHER = 526809653  # id of the teacher


# Start command
def _cmd_start(_tb, message, _args):
    chatid = message.chat.id
    # adding user to the database
    database.add_user(
        chatid, chatid == ID_OF_THE_TEACHER
    )  # all_user_id.add(message.chat.id)
    all_user_id = database.get_user_list()
    logger.info(f"All user id: {all_user_id}")
    return bot.MessageText(GREETING_MESSAGE), None


CMD_START = {HELP: "Добавляет тебя как пользователя", ARGS: {}, FUNC: _cmd_start}


# Help command
def _cmd_help(tb, message, _args):
    docstring = tb.docstring(message.chat.id)
    return bot.MessageText(f"Как пользоваться? ⚙\n{docstring}"), None


CMD_HELP = {HELP: "Выводит справку", ARGS: {}, FUNC: _cmd_help}


# Calendar command
def _cmd_calendar(_tb, _message, _args):
    now = datetime.datetime.now().timestamp()
    event_list = database.get_events_since(now - 60 * 60 * 24)

    if len(event_list) == 0:
        return (
            bot.MessageText("Пока ничего не запланировано. Можно отдохнуть 🙃"),
            None,
        )

    events_map = {}
    for event in event_list:
        if events_map.get(event["timestamp"]) is None:
            events_map[event["timestamp"]] = []
        events_map[event["timestamp"]].append(event["text"])

    res_message = ""
    times_list = list(events_map.keys())
    times_list.sort()

    for time in times_list:
        local_message = "".join(
            [f"{order}) {event}\n" for (order, event) in enumerate(events_map[time], 1)]
        )
        datestring = datetime.datetime.fromtimestamp(time).strftime("%d.%m (%a)")
        res_message += f"📌 {datestring}:\n{local_message}"

    return bot.MessageText(res_message), None


CMD_CALENDAR = {
    HELP: "Показывает список дат и прикрепленных к ним событий",
    ARGS: {},
    FUNC: _cmd_calendar,
}


# Add event command
def _cmd_add_event(tb, _message, args):
    date, _ = args["date"]
    text, _ = args["text"]
    database.add_event(text, date.timestamp())
    tb.send_all(
        database.get_user_list(), bot.MessageText(f'{date.strftime("%d.%m")} - {text}')
    )
    return bot.MessageText("Календарь обновлён"), None


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


def gen_date_menu(size):
    """
    Generates menu for dates
    """
    now = datetime.datetime.now()
    dayspan = datetime.timedelta(days=1)
    return gen_menu([(now + dayspan * n).strftime("%d.%m.%Y") for n in range(size)])


CMD_ADD_EVENT = {
    HELP: "Позволяет Вам добавить событие в календарь на конкретную дату.",
    ARGS: {
        "date": {KB: gen_date_menu(16), MESSAGE: "Выберите дату", PARSER: _parse_date,},
        "text": {
            KB: empty_menu(),
            MESSAGE: "Напишите название события",
            PARSER: lambda message: (message.text, None),
        },
    },
    FUNC: _cmd_add_event,
}


# Send all command
def _cmd_send_all(tb, _message, args):
    message, _ = args["message"]
    tb.send_all(database.get_user_list(), bot.MessageCopy(message))
    return bot.MessageText("Сообщение разослано"), None


CMD_SEND_ALL = {
    HELP: "Рассылает всем сообщение",
    ARGS: {
        "message": {
            KB: empty_menu(),
            MESSAGE: "Введите сообщение (можно прикрепить фото или файлы)",
            PARSER: lambda message: (message, None),
        }
    },
    FUNC: _cmd_send_all,
}

KEY_START = "/start"
KEY_HELP = "Справочник ⚙"
KEY_CALENDAR = "Календарь 🗓"
KEY_ADD_EVENT = "Добавить событие 🗓"
KEY_SEND_ALL = "Отправить всем 💬"


def _interface(_tb, chatid):
    if database.is_teacher(chatid):
        return {
            KEY_START: CMD_START,
            KEY_HELP: CMD_HELP,
            KEY_CALENDAR: CMD_CALENDAR,
            KEY_ADD_EVENT: CMD_ADD_EVENT,
            KEY_SEND_ALL: CMD_SEND_ALL,
        }
    else:
        return {
            KEY_START: CMD_START,
            KEY_HELP: CMD_HELP,
            KEY_CALENDAR: CMD_CALENDAR,
        }


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
