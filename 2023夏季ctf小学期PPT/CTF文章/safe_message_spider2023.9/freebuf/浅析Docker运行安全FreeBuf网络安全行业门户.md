## 一、docker run 语法

语法：

    
    
    docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
    

## 二、 Docker 运行安全相关参数

### 2.1 启用 AppArmor

AppArmor 主要的作用是设置某个可执行程序的访问控制权限，可以限制程序 读/写某个目录/文件，打开/读/写网络端口等等。

Apparmor 的配置文件保存在/etc/apparmor.d/containers/目录下

配置文件使用官方文档下的 Nginx 配置实例，见<https://docs.docker.com/engine/security/apparmor/>

加载一个新的配置文件

    
    
    $ sudo apparmor_parser -r -W /etc/apparmor.d/containers/docker-nginx
    

上传新的配置文件

    
    
    $ apparmor_parser -R /path/to/profile
    

在 Docker 里使用 AppArmor

    
    
    $ docker run --security-opt "apparmor=docker-nginx" -p 80:80 -d --name apparmor-nginx nginx
    

### 2.2 启用 SELinux

配置步骤

在宿主机上启用 SELinux，Docker 守护进程启用 SELinux，默认启动容器就开启了 SELinux

    
    
    [root@localhost selinux]# sestatus
    SELinux status: enabled
    SELinuxfs mount: /sys/fs/selinux
    SELinux root directory: /etc/selinux
    Loaded policy name: targeted
    Current mode: enforcing
    Mode from config file: enforcing
    Policy MLS status: enabled
    Policy deny_unknown status: allowed
    Max kernel policy version: 31
    [root@localhost selinux]# docker info
    ...
    init version: fec3683
    Security Options:
    seccomp
    WARNING: You're not using the default seccomp profile
    Profile: /etc/docker/seccomp/default-no-chmod.json
    selinux
    userns
    Kernel Version: 3.10.0-1062.12.1.el7.x86_64
    ...
    

测试，挂载宿主机`/`目录到容器的`/hacking`目录

    
    
    [root@localhost selinux]# docker run -it --rm -v /:/hacking centos:latest /bin/sh
    sha256:fe8d824220415eed5477b63addf40fb06c3b049404242b31982106ac204f6700
    Status: Downloaded newer image for centos:latest
    sh-4.4# cd /
    sh-4.4# ls
    bin dev etc hacking home lib lib64 lost+found media mnt opt proc root run sbin srv sys tmp usr var
    sh-4.4# cd hacking/
    sh-4.4# ls
    bin boot dev etc home lib lib64 media mnt opt proc root run sbin srv sys tmp usr var
    sh-4.4# cd var/log
    sh-4.4# ls
    ls: cannot open directory '.': Permission denied
    

运行参数可以选择 SELinux 的级别，标签包含 4 个部分`User:Role:Type:level`，可以设置 SELinux
不同的标签设定运行级别。

    
    
    docker run --security-opt label=type:spc_t replicated
    
    docker run --interactive --tty --security-opt label=level:TopSecret centos /bin/bas
    
    docker run -it --security-opt label:disable alpine sh
    

标签

    
    
    [root@localhost ~]# ls /etc/selinux/targeted/contexts/files/
    file_contexts file_contexts.homedirs file_contexts.subs media
    file_contexts.bin file_contexts.homedirs.bin file_contexts.subs_dist
    [root@localhost ~]# cat /etc/selinux/targeted/contexts/files/file_contexts
    

### 2.3 限制运行容器的内核功能

Linux内核能够将root用户的特权分解为称为功能的不同单元。例如，CAP_CHOWN功能允许root用户对文件UID和GID进行任意更改。CAP_DAC_OVERRIDE功能允许root用户绕过文件读取，写入和执行操作的内核权限检查。与Linux
root用户相关的几乎所有特殊功能都分解为单独的功能。

更细粒度的功能限制可以：

从 root 用户帐户中删除单个功能，使其功能/危险性降低。

以非常精细的级别向非root用户添加特权。

功能适用于文件和线程。文件功能允许用户以更高的特权执行程序。这类似于setuid位的工作方式。线程功能跟踪正在运行的程序中功能的当前状态。

默认情况下，Docker使用白名单方法删除除所需功能之外的所有功能。

启动命令

    
    
    docker run --rm -it --cap-drop $CAP alpine sh
    
    docker run --rm -it --cap-add $CAP alpine sh
    
    docker run --rm -it --cap-drop ALL --cap-add $CAP alpine sh
    

$CAP 包含<http://man7.org/linux/man-pages/man7/capabilities.7.html>，在 Linux
接近40项的 Capabilities 中，Docker为了确保容器的安全，仅仅支持了其中的14项基本的
Capabilities：CAP_CHOWN、CAP_DAC_OVERRIDE、CAP_FSETID、CAP_MKNOD、FOWNER、NET_RAW、SETGID、SETUID、SETFCAP、SETPCAP、NET_BIND_SERVICE、SYS_CHROOT、KILL和AUDIT_WRITE。

测试命令

    
    
    $ docker container run --rm -it alpine chown nobody /
    
    $ docker container run --rm -it --cap-drop ALL --cap-add CHOWN alpine chown nobody /
    
    $ docker container run --rm -it --cap-drop CHOWN alpine chown nobody /
    
    $ docker container run --rm -it --cap-add chown -u nobody alpine chown nobody /
    

### 2.4 不使用特权模式运行容器

特权模式参数--privileged，运行特权容器时允许容器内用户直接访问宿主机的资源，因此通过滥用特权容器，攻击者可以获取宿主机资源的访问权限。特权容器产生后，由于增强权限的许多，攻击者可能会以root权限运行代码。这表明攻击者可以以root权限运行主机，包括CAP_SYS_ADMIN。

攻击者在获取了暴露的特权容器访问权限后，就可以进一步发起很多攻击活动。攻击者可以识别出主机上运行的软件，并找出和利用相关漏洞。还可以利用容器软件漏洞或错误配置，比如使用弱凭证或没有认证的容器。由于攻击者有root访问权限，因此恶意代码或挖矿机都可以执行并有效地隐藏。

测试

创建容器：

    
    
    docker run -d -name centos7 --privileged=true centos:7 /usr/sbin/init
    

进入容器：

    
    
    docker exec -it centos7 /bin/bash
    

### 2.5 限制容器获取新的特权，使用--security-opt=no-new-privileges

含义如下：

> 进程可以在内核中设置no_new_privs位，该位在fork，clone和exec之间持续存在。
>
> no_new_privs位可确保该进程或其子进程不会获得任何其他特权。
>
> 设置no_new_privs位后，该进程将无法取消设置。
>
> 即使进程使用设置了文件功能位的setuid二进制文件或可执行文件执行，也不允许带有no_new_privs的进程更改uid /
> gid或获得任何其他功能。
>
>
> no_new_privs还可以防止SELinux之类的Linux安全模块（LSM）过渡到不允许访问当前进程的进程标签。这意味着SELinux进程仅允许转换为具有较少特权的进程类型。

testnnp.c，打印 uid 信息

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <sys/types.h>
    
    int main(int argc, char *argv[])
    {
            printf("Effective uid: %d\n", geteuid());
            return 0;
    }
    

编译

    
    
    [root@localhost ~]# make testnnp
    cc testnnp.c -o testnnp
    

制作镜像，`dockerfile`

    
    
    FROM fedora:latest
    ADD testnnp /root/testnnp
    RUN chmod +s /root/testnnp
    ENTRYPOINT /root/testnn
    

制作测试镜像

    
    
    [root@localhost ~]# docker build -t testnnp .
    

测试

    
    
    # docker run -it --rm --user=1000  testnnp
    

使用`no-new-privileges`

    
    
    # docker run -it --rm --user=1000 --security-opt=no-new-privileges testnnp
    

### 2.6 使用 cgroup 确保容器在定义的 cgroup 中运行

不使用--cgroup-parent选项 ，控制组 CGroups 是 Linux 内核的另一个重要特性，主要用来实现对资源的限制和审计等.

![](https://image.3001.net/images/20200326/1585233161_5e7cbd098a499.jpg!small)

控制组（cgroup）是Linux内核的一项功能，可让您限制访问进程和容器对系统资源（如CPU，RAM，IOPS和网络）的访问权限。

    
    
    $ docker run -d –name='low_prio' –cpuset-cpus=0 –cpu-shares=20 busybox md5sum /dev/urandom
    

### 2.7 启用 seccomp

前面讲 docker 守护进程安全时，说过 seccomp 是组内核安全策略，不同的策略有不同的名称，可以在 docker
运行时指定使用的安全策略，而不是使用 docker 守护进程设置的默认策略。seccomp=unconfined表示不启用
seccomp，下面是不建议的启动命令。

    
    
    $ docker container run --rm -it --security-opt seccomp=unconfined debian:jessie sh
    

指定 sccomp

    
    
    $ docker run --rm -it --security-opt seccomp=default-no-chmod.json alpine sh
    

### 2.8 运行容器不挂载主机的系统分区

包括：

> /
>
> /boot
>
> /dev
>
> /etc
>
> /lib
>
> /proc
>
> /sys
>
> /usr

### 2.9 容器根目录以只读方式挂载--read-only

使用--read-only会限制运行容器的跟目录为只读

    
    
    [root@localhost ~]# docker run -it --read-only 72300a873c2c /bin/bash
    root@f077b480dbe5:/# ls bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var root@f077b480dbe5:/# touch 111
    touch: cannot touch '111': Read-only file system
    

如果需要挂载的目录有读写权限可以使用更细的权限控制，如挂载特定目录有读写权限。

    
    
    docker run --interactive --tty --read-only -v /opt/app/data:/run/app/data:rw centos /bin/bash
    

### 2.10 不挂载宿主机的docker.sock到任何容器

![](https://image.3001.net/images/20200326/1585233172_5e7cbd147841c.png!small)

安装Docker之后，Docker守护进程会监听Unix域套接字：/var/run/docker.sock。

下面的命令用于运行容器，并采用交互模式(interactive mode，该模式下会直接进入容器内)，同时绑定docker.sock。

    
    
    # docker run -v /var/run/docker.sock:/var/run/docker.sock -ti alpine sh
    

绑定Docker套接字之后，容器的权限会很高，可以控制Docker守护进程。

### 2.11 不使用共享的挂载传播模式

不使用--volume=/hostPath:/containerPath:shared的配置

    
    
    # docker run <Run arguments> --volume=/hostPath:/containerPath:shared <Container Image Name or ID> <Command> 
    

### 2.12 不要直接挂载主机设备，如果需要，设置成只读

避免容器内用户直接修改设备信息。

    
    
    docker run --interactive --tty --device=/dev/tty0:/dev/tty0:rw --device=/dev/temp_sda:/dev/temp_sda:r centos bash 
    

### 2.13 on-failure容器重启策略设置为 5

通过在docker run命令中使用--restart标志，您可以指定重启策略，以指定容器在启动失败时应如何重启。
您应该选择onfailure重新启动策略，并将重新启动尝试限制为5次。

如果无限期地尝试启动容器，则可能导致宿主机上的拒绝服务，尤其是在同一主机上有多个容器的情况下。
此外，忽略容器的退出状态并始终尝试重新启动容器，会导致无法调查导致容器终止的根本原因。
如果某个容器被终止，则应调查其背后的原因，而不仅仅是尝试无限期地重新启动它。 应该使用失败时重新启动策略将容器重新启动的次数限制为最多5次尝试。

    
    
    docker run --detach --restart=on-failure:5 nginx
    

### 2.14 不使用网络空间共享

\--net=hostHost模式并没有为容器创建一个隔离的网络环境，该模式下的 Docker 容器会和 host 宿主机共享同一个网络
namespace，所以容器可以和宿主机一样，使用宿主机的eth0，实现和外界的通信，特点：

> 这种模式下的容器没有隔离的network namespace
>
> 容器的 IP 地址同 Docker主机的 IP 地址
>
> 要注意容器中服务的端口号不能与Docker主机上已经使用的端口号相冲突
>
> host模式能够和其它模式共存

### 2.15 主机进程命名空间不共享，禁用--pid=host

默认下，所有的容器都启用了PID命名空间。PID命名空间提供了进程的分离。PID命名空间删除系统进程视图，允许进程ID可重用，包括pid 1。

在一些情况下需要容器共享主机进程命名空间，基本上允许容器内的进程可以查看主机的所有进程。例如，构建了一个带调试工具容器，想在容器使用这些工具来调试主机的进程。

如果使用--pid=host参数，容器可以直接操作宿主机上的数据。如果 dockerd 守护进程设置了用户命名空间映射，运行容器时使用该参数会导致启动失败。

    
    
    docker run --interactive --tty --pid=host centos /bin/bash 
    

### 2.16 主机 IPC 命名空间不共享，禁用`--ipc=host`

进程与单个"管理程"进程共享内存，以便交换数据( 通过使用共享缓冲区) 。 这个解决方案是为了性能需求实现的。  
`--ipc=MODE`：设置容器的IPC模式，`shareable`自己的私有IPC名称空间，可以与其他容器共享。`host`：使用主机系统的IPC名称空间。

禁止使用`host`模式，下面是错误的示例：

    
    
    docker run --interactive --tty --ipc=host centos /bin/bash 
    

可以与其他容器使用共享 IPC

    
    
    docker run --ipc=container:<id> <image>
    docker run -d --ipc=shareable data-server
    docker run -d --ipc=container:data-server data-client
    

### 2.17 不共享主机 UTS 命名空间，禁用--uts=host

UTS命名空间用于设置主机名和对该命名空间中正在运行的进程可见的域。默认下，所有的容器，包括那么以--network=host运行的容器，有它们自己的UTS命名空间。设置UTS为host将使容器使用与主机相同的UTS命名空间。注意--hostname在host UTS模式是无效的。

当你想在主机更改hostname之后，同时也更改同样的hostname到容器。

### 2.18 不共享主机用户命名空间，禁用--users=host

默认情况下，Docker守护程序以root身份运行。 这使守护程序可以创建并使用启动容器所需的内核结构。 但是，它也存在潜在的安全风险。

默认的容器以 root 账号运行

    
    
    # docker run --rm alpine id
    
    # docker run --rm --user 1000:1000 alpine id
    
    # docker run --rm --privileged --userns=host alpine id
    

### 2.19 限制容器运行时占用内存和 CPU

常用于限制 CPU 和内存的参数

> -c --cpu-shares参数只能限制容器使用 CPU 的比例
>
> \--cpus后面跟着一个浮点数，代表容器最多使用的核数，可以精确到小数点二位，也就是说容器最小可以使用 0.01 核 CPU
>
> -m --memory：容器能使用的最大内存大小，最小值为 4m
>
> \--memory-swap：容器能够使用的 swap 大小

### 2.20 必要时 Docker 运行覆盖默认的ulimit

docker 守护进程可以配置默认的限制，必要时可以使用 docker run 命令覆盖的默认

    
    
    # docker run --ulimit nofile=1024:1024 --interactive --tty centos /bin/bash 
    

### 2.21 使用--pids-limit限制指定时间内生成的进程数

使用PID cgroup参数--pids-limit可以通过限制在指定时间范围内容器内部可能创建的进程数量来防止逻辑**类的攻击。

    
    
    # docker run -it --pids-limit 100 <Image_ID>
    

### 2.22 运行时检查容器运行状态，使用--health-cmd参数

用于检查容器的运行状态

    
    
    # docker run -d --name db --health-cmd "curl --fail http://localhost:8091/pools || exit 1" --health-interval=5s --timeout=3s arungupta/couchbase
    

### 2.23 传入容器的流量绑定特定的宿主机端口

指定映射到宿主机上特定网络端口：

    
    
    docker run --detach --publish 10.2.3.4:49153:80 nginx 
    

### 2.24 不使用 docker 默认的桥接网络 docker0

Docker将以桥接模式创建的虚拟接口连接到名为docker0的通用桥接。 此默认网络模型容易受到ARP欺骗和MAC泛洪攻击，因为没有对其应用过滤。

实际网络通常以编排系统的网络进行配置。

### 2.25 使用大于 1024 的端口，容器只映射必须使用的端口

低于 1024 的端口通常用于系统服务，使用低于 1024 的端口可能与宿主机服务产生冲突，80 和 443
除外，容器服务对外映射端口应该只映射必须开放的端口。

### 2.26 确保Docker命令始终使用其映像的最新版本

使用最新版本的镜像避免引入漏洞。

### 2.27 使用最小化的容器，确保不包含多余的组件或服务

如 SSH、Telnet 或者其他不需要的组件或服务。

### 2.28 docker exec 命令不使用--privileged选项

在docker exec命令中使用--privileged选项可为命令提供扩展的Linux功能。

### 2.29 docker exec 命令不使用--user=root选项

在docker exec命令中使用--user=root选项，会以root用户身份在容器内执行命令。
例如，如果容器以tomcat用户（或任何其他非root用户）身份运行，则可以使用--user=root选项通过docker exec以root身份运行命令。

## 三、其他参数说明

[OPTIONS] | 参数说明：  
---|---  
\--add-host list | 添加自定义主机到ip映射(书写格式为：主机:ip)  
-a, --attach list | 附加到STDIN、STDOUT或STDERR上  
\--blkio-weight uint16 | Block IO (相对权重)，取值10到1000之间，0为禁用(默认0)  
\--blkio-weight-device list | Block IO weight (相对于设备的权重) (默认为数组的形式)  
\--cap-add list | 添加Linux功能  
\--cap-drop list | 删除Linux功能  
\--cgroup-parent string | 容器的可选父级对照组项  
\--cidfile string | 将容器ID写入文件  
\--cpu-period int | 限制CPU CFS(完全公平调度程序)周期  
\--cpu-quota int | 限制CPU CFS(完全公平的调度程序)上限  
\--cpu-rt-period int | 限制CPU运行时周期(以微秒为单位)  
\--cpu-rt-runtime int | 限制CPU实时运行时间(以微秒为单位)  
-c, --cpu-shares int | CPU 共享 (相对权重的设定)  
\--cpus decimal | 设定cpu的数量  
\--cpuset-cpus string | 允许执行的cpu (0-3,0,1)  
\--cpuset-mems string | 允许执行的MEMs (0-3,0,1)  
-d, --detach | 在后台运行容器并打印容器ID  
\--detach-keys string | 覆盖分离容器的键序列  
\--device list | 向容器添加主机设备  
\--device-cgroup-rule list | 向 cgroup 允许的设备列表中添加一个或多个规则  
\--device-read-bps list | 限定设备的读取速率（单位: byte/s）（默认为 []）  
\--device-read-iops list | 限定设备的读取速率（单位：IO/s）（默认为 []）  
\--device-write-bps list | 限定设备的写入速率（单位: byte/s）（默认为 []）  
\--device-write-iops list | 限定设备的写入速率（单位：IO/s）（默认为 []）  
\--disable-content-trust | 跳过镜像验证(默认为 true)  
\--dns list | 设置自定义DNS服务器  
\--dns-option list | 设置DNS选项  
\--dns-search list | 设置自定义的DNS搜索域  
\--entrypoint string | 覆盖镜像的默认入口点  
-e, --env list | 设置环境变量  
\--env-file list | 读取环境变量内容  
\--expose list | 公开一个端口或多个端口  
\--group-add list | 添加其他要加入的组  
\--health-cmd string | 命令运行以检查健康  
\--health-interval duration | 运行检查之间的时间(ms  
\--health-retries int | 连续的失败需要报告不健康  
\--health-start-period duration | 启动健康重试倒计时前容器初始化的启动周期(ms  
\--health-timeout duration | 健康检查运行情况的最大时间值 格式为：(ms  
\--help | 打印出使用情况  
-h, --hostname string | 定义容器主机名  
\--init | 在容器中运行初始化，以转发信号并获取进程  
-i, --interactive | 即使没有连接，也保持STDIN开放  
\--ip string | 设定容器的 IPv4 地址 (例如，192.168.155.139)  
\--ip6 string | 设定IPv6地址(例如，2001:db8::33)  
\--ipc string | 使用IPC模式  
\--isolation string | 容器隔离技术  
\--kernel-memory bytes | 内核内存限制  
-l, --label list | 在容器上设置元数据  
\--label-file list | 在以行分隔的标签文件中读取  
\--link list | 向另一个容器添加链接  
\--link-local-ip list | 容器 IPv4/IPv6 链接本地地址  
\--log-driver string | 设定容器的日志驱动  
\--log-opt list | 设定日志驱动器选项  
\--mac-address string | 配置容器MAC地址(例如，92:d0:c6:0a:29:33)  
-m, --memory bytes | 设定内存限额  
\--memory-reservation bytes | 内存软限制  
\--memory-swap bytes | 交换限制等于内存加上交换:'-1'，以启用无限交换  
\--memory-swappiness int | 优化容器内存交换 (0 到 100) (默认为 -1)  
\--mount mount | 将文件系统挂载附加到容器  
\--name string | 为容器指定一个名称  
\--network string | 将容器连接到网络  
\--network-alias list | 为容器连接的网络添加别名  
\--no-healthcheck | 禁止任何容器指定 HEALTHCHECK  
\--oom-kill-disable | 禁止OOM事件被杀死  
\--oom-score-adj int | 优化主机的OOM事件 ，参数范围 (-1000 到 1000)  
\--pid string | 设定PID命名  
\--pids-limit int | 优化容器pid限制(如果设置-1则为无限制)  
\--privileged | 赋予容器扩展的权限  
-p, --publish list | 将容器的端口发布到主机  
-P, --publish-all | 将所有公开的端口发布到随机端口  
\--read-only | 将容器的根文件系统挂载为只读（后面会详细讲到）  
\--restart string | 配置容器的重启策略，当容器退出时重新启动(默认为“no”)  
\--rm | 当容器退出时自动移除这个容器  
\--runtime string | 使用容器的运行时  
\--security-opt list | 指定docker启动的安全项  
\--shm-size bytes | /dev/shm 的大小（这个可以使其容量进行动态的扩展）  
\--sig-proxy | 设置代理接收京城信号 (默认为 true)  
\--stop-signal string | 停止容器的信号 (默认为 "SIGTERM")  
\--stop-timeout int | 设置超时停止容器(以秒为单位)  
\--storage-opt list | 设定容器的存储驱动程序选项  
\--sysctl map | 指定系统控制项 (默认为 map[] 的格式)  
\--tmpfs list | 挂载tmpfs目录  
-t, --tty | 为当前容器分配一个客户端  
\--ulimit ulimit | 启动需要限制的项(默认为数组的形式)  
-u, --user string | 用户名或UID(格式为: <name  
\--userns string | 使用用户名称空间  
\--uts string | 使用UTS名称空间  
-v, --volume list | 绑定安装卷（关于容器卷，在Docker容器数据卷中会具体的讲解）  
\--volume-driver string | 容器的可选卷驱动程序  
\--volumes-from list | 指定容器装载卷  
-w, --workdir string | 容器内的工作目录  
  
## 参考

> <https://www.mf8.biz/ubuntu-apparmor-openresty/>
>
> <https://docs.docker.com/engine/security/apparmor/>
>
> <https://www.4hou.com/posts/4YP2>
>
> <https://www.freebuf.com/articles/system/201793.html>

***本文作者：白河·愁，转载请注明来自FreeBuf.COM**

