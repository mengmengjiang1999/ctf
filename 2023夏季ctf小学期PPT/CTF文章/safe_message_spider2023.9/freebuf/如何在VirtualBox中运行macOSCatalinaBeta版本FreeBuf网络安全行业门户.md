**本内容是关于如何在Linux上的VirtualBox中运行macOS Catalina Beta版的简短指南。**

**![1.png](https://image.3001.net/images/20190721/1563672600_5d33c01820557.png!small)**

在开始之前你需要做以下准备：

> Linux x86_64（我使用的是Mint 19.1）英特尔酷睿CPU，不少于8 GB的内存和一个不错的快速固态硬盘
>
> VirtualBox（版本为6.0.8）
>
> macOS Catalina install ISO（vanilla）
>
> Clover.iso
>
> 额外的USB鼠标（用于VirtualBox中的USB pass-through）

我已经为1280×1024分辨率准备了Clover，包括SIP启用或SIP禁用版本，并且整个操作过程都是关于在1280×1024中运行Catalina的（如果你想更改它，请参阅此处有关自定义Clover的文章
- ><https://astr0baby.wordpress.com/2019/01/19/customizing-the-clover-iso-mojave-loader/>

 **SIP-Enabled 1280×1024 Clover.iso 可以在这里下载到** ->
<https://mega.nz/#!S4MAhQoZ!nrAKce_AFhxZLm21sIjwHFpeFw6dW7Salpvs50tywYg>

**SIP-Disabled 1280×1024 Clover.iso 可以在这里下载到** ->
<https://mega.nz/#!upc21CaT!wCUnzknVODKmbwrC6NCH4engMKU7YpMyn9ezguwwx4A>

**Catalina-Beta iso 可以在这里下载到** -> <https://gofile.io/?c=MmX49O>

下载完这些文件后，让我们准备VirtualBox
Catalina环境。首先，我们需要创建一个设置如下的新VM；请确保使用的VDI磁盘足够大，最好不低于50GB并按照以下说明操作。

![2.png](https://image.3001.net/images/20190721/1563672623_5d33c02fbd0cf.png!small)

![3.png](https://image.3001.net/images/20190721/1563672651_5d33c04b3479d.png!small)![4.png](https://image.3001.net/images/20190721/1563672651_5d33c04b2d4a2.png!small)![5.png](https://image.3001.net/images/20190721/1563672651_5d33c04b37cd6.png!small)![6.png](https://image.3001.net/images/20190721/1563672651_5d33c04b8b297.png!small)

![7.png](https://image.3001.net/images/20190721/1563672686_5d33c06ec8502.png!small)

我为我的虚拟机和单独的VLAN使用静态IP，你也可以根据自己的喜好进行更改，下面包含的网络脚本需要在VM启动之前执行，并且仅在vboxnet0接口被加载时执行！（通常是在你启动VirtualBox之后）

![8.png](https://image.3001.net/images/20190721/1563672704_5d33c0802592d.png!small)

这里我们使用一个小技巧来修复“cannot move windows in Catalina
VM”这个问题，如果你只使用本地VirtualBox鼠标，那么我们将插入一个真正的辅助USB鼠标，并将其添加到USB设备筛选器，以便VM可以直接使用它。

创建Catalina VirtualBox环境后（请确保你已按照以上截图进行设置，否则它将无法工作）我们将以下的Shell脚本应用于VirtualBox
Catalina Guest（将其另存为catalina.sh，chmod +x 并执行它）。

    
    
    #!/bin/bash
    readonly VM_RES="1280x1024"
    readonly NAME="Catalina"
    
    VBoxManage modifyvm "$NAME" --usbxhci on --firmware efi --chipset ich9 --mouse usbtablet --keyboard usb
    VBoxManage setextradata "$NAME" "CustomVideoMode1" "${VM_RES}x32"
    VBoxManage setextradata "$NAME" VBoxInternal2/EfiGraphicsResolution "$VM_RES"
    VBoxManage modifyvm "$NAME" --cpuidset 00000001 000106e5 00100800 0098e3fd bfebfbff
    VBoxManage setextradata "$NAME" "VBoxInternal/Devices/efi/0/Config/DmiSystemProduct" "iMac11,3"
    VBoxManage setextradata "$NAME" "VBoxInternal/Devices/efi/0/Config/DmiSystemVersion" "1.0"
    VBoxManage setextradata "$NAME" "VBoxInternal/Devices/efi/0/Config/DmiBoardProduct" "Iloveapple"
    VBoxManage setextradata "$NAME" "VBoxInternal/Devices/smc/0/Config/DeviceKey" "ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
    VBoxManage setextradata "$NAME" "VBoxInternal/Devices/smc/0/Config/GetKeyFromRealSMC" 1
    

NETWORK：

这是我使用的网络脚本（你可以根据你的需要进行调整）你将需要uml-utilities和bridge-utils（在Debian/Ubuntu上运行 sudo
apt-get install uml-utilities bridge-utils）

    
    
    #Setup tap and bridge 
    tunctl -t tap0 -u user
    ifconfig tap0 up
    brctl addbr br0
    brctl setfd br0 0
    ifconfig enp0s25 10.0.2.1 up 
    ifconfig br0 10.0.2.2 netmask 255.255.255.0 broadcast 10.0.2.255 up
    brctl addif br0 tap0 vboxnet0 
    ifconfig tap0 0.0.0.0
    sysctl net.ipv4.ip_forward=1
    iptables --table nat -A POSTROUTING --out-interface wlan0 -j MASQUERADE

接下来，我们将通过VirtualBox正常启动Catalina.iso，并进入第一阶段macO
installer，擦除磁盘创建APFS分区并安装。这与之前的Mojave安装完全相同（你可以在[此处](https://astr0baby.wordpress.com/2018/09/25/running-macos-mojave-10-14-on-virtualbox-5-2-18-on-linux-x86_64/)查看详细信息）

![9.png](https://image.3001.net/images/20190721/1563672748_5d33c0ac0d5d7.png!small)

这一阶段大约需要5-10分钟的时间才能完成，系统将自动重启，等待它完成循环，当它再次回到同一安装程序时，只需关闭VM并将ISO从Catalina.iso替换为我们之前下载的Clover.iso。这步是必需的，因为新的驱动器用的是APFS分区，而当前的VirtualBox
UEFI看不到它，所以每次在VirtualBox中运行Catalina时都必须使用它作为引导加载程序。

接下来，我们再次启动Catalina并选择安装程序分区（Installer partition）（移动方向键 - 鼠标在这里不起作用）并确认。

这个阶段将花费更长的时间（在一个好的固态硬盘上大约需要30分钟）。一旦完成，系统将自动重启（如果它被卡住，只需硬重置并再次重启即可）

我们再次从VirtualBox启动Catalina（如果你在屏幕上看到错误提示，关闭VM并重启即可，偶尔会发生这种情况）并等待最终用户设置等。

使用以下设置进行网络连接（你也可以根据实际情况进行相应的更改）

    
    
    IP 10.0.2.12   NetMask  255.255.255.0  GW: 10.0.2.2  DNS 8.8.8.8

![10.png](https://image.3001.net/images/20190721/1563672767_5d33c0bfb12d2.png!small)

现在，你会发现在Catalina guest中有两个鼠标可用，使用我们在VirtualBox USB Pass-through中选择的USB鼠标

P.S
在缩放模式下，Clover菜单由于某种原因无法正常工作，并且无法移动方向键来选择启动，因此在启动Catalina时不要使用缩放模式，你可以在启动后立即将其更改为缩放模式）

如要对系统进行更新升级，你只需在下次macOS获得系统更新时，选择Clover中的安装程序分区即可，这个过程同样需要花费一些时间才能完成。截至目前，可以看到已经发布了第3个Beta版
<https://developer.apple.com/news/releases/?id=07022019e>

![11.png](https://image.3001.net/images/20190721/1563672784_5d33c0d0f2b91.png!small)

***参考来源：[astr0baby](https://astr0baby.wordpress.com/2019/07/04/running-macos-catalina-beta-on-virtualbox-linux/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

