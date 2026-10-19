**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/Tm4z-_po6DmurcneKQ536A>**

## **1.1** **简介**

XNU将进程凭证credential、文件系统acl授权、进程和文件系统监控这几个安全功能抽象为一个安全框架，叫做kauth子系统。它的具体功能主要包含：

\- 进程凭证credential的创建、更新、销毁。

\- 文件系统acl的创建、评估、销毁。

\- 提供kauth scope框架，对进程、文件系统做监控， 支持系统默认监控函数，提供kpi接口，使得第三方内核扩展可以动态添加钩子。

## **1.2** **进程凭证维护**

### **1.2.1 基本结构**

XNU与传统UNIX的进程凭证cred稍有不同。

    
    
    bsd/sys/ucred.h：
    struct ucred {
            TAILQ_ENTRY(ucred)      cr_link; /* never modify this without KAUTH_CRED_HASH_LOCK */
            u_long  cr_ref;                 /* reference count */
    struct posix_cred {
            uid_t   cr_uid;                 /* effective user id */
            uid_t   cr_ruid;                /* real user id */
            uid_t   cr_svuid;               /* saved user id */
            short   cr_ngroups;             /* number of groups in advisory list */
            gid_t   cr_groups[NGROUPS];     /* advisory group list */
            gid_t   cr_rgid;                /* real group id */
            gid_t   cr_svgid;               /* saved group id */
            uid_t   cr_gmuid;               /* UID for group membership purposes */
            int     cr_flags;               /* flags on credential */
    } cr_posix;
            struct label    *cr_label;      /* MAC label */
            struct au_session cr_audit;             /* user auditing data */
    };

struct ucred基本继承了BSD的ucred结构，保留了MAC
label和audit审计成员，因为xnu内核完全继承了BSD的MAC和audit子系统能力。同时去掉了poison成员， xnu没有使用bsd
jail的功能，对于xnu的沙箱功能，在后面的系列文章中在详细介绍。xnu
ucred仍然包含用户所在的组概念，成员cr_groups数组长度为16，是unix家族中标准的用户组大小。除了cr_groups，xnu使用kauth子系统扩展了用户所在组的概念，cr_groups包含的仅是本地机器的用户组，Mac
OS可以作为服务器使用，kauth建立了一种额外的扩展能力，可以将网络上的其他机器用户组包含到本地组里。

XNU是一个混合的内核，mach微内核部分控制内核的进程创建与调度功能，
mach的进程结构体包含了指向bsd进程和线程结构体的指针，而cred是BSD内核的功能，自然包含在bsd封装的进程和线程结构体里，它们之间的数据结构体关系如下：

![](https://images.seebug.org/content/images/2021/01/2dd4ee24-4013-4d63-aa29-52d396fc25e5.png-w331s)

内核通过current_thread()宏来获取mach层的struct thread指针，以i386架构为例：

    
    
    osfmk/i386/cpu_data.h
    
    #define current_thread_fast()           get_active_thread()
    #define current_thread()                current_thread_fast()
    
    static inline __pure2 thread_t
    get_active_thread(void)
    {
            CPU_DATA_GET(cpu_active_thread,thread_t)
    }
    
    #define CPU_DATA_GET(member,type)                                       \
            type ret;                                                       \
            __asm__ volatile ("mov %%gs:%P1,%0"                             \
                    : "=r" (ret)                                            \
                    : "i" (offsetof(cpu_data_t,member)));                   \
            return ret；
    
    typedef struct cpu_data
    {
            thread_t                cpu_active_thread;
    } cpu_data_t;

cpu_data_t结构体里的cpu_active_thread成员指向的就是当前cpu指向的mac thread指针，
通过offsetof宏计算处它的偏移，在i386下%gs:offset保存的就是它的地址。X64下保存在%fs:offset。

内核通过get_bsdthread_info函数获取mac thread指向的bsd thread指针：

    
    
    osfmk/kern/bsd_kern.c
    
    void *get_bsdthread_info(thread_t th)
    {
            return(th->uthread);
    }

内核通过get_threadtask函数获取mac thread指向的mac task指针，然后就可以通过mac task找到bsd进程的proc指针。

    
    
    osfmk/kern/bsd_kern.c
    
    task_t  get_threadtask(thread_t th)
    {
            return(th->task);
    }
    
    void  *get_bsdtask_info(task_t t)
    {
            return(t->bsd_info);
    }

内核通过kauth_cred_get函数获取进程的cred结构指针，根据以上结构信息也就不难理解了。

    
    
    bsd/kern/kern_credential.c
    
    kauth_cred_t
    kauth_cred_get(void)
    {
            struct proc *p;
            struct uthread *uthread;
    
            uthread = get_bsdthread_info(current_thread());
            if (uthread == NULL)
                    panic("thread wants credential but has no BSD thread info");
    
            if (uthread->uu_ucred == NOCRED) {
                    if ((p = (proc_t) get_bsdtask_info(get_threadtask(current_thread()))) == NULL)
                            panic("thread wants credential but has no BSD process");
                    uthread->uu_ucred = kauth_cred_proc_ref(p);
            }
            return(uthread->uu_ucred);
    }

### **1.2.2 cred维护**

XNU对于进程cred的维护与BSD、linux有所不同，
它将每个进程的cred缓存在一个hash表里，对于复制cred等操作，可以通过引用计数来实现，在它的代码注释中提到这种优化对于一个桌面系统来讲，可以至少节省200k左右的内存。

### **1.2.3 组扩展机制**

前面提到xnu扩展了bsd的用户组管理机制，在内核中叫做kauth resolver机制，
在kauth初始化时，建立了几个队列，当内核使用cred进行用户组授权的过程中，
将本次请求封装为一个worker，加入相应的队列中等待用户态进程进行处理。xnu增加了一个系统调用identitysvc，用户进程使用这个系统调用与kauth通讯，比如获取等待队列中的worker，然后在用户态进行处理。用户组涉及到的处理逻辑相对复杂，xnu直接引用了windows
nt内核的sid概念来完善kuath授权系统。

#### **1.2.3.1 kauth resolver机制初始化**

    
    
    bsd/kern/kern_authorization.c
    
    void
    kauth_init(void)
    {
    #if CONFIG_EXT_RESOLVER
            kauth_identity_init();[1]
            kauth_groups_init();[2]
    #endif
    
    #if CONFIG_EXT_RESOLVER
            kauth_resolver_init();[3]
    #endif
    }

Kauth_init在初始时[1]处调用kauth_identity_init()初始化kauth_identities链表，每个节点是struct
kauth_identity结构体，这个链表用来缓存cred的身份信息，因为如果每次身份验证时都要用户态进程参与，那么效率将会非常低，kauth在每次用户态验证完时，将验证成功的身份信息缓存在kauth_identities链表里，下次验证时将在缓存里进行搜索，如果没有匹配到，在通知用户态进程处理。[2]处的kauth_groups_init()函数功能机理与上述一致。[3]处的kauth_resolver_init函数初始化了三个队列，分别为kauth_resolver_unsubmitted、kauth_resolver_submitted、kauth_resolver_done。

#### **1.2.3.2 identitysvc系统调用**

用户态进程通过调用identitysvc系统调用在内核中进行注册，更新缓存大小、获取处理任务以及发送任务的处理结果。

先来看下用户进程的注册过程。

    
    
    bsd/kern/kern_credential.c
    
    int
    identitysvc(__unused struct proc *p, struct identitysvc_args *uap, __unused int32_t *retval)
    {
     if (opcode == KAUTH_EXTLOOKUP_REGISTER) {
                    new_id = current_proc()->p_pid;
                    if ((error = kauth_authorize_generic(kauth_cred_get(), KAUTH_GENERIC_ISSUSER)) != 0) {                                            [1]
                            KAUTH_DEBUG("RESOLVER - pid %d refused permission to become identity resolver", new_id);
                            return(error);
                    }
    
                    if (kauth_resolver_identity != new_id) {[2]
                            kauth_resolver_identity = new_id;[3]
                            kauth_resolver_registered = 1;
                            wakeup(&kauth_resolver_unsubmitted);[4]
    }

当来自用户空间的请求码为KAUTH_EXTLOOKUP_REGISTER时， 在[1]处调用 kauth_authorize_generic，
这是后面将要讲到的kauth scope监控机制，当前内核的默认授权只是检测当前进程uid是不是为0，
也就是说只有root权限用户才可以注册。[2]处判断当前进程和之前注册的进程号是否相同，如果不相同就会用当前进程号替换原来的进程号kauth_resolver_identity，然后在[4]处唤醒kauth_resolver_unsubmitted等待队列上的进程。

我们看到用户进程的注册过程相当简单，这里就会有几个安全问题。所有root进程都可以进行注册，linux使用了capability进一步将root权限进行了划分，
比如auditd的注册就需要有CAP_NET_ADMIN这个能力才可以。而XNU并没有继承BSD的capability能力模型以及privilege特权模型，这使得它对内核权限的控制就没有那么细致化。其次新的用户进程直接就可以替换老的用户进程，并没有使用一些可信验证手段，
这使得任何的恶意root进程都可以对其进行替换和仿冒，这样身份验证机制就形同虚设了。

我们在来看下用户进程是如何从内核获取任务的。

    
    
    bsd/kern/kern_credential.c
    
    int
    identitysvc(__unused struct proc *p, struct identitysvc_args *uap, __unused int32_t *retval)
    {
            if (opcode & KAUTH_EXTLOOKUP_WORKER) {
                    if ((error = kauth_resolver_getwork(message)) != 0)
                            return(error);
            }
    }
    
    static int
    kauth_resolver_getwork(user_addr_t message)
    {
            struct kauth_resolver_work *workp;
    
            while ((workp = TAILQ_FIRST(&kauth_resolver_unsubmitted)) == NULL) {
                    thread_t thread = current_thread();
                    struct uthread *ut = get_bsdthread_info(thread);
    
                    ut->uu_save.uus_kauth.message = message;
                    error = msleep0(&kauth_resolver_unsubmitted, kauth_resolver_mtx, PCATCH, "GRGetWork", 0, kauth_resolver_getwork_continue);
                    KAUTH_RESOLVER_UNLOCK();
    
                    if (!kauth_resolver_identity) {
                            printf("external resolver died");
                            error = KAUTH_RESOLVER_FAILED_ERRCODE;
                    }
    
                    return(error);
            }
    
            return kauth_resolver_getwork2(message);
    }

kauth_resolver_getwork函数用户获取内核任务，
首先判断kauth_resolver_unsubmitted队列是否为空，这个队列保存的是内核发布的等待用户进程获取的任务节点，下一小节会对其进行描述。如果队列为空，就使用msleep进行睡眠，同时回调函数设置为kauth_resolver_getwork_continue，这个函数只是继续判断队列是否为空，然后递归调用自己。当队列不为空时，会调用kauth_resolver_getwork2。它从kauth_resolver_unsubmitted队列头取下一个节点，用copyout函数拷贝给用户空间的进程，然后将这个节点移入到kauth_resolver_submitted队列，这样用户进程就获取了要进行身份验证的信息。

当用户进程处理完毕后，处理结果要返回给内核。

    
    
    bsd/kern/kern_credential.c
    
    int
    identitysvc(__unused struct proc *p, struct identitysvc_args *uap, __unused int32_t *retval)
    {
            if (opcode & KAUTH_EXTLOOKUP_RESULT) {
                    if ((error = kauth_resolver_complete(message)) != 0)
                            return(error);
            }
    }
    
    static int
    kauth_resolver_complete(user_addr_t message)
    {
            if ((error = copyin(message, &extl, sizeof(extl))) != 0) {
                    KAUTH_DEBUG("RESOLVER - error getting completed work\n");
                    return(error);
            }
    
            if (extl.el_result != KAUTH_EXTLOOKUP_FATAL) {
                    TAILQ_FOREACH(workp, &kauth_resolver_submitted, kr_link) {
                            if (workp->kr_seqno == extl.el_seqno) {
                                    TAILQ_INSERT_TAIL(&kauth_resolver_done, workp, kr_link);
    }

kauth_resolver_complete通过copyin将用户信息拷贝到内核，然后遍历kauth_resolver_submitted队列，根据seq号找到对应的节点，更新处理信息，然后将这个节点移动到kauth_resolver_done队列。

### 1.2.3.3 cred身份验证

当涉及到cred的身份验证时，kauth调用kauth_cred_cache_lookup函数进行处理。

    
    
    bsd/kern/kern_credential.c
    
    static int
    kauth_cred_cache_lookup(int from, int to, void *src, void *dst)
    {
            switch(from) {
            case KI_VALID_UID:[1]
                    error = kauth_identity_find_uid(*(uid_t *)src, &ki, namebuf);
                    if (expired) {
                            if (!expired(&ki)) {[2]
                                    KAUTH_DEBUG("CACHE - entry valid, unexpired");
    
            error = kauth_resolver_submit(&el, extend_data);[3]
            if (error == 0) {
                    kauth_identity_updatecache(&el, &ki, extend_data);[4]
    }

kauth在kauth_identities
cache中维护着一个转换列表，cred中的uid可以对应kauth_identities中的guid、ntsid等等。比如转换类型为KI_VALID_UID，则在[1]处调用kauth_identity_find_uid，在cache中进行搜索。找到后，还要在[2]处进行验证身份信息是否过

    
    
    static int
    
    kauth_resolver_submit(struct kauth_identity_extlookup *lkp, uint64_t extend_data)
    {
            struct kauth_resolver_work *workp, *killp;
    
            MALLOC(workp, struct kauth_resolver_work *, sizeof(*workp), M_KAUTH, M_WAITOK); [1]
            if (workp == NULL)
                    return(ENOMEM);
    
            workp->kr_work = *lkp;
            workp->kr_extend = extend_data;
            workp->kr_refs = 1;
            workp->kr_flags = KAUTH_REQUEST_UNSUBMITTED;
            workp->kr_result = 0;
    
            KAUTH_RESOLVER_LOCK();
            workp->kr_seqno = workp->kr_work.el_seqno = kauth_resolver_sequence++;
            workp->kr_work.el_result = KAUTH_EXTLOOKUP_INPROG;
    
    TAILQ_INSERT_TAIL(&kauth_resolver_unsubmitted, workp, kr_link);    [2]
        wakeup_one((caddr_t)&kauth_resolver_unsubmitted);   [3]
        error = __KERNEL_IS_WAITING_ON_EXTERNAL_CREDENTIAL_RESOLVER__(workp); [4]
        if (error == 0)
        *lkp = workp->kr_work;   [5]
    
    }

期。如果没找到会在[3]处调用kauth_resolver_submit， 将当前处理信息封装为一个struct
kauth_identity_extlookup结构体发送到等待队列中进行处理。

[1] 处封装为一个struct kauth_resolver_work
worker节点，在[2]处挂接到kauth_resolver_unsubmitted队列末尾，在[3]处唤醒在这个等待队列上睡眠的进程，通常为用户态的memberd守护进程。然后在[4]处调用
_KERNEL_IS_WAITING_ON_EXTERNAL_CREDENTIAL_RESOLVER_函数，它一直调用msleep睡眠kauth_resolver_timeout秒，再次被唤醒后，检查worker的状态是否为KAUTH_REQUEST_DONE，如果是则函数返回，否则继续睡眠重复上述行为。当worker被处理完毕后，在[5]处保存更新后的信息。这个信息是用户态进程处理完毕后使用identitysvc系统调用进行同步的。回到kauth_cred_cache_lookup函数，它将调用kauth_identity_updatecache在缓存中更新相关信息。

### **1.2.4 进程和文件系统监控**

#### **1.2.4.1 kauth scope框架**

Kauth定义了一个scope监控框架，提供默认和第三方内核扩展回调函数支持，可以对进程和文件系统的关键行为进行监控。

监控类型有几下几种：

    
    
    bsd/sys/kauth.h
    
    #define KAUTH_SCOPE_GENERIC     "com.apple.kauth.generic"
    #define KAUTH_SCOPE_PROCESS     "com.apple.kauth.process"
    #define KAUTH_SCOPE_VNODE       "com.apple.kauth.vnode"
    #define KAUTH_SCOPE_FILEOP      "com.apple.kauth.fileop"

KAUTH_SCOPE_GENERIC是通用的内核事件监控函数，比如在前面章节讲到的用户态进程注册kauth
resovler时就调用了它的默认监控函数，只判断进程的uid号是否为0。

KAUTH_SCOPE_PROCESS提供进程事件的相关监控，目前只对能否向目标进程发送信号和是否有调试权限做了监控。

KAUTH_SCOPE_VNODE提供了对vnode的权限检查以及acl评估功能。

KAUTH_SCOPE_FILEOP提供了对文件状态和属性更改的监控，它类似于linux的fsnotify文件系统监控框架。

Kauth子系统定义了struct kauth_scope结构：

    
    
    #define KAUTH_SCOPE_MAX_LISTENERS  15
    
    struct kauth_scope {
            TAILQ_ENTRY(kauth_scope)        ks_link;
            volatile struct kauth_local_listener  ks_listeners[KAUTH_SCOPE_MAX_LISTENERS];
            const char *                            ks_identifier;
            kauth_scope_callback_t          ks_callback;
            void *                                          ks_idata;
            u_int                                           ks_flags;
    };

ks_callback即为默认的callback函数。ks_listeners为第三方内核扩展定义的callback函数。每个scope最多有15个扩展回调函数。

    
    
    struct kauth_local_listener {
            kauth_listener_t                        kll_listenerp;
            kauth_scope_callback_t          kll_callback;
            void *                                          kll_idata;
    }

内核使用kauth_register_scope注册一个scope。

    
    
    kauth_scope_t
    
    kauth_register_scope(const char *identifier, kauth_scope_callback_t callback, void *idata)
    {
            kauth_scope_t           sp, tsp;
            kauth_listener_t        klp;
    
            if ((sp = kauth_alloc_scope(identifier, callback, idata)) == NULL)
                    return(NULL);
    
            KAUTH_SCOPELOCK();
            TAILQ_FOREACH(tsp, &kauth_scopes, ks_link) {
                    if (strncmp(tsp->ks_identifier, identifier,
                                            strlen(tsp->ks_identifier) + 1) == 0) {
                            KAUTH_SCOPEUNLOCK();
                            FREE(sp, M_KAUTH);
                            return(NULL);
                    }
            }
    
            TAILQ_INSERT_TAIL(&kauth_scopes, sp, ks_link);
    restart:
            TAILQ_FOREACH(klp, &kauth_dangling_listeners, kl_link) {
                    if (strncmp(klp->kl_identifier, sp->ks_identifier,
                                            strlen(klp->kl_identifier) + 1) == 0) {
                            if (kauth_add_callback_to_scope(sp, klp) == 0) {
                                    TAILQ_REMOVE(&kauth_dangling_listeners, klp, kl_link);
                            }
    
                            else {
                                    break;
                            }
    
                            goto restart;
                    }
            }
    
            KAUTH_SCOPEUNLOCK();
            return(sp);
    }

所有scope存在于kauth_scopes链表，kauth_register_scope首先根据名称搜索是否已经存在重名的scope节点，存在直接返回。如果不存在的话，将其挂接于kauth_scopes链表末尾。然后它遍历kauth_dangling_listeners链表，这里保存的是备用的第三方回调函数节点kauth
listener, 调用kauth_add_callback_to_scope将其添加到对应的scope listener数组里。

    
    
    static int kauth_add_callback_to_scope(kauth_scope_t sp, kauth_listener_t klp)
    {
            int             i；
    
            for (i = 0; i < KAUTH_SCOPE_MAX_LISTENERS; i++) {
                    if (sp->ks_listeners[i].kll_listenerp == NULL) {
                            sp->ks_listeners[i].kll_callback = klp->kl_callback;
                            sp->ks_listeners[i].kll_idata = klp->kl_idata;
                            sp->ks_listeners[i].kll_listenerp = klp;
                            sp->ks_flags |= KS_F_HAS_LISTENERS;
                            return(0);
                 }
            }
    
            return(ENOSPC);
    }

内核使用kauth_listen_scope函数注册一个第三方内核扩展listener到一个scope上。

    
    
    kauth_listener_t
    
    kauth_listen_scope(const char *identifier, kauth_scope_callback_t callback, void *idata)
    {
            kauth_listener_t klp;
            kauth_scope_t   sp;
    
            if ((klp = kauth_alloc_listener(identifier, callback, idata)) == NULL)
                    return(NULL);
    
            KAUTH_SCOPELOCK();
            TAILQ_FOREACH(sp, &kauth_scopes, ks_link) {
                    if (strncmp(sp->ks_identifier, identifier,
                                            strlen(sp->ks_identifier) + 1) == 0) {
    
                            if (kauth_add_callback_to_scope(sp, klp) == 0) {
                                    KAUTH_SCOPEUNLOCK();
                                    return(klp);
                            }
    
                            KAUTH_SCOPEUNLOCK();
                            FREE(klp, M_KAUTH);
                            return(NULL);
                    }
            } 
    
            TAILQ_INSERT_TAIL(&kauth_dangling_listeners, klp, kl_link);
            KAUTH_SCOPEUNLOCK();
    
            return(klp);
    }

它的注册逻辑也非常简单，首先遍历kauth_scopes链表找到对应的scope，如果找到，就调用kauth_add_callback_to_scope将其加入scope的listener数组里。如果没找到，将这个节点挂接于kauth_dangling_listeners备用链表中，
当需要的scope被注册时，会自动从kauth_dangling_listeners链表中找到这个节点并挂接上去。

在需要监控的内核路径中， 会调用kauth_authorize_action函数。

    
    
    int
    
    kauth_authorize_action(kauth_scope_t scope, kauth_cred_t credential, kauth_action_t action,
        uintptr_t arg0, uintptr_t arg1, uintptr_t arg2, uintptr_t arg3)
    {
            int result, ret, i;
    
            if (scope->ks_callback != NULL)
                    result = scope->ks_callback(credential, scope->ks_idata, action, arg0, arg1,
            else
                    result = KAUTH_RESULT_DEFER;
    
            if ((scope->ks_flags & KS_F_HAS_LISTENERS) != 0) {
                    for (i = 0; i < KAUTH_SCOPE_MAX_LISTENERS; i++) {
                            ret = scope->ks_listeners[i].kll_callback(
                                            credential, scope->ks_listeners[i].kll_idata,
                                            action, arg0, arg1, arg2, arg3);
                            if ((ret == KAUTH_RESULT_DENY) ||
                                    (result == KAUTH_RESULT_DEFER))
                                    result = ret;
                    }
            }
            return(result == KAUTH_RESULT_ALLOW ? 0 : EPERM);
    }

首先它会调用默认的回调函数，然后如果此scope有listener，则将依次调用listener注册的回调函数，
算法有点类似acl评估机制，如果有一个listener拒绝的话就直接返回失败。

#### **1.2.4.2 进程监控**

Kauth在初始化的时候调用kauth_scope_init初始化三个监控类型的scope。

    
    
    static void
    kauth_scope_init(void)
    {
            kauth_scope_mtx = lck_mtx_alloc_init(kauth_lck_grp, 0 /*LCK_ATTR_NULL*/);
            kauth_scope_process = kauth_register_scope(KAUTH_SCOPE_PROCESS, kauth_authorize_process_callback, NULL);
            kauth_scope_generic = kauth_register_scope(KAUTH_SCOPE_GENERIC, kauth_authorize_generic_callback, NULL);
            kauth_scope_fileop = kauth_register_scope(KAUTH_SCOPE_FILEOP, NULL, NULL);
    }

对于进程的监控，注册的默认回调函数为kauth_authorize_process_callback。

    
    
    static int
    
    kauth_authorize_process_callback(kauth_cred_t credential, __unused void *idata, kauth_action_t action,
        uintptr_t arg0, uintptr_t arg1, __unused uintptr_t arg2, __unused uintptr_t arg3)
    {
            switch(action) {
            case KAUTH_PROCESS_CANSIGNAL:
                    panic("KAUTH_PROCESS_CANSIGNAL not implemented");
                    if (cansignal(current_proc(), credential, (struct proc *)arg0, (int)arg1))
                            return(KAUTH_RESULT_ALLOW);
                    break;
            case KAUTH_PROCESS_CANTRACE:
                    if (cantrace(current_proc(), credential, (proc_t)arg0, (int *)arg1))
                            return(KAUTH_RESULT_ALLOW);
                    break;
            }
    
            return(KAUTH_RESULT_DEFER);
    }

回调函数非常简单，只判断进程是否有trace能力，对于是否能有发送信号的能力，xnu内核开发者估计也没想好，panic函数直接写在了cansignal函数的前面。

#### **1.2.4.3 文件状态监控**

在kauth_scope_init初始化时，并没有对KAUTH_SCOPE_FILEOP类型的scope设置默认回调函数。

    
    
    static void
    
    kauth_scope_init(void)
    {
            kauth_scope_fileop = kauth_register_scope(KAUTH_SCOPE_FILEOP, NULL, NULL);
    }

在文件状态发生变更的地方，都调用了kauth_authorize_fileop函数，它继而调用kauth_authorize_action函数，由于KAUTH_SCOPE_FILEOP类型的scope没有默认回调函数，它将继续判断是否有加载第三方内核扩展的回调函数。对于文件系统状态监控，开发人员需要自己编写一个内核扩展注册listene回调函数到scope中才行，xnu内核并没有提供默认的内核扩展。

kauth_authorize_fileop函数定义为：

int

kauth_authorize_fileop(kauth_cred_t credential, kauth_action_t action,
uintptr_t arg0, uintptr_t arg1)；

内核在文件系统的不同路径调用它，最后两个参数在不同的调用路径对应不同的意义。内核注释代码中写的很详细：

![](https://images.seebug.org/content/images/2021/01/6cf6675e-f2c7-40f0-a45b-0b30b5e52cba.png-w331s)

### **1.2.4.4 文件vnode授权与acl检查**

对于文件vnode监控的kauth scope注册是放在文件系统初始化进行的：

    
    
    bsd/vfs/vfs_subr.c
    
    void
    vnode_authorize_init(void)
    {
            vnode_scope = kauth_register_scope(KAUTH_SCOPE_VNODE, vnode_authorize_callback, NULL);
    }

它注册的callback函数为vnode_authorize_callback。vnode的权限检查包括以下几个：
![](https://images.seebug.org/content/images/2021/01/ce69ce21-81b3-48e5-81a9-49e19146adee.png-w331s)

为了加快检查速度，xnu使用了一个cache机制，在vnode的结构体加入了v_authorized_actions成员，它代表了上一次是做的哪项权限检查，通过调用vnode_cache_is_authorized执行vp->v_authorized_actions
&
action，来判断是否命中上次cache，之后在执行完权限检查后，通过调用vnode_cache_authorized_action执行vp->v_authorized_actions
|= action更新cache。

Xnu将文件系统的acl评估机制也封装到了kauth子系统里。

    
    
    bsd/sys/kauth.h
    
    struct kauth_acl {
            u_int32_t       acl_entrycount;
            u_int32_t       acl_flags;
            struct kauth_ace acl_ace[1];
    };

acl_entrycount表示的是struct kauth_ace acl_ace数组的大小。

    
    
    struct kauth_ace {
            guid_t          ace_applicable;
            u_int32_t       ace_flags;
            kauth_ace_rights_t ace_rights;          
    };

一个acl entry定义为struct
kauth_ace结构，acl评估的业界通用算法就是从前到后，依次对比每个ace项，如果权限匹配为deny，则直接返回失败，否则进行下一个ace匹配。

在函数vnode_authorize_simple里判断vnode结构的acl链表是否为空，如果不为空则调用kauth_acl_evaluate进行acl权限检查。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1472/>

