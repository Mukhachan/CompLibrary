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
            if res: return res 
        except:
            print('Ошибка чтения БД')
        return []
    def newbook(self, title, author, year, number, descript):
        try:
            dt = datetime.datetime.now()
            dt_string = dt.strftime("Date: %d/%m/%Y  time: %H:%M:%S")
            self.__cur.execute("insert into books VALUES(NULL, ?, ?, ?, ?, ?, ?)", (title, author, year, number, descript, dt_string))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления книги в БД: "+ str(e))
            return False
        return True