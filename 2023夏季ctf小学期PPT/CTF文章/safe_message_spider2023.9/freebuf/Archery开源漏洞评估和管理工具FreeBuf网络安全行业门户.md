**Archery是一款开源的漏洞评估和管理工具，它可以帮助开发和渗透测试人员执行漏洞扫描及管理漏洞。Archery使用流行的开源工具来执行对Web应用及网络的全面扫描。它还可执行Web应用程序动态验证扫描，并使用selenium覆盖整个应用程序。开发人员也可以使用该工具来实现其DevOps
CI/CD环境。**

**![photo.png](https://image.3001.net/images/20180212/15183973649601.png!small)  
**

 **相关文档**

<https://archerysec.github.io/archerysec/>

[API文档](https://archerysec.github.io/archerysecapi/)

 **Demo**

**![20180212090841.png](https://image.3001.net/images/20180212/15183977538007.png!small)  
**

 **工具概述**

  * 使用开源工具执行Web和网络漏洞扫描。
  * 关联和协作所有原始扫描数据，并最终以合并的方式展示它们。
  * 执行Web应用程序验证扫描。
  * 使用selenium执行Web应用程序扫描。
  * 漏洞管理。
  * 支持通过REST API来执行扫描和漏洞管理。
  * 适用于DevOps团队的漏洞管理。

 **注意**

当前该项目正处于开发阶段，还有很多工作正在进行中。

 **环境需求**

  * Python 2.7
  * OpenVas 8
  * [OWASP ZAP 2.7.0](https://github.com/zaproxy/zaproxy/wiki/Downloads)
  * [Selenium Python Firefox Web驱动](https://github.com/mozilla/geckodriver/releases)

 **Burp扫描器**

可按照以下说明文档，启用Burp REST API。启用REST API后，你可以使用Archery管理和触发扫描。

  * [Burp REST API](https://github.com/vmware/burp-rest-api)

 **安装**

    
    
    $ git clone https://github.com/archerysec/archerysec.git
    $ cd archerysec
    $ pip install -r requirements.txt
    $ python manage.py collectstatic
    $ python manage.py makemigrations networkscanners
    $ python manage.py makemigrations webscanners
    $ python manage.py makemigrations projects
    $ python manage.py makemigrations APIScan
    $ python manage.py migrate
    $ python manage.py createsuperuser
    $ python manage.py runserver

注意：请确保在每次git pull之后执行这些步骤（除了createsuperuser）。

 **设置**

Zap设置

  1. 转到设置页
  2. 编辑ZAP设置或导航到URL：<http://host:port/setting_edit/>
  3. 填写所有必填信息并点击保存。

OpenVAS设置

  1. 转到设置页
  2. 编辑OpenVAS设置或导航到URL：<http://host:port/networkscanners/> openvas_setting
  3. 填写所有必填信息并点击保存。

 **路线图**

  * API自动漏洞扫描。
  * 扫描前执行侦察。
  * 并发扫描。
  * 漏洞POC图片。
  * 云安全扫描。
  * 仪表盘。
  * 易于安装。

 **首席开发人员**

Anand Tiwari - <https://github.com/anandtiwarics>

**联系我们**

  * [官方网站](https://archerysec.github.io/archerysec/)
  * [Twitter](https://twitter.com/archerysec)
  * [Facebook](https://facebook.com/archerysec)

 ***参考来源：[GitHub](https://github.com/archerysec/archerysec)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

