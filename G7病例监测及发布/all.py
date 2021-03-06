# 程序的主入口

from flask import Flask
import os

def create_app(test_config=None):
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@120.55.44.111:3306/records'
    app.secret_key = '!@#$%^&*()11'

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 注册各子系统的蓝图
    import situation
    app.register_blueprint(situation.situation_bp, url_prefix='/situation')

    # 疫情数据子系统：初始化子系统的数据。
    situation.initSituation()

    return app

if __name__ == "__main__":
    app = create_app()
