from flask import Flask, render_template, request, session
from vsearch import search4letters
from checker import check_logged_in

# диспетчер контекста
from DBcm import UseDataBase

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


def log_request(req: 'flask_request', res: str) -> None:
    """Журналирование запросов и результатов обаботки в 
    базе данных MySQL""" 
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

        
@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """ Считывание фразы и символов из полей формы
        Передача их функции search4letters
        Журналирование формирование формы с результатом: сохранение в БД"""
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    title = 'Here are your results:'
    log_request(request, results)
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

if __name__ == '__main__':
    app.run(debug=True)
