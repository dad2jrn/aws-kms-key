from flask import Flask, request, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/keys', methods=['GET'])
@app.route('/output', methods=['POST'])
def profile(username=None):
    if request.method == 'POST':
        username = request.form['username']
        key = request.form['key']
        return render_template('keys.html', username=username, key=key)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
