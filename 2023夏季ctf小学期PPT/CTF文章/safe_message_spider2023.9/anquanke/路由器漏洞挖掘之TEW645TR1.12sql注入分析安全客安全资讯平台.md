# 路由器漏洞挖掘之 TEW_645TR_1.12 sql 注入分析

阅读量 **277393**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-13 15:45:35

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

这次再来复现一个路由器的 sql 注入类型的漏洞。在实际环境中可能注入会比较少见，而且这个洞也比较老了，但是为了掌握更大的漏洞攻击面还是有必要去接触的。

## 漏洞分析

###  环境搭建

还是使用 qemu-user 模式，同样的还是编写一个 sh 脚本：

    
    
    #!/bin/bash
    
    INPUT="$1"
    LEN=$(echo -n "$INPUT"|wc -c)
    DEBUG="$2"
    
    if [ "$DEBUG" == "-d" ]
    then
    echo $INPUT | chroot . ./qemu -E REMOTE_ADDR="127.0.0.1" -E CONTENT_TYPE="multipart/x-form-data" -E REQUEST_METHOD="POST" -g 23946 -E CONTENT_LENGTH=$LEN ./usr/bin/my_cgi.cgi
    
    else
    echo $INPUT | chroot . ./qemu -E REMOTE_ADDR="127.0.0.1" -E CONTENT_TYPE="multipart/x-form-data" -E REQUEST_METHOD="POST" -E CONTENT_LENGTH=$LEN ./usr/bin/my_cgi.cgi
    
    fi
    

不带调试的运行结果：

![](https://p1.ssl.qhimg.com/dm/1024_151_/t018fb211a555d7309a.png)

使用 IDA 进行动态调试发现已经将我们的输 **入直接拼接到 bss 段的 sql 变量中**

![](https://p0.ssl.qhimg.com/dm/1024_361_/t015ebbb259382a18d2.png)

## 漏洞分析

在进行漏洞分析时，还发现了存在多处的栈溢出漏洞。

###  多处栈溢出

在 do_login 函数的开头，s1 寄存器的值为 “request”：

![](https://p1.ssl.qhimg.com/dm/1024_420_/t018544101daf4bee64.png)

在执行第一个 strcpy 函数时， **直接将 user_name 的值复制到栈上，导致栈溢出**

![](https://p0.ssl.qhimg.com/dm/1024_429_/t01045512b95c4ac3b3.png)

同样在执行第二个 strcpy 函数之前，在右边的 `general register` 窗口中跟进 a1 寄存器的值（在 a1 寄存器上右键，`Jump
in a new window`）

![](https://p4.ssl.qhimg.com/dm/1024_391_/t01fc5fd592cf6d09b5.png)

同样使用 Ghidra 9.0 的反汇编窗口中也可以很清楚看到这个漏洞，`*(iParm1 + 0x299) 和 *(iParm1 + 0x512)`
分别为传入的 user_name 和 user_pass

![](https://p0.ssl.qhimg.com/dm/1024_450_/t01428b0d468b6d14f0.png)

继续往下分析，又有一个危险函数 sprintf ， **这里会将用户名和密码格式化一个 sql 语句到 bss 段的 sql 变量，所以按理说如果输入的
user_name 或者 user_pass 过长，那么这里也是存在一处 bss 溢出的** 。

![](https://p1.ssl.qhimg.com/dm/1024_420_/t0150f6bc62a34a6114.png)

Ghidra 中的代码：

    
    
    sprintf(sql,"select level from user where user_name='%s' and user_pwd='%s'",&local_60,&local_40);
    

接着会往下执行 exec_sql 函数来执行 sql 函数，这里先 f8 步过

![](https://p5.ssl.qhimg.com/dm/1024_540_/t01a9cc965d709a649c.png)

这里执行 sql 查询以及下面的判断如下，经过 exec_sql 函数的执行之后，取得返回值来判断登录的状态

    
    
     iVar1 = exec_sql(my_db,sql,__ptr);
      if (iVar1 == 0) {
        if (*(int *)((int)__ptr + 0x4f200) == 0) {
          __n_00 = strlen(sql);
          memset(sql,0,__n_00);
          sprintf(sql,"select level from user where user_name='%s'",&local_60);
          iVar2 = exec_sql(my_db,sql,__ptr);        // 无过滤直接拼接 SQL 语句
          if (iVar2 == 0) {
            if (*(int *)((int)__ptr + 0x4f200) == 0) {
              uVar2 = *strings;
            }
            else {
              uVar2 = strings[1];
            }
            add_msg(uVar2,"login");
          }
          free(__ptr);
          set_redirect_page(&DAT_00417e98);
          return;
        }
        iVar2 = atoi((char *)((int)__ptr + 0x20));
        iVar2 = add_login_user(uParm3,iVar2);
        if (iVar2 == 0) {
          add_msg(strings[3],"login");
          pcVar3 = "back";
        }
        else {
          if (iParm4 != 1) {
            free(__ptr);
            set_redirect_page(0x4174a8);
            return;
          }
          pcVar3 = "wlan_client_basic";
        }
      }
      else {
        pcVar3 = "login";
      }
      free(__ptr);
      set_redirect_page(pcVar3);
      return;
    

这里确实是将用户名和密码不经过过滤就直接传入拼接出 sql 语句并且传入 exec_sql 函数

    
    
    exec_sql(db,"select level...",heap_ptr)
    

在 gdb-multiarch 动态调试中也可以发现：

![](https://p1.ssl.qhimg.com/t01fd38f0ee88fa4330.png)

这里的 `exec_sql` 函数为位于：

    
    
    ./squashfs-root/lib/libdbapi.so.1.0.0
    

我们把这个链接库文件加载到 Ghidra 中进行静态分析。

![](https://p5.ssl.qhimg.com/dm/1024_429_/t01c60f2a30f74544d3.png)

在 0x766c1034 处下一个断点，可以知道这里调用的是 sqlite3_exec，此函数的地址是 0x76769470

![](https://p0.ssl.qhimg.com/t01b75827e18c206cdf.png)

此时执行的函数如下，拼接传入的 sql 语句位于第二个参数：

    
    
    sqlite3_exec(db,"select level...",(void *)(callback_exec),**a3)
    

通过 vmmap 命令可以找到这个函数位于：

    
    
    /lib/libsqlite3.so.0.8.6
    

继续将他放到 Ghidra 中分析，在左边的导出表 Exports 中找到 sqlite3_exec 函数

![](https://p2.ssl.qhimg.com/dm/1024_406_/t01dd47fda425f6a16b.png)

发现这里执行的都是 sqlite3 中标准的数据库函数，即 sqlite3_open、sqlite3_prepare、sqlite3_exec 等等，参考：  
<https://www.cnblogs.com/zfyouxi/p/5258589.html>

这里 exec_sql 函数的原型：

![](https://p0.ssl.qhimg.com/dm/1024_403_/t01482f02cbd8517cfa.png)

###  函数分析

回到上面的函数，关注前两个参数：

  1. 第一个参数为经过 sqlite3_open 函数返回的指向数据库的指针。
  2. 第二个参数为拼接的 sql 语句（sql statement）

接下来依次经过了 `sqlite3_prepare 、sqlite3_column_count、sqlite3_setp`

  * 参考上面的资料，这几个函数的作用依次为：

  1. 初始化数据库的连接，将结果的对象指针存储到 &stmt 中
  2. sqlite3_column_count 顾名思义返回查询的表中的列数
  3. sqlite3_setp 函数将 stmt 指针作为参数执行 sql 语句

接下来的一些操作就是返回执行的结果，对 sqlite3 数据库查询感兴趣的可以自行去了解下。

## 总结：

综上，这里主要是没有对用户的输入进行过滤，直接将拼接完的 sql 语句带到 exec_sql 函数中，并执行 sqlite3 的查询语句，造成注入。

## 参考资料：

<https://www.cnblogs.com/zfyouxi/p/5258589.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **H4lo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/183871](/post/id/183871)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [IoT](/tag/IoT)
  * [路由器](/tag/路由器)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t0129eee7c67478558f.jpg) H4lo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

