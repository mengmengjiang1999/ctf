## 前言

wifi攻击包括wifi中断攻击，wifi密码爆破，wifi钓鱼等。

本文章持续更新以上内容，先以wifi中断攻击为始，硬件为ESP8266（还买了一个无线网卡用作后续wifi密码爆破），网上某宝十几块钱就能玩，我买的是带Micro接口，省的买串口下载器了。

下小雨了，吃完饭，换身厚的衣服出去转了一圈，雨声听着真舒服，听着张国荣的歌，又放松又惬意。废话不多说，开干

### wifi中断攻击之ESP8266

wifi中断攻击是通过伪造取消认证报文发送给路由器，使路由器的客户端主动断开wifi连接。利用802.11W协议漏洞，对WiFi用户发起deauth攻击，来解除合法wifi用户的无线认证关系，从而使wifi用户无法连接到自己家的wifi。

#### 驱动安装

1、首先需要在主机上安装ESP8266的驱动，如果没有驱动的话，插入开发板不会显示，也就无法烧录程序

![image-20210828214127669](https://image.3001.net/images/20210829/1630170146_612a6c22c49b0e51ad7be.png!small)

![image-20210828214243950](https://image.3001.net/images/20210829/1630170155_612a6c2b6961d77b1d45d.png!small)

![image-20210828214326328](https://image.3001.net/images/20210829/1630170167_612a6c3731e5e139435b9.png!small)

2、驱动安装好后，把ESP8266接入主机，在设备管理器中可以看到ESP8266开发板的信息。兄弟们一定要找一根数据线，就是能传数据的线，充电宝、耳机充电的短线亲测不能用，安卓机正常充电的长线就行，我在这里就鼓捣了好一会

![image-20210828221605644](https://image.3001.net/images/20210829/1630170177_612a6c41ed13cf6f57e0c.png!small)

![img](https://image.3001.net/images/20210829/1630170188_612a6c4cb0110306031e6.jpg!small)

程序烧写

1、打开ESP8266 Flasher.exe 烧写工具，它已经自动识别端口COM8

![image-20210828221851046](https://image.3001.net/images/20210829/1630170217_612a6c69892b1aa2d34e5.png!small)

2、点击config，选择wi-pwn的bin文件，固件wi-pwn具有先进的渗透功能和良好的操作界面，配置了很多的攻击方式。

![image-20210828222313188](https://image.3001.net/images/20210829/1630170230_612a6c76708db88826d8e.png!small)

3、点击advanced按钮

baudrate(波特率)选择115200

Flash size(内存大小)选择4Mbyte

flash speed（内存速度）选择40Mhz

SPI Mode（SPI模式）选择QIO。

这界面突如其来的亲切感，界面跟普中一样，虽然丑但简单有效，让我想到了读大学时候，学51单片机用普中烧录C程序的感觉，天天焊什么点阵屏，智能小车，新型流水灯，各种花里胡哨的流水方式，还有带音乐的，实验室里各种焊锡，松香味，绝了哈哈哈哈

![image-20210828223832139](https://image.3001.net/images/20210829/1630170241_612a6c81b800a77567577.png!small)

4、回到operation，点击flash，开始烧，这时候ESP8266上的闪光灯开始闪

![image-20210828224254539](https://image.3001.net/images/20210829/1630170304_612a6cc0886de7ea5922b.png!small)

![lADPDhJzxXDLTp_NBH7NA50_925_1150.jpg_720x720q90g.jpg?bizType=im](https://image.3001.net/images/20210829/1630170800_612a6eb0a6cb5265d8d58.jpg!small)

5、烧写完成，就会在左下角显示绿勾，对，你看这个绿的颜色像不像曾经emmmmm

![image-20210828224516085](https://image.3001.net/images/20210829/1630170316_612a6cccb8d15a28537af.png!small)

6、烧写完成后，按下ESP8266上的RST复位键，或者在电源上重新插拔下，搜索wifi，就可以看到wi-pwn，连接上，在浏览器中输入192.168.4.1（电脑、手机都可以）就能进入配置界面，在这里我在手机上配置，电脑连接家里的wifi，攻击下家里的wifi试下效果。

![image-20210828225022159](https://image.3001.net/images/20210829/1630170343_612a6ce78af1340d3e541.png!small)

攻击配置

1、初始页面警告，哈哈哈哈

![img](https://image.3001.net/images/20210829/1630170355_612a6cf300d8655a48a0d.jpg!small)

2、上面点击接受后，进入ESP8266的配置界面，SSID后期我改成了J2W，密码是rootaccess

![img](https://image.3001.net/images/20210829/1630170379_612a6d0b165c524747f1a.jpg!small)

3、扫描下当前环境下存在的无线网络，隐藏的无线网也能扫出来（这个可以在设置中，勾选扫描隐藏的网络）

![img](https://image.3001.net/images/20210829/1630170396_612a6d1c5e095cad87ff3.jpg!small)

4、我家中的网络SSID是1805，勾选1805到右面用户中去扫描，探测该网络下的用户有多少个，后面显示的是MAC地址，确定该网络下电脑只有我这一台，处理器是Intel，所以下面那个Intel是我电脑的MAC地址，为什么该wifi网络下有这么多Mac地址，因为我的小爱同学，小米台灯，好几个智能插排都是连无线网络控制的，这都给扫出来了

  

![img](https://image.3001.net/images/20210829/1630170410_612a6d2ace6217de166b7.jpg!small)

5、到攻击这里，聊一聊图中的几种攻击方式

![img](https://image.3001.net/images/20210829/1630170428_612a6d3c065748b17469d.jpg!small)

 **Deauth（认证攻击）**
：向选中的wifi接入点的客户端发送认证帧和解离帧，通过deauth的方式指定wifi中断，如果第一个扫描网络那里没有勾选客户端的话，在攻击这里，deauth发送的报文将作为广播的形式发送。

![image-20210828232231173](https://image.3001.net/images/20210829/1630170447_612a6d4f8787b18f12f54.png!small)

![image-20210828233453535](https://image.3001.net/images/20210829/1630170455_612a6d5734b38ab5bc6a1.png!small)

 **beacon（洪水攻击）**
：克隆出的垃圾wifi接入点具有与所选的wifi接入点相似SSID的信标帧，上面wifi中断后，克隆出大量相似的信标帧，有够恶心的，48个1805假信标帧给我上，要是忘记密码，指定是找不着哪个才真是自家wifi了。对了，克隆出的SSID还可以设置统一的密码，手机探测时候都有锁的标识(下面这个我没有设置)，跟真的一毛一样，摊手

![img](https://image.3001.net/images/20210829/1630170475_612a6d6b9fd3538bf9836.jpg!small)

 **radom** ：列出与列表中所有的SSID相似的垃圾信标帧，attack一下，我人傻了，就嗯搅局呗？？

![img](https://image.3001.net/images/20210829/1630170487_612a6d7794b45244d924f.jpg!small)

![img](https://image.3001.net/images/20210829/1630170494_612a6d7ea266fc8b68159.jpg!small)

probe-request：对隐藏wifi请求洪水攻击。如果某AP的SSID是隐藏的，通常手机发送的普通的probe
request包是无法获取到隐藏的SSID，就像上面，有些SSID手机根本就探测不到，esp8266就能，这跟probe-request的SSID长度有关系，效果也是上面那样，隐藏的SSID给克隆出一大堆。

## 后记

在尝试过程中，发现在选择death认证攻击指定SSID后，会中断一次后重启。

