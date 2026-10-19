**在Google
Play商店中发现了三款恶意应用，恶意应用会攻击目标设备并收集用户信息，其中一个名为CAMMO，利用漏洞编号为CVE-2019-2215。这是在野第一个已知的使用use-after-free漏洞的主动攻击。经过进一步调查发现这三款应用可能是SideWinder组织武库的一部分。**

这三个恶意应用被伪装成摄影和文件管理工具。根据其中一款应用的证书信息推测这些应用自2019年3月起就一直处于活跃状态。目前这些应用程序已经从Google
Play中删除。

![](https://image.3001.net/images/20200107/1578366497_5e13f62147f70.png!small)![](https://image.3001.net/images/20200107/1578366577_5e13f671bcc32.png!small)

##  安装

SideWinder分两个阶段安装payload。它首先从C&C服务器下载DEX文件（Android文件格式）。该组使用应用程序转换来配置C&C服务器地址。地址由Base64编码，然后在恶意软件分发的URL中设置为referer参数。

![](https://image.3001.net/images/20200107/1578366883_5e13f7a308e0e.png!small)

下载的DEX文件将下载一个APK文件并安装。所有这些都是在隐蔽情况下完成的。为了逃避检测，它使用如模糊处理、数据加密和调用动态代码等技术。

应用程序Camero和FileCrypt
manager从C&C服务器下载额外的DEX文件后，第二层的dropper调用额外的代码来下载、安装和启动设备上的callCam应用程序。

![](https://image.3001.net/images/20200107/1578367001_5e13f8190ea3f.png!small)

![](https://image.3001.net/images/20200107/1578367048_5e13f8483ee48.png!small)

在用户不知情的情况下在设备上部署负载应用callCam，SideWinder将执行以下操作：

###  一、设备root

由Camero应用完成，仅适用于谷歌（Pixel 2，Pixel 2 XL）、诺基亚3（TA-1032）、LG V20（LG-H990）、Oppo
F9（CPH1881）和Redmi 6A设备。恶意软件根据dropper下载的索引从C&C服务器检索特定的攻击。

![](https://image.3001.net/images/20200107/1578367130_5e13f89a5f7e4.png!small)在调查期间从C&C服务器下载了5个漏洞。攻击者使用漏洞CVE-2019-2215和MediaTek
SU获取根权限。

![](https://image.3001.net/images/20200107/1578367172_5e13f8c4b5c26.png!small)![](https://image.3001.net/images/20200107/1578367186_5e13f8d24541d.png!small)获取根权限后，恶意软件将安装应用程序callCam，授权并启动。

![](https://image.3001.net/images/20200107/1578367245_5e13f90d41ab7.png!small)

###  二、使用辅助功能权限

FileCrypt Manager使用该方法，其适用于Android 1.6以上的大多数Android手机。应用程序启动后，会要求用户启用辅助功能。

![](https://image.3001.net/images/20200107/1578367328_5e13f9601e38c.png!small)一旦获得许可，应用程序将显示一个全屏窗口，显示需要进一步的安装步骤。但实际上这只是一个覆盖屏幕，显示在设备上所有活动窗口的顶部。

![](https://image.3001.net/images/20200107/1578367392_5e13f9a0026ca.png!small)同时，应用程序从额外的DEX文件调用代码，安装未知应用程序和callCam。它授予安装程序访问权限并启动程序。所有这些都发生在覆盖屏幕后面，用户不知情。

##
![](https://image.3001.net/images/20200107/1578367548_5e13fa3c2e608.png!small)![](https://image.3001.net/images/20200107/1578367563_5e13fa4b48bbe.png!small)callCam活动分析

app安装启动后会隐藏图标，收集一下用户信息并发送回c&c服务器：

位置信息、电池状态、文件、已安装app列表、设备信息、传感器信息、摄像头信息、屏幕就截屏、账户、wifi信息以及各类社交软件和浏览器数据。

应用程序使用RSA和AES加密算法对所有回传数据进行加密。它使用SHA256验证数据完整性并自定义编码接口。加密时，它会创建一个headData的数据块。此块包含原始数据的前9个字节、原始数据长度、随机AES
IV、RSA加密AES加密密钥和AES加密原始数据的SHA256值。然后通过自定义接口对头数据进行编码。编码后存储在最终加密文件的头部，然后是AES加密原始数据的数据。

##
![](https://image.3001.net/images/20200107/1578367865_5e13fb7939fb2.png!small)![](https://image.3001.net/images/20200107/1578367880_5e13fb88d5868.png!small)SideWinder关联分析

这些应用使用的C&C服务器被怀疑是SideWinder设施的一部分。在一台C&C服务器上还找到一个URL链接到应用程序的Google Play页面。

##
![](https://image.3001.net/images/20200107/1578368000_5e13fc00ef69e.png!small)IOCs

![](https://image.3001.net/images/20200107/1578368054_5e13fc3611fe3.png!small)![](https://image.3001.net/images/20200107/1578368070_5e13fc46358d3.png!small)

##  C&C Servers

> ms-ethics.net
>
> deb-cn.net
>
> ap1-acl.net
>
> ms-db.net
>
> aws-check.net
>
> reawk.net

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/first-active-attack-exploiting-cve-2019-2215-found-on-google-play-linked-to-sidewinder-apt-group/)，由Kriston编译，转载请注明来自FreeBuf.COM**

