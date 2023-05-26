from flask import Flask, redirect, request, render_template, session, flash, url_for, Blueprint
from flask_socketio import SocketIO, emit
import pymysql

bp = Blueprint('chat', __name__)
socketio = SocketIO()

conn = pymysql.connect(
host='127.0.0.1',
user='root',
password='',
db='danbi',
charset='utf8')
cur = conn.cursor()

chat_history = []

# 채팅
@bp.route('/chat/')
def chat():
    if 'user' in session:
        user_id = session['user']
        return render_template('chat/chat.html', user_id=user_id)
    else:
        return redirect('/login/')

# socket연결 
@socketio.on('connect')
def handle_connect():
    emit('join_chatroom', chat_history)

# send_message 수신
@socketio.on('send_message')
def handle_send_message(message):
    data = get_user_info()
    data['message'] = message
    if len(chat_history) < 10:
        chat_history.append(data)
    else:
        del chat_history[0]
        chat_history.append(data)
    print(chat_history)
    emit('recieve message', data, broadcast=True)

def get_user_info():
    user_id = session['user']
    cur.execute('SELECT nickname FROM users WHERE userid = %s', [user_id])
    nickname = cur.fetchone()[0]
    return {'user_id': user_id, 'nickname': nickname}

# Flask Application object 연결
def init_app(app):
    socketio.init_app(app, ping_interval=120, ping_timeout=180)
    app.register_blueprint(bp)





