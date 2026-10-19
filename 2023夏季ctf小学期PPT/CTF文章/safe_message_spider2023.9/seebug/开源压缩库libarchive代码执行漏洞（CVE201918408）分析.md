**作者：启明星辰ADLab  
公众号：<https://mp.weixin.qq.com/s/gG6hslWEyJ3Ez_xpxijPHw>**

## 前言

2019年2月，Check
Point安全研究团队检测发现WinRAR解压缩软件存在若干重大漏洞。攻击者可利用上述漏洞，通过诱使用户使用WinRAR软件打开恶意构造的压缩包文件，执行恶意代码，实现对用户主机入侵的目的。

同样，在不久前谷歌的安全研究员发现libarchive库中存在漏洞CVE-2019-18408。攻击者可利用精心构造的压缩文件，对受影响用户造成压缩程序拒绝服务或执行恶意代码。

## 漏洞危害

libarchive是一个开源的压缩和归档库。它支持实时访问多种压缩文件格式，比如7z、zip、cpio、pax、rar、cab、uuencode等，因此应用十分广泛。

这次被曝出的安全漏洞间接影响到了大量项目和产品。实际上不光是压缩/解压工具可能会采用libarchive，libarchive还应用于台式机和服务器操作系统（各大Linux发行版、MacOS、Windows）、各种包管理器（Pacman、XBPS、NetBSD’s、CMake等）、文件浏览器（Springy、Nautilus，GVFs等）中，甚至某些邮件反病毒软件都会用到它，那么攻击者完全可以利用libarchive的漏洞，发送包含恶意压缩包的邮件，利用漏洞执行任意代码甚至控制设备。

影响版本 libarchive version < 3.4.0

## 漏洞原理

概括：当解压RAR格式的压缩文件失败时，程序会继续寻找下一个文件块的Header并进行解码，而之前解压失败并释放的堆空间被重新使用，造成UAF(Use
After Free)漏洞。 通常RAR归档文件格式如下图所示，第一个必须是标志块，其它块之间没有先后顺序。

![0](https://images.seebug.org/content/images/2019/11/29/1575014657000-0.jpg-w331s)

所以，可分析如下某正常RAR文件构造：![1](https://images.seebug.org/content/images/2019/11/29/1575014657000-1.jpg-w331s)

前7个字节为RAR格式签名（v5版本以下），0x6152为块CRC，0x72为块类型，0x1A21为块标志，0x0007为块大小，由此正确判定为rar文件。

当程序处理第一个文件块Header时，因特殊构造导致解码失败，所以read_data_compressed()函数会返回ARCHIVE_FAILED。之后，在archive_read_format_rar_read_data()函数中，rar->ppmd7_context被释放，即CPpmd7结构体指针变量p。

当*buff不为NULL时，也就是unp_buffer（未解压数据）依然存在时，程序会接着处理rar文件，之后会寻找下一个文件块的Header并循环之前的解码步骤。![2](https://images.seebug.org/content/images/2019/11/29/1575014657000-2.jpg-w331s)

程序在解码下一个文件块的时候再次调用read_data_compressed()函数中的Ppmd7_DecodeSymbol()函数进行解码，再次使用被释放的对象p，因此造成UAF。

## 漏洞修补

libarchive 团队已在Github上提交最新的修复版本，建议受影响用户尽快下载并更新：
<https://github.com/libarchive/libarchive/releases/tag/v3.4.0>

各大Linux发行版安全更新信息如下：

Debian：<https://security-tracker.debian.org/tracker/CVE-2019-18408>

Ubuntu：<https://usn.ubuntu.com/4169-1/>

Gentoo：<https://bugs.gentoo.org/show_bug.cgi?id=CVE-2019-18408>

Arch
Linux：[https://www.archlinux.org/packages/?sort=&q=libarchive&maintainer=&flagged=](https://www.archlinux.org/packages/?sort=&q=libarchive&maintainer=&flagged=
"https://www.archlinux.org/packages/?sort=&q=libarchive&maintainer=&flagged=")

## 补丁分析

在最新版v3.4.0中，释放rar->ppmd7_conext之后，开发者将rar->start_new_table置为1，rar->ppmd_valid置为0，因此Ppmd7_DecodeSymbol()函数在read_data_compressed()中不再调用。
![3](https://images.seebug.org/content/images/2019/11/29/1575014657000-3.jpg-w331s)

在parse_code()函数中，对第二个文件块进行解码，但无法创建新的哈夫曼编码表，因此最终返回-30，其值是ARCHIVE_FATAL的宏定义，而ARCHIVE_FATAL意味着程序不再进行任何操作并进行退出处理。
![4](https://images.seebug.org/content/images/2019/11/29/1575014657000-4.jpg-w331s)

对于rar>ppmd_valid的设置，可以确保在rar_br_bits为0的情况下，类似构造的RAR文件在parse_code阶段始终可以返回ARCHIVE_FATAL。
![](https://images.seebug.org/content/images/2019/11/78afb324-9f5e-40ce-a3e1-36eb5445c372.jpg-w331s)

参考文献：

1.<https://www.zdnet.com/article/libarchive-vulnerability-can-lead-to-code-execution-on-linux-freebsd-netbsd/#ftag=RSSbaffb68/>

2.<https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-18408>

3.<https://github.com/libarchive/libarchive/compare/v3.3.3...v3.4.0>

4.<https://lists.debian.org/debian-lts-announce/2019/10/msg00034.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1086/>

