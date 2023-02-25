import os
import dotenv

import sqlite3

from flask import Flask, render_template, request, g, redirect, url_for, flash
from FDataBase import FDataBase
from werkzeug.utils import secure_filename

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

from time import sleep

dotenv.load_dotenv('.env')

# Константы #
DATABASE = '/tmp/flsite.db'
DEBUG = True
UPLOAD_FOLDER = 'static/pictures/'
MAX_LENGTH = 2 * 1000 * 2000
MAX_CONTENT_PATH = ''

# Создание приложения и настройка конфига # os.environ['SECRET_KEY']
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_LENGTH

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

# Настройка приложения для регистрации #
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user: ", user_id)
    return UserLogin().fromDB(user_id, dbase)


#  Создание, соединение и получение данных БД  #
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    '''Вспомогательная функция для создания таблиц бд'''
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()
    print('DB connect is OK')

def get_db():
    '''Соединение с бд, если оно ещё не установлено '''
    if not hasattr(g, 'link_dv'):
        g.link_db = connect_db()
    return g.link_db

# Соединение с бд и получение глобальной переменной #
dbase = None
@app.before_request
def before_request():
    """ Соединение с бд """
    global dbase 
    db = get_db()
    dbase = FDataBase(db)

#  Редирект на страницу рекомендации  #
@app.route('/')
def index():
    return redirect(url_for('recommended'))

#  Страница рекомендации (по сути главная)  #
@app.route('/recommended')
def recommended():
    
    if current_user.is_authenticated:
        return render_template('index.html' , auth_link = 'profile', auth_name='Профиль', 
            menu=dbase.getMenu(), restrictions=dbase.booklist_function())


    return render_template('index.html' , auth_link = 'auth', auth_name='Авторизация', 
            menu=dbase.getMenu(), restrictions=dbase.booklist_function())

#  Закрытие соединения с базой данных  #
@app.teardown_appcontext
def closed_db(error):
    """Закрытие соединения"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


#  Обработка ошибок  #
@app.errorhandler(404)
def PageNotFound(error):
    return render_template('page404.html', title='Страница не найдена',
                           menu=dbase.getMenu(), css_link='styles.css')

#  Страница "о библиотеке"  #
@app.route('/about')
def about():
    return render_template('about.html', menu=dbase.getMenu())

# Профиль пользователя
@app.route('/profile')
@login_required
def profile():
    res = dbase.get_user_data(current_user.get_id())
    return render_template('profile.html', menu=dbase.getMenu(), res = res)

# Выход из сессии
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('auth'))

#  рут авторизации  #
@app.route('/auth', methods=["POST", "GET"])
def auth():

    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        
        user = request.form['user']
        password = request.form['password']

        rm = True if request.form.get('remainme') else False

        if dbase.auth_user(user, password):
            flash('Успешная авторизация', category='success')

            user = dbase.getUserByEmail(request.form['user'])
            userlogin = UserLogin().create(user)
            login_user(userlogin, remember=rm)

            sleep(1)
            return redirect(url_for('recommended'))
        else:
            flash('Неверный логин или пароль', category='error')

    return render_template('auth.html')


#  рут регистрации  #
@app.route('/register', methods=["POST", "GET"])
def register():

    if request.method == 'POST':
        email = request.form['email']
        card = request.form['card']
        password = request.form['password']
        dbase.add_user(email, card, password)

    return render_template('register.html')


#  Страница добавления книги  #
@app.route('/newbook', methods=["POST", "GET"])
@login_required
def newbook():
    if current_user.get_role() != 'admin':
        return redirect('recommended')
    
    books = dbase.booklist_function()

        # Добавление книги #
    if request.method == 'POST':
        print('# Добавление книги #')

        if 'book_picture' not in request.files:
            flash('Обязательно добавьте картинку', category='error')

        else:
            # Сохранение картинки в файловой системе 
            file = request.files['book_picture']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Создание новой записи в бд
            dbase.newbook_function(btitle = request.form['btitle'], author = request.form['author'], 
            year = request.form['year'], number = request.form['number'], 
            descript = request.form['descript'], book_picture = request.form['book_picture'])

    return render_template('newbook.html', title='Newbook', 
            inputs=dbase.get_placeholder_newbook(), books = books)


#  Страница со списком книг  #
@app.route('/booklist', methods=["POST", "GET"])
@login_required
def booklist():
    if current_user.get_role() != 'admin':
        return redirect('recommended')


    post_req = request.args.get('qr')
    # Обработчик удаления книги #
    if request.method == 'POST' and 'id' in request.form:

        del_id = request.form['id']
        dbase.delete_book_function(del_id)  # Функция удаления #

    # Обработчик поиска #
    elif request.method == 'POST' and 'search_btn' in request.form:

        book_search = request.form['search_btn']
        results = dbase.search_book_function(book_search)  # Функция поиска #        

        if results == None:
            flash('Книга не найдена', category='error')
            return render_template('booklist.html', menu=dbase.getMenu())
        return render_template('booklist.html', menu=dbase.getMenu(), restrictions=results)

    # Создание QR кода #
    elif request.method == 'GET' and post_req != None:
        link = dbase.QR_maker(post_req)
        print('Качнём:', link)
        return render_template('booklist.html', menu=dbase.getMenu(),
            restrictions=dbase.booklist_function(), link=link, qr=int(post_req))

    print('No book for view')
    return render_template('booklist.html', menu=dbase.getMenu(), restrictions=dbase.booklist_function())


#  Карточка книги  #
@app.route('/book_card', methods=['GET','POST'])
def book_card():
    id = int(request.args.get('edit'))
    if login_required:
        role = 'anonymous'
    else:
        role = current_user.get_role()

    if request.method == 'GET':
        return render_template('book_card.html', menu=dbase.getMenu(), id = id, 
            author = dbase.search_book_function(id)[0][2], role = role,
            titlet = list(dbase.search_book_function(id)[0])[1], results=dbase.search_book_function(id))  

    elif request.method == 'POST':
        print("Запрос на редактирование книги")

        if request.form['book_picture'] == '':
            print('\nНЕТ КАРТИНКИ\n')

            # Обновление записи без новой картинки 
            dbase.update_book_function(request.form['btitle'], request.form['author'], request.form['year'], 
            request.form['number'], request.form['descript'], list(dbase.search_book_function(id)[0])[::-1][0], id)
        else:
            # Сохранение картинки в файловой системе 
            file = request.files['book_picture']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print('Название картинки: ', request.form['book_picture'], '\n')
            dbase.update_book_function(request.form['btitle'], request.form['author'], request.form['year'], 
            request.form['number'], request.form['descript'], request.form['book_picture'], id)            

        return render_template('book_card.html', menu=dbase.getMenu(), id = id, 
            author = dbase.search_book_function(id)[0][2],
            titlet = list(dbase.search_book_function(id)[0])[1], results=dbase.search_book_function(id))        

    return render_template('book_card.html', menu=dbase.getMenu(), 
        title = "Ну и чё ты тут делаешь? Тыж не мог попасть на эту страницу")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=DEBUG)
