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
    send = bot.send_message(message.chat.id, "Укажите сообщение напоминания")
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
    ADD_NOTICE: [cmd_add_notice, False],
}
