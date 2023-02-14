from flask import Flask, redirect, request, render_template, session, flash, url_for, Blueprint
import pymysql
import math
import re

bp = Blueprint('search', __name__)
conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='danbi', charset='utf8')
cur = conn.cursor()

# 식물 검색
@bp.route('/search/')
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