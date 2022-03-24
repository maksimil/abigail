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
<code><b>📌 Понедельник</b></code>
<code>1)</code> Химия
<code>2)</code> Алгебра
<code>3)</code> Английский язык (у своих учителей)
<code>4)</code> Информатика
<code>5)</code> Обществознание
<code>6)</code> Физкультура

<code><b>📌 Вторник</b></code>
<code>1)</code> Английский язык
    (у группы Браниновой - Лукина,
    у группы Лукиной - Рудь, 
    у группы Рудь - Бранинова)
<code>2)</code> Геометрия
<code>3)</code> Русский
<code>4)</code> Электив по русскому/математике
<code>5)</code> История
<code>6)</code> ОБЖ

<code><b>📌 Среда</b></code>
<code>1)</code> Английский язык
    (у группы Браниновой - Рудь,
    у группы Рудь - Лукина,
    у группы Лукиной - Бранинова)
<code>2)</code> Электив по математике/русскому
<code>3)</code> Литература
<code>4)</code> Физика
<code>5)</code> История
<code>6)</code> Физкультура

<code><b>📌 Четверг</b></code>
<code>1)</code> Астрономия
<code>2)</code> Английский язык (у своих учителей)
<code>3)</code> Английский язык
    (у группы Рудь - Бранинова,
    у группы Браниновой - Лукина,
    у группы Лукины - Рудь)
<code>4)</code> Русский
<code>5)</code> Литература
<code>6)</code> География

<code><b>🍻 Пятница</b></code>
<code>1)</code> Английский язык (у группы Браниновой - Рудь,
    у группы Рудь - Лукина,
    у группы Лукиной - Бранинова)
<code>2)</code> Биология
<code>3)</code> История
<code>4)</code> Обществознание
<code>5)</code> Алгебра
<code>6)</code> Геометрия

<code><b>🍻 Суббота</b></code>
<code>1)</code> Литература
<code>2)</code> Физика
<code>3)</code> Электив по биологии/обществознанию
<code>4)</code> Физкультура
<code>5)</code> Алгебра
<code>6)</code> Электив по истории/литературе
"""

FOOD_CANTEEN_SCHEDULE = """
<code><b>1 неделя</b></code>
<code>🍑 Понедельник</code>: борщ без фасоли, плов, капуста, яблоко
<code>🍑 Вторник</code>: гороховый суп, пюре вкусное с рыбной котлетой, морковь, йогурт
<code>🍑 Среда</code>: овощной суп со свежей капустой, куриная котлета с масленными макаронами, винегрет, яблоко, оранжевый сок
<code>🍑 Четверг</code>: рассольник, ленивые голубцы, помидоры с луком, апельсин, компот
<code>🍻 Пятница</code>: суп с лапшой, курицей и картошкой, рыба гадкая с картошкой, огурцы маринованные с луком, йогурт, морс
<code>🍻 Суббота</code>: щи с перловкой, гречка с печенкой, свекла, яблоко, сок

<code><b>2 неделя</b></code>
<code>🍑 Понедельник</code>: овощной суп со свежей капустой, рис с куриной котлетой в сыре, оливье без соуса школьный, сок яблочный, яблоко
<code>🍑 Вторник</code>: рыбный суп, рагу, салат из капусты яблока и морковки, йогурт
<code>🍑 Среда</code>: борщ с фасолью, гречка с котлетой вкусной, булка с творогом, полпомидора
<code>🍑 Четверг</code>: рассольник, рыба в яйце с пюре, свекла, йогурт
<code>🍻 Пятница</code>: похлебка крестьянская, курица в сметанном соусе, морковка, яблоко
<code>🍻 Суббота</code>: суп с картошкой, тушеные овощи с куриной котлетой, маринованный огурец, яблочный сок, яблоко
"""

SUBJECTS_MENU = Keyboard(
    [
        ["Русский", "Литература"],
        ["Алгебра", "Геометрия"],
        ["Профильная математика"],
        ["Базовая математика"],
        ["Информатика (Марина Гарриевна)"],
        ["Информатика (Попова)"],
        ["История", "Биология"],
        ["Электив по истории"],
        ["Обществознание", "ОБЖ"],
        ["Электив по биологии"],
        ["Химия", "Физика"],
        ["Астрономия", "География"],
        ["Английский язык (группа Браниновой)"],
        ["Английский язык (группа Лукиной)"],
        ["Английский язык (группа Рудь)"],
        ["Физкультура"],
    ]
)

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


CMD_HELP = {
    CMD: "Справочник ⚙",
    HELP: "Выводит это сообщение",
    ARGS: {},
    FUNC: _cmd_help,
}


# Schedule lesson command
def _cmd_lessons_schedule(_tb, _message, _args):
    return (LESSONS_SCHEDULE, None)


CMD_LESSONS_SCHEDULE = {
    CMD: "Расписание уроков 🪧",
    HELP: "Показывает расписание уроков",
    ARGS: {},
    FUNC: _cmd_lessons_schedule,
}


# Schedule food_canteen command
def _cmd_food_сanteen_schedule(_tb, _message, _args):
    return (FOOD_CANTEEN_SCHEDULE, None)


CMD_FOOD_CANTEEN_SCHEDULE = {
    CMD: "Расписание столовой 🍻",
    HELP: "Показывает расписание еды в столовой",
    ARGS: {},
    FUNC: _cmd_food_сanteen_schedule,
}

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
                KB: SUBJECTS_MENU,
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

def _parse_date_hw(message):
    if message.text == "Старое д/з":
        return database.get_hw_period(now - 60*60*24*7, now), None
    elif message.text == "Новое д/з":
        return database.get_hw_since(now - 60 * 60 * 24), None
    elif message.text == "Все д/з":
        return database.get_hw_since(now - 60 * 60 * 24 * 7), None
    try:
        text = message.text
        day, month, year = re.findall("^(.*)\\.(.*)\\.(.*)$", text)[0]

        date = datetime.datetime(int(year), int(month), int(day))

        return database.get_hw_date(date.timestamp()), None

    except Exception as err:
        logger.warn(f"Handled: {err}")
        return None, "Пожалуйста выберите один из вариантов. Не надо вводить свой."

def gen_date_menu_hw():
    hw_list = database.get_hw_since(now - 60 * 60 * 24 * 7)
    ts = set()
    for hw in hw_list:
        ts.add(hw[TIMESTAMP])
    ts = list(ts)
    ts.sort()
    kb = []

    for i in range(len(ts) // 2):
        kb.append(ts[2 * i : 2 * i + 2])

    if len(ts) % 2 != 0:
        kb.append([ts[-1]])

    return Keyboard(
        [
            ["Старое д/з", "Новое д/з"],
            ["Все д/з"],
            [kb[i+j].datetime().strftime("%d.%m.%Y") for j in range(2)]
            for i in range(0, len(kb)-1, 2)
        ]
    )

# Homework command
def _cmd_homework(_tb, _message, args):
    now = datetime.datetime.now().timestamp()
    hw_list, _ = args["date"]

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
    text = hw[TEXT]
    subject = hw[SUBJECT]

    if len(text.splitlines()) > 1:
        text = "".join(["\n" + line for line in text.splitlines()])

    return f"<code>📚 {subject}</code>: {text}"


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
