**2018
年信息安全事件频发，信息安全的技能、人才需求大增。现在，不管是普通的企业，还是专业的安全厂商，都不可避免的需要掌握和运用好信息安全的知识、技能，以便在需要的时候，能够御敌千里。所谓养兵千日，用兵一时，拥有一支完善的团队或完整的流程，可以保障企业在出现重大安全事件时，能有条不紊的进行处置，及时把破坏范围缩小。**

深信服EDR安全团队，全年参与了各种重大流行病毒和安全事件的应急响应，在此，我们将团队一整年的思考和所形成的流程，共享出来，期望能给未来即将从事，或者长期从事应急响应、安全研究的人，一些启迪。

我们大致从八个方面阐述，分别是：应急响应的整体思路、应急响应的基本流程、应急工具集简介、系统日志及日志分析、威胁情报的作用、常见病毒及分类、理解漏洞和补丁、技能提升建议。

## 一、应急响应的整体思路

应急响应的整体思路，就是上层有指导性原则和思想，下层有技能、知识点与工具，共同推进和保障应急响应流程的全生命周期。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730374_5c21f946bf4f0.png!small)  

### **原则和指导性思路**

>  **3W1H原则：**
> 3W即Who、What、Why，1H即How，做应急响应要带着疑问来做事，一定要收集清楚这些信息。网络拓扑是怎么样的？需求是啥？发生了什么事？你能做什么？用户用了什么产品？产品版本多少？病毒库版本多少？多少主机中了？主机是普通PC还是服务器？服务器是做什么的？……信息收集越多，对应急响应越有利。
>
>  **易失性原则：** 做应急响应免不了要做信息收集和取证的，但这里是有一定的先后顺序的，即最容易丢失的据，应该最先收集，其它的依次类推。
>
>  **要素原则：** 做应急响应，主要是抓关键证据，即要素，这些要素包括样本、流量、日志、进程及模块、内存、启动项。
>
>  **避害原则：**
> 做应急响应，要做到趋利避害，不能问题还没有解决，反而引入了新的问题。譬如，自己使用的工具被感染而不知情；给用户使用不恰当的工具或软件造成客户主机出现问题；给别人发样本，不加密，不压缩，导致别人误点中毒，最极端的场景就是给别人发勒索样本不加密压缩，导致别人误点中毒。

###  **技能、知识点与工具**

>  **应急工具集：** 应急响应必要的一套工具集合，可协助应急人员做分析，提高效率。
>
>  **日志分析：** 能对日志进行分析，包括但不限于系统日志（Windows/Linux等）、应用日志、安全设备日志（防火墙、防
> **病毒、态势感知等）。**
>
>  **威胁情报：** 安全事件可能不是孤立的，安全站点或搜索站点能找到安全事件的关联信息。
>
>  **漏洞补丁知识：** 知道漏洞与补丁的关系，它们在应急响应中的角色，了解常见漏洞及补丁。
>
>  **常见病毒及分类：** 知道病毒大致的分类以及常见的病毒。
>
>  **样本分析：** 至少能对样本进行一次简单动态的分析。
>
>  **操作系统知识：** 至少对Windows系统和Linux系统的有一定的知识储备，知道其基础的工作原理。

## 二、应急响应的基本流程

应急响应大致可以分为五个部分，其基本流程包括收集信息、判断类型、深入分析、清理处置、产出报告。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730386_5c21f9522f983.png!small)

> **收集信息：** 收集客户信息和中毒主机信息，包括样本。
>
>  **判断类型：** 判断是否是安全事件，何种安全事件，勒索、挖矿、断网、DoS等等。
>
>  **深入分析：** 日志分析、进程分析、启动项分析、样本分析。
>
>  **清理处置：** 直接杀掉进程，删除文件，打补丁，抑或是修复文件。
>
>  **产出报告：** 整理并输出完整的安全事件报告。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730400_5c21f960ab561.png!small)

勒索和挖矿事件，可以占比50%以上，而且这两种安全事件业务特征极其鲜明，因此可以单独提流程出来处置。

### 信息收集表

客户名称  |  什么区域的什么客户  
---|---  
感染主机数  |  感染了多数台主机  
补丁情况  |  打了哪些补丁，是否存在补丁漏打  
中毒现象  |  勒索/挖矿/DoS/僵尸网络/后门/木马  
帐号密码  |  确认是否有弱密码  
对外开发端口  |  对外开发了哪些端口  
开启的服务  |  开启了哪些服务  
操作系统版本  |  操作系统版本信息  
客户需求  |  确认客户具体需求  
  
![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730436_5c21f9849e823.png!small)

**取证要素：**
取证并非毫无头绪的，病毒本身必然有网络行为，内存必然有其二进制代码，它要么是单独的进程模块，要么是进程的dll/so模块，通常，为了保活，它极可能还有自己的启动项、网络心跳包。

总之，可以归结为如下4点要素： **流量、内存、模块、启动项。**

流量分析可以使用Wireshark，主要分析下当前主机访问了哪些域名、URL、服务，或者有哪些外网IP在访问本地主机的哪些端口、服务和目录，又使用了何种协议等等。

例如，使用Wireshark观察到，主机访问了sjb555.3322.org这种动态域名，即可粗略猜测这是一个C&C服务器（如何判断一个域名是可疑域名，可以参考后文）。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730434_5c21f9824ae6c.png!small)

有时候，可以根据网络协议来直接过滤分析流量。譬如，目前IRC协议已经很少被使用了，但利用IRC建立僵尸网络通道的现象仍比较普遍。使用Wireshark，直接在过滤条件里输入“irc”，回车看是否有相关流量。

如下图，刚好看到有相关的IRC协议流量，这便是可疑的。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730444_5c21f98ca19fd.png!small)

Wireshark执行下“Follow TCP
Stream”操作，查看到当前Botnet主机正在加入一个IRC频道。另外，也可以从目的IP下手，可查到这是一个恶意IRC僵尸网络服务器。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730458_5c21f99a9e5d9.png!small)

网络流量这块，如果具体到对应建立的连接，也可使用TCPView工具进行查看。如下，我们使用TCPView查到了2条连接：

> chenyu-57068a53.localdomain.2671-> 170.178.191.191:6667
>
> chenyu-57068a53.localdomain.2674-> amsterdam.nl.eu.undernet.org.6667

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730468_5c21f9a4ae540.png!small)

当我们分析病毒进程遇到困难的时候，其内存便是我们查找问题的最后一道防线。

以某Linux服务器应急事件为例子，如下图，我们找到三个病毒进程[ksoftirqd/7]的父子关系，可以看到，11275拉起了11276和11277，但11275是1号进程拉起来的，即init是其父进程。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730482_5c21f9b2d93b2.png!small)

这意味着，实际的父进程（原始病毒文件）在当前状态下是追查不到的了。

进程树已经追踪不到父进程了，能下手的地方不多。如反汇编[ksoftirqd/7]对应的病毒文件，则对于一次应急响应事件来说，时间是仓促的（不够）。但简单这样想，即不管病毒文件做了何种混淆、何种加壳，在最终运行于内存之上的代码上，终归是原始代码，至少堆栈就有不少信息。

Linux环境下dump内存，可以使用系统自带的gdb，键入命令 gdb attach
11275，attach到病毒进程11275，在gdb环境下，使用dump binary memory file start_addr
end_addr将11275有效内存空间dump下来。

譬如：file为输出文件，可以指定为 11275.dump，start_addr是起始地址，end_addr是终止地址，例 dump binary
memory /tmp/11275.dump 0x13838000 0x13839000 （这里仅仅只是举例，实际地址在gdb中获取）

对于内存文件11275.dump，采用命令 strings -n8 11275.dump，获取长度8及以上的字符串内容，我们发现有如下一行：

    
    
    /etc/security/ntps.conf

这是在病毒运行内存里面发现的，要么是病毒配置文件，要么是原始病毒文件。

我们 cd /etc/security 并使用 ls -al查看内容如下：

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730497_5c21f9c16a1ea.png!small)

可以看到，ntps.conf并非一个配置文件，它是可执行的（使用file命令可以知道这是个ELF可执行文件），文件修改时间应该是伪造的。

## 三、应急工具集简介

工欲善其事，必先利其器，所谓巧妇难为无米之炊，其实应急响应亦是如此。应急响应和安全研究人员，必须事先就备好完整一套的工具集，随时可以取用。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730511_5c21f9cf80793.png!small)

### 应急工具类型

>  **流量分析工具：**
> 常用的流量分析工具是Wireshark、TCPView，也可以使用科来网络分析工具，Linux下对tcpdump比较熟悉的，也可以使用tcpdump。
>
>  **进程分析工具：** 能对进程相关联信息进行分析的工具，主要是ProcessHacker和PC Hunter等。
>
>  **启动项分析工具：** 主要是AutoRuns工具，便于定位病毒启动项。
>
>  **专杀工具：** 有些流行病毒家族，通常对杀软有抑制性，或者本身有感染性，需要专杀工具去查杀和修复正常文件。
>
>  **辅助工具：** WinHex、文件Hash工具、Everything搜索工具、Unlocker文件解锁工具等。
>
>  **内存扫描工具：** 主要是MemScanner。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730524_5c21f9dc40d8a.png!small)

## 四、系统日志及日志分析

### 日志类型

>  **Windows系统日志：** Windows系统自带的审计日志、操作日志、故障日志。
>
>  **Linux系统日志：** Linux系统自带的审计日志、操作日志、故障日志。
>
>  **应用日志：** 包括但不限于Web应用等众多繁杂的日志。

 **Windows系统日志**

> 日志路径：C:\Windows\System32\winevt\Logs
>
> 必看日志：Security.evtx、System.evtx、Application.evtx

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730538_5c21f9eab112b.png!small)![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730539_5c21f9eb05c7a.png!small)![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730539_5c21f9eb0802b.png!small)

 **Linux系统日志**

> 日志路径：/var/log
>
> 必看日志：secure、history

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730557_5c21f9fd6c014.png!small)

多数日志都是可读易懂的，譬如很容易就能看出来，下面这个日志记录了ssh爆破过程。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730566_5c21fa06dbc27.png!small)

## 五、威胁情报的作用

在安全事件中，威胁情报有时候会给我们提供大量有用的信息，甚至直接推动了安全事件的快速响应。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730579_5c21fa139b000.png!small)

威胁情报的元素，包括但不限于域名、URL、IP、文件Hash、文件路径、文件名、数字签名、备案信息、排名信息。

威胁情报的获取源

> 谷歌：[www.google.com](http://www.google.com)
>
> 百度：[www.baidu.com](http://www.baidu.com)
>
> Virustotal：[www.virustotal.com](http://www.virustotal.com)
>
> 微步在线：x.threatbook.cn
>
> 腾讯哈勃：habo.qq.com
>
> Virscan：virusscan.jotti.org
>
> Freebuf：[www.freebuf.com](http://www.freebuf.com)
>
> Jotti：virusscan.jotti.org
>
> Scandir：[www.scandir.com](http://www.scandir.com)
>
> Alexa排名：[www.alexa.com](http://www.alexa.com)
>
> 备案查询：beian.cndns.com
>
> 深信服安全中心：sec.sangfor.com.cn
>
> 深信服威胁分析平台：wiki.sec.sangfor.com.cn
>
> 深信服EDR安全软件中心：edr.sangfor.com.cn

威胁情报中，域名扮演着极为基础和关键的角色，URL也是以域名为基础的。这里列举若干类域名，是属于黑客常用（偏爱）的域名，取证过程中需要重点关注这类域名的信息。

### 随机域名（DGA）：

内网IP利用特定的随机算法生成域名（DGA），同时黑客会利用该随机算法注册域名，这样就可以避免因为长期与某个域名或者IP通信而被封堵。

例如，内网某个源IP短时间内大量解析了如下域名（日志截图）

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730592_5c21fa2008630.png!small)

观察这些域名，可以发现，这些域名的“字符特征”看上去就是随机的。域名的发明（DNS）就是为了人类方便记忆而诞生的，所以，我们往往会去注册一些容易记忆且读起来朗朗上口的域名，显然例子中的域名就不具备这一特征。DGA这种反其道而行之的行为显然不是人访问网站发出来的，必然是病毒利用某种算法来实现的。

### 动态域名：

动态域名是子域名开放给其他人使用，并且子域名绑定的IP是可以动态获取的，大多数是免费的，因此常被黑客所使用，如 abc.3322.org
（3322.org就是动态域名提供者，子域名abc.3322.org可以被别人所使用）。

常见的动态域名提供商：

    
    
    'f3322.net','3322.org','7766.org','8866.org','9966.org','8800.org','2288.org','6600.org', 'f3322.org', 'ddns.net','xicp.net', 'vicp.net','wicp.net','oicp.net','xicp.net','vicp.cc','eicp.net','uicp.cn','51vip.biz','xicp.cn','uicp.net','vicp.hk','5166.info','coyo.eu','imblog.in','imzone.in','imshop.in','imbbs.in','imwork.net','iego.cn','vicp.co','iego.net','1366.co','1866.co','3utilities.com','bounceme.net','ddnsking.com','gotdns.ch','hopto.org','myftp.biz','myftp.org','myvnc.com','no-ip.biz','no-ip.info','no-ip.org','noip.me','redirectme.net','servebeer.com','serveblog.net','servecounterstrike.com','serveftp.com','servegame.com','servehalflife.com','servehttp.com','serveminecraft.net','servemp3.com','servepics.com','servequake.com','sytes.net','webhop.me','zapto.org','dynamic-dns.net','epac.to','longmusic.com','compress.to','wikaba.com','zzux.com','dumb1.com','1dumb.com','onedumb.com','wha.la','youdontcare.com','yourtrap.com','2waky.com','sexidude.com','mefound.com','organiccrap.com','toythieves.com','justdied.com','jungleheart.com','mrbasic.com','mrbonus.com','x24hr.com','dns04.com','dns05.com','zyns.com','my03.com','fartit.com','itemdb.com','instanthq.com','xxuz.com','jkub.com','itsaol.com','faqserv.com','jetos.com','qpoe.com','qhigh.com','vizvaz.com','mrface.com','isasecret.com','mrslove.com','otzo.com','sellclassics.com','americanunfinished.com','serveusers.com','serveuser.com','freetcp.com','ddns.info','ns01.info','ns02.info','myftp.info','mydad.info','mymom.info','mypicture.info','myz.info','squirly.info','toh.info','xxxy.info','free[www.info](http://www.info)','freeddns.com','myddns.com','dynamicdns.biz','ns01.biz','ns02.biz','xxxy.biz','sexxxy.biz','free[www.biz](http://www.biz)','www1.biz','dhcp.biz','edns.biz','ftp1.biz','my[www.biz](http://www.biz)','gr8domain.biz','gr8name.biz','ftpserver.biz','wwwhost.biz','moneyhome.biz','port25.biz','esmtp.biz','sixth.biz','ninth.biz','got-game.org','bigmoney.biz','dns2.us','dns1.us','ns02.us','ns01.us','almostmy.com','ocry.com','ourhobby.com','pcanywhere.net','ygto.com','ddns.ms','ddns.us','gettrials.com','4mydomain.com','25u.com','4dq.com','4pu.com','3-a.net','dsmtp.com','mynumber.org','ns1.name','ns2.name','ns3.name','changeip.name','ddns.name','rebatesrule.net','ezua.com','sendsmtp.com','trickip.net','trickip.org','dnsrd.com','lflinkup.com','lflinkup.net','lflinkup.org','lflink.com','dns-dns.com','proxydns.com','myftp.name','dyndns.pro','changeip.net','mysecondarydns.com','changeip.org','dns-stuff.com','dynssl.com','mylftv.com','mynetav.net','mynetav.org','ikwb.com','acmetoy.com','ddns.mobi','dnset.com','authorizeddns.net','authorizeddns.org','authorizeddns.us','cleansite.biz'。

f3322.net、3322.org、7766.org等等这些就是动态域名提供商。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730607_5c21fa2fbdd9a.png!small)

sjb555.3322.org就是一个动态域名，在VirusTotal上被标记为恶意的。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730619_5c21fa3b9d366.png!small)
这类域名常常是病毒的温床，不管是国家互联网应急中心，还是中国反网络病毒联盟，都是重点观察对象。企业级用户很少会主动去使用动态域名。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730633_5c21fa49e267d.png!small)

### 近期域名：

域名都是有创建时间（注册时间）的，Alexa全球排名百万之内的域名，都是很早之前就注册了的，从几年到十几、二十几年不等。黑客攻击要逃避防火墙的封堵，极可能在实施的时候，再去注册一个域名。注册一个字母长度大于7的域名，费用并不高，甚至可以低至
8元/年（还有些是免费的）。黑客之所以倾向这么做，是因为旧域名，很可能已经被安全机构列入黑名单中（也就是说，已经被封堵了）。

试想，企业级用户，无缘无故为什么要去访问一个刚刚注册的域名呢？

例如，防火墙产生日志如下，观察到，日志产生时间为 2016年1月27日，访问的站点为 cazwmwez.info。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730646_5c21fa5682d6e.png!small)

接下来，我们来查查该域名的注册时间。

方式：通过VirusTotal查询即可。在Whois lookup这一栏，如图，观察Creation Date即注册时间为
2016年1月12日，RegistryExpiry Date即过期时间 为
1年之后。很明显，这个是一个刚刚注册且很短命的域名（此域名来源于某一真实中毒客户，当时介入取证调查时间点为2016年2月初，也就是说不到1个月），域名的所有者并没有打算长期维护。此外，域名的所有者也不是客户的（询问客户得知）。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730662_5c21fa665569e.png!small)

### 暗网代理域名：

暗网，也叫Tor网络，此网络的访问、传输流量是不可追踪溯源的，因此是黑色产业链的温床。要访问暗网，要么病毒自己实现Tor客户端，要么通过Tor代理来访问Tor网络，而通过Tor代理访问的流量是未加密的，其直接使用Tor代理访问Tor站点服务器。

因此，暗网代理域名是可以被检测到的。

例如访问<https://abbujjh5vqtq77wg.onion.link/>由于二级域名onion.link属于Tor代理域名，所以认定此次访问行为是Tor网络访问行为，且为非法访问可能性极高。

### 顶级域名：

不是所有的顶级域名都需要特别关注，要从客户业务出发，去反推客户主机为何要访问相关的顶级域名。也就是说，这里面有一批顶级域名，实际客户业务是不需要去访问的，那么剩下的就只有黑客行为了。下表给出的，就是这样一批顶级域名（包括但不限于以下顶级域名）：

顶级域名  |  申请地区或机构  |  为何重点关注  
---|---|---  
.ru  |  俄罗斯  |  俄罗斯盛产黑客  
.ws  |
[东萨摩亚](https://baike.baidu.com/item/%E4%B8%9C%E8%90%A8%E6%91%A9%E4%BA%9A) |
不知名国家，易申请，难追踪注册者  
.cc  |
[科科斯群岛](https://baike.baidu.com/item/%E7%A7%91%E7%A7%91%E6%96%AF%E7%BE%A4%E5%B2%9B)
|  不知名国家，易申请，难追踪注册者  
.pw  |  帕劳  |  不知名国家，易申请，难追踪注册者  
.bz  |  [伯利兹](https://baike.baidu.com/item/%E4%BC%AF%E5%88%A9%E5%85%B9) |
不知名国家，易申请，难追踪注册者  
.su  |  苏联  |  前苏联虽然解体了，顶级域名还在使用，且多与黑产有关  
.bw  |  伯兹瓦纳  |  不知名国家，易申请，难追踪注册者  
.gw  |
[几内亚比绍](https://baike.baidu.com/item/%E5%87%A0%E5%86%85%E4%BA%9A%E6%AF%94%E7%BB%8D)
|  不知名国家，易申请，难追踪注册者  
.ms  |
[蒙塞拉特岛](https://baike.baidu.com/item/%E8%92%99%E5%A1%9E%E6%8B%89%E7%89%B9%E5%B2%9B)
|  不知名国家，易申请，难追踪注册者  
.mz  |
[莫桑比克](https://baike.baidu.com/item/%E8%8E%AB%E6%A1%91%E6%AF%94%E5%85%8B) |
不知名国家，易申请，难追踪注册者  
  
这里举个例子，我们在某台告警主机上，使用Wireshark抓网络网络，直接过滤DNS协议如下：

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730679_5c21fa7721aa1.png!small)

可以看到，此主机解析了大量.pw站点的域名，如koqqveoukgjc.pw，.pw是帕劳国家顶级域名，此国家是一个非常小的岛国，跟中国大陆都没有建交，国内企业有需要访问他们站点的可能性低到零（或者有业务在帕劳的可能性）。

## 六、常见病毒及分类

勒索病毒：能对用户文件进行加密的病毒。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730693_5c21fa8509fcf.png!small)

挖矿病毒：消耗用户CPU、GPU资源，进行大量运算，获取加密货币的病毒。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730706_5c21fa923a706.png!small)

>  **蠕虫：** 自动复制自身的副本到其它主机的病毒。
>
>  **木马：** 隐蔽性强，多用于监控用户行为或盗取用户数据的病毒。
>
>  **感染型病毒：** 能将自身恶意代码插入正常文件的病毒。
>
>  **脚本病毒：** 使用脚本编写的病毒。
>
>  **宏病毒：**
> 宏是微软公司为其Office软件包设计的一个特殊功能，由于其功能强大，使得黑客可以通过精心构造的宏代码来实现恶意操作，这些代码就叫做宏病毒。宏病毒常以垃圾邮件的方式对用户进行攻击，因为伪造的Office文档不容易引起用户的怀疑，所以当用户毫无防备的打开Office文档并启用宏之后，宏病毒便开始了运行，对用户主机进行恶意操作。
>
>  **僵尸网络病毒：** 能形成大型的一对多，多对多控制的远程控制病毒。
>
>  **后门：** 在主机上开放端口允许远程非授权访问。

以感染型病毒为例，需要知道并了解其原理：

正常PE文件的执行流程入下：

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730722_5c21faa24c85f.png!small)

> [1] 从PE头中提取入口点地址EP。
>
> [2] 定位到EP处的PE代码。
>
> [3] 开始执行PE代码。

被感染的PE文件的执行流程入下，其中多了恶意代码环节：

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730734_5c21faae0e52e.png!small)

>  
> [1] 从PE头中提取入口点地址EP。
>
> [2] 通过篡改EP或覆盖原始入口点代码的方式，使EP指向恶意代码。
>
> [3] 执行恶意代码。
>
> [4] 恶意代码执行完后，跳回到原PE代码处执行。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730745_5c21fab99726c.png!small)

虽然感染的总体思路都是让宿主文件先执行恶意代码，执行完后再跳回到原始代码，但每种病毒家族实现的方式却不尽相同。我总结为四类，复杂度由低到高依次为：偏移式、覆盖式、加密式、混淆式。

 **专业术语：** 入口点EP（Entry Point），原始入口点OEP（Original Entry Point）。

偏移式是最多感染型病毒使用的感染方式，病毒会将恶意代码注入到宿主文件的一个空闲位置，然后修改PE头中的EP地址，使其指向恶意代码起始处。被感染文件运行后就会先执行恶意代码，恶意代码执行完成后，会获取OEP的偏移（每个病毒家族的OEP偏移值藏在不同的地方），然后将执行流跳回到OEP处，执行宿主文件原始代码。

## 七、理解漏洞和补丁

漏洞和补丁，在应急响应中是不可或缺。如果黑客是通过某种漏洞入侵系统的，而在应急响应中，无法找出黑客所利用的漏洞，就会意味着，入侵行为可以反复发生。在终端侧，就会表现为病毒清理不干净，杀了又来，所以一定要找出漏洞。

找到漏洞后，就需要打上相应的补丁，这样才是一次完整的处置。

怎么查看系统补丁情况？以Windows为例，直接打开cmd，输入命令systeminfo即可获取。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730763_5c21facbee662.png!small)![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730764_5c21facc03917.png!small)

>  **漏洞是什么：** 漏洞是指一个系统存在的弱点或缺陷。
>
>  **怎么来的：** 系统设计时的缺陷或编码时产生的错误。
>
>  **有什么后果：** 黑客的侵入及病毒的驻留，数据丢失和篡改、隐私泄露，系统被控制并作为入侵其他主机系统的跳板，等等。
>
>  **解决方法：** 打补丁。

## 八、技能提升建议

多关注安全信息：多关注安全公司发布的一些安全信息，多关注，多学习。

多研读安全书籍：多研读安全书籍，推荐《恶意代码分析实战》等。

![应急响应的整体思路和基本流程](https://image.3001.net/images/20181225/1545730774_5c21fad653c35.png!small)

>  **多逛安全论坛：** 推荐多看看Freebuf、看雪学院等。
>
>  **多在安全沟通群里问：** 不懂就问。
>
>  **多实践：** 多实践，出了安全问题，多尝试自己动手解决。

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM**

