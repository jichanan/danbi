from flask import Flask, redirect, request, render_template, session, flash, url_for, Blueprint
import pymysql
import math
import re

bp = Blueprint('login', __name__)
conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='danbi', charset='utf8')
cur = conn.cursor()

# 로그인
@bp.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        id = request.form['id']
        pw = request.form['pw']
        SQL = 'select userid from users where userid = %s and userpw = %s'
        cur.execute(SQL, [id,pw])
        result = cur.fetchone()
        if result == None:
            return redirect('/login/')
        else:
            result = result[0]
            session['user'] = result
            return redirect('/')

# 로그아웃
@bp.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect('/')