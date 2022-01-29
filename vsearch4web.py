from flask import Flask, render_template, request, escape
from vsearch import search4letters

app = Flask(__name__)


def log_request(req: 'flask_request', res: str) -> None:
    """Журналирование запросов и результатов обаботки в 
    базе данных MySQL"""

    # параметры соединения с бд
    dbconfig = { 'host': '127.0.0.1',
                'user': 'fvv',
                'password': '0546Fvv-1',
                'database': 'vsearchlogDB',}
    # импорт драйвера
    # установка соединения
    # создание курсора
    import mysql.connector
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    # строка с текстом запроса
    _SQL = """insert into log
            (phrase, letters, ip, browser_string, results)
            values
            (%s, %s, %s, %s, %s)"""

    # запуск запроса
    # параметры: данные из HTML-формы веб-приложения      
    cursor.execute(_SQL, (req.form['phrase'],
                        req.form['letters'],
                        req.remote_addr,
                        req.user_agent.browser,
                        res,))
    
    conn.commit()
    cursor.close()
    conn.close()

        
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
    """Форма ввода запроса и символов"""
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/viewlog')
def view_the_log() -> 'html':
    """Чтение журнала
        преобразование журнала в список списков
        формирование формы для журнала"""
    contents = []
    with open('vsearch.log') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Result')
    return render_template('viewlog.html',
                            the_title= 'View Log',
                            the_row_titles = titles,
                            the_data = contents,)

if __name__ == '__main__':
    app.run(debug=True)
