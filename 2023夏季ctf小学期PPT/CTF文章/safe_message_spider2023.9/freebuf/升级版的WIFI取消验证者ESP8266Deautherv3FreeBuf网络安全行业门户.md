**前言：本文内容仅供学习、参考，禁止任何违法的网络攻击行为。人皆有情，国法无情！**

近几年ESP8266的Deauther v2被极客们玩的不亦乐乎，最近SpacehuhnTech更新出了Deauther的v3版本。

据官网给的信息，v3版本取消了AP和网页控制功能，使用串口命令行控制，功能更多，稳定性更强，可定制化程度更高。![1614578882_603c84c29797483df4a56.png!small](https://image.3001.net/images/20210301/1614578882_603c84c29797483df4a56.png!small)

而且还推出了v3的专用连接工具Huhnitor，其他任意支持波特率115200的串口工具也能够使用

![1614579377_603c86b1ba07774c5cc6b.png!small](https://image.3001.net/images/20210301/1614579377_603c86b1ba07774c5cc6b.png!small)

现在我们开始入手Deauther v3吧！

所需工具：#ESP8266模块x1，#电脑一台，

演示环境：#Windows 10 x64 专业版，#Ubuntu server 20.10 x64

### 0x01 烧录：

最常见的ESP8266模块TTL芯片是CP210x和CH34x，[CP210x驱动下载](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)[CH34x驱动下载](http://www.wch-ic.com/search?q=cH341&t=downloads)（看不懂英文没关系，这些驱动都烂大街了，随便百度下就能找到资源，但是有些可能会带病毒）

烧录我们使用乐鑫官方的烧录工具[flash_download_tool_v3.8.5_1.zip](https://www.espressif.com/sites/default/files/tools/flash_download_tool_v3.8.5_1.zip)

v3固件下载地址：[github官方下载](http://github.com/SpacehuhnTech/nightly-deauther/releases/download/nightly/esp8266_deauther_V3_1M_Nightly.bin)[fastgit.org镜像站下载](https://download.fastgit.org/SpacehuhnTech/nightly-deauther/releases/download/nightly/esp8266_deauther_V3_1M_Nightly.bin)

将模块连接到电脑，安装好驱动后重启电脑，解压烧录工具，运行文件夹内的flash_download_tool_v3.8.5.exe。再弹出界面选择Developer
Mode>>ESP8266 DownloadTool

![1614580394_603c8aaae662b8937a25b.png!small](https://image.3001.net/images/20210301/1614580394_603c8aaae662b8937a25b.png!small)

![1614580473_603c8af94bec8595bd1a7.png!small](https://image.3001.net/images/20210301/1614580473_603c8af94bec8595bd1a7.png!small)

选择固件和烧录地址，选择串口，波特率推荐115200，我这里是COM4，如果只有COM1的请检查数据线或者驱动是否装好。参考下图

![1614580918_603c8cb68347ba1a43b32.png!small](https://image.3001.net/images/20210301/1614580918_603c8cb68347ba1a43b32.png!small)

然后将ESP8266进入烧录模式，START开始烧录，这样就是烧录完成了![1614581039_603c8d2f97ba5bf693bbb.png!small](https://image.3001.net/images/20210301/1614581039_603c8d2f97ba5bf693bbb.png!small)

### 0x02 客户端安装：

#Windows客户端：

关闭烧录工具，重启模块，打开Huhnitor（其他串口软件也可以）。Huhnitor下载：[github官网](https://github.com/SpacehuhnTech/Huhnitor/releases)[fastgit.org镜像站](https://hub.fastgit.org/SpacehuhnTech/Huhnitor/releases)（win10防火墙可能会拦截运行，忽略即可）

运行截图![1614581590_603c8f56263728cb0511c.png!small](https://image.3001.net/images/20210301/1614581590_603c8f56263728cb0511c.png!small)

#Linux客户端（root用户，非root用户请在头部加上sudo）

打开终端输入

wget
<https://download.fastgit.org/SpacehuhnTech/Huhnitor/releases/download/1.1.2/huhnitor_1.1.2_linux>//下载二进制文件，这里我是从镜像站下载的![](https://image.3001.net/images/20210301/1614582264_603c91f8320482e3b6bce.png!small)

chmod +x huhnitor_1.1.2_linux //赋予可执行权限

ln -s /root/huhnitor_1.1.2_linux /usr/bin/huhnitor
//创建软链接，方便使用。非root用户请把/root改成/home/用户名![](https://image.3001.net/images/20210301/1614582301_603c921deebf0e231721c.png!small)

终端输入huhnitor启动客户端![1614582327_603c9237786341fa84238.png!small](https://image.3001.net/images/20210301/1614582327_603c9237786341fa84238.png!small)

### 0x03 使用：

输入串口所对应的数字，回车

windows![1614582426_603c929a7ebebf0b371e7.png!small](https://image.3001.net/images/20210301/1614582426_603c929a7ebebf0b371e7.png!small)

linux

![1614582476_603c92cc753a98daa55de.png!small](https://image.3001.net/images/20210301/1614582476_603c92cc753a98daa55de.png!small)

重启模块看有无输出STARTED

![1614582576_603c93303a24aa594b34b.png!small](https://image.3001.net/images/20210301/1614582576_603c93303a24aa594b34b.png!small)

如图就是连接并启动成功了

输入help获取命令帮助（太长就不上图了）

扫描：

    
    
    scan -m 模式 -t 客户端扫描时间 -ch 信道 -ct 信道扫描时间 -r 保存以前的扫描结果
    
    scan [-m/ode <ap+st>] [-t/ime <20s>] [-ch/annel <all>] [-ct/ime <284>] [-r/etain]
    Scan for WiFi devices
    -m:  scan mode [ap,st,ap+st] (default=ap+st)  //默认扫描模式AP+客户端
    -t:  station scan time (default=20s)  //默认客户端扫描时间20s
    -ch: 2.4 GHz channels for station scan [1-14] (default=all)  //默认扫描所有信道
    -ct: channel scan time in milliseconds (default=284)
    -r:  keep previous scan results

默认扫描 ：scan

扫描全部信道AP：scan -m ap

![1614584230_603c99a6178eba07f92c1.png!small](https://image.3001.net/images/20210301/1614584230_603c99a6178eba07f92c1.png!small)

扫描指定信道AP+客户端：scan -ch 信道

![1614584366_603c9a2e7a155c484f4e7.png!small](https://image.3001.net/images/20210301/1614584366_603c9a2e7a155c484f4e7.png!small)

Deauth攻击：

    
    
    deauth -ap 目标AP编号 -st 目标客户端编号 -mac 手动选择目标（mac地址） -t 攻击时间 -n 数据包限制 -r 每秒数据包 -m 类型
    
    deauth [-ap <value>] [-st/ation <value>] [-mac,manual <value>] [-t/ime/out <5min>] [-n/um/ber <0>] [-r/ate <20>] [-m/ode <deauth+disassoc>]
    Deauthenticate (disconnect) selected WiFi connections
    -ap:  access point IDs to attack
    -st:  station IDs to attack
    -mac: manual target selection [Sender-Receiver-Channel] for example:'aa:bb:cc:dd:ee:ff-00:11:22:33:44:55-7'
    -t:   attack timeout (default=5min)
    -n:   packet limit [>1] (default=0)
    -r:   packets per second (default=20)
    -m:   packet types [deauth,disassoc,deauth+disassoc] (default=deauth+disassoc)
    
    攻击指定AP1分钟：deauth -ap IDs -t 1min

![1614584456_603c9a88831ba03fa480e.png!small](https://image.3001.net/images/20210301/1614584456_603c9a88831ba03fa480e.png!small)

攻击指定客户端：deauth -st IDs

![1614584492_603c9aac476a0c7f654e9.png!small](https://image.3001.net/images/20210301/1614584492_603c9aac476a0c7f654e9.png!small)

停止攻击：stop deauth

![1614584509_603c9abd2e0bc0c49f80f.png!small](https://image.3001.net/images/20210301/1614584509_603c9abd2e0bc0c49f80f.png!small)

Beacon伪造AP：

beacon -ssid 名称 -bssid mac地址 -receiver 接收地址 -enc 加密方式 -ch 信道 -r 每秒数据包 -auth
扫描认证 -save 保存 -t 时间

    
    
    beacon -ssid/s <value> [-bssid,from <random>] [-receiver,to <broadcast>] [-enc/ryption <open>] [-ch/annel <1>] [-r/ate <10>] [-auth,m/on/itor] [-save] [-t/ime/out <5min>]
    Send WiFi network advertisement beacons
    -ssid: network names (SSIDs) for example: "test A","test B"
    -from: BSSID or sender MAC address (default=random)
    -to:   receiver MAC address (default=broadcast)
    -enc:  encryption [open,wpa2] (default=open)
    -ch:   2.4 GHz channel(s) [1-14] (default=1)
    -r:    packets per second per SSID (default=10)
    -m:    scan for authentications
    -save: save probe requests from auth. scan
    -t:    attack timeout (default=5min)

伪造一个AP：beacon -ssid 名字

![1614585951_603ca05f1a4951279dd6d.png!small](https://image.3001.net/images/20210301/1614585951_603ca05f1a4951279dd6d.png!small)

start引导模式（新手推荐）：

输入start进入引导模式，输入你想要发动的攻击，回车

![1614586489_603ca2797d0bd35ee3370.png!small](https://image.3001.net/images/20210301/1614586489_603ca2797d0bd35ee3370.png!small)

例如![1614586820_603ca3c43c6cf67d01f4b.png!small](https://image.3001.net/images/20210301/1614586820_603ca3c43c6cf67d01f4b.png!small)

![1614586842_603ca3dadc898152f2e47.png!small](https://image.3001.net/images/20210301/1614586842_603ca3dadc898152f2e47.png!small)

其他更有趣的功能我就不一一列举了，靠大家自己去探索了。我会尽力改出来一个汉化版的v3，供英语不太好的朋友们使用。

> 相关链接（镜像站）：
>
> <https://hub.fastgit.org/SpacehuhnTech/esp8266_deauther>
>
> <https://hub.fastgit.org/SpacehuhnTech/esp8266_deauther/tree/v3>
>
>
> [https://hub.fastgit.org/SpacehuhnTech/Huhnitor﻿](https://hub.fastgit.org/SpacehuhnTech/Huhnitor)

