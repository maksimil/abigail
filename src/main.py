import time
import datetime
from threading import Thread
import os
import telebot
from telebot import types
import database
import log

# global values
DATEFORMAT = "%d.%m (%a)"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


ID_OF_THE_TEACHER = 526809653  # id of the teacher

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

HELP_MESSAGE = """Как пользоваться? ⚙️

1)Календарь 🗓️ - показывает список дат и прикрепленных к ним событий, которые Вы уже добавили

2)Список напоминаний📃 - показывает список всех уже установленных Вами напоминаний, а так же даты и время, на которые они установлены

3)Добавить событие✏️ - позволяет Вам добавить событие в календарь на конкретную дату. Нажмите на кнопку, вам высветится список из предложенных 15-ти следующих дней, начиная с завтрашнего. Нажмите на одну из дат, или напишите в поле сообщения и отправьте свою дату в формате: дд.мм.гг. После вам высветится: "Напишите сообщение". Введите то, что вы хотите сообщить в поле сообщения и нажмите на синюю кнопку Отправить справа. Готово, Ваше событие в календаре

4)Установить напоминание⏰ -

5)Справочник⚙️ - выводит данное сообщение с объяснением, как всё работает"""

database.init_db()

log.info(log.BOT, "initializing the bot")
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None)  # bot's Token


def notice_update_loop():
    while True:
        notices = database.get_unmarked_notices()
        all_user_id = database.get_user_list()
        count = 0
        for notice in notices:
            send_all(all_user_id, notice["text"])

        time.sleep(10)


def send_all(ids, text):
    """
    Send a message to all the users
    """
    count = 0
    while True:
        try:
            for i in range(count, len(ids)):
                count += 1
                bot.send_message(ids[i], text)
                time.sleep(0.5)
            else:
                break
        except Exception as e:
            log.error(log.BOT, f"Error 403. {ids[i]} blocked me :(\n{str(e)}\n")


@bot.message_handler(commands=["start"])
def start(message):
    """
    adds new user to the database and greets them
    """
    log.bot_message(message)
    # adding user to the database
    database.add_user(
        message.chat.id, message.chat.id == ID_OF_THE_TEACHER
    )  # all_user_id.add(message.chat.id)
    all_user_id = database.get_user_list()
    log.info(log.BOT, f"All user id: {all_user_id}")
    startmenu = types.ReplyKeyboardMarkup(True, False)
    if not database.is_teacher(message.chat.id):
        startmenu.row(CALENDAR_BTN)
    else:
        startmenu.row(CALENDAR_BTN, NOTICES_BTN)
        startmenu.row(ADD_EVENT_BTN, ADD_NOTICE_BTN)
        startmenu.row(HELP_BTN)
    bot.send_message(
        message.chat.id, GREETING_MESSAGE, reply_markup=startmenu,
    )


def cmd_list_events(message):
    """
    Calendar view implementation
    """

    now = datetime.datetime.now().timestamp()
    event_list = database.get_events_since(now)

    # sending everyone message, that contains all events.
    # If there are no event_list, it'll send pre-prepared message.
    if len(event_list) == 0:
        bot.send_message(
            message.chat.id, "Пока ничего не запланировано. Можно отдохнуть 🙃"
        )
    else:
        events_map = {}
        for event in event_list:
            if events_map.get(event["timestamp"]) is None:
                events_map[event["timestamp"]] = []
            events_map[event["timestamp"]].append(event["text"])

        res_message = ""
        tss = list(events_map.keys())
        tss.sort()
        for ts in tss:
            one_message = ""
            for i in range(len(events_map[ts])):
                one_message += f"{i+1}) {events_map[ts][i]}\n"
            datestring = datetime.datetime.fromtimestamp(ts).strftime(DATEFORMAT)
            res_message += f"💠{datestring}:\n{one_message}"

        bot.send_message(message.chat.id, res_message)


def cmd_list_notices(message):
    """
    Notices list implementation
    """

    nowts = datetime.datetime.now().timestamp()
    notice_list = database.get_notices_since(nowts)

    if len(notice_list) == 0:
        bot.send_message(message.chat.id, "Пока напоминаний нет")
    else:
        notices_map = {}
        for notice in notice_list:
            if notices_map.get(notice["timestamp"]) is None:
                notices_map[notice["timestamp"]] = []
            notices_map[notice["timestamp"]].append(notice["text"])

        res_message = ""
        tss = list(notices_map.keys())
        tss.sort()
        for ts in tss:
            one_message = ""
            for i in range(len(notices_map[ts])):
                one_message += f"{i+1}) {notices_map[ts][i]}\n"
            datestring = datetime.datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
            res_message += f"📍{datestring}:\n{one_message}"

        bot.send_message(message.chat.id, res_message)


def cmd_add_notice(message):
    """
    Implementation of adding notices
    """
    send = bot.send_message(
        message.chat.id,
        "Укажите сообщение напоминания",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    bot.register_next_step_handler(send, reminder_1)


def cmd_add_event(message):
    """
    Implementation of adding events
    """
    ts = datetime.datetime.now()
    keyboard = types.ReplyKeyboardMarkup(True, False)
    for _ in range(15):
        keyboard.row(ts.strftime("%d.%m.%Y"))
        ts += datetime.timedelta(days=1)

    send = bot.send_message(message.chat.id, "Выберите дату", reply_markup=keyboard)
    bot.register_next_step_handler(send, changing_our_calendar1)


def cmd_help(message):
    """
    Help for the teacher
    """
    bot.send_message(message.chat.id, HELP_MESSAGE)


def cmd_empty(message):
    """
    Implementation of no keyword
    """
    if database.is_teacher(message.chat.id):
        ids = database.get_user_list()
        send_all(ids, message.text)


CMD_MAP = {
    CALENDAR_BTN: [cmd_list_events, True],
    ADD_EVENT_BTN: [cmd_add_event, False],
    NOTICES_BTN: [cmd_list_notices, False],
    ADD_NOTICE_BTN: [cmd_add_notice, False],
    HELP_BTN: [cmd_help, False],
}


@bot.message_handler(content_types=["text"])
def text_handler(message):
    log.bot_message(message)

    func, teacher_check = None, None

    cmdmap = CMD_MAP.get(message.text)
    if cmdmap:
        func, teacher_check = cmdmap
    else:
        func, teacher_check = [cmd_empty, False]

    if teacher_check or database.is_teacher(message.chat.id):
        func(message)


def changing_our_calendar1(message):
    global daystring
    daystring = message.text
    send = bot.send_message(
        message.chat.id,
        "Напишите название события",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    bot.register_next_step_handler(send, changing_our_calendar2)


def changing_our_calendar2(message):
    try:
        global daystring
        day, month, year = [int(x) for x in daystring.split(".")]
        daydate = datetime.datetime(year, month, day)
        nowdate = datetime.datetime.now()

        startmenu = types.ReplyKeyboardMarkup(True, False)
        startmenu.row(CALENDAR_BTN, NOTICES_BTN)
        startmenu.row(ADD_EVENT_BTN, ADD_NOTICE_BTN)
        startmenu.row(HELP_BTN)

        if daydate >= nowdate:
            database.add_event(message.text, daydate.timestamp())

            bot.send_message(
                message.chat.id, "Календарь обновлен", reply_markup=startmenu
            )

            ids = database.get_user_list()
            daystr = daydate.strftime("%d.%m")
            send_all(ids, f"{daystr} - {message.text}")
        else:
            bot.send_message(
                message.chat.id,
                "Дата слишком старая. Календарь не обновлен",
                reply_markup=startmenu,
            )
    except Exception as e:
        log.error(log.BOT, e)
        startmenu = types.ReplyKeyboardMarkup(True, False)
        startmenu.row(CALENDAR_BTN, NOTICES_BTN)
        startmenu.row(ADD_EVENT_BTN, ADD_NOTICE_BTN)
        startmenu.row(HELP_BTN)

        bot.send_message(
            message.chat.id,
            "Неправильно заполнена форма :(\nПопробуйте ещё раз.",
            reply_markup=startmenu,
        )


def reminder_1(message):
    global information
    information = message.text

    ts = datetime.datetime.now()
    keyboard = types.ReplyKeyboardMarkup(True, False)
    for _ in range(15):
        keyboard.row(ts.strftime("%d.%m.%Y"))
        ts += datetime.timedelta(days=1)

    send = bot.send_message(
        message.chat.id, "Выберите дату напоминания", reply_markup=keyboard
    )
    bot.register_next_step_handler(send, reminder_2)


def reminder_2(message):
    global date_to_remind
    date_to_remind = message.text

    keyboard = types.ReplyKeyboardMarkup(True, False)

    for v in range(24):
        keyboard.row(f"{v:02d}:00", f"{v:02d}:30")

    send = bot.send_message(
        message.chat.id, "Выберите время напоминания", reply_markup=keyboard
    )

    bot.register_next_step_handler(send, reminder_3)


def reminder_3(message):
    global for_module_threading
    time_to_remind = message.text
    try:
        day, month, year = date_to_remind.split(".")
        hours, minutes = time_to_remind.split(":")

        moment = datetime.datetime(
            int(year), int(month), int(day), int(hours), int(minutes)
        )

        database.add_notice(information, moment.timestamp())

        startmenu = types.ReplyKeyboardMarkup(True, False)
        startmenu.row(CALENDAR_BTN, NOTICES_BTN)
        startmenu.row(ADD_EVENT_BTN, ADD_NOTICE_BTN)
        startmenu.row(HELP_BTN)

        bot.send_message(
            ID_OF_THE_TEACHER,
            f"Всё! Я поставил напоминание на {moment}",
            reply_markup=startmenu,
        )

    except Exception as e:
        log.error(log.BOT, e)
        startmenu = types.ReplyKeyboardMarkup(True, False)
        startmenu.row(CALENDAR_BTN, NOTICES_BTN)
        startmenu.row(ADD_EVENT_BTN, ADD_NOTICE_BTN)
        startmenu.row(HELP_BTN)

        bot.send_message(
            message.chat.id,
            "Неправильно заполнена форма :(\nПопробуйте ещё раз.",
            reply_markup=startmenu,
        )


th = Thread(target=notice_update_loop)
th.start()

log.info(log.BOT, "Starting the bot")
bot.infinity_polling()
