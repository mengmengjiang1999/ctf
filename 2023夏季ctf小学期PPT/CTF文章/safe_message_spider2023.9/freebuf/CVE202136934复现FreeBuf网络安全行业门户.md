## 漏洞简介

微软在7月20日发布紧急安全公告，公开了一个Windows提权漏洞。由于对多个系统文件（包括安全帐户管理器 (SAM) 数据库）的访问控制列表 (ACL)
过于宽松，攻击者可读取SAM，SYSTEM，SECURITY等文件内容，进而获取用户NTLM
Hash值，从而通过解密Hash值或Hash传递等方法造成特权提升漏洞。成功利用此漏洞的攻击者可以使用 SYSTEM 权限运行任意代码。

## 影响范围

微软确认此问题会影响 Windows 10 版本 1809 和更新的操作系统，其他版本还在确认中。

## 环境配置

操作系统：本文使用Windows 10 2004 (19041.450)  
启用administrator用户：`net user administrator /active:yes`  
设置密码：`net user administrator 1qaz2wsx`  
关闭Defender：`reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows
Defender" /v "DisableAntiSpyware" /d 1 /t REG_DWORD /f`  
关闭防火墙：`netsh advfirewall set allprofiles state off`  
启用文件和打印机共享服务：`net start lanmanserver`

## 创建系统还原点

右键“此电脑->属性”，点击“系统保护->配置->启用系统保护->应用->确定”，如图：  
![image](https://image.3001.net/images/20210724/1627119505_60fbdf91ebef90508a36b.png!small)输入描述然后点击“创建”按钮创建还原点，如图：  
![image](https://image.3001.net/images/20210724/1627119515_60fbdf9b2d2b3453075bb.png!small)

## 漏洞复现

使用[GossiTheDog提供的工具](https://github.com/GossiTheDog/HiveNightmare)转储SAM，SYSTEM和SECURITY文件，如图：  
![image](https://image.3001.net/images/20210724/1627119531_60fbdfaba72c098b4caa0.png!small)

使用`impacket-secretsdump`工具获取用户Hash值，如图：  
![image](https://image.3001.net/images/20210724/1627119547_60fbdfbbbede10ca695b2.png!small)

使用`impacket-psexec`工具，通过传递Hash利用SMB服务获取目标系统SYSTEM权限，如图：  
![image](https://image.3001.net/images/20210724/1627119556_60fbdfc4b1dd138a1c45f.png!small)

## 处置建议

1、禁用默认管理员用户：`net user administrator /active:no`

2、限制对`%windir%\system32\config`内容的访问:

    
    
    # 命令提示符（以管理员身份运行）
    icacls %windir%\system32\config\*.* /inheritance:e
    
    # Windows PowerShell（以管理员身份运行）
    icacls $env:windir\system32\config\*.* /inheritance:e
    

但是我使用该方法失败了，如图  
![image](https://image.3001.net/images/20210724/1627119575_60fbdfd759920ca5aadce.png!small)

再次读取文件，如图：  
![image](https://image.3001.net/images/20210724/1627119584_60fbdfe0d2d5496ff5f5d.png!small)

3、删除所有系统还原点和删除卷影复制服务（VSS）卷影副本。该方法会影响删除卷影副本可能会影响还原操作，包括使用第三方备份应用程序还原数据的能力。有关如何删除卷影副本的详细信息，请参阅[KB5005357-删除卷影副本](https://support.microsoft.com/zh-cn/topic/kb5005357-%E5%88%A0%E9%99%A4%E5%8D%B7%E5%BD%B1%E5%89%AF%E6%9C%AC-1ceaa637-aaa3-4b58-a48b-baf72a2fa9e7)。

