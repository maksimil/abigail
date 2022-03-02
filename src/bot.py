"""
Bot functions
"""
import time
import traceback
import telebot
from telebot import types
import log
import database

logger = log.Logger(["LIBBOT", log.FBLUE])

CANCEL_BUTTON = "Отмена ❌"
KB = "kb"
ARGS = "args"
FUNC = "func"
MESSAGE = "message"
PARSER = "parser"
HIDDEN = "hidden"


def _format_user(message):
    if message.chat.username:
        return f"{message.chat.username}:{message.chat.id}"
    else:
        return f"{message.chat.id}"


MSG = ["MSG", log.FMAGENTA]


def log_usr_message(message):
    logger.log(
        [MSG, [_format_user(message), log.FGREEN], ["USR", log.FMAGENTA]], message.text,
    )


def _log_bot_message(chatid, message):
    logger.log(
        [MSG, [_format_user(message), log.FGREEN], ["BOT", log.FBLUE]], message.text,
    )


def _build_kb(keys):
    if len(keys) == 0:
        return types.ReplyKeyboardRemove()

    menu = types.ReplyKeyboardMarkup(True, False)
    for row in keys:
        menu.row(*row)
    return menu


class Keyboard:
    """Class for menu creation"""

    def __init__(self, keys: list[list[str]] = []):
        self.keys = keys

    def build_with(self, opts):
        """Builds the reply markup with opts on top"""
        keys = opts + self.keys
        return _build_kb(keys)

    def build(self):
        """Builds the reply markup"""
        return _build_kb(self.keys)


class Bot:
    """The telegram bot class"""

    def __init__(self, key, interface_fn):
        self.bot_handle = telebot.TeleBot(key, parse_mode="HTML")
        self._interface_fn = interface_fn

        @self.bot_handle.message_handler(
            content_types=[
                "text",
                "photo",
                "document",
                "video",
                "poll",
                "audio",
                "chataction",
                "voice",
                "sticker",
                "location",
                "videonote",
                "contact",
                "animation",
                "mediagroup",
                "venue",
                "dice",
            ]
        )
        def handler(message):
            self._message_handler(message)

    def start(self):
        """Starts the bot"""
        self.bot_handle.infinity_polling()

    def send_message_kb(self, chatid, text, mark):
        """Sends message with a set reply markup"""
        message = self.bot_handle.send_message(chatid, text, reply_markup=mark)
        _log_bot_message(chatid, message)
        return message

    def get_kb(self, chatid):
        """Gets default reply markup"""
        keylist = []
        interf = self._get_interface(chatid)
        for key, value in interf.items():
            if not value.get(HIDDEN, False):
                keylist.append(key)
        keys = [[keylist[2 * i], keylist[2 * i + 1]] for i in range(len(keylist) // 2)]
        if len(keylist) % 2 == 1:
            keys.append([keylist[len(keylist) - 1]])
        return Keyboard(keys)

    def send_message(self, chatid, text):
        """Sends message with text"""
        return self.send_message_kb(chatid, text, self.get_kb(chatid).build())

    def send_all(self, ids, text):
        """Sends message object to a list of ids"""
        for i in ids:
            try:
                self.send_message_kb(i, text, None)
                # time.sleep(0.1)
            except Exception as err:
                logger.warn(f"Error on user {i}:\n{str(err)}")

    def copy_message(self, chatid, message):
        """Copies message to an id"""
        if message.content_type == "poll":
            self.bot_handle.forward_message(chatid, message.chat.id, message.message_id)
        else:
            self.bot_handle.copy_message(
                chatid, message.chat.id, message.message_id, message.caption
            )
        _log_bot_message(chatid, message)

    def copy_all(self, ids, message):
        """Copies message object to a list of ids"""
        for i in ids:
            try:
                self.copy_message(i, message)
                # time.sleep(0.1)
            except Exception as err:
                logger.warn(f"Error on user {i}:\n{str(err)}")

    def _get_interface(self, chatid):
        return (self._interface_fn)(self, chatid)

    def _message_handler(self, f_msg):
        chatid = f_msg.chat.id
        interf = self._get_interface(chatid)

        if interf.get(f_msg.text) is None:
            log_usr_message(f_msg)
            # copying message to all
            if database.is_teacher(f_msg.chat.id):
                ids = database.get_user_list()
                self.copy_all(ids, f_msg)
        else:
            command = interf[f_msg.text]
            keys = list(command[ARGS].keys())
            args = {}

            def step(s_num):
                def ret(s_msg):
                    log_usr_message(s_msg)
                    try:
                        # read value
                        if s_num > 0:
                            if s_msg.text == CANCEL_BUTTON:
                                self.send_message(chatid, "Действие отменено")
                                return

                            value, err = command[ARGS][keys[s_num - 1]][PARSER](s_msg)

                            if err is not None:
                                logger.warn(f"Handled: {err}")
                                self.send_message(chatid, f"Ошибка: {err}")
                                return

                            args[keys[s_num - 1]] = (value, s_msg)

                        # ask question
                        if s_num < len(keys):
                            send = self.send_message_kb(
                                chatid,
                                command[ARGS][keys[s_num]][MESSAGE],
                                command[ARGS][keys[s_num]][KB].build_with(
                                    [[CANCEL_BUTTON]]
                                ),
                            )

                            self.bot_handle.register_next_step_handler(
                                send, step(s_num + 1)
                            )

                        # ending
                        else:
                            reply, err = command[FUNC](self, f_msg, args)

                            if err is not None:
                                logger.warn(f"Handled: {err}")
                                self.send_message(chatid, f"Ошибка: {err}")
                                return

                            if reply is None:
                                raise Exception(
                                    f"The final reply in {f_msg.txt} cannot be empty"
                                )

                            self.send_message(chatid, reply)

                    except Exception as err:
                        traceback.print_exc()
                        logger.error(err)
                        self.send_message(chatid, "Ошибка на сервере")

                return ret

            step(0)(f_msg)
