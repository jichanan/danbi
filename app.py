from flask import Flask, redirect, request, render_template, session, flash, url_for
import pymysql
import math
import re

app = Flask(__name__)
app.secret_key = "wefwg23g24t42f2r2g3g1guhwuehf2"
conn = pymysql.connect(host='127.0.0.1', user='root', password='secret', db='danbi', charset='utf8')
cur = conn.cursor()

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
        return render_template('question.html', site='1')
    else:
        return render_template("login.html")
    
# 집 환기, -> question/3/
@app.route('/question/2/')
def question2():
    global sun 
    sun = request.args.get('sunlight')
    return render_template('question.html', site='2')
# 집 습도계, -> /question/3-1
@app.route('/question/3/')
def question3():
    global win
    win = request.args.get('wind')
    return render_template('question.html', site='3')
# 집 습도, -> /question/card
@app.route('/question/3-1/')
def question3_1():
    hygrometer = request.args.get('hygrometer')
    return render_template('question.html',hygrometer=hygrometer )
# 식물 리스트
@app.route('/question/card/')
def card():
    global hum
    hum = request.args.get('humidity')
    SQL = 'select plant_requirement.name,brief from plant_requirement left join plant_info on plant_requirement.id=plant_info.id WHERE sunlight=%s and humidity=%s'
    cur.execute(SQL, [sun,hum])
    result = cur.fetchall()
    len_result = len(result)
    return render_template('card.html',result=result, len_result=len_result)
# 상세보기 
@app.route('/view_details/')
def view_details():
    name = request.args.get('name')
    SQL = 'select name, detail, eng_name, how_water, how_sunlight from plant_info where plant_info.name=%s'
    cur.execute(SQL,[name])
    result = cur.fetchall()
    return render_template('view.html', name=name, result=result)

# 홈페이지 소개
@app.route('/introduce/')
def introduce():
    return render_template('introduce.html')

# 게시판 
@app.route('/board/', methods=['GET','POST'])
def board():
    if 'user' in session:
        page = request.args.get('page', type=int, default=0)
        per_page = 10 # 1page 당 5개 게시물
        cur.execute('select count(id) from board') # board 테이블 레코드 개수
        total_cnt = cur.fetchone()
        total_cnt = total_cnt[0] # 튜플 벗기기
        total_page = math.ceil(total_cnt / per_page) # 올림, 총 페이지
        SQL = 'SELECT id, title, nickname context FROM board ORDER BY id DESC LIMIT %s OFFSET %s'
        cur.execute(SQL, [per_page, page * per_page])
        result = cur.fetchall()
        # 페이지 블럭을 5개씩 표기
        block_size = 5
        # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
        block_num = int(page / block_size)
        # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 0, 두 번째 블럭이라면, block_start = 5)
        block_start = (block_size * block_num) 
        # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
        block_end = block_start + (block_size - 1)
        return render_template('board/board.html', result=result, total_page=total_page, block_start=block_start, block_end=block_end)
    else:
        return redirect('/login/')
    
# 글쓰기
@app.route('/write/', methods=['GET', 'POST'])
def write():
    if request.method == 'GET':
        return render_template('board/write.html')
    else:
        title = request.form['title']
        context = request.form['context']
        userid = session['user']
        cur.execute("SELECT nickname FROM users WHERE userid=%s", [userid])
        nickname = cur.fetchone()
        nickname = nickname[0]
        print(nickname)
        SQL = "INSERT INTO board (userid, title, context, nickname) VALUES (%s, %s, %s, %s);"
        cur.execute(SQL, [userid, title,context, nickname])
        conn.commit()
        return redirect('/board/')

# 게시글 상세보기
@app.route('/board/<id>/')
def boardview(id):
        SQL = "SELECT title, context, userid, id FROM board where id=%s"
        cur.execute(SQL,[id])
        result = cur.fetchone()
        title = result[0]
        context = result[1]
        userid = result[2]
        if request.args.get("method") == "update":
            return render_template('board/post_update.html',title=title, context=context, userid=userid, id=id)
        else:
            return render_template('board/boardview.html',title=title, context=context, userid=userid, id=id, readonly="readonly")


# 게시글 삭제
@app.route('/board/<id>/delete/')
def post_delete(id):
    cur.execute('delete from board where id = %s',[id])
    conn.commit()
    return redirect('/board/')

# 게시글 수정
@app.route('/board/<id>/update/', methods=["GET", "POST"])
def post_update(id):
    title = request.form['title']
    context = request.form['context']
    cur.execute("UPDATE board SET title=%s, context=%s WHERE id=%s", [title,context,id])
    conn.commit()
    return redirect('/board/')

# 식물 검색
@app.route('/search/')
def search():
    search_list = ()
    search1 = request.args.get('search')
    cur.execute("select name, brief from plant_info ")
    result = cur.fetchall()
    for i in result:
        match = re.search(rf"[{i[0]}]" + "{2,}", rf"{search1}")
        if match:
            search_list += (i,)
    if search_list == ():
        flash("죄송합니다. " + search1 + "을 찾을 수 없습니다.")
    return render_template('search_plant.html', search_list=search_list)

# 회원가입
@app.route('/register/', methods=['GET', 'POST'])
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
@app.route('/register/checkid/', methods=['GET', 'POST'])
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
        return redirect(url_for("register", id=id))
    else:
        flash("이미 사용중인 아이디입니다.")
        return redirect(url_for("register", id=id))
    return redirect(url_for("register", id=id))

# 로그인
@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        id = request.form['id']
        pw = request.form['pw']
        SQL = 'select userid from users where userid = %s and userpw = %s'
        cur.execute(SQL, [id,pw])
        result = cur.fetchall()
        result = result[0][0]
        if result == ():
            return redirect('/login/')
        else:
            session['user'] = result
            return redirect('/')

# 로그아웃
@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect('/')

app.run(debug=True, port=5000)

