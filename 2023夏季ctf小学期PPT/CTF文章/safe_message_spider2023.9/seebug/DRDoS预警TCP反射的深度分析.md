**作者：百度安全实验室  
原文链接：<https://mp.weixin.qq.com/s/rhqa2RDaEYxiIjmDp99uVw>**

### 0x00 背景

TCP反射攻击是在现网的DDoS攻防对抗中，逐渐兴起的一种新型攻击方式。攻击者伪造源IP地址为被攻击目标的IP地址向公网上大量的TCP服务器（通常是CDN、WEB站点等）发送连接请求（SYN报文），这些被利用的TCP反射服务器在收到大量的连接报文后，会向被攻击目标响应大量的数据包，这些反射数据包的类型通常包括SYN-ACK、ACK和RST-ACK，由于这些攻击流量通常混杂着正常业务流量，并且存在协议栈行为，导致传统的DDoS防御系统很难防御，因而使得这种攻击方式近年来呈现出不断上升的趋势。

百度智云盾系统针对TCP反射攻击进行跟踪，分析发现攻击频率近几年呈现出明显上升的趋势，反射攻击手法也在不断变化，攻击流量从最常见的单一SYN-ACK，发展成由SYN-ACK、ACK和RST-ACK报文混合组成。根据智云盾系统监测的数据显示，混合型TCP反射已经成为了继SSDP、NTP反射之后最为流行的攻击方式。百度智云盾系统在与TCP反射攻击的长期攻防对抗中，制定出一套TCP反射防御算法，能够2s内识别攻击，实时对流量进行隔离和清洗，保障用户与公司免遭此类攻击的伤害。

### 0x01 反射原理

#### 1）标准反射流

众所周知，TCP的三次握手，服务端在接受到客户端的SYN报文后，会响应SYN-ACK报文，并开启一个半连接放入队列。如果此时服务端短时间内收到多个相同五元组的SYN报文，就会在服务端造成会话冲突，此时不同服务器的处理方式不同。

标准的TCP协议栈在遇到会话冲突的情况时，会响应出SYN-ACK、ACK和RST-ACK报文，服务端在第一次收到SYN报文后，会回复一个SYN-ACK报文，后续针对同一五元组过来的SYN报文，则会与当前数据包的seq号SEQ2、第一次收到的seq号SEQ1以及服务端的window
size有关。通常包含以下几种情况：

两次seq号相同：SEQ1=SEQ2 。

此时服务器判定这个SYN包是客户端重传，会再次响应seq号不同的SYN-ACK，也就是通常所说的重传SYN-ACK，这也是前些年网络上最为流行的SYN-ACK反射攻击。下图展示了我们使用linux系统多次发送seq号相同的SYN报文，测试反射出SYN-ACK的场景：

![
](https://images.seebug.org/content/images/2021/04/857529ba-8463-4bb1-a2df-40b990f86102.png-w331s)

图1 反射SYN-ACK报文（测试）

SEQ2在window size之内：即SEQ2大于SEQ1，且小于等于SEQ1+ windows size。

此时服务器响应报文比较特殊，呈现出首次SYN报文响应RST-ACK报文，这也是现网流量里存在较多的一类攻击流量，下图展示了我们使用linux系统发送seq号处于windows size之内，服务器响应RST-ACK的场景：

![
](https://images.seebug.org/content/images/2021/04/aafc3ed7-5b1c-478a-8358-d87d6cea603b.png-w331s)
图2 反射RST-ACK报文（测试）

SEQ2在windows size之外：即SEQ2小于SEQ1，或者SEQ2大于SEQ1+ windows size。

此时服务器会响应ACK报文，这也是当前遇到的最常见的攻击流量，下图展示了我们我们使用linux系统发送seq号按照5递减的SYN请求报文，测试反射ACK报文的场景：

![
](https://images.seebug.org/content/images/2021/04/ddb468d5-5e97-4359-b58b-a6ef86b2494f.png-w331s)
图3 反射ACK报文（测试）

标准的TCP反射流量呈现，如下图所示：

![
](https://images.seebug.org/content/images/2021/04/6c93ea02-354f-420e-bcf7-9bdc9995f13c.png-w331s)

图4 标准的TCP反射流

在攻防对抗过程中，我们发现攻击流量呈现出以ACK流量为主，SYN-ACK流量次之，以及少量的RST-ACK报文，这也符合黑客的攻击思路：攻击以随机seq的SYN报文短时间发送到TCP反射服务器，随机seq号的方式非常容易命中不在windows
size的区域，导致反射服务器响应大量的ACK报文。下列三图展示了我们在现网中捕获的真实反射流量。

![
](https://images.seebug.org/content/images/2021/04/c1afae18-48be-49da-a732-5ba4305f0557.png-w331s)
![
](https://images.seebug.org/content/images/2021/04/c0ff30bd-5501-41bb-9e72-ae3dba9ae3ab.png-w331s)
![
](https://images.seebug.org/content/images/2021/04/002fc052-779c-4150-84ad-557cc7e13291.png-w331s)
图5 真实的TCP反射攻击流量（现网）

以上均展示了端口开放时，标准的TCP协议栈处理连接请求时的响应的报文特征，那么端口关闭时，会响应什么呢？不同的系统处理不同，linux内核的TCP协议栈会响应RST-ACK报文。下图展示了我们在关闭TCP1000端口后服务器的响应报文。

![
](https://images.seebug.org/content/images/2021/04/299f4ce3-431b-43dd-8d5b-20a506df7539.png-w331s)

图6 关闭端口后的反射（RST-ACK）报文（测试）

#### 2）其他反射流

**SYNCookie**

在深入研究TCP反射攻击时，我们发现SYN Cookie机制会影响反射报文的特征。SYN Cookie机制是防护SYN
Flood攻击一种技术手段，我们都知道SYN
Flood攻击能够成立的前提关键在于服务器资源是有限的，由于服务器在收到SYN请求后会分配资源保存此次请求的关键信息，其中包括（五元组、TCP选项信息），这会占据服务器有限的系统资源，SYN
Cookie机制可以让服务器在收到客户端的SYN报文时，将客户端信息保存在SYN-ACK的初始序号和时间戳中，不消耗系统资源保存客户端信息，从而?SYN
Flood。

简单来说，开启SYN Cookie的服务器在收到SYN报文后，会根据当前五元组信息和TCP选项信息（时间戳、最大报文长度MSS）来计算出响应的SYN-ACK报文的seq号。正常的客户端收到SYN-ACK报文后会回复ACK报文，服务器根据ack确认号解析出之前计算的seq号，从而验证ACK报文的合法性。所以开启SYN
Cookie的服务器均会响应seq号不同的SYN-ACK报文。

攻击者在利用开启SYN Cookie的TCP反射服务器时，服务器所发出的反射报文均为SYN-ACK报文，但是seq号与标准TCP反射流呈现出的特征不同，这与具体服务器的SYN Cookie实现机制有关系，这里不做过多介绍。

我们选取一台机器开启SYNCookie配置：

![
](https://images.seebug.org/content/images/2021/04/830806c4-8869-4e0b-b407-8b10b5098e1a.png-w331s)

图7 开启SYNCookie

下图展示了我们我们使用linux系统测试的开启SYN Cookie的服务器响应的SYN-ACK报文：

![
](https://images.seebug.org/content/images/2021/04/93baa097-6f3b-4c43-948b-a3b061211408.png-w331s)

图8 开启SYN Cookie的反射报文（测试）

#### 3）其他类型服务器

Windows服务器在处理SYN报文时与linux有许多不同，我们使用Windows
server2016，TCP开放端口为3389，进行反射测试分析，下面是三种情况收到的数据包类型。

SEQ2=SEQ1，windows服务器与linux服务器一样，响应seq号不同的SYN-ACK报文：

![
](https://images.seebug.org/content/images/2021/04/6f53240f-f149-4478-993c-d1c3301b7630.png-w331s)

图9 windows server响应SYN-ACK（测试）

SEQ2小于SEQ1，或者大于SEQ1与windwos size之和，会直接响应SYN-ACK报文：

![
](https://images.seebug.org/content/images/2021/04/85d458cc-0157-4e22-b943-d7ed2346f718.png-w331s)
![ ](https://images.seebug.org/content/images/2021/04/42a44412-61f1-49ae-ad68-1a3d0e5ab427.png-w331s) 图10 window server响应SYN-ACK（测试）

SEQ2>SEQ1，并且小于SEQ1与windows size之和，服务器会在响应SYN-ACK后，不再响应任何报文：

![
](https://images.seebug.org/content/images/2021/04/38f4c624-3177-4260-9054-3c0dd3134c16.png-w331s)

图11 服务器只响应一次SYN-ACK报文（测试）

端口关闭时，windwos server与linux一样响应RST-ACK报文：

![
](https://images.seebug.org/content/images/2021/04/4309bcb8-9bfb-421c-a53c-d8cf4bc17dfc.png-w331s)

图12 关闭端口后windows server响应SYN-ACK报文（测试）

其他服务器：SUSE、Debian、Ubuntu等，如有兴趣，可以自行进行测试分析，这里不深入展开。

#### 4）智云盾蜜罐

值得一提的是，智云盾系统部署了多个蜜罐节点，我们在针对TCP反射攻击时，会根根据攻击特征动态调整响应报文，如果检测出攻击者恶意利用发动TCP反射，我们会针对任意SYN报文，均响应随机seq号的SYN-ACK报文，在攻击达到一定量级后，则不再响应任何数据包。

目前智云盾蜜罐系统已经长期被黑客利用进行TCP反射攻击，我们采样得到了大量的攻击踪影。

### 0x02 反射资源分析

#### 1）智云盾捕获

从近几年来跟踪分析的反射资源来看，攻击者倾向于使用的反射源端口最常见于21、22、23、80、443、1900、8080等常用的TCP端口，目的端口通常为被攻击目标的业务端口，比如：80、443、8080等。

我们对采集到的反射源端口进行分类，下图展示了反射源端口占比图：

![
](https://images.seebug.org/content/images/2021/04/473a87a2-ef61-4a98-bbd5-603a6387d53c.png-w331s)

图13 反射源端口占比

从反射源IP的属地信息来看，攻击来源几乎全部来自于国内，国内源IP占比超过98%，反射源IP国家分布如下：

![
](https://images.seebug.org/content/images/2021/04/e18b2937-06ee-4217-9ee4-77ef4c67bdd4.png-w331s)

图14 反射源归属地分布

智云盾系统多次捕获的攻击时发现，攻击者使用的反射源端口呈现出特殊的组合方式，比如1900端口通常与53、7547、1737组合攻击。

#### 2）全网数据

由于常见的TCP端口数据量非常之多，我们仅抽取了最常见的80端口在zoomeye查询，数据量之大引人深思。

![
](https://images.seebug.org/content/images/2021/04/c3dc2968-b73b-4ed3-a6ab-58452618d5fd.png-w331s)

图15 zoomeye全网数据（80端口）

### 0x03 防御措施

TCP反射与传统的UDP反射相比，其反射流量特征较为复杂，攻击流量来自于真实IP，而且具有协议栈行为，传统的DDoS防护系统往往容易将现网的TCP反射带来的ACK流量识别为Flood攻击。TCP反射攻击的防护难点：

  * 反射流量来自于真实IP，流量通常混杂着真实的业务流量

  * 反射资源丰富，公网上开放了大量的TCP服务器，主要来自于CDN、WEB站点

  * 流量类型通常包含SYN-ACK、ACK和RST-ACK，难以防护

  * 传统的DDoS防护系统，无法通过双向会话检查进行防护

智云盾系统在对抗TCP反射攻击中开发出一套防护算法，该算法已经经过长期的防护验证，算法的核心思路是：建立会话跟踪机制，分析每一个会话的意图，区分攻击流量与正常流量，防止透传，确保客户与公司的业务免遭TCP反射的伤害。防护特点：

  * 完整TCP会话状态跟踪

  * 阻断反射包，0透过

### 0x04 结尾

当前新冠疫情已经蔓延到世界各个角落，病例遍及219个国家和地区。对比疫情形势，全球地缘政治格局也在发生动荡，可以猜想网络空间冲突亦会愈演愈烈。攻击者在不断寻找防护方的弱点，防护方也需要不断研究黑客思维，提升防护能力。中国一直以来都是网络攻击最大的受害国，如此流行的TCP反射攻击将会扮演举足轻重的角色。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1571/>

