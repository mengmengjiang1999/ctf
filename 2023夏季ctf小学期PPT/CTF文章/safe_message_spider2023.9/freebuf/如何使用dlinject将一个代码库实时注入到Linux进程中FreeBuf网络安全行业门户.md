![](https://image.3001.net/images/20220708/1657294576_62c84ef01e854593350ca.jpeg!small)

## 关于dlinject

dlinject是一款针对Linux进程安全的注入测试工具，在该工具的帮助下，广大研究人员可以在不使用ptrace的情况下，轻松向正在运行的Linux进程中注入一个共享代码库（比如说任意代码）。之所以开发该工具，是因为目前社区有非常多的[
_反ptrace技术_](https://www.aldeid.com/wiki/Ptrace-anti-debugging)，而dlinject的功能并不基于ptrace实现，因此渗透测试的效果会更好。

## 工具运行机制

>
> 1、该工具首先会向目标进程发送终止运行的信号，并定位_dl_open()方法。接下来，该工具将会通过/proc/[pid]/syscall获取RIT和RSP；
>
> 2、此时，工具将会利用/proc/[pid]/mem对部分堆栈数据 以及需要使用Shellcode重写的代码进行备份；
>
> 3、生成主要和次要Shellcode缓冲区；
>
> 4、工具会通过写入/proc/[pid]/mem将第一部分Shellcode代码注入到RIP；
>
>
> 5、第一部分Shellcode会做下列三件事情：将常见注册表项注入到堆栈；通过mmap()加载第二部分Shellcode；跳转到第二部分Shellcode；
>
>
> 6、第二部分Shellcode会做下列几件事情：将备份的堆栈信息和程序代码恢复成原始状态；调用_dl_open()以加载指定的代码库，所有的构造器都会正常加载和执行；还原注册表状态和堆栈状态，重新回到SIGSTOP设置的原始状态；

## 工具下载

该工具基于Python开发，因此广大研究人员首先需要在本地设备上安装并配置好Python环境。

接下来，我们可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/DavidBuchanan314/dlinject.git

## 工具使用

![](https://image.3001.net/images/20220708/1657294602_62c84f0ad5c4a36baedfa.png!small)

## 参数解释

    
    
    pid：待注入目标进程的进程ID；
    
    /path/to/lib.so：需要注入（加载）的共享库路径，必须和目标进程的cwd关联；
    
    -h, --help：显示工具帮助信息和退出；
    
    --stopmethod {sigstop,cgroup_freeze,none}：设置在Shellcode执行之前终止目标进程，设置SIGSTOP（默认）可能会有一些副作用，而cgroup_freeze则需要root权限；

## 工具演示视频

 **演示视频** ：【[ _点我观看_](https://asciinema.org/a/290906)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/DavidBuchanan314/dlinject/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **dlinject** ：【[ _GitHub传送门_](https://github.com/DavidBuchanan314/dlinject)】

## 参考资料

> [
> _https://github.com/AonCyberLabs/Cexigua_](https://github.com/AonCyberLabs/Cexigua)
>
> [ _https://github.com/gaffe23/linux-> inject_](https://github.com/gaffe23/linux-inject)
>
> [ _https://www.aldeid.com/wiki/Ptrace-anti-> debugging_](https://www.aldeid.com/wiki/Ptrace-anti-debugging)

