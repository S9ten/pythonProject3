from flask import Flask, render_template, request 

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'button1' in request.form:
            print('Куплено')
        elif 'button2' in request.form:
            print('Понравилось')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)