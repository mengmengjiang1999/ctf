## **前言**

最近在看CNVD时无意间看到两条关于Django的最新漏洞通告，随即打开看了一下，大概意思是说Django在2.2.28
版本之前的2.2版本、3.2.13版本之前的3.2版本、4.0.4版本之前的4.0版，本使用QuerySet.annotate() aggregate()
extra()数据聚合函数时会导致SQL注入问题。由于笔者平时开发一些平台多半也是使用Django，所以便尝试进行分析了一下，如有描述不当之处，还望提出建议修改斧正。

##  **影响版本**

> Django Django >=2.2，<2.2.28  
> Django Django >=3.2，<3.2.13  
> Django Django >=4.0，<4.0.4

##  **环境构建**

> Python: 3.7.9  
> Django: 3.2.11

##  **目录结构**

![202205120958058031.png](https://image.3001.net/images/20220512/1652323123_627c73333ed37c462dade.png!small)

 **models.py**

> from django.db import models  
> ​  
> # Create your models here.  
> class User(models.Model):  
> name = models.CharField(max_length=200)  
> ​  
> def __str__(self):  
> return self.name

 **views.py**

> import datetime  
> ​  
> from django.db.models import Count  
> from django.http import HttpResponse  
> ​  
> # Create your views here.  
> from demo.models import User  
> ​  
> def loadexampledata(request):  
> u = User(name="Admin")  
> u.save()  
> u = User(name="Staff1")  
> u.save()  
> u = User(name="Staff12")  
> u.save()  
> return HttpResponse("ok")  
> ​  
> def users(request):  
> field = request.GET.get('field', 'name')  
> user_amount = User.objects.annotate(**{field: Count("name")})  
> html = ""  
> for u in user_amount:  
> html += "<h3>Amoount of users: {0}</h3>".format(u)  
> return HttpResponse(html)

 **urls.py**

> from django.contrib import admin  
> from django.urls import path  
> ​  
> from demo import views  
> ​  
> urlpatterns = [  
> path('', views.loadexampledata),  
> path('demo/', views.users)  
> ]

 **settings.py**

> INSTALLED_APPS = [  
> 'django.contrib.admin',  
> 'django.contrib.auth',  
> 'django.contrib.contenttypes',  
> 'django.contrib.sessions',  
> 'django.contrib.messages',  
> 'django.contrib.staticfiles',  
> 'demo.apps.DemoConfig' # 新增  
> ]

或者使用笔者构建好的环境：

<https://github.com/DeEpinGh0st/CVE-2022-28346>

##  **漏洞复现**

 **初始化项目**

> 1.python manage.py makemigrations  
> 2.python manage.py migrate  
> 3.访问http://x.x.x.x:8000/ 初始化数据

 **触发**

> 访问  
> http://x.x.x.x:8000/demo?field=demo.name" FROM "demo_user" union SELECT
> "1",sqlite_version(),"3" --
![202205121000361656.png](https://image.3001.net/images/20220512/1652323123_627c7333ba73e0a293e3e.png!small)

##  **漏洞分析**

老规矩,分析前可以先看看官方在修复的commit中有没有给出测试用例

在https://github.com/django/django/commit/2044dac5c6968441be6f534c4139bcf48c5c7e48中看到官方在测试组件中给出了基本的测试用例。

![202205121001431388.png](https://image.3001.net/images/20220512/1652323124_627c73342d01336be5c1a.png!small)

我们可以根据官方给出的代码编写相应的代码进行调试和分析。

在views.py的annotate打入断点后，来到db.models.query.py:__init__，进行QuerySet的初始化。

![202205121002084945.png](https://image.3001.net/images/20220512/1652323124_627c73348a2bd76126928.png!small)

在初始化QuerySet后，会来到db.models.query.py:annotate开始执行聚合流程，在annotate中首先会调用_annotate并传入kwargs。

![202205121003338232.png](https://image.3001.net/images/20220512/1652323125_627c7335159d67e08e574.png!small)

annotate在完成对kwargs.values()合法性校验等一系列操作后,将kwargs更新到annotations中,随后遍历annotations中的元素调用add_annotation进行数据聚合。

![202205121003534432.png](https://image.3001.net/images/20220512/1652323125_627c73357796d0e2c48e8.png!small)

跟进add_annotation **(print是笔者为了分析自己加入的)。**

![202205121004186482.png](https://image.3001.net/images/20220512/1652323126_627c73363cbd264aec0e2.png!small)

add_annotation继续调用resolve_expression解析表达式,在此处并没有对传入的聚合参数进行相应的检查。在经过一系列调用后,最终会来到db.models.sql.query.py:resolve_ref

resolve_ref会获取annotations中的元素,并将其转换后带入到查询的条件中，最后其结果通过transform_function聚合到一个Col对象中，可以看到聚合之后的结果。

![202205121005054073.png](https://image.3001.net/images/20220512/1652323126_627c7336a6c901d704164.png!small)

返回到db.models.query.py:_annotate可以看到具体聚合后数据值，以及执行的sql语句。

![202205121005262305.png](https://image.3001.net/images/20220512/1652323127_627c733743d6fac738b5b.png!small)

最后将结果返回到QuerySet中进行展示。

![202205121005489899.png](https://image.3001.net/images/20220512/1652323127_627c7337cacc4c6c2f543.png!small)

##  **修复**

在漏洞公开后，Django官方随即对项目进行了修复。

![202205121006137910.png](https://image.3001.net/images/20220512/1652323128_627c73384d3571749cec0.png!small)

在add_annotation中加入了check_alias对聚合参数进行检查。

##  **参考**

<https://github.com/django/django/commit/2044dac5c6968441be6f534c4139bcf48c5c7e48>

<https://www.cnvd.org.cn/flaw/show/CNVD-2022-31838>

