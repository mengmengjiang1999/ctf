# 一、前言

if语句是属于流程控制语句一种，流程控制语句是进行逆向分析和还原高级代码的基础，对于想从事逆向分析工作，流程控制语句是很重要的。

作者：rkabyss

# 二、if语句分析

if语句是分支结构的重要组成部分。if语句的功能是先运算条件进行比较，然后根据比较结果选择对应的语句块来执行。if
语句只能判断两种情况∶"0"为假值，"非0"为真值。如果为真值，则进入语句块内执行语句；如果为假值，则跳过if语句块，继续运行程序的其他语句。要注意的是，if语句转换的条件跳转指令与if语句的判断结果是相反的。

源代码：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main() {
        int index = 0;
        if (index==0)
        {
            printf("index = 0\n");
        }
        system("pause");
        return 0;
    }

Debug x86

在IDA中if语句的流程图和执行伪汇编代码。

![1662023682_6310780201e7087c0d41c.png!small](https://image.3001.net/images/20220901/1662023682_6310780201e7087c0d41c.png!small)

在dbg x32中if语句的执行伪汇编代码。

![1662023705_63107819c2b9efd06030c.png!small](https://image.3001.net/images/20220901/1662023705_63107819c2b9efd06030c.png!small)

if的比较条件为index ==
0，如果成立，即为真值，则进入if语句块内执行语句。转换后的汇编代码使用的条件指令JNE判断结果为不等于0则跳转，因为按照if语句的规定，满足if判定的表达式才能执行if的语句块，而汇编语言的条件跳转却是满足某条件则跳转。

    
    
    //将ebp栈底指针入栈，以便程序执行结束可以进行恢复
    00C91850  push        ebp
    //将栈底变成新的栈顶
    00C91851  mov         ebp,esp
    //开辟一块0CCH大小的堆栈空间
    00C91853  sub         esp,0CCh
    //ebx入栈
    00C91859  push        ebx
    //esi（源地址)入栈
    00C9185A  push        esi
    //edi（目的地址）入栈
    00C9185B  push        edi
    //将ebp-0Ch地址处的值放入到edi中
    00C9185C  lea         edi,[ebp-0Ch]
    //ecx =3，为循环次数3次
    00C9185F  mov         ecx,3
    将开辟内存空间全部初始化成0CCCCCCCCh。
    00C91864  mov         eax,0CCCCCCCCh
    //上边代码都是在做前期初始化操作，开辟新的内存空间和堆栈，把之前栈顶与栈底放入新堆栈中，并将内存空间初始化成C
    00C91869  rep stos    dword ptr es:[edi]  
    00C9186B  mov         ecx,0C9C00Eh  
    00C91870  call        00C9131B
    //上边三行代码其实就是int main（）
    // [ebp-8] = 0
    00C91875  mov         dword ptr [ebp-8],0
    //使用cmp指令，将ebp-8地址处的4字节与0相减，根据结果改变标志位
    00C9187C  cmp         dword ptr [ebp-8],0
    //jne为不相则跳转
    00C91880  jne         00C9188F
    //0C97B30h = （index = 0）
    00C91882  push        0C97B30h
    //调用printf函数，把0C97B30h当参数传进去
    00C91887  call        00C910CD
    //进行平栈，堆栈平衡操作
    00C9188C  add         esp,4
    //esi = esp
    00C9188F  mov         esi,esp 
    //0C97B40h = pause
    00C91891  push        0C97B40h
    //调用system函数，把pause当参数传进去
    00C91896  call        dword ptr ds:[00C9B170h]
    //进行平栈，堆栈平衡操作
    00C9189C  add         esp,4
    //其实下边三行做的操作是return 0，函数返回
    00C9189F  cmp         esi,esp  
    00C918A1  call        00C9123F  
    00C918A6  xor         eax,eax
        
    //下边代码是在做恢复操作，把一开始开辟的堆栈和放入到堆栈地址进行恢复操作
    00C918A8  pop         edi  
    00C918A9  pop         esi  
    00C918AA  pop         ebx  
    00C918AB  add         esp,0CCh  
    00C918B1  cmp         ebp,esp  
    00C918B3  call        00C9123F  
    00C918B8  mov         esp,ebp  
    00C918BA  pop         ebp  
    00C918BB  ret

Release x32

![1662023745_6310784172d50d6a7a752.png!small](https://image.3001.net/images/20220901/1662023745_6310784172d50d6a7a752.png!small)

![1662023778_6310786243b547dedbef0.png!small](https://image.3001.net/images/20220901/1662023778_6310786243b547dedbef0.png!small)

Release进行判断，if判断条件为true，直接省略掉了index赋值与判断，直接调用if语句里面的打印语句。

    
    
    //5E2108h = （index = 0）
    005E1040  push        5E2108h
    //调用printf函数，把0C97B30h当参数传进去
    005E1045  call        005E1010
    //0C97B40h = pause
    005E104A  push        5E2114h
    //调用system函数，把pause当参数传进去
    005E104F  call        dword ptr ds:[005E2078h]
    //进行平栈，堆栈平衡操作
    005E1055  add         esp,8
    //eax = 0
    005E1058  xor         eax,eax
    //把值返回
    005E105A  ret 

Debug
x64![1662023794_63107872db7df8fdb6a7e.png!small](https://image.3001.net/images/20220901/1662023794_63107872db7df8fdb6a7e.png!small)

![1662023864_631078b841514a11b098d.png!small](https://image.3001.net/images/20220901/1662023864_631078b841514a11b098d.png!small)

在64位程序中，默认使用的是 fastcall， fastcall用的不是堆栈传参而是使用了寄存器传参。

    
    
    // [rbp-4] = 0
    00007FF7DD69187B  mov         dword ptr [rbp+4],0
    //使用cmp指令，将rbp+4地址处的4字节与0相减，根据结果改变标志位
    00007FF7DD691882  cmp         dword ptr [rbp+4],0
    //jne为不相则跳转
    00007FF7DD691886  jne         00007FF7DD691894
    //将00007FF7DD699C28h地址的值放入到rcx寄存器里
    00007FF7DD691888  lea         rcx,[00007FF7DD699C28h]
    //调用printf函数，把rcx当参数传进去
    00007FF7DD69188F  call        00007FF7DD691190
    //将00007FF7DD699C38h地址的值放入到rcx寄存器里
    00007FF7DD691894  lea         rcx,[00007FF7DD699C38h]
    //调用system函数，把pause当参数传进去
    00007FF7DD69189B  call        qword ptr [00007FF7DD6A0300h]
    //eax = 0
    00007FF7DD6918A1  xor         eax,eax
    //将rbp+00000000000000E8h地址里的值放入到rsp寄存器里
    00007FF7DD6918A3  lea         rsp,[rbp+00000000000000E8h]
    00007FF7DD6918AA  pop         rdi  
    00007FF7DD6918AB  pop         rbp  
    00007FF7DD6918AC  ret  

Release x64

![1662023884_631078cc3780f2179a860.png!small](https://image.3001.net/images/20220901/1662023884_631078cc3780f2179a860.png!small)

![1662023519_6310775fea367f39b6ff1.png!small](https://image.3001.net/images/20220901/1662023519_6310775fea367f39b6ff1.png!small)

    
    
    //将00007FF6EE632260h地址里的值放入到rcx寄存器里
    00007FF6EE631074  lea         rcx,[00007FF6EE632260h]
    //调用printf函数，把rcx当参数传进去
    00007FF6EE63107B  call        00007FF6EE631010
    //将00007FF6EE63226Ch地址里的值放入到rcx寄存器里
    00007FF6EE631080  lea         rcx,[00007FF6EE63226Ch]
    //调用system函数，把pause当参数传进去 
    00007FF6EE631087  call        qword ptr [00007FF6EE6320F8h]
    //eax = 0
    00007FF6EE63108D  xor         eax,eax
    //进行平栈
    00007FF6EE63108F  add         rsp,28h  
    00007FF6EE631093  ret 
    
    
    先执行各类影响标志位的指令
    其后是各种条件跳转指令
    jxx   XXXX   

如果遇到以上指令序列，可高度怀疑它是一个由if语句组成的单分支结构，根据比较信息与条件跳转指令，找到其跳转相反的逻辑，即可恢复分支结构原型。由于循环结构中也会出现类似的代码，因此在分析过程中还需要结合上下文分析。

# 三、总结

大家如果觉的哪里写的不好，或则哪里没写到，欢迎大家留言交流，互相进步。写这篇也是在进行总结，把会的知识点进行总结。

