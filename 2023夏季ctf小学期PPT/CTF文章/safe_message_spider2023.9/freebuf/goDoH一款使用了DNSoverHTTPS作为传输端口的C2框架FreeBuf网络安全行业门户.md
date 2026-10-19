**今天给大家介绍的是一款名叫goDoH的工具，该工具基于DNS-over-HTTPS实现，是一款远程命令控制框架，并且可以将DNS-over-HTTPS作为传输端口来使用。**

![](https://image.3001.net/images/20190914/1568453117_5d7cb1fd1b0c5.png!small)

##  工具介绍

goDoH是一款概念验证命令与控制框架，该工具采用Golang开发，并使用了DNS-over-HTTP作为传输介质。

###  项目依赖

goDoH的代码构建需要使用到Dep（【[GitHub传送门](https://github.com/golang/dep)】），Dep是一款针对Go语言的依赖管理工具。

在macOS平台上，我们可以使用Homebrew来安装或更新Dep：

    
    
    $ brew install dep
    
        $ brew upgrade dep

在Debian平台上，我们可以直接使用apt-get来安装或更新Dep：

    
    
    $ sudo apt-get install go-dep

在Windows平台上，可以直接点击【[这里](https://go.equinox.io/github.com/golang/dep/cmd/dep)】下载tarball。

在其他平台上，你可以使用install.sh脚本完成安装：

    
    
    $ curl https://raw.githubusercontent.com/golang/dep/master/install.sh | sh

##  工具安装

我们现在只需要安装godoh代码本身即可，我们可以从该项目的releases页面直接下载项目代码，下载完成之后，请按照下列步骤对项目代码进行构建：

1、确保已安装好了[Dep](https://github.com/golang/dep)：

    
    
    go get -v -u github.com/golang/dep/cmd/dep

2、将该项目的源码克隆值本地设备中$GOPATH的src/目录中（sensepost/godoh）；

3、运行下列命令来解析依赖：

    
    
    dep ensure

4、运行下列命令生成用于通信的唯一加密秘钥：

    
    
    make key

5、使用go构建工具，或运行“make”命令来构建build/目录中的项目代码；

##  工具使用

    
    
    $ godoh -h
    
        A DNS (over-HTTPS) C2
    
            Version: dev
    
            By @leonjza from @sensepost
    
        Usage:
    
          godoh [command]
    
        Usage:
    
          godoh [command]
    
        Available Commands:
    
          agent       Connect as an Agent to the DoH C2
    
          c2          Starts the godoh C2 server
    
          help        Help about any command
    
          receive     Receive a file via DoH
    
          send        Send a file via DoH
    
          test        Test DNS communications
    
        Flags:
    
          -d, --domain string     DNS Domain to use. (ie: example.com)
    
          -h, --help              help for godoh
    
          -p, --provider string   Preferred DNS provider to use. [possible: google, cloudflare, raw] (default "google")
    
        Use "godoh [command] --help" for more information about a command.

###  许可证协议

goDoH项目开发遵循[GNU General Public
v3](https://www.gnu.org/licenses/gpl-3.0.en.html)开源许可证协议。

#
![](https://image.3001.net/images/20190914/1568453165_5d7cb22d70b4c.png!small)

##  项目地址

> goDoH：【[GitHub传送门](https://github.com/sensepost/goDoH)】

 ***
参考来源：[sensepost](https://github.com/sensepost/goDoH)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

