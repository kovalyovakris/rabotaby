from flask import url_for,flash, Flask, redirect, request, render_template, session
from flask_login import login_user,LoginManager, login_required, logout_user, current_user
from database import db
from UserDB import User
from passwordHash import check_password_hash, generate_password_hash
from userInfoDB import UserInfo
import os
from uuid import uuid4
from quiz import questions, professions
import re
from get_vacancies import get_vacancies, get_vacancy_by_name

#создаем приложение. задаем бд, папку скачивания и допустимые форматы
app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/usersrabotaby'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

#позволяем бд самой создать таблицы нужные
db.init_app(app)
with app.app_context():
    db.create_all()

def allowed_file(filename): # проверка формата
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id): #поддерживаем сессию пользователя
    return User.query.get(user_id)

@app.route('/')
def index():
    return redirect('/log')

@app.route('/log', methods=['POST', 'GET']) # авторизация
def log():
    if request.method == "POST":
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            user = User.query.filter_by(login=login).first()
            if not user:
                flash("Пользователя с таким логином не существует", "error")
                return redirect(url_for("log"))
            if check_password_hash(password, user.password):
                login_user(user)
                return redirect('/main')
            else:
                flash("Неверный логин или пароль", "error")
                return redirect(url_for("log"))
        else:
            flash("Заполните все поля!", "error")
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/reg', methods = ['POST', 'GET']) #регистрация
def register():
    if request.method == "POST":
        if len(request.form['login'])>=4 and len(request.form['password'])>=4:
            login = request.form['login']
            if User.query.filter_by(login=login).first():
                flash("Этот логин уже занят", "error")
                return render_template("register.html")
            password = request.form.get('password')
            password = generate_password_hash(password)
            newuser = User(login=login, password=password)
            try:
                db.session.add(newuser)
                db.session.commit()
                flash("Вы успешно зарегестрированы","success")
                return redirect('/log')
            except Exception as e:
                return f"При создании профиля произошла ошибка: {str(e)}"
        else:
            flash("Неверно заполнены поля, длина должна быть более 4 символов","error")
            return render_template("register.html")
    else:
        return render_template("register.html")

@app.route('/logout', methods = ['POST', 'GET']) #выйти
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/main', methods=['POST', 'GET'])# профиль пользователя
@login_required
def main_window():
    user_info = UserInfo.query.filter_by(login=current_user.login).first()

    if request.method == "POST":
        photo_path = user_info.photo_path if user_info else None
        document_path = user_info.document_path if user_info else None

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = f"photo_{uuid4()}.{photo.filename.rsplit('.', 1)[1].lower()}"
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_path = filename

        if 'document' in request.files:
            document = request.files['document']
            if document and allowed_file(document.filename):
                filename = f"doc_{uuid4()}.{document.filename.rsplit('.', 1)[1].lower()}"
                document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                document_path = filename

        # обновляем инфу о пользователе
        new_login = request.form['login']
        if new_login != current_user.login:
            if User.query.filter(User.login == new_login).first():
                flash("Этот логин уже занят", "error")
                return redirect(url_for('main_window'))
        current_user.login = new_login
        if user_info:
            user_info.name = request.form['name']
            user_info.email = request.form['email']
            user_info.photo_path = photo_path
            user_info.document_path = document_path
        else:
            user_info = UserInfo(
                login=current_user.login,
                name=request.form['name'],
                email=request.form['email'],
                photo_path=photo_path,
                document_path=document_path
            )
            db.session.add(user_info)

        db.session.commit()
        return redirect(url_for('main_window'))

    return render_template("main-window.html", user=user_info, login=current_user.login)


@app.route('/all-vacancies', methods = ['POST', 'GET']) # просмотр всех вакансий
@login_required
def vacancy_list():
    # start_db()
    min_salary = request.args.get('min_salary', type=int)
    experience = request.args.get('experience', '')
    employment_type = request.args.get('employment_type', '')
    all_vacancies = get_vacancies()

    filtered_vacancies = []
    for vacancy in all_vacancies:
        # фильтр по зарплате
        if min_salary:
            salary_text = vacancy.salary.lower()
            numbers = [int(s) for s in re.findall(r'\d+', salary_text)]
            if not numbers or max(numbers) < min_salary:
                continue

        # фильтр по опыту
        if experience and vacancy.experience != experience:
            continue

        # фильтр по типу занятости
        if employment_type and employment_type not in vacancy.type.lower():
            continue

        filtered_vacancies.append(vacancy)

    return render_template("all-vacancies.html", vacancies=filtered_vacancies)


@app.route('/all-vacancies/<string:name>', methods = ['POST', 'GET']) # просмотр отдельной вакансии по имени
@login_required
def vacancy_list_details(name):
    vacancy = get_vacancy_by_name(name)
    if vacancy:
        return render_template("vacancy-detail.html", vacancy=vacancy)
    return redirect('/all-vacancies')

@app.route('/test',  methods=['GET', 'POST']) # переход к тесту
@login_required
def testWindow():
    return render_template('index.html')

# Функция для группировки профессий по категориям
def group_professions_by_category():
    categories = {
        "people-oriented": [],
        "tech-oriented": [],
        "creative": [],
        "hybrid": []
    }

    for prof in professions:
        category = prof.get("category", "hybrid")  # По умолчанию считаем гибридной
        if category in categories:
            categories[category].append(prof)

    return categories


@app.route('/start-test', methods=['GET', 'POST'])# начало теста
@login_required
def start_test():
    session['current_question'] = 0
    session['position_x'] = 0.0
    session['position_y'] = 0.0
    session['answers'] = []
    session['path'] = [(0, 0)]  # путь для отслеживания перемещения точки
    return redirect(url_for('question'))


@app.route('/question', methods=['GET', 'POST'])# вопросы окно
@login_required
def question():
    if 'current_question' not in session:
        return redirect(url_for('confirm_test'))

    if request.method == 'POST':
        answer = request.form.get('answer')
        # сохраняем ответ
        session['answers'].append(answer)
        # обновляем положение точки
        current_question = session['current_question']
        if current_question < len(questions):
            shift = questions[current_question]['shifts'].get(answer, (0, 0))
            session['position_x'] += shift[0]
            session['position_y'] += shift[1]

            # Добавляем новую позицию в путь
            session['path'].append((session['position_x'], session['position_y']))

            # Переходим к следующему вопросу
            session['current_question'] += 1

        # Если вопросы закончились, переходим к результатам
        if session['current_question'] >= len(questions):
            return redirect(url_for('result'))

        # Отображаем текущий вопрос
        current_question = session.get('current_question', 0)
        if current_question >= len(questions):
        return redirect(url_for('result'))

    progress_percent = (current_question / len(questions)) * 100

    return render_template(
        'question.html',
        question=questions[current_question],
        question_number=current_question + 1,
        total_questions=len(questions),
        x=session.get('position_x', 0),
        y=session.get('position_y', 0),
        path=session.get('path', [(0, 0)]),
        progress_percent=progress_percent
    )


@app.route('/result')# рез-ты теста
@login_required
def result():
    if 'position_x' not in session or 'position_y' not in session:
    return redirect(url_for('index'))

    x = session['position_x']
    y = session['position_y']

    # Находим наиболее подходящую профессию
    profession = find_best_profession(x, y)

    # Группируем профессии по категориям для отображения
    categorized_professions = group_professions_by_category()

    # Находим 3 ближайшие альтернативные профессии
    alternative_professions = []
    for prof in professions:
        if prof['name'] != profession['name']:
            x_min, x_max = prof["x_range"]
            y_min, y_max = prof["y_range"]

            # Находим центр диапазона профессии
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2

            # Расстояние до центра профессии
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

            alternative_professions.append({
                'name': prof['name'],
                'distance': distance,
                'description': prof.get('description', '')
            })

    # Сортируем по расстоянию и берем 3 ближайшие
    alternative_professions.sort(key=lambda p: p['distance'])
    alternative_professions = alternative_professions[:3]

    return render_template(
        'result.html',
        x=x,
        y=y,
        path=session.get('path', [(0, 0)]),
        profession=profession,
        professions=professions,
        categorized_professions=categorized_professions,
        alternative_professions=alternative_professions
    )


if __name__ == "__main__":
    app.run(debug=True)
