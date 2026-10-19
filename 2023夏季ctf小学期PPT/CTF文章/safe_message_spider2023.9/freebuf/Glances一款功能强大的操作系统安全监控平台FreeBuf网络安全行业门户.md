![](https://image.3001.net/images/20191203/1575355006_5de6027e41423.jpg!small)

**Glances是一款跨平台的安全监控工具，该工具可以通过一个curse或Web界面来帮助研究人员完成大规模数据监控，这些所有的数据回根据用户接口的情况来进行动态适配。**

 **** 它还能够以客户端/服务器端模式运行，远程监控可以通过终端、Web接口或API（XML-RPC和RESTful）来实现。除此之外，数据还可以导出至文件或外部数据库中。 ****

Glances采用Python开发，并使用了外部库来从目标系统收集数据。该工具基于开源架构实现，开发者可以根据自己的需求来增加新的插件或导出模块。

##  工具要求

> 1、Python 2.7，>=3.4
>
> 2、Psutil >= 5.3.0

###  可选依赖

> bernhard ( Riemann 导出模块)
>
> bottle ( Web 服务器模式)
>
> cassandra-driver ( Cassandra 导出模块)
>
> couchdb ( CouchDB 导出模块)
>
> docker ( Docker 监控支持) [Linux/macOS-only]
>
> elasticsearch ( Elastic 搜索导出模块)
>
> hddtemp ( HDD 温度监控支持) [Linux-only]
>
> influxdb ( InfluxDB 导出模块)
>
> kafka-python ( Kafka 导出模块)
>
> netifaces ( IP 插件)
>
> nvidia-ml-py3 ( GPU 插件)
>
> pika ( RabbitMQ/ActiveMQ 导出模块)
>
> potsdb ( OpenTSDB 导出模块)
>
> prometheus_client ( Prometheus 导出模块)
>
> py-cpuinfo ( Quicklook CPU 信息模块)
>
> pygal ( graph 导出模块)
>
> pymdstat ( RAID 支持) [Linux-only]
>
> pySMART.smartx ( HDD Smart 支持) [Linux-only]
>
> pysnmp ( SNMP 支持)
>
> pystache ( 脚本功能 )
>
> pyzmq ( ZeroMQ 导出模块)
>
> requests ( Ports, Cloud 插件和RESTful 导出模块)
>
> scandir ( Folders 插件) [Python < 3.5]
>
> statsd ( StatsD 导出模块)
>
> wifi ( wifi 插件) [Linux-only]
>
> zeroconf (自动发现模式)

##  工具安装

###  Glances自动安装脚本

安装依赖组件以及最新版本的Glances产品，请运行下列命令：

    
    
    curl -L https://bit.ly/glances | /bin/bash

或

    
    
    wget -O- https://bit.ly/glances | /bin/bash

###  PyPI安装方法

Glances目前已托管在了PyPI上，我们可以使用PyPI来安装最新的稳定版本：

    
    
    pip install glances

如果需要使用可选功能的话，我们需要安装下列库（例如Web接口和导出模块等）：

    
    
    pip install 'glances[action,browser,cloud,cpuinfo,docker,export,folders,gpu,graph,ip,raid,snmp,web,wifi]'

更新Glances至最新版本：

    
    
    pip install --upgrade glances
    
        pip install --upgrade glances[...]

如果你需要在特定路径安装Glances的话，请运行下列命令：

    
    
    export PYTHONUSERBASE=~/mylocalpath
    
        pip install --user glances

##  Docker安装

Glances提供了Docker容器，其中包含了最新版本的开发版HEAD，我们可以用它来监控服务器或其他的容器。

获取Glances容器：

    
    
    docker pull nicolargo/glances

以控制台模式运行容器：

    
    
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host --network host -it docker.io/nicolargo/glances

除此之外，如果你想使用自己的glances.conf文件，你需要创建自己的Docker文件：

    
    
    FROM nicolargo/glances
    
        COPY glances.conf /glances/conf/glances.conf
    
        CMD python -m glances -C /glances/conf/glances.conf $GLANCES_OPT

当然了，你还可以在同一行命令中添加Docker的运行参数：

    
    
    docker run -v `pwd`/glances.conf:/glances/conf/glances.conf -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host -it docker.io/nicolargo/glances

以Web服务器模式运行容器：

    
    
    docker run -d --restart="always" -p 61208-61209:61208-61209 -e GLANCES_OPT="-w" -v /var/run/docker.sock:/var/run/docker.sock:ro --pid host docker.io/nicolargo/glances

##  FreeBSD

安装源码包：

    
    
    # pkg install py27-glances

Port安装：

    
    
    # cd /usr/ports/sysutils/py-glances/
    
        # make install clean

##  macOS安装

如果你不需要使用glances自动安装脚本，请遵循下列安装步骤。macOS用户可以使用Homebrew或MacPorts来安装Glances：

###  Homebrew

    
    
    $ brew install glances

###  MacPorts

    
    
    $ sudo port install glances

##  Windows安装

Windows平台下安装Python，并运行下列命令：

    
    
    $ pip install glances

或者使用下列命令将项目克隆至本地：

    
    
    $ git clone <https://github.com/nicolargo/glances.git>
    
        $ cd glances
    
        $ python setup.py install

##  Android

在设备上开启Termux，并运行下列命令：

    
    
    $ apt update
    
        $ apt upgrade
    
        $ apt install clang python python-dev
    
        $ pip install bottle
    
        $ pip install glances

开启Glances：

    
    
    $ glances

##  源码安装

    
    
    $ wget <https://github.com/nicolargo/glances/archive/vX.Y.tar.gz> -O - | tar xz
    
        $ cd glances-*
    
        # python setup.py install

##  工具使用

单一模式运行：

    
    
    $ glances

Web服务器模式运行：

    
    
    $ glances -w http://<ip>:61208

客户端模式运行：

    
    
    $ glances -s

服务器模式运行：

    
    
    $ glances -c <ip>

检测并查看所有的Glances服务器：

    
    
    $ glances --browser

我们还可以查看原始stats数据：

    
    
    $ glances --stdout cpu.user,mem.used,load
    
        cpu.user: 30.7
    
        mem.used: 3278204928
    
        load: {'cpucore': 4, 'min1': 0.21, 'min5': 0.4, 'min15': 0.27}
    
        cpu.user: 3.4
    
        mem.used: 3275251712
    
        load: {'cpucore': 4, 'min1': 0.19, 'min5': 0.39, 'min15': 0.27}
    
        ...

以CSV格式导出数据：

    
    
    $ glances --stdout-csv now,cpu.user,mem.used,load
    
        now,cpu.user,mem.used,load.cpucore,load.min1,load.min5,load.min15
    
        2018-12-08 22:04:20 CEST,7.3,5948149760,4,1.04,0.99,1.04
    
        2018-12-08 22:04:23 CEST,5.4,5949136896,4,1.04,0.99,1.04
    
        ...

##  项目地址

> Glances：【[GitHub传送门](https://github.com/nicolargo/glances)】

##  参考文档

> 1、<https://glances.readthedocs.io/>

 *** 参考来源：[checkpoint](https://research.checkpoint.com/2019/ponys-cc-servers-hidden-inside-the-bitcoin-blockchain/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

