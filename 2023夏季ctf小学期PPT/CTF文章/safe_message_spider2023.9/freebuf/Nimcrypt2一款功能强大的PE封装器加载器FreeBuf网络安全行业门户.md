## 关于Nimcrypt2

Nimcrypt2一款功能强大的PE封装器和加载器，该工具基于Nim开发，除了PE之外，该工具还支持对.NET、和原始Shellcode进行封装和加载。该工具能够通过尝试绕过AV/EDR来检测系统的安全性能。

该项目的前身为Nimcrypt，而Nimcrypt2则基于Nimcrypt增加了直接系统调用支持，并允许加载常规PE文件以及原始Shellcode。

## 功能介绍

> 1、NtQueueApcThread Shellcode执行
>
> 2、进程PID欺骗
>
> 3、第三方DLL屏蔽
>
> 4、使用系统调用（NimlineWhispers2 & GetSyscallStub）
>
> 5、系统调用名称随机化
>
> 6、支持加载.NET和常规PE文件
>
> 7、支持使用动态密钥生成技术的AES加密
>
> 8、支持LLVM模糊处理工具
>
> 9、字符串加密
>
> 10、沙箱绕过

## 已测试的操作系统平台

> Windows 11 (10.0.22000)
>
> Windows 10 21H2 (10.0.19044)
>
> Windows 10 21H1 (10.0.19043)
>
> Windows 10 20H2 (10.0.19042)
>
> Windows 10 19H2 (10.0.18363)
>
> Windows Server 2019 (10.0.17763)

## 工具安装&依赖

当前版本的Nimcrypt2仅支持在安装了Nim的Linux操作系统上运行，在安装Nim之前，我们必须确保已经通过包管理器安装了下列软件包：

    
    
    sudo apt install gcc mingw-w64 xz-utils git

接下来，我们可以使用[ _choosenim_](https://github.com/dom96/choosenim)来安装Nim：

    
    
    curl https://nim-lang.org/choosenim/init.sh -sSf | sh
    
    echo "export PATH=$HOME/.nimble/bin:$PATH" >> ~/.bashrc
    
    export PATH=$HOME/.nimble/bin:$PATH

Nimcrypt2还有一些其他的依赖组件，我们可以通过Nimble来安装：

    
    
    nimble install winim nimcrypto docopt ptr_math strenc

安装完所有的工具依赖组件之后，我们就可以使用下列命令将Nimcrypt2的源码克隆至本地：

    
    
    git clone https://github.com/icyguider/Nimcrypt2.git

接下来，我们就要使用下列命令来编译Nimcrypt2了：

    
    
    nim c -d=release --cc:gcc --embedsrc=on --hints=on --app=console --cpu=amd64 --out=nimcrypt nimcrypt.nim

## 可选配置

如需使用Obfuscator-LLVM选项，我们必须在系统中安装Obfuscator-LLVM和wclang。下列步骤可以指引你在Kali
Linux系统上完成安装与配置：

> 1、将Obfuscator-LLVM克隆至本地，然后完成代码构建；
>
> 2、编译完成后，备份现有版本的clang，然后将新的Obfuscator-LLVM版的clang拷贝到“/usr/bin/”；
>
> 3、安装wclang，并将其代码路径添加至PATH中；
>
> 4、备份现有clang库文件，将新构建的Obfuscator-LLVM库拷贝到“/usr/lib/clang/OLD_VERSION/”；

除此之外，我们还需要将下列文件内容添加到你的nim.cfg文件中，并将nim指向你的wclang代码：

    
    
    amd64.windows.clang.exe = "x86_64-w64-mingw32-clang"
    
    amd64.windows.clang.linkerexe = "x86_64-w64-mingw32-clang"
    
    amd64.windows.clang.cpp.exe = "x86_64-w64-mingw32-clang++"
    
    amd64.windows.clang.cpp.linkerexe = "x86_64-w64-mingw32-clang++"

此时，我们就可以运行下列命令来查看输出信息了：

    
    
    x86_64-w64-mingw32-clang -v

## 工具帮助信息

    
    
    ___                                           
    
                       .-'   `'.                                        
    
                      /         \                                       
    
                      |         ;                                       
    
                      |         |           ___.--,                     
    
             _.._     |0) ~ (0) |    _.---'`__.-( (_.                   
    
      __.--'`_.. '.__.\    '--. \_.-' ,.--'`     `""`                   
    
     ( ,.--'`   ',__ /./;   ;, '.__.'`    __                            
    
     _`) )  .---.__.' / |   |\   \__..--""  ""'--.,_                    
    
    `---' .'.''-._.-'`_./  /\ '.  \ _.-~~~````~~~-._`-.__.'             
    
          | |  .' _.-' |  |  \  \  '.               `~---`              
    
           \ \/ .'     \  \   '. '-._)                                  
    
            \/ /        \  \    `=.__`~-.   Nimcrypt v2               
    
       jgs  / /\         `) )    / / `"".`\                             
    
      , _.-'.'\ \        / /    ( (     / /  3-in-1 C#, PE, & Raw Shellcode Loader
    
       `--~`   ) )    .-'.'      '.'.  | (                              
    
              (/`    ( (`          ) )  '-;                             
    
               `      '-;         (-'                                   
    
     
    
    Nimcrypt v 2.0
    
     
    
    Usage:
    
      nimcrypt -f file_to_load -t csharp/raw/pe [-o <output>] [-p <process>] [-n] [-u] [-s] [-e] [-g] [-l] [-v]
    
      nimcrypt (-h | --help)
    
     
    
    Options:
    
      -h --help                显示帮助信息
    
      --version                现实版本信息
    
      -f --file filename          要加载的文件
    
      -t --type filetype          文件类型（csharp, raw, 或pe）
    
      -p --process process     Shellcode要注入的进程名称
    
      -o --output filename      编译后的exe文件名
    
      -u --unhook              解除ntdll.dll钩子
    
      -v --verbose             执行过程中启用Verbose消息
    
      -e --encrypt-strings       使用strenc模块加密字符串
    
      -g --get-syscallstub       使用GetSyscallStub代替NimlineWhispers2
    
      -l --llvm-obfuscator       使用Obfuscator-LLVM来编译代码
    
      -n --no-randomization    启用系统调用名称随机化
    
      -s --no-sandbox         禁用沙盒检测

## 项目地址

 **Nimcrypt2：** 【[ _GitH_ _ub_ _传送门_](https://github.com/icyguider/Nimcrypt2)】

## 参考资料

> [
> _https://github.com/icyguider/nimcrypt_](https://github.com/icyguider/nimcrypt)
>
> [
> _https://github.com/byt3bl33d3r/OffensiveNim_](https://github.com/byt3bl33d3r/OffensiveNim)
>
> [ _https://github.com/S3cur3Th1sSh1t/Nim-> RunPE_](https://github.com/S3cur3Th1sSh1t/Nim-RunPE)
>
> [
> _https://github.com/S3cur3Th1sSh1t/NimGetSyscallStub_](https://github.com/S3cur3Th1sSh1t/NimGetSyscallStub)
>
> [
> _https://twitter.com/ShitSecure/status/1482428360500383755_](https://twitter.com/ShitSecure/status/1482428360500383755)
>
> [
> _https://github.com/ajpc500/NimlineWhispers2_](https://github.com/ajpc500/NimlineWhispers2)
>
> [
> _https://github.com/dom*96/choosenim﻿_](https://github.com/dom96/choosenim)

