# 利用Metasploit和iptables进行端口扫描

阅读量 **137115**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-03-08 12:00:52

 **x**

##### 译文声明

本文是翻译文章，文章来源：www.hackingarticles.in

原文地址：<http://www.hackingarticles.in/port-scanning-using-metasploit-iptables/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t016ad8f1257f3d5dd0.jpg)

端口扫描是用于渗透测试人员通过特定端口号识别计算机网络服务状态的一种技术。比如80端口用于HTTP服务，22端口用于FTP服务。我们建议使用Nmap来穷举所有的端口状态。  
此外，Metasploit也可以进行端口扫描穷举处目标计算机的网络服务并且它在这方面要比Nmap好用得多。

**事前准备：  
攻击机：Kail Linux(192.168.1.103)  
目标机：Ubuntu(192.168.1.105)**

打开目标机的终端然后添加下面给出的iptables规则，这么做的目的是为了在目标机网络中传入的数据包将分别丢掉在80端口上ACK包和在22端口上SYN包。

    
    
    sudo iptables -I INPUT -p tcp –tcp-flags ALL ACK –dport 80 -j DROP
    sudo iptables -I INPUT -p tcp –tcp-flags ALL SYN –dport 22 -j DROP

![](https://p5.ssl.qhimg.com/t01637d2276bf14f2e1.png)

## ACK扫描

现在打开你Kali Linux机器上的终端，并且输入”msfconsole”加载metasploit并且执行下面的 **auxiliary**
命令来运行特定的模块。  
此模块将使用原始的ACK扫描来映射防火墙规则集。找到的任何未过滤的端口(unfiltered)都意味着防火墙并没有进行该端口的保护。  
现在，在这个模块中输入下面给出的命令会发送ACK数据包到21，22，80，443端口上，目的是为了检测上述这些端口在防火墙上的状态。如果收到了目标端口的reset数据包，那么会在那个特定端口上显示
**unfiltered** 状态；如果没有收到目标端口的reset数据包，那么它不会显示任何对这个端口的描述，这意味着这个端口正在受到防火墙的保护。

    
    
    use auxiliary/scanner/portscan/ack
    msf auxiliary(ack) > set rhosts 192.168.1.105
    msf auxiliary(ack) > set ports 21,22,80,443
    msf auxiliary(ack) >exploit

如下图你可以看到，图中显示了21,22,443是 **TCP UNFILTERED**
状态，并且没有对80端口的任何描述，因此80端口被过滤掉(filtered)了。利用这种扫描技巧可以通过端口的过滤或者非过滤状态来识别防火墙的状态。

![](https://p2.ssl.qhimg.com/t016fa8934a64681b17.png)

我们来使用wireshark演示下ACK扫描，通过下图你可以看到80端口并没有回复RST数据包，这意味着对于80端口的ACK数据包被网络管理员阻塞掉了。

![](https://p2.ssl.qhimg.com/t0113014ac9ae8590db.png)

## SYN扫描

这个模块可以穷举所有的开启的TCP服务通过使用原始的SYN扫描，这里SYN数据包会被发送到21，22，80，443端口上来穷举出这些端口的打开或者关闭的情况。如果收到了来自目标端口的SYN,ACK数据包，那么会显示出
**TCP OPEN**
的状态；如果没有收到目标端口的SYN,ACK数据包，那么将不会显示出任何有关目标端口的描述，这说明了该目标端口是过滤(filtered)或者关闭(closed)状态。

    
    
    use auxiliary/scanner/portscan/syn
    msf auxiliary(syn) > set rhosts 192.168.1.105
    msf auxiliary(syn) > set ports 21,22,80,443
    msf auxiliary(syn) >exploit

如下图所示你可以看见，21，80，443端口显示着 **TCP OPEN** 状态，并且没有任何有关22端口的描述，这说明22端口被过滤掉或者被关闭了。

![](https://p0.ssl.qhimg.com/t01c5e300a33ef53364.png)

好了，我们再一次使用wireshark来演示SYN扫描过程，这下图中你可以观察到22端口没有回复SYN,ACK数据包，这意味着在22端口上的SYN数据包被网络管理员阻塞掉了。  
此外，通过下面你可以观察到源地址到目的地址之间的数据包交流。

  1. 源端口发送 SYN 数据包到目的端口
  2. 源端口从目的端口那里收到SYN, ACK 数据包
  3. 源端口发送 RST 数据包到目的端口

![](https://p4.ssl.qhimg.com/t01ff4d0fb5fb9d0a24.png)

## TCP扫描

通过在每个端口上进行完整的TCP连接来穷举所有开启的TCP服务，这不需要在源地址机器上使用管理员权限，当你在pivoting时这是个很有用的技巧。

    
    
    use auxiliary/scanner/portscan/tcp
    msf auxiliary(tcp) > set rhosts 192.168.1.105
    msf auxiliary(tcp) > set ports 21,22,80,443
    msf auxiliary(tcp) >exploit

这种扫描和SYN扫描很相近，但是唯一的不同在于它是基于TCP的完整通信，即4次握手并且SYN扫描是在半TCP通信中进行的。  
如下图你可以观察到，图中显示了21，80，443端口是 **TCP OPEN**
状态，但是并没有任何有关22端口的描述，因此22端口是被过滤掉了或者被关掉了。

  
同上，使用wireshark抓包进行演示。这里你可以看到，22端口没有回复SYN,ACK数据包，这意味着22端口的SYN数据包被管理员阻塞掉了。  
此外，通过下面你可以观察到源地址到目的地址之间的数据包交流。

  1. 源端口发送 SYN 数据包到目的端口
  2. 源端口从目的端口那里收到SYN, ACK 数据包
  3. 源端口发送ACK 数据包到目的端口
  4. 源端口发送 FIN, ACK 数据包到目的端口

![](https://p0.ssl.qhimg.com/t01b2919c60044ded27.png)

## XMAS扫描

穷举 **open|filtered** 状态的TCP服务我们使用原始”XMAS”扫描，它会发送包含FIN,PSH和URG标志的探针。  
这种扫描不适用TCP 3次握手通信，而是使用TCP通信的其他TCP标志位来穷举端口的状态。

    
    
    use auxiliary/scanner/portscan/xmas
    msf auxiliary(xmas) > set rhosts 192.168.1.105
    msf auxiliary(xmas) > set ports 21,22,80,443
    msf auxiliary(xmas) >exploit

通过下图你可以看到，这次显示了TCP OPEN|FILTERED状态的端口是21,22,80,443。

  
如下图，你是否注意到了源端口发送到目的端口的数据包带有FIN,PUSH和URG标志，并且目的端口没有回复任何数据包到源端口，这表明上面那些的端口是开放的，如果任何目的端口发送RST,
ACK数据包到源端口，那么它表明这个端口是关闭的。

![](https://p5.ssl.qhimg.com/t015ef83546371659c3.png)

本文翻译自www.hackingarticles.in [原文链接](http://www.hackingarticles.in/port-scanning-using-metasploit-iptables/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Oopohh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/100373](/post/id/100373)

安全客 - 有思想的安全新媒体

本文转载自: [www.hackingarticles.in](http://www.hackingarticles.in/port-scanning-using-metasploit-iptables/)

如若转载,请注明出处： <http://www.hackingarticles.in/port-scanning-using-metasploit-iptables/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透](/tag/渗透)
  * [metasploit](/tag/metasploit)
  * [端口扫描](/tag/端口扫描)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) Oopohh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

