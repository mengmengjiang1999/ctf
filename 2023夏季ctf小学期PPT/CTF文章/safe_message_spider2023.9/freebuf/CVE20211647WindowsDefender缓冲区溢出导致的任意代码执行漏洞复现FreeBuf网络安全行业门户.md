## 0x01 漏洞概述

Windows
Defender是Windows自带的防护软件，其在对可执行文件进行检测时采用模拟执行的策略进行黑白判定，模拟执行分为两个部分：指令模拟和运行环境模拟。其中指令模拟会将程序的响应平台指令（arm/mips/x86等）转换成Defender自己的中间指令，然后运行相应的中间指令来模拟执行该文件；而运行环境模拟则是对内存系统、文件系统、系统API、DLL等进行模拟。

Defender在进行指令模拟的时候遇到带壳的可执行文件会使用内置的一些方法尝试脱壳，目前支持脱壳的方式有Upxw64/Upxw/WExtract/NSPacker/Shrinker/PECompact2/Area51/Crypter1337/Aspack/PKLite/SfxCab/Asprotect
等，这次漏洞所在的就是Asprotect壳的脱壳过程中，当攻击者构造一个带有特殊PE头的可执行文件，Windows
Defender检测时就会出发缓冲区溢出漏洞进而导致任意代码执行。

## 0x02 影响版本

![1622440103_60b478a75199616c8dbfb.png!small?1622440154017](https://image.3001.net/images/20210531/1622440103_60b478a75199616c8dbfb.png!small?1622440154017)

## 0x03 环境搭建

1.首先安装VMware workstation虚拟机（本实验使用的VMware workstation虚拟机为15版本）

2.在虚拟机上安装 Windows10 1903 靶机（或上述任一受影响版本）

3.下载POC程序

确保Windows Defender没有更新（可以采取断网措施防止后续更新）

![](https://image.3001.net/images/20210531/1622440424_60b479e8e0c09c46447b7.png!small)

## 0x04 漏洞复现

1.启动Windows 10虚拟机

2.将含有POC程序的压缩包复制到靶机任意位置

![](https://image.3001.net/images/20210531/1622440426_60b479eac0f16d31bc31d.png!small)

3.直接右键对该文件进行解压

![](https://image.3001.net/images/20210531/1622440427_60b479eb82bf311851994.png!small)

4.解压后就能弹一个system权限的命令行窗口出来，因为Windows
Defender在文件被从压缩包里解压出来的时候就会检查这几个新文件，发现是加壳的可执行文件就会让引擎脱壳，其中的溢出漏洞就会触发，进而达到任意命令执行的目的。

5.同时Windows Defender也会发生崩溃，并在数十秒后自动重新启动。

![](https://image.3001.net/images/20210531/1622440428_60b479ecb0853cd7828cd.png!small)

## 0x05 防护建议

Windows联网，打开Windows Defender防护中心手动点击更新Windows
Defender，并保持Windows自动更新开启，或通过第三方安全防护软件的相关补丁功能进行补丁安装。

