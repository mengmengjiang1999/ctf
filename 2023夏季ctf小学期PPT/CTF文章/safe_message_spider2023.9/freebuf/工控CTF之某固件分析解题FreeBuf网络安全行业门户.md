## 一、解题

**在2019年工业信息安全技能大赛第一场线上赛中有一道固件分析的题目，当时虽然Get到了答案，却终归是知其然不知其所以然，于是决定搭个环境来完整分析一下，顺便学习一下路由器漏洞分析。话不多说，先上题目：**

![](https://image.3001.net/images/20191202/1575254177_5de478a14b3d0.png!small)拿到题目后，首先想到的是：这应该是一个被公开过的路由器漏洞吧，会是什么路由器的洞呢？题目说明中提到了tddp协议，于是先搜索一把，相关结果如下：

![](https://image.3001.net/images/20191202/1575254191_5de478af0a128.png!small)

![](https://image.3001.net/images/20191202/1575254203_5de478bbd023c.png!small)![](https://image.3001.net/images/20191202/1575254210_5de478c2c4cdb.png!small)还真有发现：TP-Link
SR20路由器…数据的第二个字节为0x31…远程代码执行，难道就这么巧么？尝试根据题目提示猜测组合答案：CMD_FTEST_CONFIG+0x02+0x31，进行提交，嗯，答案正确，解题完毕……

## 二、漏洞复现

###  **基础环境搭建**

解题成功纯属巧合，要搞清楚来龙去脉还得靠漏洞复现+分析，于是决定搭个环境跑跑看（一堆坑啊，各种问题是必然的，一路坎坷一路向远方）。先下载了Ubuntu18.04
ISO把虚拟机装起，然后下载Qemu，Qemu是纯软件实现的虚拟化模拟器，几乎可以模拟任何硬件设备。可以使用命令：

    
    
    apt install qemu

直接安装，或者下载源码：<https://download.qemu.org/>编译安装,解压后进入到qemu目录，然后：

    
    
    ./configure  #配置
    
        make #编译
    
        make install

此过程将遇到各种问题，可参考<https://blog.csdn.net/snail_coder/article/details/82935081>进行解决。

安装完成后如下所示：

![](https://image.3001.net/images/20191202/1575254248_5de478e86d407.png!small)

将待分析固件拷贝进虚拟机，首选binwalk走一波：

    
    
    binwalk 6-bin.bin
    
        binwalk -Me 6-bin.bin

![](https://image.3001.net/images/20191202/1575254261_5de478f5582ad.png!small)squashfs-root目录就是路由器的固件文件系统：![](https://image.3001.net/images/20191202/1575254272_5de47900a4e71.png!small)

![](https://image.3001.net/images/20191202/1575254278_5de4790630ba0.png!small)

### **ARM QEMU** **环境搭建**

路由器固件已有，接着需要搭建ARM虚拟化环境，进而将固件跑起来。从Debian官网:
<https://people.debian.org/>~aurel32/qemu/armhf/下载Debian ARM系统的相关文件:
vmlinuz-3.2.0-4-vexpress、initrd.img-3.2.0-4-vexpress、debian_wheezy_armhf_standard.qcow2；为虚拟机添加一个网卡tap0用以与ARM虚拟机通信：

    
    
    sudo tunctl -t tap0
    
        sudo ifconfig tap0 10.10.10.1/24

执行命令开启ARM虚拟机：

    
    
    qemu-system-arm-M vexpress-a9 -kernel vmlinuz-3.2.0-4-vexpress -initrdinitrd.img-3.2.0-4-vexpress -driveif=sd,file=debian_wheezy_armhf_standard.qcow2 -append
    
    "root=/dev/mmcblk0p2console=ttyAMA0" -net nic -net tap,ifname=tap0,script=no,downscript=no-nographic

给ARM虚拟机配置IP，并将固件拷贝至ARM虚拟机中：

![](https://image.3001.net/images/20191202/1575254294_5de47916cd2d4.png!small)

使用chroot 切换根目录固件文件系统：

    
    
    mount -o bind /dev ./squashfs-root/dev/
    
        mount -t proc /proc/ ./squashfs-root/proc/
    
        chroot squashfs-root sh

成功切换至固件文件系统，将固件跑起来了：

![](https://image.3001.net/images/20191202/1575254311_5de479271086b.png!small)执行PoC代码，测试一下是否能远程执行命令：

![](https://image.3001.net/images/20191202/1575254324_5de47934eee6d.png!small)连接路由器成功并获取固件系统详细信息，至此漏洞复现完成。

##  三、漏洞分析

通过搜索关键字符串，尝试定位相关漏洞函数：

![](https://image.3001.net/images/20191202/1575254345_5de4794995b6b.png!small)

![](https://image.3001.net/images/20191202/1575254350_5de4794e96f68.png!small)来到函数sub_15E74查看伪码：![](https://image.3001.net/images/20191202/1575254361_5de4795910651.png!small)![](https://image.3001.net/images/20191202/1575254365_5de4795d88e59.png!small)该函数为处理接收到来自UDP
Port 1040基于tddp协议的数据，可以看到函数中的switch
case,对应着不同情况的处理方式。漏洞发生在分支0x31处理“CMD_FTEST_CONFIG”类型消息，因此漏洞函数为sub_A580,继续跟进：![](https://image.3001.net/images/20191202/1575254382_5de4796e38e64.png!small)此处调用了sscanf函数，将用户参数根据格式化字符串解析到后面的参数中，然后进入到sub_91DC函数中执行。由于sscanf函数中只判断了；字符，未对&和|符号进行过滤，因此可进行命令注入，拼接恶意代码然后进入sub_91DC函数中得以执行，继续跟进sub_91DC函数：![](https://image.3001.net/images/20191202/1575254394_5de4797a39cfb.png!small)这里直接调用execve函数进行命令执行，至此，漏洞分析完成。

 ***本文作者：ww5466064，转载请注明来自FreeBuf.COM**

