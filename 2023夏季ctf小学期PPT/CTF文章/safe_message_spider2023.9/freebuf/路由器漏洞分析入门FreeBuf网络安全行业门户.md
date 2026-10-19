## 路由器漏洞分析入门

路由器漏洞分析，不可能仅凭自己头脑完成。在这个过程中，我们需要借助必要的工具实现对漏洞的分析和利用。本篇文章将介绍路由器漏洞分析过程中使用的工具以及漏洞分析环境的安装、配置和使用方法,最后我们通过实战分析路由器常见的漏洞。

## 1\. 漏洞分析环境搭建

### 1.1 修改apt源

本地虚拟机Ubuntu20.04

更改系统apt源

    
    
    $ sudo gedit /etc/apt/sources.list
    

源内容

    
    
    deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
    deb-src http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
     
    deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
    deb-src http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
     
    deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
    deb-src http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
     
    deb http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
    deb-src http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
     
    deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
    deb-src http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
    

更新

    
    
    $ sudo apt-get update
    

### 1.2 Binwalk安装

Binwalk 是一种快速、易于使用的工具，用于分析、逆向工程和提取固件镜像。

 **01 安装Git**

    
    
    $ sudo apt-get install git -y
    $ sudo apt-get install build-essential autoconf -y #缺省情况下，并没有提供C/C++的编译环境，为后续安装其他软件做准备
    

**02 下载Binwalk**

    
    
    $ git clone https://github.com/ReFirmLabs/binwalk.git
    Cloning into 'binwalk'...
    remote: Enumerating objects: 8417, done.
    remote: Counting objects: 100% (99/99), done.
    remote: Compressing objects: 100% (79/79), done.
    remote: Total 8417 (delta 48), reused 51 (delta 19), pack-reused 8318
    Receiving objects: 100% (8417/8417), 43.98 MiB | 5.25 MiB/s, done.
    Resolving deltas: 100% (4872/4872), done.
    

**03 安装Binwalk**

根据INSTALL.md内容

Debian/Ubuntu 可以通过deps.sh脚本，安装所需依赖

    
    
    $ sudo ./dep.sh
    

提示没有python

    
    
    $ sudo apt-get install python -y
    

安装依赖过程可能出现`Unable to fetch some archives, maybe run apt-get update or try with
--fix-missing?`

    
    
    $ sudo apt-get update --fix-missing
    

重新执行deps.sh

    
    
    $ sudo ./deps.sh
    

缺少pip

    
    
    $ sudo apt-get install python3-pip -y
    

pip安装matplotlib可能非常慢，需要更换源

修改方法大家可以查看 https://blog.csdn.net/sinat_21591675/article/details/82770360

安装程序

    
    
    $ sudo python3 setup.py install
    $ binwalk
    Binwalk v2.2.1+2b78673
    Craig Heffner, ReFirmLabs
    https://github.com/ReFirmLabs/binwalk
    
    Usage: binwalk [OPTIONS] [FILE1] [FILE2] [FILE3] ...
    
    Disassembly Scan Options:
        -Y, --disasm                 Identify the CPU architecture of a file using the capstone disassembler
        -T, --minsn=<int>            Minimum number of consecutive instructions to be considered valid (default: 500)
        -k, --continue               Don't stop at the first match
        ......
    

### 1.3 交叉编译工具链(ARM和MIPS)

交叉编译工具链用来编译一些测试程序，如后门程序(运行在路由器设备上)

 **1.3.1 安装BuildRoot**

01 下载buildroot

下载地址 https://buildroot.org/downloads/buildroot-2021.02.3.tar.gz

02 配置

进入目录

    
    
    $ make menuconfig
    

缺少依赖 libncurse-dev

    
    
    $ sudo apt-get install libncurse5-dev -y
    

选择

    
    
    $ make menuconfig
    

Target options-> mips(little)

Toolchain options -> kernel headers(Linux 4.4.x kernel header)

编译

    
    
    $ make V=s
    

gcc位于output/host/bin目录

![image](https://image.3001.net/images/20210825/1629880988_6126029cf08ed35ebe26b.png!small)

 **1.3.2 编译简单程序**

尽量编译静态程序(动态程序依赖动态库，设备没有那么多符合条件的动态库)

    
    
    #include <stdio.h>
    
    int main(int argc,char *argv[])
    {
        printf("Hello World!");
    }
    

编译

    
    
    $ mipsel-linux-gcc --static main.c -o mips_test
    $ file mips_test
    mips_test: ELF 32-bit LSB executable, MIPS, MIPS32 version 1 (SYSV), statically linked, with debug_info, not stripped
    

### 1.4 Qemu模拟运行程序

 **1\. 安装Qmeu**

    
    
    $ sudo apt-get install qemu-user-static qemu-user -y
    

**2\. 运行程序**

    
    
    $ qemu-user-static ./qemu_test #运行刚才编译的程序
    Hello World!
    

![image](https://image.3001.net/images/20210825/1629881007_612602af033dfbf98f995.png!small)

## 2\. 固件分析

### 2.1 解压固件

    
    
    $ binwalk -Me RT-N18U_3.0.0.4_382_52288-geac6f28.trx
    

![image](https://image.3001.net/images/20210825/1629881029_612602c53908588ee85d4.png!small)

### 2.2 查看敏感信息

Firmwalker工具，该工具通过静态分析来识别固件中可能包含的常见敏感信息。

 **1)克隆项目**

    
    
    $ git clone https://github.com/craigz28/firmwalker.git
    

**2)运行脚本**

    
    
    $ ./firmwalker.sh /home/iot/Desktop/_RT-N18U_3.0.0.4_382_52288-geac6f28.trx.extracted/squashfs-root
    

![image](https://image.3001.net/images/20210825/1629881044_612602d4d5144761407bb.png!small)

**3)识别内容**

识别出多种敏感信息，包括二进制文件、证书、IP地址、私钥等，输出结果保存在firmwalker.txt

## 3\. 固件仿真模拟

FirmAE
是一个全自动框架，可以执行仿真和漏洞分析。FirmAE通过五种仲裁技术提高了仿真成功率（从[Firmadyne](https://github.com/firmadyne/firmadyne)的
16.28% 到 79.36%）。

### 3.1 安装

 **1）克隆**

    
    
    $ git clone --recursive https://github.com/pr0v3rbs/FirmAE
    

**2) 运行download.sh**

    
    
    $ ./download.sh
    

**3) 运行install.sh**

    
    
    $ ./install.sh
    

### 3.2 运行

 **1） 执行init.sh脚本**

    
    
    $ ./init.sh
    

**2) 仿真固件**

    
    
    $ sudo ./run.sh -d dlink DIR-868L_B1_FW205WWb02.bin # 调试模式
    

模拟固件创建时间较长，请耐心等待 。。。

![image](https://image.3001.net/images/20210825/1629881070_612602eea4ad4faaf42b6.png!small)

 **3)执行shell命令**

执行shell命令

![image](https://image.3001.net/images/20210825/1629881084_612602fcb2d81bfe228b3.png!small)

该框架提供了抓流量、执行shell命令、远程gdb调试、文件上传的功能。

 **3) 访问网页**

![image](https://image.3001.net/images/20210825/1629881101_6126030d03579fe1e5ff7.png!small)

## 4\. 实战分析

### CVE-2020-29321

D-Link 路由器 DIR-868L 3.01 telnet 服务中的凭据泄露，这允许未经身份验证的攻击者访问固件并提取敏感数据。

 **4.1 固件解压**

![image](https://image.3001.net/images/20210825/1629881116_6126031c50d005973c15f.png!small)

 **4.2 定位漏洞**

![image](https://image.3001.net/images/20210825/1629881131_6126032b753329b57a4d5.png!small)

IDA打开分析

![image](https://image.3001.net/images/20210825/1629881155_6126034384140fb92a454.png!small)

-u 参数指定 用户名和密码

查找调用该程序的脚本

![image](https://image.3001.net/images/20210825/1629881176_612603587c8971872e3bf.png!small)

查看该脚本

    
    
    #!/bin/sh
    echo [$0]: $1 ... > /dev/console
    orig_devconfsize=`xmldbc -g /runtime/device/devconfsize` 
    entn=`devdata get -e ALWAYS_TN`
    if [ "$1" = "start" ] && [ "$entn" = "1" ]; then
    	telnetd -i br0 -t 99999999999999999999999999999 &
    	exit
    fi
    
    if [ "$1" = "start" ] && [ "$orig_devconfsize" = "0" ]; then
    	
    	if [ -f "/usr/sbin/login" ]; then
    		image_sign=`cat /etc/config/image_sign`
    		telnetd -l /usr/sbin/login -u Alphanetworks:$image_sign -i br0 &
    	else
    		telnetd &
    	fi 
    else
    	killall telnetd
    fi
    

密码位于`/etc/config/image_sign`

查看密码内容

![image](https://image.3001.net/images/20210825/1629881190_61260366734398a02b390.png!small)

 **4.3 测试漏洞**

4.3.1 模拟固件

FirmAE模拟

    
    
    $ ./init.sh
    $ sudo ./run.sh -d dlink DIR868LC1_FW301b08.bin
    

![image](https://image.3001.net/images/20210825/1629881201_612603712c38282c37519.png!small)

访问页面

![image](https://image.3001.net/images/20210825/1629881209_6126037988ff50f24196a.png!small)

命令查看没有启动自生的telnetd

![image](https://image.3001.net/images/20210825/1629881222_612603860b4328efed3fc.png!small)

    
    
    orig_devconfsize=`xmldbc -g /runtime/device/devconfsize`  #模拟固件并没有生成，应该实体机器才会生成相应目录
    

模拟测试运行

    
    
    $ image_sign = `cat /etc/config/image_sign`
    $ telnetd -l /usr/sbin/login -u Alphanetworks:$image_sign -i br0 &
    

4.3.2 Telnet连接

![image](https://image.3001.net/images/20210825/1629881246_6126039e83002c614ca56.png!small)

## 总结

希望本篇文章对刚入门路由器安全的小伙伴起到一定帮助。

