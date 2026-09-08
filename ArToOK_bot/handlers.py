from telebot import types
from config import Config
from db import DataBase



class Handlers:
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        self.user_states = {}
        self.ADMINS_IDS = self.config.ADMINS_IDS
        self.db = DataBase()

    def register(self):  # Регистрация обработчиков
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self._handle_start(message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_messages(message):
            self._handle_messages(message)

    def _handle_start(self, message):
        self.user_states[message.chat.id] = None  # Сброс состояния
        text = 'Приветствую\nОтправить заявку на урон можно с помощью нашего бота. '
        if message.from_user.id in self.ADMINS_IDS:
            keyboard = self._create_admin_keyboard()
        else:
            keyboard = self._create_main_keyboard()
        self.bot.send_message(message.chat.id, text, reply_markup=keyboard)

    def _handle_messages(self, message): # Отслуживает сообщения и вызывает необходимые функции для обработки
        if self.user_states.get(message.chat.id) == 'waiting_for_claim':
            if message.text == 'Отмена':
                self._handle_start(message)
            else:
                self._handle_send_to_admin(message)
        elif self.user_states.get(message.chat.id) == 'waiting_for_add':
            if message.text == 'Отмена':
                self._handle_start(message)
            else:
                self._handle_to_add(message)
        elif self.user_states.get(message.chat.id) == 'waiting_for_delete':
            if message.text == 'Отмена':
                self._handle_start(message)
            else:
                self._handle_to_delete(message)
        else:
            if message.text == 'Заявить урон':
                self._handle_claim_button(message)
            elif message.text == 'Админ панель':
                self._admin_panel(message)
            elif message.text == 'Добавить':
                self._add(message)
            elif message.text == 'Удалить':
                self._delete(message)
            elif message.text == 'Отмена':
                self._handle_start(message)
            elif message.text == 'Показать топ':
                self._get_top(message)
            else:
                self.bot.send_message(message.chat.id, 'Используйте кнопки!')

    def _handle_claim_button(self, message): # Сделать проверку введенных данных!!!
        self.user_states[message.chat.id] = 'waiting_for_claim'
        keyboard = self._cancel_button()
        self.bot.send_message(message.chat.id, 'Формат заявки:\nБратулек (1837439928) - 5ккк\nКликуха (айди) - урон заявленный', reply_markup=keyboard)

    def _handle_send_to_admin(self, message):
        text_to_send = f'Заявка от @{message.from_user.username or message.from_user.id}: {message.text}'
        self.bot.send_message(self.config.group_id, text_to_send)
        self.bot.send_message(message.chat.id, 'Ваше заявка отправлена!')
        self.db.add_report(message.text)

    def _admin_panel(self, message):
        if self._check_if_admin(message):
            self.user_states[message.chat.id] = None
            keyboard = self._create_admin_panel()
            self.bot.send_message(message.chat.id, 'Выберите действие', reply_markup=keyboard)

    def _get_top(self, message):
        keyboard = self._create_main_keyboard()
        top = self.db.get_top()
        text = 'Текущий топ:\n'
        for row in top:
            text += f'{row[0]}. {row[1]} ({row[2]}) - {row[3]}\n'
        self.bot.send_message(message.chat.id, text, reply_markup=keyboard)

    def _add(self, message):
        if self._check_if_admin(message):
            self.user_states[message.chat.id] = 'waiting_for_add'
            keyboard = self._cancel_button()
            self.bot.send_message(message.chat.id, 'Формат заявки:\nБратулек (1837439928) - 5ккк\nКликуха (айди) - урон заявленный', reply_markup=keyboard)

    def _handle_to_add(self, message):
        if self._check_if_admin(message):
            self.db.add_report(message.text)
            self.bot.send_message(message.chat.id, 'Добавлено!')
            self._admin_panel(message)

    def _delete(self, message):
        if self._check_if_admin(message):
            self.user_states[message.chat.id] = 'waiting_for_delete'
            keyboard = self._cancel_button()
            reports = self.db.get_top()
            text = 'Выберите отчет для удаления:\n'
            for row in reports:
                text += f'{row[0]}. {row[1]} ({row[2]}) - {row[3]}\n'
            self.bot.send_message(message.chat.id, text, reply_markup=keyboard)

    def _handle_to_delete(self, message):
        if self._check_if_admin(message):
            if message.text.isnumeric():
                self.db.delete_report(message.text)
                self.bot.send_message(message.chat.id, 'Удалено!')
                self._admin_panel(message)
            else:
                self.bot.send_message(message.chat.id, 'Введите число!')
                self._delete(message)

    def _cancel_button(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_button = types.KeyboardButton('Отмена')
        keyboard.add(cancel_button)
        return keyboard

    def _create_main_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        claim_button = types.KeyboardButton('Заявить урон')
        keyboard.add(claim_button)
        return keyboard

    def _create_admin_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        get_button = types.KeyboardButton('Показать топ')
        claim_button = types.KeyboardButton('Заявить урон')
        admin_button = types.KeyboardButton('Админ панель')
        keyboard.add(get_button, claim_button, admin_button)
        return keyboard

    def _create_admin_panel(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        get_button = types.KeyboardButton('Показать топ')
        add_button = types.KeyboardButton('Добавить')
        delete_button = types.KeyboardButton('Удалить')
        cancel_button = types.KeyboardButton('Отмена')
        keyboard.add(get_button, add_button, delete_button, cancel_button)
        return keyboard

    def _check_if_admin(self, message):
        if message.from_user.id not in self.ADMINS_IDS:
            self.bot.send_message(message.chat.id, 'Вы не админ!')
            self._handle_start(message)
            return False
        else: return True