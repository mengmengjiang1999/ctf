## 0x00简介

linux kernel一般指Linux内核。Linux是一种开源电脑操作系统内核。它是一个用C语言写成，符合POSIX标准的类Unix操作系统。

## 0x01漏洞概述

OverlayFS漏洞允许Ubuntu下的本地用户获得root权限。Linux内核中overlayfs文件系统中的Ubuntu特定问题，在该问题中，它未正确验证关于用户名称空间的文件系统功能的应用程序。由于Ubuntu附带了一个允许非特权的overlayfs挂载的补丁，因此本地攻击者可以使用它来获得更高的特权。

## 0x02影响版本

Ubuntu 20.10

Ubuntu 20.04 LTS

Ubuntu 18.04 LTS

Ubuntu 16.04 LTS

Ubuntu 14.04 ESM

## 0x03环境搭建

1、下载漏洞镜像

下载地址：https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/18.04/ubuntu-18.04.5-desktop-amd64.iso

![1620375398_6094f766d728452cb0767.png!small?1620375399434](https://image.3001.net/images/20210507/1620375398_6094f766d728452cb0767.png!small?1620375399434)

2、在VMware中安装虚拟机，安装过程自行百度。

![1620375404_6094f76c8fe07f07f270b.png!small?1620375404763](https://image.3001.net/images/20210507/1620375404_6094f76c8fe07f07f270b.png!small?1620375404763)

3、安装完成后查看系统内核版本

![1620375408_6094f770863e401365ea7.png!small?1620375408530](https://image.3001.net/images/20210507/1620375408_6094f770863e401365ea7.png!small?1620375408530)

## 0x04漏洞复现

1、 在GitHub上下载漏洞利用exp，下载地址：

https://github.com/briskets/CVE-2021-3493

2、 使用git下载到虚拟机中查看Linux及sudo版本

lsb_release -a

sudo -V

![1620375413_6094f775066af9e1b0cc2.png!small?1620375413182](https://image.3001.net/images/20210507/1620375413_6094f775066af9e1b0cc2.png!small?1620375413182)

3、 测试漏洞是否存在如果返回以sudoedit:开头的错误，则当前系统可能存在安全风险；不受影响的系统将显示以usage:开头的错误。

sudoedit -s /

![1620375418_6094f77a7d947509cb262.png!small?1620375418624](https://image.3001.net/images/20210507/1620375418_6094f77a7d947509cb262.png!small?1620375418624)

4、将下载的payload编译exploit.c，然后给于执行权限，然后执行

gcc exploit.c -o exploit

chmod +x exploit

./exploit

![1620375422_6094f77e5679964f75fd1.png!small?1620375422366](https://image.3001.net/images/20210507/1620375422_6094f77e5679964f75fd1.png!small?1620375422366)

![1620375425_6094f781de1babd5f14ff.png!small?1620375426449](https://image.3001.net/images/20210507/1620375425_6094f781de1babd5f14ff.png!small?1620375426449)

## 0x05修复建议

1、更新系统软件包版本。

2、更新Linux内核至5.11

参考链接：https://github.com/blasty/CVE-2021-3156

