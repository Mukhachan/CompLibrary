import sqlite3
import datetime


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()

            if res: 
                return res 
        except:
            print('Ошибка чтения БД (menu)')
        return []

    def get_inputs_newbook(self):
        sql = '''SELECT * FROM placeholder'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print('Ошибка чтения БД (placeholder)')
        return []

    def all_books_function(self):
        try:
            self.__cur.execute("""SELECT * FROM books""")
            results = self.__cur.fetchall()

            if results:
                return results    
        except:
            print('Ошибка чтения БД (books)')
        return []

    def newbook_function(self, title, author, year, number, descript):
        try:
            dt = datetime.datetime.now()
            dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
            self.__cur.execute("insert into books VALUES(NULL, ?, ?, ?, ?, ?, ?)", (title, author, year, number, descript, dt_string))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления книги в БД: "+ str(e))
            return False
        return True

    def delete_book_function(self, del_id):
        try:
            del_command = """DELETE from books where id = ?"""
            self.__cur.execute(del_command, (del_id))
            self.__db.commit()
        except:
            print("Чёт не так")
            return False
        return True

    def search_book_function(self, book_search): #  Функция поиска  #
        try:
            self.__cur.execute(f"SELECT * FROM books WHERE id = '{book_search}'")
            results = self.__cur.fetchall()
            if results:
                return results
        except:
            print('Ошибка чтения из БД с ключом edit (books)')
        print('Пока функция почти не работает')
        return []

    def edit_book_function(self, book_edit): #  Функция редактирования  #
        print('Пока функция не работает')