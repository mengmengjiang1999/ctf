# 【漏洞分析】CVE-2016-5195 Dirtycow: Linux内核提权漏洞分析

阅读量 **394875**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-10-24 15:57:02

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**作者：**[ **A7um**](http://bobao.360.cn/member/contribute?uid=183557479)

**稿费：700RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿**

**  
**

**漏洞概要**

**漏洞编号：** CVE-2016-5195

**漏洞类型：** 内核竞态条件漏洞

**漏洞危害：** 本地提权

**影响范围：** Linux kernel>2.6.22 (released in 2007)

这个漏洞是在10月18号被Phil Oester提交，被Linux的创始人Linus亲自修复。10月20号，漏洞的发现者Phil
Oester将漏洞的部分细节提交到github上。当天朋友圈就被这个漏洞刷屏了，毕竟是几乎是通杀全版本linux的本地提权的神洞，这种漏洞还是很少见的。

[官方github放出的POC](https://github.com/dirtycow/dirtycow.github.io/blob/master/dirtyc0w.c)已经可以实现向任意可读文件写任意内容，所以有了这POC基本上也就可以拿到rootshell了。比如我们可以写/etc/passwd，修改相应用户的UID来达到提权的目的，我们还可以通过写一些带S位的root
owned的binary程序的代码，使其执行execve(binsh)等等，方法还是有很多的。

本文默认读者了解以下技术：

[写时拷贝(Copy on
Write,COW)](http://www.cnblogs.com/biyeymyhjob/archive/2012/07/20/2601655.html)

[竞态条件](http://baike.baidu.com/link?url=KYVGZZs3z1EstguoNCFaEmaPe-_bfbiQ47_uoP8H2HvLXxYIDtoUttgWymYFqfGOLcuY943QERhwmm-TtEDulwx7bY60s93Kho6Y8T31-enDKKVSAR4OQEkuDE2cdyUY)

页式内存管理

[缺页中断处理](http://blog.csdn.net/chenyu105/article/details/7061845)

**基础知识**

在正式的分析漏洞之前，我们首先对官方github的POC中涉及的几个系统调用与系统文件进行简单的讲解

    
    
    mmap(void* start, size_t length, int prot,int flags,int fd, off_t offset)

这是一个相对比较常用的函数，这个函数的一个很重要的用处就是将磁盘上的文件映射到虚拟内存中，对于这个函数唯一要说的就是当flags的MAP_PRIVATE被置为1时，对mmap得到内存映射进行的写操作会使内核触发COW操作，写的是COW后的内存，不会同步到磁盘的文件中。

    
    
    madvice(caddr_t addr, size_t len, int advice)

这个函数的主要用处是告诉内核内存addr～addr+len在接下来的使用状况，以便内核进行一些进一步的内存管理操作。当advice为MADV_DONTNEED时，此系统调用相当于通知内核addr～addr+len的内存在接下来不再使用，内核将释放掉这一块内存以节省空间，相应的页表项也会被置空。

    
    
    ssize_t write(int fd, const void* buf, size_t count)

这也是一个很常见的函数,主要作用是向fd描述符所指向的文件写入最多count长度的buf中的内容。

    
    
    /proc/self/mem

这个文件是一个指向当前进程的虚拟内存文件的文件，当前进程可以通过对这个文件进行读写以直接读写虚拟内存空间，并无视内存映射时的权限设置。也就是说我们可以利用写/proc/self/mem来改写不具有写权限的虚拟内存。可以这么做的原因是/proc/self/mem是一个文件，只要进程对该文件具有写权限，那就可以随便写这个文件了，只不过对这个文件进行读写的时候需要一遍访问内存地址所需要寻页的流程。因为这个文件指向的是虚拟内存。

  

**触发原理**

为了便于理解，我们首先概述一下这个漏洞的触发原理

当调用write系统调用向/proc/self/mem文件中写入数据时，进入内核态后内核会调用get_user_pages函数获取要写入内存地址。get_user_pages会调用follow_page_mask来获取这块内存的页表项，并同时要求页表项所指向的内存映射具有可写的权限。

第一次获取内存的页表项会因为缺页而失败。get_user_page调用faultin_page进行缺页处理后第二次调用follow_page_mask获取这块内存的页表项，如果需要获取的页表项指向的是一个只读的映射，那第二次获取也会失败。这时候get_user_pages函数会第三次调用follow_page_mask来获取该内存的页表项，并且不再要求页表项所指向的内存映射具有可写的权限，这时是可以成功获取的，获取成功后内核会对这个只读的内存进行强制的写入操作。

这个实现是没有问题的，因为本来写入/proc/self/mem就是一个无视映射权限的强行写入，就算是文件映射到虚拟内存中，也不会出现越权写：

如果写入的虚拟内存是一个VM_PRIVATE的映射，那在缺页的时候内核就会执行COW操作产生一个副本来进行写入，写入的内容是不会同步到文件中的

如果写入的虚拟内存是一个VM_SHARE的映射，那mmap能够映射成功的充要条件就是进程拥有对该文件的写权限，这样写入的内容同步到文件中也不算越权了。

但是，在上述流程中，如果第二次获取页表项失败之后，另一个线程调用madvice(addr,addrlen,
MADV_DONTNEED),其中addr~addr+addrlen是一个只读文件的VM_PRIVATE的只读内存映射，那该映射的页表项会被置空。这时如果get_user_pages函数第三次调用follow_page_mask来获取该内存的页表项。由于这次调用不再要求该内存映射具有写权限，所以在缺页处理的时候内核也不再会执行COW操作产生一个副本以供写入。所以缺页处理完成后后第四次调用follow_page_mask获取这块内存的页表项的时候，不仅可以成功获取，而且获取之后强制的写入的内容也会同步到映射的只读文件中。从而导致了只读文件的越权写。

  

**控制流的分析**

接下来我们看一下该漏洞的内核代码，并根据代码对内核控制流进行分析，以对漏洞进行进一步的详解

首先贴一下相关函数的精简版，虽然是精简版，但是看起来还是挺费劲的，所以我建议大家可以先大致扫一下这一部分的内容，然后继续看后面的控制流分析。然后根据控制流分析回过头再来查阅这些函数，相关函数的完整版见Reference。

    
    
    get_user_pages{//这是一个Wrap
        ...
        return __get_user_pages() //获取用户内存的核心函数
        ...
    }
    __get_user_pages(vma,...,int flag,...){
        ...
        retry:
            ...
            page = follow_page_mask(...,flag,...); //获取页表项
           if (!page) {
                int ret;
                ret = faultin_page(vma,...); //获取失败时会调用这个函数
                switch (ret) {
                   case 0://如果返回为0，就重试，这是一个循环
                   goto retry;
                ...
                
            }
    }
    follow_page_mask(...,flag,...){
        //这个函数会走 页一集目录->二级目录->页表项 的传统页式内存的管理流程
        ...
        return follow_page_pte(...,flag,...); //走到了流程的第三步：寻找页表项
        ...
    }
    follow_page_pte(...,flag,...){
        ...
        //如果获取页表项时要求页表项所指向的内存映射具有写权限，但是页表项所指向的内存并没有写权限。则会返回空
        if ((flags & FOLL_WRITE) && !pte_write(pte)) { 
           pte_unmap_unlock(ptep, ptl);
           return NULL;
        }
        
        //获取页表项的请求不要求内存映射具有写权限的话会返回页表项
        return pages;
        ...
    }
    faultin_page(vma,){
        ...
        //处理page fault
        ret = handle_mm_fault();
        //这个if对应了上一个函数的注释，如果是因为映射没有写权限导致的获取页表项失败，会去掉flags中的FOLL_WRITE标记，从而使的获取页表项不再要求内存映射具有写的权限。
        if ((ret & VM_FAULT_WRITE) && !(vma->vm_flags & VM_WRITE))
           *flags &= ~FOLL_WRITE;
        ...
        return 0；
    }
    handle_mm_fault(){
        __handle_mm_fault()
    }
    __handle_mm_fault(){
        handle_pte_fault()
    }
    handle_pte_fault(){
        //页表为空，说明缺页。调用do_fault调页
        if (!fe->pte) {
              ... 
             return do_fault(fe);
       }
       //页表不为空，但是要写入的页没有写权限，这时可能需要COW
       if (fe->flags & FAULT_FLAG_WRITE) {
            if (!pte_write(entry))
                return do_wp_page(fe, entry);
            ...
        }
    }
    do_fault(fe){
        //如果不要求目标内存具有写权限时导致缺页，内核不会执行COW操作产生副本
        if (!(fe->flags & FAULT_FLAG_WRITE))
            return do_read_fault(fe, pgoff);
        //如果要求目标内存具有写权限时导致缺页，目标内存映射是一个VM_PRIVATE的映射，内核会执行COW操作产生副本
        if (!(vma->vm_flags & VM_SHARED))
            return do_cow_fault(fe, pgoff);
    }
    do_cow_fault(fe,pgoff){
        //执行COW， 并更新页表为COW后的页表。
        new_page = alloc_page_vma(GFP_HIGHUSER_MOVABLE, vma, fe->address);
        ...
        // __do_fault会将内存
        ret = __do_fault(fe, pgoff, new_page, &fault_page, &fault_entry);
        ... 
            copy_user_highpage(new_page, fault_page, fe->address, vma);
        ret |= alloc_set_pte(fe, memcg, new_page);
        ...
        return ret
    }
    do_read_fault(fe,pgoff){
        ...
        //不执行COW，直接映射文件。
        __do_fault(fe, pgoff, NULL, &fault_page, NULL);
        ...
        ret |= alloc_set_pte(fe, NULL, fault_page);
        ...
        ret
    }
    alloc_set_pte(fe,...){
        bool write = fe->flags & FAULT_FLAG_WRITE;
        //如果执行了COW，设置页表时会将页面标记为脏，但是不会标记为可写。
        if (write)
            entry = maybe_mkwrite(pte_mkdirty(entry), vma);
    }
    do_wp_page(fe,entry){
         ....
         //内核通过检查，发现COW操作已经在缺页处理时完成了，所以不再进行COW，而是直接利用之前COW得到的页表项
         return wp_page_reuse(fe, orig_pte, old_page, 0, 0);
    }
    wp_page_reuse(){
         将页面标记为脏，但是不会标记为可写。
         entry = maybe_mkwrite(pte_mkdirty(entry), vma);
    }
    maybe_mkwrite(){
        //这就是maybe_mkwrite不会标记页为可写的原因，因为这个页为只读页。所以不满足if的条件
        if (likely(vma->vm_flags & VM_WRITE))
            pte = pte_mkwrite(pte);
        return pte;
    }

假设我们通过Mappedaddr=mmap(NULL,filesize,PROT_READ,MAP_PRIVATE,fd,0);获取了一个只读文件的只读内存映射，然后创建两个线程，Thread1通过不断写/proc/self/mem来写Mappedaddr指向的位置，Thread2不断调用madvice(Mappedaddr,len,MADV_DONTNEED)来将Mappedaddr的页表项置空。

基于以上假设，我们来分析内核的控制流。这个控制流分析的代码部分是老外写的([原文链接](https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails))，秉持着开源的精神和思想，我引用了过来并加了一下注释。

write系统调用在内核中会执行get_user_pages以获取需要写入的内存页，get_user_pages函数会调用follow_page_mask函数寻找内存页对应的页表项，由于这是mmap后第一次对Mappedmem进行操作，所以Mappedmem所对应的页表为空，pagefault，get_user_pages调用faultin_page函数进行处理，faultin_page函数会调用handle_mm_fault进行缺页处理。缺页处理时，如果页表为空，内核会调用do_fault函数调页，这个函数会检查是否是因为内存写造成的缺页以及该内存是否是以private方式map的内存，如果是，则会进行COW操作，更新页表为COW后的页表。并将返回值的FAULTFLAGWRITE位置为1（正确分词：某某位
置为1，下同）

    
    
    faultin_page
      handle_mm_fault
        __handle_mm_fault
          handle_pte_fault
            do_fault <- pte is not present
          do_cow_fault <- FAULT_FLAG_WRITE
            alloc_set_pte
              maybe_mkwrite(pte_mkdirty(entry), vma) <- mark the page dirty
                                    but keep it RO

get_user_pages会第二次调用follow_page_mask寻找页表项，follow_page_mask会调用follow_page_pte函数，这个函数会通过flag参数的FOLL_WRITE位是否为1判断要是否需要该页具有写权限，以及通过页表项的VM_WRITE位是否为1来判断该页是否可写。由于Mappedmem是以PROT_READ和MAP_PRIVATE的的形式进行映射的。所以VM_WRITE为0，又因为我们要求页表项要具有写权限，所以FOLL_WRITE为1，从而导致这次寻页会再次触发一个pagefault，faultin_page会再次调用handle_mm_fault进行处理。

    
    
    # Returns with 0 and retry
    follow_page_mask
      follow_page_pte
        (flags & FOLL_WRITE) && !pte_write(pte) <- retry fault

由于这次pagefault时页表不为空，所以不会执行do_fault函数调页，转而会去检查pagefault是否是由于要写不可写的地址导致的，如果是则会调用do_wp_page进行COW操作，不过值得注意的是，do_wp_page会进行一系列的检查来判断是否需要真的进行COW操作，如果没必要，则会直接REUSE原来的页来作为COW后的页。因为在调页过程中已经进行过COW过了，所以直接reuse了调页COW后的内存页。之后handle_mm_fault的返回值的VM_FAULT_WRITE位会被置为1。接着faultin_page会通过判断handle_mm_fault返回值的VM_FAULT_WRITE位是否为1来判断COW是否顺利完成，以及通过页表项VM_WRITE位是否为1来判断该内存是否可写。如果内存不可写且COW操作已经顺利完成，这说明mmap的内存区本来就是只读内存，因此为将FOLL_WRITE位置为0并返回到get_user_pages函数中

    
    
    faultin_page
      handle_mm_fault
        __handle_mm_fault
          handle_pte_fault
            FAULT_FLAG_WRITE && !pte_write
          do_wp_page
            PageAnon() <- this is CoWed page already
            reuse_swap_page <- page is exclusively ours
            wp_page_reuse
              maybe_mkwrite <- dirty but RO again
              ret = VM_FAULT_WRITE
    ((ret & VM_FAULT_WRITE) && !(vma->vm_flags & VM_WRITE)) <- we drop FOLL_WRITE

get_user_pages第三次调用follow_page_mask进行寻页，注意此时的FOLL_WRITE已被置为0，也就是在寻页的时候不再需要页具有写权限。正常来说，这次寻页会成功的得到Mappedmem的页表项从而继续进行写操作。但是如果这时Thread2通过madvise(Mappedmem,DONT_NEED)系统调用，通知内核Mappedmem在接下来不会被使用。内核会将Mappedmem所在页的页表项置为空。这样就再次导致了pagefault，内核会调用do_fault函数调页。不过由于这次寻页并不要求被寻找的页具有写权限，所以不会像第一次那样在缺页处理时COW。如果接下来get_user_pages第四次调用follow_page_mask进行寻页的话，会成功返回对应的页表项，接下来的写入操作会被同步到只读的文件中。从而造成了越权写。

    
    
    # Returns with 0 and retry as a read fault
    cond_resched -> different thread will now unmap via madvise
    follow_page_mask
      !pte_present && pte_none
    faultin_page
      handle_mm_fault
        __handle_mm_fault
          handle_pte_fault
            do_fault <- pte is not present
          do_read_fault <- this is a read fault and we will get pagecache
                   page!

  

**参考文献**

1\. <http://lxr.free-electrons.com/source/mm/gup.c>

2\. <http://lxr.free-electrons.com/source/include/linux/mm.h>

3\. <http://lxr.free-electrons.com/source/mm/memory.c>

4\. <https://github.com/dirtycow/>

5\. <http://blog.csdn.net/chenyu105/article/details/8653564>

6\. <http://blog.csdn.net/chenyu105/article/details/7061845>

7\. <http://www.cnblogs.com/biyeymyhjob/archive/2012/07/20/2601655.html>

8\. <http://blog.chinaunix.net/uid-16723279-id-3997363.html>

9\. <http://blog.csdn.net/vanbreaker/article/details/7881206>

10\. <http://blog.csdn.net/vanbreaker/article/details/7955713>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Atum** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84784](/post/id/84784)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t017ec6153b823abc2d.jpg) Atum

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

