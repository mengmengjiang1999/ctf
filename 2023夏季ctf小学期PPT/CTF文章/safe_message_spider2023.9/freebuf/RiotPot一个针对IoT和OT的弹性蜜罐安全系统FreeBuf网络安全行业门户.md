![](https://image.3001.net/images/20220120/1642664148_61e910d4ddad940adb9d1.png!small)

## 关于RiotPot

RiotPot是一个功能强大的弹性蜜罐系统，RiotPot主要针对的是IoT和OT协议，并且支持用户交互操作。

RiotPot支持插件机制，这些服务能够以插件的形式加载到蜜罐中，并使RIoTPot成为一个模块化的、可移植的蜜罐系统。服务是在运行时加载的，这意味着蜜罐的提及将根据情况而变化，并且加载的服务（例如HTTP）仅会在需要时使用。因此，我们强烈建议广大研究人员根据自己的需要定制自己的二进制文件。

## 系统架构

RiotPot有一个模块化的体系结构，用于支撑RiotPot蜜罐的可扩展性。除此之外，蜜罐还提供了混合交互功能，用户可以为模拟的协议选择所需的交互级别。下图显示的是RIoTPot的高级架构体系：

![](https://image.3001.net/images/20220120/1642664158_61e910de0ed3bf25a12d6.jpg!small)

## 噪音过滤

RiotPot的噪音过滤模块可以过滤来自互联网扫描引擎的攻击，以降低噪音和误报。在该模块的帮助下，但系统遭到了来源于Shodan等源的攻击时，会被标记为“良性”。RiotPot支持的扫描服务列表如下：

> Shodan (https://www.shodan.io/)
>
> Censys (https://censys.io/)
>
> Project Sonar (https://www.rapid7.com/research/project-sonar/)
>
> LeakIX (https://leakix.net/)
>
> ShadowServer (https://www.shadowserver.org/)
>
> RWTH Aachen (http://researchscan.comsys.rwth-aachen.de/)
>
> Quadmetrics (https://www.quadmetrics.com/)
>
> BinaryEdge (https://www.binaryedge.io/})
>
> ipip.net (https://en.ipip.net/)
>
> Arbor Observatory (https://www.arbor-observatory.com/)
>
> CriminalIP (https://security.criminalip.com/)
>
> BitSight (https://www.bitsight.com/)
>
> InterneTT (http://www.internettl.org/)
>
> ONYPHE (https://www.onyphe.io/)
>
> Natlas (https://github.com/natlas/natlas)
>
> Net Systems Research (https://www.netsystemsresearch.com/)
>
> Sharashka (https://sharashka.io/data-feeds)
>
> Alpha Strike Labs (https://www.alphastrike.io)
>
> Stretchoid (http://stretchoid.com/)

## 工具安装

我们的理念是使RIoTPot具有高度的可移植性，我们强烈建议使用Docker在一个虚拟化的自包含网络中运行RiotPot。

RiotPot基于Golang开发，因此我们首先需要在环境中安装并配置好Go环境。

首先，在本地文件系统中创建一个文件夹：

    
    
    $ mkdir -p $GOPATH/src/github.com

在命令行终端内切换至项目目录：

    
    
    $ mkdir -p $GOPATH/src/github.com

使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone git@github.com:aau-network-security/riotpot.git

然后切换至riotpot目录中：

    
    
    $ cd riotpot

## Docker使用

在RiotPot的开发目录下，有一个docker-compose文件：

    
    
    $ cd ~/riotpot/deployments | ls -al
    
    ...
    
    -rw-r--r--  docker-compose.yml
    
    ...

这个文件对应于相应的软件开发环境。

docker-compose.yml文件会在一个私有虚拟网络中构建该项目，其中有三台主机：riotpot、postgres和tcpdump。ostgres包含一个Postgres数据库，tcpdump包含一个数据包捕获器，riotpot包含应用程序本身，并且三者之间可以进行交互。在终端内输入下列命令，可以直接在本地开发和测试RiotPot：

    
    
    $ docker-compose -f docker-compose.yml up -d --build

蜜罐使用完毕后，可以使用下列命令来关闭容器：

    
    
    $ docker-compose down -v

### Docker Hub镜像

    
    
    # Grab and run the latest release of the riotpot consumer image
    
    # detached from the console with -d.
    
    $ docker run -d riotpot-docker:latest

## 本地使用

我们也可以通过项目源代码构建自己的代码，导航至项目目录中，然后使用命令行工具生成代码并存储至.bin/目录中：

    
    
    # build the binary in the ./bin folder
    
    $ go build -o riotpot cmd/riotpot/main.go

或者，我们也可以直接使用下列命令在本地系统中直接安装RiotPot：

    
    
    # installs riotpot at $GOPATH/bin
    
    $ go install

然后直接运行RiotPot即可：

    
    
    $ ./riotpot

## 项目地址

 **RiotPot：** 【[ _GitHub传送门_](https://github.com/aau-network-security/riotpot)】

## 参考资料

> [ _https://golang.org/_](https://golang.org/)
>
> [ _https://docs.docker.com/_](https://docs.docker.com/)
>
> [ _https://pkg.go.dev/_](https://pkg.go.dev/)
>
> [
> _https://pkg.go.dev/golang.org/x/tools/cmd/godoc_](https://pkg.go.dev/golang.org/x/tools/cmd/godoc)

