![](https://image.3001.net/images/20211117/1637144437_6194d775c6900402a2f3d.jpg!small)

## 关于PortBender

PortBender是一款功能强大的TCP端口重定向工具，该工具允许红队研究人员或渗透测试人员将一个TCP端口（例如445/TCP）的入站流量重定向到另一个TCP端口（例如8445/TCP）。PortBender项目包含了一个渗透测试脚本，可以帮助研究人员将该工具与Cobalt
Strike进行集成。但是，由于该工具是基于一个反射型DLL实现的，因此它可以通过“ReflectiveLoader”接口与支持加载模块的任何C2框架进行集成。除此之外，该工具还允许研究人员模拟Duqu
2.0恶意软件中“PortServ.sys”功能所利用的一个后门/持久化机制。

## 工具机制

PortBender利用了WinDivert库来拦截网络流量，其中还涉及到了Windows
Filtering平台（WFP）。PortBender的设计深受DivertCpconn实用程序的启发，并且基于WinDivert库实现其功能。

## 工具使用

PortBender提供了两种操作模式，第一种为“重定向模式”，第二种为“后门模式”。在“重定向模式中”，任意指向目的端口（例如445/TCP）的连接都会被重定向至我们指定的端口（例如8445/TCP）。在“后门模式”下，我们只会将渗透测试人员发送的特定格式的TCP数据包转发至目标端口（例如443/TCP）。接下来，PortBender会将该客户端IP地址添加进后门客户端列表中，并将所有发送给目标设备的网络流量重定向至其他的端口（例如3389/TCP）。研究人员可以利用这种机制来模拟Duqu
2.0恶意软件在入侵卡巴斯基网络环境时所使用的持久化技术。

如需执行PortBender，我们首先得在Cobalt
Strike中引入“PortBender.cna”脚本，并将WinDivert32.sys或WinDivert64.sys文件引入至“PortBender.zip”然后上传至目标主机。PortBender的使用样例和帮助菜单如下所示：

    
    
    beacon> help PortBender
    Redirect Usage: PortBender redirect FakeDstPort RedirectedPort
    Backdoor Usage: PortBender backdoor FakeDstPort RedirectedPort Password
    Examples:
    PortBender redirect 445 8445
    PortBender backdoor 443 3389 praetorian.antihacker

## 工具使用样例

### 使用样例1

比如说，我们可能希望以“重定向模式”来从一台被渗透的Windows系统中执行SMB中继攻击。为了实现这个目标，我们可以控制PortBender将所有流向445/TCP端口的流量重定向到8445/TCP端口，而这个端口则运行的是渗透测试人员的SMB服务。在下面这个例子中，我们将会运行如下所示的命令来完成这个目标：

    
    
    PortBender redirect 445 8445

运行结果如下所示：

![](https://image.3001.net/images/20211117/1637144483_6194d7a3dad28f1c5a890.png!small)

### 使用样例2

在下面这个例子中，我们希望在一台接入外网的部署IIS
Web服务器上部署隐蔽持久化机制。此时，我们将运行下列命令，并通过控制后门服务来将目标主机上来源于任意IP（“praetorian.antihacker”关键字定义的IP）的任何流向443/TCP端口的流量重定向到3389/TCP：

    
    
    PortBender backdoor 443 3389 praetorian.antihacker

命令运行结果如下所示：

![](https://image.3001.net/images/20211117/1637144504_6194d7b830f1b7d433692.png!small)

## 项目地址

 **PortBender：** 【[ _GitHub传送门_](https://github.com/praetorian-inc/PortBender)】

## 参考资料

  * [ _https://github.com/Arno0x/DivertTCPconn_](https://github.com/Arno0x/DivertTCPconn)
  * [ _https://github.com/stephenfewer/ReflectiveDLLInjection_](https://github.com/stephenfewer/ReflectiveDLLInjection)
  * [ _https://github.com/basil00/Divert_](https://github.com/basil00/Divert)
  * [ _https://diablohorn.com/2018/08/25/remote-ntlm-relaying-through-meterpreter-on-windows-port-445﻿_](https://diablohorn.com/2018/08/25/remote-ntlm-relaying-through-meterpreter-on-windows-port-445)

