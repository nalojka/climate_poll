import telebot
from telebot import *
import sqlite3
import os
from cfg import TOKEN

bot = telebot.TeleBot(TOKEN)

# Инициализация базы данных в папке bot
def init_db():
    # Получаем абсолютный путь к файлу БД в папке bot
    db_path = os.path.join(os.path.dirname(__file__), 'climate_poll.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS poll_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        question1 TEXT,
        question2 TEXT,
        question3 TEXT,
        question4 TEXT,
        question5 TEXT,
        question6 TEXT,
        question7 TEXT,
        question8 TEXT,
        question9 TEXT,
        question10 TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print(f"База данных создана: {db_path}")

def check_user_completed(user_id):
    """Проверяет, прошел ли пользователь уже опрос"""
    db_path = os.path.join(os.path.dirname(__file__), 'climate_poll.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM poll_answers WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

def delete_user_attempt(user_id):
    """Удаляет предыдущую попытку пользователя"""
    db_path = os.path.join(os.path.dirname(__file__), 'climate_poll.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM poll_answers WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при удалении попытки: {e}")
        return False

def save_answer(user_id, question_num, answer):
    """Сохраняет ответ во временное хранилище"""
    user_answers[user_id][f'question{question_num}'] = answer

def save_to_db(user_data):
    """Сохраняет все ответы в базу данных"""
    db_path = os.path.join(os.path.dirname(__file__), 'climate_poll.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO poll_answers 
        (user_id, username, first_name, last_name, question1, question2, question3, question4, question5, 
         question6, question7, question8, question9, question10)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data['username'],
            user_data['first_name'],
            user_data['last_name'],
            user_data.get('question1', ''),
            user_data.get('question2', ''),
            user_data.get('question3', ''),
            user_data.get('question4', ''),
            user_data.get('question5', ''),
            user_data.get('question6', ''),
            user_data.get('question7', ''),
            user_data.get('question8', ''),
            user_data.get('question9', ''),
            user_data.get('question10', '')
        ))
        
        conn.commit()
        print(f"Данные пользователя {user_data['user_id']} сохранены в БД")
        return True
        
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

# Инициализируем БД при запуске
init_db()

# Словарь для временного хранения ответов
user_answers = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    
    # Проверяем, прошел ли пользователь уже опрос
    if check_user_completed(user_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Пройти опрос заново")
        btn2 = types.KeyboardButton("Отмена")
        markup.add(btn1, btn2)
        
        bot.send_message(
            message.chat.id,
            '⚠️ Вы уже проходили этот опрос.\nХотите пройти его заново? (предыдущие ответы будут удалены)',
            reply_markup=markup
        )
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать опрос")
        markup.add(btn1)
        bot.send_message(
            message.chat.id,
            'Добро пожаловать в опрос по теме <b>глобального потепления</b>.\nЕсли вы готовы к опросу нажмите на кнопку ниже',
            parse_mode='HTML',
            reply_markup=markup
        )

@bot.message_handler(func=lambda message: message.text == "Начать опрос")
def start_test(message):
    user_id = message.from_user.id
    
    if check_user_completed(user_id):
        bot.send_message(message.chat.id, "Вы уже проходили этот опрос. Используйте /start для повторного прохождения.")
        return
    
    user_answers[user_id] = {}
    remove_markup = types.ReplyKeyboardRemove()
    markup = types.InlineKeyboardMarkup()
    
    # Вопрос 1
    btn1 = types.InlineKeyboardButton("Да, это угроза для человечества", callback_data="q1_opt1")
    btn2 = types.InlineKeyboardButton("Это проблема, но не самая критичная", callback_data="q1_opt2")
    btn3 = types.InlineKeyboardButton("Нет, это преувеличение", callback_data="q1_opt3")
    btn4 = types.InlineKeyboardButton("Затрудняюсь ответить", callback_data="q1_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.send_message(message.chat.id, ".", reply_markup=remove_markup)
    bot.send_message(
        message.chat.id,
        "<b>Вопрос 1/10</b>\nКак вы считаете, является ли глобальное потепление серьёзной проблемой?",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: message.text == "Пройти опрос заново")
def restart_poll(message):
    user_id = message.from_user.id
    delete_user_attempt(user_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать опрос")
    markup.add(btn1)
    
    bot.send_message(
        message.chat.id,
        "✅ Предыдущие ответы удалены. Теперь вы можете пройти опрос заново.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Отмена")
def cancel_restart(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id,
        "Действие отменено. Используйте /start для возврата в меню.",
        reply_markup=markup
    )

def save_answer(user_id, question_num, answer):
    """Сохраняет ответ во временное хранилище"""
    user_answers[user_id][f'question{question_num}'] = answer

def save_to_db(user_data):
    """Сохраняет все ответы в базу данных"""
    try:
        conn = sqlite3.connect('climate_poll.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO poll_answers 
        (user_id, username, first_name, last_name, question1, question2, question3, question4, question5, 
         question6, question7, question8, question9, question10)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data['username'],
            user_data['first_name'],
            user_data['last_name'],
            user_data.get('question1', ''),
            user_data.get('question2', ''),
            user_data.get('question3', ''),
            user_data.get('question4', ''),
            user_data.get('question5', ''),
            user_data.get('question6', ''),
            user_data.get('question7', ''),
            user_data.get('question8', ''),
            user_data.get('question9', ''),
            user_data.get('question10', '')
        ))
        
        conn.commit()
        print(f"Данные пользователя {user_data['user_id']} сохранены в БД")
        
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении в БД: {e}")
    finally:
        if conn:
            conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith('q1_'))
def handle_q1(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q1_opt1': 'Да, это угроза для человечества',
        'q1_opt2': 'Это проблема, но не самая критичная',
        'q1_opt3': 'Нет, это преувеличение',
        'q1_opt4': 'Затрудняюсь ответить'
    }
    save_answer(user_id, 1, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 2
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Выбросы CO₂ от промышленности", callback_data="q2_opt1")
    btn2 = types.InlineKeyboardButton("Вырубка лесов", callback_data="q2_opt2")
    btn3 = types.InlineKeyboardButton("Использование ископаемого топлива", callback_data="q2_opt3")
    btn4 = types.InlineKeyboardButton("Естественные климатические циклы", callback_data="q2_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id, 
        text="<b>Вопрос 2/10</b>\nКакие из этих факторов больше всего влияют на изменение климата?", 
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q2_'))
def handle_q2(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q2_opt1': 'Выбросы CO₂ от промышленности',
        'q2_opt2': 'Вырубка лесов',
        'q2_opt3': 'Использование ископаемого топлива',
        'q2_opt4': 'Естественные климатические циклы'
    }
    save_answer(user_id, 2, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 3
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Регулярно, стараюсь уменьшать", callback_data="q3_opt1")
    btn2 = types.InlineKeyboardButton("Иногда, но не действую", callback_data="q3_opt2")
    btn3 = types.InlineKeyboardButton("Никогда не задумывался(ась)", callback_data="q3_opt3")
    btn4 = types.InlineKeyboardButton("Не знаю что это", callback_data="q3_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>Вопрос 3/10</b>\nКак часто вы задумываетесь о своём углеродном следе?",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q3_'))
def handle_q3(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q3_opt1': 'Регулярно, стараюсь уменьшать',
        'q3_opt2': 'Иногда, но не действую',
        'q3_opt3': 'Никогда не задумывался(ась)',
        'q3_opt4': 'Не знаю что это'
    }
    save_answer(user_id, 3, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 4
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Переход на возобновляемую энергию", callback_data="q4_opt1")
    btn2 = types.InlineKeyboardButton("Повышение налогов для загрязняющих компаний", callback_data="q4_opt2")
    btn3 = types.InlineKeyboardButton("Сокращение потребления мяса", callback_data="q4_opt3")
    btn4 = types.InlineKeyboardButton("Массовые посадки деревьев", callback_data="q4_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id, 
        text="<b>Вопрос 4/10</b>\nКакие меры по борьбе с глобальным потеплением вы поддерживаете?", 
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q4_'))
def handle_q4(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q4_opt1': 'Переход на возобновляемую энергию',
        'q4_opt2': 'Повышение налогов для загрязняющих компаний',
        'q4_opt3': 'Сокращение потребления мяса',
        'q4_opt4': 'Массовые посадки деревьев'
    }
    save_answer(user_id, 4, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 5
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Да, если принять меры сейчас", callback_data="q5_opt1")
    btn2 = types.InlineKeyboardButton("Возможно, но слишком поздно", callback_data="q5_opt2")
    btn3 = types.InlineKeyboardButton("Нет, процесс необратим", callback_data="q5_opt3")
    btn4 = types.InlineKeyboardButton("Не знаю", callback_data="q5_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>Вопрос 5/10</b>\nВерите ли вы, что человечество сможет остановить глобальное потепление?",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q5_'))
def handle_q5(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q5_opt1': 'Да, если принять меры сейчас',
        'q5_opt2': 'Возможно, но слишком поздно',
        'q5_opt3': 'Нет, процесс необратим',
        'q5_opt4': 'Не знаю'
    }
    save_answer(user_id, 5, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 6
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Это оправданная реакция на кризис", callback_data="q6_opt1")
    btn2 = types.InlineKeyboardButton("Это чрезмерная паника", callback_data="q6_opt2")
    btn3 = types.InlineKeyboardButton("Люди просто не понимают науку", callback_data="q6_opt3")
    btn4 = types.InlineKeyboardButton("Мне всё равно", callback_data="q6_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>Вопрос 6/10</b>\nКак вы относитесь к идее "климатической тревоги"?',
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q6_'))
def handle_q6(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q6_opt1': 'Это оправданная реакция на кризис',
        'q6_opt2': 'Это чрезмерная паника',
        'q6_opt3': 'Люди просто не понимают науку',
        'q6_opt4': 'Мне всё равно'
    }
    save_answer(user_id, 6, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 7
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Да, уже делаю это", callback_data="q7_opt1")
    btn2 = types.InlineKeyboardButton("Готов(а), но не знаю как", callback_data="q7_opt2")
    btn3 = types.InlineKeyboardButton("Нет, это не решит проблему", callback_data="q7_opt3")
    btn4 = types.InlineKeyboardButton("Только если это будет выгодно", callback_data="q7_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>Вопрос 7/10</b>\nГотовы ли вы лично изменить свои привычки ради экологии?',
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q7_'))
def handle_q7(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q7_opt1': 'Да, уже делаю это',
        'q7_opt2': 'Готов(а), но не знаю как',
        'q7_opt3': 'Нет, это не решит проблему',
        'q7_opt4': 'Только если это будет выгодно'
    }
    save_answer(user_id, 7, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 8
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Правительства стран", callback_data="q8_opt1")
    btn2 = types.InlineKeyboardButton("Крупные корпорации", callback_data="q8_opt2")
    btn3 = types.InlineKeyboardButton("Каждый человек", callback_data="q8_opt3")
    btn4 = types.InlineKeyboardButton("Учёные и инженеры", callback_data="q8_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>Вопрос 8/10</b>\nКто, по вашему мнению, должен нести основную ответственность за борьбу с глобальным потеплением?',
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q8_'))
def handle_q8(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q8_opt1': 'Правительства стран',
        'q8_opt2': 'Крупные корпорации',
        'q8_opt3': 'Каждый человек',
        'q8_opt4': 'Учёные и инженеры'
    }
    save_answer(user_id, 8, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 9
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Большинство хорошо осведомлены", callback_data="q9_opt1")
    btn2 = types.InlineKeyboardButton("Многие не понимают масштабов", callback_data="q9_opt2")
    btn3 = types.InlineKeyboardButton("Людей сознательно вводят в заблуждение", callback_data="q9_opt3")
    btn4 = types.InlineKeyboardButton("Никто не разбирается в теме", callback_data="q9_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>Вопрос 9/10</b>\nКак вы оцениваете информированность людей о проблеме глобального потепления?',
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q9_'))
def handle_q9(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q9_opt1': 'Большинство хорошо осведомлены',
        'q9_opt2': 'Многие не понимают масштабов',
        'q9_opt3': 'Людей сознательно вводят в заблуждение',
        'q9_opt4': 'Никто не разбирается в теме'
    }
    save_answer(user_id, 9, answer_map[call.data])
    bot.answer_callback_query(call.id, "Ответ принят!")
    
    # Вопрос 10
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Научные исследования и доклады (IPCC)", callback_data="q10_opt1")
    btn2 = types.InlineKeyboardButton("Новости и СМИ", callback_data="q10_opt2")
    btn3 = types.InlineKeyboardButton("Соцсети и блоги", callback_data="q10_opt3")
    btn4 = types.InlineKeyboardButton("Не доверяю никому", callback_data="q10_opt4")
    
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>Вопрос 10/10</b>\nКакие источники информации о климате вы считаете наиболее надёжными?',
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('q10_'))
def handle_q10(call):
    user_id = call.from_user.id
    if user_id not in user_answers:
        bot.answer_callback_query(call.id, "Ошибка: сессия опроса не найдена. Начните заново с /start")
        return
        
    answer_map = {
        'q10_opt1': 'Научные исследования и доклады (IPCC)',
        'q10_opt2': 'Новости и СМИ',
        'q10_opt3': 'Соцсети и блоги',
        'q10_opt4': 'Не доверяю никому'
    }
    save_answer(user_id, 10, answer_map[call.data])
    
    # Сохраняем все ответы в БД
    user_data = user_answers[user_id]
    user_data.update({
        'user_id': user_id,
        'username': call.from_user.username,
        'first_name': call.from_user.first_name,
        'last_name': call.from_user.last_name
    })
    
    save_to_db(user_data)
    
    # Удаляем временные данные
    if user_id in user_answers:
        del user_answers[user_id]
    
    bot.answer_callback_query(call.id, "Спасибо за прохождение опроса!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="<b>Опрос завершён!</b>\nБлагодарим за ваши ответы!\n\nИспользуйте /start для возврата в меню.",
        parse_mode="HTML"
    )

print("Бот запущен и БД инициализирована")
bot.infinity_polling()