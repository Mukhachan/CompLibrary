import os
import dotenv

import sqlite3

from flask import Flask, render_template, request, g, redirect, url_for, flash, send_from_directory
from FDataBase import FDataBase
from werkzeug.utils import secure_filename


dotenv.load_dotenv('.env')

# Константы #
DATABASE = '/tmp/flsite.db'
DEBUG = True
UPLOAD_FOLDER = 'static/pictures/'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpeg', 'jpg'}
MAX_LENGTH = 2 * 1000 * 2000
MAX_CONTENT_PATH = ''

# Создание приложения и настройка конфига # os.environ['SECRET_KEY']
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_LENGTH

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

    return render_template('index.html' , menu=dbase.getMenu(), restrictions=dbase.booklist_function())


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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#  Страница добавления книги  #
@app.route('/newbook', methods=["POST", "GET"])
def newbook():
    db = get_db()
    dbase = FDataBase(db)

        # Добавление книги #
    if request.method == 'POST':
        print('# Добавление книги #')
        print(request.form)
        print(request.files)

        if 'book_picture' not in request.files:
            flash('Обязательно добавьте картинку', category='error')

        else:
            # Сохранение картинки в файловой системе 
            file = request.files['book_picture']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print(file)
            # Создание новой записи в бд
            dbase.newbook_function(btitle = request.form['btitle'], author = request.form['author'], 
            year = request.form['year'], number = request.form['number'], 
            descript = request.form['descript'], book_picture = request.form['book_picture'])

    return render_template('newbook.html', title='Newbook', inputs=dbase.get_placeholder_newbook())


@app.route('/booklist', methods=["POST", "GET"])
def booklist():
    db = get_db()
    dbase = FDataBase(db)

    post_req = request.args.get('qr')
    print(post_req)

    # Обработчик удаления книги #
    if request.method == 'POST' and 'id' in request.form:
        print(request.form)
        del_id = request.form['id']
        dbase.delete_book_function(del_id)  # Функция удаления #

    # Обработчик поиска #
    elif request.method == 'POST' and 'search_btn' in request.form:
        print(request.form)

        book_search = request.form['search_btn']
        results = dbase.search_book_function(book_search)  # Функция поиска #        

        if results == None:
            flash('Книга не найдена', category='error')
            return render_template('booklist.html', menu=dbase.getMenu())
        return render_template('booklist.html', menu=dbase.getMenu(), restrictions=results)

    # Создание QR кода #
    elif request.method == 'GET' and post_req != None:
        print(request.form)
        link = dbase.QR_maker(post_req)
        print('Качнём:', link)
        return render_template('booklist.html', menu=dbase.getMenu(),
            restrictions=dbase.booklist_function(), link=link, qr=int(post_req))

    print('Ничего')
    return render_template('booklist.html', menu=dbase.getMenu(), restrictions=dbase.booklist_function())


@app.route('/book_card', methods=['GET','POST'])
def book_card():
    db = get_db()
    dbase = FDataBase(db)
       
    if request.method == 'POST':
        print("Запрос на редактирование книги")
        print('\n',request.form)
        print(request.files,'\n')

        id = int(request.args.get('edit'))

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
