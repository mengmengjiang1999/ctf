![usb-stealer.jpg](https://image.3001.net/images/20181020/1539993367_5bca6f172c4b1.jpg!small)

**USBStealer是一款用于[窃取Windows应用密码](https://gbhackers.com/offline-password-attack-john-ripper/)的工具，可以为我们从基于Windows的应用程序中提取密码，例如Chrome Password，FireFox
Password，NetPassword，Windows管理员密码等。**

要执行破解程序，目标机器需要为Windows系统，且需要获取超级管理员权限（admin Access）。

USBStealer是一款非常棒的工具，其中还包括了一些用于提取[在线密码](https://gbhackers.com/online-password-bruteforce-attack-thc-hydra-tool-tutorial/)，用户名历史记录以及[离线密码](https://gbhackers.com/offline-password-attack-john-ripper/)的工具。

一些可执行破解程序已压缩在单个文件夹中，用于提取Windows应用中的密码。

## USBStealer是如何窃取密码和浏览历史记录的？

USBStealer拥有大量用于窃取Windows应用密码的Payload。攻击者只需将装载有Payload的U盘，插入目标Windows机器即可。

如果你需要管理员密码而你又忘了，你只需进入“USBCracker”文件夹并执行“Admin
Cracker.exe”。你将在管理员模式下使用“cmd.exe”，然后键入以下命令：

 ****

    
    
    - >(Your Drive Letter):\
    
    ->cd USBCracker
    
    ->USBCracker.exe

 ****

从[GITHUB](https://github.com/madScript01/USBStealer)下载并解压缩USBStealer。

![53233AE7-CB0C-4F02-BE4D-617C549E4DC8.png](https://image.3001.net/images/20181020/1539993405_5bca6f3d203f7.png!small)

可以看到，在文件夹中包含了许多用于不同应用的可执行文件，这些文件当前正在执行密码窃取任务。

> -> USBCracker.exe（凭据抓取）（Totally Discreet）
>
> -> Admin Cracker.exe（打开具有管理员权限的cmd.exe，绕过管理员密码限制）

下一步你将找到名为Browser History View的相关可执行Payload ，单击并执行后将弹出高级选项框。

你可以在此处自定义要从浏览器中提取的历史记录，日期，时间和类型。

![4A2D74B8-DF78-4263-B222-67945D91E757.png](https://image.3001.net/images/20181020/1539993454_5bca6f6e3b3e4.png!small)

一旦文件被执行，你将在Notepad中获取到所有浏览器的历史记录。

![E3338DA5-FCC4-4110-9E72-7CDA92D9D524.png](https://image.3001.net/images/20181020/1539993525_5bca6fb522d84.png!small)

单击并执行ChromePass payload，它将提取你用于登录的特定URL用户名和密码。

![085AD45C-D42F-41FB-9A3A-69510DABAB37.png](https://image.3001.net/images/20181020/1539993543_5bca6fc74c4a2.png!small)

单击WebBrowserPssView破解所有浏览器密码，所有用户名和密码凭据将被保存到Notepad中。

![96738292-9BDD-49B3-B64B-CDED1EA2A99A.png](https://image.3001.net/images/20181020/1539993555_5bca6fd3339d7.png!small)

你可以在Notepad中查看所有被保存的密码，只需进入USBCracker文件夹并执行USBCracker.exe，等待大约10~15秒的时间密码将被导出到txt文件中。

同样，你也可以使用相同的方法使用[PasswordStealer](https://github.com/tresacton/PasswordStealer)来窃取路由器和Skype的密码。

 ***参考来源：[gbhackers](https://gbhackers.com/pasword-hacking/)，
FB小编secist编译，转载请注明来自FreeBuf.COM**

