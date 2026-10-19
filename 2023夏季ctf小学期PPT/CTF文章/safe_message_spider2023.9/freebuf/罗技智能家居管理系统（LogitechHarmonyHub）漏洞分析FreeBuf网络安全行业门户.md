**![harmony-hub-1.png](https://image.3001.net/images/20180509/15258575899406.png!small)**

**近期，火眼公司Mandiant Red Team团队发现，罗技智能物联网家居管理系统Logitech Harmony
Hub存在多个可利用漏洞，攻击者可利用这些漏洞，绕过系统限制，通过SSH方式获取到设备系统的管理权限。Logitech Harmony
Hub是一款集成了软硬件的智能家居管理连接系统，攻击者可以通过漏洞控制Logitech Harmony
Hub，对本地网络内的智能家居系统形成攻击威胁。由于Harmony
Hub支持的设备包括对智能锁、智能恒温器以及其他智能家庭设备，使用该产品的用户会面临严重安全风险。**

## 涉及漏洞

> 不当的证书验证方式
>
> 不安全的更新过程
>
> 开发者遗留在固件镜像中的调试信息
>
> 空密码的root用户

## 影响产品

> Harmony Elite, Harmony Pro, Harmony Home Hub, Harmony Ultimate Hub, Harmony
> Hub, Harmony Home Control, Harmony Smart Control, Harmony Companion, Harmony
> Smart Keyboard, Harmony Ultimate and Ultimate Home。

## 漏洞分析

Mandiant团队使用漏洞利用组合方式最终root掉了Logitech Harmony
Hub，这篇文章分享了漏洞发现的测试和分析过程，也从侧面反映出，在与人们生活起居息息相关的智能家居时代，非常有必要对此类产品进行严格的安全性测试。

### 前期准备

一些公开的研究表明，在Logitech Harmony Hub上的某些硬件测试点上存在一个通用异步收发传输器 (UART)，我们把跳线焊接到测试点（Test
pad）上，这样我们就能够使用USB串行电缆的TTL方式连接到Logitech Harmony Hub上。启动过程的初始分析显示，Harmony
Hub利用U-Boot 1.1.4启动，并运行为一个Linux内核：

![01.png](https://image.3001.net/images/20180509/15258569702120.png!small)  

在对该测试点的启动引导过后，由于内核未配置有其它控制接口，控制端没有过多输出返回信息显示，之后，我们在U-Boot中配置了内核启动参数来观察整个启动引导过程，但是也没发现任何有用信息。此外，UART接口配置仅为传输，通过其也不能实现其它与Harmony
Hub的交互。为此，我们把研究重点转向Harmony Hub内置的Linux操作系统和相关运行软件上。

### 固件恢复和数据提取

在初始配置阶段，Harmony
Hub上的内置APP应用可通过蓝牙用Android或iOS应用程序与其配对控制。由此，我们利用hostapd工具创建了一个模拟的无线AP接入环境，并在测试用的Android设备上安装了Burp
Suite Pro证书，用以监听Harmony应用程序与Harmony Hub和外网的网络通信。一旦初始的蓝牙配对成功，Harmony
APP应用就会搜索网络内的Harmony Hub设备，并通过基于API的http方式与设备通信。

![02.png](https://image.3001.net/images/20180509/15258570149393.png!small)

另外，Harmony
Hub会向一个远端互联网的罗技服务器发送当前的固件版本信息，以检测是否存在可用的固件更新。如果有，远端的罗技服务器会通过返回一个包含最新固件版本的URL信息进行响应。

尽管我们使用了自签名证书来拦截监听Harmony Hub发送的HTTPS流量，但我们还是能够观察到整个网络请求响应过程，由此也表明Harmony
Hub未对证书的有效性进行过验证。

![03.png](https://image.3001.net/images/20180509/15258570491969.png!small)

![04.png](https://image.3001.net/images/20180509/15258570817063.png!small)

我们获取了固件并对其进行了分析，经过对其中几层目录的提取后发现，主要固件文件存储在镜像的squashfs文件夹中，从中可发现，整个镜像为开源的且为lzma压缩的SquashFS文件系统，这种系统多应用于嵌入式设备中。但是，供应商通常会使用与最新的squashfstools版本不兼容的squashfstools旧版本。之后，我们使用
[firmware-mod-kit 工具包](https://github.com/rampageX/firmware-mod-kit)中的unsqashfs_all.sh脚本来获取unsquashfs版本信息，并进行后续的镜像信息提取。  

![05.png](https://image.3001.net/images/20180509/1525857137264.png!small)  

通过提取的镜像文件发现，其中存在一些Harmony Hub操作系统的详细配置信息，另外，在镜像中还遗留了各种调试信息，如未strip清除的内核模块等。

![06.png](https://image.3001.net/images/20180509/15258571797003.png!small)  

在对 /etc/passwd 检查后发现，竟然root用户根本就没设置密码，是空密码。也就是说，如果能实现dropbear SSH
server的启用，那么就能轻松获取Harmony Hub的root访问权限。

![07.png](https://image.3001.net/images/20180509/15258571996440.png!small)

> Dropbear是一个开源的，轻量化SSH服务器和客户端程序，它运行在一个基于POSIX的各种平台，尤其是一些嵌入式的Linux设备系统中。  
>

我们发现，如果文件系统中存在file/etc/tdenetable，则在初始化期间将会启用一个dropbear SSH server实例。

![08.png](https://image.3001.net/images/20180509/15258572702223.png!small)

### 固件更新劫持

在初始化过程中，Harmony Hub会请求一个罗技API上的 GetJson2Uris
终端，来获取一个后续能用到的URL列表，这些URL可用于固件的更新检测或其它软件包获取。

![09.png](https://image.3001.net/images/20180509/15258572949066.png!small)  

我们拦截并修改了服务器响应中的JSON对象，将GetUpdates属性指向我们自己的IP地址。

![10.png](https://image.3001.net/images/20180509/15258573128826.png!small)

与固件更新过程类似，Harmony
Hub向由GetUpdates指定的终端发送了一个POST请求，其中包含了当前内部软件包的各种信息。以下为一个对HEOS包的请求示例：

![11.png](https://image.3001.net/images/20180509/15258573271698.png!small)  

如果POST请求中的sysBuild参数与当前远端罗技服务器中的版本不匹配，则远端罗技服务器会返回一个包含新版软件包的初始响应，由于某个未知原因，Harmony
Hub忽略了这个响应，并接着再次发送了第二个请求，远端罗技服务器在对这个请求的响应中，就包含了指向固件更新的URL。

![12.png](https://image.3001.net/images/20180509/15258573448522.png!small)  

通过该URL，我们下载分析了其中为ZIP格式的 .pkg 文件，其中包含了一个简单的文件结构。

![13.png](https://image.3001.net/images/20180509/15258573737844.png!small)  

其中的manifest.json文件里有一些Harmony Hub更新过程中如何处理压缩包的信息。

![14.png](https://image.3001.net/images/20180509/15258573937546.png!small)  

update.sh就是压缩包中Harmony
Hub的固件更新脚本，按照前面的分析，我们更改了该脚本，创建了/etc/tdeenable文件，使得在启动引导过程中能开启SSH接口来进行连接。

![15.png](https://image.3001.net/images/20180509/15258574217171.png!small)  

之后，我们在本地自己控制的Web服务器上托管了一个.pkg格式的恶意压缩包，当Harmony
Hub检查固件更新，并向GetJson2URIs发起请求更新时，由于我们在响应中进行了一些改动，在其URL响应时，我们会把设置的恶意更新包替换成原始更新包，这样一来，Harmony
Hub最终更新的将是我们事先构造的恶意更新包。只要设备一重启，SSH接口就会自动开启，我们也能顺利地以空密码的root账户连接到设备系统中去。

![16.png](https://image.3001.net/images/20180509/15258574405732.png!small)

## 总结

随着嵌入式智能技术在生活中的广泛应用，很多像Logitech Harmony
Hub的IoT物联网设备都使用了通用的处理器和系统架构，攻击者可以利用这些架构漏洞，添加置换进入一些恶意软件包，对目标设备系统形成安全威胁。好在我们及时把漏洞上报给了罗技官方，他们非常重视，并迅速发布了
版本为4.15.96的修复固件，在此，希望罗技相关用户请及时参照[更新指南](https://community.logitech.com/s/question/0D55A00007VY8n0SAD/harmony-hub-firmware-update-fixes-vulnerabilities-identified-by-fireeye)尽快更新。

 ***参考来源：[fireeye](https://www.fireeye.com/blog/threat-research/2018/05/rooting-logitech-harmony-hub-improving-iot-security.html)，FreeBuf 小编 clouds 编译，转载请注明来自 FreeBuf.COM**  

