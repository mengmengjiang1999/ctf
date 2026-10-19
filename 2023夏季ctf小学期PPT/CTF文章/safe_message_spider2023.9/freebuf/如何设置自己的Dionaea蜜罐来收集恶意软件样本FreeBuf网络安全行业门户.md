## 简介

 **许多安全人员都热衷于恶意软件的逆向工程。在本文中我将教大家设置一个自己的Dionaea蜜罐，来协助我们恶意软件样本的收集工作。**

本文将主要讨论在Amazon Web
Services（AWS）上的蜜罐设置步骤。如果你并不熟悉AWS，则我建议你可以先去对AWS做个基本的了解，这样会更有利于你的理解。需要提醒大家的是，如果你有一个硬盘空间小于50GB的微型实例，你将获取到一个免费的服务器。但你必须提供你的信用卡信息给AWS，只要你保持在免费限额内就可以永久的免费使用它。你也可以启动n个微型实例，但要注意即便这样你也只能获得一个月的小时数。例如你将两个微型实例分开，每个只能分配一半，而且一旦超额就将被收费。这一点大家一定要注意！

## FB百科

Dionaea是一款低交互式蜜罐，是Honeynet Project 的开源项目。Dionaea
蜜罐的设计目的是诱捕恶意攻击，获取恶意攻击会话与恶意代码程序样本。它通过模拟各种常见服务，捕获对服务的攻击数据，记录攻击源和目标
IP、端口、协议类型等信息，以及完整的网络会话过程，自动分析其中可能包含的shellcode及其中的函数调用和下载文件，并获取恶意程序。

##  **所需技能**

> 了解常用的Linux命令
>
> 对网络知识具有一定的理解

## 服务器

服务器（强烈推荐AWS，免费提供w/ CC）

## 免责声明（可选）

一些托管服务提供商并不喜欢恶意软件。因此，他们可能也不会允许你在他们的服务器上收集恶意软件样本。

## AWS设置

现在我们开始设置AWS实例。（如果您未使用AWS，请跳至下一部分）

1.单击EC2并创建新实例（EC2 == AWS Servers）。之后，选择Ubuntu Server 14.04 LTS。

![1e0080242be3ccde8ecd7f7c9497ddf9f0b653c8e_1_689x281.png](https://image.3001.net/images/20180715/15316080875406.png!small)

2.然后，选择微型实例类型。

![2d024f857936745df70cdca0409e3a5d7ef395078_1_690x371.png](https://image.3001.net/images/20180715/15316080988471.png!small)

3.很好，对于Configure Instance Details步骤，选择“Auto-assign Public IP”项，并将其设置为“Enable”。

![3a5296022a67526e77ad86d9d54fe8baf1652f9a2_1_690x387.png](https://image.3001.net/images/20180715/15316081112935.png!small)

4.对于存储配置，只需添加默认值并单击“Next”即可。

5.在添加标签中我们直接单击"Next"。

6.默认情况下，AWS仅开放了SSH端口。因此，我们必须更改此设置，让服务器开放所有端口。虽然这么做很不安全，但这是本文当中的一个重点。

![43a0ab2196c789006f47287498947774ad5db95e6_1_690x385.png](https://image.3001.net/images/20180715/1531608124743.png!small)

7.启动

![576cca5a1f6f2529e4a6ac4b4b651fade3055f7db_1_690x386.png](https://image.3001.net/images/20180715/15316081418114.png!small)

8.这部分可能会有点复杂。通过SSH连接到你的服务器实例，更改私钥（something.pem）的权限，以便ssh可以使用它。从你的实例获取你的主机名。其通常位于Public
DNS (IPv4 )下

![640a901e351ff791fc1eb6e3ee440fe1f4744b383_1_690x317.png](https://image.3001.net/images/20180715/15316081617525.png!small)

在本地输入以下命令，连接AWS服务器

    
    
    $ sudo chmod 400 /home/user/Downloads/key.pem
    $ ssh -i /home/user/Downloads/key.pem ubuntu@ec2-13-57-45-50.us-west-1.compute.amaonaws.com

## 服务器设置

让我们来更新下软件包，命令如下：

    
    
    $ sudo su
    # apt-get update; apt-get upgrade -y; apt-get dist-upgrade;

依赖项安装：

    
    
    # apt-get install git -y
    # git clone https://github.com/DinoTools/dionaea 19
    # apt-get install build-essential cmake check cython3 libcurl4-openssl-dev libemu-dev libev-dev libglib2.0-dev libloudmouth1-dev libnetfilter-queue-dev libnl-3-dev libpcap-dev libssl-dev libtool libudns-dev python3 python3-dev python3-bson python3-yaml ttf-liberation
    # mkdir build
    # cd build
    # cmake -DCMAKE_INSTALL_PREFIX:PATH=/opt/dionaea …
    # make
    # make install
    # cd /opt/dionaea/

好的，现在的位置是配置文件dionaea.cfg所在位置。

该文件用于指定你的恶意软件/二进制文件的位置，以及侦听的接口和端口。你可以保留这些默认值，但请记住，日志文件会变大。
就比如我恶意软件大约1个G但却有19G的日志。

![7e508bcffd303ecc7a237f95e9109cafa82b160d4_1_690x341.png](https://image.3001.net/images/20180715/1531608188562.png!small)

Dionaea有许多不同的服务，可以让你的蜜罐对更多类型的攻击开放。因此，你会收集到更多的恶意软件。我们可以通过services-available和services-enabled目录来切换这些设置。通过编辑各个yaml文件，可以编辑服务以及它对黑客/机器人的显示方式。例如想受到SMB攻击，比如......
WannaCry，则你需要设置你的服务器以接受smb。

    
    
    # vim services-enabled/smb.yaml

如果要启用默认的Windows 7设置，只需取消Win7注释符即可。其它的也一样，我就不多说了！

![85811c1a5532fa9e072a62a46c3d34c2dba3999ab_1_690x387.png](https://image.3001.net/images/20180715/15316082169867.png!small)

最后，我们来运行我们的蜜罐。

    
    
    # /opt/dionaea/bin/dionaea -D

##
![9c6d743e1a449250b729fceacde58522e583ec58d_1_690x266.png](https://image.3001.net/images/20180715/15316082386943.png!small)

## 总结

说实话，第一次设置并运行dionaea着实花了我不少的时间。而第二次尝试我仅用了16分钟。如果在此过程中，你遇到了一些自己没法解决的问题，请尝试翻阅他们的官方文档（<https://dionaea.readthedocs.io/en/latest/run.html>），或在相关的技术论坛提问以寻求解决方案。

 ** *参考来源：[0x00sec](https://0x00sec.org/t/run-the-trap-how-to-setup-your-own-honeypot-to-collect-malware-samples/7445)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

