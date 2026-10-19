# KCon议题解析 | 美团安全分享APT检测设备的扩展研究

阅读量 **540901**

|评论 **6**

发布时间 : 2019-08-27 11:29:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01a27a703b214b0ec3.jpg)

8月23日-25日，一年一度的KCon
黑客大会在北京昆泰嘉瑞文化中心成功举办，本届大会以「无界」为主题，通过汇聚全球黑客的智慧，探索技术的无穷奥秘，突破边界外的边界，创造不可能的可能。

作为安全领域内拥有丰富实战经验和技术积累的安全团队，美团安全研究院成员受邀参加KCon黑客大会，并针对目前主流厂商在移动平台（iOS、Android）的APT检测设备明显不足的现状，分享了关于「APT检测设备的扩展研究」的议题。

现场议题围绕业界现状分析、C相关设备的动态沙箱（蜜罐）技术等几个方面，充分展示美团安全团队对APT检测设备的扩展研究成果。

![](https://p5.ssl.qhimg.com/t01d0aca04204038cf8.jpg)

![](https://p1.ssl.qhimg.com/t0104950c4989af0873.jpg)

![](https://p4.ssl.qhimg.com/t01b640208edc20b162.jpg)

## 议题解读「APT检测设备的扩展研究」

演讲者 | JU ZHU

目前就职于美团（高级安全研究员），有着9+年的安全研究经验，其中7+年主要从事高级威胁的研究，包括0Day、nDay
和漏洞挖掘。他一直致力于使用自动化系统来 Hunt 野外的高级威胁，曾多次获得 CVE，且受到 Google、Apple、Facebook
等厂商的致谢，也多次作为 Speaker 受邀参加 BlackHat、CodeBlue、CSS 等国内外的顶级安全会议。

## 1\. 现状分析

###  1.1 业界主流APT检测设备选型对比

APT检测设备的选择一般是参考Gartner报告挑出备选，再结合实际情况做适应性检测对比。

平台支持性：

我们统计了某天内网接入设备的操作系统类型（见图1），并根据这些类型对三个备选厂商进行了平台相关性检测（见图2）。

图1 内网接入设备的操作系统类型统计

|

Windows

|

MacOS

|

iOS

|

Android

|

其它  
  
---|---|---|---|---|---  
  
厂商1

|

✔

|

✘

|

✘

|

✘

|

✘  
  
厂商2

|

✔

|

✘

|

✘

|

✘

|

✘  
  
厂商3

|

✔

|

✘

|

✘

|

✔

|

✘  
  
图2 各厂商的平台支持对比

从图1和图2可以看出，大部分厂商只是对Windows平台的支持比较好，或者也提供Android沙箱。然而这和内网接入设备的多元化还有很大差距，需要我们自己进行进一步的扩展开发。

文件类型支持性：

有些厂商对于平台的支持可能受到某些限制，所以他们通过更多的文件类型支持来进行能力补充（见图3）。

|

PE

|

Office

|

PDF

|

Mach-O

|

plist

|

APK  
  
---|---|---|---|---|---|---  
  
厂商1

|

✔

|

✔

|

✔

|

✘

|

✘

|

✘  
  
厂商2

|

✔

|

✔

|

✘

|

✘

|

✘

|

✘  
  
厂商3

|

✔

|

✔

|

✘

|

✔

|

✘

|

✔  
  
图3 各厂商的文件类型支持对比

在选型测试中，我们特地增加了plist文件格式的样本，这源于之前发现的在野的iOS Ransomware（Death
Profile[[1]](/Users/xuting16/Desktop/SRC/Kcon/%E7%BE%8E%E5%9B%A2%E5%AE%89%E5%85%A8Kcon%E9%BB%91%E5%AE%A2%E5%A4%A7%E4%BC%9A-20190826%E7%BB%88%E7%89%88.docx#_ftn1)）。它是一种基于iOS的Configuration
Profile，常用于企业为办公设备推送各类配置信息（如Wi-Fi、VPN设置等），是一种常见的公司内部交换文件格式。

从图3看，各厂商几乎覆盖了基于Windows平台的文件格式（诸如PE、Office等），只有少量厂商支持基于MacOS/iOS平台的Mach-O文件（经过实测，他们基本上采用的是静态分析方式），而plist格式目前并未有厂商支持。因此对于文件格式的支持性，还有很大的空间可提升。

###  1.2 可参考的解决方案对比

对于甲方来说，APT检测的解决方案一般以采购为主，但也不乏根据实际情况进行部分自研。我们选取了一些可参考的（除Windows外）动态沙箱技术解决方案来进行对比（见图4）。

|

MacOS

|

iOS

|

Android  
  
---|---|---|---  
  
可参考的动态沙箱

|

Darling

或

Cuckoo Sandbox

|

Corellium

|

Anbox

或

Cuckoo Droid  
  
使用方式（云或本地）

|

本地

|

云

|

本地  
  
开源？

|

是

|

否

|

是  
  
实现成本

|

中

|

极高

|

中  
  
图4 可参考的动态沙箱技术解决方案对比

MacOS：

Darling是一种比较轻量级的基于Linux的MacOS
App运行环境，主要是做了一个转换层，将App的函数调用重定向到了Linux。Darling可以运行在Docker上，方便大规模部署和维护。Cuckoo
Sandbox是比较重量级的，它运行在MacOS上，一般采用VisualBox来部署，性能会差些。

因此可以采用阶梯式部署方式：Darling完成大部分指标检测，而剩下的少部分，则由Cuckoo Sandbox来完成（如图5）。

图5 MacOS动态沙箱技术解决方案

iOS：

Corellium拥有一套比较完整的iOS虚拟机，不过目前他们只提供云服务，对于内网审计是个很大的挑战。对于很多甲方公司来说，内网的数据是不能外传的，所以我们更倾向于使用本地沙箱方式。

Android：

Anbox是一个轻量级完整模拟Android的系统， Cuckoo Droid是一个比较成熟的检测Android
Malware的沙箱系统，且它们都是开源的，比较符合甲方的需求，不需要再做拓展研究。

综上所述，大部分可参考的动态沙箱技术解决方案，基本都可实现本地部署，且开源方便二次开发。唯有iOS动态沙箱需要重新设计和开发。

## 2\. iOS动态沙箱（蜜罐）技术

###  2.1总体架构流程

为了能检测出未知Malware（0 Day等），同时又能知晓影响面（版本、位数等），我们首先需要提取iOS App中的Mach-O文件，再根据32位或者64位来进行相应的检测。

图6 针对Mach-O的流程

如图6所示，首先解开IPA文件，再分解Fat文件为32位Mach-O和64位Mach-O。由于基于Aarch 64的硬件服务器架构不能直接运行Arm
32位的程序，我们进行了分流设计：将32位的Mach-O送入模拟Arm v7的Qemu，而64位的Mach-O则送入基于Aarch 64的Docker。

另外，存在像Death Profile这样的攻击，我们还需要检测流量中plist格式的文件或者内容（如图7）。

图7 针对plist的流程

###  2.2 轻量级虚拟化设计

Corellium的虚拟化方案虽然非常完备，但对于我们的需求来说过重，且开发成本极高。因此我们更倾向于类似Darling（或者Wine）的轻量级解决方案。

我们采用API重定向的方式，将Mach-O完整地在Qemu（或者Docker）中模拟运行起来。

Loader & Run Mach-O  
  
---  
  
Foundation

|

。。。  
  
libobjc.so

|

libxml2.so

|

libdispatch.so

|

。。。  
  
libc.so

|

libc++abi.so

|

libc++.so

|

。。。  
  
Qemu（Arm v7）

|

Docker（Aarch 64）  
  
Linux（Aarch 64）  
  
Hardware（Aarch 64）  
  
图8 轻量级的虚拟化设计

图8是我们提出的轻量级虚拟化设计，最底层硬件和操作系统都是基于Aarch 64（或者Arm v8），在它们上面使用Qemu以实现Arm
v7的支持。而Docker用于直接对Arm 64的支持。

在Qemu（或者Docker）内，我们部署安装了一些基础库（诸如libc、libc++等），还编译了libobjc、libdispatch等开源库，以对更上层的API重定向库提供支持。

最后，我们实现了类似Foundation.framework的API重定向库，以支撑Mach-O的正常运行，运行效果见图9、图10。

图9 Qemu（Arm v7）的运行效果

图10 Docker（Arm 64）的运行效果

###  2.3实现

正常来说，我们运行一个Mach-O文件，需要实现一个类似dyld的Loader程序，来用于解析和加载Mach-O，并导入相关的依赖库。这里我们需要自己实现这个过程。

整个实现过程分为六个部分：解析和加载、导入相关依赖库、地址修正、地址（API）重定向、运行、回调。

![](https://p3.ssl.qhimg.com/t01d76e155ca365dafe.jpg)

图11 整个运行过程

图12 运行效果

解析和加载：

我们通过解析Mach-O文件中Load
Commands的Segment信息，将所有的Segment数据（除PageZero）按地址顺序逐一加载到虚拟内存。由于程序启动时会在进程空间加上一段偏移量（slide），我们需要计算记录下slide的结果，用于之后运行时的起始地址计算（如图13）。

slide = text_real_vm_addr – text_vm_addr

其中text_real_vm_addr是TEXT段的实际虚拟内存地址，text_vm_addr是Mach-O文件中TEXT段的VM地址。

另外，在映射时，可按实际VM Protection值来设置所映射的虚拟内存VMP属性。

slide + text_vm_addr

|  
  
---|---  
  
|  
  
|

TEXT

|

DATA

|

LLVM

|

LINKEDIT

|

。。。  
  
Loader & Run  
  
图13 所有Segment数据（除PageZero）映射到虚拟内存的实际地址分布情况

导入相关依赖库：

通过解析Mach-O文件中Load Commands的LC_LOAD_DYLIB数据，可获取所有依赖库的信息，并做模拟实现。这样就可以将Mach-O中的API调用重定向到我们希望调用的函数中去。

事实上，在实现某个依赖库（比如Foundation）时，可能会存在更多的依赖库需要实现，其工作量将是巨大的（如图14）。

图14 Foundation的实现

地址修正：

如果要正常运行main函数，Mach-O文件中Rebase所描述地址的数据还需要做修正，如Lazy Symbol
Pointer数据和CFString数据等。

|

原数据（Pointer）

|

|

新数据（Pointer）  
  
---|---|---|---  
  
Lazy Symbol Pointer

|

0x100007F9C

|

->

|

slide + 0x100007F9C  
  
CFString

|

0x100007FA8

|

->

|

slide + 0x100007FA8  
  
图15 Mach-O文件中Rebase所描述地址的数据修正

地址（API）重定向：

对于Lazy Symbol Pointer这类数据，我们还需要再做一次修正，那就是使用我们模拟实现的函数地址来替换该数据（Pointer）。

|

原地址

|

|

新地址  
  
---|---|---|---  
  
NSLog

|

slide + 0x100007F9C

|

->

|

NSLog@libFoundation.so  
  
图16 地址（API）重定向

图17 API重定向流程

运行：

如果我们希望运行某个函数，只需要找到它的入口地址，即可直接运行。比如main函数，我们通过解析Mach-O文件中Load
Commands的LC_MAIN数据，从而获得它的相对入口地址，再加上之前我们获得的slide和text_vm_addr，就可以算出它的绝对（真实）入口地址。

图18 算出main函数的绝对（真实）入口地址，并直接运行它

回调

Delegate是iOS开发常用的设计模式，所以我们也需要实现相应的回调。我们通过解析Mach-O文件中ObjC2
Class的数据，来获得Delegate类。然后，再解析它（比如AppDelegate）的Protocol数据，来获得Framework里对应的类（比如UIKit的UIApplication）最后，再解析它的Method数据，并注册到NSNotificationCenter。

图19 回调流程

图20 运行效果

2.4部署

最初研究或小批量试验，可以使用一些厂商的云服务，或者采用低成本的树莓派集群。而我们为了更好的匹配重新设计的动态沙箱（蜜罐）系统，采用了公司现有的ODM（Original
Design Manufacturer）专用Aarch 64服务器。

图21 自研服务器

### 团队介绍

美团安全部的大多数核心人员，拥有多年互联网以及安全领域实践经验，很多同学参与过大型互联网公司的安全体系建设，其中也不乏全球化安全运营人才，具备百万级IDC规模攻防对抗的经验。安全部也不乏CVE“挖掘圣手”，有受邀在Black
Hat等国际顶级会议发言的讲者，当然还有很多漂亮的运营妹子。

目前，美团安全部涉及的技术包括渗透测试、Web防护、二进制安全、内核安全、分布式开发、大数据分析、安全算法等等，同时还有全球合规与隐私保护等策略制定。我们正在建设一套百万级IDC规模、数十万终端接入的移动办公网络自适应安全体系，这套体系构建于零信任架构之上，横跨多种云基础设施，包括网络层、虚拟化/容器层、Server
软件层（内核态/用户态）、语言虚拟机层（JVM/JS
V8）、Web应用层、数据访问层等，并能够基于“大数据+机器学习”技术构建全自动的安全事件感知系统，努力打造成业界最前沿的内置式安全架构和纵深防御体系。

随着美团的高速发展，业务复杂度不断提升，安全部门面临更多的机遇和挑战。我们希望将更多代表业界最佳实践的安全项目落地，同时为更多的安全从业者提供一个广阔的发展平台，并提供更多在安全新兴领域不断探索的机会。

### 招聘

美团安全2019年招聘火热进行中~

如果你想加入我们，欢迎简历请发至邮箱zhaoyan17@meituan.com。

[具体职位信息，可点击“这里”进行查看。](http://mp.weixin.qq.com/s?__biz=MzI5MDc4MTM3Mg==&mid=2247483981&idx=1&sn=773534f644dfb9bbe4c010bbd8d3347f&chksm=ec1be39edb6c6a88b1be288dc2240e902a0d93779e5cdb0522be66f6c5184a8d38071edad7f6&scene=21#wechat_redirect)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **美团安全应急响应中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/185101](/post/id/185101)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [APT](/tag/APT)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t011de8b7028cee15f8.png) 美团安全应急响应中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

