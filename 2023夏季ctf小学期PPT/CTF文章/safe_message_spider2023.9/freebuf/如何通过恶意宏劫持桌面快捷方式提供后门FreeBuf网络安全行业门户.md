**多年以来，一直都有攻击者使用恶意宏来传播恶意软件，并且还设计出了各种方法来让这种技术变得更加有效。近期，研究人员观察到了一种更加隐蔽的基于宏的攻击活动，在这个攻击活动中，攻击者会利用宏来搜索用户系统中的特定快捷方式，并利用它们来下载恶意软件。当用户点击了修改后的桌面快捷方式后，下载下来的恶意软件将会被执行。**  

恶意软件执行之后，它会恢复原始的快捷方式并打开本应打开的应用程序。接下来，恶意软件会编译其Payload。需要注意的是，在攻击过程中它并不会使用自制的工具，它会从网上下载各种Windows工具（例如WINRAR和Ammyy
Admin）来收集信息，并通过SMTP将数据发送给远程C2服务器。

虽然恶意宏和下载下来的恶意软件并不算复杂，但这种方法还算是比较有意思的，因为从签名信息来看，这种方法还在进化之中。

下图显示的是恶意软件感染链：

![2.png](https://image.3001.net/images/20180829/1535522294_5b8635f61b026.png!small)

## 恶意文档

这种攻击技术的感染链起点是一个恶意文档，该文档的文字语言为俄语，并且带有一张房屋的照片，其中的内容会引导用户启用宏来打开完整的文档：

![3.png](https://image.3001.net/images/20180829/1535522314_5b86360a49546.png!small)

这是因为微软为了避免安全风险，默认是禁用该功能的，一旦启用了宏功能，用户的电脑将有可能受到恶意代码的攻击。

### 宏文件在劫持桌面快捷方式时起到什么作用？

用户启用宏功能后，恶意代码会尝试搜索桌面快捷方式，并替换相应的链接文件。它主要针对的是五种快捷方式，即Skype、Google
Chrome、MozillaFirefox、Opera和IE浏览器，当它找到匹配目标之后，便会从Google
Drive或GitHub下载相应文件名的恶意软件。比如说，当恶意代码查找到了Google Chrome桌面快捷方式后，它会进行以下操作：

1.在%AppData%\Google\创建一个目录；

2.下载Payload，存储到%AppData%\Google\chrome_update.exe；

3.如果.NET
Framework不存在：hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/chrome_update；

4.如果.NET
Framework存在：hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/dotnet/chrome_update；

![4.png](https://image.3001.net/images/20180829/1535522328_5b863618f3050.png!small)

5.查找目标快捷方式，删除链接；

6.创建一个新的指向已下载Payload的链接并替换目标链接：.TargetPath
=%AppData%\Google\chrome_update.exe。

![5.png](https://image.3001.net/images/20180829/1535522336_5b86362072f52.png!small)

除此之外，它还会修改快速启动栏的链接，步骤如下：

1.在%AppData%\Microsoft\Internet Explorer\Quick
Launch\UserPinned\TaskBar中寻找跟Google或GoogleChrome相关的文件名；

2.跟之前一样，修改快捷方式图标对应的链接地址，将其指向恶意软件；

上述步骤完成之后，当用户点击快捷方式图标时，恶意软件将会被执行。

## 恶意服务的运行以及如何掩盖攻击痕迹

执行之后，恶意软件会在目标系统的system32或SysWoW64目录中存放WpmPrvSE.exe
(标记为TROJ_DLOADER.COGBA)，然后开启一个名叫WPM Provider Host的服务。下图即为该服务的相关属性：

![6.png](https://image.3001.net/images/20180829/1535522359_5b863637064c2.png!small)

除此之外，它还会在system32或SysWoW64目录中存放rar.exe和一个注册表键以备后续使用。最终，它会恢复之前替换的桌面以及快速启动栏的快捷方式文件，并掩盖其攻击痕迹。

## 恶意服务如何工作？

恶意软件在运行过程中会激活相应的恶意服务，该服务首先会将其下载RAR文档（从Google
Drive或GitHub）的时间间隔设置为1小时。然后使用之前下载的WinRAR工具来打开文档，其中包含一个安装包文件、一些配置文件以及其他需要使用到的工具。

![7.png](https://image.3001.net/images/20180829/1535522372_5b8636442226e.png!small)

服务会运行RAR文档中的installer.exe（标记为HKTL_RADMIN），Installer.exe会使用certutil命令行程序，接下来会对压缩文档中的wsvchost.key进行解码，解码为wsvchost.exe。wsvchost.exe实际上是Ammyy
Admin 3.5，即一款众所周知的RAT远程管理工具：

![8.png](https://image.3001.net/images/20180829/1535522380_5b86364ca1b73.png!small)

接下来，恶意软件会运行stop_ammmyy.ps1这个Shell脚本，并强制让Ammyy进程终止运行。目前我们还无法判断这一部分在整个攻击链中的具体作用，因为在之前的恶意软件版本中并没有这一步骤。

与此同时，installer文件还会开启另一个名叫WSVCHost的服务，该服务会运行wsvchost.exe（Ammyy Admin
3.5）,并使用procdump从内存中导出跟WSVCHost相关的进程信息：

![9.png](https://image.3001.net/images/20180829/1535522398_5b86365e51eb2.png!small)![10.png](https://image.3001.net/images/20180829/1535522394_5b86365a52e3c.png!small)

完成上述步骤之后，恶意软件会使用certutil对导出数据进行编码，然后使用WinRAR将导出文件压缩为两个文件（dump1.txt.img和dump2.txt.img），并将它们存放在一个名叫“treasure”的目录中(C:\Windows\System32\send_treasure)。

![11.png](https://image.3001.net/images/20180829/1535522408_5b86366838bd4.png!small)

接下来，恶意软件会通过SMTP协议并将导出数据+系统信息+执行日志以附件的形式发送给攻击者（邮件服务器：rambler.ru/meta.ua，端口：465）。攻击者在这里使用了两个不同的邮件服务器，表明攻击者想要确保数据能够成功发送。

![12.png](https://image.3001.net/images/20180829/1535522419_5b8636739915f.png!small)

## 实践建议

微软之所以禁用宏功能，是有实际意义的，现在很多恶意软件都会在宏文件中嵌入恶意代码，而用户在启用了宏功能并点击了恶意文档之后，就毫无“招架之力”了。因此，我们建议广大用户在收到了未知来源的文件后，不要轻易开启宏功能。

## 入侵威胁指标IoC

### SHA256：

**SHA256** | **检测名**  
---|---  
0181A985897F1FA66EDE98CC04E97B05387743DE198C2DCF4667FA4FDE7779C1 | HKTL_RADMIN  
20B05A17623A7E74F7CFE4296BA79CFF8CA6B3EA64F404661B7BC46AB603511C | HKTL_RADMIN  
2864B1B7417AACC13A4277D8CB9C94B5A04420F6CCC1CC4DFD3BE4D369406383 | HKTL_RADMIN  
2B3CD4D85B2B1F22D88DB07352FB9E93405F395E7D0CFE96490EA2BC03A8C5FF | HKTL_RADMIN  
3B85E737965020D82CDC0890F1243732B71977117CDF310554E9DD91B78BFE63 | HKTL_RADMIN  
451C4C3FBF5AEC103833FA98D942B1876D9CE84575A00757562489921BC1D396 | HKTL_RADMIN  
45B2580DB6D13720014753813EB69C1AA0EFFBD100BB80E5A07D75447489BA0F | HKTL_RADMIN  
7730A98FD698F1043184992F1CA349EA1BDFD33D43A0ECE2CD88F9F6DA2E37D1 | HKTL_RADMIN  
804D883661BA51CEC97135F9F33C1FA9084384783D59A4F55D496E2901C20289 |
TROJ_DLOADER.COGBA  
96A4F844D7102D0EE757CAA1719F1CD95D1386E61EB7C694020D6CF14B546880 | HKTL_RADMIN  
9EAC92BEC146CE9CEF096105F6531F2EE4C2E1A14507F069728A1022ECDCDEDD | HKTL_RADMIN  
A4B25E5E72FC552E30391D7CD8182AF023DC1084641D93B7FA6F348E89B29492 | HKTL_RADMIN  
A9FC2B6F8BC339742268BAC6C02843011EBB670114A786A71FF0FA65397AC9C6 | HKTL_RADMIN  
C57BF08C414900B5B4AD907272A606D6695C14DC2ACC0264ECA53840EEE3F3F4 | HKTL_RADMIN  
C9B7C2189D3CEA05A666C45043812D832BED60CFCB8A97222BCA9AFC53B3D229 | HKTL_RADMIN  
CC60DAE1199C72543DD761C921397F6E457FF0440DA5B4451503BFCA9FB0C730 | HKTL_RADMIN  
d904495737dfe33599c0c408855f6d0dd9539be4b989eb5ab910eb6ab076d9ef |
W2KM_DLOADER.FODAM  
  
### 攻击第一阶段的链接：

**攻击第一阶段**  
---  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1eoZvAJNwYmj97bWhzVLUVIt0lAqWKssD&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1f84hF8spepIVwTMAQU0nYs-6o9ZI3yjo&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1G7pfj4X3R4t8wq_NyCoE2pMYFo-TIkI9&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1GofUo_21wAidnNek5wIqTEH65c5B4mYl&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1NfIqI9SJedlNn02Vww8rd5F73MfLlKsJ&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1NgMUcD8FzNTEi45sNc6Cp-VG-EnK_uL-&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1NStRbzXtC4Vwv2qZ0CjrJYbk5ENFmQv_&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1tBu1-SVAdWQccETb_AxAhBR3CLIrjkOU&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1TjywdxSZfENUorSHyjVDprOsT8Sq1_SW&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1Xhx22-OVqg-ZcpwU6bVBdP9lWZfzyFzB&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1yC0rtWErmwTTyLO3VuP33pgLkfzy0xik&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1YqlYbFUObMjRBvNFfjwkdSJTpxU-rMVy&export=download  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/chrome_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/dotnet/chrome_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/dotnet/firefox_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/dotnet/iexplorer_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/dotnet/opera_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/dotnet/updater  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/firefox_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/iexplorer_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/opera_update  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/updater  
  
### 攻击第二阶段的链接：

**攻击第二阶段**  
---  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1lcw-cN9o3NkR6zkeHrDHg-WiUhHBi1wK&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1OhTA1K04zKFaKw7omXJbmN8_S2VmIcdD&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1okynNTx2kEvx1gBQsmmB3OuS0wQ3A3uE&export=download  
hxxps://drive[.]google[.]com/uc?authuser=0&id=1ZFcguS1z4bSCpnMibYZZ8KHdFtN6hscM&export=download  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/winhost[.]img  
hxxps://raw[.]githubusercontent[.]com/microsoftstorage/vsto/master/winhost[.]ver  
hxxps://raw[.]githubusercontent[.]com/modernconceptplanet/vsto/master/winhost[.]img  
hxxps://raw[.]githubusercontent[.]com/modernconceptplanet/vsto/master/winhost[.]ver  
  
***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/malicious-macro-hijacks-desktop-shortcuts-to-deliver-backdoor/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM **

