from flask import Flask, render_template, request
from flask_socketio import SocketIO
from pmrc import PlaymobilRacer

app = Flask(__name__)
socketio = SocketIO(app)

mac = "ac:9a:22:22:c8:64"
car = PlaymobilRacer(mac)

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
    car.key(message['pressed'])


if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", port=5000)
