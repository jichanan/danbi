from flask import Flask, redirect, request, render_template, session, flash, url_for, Blueprint
import pymysql
import math
import re

bp = Blueprint('register', __name__)
conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='danbi', charset='utf8')
cur = conn.cursor()

# 회원가입
@bp.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        id = request.args.get("id", default="")
        pw = request.args.get("pw", default="")
        email = request.args.get("email", default="")
        nickname = request.args.get("nickname", default="")
        return render_template('register.html',id=id, pw=pw, email=email, nickname=nickname)
    else:
        id = request.form['id']
        pw = request.form['pw']
        email = request.form['email']
        nickname = request.form['nickname']
        check_box = request.form.get("check_box")
        cur.execute('select id from users where userid = %s',[id])
        result = cur.fetchone()
        if not (id and pw and email and nickname):
            flash("빠진 부분이 없는지 확인해주세요.") 
        elif check_box == None:
            flash("개인정보동의에 체크해주세요.")
        elif not re.search('^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{6,12}$', id):
            flash("아이디를 다시 확인해주세요.")
        elif not re.search('^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[^a-zA-Z0-9])[a-zA-Z0-9_\W]{8,16}$', pw):
            flash("비밀번호를 올바르게 입력해주세요.")
        elif result != None:
            flash("이미 중복된 아이디입니다.")
        elif not re.search('^[ㄱ-힣]{2,6}$', nickname):
            flash("닉네임을 다시 확인해주세요.")
        else:
            SQL = "INSERT INTO users (userid, userpw, email, nickname) VALUES (%s,%s,%s,%s)"
            cur.execute(SQL,[id,pw,email,nickname])
            conn.commit()
            return redirect('/login/')
        return render_template('register.html',id=id, email=email, pw=pw, nickname=nickname)

# 회원가입 아이디 중복확인
@bp.route('/register/checkid/', methods=['GET', 'POST'])
def checkid():
    id = request.form['id']
    pw = request.form['pw']
    email = request.form['email']
    cur.execute("select id from users where userid=%s",[id])
    result = cur.fetchone()
    if id == "":
        flash("아이디를 입력해주세요.")
    elif not re.search('^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{6,12}$', id):
        flash("아이디를 다시 확인해주세요.")
    elif result == None:
        flash("사용가능한 아이디입니다.")
        return redirect(url_for("register.register", id=id))
    else:
        flash("이미 사용중인 아이디입니다.")
        return redirect(url_for("register.register", id=id))
    return redirect(url_for("register.register", id=id))
