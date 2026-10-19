## 0x00 前言

**作为一个学生党，在今年的早些时候入手了Proxmark3rdv4，一下子花了不少还是有点小心疼，先上Freebuf来看了下相关的资料发现还是有点少，尤其是关于环境配置方面，虽然官方的wiki里写的也算是比较详细，但是毕竟不是人人英语基础都那么好的，而且再看这些技术文档的时候很多情况下翻译软件可能并不好用，于是萌新照着自己踩过的坑来写一篇教程，由于没有经验是第一次写相关教程，如果有不到位的地方希望大佬们指正，也希望有大佬可以带带我orz。**

好了我们话不多说，先来看一下经过了大半个月的快递才到我手上的PM3，我是在hackerwarehouse上买的，同时买了PM3，蓝牙拓展模块等，加上价格不菲的运费，差不多花了有500刀左右。

![](https://image.3001.net/images/20191114/1573675571_5dcc6233b0b36.jpg!small)

![](https://image.3001.net/images/20191114/1573675572_5dcc6234d3547.jpg!small)

![](https://image.3001.net/images/20191114/1573675573_5dcc6235325f6.jpg!small)

## 0x01 背景介绍

作为一个白帽子（或者安全研究人员）还是比较喜欢用kali的，一开始尝试在ubuntu上配置环境，但是好像问题有点多，而且很多没解决，遂放弃转而到kali上来配置环境。首先我们访问一下官方wiki，地址<https://github.com/Proxmark/proxmark3/wiki>。

在首页上就可以看到Getting
Started，其中给了我们各种不同的系统下的配置方式，我们来看kali的。开头便说到了kali的系统版本在2016.2上运行验证过，那现在可能没人会用2016的kali了吧，来看一下我的，kali是2019.3

![](https://image.3001.net/images/20191114/1573675599_5dcc624fccfb3.png!small)

那么接下来就可以愉快地进行下一步了。

![](https://image.3001.net/images/20191114/1573675614_5dcc625ecadd3.png!small)

官方给的步骤不多，看似也比较简单，首先是准备PM3的软件，然后插上PM3，更新启动加载器，更新固件，然后就能用了！

## 0x02 准备相关软件

首先第一步准备软件。

执行以下命令来安装PM3环境所需相关依赖

    
    
    sudo apt install gitbuild-essential libreadline5 libreadline-dev gcc-arm-none-eabi libusb-0.1-4libusb-dev libqt4-dev ncurses-dev perl pkg-config libpcsclite-dev pcscd

在我的系统版本里好像一共要下载1900多M，不过也挺快的（如果你已经用了国内源的话，没有用国内源的请移步百度）

然后再git clone下来以后开始编译，成功后如图所示：

![](https://image.3001.net/images/20191114/1573675624_5dcc6268c61b1.png!small)

如果之前的依赖都装上了那就不会有问题了，中间顶多报几个Warning，可能你还没看清就滚下去了。如果因为系统版本不同请百度相关依赖无法安装的问题或者将系统更新到2019.3

## 0x03 插上PM3

之后将PM3连接到kali中，我的就是这样的，连到了虚拟机，希望不要出什么岔子，我可不希望几千块买的东西变砖

![](https://image.3001.net/images/20191114/1573675679_5dcc629f0f0e2.png!small)

我是通过虚拟机连接的，不过问题不大，物理机直接插拔就好。继续跟着教程走，输入 dmesg | grep -i usb

我的出现了一大串……

![](https://image.3001.net/images/20191114/1573675695_5dcc62afae388.png!small)

根据提到的关键字检索后发现如下

![](https://image.3001.net/images/20191114/1573675707_5dcc62bb7d6d0.png!small)

此时根据教程提示我们跳到固件更新

![](https://image.3001.net/images/20191114/1573675715_5dcc62c381c3d.png!small)

## 0x04 CDCbootloader更新

如果和我不一样的，那就需要先更新CDC启动器（因为以下步骤我没做过所以没有截图了）

> 第一步：通过cd 进入client目录
>
> 第二步：输入make执行编译
>
> 第三步：编译成功后输入./flasher /dev/ttyACM0 -b
> ../bootrom/obj/bootrom.elf，来刷bootrom，其中ttyACM0要根据实际情况选择，也就是上一步执行dmesg命令的回显。
>
> 第四步：输入cd ..来返回上一级目录

## 0x05 固件更新

如果以上步骤执行完了，就可以开始更新固件了

通过以下命令进行固件升级操作

![](https://image.3001.net/images/20191114/1573675728_5dcc62d0af5da.png!small)

这个过程还是很快的，不过终端好像会卡住，我是等我pm3上的灯只剩电源灯了就Ctrl+C结束了这一步（在执行这一步之前的状态是电源灯和四个操作灯全亮，不过最好多等待一会儿，毕竟官方文档里说强制结束可能你的PM3会崩）

## 0x06使用

这时候我们来执行命令看看PM3是否正常了，确保你的终端在pm3目录下，然后通过cd 进入client目录，执行./proxmark3
/dev/ttyACM0

![](https://image.3001.net/images/20191114/1573675791_5dcc630f19d2d.png!small)

惊了，居然报错了，那问题是什么呢，报的是不正确的端口，通过之前的dmesg | grep -i
usb命令再来看一下，原来端口变了...以前在windows上玩盗版PM3也遇到过，插拔以后COM号会加1

![](https://image.3001.net/images/20191114/1573675816_5dcc6328c087d.png!small)

那让我们重新输一次命令OK了！！！！！

![](https://image.3001.net/images/20191114/1573675829_5dcc633538611.png!small)

完美！！！

我们看看随便放张卡能不能读

![](https://image.3001.net/images/20191114/1573675842_5dcc6342c023f.png!small)

读卡也成功读到了，kali Linux下入门环境搭建教程就到这边，后续会根据实际情况写一些其他的教程。

 ***本文作者：YaphetSzz，转载请注明来自FreeBuf.COM**

