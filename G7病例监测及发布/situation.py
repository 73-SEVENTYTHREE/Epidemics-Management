# 疫情数据子系统的文件。

from flask import Flask, request, flash, url_for, \
     redirect, render_template, session, jsonify
from flask import Blueprint
import json
import pymysql
import traceback
import datetime

# 为了尽可能减少部署时因服务器文件系统环境导致翻车，因此用如下写法
# app = Flask(__name__.split('.')[0])
# 为了方便整合，我们的内容用一个Blueprint封装。
situation_bp = Blueprint('situation', __name__)

#每日记录的类
class alldata(object):
    def __init__(self):
        self.ver = {}

# 管理员更新数据界面，完整路由为"/situation/admin/"
@situation_bp.route('/admin/', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if not request.form['Date']  or not request.form['Cure'] or \
           not request.form['Confirm'] or not request.form['Import'] or \
           not request.form['Asymptomatic'] or not request.form['Mortality']:
            flash('请填写全部字段', 'error')
            return render_template('admin.html')
        if not request.form['Cure'].isnumeric() or not \
             request.form['Confirm'].isnumeric() or not \
             request.form['Import'].isnumeric() or not \
             request.form['Asymptomatic'].isnumeric() or not \
             request.form['Mortality'].isnumeric():
            flash('请输入正确的数值','error')
            return render_template('situation_admin.html')
        if int(request.form['Cure'])<0 or \
           int(request.form['Confirm'])<0 or \
           int(request.form['Import'])<0 or \
           int(request.form['Asymptomatic'])<0 or \
           int(request.form['Mortality'])<0:
            flash('请输入正确的数值','error')
            return render_template('situation_admin.html')
        try:
            mydate = datetime.date(*map(int, request.form['Date'].split('-')))
        except:
            flash('请输入正确的日期','error')
            traceback.print_exc()
            return render_template('situation_admin.html')
        if mydate < datetime.date(2020, 1, 1) or\
           mydate > datetime.date.today():
            flash('请输入正确的日期','error')
        if not session.get("province") or session.get("identity") != 2:
            flash('管理员验证失败，请重新登录','error')
            # 跳转到用户管理子系统的管理员登录页面
            #return redirect(url_for('framework.a'))
        #此处要调用用户管理子系统的session获取省份
        record = (request.form['Cure'],
                  request.form['Confirm'],
                  request.form['Import'],
                  request.form['Asymptomatic'],
                  request.form['Mortality'],
                  request.form['Date'], # 注意格式！
                  session.get("province"))
        (db, cursor) = _connsql()
        sql = "SELECT Cure, Confirm, Import, Asymptomatic, Mortality \
FROM records where Region=%s and Date=%s"
        cursor.execute(sql, (session.get("province"), request.form['Date']))
        results = cursor.fetchall()
        if results:
            sql = "UPDATE records SET Cure=%s, Confirm=%s, Import=%s, \
Asymptomatic=%s, Mortality=%s WHERE Date=%s and Region=%s"
        else:
            sql = "INSERT INTO records (Cure, Confirm, Import, \
Asymptomatic, Mortality, Date, Region) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try: #先尝试是否能更新数据库，如果不能就不更新我们的数据object了。
            cursor.execute(sql, record)
            db.commit()
            cursor.close()
            db.close()
            # 更新我们的provinceset
            for i in provinceset:
                if i['province'] == session.get("province"):
                    flag = 1
                    for j in i['data']:
                        if j['date'] == request.form['Date'][-5:]:
                            print(j['date'], request.form['Date'][-5:])
                            # 更新内容
                            j['asymptomatic'] = int(request.form['Asymptomatic'])
                            j['cured'] = int(request.form['Cure'])
                            j['dead'] = int(request.form['Mortality'])
                            j['diagnosed'] = int(request.form['Confirm'])
                            j['imported'] = int(request.form['Import'])
                            flag = 0
                            break
                    if flag:
                        # 插入内容
                        i['data'].append({
                            'asymptomatic': int(request.form['Asymptomatic']),
                            'cured': int(request.form['Cure']),
                            'date': request.form['Date'][-5:],
                            'dead': int(request.form['Mortality']),
                            'diagnosed': int(request.form['Confirm']),
                            'imported': int(request.form['Import'])})
                    i['data'] = sorted(i['data'], key=lambda x: x['date'])
                    break
            if not request.form['Date'][-5:] in datadateset:
                datadateset.append(request.form['Date'][-5:])
                datadateset.sort()
            flash('数据更新成功！')
            return redirect(url_for('situation.index'))
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash('数据更新失败', 'error')
            return render_template('situation_admin.html')
    else:
        if session.get("identity") != 2: # 非我们系统的管理员
            flash('管理员验证失败，请重新登录','error')
            # 跳转到用户管理子系统的管理员登录页面
            #return redirect(url_for('framework.a'))
        return render_template('situation_admin.html')

#数据展示界面，完整路由为"/situation/"
@situation_bp.route('/')
def index():
    return render_template('situation_datapage.html')

#向前端发送json数据
@situation_bp.route('/epidata/',methods=['GET']) # 这里是GET啊！GET！
#这里原来是uplord，但是在用户的视角应当是获取数据，因此修改路由。
def upload():
    return jsonify({'provinceset': provinceset,
                    'dates': datadateset})

@situation_bp.route('/getdatedata/', methods=['GET'])
def getdatedata():
    (db, cursor) = _connsql()
    sql = "SELECT Cure, Confirm, Import, Asymptomatic, Mortality \
FROM records where Region=%s and Date=%s"
    # 这种写法可以防止sql注入
    cursor.execute(sql, (request.args.get('province'), request.args.get('date')))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:
        data = {"cured" : result[0],
                "confirm" : result[1],
                "imported" : result[2],
                "asymptomatic" : result[3],
                "dead" : result[4]}
    else:
        data = {"cured" : 0,
                "confirm" : 0,
                "imported" : 0,
                "asymptomatic" : 0,
                "dead" : 0}
    return jsonify(data)

def initSituation():
    global provinceset, datadateset
    try:
        # 打开数据库连接
        (db, cursor) = _connsql()
        # SQL 查询语句
        sql = "SELECT Region, Date, Cure, Confirm, Import, Asymptomatic, Mortality \
FROM records ORDER BY Region, Date"
        provinceset = [] # 查询时需要返回的数据
        datadateset = [] # 所有的日期，按顺序排列
        # 执行SQL语句
        cursor.execute(sql)
        results = cursor.fetchall() # 不要一个一个拿，会有问题的
        # 关闭数据库连接
        cursor.close()
        db.close()
        # print(results)
        #print("init", results)
        tempdata = {} # 一个便于后续计算，临时存储各省份信息的变量
        for result in results:
            if result[0] not in tempdata:
                tempdata[result[0]] = []
            if result[1].strftime('%m-%d') not in datadateset:
                datadateset.append(result[1].strftime('%m-%d'))
            tempdata[result[0]].append({'date': result[1].strftime('%m-%d'),
                                        'diagnosed': result[3],
                                        'cured': result[2],
                                        'dead': result[6],
                                        'imported': result[4],
                                        'asymptomatic': result[5]})
        # 将这些数据转换成所需要的格式
        for province in tempdata:
            provinceset.append({'province': province,
                                'data': tempdata[province]})
        datadateset.sort()
    except Exception as ex:
        traceback.print_exc()
        
def _connsql():
    # 所有连接sql的操作都封装这里
    db = pymysql.connect(host="120.55.44.111",
                         user="root",
                         password="root",
                         db="situation",
                         port=3306,
                         charset='utf8')
    cursor = db.cursor()
    return (db, cursor)
