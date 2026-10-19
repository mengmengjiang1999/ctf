BlackByte 勒索软件在 2021 年被首次发现，随后不断发现其变种。BlackByte
勒索软件不仅使用双重勒索，还运营着勒索软件即服务（RaaS）。最近，研究人员发现 BlackByte 开始使用名为 ExByte
的数据泄露工具来窃取受害者的数据。

## 基本情况

最初 BlackByte 由 C 语言编写，最近的样本开始转向 Go 语言编写，也有一些是两种语言混合开发。大多数在野样本都是经过 UPX
加壳的，许多变种都由自定义的 UPX 壳加壳。

该恶意软件通常带有死神图标，在其长袍上写有字母 BB 代表 BlackByte。

![image.png-59kB](https://image.3001.net/images/20221213/1670943626_6398938a037dc0b889785.png!small)恶意软件图标

为了逃避检测，恶意软件使用了类似合法程序的文件描述。研究人员以伪装程亚马逊公司程序文件的恶意样本为例：

![image.png-81.2kB](https://image.3001.net/images/20221213/1670943626_6398938aa575c2000b537.png!small)文件描述伪装

## 系统检查

勒索软件如果发现系统语言为如下语言，就会直接退出不进行加密。

国家| 语言代码  
---|---  
亚美尼亚| 1067  
阿塞拜疆| 2092  
白俄罗斯| 1059  
哈萨克斯坦| 1087  
俄罗斯| 1049  
塔吉克斯坦| 1064  
乌兹别克斯坦| 2115  
乌克兰| 1058  
土库曼斯坦| 1090  
  
此外，恶意软件还会检测安全分析工具的 DLL 文件。如果存在，恶意软件也会立即退出。

DLL 文件名称| 描述  
---|---  
DBGHELP.DLL| Windows Dbg  
SbieDll.dll| Sandboxie  
SxIn.dll| Qihu 360  
Sf2.dll| Avast  
snxhl.dll| Avast  
cmdvrt32.dll| Comodo  
  
## 持久化

BlackByte 勒索软件会删除卷影副本和系统备份，以阻碍用户的数据恢复。删除命令如下：

> “cmd.exe /c start vssadmin.exe Delete Shadows /All /Quiet  
> vssadmin Resize ShadowStorage /For=K: /On=K: /MaxSize=401MB”

BlackByte 勒索软件会删除任务管理器与资源监视器，并且终止 Windows Defender 服务：

> cmd /c del C:\Windows\System32\Taskmgr.exe /f /q & del
> C:\Windows\System32\resmon.exe /f/q&  
> powershell -command "$x =
>
> [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String  
> ('V'+'wBp'+'A'+'G4AR'+'AB'+'lAG'+'YAZQBuAGQA'));Stop-Service -Name $x;Set-> Service-StartupType Disabled

## 文件类型

BlackByte 勒索软件不会加密以下文件扩展名的文件：

![image.png-58.9kB](https://image.3001.net/images/20221213/1670943627_6398938bd2f8e7e1913ae.png!small)不加密的文件扩展名

## 文件加密

BlackByte 勒索软件执行时会通过硬编码 URL 下载 spider.png，其中包含原始加密密钥。如果下载失败，进程会直接崩溃，加密过程终止。

BlackByte 勒索软件使用 AES 对称加密，为加密后的文件增加 .Blackbyte 扩展名。

## 勒索信息

加密完成后，名为 BlackByte_restoremyfiles.txt 的勒索信息会被放置在桌面上。

![image.png-241.3kB](https://image.3001.net/images/20221213/1670943628_6398938c940fc7b09dea2.png!small)勒索信息

攻击者为受害者提供了可以通过 Tor 浏览器访问的 URL，受害者可以通过网站查看如何支付赎金。

![image.png-1235.6kB](https://image.3001.net/images/20221213/1670943629_6398938df27f4ff1c8b91.png!small)暗网网站

## ExByte

最近研究人员发现 BlackByte 勒索软件开始使用名为 ExByte 的数据泄露工具，该工具是由 Go 语言编写的。

ExByte 在执行后会通过 IsDebuggerPresent 与 CheckRemoteDebuggerPresent
来检查是否在沙盒或者虚拟环境中运行。还会检查失陷主机上是否运行以下程序：

> x64dbg  
> x32dbg  
> OLLYDBG  
> WinDbg  
> The Interactive Disassembler  
> Immunity Debugger - [CPU]  
> MegaDumper 1.0 by CodeCracker / SnD  
> Import Reconstructor

检查是否存在以下反病毒和沙盒的 DLL 文件列表：

> avghooka.dll  
> avghookx.dll  
> sxin.dll  
> sf2.dll  
> sbiedll.dll  
> snxhk.dll  
> cmdvrt32.dll  
> cmdvrt64.dll  
> wpespy.dll  
> vmcheck.dll  
> pstorec.dll  
> dir_watch.dll  
> api_log.dll  
> dbghelp.dll

ExByte 将所有收集的文件都存储在 AppData/dummy，再上传到 Mega 云存储服务，账户凭据被硬编码在恶意软件中。

## 结论

 **BlackByte 的攻击势头近几个月没有放缓的迹象，而且持续在更新迭代。** 本次发现使用自定义数据泄露工具 ExByte，表明 BlackByte
勒索软件仍然在持续运营。

## Yara

    
    
    import "pe"
    rule BlackByte_Ransomware {
       meta:
          description = "Detects BlackByte Ransomware"
          author = "BlackBerry Threat Research Team"
          date = "2022-10-23"
          hash = "1df11bc19aa52b623bdf15380e3fded56d8eb6fb7b53a2240779864b1a6474ad"
          license = "This Yara rule is provided under the Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0) and open to any user or organization, as long as you use it under this license and ensure originator credit in any derivative to The BlackBerry Research & Intelligence Team"
    
       condition:
       (
       //PE File
       uint16(0) == 0x5a4d and
    
       //Imphash
       pe.imphash() == "7c3782f1285f48d8c9a17be8db65b02d" and
    
        pe.sections[0].name contains "UPX0" and
        pe.sections[1].name contains "UPX1" )
    }
    
    
    import "pe"
    
    rule BlackByte_Unpacked {
       meta:
          description = "Detects BlackByte Unpacked Ransomware"
          author = "BlackBerry Threat Research Team"
          date = "2022-10-23"
          license = "This Yara rule is provided under the Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0) and open to any user or organization, as long as you use it under this license and ensure originator credit in any derivative to The BlackBerry Research & Intelligence Team"
    
       strings:
          $s1 = "BlackByteGO/_cgo_gotypes.go" ascii wide
          $s2 = "main.DelShadows"
          $s3 = "main.Aes256Encr"
          $s4 = "main.ShowNote"
    
       condition:
       (
       //PE File
       uint16(0) == 0x5a4d and
    
       //All Strings
       all of ($s*) )
    }

## IOC

> 1df11bc19aa52b623bdf15380e3fded56d8eb6fb7b53a2240779864b1a6474ad  
> 94ce428f04f35e434dc9bd81e17fe506d8f81fe51ea40fca530f1f2ef00e2881  
> 0097b8722c8c0840e8c1a4dd579438344b3e6b4d630d17b0bbe9c55159f43142  
> hxxp://13.107[.]4.50/spider.png

## 参考来源

> [Blackberry](https://blogs.blackberry.com/en/2022/12/blackbyte-ransomware-> takes-an-extra-bite-using-double-extortion-methods)

