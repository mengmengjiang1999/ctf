***严正声明：本文仅限于技术讨论，严禁用于其他用途。**

 **近期，来自Fleetsmith公司（一家macOS管理公司）的CPO兼CSO-Jesse
Endahl向外界演示了技术高超的攻击者如何通过DMD来入侵企业环境中的苹果Mac电脑。根据研究人员透露的信息，在这项技术的帮助下，攻击者将能够在新款Mac设备启动的时候入侵目标设备。**

![1.png](https://image.3001.net/images/20180913/1536816797_5b99f69db4c5d.png!small)

研究人员表示，他们能够利用苹果移动设备管理协议（MDM）来获取目标主机的manifest文件信息，并在目标设备上安装各种恶意应用。

MDM允许企业环境中的网络管理员远程访问企业网络中的macOS和iOS设备，在该协议的帮助下，管理员可以轻松安装或删除设备中的应用程序，他们甚至还可以锁定设备或清除设备中的数据。当企业环境中添加了新的设备时，MDM服务器会收到一份配置文件，设备会自动使用DEP设备注册程序来完成添加操作。此时，macOS设备在启动时或完成重置（恢复出厂设置）后，会自动跟MDM服务器建立通信连接。接下来，MDM服务器会将其创建的DEP配置文件发送给请求设备，其中包含了跟软件安装相关的信息，例如服务器的URL地址和绑定的证书等等。

![2.png](https://image.3001.net/images/20180913/1536816802_5b99f6a2d1c53.png!small)

通过使用MDM命令“InstallApplication”，管理员可以在目标设备上安装特定的应用程序。这条命令需要使用一个manifest
URL，并返回一个XM文件，而这个XML文件中会包含安装应用程序时所需的全部信息。

专家解释称，攻击者将有可能修改这个manifest配置文件，并通过执行中间人攻击（MitM）来在目标设备上安装恶意软件。这项攻击技术需要在macOS电脑连接MDM服务器时进行，无论怎样，虽然理论上可行，但攻击的实现难度并不低，研究人员认为目前只有国家级黑客组织或ISP服务商能够执行这种类型的攻击。

目前，研究人员已经将有关该攻击技术的详细信息上报给了苹果公司。研究人员在其发表的[研究报告](http://i.blackhat.com/us-18/Thu-August-9/us-18-Endahl-A-Deep-Dive-Into-macOS-MDM-And-How-It-Can-Be-Compromised-wp.pdf)中写到：“我们在发现了该漏洞之后，便立刻将其上报给了苹果公司，根据苹果公司的回复，他们已经修复了该漏洞，并实现了一种新的MDM命令形式：InstallEnterpriseApplication。该命令（
[macOS10.13.6](https://www.securityweek.com/apple-rolls-out-usb-restricted-mode-ios)可使用）允许MDM提供商提供指定的证书来与请求的Manifest
URL进行绑定（这里使用了新的ManifestURLPinningCerts属性），但是具体的实现方式还需要MDM服务商自行决定。”

 ***
参考来源：[securityaffairs](https://securityaffairs.co/wordpress/75240/hacking/macs-mdm-hack.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

