from flask import Flask
app = Flask(__name__)

@app.route('/')
def display_error():
    return 'The application directory has not been mounted in the right place'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
