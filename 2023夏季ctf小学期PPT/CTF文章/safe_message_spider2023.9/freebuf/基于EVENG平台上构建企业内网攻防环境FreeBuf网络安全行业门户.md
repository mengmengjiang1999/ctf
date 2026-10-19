**EVE-NG（全称EmulatedVirtual
Environment），这款模拟器已经不仅可以模拟网络设备，也可以运行一切虚拟机。理论上，只要能将虚拟机的虚拟磁盘格式转换为qcow2都可以在EVE-NG上运行。所以，EVE-NG可以算打造成最佳的网络安全攻防虚拟环境。**

EVE-NG在交互模式上采用linux内核结合PHP的WEB页面操作模式，EVE-NG像是BS模型，EVE-NG是服务端，用户端可以是支持http/https的任意OS。特别适合部署在企业内网，供网络安全从业人员做攻防演练和部分模拟内网渗透环境。

通过以下连接 <http://eve-ng.net/downloads/eve-ng-2> 登陆EVE-NG的下载网站，然后找到OVA镜像下载链接。![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951106_5cebb4c2c1127.png!small)

可以下载一个OVA的镜像，这个镜像可以直接导入到vmware workstation中。![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951127_5cebb4d728fc9.png!small)

VMware 分配给 EVE-NG 的 4 个 CPU，6GB 内存当作物理资源

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951157_5cebb4f5d9bcd.png!small)虚拟机设置参数考虑因素：

>  **内存：** EVE-NG 底层是用 KVM 运行Windows， ISE 等等这些虚拟机，内存消耗比较多，物理内存和虚拟内存占比基本上
> 1：1。内存不足时，KVM 就会做内存交换，会拖慢 EVE-NG 的运行速度。
>
>  **CPU：** KVM 允许 CPU 过载使用，即虚拟 CPU 总数大于物理 CPU 总数的，比如 4 个 CPU，可以虚出来 8 个，甚至 16
> 个 KVM 的 vCPU。具体的物理 CPU 与 vCPU 的极限比例是多少，取决于物理 CPU 的单线程性能强弱，单线程性能太弱。
>
>  **硬盘：** 硬盘大小决定着可以存放的 KVM 虚拟机镜像数量，比如一个 Win-7.qcow2 镜像文件大小 4GB+，一个
> PaloAlto.qcow2 大小 2GB+ 等等。实验环境中的虚拟设备占用容量非常小，属于增量存储，只保存改动的部分。
>
>  **网络适配器：** 不重要，这个决定着您可以桥接的数量。也可以将虚拟环境桥接到物理设备上。

然后开启虚拟机，会看到欢迎初始化页面

![4.pn基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951231_5cebb53f9cccf.png!small)

输入用户名：root，密码：eve 登录后提示您修改密码

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951239_5cebb5475f5ff.png!small)

[ ](http://www.emulatedlab.com/wp-content/uploads/2017/06/2017072602251390.jpg)

输入 hostname，默认即可。可以根据您的需要修改。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951245_5cebb54de85c8.png!small)![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951349_5cebb5b5db76a.png!small)

[ ](http://www.emulatedlab.com/wp-content/uploads/2017/06/2017072602251548.jpg)

[ ](http://www.emulatedlab.com/wp-content/uploads/2017/06/2017072602251623.jpg)

修改 IP 地址

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951363_5cebb5c3b7977.png!small)

[ ](http://www.emulatedlab.com/wp-content/uploads/2017/06/201707260225171.jpg)

设置 NTP 服务器，pool.ntp.org 是默认的 NTP Server，改成别的 NTP 服务器也 OK。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951373_5cebb5cd3efbe.png!small)

[ ](http://www.emulatedlab.com/wp-content/uploads/2017/06/2017072602251814.jpg)

选择连入 Internet 的方式，默认 direct connection 即可。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951383_5cebb5d7963cb.png!small)

[ ](http://www.emulatedlab.com/wp-content/uploads/2017/06/2017072602251982.jpg)

确认 OK 后，系统自动重启并应用您上述的配置。

系统建议采用火狐浏览器，因为后续登陆中Native mode可能需要在选项中关联应用（只有natice模式支持wireshark抓包）。

Vmware中会提示EVE-NG的web浏览地址，直接用火狐浏览器敲入 http:// 本地产生的IP地址 就可以访问。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951418_5cebb5fa45745.png!small)![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951432_5cebb60829806.png!small)

输入登陆web登陆用户名：admin，密码：eve，然后选择Html5的模式，这种方式比较便捷，因为不需要在PC上安装putty，vnc等终端软件，可以在html5的页面上完成配置。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951450_5cebb61ad29e8.png!small)

左侧为功能菜单，可以添加设备，网络，注释，图片和攻防网络和设备版本和架构描述。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951470_5cebb62e08ec4.png!small)

现在选择添加一个设备后，所有可选的设备均为灰色，为没有设备镜像状态不可选。这个时候需要下载qemu的设备镜像文件。

镜像文件可以访问 <http://eve-ng.cn> 获取下载！

下载后可以采用winscp这个工具，远程登陆EVE-NG的虚拟机，输入用户名和密码后，把下载的镜像文件上传到EVE-NG中。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951488_5cebb64055447.png!small)![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951498_5cebb64ae7ea7.png!small)

上传的目录为：/opt/unetlab/addons/qemu，把下载的RAR镜像文件解压为文件夹格式，直接拖入就可以了。对于如果想把自己的qemu虚拟镜像上传到这个攻防环境中，可以采用直接修改文件名为had.qcow2格式，放入文件夹内替换就可以了。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951516_5cebb65c5a9c2.png!small)

现在可以添加一个Node 设备，可以在下拉菜单里看到支持的设备，添加一个思科防火墙。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951534_5cebb66e7fd9f.png!small)

然后选择一个ASAv的虚拟防火墙，IOS版本为K9系列，可以自定义防火墙设备名字，镜像文件和图标以及CPU的核数，内存的大小和接口的个数，其他参数不要动。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951553_5cebb681c1800.png!small)

参数填写好后，workspace中会出现一个思科防火墙，右键可以启动，关闭，清除配置，编辑和删除等选项。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951574_5cebb696c79b7.png!small)

当启动后图标会变成蓝色的图标，同时双击后会产生另外一个html5的窗口，在窗口里可以看到标准的IOS的CLI命令行，敲入show
version的时候，可以看到防火墙的版本为9.62。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951603_5cebb6b34b39c.png!small)

此平台主要是模拟企业内网，所以需要添加服务器和客户机，这里添加一个windows
server2008的镜像，然后启动起来。双击后可以在html5浏览器的页面里看到桌面，网络安全攻防人员可以在此设置域控，NPS等安全策略，模拟企业内网的运维策略。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951628_5cebb6cc65ba6.png!small)

右侧添加网络后，选择cloud模式，这里可以选择cloud1，这里1是指你的vmware虚拟化里的增加的第二块网卡，渗透内网人员可以通过另外一个虚拟机启动kali环境，然后网卡选择桥接到EVE-NG虚拟机的虚拟网卡上，就可以代表你的渗透通道已经打通。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951652_5cebb6e405ab2.png!small)

Vmware里设置一个vnet8，分配了DHCP从192.16.0.0/24网段，kali的虚拟机网卡桥接到vnet8然后内部设置为dhcp，获得动态IP为192.16.0.128，而EVE-NG的环境增加一个网卡桥接到vnet8上，部署的windows server
2008桥接到cloud1上网卡设置为DHCP，自动获取IP的192.16.0.130，可以看到相互ping到。

![基于EVE-NG平台上构建企业内网攻防环境](https://image.3001.net/images/20190527/1558951663_5cebb6efaf27e.png!small)  

然后设置企业内网攻防网络架构，模拟企业内网的服务器和网络设备，可以完全再现网络安全攻防过程，同时EVE-NG可以多人登陆设置和维护。

### 附录：EVE-NG支持的镜像

> Cisco ACS 5.6, 5.8.1.4
>
> Cisco ISE 1.2, 1.4
>
> Cisco ISE 2.1
>
> Cisco ASA 8.0.2 (Singe and Multi Context)
>
> Cisco ASA 8.4 Multicontext Support
>
> Cisco ASA 9.1.5 Multicontext Support
>
> Cisco ASAv 9.6.2, 9.7.1 or earlier
>
> Cisco IPS 7.1
>
> Cisco Firepower 6.1, 6.2 Management centre (FMC)
>
> Cisco Firepower 6.1, 6.2 Treat defence ASAv (FTD)
>
> Cisco Firepower 6.1, 6.2 NGIPSv
>
> Cisco Firepower 5.4 (NGIPS, FMC)
>
> Cisco CSR 3.16, 3,17
>
> Cisco CSR 16.03 Denali
>
> Cisco CSR 16.0.4 Everest
>
> Cisco vIOS L3 15.5, 15.6.2T
>
> Cisco vIOS L2 15.2
>
> Cisco ESA 9.7, 9.8, Email Security Appliance
>
> Cisco WSA 8.6, 9.2 10.0 Web Security Appliance
>
> Cisco CDA 1.0 Context Delivery Agent
>
> CiscoNXOS Titanium 7.1.0.3
>
> Cisco NXOSk9 (require source of 2xCPU and 8G RAM for single node)
>
> Cisco XRv 5.2.2, 5.3.2, 6.0.1, 6.0.2
>
> Cisco XRvK9 6.0.1, 6.1.2 (require source of 4xCPU and 16G RAM for
> singlenode)
>
> Cisco vWLC, 7.4. 8.0.100, 8.2.X, 8.3.X
>
> Cisco vNAM Virtual Network Analysis Module 6.2.x
>
> Cisco vWAAS 200.5.5
>
> Cisco CUCM 11.5.1.11900-26
>
> Juniper vSRX 12.1.47D
>
> Juniper Olive M series
>
> Juniper vSRX NG 15.1×49-D40.6
>
> Juniper vXRX NG 15.1×49-D70.3
>
> Juniper vMX 14.1.4R8
>
> Juniper vMX 16.1R3.10 VCP (control plane node)
>
> Juniper vMX 16.1R3.10 VFP (forwarding plane node)
>
> Juniper vMX 17.1 VCP (control plane node)
>
> Juniper vMX 17.1 VFP (forwarding plane node)
>
> Juniper vQFX 10K VRE (routing engine)
>
> Juniper vQFX 10K VFE (forwarding engine)
>
> Junos Sphere 16.1
>
> Alcatel 7750SR: 13.0.R3
>
> A10, vThunder 2.7.1
>
> Aruba: Clearpass 6.4.X
>
> Arista vEOS 4,17.2F and earlier versions
>
> Barracuda NGFW
>
> Brocade vADX 3.01.1
>
> Checkpoint FW: R77-20, R77-30
>
> Citrix Netscaler 11.0.62
>
> Dell SonicWall 11.3.0
>
> CumulusVX 2.5.3
>
> ExtremeOS 21.1.14
>
> F5 BIG-IP 12.0.0 Supports LTM, GTM HA
>
> Fortinet Manager v5
>
> Fortinet Mail 53
>
> Fortinet FGT v5.X
>
> Fortinet 5.2.3
>
> HP VSR 1000 7.10
>
> Mikrotik 6.30.2
>
> PaloAlto FW 7.0, 7.1
>
> pfSense FW 2.3
>
> S-Terra FW, Gate 4.1,
>
> S-Terra CSP-VPN gate 3.1
>
> VyOS 1.1.6
>
> Windows XP
>
> Windows 7
>
> Windows 10
>
> Windows Server 2003
>
> Windows Server 2008R2
>
> WindowsServer 2012 R2
>
> Windows Server 2016
>
> Linux TinyCore 6.4
>
> Linux Slax 7.08
>
> Linux Mint 18
>
> Linux Kali x64 Full
>
> Linux Kali x386 light
>
> Linux Mint 18
>
> Linux Ubuntu Desktop 16.04
>
> Linux DSL 4.4.10
>
> Linus Ubuntu Server 16.04 Webmin

 **本文作者：剑思庭（
jiansiting@gmail.com；wechat：jiansiting；开源工具github.com/jiansiting），本文属FreeBuf原创奖励计划，未经许可禁止转载。**  

