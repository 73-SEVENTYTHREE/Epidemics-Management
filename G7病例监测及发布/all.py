from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
from sqlalchemy import func
import os
import user

app = Flask(__name__)
app.register_blueprint(user.bp)

bp = Blueprint('user', __name__, url_prefix='user')
bp.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Yang654321@127.0.0.1/test'
db = SQLAlchemy(bp)
bp.secret_key = '!@#$%^&*()11'

class Record(db.Model):
    __tablename__ = 'records'
    Date = db.Column(db.Date, primary_key = True)
    Region = db.Column(db.String(64), primary_key = True)
    Cure = db.Column(db.Integer)
    Comfirm = db.Column(db.Integer)
    Import = db.Column(db.Integer)
    Asymptomatic = db.Column(db.Interger)
    Mortality = db.Column(db.Integer)

    def __repr__(self):
        return '<Record %r>' % self.Record  
        
if __name__ == '__main__':
        db.drop_all()
        db.create_all()

#管理员界面
@bp.route('/')
def show_all():
   return render_template('admin.html',Record = Record.query.all() )

#管理员更新数据界面
@bp.route('/admin', methods = ['GET', 'POST'])
def admin():
   if request.method == 'POST':
      if not request.form['Date']  or not request.form['Cure'] or not request.form['Confirm'] or not request.form['Import'] or not request.form['Asymptomatic'] or not request.form['Mortality']:
         flash('Please enter all the fields', 'error')
      else:
         Record = Record(request.form['Date'], request.form['Cure'],request.form['Confirm'],
                         request.form['Import'], request.form['Asymptomatic'], request.form['Mortality'])
         
         db.session.add(Record)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('data page'))
   return render_template('admin.html')

    
# 用户请求进入数据展示界面
@bp.route('/login', methods=['GET', 'POST'])
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
@bp.route('/data')
def index():
    print(session.get('user'))
    return render_template('data.html')


#向前端发送json数据
@bp.route('/sendjson',methods=['POST'])
def sendjson():
    class alldata(object):
    def __init__(self):
        self.ver = {}
        import pymysql
        # 打开数据库连接
        db = pymysql.connect("localhost", "root", "Yang654321", "test")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # SQL 查询语句
        sql = "SELECT * FROM Record ORDER BY Region,Date"
        try:
        # 执行SQL语句
            cursor.execute(sql)
            result = cursor.fetchone()
            while result != None:
                var1 = Record.Region
                if(var1 == var2):
                    test = alldata()
                    test.ver = {'province' : Record.Region, 'data' = []}
                    dict = {'date':Record.Date,'diagnosed':Record.Confirm,'imported':Record.Import,'asymptomatic':Record.Asymptomatic,'cured':Record.Cure,'dead':Record.Mortality}
                    data.append(dict)
                    result = cursor.fetchone()
                else:
                    return jsonify(test.ver)
                    test = alldata()
                    test.ver = {'province' : Record.Region, 'data' = []}
                    dict = {'date':Record.Date,'diagnosed':Record.Confirm,'imported':Record.Import,'asymptomatic':Record.Asymptomatic,'cured':Record.Cure,'dead':Record.Mortality}
                    data.append(dict)
                    result = cursor.fetchone()
                var2 = Record.Region
         # 关闭数据库连接
         db.close()

         
if __name__ == "__main__":
    bp.run()
    bp.run(debug=True)
