##  0x00 背景介绍

 **近日，深信服安全团队排查定位到一款伪装为Windows系统帮助文件的远控木马，攻击者通过远控木马下发挖矿程序到被害主机，占用主机资源进行挖矿。**

##  0x01 威胁关联分析

通过威胁分析发现，该木马连接的域名
fuck88.f3322.net和r.nxxxn.ga是已经被开源威胁情报收录的两个恶意域名，同时用于Kryptik木马的控制端：

![](https://image.3001.net/images/20200514/1589424578_5ebcb1c22f0dc.png!small)

查询域名fuck88.f3322.net的whois信息，可以看到注册者使用名为“peng yong”，并且该注册者同时注册了多个具有欺骗性的动态域名：

![](https://image.3001.net/images/20200514/1589424588_5ebcb1ccb0cbd.png!small)![](https://image.3001.net/images/20200514/1589424606_5ebcb1de0217e.png!small)

通过深信服云脑查询恶意域名相关信息，在最近一个月内攻击次数均较为平稳：

![](https://image.3001.net/images/20200514/1589424618_5ebcb1ea909d4.png!small)

服务DLL文件Remote.hlp是一个伪装成Windows帮助文件的后门程序，仅从字符串分析，就能够得到许多功能信息，而此次事件捕获的域名所关联的后门程序中，均存在一条“TheCodeMadeByZPCCZQ”标识字符串：

![](https://image.3001.net/images/20200514/1589424635_5ebcb1fb9e9ae.png!small)

可以推断，这些后门程序均来源于同一款远控生成器，并且通过对后门dll的字符串分析，有很多中文描述的控制操作，可以确认是一款汉化的远控程序：

![](https://image.3001.net/images/20200514/1589424645_5ebcb20552672.png!small)

在此次捕获的安全事件中，除了持久化驻留的后门程序，在被害主机中存在通过后门投放的挖矿程序，伪装成银行图标，占用主机资源进行挖矿：

![](https://image.3001.net/images/20200514/1589424663_5ebcb21710688.png!small)![](https://image.3001.net/images/20200514/1589424669_5ebcb21d0f63c.png!small)

命令行中配置的的恶意域名为o.vollar.ga。

## 0x03 后门母体

1.检查互斥体“XXNBbin1”，如不存在则创建该互斥体：

![](https://image.3001.net/images/20200514/1589424736_5ebcb260d2d80.png!small)

2\. 验证路径“C:\ProgramData\Microsoft\Windows\GameExplorer”是否存在，如不存在则创建：

![](https://image.3001.net/images/20200514/1589424748_5ebcb26c28e62.png!small)3\.
创建注册表值，并设置如下键值：

    
    
    hKey = HKEY_CURRENT_USER
    
        Subkey = "Software\Microsoft\Windows\Windows Error Reporting"
    
        ValueName = "DontshowUI"
    
        Value = 0x01
    
        hKey = HKEY_LOCAL_MACHINE
    
        Subkey = "software\microsoft\remote\Desktop"
    
        ValueName = ""
    
        Value = "C:\Documents and Settings\Administrator\桌面\"

4\.
释放用于注册后门服务的DLL文件，路径为"C:\ProgramData\Microsoft\Windows\GameExplorer\Remote.hlp"，并设置文件属性为HIDDEN|SYSTEM：

![](https://image.3001.net/images/20200514/1589424782_5ebcb28edb84a.png!small)5\.
注册表里添加服务注册项，不同的母体注册的服务名称会有变化：

![](https://image.3001.net/images/20200514/1589424804_5ebcb2a47ea94.png!small)

该样本中服务名称为".Net
CLR"，研究员排查过程中发现有过“Ias”、“FastUserSwitchingCompatibilty”，服务指向的DLL程序都是母体释放的Remote.hlp：

[](https://www.freebuf.com/wp-admin/post.php?post=236732&action=edit)![](https://image.3001.net/images/20200514/1589424955_5ebcb33b63bd5.png!small)6\.
创建服务并启动：

![](https://image.3001.net/images/20200514/1589424981_5ebcb355323d4.png!small)

7\. 释放"C:\Windows\System32\\\Delete00.bat"文件，清除母体，然后退出母体进程：

![](https://image.3001.net/images/20200514/1589425271_5ebcb47780dc5.png!small)

##  0x04 服务DLL

1.服务DLL文件通常是远程控制软件批量生产的的被控端，会释放在C:\ProgramData\Microsoft\Windows\GameExplorer\目录下并命名为Remote.hlp，伪装成Windows帮助文件：

![](https://image.3001.net/images/20200514/1589425311_5ebcb49f43413.png!small)

2\. 通过逆向分析可总结该远控木马所具有的功能如下：

获取主机信息  |  进程获取/结束/暂停/恢复  
---|---  
鼠标锁定/解锁  |  文件传输  
屏幕黑屏/解除黑屏  |  重启/关机/注销  
隐藏桌面/解除隐藏  |  服务安装/启动/停止/删除  
系统操作快捷键  |  网络管理/代理设置  
Win7加速开启/关闭  |  软件管理  
hosts文件修改  |  添加用户  
远程shell  |  消息发送  
文件压缩  |  添加QQ群  
  
3\. 同时，该远控木马会检测是否存在以下安全软件，尝试绕过，具体见下表：

Navapsvc.exe  |  FilMsg.exe  
---|---  
spiderui.exe  |  Iparmor.exe  
AVK.exe  |  KSafeTray.exe  
360sd.exe  |  KvMonXP.exe  
ashDisp.exe  |  kxetray.exe  
avcenter.exe  |  mcupdui.exe  
avguard.exe  |  msseces.exe  
AVK.exe  |  Navapsvc.exe  
360sd.exe  |  360netman.exe  
ashDisp.exe  |  ns.exe  
avcenter.exe  |  PFW.exe  
avguard.exe  |  QQPCTray.exe  
360Tray.exe  |  RavMon.exe  
avp.exe  |  secenter.exe  
BaiduSdSvc.exe  |  egui.exe  
ccSvrHst.exe  |  360tray.exe  
  
##  0x05 解决方案

深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

##  0x06 加固建议

> 1\. 使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；
>
> 2\. 避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；
>
> 3\. 定期使用安全软件进行全盘扫描和处置，定期检测系统漏洞并且及时进行补丁修复。

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  

