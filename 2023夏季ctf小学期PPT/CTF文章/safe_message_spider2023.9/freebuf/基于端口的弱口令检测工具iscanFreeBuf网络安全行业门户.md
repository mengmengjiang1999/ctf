# iscan: 基于端口的弱口令检测工具

亲手打造了一款基于端口的弱口令检测工具，使用python进行编写，主要可以用于渗透测试中常见服务端口弱口令的检测。目前支持以下服务：

系统弱口令：ftp、ssh、telnet、ipc$

数据库弱口令：mssql、mysql、postgre、mongodb

中间件弱口令：phpmyadmin、tomcat、weblogic

![1.png](https://image.3001.net/images/20180713/15314673158315.png!small)

## 特点

  * 命令行,兼容OSX/LINUX/WINDOWS/Python 2.7

  * 内置弱口令字典，同时支持外部导入执行

  * 支持多线程、线程可调控

  * 支持中间件弱口令扫描

## 基本使用

### 1、地址格式

-h ：指定ip地址，ip地址支持以下格式：

支持单个ip，如 `iscan.py -h 10.9.10.201 --ssh`

支持多个ip，如 `iscan.py -h 10.9.10.201-10.9.10.205 --ssh //201-205 5个ip` `iscan.py
-h 10.9.10.201,10.9.10.205 --ssh //201、205 2个ip`

网段地址，如 `iscan.py -h 10.9.10.0/24 --ssh // 识别24结束的网段`

文本导入，如 `iscan.py -h 1.txt --ssh //导入1.txt，每行一个ip地址`

### 2、支持的弱口令类型

系统弱口令：ftp、ssh、telnet、ipc$数据库弱口令：mssql、mysql、postgresql、mongodb中间件弱口令：phpmyadmin、tomcat、weblogic

指定mysql进行弱口令检测：`iscan.exe -h 10.9.10.201 --mysql`

### 3、导入字典进行猜解

iscan默认已内置常见的弱口令，也可以从外部导入字典进行猜解

`iscan.py -h 10.9.10.201 -u user.txt -s pwd.txt --ssh`

-u: 指定用户字典-p：指定密码字典

### 4、可以指定端口，设置线程数

iscan支持指定端口、支持多线程

例如：

`iscan.py -h 10.9.10.201 -p 2222 -t 20 --ssh`

以20线程数，指定2222端口扫描ssh弱口令

-p：指定端口 -t：设置线程数

### 5、日志记录

在本目录下生成result.log日志记录扫描结果

# 测试截图

ipc$检测：

![2.png](https://image.3001.net/images/20180713/15314673316938.png!small)  

Mongodb检测：

  
![3.png](https://image.3001.net/images/20180713/15314673464120.png!small)  

PS：海峡信息白帽子id:Bypass 两年前写的工具，最后在2017年3月更新过一次，就一直遗忘在角落了。最近在整理以前的博客，又重新拾回了代码。

代码有攻击性，防止被恶意使用，就不放出来了，代码实现很简单，有时间的话，准备写一个系列：《手把手教你打造自己的弱口令扫描工具》。

![TIM图片20180713152618.gif](https://image.3001.net/images/20180713/1531467403525.gif!small)

