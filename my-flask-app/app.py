
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Dockerized Flask!'

if __name__ == '__main__':
    # Docker 컨테이너 외부와의 통신을 위해 host를 '0.0.0.0'으로 설정한다
    app.run(host='0.0.0.0', port=5000)