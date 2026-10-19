## **0x00** **前言**

**都听过一句话，没有网络安全就没有国家安全，网络安全一直是这几年的热议话题，未来战争是一个多元化的战争，网络战电子战成为主流必然是趋势所向。而信号干扰是这种战争的主流攻击手段，通过干扰手机、GPS、wifi，甚至卫星链路等电磁波的正常传输，可以影响到整个战争的走向。这里我们讨论的是基本的无线干扰，通过控制未加密的管理帧实现。**

802.11标准将所有的数据包分为3种：数据、管理、控制。

### 数据帧：

携带更高层次的数据，也是唯一可以从无线网络转发到有线网络的数据包

### 控制帧：

通常与数据帧搭配使用，负责区域的清空、信道的取得以及载波监听的维护，并于收到数据时予以正面的应答，借此促进工作站间数据传输的可靠性

### 管理帧：

信标帧(Beacons): 在无线设备中，定时依次按指定间隔发送的有规律的无线信号(类似心跳包)，主要用于定位和同步使用；

解除认证(Deauthentication)帧：解除身份认证，用于结束一段认证关系；

Probe(request and response)帧：探测区域内有哪些无线信号；

Authenticate(request and response)帧：身份验证；

Associate(request and response)帧：关联请求、响应；

Reassociate(request and
response)帧：位于相同扩展服务区域，但在不同基本服务区域间游走的移动式工作站，再次使用分布式系统时，必须与网络重新关联；

Dissassociate(notify) 帧：取消关联。

##  **0x01** **攻击原理**

仔细观察管理帧的类型就会发现，如果攻击者伪造MAC地址，对受害者ap或设备发送指定帧，就会造成目标设备或ap的巨大影响。具体技术手段如下：

 **第一种：**
验证洪水攻击，俗称Authdos，通过随机生成大量mac地址，伪装设备向ap发送大量身份验证Authenticate请求帧，使请求数量超出ap承载能力，从而造成拒绝服务攻击，使正常用户无法连接ap。

图示：![1.png](https://image.3001.net/images/20180815/1534263254_5b72ffd6825a8.png!small)

 **第二种：**
取消验证洪水攻击，俗称deauth攻击，通过伪造mac地址，伪装成目标ap已连接的设备，向ap发送Deauthentication解除认证帧，造成设备掉线，从而达到拒绝服务的目的。

图示：![2.png](https://image.3001.net/images/20180815/1534263263_5b72ffdf45dcb.png!small)

破解无线密码时经常用到这种攻击，利用deauth帧解除设备的连接，从而嗅探到设备再次连接时的握手包，通过字典中的大量密码匹配，爆破穷举出无线密码。

 **第三种：** 关联洪水攻击，俗称asso攻击，主要针对空密码或已破解密码的无线信号，伪造大量设备，淹没ap的关联表，使ap无法给正常用户建立关联

图示：![3.png](https://image.3001.net/images/20180815/1534263270_5b72ffe6b6802.png!small)

 **第四种：** 射频干扰攻击 RF jammingAttack，这种不再针对管理帧的漏洞，而是上升到物理干扰的层次，用噪声信号淹没射频信号导致系统失效。
这种干扰不分敌我，会影响到一片区域指定频带范围的信号，高考等重要国家考试屏蔽信号用的就是这个方法。

![4.png](https://image.3001.net/images/20180815/1534263342_5b73002ea8ec7.png!small)20米范围的手机干扰器

![5.jpg](https://image.3001.net/images/20180815/1534263387_5b73005b287f0.jpg!small)双频汽车干扰器（315MHz/433MHz）

![6.png](https://image.3001.net/images/20180815/1534263405_5b73006decd51.png!small)覆盖范围3-8m的2.4GHz屏蔽器

##  **0x02** **攻击工具**

纸上得来终觉浅，下面进行工具实操的演示：

第一个工具：aireplay-ng，这款工具利用的是上述中的deauth攻击。

首先：

    
    
    airmon-ngstart wlan0       将网卡置为监听模式
    
    airodump-ngwlan0mon –bssid 目标ap的ssid       开始侦听目标网络

![7.png](https://image.3001.net/images/20180815/1534263532_5b7300ec9b15b.png!small)

    
    
    aireplay-ng-0 0 -a ap的ssid-c 设备的ssid wlan0mon 开始攻击

![8.png](https://image.3001.net/images/20180815/1534263553_5b730101a63f3.png!small)

可以看到攻击起了作用，我的windows主机已经ping不通路由器了。

![9.png](https://image.3001.net/images/20180815/1534263571_5b7301137352c.png!small)

第二个工具：mdk3

这是mdk3的帮助文档：

![10.png](https://image.3001.net/images/20180815/1534263591_5b7301276bc92.png!small)

可以看到，a参数是第一种攻击——authdos攻击，d参数是第二种攻击——deauth攻击，b参数是信标泛洪攻击，伪造大量虚假ap，只能起到混淆的作用。

首先演示a参数，将网卡置成监听模式后，查找目标ap的mac地址：

    
    
    airodump-ngwlan0mon

找到后，使用mdk3 wlan0mon a -a mac地址发起攻击：

![11.png](https://image.3001.net/images/20180815/1534263612_5b73013c3f7f0.png!small)

发起攻击后，我的windows主机死活连不上ap，还会在连接过程中重启适配器：

![12.png](https://image.3001.net/images/20180815/1534263737_5b7301b99018b.png!small)

再来试一下d参数，先来看一下d参数的帮助文档：

![13.png](https://image.3001.net/images/20180815/1534263699_5b730193cf316.png!small)

直接用d参数看起来杀伤范围比较大，还是用一下黑名单功能，只干扰自己的设备吧。

先把目标ap的设备mac地址加入blacklists.txt黑名单：

    
    
    vimblack.txt

开始攻击：

    
    
    mdk3wlan0mon –c 目标ap的信道 –b~/blacklists.txt

![14.png](https://image.3001.net/images/20180815/1534263762_5b7301d298709.png!small)

干扰成功。

第三个工具：esp8266

![15.png](https://image.3001.net/images/20180815/1534263826_5b7302123167c.png!small)

这是一款低功耗、高度集成的wifi芯片，将程序烧录进去后，用充电宝供电，不需要kali和无线适配器，也能进行无线干扰攻击，非常便携。

程序烧录后，手机连接控制板子的wifi，进入管理页面：

![16.png](https://image.3001.net/images/20180815/1534263852_5b73022c6f894.png!small)

选择好目标ap后，发起deauth攻击：

![17.png](https://image.3001.net/images/20180815/1534263896_5b73025808364.png!small)

被断开连接了。

第四个工具：airgeddon

安装：

    
    
    git clone <https://github.com/v1s1t0r1sh3r3/airgeddon.git>  
    cd airgeddon   
    sudo bash airgeddon.sh

选择无线网卡：

![18.png](https://image.3001.net/images/20180815/1534263921_5b730271ab7ba.png!small)

进入监听模式，并开始dos攻击：![19.png](https://image.3001.net/images/20180815/1534263948_5b73028c00dd8.png!small)![20.png](https://image.3001.net/images/20180815/1534263978_5b7302aa896aa.png!small)

这款工具其实就是很多工具的集合，最后调用的还是mdk3和aireplay，只是设计的更新手化一些。

##  **0x03** **检测及防御手段**

以上工具演示完可以发现，想要进行无线干扰攻击非常简单，不需要任何基础就可以对无线网络造成巨大影响。虽然脚本小子很容易就能破坏网络，但是他们也很容易被发现。

对于检测攻击来说，kismet和wireshark等嗅探工具都是不错的选择。如果想对网络发起监控，对可疑行为报警，可以选择kismet。如果想获得更多的packet信息，可以选择wireshark、omnipeek、commview等抓包工具，具体取决于哪款支持你的无线网卡。因为commview支持我的笔记本集成网卡，下面就用它来做一个抓包演示：

![21.png](https://image.3001.net/images/20180815/1534264089_5b73031981c33.png!small)选择只抓管理帧的包并忽略beacons帧

aireplay-ng的取消验证洪水攻击：![22.png](https://image.3001.net/images/20180815/1534264110_5b73032ee3bbd.png!small)

可以看到大量的deauth解除认证帧。

mdk3的身份验证洪水攻击：![23.png](https://image.3001.net/images/20180815/1534264122_5b73033ad339b.png!small)

可以看到大量设备的身份验证请求。

配合esp8266和kali来演示一下kismet的用法:

输入 sudo kismet –c wlan0mon
就进入了kistmet的主界面：![24.png](https://image.3001.net/images/20180815/1534264146_5b73035285174.png!small)![25.png](https://image.3001.net/images/20180815/1534264178_5b730372d8cf2.png!small)

windows-alerts选项，可以在检测到异常情况时报警。

用esp8266发起deauth攻击：![26.png](https://image.3001.net/images/20180815/1534264203_5b73038b34301.png!small)

检测到了攻击。

可以发现，虽然干扰攻击很容易被检测到，但是很难取证，因为源头的mac地址都是伪造的，所以提前做好防御才是解决的方法。

为防止这类攻击，最佳解决防范是尽量使用以太网，避免无线网络。如果必须使用，可以采取降低无线功率的手段降低被攻击概率，但大多数物联网设备都不具备这个功能。其实也不必担心，WPA3已经慢慢出现在公众的视线中，wpa3和wpa2核心差异之一是不允许伪造身份验证或解除关联数据帧，如果你的设备支持wpa3，可以升级以杜绝无线干扰攻击。

## 参考：

<http://www.cnblogs.com/littlehann/p/3700357.html>

<https://www.tripwire.com/state-of-security/security-awareness/radio-killed-the-security-of-things-rf-jammers-crime/>

<http://sccsec.com/2016/11/23/WIFI%E5%AE%89%E5%85%A8%E4%B9%8B%E5%8C%85%E7%BB%93%E6%9E%84%E8%A7%A3%E6%9E%90/>

 ***本文作者：thr0cyte，转载请注明来自FreeBuf.COM**

