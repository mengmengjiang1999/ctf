![](https://image.3001.net/images/20230421/1682064541_6442449da2e74b7348d34.png!small)  

## 关于Th3inspector

Th3inspector是一款功能强大的网络侦查信息收集工具，该工具整合了多种信息收集组件，可以帮助广大研究人员在网络侦查活动中完成各种信息收集任务。

值得一提的是，该工具支持在Linux和Windows，甚至是Android操作系统平台上运行。

## 工具安装

### Linux安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Moham3dRiahi/Th3inspector.git

然后切换到项目目录中，执行安装脚本install.sh即可完成工具的安装：

    
    
    cd Th3inspector
    
    chmod +x install.sh && ./install.sh

### Android安装

首先，我们需要在Android手机中安装并配置好Termux，然后进入终端仿真应用程序，运行下列命令来安装Th3inspector：

    
    
    git clone https://github.com/Moham3dRiahi/Th3inspector.git
    
    cd Th3inspector
    
    chmod +x install.sh && ./install.sh

### Windows安装

首先，我们需要在Windows设备上安装并配置好Perl，然后使用下列命令下载Th3inspector：

    
    
    git clone https://github.com/Moham3dRiahi/Th3inspector.git

然后使用cpan来安装JSON模块：

    
    
    cpan install JSON

接下来，将下载好的Th3inspector项目解压到桌面，并打开终端窗口执行下列命令：

    
    
    cd Desktop/Th3inspector-master/
    
    perl Th3inspector.pl

## 工具使用命令

 ** **短命令****

|

 ** **长命令****

|

 ** **命令描述****  
  
---|---|---  
  
-i

|

\--info

|

获取网站信息  
  
-n

|

\--number

|

获取手机号信息  
  
-mx

|

\--mailserver

|

查找IP地址和电子邮件服务器  
  
-w

|

\--whois

|

域名Whois查询  
  
-l

|

\--location

|

Location查找网站或IP地址地理定位  
  
-c

|

\--cloudflare

|

绕过CloudFlare  
  
-a

|

\--age

|

域名年限查询  
  
-ua

|

\--useragent

|

获取用户代理信息  
  
-p

|

\--port

|

检测开放端口和活动服务  
  
-b

|

\--bin

|

信用卡Bin码检测  
  
-s

|

\--subdomain

|

子域名扫描  
  
-e

|

\--email

|

电子邮件地址检测  
  
-cms

|

\--cms

|

内容管理系统CMS检测  
  
-h

|

\--help

|

显示工具帮助信息和退出show the help message and exit  
  
## 工具使用样例

查看工具帮助选项：

    
    
    perl Th3inspector.pl -h

获取网站信息：

    
    
    perl Th3inspector.pl -i example.com

获取手机号信息：

    
    
    perl Th3inspector.pl -n xxxxxxx

查找IP地址和电子邮件服务器：

    
    
    perl Th3inspector.pl -mx example.com

查找网站或IP地址的地理定位：

    
    
    perl Th3inspector.pl -l example.com

使用CloudFlare Protection获取网站的真实IP：

    
    
    perl Th3inspector.pl -c example.com

## 工具运行截图

![](https://image.3001.net/images/20230421/1682064684_6442452c10db28d2104ad.png!small)

![](https://image.3001.net/images/20230421/1682064693_6442453553ea91046845c.jpeg!small)

![](https://image.3001.net/images/20230421/1682064703_6442453fa3aa39ffbcbb0.jpeg!small)

![](https://image.3001.net/images/20230421/1682064712_6442454823e8f254c3318.jpeg!small)

![](https://image.3001.net/images/20230421/1682064720_6442455065497365c6032.jpeg!small)

![](https://image.3001.net/images/20230421/1682064728_644245589bfc12137f9d0.jpeg!small)

![](https://image.3001.net/images/20230421/1682064735_6442455faedb0ba3aa8fb.jpeg!small)

![](https://image.3001.net/images/20230421/1682064749_6442456d859c473ac6041.jpeg!small)

## 工具演示视频

 **演示视频** ：【[ _点我观看_](https://youtu.be/ZvsIbhRPSrI)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Moham3dRiahi/Th3inspector/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Th3inspector** ：【[
_GitHub传送门_](https://github.com/Moham3dRiahi/Th3inspector)】

## 参考资料

> [ _https://wikipedia.org/wiki/Linux_](https://wikipedia.org/wiki/Linux)
>
> [ _https://wikipedia.org/wiki/Android_](https://wikipedia.org/wiki/Android)
>
> [
> _https://wikipedia.org/wiki/Microsoft_Windows_](https://wikipedia.org/wiki/Microsoft_Windows)
>
> [
> _https://play.google.com/store/apps/details?id=com.termux_](https://play.google.com/store/apps/details?id=com.termux)

