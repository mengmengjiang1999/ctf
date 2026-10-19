文章来源：知了堂冯老师  

![v2-c4c958a3e1dfbc0814708d05a49ef731_hd
\(1\).jpg](https://image.3001.net/images/20191113/1573636231_5dcbc8875a08e.jpg!small)  

昨天的笔记大家觉得可还满意？是不是感觉相见恨晚。今天宝藏小编继续给你带来我们学员的优质笔记供大家食用。

![v2-fa55762ec6cfcbc85ee20a6b0c1bc3c2_hd.jpg](https://image.3001.net/images/20191113/1573635460_5dcbc584e44b1.jpg!small)

## 第2章 用户和磁盘管理

## 一. 用户帐号管理

### 1.1添加用户账号（useradd）

命令： useradd [-选项] [用户名]

选项：

-u: UID标记号

-d: 指定宿主目录

-e: 指定账号失效时间

-g: 指定UID用户的基本组名

-G: 指定GID的附加组名

-M: 不为用户建立初始化宿主目录

-S: 指定用户登陆shell

### 1.2设置用户密码（passwd）

命令: passwd [-选项] [用户名]

选项：

-d: 清空密码

-l: 锁定用户账号

-S: 查看用户当前状态

-U: 解锁用户账号

### 1.3修改用户账号属性（usermod）

命令: usermod [-选项] [用户名]

选项:

-l: 修改用户登录名

-L: 锁定用户账号

-U: 解锁用户账号

-u d e g G s 同useradd

## 二. 组账号管理

### 2.1组账号添加 (groupadd）

命令: groupadd [-选项] [用户名]

选项：

-g: 添加组账号

### 2.2添加组成员（gpasswd）

命令: gpasswd [-选项] [用户名]

选项:

-a: 添加用户

-d: 删除用户

-M: 自定义添加多用户用”，”隔开

### 2.3删除组成员（groupdel）

命令: groupdel [-选项] [用户名]

选项：

-a: 添加用户

-d: 删除用户

-M: 自定义添加多用户用”，”隔开

### 2.4查看用户信息

id（用户）：身份标识

groups（用户）：所属的组

finger（用户）：用户详细信息

users、who、w：已登录的用户信息 [设备路径]

## 三. 用户、文件、目录的权限和归属

### 3.1访问权限

读取r：允许查看文件内容、显示目录列表

写入w：允许修改文件内容、子目录

可执行x：允许运行程序、切换目录

属主：拥有该文件或目录的用户账号

属组：拥有该文件或目录的组账号

d(目录)、b(块设备文件)、c(字符设备文件)

“-”（普通文件）、 “l”（链接文件）

## 四. 权限和归属的修改

### 4.1修改权限

#chmod +ugoa（属主、属组、other、所有用户）+-= 文件或目录

#chmod xxx + 文件或目录（r=4、w=2、x=1）

### 4.2修改归属

chown 属主 + 文件或目录

chown：属组 + 文件或目录

chown 属主：属组 + 文件或目录

## 第3章 磁盘管理和用户磁盘配额

## 一. 磁盘设备的分区、格式化、挂载

### 1.1分区：在交互式的环境中管理磁盘分区

fdisk 磁盘设备（路径）

交互模式中的常用指令：

-m：查看帮助信息

-p：查看分区信息

-n：新建分区

-d：删除分区

-t：变更分区类型

-w：保存并退出

-q：放弃并退出

### 1.2创建文件系统（格式化）

mkfs -t 类型 分区设备

eg: # mkfs -t etx4 /dev/sdb1 //把/dev/sdb1 盘格式为ext4

### 1.3.创建交换文件系统（交换分区）

mkswap 分区设备

swapon（打开）；swapoff（关闭）

### 1.4挂载、卸载文件系统

mount [-t 类型] 存储设备 挂载点目录

mount -o loop 镜像文件 挂载点目录

umount 存储设备位置

umount 挂载点目录

### 1.5开机自动挂载——修改配置文件

### 1.5.1修改配置文件

vim /etc/fstab

/dev/sdb1盘 /var/ltc路径 ext4类型 default 0 0

#Mount -o remount,usrquota,grpquota /dev/sdb1 /home/ltc

//临时添加磁盘/dev/sdb1配额文件挂载在/home/ltc下

### 1.5.2查看挂载情况

#mount –a

#mount

### 1.5.3查看磁盘使用情况

df [-选项] [文件]

例：#df -hT

## 二. LVM（逻辑卷管理）

### 1.1 LVM概述

PV：物理卷

使用fdisk建立的普通分区,包括许多默认的4kb大小的PE

VG：卷组

一个或多个物理卷组合而成的整体

LV：逻辑卷

从卷组中分割出的一块空间,用于建立文件系统

### 1.2创建命令

PVVGLV扫描Scanpvscanvgscanlvscan建立Createpvcreatevgcreatelvcreate显示displaypvdisplayvgdisplaylvdisplay删除removepvremovevgremovelvremove扩展extend
------vgextendlvextend减少reduce------vgreducelvreduce

创建pv pvcreate 设备名/dev/sdb1

创建vg vgcreate 卷组名/ltc 物理卷/dev/sdb1 物理卷/dev/sdb2

创建lvm lvcreate -L 大小/100M -n 逻辑卷名 卷组名

创建扩展lvm lvextend -L +大小 /dev/卷组名/逻辑卷名

### 1.3转化物理卷/卷组/逻辑卷

用fdisk命令划分区，类型设为“8e”lvm 用pvcreate创建

#pvcreate /dev/sdb1 /dev/sdc1

#vgcreate jdy /dev/sdb1 dev/sdc1

#lvcreate –L 100M –n zr jdy

### 1.4逻辑卷LVM 扩容量

#Lvextend –L 100M /dev/卷组/逻辑卷

### 1.5创建ext4文件系统格式化

# mkfs -t ext4 /dev/卷组/逻辑卷

## 三. 磁盘配额

磁盘限额的特点

限制范围：针对指定的文件系统(分区)

限制对象：用户帐号，组帐号

限制类型：磁盘容量，文件数量

限制方法：软限制，硬限制

### 3.1开启、关闭文件系统的配额支持

quotaon -u [设备] /挂载的路径

quotaoff

### 3.2检测磁盘配额并创建配额文件

rpm –qa quota /-ql

quotacheck -ugcy 文件系统

quotacheck -augcy

u g 检测用户、组配额

c：创建配额数据文件

v：显示执行过程

a：检测所有可用的分区

### 3.3编辑用户的配额并开启配额功能

#edquota -u 用户名

#edquota -g 组名

#quotaon -ugv /ltc

#quotaoff -ugv /ltc

### 3.4 验证磁盘配额

要切换用户 到配额的分区/挂载目录

命令 dd 进行配置

#cd /ltc

#dd if=/dev/zero of=myfile bs=10M count=120

### 3.5 查看配额使用情况

#quota –u 用户名

#quota –g 组名

#requota 文件

## 四. 实验环境要求和配置

要求：1 新添加2块磁盘/dev/sdb /dev/sdc

2 创建4个物理卷pv 2个卷组vg 1个逻辑卷

3 将逻辑卷设为开机自动挂载

4 对该逻辑卷做用户配额限制最大不超过50M

### 第一步 添加磁盘

1.在虚拟机中新添加2块硬盘，并重启初始化硬盘

2.通过#fdisk /dev/sdb #fdisk /dev/sdc

n：创建 选择类型extended primary partition

p：选择分区1-4

t: 选择类型

#/dev/sdb sdb1 8e sdb2 8e sdb3 83

//在/dev/sdb这块盘 类型8e lvm 83标准分区

#/dev/sdc sdc1 8e sdc2 8e sdc3 8e sdc4 5 Extend

### 第二步 创建物理卷 卷组 逻辑卷

1 #pvcreate /dev/sdb1 /dev/sdb2 /dev/sdc1 dev/sdc2 /dev/sdc3 查看pvs

2 #vgcreate jdy1 /dev/sdb1 /dev/sdc1

#vgcreate jdy2 /dev/sdb2 dev/sdc2 /dev/sdc3 查看vgs

3 #lvcreate –L 200M –n zr jdy2 查看lvs 路径/dev/jdy2/zr

4 #mkfs –t ext4 /dev/jdy2/zr 格式化支持挂载

5 自动挂载

#vim /etc/fstab

#/dev/jdy2/zr /test ext4 default，usrcheck，grpquota 0 0

//逻辑卷LVM地址 挂载到/test 格式为ext4 支持配额

### 第三步 磁盘配额限制

1 检查配置软件是否存在

#rpm –q quota

#rpm –ql quota

2 创建磁盘配额配置文件

#quotacheck -ugc /dev/jdy2/zr //创建lvm磁盘的额配文件

3 去挂载的目录下查看

#ls –l /ltc //查看目录

### 第四步 给用户添加配额

1编辑用户和组账号的配置设置

# edquota -u 1/用户名

filesystem blocks soft hard inodes soft hard

/dev/jdy2/zr 10 20 5 10

系统设备 软限额K 硬限额 软文件个数 硬文件个数

2 启用和关闭文件系统配额的功能

#quotaon –ugv [设备路径]

#quotaoff –ugv [设备路径]

3 验证磁盘配额功能

查看磁盘配额信息 repquota -a

切换用户 在目录下创建一个文件 显示的是小b

（ltc）#dd if=/dev/zero of=/宿主目录下文件路径 bs=1M count=10

今天的笔记也到这里结束啦，你不赞，他不赞，小编的笔记没人看，嘻嘻。

![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

