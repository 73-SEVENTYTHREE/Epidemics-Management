from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
import json
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Yang654321@127.0.0.1/test'
db = SQLAlchemy(app)
app.secret_key = '!@#$%^&*()11'

#每日记录的类
class alldata(object):
    def __init__(self):
        self.ver = {}
        
#建立数据库表
class Record(db.Model):
    __tablename__ = 'records'
    Region = db.Column(db.String(64), primary_key = True)
    Date = db.Column(db.Date, primary_key = True)
    Cure = db.Column(db.Integer)
    Comfirm = db.Column(db.Integer)
    Import = db.Column(db.Integer)
    Asymptomatic = db.Column(db.Integer)
    Mortality = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Record %r>' % self.Record  
             
#管理员界面
@app.route('/')
def show_all():
    return render_template('admin.html',Record = Record.query.all() )

#管理员更新数据界面
@app.route('/admin', methods = ['GET', 'POST'])
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
            db.session.add(record)
            db.session.commit()
            
            flash('Record was successfully added')
            return redirect(url_for('data page.html'))
    return render_template('admin.html')

    
# 用户请求进入数据展示界面
@app.route('/login', methods=['GET', 'POST'])
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

#数据展示界面
@app.route('/data')
def index():
    print(session.get('user'))
    return render_template('data page.html')

#向前端发送json数据
@app.route('/uplord',methods=['POST'])
def uplord():
    return jsonify(provinceset)

#查询数据库
if __name__ == "__main__":
    app.run()
    app.run(debug=True)
    db.drop_all()
    db.create_all()
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "Yang654321", "test")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
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
    # db.close()    
