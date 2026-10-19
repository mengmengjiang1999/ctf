![AndroidForensic.jpg](https://image.3001.net/images/20181231/1546219326_5c296f3e97828.jpg!small)

**从本文开始我将为大家带来一系列与数字取证相关的文章，并将重点关注移动设备方面的取证技术。在这篇文章中，我将为大家分享一些关于我对Android设备镜像采集的想法。在Android设备上，有两种我们可以执行的镜像采集类型：**

> 实时采集：在正在运行的设备上执行。通常，分析人员会使用各种工具获取root权限，并使用DD提取镜像；
>
> 死采集：在设备上执行启动到另一个状态。例如，如果设备安装了ClockwordMod，则分析人员可以重启设备恢复并获取root shell。

在本文中我将为大家展示如何执行Android data分区的实时采集。

 **注意：** 为了执行过程的顺利，设备必须已获取root权限。

## Root Android

如今，root
Android设备已成为一种非常普遍的现象，在我的取证工作中我经常会碰到已root的手机设备。此外，在某些情况下为了提取某些数据，取证人员必须要自己root设备。Root的过程特定于每个手机型号，Android版本以及内部版本号，因此想要成功root必须根据你的手机型号找到合适的工具。

大多数现代Android手机都可以使用一款名为KingoRoot的工具获取root权限，如果你的手机并不适用（bootloader锁定，Knox等），你可以在[XDA
Developers](https://xda-developers.com/)上寻求帮助。

Android
root软件有时会使用恶意软件重新打包一些可能不需要的程序，这可能会改变文件系统，必须在分析过程中进行过滤。因此，为了安全起见我建议大家，只在官方方法不起作用时再使用这些软件。

## 镜像 /data 分区

我们将使用“dd”工具来完成我们的工作。默认情况下，“dd”在Android的“/system/bin”目录下。

为了限制设备文件系统的更改，镜像将使用NetCat创建的隧道传输到工作站。

因此，root后的第一步必须先安装Busybox（[在这里下载](https://www.appsapk.com/busybox-app/)），这是一个集成了三百多个最常用Linux命令和工具的软件。

下载busybox Apk后，使用adb命令在设备上进行安装：

    
    
    adb -d install BusyBox.apk

然后，连接到手机并检查root访问权限：

    
    
    adb -d shell
    ls /data
    su
    ls /data

我们使用 **ls /data** 来测试我们是否可以访问受保护的目录。

第一次运行它时，应该会出现失败的情况。我们使用 **su** 命令将用户切换到root。然后，再次使用 **ls /data**
命令进行测试看现在我们是否可以访问受保护的目录。

接下来，我们需要检查设备上已安装的分区：

    
    
    root@VF-895N:/ # mount
    rootfs / rootfs ro,relatime 0 0
    tmpfs /dev tmpfs rw,seclabel,nosuid,relatime,size=450904k,nr_inodes=112726,mode=755 0 0
    devpts /dev/pts devpts rw,seclabel,relatime,mode=600 0 0
    none /dev/cpuctl cgroup rw,relatime,cpu 0 0
    adb /dev/usb-ffs/adb functionfs rw,relatime 0 0
    proc /proc proc rw,relatime 0 0
    sysfs /sys sysfs rw,seclabel,relatime 0 0
    selinuxfs /sys/fs/selinux selinuxfs rw,relatime 0 0
    debugfs /sys/kernel/debug debugfs rw,relatime 0 0
    none /sys/fs/cgroup tmpfs rw,seclabel,relatime,size=450904k,nr_inodes=112726,mode=750,gid=1000 0 0
    none /acct cgroup rw,relatime,cpuacct 0 0
    tmpfs /mnt/asec tmpfs rw,seclabel,relatime,size=450904k,nr_inodes=112726,mode=755,gid=1000 0 0
    tmpfs /mnt/obb tmpfs rw,seclabel,relatime,size=450904k,nr_inodes=112726,mode=755,gid=1000 0 0
    /dev/block/bootdevice/by-name/system /system ext4 ro,seclabel,relatime,discard,data=ordered 0 0
    /dev/block/bootdevice/by-name/userdata /data ext4 rw,seclabel,nosuid,nodev,relatime,discard,noauto_da_alloc,data=ordered 0 0
    /dev/block/bootdevice/by-name/cache /cache ext4 rw,seclabel,nosuid,nodev,relatime,data=ordered 0 0
    /dev/block/bootdevice/by-name/persist /persist ext4 rw,seclabel,nosuid,nodev,relatime,data=ordered 0 0
    /dev/block/bootdevice/by-name/tctpersist /tctpersist ext4 rw,seclabel,nosuid,nodev,relatime,data=ordered 0 0
    /dev/block/bootdevice/by-name/modem /firmware vfat ro,context=u:object_r:firmware_file:s0,relatime,uid=1000,gid=1000,fmask=0337,dmask=0227,codepage=437,iocharset=iso8859-1,shortname=lower,errors=remount-ro 0 0
    /dev/fuse /storage/uicc1 fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
    /dev/fuse /storage/uicc0 fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
    /dev/fuse /mnt/shell/emulated fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
    /dev/fuse /storage/usbotg fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
    /dev/fuse /storage/sdcard0 fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
    /dev/block/vold/179:65 /mnt/media_rw/sdcard1 vfat rw,dirsync,nosuid,nodev,noexec,relatime,uid=1023,gid=1023,fmask=0007,dmask=0007,allow_utime=0020,codepage=437,iocharset=iso8859-1,shortname=mixed,utf8,errors=remount-ro 0 0
    /dev/block/vold/179:65 /mnt/secure/asec vfat rw,dirsync,nosuid,nodev,noexec,relatime,uid=1023,gid=1023,fmask=0007,dmask=0007,allow_utime=0020,codepage=437,iocharset=iso8859-1,shortname=mixed,utf8,errors=remount-ro 0 0
    /dev/fuse /storage/sdcard1 fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0

我们重点来关注data分区，在本例中为“ **/dev/block/bootdevice/by-name/userdata** ”。

接下来，我们需要设置工作站和移动设备之间的连接路由，转发端口为8888。

在工作站上运行：

    
    
    adb forward tcp:8888 tcp:8888

现在让我们使用“dd”启动镜像过程并使用netcat管道传输数据。

在手机设备的root shell下运行：

    
    
    root@VF-895N:/ #dd if=/dev/block/bootdevice/by-name/userdata | busybox nc -l -p 8888

并在取证工作站上运行：

    
    
    nc 127.0.0.1 8888 > android_data.dd

镜像过程完成后，将如下图所示：

![image-1.png](https://image.3001.net/images/20181231/1546219374_5c296f6ed0eba.png!small)

然后，我们可以使用sleuthkit或Autopsy对镜像进行分析。

![image-2.png](https://image.3001.net/images/20181231/1546219387_5c296f7b303e5.png!small)

 ***参考来源：[andreafortuna](https://www.andreafortuna.org/dfir/android-forensics-imaging-android-file-system-using-adb-and-dd/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

