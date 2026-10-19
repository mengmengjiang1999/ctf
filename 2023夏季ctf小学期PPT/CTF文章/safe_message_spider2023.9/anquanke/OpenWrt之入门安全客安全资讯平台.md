# OpenWrt之入门

阅读量 **495630**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-12 10:00:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01155d17b34b983e69.jpg)

作者： L.A.M@Duncan SecTeam

## 0x00：引言

对于OpenWrt的认知，可能很多人都还停留在路由器或者路由器“刷机”上。在网上搜了一下，这种印象在小米等一众“智能”路由器大卖之后貌似更加深刻了[1]。当然，从OpenWrt官方的描述以及从操作系统的角度来看的话，官方的大白话的确蛮中肯。

“OpenWrt 项目是一个针对嵌入式设备的Linux操作系统。OpenWrt
不是一个单一且不可更改的固件，而是提供了具有软件包管理功能的完全可写的文件系统。这使您可以不使用供应商提供的应用程序选择和配置，而是通过使用软件包来定制设备以适应任何应用程序。对于开发人员来说，OpenWrt
是一个无需围绕它构建完整固件就能开发应用程序的框架; 对于普通用户来说，这意味着拥有了完全定制的能力，能以意想不到的方式使用该设备。”

作为一个技术小白为什么会想到倒腾OpenWrt呢？嗯，当然并不是主要为了搞机器人，而是因为一些光猫上跑了Luci。总觉得这些IoT设备会有为题，其实网上一搜一大堆破解光猫密码啥的，挺有意思，就想自己先搭个环境倒腾一下。前前后后，折腾了有一段时间了，发现挺好玩的，顺带还把计算机体系结构中逃的课都给补上了，毕竟谁还没翘过课呢。。。

还是按照team的老规矩，先把文章的mindmap贴上。

![](https://p5.ssl.qhimg.com/t01b3aff24edd98b4a4.png)

## 0x01：OpenWrt是什么？

其实，一开始没想着写这篇文章的，因为网上OpenWrt的资料还是蛮多的，当然杂且多坑，复制转发的居多。小白很懒，不想去看纯英文的官(方)文(章)，所以动了买本书看看的念头。在叮叮当当上搜了一下，数量不多，就那么两三本，而且基本是站在玩路由的角度写的，对OpenWrt的介绍，尤其是偏向于系统架构和系统安全的介绍基本上可以忽略不计，甚至压根儿没有，但这正是我最想看的，于是打消了偷懒的念头，硬着头皮啃呗。其实，偶尔读一读官文挺好，尤其是晚上睡觉之前，入睡蛮快的。。。因此，这篇文章算是干货满满吧，我把所有填过的坑，踩过的雷都一一罗列出来了，就当为有兴趣一起玩的朋友们铺路了^_^

在我看来，OpenWrt就是一个Linux操作系统，当然是针对低功耗Arm、MIPS等架构的嵌入式计算环境做过详细优化的系统，最重要的是它让针对嵌入式的开发变得愈发简单，用网上的大白话说：OpenWrt之余嵌入式设备，就如Android之余智能手机，不需要为了更新微信而重新安装Android。我觉得这个比喻特别好，对于那些不想深入了解，完了还想到处吹牛逼的人而言，简直就是天上掉下来的福利啊，而且这比喻几乎搁谁都能看懂，当然我爸妈不在此列。所以，下面这段话只能跟技术宅分享了：

“OpenWrt 项目是一个针对嵌入式设备的Linux操作系统。OpenWrt
不是一个单一且不可更改的固件，而是提供了具有软件包管理功能的完全可写的文件系统。这使您可以不使用供应商提供的应用程序选择和配置，而是通过使用软件包来定制设备以适应任何应用程序。对于开发人员来说，OpenWrt
是一个无需围绕它构建完整固件就能开发应用程序的框架; 对于普通用户来说，这意味着拥有了完全定制的能力，能以意想不到的方式使用该设备。”

那么OpenWrt与其他的Linux发行版之间有什么不同呢？停留于应用层面的比较在这里就不说了，说多了都是废话。在技术层面上，二者最大的不同包括但不限于以下几点：

###  1）软件包管理工具。

对于熟悉Linux的朋友而言，rpm，apt，apt-get，dnf，yum，pacman等等都应该比较熟悉，要么都或多或少用过、听过。可是你听过ipkg吗？你又有听说过opkg吗？ipkg是一个轻量化的包管理系统，它被设计用于在掌上电脑等存储能力有限的设备上进行linux的程序安装。现在许多嵌入式linux的手机、pda上常用它作为包管理系统。Opkg则是ipkg的一个变种，专门用于OpenWrt上的软件包管理，目前可以下载的工具大概有3000多个，较之于主流Linux发行版而言，这个数字简直是少得可怜了，但是对于这样一个小圈子而言已经非常腻害了。

###  2）自创的进程间通信机制uBus。

关于uBus的定义，官网是这样说的：

“uBus是OpenWrt的微总线体系架构，用于提供后台进程和应用程序之间的进程间通信，该机制主要包括了后台进程，库文件以及额外的辅助程序(helper)。”

从个人学习体会来看，uBus核心就是进程间通信，弥补Posix机制中传统IPC(信号量，内存共享，套接字等)的不足，同时尽量简化Deamon与App之间通信的成本与时间开销，当然还能够尽可能的统一不同Deamon与App之间的IPC规范，让开发者不用操那么多的心，可以集中精力办大事。其实，很多兼容POSIX接口的系统都实现了自己独有的IPC机制，比如MacOS。

uBus的核心部件包括了：

—— ubusd后台进程。这是整个uBus
IPC架构的核心，为其它Deamon进程提供注册接口，进而从uBus总线上获取消息。在实现上，uBus采用的是Posix套接字和“类型-长度-值”消息类型。如果有感兴趣的童鞋，可以参考官网uBus[2]。

—— Libubus库。为了便于开发者使用uBus IPC机制，OpenWrt提供Libubus库。

—— Command-line uBus
tool。OpenWrt开发了uBus的命令行工具，开发者和用户可以通过命令行与ubusd交互，可以更加直接的与系统底层组件打交道。

![](https://p1.ssl.qhimg.com/t01623dafc2b91b42ed.jpg)

###  3）UCI系统。

UCI是“Unified Configuration
Interface”的缩写，顾名思义，OpenWrt通过UCI为开发者和用户提供了一个统一Deamon进程参数配置接口。其实，UCI可以理解为OpenWrt采用类似面向对象的方法，为配置文件提供了一些列“getter/setter”方法，当然不限于此。个人觉得UCI系统是一个非常“OpenWrt”的东西，简直就是无条件的贯彻了让一切变得简单，让一切变得方便的宗旨。不过，按照UCI规范开发的OpenWrt软件或者插件并不多，目前只有一些核心服务实现了对UCI的兼容，毕竟在能用性之外再附件一层易用性的东西，还是需要码农下田出力的。

![](https://p0.ssl.qhimg.com/t01c7d5b809d225823b.jpg)

## 0x02：基于虚拟化环境安装OpenWrt

我个人安装OpenWrt的动因不是为了刷路由，也不只是倒腾机器人，就是想倒腾OpenWrt，并且尝试着从操作系统和网络安全的角度去了解这个小众的Linux发行版。那么，我在选择安装OpenWrt时，首要考虑的自然就是花最少的时间把它跑起来，至于Arm，Arm64，x86，x86_64还是MIPS这些都不是我关心的。当然，在尝试安装OpenWrt的过程中，还是体验了一下在qemu上跑基于Arm架构的OpenWrt，感受很拧巴，主要还是自己不熟悉qemu。在安装过程中，我实验了Parallels，qemu和VMWare
Workstations/Fusion四种种虚拟化环境，具体安装的情况如下（仅仅是个人安装的总结，所以仅供参考）。

###  1）虚拟机配置：

硬件配置：  
——CPU：1*2  
——内存：1024MB  
——硬盘：8GB  
——网卡：桥接模式(eth0)，仅主机模式(eth1)

OpenWrt版本  
——OpenWrt 19.07.8, r11364-ef56c85848

**a）Windows主机**

![](https://p5.ssl.qhimg.com/t01db750c91bffcce8d.jpg)

**b）MacOS主机（M1，Intel）**

![](https://p2.ssl.qhimg.com/t01ad0b51fc3a36df72.jpg)

###  2）通过虚拟磁盘转化在VMWare Workstations及VMWare Fusion(x86)运行OpenWrt

通过这种方法运行OpenWrt对于绝大多数人来说可能要容易接受一些，而且有虚拟化软件提供的GUI的加持，运行OpenWrt的感受要比qemu好。这种方法是利用qemu提供的qemu-img程序将OpenWrt提供的raw格式的磁盘文件转换为vmdk格式，这样在配置好OpenWrt的虚拟机后指定硬盘为转换后得到的vmdk文件即可。这种方法适用于Windows
PC上的VMWare Workstations以及MacOS（Intel）上的VMWare
Fusion，不得不服VMWare强大的软件开发能力和强悍的兼容性。

接下来，我们将以OpenWrt v19.07.8版本为例（经过实测，也适用于最新的v21版本），首先是进行镜像文件的格式转换：

`qemu-img convert -f raw openwrt.img -O vmdk openwrt.vmdk`

然后，用生成的vmdk磁盘文件作为OpenWrt虚拟机的磁盘文件，直接启动虚拟机就OK了，这应该是Windows上基于VMWare
Workstations运行OpenWrt最简单的方法了吧。

![](https://p3.ssl.qhimg.com/t01d766b0cbd990d95d.jpg)

当然，也适用于MacOS（Intel）上的VMWare Fusion。

![](https://p1.ssl.qhimg.com/t01f5d9117cd3c194d5.jpg)

###  3）在VMWare Workstations，VMWare
Fusion以及Parallels虚拟化环境下，通过Linux的dd命令将镜像文件写入虚拟磁盘来运行OpenWrt

在Linux系统上用dd命令直接写OpenWrt这种方法是在网上找到的，后来在VMWare，Parallels虚拟化环境上都进行了测试，验证成功，确实可行。但是，用起来比前面的方法略显笨拙。不过，对于Parallels虚拟化环境而言，这是目前我验证成功的唯一方法，当然不排除大神们还有别的方法。如果非要在基于x86架构的MacOS上用Parallels跑OpenWrt虚拟机的话，创建磁盘的时候尽量不要启用虚拟磁盘“Trim”选项。

这种方法大致上是这样的：先创建一个Linux虚拟机，CentOS或者Debian什么的都可以，怎么简单、方便就怎么来。然后，创建一个OpenWrt的虚拟机，假设虚拟磁盘还是命名为openwrt.vmdk或者openwrt.hdd。然后，将虚拟磁盘加入到已经创建好的Linux虚拟机中，并启动Linux虚拟机。在验证新的磁盘加载成功后，用下面的命令将下载并解压后的raw格式的openwrt*.img镜像文件写入到新加载的磁盘中。

`#查看磁盘，验证磁盘加载成功`  
`#lsblk`  
`#dd if=openwrt.img of=/dev/sdb`

关闭Linux虚拟机，最好将刚刚添加的磁盘一并移除（但是不要删除），切换到OpenWrt虚拟机，直接开机就OK了。

![](https://p3.ssl.qhimg.com/t01d766b0cbd990d95d.jpg)

![](https://p1.ssl.qhimg.com/t01f5d9117cd3c194d5.jpg)

###  4） 基于qemu运行OpenWrt的initramfs文件系统（RAM镜像文件）

在这种运行模式下，我们通过qemu运行OpenWrt的内存文件系统，而且这个系统是只读的，用户的所有修改操作只能保存在内存中（不会写入硬盘），那么一旦系统重新启动，所有的修改全部丢失。这种模式虽然不能保存修改，但是运行最为简单、方便，做一些简单的实验感受一下OpenWrt还是可以的。通过以下命令可以运行OpenWrt的initramfs系统：

`qemu-system-aarch64 -M virt -m 1024m -kernel
openwrt-21.02.0-armvirt-64-Image-initramfs -no-reboot -nographic -nic user
-nic user -cpu cortex-a53 -smp 4`

###  5） 基于qemu运行OpenWrt并指定可读写文件系统

通过qemu运行OpenWrt时，可以指定运行哪一个内核文件，而且可以指定存储系统对应的文件，比如下面这个命令：

`qemu-system-aarch64 -M virt -m 1024m -kernel openwrt-21.02.0-armvirt-64-Image
-drive file=openwrt-21.02.0-armvirt-64-rootfs-ext4.img,format=raw,if=virtio
-no-reboot -nographic -nic user -nic user -cpu cortex-a53 -smp 4 -append
root=/dev/vda`

###  6）关于Parallels运行OpenWrt

按照前面在VMWare上运行OpenWrt的思路，我分别尝试了转化虚拟磁盘和使用dd命令直接写磁盘。测试的结果是，Parallels无法识别qemu-img转换后的parallels格式虚拟磁盘，但是通过dd命令方式可以将raw格式的镜像文件成功写入parallels虚拟磁盘并且正常运行OpenWrt系统。

后来查阅了qemu官方资料中关于qemu-img的介绍，发现qemu-img当前版本只能读取Parallels虚拟机的虚拟磁盘文件，但是无法创建Parallels虚拟磁盘格式的文件，所以第一种方法最终会失败。

再者，由于OpenWrt不支持Apple M1处理器，也就没有提供针对Apple
M1的镜像文件下载，因此无法在基于M1处理器的MacOS上通过Parallels运行OpenWrt。而且，下载openwrt编译源代码也不行，官方没有提供对M1处理器的支持。

后来，打算尝试直接用Parallels运行armvirt格式的镜像文件（也自己编译过），也都失败了。我仔细看了看OpenWrt官网关于armvirt版本的描述，“virt
is a platform which doesn’t correspond to any real hardware and is designed
for use in virtual machines”，那么跑不起来也在情理之中。刚刚才开始IoT操作系统，对于固件的知识了解不多，若有不当，还望不吝赐教
^_^

## 0x03：OpenWrt配置OpenSSH

OpenWrt自身支持OpenSSH协议，不过采用的是针对嵌入式应用环境的Dropbear版本，与PC和Server端的OpenSSH有些差别。不过，OpenWrt提供了比较多样化的配置方法，用起来还是挺趁手的。

###  1） 基于UCI的OpenWrt配置

通过uci命令可以查看Dropbear的配置文件：

![](https://p5.ssl.qhimg.com/t0138f4a0ab5675ebac.png)

设置dropbear，允许其开启密码验证，并运行root用户登录：

![](https://p4.ssl.qhimg.com/t01803bebf34b1845af.png)

其中，有三点需要注意：

1.通过uci完成dropbear（包括其他后台deamon进程）设置后，需要通过commit提交并保存结果，eg： #uci commit
dropbear。

2.如果配置依然无法生效，可以考虑reload或者restart一下后台进程。

3.如果你使用的是OpenWrt默认密码，即空密码，那么你将无法连接OpenSSH，这是dropbear默认的规则，即“不允许空密码登录”。

![](https://p1.ssl.qhimg.com/t01d4815d9946acefdc.png)

默认情况下，dropbear监听任意地址的22端口，这样我们就可以通过配置的WAN口连接OpenSSH。当然，事先最好查看防火墙配置规则中关于WAN口的规则，通常情况下WAN是拒绝连入请求的。

![](https://p2.ssl.qhimg.com/t0193615b6eac33cd3a.png)

将wan对应的INPUT规则修改为ACCEPT，即允许从wan口访问OpenSSH服务，这样就可以继续愉快的玩dropbear。

###  2） 基于Web界面配置Dropbear

正常情况下，当配置的虚拟网卡正常启用，可以通过LAN网卡对应的网址访问OpenWrt所提供的Web服务，即Luci，那么一切就很简单了，网上教材特别多，我也不好意思继续瞎比比。总的来说，我个人非常喜欢Luci的界面，清晰，简洁，清新，没有那些花里胡哨的东西，让人很愉快。

![](https://p0.ssl.qhimg.com/t012f6ffc8e0d369ed2.png)

点击“System —> Administration”就可以设置root账户密码。

![](https://p4.ssl.qhimg.com/t0159ba87eb6d6d01ce.png)

点击“Network —> Firewall”可以修改防火墙规则，比如添加一个允许从WAN连入22端口。

![](https://p3.ssl.qhimg.com/t0148fd29195e8ad6d6.png)

###  3）最笨但最直接的配置方法——修改配置文件

除了上面两种优雅的办法，还可以直接修改配置文件，虽然显得很简单粗暴，但是好使。OpenWrt中很多的配置文件都存储在/etc/config目录下，比如。。。

![](https://p1.ssl.qhimg.com/t014ccd0673a5bb367d.png)

下面就是dropbear的配置文件，congfig关键字，加上配置文件声明dropbear，每一个配置选项都是用option关键字作为前导，后面便是字段名称和一对单引号括起来的字段值，相比较于那些庞大的PC端的Linux系统而言，这样的配置简直太有爱了
^_^

![](https://p1.ssl.qhimg.com/t01f2cea00e1c0a2a51.png)

下面是防火墙的配置文件：

![](https://p3.ssl.qhimg.com/t01862969cd74128a69.png)

## 0x04、总结

OpenWrt的模拟环境还是比较好搭建的，Windows平台下利用VMWare和qemu都能很容易的搞定，对于新手而言上手也比较容易。有了这个虚拟化的平台，后期就可以进行一系列的研究了，写插件，复现漏洞，DIY一个自己的“Packet
Squirrel”等等。。。

![](https://p2.ssl.qhimg.com/t01e8fb5919697a976c.png)

## 0x05、引用

1、 OpenWrt十年. <https://www.zhidx.com/p/322.html>.  
2、 uBus(OpenWrt Micro Bus Architecture).
<https://openwrt.org/docs/techref/ubus>.

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **邓肯安全小组** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/257719](/post/id/257719)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [IoT](/tag/IoT)
  * [linux](/tag/linux)
  * [OpenWRT](/tag/OpenWRT)
  * [Wi-Fi](/tag/Wi-Fi)

 **+1** __72赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLLFZlMALuORFgmYVcoGv0Sk7X8wsQXkRJgpZkIjRsdBgVoMfUJRWicltOjaic4vW5CfY08KAicYur9g/132)
邓肯安全小组

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

