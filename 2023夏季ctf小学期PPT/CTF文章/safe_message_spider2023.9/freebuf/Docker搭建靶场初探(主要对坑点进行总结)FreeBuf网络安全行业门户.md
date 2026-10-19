> 本次测试使用Deepin OS(Kernel base debian)虚拟机安装Sqli-labs(Docker)

### 首先 进入虚拟机配置apt源以及docker仓库镜像

#### 安装配置过程中发现坑点如下

1.按照官方设置存储库，并将对应的链接改至阿里镜像地址，进行apt-get update操作更新出现失败

    
    
    root@PC:/ sudo apt-get update
    忽略:1 http://mirrors.aliyun.com/debian stretch InRelease
    命中:2 http://mirrors.aliyun.com/debian-security stretch/updates InRelease
    命中:3 http://mirrors.aliyun.com/debian stretch-updates InRelease
    命中:5 http://mirrors.aliyun.com/debian stretch-backports InRelease
    命中:6 http://mirrors.aliyun.com/debian stretch Release
    命中:7 https://cdn-package-store6.deepin.com/appstore eagle InRelease
    命中:4 https://packages.chinauos.com/printer eagle InRelease
    忽略:9 https://download.docker.com/linux/debian n/a InRelease
    错误:10 https://download.docker.com/linux/debian n/a Release
      404  Not Found [IP: 13.225.94.4 443]
    正在读取软件包列表... 完成
    E: 仓库 “https://download.docker.com/linux/debian n/a Release” 没有 Release 文件。
    N: 无法安全地用该源进行更新，所以默认禁用该源。
    N: 参见 apt-secure(8) 手册以了解仓库创建和用户配置方面的细节。
    

解决方法: 将`$(lsb_release -cs)`换至`buster`  
参考链接：[deepin_v20安装docker（解决lsb_release -cs
返回n/a的问题）](https://bbs.deepin.org/post/191846)  
2.配置完成后，进行依赖库安装containerd.io依赖项，出现404

    
    
    错误:1 https://mirrors.aliyun.com/docker-ce/linux/debian buster/stable amd64 containerd.io amd64 1.6.6-1
      404  Not Found [IP: 111.19.143.227 443]
    E: 无法下载 https://mirrors.aliyun.com/docker-ce/linux/debian/dists/buster/pool/stable/amd64/containerd.io_1.6.6-1_amd64.deb  404  Not Found [IP: 111.19.143.227 443]
    E: 有几个软件包无法下载，要不运行 apt-get update 或者加上 --fix-missing 的选项再试试？
    

解决方法: 使用`apt-cache madison containerd.io`查询其他版本进行安装  
参考链接：[Docker 官方教程 节选自`Install Docker
Engine`部分](https://docs.docker.com/engine/install/debian/)

### 其次 成功运行 docker Hello-world镜像，此部分正常运行未出现坑点

### 最后 部署Sqli-labs靶场，虚拟机Deepin OS采用Docker部署Sqli-labs靶场

![Docker网卡信息](https://image.3001.net/images/20220712/1657593149_62ccdd3d2993cb0838393.png!small)  
Docker IP：172.10.0.1/16  
Vmware IP(NAT):192.168.163.133/24  
Host IP:192.168.1.140/24  
![主机网卡信息](https://image.3001.net/images/20220712/1657593167_62ccdd4fdc57ae56e00a8.png!small)  
![主机路由信息](https://image.3001.net/images/20220712/1657593364_62ccde1432d13df80c58c.png!small)  
针对无法Ping通。不得不使用自己那一点点的网络知识老本，添加static route进行解决。

    
    
    route add -p 172.17.0.0 mask 255.255.0.0 192.168.163.133
    

完成物理机的静态路由添加后，可通过物理机访问IP地址成功访问sqli-labs靶场  
![Sqli-labs成功访问](https://image.3001.net/images/20220712/1657593213_62ccdd7da2f88518fa237.png!small)  
其他资源：  
Docker 阿里镜像站：https://mirrors.aliyun.com/docker-ce/linux/  
Docker 官网：https://www.docker.com  
Docker 官方文档： https://docs.docker.com  
Docker Hub : https://hub.docker.com

