原创 青空 合天智汇

## 0x00 前言  

疫情期间闲着也是闲着，在逆向某软件时深入了解了下ESP定律，然后就想写个文章记录并分享下。

> ESP定律又称堆栈平衡定律，是应用频率最高的脱壳方法之一
> ,不论是新手还是老手都经常用到。据我所知，ESP定律是一位外国大牛发现的，但目前已无从考证（未找到相关资料）。  
>

## 0x01 前置知识  

### 栈  

> 栈（stack）是内存中分配的一段空间。 向一个栈插入新元素又称作入（push）放到栈顶元素的上面，使之成为新的栈顶元素；
> 从一个栈删除元素又称作出栈（pop），它把栈顶元素删除掉，使其相邻的元素成为新的栈顶元素。  
>

![v2-97fafe9cb378ef9809dd315379169f24_720w](https://pic4.zhimg.com/80/v2-97fafe9cb378ef9809dd315379169f24_720w.jpg)

### call  

相当于高级语言中的函数调用。 当执行call指令时，进行两步操作： 将下一条的指令的地址压入栈中，再跳转到该地址处。 相当于：

    
    
    push ip 
    jmp near ptr 地址

### ret && retf  

> 与call指令相对应，将当前的ESP寄存器中指向的地址出栈，然后跳转到这个地址。 相当于：  
>
    
    
    pop ip
    #ret
    pop IP
    pop CS
    #retf

## 0x02 操作示例  

这是我写的一个带壳的32位小程序，用来当做esp定律应用的一个示例。这是一个比较机械的方法，但可以对esp定律有一个感性的认识。

首先用Exeinfo Pe查壳，发现是nspack壳。

![v2-c973c827d6de4b57c4a05d70d81a5c1e_720w](https://pic4.zhimg.com/80/v2-c973c827d6de4b57c4a05d70d81a5c1e_720w.png)

接下来用od载入程序，单步步入后，如箭头所示发现ESP寄存器变红。

![v2-2e6ebce30bd9ffc0eebdf9d45c4eb4a9_720w](https://pic3.zhimg.com/80/v2-2e6ebce30bd9ffc0eebdf9d45c4eb4a9_720w.png)

此时单击右键选中该寄存器进行数据窗口跟随。然后选中数据窗口任意字符下硬件断点（byte，word，dword均可）。

![v2-2a74f4e09cacc93a1370593eec459784_720w](https://pic3.zhimg.com/80/v2-2a74f4e09cacc93a1370593eec459784_720w.png)

f9运行后，f8连续单步步过找到OEP（ 程序的入口点
）。选中该地址单击右键选中用OllyDump脱壳调试进程，然后进行脱壳（如果发现程序不能打开，可以试试勾选重建输入表）。

![v2-7c08f06a5aa31b720ffccb8246dc5c1c_720w](https://pic1.zhimg.com/80/v2-7c08f06a5aa31b720ffccb8246dc5c1c_720w.png)

接着用Exeinfo Pe查壳，壳已经被去掉了。

![v2-cd22f1c3931a7f5c255c2d2076b01880_720w](https://pic3.zhimg.com/80/v2-cd22f1c3931a7f5c255c2d2076b01880_720w.png)

## 0x03 原理详解  

首先，壳实质上是一个子程序，它在程序运行时首先取得控制权并对程序进行压缩。 同时隐藏程序真正的OEP。大多数病毒就是基于此原理，从而防止被杀毒软件扫描。

壳的类型：

    
    
    • 解压->运行
    • 解压->运行->解压.->运行
    • 解压 decoder|encoded code->decode ->exc
    • Run the virtual machine

而脱壳的目的就是找到真正的OEP（入口点）。

而我们所讲到的ESP定律的本质是堆栈平衡，具体如下：

让我们看下加了壳的这个小程序的入口的各个寄存器的情况

    
    
    EAX 00000000
    ECX 004E820D offset r1.<ModuleEntryPoint>
    EDX 004E820D offset r1.<ModuleEntryPoint>
    EBX 0036C000
    ESP 0072FF74
    EBP 0072FF80
    ESI 004E820D offset r1.<ModuleEntryPoint>
    EDI 004E820D offset r1.<ModuleEntryPoint>
    EIP 004E820D r1.<ModuleEntryPoint>

然后是到OEP时各寄存器的情况

    
    
    EAX 0072FFCC
    ECX 004E820D offset r1.<ModuleEntryPoint>
    EDX 004E820D offset r1.<ModuleEntryPoint>
    EBX 0036A000
    ESP 0072FF74
    EBP 0072FF80
    ESI 004E820D offset r1.<ModuleEntryPoint>
    EDI 004E820D offset r1.<ModuleEntryPoint>
    EIP 00401500 r1.00401500

我们发现只有EIP和EAX寄存器的数值发生了变化，而EAX保存的是OEP的地址，这是什么原因呢？

> 由于在程序自解密或者自解压过程中, 多数壳会先将当前寄存器状态压栈, 如使用pushad, 而在解压结束后, 会将之前的寄存器值出栈,
> 如使用popad. 因此在寄存器出栈时, 往往程序代码被恢复, 此时硬件断点触发（这就是我们要下硬件断点的原因），然后在程序当前位置,
> 只需要一些单步操作, 就会到达正确的OEP位置.  
>

## 0x04 适用范围  

我自己总结了一个比较小白的方法，那就是载入程序后只有esp寄存器内容发生变化，那么这个程序多半可以用ESP定律（如有错误多谢指正）。

几乎全部的压缩壳， 一些早期的加密壳 （这是在网上收集到的资料总结的，经过我自己的实践，基本准确）。

## 0x05 总结  

以上就是我对ESP定律的理解，如有错误，请轻喷 ^-^ ，我也还只一只刚迈入二进制世界的菜鸟，希望我这篇文章对刚入门的小白有所帮助>_<

最后再加一句找OEP不是最难的，最难的还是修复。如果对OEP的识别有所疑惑可以问我也可以在网上收集相关资料，还是比较多的。

利用ESP定律进行脱壳

<http://www.hetianlab.com/expc.do?ec=ECID4054-1b54-4b49-9aa7-61ed981ca101>理解ESP原理的操作机理并掌握使用ESP原理进行脱壳的流程。）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

