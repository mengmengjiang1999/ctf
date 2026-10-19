**作者：[Hcamael@知道创宇404实验室](http://0x48.pw)**  
**英文版本：<https://paper.seebug.org/1028/>**

感恩节那天，meh在Bugzilla上提交了一个exim的uaf漏洞：<https://bugs.exim.org/show_bug.cgi?id=2199>，这周我对该漏洞进行应急复现，却发现，貌似利用meh提供的PoC并不能成功利用UAF漏洞造成crash

#### 漏洞复现

首先进行漏洞复现

##### 环境搭建

复现环境：ubuntu 16.04 server

    
    
    # 从github上拉取源码
    $ git clone https://github.com/Exim/exim.git
    # 在4e6ae62分支修补了UAF漏洞，所以把分支切换到之前的178ecb：
    $ git checkout ef9da2ee969c27824fcd5aed6a59ac4cd217587b
    # 安装相关依赖
    $ apt install libdb-dev libpcre3-dev
    # 获取meh提供的Makefile文件，放到Local目录下，如果没有则创建该目录
    $ cd src
    $ mkdir Local
    $ cd Local
    $ wget "https://bugs.exim.org/attachment.cgi?id=1051" -O Makefile
    $ cd ..
    # 修改Makefile文件的第134行，把用户修改为当前服务器上存在的用户，然后编译安装
    $ make && make install

然后再修改下配置文件`/etc/exim/configure`文件的第364行，把 `accept hosts = :` 修改成 `accept hosts
= *`

##### PoC测试

从<https://bugs.exim.org/attachment.cgi?id=1050>获取到meh的debug信息，得知启动参数：

    
    
    $ /usr/exim/bin/exim -bdf -d+all

PoC有两个:

  1. <https://bugs.exim.org/attachment.cgi?id=1049>
  2. <https://bugs.exim.org/attachment.cgi?id=1052>

需要先安装下pwntools，直接用pip装就好了，两个PoC的区别其实就是padding的长度不同而已

然后就使用PoC进行测试，发现几个问题：

  1. 我的debug信息在最后一部分和meh提供的不一样
  2. 虽然触发了crash，但是并不是UAF导致的crash

debug信息不同点比较：

    
    
    # 我的debug信息
    12:15:09  8215 SMTP>> 500 unrecognized command
    12:15:09  8215 SMTP<< BDAT 1
    12:15:09  8215 chunking state 1, 1 bytes
    12:15:09  8215 search_tidyup called
    12:15:09  8215 SMTP>> 250 1 byte chunk received
    12:15:09  8215 chunking state 0
    12:15:09  8215 SMTP<< BDAT 
    12:15:09  8215 LOG: smtp_protocol_error MAIN
    12:15:09  8215   SMTP protocol error in "BDAT \177" H=(test) [10.0.6.18] missing size for BDAT command
    12:15:09  8215 SMTP>> 501 missing size for BDAT command
    12:15:09  8215 host in ignore_fromline_hosts? no (option unset)
    12:15:09  8215 >>Headers received:
    12:15:09  8215 :
    ...一堆不可显字符
    **** debug string too long - truncated ****
    12:15:09  8215
    12:15:09  8215 search_tidyup called
    12:15:09  8215 >>Headers after rewriting and local additions:
    12:15:09  8215 :
    ......一堆不可显字符
    **** debug string too long - truncated ****
    12:15:09  8215
    12:15:09  8215 Data file name: /var/spool/exim//input//1eKcjF-00028V-5Y-D
    12:15:29  8215 LOG: MAIN
    12:15:29  8215   SMTP connection from (test) [10.0.6.18] lost while reading message data
    12:15:29  8215 SMTP>> 421 Lost incoming connection
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x2443048) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x2443068) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x2443098) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x24430c8) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x24430f8) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x2443128) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x2443158) failed: pool=0      smtp_in.c  841
    12:15:29  8215 SMTP>> 421 Unexpected failure, please try later
    12:15:29  8215 LOG: MAIN PANIC DIE
    12:15:29  8215   internal error: store_reset(0x2443188) failed: pool=0      smtp_in.c  841
    12:16:20  8213 child 8215 ended: status=0x8b
    12:16:20  8213   signal exit, signal 11 (core dumped)
    12:16:20  8213 0 SMTP accept processes now running
    12:16:20  8213 Listening...
                 --------------------------------------------    # meh的debug信息
    10:31:59 21724 SMTP>> 500 unrecognized command
    10:31:59 21724 SMTP<< BDAT 1
    10:31:59 21724 chunking state 1, 1 bytes
    10:31:59 21724 search_tidyup called
    10:31:59 21724 SMTP>> 250 1 byte chunk received
    10:31:59 21724 chunking state 0
    10:31:59 21724 SMTP<< BDAT 
    10:31:59 21724 LOG: smtp_protocol_error MAIN
    10:31:59 21724   SMTP protocol error in "BDAT \177" H=(test) [127.0.0.1] missing size for BDAT command
    10:31:59 21724 SMTP>> 501 missing size for BDAT command
    10:31:59 21719 child 21724 ended: status=0x8b
    10:31:59 21719   signal exit, signal 11 (core dumped)
    10:31:59 21719 0 SMTP accept processes now running
    10:31:59 21719 Listening...

发现的确是抛异常了，但是跟meh的debug信息在最后却不一样，然后使用gdb进行调试，发现：

    
    
    RAX  0xfbad240c
    *RBX  0x30
    *RCX  0xffffffffffffffd4
     RDX  0x2000
    *RDI  0x2b
    *RSI  0x4b7e8e ◂— jae    0x4b7f04 /* 'string.c' */
    *R8   0x0
    *R9   0x24
    *R10  0x24
    *R11  0x4a69e8 ◂— push   rbp
    *R12  0x4b7e8e ◂— jae    0x4b7f04 /* 'string.c' */
    *R13  0x1a9
    *R14  0x24431b8 ◂— 0x0
    *R15  0x5e
    *RBP  0x2000
    *RSP  0x7ffd75b862c0 —▸ 0x7ffd75b862d0 ◂— 0xffffffffffffffff
    *RIP  0x46cf1b (store_get_3+117) ◂— cmp    qword ptr [rax + 8], rdx
    --------------     > 0x46cf1b <store_get_3+117>    cmp    qword ptr [rax + 8], rdx
    ------------     Program received signal SIGSEGV (fault address 0xfbad2414)

根本就不是meh描述的利用UAF造成的crash，继续研究，发现如果把debug
all的选项`-d+all`换成只显示简单的debug信息的选项`-dd`，则就不会抛异常了

    
    
    $ sudo ./build-Linux-x86_64/exim -bdf -dd
    ......
     8266 Listening...
     8268 Process 8268 is handling incoming connection from [10.0.6.18]
     8266 child 8268 ended: status=0x0
     8266   normal exit, 0
     8266 0 SMTP accept processes now running
     8266 Listening...

又仔细读了一遍meh在Bugzilla上的描述，看到这句，所以猜测有没有可能是因为padding大小的原因，才导致crash失败的？所以写了代码对padding进行爆破，长度从0-0x4000，爆破了一遍，并没有发现能成功造成crash的长度。

> This PoC is affected by the block layout(yield_length), so this line:
> `r.sendline('a'*0x1250+'\x7f')` should be adjusted according to the program
> state.

所以可以排除是因为padding长度的原因导致PoC测试失败。

而且在漏洞描述页，我还发现Exim的作者也尝试对漏洞进行测试，不过同样测试失败了，还贴出了他的debug信息，和他的debug信息进行对比，和我的信息几乎一样。(并不知道exim的作者在得到meh的Makefile和log后有没有测试成功)。

所以，本来一次简单的漏洞应急，变为了对该漏洞的深入研究

#### 浅入研究

UAF全称是use after free，所以我在free之前，patch了一个printf：

    
    
    # src/store.c
    ......
    448 void
    449 store_release_3(void *block, const char *filename, int linenumber)
    450 {
    ......
    481    printf("--------free: %8p-------\n", (void *)bb);
    482    free(bb);
    483    return;
    484    }

重新编译跑一遍，发现竟然成功触发了uaf漏洞：

    
    
    $ /usr/exim/bin/exim -bdf -dd
     8334 Listening...
     8336 Process 8336 is handling incoming connection from [10.0.6.18]
    --------free: 0x1e2c1b0-------     8334 child 8336 ended: status=0x8b
     8334   signal exit, signal 11 (core dumped)
     8334 0 SMTP accept processes now running
     8334 Listening...

然后gdb调试的信息也证明成功利用uaf漏洞造成了crash：

    
    
    *RAX  0xdeadbeef
    *RBX  0x1e2e5d0 ◂— 0x0
    *RCX  0x1e29341 ◂— 0xadbeef000000000a /* '\n' */
    *RDX  0x7df
    *RDI  0x1e2e5d0 ◂— 0x0
    *RSI  0x46cedd (store_free_3+70) ◂— pop    rbx
    *R8   0x0
     R9   0x7f054f32b700 ◂— 0x7f054f32b700
    *R10  0xffff80fab41c4748
    *R11  0x203
    *R12  0x7f054dc69993 (state+3) ◂— 0x0
    *R13  0x4ad5b6 ◂— jb     0x4ad61d /* 'receive.c' */
    *R14  0x7df
    *R15  0x1e1d8f0 ◂— 0x0
    *RBP  0x0
    *RSP  0x7ffe169262b8 —▸ 0x7f054d9275e7 (free+247) ◂— add    rsp, 0x28
    *RIP  0xdeadbeef
    ------------------------------------------    Invalid address 0xdeadbeef

PS: 这里说明下`./build-Linux-x86_64/exim`这个binary是没有patch
printf的代码，`/usr/exim/bin/exim`是patch了printf的binary

到这里就很奇怪了，加了个printf就能成功触发漏洞，删了就不能，之后用`puts`和`write`代替了`printf`进行测试，发现`puts`也能成功触发漏洞，但是`write`不能。大概能猜到应该是stdio的缓冲区机制的问题，然后继续深入研究。

#### 深入研究

来看看meh在Bugzilla上对于该漏洞的所有描述：

    
    
    Hi, we found a use-after-free vulnerability which is exploitable to RCE in the SMTP server.
    
    According to receive.c:1783, 
    1783     if (!store_extend(next->text, oldsize, header_size))
    1784       {
    1785       uschar *newtext = store_get(header_size);
    1786       memcpy(newtext, next->text, ptr);
    1787       store_release(next->text);
    1788       next->text = newtext;
    1789       }
    
    when the buffer used to parse header is not big enough, exim tries to extend the next->text with store_extend function. If there is any other allocation between the allocation and extension of this buffer, store_extend fails.
    store.c
    276 if ((char *)ptr + rounded_oldsize != (char *)(next_yield[store_pool]) ||
    277     inc yield_length[store_pool] + rounded_oldsize - oldsize)
    278   return FALSE;
    
    Then exim calls store_get, and store_get cut the current_block directly.
    store.c
    208 next_yield[store_pool] = (void *)((char *)next_yield[store_pool] + size);
    209 yield_length[store_pool] -= size;
    210
    211 return store_last_get[store_pool];
    
    However, in receive.c:1787, store_release frees the whole block, leaving the new pointer points to a freed location. Any further usage of this buffer leads to a use-after-free vulnerability.
    To trigger this bug, BDAT command is necessary to perform an allocation by raising an error. Through our research, we confirm that this vulnerability can be exploited to remote code execution if the binary is not compiled with PIE.
    An RIP controlling PoC is in attachment poc.py. The following is the gdb result of this PoC:
    Program received signal SIGSEGV, Segmentation fault.
    0x00000000deadbeef in ?? ()
    (gdb)
     -------------------------------------------------------------    In receive.c, exim used receive_getc to get message.
    1831     ch = (receive_getc)(GETC_BUFFER_UNLIMITED);
    When exim is handling BDAT command, receive_getc is bdat_getc.
    In bdat_getc, after the length of BDAT is reached, bdat_getc tries to read the next command.
    smtp_in.c
     536 next_cmd:
     537   switch(smtp_read_command(TRUE, 1))
     538     {
     539     default:
     540       (void) synprot_error(L_smtp_protocol_error, 503, NULL,
     541     US"only BDAT permissible after non-LAST BDAT");
    
    synprot_error may call store_get if any non-printable character exists because synprot_error uses string_printing.
    
    string.c
     304 /* Get a new block of store guaranteed big enough to hold the
     305 expanded string. */
     306
     307 ss = store_get(length + nonprintcount * 3 + 1);
     ------------------------------------------------------------------    receive_getc becomes bdat_getc when handling BDAT data.
    Oh, I was talking about the source code of 4.89. In the current master, it is here:
    https://github.com/Exim/exim/blob/master/src/src/receive.c#L1790
    
    What this PoC does is:
    1. send unrecognized command to adjust yield_length and make it less than 0x100
    2. send BDAT 1
    3. send one character to reach the length of BDAT
    3. send an BDAT command without size and with non-printable character -trigger synprot_error and therefore call store_get
    // back to receive_msg and exim keeps trying to read header
    4. send a huge message until store_extend called
    5. uaf
    
    This PoC is affected by the block layout(yield_length), so this line: `r.sendline('a'*0x1250+'\x7f')` should be adjusted according to the program state. I tested on my ubuntu 16.04, compiled with the attached Local/Makefile (simply make -j8). I also attach the updated PoC for current master and the debug report.

在这里先提一下，在Exim中，自己封装实现了一套简单的堆管理，在src/store.c中

    
    
    void *
    store_get_3(int size, const char *filename, int linenumber)
    {
    /* Round up the size to a multiple of the alignment. Although this looks a
    messy statement, because "alignment" is a constant expression, the compiler can
    do a reasonable job of optimizing, especially if the value of "alignment" is a
    power of two. I checked this with -O2, and gcc did very well, compiling it to 4
    instructions on a Sparc (alignment = 8). */
    
    if (size % alignment != 0) size += alignment - (size % alignment);
    
    /* If there isn't room in the current block, get a new one. The minimum
    size is STORE_BLOCK_SIZE, and we would expect this to be the norm, since
    these functions are mostly called for small amounts of store. */
    
    if (size > yield_length[store_pool])
      {
      int length = (size <= STORE_BLOCK_SIZE)? STORE_BLOCK_SIZE : size;
      int mlength = length + ALIGNED_SIZEOF_STOREBLOCK;
      storeblock * newblock = NULL;
    
      /* Sometimes store_reset() may leave a block for us; check if we can use it */
    
      if (  (newblock = current_block[store_pool])
         && (newblock = newblock->next)
         && newblock->length < length
         )
        {
        /* Give up on this block, because it's too small */
        store_free(newblock);
        newblock = NULL;
        }
    
      /* If there was no free block, get a new one */
    
      if (!newblock)
        {
        pool_malloc += mlength;           /* Used in pools */
        nonpool_malloc -= mlength;        /* Exclude from overall total */
        newblock = store_malloc(mlength);
        newblock->next = NULL;
        newblock->length = length;
        if (!chainbase[store_pool])
          chainbase[store_pool] = newblock;
        else
          current_block[store_pool]->next = newblock;
        }
    
      current_block[store_pool] = newblock;
      yield_length[store_pool] = newblock->length;
      next_yield[store_pool] =
        (void *)(CS current_block[store_pool] + ALIGNED_SIZEOF_STOREBLOCK);
      (void) VALGRIND_MAKE_MEM_NOACCESS(next_yield[store_pool], yield_length[store_pool]);
      }
    
    /* There's (now) enough room in the current block; the yield is the next
    pointer. */
    
    store_last_get[store_pool] = next_yield[store_pool];
    
    /* Cut out the debugging stuff for utilities, but stop picky compilers from
    giving warnings. */
    
    #ifdef COMPILE_UTILITY
    filename = filename;
    linenumber = linenumber;
    #else
    DEBUG(D_memory)
      {
      if (running_in_test_harness)
        debug_printf("---%d Get %5d\n", store_pool, size);
      else
        debug_printf("---%d Get %6p %5d %-14s %4d\n", store_pool,
          store_last_get[store_pool], size, filename, linenumber);
      }
    #endif  /* COMPILE_UTILITY */
    
    (void) VALGRIND_MAKE_MEM_UNDEFINED(store_last_get[store_pool], size);
    /* Update next pointer and number of bytes left in the current block. */
    
    next_yield[store_pool] = (void *)(CS next_yield[store_pool] + size);
    yield_length[store_pool] -= size;
    
    return store_last_get[store_pool];
    }
    
    
    BOOL
    store_extend_3(void *ptr, int oldsize, int newsize, const char *filename,
      int linenumber)
    {
    int inc = newsize - oldsize;
    int rounded_oldsize = oldsize;
    
    if (rounded_oldsize % alignment != 0)
      rounded_oldsize += alignment - (rounded_oldsize % alignment);
    
    if (CS ptr + rounded_oldsize != CS (next_yield[store_pool]) ||
        inc > yield_length[store_pool] + rounded_oldsize - oldsize)
      return FALSE;
    
    /* Cut out the debugging stuff for utilities, but stop picky compilers from
    giving warnings. */
    
    #ifdef COMPILE_UTILITY
    filename = filename;
    linenumber = linenumber;
    #else
    DEBUG(D_memory)
      {
      if (running_in_test_harness)
        debug_printf("---%d Ext %5d\n", store_pool, newsize);
      else
        debug_printf("---%d Ext %6p %5d %-14s %4d\n", store_pool, ptr, newsize,
          filename, linenumber);
      }
    #endif  /* COMPILE_UTILITY */
    
    if (newsize % alignment != 0) newsize += alignment - (newsize % alignment);
    next_yield[store_pool] = CS ptr + newsize;
    yield_length[store_pool] -= newsize - rounded_oldsize;
    (void) VALGRIND_MAKE_MEM_UNDEFINED(ptr + oldsize, inc);
    return TRUE;
    }
    
    
    void
    store_release_3(void *block, const char *filename, int linenumber)
    {
    storeblock *b;
    
    /* It will never be the first block, so no need to check that. */
    
    for (b = chainbase[store_pool]; b != NULL; b = b->next)
      {
      storeblock *bb = b->next;
      if (bb != NULL && CS block == CS bb + ALIGNED_SIZEOF_STOREBLOCK)
        {
        b->next = bb->next;
        pool_malloc -= bb->length + ALIGNED_SIZEOF_STOREBLOCK;
    
        /* Cut out the debugging stuff for utilities, but stop picky compilers
        from giving warnings. */
    
        #ifdef COMPILE_UTILITY
        filename = filename;
        linenumber = linenumber;
        #else
        DEBUG(D_memory)
          {
          if (running_in_test_harness)
            debug_printf("-Release       %d\n", pool_malloc);
          else
            debug_printf("-Release %6p %-20s %4d %d\n", (void *)bb, filename,
              linenumber, pool_malloc);
          }
        if (running_in_test_harness)
          memset(bb, 0xF0, bb->length+ALIGNED_SIZEOF_STOREBLOCK);
        #endif  /* COMPILE_UTILITY */
    
        free(bb);
        return;
        }
      }
    }

UAF漏洞所涉及的关键函数：

  * store_get_3 堆分配
  * store_extend_3 堆扩展
  * store_release_3 堆释放

还有4个重要的全局变量：

  * chainbase
  * next_yield
  * current_block
  * yield_length

###### 第一步

发送一堆未知的命令去调整`yield_length`的值，使其小于0x100。

`yield_length`表示的是堆还剩余的长度，每次命令的处理使用的是[src/receive.c](https://github.com/Exim/exim/blob/ef9da2ee969c27824fcd5aed6a59ac4cd217587b/src/src/receive.c#L1617)代码中的`receive_msg`函数

在该函数处理用户输入的命令时，使用`next->text`来储存用户输入，在1709行进行的初始化：

    
    
    1625  int  header_size = 256;
    ......
    1709  next->text = store_get(header_size);

在执行1709行代码的时候，如果`0x100 > yield_length`则会执行到`newblock =
store_malloc(mlength);`，使用glibc的malloc申请一块内存，为了便于之后的描述，这块内存我们称为heap1。

根据`store_get_3`中的代码，这个时候：

  * current_block->next = heap1 (因为之前current_block==chainbase，所以这相当于是chainbase->next = heap1)
  * current_block = heap1
  * yield_length = 0x2000
  * next_yield = heap1+0x10
  * return next_yield
  * next_yield = next_yield+0x100 = heap1+0x110
  * yield_length = yield_length - 0x100 = 0x1f00

###### 第二步

发送`BDAT 1`，进入`receive_msg`函数，并且让`receive_getc`变为`bdat_getc`

###### 第三步

发送`BDAT \x7f`

相关代码在[src/smtp_in.c](https://github.com/Exim/exim/blob/b488395f4d99d44a950073a64b35ec8729102782/src/src/smtp_in.c)中的`bdat_getc`函数：

    
    
    int
    bdat_getc(unsigned lim)
    {
    uschar * user_msg = NULL;
    uschar * log_msg;
    
    for(;;)
      {
    #ifndef DISABLE_DKIM
      BOOL dkim_save;
    #endif
    
      if (chunking_data_left > 0)
        return lwr_receive_getc(chunking_data_left--);
    
      receive_getc = lwr_receive_getc;
      receive_getbuf = lwr_receive_getbuf;
      receive_ungetc = lwr_receive_ungetc;
    #ifndef DISABLE_DKIM
      dkim_save = dkim_collect_input;
      dkim_collect_input = FALSE;
    #endif
    
      /* Unless PIPELINING was offered, there should be no next command
      until after we ack that chunk */
    
      if (!pipelining_advertised && !check_sync())
        {
        unsigned n = smtp_inend - smtp_inptr;
        if (n > 32) n = 32;
    
        incomplete_transaction_log(US"sync failure");
        log_write(0, LOG_MAIN|LOG_REJECT, "SMTP protocol synchronization error "
          "(next input sent too soon: pipelining was not advertised): "
          "rejected \"%s\" %s next input=\"%s\"%s",
          smtp_cmd_buffer, host_and_ident(TRUE),
          string_printing(string_copyn(smtp_inptr, n)),
          smtp_inend - smtp_inptr > n ? "..." : "");
        (void) synprot_error(L_smtp_protocol_error, 554, NULL,
          US"SMTP synchronization error");
        goto repeat_until_rset;
        }
    
      /* If not the last, ack the received chunk.  The last response is delayed
      until after the data ACL decides on it */
    
      if (chunking_state == CHUNKING_LAST)
        {
    #ifndef DISABLE_DKIM
        dkim_exim_verify_feed(NULL, 0); /* notify EOD */
    #endif
        return EOD;
        }
    
      smtp_printf("250 %u byte chunk received\r\n", FALSE, chunking_datasize);
      chunking_state = CHUNKING_OFFERED;
      DEBUG(D_receive) debug_printf("chunking state %d\n", (int)chunking_state);
    
      /* Expect another BDAT cmd from input. RFC 3030 says nothing about
      QUIT, RSET or NOOP but handling them seems obvious */
    
    next_cmd:
      switch(smtp_read_command(TRUE, 1))
        {
        default:
          (void) synprot_error(L_smtp_protocol_error, 503, NULL,
        US"only BDAT permissible after non-LAST BDAT");
    
      repeat_until_rset:
          switch(smtp_read_command(TRUE, 1))
        {
        case QUIT_CMD:  smtp_quit_handler(&user_msg, &log_msg); /*FALLTHROUGH */
        case EOF_CMD:   return EOF;
        case RSET_CMD:  smtp_rset_handler(); return ERR;
        default:    if (synprot_error(L_smtp_protocol_error, 503, NULL,
                          US"only RSET accepted now") > 0)
                  return EOF;
                goto repeat_until_rset;
        }
    
        case QUIT_CMD:
          smtp_quit_handler(&user_msg, &log_msg);
          /*FALLTHROUGH*/
        case EOF_CMD:
          return EOF;
    
        case RSET_CMD:
          smtp_rset_handler();
          return ERR;
    
        case NOOP_CMD:
          HAD(SCH_NOOP);
          smtp_printf("250 OK\r\n", FALSE);
          goto next_cmd;
    
        case BDAT_CMD:
          {
          int n;
    
          if (sscanf(CS smtp_cmd_data, "%u %n", &chunking_datasize, &n) < 1)
        {
        (void) synprot_error(L_smtp_protocol_error, 501, NULL,
          US"missing size for BDAT command");
        return ERR;
        }
          chunking_state = strcmpic(smtp_cmd_data+n, US"LAST") == 0
        ? CHUNKING_LAST : CHUNKING_ACTIVE;
          chunking_data_left = chunking_datasize;
          DEBUG(D_receive) debug_printf("chunking state %d, %d bytes\n",
                        (int)chunking_state, chunking_data_left);
    
          if (chunking_datasize == 0)
        if (chunking_state == CHUNKING_LAST)
          return EOD;
        else
          {
          (void) synprot_error(L_smtp_protocol_error, 504, NULL,
            US"zero size for BDAT command");
          goto repeat_until_rset;
          }
    
          receive_getc = bdat_getc;
          receive_getbuf = bdat_getbuf;
          receive_ungetc = bdat_ungetc;
    #ifndef DISABLE_DKIM
          dkim_collect_input = dkim_save;
    #endif
          break;    /* to top of main loop */
          }
        }
      }
    }

BDAT命令进入下面这个分支：

    
    
    f (sscanf(CS smtp_cmd_data, "%u %n", &chunking_datasize, &n) < 1)
        {
        (void) synprot_error(L_smtp_protocol_error, 501, NULL,
          US"missing size for BDAT command");
        return ERR;
        }

因为`\x7F` 所以sscanf获取长度失败，进入`synprot_error`函数，该函数同样是位于`smtp_in.c`文件中：

    
    
    static int
    synprot_error(int type, int code, uschar *data, uschar *errmess)
    {
    int yield = -1;
    
    log_write(type, LOG_MAIN, "SMTP %s error in \"%s\" %s %s",
      (type == L_smtp_syntax_error)? "syntax" : "protocol",
      string_printing(smtp_cmd_buffer), host_and_ident(TRUE), errmess);
    
    if (++synprot_error_count > smtp_max_synprot_errors)
      {
      yield = 1;
      log_write(0, LOG_MAIN|LOG_REJECT, "SMTP call from %s dropped: too many "
        "syntax or protocol errors (last command was \"%s\")",
        host_and_ident(FALSE), string_printing(smtp_cmd_buffer));
      }
    
    if (code > 0)
      {
      smtp_printf("%d%c%s%s%s\r\n", FALSE, code, yield == 1 ? '-' : ' ',
        data ? data : US"", data ? US": " : US"", errmess);
      if (yield == 1)
        smtp_printf("%d Too many syntax or protocol errors\r\n", FALSE, code);
      }
    
    return yield;
    }

然后在`synprot_error`函数中有一个`string_printing`函数，位于[src/string.c](https://github.com/Exim/exim/blob/9242a7e8cfa94bbc9dd7eca6bd651b569b871c4e/src/src/string.c)代码中：

    
    
    const uschar *
    string_printing2(const uschar *s, BOOL allow_tab)
    {
    int nonprintcount = 0;
    int length = 0;
    const uschar *t = s;
    uschar *ss, *tt;
    
    while (*t != 0)
      {
      int c = *t++;
      if (!mac_isprint(c) || (!allow_tab && c == '\t')) nonprintcount++;
      length++;
      }
    
    if (nonprintcount == 0) return s;
    
    /* Get a new block of store guaranteed big enough to hold the
    expanded string. */
    
    ss = store_get(length + nonprintcount * 3 + 1);
    
    /* Copy everything, escaping non printers. */
    
    t = s;
    tt = ss;
    
    while (*t != 0)
      {
      int c = *t;
      if (mac_isprint(c) && (allow_tab || c != '\t')) *tt++ = *t++; else
        {
        *tt++ = '\\';
        switch (*t)
          {
          case '\n': *tt++ = 'n'; break;
          case '\r': *tt++ = 'r'; break;
          case '\b': *tt++ = 'b'; break;
          case '\v': *tt++ = 'v'; break;
          case '\f': *tt++ = 'f'; break;
          case '\t': *tt++ = 't'; break;
          default: sprintf(CS tt, "%03o", *t); tt += 3; break;
          }
        t++;
        }
      }
    *tt = 0;
    return ss;
    }

在`string_printing2`函数中，用到`store_get`, 长度为`length + nonprintcount * 3 +
1`，比如`BDAT \x7F`这句命令，就是`6+1*3+1 => 0x0a`，我们继续跟踪store中的全局变量，因为`0xa <
yield_length`，所以直接使用的Exim的堆分配，不会用到malloc，只有当上一次malloc
0x2000的内存用完或不够用时，才会再进行malloc

  * 0xa 对齐-> 0x10
  * return next_yield = heap1+0x110
  * next_yield = heap1+0x120
  * yield_length = 0x1f00 - 0x10 = 0x1ef0

最后一步，就是PoC中的发送大量数据去触发UAF：

    
    
    s = 'a'*6 + p64(0xdeadbeef)*(0x1e00/8)
    r.send(s+ ':\r\n')

再回到`receive.c`文件中，读取用户输入的是1788行的循环，然后根据meh所说，UAF的触发点是下面这几行代码：

    
    
    if (ptr >= header_size - 4)
        {
        int oldsize = header_size;
        /* header_size += 256; */
        header_size *= 2;
        if (!store_extend(next->text, oldsize, header_size))
          {
          uschar *newtext = store_get(header_size);
          memcpy(newtext, next->text, ptr);
          store_release(next->text);
          next->text = newtext;
          }
        }

当输入的数据大于等于`0x100-4`时，会触发`store_extend`函数，`next->text`的值上面提了，是`heap1+0x10`，`oldsize=0x100,
header_size = 0x100*2 = 0x200`

然后在`store_extend`中，有这几行判断代码：

    
    
    if (CS ptr + rounded_oldsize != CS (next_yield[store_pool]) ||
        inc > yield_length[store_pool] + rounded_oldsize - oldsize)
      return FALSE;

其中`next_yield = heap1+0x120`, `ptr + 0x100 = heap1+0x110`

因为判断的条件为true，所以`store_extend`返回False

这是因为在之前`string_printing`函数中分配了一段内存，所以在`receive_msg`中导致堆不平衡了，

随后进入分支会修补这种不平衡，执行`store_get(0x200)`

  * return next_yield = heap1+0x120
  * next_yield = heap1+0x320
  * yield_length = 0x1ef0 - 0x200 = 0x1cf0

然后把用户输入的数据复制到新的堆中

随后执行`store_release`函数，问题就在这里了，之前申请的0x2000的堆还剩0x1cf0，并没有用完，但是却对其执行glibc的free操作，但是之后这个free后的堆却仍然可以使用，这就是我们所知的UAF,
释放后重用漏洞

    
    
    for (b = chainbase[store_pool]; b != NULL; b = b->next)
      {
      storeblock *bb = b->next;
      if (bb != NULL && CS block == CS bb + ALIGNED_SIZEOF_STOREBLOCK)
        {
        b->next = bb->next;
        .......
        free(bb);
        return;
        }

其中，`bb = chainbase->next = heap1`, 而且`next->text == bb + 0x10`

所以能成功执行`free(bb)`

因为输入了大量的数据，所以随后还会执行：

  * store_extend(next->text, 0x200, 0x400)
  * store_extend(next->text, 0x400, 0x800)
  * store_extend(next->text, 0x800, 0x1000)

但是这些都不能满足判断：

    
    
    if (CS ptr + rounded_oldsize != CS (next_yield[store_pool]) ||
      inc > yield_length[store_pool] + rounded_oldsize - oldsize)

所以都是返回true，不会进入到下面分支

但是到`store_extend(next->text, 0x1000, 0x2000)`的时候，因为满足了第二个判断`0x2000-0x1000 >
yield_length[store_pool]`, 所以又一次返回了False

所以再一次进入分支，调用`store_get(0x2000)`

因为`0x2000 > yield_length`所以进入该分支：

    
    
    if (size > yield_length[store_pool])
      {
      int length = (size <= STORE_BLOCK_SIZE)? STORE_BLOCK_SIZE : size;
      int mlength = length + ALIGNED_SIZEOF_STOREBLOCK;
      storeblock * newblock = NULL;
    
      if (  (newblock = current_block[store_pool])
         && (newblock = newblock->next)
         && newblock->length < length
         )
        {
        /* Give up on this block, because it's too small */
        store_free(newblock);
        newblock = NULL;
        }
    
      if (!newblock)
        {
        pool_malloc += mlength;           /* Used in pools */
        nonpool_malloc -= mlength;        /* Exclude from overall total */
        newblock = store_malloc(mlength);
        newblock->next = NULL;
        newblock->length = length;
        if (!chainbase[store_pool])
          chainbase[store_pool] = newblock;
        else
          current_block[store_pool]->next = newblock;
        }
    
      current_block[store_pool] = newblock;
      yield_length[store_pool] = newblock->length;
      next_yield[store_pool] =
        (void *)(CS current_block[store_pool] + ALIGNED_SIZEOF_STOREBLOCK);
      (void) VALGRIND_MAKE_MEM_NOACCESS(next_yield[store_pool], yield_length[store_pool]);
      }

这里就是该漏洞的关键利用点

首先：`newblock = current_block = heap1`

然后：`newblock = newblock->next`

我猜测的meh的情况和我加了`printf`进行测试的情况是一样的，在`printf`中需要malloc一块堆用来当做缓冲区，所以在heap1下面又多了一块堆，在free了heap1后，heap1被放入了unsortbin，fd和bk指向了arena

所以这个时候，`heap1->next = fd = arena_top`

之后的流程就是：

  * current_block = arena_top
  * next_yield = arena_top+0x10
  * return next_yield = arena_top+0x10
  * next_yield = arena_top+0x2010

在执行完`store_get`后就是执行`memcpy`:

    
    
    memcpy(newtext, next->text, ptr);

上面的`newtext`就是`store_get`返回的值`arena_top+0x10`

把用户输入的数据copy到了arena中，最后达到了控制`RIP=0xdeadbeef`造成crash的效果

但是实际情况就不一样了，因为没有printf，所以heap1是最后一块堆，再free之后，就会合并到top_chunk中，fd和bk字段不会被修改，在释放前，这两个字段也是用来储存storeblock结构体的next和length，所以也是没法控制的

#### 总结

CVE-2017-16943的确是一个UAF漏洞，但是在我的研究中却发现没法利用meh提供的PoC造成crash的效果

之后我也尝试其他利用方法，但是却没找到合适的利用链

发现由于Exim自己实现了一个堆管理，所以在heap1之后利用`store_get`再malloc一块堆是不行的因为current_block也会被修改为指向最新的堆块，所以必须要能在不使用`store_get`的情况下，malloc一块堆，才能成功利用控制RIP，因为exim自己实现了堆管理，所以都是使用`store_get`来获取内存，这样就只能找`printf`这种有自己使用malloc的函数，但是我找到的这些函数再调用后都会退出`receive_msg`函数的循环，所以没办法构造成一个利用链

#### 引用

  1. [Exim源码](https://github.com/Exim/exim.git)
  2. [Bugzilla-2199](https://bugs.exim.org/show_bug.cgi?id=2199)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/469/>

