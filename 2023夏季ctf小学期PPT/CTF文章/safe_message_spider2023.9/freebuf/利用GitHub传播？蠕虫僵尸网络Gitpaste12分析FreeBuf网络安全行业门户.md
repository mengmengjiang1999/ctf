![](https://image.3001.net/images/20201116/1605490103_5fb1d5b7718fcc7e60eb0.png!small)

## 写在前面的话

几个月前，[ _Octopus Scanner_](https://blog.sonatype.com/octopus-scanner-compromises-26-oss-projects-on-github)被发现感染了GitHub上的26个开源项目，而就在几个月后，又有新的报告显示了另一个复杂的恶意软件感染链，即本文的主角：[
_Gitpaste-12_](https://www.bleepingcomputer.com/news/security/reverse-shell-botnet-gitpaste-12-spreads-via-github-and-pastebin/)。它是一个蠕虫僵尸网络，这个蠕虫僵尸网络采用了非常先进的技术，并且拥有非常强大的功能，可以利用像GitHub和Pastebin这样值得信赖的网站来托管自己的恶意代码。

Gitpaste-12在蠕虫主体程序中使用了12个已知的安全漏洞，因此得名Gitpaste-12，这就有点“瑞士Knife”的味道了。而其中有两个漏洞针对的是当前热门的开源组件，即[
_Apache Struts_](https://www.sonatype.com/struts2-vulnerability)和mongoDB。

## 在GitHub上隐藏了超过3个月之久

Gitpaste-12通过将其恶意Payload托管在类似GitHub和Pastebin这样的开源网站上，导致现在仅仅使用基于IoC的屏蔽方法是无法屏蔽Gitpaste-12的命令控制基础设施的，因为这些网站还涉及到很多合法用例。

实际上，Gitpaste-12从2020年7月份开始就已经悄悄托管在了GitHub上了。

![](https://image.3001.net/images/20201116/1605490121_5fb1d5c9648f3b0107215.png!small)

直到2020年的10月15日，Juniper Threat实验室的研究人员才发现了了个蠕虫僵尸网络，并在大约两周后让GitHub将它彻底下架。

Juniper Threat实验室的研究人员Alex Burt和Trevor
Pott表示：“这款恶意软件之所以使用GitHub这样的开源网站来作为其基础准备环境，是因为攻击者想要绕过常见的网络安全防御系统，包括防火墙规则在内。因为常见的攻击防御和网络监控系统是不会屏蔽来自合法站点的流量的。”

![](https://image.3001.net/images/20201116/1605490129_5fb1d5d16cc927d7e85cf.png!small)

蠕虫可以给攻击者提供反向Shell，根据研究人员的发现，Gitpaste-12还会在某些受感染的系统上使用TCP端口30004和30005来监听Shell命令。

值得一提的是，Gitpaste-12还会在受感染主机上安装一个门罗币挖矿工具，并且使用了额外代码来将其隐藏起来，也就是不在进程管理器中显示挖矿进程。除了挖矿工具之外，它还可以使用一个基于Telnet的脚本并通过暴力破解的方式攻击Linux服务器和IoT设备，然后通过这些方法来实现蠕虫的持久性感染。

Juniper的研究人员表示，Gitpaste-12恶意软件还包含了一个能够针对网络内其他设备发动攻击的脚本，而且还会尝试进行自我复制和横向传播。它会选择一个随机的/8
CIDR地址，然后尝试攻击该地址范围内的所有地址。

## Gitpaste-12还会继续进化

从功能性和躲避安全检测方面，Gitpaste-12这个蠕虫僵尸网络确实是“八面玲珑”。而且Gitpaste-12之所以特别危险，是因为它利用的是社区对GitHub这种网站的信任。

在我们最近的软件供应链状态报告中，我们记录了OSS项目中恶意代码注入或下一代软件供应链攻击活动增加了430%，而这已经是我们第二次看到这种形式的攻击了。

Juniper的研究人员明确表示，尽管这款恶意软件目前可能针对Linux服务器和物联网设备进行攻击，但恶意软件样本中的测试代码表明它有可能在将来版本中引入更加多的攻击模块，这也表明Gitpaste-12目前仍在开发过程中。

Gitpaste-12攻击将会感染开发人员所使用的开发工具，而这些工具将用于各类项目的开发，这将导致后续的项目受到感染，从而实现漏洞的传播。在这个开源的年代，这无疑是一个正在发展的新型攻击向量。

我们可以看到，Gitpaste-12利用的是一个原本值得我们信赖的开源生态系统，再加上它躲避安全检测的巧妙特性，下一个版本的Gitpaste-12会先进成什么样子，我们无法得知。但是Gitpaste-12的出现，表明了通过自动化定期审查软件供应链的重要性。

## 入侵威胁指标IoC

Juniper Threat实验室给出的Gitpaste-12入侵威胁指标IoC如下。

### URL地址：

    
    
    https://raw.githubusercontent[.]com/cnmnmsl-001/-/master/shadu1
    
     
    
    https://raw.githubusercontent[.]com/cnmnmsl-001/
    
     
    
    https://pastebin[.]com/raw/Tg5FQHhf
    
     
    
    https://github[.]com/cnmnmsl-001/-
### 哈希：

门罗币挖矿程序

|

e67f78c479857ed8c562e576dcc9a8471c5f1ab4c00bb557b1b9c2d9284b8af9  
  
---|---  
  
hide.so

|

ed4868ba445469abfa3cfc6c70e8fdd36a4345c21a3f451c7b65d6041fb8492b  
  
挖矿工具配置文件

|

bd5e9fd8215f80ca49c142383ba7dbf7e24aaf895ae25af96bdab89c0bdcc3f1  
  
Shell 脚本

|

5d1705f02cde12c27b85a0104cd76a39994733a75fa6e1e5b014565ad63e7b  
  
  

  

