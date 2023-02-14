from flask import Flask, redirect, request, render_template, session, flash, url_for, Blueprint
import pymysql
import math
import re

bp = Blueprint('board', __name__)
conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='danbi', charset='utf8')
cur = conn.cursor()

# 게시판 
@bp.route('/board/', methods=['GET','POST'])
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
@bp.route('/write/', methods=['GET', 'POST'])
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
@bp.route('/board/<id>/')
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
@bp.route('/board/<id>/delete/')
def post_delete(id):
    cur.execute('delete from board where id = %s',[id])
    conn.commit()
    return redirect('/board/')

# 게시글 수정
@bp.route('/board/<id>/update/', methods=["GET", "POST"])
def post_update(id):
    title = request.form['title']
    context = request.form['context']
    cur.execute("UPDATE board SET title=%s, context=%s WHERE id=%s", [title,context,id])
    conn.commit()
    return redirect('/board/')