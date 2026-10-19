近期我们对一些智能家电设备进行了渗透测试，其中一个目标设备是某公司的智能插座产品。拿到产品后我们一般会进行下面的两步操作：第一步设备配网，即插座绑定；第二步通过APP实现智能插座的远程通电和断电操作。

前面的操作都很顺利，但当我们用Burpsuite设置代理到进行抓包分析时，发现基本抓不到什么https和http包。经过一番头脑风暴后，我们找到了抓不到包的原因，APP与设备之间很可能使用了其他通信协议进行通讯，遇到这种情况Burpsuite当然会蒙圈了。

针对物联网设备的抓包问题，我们对多种抓包方式进行了研究和整理，最终总结出以下五种方法，大家可以根据自己的实际情况选择适合的方法。

## 1、通过Android模拟器进行抓包与重放

第一种方法是，在Android模拟器上安装tcpdump，再使用科来网络分析系统进行抓包与重放。

  * Android模拟器
  * tcpdump
  * 科来网络分析系统
  * Wireshark

在Android模拟器上安装tcpdump。

    
    
    // android下安装和使用tcpdump工具 
    adb push tcpdump /storage/sdcard0/tcpdump 
    // 使用RE文件管理器，将/system/bin/目录设置为可读写
    cp /storage/sdcard0/tcpdump /system/bin/tcpdump 
    chmod 755 /system/bin/tcpdump

先启动APP，再使用tcpdump进行抓包。

    
    
    // 运行tcpdump，将监听的数据包存放在/sdcard/capture.pcap  
    tcpdump -p -vv -s 0 -w /sdcard/capture.pcap  
    // 下载监听的数据包capture.pcap到PC的当前目录：  
    adb pull /sdcard/capture.pcap d:/

打开科来网络分析工具对抓到的封包进行分析和数据包重放。

![](https://image.3001.net/images/20200817/1597649823.png!small)

我们在路由器上可以获得设备的ip，在分析工程页面，双击Android模拟器的ip进入数据包分析工程页面。重点关注Android模拟器->智能插座之间数据包，这些包就是对插座进行通断电的操作。

![](https://image.3001.net/images/20200817/1597650190.png!small)将所有的数据包选取后点右键-发送数据包到数据包生成器。

![](https://image.3001.net/images/20200817/1597650302.png!small)

进入科来数据包生成器，将不相关的数据选取后删除，然后选择发送全部，智能插座马上有反应了，快速的开关一次，数据包重放成功！

![](https://image.3001.net/images/20200817/1597650320.png!small)

## 2、在路由器上进行抓包

第二种方法是在newifi3上刷Openwrt固件，再安装tcpdump进行抓包。

  * newwifi3+openwrt19.07
  * tcpdump
  * 科来网络分析系统
  * Wireshark

新路由3下刷入openwrt19.07固件，前提是已经刷入了Breed Web系统：

> （1）准备好openwrt19.07固件
>
> （2）打开浏览器输入 192.168.1.1，进入 Breed Web 恢复控制台刷系统前只能通过有线连接的方式进行，因为进入 BreedWeb
> 恢复控制台后，无线功能是没有打开的。
>
> （3）进入 Breed Web
> 恢复控制台后，先不要急着进行升级，先在控制台点击恢复出厂设置。路由如果从一个系统刷入另一个系统，最好先恢复出厂设置，这样也能保持在刷入系统之前是最初始状态。
>
> （4）恢复出厂设置后，不需要进行任何操作，会自动跳到 BreedWeb 恢复控制台。然后在固件前面打勾，再点击”浏览”，跳出固件选择窗口。
>
> （5）固件上传完成后，到 Breed Web 恢复控制台更新确认界面，点击更新。

下面开始在openwrt下安装tcpdump。输入<http://192.168.2.1>进入路由的管理界面，先打开ssh服务。

![](https://image.3001.net/images/20200817/1597651114.png!small)

安装tcpdump。

    
    
    ssh 192.168.2.1 22
    mkdir /test2020
    cd /test2020
    opkg update
    opkg install tcpdump
    ifconfig -a  
    //测试tcpdump是否安装成功
    tcpdump -h 
    

先启动APP，再使用tcpdump进行抓包。

    
    
    //将监听的数据包存放在/test2020/tmp1.pcap
    tcpdump -i br-lan -U -c 300 -vvv -w tmp1.pcap
    //下载监听的数据包capture.pcap到PC的当前目录
    adb pull /test2020/tmp1.pcap d:/movie

接下来打开科来网络分析工具对抓到的封包进行分析和数据包重放，与方法1中的步骤相同，不再赘述。

## 3、在win10上建立WiFi热点

第三种方法是win10下建立WIFI热点，使用科来和wireshark进行抓包。

  * 科来网络分析系统
  * Wireshark
  * WIFI热点工具

进入app,然后打开科来网络分析工具对wifi热点网卡进行抓包和重放。但经过测试，这种方法效果不是很好，会出现抓包不全的情况。

![](https://image.3001.net/images/20200817/1597651565.png!small)

## 4、在Ubuntu上建立WIFI热点+伪造证书

第四种方式是在ubuntu19.04下建立WIFI热点，使用tcpdump进行抓包，再通过sslsplit伪造CA证书，实现SSL中间人攻击。经过实际测试和几种方法的对比，这种方法的抓包效果最好。

SSLSplit的主要原理是以中间人的身份将证书插入到客户端和服务器中间，从而截断客户端和服务器之间的数据。之前我们大多数做的都是针对于80端口的欺骗，也就是说，只要是超越了80端口我们就会有点棘手：比如常用的443端口，比如465和587端口，这些都是通过SSL加密进行数据传输的，简单的80端口监听肯定是什么都拿不到的。这个时候，就体现出SSL证书劫持的作用了。

  * 免驱动网卡
  * tcpdump
  * sslsplit
  * tcpreplay

在ubuntu19.04下开启WIFI热点。

![](https://image.3001.net/images/20200817/1597651885.png!small)

![](https://image.3001.net/images/20200817/1597651967.png!small)ubuntu19.04下面安装sslsplit。

    
    
    apt-get install libssl-dev libevent-dev
    make
    make install
    //根据提示搜索安装相应版本：
    apt install pkgconf
    aptitude search libpcap* 
    apt-get install libpcap-dev
    aptitude search libnet*
    apt install libnet-dev
    sslsplit -h //安装成功后进行测试
    cd /test2020
    openssl genrsa -out ca.key 2048 //生成一个key文件
    //自签名用生成的key生成公钥证书:
    openssl req -new -x509 -days 1096 -key ca.key -out ca.crt 
    

![](https://image.3001.net/images/20200817/1597652364.jpg!small)

    
    
    //打开端口流量转发
    echo 1 > /proc/sys/net/ipv4/ip_forward 
    //用iptables进行流量转发，需要把我们需要的端口进行转发:
    iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
    iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443
    iptables -t nat -A PREROUTING -p tcp --dport 587 -j REDIRECT --to-ports 8443
    iptables -t nat -A PREROUTING -p tcp --dport 465 -j REDIRECT --to-ports 8443
    iptables -t nat -A PREROUTING -p tcp --dport 993 -j REDIRECT --to-ports 8443
    iptables -t nat -A PREROUTING -p tcp --dport 995 -j REDIRECT --to-ports 8443
    

启动sslsplit进行SSL分离抓包，将数据包日志保存在/test2020/log目录下面。

    
    
    sslsplit -D -l connect.log -j /test2020 -S log/ -k ca.key -c ca.crt ssl 0.0.0.0 8443 tcp 0.0.0.0 8080

先启动APP，再使用tcpdump进行抓包，将监听的数据包存放在/test2020/tmp1.pcap。

    
    
    cd /test2020
    tcpdump -i wlxe84e0615571b -U -c 300 -vvv -w tmp1.pcap
    

ubuntu19.0.4下使用tcpreplay进行数据包重放。

    
    
    apt install tcpreplay //安装tcpreplay
    tcpreplay -V //查看安装版本
    cd /test2020
    tcpreplay -i wlxe84e0615571b  tmp1.pcap
    

![](https://image.3001.net/images/20200817/1597652578.png!small)

## 5、数据流量重定向抓包

最后一种方法是，通过AP上面的DHCP SERVER功能。插座和APP应用在配网的时候，会提示输入路由器WIFI接入点名称和连接密码，通过AP上面的DHCP
SERVER功能，可以将插座与android
app的网关地址设为攻击机(ubuntu19.04)的IP地址，再使用tcpdump进行抓包，同时通过sslsplit伪造CA证书，实现SSL中间人攻击。

  * 新3路由器
  * tcpdump
  * 科来网络分析系统
  * wireshark
  * sslsplit

将插座与android app的网关地址设为攻击机(ubuntu19.04)的IP地址。

对SSLSplit的设置与方法四中的步骤相同，在此不再重复。

启动APP，再使用tcpdump进行抓包，将监听的数据包存放在/test2020/tmp1.pcap。

    
    
    cd /test2020
    tcpdump -i ens33 -U -c 300 -vvv -w tmp1.pcap
    

![](https://image.3001.net/images/20200817/1597657407.png!small)最后，打开科来网络分析工具对抓到的封包进行分析和数据包重放。

## 总结

上面一共介绍了五种针对物联网设备的抓包方法，详细介绍了具体的操作步骤。从抓包的位置看，可以归纳成为Android设备端、路由端、WIFI热点几个角度；技巧方面包括Openwrt刷机、sslsplit伪造证书和DHCP
SERVER功能等。希望可以帮助大家在今后的工作和研究中扩展一些关于抓包的思路。

 ***本文作者：pt007 & qui3t，转载请注明来自FreeBuf.COM**

