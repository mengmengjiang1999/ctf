**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/Qs_-CTZyojRe_x8E0KiXMg>**

# 一、 前言

数月前，国外安全组织ZDI研究人员披露了一个Linux内核本地权限提升漏洞，该漏洞出现在流量控制子系统包分类器的cls_route过滤器中，当旧过滤器句柄为0时，在释放之前内核不会从哈希表中将其删除，其漏洞编号为CVE-2022-2588，而且还提出了一种新的漏洞利用方法，命名为DirtyCred，该方法可绕过广泛采用的内核保护和漏洞利用缓解措施，从而实现权限提升。

# 二、 Rtnetlink简述与实现简析

## （一）Rtnetlink简述

Rtnetlink是所有内核网络子系统使用的网络连接总线，包括网络接口、路由、fdb和邻居。一些内核网络子系统也在通用netlink总线上提供服务。Linux内核网络子系统使用消息类型和系列向Rtnetlink内核注册处理程序。Rtnetlink允许读取和更改内核的路由表。它在内核中用于在各种子系统之间进行通信，也用于与用户空间程序进行通信。网络路由、IP地址、链接参数、邻居设置、排队规则、流量类别和数据包分类器都可以通过NETLINK_ROUTE套接字进行控制。Rtnetlink由以下消息类型组成（除了标准的netlink消息）：

  * RTM_NEWLINK、RTM_DELLINK、RTM_GETLINK创建、删除或获取有关特定网络接口的信息。

  * RTM_NEWADDR、RTM_DELADDR、RTM_GETADDR添加、删除或接收有关与接口关联的IP地址的信息。

  * RTM_NEWROUTE、RTM_DELROUTE、RTM_GETROUTE创建、删除或接收有关网络路由的信息。

  * RTM_NEWNEIGH、RTM_DELNEIGH、RTM_GETNEIGH添加、删除或接收有关邻居表条目的信息（例如，ARP条目）。

  * RTM_NEWRULE、RTM_DELRULE、RTM_GETRULE添加、删除或检索路由规则。

  * RTM_NEWQDISC、RTM_DELQDISC、RTM_GETQDISC添加、删除或获取排队规则。

  * RTM_NEWTCLASS、RTM_DELTCLASS、RTM_GETTCLASS添加、删除或获取流量类别。

  * RTM_NEWTFILTER, RTM_DELTFILTER, RTM_GETTFILTER添加、删除或接收有关流量过滤器的信息。

## （二）实现简析

当内核启动加载，在初始化netlink协议实现时，会调用rtnetlink_init()函数初始化路由netlink socket接口，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/6cc3499a-c4b1-43a4-93bf-bbb91177177c.jpg-w331s)

根据代码可知，通过rtnl_register()函数将不同的消息类型和对应操作进行绑定，该函数签名为void rtnl_register(int
protocol, int msgtype,rtnl_doit_func doit, rtnl_dumpit_func dumpit,unsigned
int
flags)，有的消息类型只有动作函数doit，有的消息类型只有dump函数dompit，有的消息类型两者皆有。有的消息类型例如RTM_NEWTFILTER，添加一个流量过滤器，则是在tc_filter_init()函数中初始化，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/e9fce12d-3e40-49aa-92fb-ffb0607c3a03.jpg-w331s)

当用户层通过NETLINK_ROUTE套接字发送RTM_NEWTFILTER消息用于创建一个流量过滤器时，内核将调用rtnetlink_rcv_msg()函数来处理rtnetlink消息，该函数关键实现如下：

![](https://images.seebug.org/content/images/2022/11/38418655-2ab4-4d35-8f19-7f2dc6f41d6a.jpg-w331s)

从消息中获取family和type，然后调用rtnl_get_link()函数根据family和type获取link，行5246，调用link->doit回调函数，这里的doit回调函数即为tc_new_tfilter()函数。该函数会进一步解析rtnetlink消息数据包，判断并创建哪种类型的过滤器，具体实现如下：

![](https://images.seebug.org/content/images/2022/11/03b69df9-44db-4a62-8627-00d9dfb14934.jpg-w331s)

获取指定的过滤器名字，然后会获取指定协议的过滤器tp。如下代码所示：

![](https://images.seebug.org/content/images/2022/11/69cdf66f-609d-4c5c-903c-05d5751a666e.jpg-w331s)

如果没有，便根据name创建一个新的tp。如下代码所示：

![](https://images.seebug.org/content/images/2022/11/5daee4c3-2f59-4051-8790-ed012939d28c.jpg-w331s)

判断tca[TCA_KIND]不为空和nlmsg_flags为NLM_F_CREATE，然后调用tcf_proto_create()函数创建，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/1bf0f109-c288-4498-a75e-435fa7193f4c.jpg-w331s)

行258，分配一个tp，行262，调用tcf_proto_lookup_ops()函数根据kind获取对应的ops，这里以route为例，将获取到cls_route4_ops，如下代码所示：

![](https://images.seebug.org/content/images/2022/11/1039a274-a3b2-46eb-b3c0-3241c133850e.jpg-w331s)

然后初始化tp，行274，调用route4_init()函数初始化一个route4_head，用于存放过滤器对应的哈希值，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/df944f41-e456-4b40-8c4c-32f4c05c6835.jpg-w331s)

然后tcf_proto创建完成后，将其插入chain中。如下代码所示：

![](https://images.seebug.org/content/images/2022/11/f9b608a0-dec8-4fb0-982d-9d6336b5a743.jpg-w331s)

接下来调用对应的get函数，根据tcm_handle获取过滤器。

![](https://images.seebug.org/content/images/2022/11/5f26fdaa-80c4-4120-8d87-edba305a7f42.jpg-w331s)

这里将调用route4_get()函数获取，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/6b86346e-26ae-4423-ab14-6138c8345342.jpg-w331s)

根据handle从route4_head链表中获取对应的route4_filter。如果为空，便调用change函数进行创建。如下代码所示：

![](https://images.seebug.org/content/images/2022/11/41d99d24-b0be-46cd-83e0-97312d55152a.jpg-w331s)

这里将调用ruote4_change()函数进行创建，该函数具体分析见下文。创建成功后，添加一个新的route4过滤器的整个流程便完成了。

# 三、 漏洞原理

漏洞代码出现在route4_change()函数中，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/45a98db2-95eb-4f41-8dab-2ded266de03e.jpg-w331s)

行483，首先进一步解析消息数据包，行488，拿出传入的route4_filter，然后判断是否已创建，如果创建过，再判断handle是否一致。由于第一次创建，这里fold为空。接下来进行创建并初始化，如下代码所示：

![](https://images.seebug.org/content/images/2022/11/5bf038c4-c4a6-40c0-bc99-200fd2dcd3f5.jpg-w331s)

行493，调用kzalloc()函数分配route4_filter，该结构体大小为144字节。行497，调用tcf_exts_init()函数进行初始化，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/6855894e-8164-4459-bc29-6e8e3dd9c634.jpg-w331s)

如果内核开启了CONFIG_NET_CLS_ACT，便调用kcalloc()函数分配exts->actions，分配大小为256字节。初始化完成返回到route4_change()函数中，行501，如果fold不为空，便将fold的数据域赋值给f。行512，然后调用route4_set_parms()函数设置其他参数。行517到行527，将新创建的route4_filter对应的哈希值放到route4_head中。如下代码所示：

![](https://images.seebug.org/content/images/2022/11/9a79d624-d674-47df-a3ec-d907470884ae.jpg-w331s)

行529到行543，该段代码是将旧过滤器的哈希值从route4_head中移除。如下代码所示：

![](https://images.seebug.org/content/images/2022/11/45383df7-a743-428b-845d-b04191424fbe.jpg-w331s)

由于是第一次创建，fold为空，因此不进入。但是行529代码是有问题的，这里不仅判断fold是否为空，同时还判断fold->handle是否为空。那如果第一次创建一个handle为0的过滤器，第二次创建新过滤器时，fold不为空，但是fold->handle为0，因此并不会将handle为0的旧过滤器的哈希值从route4_head中移除，保留了对其的索引。接下来开始释放旧过滤器内存，如下代码所示：

![](https://images.seebug.org/content/images/2022/11/877112a9-4ebc-4ef6-b7b7-9bcb1ee841d2.jpg-w331s)

第一次创建过滤器时，fold为空，不进入。当第二次创建新过滤器时，fold不为空，行550，调用tcf_queue_work()函数对handle为0的旧过滤器进行释放操作，回调函数为route4_delete_filter_work()函数，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/a87495a7-9329-4d0c-8c3f-50b8fdda29b3.jpg-w331s)

行266，最后调用__route4_delete_filter()函数分别释放f->exts和f。当内核调用route4_delete()函数进行释放所有过滤器时，行344，会调用route4_delete_filter_work()函数进行释放，该函数实现如下：

![](https://images.seebug.org/content/images/2022/11/3585e70d-c0c8-4a56-b076-d8138f0f4875.jpg-w331s)

由于handle为0的旧过滤器对应的哈希值依然在route4_head中，因此会对两个对象进行二次释放，分别是route4_filer及对应的exts。该漏洞修复补丁如下代码所示：

![](https://images.seebug.org/content/images/2022/11/f3e415ab-10d2-4bd5-a5c7-7b7d72e13197.jpg-w331s)

将判断条件改成fold是否为空，fold不为空便将其从哈希表中删除。

# 四、 利用研究

## （一）DirtyCred

研究人员提出了一种新的漏洞利用方法，命名为DirtyCred，该利用方法将非特权cred与特权cred进行交换以提升权限，且不需要覆盖内核堆栈上的任何关键数据字段，而是滥用堆内存重写机制来获得特权。该利用技术无需泄露内核地址绕过KASLR，且通用性较强，可跨不同的内核和架构，能绕过广泛采用的内核保护和漏洞利用缓解措施。DirtyCred分为三个步骤，过程如下图所示：

![](https://images.seebug.org/content/images/2022/11/a5318a51-7ed2-4acd-a22f-37e6be25ee06.jpg-w331s)

首先，DirtyCred打开一个可写文件“/tmp/x”，它将在内核中分配一个可写file对象。通过触发漏洞，源指针会引用相应缓存中的file对象。然后，DirtyCred尝试将内容写入打开的文件“/tmp/x”中。在实际写入内容之前，内核会检查当前文件是否有写权限，该位置是否可写等。通过检查后，DirtyCred会继续这个实际的文件写入操作，进入第二步。在此步骤中，DirtyCred触发fs_context对象的释放点以解除分配file对象，这就使file对象成为一个被释放的内存点。第三步，DirtyCred打开了一个只读文件“/etc/passwd”，这触发了内核为“/etc/passwd”分配file对象。如上图所示，新分配的file对象接管了被释放的位置。完成此设置后，DirtyCred将释放其暂停的写入操作，而内核将执行实际的内容写入。由于file对象已经被调换，搁置的内容将被重定向到只读文件“/etc/passwd”中。假设写入“/etc/passwd”的内容是“hacker:x:0:0:root:/:/bin/sh”，轻易地注入一个特权账户，从而实现权限提升。

## （二）利用分析

1、file slab碎片整理

首先创建10000个“/etc/passwd”的file对象，进行file slab碎片整理，为堆喷做准备。

![](https://images.seebug.org/content/images/2022/11/8a656028-4d85-4661-96ed-8b42263d5713.jpg-w331s)

2、缓存跨越（cross-cache）

当为特定类型的对象创建专用的内存缓存时，该缓存中将只存在该类型的对象，从而防止不同类型的对象相邻。但是，不同slab cache的slab
page可以相邻。当slab A与slab B相邻时，slab A末尾的对象与slab
B开头的另一个对象相邻。因此，攻击者有可能放置带有任何类型受害者对象的slab页在易受攻击对象的slab page之后，溢出受害者对象来执行攻击。

![](https://images.seebug.org/content/images/2022/11/830ebe2c-7d69-4aaa-ba35-a07584d06afb.jpg-w331s)

当一个slab page被释放给伙伴系统时，它会在稍后的某个时候被重用，因为内存页面应该被内核回收。cross-cache攻击的技术是释放slab
page中的所有内存槽，强制释放slab page。然后再喷射另一种类型的对象分配新的slab page，回收释放的slab
page。如果攻击成功，被释放对象的内存将被另一种类型的对象占用。

![](https://images.seebug.org/content/images/2022/11/8f460b89-f473-45ce-821e-4bbe31a16336.jpg-w331s)

由于file对象在专属缓存中分配，而漏洞中route4_filter和exts在通用缓存中分配，正常情况下，两个缓存是隔离的，无法进行常规的对象占坑。作者采用了缓存跨越攻击解决了这个问题。前文讲到route4_filter对象大小为144，在kmalloc-192中分配，exts对象大小为256，在kmalloc-256中分配。file对象大小为256（默认配置情况下），在专属内存中分配。先通过创建basic过滤器在kmalloc-256
slab中进行内存布局。

![](https://images.seebug.org/content/images/2022/11/2cb9e862-c557-475a-90b8-1f7204c7e95f.jpg-w331s)

然后创建route4过滤器，将会创建一个route4_filter漏洞对象和exts对象。最后再进行一部分basic过滤器创建，完成内存布局。关键对象内存分布如下图所示：

![](https://images.seebug.org/content/images/2022/11/304ca56d-e962-49d1-b768-74e15b992c7c.jpg-w331s)

然后第一次触发漏洞，释放route4_filter对象和exts对象。然后再全部释放basic->exts对象，让伙伴系统回收kmalloc-256
slab page。

![](https://images.seebug.org/content/images/2022/11/7b29154d-f648-4580-9344-272f3b94a42d.jpg-w331s)

由于内核默认开启slab double free缓解机制，所以这里要乱序释放多个basic->exts。

3、堆喷占坑

大量打开一个普通文件data2，进行file对象分配占坑route4->exts。缓存跨越攻击成功后，然后再次触发漏洞，第二次释放route4_filter，跟着释放route4->exts，将会把file对象非法释放掉。

![](https://images.seebug.org/content/images/2022/11/678fdc00-047e-4371-a205-db1680d4f39a.jpg-w331s)

关键对象内存布局如下图所示：

![](https://images.seebug.org/content/images/2022/11/901cf8fd-7f58-4aa1-9d35-284cc257db34.jpg-w331s)

4、寻找file对象空洞

二次释放后，出现了一个file对象空洞，需要找到它。所以此时再次大量打开另一个普通文件uaf，进行file对象堆喷，将会占据这个file对象空洞。然后通过kcmp()系统调用检查
pid1 和 pid2 标识的两个进程是否共享文件描述符定位fds[j]。

![](https://images.seebug.org/content/images/2022/11/6d1695eb-02aa-407e-8b48-cfb0d23a19d0.jpg-w331s)

5、延长时间窗口和写恶意数据

找到目标file对象的文件描述符fds[j]后，启动两个线程，slow_write线程向uaf文件中写2G数据，用于延长时间窗口。

![](https://images.seebug.org/content/images/2022/11/27464364-fdae-4f11-8799-d040f8877a62.jpg-w331s)

然后write_cmd线程通过fds[j]文件描述符写恶意数据。

![](https://images.seebug.org/content/images/2022/11/c3abdc82-4b55-4178-b43d-5ab124eddc41.jpg-w331s)

6、再次释放并堆喷

最后进行close操作，释放file对象，随即大量打开“/etc/passwd”文件进行file对象堆喷。堆喷成功后，顺利向“/etc/passwsd”写数据，注入一个特权账户完成权限提升。

![](https://images.seebug.org/content/images/2022/11/845660f7-7d43-49cb-a39b-394237c146dd.jpg-w331s)

# 五、 漏洞复现

在内核版本5.4.124中，开启CONFIG_NET_CLS_ACT和CONFIG_NET_SCH_SFQ，成功复现漏洞。打印调试关键数据，如下图所示：

![](https://images.seebug.org/content/images/2022/11/a1f2095c-fa4e-44b1-ac94-476c15df11a9.jpg-w331s)

# 六、 参考

1、 <https://grsecurity.net/how_autoslab_changes_the_memory_unsafety_game>

2、 <https://www.openwall.com/lists/oss-security/2022/08/09/6>

3、<https://www.man7.org/linux/man-pages/man7/rtnetlink.7.html>

4、 <https://legacy.netdevconf.info/0.1/papers/Rtnetlink-dump-filtering-in-the-kernel.pdf>

5、 <https://github.com/Markakd/DirtyCred>

6、 <https://github.com/Markakd/CVE-2022-2588>

7、 <https://zplin.me/papers/DirtyCred.pdf>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2019/>

