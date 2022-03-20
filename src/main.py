"""Main module with def main()"""
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

👇Нажмите кнопку \"Календарь\", чтобы увидеть, что запланировано на ближайшее будущее"
"""

LESSONS_SCHEDULE = """
Понедельник:
1) Химия 
2) Алгебра
3) Английский язык (у своих учителей)
4) Информатика
5) Обществознание
6) Физкультура 

Вторник:
1) Английский язык 
    (у группы Браниновой - Лукина,
    у группы Лукиной - Рудь, 
    у группы Рудь - Бранинова)
2) Геометрия
3) Русский
4) Электив по русскому/математике 
5) История
6) ОБЖ

Среда:
1) Английский язык
    (у группы Браниновой - Рудь,
    у группы Рудь - Лукина,
    у группы Лукиной - Бранинова)
2) Электив по математике/русскому
3) Литература 
4) Физика
5) История
6) Физкультура

Четверг:
1) Астрономия
2) Английский язык (у своих учителей)
3) Английский язык
    (у группы Рудь - Бранинова,
    у группы Браниновой - Лукина,
    у группы Лукины - Рудь)
4) Русский
5) Литература
6) География

Пятница:
1) Английский язык (у группы Браниновой - Рудь,
    у группы Рудь - Лукина,
    у группы Лукиной - Бранинова)
2) Биология
3) История
4) Обществознание 
5) Алгебра
6) Геометрия 

Суббота:
1) Литература
2) Физика
3) Электив по биологии/обществознанию
4) Физкультура
5) Алгебра
6) Электив по истории/литературе
"""

FOOD_CANTEEN_SCHEDULE = """
1 неделя
🍑Понедельник: борщ без фасоли, плов, капуста, яблоко
🍑Вторник: гороховый суп, пюре вкусное с рыбной котлетой, морковь, йогурт
🍑Среда: овощной суп со свежей капустой, куриная котлета с масленными макаронами, винегрет, яблоко, оранжевый сок
🍑Четверг: рассольник, ленивые голубцы, помидоры с луком, апельсин, компот
🍑Пятница: суп с лапшой, курицей и картошкой, рыба гадкая с картошкой, огурцы маринованные с луком, йогурт, морс
🍑Суббота: щи с перловкой, гречка с печенкой, свекла, яблоко, сок
2 неделя
🍑Понедельник: овощной суп со свежей капустой, рис с куриной котлетой в сыре, оливье без соуса школьный, сок яблочный, яблоко
🍑Вторник: рыбный суп, рагу, салат из капусты яблока и морковки, йогурт
🍑Среда: борщ с фасолью, гречка с котлетой вкусной, булка с творогом, полпомидора
🍑Четверг: рассольник, рыба в яйце с пюре, свекла, йогурт
🍑Пятница: похлебка крестьянская, курица в сперме, морковка, яблоко
🍑Суббота: суп с картошкой, тушеные овощи с куриной котлетой, маринованный огурец, яблочный сок, яблоко
""" 

subjects = {
        "Русский", 
        "Литература", 
        "Алгебра", 
        "Геометрия", 
        "Профильная математика", 
        "Базовая математика",
        "Информатика (Марина Гарриевна)",
        "Информатика (Попова)",
        "История",
        "Электив по истории",
        "Обществознание",
        "Биология",
        "Электив по биологии",
        "Химия",
        "Физика",
        "Астрономия",
        "ОБЖ",
        "Аглийский язык (Бранинова)",
        "Аглийский язык (Лукина)",
        "Аглийский язык (Рудь)",
        "География",
        "Физкультура",
}

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

# Schedule lesson command
def _cmd_lessons_schedule():
    return (
        LESSONS_SCHEDULE,
        None   
    )

# Schedule food_canteen command
def _cmd_foodCanteen_schedule():
    return (
        FOOD_CANTEEN_SCHEDULE,
        None
    )
        

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
                f"<code>👉</code> {event}\n"
                for (order, event) in enumerate(events_map[time], 1)
            ]
        )
        datestring = datetime.datetime.fromtimestamp(time).strftime("%d.%m (%a)")
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
    database.add_event(text, date.timestamp())
    tb.send_all(database.get_user_list(), f'🗓 {date.strftime("%d.%m")} - {text}')
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


def _parse_text(message):
    if message.text is None:
        return (None, "Поле не может быть пустым")
    return (message.text, None)


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
    database.add_hw(subject, date.timestamp(), text)
    # tb.send_all(
    #     database.get_user_list(), f'{date.strftime("%d.%m")} - {subject}: {text}'
    # )
    return "Задание добавлено 📚", None

def gen_homework_menu():
    """Generates menu for homework"""
    return Keyboard(
        [
            for i in subjects
        ]
    )

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
                KB: gen_homework_menu(),
                MESSAGE: "Напишите предмет дз",
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


# Homework command
def _cmd_homework(_tb, _message, _args):
    now = datetime.datetime.now().timestamp()
    hw_list = database.get_hw_since(now - 60 * 60 * 24 * 7)

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
        res_message += f"<code><b>📌 {datestring}</b></code>\n{local_message}\n\n"

    return res_message, None


def format_hw(hw):
    """Formats homework statement"""
    text = hw[TEXT]
    subject = hw[SUBJECT]

    if len(text.splitlines()) > 1:
        text = "".join(["\n" + line for line in text.splitlines()])

    return f"<code>📚 {subject}</code>: {text}"


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
                _gen_cmd_add_event(),
                CMD_HOMEWORK,
                _gen_cmd_add_homework(),
                _cmd_lessons_schedule,
                _cmd_foodCanteen_schedule,
                CMD_HELP,
                CMD_START,
            ]
        )
    else:
        return _build_interface(
            [
                CMD_CALENDAR, 
                CMD_HOMEWORK, 
                _cmd_lessons_schedule, 
                _cmd_foodCanteen_schedule, 
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
