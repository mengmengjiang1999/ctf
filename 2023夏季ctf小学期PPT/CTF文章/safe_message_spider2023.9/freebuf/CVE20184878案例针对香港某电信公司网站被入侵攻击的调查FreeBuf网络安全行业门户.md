***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![01.jpg](https://image.3001.net/images/20180402/15226383674607.jpg!small)**

**早前，有研究人员发现香港某电信公司网站被黑客入侵攻击，3月21日，Morphisec实验室就此次网站攻击开展了调查，调查人员最终发现，该电信公司集团官网被黑客入侵后，在主页面home.php中嵌入了一个Flash
exploit 的CVE-2018-4878漏洞利用文件。**

##  **攻击事件概述**

该攻击算是一例教科书式的有针对性的的“水坑攻击”，攻击者通过在目标受害者可能访问的网站上植入恶意软件或代码，来诱使受害者系统被感染，给攻击者敞开门户，这种攻击多用于网络间谍活动。Morphisec调查发现，此次的水坑攻击具备非常高级的免杀逃逸特征
：攻击完全是无文件的，在受害者磁盘上不会留下任何持久性或可追溯痕迹，另外还在一个非过滤端口上使用了自定义协议。通常来说，这种高级类型的水坑攻击极具针对性，并且也会具有非常复杂的攻击者背景。

当CVE-2018-4878漏洞代码被披露后，全球范围内发生了多起[国家支持黑客攻击](http://blog.morphisec.com/the-lazarus-group-strikes-again-or-is-it-an-imposter-the-latest-cve-2018-4878-attack)、恶意软件攻击和漏洞利用工具包扩散利用等，此次水坑攻击也算是利用CVE-2018-4878漏洞最近的一起攻击案例了。目前，经Morphisec分析报告之后，该香港电信公司网站恶意代码已被清除，网站安全状况恢复正常。  

## 攻击分析

被攻击者嵌入漏洞利用文件（Flash exploit）的home.php主页面：

![02.jpg](https://image.3001.net/images/20180402/1522637545590.jpg!small)

这个被嵌入的Flash exploit与先前普遍的CVE-2018-4878漏洞利用程序非常相似，但不同之处在于，它是一个后利用型（post-exploitation）的执行程序：

![03.png](https://image.3001.net/images/20180402/15226375634791.png!small)

其shellcode会执行Windows系统中有效的rundll32.exe进程，通过注入该进程，用它来隐藏恶意代码运行的内存空间，然后，shellcode会下载其它后续利用代码注入到rundll32进程中：

![HK-attack2.png](https://image.3001.net/images/20180402/15226376447565.png!small)

![04.png](https://image.3001.net/images/20180402/15226376116425.png!small)

攻击者使用的C2服务器是106[.]185.24.241（日本），它在受害主机通讯时，使用了443端口的自定义协议，目前，Morphisec正在对该协议进行深入分析:

![05.png](https://image.3001.net/images/20180402/15226376876444.png!small)

## 攻击使用的Metasploit模块  

shellcode下载注入到rundll32进程空间的后续利用代码包括Metasploit
Meterpreter和Mimikatz模块，从时间上来看，这些模块都是于攻击事件前一周，也就是2月15日被编译的：

![2018040210563060956.png](https://image.3001.net/images/20180402/15226379159923.png!small)

以下黄色模块是原始的Metasploit利用模块：

![07.png](https://image.3001.net/images/20180402/15226380595620.png!small)

## 总结

通过调查，Morphisec发现，此次复杂的水坑攻击是攻击者计划进行深入攻击的前奏，可能具有非常高深复杂的攻击者背景。Morphisec声称，由于这次攻击中使用了CVE-2018-4878利用程序，与之前被发现的[用于国家黑客活动](http://blog.morphisec.com/the-lazarus-group-strikes-again-or-is-it-an-imposter-the-latest-cve-2018-4878-attack)相关的攻击高度相似，其中可能存在某些关联。目前，Morphisec还未定位追溯到具体的攻击者，他们将会持续跟进调查。

## 攻击特征

> Flash - 58D15B7A49193022D8FB9712FAC1A9E2
>
> C2- 106[.]185.24.241 (li715-241.members.linode[.]com:https)

 ***参考来源：[morphisec](http://blog.morphisec.com/watering-hole-attack-hong-kong-telecom-site-flash-exploit-cve-2018-4878)，FreeBuf小编clouds编译，转载请注明来自FreeBuf.COM**  

