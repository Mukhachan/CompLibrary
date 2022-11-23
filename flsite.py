import os
import dotenv

import sqlite3

from flask import Flask, render_template, request, g, redirect, url_for, flash
from FDataBase import FDataBase


dotenv.load_dotenv('.env')

# Обработка глобальных переменных #
DATABASE = '/tmp/flsite.db'
DEBUG = True

# Создание приложение и настройка конфига # os.environ['SECRET_KEY']
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))



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

def get_db():
    '''Соединение с бд, если оно ещё не установлено '''
    if not hasattr(g, 'link_dv'):
        g.link_db = connect_db()
    return g.link_db


#  Редирект на страницу рекомендации  #
@app.route('/')
def index():
    return redirect(url_for('recommended'))


#  Страница рекомендации (по сути главная)  #
@app.route('/recommended')
def recommended():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', css_link='styles.css', menu=dbase.getMenu())


#  Закрытие соединения с базой данных  #
@app.teardown_appcontext
def closed_db(error):
    """Закрытие соединения"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


#  Обработка ошибок  #
@app.errorhandler(404)
def PageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', title='Страница не найдена',
                           menu=dbase.getMenu(), css_link='styles.css')


#  Страница "о библиотеке"  #
@app.route('/about')
def about():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('about.html', menu=dbase.getMenu())


#  рут авторизации  #
@app.route('/auth', methods=["POST", "GET"])
def auth():
    if request.method == 'POST':
        print(request.form)

    return render_template('auth.html')


#  рут регистрации  #
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        print(request.form)
    return render_template('register.html')


#  Страница добавления книги  #
@app.route('/newbook', methods=["POST", "GET"])
def newbook():
    db = get_db()
    dbase = FDataBase(db)

    # Добавление книги #
    if request.method == 'POST':
        print(request.form)
        if len(request.form['title']) != 0 and len(request.form['descript']) != 0:
            dbase.newbook_function(request.form['title'], request.form['author'],
                                   request.form['year'], request.form['number'], request.form['descript'], )

            flash('Книга добавлена', category='success')
        else:
            flash('Ошибка добавления книги', category='error')

        # GET запрос на редактирование книги #
    elif request.method == 'GET' and request.args.get('edit') != None:
        edit = request.args.get('edit')

        results = dbase.search_book_function(edit)

        return render_template('newbook.html', title='Editbook', edit=edit, results=results,
                               header_title='Редактирование книги', button='Изменить', inputs=dbase.get_inputs_newbook())

    return render_template('newbook.html', title='Newbook',
                           header_title='Добавить книгу', button='Добавить', inputs=dbase.get_inputs_newbook())


@app.route('/booklist', methods=["POST", "GET"])
def booklist():
    db = get_db()
    dbase = FDataBase(db)
    results = dbase.all_books_function()

    # Обработчик удаления книги #
    if request.method == 'POST' and 'id' in request.form:
        print(request.form)
        del_id = request.form['id']
        dbase.delete_book_function(del_id)  # Функция удаления #

        # Обработчик поиска #
    elif request.method == 'POST' and 'search_btn' in request.form:

        book_search = request.form['search_btn']
        results = dbase.search_book_function(book_search)  # Функция поиска #        

        if results == None:
            flash('Книга не найдена', category='error')
            return render_template('booklist.html', menu=dbase.getMenu())

    else:
        print(request.form)
        print('Типо ни одно условие не соблюдено')

    return render_template('booklist.html', menu=dbase.getMenu(), restrictions=results)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)