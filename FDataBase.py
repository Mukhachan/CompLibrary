import sqlite3
import datetime
from flask import flash
import qrcode
from werkzeug.security import generate_password_hash, check_password_hash

class FDataBase:
    def __init__(self, db):
        self.__db = db

        def lower_string(_str):
            return _str.lower()
        self.__db.create_function("mylower", 1, lower_string)
        self.__cur = db.cursor()

    def getMenu(self):
        '''Получает кнопки для меню'''
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print('Ошибка чтения БД (menu)')
        return []

    def value_list(self, book_id):
        '''Возвращает значения книги для страницы редактирования'''
        
        
        sql = '''SELECT * FROM books where id = ?'''
        self.__cur.execute(sql, (book_id,))
        res = self.__cur.fetchall()
        if res:
            print(f"Это вот то что получилось с бд: {list(res)}")
            return res
        return ['Пустота']

    def get_placeholder_newbook(self):
        '''Возвращет все плэйсхолдеры для страницы редактирования и добавления книги'''
        
        
        sql = '''SELECT * FROM placeholder'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print('Ошибка чтения БД (placeholder)')
        return ['Пустота']

    def booklist_function(self):
        """Возвращает все книги из таблицы books
        в виде великого и ужасного списка словарей(кортежей)
        """

        try:
            self.__cur.execute("""SELECT * FROM books""")
            results = self.__cur.fetchall()

            if results:
                return results
        
        except:
            print('Ошибка чтения БД (books)')
        return ['Пустота']

    def update_book_function(self, btitle, author, year, number, descript, book_picture, book_id):
        '''
        Функция принимает в себя ID книги, а также все обновлённые данные и применяет их 
        для записи с соответствующим ID в базе данных. 
        '''
        try:
            self.__cur.execute("""UPDATE books SET btitle = ?, author = ?, year = ?, number = ?,
                                descript = ?, book_picture = ? WHERE id == ?""",
                (btitle, author, year, number, descript, book_picture, book_id))
                                                         
            self.__db.commit()
            flash('Произошло что-то хорошее!', category='success')
            
        except sqlite3.Error as e:

            flash('Загляни в консоль. Там чё-то случилось', category='error')
            print('Произошла какая-то ошибка. Наши полномочия всё')
            print(e)

    def newbook_function(self, btitle, author, year, number, descript, book_picture):
        '''Принимает характеристики книги и создаёт новую запись в бд'''

        try:
            dt = datetime.datetime.now()
            dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
            self.__cur.execute("insert into books VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)",
                               (btitle, author, year, number, descript, dt_string, book_picture))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка добавления книги в БД: " + str(e))
            flash('Ошибка добавления книги', category='error')
            return False
        flash('Книга добавлена', category='success')
        return True

    def delete_book_function(self, del_id):
        '''Принимает ID книги и удаляет её из БД'''
        
        
        try:
            del_command = f"DELETE from books where id = {del_id}"
            self.__cur.execute(del_command)
            self.__db.commit()
        except:
            print("Чёт не так")
            return False
        return True

    def search_book_function(self, book_search):  # Функция поиска  #
        '''Функция поиска книги по БД.
            Если Входное == str, то производится поиск по названию или автору
            если Входное == int, то поиск по ID книги 
        '''

        
        if type(book_search) == str:
            print('(STR) _SEARCH "' + book_search.lower() + '"')
            req = '%' + book_search.lower() + '%'
            print('- ' + req)
            
            try:
                self.__cur.execute("""
                SELECT * FROM books WHERE mylower(btitle) LIKE ? or mylower(author) LIKE ?""", (req, req))

                results = self.__cur.fetchall()
                if results:
                    return results
            except:
                print('Ошибка чтения из БД ')

        elif type(book_search) == int:
            print('\n(INT) _SEARCH Book_Id =', book_search, '\n')
            try:
                self.__cur.execute(
                    f"SELECT * FROM books WHERE id = '{book_search}'")
                results = self.__cur.fetchall()
                if results:
                    return results
            except:
                print('Ошибка чтения из БД с ключом edit (books)')

    def QR_maker(self, id):
        '''
        Функция принимает в себя Данные о книге, а так же номер её экземпляра. 
        На основе входных данных создаётся QR-код, содержащий ссылку на страницу с книгой. 
        
        в GET-части запроса должен быть ID книги и номер экземпляра книги
        '''
        data = "http://192.168.0.133:5000/book_card?id="+ id
        filename = f"book_{id}.png"

        img = qrcode.make(data)
        img.save(f"static\pictures\{filename}")
        
        return f"static\pictures\{filename}"

    def add_user(self, email, card, password):
        """ Добавление нового юзера.
            Хеширование его пароля.
        """
        password = generate_password_hash(password)
        self.__cur.execute("SELECT * from users WHERE email = ?", (email,))

        if len(self.__cur.fetchall()) > 0: # Проверяем зарегестрирована ли почта
            flash('Такая почта уже зарегистрирована', category='error')
            return False
        self.__cur.execute("SELECT * from users WHERE card = ?", (card,))
        if len(self.__cur.fetchall()) > 0: # Проверяем зарегестрирована ли карта
            flash('Номер карты уже используется', category='error')
            return False

        role = 'student'
        dt = datetime.datetime.now()
        dt_string = dt.strftime("%d/%m/%Y %H:%M:%S") # Добавляем время создания юзера

        try:
            self.__cur.execute("insert into users VALUES(NULL, ?, ?, ?, ?, ?)", 
                                (role, email, card, password, dt_string))
            self.__db.commit()
            flash('Вы успешно зарегестрированы', category='success')

            self.__cur.execute("SELECT id from users WHERE email = ?", (email,))
            
            res = self.__cur.fetchall()
            res = list(res[0])[0]
            print(res)

            self.__cur.execute("insert into user_data VALUES(?, NULL, NULL, NULL, NULL)", (res,))
            self.__db.commit()
            return True

        except sqlite3.Error as error:
            print(error)
            flash('Возникла непредвиденная ошибка', category='error')
            return False
           
    def auth_user(self, user, password):
        """ Авторизация юзера """
        print(user)
        if "@" in user:
            """ Ищем по email """
            self.__cur.execute('SELECT * from users WHERE email = ?', (user,))
        elif user.isdigit():
            """ Ищем по карте """
            self.__cur.execute('SELECT * from users WHERE card = ?', (user,))

        result = self.__cur.fetchall()
        hash_psw = (list(result[0])[4])
        
        if check_password_hash(hash_psw, password):
            return list(result[0])[0]
        else:    
            return False
    
    def get_user_data(self, user_id):
        """
        Берёт данные об ученике из таблицы user_data, используя user_id 
        """
        self.__cur.execute(f"SELECT * from user_data WHERE id = {user_id}")
        res = self.__cur.fetchone()
        return res


    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False 
            return res

        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False