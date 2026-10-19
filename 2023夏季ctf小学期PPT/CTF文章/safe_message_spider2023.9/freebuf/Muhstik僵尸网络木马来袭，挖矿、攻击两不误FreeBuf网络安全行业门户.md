# 背景概述

近日，深信服安全团队捕获到一款Muhstik僵尸网络木马，多个国内的服务器被爆破登录，在主机执行恶意代码以下载Muhstik僵尸木马和挖矿病毒，从而利用服务器进行挖矿，以及进行DDos攻击。

##  ** **情报分析****

攻击者主要会在爆破登录成功后用wget下载shell脚本

![](https://image.3001.net/images/20201124/1606216595_5fbceb933215263f506bd.png!small)

 **Virus**

|

 **MD5**  
  
---|---  
  
1sh

|

861c40811b98780ce8eba0c572dfaa9b  
  
2sh

|

bfc90665de5c74c45488226a8999630b  
  
3sh

|

ca6d74719f063b9c79cb4d81d7299392  
  
 **1sh:** 主要下载pty1,pty2,pty5,pty11到/var/run目录下，更改文件的权限。

首先是进行 chmod + x 提供可执行功能 ，再进行 chmod
700让其他人没有更改文件的权限。同样，将pty3,pty10,pty4放到当前的目录下，pty3在/var/run和/var/tmp目录下，执行完这些操作之后删除自身的文件1sh。

![](https://image.3001.net/images/20201124/1606216617_5fbceba9e1b02e64bc98b.png!small)

 **2sh:** 主要下载pty1,pty2,pty11,pty10,pty4,pty5到/tmp目录下，更改文件的权限。

首先是进行 chmod + x 提供可执行功能 ，再进行 chmod
700让其他人没有更改文件的权限。将下载的文件复制到/tmp目录下的loop0,loop1,loop2,loop3,loop4，执行完操作之后删除自身的文件2sh。

![](https://image.3001.net/images/20201124/1606216629_5fbcebb57463d1bf485e5.png!small)

 **3sh:** 主要下载pty10,pty3,pty4到当前的目录下，更改文件的权限。

首先是进行 chmod + x 提供可执行功能 ，再进行 chmod
700让其他人没有更改文件的权限。然后下载pty10,pty1,pty2,pty5,pty11到/tmp目录下进行 chmod + x 提供可执行功能
，再进行 chmod 700让其他人没有权限更改文件，3sh文件进行自删除。

![](https://image.3001.net/images/20201124/1606216639_5fbcebbfb78af3f8ea68d.png!small)

 **病毒运行：**

![](https://image.3001.net/images/20201124/1606216655_5fbcebcf05db6374403a5.png!small)

##  ** **技术分析****

![](https://image.3001.net/images/20201124/1606216687_5fbcebefc042b390a3207.png!small)

下载下来的文件pty* 等等的，主要是muhstik主要的病毒文件，主要功能：

1.蠕虫式传播；

2.长期驻留；

3.利用多种漏洞；

4.挖矿获利。

  

pty*采用UPX壳：

![](https://image.3001.net/images/20201124/1606216742_5fbcec2664e81feba906b.png!small)

通过ida分析，恶意文件具有crontab定时任务，以及/etc/inittab系统启动项进行持久化

![](https://image.3001.net/images/20201124/1606216766_5fbcec3ea8f9dcb744aa1.png!small)![](https://image.3001.net/images/20201124/1606216775_5fbcec4742e5533fac8aa.png!small)![](https://image.3001.net/images/20201124/1606216791_5fbcec57c1cfc52898e90.png!small)![](https://image.3001.net/images/20201124/1606216805_5fbcec6593863a34d12db.png!small)  

可以看到计划性任务和我们ida中的路径相吻合：

![](https://image.3001.net/images/20201124/1606216831_5fbcec7f87cb60d5fbe26.png!small)

我们也可以发现通信端口号是2407，和165.22.217.181:2407进行通信

![](https://image.3001.net/images/20201124/1606216850_5fbcec927754a7de020c9.png!small)

经过wieshark进行抓包可以看到和165.22.217.181:2407进行了网路上的通信，并且传递了数据包

![](https://image.3001.net/images/20201124/1606216866_5fbceca2c48ca38f3a4a0.png!small)

恶意文件为受害主机的系统分配了相应的昵称：

主要收集了电脑的体系结构、是否为root用户、编号以及设备的一部分信息，进行传送，如下：

NICK x86|f|1|8090634|unknown

![](https://image.3001.net/images/20201124/1606216887_5fbcecb79cbae11045f0c.png!small)  

主要通过Connect命令中含有设备命名unknown加入到信道中，服务器进行PING命令后，病毒主机回复PONG，病毒主机通过ex86信道密码为8974来跟僵尸网络命令互通

![](https://image.3001.net/images/20201124/1606216906_5fbcecca39d2b0c15fdfb.png!small)

在经过1小时左右会Get下载xmra64文件，并且进行加密矿工的通信还有挖矿的行为

![](https://image.3001.net/images/20201124/1606216922_5fbcecda564f33e83fc0d.png!small)

可以确定为是门罗XMR挖矿程序

![](https://image.3001.net/images/20201124/1606216937_5fbcece9db7b7a22ad78b.png!small)

看下本机网络行为：开始进行通信挖矿

![](https://image.3001.net/images/20201124/1606216948_5fbcecf435a2af1283069.png!small)

##  ** **解决方案****

###  ** **加固建议****

  1. 避免使用弱密码，定时进行改密以及加固密码；
  2. 尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；
  3. 经常查看服务器的日志，发现有不明ip经常爆破，建议直接封禁，避免带来不必要的风险;
  4. 定期检测系统漏洞并且及时进行补丁修复。

###  ** **手动解决方案****

1.查找到下文所述的文件，kill其进程并删除文件：

/var/run目录下的pty1,pty2,pty5,pty11

/tmp目录下的pty1,pty2,pty11,pty10,pty4,pty5,xmra64

/tmp目录下的loop0,loop1,loop2,loop3,loop4

当前的目录下的pty3,pty10,pty4，xmra64

/dev/shm/pty*（\\*代表任意字符）

/var/tmp/pty*

/var/lock/pty*

/var/run/pty*

2.crontab -l命令查看定时任务中是否包含以上pty*相关的文件内容，有将其删除即可

3.cat /etc/inittab查看系统启动任务中是否包含以上pty* 相关的文件内容，有将其删除即可

