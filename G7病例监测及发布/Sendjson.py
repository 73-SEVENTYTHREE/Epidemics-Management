from  flask import Flask
app = Flask(__name__)

@app.route('/sendjson',methods=['POST'])
def sendjson():

# 接收前端发来的数据,转化为Json格式,我个人理解就是Python里面的字典格式
data = json.loads(request.get_data())

# 然后在本地对数据进行处理,再返回给前端
province = data["province"]
date = data["date"]
diagnosed = data["diagnosed"]
imported = data["imported"]
asymptomatic = data["asymptomatic"]
cured = data["cured"]
dead = data["dead"]

# Output: {u'province': u'浙江', u'date': u'03-01', u'diagnosed': u'100' , u'imported':u'10' , u'asymptomatic':u'15' , u'cured':u'5' , u'dead':u'1'}
# print data
return jsonify(data)

if __name__ == '__main__':
    app.run()
