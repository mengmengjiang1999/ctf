**今天给大家介绍的是一款名叫Swap
Digger的工具，大家可以利用这款工具自动化搜索并提取Linux用户凭证、Web表单凭证、Web表单邮件、HTTP认证数据、WiFi
SSID和密钥等等。**

Swap_Digger是一个Bash脚本，它可以自动对目标Linux系统进行数据提取和分析，它不仅能给取证人员提供数据支持，而且还能给渗透测试人员提供后渗透阶段所需的信息。

## 下载并运行工具

在本地主机上打开命令行终端，输入下列命令下载并运行Swap_Digger脚本：

    
    
    alice@1nvuln3r4bl3:~$git clone <https://github.com/sevagas/swap_digger.git>
    
    alice@1nvuln3r4bl3:~$cd swap_digger
    
    alice@1nvuln3r4bl3:~$chmod +x swap_digger.sh
    
    alice@1nvuln3r4bl3:~$sudo ./swap_digger.sh -v

在加载的硬盘驱动器上，首先使用下列命令下载脚本：

    
    
    alice@1nvuln3r4bl3:~$git clone <https://github.com/sevagas/swap_digger.git>
    
    alice@1nvuln3r4bl3:~$cd swap_digger
    
    alice@1nvuln3r4bl3:~$chmod +x swap_digger.sh

接下来，寻找目标swap文件/分区：

    
    
    alice@1nvuln3r4bl3:~$sudo ./swap_digger.sh -S

最后，运行下列命令对目标进行分析：

    
    
    alice@1nvuln3r4bl3:~$sudo ./swap_digger.sh -vx -r path/to/mounted/target/root/fs -spath/to/target/swap/device

在第三方设备上，使用下列命令下载并运行脚本（可用于渗透测试和CTF）：

    
    
    alice@1nvuln3r4bl3:~$wget<https://raw.githubusercontent.com/sevagas/swap_digger/master/swap_digger.sh>
    
    alice@1nvuln3r4bl3:~$chmod +x swap_digger.sh
    
    alice@1nvuln3r4bl3:~$sudo ./swap_digger.sh -vx

## 简单运行

如果你只需要恢复出Linux用户的明文密码，可以直接运行下列命令：

    
    
    alice@1nvuln3r4bl3:~$sudo ./swap_digger.sh

## 可用选项

    
    
    ./swap_digger.sh[ OPTIONS ]
    
     Options : 
    
      -x, --extended    Run Extended tests on the target swap toretrieve other interesting data
    
            (web passwords, emails, wifi creds,most accessed urls, etc)
    
      -g, --guessing  Try to guess potential passwords based onobservations and stats
    
            Warning: This option is not reliable,it may dig more passwords as well as hundreds false positives.
    
      -h, --help   Display this help.
    
      -v, --verbose Verbose mode.
    
      -l, --log Log all outputs in a log file(protected inside the generated working directory).
    
      -c, --clean Automatically erase the generatedworking directory at end of script (will also remove log file)
    
      -r PATH, --root-path=PATH   Location of the target file-system root(default value is /)
    
            Change this value for forensic analysiswhen target is a mounted file system.
    
            This option has to  be used along the -s option to indicate pathto swap device.
    
      -s PATH, --swap-path=PATH   Location of swap device or swap dump toanalyse
    
            Use this option for forensic/remoteanalysis of a swap dump or a mounted external swap partition.
    
            This option should be used with the -roption where at least /<root-path>/etc/shadow exists.
    
      -S, --swap-search   Search for all available swap devices (usefor forensics).

## 相关资源

<http://blog.sevagas.com/?Digging-passwords-in-Linux-swap>  

 ***参考来源：[kitploit](https://www.kitploit.com/2018/10/swap-digger-tool-that-automates-swap.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+PentestTools+%28PenTest+Tools%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

