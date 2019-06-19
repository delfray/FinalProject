from flask import Flask, render_template, request
import search
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        input_sentence = request.form['input-sentence']
        try:
            a = int(input_sentence)
        except:
            return render_template('error.html', error="Вы указали неверный Id")
        result = search.search(input_sentence)
        if result == 0:
            return render_template('error.html', error="Данная страница закрыта для чтения")
        if result == 1:
            return render_template('result.html', alarm="Комментарии пользователя недоступны для чтения")
        return render_template('result.html')
    return render_template('index.html')


if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)