"""
Bot functions
"""
import time
import traceback
import telebot
from telebot import types
import log

logger = log.Logger(["LIBBOT", log.FBLUE])

KB = "kb"
ARGS = "args"
FUNC = "func"
MESSAGE = "message"
PARSER = "parser"
HELP = "help"

MESSAGE_LOG = ["MESSAGE", log.FMAGENTA]


def _log_message(message):
    print(type(message))
    logger.log(
        [MESSAGE_LOG, [f"{message.chat.username}:{message.chat.id}", log.FGREEN]],
        message.text,
    )


def _log_bot_message(chatid, text):
    logger.log([MESSAGE_LOG, [f"Bot->{chatid}", log.FGREEN]], text)


def gen_menu(values):
    """
    Builds reply markup from options
    """
    menu = types.ReplyKeyboardMarkup(True, False)

    for i in range(len(values) // 2):
        menu.row(values[2 * i], values[2 * i + 1])

    if len(values) % 2 == 1:
        menu.row(values[len(values) - 1])

    return menu


def empty_menu():
    """
    Builds empty menu reply markup
    """
    return types.ReplyKeyboardRemove()


def _keyb(interf):
    keys = list(interf.keys())
    return gen_menu(keys)


class MessageText:
    """
    Text message instruction
    """

    def __init__(self, text):
        self.text = text

    def send(self, bot, chatid):
        """
        Sends message to chatid
        """
        bot.send_text(chatid, self.text)


class MessageCopy:
    """
    Copy message instruction
    """

    def __init__(self, message):
        self.message = message

    def send(self, bot, chatid):
        """
        Sends message chatid
        """
        _log_bot_message(chatid, self.message.text)

        if self.message.content_type == "poll":
            bot.bot_handle.forward_message(
                chatid,
                self.message.chat.id,
                self.message.message_id,
                reply_markup=bot.get_kb(chatid),
            )
        elif self.message.content_type == "photo":
            bot.bot_handle.send_photo(
                chatid, self.message.photo[0].file_id, reply_markup=bot.get_kb(chatid)
            )
        elif self.message.content_type:
            bot.bot_handle.copy_message(
                chatid,
                self.message.chat.id,
                self.message.message_id,
                self.message.caption,
                reply_markup=bot.get_kb(chatid),
            )


class Bot:
    """
    The telegram bot class
    """

    def __init__(self, key, interface_fn):
        self.bot_handle = telebot.TeleBot(key, parse_mode=None)
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
            self._text_handler(message)

    def start(self):
        """
        Starts the bot
        """
        self.bot_handle.infinity_polling()

    def docstring(self, chatid):
        """
        Generates the docstring
        """
        interface = self._get_interface(chatid)
        docs = ""
        for cmd in interface.keys():
            docs += f"{cmd} - {interface[cmd][HELP]}\n"
        return docs

    def _send_message_kb(self, chatid, text, mark):
        _log_bot_message(chatid, text)
        return self.bot_handle.send_message(chatid, text, reply_markup=mark)

    def get_kb(self, chatid):
        """
        Gets default reply markup
        """
        return _keyb(self._get_interface(chatid))

    def send_text(self, chatid, text):
        """
        Sends message with text
        """
        return self._send_message_kb(chatid, text, self.get_kb(chatid))

    def send_message(self, chatid, message):
        """
        Sends message object
        """
        message.send(self, chatid)

    def send_all(self, ids, message):
        """
        Sends message object to a list of ids
        """
        count = 0
        while True:
            try:
                for i in range(count, len(ids)):
                    count += 1
                    self.send_message(ids[i], message)
                    time.sleep(0.5)
                else:
                    break
            except Exception as err:
                logger.warn(f"Error 403. {ids[i]} blocked me\n{str(err)}\n")

    def _get_interface(self, chatid):
        return (self._interface_fn)(self, chatid)

    def _text_handler(self, f_msg):
        chatid = f_msg.chat.id
        interf = self._get_interface(chatid)

        if interf.get(f_msg.text) is None:
            _log_message(f_msg)
            self.send_text(
                chatid,
                "Ошибка: команда не найдена, "
                'для списка команд напишите "Справочник ⚙"',
            )

        else:
            command = interf[f_msg.text]
            keys = list(command[ARGS].keys())
            args = {}

            def step(s_num):
                def ret(s_msg):
                    _log_message(s_msg)
                    try:
                        # read value
                        if s_num > 0:
                            value, err = command[ARGS][keys[s_num - 1]][PARSER](s_msg)

                            if err is not None:
                                logger.warn(f"Handled: {err}")
                                self.send_text(chatid, f"Ошибка: {err}")
                                return

                            args[keys[s_num - 1]] = (value, s_msg)

                        # ask question
                        if s_num < len(keys):
                            send = self._send_message_kb(
                                chatid,
                                command[ARGS][keys[s_num]][MESSAGE],
                                command[ARGS][keys[s_num]][KB],
                            )

                            self.bot_handle.register_next_step_handler(
                                send, step(s_num + 1)
                            )

                        # ending
                        else:
                            reply, err = command[FUNC](self, f_msg, args)

                            if err is not None:
                                logger.warn(f"Handled: {err}")
                                self.send_text(chatid, f"Ошибка: {err}")
                                return

                            if reply is None:
                                raise Exception(
                                    f"The final reply in {f_msg.txt} cannot be empty"
                                )

                            self.send_message(chatid, reply)

                    except Exception as err:
                        traceback.print_exc()
                        logger.error(err)
                        self.send_text(chatid, "Ошибка на сервере")

                return ret

            step(0)(f_msg)
