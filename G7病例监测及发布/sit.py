# 疫情数据子系统的文件。主入口在all.py。

from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
import json
import pymysql

# 为了尽可能减少部署时因服务器文件系统环境导致翻车，因此用如下写法
app = Flask(__name__.split('.')[0])
# 为了方便整合，我们的内容用一个Blueprint封装。
bp = Blueprint('sit', __name__, url_prefix='/situation')
_db = SQLAlchemy(app) #为了防止和其他组的变量名冲突，因此改为私有

#每日记录的类
class alldata(object):
    def __init__(self):
        self.ver = {}
        
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
             
###管理员界面
##@app.route('/')
##def show_all():
##    return render_template('admin.html',Record = Record.query.all() )

# 管理员更新数据界面，完整路由为"/situation/admin/"
@bp.route('/admin/', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if not request.form['Date']  or not request.form['Cure'] or not request.form['Confirm'] or not request.form['Import'] or not request.form['Asymptomatic'] or not request.form['Mortality']:
            flash('Please enter all the fields', 'error')
        elif not isinstance(request.form['Cure'],int) or not isinstance(request.form['Confirm'],int) or not isinstance(request.form['Import'],int) or not isinstance(request.form['Asymptomatic'],int) or not isinstance(request.form['Mortality'],int):
            flash('Please enter correct forms','error')
        elif request.form['Cure']<0 or request.form['Confirm']<0 or request.form['Import']<0 or request.form['Asymptomatic']<0 or request.form['Mortality']<0:
            flash('Please enter correct forms','error')
        else:
            #此处要调用用户管理子系统的session获取省份
            record = Record(session.get("region"), request.form['Date'], request.form['Cure'],request.form['Confirm'],
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
        if not session.get("region"):
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
    # 暂时先禁用，使用测试数据，待后端部署完成
    # return jsonify(provinceset)
    return """
    [{
        "province": "浙江",
        "data": [{
            "date": "03-01", "diagnosed": 100, "imported": 10,
            "asymptomatic": 15, "cured": 5, "dead": 1
        },
        {
            "date": "03-02", "diagnosed": 90, "imported": 9,
            "asymptomatic": 20, "cured": 10, "dead": 2
        },
        {
            "date": "03-03", "diagnosed": 80, "imported": 2,
            "asymptomatic": 17, "cured": 15, "dead": 0
        }]
    },
    {
        "province": "江苏",
        "data": [{
            "date": "03-01", "diagnosed": 70, "imported": 5,
            "asymptomatic": 12, "cured": 13, "dead": 1
        },
        {
            "date": "03-02", "diagnosed": 30, "imported": 6,
            "asymptomatic": 32, "cured": 43, "dead": 0
        },
        {
            "date": "03-03", "diagnosed": 40, "imported": 7,
            "asymptomatic": 14, "cured": 24, "dead": 1
        }]
    },
    {
        "province": "湖北",
        "data": [{
            "date": "03-01", "diagnosed": 70, "imported": 6,
            "asymptomatic": 12, "cured": 13, "dead": 1
        },
        {
            "date": "03-02", "diagnosed": 30, "imported": 30,
            "asymptomatic": 32, "cured": 43, "dead": 0
        },
        {
            "date": "03-03", "diagnosed": 40, "imported": 1,
            "asymptomatic": 14, "cured": 24, "dead": 1
        }]
    }
    ]
    """

def initSituation():
    global _db
    # 初始化本模块
    _db.drop_all()
    _db.create_all()
    # 打开数据库连接
    _db = pymysql.connect("localhost", "root", "Yang654321", "test")
    # SQL 查询语句
    sql = "SELECT * FROM Record ORDER BY Region,Date"
    var1=''
    var2=''
    provinceset=[]
    try:
    # 执行SQL语句
        cursor.execute(sql)
        result = cursor.fetchone()
        while result != None:
            var1 = Record.Region
            if(var1 == var2):
                test = alldata()
                dic = {}
                test.ver = {'province' : Record.Region, 'data' : []}
                dic = {'date':Record.Date,'diagnosed':Record.Confirm,'imported':Record.Import,'asymptomatic':Record.Asymptomatic,'cured':Record.Cure,'dead':Record.Mortality}
                test['data'].append(dic)
                result = cursor.fetchone()
            else:
                provinceset.append(test)
                test = alldata()
                dic = {}
                test.ver = {'province' : Record.Region, 'data' : []}
                dic = {'date':Record.Date,'diagnosed':Record.Confirm,'imported':Record.Import,'asymptomatic':Record.Asymptomatic,'cured':Record.Cure,'dead':Record.Mortality}
                test['data'].append(dict)
                result = cursor.fetchone()
            var2 = Record.Region
    except Exception as ex:
        print('wrong!')
        # 关闭数据库连接

