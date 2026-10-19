快捷键，几乎在每个人的日常办公生活中都会用到，通过某些特定的按键、按键顺序或按键组合来替代鼠标完成一些工作过程，能够提高操作效率。常用快捷键往往会与Ctrl
键、Shift 键、Alt 键、Fn 键、 Windows
键等配合使用，但Windows下其实还存在很多鲜为人知的冷门快捷键，这篇文章的主角，就是Windows下的粘滞键和“讲述人”快捷键。

##  ** **黑客工具上传****

故事的开头总是相似。

深信服终端安全专家巡查云端日志时，被一众特别的“administratOr”吸引了目光，并且该目录的desktop目录下，出现了不少“高危”文件，是用于实现内网横向扫描、RDP远程连接、DNS切换工具等内网渗透功能的工具：

![](https://image.3001.net/images/20210901/1630488043_612f45eba634ecc96d717.png!small)

通过定位到产生日志的终端排查，在隔离区发现如下的可疑文件：

![](https://image.3001.net/images/20210901/1630488068_612f46045bf2170a85048.png!small)

其中包含部分常见工具：

 **文件名称**

|

 **功能描述**  
  
---|---  
  
d**jumper.exe

|

DNS切换工具/一键网卡切换  
  
w**pcap-4.13.exe

|

网络抓包软件  
  
svchost.exe(xD**ic IP Scanner)

|

IP扫描工具  
  
server(N*Brute 1.2)

|

暴力破解工具  
  
m**scan.exe

m**sscan_gui.exe

|

端口扫描工具  
  
##  ** **快捷键恶意利用****

另外svc.exe、bd64.exe、hs.exe、4haste.exe是四个自解压文件，里面分别包含了如下内容：

###  ** **s**** ** **vc.exe****

解压后包含一个reg文件和一个压缩包REBE1l.exe，reg文件是将sethc.exe的执行设置中，debugger值设置为"C:\\\Windows\\\reg\\\REBE1l.exe"。

![](https://image.3001.net/images/20210901/1630488374_612f4736833307907dfa7.png!small)

sethc.exe文件是Windows下的粘滞键，在连续快速按5下shift键后，windows会自动执行system32下的sethc.exe进程，早期sethc.exe会被攻击者替换，例如，替换为cmd.exe，就可以直接执行cmd命令了。考虑到直接替换文件容易被发现，后来衍生出了通过修改执行设置，将debugger值指向设置的路径（镜像劫持），也可以做到在调用sethc.exe时启动其他进程，正如此次发现的攻击手法。

而REBE1l.exe压缩包里是一个名为cmd.exe的文件，但由于解压需要密码，无法进一步确认详情：

![](https://image.3001.net/images/20210901/1630488465_612f4791139c67d563cb5.png!small)

###  ** **b**** ** **d64.exe****

该压缩包里包含了一个BC.exe压缩文件、一个reg文件、一个bat文件以及一个vbs文件：

![](https://image.3001.net/images/20210901/1630488476_612f479c969455ed2d3cb.png!small)

Hide.vbs是用于调用Hide.bat批处理文件，而Hide.bat的功能则是设置相关文件的属性，将其隐藏：

![](https://image.3001.net/images/20210901/1630488487_612f47a78ab86654284ab.png!small)![](https://image.3001.net/images/20210901/1630488495_612f47af5aa6b7133f9eb.png!small)

而reg文件的功能则与svc.exe中的reg类似，是将Narrator.exe执行设置中的debugger设置为"C:\\\Windows\\\Help\\\BC.exe"。Narrator.exe是在执行“Windows
键 + Enter 键”组合键时会调用的程序，此设置更改会使得“Windows 键 + Enter 键”组合键直接调用BC.exe：

![](https://image.3001.net/images/20210901/1630488524_612f47cc3cae8c7081beb.png!small)

BC.exe压缩包中是一个名为Xxx64.exe的文件，同样是需要密码解压，无法进一步确认，但原始文件大小与svc.exe中的cmd.exe一样：

![](https://image.3001.net/images/20210901/1630488534_612f47d6ae97f28bce628.png!small)

快捷键程序替换和镜像劫持其实是一个比较古老的技术了，没想到直至十多年后的今天仍然在被攻击者利用，不仅仅是sethc.exe和Narrator.exe，甚至包括osk.exe、Magnify.exe等程序，当某些程序被替换成cmd.exe时，攻击者在登录界面无需知道登录密码，即可直接使用快捷键或组合键调用cmd命令行，进行提权操作并执行cmd命令。

##  ** **挖矿程序****

###  ** **4haste.exe/**** ** **hs**** ** **.exe****

4haste.exe和hs.exe压缩包的内容实际是相同的：

![](https://image.3001.net/images/20210901/1630488557_612f47edef17a6682dd23.png!small)

svchost.exe实际上是NSSM（一个服务封装程序），cmd.bat的功能则是调用NSSM将systems.exe封装成一个服务以达到自启动的目的：

![](https://image.3001.net/images/20210901/1630488572_612f47fc865fcb3c26e7d.png!small)

systems.exe是一个挖矿程序，读取config.json的配置文件进行挖矿，

矿池地址：xmr.viabtc.com:8888

用户：4haste

密码：x

![](https://image.3001.net/images/20210901/1630488583_612f480782375341e8b14.png!small)

##  ** **解决方案****

网络上有给出防止篡改和镜像劫持的一些通用方式：

> 对应用程序右键进行权限设置，删除所有用户组；
>
> 针对注册表项HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image
> File Execution Options右键进行权限设置，删除所有用户组；
>
> 设置禁用部分键盘快捷方式；
>
> 在“【组策略编辑器】——>【用户配置】——>【系统】——>右击【不要运行指定的Windows 应用程序】”中，设置禁用易遭到篡改和劫持的程序；

但此类方法需要繁琐的手动操作，比较适合个人用户；针对企业用户，深信服终端安全专家建议：

> 使用企业级的终端防护软件，对终端进行实时防护和定期查杀并开启自动处置；深信服EDR支持对各类黑客工具、挖矿木马等恶意程序进行检测拦截：

