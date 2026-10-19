## 漏洞描述

Django 组件存在 SQL 注入漏洞，该漏洞是由于对
QuerySet.order_by()中用户提供数据的过滤不足，攻击者可利用该漏洞在未授权的情况下，构造恶意数据执行 SQL
注入攻击，最终造成服务器敏感信息泄露。

### 组件介绍

Django是一个开放源代码的Web应用框架，由Python写成。采用了MVC的框架模式，即模型M，视图V和控制器C。它最初是被开发来用于管理劳伦斯出版集团旗下的一些以新闻内容为主的网站的，即是CMS（内容管理系统）软件。

### 利用条件

1、用户认证：不需要用户认证 2、触发方式：远程

综合评价

高危，最终造成服务器敏感信息泄露

影响版本

Django 3.2  
Django 3.1

安全版本

Django >= 3.2.5  
Django >= 3.1.13

### 漏洞复现

搭建环境

https://github.com/YouGina/CVE-2021-35042

运行（这里为了方便可以提前切换到root用户）

git clone https://github.com/YouGina/CVE-2021-35042.git  
cd CVE-2021-35042

![image-20210802231815633](https://image.3001.net/images/20210803/1627973586_6108e7d222615b8eeb22e.png!small)

初始设置

./setup.sh #./setup.sh执行之后，docker开启的是数据库服务器

![image-20210803132720257.png](https://image.3001.net/images/20210803/1627973587_6108e7d35e2ea00de1841.png!small)

在这一步运行过程中会出现下面这个错误，这个意思是不要以root用户执行，以普通用户即可，不用理会这个报错；

![image-20210803132837868](https://image.3001.net/images/20210803/1627973588_6108e7d4c1d854a073dae.png!small)

此时数据库服务已经开启

![image-20210803133414746](https://image.3001.net/images/20210803/1627973589_6108e7d5ea0bb555a0969.png!small)

接着把web服务也开启

docker-compose up -d #此时web服务器和数据库服务器均开启

![image-20210803133557896.png](https://image.3001.net/images/20210803/1627973590_6108e7d6c8fc45034ccef.png!small)

进入web服务容器中

docker exec -it {container_id} /bin/bash #进入web服务器

![image-20210803133704686](https://image.3001.net/images/20210803/1627973595_6108e7db3d3fa96c80c1e.png!small)

执行下面这两条命令

python manage.py makemigrations cve202135042

红线框中表示在cve202135042应用目录下的migations的文件下多了一个0001_initial.py的文件,查看这个文件内容，表示我们创建了一个User这个模型类，并且指出这个类的成员属性id,name,以及他们的属性，同时我们了解到djnago在models.py创建模型类，其中一个模型类对应的是一张数据表，但是该命令并没有作用到数据库，这个命令中python
manage.py
makemigrations是记录我们对models.py的所有改动，并且将这个改动迁移到migrations这个文件下生成一个文件0001_initial.py。

![image-20210803134349702](https://image.3001.net/images/20210803/1627973596_6108e7dc854cae3d8930e.png!small)

接着执行下面这条命令，
这条命令的主要作用就是把上一条的改动作用到数据库也就是执行migrations里面新改动的迁移文件来更新数据库，比如创建数据表，或者增加字段属性

python manage.py migrate

![image-20210803135349050](https://image.3001.net/images/20210803/1627973598_6108e7de1b95c4392127c.png!small)

打开以下 URL 以加载示例数据：

http://localhost:8000/load_example_data

![image-20210803140014375.png](https://image.3001.net/images/20210803/1627973599_6108e7df78aad99845c4a.png!small)

然后转到易受攻击的页面

http://localhost:8000/users/

![image-20210803135809936](https://image.3001.net/images/20210803/1627973600_6108e7e033bc88554cb92.png!small)

![image-20210803140001935.png](https://image.3001.net/images/20210803/1627973600_6108e7e0de7e5bc77ec48.png!small)

## 漏洞防御

及时更新到最新版本

链接 : <https://www.djangoproject.com/weblog/2021/jul/01/security-releases/>

这个漏洞复现因为网络环境问题卡了好久，这里感谢zly师兄的指点，这家伙搭环境比我快多了>_<

