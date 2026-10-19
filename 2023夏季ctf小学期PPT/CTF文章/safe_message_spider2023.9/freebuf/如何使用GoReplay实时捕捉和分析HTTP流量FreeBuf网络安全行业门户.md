![](https://image.3001.net/images/20220708/1657285498_62c82b7a27d914c5dbcf7.png!small)  

## 关于GoReplay

GoReplay是一款功能强大的开源网络监控工具，该工具可以帮助广大研究人员捕捉、监控和记录实时HTTP流量，并将其重放到测试环境中，以便使用真实数据来进行实现分析系统的数据连贯性。除此之外，该工具还能够提升代码部署、配置修改和基础架构的数据完整性。

值得一提的是，该工具所采用的先进技术将允许我们在不影响应用程序流量的情况下分析和记录应用程序流量，这也消除了将第三方组件存在于业务关键路径中所带来的风险。

GoReplay不是代理，而是在后台侦听网络接口上的流量，不需要更改生产基础结构，只需在机器上运行GoReplay守护进程即可。

## 工具运行机制

![](https://image.3001.net/images/20220708/1657285511_62c82b87034bb9297bc3c.png!small)

## 工具安装

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/buger/goreplay/releases)】获取最新版本的GoReplay已编译源码。

除此之外，我们也可以自行动手针对macOS和Linux来编译GoReplay源码。

GoReplay基于Go语言开发，因此我们首先需要在本地设备上安装并配置好Go语言环境。

接下来，安装好GoReplay所需的[ _libpcap_](https://github.com/the-tcpdump-group/libpcap)库，这个库将作为各种内核包捕捉机制的接口。以然后安装[
_gopacket_](https://github.com/google/gopacket)，即针对[
_libpcap_](http://www.tcpdump.org/release/)的Go封装器。

接下来，运行下列命令即可：

    
    
    # Fetch libpcap dependencies. Depending on your OS, instead of `apt` you will use `yum` or `rpm`, or `brew` on Mac.
    
    sudo apt-get install flex bison -y
    
     
    
    # Download latest stable release, compile and install it
    
    wget http://www.tcpdump.org/release/libpcap-1.7.4.tar.gz && tar xzf libpcap-1.7.4.tar.gz
    
    cd libpcap-1.7.4
    
    ./configure && make install
    
     
    
     
    
    # Lets fetch Gor source code
    
    mkdir $HOME/gocode
    
    # See more information about GOPATH https://github.com/golang/go/wiki/GOPATH
    
    export GOPATH=$HOME/gocode
    
    # Fetch code from the Github
    
    go get github.com/buger/gor
    
     
    
    # Compile from source
    
    cd $HOME/gocode/src/github.com/buger/gor
    
    go build LDFLAGS = -ldflags "-extldflags \"-static\""

## 工具使用

如果你已经搭建好了测试环境，那么直接运行下列命令便可执行GoReplay操作：

    
    
    sudo ./gor --input-raw :8000 --output-http http://staging.env

### 捕捉Web流量

下列命令将监听端口8000的所有网络活动，并将其记录到stdout：

    
    
    sudo ./gor --input-raw :8000 --output-stdout

接下来，
在浏览器中打开http://localhost:8000并发送一些请求，你将会在GoReplay中看到输出的所有HTTP请求，此时我们可以运行下列命令追踪请求的响应信息：

    
    
    --output-http-track-response

### 流量重放

此时，我们就可以将捕捉到的原始流量重返到测试环境中了。下列命令可以开启另一台不同端口的文件Web服务器：

    
    
    gor file-server :8001

使用“--output-http”选项并提供第二台服务器的URL：

    
    
    sudo ./gor --input-raw :8000 --output-http="http://localhost:8001"

### 存储文件请求（以便之后重放）

某些情况下，你可能不需要立即重放捕捉到的流量，因此我们可以将其存储到文件中以备后续使用。

首先，使用“--output-file”选项存储捕捉到的流量：

    
    
    sudo ./gor --input-raw :8000 --output-file=requests.gor

接下来，使用下列命令重放捕捉到的流量：

    
    
    ./gor --input-file requests.gor --output-http="http://localhost:8001"

## 工具演示视频

 **视频地址** ：[
_https://www.you*tube.com/watch?v=CxuKZcMKaW4_](https://www.youtube.com/watch?v=CxuKZcMKaW4)

## 许可证协议

本项目的开发与发布遵循[
_LGPLv3_](https://github.com/buger/goreplay/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **GoReplay** ：【[ _GitHub传送门_](https://github.com/buger/goreplay)】

## 参考资料

> [ _https://goreplay.org/_](https://goreplay.org/)
>
> [
> _http://github.com/buger/goreplay/wiki_](http://github.com/buger/goreplay/wiki)
>
> [ _https://github.com/the-tcpdump-group/libpcap_](https://github.com/the-> tcpdump-group/libpcap)
>
> [ _http://www.tcpdump.org/release/_](http://www.tcpdump.org/release/)

