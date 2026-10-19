​WiFi中断攻击是指通过发送取消认证报文让客户端以为路由器需要让自己断开连接从而断开WiFi，伪造路由器向客户端发送取消认证报文，使客户端主动断开WiFi连接。

WiFi中断后有可能注入钓鱼，轻则泄露密码，重则攻击主机，需要用户注意安全防护。今天分享一个WiFi中断攻击实验，欢迎大家交流讨论。

##  **01**

先将ESP8266开发板接入PC，在设备管理器中可看到开发板信息。

![v2-1cb2883c6e632c61e6f911fbb2e6605c_720w.jpg](https://image.3001.net/images/20210512/1620810475_609b9aeb0ffa3ece5d95b.jpg!small)

##  **02**

如果无法在端口中无法发现开发板，需要安装ESP8266开发驱动。

![v2-a9a834fc35c2aed388d8200c9ca56a52_720w.jpg](https://image.3001.net/images/20210512/1620810475_609b9aeb569525338489d.jpg!small)

安装完驱动后，就可看到ESP8266开发板。

##  **03**

使用python安装esptool和pyserial，安装esptool，使用命令：

    
    
    Pip install esptool

![v2-4875553bd9e48b9a3707c4aa7152f2e2_720w.jpg](https://image.3001.net/images/20210512/1620810475_609b9aebbbf0b1c48cf7c.jpg!small)

安装pyserial，使用命令：

    
    
    Pip install pyserial

![v2-64fade1e807b9f62f38de818050a4612_720w.jpg](https://image.3001.net/images/20210512/1620810476_609b9aec118670780df6f.jpg!small)

##  **04**

擦除ESP8266开发板。

如果开发板之前有使用过，就会留有之前开发板上的相应烧录代码，使用esptool擦除开发板可用命令：

    
    
    esptool.exe --port COM3(硬件对应COM端口) erase_flash     擦除开发板

![v2-b8c2f3f2cd7ff32183ff914446d8c1d2_720w.jpg](https://image.3001.net/images/20210512/1620810476_609b9aec6419e74e1dfc9.jpg!small)

直到开发板蓝灯闪烁结束即擦除完毕，如果出现下面类似错误。

![v2-fbceeb1bfbf7fd9365ca5213d3afe706_720w.jpg](https://image.3001.net/images/20210512/1620810476_609b9aecc9ce1f5c81a72.jpg!small)

需要在执行擦除命令前，让ESP8266进入升级模式，即按住板上的flash键不放，按下rst键，等待两秒，松开rst键，再松开flash键。

##  **05**

打开ESP8266flasher.exe，选择开发板对应的COM端口。

![v2-da93c694920be0668f17d8d0c780551a_720w.jpg](https://image.3001.net/images/20210512/1620810477_609b9aed4ebc00569c4ac.jpg!small)

##  **06**

选择config选项卡，设置文件为Wi-PWN.ino.CH.bin

![v2-cd2e61f327b3f0eaf29e6d2ef45f936f_720w.jpg](https://image.3001.net/images/20210512/1620810477_609b9aedc40aef563a051.jpg!small)

##  **07**

选择advanced选项卡，进行设置。

设置信息应对应ESP8266开发板上相关信息，以下为个人使用ESP8266开发板信息：

Baudrate（波特率）：115200

Flash size（内存大小）：4Mbyte

Flash speed（内存速度）：40MHz

SPI Mode（SPI模式）：QIO

![v2-1287985e6ec07033a6fe191e93e9f89e_720w.jpg](https://image.3001.net/images/20210512/1620810478_609b9aee32d66ecf048ca.jpg!small)

##  **08**

回到Operation选项卡，选择Flash烧录，烧录完成后，左下角会打绿勾。

![v2-aad1cd42886ed840ac68749bf740f990_720w.jpg](https://image.3001.net/images/20210512/1620810478_609b9aee95ed64daad0fc.jpg!small)

##  **09**

此时按ESP8266上的RTS复位键或者拔出USB再插入，重启ESP8266。

之后在网络连接处可搜索到名为WI-PWN的WiFi。

![v2-98b97766ba43b5ed66b908ea199ca426_720w.jpg](https://image.3001.net/images/20210512/1620810479_609b9aef0005c19a5e64b.jpg!small)

##  **10**

连接上WI-PWN的WiFi之后，打开浏览器，访问192.168.4.1会进入攻击初始页面（有时浏览器无法打开，需要用手机打开）。

![v2-37b8e477478458454f5664565e555188_720w.jpg](https://image.3001.net/images/20210512/1620810479_609b9aef64304340b078d.jpg!small)

##  **11**

点击接受后可更改SSID（WiFi名称）和密码，WiFi即更改。

![v2-d02418086d009404a3c161c425e58455_720w.jpg](https://image.3001.net/images/20210512/1620810479_609b9aefb27ed70488c91.jpg!small)

可搜索到一个命名的WiFi。

![v2-49b3d6e43a1a4cec7dd77a059c41b1b1_720w.jpg](https://image.3001.net/images/20210512/1620810480_609b9af0255ee988c516f.jpg!small)

使用之前设计的账号和密码，登录，访问192.168.4.1。

![v2-28955ba176025cb13f6a08179d26688d_720w.jpg](https://image.3001.net/images/20210512/1620810480_609b9af085d8a0bba91b3.jpg!small)

即可扫描到附近所有的WiFi。

##  **12**

勾选想要攻击的WiFi，点击攻击。

![v2-62252369dc21b1de601fa2c6e2cc1733_720w.jpg](https://image.3001.net/images/20210512/1620810480_609b9af0f23bceaf764eb.jpg!small)

##  **13**

![v2-f2c3dcc47afccd5338166ce71e4a315c_720w.jpg](https://image.3001.net/images/20210512/1620810481_609b9af151eac95dc7d99.jpg!small)

从选项中选择攻击方式。

 **Deauth-认证攻击：**
向选定的WiFi接入点中的所选客户端发送去认证帧和解离帧。即可通过该方法使指定WiFi中断。（注意：如果没有选择客户端，报文将作为广播发送！）

 **Beacon-洪水攻击-clone：** 垃圾邮件具有与所选WiFi接入点相似的SSID的信标帧。

 **Beacon-洪水攻击-list：** 垃圾邮件信标帧与下面列表中的所有SSID。

 **Probe-request-探测请求洪水攻击：** 以下列表中的所有SSID的垃圾邮件探测请求帧。有效的混淆和垃圾邮件的WiFi追踪器。

可以选择完用户后，选择克隆的WIFI SSID以及X个数，可以克隆出X个指定名字（或随机名字）的开放WiFi。

选择使用Deauth-认证攻击攻击指定WiFi，该WiFi会马上被中断，然后一段时间后重启。所以可以在中断的这段时间将被中断WiFi的SSID进行克隆，然后放上钓鱼页面，轻则泄露原本WiFi密码，重则可能被控制主机。

