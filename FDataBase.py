import sqlite3
import time
import math


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
            tm = math.floor(time.time())
            self.__cur.execute("insert into books VALUES(NULL, ?, ?, ?, ?, ?, ?)", (title, author, year, number, descript, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления книги в БД: "+ str(e))
            return False
        return True