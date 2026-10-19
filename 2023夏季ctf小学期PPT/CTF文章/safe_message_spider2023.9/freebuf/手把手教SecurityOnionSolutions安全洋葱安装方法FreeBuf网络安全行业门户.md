## **securityonion安全洋葱介绍**

安全洋葱是一款开源的入侵检测系统、集成了日志分析、流量分析安全告警如：Grafana、TheHive、Playbook、 Fleet /
Osquery、Winlogbeat，集众多安全软件工具为一身的开源流量分析平台。

Securityonion的部署方式

![](https://image.3001.net/images/20200829/1598714358.png!small)

配置文档

<https://docs.securityonion.net/en/2.0/getting-started.html>

securityonion-2.1.0-rc2基于DOCKER环境搭建、如果DOCKER命令不熟悉可以跳转到我的第一篇文章中查看DOCKER的扩展命令、后续我们会经常用到

下载地址

<https://download.securityonion.net/file/securityonion/securityonion-2.1.0-rc2.iso>

虚拟机配置要求：

系统Centos7 64位 、磁盘200G、内存最少12G、CPU4核

##  **开始安装**

新建虚拟机

![](https://image.3001.net/images/20200829/1598714417.png!small)

稍后安装操作系统

![](https://image.3001.net/images/20200829/1598714465.png!small)

选择centos7 64位

![](https://image.3001.net/images/20200829/1598714499.png!small)

虚拟机名称和存放的位置

![](https://image.3001.net/images/20200829/1598714529.png!small)

硬盘建议200G

![](https://image.3001.net/images/20200829/1598714559.png!small)

点击完成 即可创建虚拟机

![](https://image.3001.net/images/20200829/1598714598.png!small)

点击编辑虚拟机

![](https://image.3001.net/images/20200829/1598714625.png!small)

内存设置8G

![](https://image.3001.net/images/20200829/1598714655.png!small)

CPU设置4核

![](https://image.3001.net/images/20200829/1598714680.png!small)

添加一快网卡

![](https://image.3001.net/images/20200829/1598714704.png!small)

两快网卡都使用桥接模式

![](https://image.3001.net/images/20200829/1598714732.png!small)

最后选择下载好的镜像点击确定即可

![](https://image.3001.net/images/20200829/1598714766.png!small)

开启虚拟机、直接选择安装安全洋葱

![](https://image.3001.net/images/20200829/1598714793.png!small)直接回车

![](https://image.3001.net/images/20200829/1598714822.png!small)

输入yes、之后创建安全洋葱系统账号，我这里创建的账号密码为:onion/admin123

![](https://image.3001.net/images/20200829/1598714852.png!small)

回车后静静等待安装、安装的快慢取决于你电脑的配置，反正我安装了半小时....

![](https://image.3001.net/images/20200829/1598714889.png!small)

安装系统镜像结束、按回车重启系统

![](https://image.3001.net/images/20200829/1598714925.png!small)

重启后会让你输入账号密码、此账号密码就是刚刚安装时创建的onion/admin123

![](https://image.3001.net/images/20200829/1598715014.png!small)

选择安装类型、按上下来切换、空格选中、tab切换到OK或者Cancel

![](https://image.3001.net/images/20200829/1598715057.png!small)

设置主机名

![](https://image.3001.net/images/20200829/1598715116.png!small)

选择管理网卡、这里我们选择ens33为管理网卡、ens34为镜像口

![](https://image.3001.net/images/20200829/1598715181.png!small)

设置静态IP

![](https://image.3001.net/images/20200829/1598715225.png!small)

因为是桥接模式需要查看本地IP地址、本地IP为192.168.0.4,我们在安全洋葱下配置地址为192.168.0.10

![](https://image.3001.net/images/20200829/1598715343.png!small)

配置静态地址为192.168.0.10

![](https://image.3001.net/images/20200829/1598715372.png!small)

掩码默认24位

![](https://image.3001.net/images/20200829/1598715423.png!small)

设置网关

![](https://image.3001.net/images/20200829/1598715467.png!small)

设置DNS

![](https://image.3001.net/images/20200829/1598715503.png!small)备用DNS

![](https://image.3001.net/images/20200829/1598715538.png!small)![](https://image.3001.net/images/20200829/1598715586.png!small)

创建安全洋葱web登录账号密码、账号必须以邮件格式

![](https://image.3001.net/images/20200829/1598715630.png!small)

创建密码

![](https://image.3001.net/images/20200829/1598715675.png!small)重复密码

![](https://image.3001.net/images/20200829/1598715712.png!small)

界面登录的方法我们选择web登录

![](https://image.3001.net/images/20200829/1598715749.png!small)

选择yes允许so-allow访问web工具、因为安装完成后我们要使用sudo so-allow 来启动web界面

![](https://image.3001.net/images/20200829/1598715784.png!small)

这里IP直接为空、选择OK

![](https://image.3001.net/images/20200829/1598715816.png!small)

点击yes 开始安装

![](https://image.3001.net/images/20200829/1598715837.png!small)

开始安装进度

![](https://image.3001.net/images/20200829/1598715857.png!small)安装完成后重启

![](https://image.3001.net/images/20200829/1598715898.png!small)

使用onion/admin123 登录到系统中、之后使用sudo so-allow
启动服务、密码为admin123，之后选择a回车后输入允许登录安全洋葱的主机地址

![](https://image.3001.net/images/20200829/1598715929.png!small)![](https://image.3001.net/images/20200829/1598715954.png!small)

到此安全洋葱才算真正安装完成。

我们修改下root密码

运行sudo passwd，首次运行需要输入onion密码、输入成功后直接可以设置root密码

![](https://image.3001.net/images/20200829/1598715983.png!small)

设置了root密码后我们可以使用CRT/XSHELL对安全洋葱ssh远程登录、检查下80、443端口是否启动、如果80
443端口并未启动、我们可以在root权限下使用docker start $(docker ps -qa) 来启动所有已挂起的镜像

![](https://image.3001.net/images/20200829/1598716011.png!small)

我们打开浏览器输入https://192.168.0.10,输入我们安装时候创建的web登录账号密码

[admin@qq.com/admin123](mailto:admin@qq.com/admin123)

![](https://image.3001.net/images/20200829/1598716049.png!small)![](https://image.3001.net/images/20200829/1598716070.png!small)![](https://image.3001.net/images/20200829/1598716088.png!small)

Kibana 数据展示界面

![](https://image.3001.net/images/20200829/1598716121.png!small)

Grafana 监控服务器应用运行状态

![](https://image.3001.net/images/20200829/1598716153.png!small)![](https://image.3001.net/images/20200829/1598716164.png!small)

Cyberchef 界面、可以加密解密数据

![](https://image.3001.net/images/20200829/1598716202.png!small)

Fleet 登录账号密码同安全洋葱账号一样 [admin@qq.com/admin123](mailto:admin@qq.com/admin123)

![](https://image.3001.net/images/20200829/1598716230.png!small)

Thehive 登录账号密码同安全洋葱账号一样admin@qq.com/admin123

![](https://image.3001.net/images/20200829/1598716255.png!small)

至此安全洋葱基本已经安装介绍完成、功能也基本完善，要抓取所有流量数据必须做端口镜像、否则抓不到攻击告警的数据流。下篇文章我将介绍如何在不同的设备上做端口镜像、以及Kibana、Fleet
、Thehive的使用方法及流量分析。

 **温馨提示：在虚拟机中安装完成一定要打快照哦.....**

