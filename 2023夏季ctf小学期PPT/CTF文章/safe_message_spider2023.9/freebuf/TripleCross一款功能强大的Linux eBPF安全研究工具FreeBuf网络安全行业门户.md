![](https://image.3001.net/images/20221204/1670166685_638cb89d6ab42ecd4e645.jpg!small)

## 关于TripleCross

TripleCross是一款功能强大的Linux eBPF安全研究工具，该工具提供了后门、C2、代码库注入、执行劫持、持久化和隐蔽执行等功能。

## 功能介绍

> 1、使用一个代码库注入模块通过往进程的虚拟内存中写入命令来执行恶意代码；
>
> 2、提供了一个行劫持模块，用于修改传递给内核的数据以执行恶意程序；
>
> 3、提供了一个本地权限升级模块，允许使用root权限运行恶意程序；
>
> 4、提供了具有C2功能的后门，可以监控网络并执行从远程rootkit客户端发送的命令。它包含多个激活触发器，因此这些操作会被秘密传输；
>
> 5、一种rootkit客户端，允许研究人员建立3种不同类型的类似Shell的连接，以发送远程控制rootkit状态的命令和操作；
>
> 6、提供了一个持久化模块，确保rootkit保持安装状态，即使在重新启动事件后仍保持完全权限；
>
> 7、提供了一个隐蔽模块，可以隐藏与rootkit相关的文件和目录；

## 工具模块架构

![](https://image.3001.net/images/20221204/1670166701_638cb8adebae87fbcd0f6.png!small)

## 工具要求

该工具已在下列环境中进行过测试：

![](https://image.3001.net/images/20221204/1670166711_638cb8b73451e47ec1773.png!small)

我们建议使用Ubuntu 21.04环境。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/h3xduck/TripleCross.git

## 代码编译

    
    
    # 构建rootkit
    
    cd src
    
    make all
    
    # 构建rootkit客户端
    
    cd client
    
    make

## Rootkit安装

Rootkit文件生成后可以在src/bin/目录下查看，我们必须按顺序加载tc.o和kit程序。下列样例中，Rootkit后门将会在网络接口enp0s3中操作：

    
    
    // TC egress program
    
    sudo tc qdisc add dev enp0s3 clsact
    
    sudo tc filter add dev enp0s3 egress bpf direct-action obj bin/tc.o sec classifier/egress
    
    // Libbpf-powered rootkit
    
    sudo ./bin/kit -t enp0s3

![](https://image.3001.net/images/20221204/1670166736_638cb8d02abdafee998d2.png!small)

## 工具使用演示

### TCP转储

![](https://image.3001.net/images/20221204/1670166753_638cb8e1acb2e74ad177e.png!small)

### sch props映射

![](https://image.3001.net/images/20221204/1670166761_638cb8e94e715649264ce.png!small)

### ASLR绕过

![](https://image.3001.net/images/20221204/1670166799_638cb90f4da2b196f6ba4.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/h3xduck/TripleCross/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **TripleCross** ：【[ _GitHub传送门_](https://github.com/h3xduck/TripleCross)】

## 参考资料

> [
> _https://github.com/h3xduck/TripleCross/blob/master/docs/ebpf_offensive_rootkit_tfg.pdf_](https://github.com/h3xduck/TripleCross/blob/master/docs/ebpf_offensive_rootkit_tfg.pdf)
>
> [ _https://raw.githubusercontent.com/nccgroup/ebpf/master/talks/Evil_eBPF-> DC27-v2.pdf_](https://raw.githubusercontent.com/nccgroup/ebpf/master/talks/Evil_eBPF-> DC27-v2.pdf)
>
> [ _https://www.you_ _*_
> _tube.com/watch?v=g6SKWT7sROQ_](https://www.youtube.com/watch?v=g6SKWT7sROQ)
>
> [
> _https://media.defcon.org/DEF%20CON%2029/DEF%20CON%2029%20presentations/Guillaume%20Fournier%20Sylvain%20Afchain%20Sylvain%20Baubeau%20-%20eBPF%2C%20I%20thought%20we%20were%20friends.pdf_](https://media.defcon.org/DEF%20CON%2029/DEF%20CON%2029%20presentations/Guillaume%20Fournier%20Sylvain%20Afchain%20Sylvain%20Baubeau%20-%20eBPF%2C%20I%20thought%20we%20were%20friends.pdf)
>
> [ _https://github.com/kris-nova/boopkit_](https://github.com/kris-> nova/boopkit)

