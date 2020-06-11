import json
import pymysql
def initialDataV1(db, cursor):
    with open("data.json", 'r', encoding="UTF-8") as f:
        data = json.load(f)
    data = map(lambda x: tuple(x), data)

    # 这句我瞎打的如果有问题你们自己改一下我只是做个示范
    for count in data:
        test=list(count)
        test[1]='2020-'+test[1]
        sql = f"INSERT INTO records \
            VALUES ('{test[0]}', '{test[1]}', {test[2]}, {test[3]}, {test[4]}, {test[5]}, {test[6]})"
        print (sql)
        cursor.execute(sql)
    db.commit()

db= pymysql.connect("127.0.0.1","yourdatabase account","password of the account","databasename")
cursor=db.cursor()
initialDataV1(db, cursor)
db.close()