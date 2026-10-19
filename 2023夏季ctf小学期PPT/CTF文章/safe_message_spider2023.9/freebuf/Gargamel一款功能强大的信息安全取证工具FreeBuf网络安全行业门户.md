![](https://image.3001.net/images/20210310/1615357396_604865d40cdbddf35a073.png!small)

## Gargamel

Gargamel是一款基于Rust开发的信息安全取证工具，广大研究人员可以使用Gargamel来完成日常的信息取证任务。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Lifars/gargamel.git

## 项目编译

假设你已经在本地设备上安装并配置好了Rust v1.41+，打开终端窗口，并切换到项目目录下，输入下列命令即可编译项目：

    
    
    cargo build --release

我们可以使用下列命令编译调试构建：

    
    
    cargo build

已编译好的可执行文件可以在target/release/gargamel.exe或target/debug/gargamel.exe路径下找到。

## 设置日志等级

我们可以按照下列方式修改工具的日志记录等级：

> 打开src/main.rs；
>
> 在第42和43行，将LevelFilter::Info修改为LevelFilter::Trace即可查看更多详细日志信息；
>
> 注意，LevelFilter::Trace将会记录下包括密码在内的所有内容；

## 用户指南

现在，这款应用程序仅支持在Windows系统上运行，目标设备必须是Windows或Linux系统。你还需要确保下列程序已经存储在了跟Gargamel相同的目录之中：

> psexec：【[ _下载_](https://docs.microsoft.com/en-> us/sysinternals/downloads/psexec)】
>
> paexec：【[ _下载_](https://www.poweradmin.com/paexec/)】
>
> winpmem：【[ _下载_](https://github.com/Velocidex/c-aff4/releases)】
>
> plink和pscp：【[
> _下载_](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)】
>
> SharpRDP：【[
> _下载_](https://github.com/vildibald/SharpRDP/releases/tag/v1.0.0)】
>
> WMImplant：【[ _下载_](https://github.com/vildibald/WMImplant)】
>
> exe：【[ _下载_](https://www.7-zip.org/download.html)】

## Gargamel的使用

Gargamel需要在具备高级权限的终端中启动才能完全发挥其功能。目前，它不支持UAC对话框，也不支持在有限权限下运行时的任何类型的通知。当以有限的用户权限运行时，一些操作（如目标内存转储）将不起作用。

### 基础使用

假设你想要连接到一台带有下列参数的计算机：

> 地址：192.168.42.47
>
> 用户名：Jano
>
> 密码：nbusr123

下列命令将利用PsExec方法获取防火墙状态、网络状态、登录用户、运行进程、活动网络连接、注册表、系统&应用事件日志。获取到的取证信息将存储在Gargamel的testResults目录下：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec -o testResults

Gargamel将会询问输入远程用户的密码，我们这里的密码为nbusr123。注意，密码在输入过程中是隐藏的。

我们还可以直接在命令行参数中指定用户名和密码：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec -p nbusr123 -o testResults

### 域使用

假设你想要连接到域中一台带有下列参数的计算机：

> 域：WORKSPACE
>
> 计算机名：JanovPC
>
> 用户名：Jano
>
> 密码：nbusr123

下列命令将利用PsExec方法获取防火墙状态、网络状态、登录用户、运行进程、活动网络连接、注册表、系统&应用事件日志：

    
    
    gargamel.exe -c JanovPC -u Jano -d WORKSPACE --psexec -o testResults

或者，直接在命令行参数中指定目标设备信息：

    
    
    gargamel.exe -c JanovPC -u Jano -d WORKSPACE --psexec -p nbusr123 -o testResults

### 其他连接方式

PsExec是其中一种支持的连接方法，我们可以将--psexec替换为下列选项：

> \--psexec
>
> \--psrem
>
> \--rdp
>
> \--wmi
>
> \--ssh

我们也可以一次使用多种方法。比如说，同时使用PsExec和RDP：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec --rdp -o testResults

### 获取内存

为了获取内存导转储，可以直接在参数后添加-m选项：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec -o testResults -m

如果你只需要获取内存转储而不需要其他取证信息，可以直接使用下列命令：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec -o testResults -m --no-events-search --no-evidence-search --no-registry-search

这个功能目前仅支持目标为Windows系统的主机。

### 运行自定义命令

Gargamel可以在远程主机中运行自定义Windows CMD或Linux Shell命令。

我们需要使用下列内容创建一个custom-commands.txt文件：

    
    
    # Will be run using any method
    
    ipconfig
    
    # Will run only when launching with at least one of --all, --psexec, --wmi methods
    
    :psexec:wmi ipconfig -all

接下来，我们就可以使用-e选项来运行上述命令了：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec -o testResults -e custom-commands.txt

### 下载自定义文件

Gargamel能够下载远程文件，首先我们需要使用下列内容创建一个custom-files.txt文件：

    
    
    C:\Users\Public\sss*
    
    C:\Users\Jano\danove.pdf
    
    # This line and the next one will be ignored
    
    # C:\Users\Jano\somBajecny.pptx  

接下来，我们就可以使用-s选项来运行上述命令了：

    
    
    gargamel.exe -c 192.168.42.47 -u Jano --psexec -o testResults -s custom-files.txt

## 所有选项

    
    
    USAGE:
    
        gargamel.exe [FLAGS] [OPTIONS] --user <user>
    
     
    
    FLAGS:
    
        -a, --all                   Acquire evidence from Windows machine using all supported methods (PsExec, PsRemote,
    
                                    WMI, RDP).
    
            --no-events-search      Disables Windows event logs acquisition.
    
            --no-evidence-search    Disables acquisition of evidence that can be usually downloaded quickly (like ipconfig,
    
                                    firewall status etc..)
    
            --no-registry-search    Disables target registry acquisition.
    
        -h, --help                  Prints help information
    
        -m, --mem-image             Optional: Memory dump of a target Windows machine.
    
            --local                 Acquire evidence from local machine.
    
            --nla                   Optional: Use network level authentication when using RDP. (Windows targets only)
    
            --no-7z                 Optional: Disable 7zip compression for registry & memory images.This will significantly
    
                                    decrease the running time, but WMI and RDP connections will probably not work properly.
    
                                        (Windows targets only)
    
            --psexec                Acquire evidence from Windows machine using PsExec. Requires both PsExec64.exe and
    
                                    paexec.exe in the current directory or in the path.
    
            --psrem                 Acquire evidence from Windows machine using PowerShell. Requires both PsExec64.exe and
    
                                    paexec.exe in the current directory or in the path.
    
            --rdp                   Acquire evidence from Windows machine using RDP. Requires SharpRDP.exe in the current
    
                                    directory or in the path.
    
            --ssh                   Acquire evidence from Linux machine using SSH. Requires both plink.exe and pscp.exe in
    
                                    the current directory or in the path.
    
        -V, --version               Prints version information
    
            --wmi                   Acquire evidence from Windows machine using WMI. Requires WMImplant.ps1 in the current
    
                                    directory or in the path and PowerShell 3.0+ on the host machine.Note: It is necessary
    
                                    to disable Windows Defender real-time protection (other AVs not tested).
    
     
    
    OPTIONS:
    
        -c, --computer <computer>                        Remote computer address/name. [default: 127.0.0.1]
    
        -u, --user <user>                                Remote user name
    
        -d, --domain <domain>                            Optional: Remote Windows domain
    
        -o, --output <local-store-directory>
    
                Name of local directory to store the evidence [default: evidence-output]
    
     
    
        -p, --password <password>
    
                Optional: Remote user password. Skipping this option will prompt a possibility to put a password in hidden
    
                way.To specify an empty password use `-p ""`
    
     
    
            --redownload <re-download>
    
                Optional: Download and DELETE specified file from target computer. Use this in case of previous failed
    
                partially completed operation. For just downloading a file (without deleting it) please use a `search`
    
                switch. If you specify a 7zip chunk (.7z.[chunk-number], e.g. .7z.004), then it will also automatically try to
    
                download subsequent chunks.Use also with --psexec --psrem, --rdp, --wmi, --all
    
     
    
        -r, --remote-storage <remote-store-directory>
    
                Name of remote directory to be used as a temporary storage. (Windows targets only) [default:
    
                C:\Users\Public]
    
     
    
        -e, --commands <custom-command-path>             Optional: File with custom commands to execute on remote computer
    
     
    
        -s, --search <search-files-path>
    
                Optional: File with files names to be searched on remote computer. File names supports also `*` and `?`
    
                wildcards on file names (but not yet parent directories).
    
     
    
            --key <ssh-key>                              Optional: Name/path of SSH private key file. (Linux target only)
    
     
    
            --timeout <timeout>
    
                Optional: Timeout in seconds for long running operations.This option is a workaround for a bug in
    
                WMImplant.ps1 amd SharpRDP.exe where finishing of a long running operation cannot sometimes properly close
    
                the connection leaving the Gargamel in seemingly frozen state or executing the next operation with the
    
                previous one unfinished on target site.Increasing this timeout may solve issues when acquiring registry or
    
                memory image from target machine. [default: 300]

## 存在的问题

> WMI无法将输出写入至包含“_”符号的路径/文件名中。

## 项目地址

Gargamel：【[ _GitHub传送门_](https://github.com/Lifars/gargamel)】

