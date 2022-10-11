import sqlite3
import os
from flask import Flask, render_template, request, g , redirect, url_for
from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'ToRa#UCLp1EBPmK6p25W'

app = Flask(__name__)
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


#  редирект на страницу рекомендации  #
@app.route('/')
def index():
    db = get_db()
    dbase = FDataBase(db)
    print( url_for('index') )
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

#  Страница "о библиотеке"  #
@app.route('/about')
def about():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('about.html', menu=dbase.getMenu())


#  руты авторизации и регистрации  #
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


#  Обработка ошибок  #
@app.errorhandler(404)
def PageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template('page404.html', title='Страница не найдена', 
                            menu=dbase.getMenu(), css_link = 'styles.css')

#  Добавление книги  #
@app.route('/newbook', methods=["POST", "GET"])
def newbook():
    if request.method == 'POST':
        print(request.form)
    
    return render_template('newbook.html', css_link= 'newbook.css', title='Newbook')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)