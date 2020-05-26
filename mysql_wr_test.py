#!/usr/sbin/python
# Author: hexh
# Contact: 1282037943
# Date: 20200526

import pymysql
import random

class mysqlHelper():
    def __init__(self, host, port, user, password, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname

    def executesql(self,sqlstr):
        try:
            db = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.dbname)
            cursor = db.cursor()
            cursor.execute(sqlstr)
            db.commit()
        except Exception as e:
            print("execute error! {0}".format(e))
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    mh = mysqlHelper('192.168.0.33', 1234, 'admin', '123456', 'testdb')
    createdatabasesql = "CREATE DATABASE IF NOT EXISTS testdb DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_bin;"
    createtablesql = "create table if not exists student(id int(11) NOT NULL AUTO_INCREMENT primary key,StudentName varchar(20),Age int(10),Address varchar(50))"
    mh.executesql(createdatabasesql)
    mh.executesql(createtablesql)
    # 开始插入数据
    count = 1
    while count < 100000:
        insertsql = "insert into student(id,StudentName,Age,Address)value({0},concat('hexh',{1}),{2},concat('深圳市罗湖区',{3},'号'));".format(count,str(count),random.randint(1,100),str(count))
        mh.executesql(insertsql)
        count = count + 1
