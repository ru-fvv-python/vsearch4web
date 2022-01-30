from sqlite3 import Cursor
import mysql.connector

# Database context manager
class UseDataBase():

    def __init__(self, config: dict) -> None:
        """метод принимает один аргумент — словарь c параметрами
        подключения"""
        self.configuration = config

    def __enter__(self) -> 'cursor':
        """ метод выполняет настройку объекта перед началом 
        блока инструкции with: подключение к БД"""
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()   
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """ кода, который должен выполниться по завершении тела
        инструкции with: закрывает курсор и соединение"""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
