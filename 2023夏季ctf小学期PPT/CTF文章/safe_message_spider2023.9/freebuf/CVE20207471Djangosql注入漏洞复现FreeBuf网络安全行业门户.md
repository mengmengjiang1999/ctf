## 0x00简介

Django 是一个由 Python 编写的一个开放源代码的 Web 应用框架。

使用 Django，只要很少的代码，Python 的程序开发人员就可以轻松地完成一个正式网站所需要的大部分内容，并进一步开发出全功能的 Web 服务
Django 本身基于 MVC 模型，即 Model（模型）+ View（视图）+ Controller（控制器）设计模式，MVC
模式使后续对程序的修改和扩展简化，并且使程序某一部分的重复利用成为可能。

## 0x01漏洞概述

攻击者可通过构造分隔符传递给聚合函数contrib.postgres.aggregates.StringAgg，从而绕过转义符号（\）并注入恶意SQL语句。

## 0x02影响范围

Django 1.11.x < 1.11.28

Django 2.2.x < 2.2.10

Django 3.0.x < 3.0.3

Django 主开发分支

不受影响范围：

Django 1.11.28

Django 2.2.10

Django 3.0.3

## 0x03环境搭建

1.使用kali搭建django 漏洞版本使用版本为3.0.2

pip3 install django==3.0.2

![](https://image.3001.net/images/20201126/1606382576_5fbf73f002f2aeaa303d1.png!small)

2\. 安装postgres 数据库，由于kali自带了postgres数据库，这里直接启动

systemctl start postgresql

![](https://image.3001.net/images/20201126/1606382588_5fbf73fc08805f86ffac8.png!small)

3.使用命令sudo -i -u postgres进入postgres账户，然后输入psql进入数据库，并创建测试数据库test。CREATE
DATABASE test;

![](https://image.3001.net/images/20201126/1606382598_5fbf7406e071a2aace437.png!small)

4.修改数据库密码，ALTER USER postgres WITH PASSWORD 'root';

![](https://image.3001.net/images/20201126/1606382608_5fbf741003953cc5e737a.png!small)

## 0x04漏洞复现

1.这里使用poc来进行实验，下载poc到本地

    
    
    git clone https://github.com/Saferman/CVE-2020-7471.git

![](https://image.3001.net/images/20201126/1606382615_5fbf74177ca5af3b1934a.png!small)

2.然后进入到CVE-2020-7471/sqlvul_projects/settings.py，修改数据库配置，如果之前安装postgres数据库使用的默认配置（包括密码），这里就不需修改任何任何配置

![](https://image.3001.net/images/20201126/1606382622_5fbf741e100d0995573eb.png!small)

3\. 修改完成后回到上层，然后利用CVE中的代码初始化测试数据库test中的表

    
    
    python3 manage.py migrate
    python3 manage.py makemigrations vul_app
    python3 manage.py migrate vul_app

![](https://image.3001.net/images/20201126/1606382629_5fbf7425cbd3fa5286cb9.png!small)

运行没有改变数据没关系，初始化环境完成

![](https://image.3001.net/images/20201126/1606382644_5fbf7434256036bd1d85d.png!small)

4.进test数据库查看数据表

    
    
    \c test //进入test数据库
    \d 查看全部表

查看vul_app_info表的信息

    
    
    select * from vul_app_info;

![](https://image.3001.net/images/20201126/1606382658_5fbf74420f41a8143e804.png!small)

5.没有插入数据没没关系，使用vim 查看CVE-2020-7471.py里内容

    
    
    vim CVE-2020-7471.py

![](https://image.3001.net/images/20201126/1606382672_5fbf745090ccb4e6daee1.png!small)

6.执行poc向数据库插入数据

    
    
    python3 CVE-2020-7471.py

![](https://image.3001.net/images/20201126/1606382688_5fbf746080ebfd1ed398e.png!small)可以看到POC里面的数据写入到数据库中，注入成功

## 0x05修复方式

升级到Django最新版3.0.3

参考链接: <https://zhuanlan.zhihu.com/p/133352594>

免责申明： 本项目仅进行信息搜集，漏洞探测工作，无漏洞利用、攻击性行为，发文初衷为仅为方便安全人员对授权项目完成测试工作和学习交流使用。
请使用者遵守当地相关法律，勿用于非授权测试，勿用于非授权测试，勿用于非授权测试~~（重要的事情说三遍）~~，如作他用所承受的法律责任一概与东塔网络安全学院无关！！！

