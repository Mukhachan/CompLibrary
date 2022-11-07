# -*- coding: utf-8 -*-
import sqlite3
# Пользовательская функция изменения регистра
def myfunc(s):
    return s.lower()

con = sqlite3.connect("catalog.db")
# Связываем имя "mylower" с функцией myfunc()
con.create_function("mylower", 1, myfunc)
cur = con.cursor()
string = "%МуЗЫка%"	#  Строка для поиска
# Поиск без учета регистра символов
sql = """SELECT * FROM rubr
   WHERE mylower(name_rubr) LIKE ?"""
cur.execute(sql,(string.lower(),))
print(cur.fetchone()[1]) # Результат:   Музыка
cur.close()
con.close()
input()