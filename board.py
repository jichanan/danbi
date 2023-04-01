from flask import Flask, redirect, request, render_template, session, flash, url_for, Blueprint
import pymysql
import math
from datetime import datetime, timedelta
import re
import base64, io
from PIL import Image

bp = Blueprint('board', __name__)
conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='danbi', charset='utf8')
cur = conn.cursor()

# 게시판 
@bp.route('/board/', methods=['GET','POST'])
def board():
    if 'user' in session:
        page = request.args.get('page', type=int, default=0)
        per_page = 10 
        cur.execute('select count(id) from board') 
        total_cnt = cur.fetchone()
        total_cnt = total_cnt[0] 
        total_page = math.ceil(total_cnt / per_page)
        SQL = 'SELECT id, title, nickname, comment_count, hits FROM board ORDER BY id DESC LIMIT %s OFFSET %s'
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
        editor_content = request.form['editor_content']
        pattern = '<img src=".*?(?=")'
        images64 = re.findall(pattern, editor_content)
        userid = session['user']
        cur.execute("SELECT nickname FROM users WHERE userid=%s", [userid])
        nickname = cur.fetchone()[0]
        SQL = "INSERT INTO board (userid, title, context, nickname) VALUES (%s, %s, %s, %s);"
        cur.execute(SQL, [userid, title, editor_content, nickname])
        conn.commit()
        imgNum = 1
        for image64 in images64:
            b64string = image64.split(',')[1]
            img = Image.open(io.BytesIO(base64.b64decode(b64string)))
            cur.execute('SELECT id FROM board ORDER BY id DESC LIMIT 1')
            board_id = cur.fetchone()[0]
            img.save('static/post_img/' + str(board_id) + '-' + str(imgNum) + '.png')
            img_path = '/static/post_img/' + str(board_id) + '-' + str(imgNum) + '.png'
            editor_content = re.sub('data:.*?(?=")', img_path, editor_content, count=1)
            cur.execute('UPDATE board SET context = %s WHERE id = %s', [editor_content, board_id])
            conn.commit()
            imgNum += 1
        return redirect('/board/')

# 게시글 상세보기
@bp.route('/board/<id>/', methods=['POST', 'GET'])
def boardview(id):
        cur.execute("SELECT title, context, userid, id FROM board where id=%s",[id])
        result = cur.fetchone()
        title = result[0]
        context = result[1]
        userid = result[2]
        cur.execute('select comment, comment_time, nickname from postcomment where board_id = %s', [id])
        comments = cur.fetchall()
        session_id = session['user']    
        cur.execute('select nickname from users where userid=%s',[session_id])
        nickname = cur.fetchone()[0]
        # 조회수
        cur.execute('SELECT board_no FROM hit_count WHERE userid = %s', [session_id])
        hit = cur.fetchall()
        if (id,) not in hit:
            hit_time = datetime.now()
            cur.execute('INSERT INTO hit_count (userid, board_no, hit_time) VALUES (%s, %s, %s)', [session_id, id, hit_time])
            conn.commit()
            # increase 1 hits
            cur.execute('SELECT hits FROM board WHERE id = %s', [id])
            hits = cur.fetchone()[0]
            hits = int(hits)
            hits += 1
            cur.execute('UPDATE board SET hits = %s WHERE id = %s', [hits, id])
            conn.commit()
        else:
            cur.execute('SELECT hit_time FROM hit_count WHERE userid = %s AND board_no = %s', [session_id, id])
            hit_time = cur.fetchone()[0]
            hit_time = datetime.strptime(hit_time, '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() - hit_time > timedelta(days=1):
                current_time = datetime.now()
                cur.execute('UPDATE hit_count SET hit_time = %s WHERE userid = %s AND board_no = %s',[current_time, session_id, id])
                conn.commit()
                cur.execute('SELECT hits FROM board WHERE id = %s', [id])
                hits = cur.fetchone()[0]
                hits = int(hits)
                hits += 1
                cur.execute('UPDATE board SET hits = %s WHERE id = %s', [hits, id])
                conn.commit()
        if request.args.get("method") == "update":
            return render_template('board/post_update.html',title=title, context=context, userid=userid, id=id)
        else:
            return render_template('board/boardview.html',title=title, context=context, userid=userid, id=id, nickname=nickname, comments=comments, readonly="readonly")

# 게시글 댓글
@bp.route('/postcomment/<id>/', methods=['GET', 'POST'])
def post_comment(id):
    comment = request.form['comment']
    nickname = request.form['nickname']
    currentTime = datetime.now()
    comment_time = currentTime.strftime('%Y-%m-%d %I:%M:%S %p')
    cur.execute('insert into postcomment (board_id, comment, comment_time, nickname) values (%s, %s, %s, %s)', [id, comment, comment_time, nickname])
    conn.commit()
    cur.execute('select count(postcomment.id) from board left join postcomment on board.id = postcomment.board_id where board.id = %s', [id])
    comment_count = cur.fetchone()[0]
    cur.execute('UPDATE board SET comment_count = "%s" WHERE id = %s', [comment_count, id])
    conn.commit()
    return redirect(f'/board/{id}/')
    

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