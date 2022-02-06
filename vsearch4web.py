
from flask import Flask, render_template, request, session
from flask import copy_current_request_context
from vsearch import search4letters
from checker import check_logged_in
from time import sleep
from threading import Thread


# диспетчер контекста
from DBcm import UseDataBase, ConnectionError, CredentialError, SQLError

app = Flask(__name__)

# добавление в конфигурацию веб-приложения параметров 
# соединения с бд
app.config['dbconfig'] = {'host': '127.0.0.1',
                        'user': 'fvv',
                        'password': '0546Fvv-1',
                        'database': 'vsearchlogDB',}

                        
app.secret_key = 'YouWillNeverGuessMySecretKey'

@app.route('/login')
def do_login() -> str:
    """ авторизация пользователя: добавление элемента в словарь session """
    session['logged_in'] = True
    return 'You are now logged in.'


@app.route('/logout')
def do_logout() -> str:
    """ выход пользователя: удаление элемента из словаря session"""
    session.pop('logged_in')
    return 'You are now logged out'


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """ Считывание фразы и символов из полей формы
    Передача их функции search4letters
    Журналирование формирование формы с результатом: сохранение в БД"""

    """Декоратор copy_current_request_context гарантирует, что HTTP-запрос,
    который активен в момент вызова функции, останется активным, когда функция
    позже запустится в отдельном потоке."""
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """Журналирование запросов и результатов обработки в
        базе данных MySQL"""
        # This makes log_request really slow...
        sleep(15)
        try:
            # используем диспетчер контекста
            with UseDataBase(app.config['dbconfig']) as cursor:
                # строка с текстом запроса
                _SQL = """insert into log
                        (phrase, letters, ip, browser_string, results)
                        values
                        (%s, %s, %s, %s, %s)"""

                # запуск запроса. параметры: данные из HTML-формы веб-приложения
                cursor.execute(_SQL, (req.form['phrase'],
                                      req.form['letters'],
                                      req.remote_addr,
                                      req.user_agent.browser,
                                      res,))
        except ConnectionError as err:
            print('Is your database switched on? Error:', str(err))
        except CredentialError as err:
            print('User-id/Password issues. Error:', str(err))
        except SQLError as err:
            print('Is your query correct? Error:', str(err))
        except Exception as err:
            print('Something went wrong:', str(err))
        return 'Error'
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    title = 'Here are your results:'
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print("***** Logging failed with this error:", str(err))
    return render_template('results.html',
                           the_title = title,
                           the_phrase = phrase,
                           the_letters = letters,
                           the_results = results)

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    """HTML-форма для ввода запроса и символов"""
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    """ функция декорирована: выполнится только для аторизованного пользователя
    Чтение содержимого журнала, преобразование в список списков
    и вывод в виде HTML- таблицы"""

    try:
        with UseDataBase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results
                    from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()

        titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                                the_title = 'View Log',
                                the_row_titles = titles,
                                the_data = contents,)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
    except CredentialError as err:
        print('User-id/Password issues. Error:', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print('Something went wrong:', str(err ))
    return 'Error'

if __name__ == '__main__':
    app.run(debug=True)
