## 一、背景

腾讯主机安全（云镜）捕获一个新的挖矿木马LoggerMiner，该木马在云上主机中攻击传播，会利用当前主机上的ssh账号信息对其他主机发起攻击，以控制更多系统。并且，LoggerMiner​还会尝试对当前主机上的docker容器进行感染。

该木马代码中大量使用了logger字符串作为系统账号名、文件路径、通信域名等，腾讯安全团队据此将其命名为“LoggerMiner”挖矿木马。该木马存在多个模块具备以下恶意行为：

利用ssh爆破感染其他云主机、修改ssh配置，关闭安全设置，留置后门，方便攻击者远程登录；向docker容器发送恶意命令，进行感染；木马的部分攻击代码尚未完工。

木马还会尝试卸载云服务器安全软件、结束竞品挖矿木马进程、停止系统日志、修改系统安全设置，删除其他竞品挖矿木马创建的帐户、添加自己的新帐号，安装定时任务实现持久化等功能。

## 二、详细分析

首先解释一下为什么起名LoggerMiner，原因是该木马的代码中大量使用了logger字符串作为系统账号名、文件路径、通信域名等。

LoggerMiner挖矿木马感染主机后会通过cron定时任务实现持久化，从定时任务里可以看到，LoggerMiner挖矿木马会执行3个恶意脚本，我们把这3个脚本定义为3个模块：xanthe、xesa、fczyo，然后逐个分析。

![](https://image.3001.net/images/20201117/1605579362_5fb332628832865055655.png!small)

首先看下xanthe模块，该模块有14个函数，大体功能如下：

![](https://image.3001.net/images/20201117/1605579562_5fb3332af3beaa5d735ce.png!small)

具体函数执行步骤如下：

initializego

filegetgo

filesetupgo

#filerungo

sshdconfig

resetsshgo

# scancheck

# scango

#stopscan

localgo

  

总结起来，xanthe模块大体执行流程如下：

> xanthe模块首先会检查感染标识文件/tmp/.firstrun-> update_ivan1.pid是否存在，如果不存在则进行感染，下载并执行xesa和fczyo模块；
>
> 尝试下载挖矿程序java_c、进程隐藏模块so、以及配置文件config.json并启动java_c挖矿程序；
>
> 尝试重新挂载/var/tmp、/tmp目录；
>
> 修改ssh配置文件，启用22和33768端口进行连接，允许root账号通过密码登录，允许密钥登录，关闭GSSAPI 认证等；
>
> 重启ssh服务；
>
>
> 尝试搜索当前主机的known_hosts、bash_history等配置文件，从里面获取用户名、主机地址、ssh密码/密钥信息，然后利用ssh执行感染模块xanthe。

部分功能代码片段如下：

  1. 感染判断：

![](https://image.3001.net/images/20201117/1605579584_5fb33340f1d8b11594125.png!small)

  2. 利用当前主机上保存的ssh账号信息尝试感染其他机器：

![](https://image.3001.net/images/20201117/1605579596_5fb3334c133718c84404f.png!small)

除了以上功能外，该模块代码里有几个函数正在编写中，在此并未启用，从代码上看，该代码功能如下：

> 尝试搜索当前主机上的known_hosts文件，利用里面保存的ssh登录信息尝试登录并执行恶意代码；
>
> 安装masscan后，尝试扫描当前主机上开启2375端口的docker容器，然后利用命令行向容器内部发送恶意命令，实现docker容器感染；
>
> 还会尝试下载zgrab扫描器，下载后并未有其他动作，应该是代码没有完成。

相关代码片段如下：

利用当前主机上保存的ssh账号信息进行横向感染：

![](https://image.3001.net/images/20201117/1605579650_5fb333829ae1cfce8fdd2.png!small)

利用masscan扫描docker容器，并尝试感染docker容器：

![](https://image.3001.net/images/20201117/1605579661_5fb3338df3725eb7f0ccc.png!small)

下载zgrab扫描器

![](https://image.3001.net/images/20201117/1605579672_5fb33398b0554a8e95126.png!small)

接下来分析xesa模块，该模块的8个函数功能大致如下：

![](https://image.3001.net/images/20201117/1605579683_5fb333a380f3771dbf779.png!small)

从以上函数功能可以看出，xesa模块主要负责安全对抗，大致功能总结如下：

> 卸载阿里云等安全监控服务
>
> 停止系统常用的日志监控服务syslog等
>
> 结束其他挖矿木马进程
>
> 修改系统安全设置等

部分功能代码片段如下：

![](https://image.3001.net/images/20201117/1605579712_5fb333c0b110c3ab56c69.png!small)![](https://image.3001.net/images/20201117/1605579722_5fb333ca809d4d00e33f5.png!small)

最后我们分析下fczyo模块，该模块函数功能大致如下：

![](https://image.3001.net/images/20201117/1605579734_5fb333d61e3c78c5e55e3.png!small)

从上面函数功能可以看到，该模块功能主要集中在持久化安装方面，大致功能如下：

> 通过cron安装定时任务，实现恶意代码执行；
>
> 通过/etc/rc.d/rc.local 实现开机自启动，实现恶意代码执行；
>
> 修改防火墙策略；
>
> 修改ssh配置文件，添加ssh密钥，实现免密码登录：

/opt/autoupdater/.ssh/authorized_keys

/opt/system/.ssh/authorized_keys

/opt/logger/.ssh/authorized_keys

添加后门账号，删除其他挖矿木马的后门账号：

> 添加的账号列表：sysall、system、logger、autoupdater
>
> 删除的账号列表：darmok、cokkokotre1、akay、o、phishl00t、opsecx12

部分功能代码片段如下：

修改防火墙配置

![](https://image.3001.net/images/20201117/1605579746_5fb333e252e5093c46d34.png!small)

ssh配置文件修改

![](https://image.3001.net/images/20201117/1605579759_5fb333ef83cbc95c70311.png!small)

系统账号添加及修改

![](https://image.3001.net/images/20201117/1605579771_5fb333fb0194f71aef10b.png!small)![](https://image.3001.net/images/20201117/1605579781_5fb3340569bcf20d54a83.png!small)

## IOCs

 **URL**

> http://34.92.166.158:8080/files/xanthe
>
> http://34.92.166.158:8080/files/fczyo
>
> http://34.92.166.158:8080/files/xesa.txt
>
> http://34.92.166.158:8080/files/java_c
>
> http://34.92.166.158:8080/files/config.json
>
> http://34.92.166.158:8080/files/libprocesshider.so
>
> http://139.162.124.27:8080/files/xanthe
>
> http://139.162.124.27:8080/files/fczyo
>
> http://139.162.124.27:8080/files/xesa.txt
>
> http://139.162.124.27:8080/files/java_c
>
> http://139.162.124.27:8080/files/config.json
>
> http://139.162.124.27:8080/files/libprocesshider.so
>
> https://iplogger.org/11sxm
>
> https://iplogger.org/17Cph7

 **Domain**

> iplogger.org

 **IP**

> 34.92.166.158
>
> 139.162.124.27

 **MD5**

> 776227b07b2f1b82ffcc3aa38c3fae09
>
> 70b3ad8f1ce58203c18b322b1d00dd9a
>
> 7309b0f891a0487b4762d67fe44be94a
>
> 7633912d6e1b62292189b756e895cdae
>
> 025685efeb19a7ad403f15126e7ffb5a
>
> 83acf5a32d84330bbb0103f2169e10bb

 **钱包地址**

>
> 47TmDBB14HuY7xw55RqU27EfYyzfQGp6qKmfg6f445eihemFMn3xPhs8e1qM726pVj6XKtyQ1zqC24kqtv8fXkPZ7bvgSPU
>
>
> 47E4c2oGb92V2pzMZAivmNT2MJXVBj4TCJHad4QFs2KRjFhQ44Q81DPAjPCVc1KwoKQEp1YHdRMjGLUe6YdHPx5WEvAha1u

 **ssh密钥**

>
> AAAAB3NzaC1yc2EAAAADAQABAAABAQDLVZNrAJ1uzR7d2bm1iUQPAgjuBlyLQQNaEHVmACWtGwwiOKMPiFBfBjuNJIyZFnGkkFgJP5fi8v1eqliaBgqERUDDtW/RZDDIz8DovDrA4/MGlxpCHLeViN+F62W/jgeufiQ7NiPTlPB3Fuh7E7QXXpXqQ6EmVlV0iWdzqRvSiDIB3cIL6E2CrK47pY6Rp6rY2YKYzUhiZRqAMHViMR+2MARL2jERfF3CsG6ZXo/7UVVx+tqoKQDHPmz21mrulOF6RW5hh04dE2q1+/w6xmX8AxUSGmPdpwQa8GuV7NHHZmYO26ndTVi2ES472tJdkXVHmLX8B9Un42JLNVXwPU/H
> linux@linux.com

