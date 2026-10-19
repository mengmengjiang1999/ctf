## 漏洞描述

7月20日，微软确认了一个新的本地提权漏洞，安全研究成员将其称为HiveNightmare或者SeriousSAM，该漏洞允许低权限的用户访问Windows系统文件。成功利用此漏洞的攻击者可以使用SYSTEM特权运行任意代码。然后攻击者就可以安装程序、查看更改删除数据或创建具有完全用户权限的新账户经过身份认证的攻击者可利用此漏洞在目标设备上以SYSTEM
权限运行任意代码

微软发文称，由于多个系统文件（包括安全账户管理器数据库SAM）过度许可访问控制列表，导致出现本地提权漏洞

通过该漏洞，攻击者可以获得%windir%\system32\config目录中文件的权限。一般情况下，注册表文件（如 SAM
文件）始终由操作系统运行，因此当用户尝试访问这些文件时，将会显示访问违规，这是因为文件由其他程序打开并锁定

但是，由于注册表文件（包括 SAM）通常由Windows卷影副本备份，这意味着攻击者可以在不违反访问规定的情况下通过卷影副本访问这些文件

而这最终导致的结果是，如果系统驱动器的VSS卷影副本可用，低权限用户可以利用该漏洞访问注册表文件来实现以下目的：

  * 提取和利用帐户密码

  * 发现原始的 Windows 安装密码

  * 获取 DPAPI 计算机密钥，可用于解密所有计算机私钥

  * 获取计算机帐户，可用于银票攻击

目前 POC 和 EXP 已经被公开，利用公开的 POC 可以低权限账号读取 SAM 等文件

## 环境搭建

靶机系统下载地址链接

    
    
    ed2k://|file|cn_windows_10_business_editions_version_1809_updated_sept_2019_x64_dvd_f873d037.iso|5444462592|BF3C1964141BCF6ACD40EC6AAF2A0940|/ 
    

打开安装Vmware的安装Windows虚拟机的过程请自行百度

如果你的系统在这个范围内，想知道自己的系统是否容易受到攻击，可以从低权限命令提示符中使用以下命令：

    
    
    icacls c:\windows\system32\config\sam
    

如果输出Access is denied 或拒绝访问，则说明不容易受到攻击

![图片.png](https://image.3001.net/images/20230712/1689140629_64ae3d95864f425cc6e5d.png!small)

如果你看到输出结果是：BUILTIN\USERS:(I)(RX)，表面您的系统存在漏洞（RX代表[READ/EXecute权限）

![图片.png](https://image.3001.net/images/20230712/1689140642_64ae3da210e855642ecb0.png!small)

## 漏洞影响

  * Windows 10 Version 20H2 for ARM64-based Systems

  * Windows 10 Version 20H2 for 32-bit Systems

  * Windows 10 Version 20H2 for x64-based Systems

  * Windows 10 Version 2004 for x64-based Systems

  * Windows 10 Version 2004 for ARM64-based Systems

  * Windows 10 Version 2004 for 32-bit Systems

  * Windows 10 Version 21H1 for 32-bit Systems

  * Windows 10 Version 21H1 for ARM64-based Systems

  * Windows 10 Version 21H1 for x64-based Systems

  * Windows 10 Version 1909 for ARM64-based Systems

  * Windows 10 Version 1909 for x64-based Systems

  * Windows 10 Version 1909 for 32-bit Systems

  * Windows 10 Version 1809 for ARM64-based Systems

  * Windows 10 Version 1809 for x64-based Systems

## 漏洞复现

EXP下载地址：`https://github.com/GossiTheDog/HiveNightmare`  
作者已经编译好的利用脚本下载地址：`https://github.com/GossiTheDog/HiveNightmare/releases/tag/0.6`

直接将作者编译好的 HiveNightmare.exe 拷贝到目标系统上执行

 **注** ：在虚拟机复现导出SAM可能会报以下错误

![图片.png](https://image.3001.net/images/20230712/1689140665_64ae3db9644f348d4e8dd.png!small)

这是因为虚拟机中系统保护可能没有打开，也不会自动创建系统还原点，这里就需要自己手动去开启系统保护并创建一个系统还原点，右键点击此电脑->属性->系统保护->配置->启用系统保护

![图片.png](https://image.3001.net/images/20230712/1689140679_64ae3dc7379b08b8ed1bb.png!small)

然后再点击“创建”设置一个还原点

![图片.png](https://image.3001.net/images/20230712/1689140691_64ae3dd33e665c97697ec.png!small)

然后使用

    
    
    vssadmin list shadows
    

命令查看会有一个卷影

![图片.png](https://image.3001.net/images/20230712/1689140703_64ae3ddff045151db000f.png!small)

此时再来使用HiveNightmare.exe导出SAM，可以看到导出成功

![图片.png](https://image.3001.net/images/20230712/1689140716_64ae3dec098aeec124dbf.png!small)

接下来我们就可以使用kali中impacket包中的secretsdump.py导出靶机上所有账号的hash值了

我们先进入impacket的路径下

    
    
    cd /usr/share/doc/python3-impacket/examples
    

![图片.png](https://image.3001.net/images/20230712/1689140727_64ae3df773720d5915ad0.png!small)

然后再将目标主机中的三个文件拷贝到impacket中的相同目录下，如图所示：

![图片.png](https://image.3001.net/images/20230712/1689140739_64ae3e031e0f25645a0a3.png!small)

然后执行以下的命令导出hash值

    
    
    python3 secretsdump.py -sam SAM-2023-07-12 -system SYSTEM-2023-07-12 -security SECURITY-2023-07-12 LOCAL
    

![图片.png](https://image.3001.net/images/20230712/1689140750_64ae3e0e54e3f87e9829a.png!small)

## 漏洞修复

们建议尽快安装此安全更新。如果您不得不延迟安装此安全更新，我们建议您使用以下解决方法：

限制对 %windir%\system32\config 内容的访问

命令提示符（以管理员身份运行）：icacls %windir%\system32\config*.* /inheritance:e

Windows PowerShell （以管理员身份运行）：icacls $env:windir\system32\config*.*
/inheritance:e

删除卷影复制服务 (VSS) 卷影副本

删除 %windir%\system32\config 访问限制之前存在的任何系统还原点和卷影卷。

新建一个系统还原点（如果需要）

 **警告** ：从备份还原您的系统也可能同时恢复过于宽松的 ACL，从而将您的系统恢复到易受攻击的状态。还原备份后，您必须验证 ACL
是否正确，确保还原操作不会重新引入此漏洞

