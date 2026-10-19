## 1.何为tracee

Tracee 是 Linux 的运行时安全和取证工具。它使用 Linux eBPF
技术在运行时跟踪您的系统和应用程序，并分析收集到的事件以检测可疑的行为模式。Tracee 由以下子项目组成：

Tracee-eBPF - 使用 eBPF 的 Linux 跟踪和取证程序

Tracee-Rules - 运行时安全规则检测引擎

## 2.安装tracee

 **运行tracee的必要条件**

> Linux 内核版本 >= 4.18
>
> Linux 内核头文件在常规位置下可用
>
> 系统库 libelf 和 zlib

 **快速开始安装**

    
    
    docker run --name tracee --rm --pid=host --privileged -v /tmp/tracee:/tmp/tracee -it aquasec/tracee:latest trace
    
    
    
    本条命令将仅启动原始跟踪 (Tracee-eBPF)，没有检测引擎 (Tracee-Rules)，用户将会看到如下的大量的原始事件输出：
    
    [root@localhost ~]# docker run --name tracee --rm --pid=host --privileged -v /tmp/tracee:/tmp/tracee -it aquasec/tracee:latest trace
    TIME             UID    COMM             PID     TID     RET              EVENT                ARGS
    06:16:20:529134  0      assist_daemon    719     759     0                security_file_open   pathname: /proc/stat, flags: O_RDONLY|O_LARGEFILE, dev: 5, inode: 4026532025
    06:16:20:529094  0      assist_daemon    719     759     7                open                 pathname: /proc/stat, flags: O_RDONLY|O_LARGEFILE|O_CLOEXEC, mode: 0
    06:16:20:529244  0      assist_daemon    719     759     0                close                fd: 7
    06:16:20:529274  0      assist_daemon    719     759     0                security_file_open   pathname: /proc/719/stat, flags: O_RDONLY|O_LARGEFILE, dev: 5, inode: 16789925
    06:16:20:529267  0      assist_daemon    719     759     7                open                 pathname: /proc/719/stat, flags: O_RDONLY|O_LARGEFILE|O_CLOEXEC, mode: 0
    06:16:20:529332  0      assist_daemon    719     759     0                close                fd: 7
    06:16:20:652683  0      systemd          1       1       0                security_file_open   pathname: /proc/1/mountinfo, flags: O_RDONLY|O_LARGEFILE, dev: 5, inode: 387752
    06:16:20:652646  0      systemd          1       1       21               openat               dirfd: -100, pathname: /proc/self/mountinfo, flags: O_RDONLY|O_CLOEXEC, mode: 0
    06:16:20:653013  0      systemd          1       1       0                lstat                pathname: /proc, statbuf: 0x7FFE8EE051E0
    

`每行是 Tracee-eBPF 收集的单个事件，包含以下信息：`

> TIME - 以秒为单位显示相对于系统启动时间的事件时间
>
> UID - 调用进程的真实用户 ID（在主机用户命名空间中）
>
> COMM - 调用进程的名称
>
> PID - 调用进程的pid
>
> TID - 调用线程的 tid
>
> RET - 函数返回的值
>
> EVENT - 标识事件（例如系统调用名称）
>
> ARGS - 函数的参数列表

## 3.使用tracee-rules检测可疑行为

目前官方未给出docker运行的方式，根据官方文档，可以从源码进行编译(cd tracee-rules &&
make),或者从release内下载编译好的包。为了方便测试，选择使用官方release包。

    
    
    wget https://github.com/aquasecurity/tracee/releases/download/v0.6.3/tracee.tar.gz
    cd dist
    
    sudo ./tracee-ebpf -o format:gob | ./tracee-rules --input-tracee file:stdin --input-tracee format:gob
    

以上命令会执行tracee-rules默认的检测规则，包含以下可疑行为的检测：

Name| Description| Tags  
---|---|---  
Standard Input/Output Over Socket| Redirection of process's standard
input/output to socket| "linux", "container"  
Anti-Debugging| Process uses anti-debugging technique to block debugger|
"linux", "container"  
Code injection| Possible code injection into another process| "linux",
"container"  
Dynamic Code Loading| Writing to executable allocated memory region| "linux",
"container"  
Fileless Execution| Executing a process from memory, without a file in the
disk| "linux", "container"  
kernel module loading| Attempt to load a kernel module detection| "linux",
"container"  
LD_PRELOAD| Usage of LD_PRELOAD to allow hooks on process| "linux",
"container"  
Container Host Mount| Mounting of the host filesystem into a container|
"container"  
Dropped Executable| Creation or dropping of an executable file from a
container at runtime| "linux", "container"  
Illegitimate Shell| Spawning of a shell program| "linux", "container"  
K8S API Connection| Connection to the Kubernetes cluster API server|
"container"  
K8S Service Account Use| Reading of the Kubernetes service account token file
in a container| "container"  
K8S TLS Certificate Theft| Accessing of the TLS certificate used for secure
communication between Kubernetes components| "linux", "container"  
  
我们可以简单的选用Fileless Execution(从内存执行进程，磁盘中没有文件)这个行为测试一下：

    
    
    wget https://github.com/abbat/elfexec/releases/download/v0.3/elfexec.x64.glibc.xz
    xz -d elfexec.x64.glibc.xz
    chmod u+x elfexec.x64.glibc && mv ./elfexec.x64.glibc ./elfexec
    
    echo '
    #include <unistd.h>
    
    int main(int argc, char* argv[])
    {
        write(STDOUT_FILENO, "Hello!\n", 7);
        return 0;
    }
    ' | cc -xc - -o /dev/stdout | elfexec
    

执行打印hello的命令以后，tracee-rules捕捉到结果如下：

    
    
    Loaded 14 signature(s): [TRC-1 TRC-13  TRC-2 TRC-3 TRC-11 TRC-9 TRC-4 TRC-5 TRC-12 TRC-8 TRC-6 TRC-10 TRC-7]
    
    *** Detection ***
    Time: 2021-11-04T07:55:05Z
    Signature ID: TRC-5
    Signature: Fileless Execution
    Data: map[]
    Command: elfexec
    Hostname: localhost
    

从返回中可以看出，该命令触发了TRC-5规则。

## 4.创建自定义规则

tracee-rules提供了两种方式自定义规则：使用.rego语言的规则文本，或使用go
Signature接口的规则。这里我们以rego规则示例，如何自定义规则，捕获可疑的系统行为。

 **rego规则**

根据示例规则文件，我们需要编写以下三个位置：

  1. `__rego_metadoc__`：定义规则元数据的文档规则。

  2. `tracee_selected_events`：定义事件选择器的集合规则。

  3. `tracee_match`：编写匹配逻辑，可以拥有多个trace_match块。  
笔者以编写一个监控`whoami`命令为例。需要监控whoami命令，则需要监视execve内核函数，并且执行的路径参数应该是whoami的文件路径。完整的规则文本如下：

    
    
    package tracee.TCR_1
    import data.tracee.helpers
    __rego_metadoc__ := {
        "id": "TCR-1",
        "version": "1.0.0",
        "name": "cmd whoami",
        "description": "cmd whoami",
        "tags": ["linux", "container"],
        "properties": {
            "Severity": 2,
            "MITRE ATT&CK": "cmd",
        }
    }
    eventSelectors := [
        {
            "source": "tracee",
            "name": "execve"
        }
    ]
    tracee_selected_events[eventSelector] {
    	eventSelector := eventSelectors[_]
    }
    tracee_match {
        input.eventName == "execve"
        pathname = helpers.get_tracee_argument("pathname")
        startswith(pathname, "/usr/bin/whoami")
    }
    

将此规则文件保存于rules目录下，重新启动tracee-rules即可监控到whoami命令的执行。

    
    
    Loaded 1 signature(s): [TCR-1]
    
    *** Detection ***
    Time: 2021-11-08T06:50:52Z
    Signature ID: TCR-1
    Signature: cmd whoami
    Data: map[]
    Command: bash
    Hostname: localhost
    

本文作者：常箭@涂鸦智能安全实验室

