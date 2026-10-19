## 0x00 前言

 **Rainmap Lite 是一款Nmap对应Web应用程序，它允许用户从他们的手机/平板电脑/网络浏览器启动Nmap扫描！不像它的前身[1]
，Rainmap Lite 并不依赖特殊服务（RabbitMQ，PostgreSQL，Celery，
supervisor等），它可以很容易地安装在任何服务器上。你只需要安装Django应用程序，并添加cron的轮询任务，便可以建立一个新的扫描服务器。
Nmap扫描已准备好给大家！**

【[1] Rainmap - <https://nmap.org/rainmap/>】

## 0x01 工作原理

Django应用把Nmap命令储存在SQLite[数据库](http://lib.csdn.net/base/mysql)来执行。另一脚本读取数据库中的命令和按照用户定义的配置来定期执行它们。需要访问SMTP服务器来，通过电子邮件发送报告（Gmail是可以的）。

### 1Rainmap Lite 特征

> 点击几下即可轻松启动Nmap扫描
>
> Web界面平稳运行于手机/平板电脑
>
> 通过各种电子邮件发送扫描报告
>
> 从Web浏览器查看报告
>
> 预设扫描
>
> 几十个可供选择的扫描配置文件
>
> 易于安装/建立
>
> 分享与你的团队结果
>
>  
>

### 2 用扫描配置文件

> 基本扫描：--script bacnet-info -sU -p47808
>
> 广播扫描：-sn --script broadcast
>
> DDOS反向UDP扫描：–sU –A –PN –n –pU:19,53,123,161 --script=ntp-monlist,dns-> recursion,snmp-sysdescr
>
> DDOS Slowloris检查扫描：–p- -sV --script=http-slowloris-check
>
> DNS枚举扫描：-sn --script dns-brute
>
>
> ..............................................................................（此处还有更多扫描配置，省略）

## 0x02 安装

### 1 基本环境搭建

  

  

`pip install Django #安装Django 环境，建议安装1.9版本`

``

`pip install lxml #安装lxml，[Python](http://lib.csdn.net/base/python)实现高性能 XML
解析`

``

  

  

### 2 下载文件

【浏览器下载】<https://github.com/ym2011/penetration/tree/master/rainmap-lite>

### 3 更改配置

在【rainmap-lite/nmaper-cronjob.py】更新BASE_URL, SMTP_USER, SMTP_PASS, SMTP_SERVER
and SMTP_PORT这些配置信息，以此来接收email 警告。

### 4 创建数据库模式

  

    
    
    python manage.py migrate 

  

### 5 加载默认的扫描配置

  

    
    
    python manage.py loaddata nmapprofiles

  

### 6 添加定时任务

  

`命令格式：`

``

`*/5 * * * * cd <App path> && /usr/bin/python nmaper-cronjob.py >>
/var/log/nmaper.log 2>&1`

``

`示例1：`

``

`*/5 * * * * cd /root/rainmap-lite && /usr/bin/python nmaper-cronjob.py >>
/var/log/nmaper.log 2>&1`

``

  

### 7 运行程序

  

    
    
    python manage.py runserver 0.0.0.0:8001

  

### 8 添加管理员

  

    
    
    python manage.py createsuperuser

  

### 9 打开流量

<http://127.0.0.1:8001/console/>

#输入刚刚设置的用户名/密码，进行管理和扫描

## 0x03 使用

### 1 基本扫描

首先我们可以选择一个目标网站或者IP地址，输入后，选择【Profile】中的扫描选项后，即可启动扫描。

![rainmap-lite-1.png](https://image.3001.net/images/20161003/14754470397835.png!small)

### 2 可用的扫描配置

![rainmap-lite-3.png](https://image.3001.net/images/20161003/14754470687836.png!small)

### 3 Nmap的web 管理

![rainmap-lite-4.png](https://image.3001.net/images/20161003/14754470745246.png!small)

### 4 增加自定义扫描配置

![rainmap-lite-5.png](https://image.3001.net/images/20161003/14754470808603.png!small)

![rainmap-lite-6.png](https://image.3001.net/images/20161003/14754470885246.png!small)

### 5 邮件通知

![rainmap-lite-7.png](https://image.3001.net/images/20161003/14754471006958.png!small)

## 0x04 参考资料

<https://github.com/ym2011>

<https://nmap.org/rainmap/>

<https://nmap.org/book/man.html>

<https://nmap.org/nsedoc/>

 ***本文原创作者：ymmy，本文属FreeBuf原创奖励计划，未经许可禁止转载 。**

