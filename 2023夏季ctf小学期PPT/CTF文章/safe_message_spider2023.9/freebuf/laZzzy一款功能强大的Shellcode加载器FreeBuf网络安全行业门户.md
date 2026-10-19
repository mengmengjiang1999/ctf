## 关于laZzzy

laZzzy是一款功能强大的Shellcode加载器，该工具使用了各种不同的开源代码库实现其功能，能够给广大研究人员更好地演示恶意软件所使用的常见的不同代码执行技术。

## 功能介绍

> 1、直接系统调用和本地函数（Nt*）调用（支持绝大多数本地函数）；
>
> 2、IAT（导入地址表）绕过；
>
> 3、Payload加密（AES、异或）：随机生成密钥、自动填充Payload（\x90）、在内存中逐字节解密Payload；
>
> 4、字符串异或加密；
>
> 5、PPID欺骗；
>
> 6、屏蔽非微软签名的DLL；
>
> 7、（可选）克隆PE图标和属性；
>
> 8、（可选）使用伪造的证书进行 代码签名；

## 使用的代码库

> [ _kokke/tiny-AES-c_](https://github.com/kokke/tiny-AES-c)
>
> [ _skadro-official/skCrypter_](https://github.com/skadro-official/skCrypter)
>
> [
> _JustasMasiulis/lazy_importer_](https://github.com/JustasMasiulis/lazy_importer)
>
> [
> _JustasMasiulis/inline_syscall_](https://github.com/JustasMasiulis/inline_syscall)

## 工具依赖

Windows系统 + Visual Studio + C++ Clang：

![](https://image.3001.net/images/20221220/1671532601_63a19039024baba04caa3.png!small)

![](https://image.3001.net/images/20221220/1671532607_63a1903fe176a8eb243e3.png!small)

Python 3和相关模块：

    
    
    python3 -m pip install -r requirements.txt

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/capt-meelo/laZzzy.git

![](https://image.3001.net/images/20221220/1671532622_63a1904ea426a68c4a3bd.png!small)

## 支持的Shellcode执行技术

> 1、Early-bird APC队列注入
>
> 2、线程劫持
>
> 3、KernelCallbackTable
>
> 4、线程挂起
>
> 5、LineDDA回调
>
> 6、EnumSystemGeoID回调
>
> 7、FLS回调
>
> 8、SetTimer
>
> 9、剪贴板

## 工具使用样例

执行builder.py后，提供工具所需的信息，我们便会看到如下所示的样例输出：

    
    
    (venv) PS C:\MalDev\laZzzy> python3 .\builder.py -s .\calc.bin -p CaptMeelo -m 1 -pp explorer.exe -sp C:\\Windows\\System32\\notepad.exe -d www.microsoft.com -b C:\\Windows\\System32\\mmc.exe
    
     
    
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣤⣤⣤⠀⢀⣼⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀⣿⣿⠀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⢀⣼⡿⠁⠀⠛⠛⠒⠒⢀⣀⡀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀⣿⣿⠀⠀⣰⣾⠟⠋⠙⢻⣿⠀⠀⠛⠛⢛⣿⣿⠏⠀⣠⣿⣯⣤⣤⠄⠀⠀⠀⠀⠈⢿⣷⡀⠀⣰⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀⣿⣿⠀⠀⣿⣯⠀⠀⠀⢸⣿⠀⠀⠀⣠⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⣰⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀⣿⣿⠀⠀⠙⠿⣷⣦⣴⢿⣿⠄⢀⣾⣿⣿⣶⣶⣶⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⠀⠀by: CaptMeelo⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠁⠀⠀⠀
    
     
    
    [+] XOR-encrypting payload with
    
            [*] Key:                        d3b666606468293dfa21ce2ff25e86f6
    
     
    
    [+] AES-encrypting payload with
    
            [*] IV:                         f96312f17a1a9919c74b633c5f861fe5
    
            [*] Key:                        6c9656ed1bc50e1d5d4033479e742b4b8b2a9b2fc81fc081fc649e3fb4424fec
    
     
    
    [+] Modifying template using
    
            [*] Technique:                  Early-bird APC Queue
    
            [*] Process to inject:          None
    
            [*] Process to spawn:           C:\\Windows\\System32\\RuntimeBroker.exe
    
            [*] Parent process to spoof:    svchost.exe
    
     
    
    [+] Spoofing metadata
    
            [*] Binary:                     C:\\Windows\\System32\\RuntimeBroker.exe
    
            [*] CompanyName:                Microsoft Corporation
    
            [*] FileDescription:            Runtime Broker
    
            [*] FileVersion:                10.0.22621.608 (WinBuild.160101.0800)
    
            [*] InternalName:               RuntimeBroker.exe
    
            [*] LegalCopyright:             © Microsoft Corporation. All rights reserved.
    
            [*] OriginalFilename:           RuntimeBroker.exe
    
            [*] ProductName:                Microsoft® Windows® Operating System
    
            [*] ProductVersion:             10.0.22621.608
    
     
    
    [+] Compiling project
    
            [*] Compiled executable:        C:\MalDev\laZzzy\loader\x64\Release\laZzzy.exe
    
     
    
    [+] Signing binary with spoofed cert
    
            [*] Domain:                     www.microsoft.com
    
            [*] Version:                    2
    
            [*] Serial:                     33:00:59:f8:b6:da:86:89:70:6f:fa:1b:d9:00:00:00:59:f8:b6
    
            [*] Subject:                    /C=US/ST=WA/L=Redmond/O=Microsoft Corporation/CN=www.microsoft.com
    
            [*] Issuer:                     /C=US/O=Microsoft Corporation/CN=Microsoft Azure TLS Issuing CA 06
    
            [*] Not Before:                 October 04 2022
    
            [*] Not After:                  September 29 2023
    
            [*] PFX file:                   C:\MalDev\laZzzy\output\www.microsoft.com.pfx
    
     
    
    [+] All done!
    
            [*] Output file:                C:\MalDev\laZzzy\output\RuntimeBroker.exe

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/capt-meelo/laZzzy/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **laZzzy** ：【[ _GitHub传送门_](https://github.com/capt-meelo/laZzzy)】

## 参考资料

> [
> _http://undocumented.ntinternals.net/_](http://undocumented.ntinternals.net/)
>
> [
> _https://doxygen.reactos.org/index.html_](https://doxygen.reactos.org/index.html)
>
> [
> _https://github.com/processhacker/phnt_](https://github.com/processhacker/phnt)
>
> [ _https://www.vergiliusproject.com/_](https://www.vergiliusproject.com/)
>
> [ _https://www.ired.team/_](https://www.ired.team/)
>
> [
> _https://github.com/snovvcrash/DInjector_](https://github.com/snovvcrash/DInjector)
>
> [
> _https://github.com/aahmad097/AlternativeShellcodeExec_](https://github.com/aahmad097/AlternativeShellcodeExec)
>
> [
> _https://github.com/paranoidninja/CarbonCopy_](https://github.com/paranoidninja/CarbonCopy)
>
> [ _https://github.com/kokke/tiny-AES-c_](https://github.com/kokke/tiny-> AES-c)
>
> [ _https://github.com/skadro-official/skCrypter_](https://github.com/skadro-> official/skCrypter)
>
> [
> _https://github.com/JustasMasiulis/lazy_importer_](https://github.com/JustasMasiulis/lazy_importer)
>
> [
> _https://github.com/JustasMasiulis/inline_syscall_](https://github.com/JustasMasiulis/inline_syscall)

