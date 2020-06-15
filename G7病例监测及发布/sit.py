# 疫情数据子系统的文件。主入口在all.py。

from flask import Flask, request, flash, url_for, \
     redirect, render_template, session, jsonify
from flask import Blueprint
import json
import pymysql
import traceback

# 为了尽可能减少部署时因服务器文件系统环境导致翻车，因此用如下写法
app = Flask(__name__.split('.')[0])
# 为了方便整合，我们的内容用一个Blueprint封装。
bp = Blueprint('sit', __name__, url_prefix='/situation')

#每日记录的类
class alldata(object):
    def __init__(self):
        self.ver = {}

# 管理员更新数据界面，完整路由为"/situation/admin/"
@bp.route('/admin/', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if not request.form['Date']  or not request.form['Cure'] or not request.form['Confirm'] or not request.form['Import'] or not request.form['Asymptomatic'] or not request.form['Mortality']:
            flash('请填写全部字段', 'error')
        elif not isinstance(request.form['Cure'],int) or not isinstance(request.form['Confirm'],int) or not isinstance(request.form['Import'],int) or not isinstance(request.form['Asymptomatic'],int) or not isinstance(request.form['Mortality'],int):
            flash('请输入正确的值','error')
        elif request.form['Cure']<0 or request.form['Confirm']<0 or request.form['Import']<0 or request.form['Asymptomatic']<0 or request.form['Mortality']<0:
            flash('请输入正确的值','error')
        else:
            if not session.get("province") or session.get("identity") != 2:
                flash('管理员验证失败，请重新登录','error')
                pass # TODO：跳转到用户管理子系统的管理员登录页面
            #此处要调用用户管理子系统的session获取省份
            record = Record(session.get("province"), request.form['Date'], request.form['Cure'],request.form['Confirm'],
                            request.form['Import'], request.form['Asymptomatic'], request.form['Mortality'])
            #更新返回前端的数据
            for pro in provinceset:
                if pro['province'] == record.Region:
                    dic = {}
                    dic = {'date':record.Date,'diagnosed':record.Confirm,'imported':record.Import,'asymptomatic':record.Asymptomatic,'cured':record.Cure,'dead':record.Mortality}
                    pro['data'].append(dic)  
            #更新数据库
            _db.session.add(record)
            _db.session.commit()
            
            flash('Record was successfully added')
            return redirect(url_for('data page.html'))
    else:
        if session.get("identity") != 2: # 非我们系统的管理员
            pass # TODO：跳转到用户管理子系统的管理员登录页面
        return render_template('admin.html')

#数据展示界面，完整路由为"/situation/"
@bp.route('/')
def index():
    session['name'] = "杨凌霄"
    session['province'] = '浙江'
    return render_template('data page.html')

#向前端发送json数据
@bp.route('/epidata/',methods=['GET']) # 这里是GET啊！GET！
#这里原来是uplord，但是在用户的视角应当是获取数据，因此修改路由。
def upload():
    return jsonify({'provinceset': provinceset,
                    'dates': datadateset})

@bp.route('/getdatedata/', methods=['GET'])
def getdatedata():
    (db, cursor) = _connsql()
    sql = "SELECT Cure, Confirm, Import, Asymptomatic, Mortality \
FROM records where Region=%s and Date=%s"
    # 这种写法可以防止sql注入
    cursor.execute(sql, (request.args.get('province'), request.args.get('date')))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    print(result)
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
        sql = "SELECT * FROM records ORDER BY Region, Date"
        provinceset = [] # 查询时需要返回的数据
        datadateset = [] # 所有的日期，按顺序排列
        # 执行SQL语句
        cursor.execute(sql)
        results = cursor.fetchall() # 不要一个一个拿，会有问题的
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
                                        'diagnosed': result[2],
                                        'cured': result[3],
                                        'dead': result[4],
                                        'imported': result[5],
                                        'asymptomatic': result[6]})
        # 将这些数据转换成所需要的格式
        for province in tempdata:
            provinceset.append({'province': province,
                                'data': tempdata[province]})
        datadateset.sort()
    except Exception as ex:
        traceback.print_exc()
        # 关闭数据库连接

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
