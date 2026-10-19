**今天给大家介绍的是一款名叫KillerBee的工具，研究人员可以利用该工具对ZigBee及IEEE 802.15.4网络进行安全分析。**

![KillerBee：一款针对IEEE
802.15.4ZigBee的安全研究工具套件](https://image.3001.net/images/20180722/15322253393221.png!small)

## 工具要求

KillerBee目前仅支持Linux系统，之后会添加对macOS的支持。在开发过程中，我们尽量减少了使用的软件依赖，但是该工具的运行仍需要用户安装以下Python模块：

> 1\. serial;
>
> 2\. usb;
>
> 3\. crypto;
>
> 4\. pygtk;
>
> 5\. cairo;
>
> 6\. scapy

在Ubuntu系统中，你可以使用下列命令安装依赖组件：

    
    
    #apt-get install python-gtk2 python-cairo python-usb python-crypto python-serialpython-dev libgcrypt-dev
    # git clone https://github.com/secdev/scapy
    # cd scapy
    #python setup.py install

 **注：**
KillerBee虽然功能强大，但它并不是一个“用户友好”的测试平台，它主要是为开发人员和高级分析专家服务的，所以在使用KillerBee之前我建议大家先了解一下[ZigBee协议](http://bit.ly/2I5ppI)并熟悉一下Python编程语言。

## 工具安装

KillerBee使用了标准的“setup.py”来作为安装文件，你可以使用下列命令安装KillerBee：

    
    
    #python setup.py install

### 工具目录

KillerBee代码的目录结构如下：

>  **doc：** KillerBee代码库的相关HTML文档；
>
>  **firmware：** KillerBee支持的硬件设备固件。
>
>  **killerbee：** Python库源码；
>
>  **sample：** 数据包样本；
>
>  **scripts：** 开发过程中需要使用到的Shell脚本；
>
>  **tools：** 用本框架开发的ZigBee和IEEE 802.15.4 攻击工具；

### 硬件要求

KillerBee目前支持多款设备，其中包括River LoopApiMote、Atmel RZ RAVEN无线电收发器、MoteIVTmote
Sky、TelosB和Sewino嗅探器。

## 框架介绍

KillerBee的主要目的是简化研究人员对数据包的嗅探过程，并帮助研究人员注入任意数据包。KillerBee
API的文档为epydoc格式，并提供了额外的HTML文档。如果你安装了epydoc，你可以生成PDF格式便于打印和发送：

    
    
    $ cd killerbee
    $mkdir pdf
    $epydoc --pdf -o pdf killerbee/

pdf/目录下将会生成一个名叫api.pdf的文件，其中包含了框架的使用文档。

由于KillerBee是一个Python库，它还整合了其他的Python软件。比如说，Sulley库就是一个采用Python开发的模糊测试框架，KillerBee将会使用它来生成和发送恶意格式的ZigBee数据。

## 可用的工具

KillerBee默认提供了多款可用于攻击ZigBee和IEEE
802.15.4网络的工具，每一款工具都有自己的使用命令，你可以使用“-h”参数来了解详情。

> 1\. zbid：识别KillerBee和相关工具的可用接口；
>
> 2\. zbwireshark：跟zbdump类似，但它能够提供一个命名管道来实时捕捉和查看网络数据（Wireshark）；
>
> 3\. zbdump：跟tcpdump类似，用于捕捉libpcap数据包文件；
>
> 4\. zbreplay：用于实现重放攻击；
>
> 5\. zbstumbler：激活ZigBee和IEEE 802.15.4网络发现工具；
>
> 6\. zbconvert：将一个捕捉到的数据包从libpcap转换为Daintree SNA格式；
>
> 7\. zbdsniff：捕捉ZigBee流量；
>
> 8\. zbfind：一个GTK GUI应用，可追踪和定位IEEE 802.15.4发射器；
>
> 9\. zbscapy：提供了一个交互式Scapy Shell接口；

更多可用工具的信息，请参考该项目的【[GitHub主页](https://github.com/riverloopsec/killerbee)】。

 ***
参考来源：[killerbee](https://github.com/riverloopsec/killerbee)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

