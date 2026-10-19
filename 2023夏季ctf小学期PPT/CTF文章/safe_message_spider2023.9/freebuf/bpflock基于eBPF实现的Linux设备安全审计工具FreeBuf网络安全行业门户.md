![](https://image.3001.net/images/20220809/1660045659_62f2495ba2d28e5985ee1.png!small)

## 关于bpflock

bpflock是一款基于[
_eBPF_](https://ebpf.io/)驱动的Linux设备安全审计工具，该工具使用了eBPF来帮助广大研究人员增强Linux设备的安全性。通过限制对各种Linux功能的访问，bpflock能够减少攻击面并阻止一些众所周知的攻击技术。

bpflock只允许类似容器管理器、systemd和其他以[ _主机PID或网络命名空间_](https://man7.org/linux/man-pages/man7/namespaces.7.html)运行的容器/程序访问完整的Linux功能，并限制那些以自己命名空间运行的容器或程序。如果bpflock在受限配置文件下运行，则所有程序/容器（包括特权程序/容器）都将被拒绝访问。

除此之外，bpflock还可以通过各种安全功能来保护Linux设备安全，比如说[
_Linux安全模块+BPF_](https://docs.kernel.org/bpf/prog_lsm.html)等等。

## 功能介绍

> 1、内存保护：内核镜像锁定、内核模块保护、BPF保护；
>
> 2、进程保护：无文件内存执行、命名空间保护；
>
> 3、硬件攻击测试：USB保护；
>
> 4、系统和应用程序跟踪：跟踪应用程序执行、跟踪特权系统操作；
>
> 5、文件系统保护：只读Root文件系统保护、sysfs保护；
>
> 6、网络保护；

## 工具开发

### 依赖组件

bpflock需要使用下列组件：

1、Linux内核版本 >= 5.13，相关配置如下：

    
    
    CONFIG_BPF_SYSCALL=y
    
    CONFIG_DEBUG_INFO=y
    
    CONFIG_DEBUG_INFO_BTF=y
    
    CONFIG_KPROBES=y
    
    CONFIG_LSM="...,bpf"
    
    CONFIG_BPF_LSM=y

2、一个启用了BTF的内核

### 启用BPF LSM支持

1、使用高级权限打开/etc/default/grub文件；

2、将下列内容添加到GRUB_CMDLINE_LINUX变量并保存：

    
    
    "lsm=lockdown,capability,yama,apparmor,bpf"

或

    
    
    GRUB_CMDLINE_LINUX="lsm=lockdown,capability,yama,apparmor,bpf"

3、更新grub配置：

    
    
    sudo update-grub2

4、重启设备

## Docker使用

下列命令可以使用默认的配置文件运行工具：

    
    
    docker run --name bpflock -it --rm --cgroupns=host \
    
      --pid=host --privileged \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

### 无文件代码执行

    
    
    docker run --name bpflock -it --rm --cgroupns=host --pid=host --privileged \
    
      -e "BPFLOCK_FILELESSLOCK_PROFILE=restricted" \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

### 内核模块执行

    
    
    docker run --name bpflock -it --rm --cgroupns=host --pid=host --privileged \
    
      -e "BPFLOCK_KMODLOCK_PROFILE=restricted" \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

使用样例：

    
    
    $ sudo unshare -p -n -f
    
    # modprobe xfs
    
    modprobe: ERROR: could not insert 'xfs': Operation not permitted

输出结果：

    
    
    time="2022-02-07T06:50:25+01:00" level=info msg="event=syscall_execve tgid=52323 pid=52323 ppid=52288 uid=0 cgroupid=7014 comm=modprobe pcomm=bash filename=/usr/sbin/modprobe retval=0" bpfprog=execsnoop subsys=bpf
    
     
    
    time="2022-02-07T06:50:25+01:00" level=info msg="event=lsm_kernel_read_file operation=loading module tgid=52323 pid=52323 ppid=52288 uid=0 cgroupid=7014 comm=modprobe pcomm=bash filename=xfs.ko retval=-1 reason=denied (restricted)" bpfprog=kmodlock subsys=bpf

### 内核镜像锁定

    
    
    docker run --name bpflock -it --rm --cgroupns=host --pid=host --privileged \
    
      -e "BPFLOCK_KIMGLOCK_PROFILE=baseline" \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

使用样例：

    
    
    $ sudo unshare -f -p -n bash
    
    # head -c 1 /dev/mem
    
    head: cannot open '/dev/mem' for reading: Operation not permitted

输出结果：

    
    
    time="2022-02-07T06:57:22+01:00" level=info msg="event=syscall_execve tgid=52428 pid=52428 ppid=52288 uid=0 cgroupid=7014 comm=head pcomm=bash filename=/usr/bin/head retval=0" bpfprog=execsnoop subsys=bpf
    
     
    
    time="2022-02-07T06:57:22+01:00" level=info msg="event=lsm_locked_down operation=/dev/mem,kmem,port tgid=52428 pid=52428 ppid=52288 uid=0 cgroupid=7014 comm=head pcomm=bash retval=-1 reason=denied (baseline)" bpfprog=kimglock subsys=bpf

### BPF保护

    
    
    docker run --name bpflock -it --rm --cgroupns=host --pid=host --privileged \
    
      -e "BPFLOCK_BPFRESTRICT_PROFILE=baseline" \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

使用样例：

    
    
    $ sudo unshare -f -p -n bash
    
    # bpftool prog
    
    Error: can't get next program: Operation not permitted

输出结果：

    
    
    time="2022-02-04T15:40:56Z" level=info msg="event=lsm_bpf tgid=2378 pid=2378 ppid=2364 uid=0 cgroupid=9458 comm=bpftool pcomm=bash filename= retval=-1 reason=baseline" bpfprog=bpfrestrict subsys=bpf
    
     
    
    time="2022-02-04T15:40:56Z" level=info msg="event=lsm_bpf tgid=2378 pid=2378 ppid=2364 uid=0 cgroupid=9458 comm=bpftool pcomm=bash filename= retval=-1 reason=baseline" bpfprog=bpfrestrict subsys=bpf

## 工具配置&环境配置

假设你项目的bpflock目录中已经包含了 bpflock.yaml和bpf.d这两个配置文件了，接下来运行下列命令：

    
    
    ls bpflock/
    
      bpf.d  bpflock.d  bpflock.yaml
    
    docker run --name bpflock -it --rm --cgroupns=host --pid=host --privileged \
    
      -v $(pwd)/bpflock/:/etc/bpflock \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

我们也可以使用“--env-file”命令来传递环境变量：

    
    
    docker run --name bpflock -it --rm --cgroupns=host --pid=host --privileged \
    
      --env-file bpflock.env.list \
    
      -v /sys/kernel/:/sys/kernel/ \
    
      -v /sys/fs/bpf:/sys/fs/bpf linuxlock/bpflock

## 许可证协议

本项目的开发与发布遵循[ _Apache-2.0_](https://github.com/linux-lock/bpflock/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **bpflock** ：【[ _GitHub传送门_](https://github.com/linux-lock/bpflock)】

## 参考资料

> [ _https://ebpf.io/_](https://ebpf.io/)
>
> [ _https://man7.org/linux/man-> pages/man7/namespaces.7.html_](https://man7.org/linux/man-> pages/man7/namespaces.7.html)
>
> [
> _https://docs.kernel.org/bpf/prog_lsm.html_](https://docs.kernel.org/bpf/prog_lsm.html)
>
> [ _https://github.com/linux-> lock/bpflock/tree/main/deploy/configs/_](https://github.com/linux-> lock/bpflock/tree/main/deploy/configs/)
>
> [ _https://github.com/linux-> lock/bpflock/tree/main/docs/_](https://github.com/linux-> lock/bpflock/tree/main/docs/)
>
> [ _https://github.com/linux-lock/bpflock/tree/main/docs/memory-> protections.md#3-bpf-protection_](https://github.com/linux-> lock/bpflock/tree/main/docs/memory-protections.md#3-bpf-protection)
>
> [ _https://github.com/libbpf/bpftool_](https://github.com/libbpf/bpftool)
>
> [ _https://go.dev/doc/install_](https://go.dev/doc/install)
>
> [ _https://docs.docker.com/develop/develop-> images/build_enhancements/_](https://docs.docker.com/develop/develop-> images/build_enhancements/)

