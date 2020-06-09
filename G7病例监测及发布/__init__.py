from flask import Flask, request, url_for, redirect, render_template, session
from flask import Blueprint
import os
import user

app = Flask(__name__)
app.register_blueprint(user.bp)
app.register_blueprint(update.bp)
app.register_blueprint(send.bp)

bp = Blueprint('user', __name__, url_prefix='user')

bp.secret_key = '!@#$%^&*()11'

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

@bp.route('/index')
def index():
    print(session.get('user'))
    return render_template('index.html')


if __name__ == "__main__":
    bp.run(host='0.0.0.0', port=9000, debug=True)
