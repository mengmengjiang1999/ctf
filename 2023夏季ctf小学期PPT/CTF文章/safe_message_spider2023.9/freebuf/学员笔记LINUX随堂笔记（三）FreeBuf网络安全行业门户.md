文章来源：知了堂冯老师  

![v2-c4c958a3e1dfbc0814708d05a49ef731_hd
\(1\).jpg](https://image.3001.net/images/20191113/1573636231_5dcbc8875a08e.jpg!small)  

我来啦我来啦~昨天的消化好了吗？今天我们继续向优秀的同学学习！

![v2-cbc22948fe4f88c2fa26d343e8b88580_hd.j](https://pic1.zhimg.com/80/v2-cbc22948fe4f88c2fa26d343e8b88580_hd.jpg)  

## 第4章 服务引导过程

## 一. 开机启动进程管理

### 1.1引导过程总览

![v2-2bad4bd839525c6417eebac8583f482a_hd.j](https://pic3.zhimg.com/80/v2-2bad4bd839525c6417eebac8583f482a_hd.jpg)

### 1.2 init进程

由linux内核加载运行/sbin/init程序

是系统中第一个进程，PID（进程标记）号永远为1

配置文件：/etc/inittab

### 1.3 inittab文件的结构

x ： 5 ： respawn ：/etc/X11/prefdm-nodaemon

id runlevels字段 action字段 prcocess字段

![v2-cdad108774ca4504d9d29c88cec279fe_hd.j](https://pic3.zhimg.com/80/v2-cdad108774ca4504d9d29c88cec279fe_hd.jpg)

字段说明id用于在inittab文件中唯一标识一个配置记录runlevels用于指定该记录在那些运行级别中运行action用于描述记录将执行哪种类型的动作process用于设置启动进程所执行的命令

### 1.4 rc.sysinit脚本文件

路径/etc/rc.d/rc.sysinit

由init进程调用执行

完成设置网络、主机名、加载文件系统等初始化工作

### 1.5 rc脚本文件

/etc/rc.d/rc脚本文件

有init进程调用执行

根据指定的运行级别，加载或终止相应的系统服务

### 1.6 rc.local脚本文件

/etc/rc.local脚本文件

由rc脚本调用执行

保存用户定义的需开机后自动执行的命令

### 1.7 service系统服务控制

语法：service [服务名称][控制类型]

/etc/rc.d/init.d [服务器名称][控制类型]

控制类型

start: 启动

stop: 停止

restart：重新启动

reload：重新加载

status：查看服务状态

\--status-all：查看所有服务状态

### 1.8 linux系统的运行级别

init

语法：init [级别参数]

级别参数

0 - halt //关闭

1 - //维护模式

2 - //unix系统间只做NFS（网络文件系统）

3 - //字符模式

4 - unused //保留

5 - X11 //图形模式

6 –reboot //重启

## 二. 系统优化

### 2.1系统服务管理

### 2.1.1 ntsysv工具

命令：ntsysv

![v2-9a5c4cddf38e9fddfc80c26a64d76cda_hd.j](https://pic3.zhimg.com/80/v2-9a5c4cddf38e9fddfc80c26a64d76cda_hd.jpg)

调取特定的level级别，开启或关闭该级别服务的设置

ntsysv --level [级别编号]

chkconfig管理工具

查看所有的服务启用状态

语法：chkconfig

![v2-71d1a042c158e55b4797741a1e4c2673_hd.j](https://pic4.zhimg.com/80/v2-71d1a042c158e55b4797741a1e4c2673_hd.jpg)

查看某个特定服务的状态

语法：chkconfig --list [服务名称]

![v2-0420f523dfe22846d9a1a503fe48deca_hd.j](https://pic3.zhimg.com/80/v2-0420f523dfe22846d9a1a503fe48deca_hd.jpg)

设置系统服务的启动状态

语法：chkconfig --level [级别列表][服务名] on|off

![v2-ac0085b45b6236e8cafea6edfc430433_hd.j](https://pic4.zhimg.com/80/v2-ac0085b45b6236e8cafea6edfc430433_hd.jpg)

### 2.2进程管理

### 2.2.1查看进程信息

ps

语法：ps aux

ps -elf

![v2-c08097bc92a0cf26c33e8a10ea98586b_hd.j](https://pic4.zhimg.com/80/v2-c08097bc92a0cf26c33e8a10ea98586b_hd.jpg)![v2-06f47b38521f247eef61ef6cfc7f71fa_hd.j](https://pic3.zhimg.com/80/v2-06f47b38521f247eef61ef6cfc7f71fa_hd.jpg)

top

用途：查看动态的进程排名信息（相当于windows中任务管理器中的进程）

![v2-ebed59e44e1002eebb3ff00cfbd7277e_hd.j](https://pic3.zhimg.com/80/v2-ebed59e44e1002eebb3ff00cfbd7277e_hd.jpg)

pgrep

用途：根据特定的条件查询进程PID信息

语法：pgrep “服务进程的名称”

![v2-a3483cda3188578889220033639487bc_hd.j](https://pic1.zhimg.com/80/v2-a3483cda3188578889220033639487bc_hd.jpg)

语法：pgrep [选项] [参数]

选项

-l //显示进程名称

-U //指定特定的用户

-t //指定终端

![v2-c8aacf32102d034d7071f07bd1be2a77_hd.j](https://pic4.zhimg.com/80/v2-c8aacf32102d034d7071f07bd1be2a77_hd.jpg)

2.2.2以树状形式查看进程

pstree

pstree [选项]

选项

-a //显示完整信息

-u //列出对应用户名

-p //列出对应PID

![v2-eef3beff15d9e16e8a552dd00c051f7b_hd.j](https://pic4.zhimg.com/80/v2-eef3beff15d9e16e8a552dd00c051f7b_hd.jpg)![v2-c440a0d6878a75b60908248e658b0aa8_hd.j](https://pic1.zhimg.com/80/v2-c440a0d6878a75b60908248e658b0aa8_hd.jpg)

### 2.3进程的启用

### 2.3.1手动启动

前台启动：用户执行命令，直接执行程序，需要等待该命令执行完毕，才能做其他操作

![v2-d65fcc3ef4442914b11e6510c4c677cf_hd.j](https://pic4.zhimg.com/80/v2-d65fcc3ef4442914b11e6510c4c677cf_hd.jpg)

后台启动：在命令行尾加入“&”符号，让当前的命令行在后台自行执行

![v2-ed5ad48757c010dc6a465d8299df820e_hd.j](https://pic3.zhimg.com/80/v2-ed5ad48757c010dc6a465d8299df820e_hd.jpg)

进程前后台调用

### 2.3.2 Ctrl+z组合键

将当前执行的进程挂起，调入后台并暂停执行

jobs

查看处于后台的任务列表

fg

将处于后台的进程恢复到前台运行，并指定任务序号

### 2.4终止进程的运行

ctrl+c组合键

中断正在执行的命令

kill终止命令

kill -9 7669 //终止指定PID号的进程

killall -9 vim //终止所有vim进程

pkill终止命令

用途：根据特定条件终止相应的进程

选项

-U：根据进程所属的用户名终止相应进程

-t：根据进程所在的终端终止相应进程

pkil -9 -U “admin” //将admin的所有进程全部终止

## 三. 计划任务管理

### 3.1一次性计划任务管理

创建：一次性计划任务

语法：at [HH:MM][yyyy-mm-dd ]

所需执行的计划任务 ctrl+d（执行这个计划任务）

查看未执行的任务列表

atq

删除对应的任务

atrm [任务编号]

### 3.2设置周期性任务

crond

编辑计划任务：crontab -e [-u 用户名]

查看计划任务：crontab -l [-u 用户名]

删除计划任务：crontab -r [-u 用户名]

### 3.2.1任务配置的格式

分钟 小时 日期 月份 星期 任务内容

![v2-158b01f7616be9a096a65535c9052c49_hd.j](https://pic2.zhimg.com/80/v2-158b01f7616be9a096a65535c9052c49_hd.jpg)

### 3.2.2时间数字特殊表示方法

* ： 表示该范围内的任意时间

， ： 表示间隔的多个不连续时间点

\- ：表示一个连续的时间范围

/ ：指定间隔的时间频率

### 3.2.3应用时间格式

0 17 * * 1-5 //周一到周五每天17：00

30 8 * * 1，3，4 //每周一、三、五的8点30分

0 8-18/2 * * *8 //点到18点之间每隔2小时

* 0 * */3 * * //每隔3天

语法：crontab -e [编辑时间条件][编写需要执行的操作]（使用的命令，必须

使用该命令的绝对路径）

语法：crontab -e -u [用户名] [编辑时间条件][编写需要执行的操作]

注释：（该语法适用于，将系统文件导入其他用户属主目录，需要获取该属主

权限）

crontab -l //查看周期性任务

crontab -l -u [用户名] //查看某用户的计划任务

crontab -r -u [用户名] //删除某用户的计划任务

## 四. 系统故障分析和排查

### 4.1主要日志文件

内核及公共消息日志：/var/log/messages

计划任务日志：/var/log/cron

系统引导日志：/var/log/dmesg

邮件系统日志：/var/log/maillog

用户登录日志：/var/log/lastlog、/var/log/secure、/var/log/wtmp、/var/run/btmp

### 4.2日志消息级别

0 EMERG（紧急）：会导致主机系统不可用的情况

1 ALERT （警告）：必须马上采取措施解决的问题

2 CRIT （严重）：比较严重的情况

3 ERR （错误）：运行出现错误

4 WARNING （提醒）：可能会影响系统功能的事件

5 NOTICE （注意）：不会影响系统但值得注意

6、INFO （信息）：一般信息

7、DEBUG （调试）：程序或系统调试信息等

### 4.3用户日志路径

/var/log/lastlog：最近用户登录时间

/var/log/vtmp ：用户登录、注销及系统开、关机事件

/var/run/utmp：当前登录的每个用户的详细信息

/var/log/secure：与用户验证相关的安全性事件

### 4.4分析工具

users 、who、w、last、lastb

修复MBR扇区故障

备份MBR扇区数据

dd if=/dev/sda of=/backup/sda.mbr.bak bs=512 count=1

模拟MBR被破坏的故障

dd if=/dev/zero of=/dev/sda bs=512 count=1

RHEL对应版本光盘引导，进入急救模式不

boot:linux rescue

从备份文件中恢复MBR扇区

dd if=/tempdir/sda.mbr.bak of=/dev/sda bs=512 count=1

### 4.5重置root用户密码

1.开机启动系统

2.在GRUB引导界面输入e键，在e键，选择第二项，再按e键，将table=/后的单 改为1或者single

3.按b键引导启动

4.进入sh-3.1# //维护模式

5.输入passwd root

6.输入密码（不显示密码），确定密码

7.输入exit 注销并重启

\----------------------------------------------end----------------------------------------------
![v2-be7b3a919d240f369cef3d85db776fa7_hd.j](https://pic4.zhimg.com/80/v2-be7b3a919d240f369cef3d85db776fa7_hd.jpg)

##  

