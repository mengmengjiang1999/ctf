## 一、SELKS 简介

### 1.SELKS 社区版

随着数字经济快速发展和成熟，网络安全重要性地位越来越高，而中小企业在产业链中具有举足轻重的作用，由于中小企业中，缺乏网络安全专业人员，企业面临的网络安全威胁的风险进一步加大，急需一款能开箱即用的网络安全系统。

SELKS是Stamus
Networks公司（位于美国印第安纳州，主要研发Suricata安全产品,OISF执行团队的成员）所开发开源ELK项目，该项目具有带GUI功能的Suricata规则管理系统以及网络威胁搜索功能，SELKS社区版是在GPL
v3许可证下发布。

本文介绍的社区版SELKS 7 适合这种场景。社区版SELKS（7是目前的最新版本）包括5个关键开源组件：

S --Suricata

E --Elasticsearch

L --Logstash

K --Kibana

S-- Scirius-CE (包含Suricata Management 和 Suricata Hunting）

  
从这几个字母的组合可以看出，该系统是基于Suricata的全套解决方案，从SELKS
1.0版开始，技术架构通过Suricata+ELK+Scirius实现。

注：Scirius
采用Django开发，用于Suricata规则集管理的应用程序。另外系统中还有两个重要组件分别是Arkime(原Moloch）和Evebox，主要用于网络Session通信分析和分析报警，都是威胁狩猎中不可或缺的工具。

既然Arkime和Evebox都很重要，为什么没有把它们的首字母加到SELKS中？这要从SELKS
1.0发布日期说起，最早的这个版本发布于2014年10月，当时Arkime和Evebox都还没有诞生，这就是原因所在。

### 2.SELKS社区版的局限

 **开源“不是免费的午餐”**
，在SELKS社区版中Scirius仅能管理1个规则集，Suricata只能调用默认规则集。社区版仅支持一个Suricata探针。

![1687267209_6491a789b8433e1c189f7.png!small?1687267209837](https://image.3001.net/images/20230620/1687267209_6491a789b8433e1c189f7.png!small?1687267209837)

当企业内网中存在多个VLAN，如要部署社区版SELKS，需要在每个VLAN中分别部署,各系统间无关联。

### 3.Stamus 安全平台

StamusNetwork公司在商业版产品Stamus Security
Platform(SSP)中提供了NSM和NDR功能和社区版中提供的IDS共同组成了Stamus安全平台。在SSP（商业版）中支持多传感器部署，系统架构如下图所示。多个传感器将收集的数据发送到管理端集中分析。

![1687267315_6491a7f3d27ed4ae2b31a.png!small?1687267315855](https://image.3001.net/images/20230620/1687267315_6491a7f3d27ed4ae2b31a.png!small?1687267315855)

### 4.SELKS社区版和SSP功能对比

相对于社区版，在SSP中支持多传感器、多规则集，以及IDS 事件、网络流量分析关联分析，更多区别大家可参考下列网址：
<https://www.stamus-networks.com/selks#selks>

  

## 二、威胁狩猎

### 1.基本概念

威胁狩猎（Threat Hunting）是一种主动查询攻击踪迹的方法，就像猎人猎杀猎物，猎人猎杀猎物之后都要拔掉一颗牙或者留下点什么作为纪念，但威胁
狩猎中，需要留存攻击线索。

威胁狩猎相比以前的网络受到攻击之后，调查人员进行取证这种过程，更加主动，更加具有想象（一种假设）更加具有战术效果，就是通过搜索到的数据来证明之前的假设。例如安全分析师在日志或者仪表板中发现某个内网陌生IP在持续访问外网IP的敏感端口，但也不确定该连接是正常流量，威胁狩猎人员利用各种工具和经验从海量数据中过滤出相关数据（也就是可疑数据），再利用威胁情报系统，调查这些IP的档案，最终证明假设是否成立。

### 2.收集内容

SELKS中实现威胁狩猎的工具是Suricata，所有数据都来源于Suricata中网络流量内容的分析，最后把详细日志信息存放在eve.json文件，所以威胁狩猎需要收集的信息就来源于此。

 **1）.网络流数据**

分析师从连接本身的metadata数据开始分析。比如哪些IP地址在什么时候使用什么端口与其他IP地址通信，传输了多少数据，哪一方发起连接，连接持续了多长时间。分析师通过这些数据来对判断网络的状况。但对于威胁狩猎而言，分析师还需要获取网络协议信息。

 **2）.网络协议数据**

TCP / IP/ UDP

 **3）.服务器日志**

服务器事件日志包括DNS查询和响应，HTTP查询，DHCP日志、SMB、SSH、SMTP等。

## 三、SELKS架构

目前版本的SELKS
7可部署在Ubuntu/CentOS各种操作系统，就在于它采用了Docker容器技术，不会受到操作系统版本的影响，但缺点是安装过程严重依赖网络，无法做到离线安装。

### 1.简体架构

新版系统中采用Portainer CE 作为容器的Web管理工具，非常适合新手小白管理Docker。
Suricata也安装在容器中，但Suricata不适用容器网络，而是直接连接到宿主机的网络接口。
Logstash+Elasticsearch+Kibana+EveBOX+Scirius+Arkime+Nginx他们分别安装在自己的容器中，共用容器提供的网络。各个容器中计划任务由cron容器负责。它安装在单独网段。为了便于理解笔者将实际架构做了拆解并做了简化系统架构如下：

![1687267608_6491a91835653f93d7eca.png!small?1687267608273](https://image.3001.net/images/20230620/1687267608_6491a91835653f93d7eca.png!small?1687267608273)

上图展示的就是将传统Suricata+ELK转换为基于Docker容器的架构。下面这段视频是通过Portainer结合Suricata、ELK、Nginx这几个容器的通信原理进行简要说明。

### 2.容器间数据共享

  
Suricata容器、logstatsh容器共享本地硬盘的数据。

  

## 四、系统安装

  
AT&T发布的开源OSSIM系列安全产品都是在Debian
Linux操作系统上开发，今天所介绍的SELKS从1.0开始也都是在Debian系统上做的二次开发，这些全球知名的安全厂商选用Debian系统作为开发平台，Debian有着超强的安全性和稳定性，特别适应于需要长期运行的服务器环境。

### 1.安装准备

  
初次使用该系统，建议在VMware虚拟机环境下完成，硬件配置清单如下：

CPU 4+ core  
RAM 12G +  
Disk 50G+  
NIC 1  
注：如采用VirtualBOX虚拟机，安装网卡需设置嗅探模式。

### 2.基于ISO安装

  
由ISO引导系统后，选择第三项菜单，安装过程跟Debian Linux基本一致。

### 3.基于Dockers容器安装

  
由于安装过程严重依赖网络，所以网络环境需通畅，安装命令如下：

    
    
    git clone https://github.com/StamusNetworks/SELKS.git
    cd SELKS/docker/
    ./easy-setup.sh
    sudo docker compose up -d

在这几个步骤中，最要的是easy-setup.sh脚本，主要功能是检查docker和docker
compose是否安装正确版本，生成Nginx的SSL证书和创建密钥以及拉取容器的任务。作为最终用户并不需要掌握细节，除非需进行二次开发。

### 4.系统配置

  
操作系统安装完成，进入系统，首次运行SELKS7需要设置，由于架构的改变，方法不能沿用SELSK6里讲的内容，分为两种一种是交换式安装另一种是非交互式安装，都可以通过脚本实现。

### 5.参数配置

  
默认登录操作用户名selks-user，密码：selks-user，  
登录Web界面的用户名selks-user，密码：selks-user，  
图形界面采用Python django框架开发  
默认root用户密码：StamusNetworks  
系统默认使用Xfce桌面环境  
详细安装过程没有必要在本文中介绍，感兴趣的读者可以访问
https://edu.51cto.com/course/33730.html，学习[《开源入侵检测系统SELKS 7
安装与应用》](https://edu.51cto.com/course/33730.html)课程。

### 6.修改容器配置（以Suricata为例）

  
有时根据实验环境需要，我们需要修改Suricata容器的配置，首先我们要对现有suricata容器的配置有所了解。宿主机中输入下面命令：

    
    
    docker inspect suricata //获取镜像详细信息
    docker exec suricata suricata --build-info //检查Suricata配置信息
    docker exec -it suricata bash //进入suricata容器
    cat /etc/logrotate.d/suricata //在容器中查看日志轮训配置
    docker exec suricata logrotate -v /etc/logrotate.d/suricata $@ && echo "done." || echo "ERROR" //执行日志轮训
    cd /opt/selksd/SELKS/docker && docker-compose restart suricata //重启容器

我们想修改Suricata程序的配置，修改规则路径或添加额外的规则文件，无需编辑suricata.yaml，而只要修改selks6-addin.yaml即可。具体方法大家可参阅上面的课程。

注：对于logstash、kibana、arkime等容器操作参照上面的配置。

此外还有2个例外，进入cron、evebox容器分别输入下列命令：

    
    
    docker exec -it cron sh
    docker exec -it evebox sh

### 7.系统升级

  
SELKS更新系统非常方便，运行在Docker上跑SELKS,只需要下面几条命令就能升级到最新版本。

    
    
    git pull
    docker compose pull
    docker compose stop
    sudo -E docker compose up -d

注：升级前需备份各项服务配置文件，以免覆盖数据。

### 8.常见故障

  
无论是在系统安装阶段还是运维阶段或者是升级阶段都会遇到各种问题，下面举两个例子：

a) 启动容器故障

![1687297663_64921e7f6634d9d9ff694.png!small?1687297663899](https://image.3001.net/images/20230621/1687297663_64921e7f6634d9d9ff694.png!small?1687297663899)

b) 无法打开首页

![1687297702_64921ea60c072e79adf0b.png!small?1687297701881](https://image.3001.net/images/20230621/1687297702_64921ea60c072e79adf0b.png!small?1687297701881)

由于篇幅限制，更多故障解决方法，大家可以在课程中找到解决方法。

### 9.生产环境设置

  
上述硬件配置参数，仅适合于实验环境，对于生产环境，Elasticsearch需要分配内存64G，CPU内核为8 Core ，启动命令如下：

    
    
    cd /opt/selksd/SELKS/docker  
    ./easy-setup.sh  --non-interactive -i ens33 --iA --restart-mode always --es-memory 64G  
    sudo -E docker compose up -d

## 五、主要模块应用

SELKS系统中涉及的几个模块应用我们在课程中有详细讲解，在本文我们仅给出一些截图供参考。

###  
1.Suricata Management规则管理

![1687297862_64921f467584fcbfb753e.png!small?1687297862555](https://image.3001.net/images/20230621/1687297862_64921f467584fcbfb753e.png!small?1687297862555)

![1687297903_64921f6fdd199a244475c.png!small?1687297904644](https://image.3001.net/images/20230621/1687297903_64921f6fdd199a244475c.png!small?1687297904644)

 **可视化展示实时IP连接过程中的报警事件。**

![1687297936_64921f9009d6e46ff3605.png!small?1687297936081](https://image.3001.net/images/20230621/1687297936_64921f9009d6e46ff3605.png!small?1687297936081)

### 2.Suricata Threat Hunting

利用Suricata进行威胁狩猎

![1687297987_64921fc365935c106d6bb.png!small?1687297987486](https://image.3001.net/images/20230621/1687297987_64921fc365935c106d6bb.png!small?1687297987486)

### 3.EveBOX

Evebox是一个用来读取Suricata事件的Web应用程序，通过连接到Elasticsearch的TCP 9200端口实现。

![1687298247_649220c79851ec61c7051.png!small?1687298247787](https://image.3001.net/images/20230621/1687298247_649220c79851ec61c7051.png!small?1687298247787)

![1687299831_649226f732855e51e8e73.png!small?1687299831240](https://image.3001.net/images/20230621/1687299831_649226f732855e51e8e73.png!small?1687299831240)

下面举个实例，发现Malware，检测到 Cryptowall Malware 时系统报警。

![1687298589_6492221dc34837d00143d.png!small?1687298590419](https://image.3001.net/images/20230621/1687298589_6492221dc34837d00143d.png!small?1687298590419)

![1687298612_649222346bb8d4a519398.png!small?1687298612546](https://image.3001.net/images/20230621/1687298612_649222346bb8d4a519398.png!small?1687298612546)

![1687298634_6492224a299bb687f84c8.png!small?1687298634132](https://image.3001.net/images/20230621/1687298634_6492224a299bb687f84c8.png!small?1687298634132)

### 4.kibana

  
Kibana中内置了28个仪表盘400多个可视化效果。下面我们看一下系统检测到 Cryptowall Malware报警时在仪表盘中的展现。

![1687298724_649222a42e03dea2903a7.png!small?1687298724150](https://image.3001.net/images/20230621/1687298724_649222a42e03dea2903a7.png!small?1687298724150)

![1687298792_649222e87869b47fa76a7.png!small?1687298793472](https://image.3001.net/images/20230621/1687298792_649222e87869b47fa76a7.png!small?1687298793472)

![1687298823_64922307ac7cb1862792c.png!small?1687298824195](https://image.3001.net/images/20230621/1687298823_64922307ac7cb1862792c.png!small?1687298824195)

### 5\. Arkime

通过读取Elasticsearch 里的所以实现网络通信数据分析的开源工具，可视化方面做的不错，在SELKS中Suricata
Hunting里的报警数据到Kibana展示再到Arkime数据分析可以做相互关联，虽UI不能做到统一，功能上基本满足要求，对于社区版的系统已经很不错了。

![](https://image.3001.net/images/20230621/1687301222_64922c66d4309000e54cf.png!small)

## 六 、总结

本文介绍的这种开箱即用的开源SELKS系统，可以让企业在没有太多资金预算进行 IT
投资的情况下快速部署威胁狩猎平台，但它不能直接告诉你威胁在哪儿，对于分析人员在安全事件分析响应方面的经验要求比较高。SELKS社区版仅能管理一个Suricata探针、一个规则集、缺乏策略管理、Scirius管理界面无法新增或编辑现有规则，没有资产管理的功能等。

另外，在社区版SELKS系统当中由于缺乏HIDS功能，无法对保护的资产进行主机日志数据分析以及文件完整性监控，在UI方面，Suricata
Hunting、evebox、kibina仪表盘、Arkime没做到统一风格。

综上所述，SLEKS社区版可帮助中小企业快速构建威胁狩猎系统，当然每种系统都要先熟悉套路，习惯之后可以再继续深入二次开发，今后大家如有遇到关SELKS应用问题欢迎交流。

  
  

