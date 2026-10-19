VMware 是全球桌面到数据中心虚拟化解决方案的领导厂商。1998 年2月公司成立，今年，VMware 将庆祝其成为行业先驱 20
周年。VMware官网（[https://www.vmware.com](https://www.vmware.com/)）列出其从数据中心和云计算基础架构到个人桌面工具等众多产品。  

![image003.jpg](https://image.3001.net/images/20180706/15308539684746.jpg!small)

目前，VMwareWorkstation Pro最新版本为14，适用最新版本的Windows 10。

  
![image004.png](https://image.3001.net/images/20180706/15308539834001.png!small)  

总体来看VMware Workstation
Pro简单易用，但是我个人对网络模式的设置一直比较迷惑，设置虚拟机网络适配器的集中网络连接模式：桥接模式，NAT模式，仅主机模式分别代表什么呢？

![image005.png](https://image.3001.net/images/20180706/15308540973087.png!small)  

下面我们一起来了解一下：  

安装了VMware Workstation之后，会在网络连接对话框中多出两个虚拟网卡，如图：

![image007.png](https://image.3001.net/images/20180706/1530854021882.png!small)

  

这代表什么呢？先来看下的几个虚拟设备的含义：

VMnet0：用于虚拟桥接网络下的虚拟交换机

VMnet1：用于虚拟Host-Only网络下的虚拟交换机

VMnet8：用于虚拟NAT网络下的虚拟交换机

VMware Network Adepter VMnet1：Host用于与Host-Only虚拟网络进行通信的虚拟网卡

VMware Network Adepter VMnet8：Host用于与NAT虚拟网络进行通信的虚拟网卡。

 **一、桥接模式**

桥接模式网络连接通过使用主机系统上的网络适配器将虚拟机连接到网络。如果主机系统位于网络中，桥接模式网络连接通常是虚拟机访问该网络的最简单途径。

桥接模式下本地物理网卡和虚拟网卡通过VMnet0（默认，当然也可以修改）虚拟交换机进行桥接。

  
![image009.png](https://image.3001.net/images/20180706/15308541157587.png!small)  

桥接模式网络连接支持有线和无线主机网络适配器。桥接模式网络连接将虚拟机配置为在网络中具有唯一标识，与主机系统相分离，且与主机系统无关。桥接模式下虚拟机可完全参与到网络活动中。它能够访问网络中的其他计算机，也可以被网络中的其他计算机访问，就像是网络中一台物理机一样。

假如下面我们要做渗透测试实验了，真实的主机通过无线接入网络，IP为192.168.10.27。

![image010.png](https://image.3001.net/images/20180706/15308541344405.png!small)

物理网卡IP地址

虚拟机网络连接设置为桥接模式，设置自动获取IP地址，会发现虚拟网卡的IP自动变成了192.168.10.69，物理网卡和虚拟网卡的IP地址成为同一网段，子网掩码、网关、DNS等参数都相同。两个网卡在拓扑结构中是相对独立的。

  
![image011.png](https://image.3001.net/images/20180706/1530854167772.png!small)  

虚拟网卡IP地址

  

好了，现在可以Ping通了。

![image015.png](https://image.3001.net/images/20180706/1530854212198.png!small)  

桥接模式有一个选项是复制物理网卡连接状态，就是本机的真实网卡的状态信息复制给虚拟机的虚拟网卡，比如说本机物理网卡使用DHCP分配的地址，不需要设置就可以直接获得DHCP分配到的地址。

 **二.NAT模式**

NAT是Network Address
Translation的缩写，即网络地址转换。使用NAT模式网络连接时，VMware会在主机上建立单独的专用网络，用以在主机和虚拟机之间相互通信。虚拟机向外部网络发送的请求数据"包裹"，都会交由NAT网络适配器加上"特殊标记"并以主机的名义转发出去，外部网络返回的响应数据"包裹"，也是先由主机接收，然后交由NAT网络适配器根据"特殊标记"进行识别并转发给对应的虚拟机，虚拟机在外部网络中不必具有自己的IP地址。从外部网络来看，虚拟机和主机在共享一个IP地址，默认情况下，外部网络终端也无法访问到虚拟机。

![image016.png](https://image.3001.net/images/20180706/15308542511485.png!small)  
  

在一台主机上只允许有一个NAT模式的虚拟网络。因此，同一台主机上的多个采用NAT模式网络连接的虚拟机也是可以相互访问的。

前面我们已经提到，默认情况下，外部网络无法访问到虚拟机，不过我们也可以通过手动修改NAT设置实现端口转发功能，将外部网络发送到主机指定端口的数据转发到指定的虚拟机上。比如，我们在虚拟机的80端口上"建立"了一个站点，只要我们设置端口转发，将主机88端口上的数据转发给虚拟机的80端口，就可以让外部网络通过主机的88端口访问到虚拟机80端口上的站点。

  
![image017.png](https://image.3001.net/images/20180706/15308542664852.png!small)  

在NAT网络中，会用到VMware Network Adepter VMnet8虚拟网卡，主机上的VMwareNetwork Adepter
VMnet8虚拟网卡被直接连接到VMnet8虚拟交换机上与虚拟网卡进行通信。VMware Network Adepter
VMnet8虚拟网卡的IP地址是在安装VMware时由系统指定生成的。下图显示的是主机VMware Network Adepter VMnet8的参数。

  
![image019.png](https://image.3001.net/images/20180706/153085429647.png!small)  

虚拟出来的网段和NAT模式虚拟网卡的网段是一样的，包括NAT服务器的IP地址也是这个网段。在安装VMware之后同样会生成一个虚拟DHCP服务器，为NAT服务器分配IP地址。下图为虚拟机自动获取到的IP。

![image020.png](https://image.3001.net/images/20180706/1530854321578.png!small)

主机和虚拟机进行通信的时候会调用VMware NetworkAdepter VMnet8虚拟网卡，因为他们都在一个网段，所以可以顺利通信。

 **三.仅主机模式**

在仅主机模式网络中，虚拟机和主机虚拟网络适配器均连接到专用以太网络。主机和虚拟机之间的通信是通过VMware Network Adepter
VMnet1虚拟网卡来实现的。虚拟网络是一个全封闭的网络，在默认配置中它唯一能够访问的就是主机,仅主机模式网络中的虚拟机无法连接到 Internet。

![image022.png](https://image.3001.net/images/20180706/15308543647626.png!small)  
  

下图是VMware Network Adepter
VMnet1的参数，生成的虚拟DHCP服务器和虚拟网卡的IP地址位于同一网段，但和物理网卡的IP地址不在同一网段。

  
![image023.png](https://image.3001.net/images/20180706/15308543819191.png!small)

仅主机模式下，我们自动获取到的虚拟机网卡参数如下图所示：

![image024.png](https://image.3001.net/images/20180706/15308544037834.png!small)

  

 **总结：**

 **1.** **仅主机模式下宿主机能访问虚拟机，虚拟机无法访问宿主机外部网络；**

 **2.** **桥接模式下需要和宿主机保持在同一网段，一般通过dhcp自动获取网络IP，有可能发生IP冲突，最好手工修改虚拟机固定IP。**

 **3.NAT**
**模式下，虚拟机可以通过宿主机访问外部网通，原理是通过在宿主机安装的vm8网卡作为代理访问外部网络，而且还可以通过端口映射的方式实现宿主机外部网络访问虚拟机。**

  

 **  
**

参考：[https://www.vmware.com](https://www.vmware.com/)

