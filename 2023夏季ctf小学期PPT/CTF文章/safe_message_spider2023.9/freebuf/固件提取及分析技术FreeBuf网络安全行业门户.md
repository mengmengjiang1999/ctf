## 概念

固件（firmware）是一种写入硬件设备的软件，作用是对应用和各项系统功能实时控制。固件中包含底层代码，这些代码能实现软件对硬件的操作。运行固件的设备称为嵌入式系统，嵌入式系统的硬件资源在存储能力以及内存等方面往往具有诸多限制。举例来说，智能手机、智能终端、交通信号灯、无人机、机顶盒都是运行固件的嵌入式设备。

固件通常由bootloader、内核、根文件系统及其他资源组成。根据嵌入式linux、嵌入式windows（WinCE）、windowsIOT内核及各种实时操作系统（RTOS）的区别，固件也有多种类型。

下图是固件的组成，即闪存（或EEPROM）、bootlodaer、内核和根文件系统。

![](https://image.3001.net/images/20210129/1611902357_6013ad9505b51ce79fee0.png!small)

图1 固件基本构成

### bootloader

bootloader的作用主要包括RAM的初始化（存储易失性数据），串口初始化、设备类型检测、内核参数链表设置、initramfs（基于RAM的初始文件系统）加载及内核镜像调用等。Bootloader通过板机支持包（BSP）初始化硬件驱动。简单的说，bootloader和PC的BIOS在启动时的作用是一致的。ARM、MIPS架构架构中常见的bootloader包括redboot、u-boot及barebox等，本文主要对固件中的根文件分析技术进行阐述，涉及bootloader的部分不再赘述。在bootloader启动内核后，文件系统也就完成了加载过程。

### 根文件系统

根文件系统首先是内核启动时所mount的第一个文件系统，内核代码映像文件保存在根文件系统中，而系统引导启动程序会在根文件系统挂载之后从中把一些基本的初始化脚本和服务等加载到内存中去运行。

Linux根文件系统中一般有如下的几个目录：

/bin目录

该目录下的命令可以被root与一般账号所使用，由于这些命令在挂接其它文件系统之前就可以使用，所以/bin目录必须和根文件系统在同一个分区中。

/sbin 目录

该目录下存放系统命令，即只有系统管理员（俗称最高权限的root）能够使用的命令，系统命令还可以存放在/usr/sbin,/usr/local/sbin目录下，/sbin目录中存放的是基本的系统命令，它们用于启动系统和修复系统等，与/bin目录相似，在挂接其他文件系统之前就可以使用/sbin，所以/sbin目录必须和根文件系统在同一个分区中。

/dev目录

该目录下存放的是设备与设备接口的文件，设备文件是Linux中特有的文件类型，在Linux系统下，以文件的方式访问各种设备，即通过读写某个设备文件操作某个具体硬件。

/etc目录

该目录下存放着系统主要的配置文件，例如人员的账号密码文件、各种服务的其实文件等。一般来说，此目录的各文件属性是可以让一般用户查阅的，但是只有root有权限修改。

/lib目录

该目录下存放共享库和可加载（驱动程序），共享库用于启动系统。运行根文件系统中的可执行程序，比如：/bin /sbin 目录下的程序。

/root目录

系统管理员（root）的主文件夹，即是根用户的目录，与此对应，普通用户的目录是/home下的某个子目录。

/var目录

/var目录中存放可变的数据，比如spool目录（mail,news），log文件，临时文件。

/proc目录

这是一个空目录，常作为proc文件系统的挂接点，proc文件系统是个虚拟的文件系统，它没有实际的存储设备，里面的目录，文件都是由内核临时生成的，用来表示系统的运行状态，也可以操作其中的文件控制系统。

/mnt目录

用于临时挂载某个文件系统的挂接点，通常是空目录，也可以在里面创建一引起空的子目录，比如/mnt/cdram /mnt/hda1
。用来临时挂载光盘、移动存储设备等。

/tmp目录

用于存放临时文件，通常是空目录，一些需要生成临时文件的程序用到的/tmp目录下，所以/tmp目录必须存在并可以访问。

对于嵌入式Linux系统的根文件系统来说，一般可能没有上面所列出的那么复杂，比如嵌入式系统通常都不是针对多用户的，所以/home这个目录在一般嵌入式Linux中可能就很少用到，而/boot这个目录则取决于你所使用的BootLoader是否能够重新获得内核映象从你的根文件系统在内核启动之前。一般说来，只有/bin，/dev，/etc，/lib，/proc，/var，/usr这些需要的，而其他都是可选的。

固件可以采用的文件类型有很多种，常见的有squashfs【1】、cramfs、ext2、jeffs2等。其中设备（尤其是消费级电子设备）最常采用的文件系统是squashfs，分析人员可以使用unsqushfs工具对文件系统提取数据。需要注意的时，有些厂商采用了非标准的squasgfs压缩算法，如LZMA和XZ。本文中以某路由潘多拉固件为模型，对该固件进行提取和分析，关于本固件的文件系统和压缩算法如下所示：

![](https://image.3001.net/images/20210129/1611904594_6013b652966fb9a4bbc05.png!small)

图2 固件文件系统及压缩算法（放大观看细节）

该固件文件即为squashfs文件系统，并使用LZMA和XZ压缩算法。

【1】注：SquashFS是基于Linux内核使用的压缩只读文件系统。该文件系统能够压缩系统内的文档,inode以及目录，文件最大支持2^64字节。每一个文件都有对应的inode，里面包含了与该文件有关的一些信息。inode包含文件的元信息，具体来说有Size
文件的字节数、Uid 文件拥有者的User ID、Gid 文件的Group ID、Access
文件的读写执行权限等。linux可以用stat命令，查看某个文件的inode信息。

对squashsf文件系统的解压、提取，需要借助sasquatch工具，可从<https://github.com/devttys0/sasquatch>下载安装。

如果sasquatch工具不起作用，也可以使用7-zip对后缀为squashsf的文件进行提取（推荐本方式）。

从分析角度出发，可以把文件系统看作存储配置文件、服务、账号口令、哈希、应用程序代码及启动脚本的地方。

### 关于固件研究的范围

从广义上讲，固件分为两种形式，第一种，对于独立可操作的电子产品，固件一般指它的操作系统（担任着一个数码产品最基础、最底层工作的软件才可以称之为固件，这和操作系统的定义很一致）。比如交换机的固件，就是指交换机的操作系统。同理，IPHONE的固件也是其操作系统，路由器的固件就是路由器的操作系统，MP4的固件就是MP4的操作系统等。

第二种，而对于非独立的电子产品，比如硬盘、鼠标、BIOS、光驱、U盘等设备，固件就是指其最底层的，让设备得以运行的程序代码。

本文阐述的范围限定于第一种形式。

## 固件的提取与分析

### 根文件识别与提取

通常固件文件以bin、zip、LZMA、arj等文件压缩类型封装，其中，最常见的为bin和zip格式，bin文件是二进制镜像形式，需要使用binwalk提取squashsf文件系统。

以下为典型的二进制镜像提取文件系统的例程：

    
    
    [root@localhost dm203]# binwalk -e PandoraBox.bin
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    
    --------------------------------------------------------------------------------    
    0             0x0             uImage header, header size: 64 bytes, header CRC: 0x2E8A7ACF, created: 2019-01-01 09:25:02, image size: 1452817 bytes, Data Address: 0x80000000, Entry Point: 0x80000000, data CRC: 0x9C0D7442, OS: Linux, CPU: MIPS, image type: OS Kernel Image, compression type: lzma, image name: "MIPS PandoraBox Linux-3.14.79"
    
    64            0x40            LZMA compressed data, properties: 0x6D, dictionary size: 8388608 bytes, uncompressed size: 4577808 bytes
    
    WARNING: Extractor.execute failed to run external extractor 'sasquatch -p 1 -le -d 'squashfs-root' '%e'': [Errno 2] No such file or directory, 'sasquatch -p 1 -le -d 'squashfs-root' '%e'' might not be installed correctly
    
    WARNING: Extractor.execute failed to run external extractor 'sasquatch -p 1 -be -d 'squashfs-root' '%e'': [Errno 2] No such file or directory, 'sasquatch -p 1 -be -d 'squashfs-root' '%e'' might not be installed correctly
    
    1453905       0x162F51        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 7132962 bytes, 2102 inodes, blocksize: 262144 bytes, created: 2018-12-31 13:03:10
    
    [root@localhost _PandoraBox.bin.extracted]# ls
    
    162F51.squashfs  40  40.7z  squashfs-root

对于bin文件来说，可能未必是二进制镜像文件，也可能是数据文件，首先要对文件进行识别，可以借助linux下的file命令，如下所示：

    
    
    [root@localhost dm203]# file PandoraBox.bin
    
    PandoraBox.bin: u-boot legacy uImage, MIPS PandoraBox Linux-3.14.79, Linux/MIPS, OS Kernel Image (lzma), 1452817 bytes, Tue Jan  1 17:25:02 2019, Load Address: 0x80000000, Entry Point: 0x80000000, Header CRC: 0x2E8A7ACF, Data CRC: 0x9C0D7442

这是一个嵌入式linux/MIPS架构的镜像文件，可以使用binwalk提取出squashsf后缀文件（有时也可能是其他后缀）。

对提取出的文件系统可以借助hexdump及grep进一步确认：

    
    
    [root@localhost _PandoraBox.bin.extracted]# hexdump -C 162F51.squashfs |grep -i 'hsqs'
    
    68 73 71 73 36 08 00 00 8e 13 2a 5c 00 00 04 00  |hsqs6.....*\....|

如上所示，地址00包含squashsf的头部特征【2】。

通过对bin文件的提取，获得了后缀为squashfs的固件文件，该文件需要进一步解压，从而获得固件的根文件（本例为7-zip方式提取）。

![](https://image.3001.net/images/20210129/1611904762_6013b6fab9719a378e607.png!small)

图3 提取的根文件系统

【2】注：squashsf文件系统的头部特征已知的有七种：标准固件大端sqsh、标准固件小端hsqs、LZMA压缩的大端sqlz、squashfs3.3在LZMA压缩下的大端qshs部分非标准小端shsq（D-LINK固件）、DD-WRT固件小端hsqt、DD-WRT固件大端tqsh。

下面为Dlink
DWR-932B路由器固件（下载地址https://media.dlink.eu/ftp/products/dwr/dwr-932/driver_software/DWR-932_fw_revB_2_02_eu_en_20150709.zip）的提取实例，该固件中存在大量的安全漏洞，包括后门、后门账号、弱WPS、以及远程代码执行漏洞等等。

DWR-932_fw_revB_2_02_eu_en_20150709.zip是经过加密的压缩包，无法直接解压缩，这是厂商对固件做了保护，防止逆向分析。使用frackzip工具可以破解该zip密码，这里直接给出该压缩包的密码：beUT9Z。

解压后得到另一个40.zip的压缩包，继续对40.zip解压，获得下列文件：

![](https://image.3001.net/images/20210129/1611904700_6013b6bc9fb3e30e7849a.png!small)

图4 932b固件镜像文件

其中，后缀为yaffs2的文件就是包含932b固件根文件的镜像。这里顺带说一下yaffs文件系统，Yaffs(Yet Another FlashFile
System)文件系统是专门针对NAND闪存设计的嵌入式文件系统，目前有YAFFS和YAFFS2两个版本，两个版本的主要区别之一在于YAFFS2能够更好的支持大容量的NAND
FLASH芯片。

尝试对yaffs2文件提取，首先使用的是binwalk，但无法提取出根文件系统（见如下提取过程）：

    
    
    [root@localhost 40]# binwalk -e  2K-mdm9625-usr-image.usrfs.yaffs2
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    
    --------------------------------------------------------------------------------    
    WARNING: Extractor.execute failed to run external extractor 'yaffshiv --auto --brute-force -f '%e' -d 'yaffs-root'': [Errno 2] No such file or directory, 'yaffshiv --auto --brute-force -f '%e' -d 'yaffs-root'' might not be installed correctly
    
    0             0x0             YAFFS filesystem, little endian
    
    6336          0x18C0          ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    284836        0x458A4         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    291456        0x47280         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    339328        0x52D80         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    346368        0x54900         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    359040        0x57A80         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    383404        0x5D9AC         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    388608        0x5EE00         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    389367        0x5F0F7         mcrypt 2.2 encrypted data, algorithm: blowfish-448, mode: CBC, keymode: 8bit
    
    403392        0x627C0         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    433596        0x69DBC         Unix path: /usr/lib/xtables
    
    438592        0x6B140         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    445632        0x6CCC0         ELF, 32-bit LSB shared object, ARM, version 1 (SYSV)
    
    1196884       0x124354        Unix path: /usr/lib/gio/modules
    
    1210088       0x1276E8        PEM RSA private key
    
    1210292       0x1277B4        PEM certificate
    
    1230336       0x12C600        XML document, version: "1.0"
    
    1245430       0x1300F6        Unix path: /var/run/dbus/system_bus_socket
    
    1267812       0x135864        Unix path: /var/lib/dbus/machine-id
    
    ………………………………………………………………………………………………….
    
    [root@localhost _2K-mdm9625-usr-image.usrfs.yaffs2.extracted]# ls
    
    0.yaffs  194E86A.zlib  195F07C.zlib  1968A0E.zlib  196B67C.zlib  196C740.zlib  19705CE.zlib  197533C.zlib  19763BC.zlib  197710E.zlib  197818E.zlib  197AACE.zlib
    
    194E86A  195F07C       1968A0E       196B67C       196C740       19705CE       197533C       19763BC       197710E       197818E       197AACE

显然提取后的文件夹中并非根文件系统，查阅资料后，了解到932b采用了yaffs的原生态压缩算法，需要使用工具unyaffs提取。

![](https://image.3001.net/images/20210129/1611904793_6013b719ba3e109ab8975.png!small)

图5 提取932B根文件系统

将镜像文件提取到yaffs2-root目录，获得完整的932B根文件系统。

### 固件分析

固件的分析可以采用人工或工具方式进行。本文介绍其中的三种分析方法：

文件分析

文件分析方法是通过对根文件系统进行遍历，以此发现存在安全隐患的文件或配置信息。以D-LINK固件DWR
932B为例，通过遍历.conf文件，在inadyn-mt.conf文件（用于dyndns客户端）中存储了路由器no-IP配置信息，其中包含了了用于访问网站<https://www.no-ip.com>的用户名和硬编码口令。

    
    
    --log_file /usr/inadyn_srv.log
    
    --forced_update_period 6000
    
    --username alex_hung
    
    --password 641021
    
    --dyndns_system default@no-ip.com
    
    --alias test.no-ip.com

熵分析

熵分析用以分析二进制固件文件的加密情况，常用工具是binwalk -E，推荐使用另一种熵分析在线工具：<https://binvis.io/#/>

![](https://image.3001.net/images/20210129/1611904825_6013b73952a23d25496d4.png!small)

图6 熵分析在线工具binbis.io

下图是某固件文件的熵分析结果：

![](https://image.3001.net/images/20210129/1611904841_6013b749ebd32f5f1e292.png!small)

图7 熵分析实例

视图左侧色块区域中，黑色部分代表0x00字节，绿色部分为低地址，蓝色部分为ASCII码，红色部分为高地址，该分析方式下依据数据位的连续曲线变化对加密特征进行分析。

脚本分析

常用脚本工具是firmwalker，可以自动化遍历固件文件系统中的所有敏感文件内容。使用效果如下（需指定固件根文件系统路径）：

    
    
    [root@localhost firmwalker]# ./firmwalker.sh /tmp/dm203/_DWR-932_B.zip.extracted/40/yaffs2-root/
    
    ***Firmware Directory***
    
    /tmp/dm203/_DWR-932_B.zip.extracted/40/yaffs2-root/
    
    ***Search for password files***
    
    ##################################### passwd
    
    /bin/passwd
    
    /var/lib/opkg/alternatives/passwd
    
    /etc/passwd
    
    ##################################### shadow
    
    /etc/shadow
    
    ##################################### *.psk
    
    ***Search for Unix-MD5 hashes***
    
    ***Search for SSL related files***
    
    ##################################### *.crt
    
    ##################################### *.pem
    
    ##################################### *.cer
    
    ##################################### *.p7b
    
    ##################################### *.p12
    
    ##################################### *.key
    
    ***Search for files***
    
    ##################################### *.conf
    
    /etc/host.conf
    
    /etc/inadyn-mt.conf
    
    -------------------- password --------------------    
    /disk/internal-storage.iso
    
    /bin/appmgr
    
    /var/lib/opkg/info/shadow.control
    
    /WEBSERVER/www/QCMAP_Account.html
    
    /etc/tr069/igd_10.xml
    
    /etc/inadyn-mt.conf
    
    ………………………………………………………………

该脚本工具会自动对.conf、.key、.bin、.sh及shadow、passwd等文件进行遍历，收集敏感文件信息，当然，具体分析工作依然是人工完成。

## 固件文件系统提取基本原理

提取固件二进制镜像中的根文件系统，是对固件进行分析的前提条件，以binwalk提取固件文件系统为例，通过binwalk的魔法数【3】特征库，对固件文件初始位置的特征码进行匹配，并将起始地址为开头的整段数据dump下来。

本文 中对某路由潘多拉固件进行文件系统的识别，如下所示：

    
    
    [root@localhost dm203]# binwalk  PandoraBox.bin
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    
    --------------------------------------------------------------------------------    
    0             0x0             uImage header, header size: 64 bytes, header CRC: 0x2E8A7ACF, created: 2019-01-01 09:25:02, image size: 1452817 bytes, Data Address: 0x80000000, Entry Point: 0x80000000, data CRC: 0x9C0D7442, OS: Linux, CPU: MIPS, image type: OS Kernel Image, compression type: lzma, image name: "MIPS PandoraBox Linux-3.14.79"
    
    64            0x40            LZMA compressed data, properties: 0x6D, dictionary size: 8388608 bytes, uncompressed size: 4577808 bytes
    
    1453905       0x162F51        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 7132962 bytes, 2102 inodes, blocksize: 262144 bytes, created: 2018-12-31 13:03:10
    
    [root@localhost _PandoraBox.bin.extracted]# hexdump -C 162F51.squashfs |grep -i 'hsqs'
    
    68 73 71 73 36 08 00 00 8e 13 2a 5c 00 00 04 00  |hsqs6.....*\....|

由上可知，固件二进制镜像文件中，根文件系统起始地址为0x162F51开始到其后的7132962个字节（实际有效为7197026个字节），只需要dump出这个范围的内容，就可以获得二进制镜像文件内的根文件系统。

    
    
    [root@localhost dm203]# dd if=PandoraBox.bin bs=1 skip=1453905 of=pandora

记录了7197026+0 的读入

记录了7197026+0 的写出

7197026字节(7.2 MB)已复制，6.56635 秒，1.1 MB/秒

    
    
    [root@localhost dm203]# ls
    
    DWR-932_B.zip  _DWR-932_B.zip.extracted  eeprom.bin  pandora  PandoraBox.bin  _PandoraBox.bin.extracted  SmartGateway1.0.78.bin
    
    [root@localhost dm203]# unsquashfs pandora
    
    Parallel unsquashfs: Using 8 processors
    
    1951 inodes (1984 blocks) to write
    
    [================================================================================================================================================================================================/] 1984/1984 100%
    
    created 1671 files
    
    created 153 directories
    
    created 277 symlinks
    
    created 1 devices
    
    created 0 fifos
    
    [root@localhost dm203]# ls
    
    DWR-932_B.zip  _DWR-932_B.zip.extracted  eeprom.bin  pandora  PandoraBox.bin  _PandoraBox.bin.extracted  SmartGateway1.0.78.bin  squashfs-root
    
    [root@localhost dm203]# cd squashfs-root/
    
    [root@localhost squashfs-root]# ls
    
    bin  dev  etc  etc_ro  init  lib  mnt  overlay  proc  rom  root  sbin  sys  tmp  usr  var  www

如上所示，成功提取出了PandoraBox.bin二进制镜像内的根文件系统。同理，如果能获得已知固件二进制镜像文件的头部信息及魔法值，了解根文件系统的压缩算法，就可以提取出二进制镜像内的根文件系统。

作为参照，查询binwalk魔法数特征库，得到以下信息：

    
    
    # Squashfs, little endian
    
    0       string  hsqs    Squashfs filesystem, little endian,
    
    >28     leshort >10     {invalid}
    
    >28     leshort <1      {invalid}
    
    >30     leshort >10     {invalid}
    
    >28     leshort x       version %d.
    
    >30     leshort x       \b%d,
    
    >28     leshort >3      compression:
    
    >>20    leshort 1       \bgzip,
    
    >>20    leshort 2       \blzma,
    
    >>20    leshort 3       \bgzip (non-standard type definition),
    
    >>20    leshort 4       \bxz,
    
    >>20    leshort 0       \b{invalid},
    
    >>20    leshort >4      \b{invalid},
    
    >28     leshort <3
    
    >>8     lelong  x       size: %d bytes,
    
    >>8     lelong  x       {size:%d}
    
    >28     leshort 3
    
    >>63    lequad  x       size: %ld bytes,
    
    >>63    lequad  x       {size:%ld}
    
    >28     leshort >3
    
    >>40    lequad  x       size: %ld bytes,
    
    >>40    lequad  x       {size:%ld}
    
    >4      lelong  x       %d inodes,
    
    >28     leshort >3
    
    >>12    lelong  x       blocksize: %d bytes,
    
    >28     leshort <2
    
    >>32    leshort x       blocksize: %d bytes,
    
    >28     leshort 2
    
    >>51    lelong  x       blocksize: %d bytes,
    
    >28     leshort 3
    
    >>51    lelong  x       blocksize: %d bytes,
    
    >28     leshort <4
    
    >>39    ledate  x       created: %s
    
    >28     leshort >3
    
    >>8     ledate  x       created: %s
    
    >28     leshort <3
    
    >>8     lelong  x       {jump:%d}
    
    >28     leshort 3
    
    >>63    lequad  x       {jump:%ld}
    
    >28     leshort >3
    
    >>40    lequad  x       {jump:%ld}

由binwalk提取出的162F51.squashfs是一个标准Squashfs小端系统（LITTLE-ENDIAN,
即低位字节排放在内存的低地址端，高位字节排放在内存的高地址端），特征码为hsqs。

两种方法是殊途同归，原理并无二致。

【3】注：魔法数指文件的最开头的几个用于唯一区别其它文件类型的字节，有了这些魔法数，就可以区别不同的文件。

Binwalk支持的固件文件系统及相关特征码参见：

<https://github.com/ReFirmLabs/binwalk/blob/62e9caa164305a18d7d1f037ab27d14ac933d3cf/src/binwalk/magic/filesystems>

## 关于固件提取与分析的意义

5G、物联网、工业互联网、智能制造、智能家居…当下信息技术几大热门领域，都在显著扩大一个攻击面：固件安全。

固件是物联网设备的关键组成部分，固件决定了物联网设备的功能与性能，如果固件出现安全漏洞，就会对该物联网设备的使用带来严重的安全隐患，物联网固件安全也正因此而变得至关重要。

固件通常写入设备底层，直接驱动物联网设备，不像应用软件，可以被基础安全软件轻松地访问或扫描。固件本身有一定的封闭性，各个设备厂商采用的文件系统各不相同，生成二进制镜像文件时也可能使用了非标准的压缩算法，甚至对固件进行加密。

正是基于上述原因，目前固件扫描装置或平台而言，存在无法识别和提取出固件文件系统的问题，对于固件的扫描成功率很低。解决这一问题的根本，是建立固件文件特征库，通过收集不同固件的魔法值、文件头、文件系统特征、压缩算法、文件系统结构等信息，尽可能充实以上类型的数据，是有效提高自动化扫描成功率的根本。

