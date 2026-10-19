**之所以把这个蜜罐平台的搭建教程写出来，是因为关于这个平台全网教程实在少之又少，几乎都是相互转载摘抄，甚至还带来了些许误导。**

此处绝无诋毁大佬的意思，只是T-Pot于11月份更新到了18.11版本，基于ubuntu18.0
LTS，相对于之前的版本不管是系统环境还是平台习惯都有了不少变化，所以旧版本的教程难免有些不适用了，然而新版本的教程目测还没有流传开。

于是，在这个青黄不接的时间点，这篇文章就诞生了。关于此项目的动机呢，咳咳，最近公司要打通内网，想想分公司那帮家伙，这场战斗已经避免不了了，所以……

T-Pot
18.11整合了如下主流蜜罐的docker环境adbhoney,ciscoasa,conpot,cowrie,dionaea,elasticpot,glastopf,  
glutton,heralding,honeytrap,mailoney,medpot,rdpy,snare,tanner  
并借助统一的web页面，实现对多个docker的统一管理与数据整合。实乃居家旅行，杀*越货，必备佳品。  
盗取一张官方的宣传图，实时统计各项攻击行为，清晰的各种报表统计，准确定位攻击源IP与真实地理位置，看到这里的你还能忍得住么？上车~  

##
![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489577_5c2d8ee990d70.png!small)T-Pot主界面

关于蜜罐的基础概念，大家自行百度，今天我们来简单看一下18.11 T-Pot的安装与使用。

> GitHub项目地址：  
> _<https://github.com/dtag-dev-sec/tpotce>  
> _ GitHub镜像地址：  
> [_https://github.com/dtag-dev-sec/tpotce/releases_](https://github.com/dtag-> dev-sec/tpotce/releases)

之前接触过T-Pot的话应该知道，上个版本是基于ubuntu16.0的17.10版本，如果你尝试它的安装，会收到各种“not
found”的回复，没错，他已经被完全抛弃了。这个团队将发布日期作为版本号，正如此次的18.11发布日期为2018年11月。  

![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489599_5c2d8eff05ac4.png!small)17.10

## 安装篇

关于T-Pot的安装，官方提供了三种安装方式（说实话是两种）。

### 一、使用官方提供的镜像进行安装

![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489624_5c2d8f18428c6.png!small)ISO

就是这个59MB的.iso文件，显然这是最偷懒的一种安装方式，边下载边安装，这就需要我们的网络环境足够稳定。然后考虑到源问题，安装所使用的网络需要使用代理，大家自行解决。  
其次，如果你一定要尝试这种使用方式的话，我建议你使用手动方式一步步安装，别去用它那个一键自动安装，哪里错了你都看不到，而且一出错就需要重头再来。因为这两天公司在做设备调整，网络质量不是太好，我安了七八遍吧，都失败了。233333333

### 二、使用官方提供的ISO Creator创建镜像，然后安装

官方的出发点是力求透明，可谓是诚意满满，显然这样做还有一个优点，这使得我们可以更方便的根据自己的地区所在地修改安装配置文件以调整源位置，这样根据个人需求定制的镜像安装也会变得快速。

> 官方参考的创建ISO镜像的环境要求如下：
>
> Ubuntu 18.04 LTS或更新作为主机系统（其他可能工作，但仍未经测试）  
> 4GB的可用内存  
> 32GB的免费存储空间  
> 有效的互联网连接
    
    
    git clone https://github.com/dtag-dev-sec/tpotce
    cd tpotce
    sudo ./makeiso.sh
    

操作完成之后，在当前目录下你会得到一个tpot.iso文件，接下来的安装同上个方法。

### 三、使用安装文件自行安装至现有环境

较上述两种方法，此方法目测是最复杂的，但是中间的操作步骤也更清晰，对于各种报错也方便我们处理，安利一下，当然、这也是我最终选择的安装方式。  
首先，自行准备Ubuntu Server 18.04 LTS。（瞥了一眼自己的傻parrot，有空尝试一下）  
全新的ubuntu的话，大家自行调整下源，附个阿里云给大家，只是个人习惯。

    
    
    sudo vim /etc/apt/sources.list
    :%d
    

> deb [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic main restricted universe multiverse  
> deb [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-security main restricted universe multiverse  
> deb [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-updates main restricted universe multiverse  
> deb [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-proposed main restricted universe multiverse  
> deb [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-backports main restricted universe multiverse  
> deb-src
> [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic main restricted universe multiverse  
> deb-src
> [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-security main restricted universe multiverse  
> deb-src
> [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-updates main restricted universe multiverse  
> deb-src
> [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-proposed main restricted universe multiverse  
> deb-src
> [_http://mirrors.aliyun.com/ubuntu/_](http://mirrors.aliyun.com/ubuntu/)
> bionic-backports main restricted universe multiverse
    
    
    sudo apt-get update
    sudo apt install git
    

顺手安装git，等下用到。  
17.10和16.10用到的T-Pot-Autoinstaller在当前版本已经被取代了，直接包含在了T-Pot的Installer中，官方给出的安装方式如下。

    
    
    git clone https://github.com/dtag-dev-sec/tpotce
    cd tpotce/iso/installer/
    ./install.sh --type=user
    

如果想解放双手，可将最后一步替换为`./install.sh --type=auto
--conf=tpot.conf`,tpot.conf.dist文件的位于Installer目录下，通过`cp tpot.conf.dist
tpot.conf`生成下配置文件就好啦。  
然后，关于网上缺失的安装流程给大家简单截图说明下。  

![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489639_5c2d8f274f3d1.png!small)端口确认

在这一步的时候我们根据需求选择适合自己的版本，如果学习使用，就默认STANDARD标准安装吧，这一块介绍的话文字太多，详情大家自行参见官方说明吧。  

![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489660_5c2d8f3c02e4f.png!small)版本选择

参照向导设置控制台的账号密码。  

![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489685_5c2d8f55b9e75.png!small)账号密码

好评，居然还对密码安全等级进行了确认。  

![T-Pot18.11的安装与使用](https://image.3001.net/images/20190103/1546489697_5c2d8f61b0a76.png!small)安全性确认

当来到这一步的时候，T-Pot的安装正式开始：

![T-Pot安装](https://image.3001.net/images/20190103/1546489708_5c2d8f6c17f75.png!small)T-Pot安装

接下来的这一幕不得不吐槽下，即使开着代理，但是下载速度却极慢。而且该界面没有进度条，让人一度以为它卡j2了！小伙伴们沉住气~  

![Cloning](https://image.3001.net/images/20190103/1546489715_5c2d8f73db448.png!small)Cloning

该文件夹2266个项目，90.6MB大小，在此告知下，方便大家了解当前下载进度。【没有进度条!!!】【没有进度条!!!】【没有进度条!!!】  

![tpot文件详情](https://image.3001.net/images/20190103/1546489731_5c2d8f8396e17.png!small)tpot文件详情

然后会进入docker的安装与部属，当然，蜜罐也已经被预装在了docker中，又到了拼网速的时间，dockers下载位置为GitHub，怎么处理，你懂的。如果碰到网络波动，稳住，他会自动如下图retrying，耐心坚持下~  

![docker](https://image.3001.net/images/20190103/1546489744_5c2d8f90c52af.png!small)docker

docker安装完成后，系统重启，本次安装完成~  

![安装完成](https://image.3001.net/images/20190103/1546489762_5c2d8fa23bb7b.png!small)安装完成

## 使用篇

关于这个系统的使用，显然作为一个蜜罐系统，它的常见端口均为入侵者开放，布置了各种伪造的服务，对应各个docker的内容。

> web管理界面：https://[IP]:64297

emmm，这配色，，，姨妈粉？  
让小伙伴帮忙nmap扫了一下，我们可以实时看到入侵者的攻击类型与攻击方式，因为是内网，所以没出现地理定位。![主界面](https://image.3001.net/images/20190103/1546489784_5c2d8fb8e0dd6.png!small)

主界面

我们可以看到实时的攻击分析，与攻击者的IP，结果可以表格导出，用于数据整合与分析。  

![追踪IP](https://image.3001.net/images/20190103/1546489812_5c2d8fd4c6b58.png!small)追踪IP

更多功能牵扯具体蜜罐，我们在接下来的蜜罐教程中具体讲解。

> 服务器管理界面：https://[IP]:64294

这配色！真的舒服！

![服务器管理](https://image.3001.net/images/20190103/1546489834_5c2d8fea03bcf.png!small)服务器管理

实时的系统各项硬件指标，方便及时的觉察各项异常。  

![系统运行情况](https://image.3001.net/images/20190103/1546489853_5c2d8ffd58ad1.png!small)系统运行情况

通过UI管理docker，及时查看docker运行状态，并可根据需要启停。如图中为80端口对应web网站（是个wordpressblog）蜜罐。![docker管理](https://image.3001.net/images/20190103/1546489878_5c2d9016a3706.png!small)

docker管理

ssh？不需要的~这界面、经典的配色。![命令行界面](https://image.3001.net/images/20190103/1546489931_5c2d904bdf607.png!small)

BASH界面

用过旧版本T-Pot的小伙伴现在是什么感受？18.11将服务器相关的管理统归到了一个页面下，web管理界面只负责攻击行为分析，各司其职，新版本T-Pot真的舒服！

那么，最后，祝大家新年快乐~

 ***本文作者：rabbitmask，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

