## 写在前面

本次测试仅供学习使用，如若非法他用，与本文作者无关，需自行负责！

## 漏洞描述

该漏洞的存在是由于Linux内核中某些*_OR_NULL指针类型的指针算法的可用性。本地用户可以运行特制的程序，最终以root权限执行任意代码，利用条件为低权限用户认证。

## 影响版本

linux内核 5.8 - 5.16

## 漏洞复现

内核版本

![1654909100_62a3e8acd7ec9df5bec7c.png!small?1654909101319](https://image.3001.net/images/20220611/1654909100_62a3e8acd7ec9df5bec7c.png!small?1654909101319)

1.github下载利用exp

git clone <https://github.com/tr3ee/CVE-2022-23222.git>

![1654909134_62a3e8ce5aefdf29827ee.png!small?1654909134592](https://image.3001.net/images/20220611/1654909134_62a3e8ce5aefdf29827ee.png!small?1654909134592)

2.make进行编译

![1654909172_62a3e8f4ec96b6485551b.png!small?1654909173118](https://image.3001.net/images/20220611/1654909172_62a3e8f4ec96b6485551b.png!small?1654909173118)

3.执行exp进行本地提权到root

普通用户权限

![1654909205_62a3e915d43a03baafbd5.png!small?1654909205912](https://image.3001.net/images/20220611/1654909205_62a3e915d43a03baafbd5.png!small?1654909205912)

root权限

![1654909247_62a3e93f473cf91997f5f.png!small?1654909247890](https://image.3001.net/images/20220611/1654909247_62a3e93f473cf91997f5f.png!small?1654909247890)

这里是github执行效果

![1654909276_62a3e95c7d7e4e65e2733.png!small?1654909276604](https://image.3001.net/images/20220611/1654909276_62a3e95c7d7e4e65e2733.png!small?1654909276604)

## 修复建议

目前厂商已发布升级补丁以修复漏洞，更新到以下版本

linux内核 5.10.92 / 5.15.15 / 5.16.1，

补丁获取链接：

[https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/kernel/bpf/verifier.c?h=v5.10.83#n6022﻿](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/kernel/bpf/verifier.c?h=v5.10.83#n6022)

