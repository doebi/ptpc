from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/dd')
def ws_connect():
    socketio.emit('msg', {'count': 42}, namespace='/dd')


@socketio.on('disconnect', namespace='/dd')
def ws_disconnect():
    socketio.emit('msg', {'count': 42}, namespace='/dd')

@socketio.on('key', namespace='/dd')
def ws_key(message):
    print(message['key'])

if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", port=5000)
