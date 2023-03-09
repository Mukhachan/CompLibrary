import os
from pathlib import Path
from time import sleep

import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from FDataBase import FDataBase
from UserLogin import UserLogin

import dotenv
dotenv.load_dotenv('.env')

app = Flask(__name__)

menu = [{"name": "Рекомендации", "url" : "recommended"},
        {"name": "Жанры", "url" : "genre"},
        {"name": "Что нового", "url" : "news"},
        {"name": "О библиотеке", "url" : "about"}]

#  Создание, соединение и получение данных БД  #
def connect_db():
    '''Соедиение с бд'''
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
    print('БД подключена')
def get_db():
    '''Соединение с бд, если оно ещё не установлено'''
    if 'link_db' not in g:
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

@app.teardown_appcontext
def closed_db(error):
    '''Закрытие соединения'''
    if 'link_db' in g:
        g.link_db.close()



@app.route('/')
def index():
    print( url_for('index') )
    return redirect(url_for('recommended'))

@app.route('/recommended')
def recommended():
    return render_template('index.html', css_link='styles.css', menu=menu)


@app.route('/auth', methods=["POST", "GET"])
def auth():
    if request.method == 'POST':
        print(request.form)

    return render_template('auth.html')
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        print(request.form)
    return render_template('register.html')


@app.route('/newbook', methods=["POST", "GET"])
def newbook():
    if request.method == 'POST':
        print(request.form)
    
    return render_template('newbook.html', css_link= 'newbook.css', title='Newbook')

@app.route('/about')
def about():
    return render_template('about.html', menu=menu)


@app.errorhandler(404)
def PageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu, css_link = 'styles.css')

# Вот как нейросеть отрефакторила код #
@app.route('/book_card', methods=['GET','POST'])
def book_card():
    id = int(request.args.get('edit')) if request.args.get('edit') else None

    if id is None:
        return render_template('book_card.html', menu=dbase.getMenu(), 
                               title="Ну и чё ты тут делаешь? Тыж не мог попасть на эту страницу")

    if current_user.is_authenticated:
        role = current_user.get_role()
    else:
        role = 'anonymous'
    print(role)

    book_data = dbase.search_book_function(id)
    if book_data:
        book_data = book_data[0]
        author = book_data[2]
        titlet = book_data[1]

        if request.method == 'GET':
            return render_template('book_card.html', menu=dbase.getMenu(), id=id, author=author,
                                   role=role, titlet=titlet, results=book_data)

        elif request.method == 'POST':
            print("Запрос на редактирование книги")

            if request.form['book_picture'] == '':
                print('\nНЕТ КАРТИНКИ\n')

                # Обновление записи без новой картинки
                dbase.update_book_function(request.form['btitle'], request.form['author'], request.form['year'],
                                           request.form['number'], request.form['descript'], book_data[-1], id)
            else:
                # Сохранение картинки в файловой системе
                file = request.files['book_picture']
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                print('Название картинки: ', request.form['book_picture'], '\n')
                dbase.update_book_function(request.form['btitle'], request.form['author'], request.form['year'],
                                           request.form['number'], request.form['descript'], request.form['book_picture'], id)

            return render_template('book_card.html', menu=dbase.getMenu(), id=id, author=author,
                                   titlet=titlet, results=book_data)

    else:
        flash('Книга не найдена', 'error')
        return redirect(url_for('index'))

# А вот так писал я #
@app.route('/book_card', methods=['GET','POST'])
def book_card():
    if request.args.get('edit'):
        id = int(request.args.get('edit'))    
    else:
        return render_template('book_card.html', menu=dbase.getMenu(), 
        title = "Ну и чё ты тут делаешь? Тыж не мог попасть на эту страницу")
    
    if current_user.is_authenticated():
        role = current_user.get_role()
    else:
        role = 'anonymous'
    print(role)
    
    author = dbase.search_book_function(id)[0][2]
    titlet = list(dbase.search_book_function(id)[0])[1]
    if request.method == 'GET':
        return render_template('book_card.html', menu=dbase.getMenu(), id = id, 
            author = author, role = role, titlet = titlet, results=dbase.search_book_function(id))  

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
            author = author, titlet = titlet, results=dbase.search_book_function(id))        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)