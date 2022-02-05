from sqlite3 import Cursor
import mysql.connector

# для обработки ошибки при подключении к БД
class ConnectionError(Exception):
    pass

# для обработки ошибки при регистрации в БД
class CredentialError(Exception):
    pass

# для обработки ошибки в запросах SQL
class SQLError(Exception):
    pass


# Database context manager
class UseDataBase():

    def __init__(self, config: dict) -> None:
        """метод принимает один аргумент — словарь c параметрами
        подключения"""
        self.configuration = config


    def __enter__(self) -> 'cursor':
        """ метод выполняет настройку объекта перед началом 
        блока инструкции with: подключение к БД"""
        # защита подключения к БД
        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.InterfaceError as err:
            # возбуждаем собственное исключение
            raise ConnectionError(err)
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialError(err)

    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """ код, который должен выполниться по завершении тела
        инструкции with: закрывает курсор и соединение"""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exc_type == mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)

