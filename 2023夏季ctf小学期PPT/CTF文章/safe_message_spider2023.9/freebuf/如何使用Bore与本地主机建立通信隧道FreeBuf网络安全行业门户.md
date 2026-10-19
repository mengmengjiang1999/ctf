![](https://image.3001.net/images/20220507/1651853289_627547e9247bb69f73c85.jpeg!small)

## 关于Bore

Bore是一款功能强大的现代化命令行CLI工具，在该工具的帮助下，广大研究人员可以轻松与本地主机localhost建立通信隧道。Bore基于Rust开发，可以将本地端口暴露给远程服务器，并能够绕过标准NAT连接防火墙。

该工具易于安装和使用，且支持自托管。跟[
_localtunnel_](https://github.com/localtunnel/localtunnel)和[
_ngrok_](https://ngrok.io/)类似，但Bore旨在实现一种高效的、无需添加任何额外组件的解决方案，而且可以执行TCP流量转发。

## 工具安装

由于Bore基于Rust开发，因此广大研究人员首先需要在本地设备上安装并配置好Rust环境。

我们可以直接访问该项目的【[
_Releases页面_](https://github.com/ekzhang/bore/releases)】下载macOS、Windows或Linux版本的Bore预编译代码。然后解压并运行Bore可执行程序即可。

或者，也可以使用Rust的包管理器[ _Cargo_](https://doc.rust-lang.org/cargo/)来从源码构建Bore，使用下列命令即可安装Bore：

    
    
    cargo install bore-cli

接下来，在本地设备上运行下列命令即可执行Bore：

    
    
    bore local 8000 --to bore.pub

上述命令将会把“localhost:8000”暴露给外网地址“bore.pub:<PORT>”，其中的PORT端口号是随机分配的。

除此之外，广大研究人员也可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ekzhang/bore.git

### Docker使用

我们还发布了Bore的Docker镜像，每一个镜像都提供了AMD 64位和ARM 64位架构的版本：

    
    
    docker run -it --init --rm --network host ekzhang/bore <ARGS>

## 工具使用

### 本地转发

我们可以通过使用“bore local”命令来转发本地设备的端口数据，并使用“--to”参数来指定远程服务器地址：

    
    
    bore local 5000 --to bore.pub

除此之外，还可以使用“--port”参数来指定远程主机暴露的端口。“--local-host”还支持在本地局域网中暴露不同的主机，而不只是localhost。

 **命令完整选项如下：**

    
    
    bore-local 0.4.0
    
    Starts a local proxy to the remote server
    
     
    
    USAGE:
    
        bore local [OPTIONS] --to <TO> <LOCAL_PORT>
    
     
    
    ARGS:
    
        <LOCAL_PORT>        暴露的本地端口
    
     
    
    OPTIONS:
    
        -h, --help                打印帮助信息
    
        -l, --local-host <HOST>    暴露的本地主机，默认为localhost
    
        -p, --port <PORT>         选择远程服务器的端口，默认为0
    
        -s, --secret <SECRET>     选择认证所需的密钥[env: BORE_SECRET]
    
        -t, --to <TO>              远程服务器的地址
    
        -V, --version              打印版本信息

### 自托管

Bore执行之后，相当于在“bore.pub”运行了一个公共的Bore服务器实例。但是，如果你想要在本地网络上自托管Bore的话，可以使用下列命令：

    
    
    bore server

该命令支持的完整选项如下：

    
    
    bore-server 0.4.0
    
    Runs the remote proxy server
    
     
    
    USAGE:
    
        bore server [OPTIONS]
    
     
    
    OPTIONS:
    
        -h, --help                     打印帮助信息
    
            --min-port <MIN_PORT>   接受的最小TCP端口号，默认为1024
    
        -s, --secret <SECRET>        选择认证所需的密钥[env: BORE_SECRET]
    
        -V, --version                  打印版本信息

### 认证

 **服务器端命令** ：

    
    
    bore server --secret my_secret_string

 **客户端命令：**

    
    
    bore local <LOCAL_PORT> --to <TO> --secret my_secret_string

## 工具使用演示

![](https://image.3001.net/images/20220507/1651853398_627548564a0c35448454c.gif)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/ekzhang/bore/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Bore：** 【[ _GitHub传送门_](https://github.com/ekzhang/bore)】

## 参考资料

> [
> _https://github.com/localtunnel/localtunnel_](https://github.com/localtunnel/localtunnel)
>
> [ _https://ngrok.io/_](https://ngrok.io/)
>
> [ _https://doc.rust-lang.org/cargo/_](https://doc.rust-lang.org/cargo/)

