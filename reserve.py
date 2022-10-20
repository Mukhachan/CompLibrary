from flask import Flask, render_template , url_for, request, redirect

app = Flask(__name__)

menu = [{"name": "Рекомендации", "url" : "recommended"},
        {"name": "Жанры", "url" : "genre"},
        {"name": "Что нового", "url" : "news"},
        {"name": "О библиотеке", "url" : "about"}]



@app.route('/')
def index():
    print( url_for('index') )
    return redirect(url_for('recommended'))

@app.route('/recommended')
def recommended():
    return render_template('index.html', css_link='styles.css', menu=menu)


@app.route('/auth', methods=["POST", "GET"])
def auth():
    if request.method == 'POST':
        print(request.form)

    return render_template('auth.html')
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        print(request.form)
    return render_template('register.html')


@app.route('/newbook', methods=["POST", "GET"])
def newbook():
    if request.method == 'POST':
        print(request.form)
    
    return render_template('newbook.html', css_link= 'newbook.css', title='Newbook')

@app.route('/about')
def about():
    return render_template('about.html', menu=menu)


@app.errorhandler(404)
def PageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu, css_link = 'styles.css')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)