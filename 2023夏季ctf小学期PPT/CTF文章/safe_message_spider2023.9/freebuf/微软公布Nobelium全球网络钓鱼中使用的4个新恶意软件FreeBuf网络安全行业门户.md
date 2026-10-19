前几天微软警告称，被认为是去年灾难性 SolarWinds 攻击幕后黑手的黑客利用系统漏洞发起另一次重大网络攻击。攻击者利用美国国际开发署的Contact
Contact 帐户向150多个不同组织，大概3000个电子邮件帐户发送网络钓鱼邮件，其中包括致力于国际发展、人道主义和人权工作的政府机构和组织。

### Nobelium 使用的新恶意软件

继发布警告之后，微软详细介绍了Nobelium在最近的这些攻击中使用的4个新系列恶意软件。

这四个新系列包括一个名为“EnvyScout”的 HTML
附件、一个名为“BoomBox”的下载器、一个名为“NativeZone”的加载器，以及一个名为“VaporRage”的 shellcode下载器和启动器。

### EnvyScout

enviyscout是一种恶意HTML/JS文件附件，用于鱼叉式网络钓鱼邮件，它试图利用系统漏洞窃取Windows帐户的NTLM证书，并在受害者的设备上放置恶意ISO。

作为一个名为nvw . HTML的文件分发，当打开时，HTML文件将尝试从文件://
URL加载图像。在执行此操作时，Windows可能会将登录用户的Windows
NTLM凭据发送到远程站点，攻击者可以捕获该站点并通过暴力破解以显示明文密码。

![](https://image.3001.net/images/20210602/1622605310_60b6fdfe4f5856135099d.jpg!small)

使用 file:// URL 加载远程图像

微软表示，该附件还用于将嵌入的文本blob转换为恶意的ISO，保存为nvm .img到本地文件系统。

![](https://image.3001.net/images/20210602/1622605323_60b6fe0bebe3b988100e4.jpg!small)

保存 ISO 映像的 NV.html 附件

通常，此阶段用户的计算机系统已受感染，并准备打开下载ISO NV.img。当ISO映像打开时，Windows 将向用户显示一个名为 NV
的快捷方式，该快捷方式执行隐藏的 BOOM.exe，它是下面描述的新BoomBox恶意软件家族的一部分。

![](https://image.3001.net/images/20210602/1622605341_60b6fe1d80336449dab1a.jpg!small)

NV.img ISO 文件的内容

安全研究员发现了另一个冒充来自比利时大使馆的钓鱼活动，使用的是同样的恶意软件附件。可以发现，黑客已经利用微软此系统漏洞熟练进行钓鱼活动，通过相同手段持续进行网络攻击。

![](https://image.3001.net/images/20210602/1622605356_60b6fe2cd887089ad7278.jpg!small)

冒充比利时大使馆的网络钓鱼活动

### BoomBox

微软追踪到ISO文件中的BoomBox .exe文件名为“BoomBox”，并表示该文件被用来从DropBox下载两个加密的恶意软件文件到受感染的设备。

将下载的文件解密后，BoomBox将其保存为%AppData%MicrosoftNativeCacheNativeCacheSvc.dll和%AppData%SystemCertificatesCertPKIProvider.dll，并使用rundll32.exe执行。

NativeCacheSvc.dll被配置为用户登录Windows时自动启动，并用于启动CertPKIProvider.dll。作为最后一个阶段，BoomBox恶意软件将收集有关系统中Windows域的信息，对收集到的数据进行加密，然后将其发送到攻击者控制下的远程服务器。

作为最后的侦察步骤，如果系统已在域中，BoomBox
会执行一个LDAP查询来收集数据，如可识别的名称、SAM帐户名称、电子邮件、并通过过滤器(&(objectClass=user)(objectCategory=person))显示所有域用户的名称。

### NativeZone

微软检测到NativeCacheSvc.dll文件是一个名为“NativeZone”的新的恶意软件加载程序。该恶意软件被BoomBox删除并配置为当用户登录到Windows时自动启动。当通过
rundll32.exe 启动时，它会启动 CertPKIProvider.dll 恶意软件，微软将其检测为“VaporRage”。

### VaporRage

在这些攻击中使用的第四个恶意软件是“VaporRage”，它是之前NativeZone一节中描述的CertPKIProvider.dll文件。当启动时，恶意软件将连接回一个远程命令和控制服务器，在那里它将进行注册，然后反复连接回远程站点以下载shellcode，下载shellcode
后，恶意软件将执行以上用以实施各种恶意活动，包括部署 Cobalt Strike 信标。

### SolarWinds 攻击背后的同一团体

这些攻击背后的黑客组织被认为是SolarWinds供应链攻击背后的同一个组织。该组被跟踪为Nobelium (Microsoft)、NC2452
(FireEye)、StellarParticle (CrowdStrike)、SolarStorm (Palo Alto Unit 42) 和Dark
Halo (Volexity)。

邮箱在日常办公中作为商务沟通、信息存储的载体，重要性不言而喻。但近年来黑客们无孔不入，企业屡屡遭受漏洞攻击的困扰，一方面由于互联网通信协议本身的问题，另一方面因为系统漏洞给黑客以可乘之机。研究显示，超95%的企业系统存在严重的漏洞问题，这些问题将它们置于网络攻击风险之中并可能导致严重的数据泄露。

出现漏洞并不可怕，及时做好系统漏洞防御可有效防止数据泄露：

1、及时维护系统设备，针对系统静代码进行检测，减少系统漏洞数并按时检测查杀病毒;

2、对收发及储存的数据进行加密;

3、做好防范手段如数据跟踪、数据防泄漏等防控机制，确保企业数据安全。

