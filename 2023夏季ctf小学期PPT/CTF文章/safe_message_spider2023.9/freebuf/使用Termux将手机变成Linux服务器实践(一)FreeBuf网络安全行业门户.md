## 背景

最近觉得手机仅仅作为手机去使用 , 这么高的配置岂不是浪费 , 要是把电脑上的工具安装到手机上,岂不是就能随时随地使用, 更加便捷与灵活,
但是手机敲命令着实难受,屏幕太小让人实在不适应,想着如果能用电脑连接手机终端岂不美滋滋。尝试了一番发现操作非常简单。

一台Root手机安装Tremux终端 ,  
一台电脑安装xshell

由于Google play不提供apk安装包，需要大家自己去它的商店下载，  
termux下载地址https://play.google.com/store/apps/details?id=com.termux

xshell破解版  
链接：https://pan.baidu.com/s/1CCKDSslpPGxpWq3PiDqOwQ  
提取码：hxs9

## 一、 安装SSH

安装termux终端前必须root手机，网上很多root jiaocheng  
大家可以自己去找，或者我过几天出一个手机root jiaocheng供大家参考。

### 1.1 安装SSH

手机安装termux，打开后输入安装命令如下所示:

    
    
    pkg install openssh
    

![](https://image.3001.net/images/20210419/1618762886_607c5c8611216b4e0e2d9.jpg!small)

从上图可以看到ssh已经安装成功 , 接下来去启动ssh

### 1.2 启动SSH

启动ssh命令如下所示:

    
    
    sshd
    

![](https://image.3001.net/images/20210419/1618762887_607c5c8787d2f409e9201.png!small)

从上图可以看到已经启动ssh服务 , 接下来去查看终端用户名。

## 二、 获取终端用户名与密码

SSH服务已经安装并启动了，现在我们去获取手机终端的用户名、密码和ip，然后用电脑xshell去连接手机终端

### 2.1 查看终端用户名

查看终端用户名命令如下所示:

    
    
    whoami
    

![](https://image.3001.net/images/20210419/1618762888_607c5c8843130affebe44.png!small)

从上图中可以看到此处的用户名为u0_a249 , 接下来去设置终端密码.

### 2.2 设置终端密码

由于刚安装好的终端是没有密码的，我们可以通过passwd去设置密码。命令如下所示:

    
    
    passwd
    

![](https://image.3001.net/images/20210419/1618762888_607c5c888440f582abe9e.png!small)

从上图可以看到我们设置了终端密码 , 接下来去查看终端ip地址 , 然后通过电脑xshell去连接手机终端

### 2.3 查看终端IP地址

命令如下所示:

    
    
    ifconfig
    

![](https://image.3001.net/images/20210419/1618762888_607c5c88e8dd1fbc76a25.png!small)

从上图可以看到本文的IP地址为192.168.3.255 ，到此我们已经获取到了终端用户名、密码和ip ， 现在用电脑xshell去连接手机

## 三、xshell连接手机终端

如果你有公网服务器那么可以把手机ip映射到公网地址上，本文中就用局域网给大家做演示，保持手机和电脑在同一网段下，我的电脑和手机连的是同一个wifi，所以它们在同一个网段。

### 3.1 xshell连接手机

打开xshell点击新建会话，输入ip和端口，这里要注意的是手机终端的默认连接端口为8022

![](https://image.3001.net/images/20210419/1618762889_607c5c8960df1be540783.png!small)

点击用户身份验证，输入上文中获取到的用户名与密码，点击连接！

![](https://image.3001.net/images/20210419/1618762889_607c5c89b9de699b3b224.png!small)

会弹出SSH安全警告，点击接受并保存。

![](https://image.3001.net/images/20210419/1618762890_607c5c8a2083e6b69a02e.png!small)

### 3.2 连接成功

这样我们就连接到手机终端，可以尽情做一些你想做的事情

![](https://image.3001.net/images/20210419/1618762890_607c5c8a7bfdf2af34656.png!small)

作者：陈婷

日期：2021年4月18日

