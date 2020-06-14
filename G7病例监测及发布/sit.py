# 疫情数据子系统的文件。主入口在all.py。

from flask import Flask, request, flash, url_for, \
     redirect, render_template, session, jsonify
#from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
import json
import pymysql
import traceback

# 为了尽可能减少部署时因服务器文件系统环境导致翻车，因此用如下写法
app = Flask(__name__.split('.')[0])
# 为了方便整合，我们的内容用一个Blueprint封装。
bp = Blueprint('sit', __name__, url_prefix='/situation')
#_db = SQLAlchemy(app) #为了防止和其他组的变量名冲突，因此改为私有

#每日记录的类
class alldata(object):
    def __init__(self):
        self.ver = {}

'''
#建立数据库表
class Record(_db.Model):
    __tablename__ = 'records'
    Region = _db.Column(_db.String(64), primary_key = True)
    Date = _db.Column(_db.Date, primary_key = True)
    Cure = _db.Column(_db.Integer)
    Comfirm = _db.Column(_db.Integer)
    Import = _db.Column(_db.Integer)
    Asymptomatic = _db.Column(_db.Integer)
    Mortality = _db.Column(_db.Integer)
    
    def __repr__(self):
        return '<Record %r>' % self.Record  
'''

###管理员界面
##@app.route('/')
##def show_all():
##    return render_template('admin.html',Record = Record.query.all() )

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

# 下面这堆其实不是我们组管的，也没必要真整个login出来……
'''
# 用户请求进入数据展示界面
@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        if request.form.get('username') == 'anwen':
            session['user'] = request.form.get('username')
            return redirect('/')
# 交由客户端保管机制
# 开启session['ursernsm'] = request.form.get('username')
# {"username":anwen}
# 序列化字典 == 字符串
# 加密字符串 Secret key 密钥字符串
#
# 接受反序列化Session;从cookie中获取到一个session key的值
# 通过Secretkey 解密session
# 反序列化成字典
'''

#数据展示界面，完整路由为"/situation/"
@bp.route('/')
def index():
    print(session.get('user'))
    return render_template('data page.html')

#向前端发送json数据
@bp.route('/epidata/',methods=['GET']) # 这里是GET啊！GET！
#这里原来是uplord，但是在用户的视角应当是获取数据，因此修改路由。
def upload():
    return jsonify({'provinceset': provinceset,
                    'dates': datadateset})

def initSituation():
    global provinceset, datadateset
    global _db
    try:
        # 初始化本模块
        #_db.drop_all()
        #_db.create_all()
        # 打开数据库连接
        _db= pymysql.connect(host="120.55.44.111",user="root",password="root",db="situation",port=3306,charset='utf8')
        cursor = _db.cursor()
        # SQL 查询语句
        sql = "SELECT * FROM records ORDER BY Region, Date"
##        var1=''
##        var2=''
        provinceset = [] # 查询时需要返回的数据
        datadateset = [] # 所有的日期，按顺序排列
        # 执行SQL语句
        cursor.execute(sql)
        results = cursor.fetchall() # 不要一个一个拿，会有问题的
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
        #print(provinceset)
            #print(tempdata)
##            var1 = Record.Region
##            if(var1 == var2):
##                test = alldata()
##                dic = {}
##                test.ver = {'province' : Record.Region, 'data' : []}
##                dic = {'date':Record.Date,'diagnosed':Record.Confirm,'imported':Record.Import,'asymptomatic':Record.Asymptomatic,'cured':Record.Cure,'dead':Record.Mortality}
##                test['data'].append(dic)
##                result = cursor.fetchone()
##            else:
##                provinceset.append(test)
##                test = alldata()
##                dic = {}
##                test.ver = {'province' : Record.Region, 'data' : []}
##                dic = {'date':Record.Date,'diagnosed':Record.Confirm,'imported':Record.Import,'asymptomatic':Record.Asymptomatic,'cured':Record.Cure,'dead':Record.Mortality}
##                test['data'].append(dict)
##                result = cursor.fetchone()
##            var2 = Record.Region
    except Exception as ex:
        traceback.print_exc()
        # 关闭数据库连接

