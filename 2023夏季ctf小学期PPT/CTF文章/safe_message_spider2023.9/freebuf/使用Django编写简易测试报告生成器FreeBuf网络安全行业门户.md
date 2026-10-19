***本文原创作者：海带头，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 概述

**安全测试人员在工作的时候，不单单需要发现问题，还需要花费精力去撰写安全测试报告来记录结果。为了方便，我利用django框架写了个简易的安全测试报告撰写系统。**

![image.png](https://image.3001.net/images/20180327/15221461638119.png!small)

撰写报告的时候，需要写明漏洞名称、漏洞风险等很多项目内容。对于某一类型漏洞而言，其实有很多项在大多数情况是固定不变的（比如漏洞名称、修复建议）。我们可以在编写漏洞的时候直接调用漏洞模板，再添加和修改需要记录的数据，最终一键导出我们设计好的模板。

## 配置和安装环境

> Django-1.10.8
>
> python2.7
>
> Wndows/Mac

## 安装

    
    
    python –m pip install –r requirements.txt

### 说明

Mac下安装mysql以及MySQL-python

    
    
    brew install mysql
    
    pip install MySQL-python

如果第二条安装出现"Failed building wheel for mysql-python"错误，则采用以下方法

    
    
    LDFLAGS=-L/usr/local/opt/openssl/lib pip install mysql-python

## 启动服务

### 建库

本地mysql需要新建配置文件中的数据库settings.py文件：

    
    
    DATABASES ={
     'default':{ 'ENGINE':'django.db.backends.mysql', 'HOST':'127.0.0.1', 'PORT':'3306', 'NAME':'bugwrite', # 数据库名 'USER':'root', 'PASSWORD':'root', 'OPTIONS':{ 'init_command':"SET sql_mode='STRICT_TRANS_TABLES'" }, }
    }
    

### 建表

    
    
    cd myweb01
    
    python manage.py makemigrations
    
    python manage.py migrate

### 启服务

    
    
    python manage.py runserver

## 功能描述

启动本地服务后，访问<http://localhost:8000/blog/work>可以在本地新建一个项目，如下图所示：

![image.png](https://image.3001.net/images/20180327/15221461803267.png!small)

点开项目详情，可以在其中创建漏洞，并且可以引用不同的漏洞模板：

![image.png](https://image.3001.net/images/20180327/15221463411705.png!small)

点击新建XSS漏洞后，XSS漏洞名称、风险分析、风险等级、修复建议会自动填充，只需要填写记录测试过程即可：

![image.png](https://image.3001.net/images/20180327/15221463599571.png!small)

回到之前创建的项目，可以导出报告：

![image.png](https://image.3001.net/images/20180327/15221463715806.png!small)![image.png](https://image.3001.net/images/20180327/15221463766690.png!small)

实现了漏洞管理

## 扩展和说明

### 漏洞模板创建

models.py文件中创建了BugModel类作为漏洞模板，并添加到admin中，在django的管理后台可以添加模板，访问<http://localhost:8000/admin>
，编辑BugModel即可：

![image.png](https://image.3001.net/images/20180327/15221464082989.png!small)

然后在views.py中编辑form表单SelectTestFrom，添加模板选择项：

![image.png](https://image.3001.net/images/20180327/15221464131420.png!small)

### Word模板扩展

漏洞详情的使用ckeditor获取用户输入，提交的数据类型为html格式，我这边自己写了一个解析html数据的类Html2Word，处理了p/ul/ol/strong/em/img便签，为防止数据丢失，建议编辑器只用加粗、斜体、图片、序标的格式：html2word.py

![image.png](https://image.3001.net/images/20180327/15221464373420.png!small)

下面是将漏洞字段填充到word中，如果有需要丰富生成的word模板，可以修改下面的内容：Object2word.py

![image.png](https://image.3001.net/images/20180327/15221464435490.png!small)

## 附件

源码已经上传至github：<https://github.com/Gin-Cy/bugeditor.git>

 ***本文原创作者：海带头，本文属FreeBuf原创奖励计划，未经许可禁止转载**

