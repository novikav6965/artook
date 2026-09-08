import telebot as tb
from config import Config
from handlers import Handlers
import time

class ArToOk_BOT:
    def __init__(self):
        self.config = Config()
        self.bot = tb.TeleBot(self.config.BOT_TOKEN)
        self.handlers = Handlers(self.bot)
        self.handlers.register()

    def run(self): # Запуск бота
        while True:
            try:
                print("Бот запущен...")
                self.bot.polling(non_stop=True, skip_pending=True, interval=1, timeout=30)
            except Exception as e:
                print(f"Бот упал: {e}")
                print("Перезапуск через 1 секунду...")
                time.sleep(1)
