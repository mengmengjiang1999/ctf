Claroty及JFrog研究人员11月9日发表研究结果表示，其在嵌入式Linux应用程序BusyBox中发现了14个漏洞，可导致拒绝服务（DoS）、数据泄露、及远程代码执行（RCE）。BusyBox在很多OT及IoT设备中使用，包括PLC、HMI、及RTU。

## 一、背景介绍

BusyBox是一款软件套件，包含许多有用的Unix实用程序（Applet），这些实用程序打包为单个可执行文件。内存和存储资源有限的嵌入式设备可能会利用BusyBox工具。

BusyBox中包含一个完整的Shell、一个DHCP客户端/服务器、和一些小型实用程序，例如cp、ls、grep等。许多OT和IoT设备都使用BusyBox，包括可编程逻辑控制器(PLC)、人机界面(HMI)和远程终端单元(RTU)，其中许多在Linux上运行。

作为致力于提高开源软件安全性的一部分，Claroty的Team82和JFrog研究人员合作开展了一个检查BusyBox的漏洞研究项目。研究人员使用静态和动态技术发现了影响最新版本BusyBox的14个漏洞。BusyBox在8月19日发布的1.34.0版本中私下披露并修复了所有漏洞。

在大多数情况下，这些漏洞会导致是拒绝服务(DoS)，在极少数情况下，也可能导致信息泄漏和远程代码执行（RCE）。

## 二、漏洞概述

![](https://image.3001.net/images/20211110/1636531529_618b7d49597d9d35f4efb.jpg!small)

## 三、漏洞触发条件

由于受影响的程序不是daemons，因此只有向易受攻击的小程序提供不受信任的数据时，通常通过命令行参数，漏洞才能被利用。具体而言，以下是触发每个漏洞必须发生的条件：

 **CVE-2021-42373**
。如果攻击者可以控制传递给man的所有参数，则可触发。man由默认的BusyBox配置构建，但未随Ubuntu的默认BusyBox二进制文件一起提供。

 **CVE-2021-42374。**
如果攻击者可以提供精心制作的压缩文件，该文件将使用unlzma进行解压缩，则可触发。即使unlzma小程序不可用，但启用了CONFIG_FEATURE_SEAMLESS_LZMA（默认启用），其他小程序如tar、unzip、rpm、dpkg、lzma和man在处理带有.lzma文件名后缀的文件时也可以访问易受攻击的代码。unlzma是由默认的BusyBox配置构建的，并随Ubuntu的默认BusyBox二进制文件一起提供。

 **CVE-2021-42375**
。如果攻击者可以向ash提供包含特殊字符$、{、}或#的命令行，则可触发。ash由默认的BusyBox配置构建，并随Ubuntu的默认BusyBox二进制文件一起提供。

 **CVE-2021-42376。**
如果攻击者可以向hush提供包含特殊字符\x03（分隔符）的命令行，则可触发。hush是由默认的BusyBox配置构建的，但不随Ubuntu的默认BusyBox二进制文件一起提供。

 **CVE-2021-42377。** 如果攻击者可以向hush提供包含特殊字符&的命令行，则可触发。

 **CVE-2021-42378及CVE-2021-42386。**
如果攻击者可以向awk提供任意模式，该模式是此小程序采用的第一个位置参数，则可触发。awk由默认的BusyBox配置构建，并随Ubuntu的默认BusyBox二进制文件一起提供。

## 四、研究方法

研究人员使用了静态和动态分析方法来研究BusyBox。首先，以自上而下的方式对BusyBox源代码进行人工审查，遵循用户输入直到特定的小程序处理。研究人员还查找了明显的逻辑/内存损坏漏洞。

另一个方法是模糊测试。研究人员用ASan编译了BusyBox，并为每个BusyBox小程序实现了一个AFL工具。随后通过删除不必要的代码部分、在同一进程（持久模式）上运行多个模糊测试循环以及并行运行多个模糊测试实例，对每个线束进行了优化。

研究人员从模糊测试所有daemons小程序开始，包括HTTP、Telnet、DNS、DHCP、NTP等。为了有效地模糊基于网络的输入，需要进行许多代码更改。例如，研究人员执行的主要修改是用来自STDIN的输入替换所有recv函数，以支持模糊输入。对非服务器小程序进行模糊测试时也进行了类似的更改。

研究人员为每个小程序准备了几个示例，并在几天内运行了数百个经过模糊测试的BusyBox实例，因此得到了数万次可供研究的异常结果（crash）。研究人员根据崩溃的根本原因进行了分类，以减少样本中的崩溃数量。随后研究人员将每个分类最小化至只有唯一的崩溃输入，以方便处理。

为了完成这些任务，研究人员开发了自动工具，来消化所有崩溃数据，并根据崩溃分析报告进行分类，主要包括相关代码区域的崩溃堆栈跟踪、寄存器和汇编代码。例如，研究人员合并了具有类似崩溃堆栈跟踪的案例，因为其通常具有相同的问题根本原因。

最后，研究人员研究了每个单独的崩溃并最小化其输入向量，以了解根本原因，并创建一个利用导致崩溃的漏洞PoC。此外，研究人员针对多个BusyBox版本测试了PoC，以了解漏洞是何时引入源代码的。

总而言之，研究中采取的步骤包括：代码审查、模糊测试、减少和最小化、分类、PoC、测试多个版本、披露。

## 五、威胁分析

为了评估这些漏洞造成的威胁级别，研究人员检查了JFrog的数据库，其中包含10,000多个嵌入式固件映像，仅包含公开可用的固件，不包括上传到JFrog的Artifactory映像。研究人员发现其中40%包含一个BusyBox可执行文件，该文件与其中一个受影响的小程序相关联，这使得这些问题在基于Linux的嵌入式固件中极为普遍。

然而研究人员认为，这些问题目前不会构成严重的安全威胁，因为：

  * 虽然DoS漏洞很容易被利用，但小程序几乎总是作为单独的分叉进程运行，这通常可以减轻影响；
  * 信息泄漏漏洞很难被利用；
  * Use-After-Free漏洞可用于远程代码执行，但目前没有尝试为其创建武器化漏洞。此外，从外部输入处理awk模式是非常罕见的，并且本质上是不安全的。

## 六、CVE-2021-42374 LZMA越界读取漏洞

其中最危险的漏洞CVE-2021-42374是LZMA越界读取漏洞，可能导致DoS和信息泄漏，该漏洞只能在精心制作的LZMA压缩输入被解压缩时用于攻击设备。

该漏洞是由于函数decompress_unlzma.c中的大小检查不足引起的。LZMA是一种使用字典压缩的压缩算法，并使用范围编码器对其输出进行编码，需要满足两个特定的编码条件才能利用该漏洞，buffer_pos
= 0和rep0 = offset + dict_size。

利用此漏洞通常需要准备一个特制的LZMA编码流，以便在解码时，两个条件都将被满足，并且pos将等于负数-offset。最终，解压后的流将包含泄漏的内存，这些内存将被写入输出流。

为了达到越界条件，需要写入一些字节，然后使用匹配将缓冲区填充到header.dict_size，并将rep0更改为所需的值。因此，pos将等于-offset并且可以从offset泄漏字节作为对缓冲区指针的引用。

尽管该漏洞是在LZMA解压算法中发现的，但是许多小程序支持LZMA压缩，并且默认情况下会尝试解压编码的LZMA流，例如无处不在的ZIP格式支持将LZMA压缩作为Type14压缩。因此从攻击者的角度来看，ZIP是一个更好的攻击媒介。

## 七、修复及解决方法

BusyBox
1.34.0版本已修复所有14个漏洞，用户可从https://busybox.net/downloads/busybox-1.34.0.tar.bz2下载并尽快升级。

由于特定版本兼容性需要，如果无法升级BusyBox，则可以在没有易受攻击的功能（Applets）的情况下编译BusyBox 1.33.1和更早版本。

在BusyBox的源目录中运行make deconfig后，或者重新使用以前的配置，可按照以下方式编辑.config文件：

  * man注释掉CONFIG_MAN=y；
  * lzma注释掉CONFIG_UNLZMA=y、CONFIG_FEATURE_SEAMLESS_LZMA=y、及CONFIG_FEATURE_UNZIP_LZMA=y；
  * ash注释掉CONFIG_ASH=y；
  * hush注释掉CONFIG_HUSH=y；
  * awk注释掉CONFIG_AWK=y。

  

 **参考资源：**

【1】https://claroty.com/2021/11/09/blog-research-unboxing-busybox-14-vulnerabilities-uncovered-by-claroty-jfrog/

【2】https://jfrog.com/blog/unboxing-busybox-14-new-vulnerabilities-uncovered-by-claroty-and-jfrog/

【3】https://threatpost.com/busybox-security-bugs-linux-devices/176098/

