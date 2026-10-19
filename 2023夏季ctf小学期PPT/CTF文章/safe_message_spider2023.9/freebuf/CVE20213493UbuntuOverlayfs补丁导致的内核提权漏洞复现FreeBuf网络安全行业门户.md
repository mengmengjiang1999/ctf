## 0x00 简介

OverlayFS是一个面向Linux的文件系统服务，是一种类似aufs的一种堆叠文件系统，它依赖并建立在其它的文件系统上（如ext4fs和xfs等），并不直接参与磁盘空间结构的划分，仅仅将原来底层文件系统中不同的目录进行合并，然后向用户呈现，因此对于用户来说，它所见到的overlay文件系统根目录下的内容就来自挂载时所指定的不同目录的合集。

![image-20210701021013305](https://image.3001.net/images/20210713/1626143673_60ecfbb94ae0d7cd2c709.png!small)

## 0x01 漏洞概述

CVE-2021-3493漏洞是Linux内核中overlayfs文件系统中的Ubuntu特定问题，在Ubuntu中没有正确验证关于用户名称空间的文件系统功能的应用程序。由于Ubuntu带有一个支持非特权的overlayfs挂载的补丁，因此本地攻击者可以使用它来进行提权操作，因此该漏洞对Linux的其他发行版没有影响。

## 0x02 影响版本

    
    
    Ubuntu20.10  
    Ubuntu20.04LTS  
    Ubuntu18.04LTS  
    Ubuntu16.04LTS  
    Ubuntu14.04ESM  
    （Linux内核版本<5.11）

## 0x03 环境搭建

本次复现测试使用的是Vmware Workstation Pro 15虚拟机软件，安装Ubuntu 16.04LTS虚拟机

1.安装Vmware Workstation Pro或其他软件来安装虚拟机；

2.安装受影响版本的Ubuntu虚拟机；

具体虚拟机安装步骤可以自行上网搜索；

3.安装完后可以查看安装的具体版本；

    
    
    lsb_release -a

![image-20210701015940366](https://image.3001.net/images/20210713/1626143675_60ecfbbbe4ecc60397bf0.png!small)

4.查看Linux内核版本。

    
    
    uname -a

![image-20210701020518683](https://image.3001.net/images/20210713/1626143676_60ecfbbcd2101fe943f70.png!small)

## 0x04 漏洞复现

1.拷贝exp代码，并保存到测试机器上（这里是Ubuntu16.04.7LTS虚拟机）

    
    
    https://github.com/briskets/CVE-2021-3493/blob/main/exploit.c

![image-20210701014117987](https://image.3001.net/images/20210713/1626143677_60ecfbbdb8af3b80826e1.png!small)

2.保存exp代码为 cve-2021-3493.c 后在Linux上使用gcc进行编译，生成cve-2021-3494可执行文件

    
    
    gcccve-2021-3493.c -ocve-2021-3493

![image-20210701014022747](https://image.3001.net/images/20210713/1626143678_60ecfbbeea97ac05d4136.png!small)

3.查看当前用户信息，运行exp后再查看用户信息

![image-20210701014454593](https://image.3001.net/images/20210713/1626143680_60ecfbc09f4bc2d6df922.png!small)

可以看到运行脚本后开启的shell已经是root用户权限的shell了，提权成功，此时我们可以通过root权限的shell来对目标进行任意操作。

我们知道 user namespace（用户名字空间）主要起对用户和用户组进行隔离的作用，user
namespace一个特定的目标就是允许一个进程在容器中的操作拥有root特权，与此同时，在托管容器的宿主机上是一个无特权的正常进程。

而在该EXP的原理就是通过修改 user namespace
使其在另一个名字空间下具有root权限，从而可以挂载overlay，然后再利用挂载的overlay拷贝magic可执行文件，由于当前修改后所在的名字空间有超级权限，就可以直接设置capability，来赋予magic文件root权限，然后运行magic，此时进程就已经被赋予
all + eip的权限，然后就能进行 setuid(0) setgid(0) 的提权操作，从而达到拿root权限shell的目的。

![image-20210701173659796](https://image.3001.net/images/20210713/1626143681_60ecfbc1b9aee6d59af03.png!small)

## 0x05 修复建议

1）更新系统软件包版本；

可参考供应商公告，如下链接所示。

<https://ubuntu.com/security/notices/USN-4915-1>

<https://ubuntu.com/security/notices/USN-4916-1>

<https://ubuntu.com/security/notices/USN-4917-1>

2）在Linux 5.11中，对的调用 cap_convert_nscap 已移入 vfs_setxattr，更新Linux内核至5.11则不会再被利用。

