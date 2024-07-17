from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from db import get_user
app = Flask(__name__)
app.secret_key = "my_secret_key"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Failed to login!'

    return render_template('login.html', message=message)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/chat')
@login_required
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@socketio.on('join_room')
def handle_join_room_event(data):
    print("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data)

@socketio.on('send_message')
def send_message(data):
    print("{} has sent message to the room {}: {}".format(data['username'], data['room'], data['message']))
    socketio.emit('receive_message', data, room=data['room'])

@login_manager.user_loader
def load_user(username):
    return get_user(username)



if __name__ == '__main__':
    socketio.run(app, debug=True)
