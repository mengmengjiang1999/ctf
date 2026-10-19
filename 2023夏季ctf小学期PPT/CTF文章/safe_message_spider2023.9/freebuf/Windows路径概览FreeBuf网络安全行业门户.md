# Windows 路径概览

## 0x00 前言

​ windows 中有多少路径支持，你知道吗？本文就简单讲下对windows的路径的理解，在不同漏洞中利用的技巧。

## 0x01 几种常见路径

在微软文档里面，总共定义了如下路径形式，通过 **RtlDetermineDosPathNameType_U** 函数判断。

    
    
    enum RTL_PATH_TYPE {
      RtlPathTypeUnknown,
      RtlPathTypeUncAbsolute,
      RtlPathTypeDriveAbsolute,
      RtlPathTypeDriveRelative,
      RtlPathTypeRooted,
      RtlPathTypeRelative,
      RtlPathTypeLocalDevice,
      RtlPathTypeRootLocalDevice
    };
    
    RTL_PATH_TYPE NTAPI RtlDetermineDosPathNameType_U(_In_ PCWSTR Path);
    

  1. W32path: `C:\Windows\System32\csrss.exe`

  2. Ntpath:

    * `\GLOBAL??\C:\Windows\System32\csrss.exe`

    * `\??\C:\Windows\System32\csrss.exe`

    * `\SystemRoot\System32\csrss.exe`

  3. LocalDevice: `\\.\C:\Windows\System32\csrss.exe`

  4. RootLocalDevice:`\\?\C:\Windows\System32\csrss.exe`

  5. DosPath主要对于文件名过长的简写，`C:\PROGRA~1`与`C:\Program Files`

## 0x02 路径转换和使用详解

​
比如将`C:\Windows\System32\csrss.exe`、`\\.\C:\Windows\System32\csrss.exe`、`\\?\C:\Windows\System32\csrss.exe`当传递给类似
`CreateFile`API
时，对象管理器会处理为`\??\C:\Windows\System32\csrss.exe`，可以看到最终都转为Ntpath进行下一步的操作。

​ 通常object manager会有如下映射（在老版本系统中可能不一致）：

​ `C:\`=>`\Device\HarddiskVolume3`

​ `\Device\HarddiskVolume3`=>`\Device\BootDevice`

​ `\SystemRoot`=>`\Device\BootDevice\windows`

这里做个简单的实验来了解下不同的路径使用效果：

  1. `echo . > \??\%CD%\test.txt.`利用ntpath路径写入一个文件名为小数点结尾的文件

  2. `notepad test.txt.`尝试打开，会报错文件不存在

  3. `del /f \\?\%CD%\test.txt.`使用rootlocaldevice的方式删除文件，`\??\%CD%\test.txt.`和`\\.\%CD%\test.txt.`都是不能删除的

在使用”某些“的路径时，斜杠和点转换如下：

 _Dos Path_|  _Full Path_|  _NT Path_  
---|---|---  
X:/ABC/DEF| X:\ABC\DEF| ??\X:\ABC\DEF  
X:\ABC\\..\XYZ| X:\XYZ| ??\X:\XYZ  
X:\ABC\\..\\..\\..| X:\| ??\X:\  
  
当盘符的冒号后直接加上路径时，会被转为当前路径在拼接，如下图大家可以多尝试：

 _Dos Path_|  _Full Path_|  _NT Path_  
---|---|---  
X:DEF\GHI| X:\ABC\DEF\GHI| ??\X:\ABC\DEF\GHI  
X:| X:\ABC| ??\X:\ABC  
Y:| Y:\DEF| ??\Y:\DEF  
Z:| Z:\| ??\Z:\  
X:ABC\\..\XYZ| X:\ABC\XYZ| ??\X:\ABC\XYZ  
X:ABC\\..\\..\\..| X:\| ??\X:\  
  
![image](https://image.3001.net/images/20220824/1661353423_63063dcfb3a29160f7ca7.png!small)

![image](https://image.3001.net/images/20220824/1661353433_63063dd9149745898016c.png!small)

![image](https://image.3001.net/images/20220824/1661353443_63063de3bc9a5d6a12a85.png!small)

 **神奇的路径**

​ 在windows路径中，有一种`::\`路径，这其实是Explorer 使用一种特殊的格式来引用 shell 对象，例如在cmd中执行`start
::{20d04fe0-3aea-1069-a2d8-08002b30309d}`会打开文件夹管理器。只要路径的第二个字符是冒号，转换就会将其视为
Drive Absolute 或 Drive Relative 路径。

## 0x03 UNC 路径

​ 通用命名约定 (UNC) 路径是一种几乎只能在 Windows 上找到的类型（尽管可以说 URI
取代了它们在其他所有东西上的作用）。它们用于访问远程文件系统，通常是 SMB，但几乎可以是任何实现，例如
WebDAV（默认安装）或许多虚拟化共享文件夹实现之一。按照惯例，UNC 路径以两个路径分隔符开头，一个是服务器地址（无论是域名还是 IP
地址），然后是该服务器上共享的名称。最后，之后指定所需资源的相对路径。

 _Dos Path_|  _Full Path_|  _NT Path_  
---|---|---  
\\\server\share\ABC\DEF| \\\server\share\ABC\DEF| ??\UNC\server\share\ABC\DEF  
\\\server| \\\server| ??\UNC\server  
//server/share/ABC/DEF| \\\server\share\ABC\DEF| ??\UNC\server\share\ABC\DEF  
\\\server\share\ABC\\..\XYZ| \\\server\share\XYZ| ??\UNC\server\share\XYZ  
\server\share\ABC\\..\\..\\..| \\\server\share| ??\UNC\server\share  
  
​ **本地设备路径** 是以序列`\\.\`开头的任何路径。这看起来像一个服务器名称为“.”的 UNC 路径，但它用于直接转义到 DosDevices
对象管理器目录。该目录包含驱动器号和内核驱动程序的符号链接等内容。它最常用于访问 COM 端口和命名管道等设备。

 _Dos Path_|  _Full Path_|  _NT Path_  
---|---|---  
\\\\.\COM20| \\\\.\COM20| ??\COM20  
\\\\.\pipe\mypipe| \\\\.\pipe\mypipe| ??\pipe\mypipe  
\\\\.\X:/ABC/DEF| \\\\.\X:\ABC\DEF| ??\X:\ABC\DEF  
\\\\.\X:\ABC\\..\XYZ| \\\\.\X:\XYZ| ??\X:\XYZ  
\\\\.\X:\ABC\\..\\..\C:\| \\\\.\C:\| ??\C:\  
\\\\.\pipe\mypipe\\..\notmine| \\\\.\pipe\notmine| ??\pipe\notmine  
  
`\\localhost\xyz`与`\\.\xyz`是不同的，前者通过IP访问一个共享，后者是访问一个管道，不能认为localhost等于点。为了对原DOS的支持，不能使用以下名称，更多命名规则可参考：https://docs.microsoft.com/zh-cn/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN

  * PRN

  * AUX

  * NUL

  * CON

  * LPT[1-9]

  * COM[1-9]

  * CONIN$

  * CONOUT$

针对这些名称，后面跟冒号或者引号都会忽略后面的内容，`X:\COM1:blah`或`X:\COM1.blah`-> `\\.\COM1`

## 0x04 小Tricks

 **绕过UNC检测**

`\\.\C:\abc\xyz`会被判断为UNC，但是`\\?\C:\abc\xyz`却不会。本地设备路径始终被视为 UNC 路径，根本地设备路径不被视为
UNC 路径，但是如果后面跟着 _UNC_ ，比如`\\?\UNC\abc\xyz`，也会被认为是UNC路径。以下路径也是可利用标准 GLOBALROOT
符号链接来创建文件：

\\\?\GLOBALROOT??\UNC\abc\xyz  
---  
\\\?\GLOBALROOT\DosDevices\UNC\abc\xyz  
\\\?\GLOBALROOT\Device\Mup\abc\xyz  
\\\?\GLOBALROOT\Device\LanManRedirector\abc\xyz  
\\\?\GLOBALROOT\Device\WebDavRedirector\abc\xyz  
  
![image](https://image.3001.net/images/20220824/1661353469_63063dfdb50296997adb9.png!small)

其中 _LanManRedirector或_ WebDavRedirector _条目_
，是指向\Device\Mup;NAME的符号，`\\;LanmanRedirector\evil.com\xyz`=>`\Device\Mup\;LanmanRedirector\evil.com\xyz`，`\\;WebDavRedirector\evil.com\xyz`=>`\Device\Mup\;WebDavRedirector\evil.com\xyz`

 **蓝屏**

`\\\\.\globalroot\device\condrv\kernelconnect`某些版本可以

 **读取sam文件**

`\\\??\C:\system~1\systemrestore\new-sam`如果存在，默认低权限用户使用filetest ntcreatefile读取

`cmd /c copy
\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit c:\temp\
& `

`copy
\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM
c:\temp\ & `

`copy
\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SECURITY
c:\temp\`

 **RPC的替换**

\RPC Control
可以使用如下替换`\BaseNamedObjects\Restricted\Sessions\<your_sess_id>\BaseNamedObjects`

 **Hyper-v**

hyper-v
开启的，普通用户可以通过ntcreatefile:`\Device\STORVSP\vSMB\??\c:\windows\system32\phoneinfo.dll`创建文件。

## 0x03 总结

所有的路径方式都可以通过此工具来测试调用，http://www.zezula.net/download/filetest.zip，当然也可查看源码了解此函数如何工作：https://github.com/reactos/reactos/blob/master/modules/rostests/apitests/ntdll/RtlDetermineDosPathNameType.c，其中常用路径转换的函：
_RtlDosPathNameToNtPathName_U_ ， _RtlDosPathNameToRelativeNtPathName_U_ ，
_RtlDetermineDosPathNameType_U_
，GetFullPathName。我也搞了个小工具来测试：https://github.com/Nan3r/Dos2NtPath，后面会讲解如何利用这些特性去绕过补丁。

