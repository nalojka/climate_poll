from flask import Flask, render_template, redirect
from sqlalchemy import create_engine, func, inspect, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

app = Flask(__name__)

# Указываем абсолютный путь к БД в папке bot
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'bot', 'climate_poll.db')

# Проверяем существование файла БД
if not os.path.exists(db_path):
    print(f"Ошибка: Файл базы данных не найден: {db_path}")
    print("Запустите сначала бота, чтобы создать БД")
    db_path = ":memory:"

# Подключаемся к существующей БД
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def statistics():
    try:
        session = Session()
        
        # Проверяем, существует ли таблица
        inspector = inspect(engine)
        if 'poll_answers' not in inspector.get_table_names():
            return render_template('error.html', 
                                error="База данных не инициализирована",
                                message="Запустите бота сначала для создания БД")
        
        # Получаем общее количество участников
        result = session.execute(text("SELECT COUNT(*) FROM poll_answers"))
        total_participants = result.scalar() or 0
        
        questions_stats = {}
        question_texts = {
            'question1': '1. Как вы считаете, является ли глобальное потепление серьёзной проблемой?',
            'question2': '2. Какие из этих факторов больше всего влияют на изменение климата?',
            'question3': '3. Как часто вы задумываетесь о своём углеродном следе?',
            'question4': '4. Какие меры по борьбе с глобальным потеплением вы поддерживаете?',
            'question5': '5. Верите ли вы, что человечество сможет остановить глобальное потепление?',
            'question6': '6. Как вы относитесь к идее "климатической тревоги"?',
            'question7': '7. Готовы ли вы лично изменить свои привычки ради экологии?',
            'question8': '8. Кто, по вашему мнению, должен нести основную ответственность за борьбу с глобальным потеплением?',
            'question9': '9. Как вы оцениваете информированность людей о проблеме глобального потепления?',
            'question10': '10. Какие источники информации о климате вы считаете наиболее надёжными?'
        }

        question_options = {
            'question1': ['Да, это угроза для человечества', 'Это проблема, но не самая критичная', 'Нет, это преувеличение', 'Затрудняюсь ответить'],
            'question2': ['Выбросы CO₂ от промышленности', 'Вырубка лесов', 'Использование ископаемого топлива', 'Естественные климатические циклы'],
            'question3': ['Регулярно, стараюсь уменьшать', 'Иногда, но не действую', 'Никогда не задумывался(ась)', 'Не знаю что это'],
            'question4': ['Переход на возобновляемую энергию', 'Повышение налогов для загрязняющих компаний', 'Сокращение потребления мяса', 'Массовые посадки деревьев'],
            'question5': ['Да, если принять меры сейчас', 'Возможно, но слишком поздно', 'Нет, процесс необратим', 'Не знаю'],
            'question6': ['Это оправданная реакция на кризис', 'Это чрезмерная паника', 'Люди просто не понимают науку', 'Мне всё равно'],
            'question7': ['Да, уже делаю это', 'Готов(а), но не знаю как', 'Нет, это не решит проблему', 'Только если это будет выгодно'],
            'question8': ['Правительства стран', 'Крупные корпорации', 'Каждый человек', 'Учёные и инженеры'],
            'question9': ['Большинство хорошо осведомлены', 'Многие не понимают масштабов', 'Людей сознательно вводят в заблуждение', 'Никто не разбирается в теме'],
            'question10': ['Научные исследования и доклады (IPCC)', 'Новости и СМИ', 'Соцсети и блоги', 'Не доверяю никому']
        }
        
        for i in range(1, 11):
            question_name = f'question{i}'
            
            # Получаем ответы из базы данных с помощью текстового SQL
            query = text(f"SELECT {question_name}, COUNT(*) FROM poll_answers GROUP BY {question_name}")
            results = session.execute(query).fetchall()
            
            answers_dict = {}
            for answer, count in results:
                if answer:
                    answers_dict[answer] = count
            
            # Добавляем все варианты ответов
            full_answers_dict = {}
            for option in question_options[question_name]:
                full_answers_dict[option] = answers_dict.get(option, 0)
            
            questions_stats[question_name] = {
                'question_text': question_texts[question_name],
                'answers': full_answers_dict,
                'total': sum(full_answers_dict.values())
            }
        
        session.close()
        
        return render_template('stats.html',
                             total_participants=total_participants,
                             questions_stats=questions_stats)
    
    except Exception as e:
        return render_template('error.html', 
                             error="Ошибка подключения к базе данных",
                             message=str(e))

@app.route('/bot')
def bot_redirect():
    return redirect('https://t.me/oprosglobalbot')

if __name__ == '__main__':
    print(f"Подключение к БД: {db_path}")
    if not os.path.exists(db_path):
        print("ВНИМАНИЕ: Файл БД не найден. Запустите сначала бота!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)