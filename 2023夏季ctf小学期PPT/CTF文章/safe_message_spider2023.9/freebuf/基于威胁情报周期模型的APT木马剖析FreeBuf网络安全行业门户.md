## **前言**

近日，腾讯服务器安全系统“洋葱”协助部署于公有云的某合作方捕获到一起APT事件，目前已处置完毕。处置过程中捕获木马样本一枚，该样本中包含了大量隐匿攻击手法，“洋葱”团队会同腾讯安全应急响应中心（TSRC）秉承共建行业安全生态的原则，采用威胁情报处理周期模型梳理该攻击手法，将分析结果与业界共享。

![](https://image.3001.net/images/20210208/1612786474_60212b2a66128ea4007aa.png!small)

 **关于威胁情报处理周期模型**

>
> “威胁情报处理周期”（F3EAD）一词源于军事，是美陆军为主战兵种各级指挥员设计的组织资源、部署兵力的方法。网络应急响应中心借鉴这套方法，分以下六个阶段处理威胁情报信息：

![](https://image.3001.net/images/20210208/1612786612_60212bb45e3245fdef1ad.png!small)威胁情报处理周期F3EAD

##  **威胁情报处理周期模型** **的应用**

###  **第一步：查找**

某月某日，部署在合作方公有云服务器上的“洋葱”系统告警发现疑似木马程序，于是应急响应团队快速启动应急相应流程：

> 干系人等一键拉群，电话接入。
>
> 受害系统隔离待查。
>
> 安全系统、审计日志导出待溯源分析。
>
> 业务系统架构、代码相关资料准备，待分析入侵突破口及受影响范围

###  **第二步：定位**

根据安全系统的审计记录发现，恶意文件目录存在另一个*.ko文件，而此文件是通过scp从另一服务器传过来。

由此可见，攻击者首先拿到某个存在弱点的服务器权限，然后再跳转scp木马文件到包括当前受害机在内的通过已攻陷的服务器可访问的机器，并安装控制。

接下来咱们重点分析这组木马文件，根据AV厂商的命名规则（附录1），暂为其命名为"Backdoor:Linux/Rmgr!rookit"，其中“rmgr”来至木马代码中多个函数用了rmgr前缀。

 **2.1. 木马文件**

目前已经掌握的木马文件分四部分，其功能简单描述如下：

![](https://image.3001.net/images/20210208/1612786951_60212d079e72afbc878b0.png!small)

 **2.2 木马工作流程**

木马从植入到运行，包括后续可能的渗透活动都采用了各种技术进行隐藏，如果没有安全系统则很难发现。同时，该木马也做了很多对抗，常规的安全监测能力未必可以发现。其运行流程简要描述如下图：

![](https://image.3001.net/images/20210208/1612786999_60212d37f16b4ac0afa33.png!small)

木马工作流程

 **2.3 木马各部分主要功能**

 **1\. rmgr.ko**

rootkit采用常见的LKM内核模块。下面逐个列举此rootkit加载后的主要操作。

1）proc_create_data创建虚拟文件/proc/.dot3，用于后续与木马用户态进程交互；

2) register_kprobe注册4个kp结构体：

kp_kallsyms_lookup_name\krp_alloc_pid\kp_do_exit\kp_seq_path，用于通过kprobe来抢先在系统执行到这些函数的时候抹除对木马进程的操作；

![](https://image.3001.net/images/20210208/1612787077_60212d858eafba8efe81a.png!small)

3) 上述kp结构注册的处理函数，fake_seq_path用于摘除内核进程链表；

![](https://image.3001.net/images/20210208/1612787092_60212d943e60225f1dfd0.png!small)

4) 当系统有读“/proc/net/tcp”文件的时候，由fake_seq_show处理，抹除木马网络连接；

![](https://image.3001.net/images/20210208/1612787111_60212da780e3cc3b3f60a.png!small)

5) 在fake_sys_getdents中patch vfs_readdir，抹除与木马相关的所有信息；

![](https://image.3001.net/images/20210208/1612787123_60212db3dbd11f7ae2737.png!small)

6) 当系统对木马相关文件访问的时候，会由fake_filldir处理，根据判断调用者是否木马操作来决定是否返回正确结果；

![](https://image.3001.net/images/20210208/1612787147_60212dcb8435403a887ac.png!small)

7) 在内核模块链表中删除自己，kobject_del删除自己的内核对象；

![](https://image.3001.net/images/20210208/1612787168_60212de0c2026ad23c25a.png!small)

8) kthread_create创建内核线程dot_thread

![](https://image.3001.net/images/20210208/1612787185_60212df131453b504b3ca.png!small)

> 创建内核模块自启动/etc/sysconfig/modules/ati_remote3.modules
>
> 写入内核模块文件/lib/modules/%s/kernel/drivers/input/misc/ati_remote3.ko
>
> 释放rmgr_fake_libc.so文件到磁盘
>
> 释放rmgr_daemon文件到磁盘，并以“[khelper]”进程名通过call_usermodehelper_exec运行它。

![](https://image.3001.net/images/20210208/1612787237_60212e250f125985db9df.png!small)

 **2\. rmgr__fake_libc.so**

此共享库文件，由内核rootkit释放写入磁盘，路径为/tmp/.tmp_{21个随机字母数字}，用于木马的用户态进程的行为隐藏。

subhook前缀的函数摘抄自开源代码（附录2），详细功能请移步github围观，本文不赘述。

![](https://image.3001.net/images/20210208/1612787274_60212e4adb68d31f2b15d.png!small)

fake前缀的函数主要用于对抗常见HIDS的进程和命令记录，fork和execve直接通过syscall调用，而不使用glibc的封装，避开了hook
glibc方式的HIDS。

![](https://image.3001.net/images/20210208/1612787304_60212e68d016fd7e9c275.png!small)

fake_bash_add_history则让bash命令审计功能失效。

![](https://image.3001.net/images/20210208/1612787318_60212e760686040053d01.png!small)

 **3\. rmgr_daemon**

此进程由rmgr.ko释放写入磁盘，路径为/tmp/.tmp_{21个随机字母数字}。由C++开发，编译后upx加壳压缩，直接用开源软件upx -d
rmgr_daemon即可脱壳，并无特殊处理。

它主要有的功能有：

1) 监控内核模块状态，与内核rootkit信息交互；

![](https://image.3001.net/images/20210208/1612787350_60212e96c71ea8818113a.png!small)2)
更新；

![](https://image.3001.net/images/20210208/1612787366_60212ea69e07fb095b198.png!small)3)
生成rmgr_fake_sshd，并patchELF，修改依赖的动态库，也就是加入rmgr_fake_libc.so，功能如前述；

![](https://image.3001.net/images/20210208/1612787391_60212ebff1a4936137b50.png!small)从内核获取路径

![](https://image.3001.net/images/20210208/1612787419_60212edbda08f50b134f1.png!small)返回路径

![](https://image.3001.net/images/20210208/1612787445_60212ef5a217d1c249078.png!small)

patch ELF

4) 连接C2
hm2.yrnykx.com；![](https://image.3001.net/images/20210208/1612787471_60212f0fcc5618a38bdf4.png!small)5)
管理rmgr_fake_sshd；

其中patchELF代码摘抄自GitHub - NixOS/patchelf （附录3）

 **4\. rmgr_fake_sshd**

文件由rmgr_daemon写入磁盘，路径为/tmp/.tmp_{21个随机字母数字}，它的运行均由rmgr_daemon管理。

作为后门它硬编码了PRIVATE KEY
，如下图：![](https://image.3001.net/images/20210208/1612787520_60212f40db0777cc635a9.png!small)

因为通过patchELF
hook了部分函数，实现了ssh登录之后的命令执行等行为的隐匿。而rmgr_fake_sshd本身，以及ssh登录派生的子进程均通过rmgr.ko根据前述分析通过patch内核调用实现隐匿。

rmgr_fake_sshd启动时加载了硬编码的sshd_config，请注意其中几个关键配置。![](https://image.3001.net/images/20210208/1612787545_60212f59c6be922195c2a.png!small)监听在本地的26657端口，rmgr_daemon连接此端口转发来至C2的ssh指令。这里实现了拟合业务环境常用网络协议，使得常规的NIDS的检测逻辑被绕过。

###  **第三步：消除**

这里主要是指加固，避免被攻击者以同样的手法攻击。具体手段如下：

> 突破口加固，补丁更新，ACL加固。
>
> 运维通道，停用旧账户，修改攻击链路中服务器账户，并上双因素认证。
>
> 根据用户角色限定可访问系统范围。
>
> 受害系统dump保存虚机镜像，待查。
>
> 重装受害系统，重新发布部署业务环境。
>
> 新系统内核模块加载要求签名校验。

###  **第四步：利用**

完成应急响应工作，分析完事件现场和文件之后，整个事件中提取到的关键信息将沉淀为威胁情报。本文将威胁情报金字塔模型的内容缩减到iocs和ttps两部分，ttps用att&ck矩阵模型做归纳。![](https://image.3001.net/images/20210208/1612787609_60212f9946b658f49b0df.png!small)威胁情报金字塔模型

 **1\. iocs**

1) md5：

7d859a22f38f0bcd55a46bc8b67c40df

fa73b2fd914a0cfd5e7d3161af903b6c

2) c2:

hm2.yrnykx.com

 **2\. ttps**

![](https://image.3001.net/images/20210208/1612787639_60212fb7df62b9780e4ee.png!small)

###  **第五步：分析**

从上节ttps可以看出来，att&ck矩阵并不能完全覆盖此次木马用于对抗安全系统的全部隐匿手段。

粗略的分类其隐匿（进程、网络、文件）手段有：

> C2通过fake_sshd避开NIDS的检测；
>
> 通过patchELF绕开hook libc的命令审计HIDS；
>
> 通过fake_bash_add_history让shell审计失效；
>
> 通过patch seq_show修改系统对/proc下文件信息读取的返回，实现对木马相关的文件、进程、网络连接信息的隐匿；
>
> 通过patch vfs_readdir实现隐藏木马文件；
>
> 通过摘除内核进程、模块链表信息，避免被rookit检测工具发现内核中木马痕迹；

可见，此款木马套装存在大量技术细节来对抗安全系统，不过它主要针对市面上已知的一些旧款HIDS和事后取证调查工具。内核态的进程派生syscall
hook和inotify+云查杀还是可以发现它的。

![](https://image.3001.net/images/20210208/1612787695_60212fef6a608fa5bbcbb.png!small)

木马与安全系统的对抗维度

一套完整的木马系统不可能仅仅因为一次渗透入侵而开发，必然会借鉴很多开源或者家族代码。所以从溯源角度来说，可以做代码“考古”工作，同时将相关代码风格和木马行为纳入安全系统特征库。限于篇幅，暂不在此赘述。

###  **第六步：传播**

传播即本文本身。

##  **总结**

事实上，实际的事件响应处置过程顺序不可能完全跟上述流程一致。但走完整套流程，笔者认为才能算是一个安全事件处置圆满的结束。其实，F3EAD流程比较重视情报从分析到应用（改进安全对抗能力），特别是在“分析”阶段的反复迭代。![](https://image.3001.net/images/20210208/1612787753_602130292bc5cb6a4b213.png!small)F3EAD周期的分析阶段(迭代)（参考《情报驱动应急响应》）

从冰冷的情报到落地到我们安全系统安全能力的提升，这才实现了威胁情报的真正价值。

###  **附录**

> 1\. Malware names, https://docs.microsoft.com/en-us/windows/security/threat-> protection/intelligence/malware-naming
>
> 2\. subhook, https://github.com/Zeex/subhook/blob/master/subhook_x86.c
>
> 3\. NixOS/patchelf, https://github.com/NixOS/patchelf
>
> 4\. 《情报驱动应急响应》，斯科特·罗伯茨（Scott J.Roberts）

