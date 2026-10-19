![ThinkPad_Lenovo_Yoga-680x400.jpg](https://image.3001.net/images/20180508/15257695732026.jpg!small)  

**联想在周五发布了两则安全公告，分别针对ThinkPad产品线和System
x服务器。一个漏洞与安全引导过程中的身份验证环节有关；另一个漏洞会被用来任意代码执行。**

联想的内部测试团队发现了第一个被评为高危的Secure Boot漏洞（CVE-2017-3775）。受影响的有近十几个企业级系统，包括System
x，Flex System和NeXtScale nx360 M5型服务器。

安全启动(Secure Boot)是英特尔固件的功能，是操作系统与固件/
BIOS之间的接口。启用并配置后能够帮助计算机抵御来自恶意软件的攻击和感染；它会通过验证其数字签名阻止入侵行为。

在受影响的联想服务器上，某些BIOS / UEFI版本在进入安全引导模式之前没有正确验证签名代码。能够物理访问的黑客可以将未签名的恶意代码引导至设备。

联想表示，它出售的系统会默认关闭Secure Boot功能，但对于那些需要使用安全启动的人，联想已经发布了一系列BIOS / UEFI补丁。

## 缓冲区溢出漏洞

与此同时另一个漏洞由白帽SaifAllah
benMassaoud提交，漏洞来自于MapDrv程序中的缓冲区溢出问题（CVE-2018-9063），MapDrv程序为System
Update提供网络共享相关功能。拥有权限的管理员可以使用MapDrv程序连接或断开网络共享。

MapDrv（C:\Program Files\Lenovo\System
Update\mapdrv.exe）中的漏洞可以让攻击者输入非常大的用户ID或密码来溢出程序的缓冲区，进而导致任意代码执行。

这是一个中危漏洞，因为攻击者的权限有限，并且这种权限不可远程利用。即便如此，联想还是建议用户使用补丁来保护自己。

漏洞补丁针对5.07.0072或更高版本的操作系统中可用。

> “你可以通过打开联想系统更新查看当前安装的版本，点击右上角的绿色问号，然后选择关于”，联想公告中说。

联想系统更新会自动检查更新版本，但用户也可以手动更新其系统。

 *** 参考来源：[ThreatPost](https://threatpost.com/lenovo-patches-arbitrary-code-execution-flaw/131725/)，本文作者Sphinx，转载注明来自FreeBuf**  

