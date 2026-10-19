# **0x00简介**

XAMPP是一个建站集成软件包，一个易于安装且包含 MySQL、PHP 和 Perl 的 Apache
发行版。类似与WampServer，phpstudy，他可以运行在Wndows、Linux、Mac OS等多种操作。XAMPP
的确非常容易安装和使用：只需下载，解压缩，启动，方便渗透测试人员搭建各种web环境。

#  **0x01漏洞概述**

在Windows上的XAMPP 7.2.29之前，7.3.16之前的7.3.x和7.4.4之前的7.4.x中发现了一个问题。非特权用户可以在xampp-contol.ini中为所有用户（包括管理员）更改.exe配置，当恶意用户修改配置后，管理员通过xampp查看日志时，将会执行恶意用户创建的代码。

#  **0x02影响版本**

Apache Friends XAMPP <7.2.29

Apache Friends XAMPP 7.3.，<7.3.16

Apache Friends XAMPP 7.4.，<7.4.4

#  **0x03环境搭建**

环境：windows7+XAMPP7.2.25版本

下载地址：链接：https://pan.baidu.com/s/1l5fSiy4uiQNZy8fi97WdaQ

提取码：dota

1.安装XAMPP不能安装在C盘，如果利用虚拟机搭建漏洞环境，可以在虚拟机设置中添加一块新的硬盘。

![](https://image.3001.net/images/20210104/1609752179_5ff2de73db4378c99975b.jpg!small)

![](https://image.3001.net/images/20210104/1609752190_5ff2de7e592c563916a78.jpg!small)![](https://image.3001.net/images/20210104/1609752364_5ff2df2c5293a3c7b05a5.jpg!small)

2.使用管理员权限运行安装XAMPP，选择除C盘外的硬盘安装

![](https://image.3001.net/images/20210104/1609752380_5ff2df3cbd527e50f6809.jpg!small)

4.一直下一步安装即可，安装完成为以下图片

![](https://image.3001.net/images/20210104/1609752392_5ff2df48778da1e5432bb.jpg!small)

#  **0x04漏洞复现**

​1. 在系统中新建立一个低权限demo用户

net user demo 123 /add

![](https://image.3001.net/images/20210104/1609752233_5ff2dea90bc46ca9f4a58.jpg!small)![](https://image.3001.net/images/20210104/1609752405_5ff2df5540b49bc167713.jpg!small)

2.在系统中切换成demo的低权限用

![](https://image.3001.net/images/20210104/1609752415_5ff2df5fb8a9d374bb2c1.jpg!small)

3.查看是否存在漏洞，使用低权限用进入XAMPP目录，运行xampp-control文件可查看XAMPP版本号

![](https://image.3001.net/images/20210104/1609752430_5ff2df6e4213e120a91c7.jpg!small)

4.使用低权限账号在桌面新建一个.bat的文件，文件内容如下

@echo off

net localgroup administrators demo /add //注：demo改为你的用户名

![](https://image.3001.net/images/20210104/1609752297_5ff2dee9616d4522aaef0.jpg!small)

5.打开XAMPP点击右上角的config，选择刚才创建的bat文件，并保存。

![](https://image.3001.net/images/20210104/1609752288_5ff2dee0974c3b68f8f6c.jpg!small)

6.切换成管理员用户并以管理员权限运行XAMPP，然后点击查看apache或mysql的日志文件

![](https://image.3001.net/images/20210104/1609752280_5ff2ded8ee202951041e9.jpg!small)

![](https://image.3001.net/images/20210104/1609752273_5ff2ded1dc933068f8c29.jpg!small)

7.点击后会看见一阵黑影闪过，然后在cmd命令中查看demo用户权限，可以看到提权成功

![](https://image.3001.net/images/20210104/1609752265_5ff2dec9141d59e9c0493.jpg!small)

 **小结**

1\. 此次漏洞复现只能在windows系统上使用，并且须导入命令执行文件，并且需要管理员点击日志文件才能执行。

#  **0x05修复建议**

1.建议更新至最新版本

