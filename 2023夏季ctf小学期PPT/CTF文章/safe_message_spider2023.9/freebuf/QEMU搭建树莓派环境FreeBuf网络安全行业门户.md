# 0x01

最近树莓派被同学借去做毕设了，没有其他ARM平台供我研究，无奈之下只好尝试使用QEMU模拟raspbian，搭建过程比较繁琐，网上的教程有很多坑都没有指出，所以有了此文，给同样有兴趣做IoT安全、ARM平台安全的小伙伴们的入门铺平道路。

# 0x02

QEMU是啥？

QEMU是一个托管的虚拟机镜像，它通过动态的二进制转换，模拟CPU，并且提供一组设备模型，使它能够运行多种未修改的客户机OS，可以通过与KVM（kernel-basedvirtual machine开源加速器）一起使用进而接近本地速度运行虚拟机（接近真实计算机的速度）。

# 0x03

平台说明：

Ubuntu18.04(4G内存，40G硬盘)

为项目创建一个新的文件夹

![0X7kNW3L1tY](http://si1.go2yd.com/get-image/0X7kNW3L1tY)

​

将下载来的树莓派镜像放到这个文件夹下，将从github上下载来的qemukernel（官方内核在qemu中无法运行，所以在github上找了个能用的：<https://github.com/dhruvvyas90/qemu-rpi-kernel>）也放在这儿，解压镜像

![0X7kNuBFrd2](http://si1.go2yd.com/get-image/0X7kNuBFrd2)

​

使用fdisk观察硬盘实体使用情况

![0X7kNzvlpiK](http://si1.go2yd.com/get-image/0X7kNzvlpiK)

​

可以看到img2的bootstart为92160，将其乘以512（在上图中可以看到单位units:sectorsof 1 *512
=512bytes，说明还需乘以512），得到47185920，这就是后面命令中的offset

接下来先创建一个挂载用的文件夹

![0X7kNtAy4Ku](http://si1.go2yd.com/get-image/0X7kNtAy4Ku)

​

然后使用下面的挂载命令

![0X7kNr3ja08](http://si1.go2yd.com/get-image/0X7kNr3ja08)

​

接下来编辑ld.so.preload文件，将其中的内容注释，然后使用umount写在已经加载的文件系统

![0X7kNsuzbt2](http://si1.go2yd.com/get-image/0X7kNsuzbt2)

​

接下来通过qemu模拟树莓派，使用下面的命令

qemu-system-arm-kernel ~/qemu_vms/<your-kernel-qemu> -cpu arm1176 -m 256
-Mversatilepb -serial stdio -append "root=/dev/sda2rootfstype=ext4 rw" -hda
~/qemu_vms/<your-jessie-image.img>-redir tcp:5022::22 -no-reboot

![0X7kNqux2Iq](http://si1.go2yd.com/get-image/0X7kNqux2Iq)

​

启动过程如下图

![0X7kNtoZQYq](http://si1.go2yd.com/get-image/0X7kNtoZQYq)

​

启动完毕后如图所示

![0X7kNpe6dMW](http://si1.go2yd.com/get-image/0X7kNpe6dMW)

​

为了后续的方便，我们一般会使用远程连接，所以先安装ssh服务端

![0X7kNo9COB6](http://si1.go2yd.com/get-image/0X7kNo9COB6)

​

在ubuntu上启动ssh服务，在kali上测试下

![0X7kNmgtQcy](http://si1.go2yd.com/get-image/0X7kNmgtQcy)

​

然后在树莓派上也启动ssh服务，就可以远程了，下图是我kali远程到ubuntu上后再远程到树莓派

![0X7kNnHOnqq](http://si1.go2yd.com/get-image/0X7kNnHOnqq)

​

或者也可以直接在kali上远程到书树莓派

![0X7kNojuNt2](http://si1.go2yd.com/get-image/0X7kNojuNt2)

​

因为我们后续基本都是靠ssh远程连接，所以使用下面的命令使得树莓派能够开机自启ssh服务

![0X7kNkYRJKK](http://si1.go2yd.com/get-image/0X7kNkYRJKK)

​

树莓派默认以图形化界面展示，如果想要以命令行模式启动的话，按照如下步骤操作即可

输入sudoraspi-config进入设置页面，如下选择bootoption

![0X7kNkmKghE](http://si1.go2yd.com/get-image/0X7kNkmKghE)

​

然后选择desktop/cli

![0X7kNkC6o2i](http://si1.go2yd.com/get-image/0X7kNkC6o2i)

​

然后选择consoleautologin

![0X7kNojMlXc](http://si1.go2yd.com/get-image/0X7kNojMlXc)

​

最后重启即可

![0X7kNhWNQjA](http://si1.go2yd.com/get-image/0X7kNhWNQjA)

​

重启后的界面就是这样子的了

![0X7kNi0Tz0q](http://si1.go2yd.com/get-image/0X7kNi0Tz0q)

​

此时使用df–hl可以看到3.9G的空间现在已经用了3.6G了

![0X7kNhVpogK](http://si1.go2yd.com/get-image/0X7kNhVpogK)

​

为了以便不时之需，我们需要扩大容量，安装如下步骤进行

先把树莓派关掉

先拷贝一份原来的镜像文件

![0X7kNfRcLLs](http://si1.go2yd.com/get-image/0X7kNfRcLLs)

​

再给新的镜像文件扩容

![0X7kNfuzE7U](http://si1.go2yd.com/get-image/0X7kNfuzE7U)

​

接下来将扩容后的新镜像作为第二块硬盘启动

![0X7kNeqcTMe](http://si1.go2yd.com/get-image/0X7kNeqcTMe)

​

输入命令后进入如下的界面

![0X7kNclK2rI](http://si1.go2yd.com/get-image/0X7kNclK2rI)

​

如下图选中将sdb2删除

![0X7kNiGic6K](http://si1.go2yd.com/get-image/0X7kNiGic6K)

​

然后从freespace创建一个新分区，如下图选中即可

![0X7kNbpDbuq](http://si1.go2yd.com/get-image/0X7kNbpDbuq)

​

选中write写入

![0X7kNcCnNYm](http://si1.go2yd.com/get-image/0X7kNcCnNYm)

​

输入yes确认

![0X7kNeQXKt6](http://si1.go2yd.com/get-image/0X7kNeQXKt6)

​

会提示写入成功

![0X7kNZwJh4q](http://si1.go2yd.com/get-image/0X7kNZwJh4q)

​

然后退出即可

![0X7kNYtVyoy](http://si1.go2yd.com/get-image/0X7kNYtVyoy)

​

接下来使用fsck检查文件系统中是否存在错误

![0X7kNZIJ6ES](http://si1.go2yd.com/get-image/0X7kNZIJ6ES)

​

可以看到没有报错

然后关闭树莓派

接下来我们在使用qemu启动树莓派的命令中只需要使用新镜像就可以了

命令如图中所示

![0X7kNZLcCDg](http://si1.go2yd.com/get-image/0X7kNZLcCDg)

​

这样就完成了全部的工作。

# 0x04参考

1.https://zh.wikipedia.org/wiki/QEMU

2.https://azeria-labs.com/emulate-raspberry-pi-with-qemu/

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

