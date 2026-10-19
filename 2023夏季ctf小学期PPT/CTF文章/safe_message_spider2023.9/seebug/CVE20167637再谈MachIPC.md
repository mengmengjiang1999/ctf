来源：[turingh.github.io](http://turingh.github.io/2017/01/10/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/)

作者：[turingH](https://github.com/turingH)

> 为学大病在好名。

## 0x00 摘要

去年在分析[CVE-2016-1757](http://turingh.github.io/2016/07/05/%E5%86%8D%E7%9C%8BCVE-2016-1757%E6%B5%85%E6%9E%90mach%20message%E7%9A%84%E4%BD%BF%E7%94%A8/)时，初步的接触了`Mach`在`IPC`系统中使用的`Message`，在分析最近的一系列与`IPC`模块相关的漏洞时，又加强对`IPC`模块的理解，所以通过一到两篇文章梳理一下最近的学习总结与心得体会。

关于[CVE-2016-7637](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-7637)这个漏洞的描述有很多资料了，是一个攻击`Mach`的内核`IPC`模块的漏洞，本文最后会对漏洞做出比较详细的解释，这里给出几个链接，不熟悉这个漏洞的读者可以先了解一下。

[黑云压城城欲摧 -2016年iOS公开可利用漏洞总结](https://jaq.alibaba.com/community/art/show?articleid=687)

[mach portal漏洞利用的一些细节](http://blog.pangu.io/mach-portal-details/)

[Broken kernel mach port name uref](https://bugs.chromium.org/p/project-zero/issues/detail?id=959&can=1&q=apple&sort=-id)

## 0x01 什么是Port

对于一般的开发者，在用到`Port`的时候可以简单的将`Port`理解为进程间通信所使用的类似于`Socket`的东西，可以用他来发送消息，也可以用来接收消息。

下面我们来一步一步的构建对整个模块的理解。

已经知道`Port`是什么的读者可以跳过这一个部分。

### 1.1 利用Port传递数据

`Port`最简单的可以理解为一个内核中的消息队列。不同的`Task`通过这个消息队列相互传递数据。而`Port`就是用于找到这个队列的索引。

![利用Port传递数据](https://raw.githubusercontent.com/turingH/BLOGIMAGE/master/png/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/%E5%88%A9%E7%94%A8Port%E4%BC%A0%E9%80%92%E6%95%B0%E6%8D%AE.png)

### 1.2 Port、Port Name 与 Right

通过函数`mach_port_allocate`就可以在内核中建立一个消息队列，并获取一个与之对应的的`Port`。代码如下。

    
    
    mach_port_t p;
    mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &p);

通过查看内核源码，

    
    
    /*
     *  Purpose:
     *      Allocates a right in a space.  Like mach_port_allocate_name,
     *      except that the implementation picks a name for the right.
     *      The name may be any legal name in the space that doesn't
     *      currently denote a right.
     */
    kern_return_t
    mach_port_allocate(
        ipc_space_t     space,
        mach_port_right_t   right,
        mach_port_name_t    *namep)
    {
        kern_return_t       kr;
        mach_port_qos_t     qos = qos_template;
    
        kr = mach_port_allocate_full (space, right, MACH_PORT_NULL,
                        &qos, namep);
        return (kr);
    }

仔细看的话会发现，对我们刚刚申请的`p`出现了好几个解释，一下就晕了。

  * 在应用层代码中，p被定义为`mach_port_t`。
  * 在内核中代码中，`namep`是`mach_port_name_t`。
  * 在注释中又说，Allocates a RIGHT in a space。

#### 1.2.1 Port与Port Name

通过调试器观察一下，可以发现，

    
    
    (lldb) p p
    (mach_port_t) $0 = 3331
    
    
     * frame #0: 0xffffff801d4ee11d kernel`mach_port_allocate_full(space=0xffffff8024ceac00, right=1, proto=0x0000000000000000, qosp=0xffffff887d7b3ef0, namep=0xffffff887d7b3eec

在应用层的`mach_port_t`是一个已经经过代码处理的类似于`Socket`的一个整数，来表示这个`Port`。

而`namep`在内核之中是一个地址，指向了一块用来索引`Port`的内存，具体的实现在本文的后面会有更详细的解释。

#### 1.2.2 Right

这里注释所说的`Right`简单的理解，其实是一个`Port`和对这个`Port`进行访问的权限。每一个`Port`代表的消息队列并不是可以任意访问的，需要有对这个队列的访问权限。各种权限在头文件中的定义如下。

    
    
    #define MACH_PORT_RIGHT_SEND      ((mach_port_right_t) 0)
    #define MACH_PORT_RIGHT_RECEIVE   ((mach_port_right_t) 1)
    #define MACH_PORT_RIGHT_SEND_ONCE ((mach_port_right_t) 2)
    #define MACH_PORT_RIGHT_PORT_SET  ((mach_port_right_t) 3)
    #define MACH_PORT_RIGHT_DEAD_NAME ((mach_port_right_t) 4)
    #define MACH_PORT_RIGHT_NUMBER    ((mach_port_right_t) 5)

每种`Right`都有不同的含义，可以自行查阅文档。

这里需要简单的提一下的就是每一个`Port`都有且只有`Task`对其拥有`RECEIVE`的权限，`SEND`的权限不限。拥有`MACH_PORT_RIGHT_RECEIVE`时也可以对`Port`进行消息的Send。

![PORT_NAME_RIGHT](https://raw.githubusercontent.com/turingH/BLOGIMAGE/master/png/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/PORT_NAME_RIGHT.png)

### 1.3 Port的具体实现

阅读`mach_port_allocate_full`函数的源码，最终在一个`port`的创建流程中，最主要的函数是`ipc_port_alloc`以及在其实现中调用的`ipc_object_alloc`。

    
    
    kern_return_t
    ipc_port_alloc(
        ipc_space_t     space,
        mach_port_name_t    *namep,
        ipc_port_t      *portp)
    {
        ipc_port_t port;
        mach_port_name_t name;
        kern_return_t kr;
    
        kr = ipc_object_alloc(space, IOT_PORT,
                      MACH_PORT_TYPE_RECEIVE, 0,
                      &name, (ipc_object_t *) &port);
        if (kr != KERN_SUCCESS)
            return kr;
    
        /* port and space are locked */
        ipc_port_init(port, space, name);
        [...]
    
        *namep = name; <--namep是从这里来的。
        *portp = port;
    
        return KERN_SUCCESS;
    }

很明显，`port`和`name`两个变量都是由函数`ipc_object_alloc`中获取的。关键源码如下。

    
    
    kern_return_t
    ipc_object_alloc(
        ipc_space_t     space, 
        ipc_object_type_t   otype,
        mach_port_type_t    type,
        mach_port_urefs_t   urefs,
        mach_port_name_t    *namep,
        ipc_object_t        *objectp)
    {
        ipc_object_t object;
        ipc_entry_t entry;
        kern_return_t kr;
    
        [...]
    
        //从zone中申请内存,这个object就是ipc_port
        object = io_alloc(otype);   
    
        [...]
    
        //获取namep和entry
        *namep = CAST_MACH_PORT_TO_NAME(object);
        kr = ipc_entry_alloc(space, namep, &entry);
        if (kr != KERN_SUCCESS) {
            io_free(otype, object);
            return kr;
        }
        /* space is write-locked */
    
        //设置关键的参数
        entry->ie_bits |= type | urefs;
        entry->ie_object = object;
        ipc_entry_modified(space, *namep, entry);
    
        io_lock(object);
    
        object->io_references = 1; /* for entry, not caller */
        object->io_bits = io_makebits(TRUE, otype, 0);
    
        *objectp = object;
        return KERN_SUCCESS;
    }

#### 1.3.1 IPC Space 和 IPC Entry

细心的读者会发现前面有个叫做`space`的参数没有解释。这里又出现了一个新的结构叫做`entry`。他们是有关系的，这里我们来一起解释一下。

> Each task has a private IPC _space_ a namespace for portsthat is represented
> by the ipc_space structure in the kernel.
>
> Mac OS X Internals

每一个`Task`都有一个自己独立的`IPC`的数据空间，就是这里的`space`。他的数据结构是定义如下。

    
    
    // osfmk/ipc/ipc_space.h
    
    typedef natural_t ipc_space_refs_t;
    
    struct ipc_space {
        decl_mutex_data(,is_ref_lock_data)
        ipc_space_refs_t is_references;
    
        decl_mutex_data(,is_lock_data)
    
        // is the space active?
        boolean_t is_active;
    
        // is the space growing?
        boolean_t is_growing;
    
        // table (array) of IPC entries
        // 这个是最重要的，存放了所有的entry
        ipc_entry_t is_table; 
    
        // current table size
        ipc_entry_num_t is_table_size;
    
        // information for larger table
        struct ipc_table_size *is_table_next;
    
        // splay tree of IPC entries (can be NULL)
        struct ipc_splay_tree is_tree;
    
        // number of entries in the tree
        ipc_entry_num_t is_tree_total;
    
        // number of "small" entries in the tree
        ipc_entry_num_t is_tree_small;
    
        // number of hashed entries in the tree
        ipc_entry_num_t is_tree_hash;
    
        // for is_fast_space()
        boolean_t is_fast;
    };

而我们研究的对象 `Mach Ports`全都存储在`is_table`这个数组中，这个数组就是由`ipc_entry`组成的。

    
    
        struct ipc_entry {
            struct ipc_object *ie_object;   //ipc_port_t
            ipc_entry_bits_t ie_bits;       //gen|0|0|0|capability|user reference
            mach_port_index_t ie_index;
            union {
                mach_port_index_t next;     /* next in freelist, or...  */
                ipc_table_index_t request;  /* dead name request notify */
            } index;
        };

用一张书上的图，很清楚的表明了他们之间的关系。

![](https://raw.githubusercontent.com/turingH/BLOGIMAGE/master/png/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/space%E5%92%8Centry.png)

#### 1.3.2 ipc_port

相对而言ipc_port的数据结构就较为简单了。在复制给`space`的`ie_object`之后，通过`ipc_port_init`函数的初始化，就完成了`port`的创建了。

    
    
    ipc_port_init(
        ipc_port_t      port,
        ipc_space_t     space,
        mach_port_name_t    name)
    {
        /* port->ip_kobject doesn't have to be initialized */
    
        port->ip_receiver = space;
        port->ip_receiver_name = name;
    
        port->ip_mscount = 0;
        port->ip_srights = 0;
        port->ip_sorights = 0;
    
        port->ip_nsrequest = IP_NULL;
        port->ip_pdrequest = IP_NULL;
        port->ip_requests = IPR_NULL;
    
        port->ip_premsg = IKM_NULL;
        port->ip_context = 0;
    
        port->ip_sprequests  = 0;
        port->ip_spimportant = 0;
        port->ip_impdonation = 0;
        port->ip_tempowner   = 0;
    
        port->ip_guarded      = 0;
        port->ip_strict_guard = 0;
        port->ip_impcount    = 0;
    
        port->ip_reserved    = 0;
    
        ipc_mqueue_init(&port->ip_messages,
                FALSE /* !set */, NULL /* no reserved link */);
    }

这里同样的用书上的一张图就可以很简单的解释清楚了。

![ipc_port](https://raw.githubusercontent.com/turingH/BLOGIMAGE/master/png/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/ipc_port.png)

## 0x02 POC的分析

​ POC原来的writeup在[这里](https://bugs.chromium.org/p/project-zero/issues/detail?id=959&can=1&q=apple&sort=-id)。

​ 原文已经解释的非常清楚了，我就不画蛇添足了。简单记录一下我自己在分析的过程中的一些问题。

### 2.1 port的user reference计数代表了什么？

​ 一个`port`的`user
reference`只表示了某个`entry`在`task`的`space`中被多少个地方使用，和`entry`实际指向哪个`port`没有关系。

​

### 2.2 ipc_right_dealloc函数是只释放了entry还是同时也在内存中释放了port？

​ `ipc_right_dealloc`函数相关部分源码如下：

    
    
    kern_return_t
    ipc_right_dealloc(
        ipc_space_t     space,
        mach_port_name_t    name,
        ipc_entry_t     entry)
    {
        ipc_port_t port = IP_NULL;
        ipc_entry_bits_t bits;
        mach_port_type_t type;
    
        bits = entry->ie_bits;
        type = IE_BITS_TYPE(bits);
    
        assert(is_active(space));
        switch (type) {
             [...]
            case MACH_PORT_TYPE_SEND: {
            [...]
            port = (ipc_port_t) entry->ie_object;
            [...]
             //如果在task内entry的reference已经为1了就
             //释放entry
             //如果计数不为1，就将计数减一
            if (IE_BITS_UREFS(bits) == 1) {
                if (--port->ip_srights == 0) {
                    nsrequest = port->ip_nsrequest;
                    if (nsrequest != IP_NULL) {
                        port->ip_nsrequest = IP_NULL;
                        mscount = port->ip_mscount;
                    }
                }
    
                [...]
                entry->ie_object = IO_NULL;
                ipc_entry_dealloc(space, name, entry);
                is_write_unlock(space);
                ip_release(port);
    
            } else {
                ip_unlock(port);            
                entry->ie_bits = bits-1; /* decrement urefs */
                ipc_entry_modified(space, name, entry);
                is_write_unlock(space);
            }
        [...]
    
        return KERN_SUCCESS;
    }

所以当`entry`计数为1的时候，调用了`ipc_entry_dealloc`，`ipc_entry_dealloc`不会将`entry`对应的内存释放，而是将其放入一个`free_list`等待重复使用。`entry`的内存不会释放，而且`entry`在`is_table`中的`index`也并不会改变，只是被放到了一个结构管理的队列中去了。

对于`Port`来说，内核调用了`ip_release`，这个函数的作用是减少`ipc_object`自身的`reference`，如果`port`的索引变为0了，那就会被释放，如果系统中还有其他的进程在使用这个`port`，那么这个`port`就不会被释放。

### 2.3 如何通过调试器调试漏洞触发的现场?

一开始我想的方法是对`ipc_right_copyout`下条件断点，条件是`entry->ie_bits&0xffff ==
0xfffe`。但是因为`ipc_right_copyout`这个函数在内核中的调用太过于频繁，导致虚拟机跑太卡了。

只能通过逆向，在汇编代码处下断点。（内核版本10.12_16A323）

![](https://raw.githubusercontent.com/turingH/BLOGIMAGE/master/png/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/bug%E7%82%B9.png)

对应的就是出bug的代码段。

    
    
               if (urefs+1 == MACH_PORT_UREFS_MAX) {
                    if (overflow) {
                        /* leave urefs pegged to maximum */     <---- (1)
    
                        port->ip_srights--;
                        ip_unlock(port);
                        ip_release(port);
                        return KERN_SUCCESS;
                    }
    
                    ip_unlock(port);
                    return KERN_UREFS_OVERFLOW;
                }

所以通过断点

    
    
    b *(0xffffff80002e6fbb + kslide)

就可以得到漏洞触发时的情况。

![](https://raw.githubusercontent.com/turingH/BLOGIMAGE/master/png/CVE-2016-7637-%E5%86%8D%E8%B0%88Mach-IPC/%E8%A7%A6%E5%8F%91.png)

### 2.4 port替换的原理是什么?

port是通过`port
name`在task中来获取的。在前文中提到，`namep`是通过函数`ipc_entry_alloc`来获取的。查看获取到`namep`的核心代码如下：

    
    
    kern_return_t
    ipc_entry_claim(
        ipc_space_t     space,
        mach_port_name_t    *namep,
        ipc_entry_t     *entryp)
    {
        ipc_entry_t entry;
        ipc_entry_t table;
        mach_port_index_t first_free;
        mach_port_gen_t gen;
        mach_port_name_t new_name;
    
        table = &space->is_table[0];
    
        first_free = table->ie_next;
        assert(first_free != 0);
    
        entry = &table[first_free];  //[1]
        table->ie_next = entry->ie_next;
        space->is_table_free--;
    
        assert(table->ie_next < space->is_table_size);
    
        /*
         *  Initialize the new entry.  We need only
         *  increment the generation number and clear ie_request.
         */
        gen = IE_BITS_NEW_GEN(entry->ie_bits); //[2]
        entry->ie_bits = gen;
        entry->ie_request = IE_REQ_NONE;
    
        /*
         *  The new name can't be MACH_PORT_NULL because index
         *  is non-zero.  It can't be MACH_PORT_DEAD because
         *  the table isn't allowed to grow big enough.
         *  (See comment in ipc/ipc_table.h.)
         */
        new_name = MACH_PORT_MAKE(first_free, gen); //[3]
        assert(MACH_PORT_VALID(new_name));
        *namep = new_name;
        *entryp = entry;
    
        return KERN_SUCCESS;
    }

通过[1]可以看到，正如2.2节提到的一样，`entry`在`table`中的`index`是不变的。

通过[2]可以看到，每次使用`entry`来存放一个新`port`时，`gen`的值会加1。

通过[3]可以看到，`namep`就是通过这两个参数生成的。

因为`index`是不变的，所以在通过漏洞释放target_port之后，不断的对目标`entry`进行申请和释放，就可以通过整形溢出，使得`gen`变成和taget_port释放之前使用的entry相同。

那么就实现了在`port_name`不变的情况下替换了`port`的内核对象。

## 0x03 小结

通过CVE-2016-7637的分析和研究加深了对`port`这个数据结构的理解，并且通过对`poc`的分析，体现了一个`port`在单个`task`中的状态变化，实际上是`ipc_space`和`ipc_entry`状态变化。

接下来就要分析学习CVE-2016-7644，通过对CVE-2016-7644的分析学习，可以更加深入的理解port在内核中状态的变化。也就是`port`自身的`port->srights`和`io_reference`的状态变化及漏洞的利用。

## 参考

  1. 《Mac OS X Internals》

  2. [Broken kernel mach port name uref](https://bugs.chromium.org/p/project-zero/issues/detail?id=959&can=1&q=apple&sort=-id)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/197/>

