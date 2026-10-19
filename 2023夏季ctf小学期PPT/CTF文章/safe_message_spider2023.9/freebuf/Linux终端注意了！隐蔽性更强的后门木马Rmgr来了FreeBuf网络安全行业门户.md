## **背景概述**

深信服终端安全团队近期捕获到一个后门木马样本，是一个64位的Linux内核模块，根据代码中出现的关键词将其命名为Rmgr木马。该木马病毒会连接恶意域名，隐藏本身的进程，并对终端植入后门，用于后续进行其他入侵行为。

经过研究人员分析，木马包含如下几个文件：

![](https://image.3001.net/images/20210922/1632279210_614a9aaa664db645bd2c7.png!small)

##  **执行流程**

木马的母体文件只有 rmgr.ko 这一个文件，通过 insmod
命令装载到内核模块后开启运作，逐步释放木马的其他组件部分。木马本身作为一个内核模块，具有ring0的权限，可以从内核层面实现隐藏进程、文件、端口等操作，相较于ring3具有更强的隐藏能力。

![](https://image.3001.net/images/20210922/1632279245_614a9acda58f98f186aa3.png!small)

##  **样本分析**

###  **rmgr.ko 分析**

####  **1、隐藏自身模块**

模块隐藏对自身进行了隐藏处理：

![](https://image.3001.net/images/20210922/1632279283_614a9af308f59932c5649.png!small)

其代码效果等同于如下：

list_del(&THIS_MODULE->list); //实现 lsmod 的隐藏

kobject_del(&THIS_MODULE->mkobj.kobj); //实现 /sys/modules 的隐藏

随后还通过底层替换 /proc/modules 文件的show函数过滤了ati_remote3模块的显示

![](https://image.3001.net/images/20210922/1632279301_614a9b054373489d44b18.png!small)![](https://image.3001.net/images/20210922/1632279309_614a9b0d1a28d7e3c6a9a.png!small)

####  **2、隐藏进程加载模块**

我们在使用诸如 cat /proc/PID/maps 这样的指令查看进程加载的模块时，底层会调用到 seq_path 函数，木马则使用了
register_kretprobe 技术对 seq_path 实施了监听，只要检测到路径为 /tmp/.tmp_ 开头的模块则将其信息隐藏，可实现
/proc/PID/maps 中木马模块的隐藏。

![](https://image.3001.net/images/20210922/1632279357_614a9b3db957238ee9735.png!small)![](https://image.3001.net/images/20210922/1632279364_614a9b44d5954a6062e16.png!small)

####  **3、隐藏文件**

木马通过hook的方式替换了 sys_getdents 系统调用，然后执行如下流程：fake_sys_getdents -> vfs_readdir ->
fake_filldir

![](https://image.3001.net/images/20210922/1632279396_614a9b645b060735b4420.png!small)![](https://image.3001.net/images/20210922/1632279405_614a9b6d90f9618931286.png!small)

fake_filldir 函数中可以看到模块隐藏了/proc/[PID]、/tmp/.tmp_*、模块自身以及所释放的数个文件，使用 ls
命令就再也看不到这些文件了；

![](https://image.3001.net/images/20210922/1632279426_614a9b824481e8fc4a003.png!small)

只有在明确知道文件名的情况下才能看到被隐藏的文件，增强了木马的隐蔽性。

![](https://image.3001.net/images/20210922/1632279434_614a9b8a3c232e533f06d.png!small)

####  **4、隐藏端口**

![](https://image.3001.net/images/20210922/1632279460_614a9ba45c91792197558.png!small)![](https://image.3001.net/images/20210922/1632279469_614a9bad1bcd5737219d1.png!small)

木马还替换了 /proc/net/tcp 文件的 seq_show 函数，隐藏 6825/6826/6821/6822 端口。

####  **5、内核与用户态进程间通信**

木马病毒创建 /proc/.dot3 文件用于接受用户态进程的指令；

![](https://image.3001.net/images/20210922/1632279504_614a9bd037dfd2f1a3462.png!small)

在 proc_create_data 的第四个参数中，/proc/.dot3 文件的写入和读取操作分别由 dot_write 和 dot_open 控制；

![](https://image.3001.net/images/20210922/1632279518_614a9bde563eaffd51a19.png!small)

查看 dot_write 的内容，通过switch case分支条件可以看出外部进程对 /proc/.dot3 写入不同的内容可以实现不同的功能：

![](https://image.3001.net/images/20210922/1632279529_614a9be904d353681a5e0.png!small)

这里是总结出来的功能列表：

 **• 8字节长度指令**

– 0xFF11 = 向木马内核模块注册写入该命令的进程，该进程及子进程将会受到内核的保护

– 0x55AA = 更新木马内核模块的文件信息

– 0x66BC = 控制C2服务器的交互频率

– 0x66BD = 向指定进程注入rmgr_inject.so文件，替换部分C库函数

– 0x66BE = 取消0x66BD指令

 **• 40字节长度指令**

– 0xA43F = 查看 rmgr_inject.so 文件的路径

– 0xA45F = 更新 rmgr_inject.so 文件的路径

– 0xF33F = 更新 rmgr.elf 文件的路径

– 0xF34F = 查看 rmgr.elf 文件的路径

 **• 其他非指令数据**

– 直接存入内核缓冲区，其内容可以通过直接读取 /proc/.dot3 文件获得

查看/proc/.dot3 的的读取部分，其实际是由 dot_show 函数实现：

![](https://image.3001.net/images/20210922/1632279564_614a9c0c09e99ccad3e2c.png!small)

dot_show 的操作：

![](https://image.3001.net/images/20210922/1632279580_614a9c1ced2f9fb7132fd.png!small)

木马病毒在读取的进程上做了限制，只允许 rmgr.elf 进程读取，而所读取到内容即是前面提到的向 /proc/.dot3 中写入的非指令数据。

####  **6、启动内核线程**

木马病毒在完成前面的工作后，启动 dot_thread 线程；

![](https://image.3001.net/images/20210922/1632279598_614a9c2ef350eb4c5cbe6.png!small)

然后释放 rmgr_inject.so 和 rmgr.elf 文件，并使用 /bin/chmod 命令赋予了 755 权限；

![](https://image.3001.net/images/20210922/1632279618_614a9c42372d8d78f3f14.png!small)![](https://image.3001.net/images/20210922/1632279632_614a9c504513513041222.png!small)

随后以 [khelper] 为名称启动了 rmgr.elf 进程。

![](https://image.3001.net/images/20210922/1632279650_614a9c621dd270130208a.png!small)

###  **rmgr_inject.so 分析**

rmgr_inject.so
是一个动态链接库，可以通过LD_PRELOAD环境变量及/etc/ld.so.preload等方式注入到普通进程中，达到替换C库函数的目的；

![](https://image.3001.net/images/20210922/1632279687_614a9c876a328ee6aee89.png!small)

rmgr_inject.so 替换了 bash_add_history
函数，将用户执行过的命令一一记录，储存到/proc/.dot3文件中，可供将来发回C2服务端；

![](https://image.3001.net/images/20210922/1632279700_614a9c9496e82d936f0ce.png!small)

同时监控 ss 指令，隐藏26660/26661/26662/26657/26658/26659这几个端口。

###  **rmgr.elf 分析**

rmgr.elf加了UPX壳，脱壳后的函数列表如下：

![](https://image.3001.net/images/20210922/1632279724_614a9cac1735365ad7b07.png!small)

可以看出该二进制文件是由C++编写的。经过分析后得知该文件包含两个类，rmgr_client类处理与C2服务器的交互，sshd_client类处理与sshd后门的交互。

####  **1、利用内核模块隐藏进程**

![](https://image.3001.net/images/20210922/1632279741_614a9cbd682fe85af69c3.png!small)

进程启动后首先第一件事就是向 /proc/.dot 写入 0xFF11 指令获得保护，利用rmgr.ko 的ring0权限隐藏自身进程以及子进程。

####  **2、与C2服务器通信**

随后与 hm2.yrnykx.com C2服务器进行连接，等待指令；

![](https://image.3001.net/images/20210922/1632279756_614a9ccc8037cd43af7f4.png!small)

rmgr_client::handle_read_body 函数负责处理C2服务端发来的命令；

![](https://image.3001.net/images/20210922/1632279775_614a9cdf696b0df752146.png!small)

这里整理了一份可供C2服务端调用的功能指令，列表如下：

• 0x1000F = 从C2服务端下载更新木马的所有组件

• 0x10008 = 未知功能

• 0x1000A = 创建一个新的sshd后门会话

• 0x1000B = 关闭指定的sshd后门会话

• 0x10004 = 读取 /proc/.dot3 中储存的内容，发往C2服务器

• 0x10007 = 接收文件

• 0x10011 = 启动sshd后门

• 0x10012 = 停止sshd后门

• 0x10010 = 暂停sshd后门

其中比较值得注意的是，收到0x10011指令后，rmgr.elf会从自身释放出 rmgr_sshd.elf
后门文件并启动，这是个被修改过的openssh服务，后面会有这个文件的分析；

![](https://image.3001.net/images/20210922/1632279818_614a9d0add95a04c004b0.png!small)

创建好ssh后门后（监听地址是127.0.0.1:26657），C2服务端便可使用 0x1000A
指令连接，此时C2服务器和ssh后门的流量会通过sshd_client类进行处理和转发；

![](https://image.3001.net/images/20210922/1632279834_614a9d1a210d6e58980dc.png!small)

rmgr.elf 还存在下载替换
/usr/sbin/sshd、/usr/bin/ssh、/lib/modules/%s/kernel/drivers/input/misc/ati_remote3.ko、/etc/sysconfig/modules/ati_remote3.modules
文件的行为。

![](https://image.3001.net/images/20210922/1632279863_614a9d37f3226430cc33a.png!small)

###  **rmgr_sshd.elf 分析**

rmgr_sshd.elf
由rmgr.elf释放，本身是一个被修改过的openssh，用于提供ssh后门。该后门的配置文件是硬编码的，监听地址为127.0.0.1:26657。

![](https://image.3001.net/images/20210922/1632279875_614a9d43063ca25e5bb70.png!small)

ssh中硬编码的私钥文件：

![](https://image.3001.net/images/20210922/1632279886_614a9d4e112a0bc00ec9a.png!small)

这个ssh后门的认证函数还被修改过了，不论输入什么密码都会直接认证成功。

![](https://image.3001.net/images/20210922/1632279896_614a9d5823214a4da2746.png!small)

由于ssh后门的监听地址位于本地，因此从外部扫描是观察不到这个后门存在的，并且只能通过rmgr.elf中的sshd_client对象进行流量转发访问。

##  **IOC**

a4013790035fc3021546c09e9cf85df1

5ecf30b7a6221af8f209a7b6681f91f9

7d859a22f38f0bcd55a46bc8b67c40df

82bf8e99391ec0cdc527f2fc94621899

hxxp://hm2.yrnykx.com

