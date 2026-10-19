## 简介

frp 是一个专注于内网穿透的高性能的反向代理应用，支持 TCP、UDP、HTTP、HTTPS 等多种协议。可以将内网服务以安全、便捷的方式通过具有公网
IP 节点的中转暴露到公网。

通过在具有公网 IP 的节点上部署 frp 服务端，可以轻松地将内网服务穿透到公网，同时提供诸多专业的功能特性，这包括：

> `客户端服务端通信支持 TCP、KCP 以及 Websocket 等多种协议。 采用 TCP 连接流式复用，在单个连接间承载更多请求，节省连接建立时间。
> 代理组间的负载均衡。 端口复用，多个服务通过同一个服务端端口暴露。 多个原生支持的客户端插件（静态文件查看，HTTP、SOCK5 代理等），便于独立使用
> frp 客户端完成某些工作。 高度扩展性的服务端插件系统，方便结合自身需求进行功能扩展。 服务端和客户端 UI 页面。`

frp 采用 Golang 编写，支持跨平台，仅需下载对应平台的二进制文件即可执行，没有额外依赖。

## 安装

<https://github.com/fatedier/frp/releases>

解压缩下载的压缩包，将其中的 frpc 拷贝到内网服务所在的机器上，将 frps 拷贝到具有公网 IP 的机器上，放置在任意目录。

编写配置文件，先通过 ./frps -c ./frps.ini 启动服务端，再通过 ./frpc -c ./frpc.ini
启动客户端。如果需要在后台长期运行，建议结合其他工具使用，例如 systemd 和 supervisor。

如果是 Windows 用户，需要在 cmd 终端中执行命令。

frp 主要由 客户端(frpc) 和 服务端(frps) 组成，服务端通常部署在具有公网 IP 的机器上，客户端通常部署在需要穿透的内网服务所在的机器上。

内网服务由于没有公网 IP，不能被非局域网内的其他用户访问。

用户通过访问服务端的 frps，由 frp 负责根据请求的端口或其他信息将请求路由到对应的内网机器，从而实现通信。

## 代理类型

frp 支持多种代理类型来适配不同的使用场景。

> tcp ：单纯的 TCP 端口映射，服务端会根据不同的端口路由到不同的内网服务。  
> udp ：单纯的 UDP 端口映射，服务端会根据不同的端口路由到不同的内网服务。  
> http ：针对 HTTP 应用定制了一些额外的功能，例如修改 Host Header，增加鉴权。  
> https ：针对 HTTPS 应用定制了一些额外的功能。  
> stcp ：安全的 TCP 内网代理，需要在被访问者和访问者的机器上都部署 frpc，不需要在服务端暴露端口。  
> sudp ：安全的 UDP 内网代理，需要在被访问者和访问者的机器上都部署 frpc，不需要在服务端暴露端口。  
> xtcp ：点对点内网穿透代理，功能同 stcp，但是流量不需要经过服务器中转。  
> tcpmux ：支持服务端 TCP 端口的多路复用，通过同一个端口访问不同的内网服务。

## 使用教程

实验环境是  
攻击机IP：192.168.51.209  
vps：x.x.x.x  
目标主机：192.168.48.181

在vps上传linux版本的frp  
首先先下载对应的安装包，上边有下载地址。打开后点击要下载的包，复制链接如下：  
<https://github.com/fatedier/frp/releases/download/v0.36.2/frp_0.36.2_linux_amd64.tar.gz>  
![image](https://image.3001.net/images/20210430/1619770649_608bbd196a7fbc80f2a9e.png!small)使用curl安装（vps上边已经安装好，这里使用kali演示下）

    
    
    curl -# -LJOhttps://github.com/fatedier/frp/releases/download/v0.36.2/frp_0.36.2_linux_amd64.tar.gz
    

没有curl也可以使用wget安装

    
    
    wgethttps://github.com/fatedier/frp/releases/download/v0.36.2/frp_0.36.2_linux_amd64.tar.gz
    

使用tar指令解压tar.gz文件

    
    
    tar -zxvf frp_0.36.2_linux_amd64.tar.gz
    

![image](https://image.3001.net/images/20210430/1619770751_608bbd7f9bd534f43d637.png!small)

![image](https://image.3001.net/images/20210430/1619770839_608bbdd7a9cde89cb2b2d.png!small)在服务端使用frps,查看frps的配置,默认如下：  
![image](https://image.3001.net/images/20210430/1619770919_608bbe2789aff4a665511.png!small)在这里添加一个控制台,如果没有vim安装如下

    
    
    sudo apt-get -f install #是修复损坏的软件包，尝试卸载出错的包，重新安装正确版本的
    
    sudo apt install vim #安装vim
    

![image](https://image.3001.net/images/20210430/1619771686_608bc126f042e3e313b13.png!small)

    
    
    [common]
    bind_port = 7000 #绑定的端口
    
    dashboard_user = admin #控制台用户名
    dashboard_pwd = password #控制台密码
    dashboard_port = 7500 #控制台的端口
    

保存退出  
![image](https://image.3001.net/images/20210430/1619771753_608bc169bf13bcd73b6ea.png!small)启动服务端,7500端口已经启用  
./frps -c ./frps.ini  
![image](https://image.3001.net/images/20210430/1619771794_608bc192a3d890b4cc747.png!small)打开浏览器，输入公网IP+7500端口（自己设置的控制台端口），这样服务端已经配置完成。  
![image](https://image.3001.net/images/20210430/1619771844_608bc1c4c9090598daa16.png!small)在客户端下载win的frp(环境是win),接下来配置frpc.ini如下  
![image](https://image.3001.net/images/20210430/1619771894_608bc1f6d499490fc885a.png!small)cmd运行方法：frpc
-c frpc.ini  
![image](https://image.3001.net/images/20210430/1619771932_608bc21c4b975d50429f9.png!small)powershell运行方法：.\frpc.exe
-c frpc.ini  
![image](https://image.3001.net/images/20210430/1619771981_608bc24d892c2b94c360c.png!small)使用远程连接进行连接，IP使用公网IP，端口使用remote_port映射到公网IP的端口  
![image](https://image.3001.net/images/20210430/1619772021_608bc275d5ce3454a3b24.png!small)![image](https://image.3001.net/images/20210430/1619772120_608bc2d8649a72e6f1c54.png!small)输入目标主机的用户名和密码进行远程登录  
![image](https://image.3001.net/images/20210430/1619772409_608bc3f9c8a4eb5727b65.png!small)

## 让进程后台运行方法

##### Linux：

    
    
    nohup ./frps -c ./frps.ini&
    

使用Ctrl+C退出后后台依然运行  
![image](https://image.3001.net/images/20210430/1619772528_608bc470a790456aa0178.png!small)使用`ps
aux`查看当前进程  
![image](https://image.3001.net/images/20210430/1619772580_608bc4a407b7b630a7a85.png!small)结束进程方法  
使用`kill -9 PID`  
![image](https://image.3001.net/images/20210430/1619772610_608bc4c25b86ecd0e094b.png!small)

win:

    
    
    `start /b frpc.exe -c frpc.ini
    

使用tasklist查看  
![image](https://image.3001.net/images/20210430/1619772645_608bc4e5803db9a338b13.png!small)结束进程方法  
taskkill /pid PID号 -f  
![image](https://image.3001.net/images/20210430/1619772680_608bc508f33d5a46c1e75.png!small)

## 问题解决

当服务端运行时有以下报错，启动程序端口被占  
![image](https://image.3001.net/images/20210430/1619772721_608bc531362bed741be28.png!small)使用netstat
-nap查看端口状态及PID  
kill -9 PID(被占用的端口PID)就可以重新运行了

## 参考链接

<https://www.runoob.com/linux/linux-comm-nohup.html>  
<https://gofrp.org/docs/>  
<https://www.jianshu.com/p/e0581ee84323>

