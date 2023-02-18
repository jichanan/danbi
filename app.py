from flask import Flask, redirect, request, render_template, session, flash, url_for
import pymysql
import math
import re
import register, login, board, search

app = Flask(__name__)
app.secret_key = "wefwg23g24t42f2r2g3g1guhwuehf2"
conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='danbi', charset='utf8')
cur = conn.cursor()

app.register_blueprint(register.bp)
app.register_blueprint(login.bp)
app.register_blueprint(board.bp)
app.register_blueprint(search.bp)

# no-cache
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# 입력 데이타 저장 
sun = ''
win = ''
hum = ''

# main
@app.route('/', methods=['GET', 'POST'])
def home():
        return render_template('main.html')

#집 햇빛, -> /question/2/
@app.route('/question/1/')
def question():
    if 'user' in session:
        return render_template('recommend/question.html', site='1')
    else:
        return render_template("login.html")
    
# 집 환기, -> question/3/
@app.route('/question/2/')
def question2():
    global sun 
    sun = request.args.get('sunlight')
    return render_template('recommend/question.html', site='2')

# 집 습도계, -> /question/3-1
@app.route('/question/3/')
def question3():
    global win
    win = request.args.get('wind')
    return render_template('recommend/question.html', site='3')

# 집 습도, -> /question/card
@app.route('/question/3-1/')
def question3_1():
    hygrometer = request.args.get('hygrometer')
    return render_template('recommend/question.html',hygrometer=hygrometer )

# 식물 리스트
@app.route('/question/card/')
def card():
    global hum
    hum = request.args.get('humidity')
    SQL = 'select plant_requirement.name,brief from plant_requirement left join plant_info on plant_requirement.id=plant_info.id WHERE sunlight=%s and humidity=%s'
    cur.execute(SQL, [sun,hum])
    result = cur.fetchall()
    len_result = len(result)
    return render_template('recommend/card.html',result=result, len_result=len_result)

# 상세보기 
@app.route('/view_details/')
def view_details():
    name = request.args.get('name')
    SQL = 'select name, detail, eng_name, how_water, how_sunlight from plant_info where plant_info.name=%s'
    cur.execute(SQL,[name])
    result = cur.fetchall()
    return render_template('recommend/view.html', name=name, result=result)

# 홈페이지 소개
@app.route('/introduce/')
def introduce():
    return render_template('introduce.html')

app.run(debug=True, port=5000)

