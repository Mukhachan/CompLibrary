import sqlite3
import datetime


class FDataBase:
    def __init__(self, db):
        self.__db = db

        def lower_string(_str):
            return _str.lower()
        self.__db.create_function("mylower", 1, lower_string)
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

    def value_list(self, book_id):
        sql = '''SELECT * FROM books where id = ?'''
        self.__cur.execute(sql, (book_id,))
        res = self.__cur.fetchall()
        
        if res:
            print(f"Это вот то что получилось с бд: {list(res)}")
            return res
        return ['Пустота']
    
    def get_inputs_newbook(self):
        sql = '''SELECT * FROM placeholder'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print('Ошибка чтения БД (placeholder)')
        return ['Пустота']

    def all_books_function(self):
        try:
            self.__cur.execute("""SELECT * FROM books""")
            results = self.__cur.fetchall()

            if results:
                return results
        except:
            print('Ошибка чтения БД (books)')
        return []

    def newbook_function(self, btitle, author, year, number, descript, book_picture):
        try:
            dt = datetime.datetime.now()
            dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
            self.__cur.execute("insert into books VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)",
                               (btitle, author, year, number, descript, dt_string, book_picture))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления книги в БД: " + str(e))
            return False
        return True

    def delete_book_function(self, del_id):
        try:
            del_command = f"DELETE from books where id = {del_id}"
            self.__cur.execute(del_command)
            self.__db.commit()
        except:
            print("Чёт не так")
            return False
        return True

    def search_book_function(self, book_search):  # Функция поиска  #

        if book_search.isdigit() == False:

            print('(STR) _SEARCH "' + book_search.lower() + '"')
            req = '%' + book_search.lower() + '%'
            print('- ' + req)

            try:
                self.__cur.execute("""SELECT * FROM books WHERE mylower(btitle) LIKE ? or mylower(author) LIKE ?""", (req, req))

                results = self.__cur.fetchall()
                if results:
                    return results
            except:
                print('Ошибка чтения из БД ')

            #   or mylower(author)
        elif book_search.isdigit():
            print('(INT) _SEARCH ' + book_search.lower())
            try:
                self.__cur.execute(
                    f"SELECT * FROM books WHERE id = '{book_search}'")
                results = self.__cur.fetchall()
                if results:
                    return results
            except:
                print('Ошибка чтения из БД с ключом edit (books)')

            print('Пока функция почти не работает')
