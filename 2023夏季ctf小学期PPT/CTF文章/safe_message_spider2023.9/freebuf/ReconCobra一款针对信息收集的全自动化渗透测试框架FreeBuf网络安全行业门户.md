##  ReconCobra

**今天给大家介绍的是一款名叫ReconCobra的全自动渗透测试框架，该框架可以帮助安全研究人员在研究的信息收集阶段自动化完成绝大部分的任务。本质上来说，ReconCobra是一款指纹识别与收集框架，该框架目前支持在Kali、Parrot
OS、Black Arch、Termux和Android Led TV平台上运行。**

##  框架接口

软件框架拥有82个不同的操作选项，并且完全自动化实现了功能强大的信息收集能力：

![](https://image.3001.net/images/20200203/1580665974_5e370c76a899c.jpg!small)![](https://image.3001.net/images/20200203/1580665974_5e370c76c67c9.png!small)

##  工具运行

![](https://image.3001.net/images/20200203/1580665990_5e370c86722b8.png!small)![](https://image.3001.net/images/20200203/1580665990_5e370c86862f8.png!small)![](https://image.3001.net/images/20200203/1580665990_5e370c86a3e06.png!small)![](https://image.3001.net/images/20200203/1580665990_5e370c86e822f.png!small)![](https://image.3001.net/images/20200203/1580665990_5e370c86efc31.png!small)![](https://image.3001.net/images/20200203/1580665991_5e370c876511e.png!small)![](https://image.3001.net/images/20200203/1580665991_5e370c879581b.png!small)

###  ReconCobra特性

> 1、ReconCobra对于银行、私人组织和安全研究人员来说非常有价值。
>
> 2、ReconCobra可以被视作是一种防御技术，它可以帮助我们尽可能多地找到有价值的信息，以及未经授权的访问和入侵行为。
>
> 3、随着新技术的出现，网络犯罪分子也找到了更多入侵目标组织体系的方法和途径，ReconCobra便应运而生。
>
>
> 4、ReconCobra可以审计防火墙行为，并寻找内部以及外部网络中的相关软件，如ERP、邮件防火墙和不安全的服务器等等，以便研究人员能够尽可能多地收集目标的指纹、和相关信息，例如用户名、Web技术架构、文件、终端节点和API接口等等。
>
> 5、ReconCobra也是阻止网络犯罪的第一步，它可以有效保护我们的基础设施不会发生信息泄露。除此之外，ReconCobra是无假阳性的。

**工具整合**

ReconCobra的功能实现还整合了Tigerman Root软件包。

##  工具安装

###  Kali安装

广大用户可以使用下列命令在Kali平台下完成工具的安装与构建：

> git clone <https://github.com/haroonawanofficial/ReconCobra.git>
>
> cd Reconcobra
>
> sudo chmod u+x *.sh
>
> ./Kali_Installer.sh

安装完成之后，ReconCobra将以系统软件的形式呈现，依赖组件将会自动完成安装，第三方软件即模块同样会自动安装。

###  Parrot OS安装

广大用户可以使用下列命令在Parrot OS平台下完成工具的安装与构建：

> git clone <https://github.com/haroonawanofficial/ReconCobra.git>
>
> cd Reconcobra
>
> chmod u+x *.sh
>
> Bash ParrotOS_Installer.sh

安装完成之后，ReconCobra将以系统软件的形式呈现，依赖组件将会自动完成安装，第三方软件即模块同样会自动安装。

###  Termux安装

广大用户可以使用下列命令在Termux平台下完成工具的安装与构建：

> git clone <https://github.com/haroonawanofficial/ReconCobra.git>
>
> cd Reconcobra
>
> chmod u+x *.sh
>
> pkg install proot
>
> type: termux-chroot
>
> ./Termux_Installer.sh
>
> ./Termux_fixme.sh

安装完成后，重启Termux，然后运行下列命令：

    
    
    perl ReconCobraTermux.pl

依赖组件将会自动完成安装，第三方软件即模块同样会自动安装。

###  Black Arch安装

广大用户可以使用下列命令在Black Arch平台下完成工具的安装与构建：

> git clone <https://github.com/haroonawanofficial/ReconCobra.git>
>
> cd Reconcobra
>
> chmod u+x *.sh
>
> ./BlackArch_Installer.sh

安装完成之后，ReconCobra将以系统软件的形式呈现，依赖组件将会自动完成安装，第三方软件即模块同样会自动安装。

###  API接口

> 1、针对Python模块，可以从censys.io获取我们的API和密钥-censys.py
>
> 2、针对Python模块，可以从securitytrails.com获取我们的API和密钥-vasl/vasl.py

##  项目地址

> ReconCobra：【[GitHub传送门](https://github.com/haroonawanofficial/ReconCobra)】

##  参考资料

> 1、<https://codeby.net/threads/reconcobra.68782>
>
> 2、<https://www.facebook.com/1470285456587684/posts/reconcobra-ultimate-> recon-software-for-information-gatheringbrief-> introductionre/2351883108427910/>
>
> 3、<https://raidforums.com/Thread-reconcobra-Ultimate-Recon-Software-for-> Information-Gathering>
>
> 4、<https://psdrepo.blogspot.com/2019/08/codebynet_14>
>
> 5、<https://vaultdomain.com/reconcobrathe-ultimate-recon-software-for-> information-gathering-osint/>

 ***
参考来源：[haroonawanofficial](https://github.com/haroonawanofficial/ReconCobra)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

