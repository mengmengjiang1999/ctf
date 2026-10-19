**[上一篇文章](https://www.freebuf.com/articles/ics-articles/221625.html)分了一下ARM系统的路由器漏洞，本次打算尝试一下MIPS系统，于是选了最近DLink路由器的漏洞CVE-2019-17621作为目标。同样一路走来各种踩坑不断，“纸上得来终觉浅，绝知此事要躬行”，对整个过程做一下梳理。  
**

## 1、环境搭建

运行环境安装配置之前须了解你所使用的Linux系统的版本以及Qemu的版本，因为这直接影响着你后续选择安装各种依赖包、mips
qemu镜像等的版本，各种版本都对应上，最终系统才能正确运行。本次漏洞分析的基础环境为前期的Ubuntu18.04虚拟机和基于qemu-4.0.0源码编译安装的Qemu运行环境：

![](https://image.3001.net/images/20200228/1582890441_5e58fdc9d52c0.png!small)

从站点<https://people.debian.org/~aurel32/qemu/mips/>下载debianmips
qemu镜像，由于虚拟机是Ubuntu
linux，下载debian_squeeze_mips_standard.qcow2和vmlinux-2.6.32-5-4kc-malta即可：

![](https://image.3001.net/images/20200228/1582890482_5e58fdf265e80.png!small)

### MIPS系统网络配置

使用QEMU
模拟运行MIPS系统，需要将ubuntu虚拟机设置成桥接，这样以来ubuntu系统就可以和QEMU虚拟机进行通信和数据传输（此操作类似配置VMware
Workstation的桥接用以与物理机的通信）。

获取安装依赖，执行以下命令：

    
    
    sudo apt-get install bridge-utils uml-utilities

修改ubuntu主机网络配置，将ubuntu的网络接口配置文件 /etc/network/interfaces 修改为如下内容并保存、关闭：

    
    
    sudo gedit /etc/network/interfaces

![](https://image.3001.net/images/20200228/1582890507_5e58fe0b3d211.png!small)

修改QEMU的网络接口启动脚本，重启网络使配置生效，执行以下命令：

    
    
    sudo gedit /etc/qemu-ifup

在脚本文件/etc/qemu-ifup结尾增加如下内容：

![](https://image.3001.net/images/20200228/1582890543_5e58fe2f21a00.png!small)

保存文件/etc/qemu-ifup 以后，赋予可执行权限，然后重启网络使所有的配置生效：

> sudo chmod a+x /etc/qemu-ifup
>
> sudo /etc/init.d/networking restart

### QEMU启动配置

Qemu运行之前先启动桥接网络，在本地ubuntu命令行终端执行以下命令（注意：ens33为ubuntu默认网卡）：

    
    
    sudo ifdown ens33

![](https://image.3001.net/images/20200228/1582890566_5e58fe46ad15e.png!small)

sudo ifup br0

![](https://image.3001.net/images/20200228/1582890589_5e58fe5d6b821.png!small)

### QEMU MIPS虚拟机启动

进入前面下载的mips镜像目录，执行以下命令：

    
    
    sudo qemu-system-mips -M malta -kernelvmlinux-2.6.32-5-4kc-malta -hda debian_squeeze_mips_standard.qcow2 -append"root=/dev/sda1 console=tty0" -net nic,macaddr=00:16:3e:00:00:01 -nettap

![](https://image.3001.net/images/20200228/1582890610_5e58fe729f851.png!small)

输入root/root便可登入qemu mips虚拟机，为了更便操作mips虚拟机，可在unbuntu中新开启一个终端，ssh连接到qemu mips：

![](https://image.3001.net/images/20200228/1582890646_5e58fe9601280.png!small)

### 固件模拟运行

从DLink官网下载包含漏洞版本的路由器固件：<ftp://ftp2.dlink.com/PRODUCTS/DIR-859/DIR-859_REVA_FIRMWARE_v1.05B03.zip>，使用binwalk-Me直接解压固件可得到文件系统文件：

![](https://image.3001.net/images/20200228/1582890670_5e58feaef0fff.png!small)

固件模拟运行由两种方式可以考虑：① 将文件系统上传到qemu mips虚拟机中运行；②
借助firmadyne工具运行固件（当然也可以尝试使用AttifyOS VM）：

① 使用scp命令将squashfs-root目录上传到qemu mips虚拟机：

![](https://image.3001.net/images/20200228/1582890696_5e58fec8e8ded.png!small)

chroot /root/squashfs-root sh

![](https://image.3001.net/images/20200228/1582890721_5e58fee17cc85.png!small)

② 借助firmadyne工具运行固件

Firmadyne是一款自动化和可裁剪的嵌入式Linux系统固件分析框架，它支持系统固件逆向QEMU嵌入式系统模拟执行，使用其可模拟路由器固件、执行路由器。安装和使用方法详见<https://github.com/firmadyne/firmadyne>。注意：Firmadyne安装之前，先安装firmware-analysis-toolkit，安装方法详见<https://github.com/attify/firmware-analysis-toolkit>，安装完成之后在firmware-analysis-toolkit目录中创建firmadyne目录并下载安装Firmadyne。各自全部安装完成后如下所示（注意两个工具须完全按照步骤安装完成，否则后续固件运行会出错）：

![](https://image.3001.net/images/20200228/1582890746_5e58fefa38bce.png!small)

首先将firmware-analysis-toolkit目录下的fat.py和reset.py文件移动到firmadyne目录；接着进入firmadyne修改firmadyne.config设置路径如下：

![](https://image.3001.net/images/20200228/1582890774_5e58ff161421c.png!small)

将固件bin文件拷贝至firmadyne目录，继续执行以下命令：

    
    
    rm -rf images*
    
    python3 reset.py
    
    sudo -u postgres createdb -O firmadyne firmware
    
    sudo -u postgres psql -d firmware < ./database/schema
    
    ./sources/extractor/extractor.py -b Dlink -sql 127.0.0.1 -np-nk "DIR859Ax_FW105b03.bin" images
    
    ./scripts/getArch.sh ./images/1.tar.gz
    
    ./scripts/makeImage.sh 1
    
    ./scripts/inferNetwork.sh 1
    
    ./scratch/1/run.sh

![](https://image.3001.net/images/20200228/1582890855_5e58ff6789af4.png!small)

![](https://image.3001.net/images/20200228/1582890867_5e58ff7362053.png!small)

Ubuntu中打开浏览器，输入192.168.0.1即可访问仿真路由器：

![](https://image.3001.net/images/20200228/1582890896_5e58ff9016712.png!small)

## 2、远程调试

路由器固件已成功得以运行，接下来可以对目标程序进行调试，此时可借助物理机中IDA进行远程调试（当然，IDA也可以安装在ubuntu中）。调试仍然有两种思路：

① 在qemu mips虚拟机中，借助静态gdbserver和远程IDA的“remote GDB
debugger”功能对目标mips程序进行动态调试，此处需要注意的是静态gdbserver文件格式必须和mips系统的大/小端完全对应，可用file命令查看固件的相关信息：

![](https://image.3001.net/images/20200228/1582890924_5e58ffacb99e1.png!small)

因此须首先交叉编译得到32bit MSB格式的静态gdbserver文件，交叉编译可用选择Openwrt或Buildroot，此处省略。

② 在ubuntu解出固件文件系统后，使用chroot命令，配合qemu-mips-static运行目标文件（cgibin为目标文件），然后附件远程IDA进行动态调试，首先在ubuntu中执行以下命令：

    
    
    chroot ../qemu-mips-static -g 1235./htdocs/cgibin

![](https://image.3001.net/images/20200228/1582890944_5e58ffc0ea91b.png!small)

接着在物理集中打开IDA调试器，进行如下操作：

![](https://image.3001.net/images/20200228/1582890962_5e58ffd2a021e.png!small)

![](https://image.3001.net/images/20200228/1582890969_5e58ffd96d144.png!small)

![](https://image.3001.net/images/20200228/1582890976_5e58ffe09a5d3.png!small)

![](https://image.3001.net/images/20200228/1582890985_5e58ffe9e2f9f.png!small)

最终可成功进行远程调试：

![](https://image.3001.net/images/20200228/1582890999_5e58fff758db8.png!small)

## 3、漏洞分析

在路由器运行状态下，文件系统中的/htdocs/cgibin的genacgi_main()函数在UPnP请求处理过程中，存在远程执行代码漏洞。UPnP是专用网络中设备之间的通信协议，实现了智能设备端到端网络连接结构。它也是一种架构在TCP/IP和HTTP技术之上的，分布式、开放的网络结构，以使得在联网的设备间传递控制和数据。UPnP不需要设备驱动程序，因此使用UPnP建立的网络是介质无关的。同时UPnP使用标准的TCP/IP和网络协议，使它能够无缝的融入现有网络。构造UPnP应用程序时可以使用任何语言，并在任何操作系统平台上编译运行。

尝试静态下使用IDA反汇编cgibin文件，然后F5查看伪代码，发现操作失败，故换用Ghidra(NSA发布的、基于Java开发的、适用于Windows、Mac和Linux的跨平台反汇编工具)，发现可快速定位genacgi_main()函数并查看伪码（貌似反汇编能力优于IDA？）：

![](https://image.3001.net/images/20200228/1582891022_5e59000e7adc7.png!small)

从伪码中可以看到，sprintf()函数设置了一个包含所有值的缓冲区，其中函数参数
?service=及其值，被xmldbc_ephp()函数(最后调用send())将“buffer_8”中包含的数据发送给PHP：

![](https://image.3001.net/images/20200228/1582891040_5e590020c5eaf.png!small)

可看出sprintf()用于连接多个变量的值，用于填充一个缓冲区，设置要传递的新变量，其中SHELL_FILE将以格式%s_%d.sh进行传递，主要用于为新的shell脚本命名。缓冲区中的数据经过xmldbc_ephp处理，由PHP文件run.NOTIFY.php进行处理，如下：

![](https://image.3001.net/images/20200228/1582891056_5e5900303460d.png!small)

![](https://image.3001.net/images/20200228/1582891063_5e5900370ed1f.png!small)

![](https://image.3001.net/images/20200228/1582891068_5e59003cbe2a6.png!small)

程序的调用流程为：buf_8 ->xmldbc_ephp->FUN_0041420c ->FUN_0041372c -> socket。

关于run.NOTIFY.php内容：

![](https://image.3001.net/images/20200228/1582891085_5e59004dc5ea7.png!small)

其中可见调用了PHP函数
GENA_subscribe_new()，并传递cgibin程序中genacgi_main()函数获得的变量，还包括变量SHELL_FILE。搜索GENA_subscribe_new()发现其定义在gena.php文件中，分析GENA_subscribe_new功能可知其并不修改$shell_file变量，

![](https://image.3001.net/images/20200228/1582891103_5e59005fe9d7b.png!small)

其传递
$shell_file到GENA_notify_init函数，也就是shell_file最终处理的地方：通过调用PHP函数fwrite()创建新文件，且fwrite()函数被使用了两次：

![](https://image.3001.net/images/20200228/1582891121_5e5900718474a.png!small)

fwrite()函数第一次创建文件，文件名由可控的SHELL_FILE变量(uri_service)以及getpid()组成：

![](https://image.3001.net/images/20200228/1582891139_5e59008389fda.png!small)

第二次调用fwrite()向文件中添加删除命令"rm
-f".$shell_file."\n"，攻击时，只需要插入一个反引号包裹的系统命令，将其注入到shell脚本中，当脚本执行rm命令时遇到反引号将失败，继续执行引号里面的系统命令，从而达到远程命令执行漏洞的触发。因此，控制好"/gena.cgi?service=shell_file"中shell_file的内容为反引号包裹的系统命令，就可以触发漏洞。

## 4、漏洞重现

根据漏洞原理，执行以下PoC脚本：

![](https://image.3001.net/images/20200228/1582891167_5e59009f91e07.png!small)

由此可见漏洞利用后，目标路由器的telnetd服务被开启，获得维持访问shell。

![](https://image.3001.net/images/20200228/1582891184_5e5900b0004d5.png!small)

 ***本文原创作者：ww5466064，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

