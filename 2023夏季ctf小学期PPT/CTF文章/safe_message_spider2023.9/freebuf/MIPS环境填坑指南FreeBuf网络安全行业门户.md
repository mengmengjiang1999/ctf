  

原创 萌新 合天智汇

0x00前言：

今年来IoT安全火热，2019年公众号发了一篇《QEMU搭建树莓派环境》，算是给研究ARM平台下的漏洞分析、漏洞挖掘以及熟悉ARM指令等打下了基础。

合天网安实验室也开设了相关实验课程：

《ARM汇编教程》、《ARM漏洞利用技术》

ARM在移动平台，或者说物联网领域独领风骚，不过在路由器领域基本还是以MIPS为主，本文的目的就是搭建在软件层面分析路由器安全（MIPS架构下）的环境。

本文所述工具、搭建方法在2020年2月24日可以完全复现，在ubuntu16.04下展开，如果对mips架构、路由器固件安全有兴趣的师傅们可以尝试自己动手搭建这套环境，方便后续的深入分析。

至于本文为什么要取这个标题，是因为网上很多环境搭建的资料太久了，或者有很多坑那些作者没有告诉你，自己填上了，留下读者一脸懵逼。本文在搭建过程中会说明存在哪些坑以及填坑的方法，作者以人格担保，看完这篇文章，要是复现不出环境，小编的命就交给你们了。

0x01安装binwalk

直接使用apt-get install binwalk就可以了

不过这样子安装的binwalk面对如squashfs的识别提取可能无效，会报错（以kali内置的binwalk来解析某路由器固件为例）

![v2-1a8d9691d9c650fb1119fee6bacfffc1_720w](https://pic3.zhimg.com/80/v2-1a8d9691d9c650fb1119fee6bacfffc1_720w.jpg)

这时候我们需要安装sasquatch

输入这三条命令就可以了

sudo apt-get install zlib1g-dev liblzma-dev liblzo2-dev sudo git clone
https://github.com/devttys0/sasquatch cd sasquatch && sudo make && sudo make
install

由于我ubuntu的已经安装过了，所以这三条命令就不截图说明了，直接看看对于同样的文件，安准了sqsuatch后，binwalk是否能够识别解压

![v2-4fabe3c5adb3d2019929b7bbff83dd6f_720w](https://pic3.zhimg.com/80/v2-4fabe3c5adb3d2019929b7bbff83dd6f_720w.jpg)

可以看到此时是可以识别并提取的，固件的文件系统就在原路径下方生成的以extracterd结尾的文件夹。

0x02安装buildroot

注意这里安装的时候会提示缺少各种库文件，所以在正式安装buildroot前，我们先把相关的库文件装上

sudo apt-get install curses-devel sudo apt-get install libncurs* sudo apt-get
update

然后下载

git clone https://github.com/buildroot/buildroot.git

进行编译的配置

cd buildroot make clean make menuconfig

输入上面这条命令后会出现buildroot的编译配置界面

![v2-23dc6acaf9e04ee73a8aaa9449d406f8_720w](https://pic4.zhimg.com/80/v2-23dc6acaf9e04ee73a8aaa9449d406f8_720w.jpg)

这里有三个地方需要我们设置

![v2-c90f9ba3ad936f41beea4a2b4deeea4a_720w](https://pic4.zhimg.com/80/v2-c90f9ba3ad936f41beea4a2b4deeea4a_720w.jpg)

target option中设置，第一个是设置大端还是小端，由于本文是准备两个都安装（原因后面会说明），所以这里随意选择一个，第二个设置成generic
mips32即可

然后是toolchain

![v2-9c6865eadb8e71e6497ea17f51c98c82_720w](https://pic3.zhimg.com/80/v2-9c6865eadb8e71e6497ea17f51c98c82_720w.jpg)

这里的linux headers根据自己的内核进行选择

查看内核使用uname –r即可

![v2-15be13d1152d4a03932967969db155f9_720w](https://pic2.zhimg.com/80/v2-15be13d1152d4a03932967969db155f9_720w.jpg)

设置完成后，输入make就可以开始自动编译了

这里大概要等30分钟到1个小时，根据我的观察，主要的时间是浪费在联网下载部分组件上（我已经安装过了，无法截图，等自己动手安装的时候就知道什么意思了）

针对这种情况，可以考虑在make期间直接ctrl+c终止掉，然后再继续make。

注：一般而言make情况下是不应该终止的，或者终止后需要make
clean再make，不过这里的情况比较特殊，make任务是卡在下载组件上，而在此之前，一些编译的任务已经结束了，所以用我这种做法是安全的。

以小端为例，安装完成后在相关路径下会出现一些跨平台交叉编译的工具：

![v2-876a445b5eafe844db959ff83ff20b10_720w](https://pic3.zhimg.com/80/v2-876a445b5eafe844db959ff83ff20b10_720w.jpg)

注意到这些名字都是mipsel开头，表示的是小端

这时候尝试编译的话，由于工具都在该路径下，我们在其他路径下编译很不方便，所以需要设置环境变量

打开/etc/profile在最后如图格式添加即可

![v2-5509436eca5fa8fd6848fbf30db989fb_720w](https://pic1.zhimg.com/80/v2-5509436eca5fa8fd6848fbf30db989fb_720w.jpg)

添加完后source ~/etc/profile立即生效

也可以重启后生效

查看环境变量

![v2-cb4eed532596fca41406ba88654be7d6_720w](https://pic1.zhimg.com/80/v2-cb4eed532596fca41406ba88654be7d6_720w.jpg)

接下来写一个c源程序测试下

![v2-76026d26c00500ca6a8a914fe10a3734_720w](https://pic1.zhimg.com/80/v2-76026d26c00500ca6a8a914fe10a3734_720w.jpg)

编译后使用file查看

![v2-84d887dc3f4ea4e5fb85db8d062445ba_720w](https://pic2.zhimg.com/80/v2-84d887dc3f4ea4e5fb85db8d062445ba_720w.jpg)

![v2-1ee75a50dfa3131751c84efa896a7537_720w](https://pic2.zhimg.com/80/v2-1ee75a50dfa3131751c84efa896a7537_720w.jpg)

确实是小端

那么大端怎么编译呢？

在stackoverflow上大佬提出的解决方案是加上-EB参数

不过尝试后会报错

![v2-211a8f4b1077b601f1527c304015d4ab_720w](https://pic4.zhimg.com/80/v2-211a8f4b1077b601f1527c304015d4ab_720w.jpg)

根据H4lo师傅的解决方案是编译、链接两步走

![v2-774c472c0d557f398dc6a2fda2b2cffd_720w](https://pic1.zhimg.com/80/v2-774c472c0d557f398dc6a2fda2b2cffd_720w.jpg)

不过依然会报错，原因未知，所以我的解决方案是再建一个文件夹，另外编译一个大端的，方法同上，我这里已经编译好，同时环境变量也设置好了，接下里尝试使用大端的编译

![v2-558b7c7b64978342d1ef516ef0d84f62_720w](https://pic3.zhimg.com/80/v2-558b7c7b64978342d1ef516ef0d84f62_720w.jpg)

可以看到是大端的。

那么我们就顺利完成了MIPS交叉编译环境的安装和测试。

0x03安装QEMU

在之前发布的文章中已经介绍了QEMU的安装方法，这里就简单给出命令，不放安装的图片了。

sudo apt-get install qemu sudo apt-get install qemu-user-static sudo apt-get
install qemu-system

安装网络配置工具

apt-get install bridge-utils uml-utilities

修改ubuntu网卡配置文件如图所示

![v2-9d8cbb35b5a7181fe99549b9ff190d09_720w](https://pic3.zhimg.com/80/v2-9d8cbb35b5a7181fe99549b9ff190d09_720w.jpg)

修改qemu网卡启动文件，如图所示

![v2-721bfc4dbb02f85900e3b77925b1b743_720w](https://pic3.zhimg.com/80/v2-721bfc4dbb02f85900e3b77925b1b743_720w.jpg)

在ubuntu上关闭ens33，启动br0

sudo ifdown eth0

sudo ifup br0

到这一步之前都是通用的，接下里的步骤根据你要搭的环境而有所不同

下载对应的内核文件和磁盘镜像，我这里以

debian_squeeze_mips_standard.qcow2

vmlinux-2.6.32-5-4kc-malta

为例

使用这条命令启动

sudo qemu-system-mips -M malta -kernel vmlinux-2.6.32-5-4kc-malta -hda
debian_squeeze_mips_standard.qcow2 -append "root=/dev/sda1 console=tty0" -net
nic,macaddr=00:16:3e:00:00:01 -net tap

![v2-14d3c5c3ffa256ec9ed9d896015cc87d_720w](https://pic2.zhimg.com/80/v2-14d3c5c3ffa256ec9ed9d896015cc87d_720w.jpg)

可以看到qemu正在启动

![v2-1d977a478d5bb00feb7bc9be7f58c33c_720w](https://pic4.zhimg.com/80/v2-1d977a478d5bb00feb7bc9be7f58c33c_720w.jpg)

输入root/root

![v2-33f67e07f6bc19ce256457ae90b31135_720w](https://pic1.zhimg.com/80/v2-33f67e07f6bc19ce256457ae90b31135_720w.jpg)

输入ifconfig注意到ip为192.168.1.107，网卡对应的为eth1

注意，如果你在操作的时候没有这一步，可以到配置文件中设置

![v2-4d91ff727e81943fe82451578976deef_720w](https://pic1.zhimg.com/80/v2-4d91ff727e81943fe82451578976deef_720w.jpg)

将红色的地方改为eth1即可

回到shell后输入ifup eth1即可

这时候网就通了，我们接下来可以在ubuntu上ssh过去操作

![v2-75da808cc4d9c013a4f86b0ce74ba6c9_720w](https://pic3.zhimg.com/80/v2-75da808cc4d9c013a4f86b0ce74ba6c9_720w.jpg)

至此，qemu的环境也搭好了

需要注意，qemu有两种运行模式，分别是use mode,和system mode，

前面的方式属于system mode.此时qemu模拟的是整个计算机系统，包括cpu及其他周边设备。

根据目的的不同，有时候可以使用user mode。这时qemu能启动那些为不同cpu编译的linux程序

以前面编译出的小端hello为例

先将小端格式的qemu-mipsel复制到当前目录下

![v2-a0ed1592c07e849ccb60daebb982b550_720w](https://pic1.zhimg.com/80/v2-a0ed1592c07e849ccb60daebb982b550_720w.jpg)

然后传参运行

![v2-76a0360f6de***49eef4a6d1ee5419ed_720w](https://pic3.zhimg.com/80/v2-76a0360f6de***49eef4a6d1ee5419ed_720w.jpg)

这里还有个细节需要注意

如果程序依赖动态链接库的话，如上执行是会报错的，我们重新编译hello看看是什么情况

![v2-4dead1921cc9cffab64fefb1d863a3f4_720w](https://pic4.zhimg.com/80/v2-4dead1921cc9cffab64fefb1d863a3f4_720w.jpg)

注意这里编译时我没加上-static

此时运行会报错

这是正确的做法是：使用chroot定义根目录，以便运行前加载相应的lib库文件

如下所示

![v2-34b285bcf02d1723dcc37e20696c9e81_720w](https://pic3.zhimg.com/80/v2-34b285bcf02d1723dcc37e20696c9e81_720w.jpg)

这里因为用到了qemu-mipsel-static，所以需要另外安装

apt-get install qemu binfmt-support qemu-user-static

Unicorn Engine基础教程一：

<http://www.hetianlab.com/expc.do?ec=ECIDac22-afdb-4162-a8c8-134e08735f8a>

（以模拟x86 32位和mips架构为例,学习unicorn engine简单的使用）

0x04安装wine

很简单，apt-get wine即可

0x05安装IDAPro

新建一个文件夹，把ida下的文件全部拷贝过来

![v2-b1b590268e42fb567f2eda25895f8771_720w](https://pic2.zhimg.com/80/v2-b1b590268e42fb567f2eda25895f8771_720w.jpg)

尝试运行会报错

![v2-9535c120cd09958ea943c92e996d006c_720w](https://pic3.zhimg.com/80/v2-9535c120cd09958ea943c92e996d006c_720w.jpg)

以下命令安装即可

curl -O https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi wine
msiexec /i python-2.7.15.msi

我们再去这里下载mips分析可能用到的插件

git clone https://github.com/devttys0/ida

把下载的ida/plugins目录下所有后缀为:,py“d的文件复制到IDA pro插件目录：

sudo cp –r `find /home/yale/a/ida/plugins –iname *.py`
/home/yale/ida/ida/plugins/

将scrpit复制到idapro根目录下

sudo mkdir /home/yale/ida/ida/plugins/scripts sudo cp –r ida/scripts
/opt/ida61/scripts/

再次执行，可以看到ida可以正常启动，这里以之前编译出来的小端mips程序hello为例

![v2-a57d6105b80175ee53c486285d200c27_720w](https://pic3.zhimg.com/80/v2-a57d6105b80175ee53c486285d200c27_720w.jpg)

而且下载插件都可以正常用了,以mipsrop为例

![v2-d77bc05e135e5d77d6263d95b4a6187d_720w](https://pic3.zhimg.com/80/v2-d77bc05e135e5d77d6263d95b4a6187d_720w.jpg)

![v2-190ea4218fe16c56c9149aa2b8b0db09_720w](https://pic4.zhimg.com/80/v2-190ea4218fe16c56c9149aa2b8b0db09_720w.jpg)

不过每次跑到ida根目录下执行wine idaq比较麻烦，这里我们可以考虑写个shell脚本

如下所示

![v2-6371348802de054944be86164faf9fd9_720w](https://pic4.zhimg.com/80/v2-6371348802de054944be86164faf9fd9_720w.jpg)

接下来要启动ida的话我们只用使用

sh ida.sh即可

0x06配置gdb

一条命令就可以了

sudo apt install gdb-multiarch

看看效果是怎样的，以调试stack_bof_01为例

开两个终端：

一个终端用于gdb调试，-multiartch是为了支持其他架构用的，比如我们这里的mips架构，另一终端执行被调试程序

![v2-a8d6cb1515c6cb3b152b724d837cc7d7_720w](https://pic4.zhimg.com/80/v2-a8d6cb1515c6cb3b152b724d837cc7d7_720w.jpg)

设置架构为mips

![v2-17b8fa805b683f1324ce3c59f46ad0f8_720w](https://pic2.zhimg.com/80/v2-17b8fa805b683f1324ce3c59f46ad0f8_720w.jpg)

设置ip和端口

![v2-5214f360f783711ad882a6fe816e4acd_720w](https://pic1.zhimg.com/80/v2-5214f360f783711ad882a6fe816e4acd_720w.jpg)

按c继续执行，可以看到程序异常终止了，同时在另一个终端这儿也打印出了try again

![v2-66ee6073021b9da9546d734a46b8a39b_720w](https://pic3.zhimg.com/80/v2-66ee6073021b9da9546d734a46b8a39b_720w.jpg)

0x07安装firmadyne(替代方案：attifyos)

Firmadyne是一款自动化分析嵌入式Linux系统安全的开源软件，由卡内基梅隆大学的Daming D.
Chen开发完成的。它支持批量检测，整个系统包括固件的爬取、root文件系统的提取、QEMU模拟执行以及漏洞的挖掘。

搭建起来比较繁琐，外文原文在这：<https://blog.attify.com/getting-started-with-firmware-emulation/>

或者可以直接看知道创宇seebug收录的这篇译文https://paper.seebug.org/639/

我搭建起来后最后会碰到一个问题：

![v2-4077474c55573a16952b2ddb17dbb385_720w](https://pic2.zhimg.com/80/v2-4077474c55573a16952b2ddb17dbb385_720w.jpg)

提示没有网卡的信息，这个问题我在官方的github项目地址上看到有人已经在问了，下面也有很多人讨论

![v2-fdbeed4e24aa65df6b41ae4b0f3ada23_720w](https://pic1.zhimg.com/80/v2-fdbeed4e24aa65df6b41ae4b0f3ada23_720w.jpg)

不过一直没有解决方案，开发者也没有出来回应。

所以我这里给出了替代方案：使用attifyos

官方介绍说，配置IoT渗透测试所需的各种工具，当然其中已经配置好firmadyne了

项目地址在这里：

<https://github.com/adi0x90/attifyos>

它基于ubuntu14.02开发，下载过来后是一个ova镜像，直接导入vmware就可以用，这里的安装没有什么难度，这里直接给出在attifyos上模拟运行dlink300的情况

输入fat.py启动

![v2-ee97cd676612a686caf3be50db87e80f_720w](https://pic3.zhimg.com/80/v2-ee97cd676612a686caf3be50db87e80f_720w.jpg)

下图红色的地方都是需要填写的

![v2-2dbba881dd9ea7a09f2eecb71e5da5f0_720w](https://pic2.zhimg.com/80/v2-2dbba881dd9ea7a09f2eecb71e5da5f0_720w.jpg)

环境准备好后可以看到ip信息

![v2-fba4028585500c1501f49c1c66b27aed_720w](https://pic2.zhimg.com/80/v2-fba4028585500c1501f49c1c66b27aed_720w.jpg)

在浏览器中输入相应的ip

![v2-9866682a7ce3d1ea3814a9de37f355c1_720w](https://pic4.zhimg.com/80/v2-9866682a7ce3d1ea3814a9de37f355c1_720w.jpg)

就成功模拟出这个环境了

0xxx后记

读者需注意，并不是所有的mips分析人物都需要用到上述的全部工具，本文只是尽量把难搭的、常用的工具介绍出来并以具体的例子给出使用方法。另外还有两款工具分别是JEB,Ghidra下载来就能直接用了，文中也不再赘述。建议读者结合自身实际情况进行参考。

初识Ghidra

<http://www.hetianlab.com/expc.do?ec=ECIDdded-c215-40bd-b479-7f7cbb25e5a1>

点击链接做实验（Ghidra能运行在Windows，Mac
OS和Linux上，支持多种处理器指令集，功能包括反汇编、汇编、反编译、图像界面和脚本，以及数百个功能，还可以根据API开发自己的Ghidra插件或脚本。）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关

