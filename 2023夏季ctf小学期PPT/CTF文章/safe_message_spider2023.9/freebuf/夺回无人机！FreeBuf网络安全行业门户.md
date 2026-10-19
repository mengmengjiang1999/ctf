**识链实验室@李饼饼**  
李某人今天新买了个无人机~  
![](https://image.3001.net/images/20211118/1637237363_619642730331ab20dd90c.png!small)  
美滋滋想飞一飞再拆解研究固件时.....  
![](https://image.3001.net/images/20211118/1637237378_61964282518b4d7fa9847.png!small)  
面对砂锅大的拳头，李某人觉得还是以同事间的感情为重！  
![](https://image.3001.net/images/20211118/1637237417_619642a9319ef58a3cd18.png!small)  
哼~搁那儿研究呢  
![](https://image.3001.net/images/20211118/1637237426_619642b2ed525ee287f7d.png!small)  
李某人决定用知识夺回心爱的无人机！  
首先IOT设备通常脆弱点为：Web端漏洞、APP端漏洞、固件漏洞、无线电通信漏洞、硬件漏洞  
无人机这类设备通常可以以无线电通信为切入点(固件被抢走了还没来得及研究)  
既然讲到无人机无线电通信，第一时间想到的当然是WiFi，而且既然是新设备处于未配置状态，大概率连接是空口令或者弱口令，如果设备没有绑MAC地址，用常规的WiFi渗透思路通过发包让对方设备掉线，然后重新用客户端连接并接管设备理论上是可行的，接着来试试~  
1.启动kali，iwconfig查看无线网卡配置  
![](https://image.3001.net/images/20211118/1637237441_619642c1136c9f367c6c3.png!small)  
2.airmon-ng start wlan0将wlan0开启监听模式  
![](https://image.3001.net/images/20211118/1637237449_619642c981b961c3e8b1e.png!small)  
3.airodump-ng wlan0mon扫描网络，TELLO-EE8A75，就是你了  
BSSID：WiFi MAC地址  
PWR：信号强度  
BEACONS：信标  
DATA：数据  
CH：信道  
ENS：加密方式，图中OPN为开放  
ESSID：WiFi名称  
![](https://image.3001.net/images/20211118/1637237463_619642d706c938bea9eee.png!small)  
4.新建个终端airodump-ng wlan0mon --bssid <BSSID> \--channel 9  
STATION为无人机MAC地址  
![](https://image.3001.net/images/20211118/1637237475_619642e3220a9229436d4.png!small)  
5.再新建个终端aireplay-ng --deauth 0 -c <STATION> -a <BSSID> wlan0mon看看效果去~  
\--deauth为冲突攻击模式，0为循环攻击  
![](https://image.3001.net/images/20211118/1637237485_619642edf39bbd3087dae.png!small)  
6.屏都黑了，还搁那儿研究呢  
![](https://image.3001.net/images/20211118/1637237499_619642fbde813a9100833.png!small)  
7.登录APP客户端，成功夺回  
![](https://image.3001.net/images/20211118/1637237520_61964310ecb44b949eaa1.png!small)  
市面上无人机安全问题各个层面层出不穷，这里仅提供简单思路，供各位举一反三，之后拆解设备分析固件安全问题。

