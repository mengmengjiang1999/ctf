## 写在前面

**无聊的时候bypass了家里电视盒子禁止安装第三方app的限制，又因为在找相关资料的时候发现都对萌新不太友好，希望这篇文章能让和我一样的安全萌新能了解到arp污染在内网中的巨大作用。**

## 快速开始

本人使用Ubuntu 19，所需软件如下：

名称 | 作用  
---|---  
mitmproxy | 伪造web服务  
wireshark | 流量分析  
Ettercap | arp污染  
  
至于安装都比较简单，mitmproxy使用pip install；

wireshark和Ettercap使用apt install。

## 基础的arp污染

用网线将网关WAN口与笔记本相连，使得笔记本与电视盒子处于同于子网（192.168.1.0/24）：

![ip_a.png](https://image.3001.net/images/20190729/1564394300_5d3ec33cbb092.png!small)

    
    
    sudo ettercap -G

启动带GUI的ettercap。

    
    
    sudo wirseshark

启动wirshshark。

选择合适的网卡：

![wirshshark_enter.png](https://image.3001.net/images/20190729/1564394259_5d3ec31367f60.png!small)

![ettercap_select_eth.png](https://image.3001.net/images/20190729/1564394376_5d3ec3881a093.png!small)

ettercap扫描主机：

![etterca\[_scan_hosts.png](https://image.3001.net/images/20190729/1564394225_5d3ec2f145313.png!small)

把网关和电视盒子分别加入target1，target2。

开始arp欺骗，可以看到wirseshark中已经有流量。

## 一些分析

    
    
    ip.adder = 192.168.1.8 and http

分析一下电视盒子的请求。

可以明显的看到有个域名appcenter.*：

![wirshshark_catch_appcenter.png](https://image.3001.net/images/20190729/1564394196_5d3ec2d498cc3.png!small)

这就是盒子应用中心的服务器了。

剔除显然不对的目标，同时还有几个奇怪的域名。看具体的返回都是一些true，succes之类的，应该是一些校验。

这些服务器可能与安装app有关，先记下。

然后，安装一个app，分析附近的流量。在拿到apk后，盒子又向log.*发送了请求，看起来这个log.*很可疑。

（后来写exp时证实，这个log.*就是用于校验用的）

##
![wirsesark.jpg](https://image.3001.net/images/20190729/1564395109_5d3ec66573451.jpg!small)

## explot it

通过分析我知道，app更新服务器是appcenter.*，那么自然的想到了中间人攻击。

可以使用ettercap的插件dns_spof。

    
    
    vim /etc/ettercap/etter.dns

添加解析：

    
    
    appcenter.* 192.168.1.7log.* 192.168.1.7

然后使用mitmproxy进行站点克隆：

    
    
    mitmweb -p 17080 --mode reverse:http://appcenter.*:17080

在127.0.0.1:8081上可以比较直观的看到请求了。

然后再写一个mitmproxy的脚步替换原本appcenter下发的apk：

![exp.png](https://image.3001.net/images/20190729/1564394064_5d3ec25098f65.png!small)

再启动一个mitmproxy克隆log服务器：

    
    
    mitmproxy -p 8080 --mode reverse:http://log.*:8080

点击更新app：

![IMG_20190724_163542.jpg](https://image.3001.net/images/20190729/1564394083_5d3ec263e363a.jpg!small)

斜眼笑.jpg

## 一些失败的尝试

wps投影宝具有文件管理功能。

移动某app，上传文件校验不严格，可以上传下载任意后缀的文件，但是我并没有找到利用点。

 ***本文作者：test890，本文属FreeBuf原创奖励计划，未经许可禁止转载**

