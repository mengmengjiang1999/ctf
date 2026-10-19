**今天给大家介绍的是一款名叫Rock-ON的网络侦察工具，它是一款多功能合一的情报侦察工具，广大研究人员只需要给它提供一个域名地址，剩下的工作就可以交给Rock-ON来完成啦！**  

![1.jpg](https://image.3001.net/images/20190721/1563696346_5d341cda7cd70.jpg!small)

## 一、工具介绍

Rock-On是一款集多功能于一身的网络侦查工具，它可以给广大研究人员的网络侦查活动提供帮助。它的主要功能是将整个网络侦查过程中需要手动处理的过程全部以自动化的方式实现，以帮助研究人员节省时间上的开支。

### 2.1.功能介绍

> 1、 子域名爬取
>
> 2、 搜索A.S.N -> NetBlock ->IP地址
>
> 3、 地址解析
>
> 4、 搜索端口
>
> 5、 搜索VHost
>
> 6、 搜索目录
>
> 7、 搜索次级域名
>
> 8、 资产跟踪&实时监控
>
> 9、 Slack通知推送
>
> 10、搜索JS链接&相关链接&敏感文件
>
> 11、主动/被动爬取

### 2.2.工具使用建议

设备配置：Debian（v9.4）、4GB RAM（DigitalOcean），VPS

## 二、基于Censys

首先，我们需要在sub.sh中设置API以及相应的密钥。

如需移除：

> 1、 删除第13-18行；
>
> 2、 在第47和48行设置你的API以及相应的密钥：
    
    
    export CENSYS_API_ID=your_key_here

Slack通知推送

在sub.sh、ASN.sh、Sublert.py和config.py中修改你的WebHook地址，修改方式如下：

> 1、 替换sub.sh中第113行以及ASN.sh中第15行的WebHook地址；
>
> 2、 替换Tools/sublert/config.py中的WebHook地址；

配置手册：【[参考文档](https://medium.com/@yassineaboukir/automated-monitoring-of-subdomains-for-fun-and-profit-release-of-sublert-634cfc5d7708)】

### 2.1.引用代码库

开发人员在实现Rock-On的过程中，使用到了社区中大量优秀的代码库，其中包括：

    
    
    1.Sublist3r
    
    2.Knock
    
    3.Subfinder
    
    4.Censys
    
    5.Amass
    
    6.CTLogs
    
    7.CTFR
    
    8.Wayback
    
    9.SanDomains
    
    10.AltDns
    
    11.NMAP
    
    12.Masscan
    
    13.MassDNS
    
    14.Sublert
    
    15.Aquatone
    
    16.Vhost
    
    17.Rapid7FDNS DB
    
    18.AWS-CLI
    
    19.Dirsearch

## 三、工具依赖

### 3.1.Go语言环境

大家可以使用下列命令配置Go环境：

    
    
    wget <https://dl.google.com/go/go1.12.5.linux-amd64.tar.gz>
    
    tar -C /usr/local -xzfgo1.12.5.linux-amd64.tar.gz
    
    rm -f go1.12.5.linux-amd64.tar.gz
    
    nano ~/.profile

完成之后，需要在.profile文件中添加下列配置代码：

    
    
    export PATH=$PATH:/usr/local/go/bin
    
    export GOROOT=/usr/local/go

## 四、工具安装

如果你使用的是一台全新的VPS，请在安装之前运行下列代码：

    
    
    sudo apt-get upgrade && sudo apt-getupdate && sudo apt-get install git

接下来，使用git命令将Rock-On从GitHub代码库克隆至本地：

    
    
    git clone <https://github.com/SilverPoision/Rock-ON.git>
    
    cd Rock-ON
    
    chmod +x rockon.sh
    
    ./rockon.sh
    
    1

除此之外，别忘了使用下列命令配置你的AWS凭证：

    
    
    aws configure

## 五、工具使用

运行下列命令：

    
    
    ./rockon.sh

然后根据你的需求来选择相应的功能。

工具运行截图：

![2.png](https://image.3001.net/images/20190721/1563696443_5d341d3badbbd.png!small)

![3.png](https://image.3001.net/images/20190721/1563696449_5d341d4147c21.png!small)

如果你需要选择第四个选项，那么在首次使用之前需要先运行下列命令：

    
    
    gem install colorize

## 六、项目地址

> Rock-On：【[GitHub传送门](https://github.com/SilverPoision/Rock-ON)】

 *** 参考来源：[SilverPoision](https://github.com/SilverPoision/Rock-ON)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

