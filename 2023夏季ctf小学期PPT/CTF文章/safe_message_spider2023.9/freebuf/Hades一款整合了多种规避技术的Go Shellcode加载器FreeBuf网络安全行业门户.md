![](https://image.3001.net/images/20230607/1686129019_6480497b7b784f99f6e44.jpeg!small)  

## 关于Hades

Hades是一款整合了多种规避技术的Go
Shellcode加载器，当前版本的Hades只是一个概念验证程序，旨在帮助广大研究人员尝试绕过流行AV/EDR的安全防御机制，并以此来验证安全防护产品的能力。

## 工具要求

由于该工具基于Go语言开发，因此我们首先需要在本地设备上安装并配置好最新版本的Go环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地，并使用make命令在Linux操作系统上完成项目代码构建：

    
    
    git clone https://github.com/f1zm0/hades && cd hades
    
    make

## 工具使用

接下来，我们就可以将生成的可执行文件拷贝到x64 Windows主机中，并使用下列命令来运行Hades：

    
    
    .\hades.exe [options]

我们可以使用-h选项来查看工具的帮助信息：

    
    
    PS > .\hades.exe -h
    
     
    
      '||'  '||'     |     '||''|.   '||''''|   .|'''.|
    
       ||    ||     |||     ||   ||   ||  .     ||..  '
    
       ||''''||    |  ||    ||    ||  ||''|      ''|||.
    
       ||    ||   .''''|.   ||    ||  ||       .     '||
    
      .||.  .||. .|.  .||. .||...|'  .||.....| |'....|'
    
     
    
              version: dev [11/01/23] :: @f1zm0
    
     
    
    Usage:
    
      hades -f <filepath> [-t selfthread|remotethread|queueuserapc]
    
     
    
    Options:
    
      -f, --file <str>        Shellcode文件路径（默认.bin）
    
      -t, --technique <str> 要使用的注入技术，包括[selfthread, remotethread, queueuserapc]

## 工具使用样例

使用[ _queueuserapc技术_](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc)注入Shellcode并执行calc.exe：

    
    
    .\hades.exe -f calc.bin -t queueuserapc

## 工具使用演示

使用系统调用RAV排序绕过用户模式钩子（NtQueueApcThread挂钩[ _frida_ _-_
_trace_](https://frida.re/)和[
_自定义Handler_](https://github.com/f1zm0/hades/blob/main/scripts/NtQueueApcThread.js)）：

![](https://image.3001.net/images/20230607/1686129071_648049af7b25cba292f0b.gif!small)

使用间接系统调用实现指令回调绕过（注入的DLL来源于[ _jackullrich_](https://twitter.com/winternl_t)的[
_syscal_ _-detect_](https://github.com/jackullrich/syscall-detect)）:

![](https://image.3001.net/images/20230607/1686129106_648049d2dd1ba8b0e64d3.gif!small)

## 杂项-直接系统调用版本

在最新发布版本中，直接系统调用功能被替换成了[
_acheron_](https://github.com/f1zm0/acheron)提供的间接系统调用。出于某些原因，你可能想要使用之前的加载器版本（使用直接系统调用），那么你需要显式地将direct_syscalls标签传递给编译器，编译器将决定在构建过程中需要包含或排除哪些文件：

    
    
    GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -tags='direct_syscalls' -o dist/hades_directsys.exe cmd/hades/main.go

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3_ _._
_0_](https://github.com/f1zm0/hades/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Hades** ：【[ _GitHub传送门_](https://github.com/f1zm0/hades)】

## 参考资料

> [ _https://github.com/f1zm0/acheron_](https://github.com/f1zm0/acheron)
>
> [ _https://pkg.go.dev/unsafe_](https://pkg.go.dev/unsafe)
>
> [ _https://go.dev/doc/asm_](https://go.dev/doc/asm)
>
> [ _https://frida.re/_](https://frida.re/)
>
> [
> _https://github.com/f1zm0/hades/blob/main/scripts/NtQueueApcThread.js_](https://github.com/f1zm0/hades/blob/main/scripts/NtQueueApcThread.js)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-> processthreadsapi-queueuserapc_](https://docs.microsoft.com/en-> us/windows/win32/api/processthreadsapi/nf-processthreadsapi-queueuserapc)

