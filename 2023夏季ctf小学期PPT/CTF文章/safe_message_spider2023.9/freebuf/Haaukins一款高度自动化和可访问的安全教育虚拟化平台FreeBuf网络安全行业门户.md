##  Haaukins

**Haaukins是一个高度可访问和自动化的安全教育[虚拟化](https://www.kitploit.com/search/label/Virtualization)平台，它由三个主要组件组成，即Docker、[Virtualbox](https://www.kitploit.com/search/label/Virtualbox)和Golang，各个组件之间的通信和调用通过Go编程语言来进行管理。使用Go语言环境来管理和部署Haaukins平台的主要原因是Go具有简单的并发和并行机制。如需了解Haaukins的更多架构信息，请访问【[这个页面](https://github.com/aau-network-security/haaukins/wiki/Architecture-of-Haaukins)】。**

我们的主要目标是让任何希望学习网络安全相关内容的人，能够学习如何在一个目标系统上发现[漏洞](https://www.kitploit.com/search/label/Vulnerability)。而Haaukins正好提供了自己的虚拟化环境以及专门用于查找安全漏洞的操作系统。

###  依赖组件

Haaukins的正常运行需要用户安装下列组件：

> 1、Linux
>
> 2、Docker
>
> 3、Go 1.13+

##  工具安装

在安装Haaukins客户端或守护进程时，有很多选项需要用户通过[二进制文件](https://www.kitploit.com/search/label/Binary)进行配置，广大用户可以访问该项目的【[release页面](https://github.com/aau-network-security/haaukins/releases)】获取。

###  客户端安装

1、下载最新版本的客户端

访问项目的【[release页面](https://github.com/aau-network-security/haaukins/releases)】，找到最新版本的Haaukins：

![](https://image.3001.net/images/20191218/1576652653_5df9cf6d4dd8c.png!small)

根据不同的操作系统和架构选择安装的版本：

    
    
    32-bit: ARCH = 386
    
        64-bit: ARCH = amd64
    
        Mac OSX: OS = darwin
    
        Windows: OS = windows
    
        Linux: OS = linux

2、在系统中安装客户端（以Windows为例，详细安装请参考【[安装文档](https://github.com/aau-network-security/haaukins/wiki/Installation)】）：

先进入“C:\Program
Files\”，创建一个名为“hkn”的新目录，将下载下来的文件拷贝到该目录，并将其命名为“hkn.exe”，完成后的目录结构应该为“C:\Program
Files\hkn\hkn.exe”。

接下来，按照图示进行操作完成安装:

![](https://image.3001.net/images/20191218/1576652711_5df9cfa74cc93.png!small)![](https://image.3001.net/images/20191218/1576652711_5df9cfa7c6fca.png!small)![](https://image.3001.net/images/20191218/1576652711_5df9cfa7bdaf4.png!small)![](https://image.3001.net/images/20191218/1576652711_5df9cfa7d3260.png!small)![](https://image.3001.net/images/20191218/1576652712_5df9cfa844d67.png!small)![](https://image.3001.net/images/20191218/1576652712_5df9cfa8554db.png!small)![](https://image.3001.net/images/20191218/1576652712_5df9cfa863da6.png!small)![](https://image.3001.net/images/20191218/1576652712_5df9cfa8dbf56.png!small)![](https://image.3001.net/images/20191218/1576652713_5df9cfa93433c.png!small)

完成之后，打开我们的cmd或PowerShell，然后输入“hkn”命令即可开始使用Haaukins了。

##  工具测试

确保命令行工具已进入到“$GOPATH/src/github.com/aau-network-security/haaukins/”路径，然后运行下列命令：

    
    
    go test -v -short ./...

###  重编译proto

Haaukins平台使用了gRPC来实现客户端和守护进程的通信，更新好协议缓冲区定义后，使用下列命令完成重编译：

    
    
    cd $GOPATH/src/github.com/aau-network-security/haaukins/daemon/
    
        protoc -I proto/ proto/daemon.proto --go_out=plugins=grpc:proto

##  项目地址

> Haaukins：【[GitHub传送门](https://github.com/aau-network-security/haaukins)】

 *** 参考来源：[haaukins](https://github.com/aau-network-security/haaukins)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

