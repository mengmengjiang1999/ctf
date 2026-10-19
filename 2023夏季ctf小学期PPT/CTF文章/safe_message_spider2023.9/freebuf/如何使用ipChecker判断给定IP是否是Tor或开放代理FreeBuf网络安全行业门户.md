![](https://image.3001.net/images/20230515/1684140344_6461f138e923173250bc4.jpeg!small)  

## 关于ipChecker

ipChecker是一款功能强大的IP地址检测工具，该工具可以帮助广大研究人员判断一个给定的IP地址是否是一个Tor节点或是一个恶意开放代理。

## 工作机制

ipChecker提供了一些插件可以帮助我们从公共站点中删除代理IP，所有的这些IP都会存储在一个数据库中，我们可以使用提供的API进行查询。

当我们运行make run命令时，它将启动docker
swarm来为API创建一个服务，该服务可以升级并被四个容器使用，另一个服务专门用来更新脚本程序并捕捉所有的代理和Tor节点中所有的插件，最后一个服务时一个容器，用于运行Mongodb并存储所有的数据。

这些容器通过一个名为ipchecker-network的Docker网络进行通信，并只会暴露8080端口。

为了避免误报，API只会返回当前日期的IP，因为几乎所有的代理服务器或Tor节点使用的都是动态IP。

## 插件

下面给出的是ipChecker所使用的插件列表：

> cloudproxies.com
>
> gatherproxy.com
>
> hidemy.name
>
> httptunnel.ge
>
> multiproxy.org
>
> nordvpn.com
>
> proxy-list.org
>
> rebro.weebly.com
>
> samair.ru
>
> torstatus.blutmagie.de
>
> xroxy.com

## 工具安装

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mthbernardes/ipChecker
    
    cd ipchecker/

 **Docker安装** ：【[ _参考文档_](https://docs.docker.com/install/)】

## 服务执行命令选项

 ** **命令****

|

 ** **描述****  
  
---|---  
  
make buld

|

构建所有的镜像  
  
make run

|

构建并运行所有镜像  
  
make stop

|

终止所有的服务  
  
make wipe

|

终止所有的服务并清理所有的镜像和MongoDB数据  
  
## 工具基础使用

下面给出的是工具API的基础使用方法：

 ** **节点****

|

 ** **方法****

|

 ** **描述****  
  
---|---|---  
  
/

|

GET

|

所有节点的文档  
  
/statistics

|

GET

|

获取统计信息，包括被屏蔽的请求和数据库中每天获取到的全部代理信息  
  
/ips?ip=127.0.0.1

|

GET

|

搜索数据库中的单个IP地址  
  
/all

|

GET

|

返回数据库中的所有IP信息  
  
## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/mthbernardes/ipChecker/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **ipChecker** ：【[ _GitHub传送门_](https://github.com/mthbernardes/ipChecker)】

## 参考资料

> [ _https://docs.docker.com/install/_](https://docs.docker.com/install/)

