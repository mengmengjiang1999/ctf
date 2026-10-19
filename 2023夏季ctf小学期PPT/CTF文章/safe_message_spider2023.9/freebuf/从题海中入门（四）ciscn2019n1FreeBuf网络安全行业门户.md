## 0x01 前言

题目来自BUUCTF pwn。相关知识点总结是针对于题目写的，所以会比较简洁，如果想详细了解，知识点来源会在参考文献里给出链接^^。

## 0x02 审题

![image.png](https://image.3001.net/images/20220609/1654766444_62a1bb6c5255fffaea5a6.png!small)没从名字来看出啥，直接对文件进行分析吧。

## 0x03 静态分析

### 3.1 checksec体检

![image.png](https://image.3001.net/images/20220609/1654766770_62a1bcb212f017b3d2cab.png!small)  
`Stack: No canary found （栈溢出关闭） PIE: No PIE (0x400000) （地址随机化关闭） `

猜测又是一道栈溢出题目。

### 3.2 IDA pro分析

#### 3.2.1 阅读源码

主函数的内容没什么特别的，但是调用了func函数：![image.png](https://image.3001.net/images/20220609/1654767196_62a1be5c9e4216c2af918.png!small)就直接看func函数：  
![image.png](https://image.3001.net/images/20220609/1654767282_62a1beb229f11bdcef768.png!small)可以直接看到红框中的代码段就是我们的目标，那么往上阅读代码就可以知道如何才能让程序走到这个分支里：  
![image.png](https://image.3001.net/images/20220609/1654767530_62a1bfaabf41c302c1f00.png!small)这里的逻辑其实很清楚：

  1. call _gets 使用栈溢出的方法；

  2. jp short loc_4006CF 标志位PF为1时跳转，即奇偶性为偶数时跳转；

  3. jnz short loc_4006CF 标志位ZF不为0时跳转，即不相等时跳转；

命令ucomiss会比较两个数的值，进而影响ZF、PF、CF的值，我记忆的方法就是：第一个操作数减去第二操作数，根据结果判断那个标志位会发生改变，如结果为负数，说明发生了进位，即CF会变成1。  
根据以上逻辑，得出的判断就是：使程序不会跳转到loc_4006CF ——> PF为0，ZF为1 ——>
var_4是一个正常的数，且var_4与0x4007F4上的数相等。  
0x4007F4位置的数为：![image.png](https://image.3001.net/images/20220609/1654772670_62a1d3bed86d5989a9fe6.png!small)这是一个dd（四字节的数）:
41348000h

  
3.2.2 栈溢出点

在上文知道gets函数的输入变量是var_30，那么需要做的就是溢出var_30的范围进而覆盖var_4中的值，且使覆盖的值为41348000h。  
由下图stack of main所示，需要先填充30h-4h=2c h 个字节，再赋值41348000h。  
![image.png](https://image.3001.net/images/20220609/1654773373_62a1d67d2d1640e95fa28.png!small)  
![image.png](https://image.3001.net/images/20220609/1654773388_62a1d68c63689c34b72ab.png!small)

## 0x04 动态调试

为了方便验证思路，可以直接在gdb中给var_4的位置赋值，可以看到在gdb中，var_4的位置位于rbp-4：  
![image.png](https://image.3001.net/images/20220614/1655191619_62a83843b88703e731a62.png!small)那就直接打印出此位置，然后赋值：  
![image.png](https://image.3001.net/images/20220614/1655191760_62a838d0c31e71e6decde.png!small)![image.png](https://image.3001.net/images/20220614/1655191792_62a838f04428c47c20a3d.png!small)

赋值之后检查内存是否如料想中那样：  
![image.png](https://image.3001.net/images/20220614/1655191809_62a8390140de9c9dd7dc4.png!small)

再检查标志寄存器，确实如分析的那样，两个值相等会得到ZF：  
![image.png](https://image.3001.net/images/20220614/1655191875_62a839438c485de9d42ef.png!small)  
往下运行，发现可以成功走到system函数即为成功：  
![image.png](https://image.3001.net/images/20220614/1655192046_62a839eed4ca5877d7308.png!small)0x05
Exp编写

    
    
    from pwn import *
    
    #p = process('./warmup_csaw_2016')
    
    p = remote('node4.buuoj.cn', 25946)
    #context.terminal = ['tmux','splitw', '-h']
    #context(arch = 'amd64' , os = 'linux', log_level="debug")
    
    payload = b'a'*0x2c + p64(0x41348000)
    #gdb.attach(p, gdbscript="b *(0x40069e)")
    p.sendline(payload)
    
    p.interactive()
    

![image.png](https://image.3001.net/images/20220614/1655192594_62a83c12ec69a02c64608.png!small)

## 0x06 知识点总结

### 6.1 汇编

#### lea (load effective address)

lea reg16, mem  
LEA指令将存储器操作数mem的4位16进制偏移地址送到指定的寄存器。这里，源操作数必须是存储器操作数，目标操作数必须是16位通用寄存器。因该寄存器常用来作为地址指针，故在此最好选用四个间址寄存器BX,BP,SI,DI之一。

#### pxor

pxor XMM, XMM/m128  
源存储器128个二进制位'异或'目的寄存器128个二进制位,结果送入目的寄存器,内存变量必须对齐内存16字节。  
  

#### dword ptr [ ]

dword 双字 就是四个字节;  
ptr pointer缩写 即指针;  
[]里的数据是一个地址值，这个地址指向一个双字型数据;  
比如mov eax, dword ptr [12345678] 把内存地址12345678中的双字型（32位）数据赋给eax。  
  

#### movss

movss XMM, m32/XMM  
源操作数为m32时：dest[31-00] <== m32 dest[127-32] <== 0，即低位赋值，高位置零；  
源操作数为XMM时: dest[31-00] <== src[31-00] dest[127-32]不变。  
  

#### ucomiss

ucomiss XMM, m32/XMM  
ucomiss 这条指令会根据两个比较操作数的数值得到对应的四种不同的结果，对于每一种结果，OF、AF、SF 这三个标志位都会被清零，而 ZF、CF、PF
这三个标志位会根据比较结果的不同而有所不同。因此我们在实际应用场合不能用 L、G 等表示通用算术比较指令得到的带符号的条件码，因为它们主要依赖 OF 和
AF 这两个标志位。下面详细介绍这四种结果。

比较结果| 描述| ZF| PF| CF  
---|---|---|---|---  
UNORDERED| 当任一一个操作数为NaN时（包括QNaN和SNaN）| 1| 1| 1  
大于| 当第一个操作数大于第二个操作数时| 0| 0| 0  
小于| 当第一个操作数小于第二个操作数时| 0| 0| 1  
等于| 当第一个操作数相等于第二个操作数时| 1| 0| 0  
  
这里稍微科普一下关于QNaN和SNaN。QNaN表示“Quiet Not a
Number”，指示当前所产生的非数不需要发出异常信号；而SNaN表示“Signaling Not a
Number”，指示当前所产生的非数是情况比较严重的，可能需要发出异常信号（比如 0.0 / 0.0 之类的）。  
  

#### jp/jpe (jump when has parity flag)

jp/jpe xxx  
奇偶性为偶数时转移，当执行到JPE（JP）命令时，如果此时标志位PF=1，则跳转到指定的地址，如果PF=0，不跳转。  
  

#### jne/jnz (jump when not has zero flag）

jne/jnz xxx  
不等于时转移。  
  

#### 6.2 IDA pro

变量类型| 存储大小  
---|---  
db| 一字节  
dw| 两字节  
dd| 四字节  
df| 六字节  
dq| 八字节  
  
## 0x07 参考文献

[[BUUCTF]PWN5——ciscn_2019_n_1](https://blog.csdn.net/mcmuyanga/article/details/108219282)  
[BUUCTF—ciscn_2019_n_1
1](https://blog.csdn.net/qq_41560595/article/details/108783758)  
[汇编指令LEA](https://www.jianshu.com/p/3e89d834df85)  
[汇编指令:
JO、JNO、JB、JNB、JE、JNE、JBE、JA、JS、JNS、JP、JNP、JL、JNL、JNG、JG、JCXZ、JECXZ、JMP、JMPE](https://blog.csdn.net/ssihc0/article/details/5215044)  
[JS、JNS、JP（JPE）、JNP（JPO）指令详解、从原理上解释](https://blog.csdn.net/qq_41683305/article/details/105547177)  
[X86-EFLAGS寄存器](https://blog.csdn.net/jn1158359135/article/details/7761011)  
[汇编语言指令英文全称](https://blog.csdn.net/oBuYiSeng/article/details/48394667)  
[关于dword ptr 指令的意思](https://blog.csdn.net/kaiwii/article/details/7385929)  
[Intel 64/x86_64/IA-32/x86处理器 - SIMD指令集 - SSE扩展(6) - 逻辑指令 &
比较指令](https://blog.csdn.net/qq_43401808/article/details/86739754)  
[SSE2指令集](https://blog.csdn.net/hksoobe/article/details/100638536)

