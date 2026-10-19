***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 一、实验目的

1、在XP系统上搭建Tomcat服务器平台；

2、在另一台虚拟机上利用弱口令漏洞上传木马程序，使得XP系统中木马。

## 二、实验设备及环境

VMWare、XP系统、2003系统

## 三、实验步骤

### 实验内容

1、在XP系统上搭建Tomcat服务器平台；

2、在另一台虚拟机上利用弱口令漏洞上传木马程序，使得XP系统中木马

 ** **搭建**** ** **Tomcat**** ** **服务器平台****

安装JAVA JDK:目的是打包木马

环境变量的配置：

> JAVA_HOME：C:\Program Files\Java\jdk1.7.0_79
>
> Path：%JAVA_HOME%\bin;
>
> CLASSPATH：.%JAVA_HOME%\lib\dt.jar;%JAVA_HOME%\lib\tool.jar;

Window2003:

![](https://image.3001.net/images/20210428/1619612718_6089542e95cfe33da6c29.png!small)

Window xp:

![1619612725_608954356829b26ba37a5.png!small](https://image.3001.net/images/20210428/1619612725_608954356829b26ba37a5.png!small)

![1619612743_608954472c8242039ca73.png!small](https://image.3001.net/images/20210428/1619612743_608954472c8242039ca73.png!small)

Window xp 安装成功

![1619612752_60895450de4a512975b3d.png!small](https://image.3001.net/images/20210428/1619612752_60895450de4a512975b3d.png!small)

Window 2003安装成功

![1619612758_60895456bd8559c828602.png!small](https://image.3001.net/images/20210428/1619612758_60895456bd8559c828602.png!small)

![1619612775_60895467bb7612f57f6ac.png!small](https://image.3001.net/images/20210428/1619612775_60895467bb7612f57f6ac.png!small)![1619612769_608954614371d1607e530.png!small](https://image.3001.net/images/20210428/1619612769_608954614371d1607e530.png!small)

安装Apache-Tomcat服务器

> 将压缩包解压，把整个文件夹拷贝至C盘。（免安装）
>
> 添加环境变量：
>
> TOMCAT_HOME：C:\apache-tomcat-6.0.37
>
> 进入bin目录，点击bat或者shutdown.bat可以启动或关闭服务器。

![1619612819_60895493269ce325d4a3c.png!small](https://image.3001.net/images/20210428/1619612819_60895493269ce325d4a3c.png!small)

成功打开！

点击exe，启动服务器，在浏览器中输入：http://127.0.0.1:8080/，若显示如下界面，则服务器启动成功。

![1619612831_6089549fcd538f783c29f.png!small](https://image.3001.net/images/20210428/1619612831_6089549fcd538f783c29f.png!small)

登录管理员后台需要用户名密码，刚开始未设置，我们要自行设置。

首先查看存放用户名密码的文件：在conf文件夹下的tomcat-users.xml，用记事本打开。将管理员账号添加进去：

    
    
    <role rolename="manager-gui"/>
    
    <role rolename="manager-script"/>
    
    <role rolename="manager-jmx"/>
    
    <role rolename="manager-status"/>
    
    <user username="admin" password="admin" roles="manager-gui,manager-script,manager-jmx,manager-status"/>

点击保存后 ** **重启服务器**** ，回到登录界面，输入用户名密码，即可进入管理员界面：

![1619612849_608954b18a5d4b4718b5c.png!small](https://image.3001.net/images/20210428/1619612849_608954b18a5d4b4718b5c.png!small)

 ** **木马制作****

Tomcat只支持war的后缀文件包的上传，因此，必须将jsp木马程序与其他木马一起打包成war包才能上传。

在安装有JDK的操作系统上，将所需要上传的木马放在同一个文件夹中，存放到C盘。

这里用到一个jsp的木马程序以及V.vbs病毒程序。

运行cmd，使用cd命令将目录切换到刚刚存放的c文件夹下：

![1619612858_608954ba0796c4c057e6d.png!small](https://image.3001.net/images/20210428/1619612858_608954ba0796c4c057e6d.png!small)

使用命令将木马程序打包：

    
    
    jar cvf shell.war *

 ** **若提示**** ** **jar**** ** **不是内部命令，请回到**** ** **JDK**** **
**安装步骤查看环境变量是否配置正确。****

 ** **成功时的命令提示如下：****

![1619612901_608954e51c0f1da658dbf.png!small](https://image.3001.net/images/20210428/1619612901_608954e51c0f1da658dbf.png!small)

 ** **漏洞入侵****

使用另一台电脑（2003）输入以下网址：

http://192.168.78.137:8080/（对应IP地址要改）

访问

成功将出现以下界面：

![1619612910_608954ee2828e1e19c74a.png!small](https://image.3001.net/images/20210428/1619612910_608954ee2828e1e19c74a.png!small)

弱口令扫描

打开Apache Tomcat crack软件，界面如下：

设置扫描网段，点击add按钮添加；点击start按钮开始扫描。扫描成功将获得口令和密码。

![1619612966_60895526c6fe368ddb00d.png!small](https://image.3001.net/images/20210428/1619612966_60895526c6fe368ddb00d.png!small)

上传木马

利用前面扫描到的口令密码登录管理员网页，将之前做好的war包上传至服务器:

![1619612988_6089553c880dc589c53c8.png!small](https://image.3001.net/images/20210428/1619612988_6089553c880dc589c53c8.png!small)

![1619612995_6089554317eaf3363301b.png!small](https://image.3001.net/images/20210428/1619612995_6089554317eaf3363301b.png!small)

在地址栏中输入网址：

http://192.168.78.137:8080/shell/s.jsp

即可看到对方电脑中所有的文件目录：

![1619613018_6089555a1579adb5c2d8b.png!small](https://image.3001.net/images/20210428/1619613018_6089555a1579adb5c2d8b.png!small)

找出之前一并上传的木马文件vbs，利用下面的执行功能让其在被害者电脑上运行：

    
    
    c:\hzx\V.vbs -install

![1619613046_608955760f075db43c3bd.png!small](https://image.3001.net/images/20210428/1619613046_608955760f075db43c3bd.png!small)

此时在被攻击者电脑上会自运行病毒程序，即中病毒了。也可将病毒用灰鸽子木马替换实现远程控制。

![1619613220_60895624d46a3537f6b49.png!small](https://image.3001.net/images/20210428/1619613220_60895624d46a3537f6b49.png!small)

