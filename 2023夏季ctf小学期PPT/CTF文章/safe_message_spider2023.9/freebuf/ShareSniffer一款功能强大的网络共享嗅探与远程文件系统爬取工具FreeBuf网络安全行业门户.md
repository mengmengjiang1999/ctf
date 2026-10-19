![](https://image.3001.net/images/20230829/1693314406_64eded66e0a95674d9504.jpg!small)

## 关于ShareSniffer

ShareSniffer是一款功能强大的网络共享嗅探与远程文件系统爬取工具，该工具基于纯Python开发，本质上是一款网络分析工具，可以帮助广大研究人员寻找目标网络系统中已打开或已关闭的文件共享，其中包括自动化网络发现和开放CIFS和NFS共享自动加载。

## 工具要求

> 1、Python 2.7或3.5/3.6；
>
> 2、Linux或macOS操作系统平台；
>
> 3、[ _Nmap_ _7.70_](https://nmap.org/)（要求设置好PATH环境变量）；
>
>
> 4、Nmap脚本（.nse文件，在Linux和macOS系统中路径通常为/usr/local/share/nmap/scripts/或/usr/share/nmap/scripts/）；
>
> 5、python-nmap（安装命令：pip install python-nmap）；
>
> 6、netifaces（安装命令：pip install netifaces）；

## 工具下载

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境（2.7或3.5/3.6）。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/shirosaidev/sharesniffer.git
    
    $ cd sharesniffer

除此之外，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/shirosaidev/sharesniffer/releases/latest)】下载最新版本的ShareSniffer。

## 工具命令行选项

    
    
    usage: sharesniffer.py [-h] [--hosts HOSTS] [-e EXCLUDEHOSTS] [-l SPEEDLEVEL]
    
                           [-n] [--nfsmntopt NFSMNTOPT] [-s]
    
                           [--smbmntopt SMBMNTOPT] [--smbtype SMBTYPE]
    
                           [--smbuser SMBUSER] [--smbpass SMBPASS] [-a]
    
                           [-m MOUNTPOINT] [-p MOUNTPREFIX] [-v] [--debug] [-q]
    
                           [-V]
    
     
    
    optional arguments:
    
      -h, --help             显示工具帮助信息
    
      --hosts HOSTS       目标主机，例如10.10.56.0/22或10.10.56.2，默认扫描所有主机
    
      -e EXCLUDEHOSTS, --excludehosts EXCLUDEHOSTS
    
                            扫描需要排除的主机，例如10.10.56.1,10.10.56.254
    
      -l SPEEDLEVEL, --speedlevel SPEEDLEVEL
    
                            扫描速度等级，3-5，等级越低准确率越高，默认为4
    
      -n, --nfs               扫描目标网络NFS共享
    
      --nfsmntopt NFSMNTOPT
    
                            NFS加载点，默认为ro,nosuid,nodev,noexec,udp
    
                            ,proto=udp,noatime,nodiratime,rsize=1024,dsize=1024,ve
    
                            rs=3,rdirplus
    
      -s, --smb              扫描目标网络SMB共享
    
      --smbmntopt SMBMNTOPT
    
                            SMB加载选项，默认为ro,nosuid,nodev,noexec,udp
    
                            ,proto=udp,noatime,nodiratime,rsize=1024,dsize=1024
    
      --smbtype SMBTYPE      设置SMB类型，smbfs（默认）或
    
      --smbuser SMBUSER     SMB用户名，默认为guest
    
      --smbpass SMBPASS    SMB密码，默认为空
    
      -a, --automount        自动加载任意开放NFS/SMB共享
    
      -m MOUNTPOINT, --mountpoint MOUNTPOINT
    
                            加载点（加载共享），默认为./
    
      -p MOUNTPREFIX, --mountprefix MOUNTPREFIX
    
                            加载点目录名称前缀，默认为sharesniffer)
    
      -v, --verbose          开启Verbose模式输出
    
      --debug              输出调试信息
    
      -q, --quiet           静默模式，仅显示可能的爬取点
    
      -V, --version         显示工具版本

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/shirosaidev/sharesniffer/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **ShareSniffer** ：【[
_GitHub传送门_](https://github.com/shirosaidev/sharesniffer)】

## 参考资料

> [ _https://nmap.org/_](https://nmap.org/)

