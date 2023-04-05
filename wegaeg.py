from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        button = request.form.get('button')
        if button == 'button1':
            result = 'Вы нажали на кнопку 1'
        elif button == 'button2':
            result = 'Вы нажали на кнопку 2'
        else:
            result = 'Неизвестная кнопка'
        return render_template('result.html', result=result)
    else:
        return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
