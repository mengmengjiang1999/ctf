**本文是一篇完整的关于环境安装和设置的指南。你将学习到如何在Virtualbox中练习Solaris 10
x86漏洞的配置修补与利用。其实对于多年来从事信息安全的我来说这是件及其无聊的事，而如果你是位UNIX的系统管理员则更是如此。**

**![1.png](https://image.3001.net/images/20190808/1565226045_5d4b743d778d7.png!small)**

过去，你很难掌握所有的架构。因为在当时硬件非常难得，并且价格也非常昂贵。如今，随着虚拟化技术（Qemu，VirtualBox，VMWare，AlphaVM，simh）的普及，这一切都开始变得容易。

## Solaris（Solaris 10）

Solaris是Sun Microsystems研发的计算机操作系统。Solaris 10已于2018年1月份正式停止更新。

我们将使用x86端口，在Linux x86_64（（我使用的是Mint 19.1））上的Oracle VirtualBox中运行它的x86_64版本。

下面，让我们开始在Linux上的VirtualBox中安装Solaris 10 - 以下是我们将要用到的（假设我们已对Linux发行版做了一些基本的设置）

> Linux x86_64 (Linux Mint 19.1)
>
> VirtualBox (6.0.10 –[
> https://www.virtualbox.org/wiki/Linux_Downloads](https://www.virtualbox.org/wiki/Linux_Downloads)
> )
>
> Solaris 10 x86 ([
> ftp://ftp.deu.edu.tr/pub/Solaris/iso/Solaris-10,8_11/sol-10-u10-ga2-x86-dvd.iso](ftp://ftp.deu.edu.tr/pub/Solaris/iso/Solaris-10,8_11/sol-10-u10-ga2-x86-dvd.iso))
>
> Solaris 10 x86 Oct-2017-CPU
> (<ftp://ftp.deu.edu.tr/pub/Solaris/patch/x86/10_x86_Recommended.zip> )
>
> networking.sh (用于设置网络适配器仅主机模式的自定义脚本)
    
    
    networking.sh 
    
    #Setup tap and bridge 
    tunctl -t tap0 -u user
    ifconfig tap0 up
    brctl addbr br0
    brctl setfd br0 0
    #ifconfig eth0 10.0.2.1 up 
    ifconfig br0 10.0.2.2 netmask 255.255.255.0 broadcast 10.0.2.255 up
    brctl addif br0 tap0 vboxnet0 
    ifconfig tap0 0.0.0.0
    sysctl net.ipv4.ip_forward=1
    #iptables -A FORWARD --in-interface eth0 -j ACCEPT
    iptables --table nat -A POSTROUTING --out-interface wlan0 -j MASQUERADE

请确保你已安装uml-utilities和bridge-util软件包，并使其正常工作。（注意：这里被注释的eth0条目 -这仅在你希望将模拟仿真网络连接到物理网络，并使其可用于其他设备时启用）

    
    
    # apt-get install uml-utilities bridge-utils

此外，这里还有一个关于vboxnet0接口的重要说明，只有在virtualbox启动之后才能在我的系统上使用。因此，在重启并运行networking.sh脚本后务必牢记这点。

现在，让我们开始吧！在VirtualBox中安装Solaris 10非常简单。我们将使用virtualbox中提供的Oracle Solaris 10
10/09和更高版本（64位）模板创建新的虚拟机。对于网络，我们将使用Host-only-Adapter和vboxnet0。对于磁盘，我们将分配不少于30
GB的存储空间（由于/usr/pkgsrc的原因）。

我们将使用ZFS文件系统，因此选择具有ZFS内核支持的Grub条目。以下是我将用于Solaris10 VM的网络配置。

![2.png](https://image.3001.net/images/20190808/1565226069_5d4b74556a261.png!small)

并遵循以下DNS条目（如果你有自己的DNS，也可以使用你自己的DNS）

![3.png](https://image.3001.net/images/20190808/1565226080_5d4b74604d7b5.png!small)

我们将安装Solaris 10 DVD ISO中的所有内容，设置root密码等。一旦安装程序完成关闭系统，从VM中删除Solaris 10 DVD
ISO并引导新磁盘。在控制台中等待一段时间（尚未登录），等待X11出现。我喜欢CDE，所以我将默认桌面切换为了CDE

![4.png](https://image.3001.net/images/20190808/1565226095_5d4b746f43c5a.png!small)

![5.png](https://image.3001.net/images/20190808/1565226106_5d4b747ad0b43.png!small)

以root身份登录后不要注册Oracle（我们不需要这么做，因为我们有pkgsrc bootstrap。

接下来，我们下载适用于Solaris10 x86_64的2017年10月CPU补丁并安装它（这是Oracle的最后一个Solaris10
CPU，除非有扩展支持..）

在我们的Linux主机上执行以下操作

    
    
    $ mkdir -p SOL10/patch
    $ cd SOL10/patch
    $ wget ftp://ftp.deu.edu.tr/pub/Solaris/patch/x86/10_x86_Recommended.zip
    $ unzip 10_x86_Recommended.zip
    $ mkisofs -iso-level 3 -J -joliet-long -rock -input-charset utf-8 -o patch.iso 10_x86_Recommended/

接下来，我们将这个新的patch.iso添加到我们的VirtualBox CDROM，并重启到单用户模式（对于Solaris上的CPU修补，这是一个好主意）

实际上，当我从CDE dtterm运行时，就是这样进入单用户模式的。

    
    
    # shutdown -g 0

在Solaris10中进入单用户模式后，使用Oct2017 CPU安装ISO

    
    
    # mount -r -F hsfs /dev/dsk/c0t1d0s0/ /cdrom/cdrom
    # cd /cdrom/cdrom

现在，我们将运行补丁集

    
    
    # ./installpatchset --s10patchset

你现在可以去泡杯咖啡或茶放松下，因为这可能需要你等待一段时间。修补过程完成后，重启即可。

![6.png](https://image.3001.net/images/20190808/1565226126_5d4b748e48e07.png!small)

我们来检查下内核版本，看看是否应用了补丁。可以看到，我们当前运行的是2017年10月的内核。两年前曾有披露过两款NSA开发的专门用于攻击Solaris系统的工具“EXTREMEPARR”和“EBBISLAND”。
登录用户使用这两款工具可以提升到Root权限，并通过网络远程获取Root访问权限。这两款工具对x86和Sparc上运行的Solaris版本6至版本10奏效，版本11也未能幸免。
exploit代码可以[在此处获取](https://github.com/0xdea/exploits/blob/master/solaris/raptor_dtprintname_intel.c)。CDE本地提权exploit，我们将在稍后讨论。

    
    
    # uname -a
    SunOS solaris10 5.10 Generic_150401-55 i86pc i386 i86pc

现在，让我们仔细检查一下是否已安装了GCC编译器，如果没有安装那么请安装它。再次在VirtualBox中安装Solaris 10 installation
DVD iso，Solaris将在OS中自动安装ISO。

    
    
    # cd /cdrom/sol_10_811_x86/Solaris_10/Product
    # pkgadd -d . SUNWgcc (answer y)

我们来验证安装，可以看到有一个正常工作的GCC编译器（版本为3.4.3）

    
    
    # /usr/sfw/bin/gcc -v

现在，我们应该要为pkgsrc bootstrap做准备了。让我们先下载Q2-2019稳定快照。

    
    
    # cd /usr
    # ftp ftp.netbsd.org (login as anonymous or ftp)
    ftp> pass
    ftp> cd pub/pkgsrc/pkgsrc-2019Q2
    ftp> get pgsrc.tar.gz
    ftp> quit
    # gunzip pkgsrc.tar.gz
    # tar -xvf pkgsrc.tar
    # rm pkgsrc.tar

一旦提取了tarball，我们就可以相应地设置bootstrap环境了

<https://wiki.netbsd.org/pkgsrc/how_to_use_pkgsrc_on_solaris/>

不要在Solaris中使用附带的bash shell运行bootstrap，请使用默认的sh！

    
    
    # cd /usr/pkgrc/bootstrap
    # env CFLAGS=-O2 CC=/usr/sfw/bin/gcc ./bootstrap

如果一切顺利，我们应该会看到一个成功状态的提示（在Core i5 Panasonic CF-53上花了大约5分钟的时间）。

![7.png](https://image.3001.net/images/20190808/1565226150_5d4b74a6d0cd4.png!small)

在构建任何内容之前，我们需要在/usr/pkg/etc/mk.conf中设置一些选项

    
    
    CC= /usr/sfw/bin/gcc !! (this is needed to get newer GCC compiled, we will change it later)
    X11_TYPE= modular
    PKG_DEVELOPER=yes
    PKG_DEFAULT_OPTONS+=freetype truetype mmx subpixel official-mozilla-branding
    FETCH_USING=fetch

另外，在开始编译GCC6之前，我们还需要准备一些其他的东西…

现在我们可以使用本地bash

    
    
    # bash

让我们为shell设置额外的二进制文件路径（稍后你可以将其添加到你的配置文件中）

    
    
    # export PATH=/usr/sbin:/usr/bin:/usr/dt/bin:/usr/ucb:/usr/ccs/bin:/usr/sfw/bin

清除摘要工作目录并安装它

    
    
    # cd /usr/pkgsrc/pkgtools/digest
    # rm -rf .work
    # /usr/pkg/bin/bmake install clean clean-depends

如果在mk.conf中使用PKG_DEVELOPER = yes进行编译，那么首先构建perl，因为在包创建过程中会出现错误“perl
interpreter for Trace.pm not
existing”，因此对于perl，我们将在/usr/pkg/etc/mk.conf中将其更改为no as -> PKG_DEVELOPER=no。

    
    
    # cd /usr/pkgsrc/lang/perl5
    # /usr/pkg/bin/bmake install clean clean-depends

perl构建完成后，我们就可以在mk.conf中将其设置回PKG_DEVELOPER = yes并继续构建。

现在我们终于转到了GCC 6！

    
    
    # cd /usr/pkgsrc/lang/gcc6
    # /usr/pkg/bin/bmake install clean clean-depends

一旦我们编译了GCC6，就必须设置/usr/pkg/etc/mk.conf来使用新的CC和CXX变量，如下所示：

    
    
    CC=    /usr/pkg/gcc6/bin/gcc
    CXX=   /usr/pkg/gcc6/bin/g++

p.s
我将保持这部分开放，并在Solaris10上构建pkgsrc软件包时添加其他注释，你可以[在此处查看](https://astr0baby.wordpress.com/2019/07/29/pkgsrc-2019q2-on-solaris-1086/)更多详细信息。

现在我们将/usr/pkg/bin:/usr/pkg/sbin/usr/pkg/gcc6/bin/添加到我们的path中，因为我们有了一个新的工作编译器。

    
    
    # export PATH=/usr/sbin:/usr/bin:/usr/dt/bin:/usr/ccs/bin:/usr/pkg/bin:/usr/pkg/sbin:/usr/pkg/gcc6/bin
    # ln -s /usr/ccs/bin/ar /usr/bin/ar
    # ln -s /usr/ccs/bin/ranlib /usr/bin/ranlib

 **INFOSEC部分 - 在Solaris上测试一些0days！CVE-2019-2832**

我们可以使用最新的GCC6或旧版本GCC3，它们都可以正常工作。在本例中我使用的是本机的gcc
3.4.3，对于那些想要跳过gcc6编译步骤的人来说（需要花费很多时间）

我们现在将创建标准用户并设置密码

    
    
    # useradd -m -d /export/home/user user -s /usr/bin/bash
    # passwd user

并定义一些新的.profile变量，以便我们可以使用/usr/pkg，以user身份登录（或 # su – user）

一旦我们以user身份登录，就可以下载并构建Raptor的<https://twitter.com/0xdea> dtprintinfo
exploit。在Linux主机上你可以从这里下载exploit代码：<https://raw.githubusercontent.com/0xdea/exploits/master/solaris/raptor_dtprintname_intel.c>，并通过FTP上传到Solaris
10 VM

    
    
    $ wget https://raw.githubusercontent.com/0xdea/exploits/master/solaris/raptor_dtprintname_intel.c
    $ ftp 10.0.2.12 
    user Name (10.0.2.12:user): user
    331 Password required for user.
    Password:
    ftp> put raptor_dtprintname_intel.c

在Solaris 10 VM上，我们在DT会话中编译用户下的代码并运行。

    
    
    $ /usr/sfw/bin/gcc raptor_dtprintname_intel.c -o raptor_dtprintname_intel -Wall 
    $ ./raptor_dtprintinfo_intel 10.0.2.12:0

![8.png](https://image.3001.net/images/20190808/1565226198_5d4b74d6a0ed8.png!small)

但是出现一个错误，即Xlib连接到10.0.2.12:0.0被服务器拒绝（安装后的默认行为）所以让我们允许所有与X的通信连接，以root用户身份运行以授权/禁用远程主机的X11连接

    
    
    # xhost +    (this is to allow all to connect to X11; not a good idea) 
    # xhost -    (forbid all who are not authorized) 
    # xhost +10.0.2.12 (in our case this would be better, so only trusted hosts can connect to X11)

我们再次运行exploit代码，这次可以正常运行：）

![9.png](https://image.3001.net/images/20190808/1565226214_5d4b74e6724a0.png!small)

因此，现在我们可以从被利用的root
shell修复上述的CDE提权问题，即使我们没有来自Oracle的官方补丁（如果你很幸运并且可以访问Oracle的扩展用户支持，那么你可以像我们之前一样应用July-2019-CPU补丁）。

所需要的只是从/usr/dt/bin/dtprintinfo二进制文件中删除(S)etuid位。

    
    
    # chmod -s /usr/dt/bin/dtprintinfo

这一次显然exploit已不起作用了，因为它已进行了修补

![10.png](https://image.3001.net/images/20190808/1565226229_5d4b74f550f24.png!small)

如果你对上述bug感兴趣，你可以[在此处](https://lab.mediaservice.net/advisory/2019-01-cde-dtprintinfo.txt)获取更多相关信息。

最后，希望大家都能在本文中学习到一些东西。感谢阅读！

***参考来源：[astr0baby](https://astr0baby.wordpress.com/2019/07/28/solaris-10-x86-in-virtualbox-infosec-exercise-cve-2019-2832/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

