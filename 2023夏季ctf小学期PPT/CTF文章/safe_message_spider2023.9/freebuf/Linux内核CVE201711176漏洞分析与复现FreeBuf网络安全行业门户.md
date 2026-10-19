***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  一、漏洞背景  

 **Linux内核中的POSIX
消息队列实现中存在一个UAF漏洞CVE-2017-11176。攻击者可以利用该漏洞导致拒绝服务或执行任意代码。本文将从漏洞成因、补丁分析以及漏洞复现等多个角度对该漏洞进行详细分析。**

## 二、漏洞分析

Posix消息队列允许异步事件通知，当往一个空队列放置一个消息时，Posix消息队列允许产生一个信号或启动一个线程。这种异步事件通知调用mq_notify函数实现，mq_notify为指定队列建立或删除异步通知。由于mq_notify函数在进入retry流程时没有将sock指针设置为NULL，可能导致UAF漏洞。

从补丁代码可知，将sock设置为NULL即可。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158104_5c74cb5859398.png!small)

接下来看看漏洞起因，这里以4.1.0版本源码为例。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158139_5c74cb7b0a7d9.png!small)

在mq_notify函数中，
u_notification是从用户层传进来的，1193行判断u_notification是否为空，如果非空，通过copy_from_user将u_notification中
的数据拷贝到notification中，这里将数据从用户层拷贝到了内核层。如果拷贝失败，直接退出。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158160_5c74cb90b936e.png!small)

接下来，nc和sock分别置空。行1203，如果u_notification不为空，首先依次判断notification.sigev_notify必须为SIGEV_NONE或SIGEV_SIGNAL或SIGEV_THREAD。如果notification.sigev_notify为SIGEV_SIGNAL，就判断该信号是否合法。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158207_5c74cbbf78a79.png!small)

行1212，如果notification.sigev_notify为SIGEV_THREAD，进入关键代码块。行1216，通过alloc_skb创建一个notify_skb，用于接收数据。行1221，通过copy_from_user将notification.sigev_value.sival_ptr指向的数据拷贝到nc->data中。这里必须成功，不然直接退出；行1229，调用skb_put设置消息数据头部。行1231到行1248是retry循环体。行1232，调用fdget函数获取文件描述符。行1237，调用netlink_getsockbyfilp函数通过文件描述符获取netlink_sock，具体看一下netlink_getsockbyfilp函数。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158229_5c74cbd5aed0b.png!small)

调用file_inode通过filp找到对应的inode节点，然后通过SOCK_I函数处理inode节点。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158259_5c74cbf3af2fe.png!small)

这里通过宏container_of在socket_alloc结构体中找出socket成员。这里解释一下，SOCKET_I返回值是socket结构体。其实sock结构体中第一个成员sock_common也是socket类型，是一个迷你版socket。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158274_5c74cc02eabb4.png!small)

下面看一下sock_common结构体。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158297_5c74cc19f0e2b.png!small)

行1609，获取到sock后，然后判断sock->sk_family是否等于AF_NETLINK。行1613，接着调用sock_hold增加引用计数。sock_hold函数如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158321_5c74cc3115ea7.png!small)

这里atomic_inc进行sk_refcnt加1。netlink_getsockbyfilp函数返回sock，这时sock的引用计数为1。接下来，行1246，调用netlink_attachskb。这是个关键函数，该函数功能是将skb绑定到netlink
socket上，具体关键代码如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158338_5c74cc42b23ec.png!small)

行1683，调用sock_put减少引用计数一次，最后return 1，函数返回，直接goto到retry标签地方。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158363_5c74cc5b12aff.png!small)

这里行1237和行1246，这两处调用正好进行了引用计数抵消。行1247的if语句中并没有将sock置空，再看行1233，如果f.file为空，那就直接goto到out标签。out标签代码如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158380_5c74cc6c7a7cb.png!small)

行1306，判断sock是否为空，如果不为空，调用netlink_detachskb函数。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158396_5c74cc7cc25ec.png!small)

释放skb，并减少sk引用计数，进行释放。
那么就有问题了，如果我们创建A线程保持netlink_attachskb返回1，并重复retry逻辑，这个时候sock的引用计数是保持平衡的，一加一减，但是sock并不是为空。同时再创建B线程去关闭netlink
socket对应的文件描述符。由于B线程关闭了netlink
socket的文件描述符，那A线程在retry逻辑中，行1232，调用fdget时会失败，然后直接goto到out标签，进行释放，进行了二次释放，导致漏洞。这个漏洞是属于条件竞争型的二次释放漏洞，只在一个线程中，是无法触发漏洞。

这个漏洞原理比较简单，但是如何触发这个漏洞还是比较复杂。首先，如何让netlink_attachskb返回1，从而顺利进入retry逻辑。再次回看netlink_attachskb的实现。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158416_5c74cc903fe36.png!small)

行1657，通过nlk_sk函数通过sk获取netlink_sock。这里的nlk_sk如下。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158431_5c74cc9fe7adf.png!small)

通过调用宏container_of获取netlink_sock。netlink_sock结构体如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158448_5c74ccb02a3c6.png!small)

netlink_sock结构体第一个成员是sock类型，而sock结构体的第一个成员是socket。行1660，第一个if判断必须得进入。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158465_5c74ccc1eac0f.png!small)

!netlink_skb_is_mmaped(skb)肯定返回true，关键是sk->sk_rmem_alloc>sk->sk_rcvbuf||
test_bit(NETLINK_CONGESTED, &nlk->state)结果必须是true。

这里通过设置sk->sk_rmem_alloc的大小绕过check更为方便，代码如下。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158520_5c74ccf8d2c05.png!small)

假如if判断不通过，接着调用netlink_skb_set_owner_r函数，如下所示。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158541_5c74cd0d8b173.png!small)

行878，调用宏atomic_add，该宏执行原子加操作。这行代码的含义是：在sk->sk_rmem_alloc的基础上加上skb->truesize。等同于sk->sk_rmem_alloc
+=skb->truesize。既然该函数里这行代码可以直接增加sk->sk_rmem_alloc的大小，那么可不可以多次调用netlink_skb_set_owner_r函数增加sk->rmem_alloc的值？理论上是完全可以的，看看如何从用户层到达这个函数。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158564_5c74cd247e3da.png!small)

通过understand工具可以快速找到netlink_skb_set_owner_r的调用链：

    
    
    netlink_sendmsg->netlink_unicast->netlink_attachskb->netlink_skb_set_owner_r

如何顺利的通过函数调用路径？这里需要分析如何从netlink_sendmsg到达netlink_skb_set_owner_r。

netlink_sendmsg函数实现如下。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158587_5c74cd3b7b5f8.png!small)

行2285，首先判断msg->msg_flag不能为MSG_OOB，继续往下看。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158612_5c74cd54d6a4e.png!small)

行2292，判断msg->msg_namelen的长度，这里必须不为空，当然也不会为空。进入if后，判断addr->nl_family是否等于AF_NETLINK。行2299，判断dst_group或dst_portid不为空，dst_group表示多播模式，dst_portid来自于addr->nl_pid，因此保证dst_portid不为空比较容易。接下来：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158627_5c74cd63e7165.png!small)

行2320，判断了msg->msg_iter.iov->iov_base不能为空。并且len不可以大于sk->sk_sndbuf-32。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158658_5c74cd82e0e14.png!small)

其实整个函数中，用户层可控的只有这么多。直接看netlink_unicast的调用。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158680_5c74cd981ec54.png!small)

netlink_unicast函数实现如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158702_5c74cdae64c80.png!small)

整个函数中，用户能控制的不多。行1783，设置了timeo，这里要保证nonblock为msg->msg_flags&MSG_DONTWAIT，这样线程才不会被block。行1790，判断sk是否为内核版的sk，在用户层创建socket时应使用NETLINK_USERSOCK。行1793，判断是否有sk_filter，这里保证不进入该if语句，不要设置过滤器。行1800，直接调用netlink_attachskb，成功到达netlink_skb_set_owner_r函数。这算是通过调用netlink_sendmsg来增加sk->sk_rmem_alloc的过程。其实我们不光可以增加sk->sk_rmem_alloc，还可以减小sk->sk_rcvbuf。

那么如何减小sk->sk_rcvbuf？在setsockopt函数中，找到sock_setsockopt函数中对sk->sk_rcvbuf的操作。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158727_5c74cdc747d44.png!small)

行773，sk->sk_rcvbuf取val*2和SOCK_MIN_RCVBUF之间的最大值。行755，val取val和sysctl_rmem_max之间的最小值。行749，这个case为SO_RCVBUF。继续往上看。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158747_5c74cddbe659f.png!small)

行693，要保证optlen不小于sizeof(int)。行696，将optval赋值到val中，这里optval是用户可控的。行703，switch分发optname，所以要保证optname为SO_RCVBUF。这样就可以保证顺利到达修改sk->rcvbuf的代码处。

到这里，我们通过两种方式进行绕过netlink_attachskb函数中的第一个check。

> 1) 通过netlink_sendmsg增加sk->sk_rmem_alloc的值。
>
> 2) 通过sock_setsockopt尽可能地减小sk->rcvbuf的值。

进入if语句后，看如下代码：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158770_5c74cdf24d061.png!small)

这段代码会让当前线程进入等待状态，直接block。如果不想进入等待状态，只有设置sock_flag为SOCK_DEAD。但是如果把sock_flag设置成SOCK_DEAD，那后面也没有必要进行，因此这里是必然要进入等待状态的。一种巧妙的方法是直接调用wake_up_interruptible强行唤醒线程。那如何调用wake_up_interruptible呢？函数调用链非常简短：netlink_setsockopt->wake_up_interruptible。

在Netlink_setsockopt函数中：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158792_5c74ce08207d9.png!small)

行2182，调用wake_up_interruptible唤醒线程。行2178，case为NETLINK_NO_ENOBUFS。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158806_5c74ce16c92cd.png!small)

行2131，判断level必须为SOL_NETLINK，行2134，判断optname不能为NETLINK_RX_RING和NETLINK_TX_RING，同时保证optlen大于等于sizeof(int)。行2139，switch分发optname，这里要保证optname为NETLINK_NO_ENOBUFS。到这里，基本上就可以保证netlink_attachskb返回1。

保证进入retry循环后，这个时候sock已经不为空。接下来要使retry循环中出错，直接跳转到out，代码如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158824_5c74ce287e831.png!small)

行1232，通过fdget获取notification.sigev_signo的fd。Notification.sigev_signo是用户态传进来的，因此完全可以在用户层直接close这个socket。在用户层close这个socket后，行1233，进入if逻辑，然后跳到out标签。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158842_5c74ce3aa19e7.png!small)

这个时候sock是非空的，if判断为真，进入netlink_destachskb，接着就是free崩溃。

## 三、漏洞复现

对于UAF类型的漏洞，通用方法就是使用堆喷射占位。本次漏洞中被多次释放的对象是netlink_sock对象。netlink_sock对象大小为0x3f0字节，即是1008byte。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158866_5c74ce524766e.png!small)

根据内核对象内存分配规则， netlink_sock对象应该从kmalloc-1024这个缓存中进行分配。

slab分配器在分配对象时，遵守后进先出的规则。

下面是slab分配器释放对象的过程。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158881_5c74ce6128f13.png!small)

要释放的对象objp放在了ac->entry[]的末端。下面是slab分配器分配对象的过程：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158903_5c74ce779ed25.png!small)

分配对象直接从ac->entry[]末端弹出一个对象。

所以一个刚刚被释放的对象是排在链表末段，如果此时恰好在同一缓存中进行对象分配，那刚刚释放的对象就会被重新分配出去，这就出现两个指针指向同一块内存地址。要想保证申请的内存正好落在漏洞对象的内存位置中，需要把握住几点：

> 堆喷对象使用的内核缓存应该和漏洞对象内存在同一个缓存中。即大小必须落在同一个kmalloc-X中；
>
> ac本身是array_chche结构体，该结构体是本地高速缓存，每个CPU对应一个，所以还要保证堆喷申请的对象和漏洞对象在同一个CPU本地高速缓存中；
>
>
> 如果堆喷申请的对象只是短暂驻留，当该函数返回时将申请的对象进行了释放，导致无法正确占位。所以要能保证申请的对象不被释放，至少保证在使用漏洞对象时不被释放，这里要采用驻留式内存占位，可以采取让某些系统调用过程阻塞；
>
> slab缓存碎片化问题，这里要占位的对象大小为1008，对象尺寸比较大，占据四分之一页，比较整齐，应该没有碎片化问题；

那么如何判断堆喷是否成功呢？

通用情况下，在进行堆喷时候，构造堆喷对象时，有必要在对应漏洞对象的一些特殊成员域的内存偏移处设置magic
value，然后可以采用系统调用去获取漏洞对象中相关数据进行判断。netlink_sock结构体几个关键的成员如下。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158925_5c74ce8d731d8.png!small)

采用getsockname系统调用获取数据，getsockname会调用netlink_getname。具体看一下netlink_getname函数：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158942_5c74ce9eb6d34.png!small)

代码1576行，将netlink_sock对象中的portid复制给nladdr->nl_pid。代码1577行，如果nlk->group为0，将nladdr->nl_groups赋值为NULL，这里避免解引用nlk->groups指针，直接可以在构造堆喷对象时将groups域填零。而nladdr是从addr转换过来的，addr就是从用户层传入的缓冲区。

堆喷成功如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158965_5c74ceb5ae226.png!small)

通常情况是覆盖结构体中的函数指针或者包含函数指针的结构体成员，这视情况而定。这里选择覆盖wait等待队列。netlink_sock结构体如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158981_5c74cec581a3f.png!small)

wait_queue_haed_t结构体如下：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551158996_5c74ced429dd0.png!small)

task_list成员是一个双向循环链表头，task_list中链接的每一个成员都是需要处理的等待例程元素。那该如何使用这个成员？看如下代码。

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159011_5c74cee3c70f1.png!small)

这是netlink_setsockopt函数中的代码片段，前面恢复线程复活分析过，这里将会调用netlink_sock对象中的等待例程，直接使用参数nlk->wait。继续深入分析：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159026_5c74cef22b6fe.png!small)

调用__wake_up_common函数：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159042_5c74cf02784dd.png!small)

代码70行，宏list_for_each_entry_safe遍历q->task_list中的成员，返回到curr。代码68行，curr为wait_queue_t指针，说明q->task_list链表中存的是wait_queue_t类型的元素，wait_queue_t结构体如下：

![image.pngLinux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159057_5c74cf11d6908.png!small)

wait_queue_t结构体中有一个函数指针func。再看__wake_up_common函数中，代码73行，直接执行curr>func函数，可以通过构造__wait_queue的func参数控制RIP。再回过头看list_for_each_entry_safe宏：

![image.pngLinux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159075_5c74cf232af2f.png!small)

pos是__wait_queue元素，代码62行，对pos->member.next进行了解引用，这里的pos->member就是__wait_queue中的task_list。__wait_queue中的task_list也是一个链表头，需要指向一个list_head，所以还必须要构造一个假的list_head以便于该宏进行解引用。测试如下：

![image.pngLinux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159095_5c74cf373775b.png!small)

接下来就是通过ROP链绕过SMEP执行提权代码。成功提权后如下所示：

![Linux内核CVE-2017-11176漏洞分析与复现](https://image.3001.net/images/20190226/1551159117_5c74cf4d58f80.png!small)

## 四、参考链接

[1] <https://blog.lexfo.fr/cve-2017-11176-linux-kernel-exploitation-part1.html>

[2] <https://blog.lexfo.fr/cve-2017-11176-linux-kernel-exploitation-part2.html>

[3] <https://blog.lexfo.fr/cve-2017-11176-linux-kernel-exploitation-part3.html>

[4] <https://blog.lexfo.fr/cve-2017-11176-linux-kernel-exploitation-part4.html>

***本文作者：ADLab，转载请注明来自FreeBuf.COM**

