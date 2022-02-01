from flask import session
from functools import wraps

# декоратор
def check_logged_in(func):
    """декоратор check_logged принимает объект декорируемой функции
    возвращает вложенную функцию wrapper"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """если пользователь выполнил вход, то вызвать декорируемую функцию
        если пользователь не выполнил вход, то вернуть сообщение"""

        if 'logged_in' in session:
            return func(*args, **kwargs)
        return 'You are NOT logged in'

    return wrapper
