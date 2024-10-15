import logging


logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, chat_id, logger_bot):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = logger_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)