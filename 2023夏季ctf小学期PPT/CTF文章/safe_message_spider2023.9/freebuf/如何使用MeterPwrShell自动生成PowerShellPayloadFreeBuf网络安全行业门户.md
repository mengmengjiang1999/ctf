![](https://image.3001.net/images/20210505/1620194923_6092366b840379cc10087.png!small)

## 关于MeterPwrShell

MeterPwrShell是一款功能强大的自动化工具， **可以帮助广大研究人员以自动化的形式生成完美的PowerShell Payload。**
MeterPwrShell基于[ _Metasploit框架_](https://github.com/rapid7/metasploit-framework)和[ _amsi.fail_](https://amsi.fail/)实现其功能，可以生成PowerShell One-Liner，并能够创建Meterpreter Shell，而且还可以绕过AMSI、防火墙、UAC和任意反病毒产品。

## 功能介绍

使用PrependMigrate实现自动化免杀；

自动从普通用户提权为SYSTEM权限；

禁用所有的防火墙配置；

绕过Windows Defender实时保护功能；

Payload免杀；

绕过AMSI；

简单的代码，One-Liner；

绕过防火墙；

方便的命令行接口；

......

## 注意事项

切勿将此程序生成的Payload上传到任何在线扫描服务；

切勿将此程序用于恶意目的；

请不要尝试Fork这个代码库；

所有的Payload功能都已在Windows 10 v20H2平台上进行过测试。

## MeterPwrShell和Metasploit框架中的web_delivery模块对比

更简短的脚本代码（One-Liner）；

不需要为Stager安装服务器；

支持内置Ngrok；

自动内置Privesc；

可轻松绕过Windows Defender；

## 工具要求

Kali Linux、Ubuntu或Debian；

Metasploit框架；

接入网络（目标主机和攻击者主机都需要）；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/GetRektBoy724/MeterPwrShell.git

## 工具使用

    
    
    # ./MeterPwrShell2Kalix64 -c help
    
     Available arguments : help, version, showbanner, showlastdebuglog   
    help : Show this page   
    version : Show MeterPwrShell's version   
    showbanner : Show MeterPwrShell's Banner                   
    
     showlastdebuglog : Well,Its kinda self-explanatory tho       

## 攻击向量

BadUSB

恶意快捷方式（[ _lnk2pwn_](https://github.com/it-gorillaz/lnk2pwn/)）

恶意宏文档Payload

MS DDE漏洞利用

在目标设备上执行命令以利用任意漏洞

## 项目地址

MeterPwrShell：【[ _GitHub传送门_](https://github.com/GetRektBoy724/MeterPwrShell)】

## 参考资料

> [ _https://github.com/rapid7/metasploit-> framework_](https://github.com/rapid7/metasploit-framework)
>
> [ _https://amsi.fail/_](https://amsi.fail/)
>
> [
> _https://gist.github.com/GetRektBoy724/9383c9580cb1c9935fc04cc7eb7ef004_](https://gist.github.com/GetRektBoy724/9383c9580cb1c9935fc04cc7eb7ef004)
>
> [ _https://blog.sevagas.com/Bypass-Antivirus-Dynamic-> Analysis_](https://blog.sevagas.com/Bypass-Antivirus-Dynamic-Analysis)
>
> [ _https://github.com/it-gorillaz/lnk2pwn/﻿_](https://github.com/it-> gorillaz/lnk2pwn/)

