# Apache安全——挂钩分析

阅读量 **496867**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-05 10:30:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01fa0544b9500773ac.jpg)

Apache
是一个被广泛使用的web服务器，这段时间爆出了很多关于Apache挂钩模块的漏洞，比如CVE-2021-40438、CVE-2021-22986等等，为了更好的理解漏洞挖掘的原理以及梳理知识体系，本文从Apache挂钩模块的角度分析Apache安全。笔者将从什么是挂钩、调试环境搭建、挂钩操作流程、自己编写挂钩等多个角度给大家无死角的介绍隐藏在挂钩中的安全问题。

## 0x01 挂钩简介

###  0x1 简介

为了让Apache
2.0版本能够更模块化，更具拓展性，Apache采取了更加灵活的处理策略—“模块自行管理”策略，即挂钩（Hooks）的概念。Hooks的使用将函数从静态变为动态，模块编写者可以通过Hooks自行增加处理句柄，而不需要所有的模块都千篇一律。因此，每次增加新函数时，唯一修改的就是函数所在的模块而已。  
​

想必大家已经对Apache挂钩有了基本的认识，本文主要记录在学习挂钩过程中思考总结的东西。打算从apache默认挂钩开始分析，比如Basic认证模块，通过分析标准挂钩的声明、注册、使用，打造属于自己的挂钩已经挂钩处理函数，下面开始进入正题。

###  0x2 环境搭建

docker 调试环境

    
    
    docker run -it 8237:80 turkeys/apache:2.4.41 bash
    

源码安装可参考
<https://www.yuque.com/docs/share/771a78c6-7fca-44c7-9cb3-6d1fb3594921?#>
《Apache 源码编译及调试》

## 0x02 挂钩名词梳理

我们以Aapche内部挂钩为例详细分析整个Apache挂钩操作过程中的操作细节。
**因为Apache挂钩知识点比较多，为了方便理解，从宏观角度首先给大家引入几个概念，以及梳理其中的关系** 。主要涉及到了以下几个名词和几个动词  
n:

  * 挂钩
  * 挂钩数组
  * 挂钩结构
  * 挂钩注册函数
  * 挂钩处理函数

v:

  * 声明挂钩
  * 声明挂钩数组
  * 声明挂钩结构
  * 注册挂钩处理函数
  * 注册挂钩函数

猛的一看这些名词及其相似，但细细品味还是有很多不同的，我们暂且把其关系用下图表示：

1.挂钩的名字需要在 **声明挂钩** 中指定，同时在声明挂钩的过程中定义了很多挂钩信息  
2.每个挂钩有一个 **数组结构** 用来保存该挂钩信息  
3.利用 **挂钩结构** 保存 **挂钩数组**  
4.每个挂钩需要利用 **挂钩注册函数** 去单独注册  
5.在 **声明挂钩** 的同时会产生 **注册挂钩处理函数的函数、挂钩执行函数、获取挂钩函数的函数**  
6. **挂钩处理函数** 需要 **注册挂钩处理函数的函数** 才能注册到对应的 **挂钩数组** 中

![](https://p2.ssl.qhimg.com/t013f00561e3785da1d.png)

可能看着上面的流程图也会感觉到懵逼，不过没关系我们具体结合着Apache源码，一起品尝其中的知识盛宴。

## 0x03 挂钩操作流程

在一个挂钩的生命周期中要经历以下过程：

1.声明挂钩  
2.声明挂钩数组  
3.声明挂钩结构  
4.声明挂钩函数调用类型  
5.编写挂钩函数  
6.注册挂钩函数

这个过程有线性调用也有回调函数，我们由浅入深具体分析下整个挂钩操作流程。

###  0x1 声明挂钩

声明一个挂钩的结构类型，用来保存挂钩的相关定义。Apache中关于挂钩的实现大部分通过宏来完成，先看下怎么去声明一个挂钩

![](https://p2.ssl.qhimg.com/t01381faf03a5213a0f.png)

    
    
    AP_DECLARE_HOOK(int,check_user_id,(request_rec *r))
    

* * *

对应的宏定义在ap_hooks.h文件中体现，发现它是由 APR_DECLARE_EXTERNAL_HOOK 宏实现的，再次寻找调用。

![](https://p1.ssl.qhimg.com/t013e29efcaead1685a.png)

    
    
    /**
     * Declare a hook function
     * @param ret The return type of the hook
     * @param name The hook's name (as a literal)
     * @param args The arguments the hook function takes, in brackets.
     */
    #define AP_DECLARE_HOOK(ret,name,args) \
            APR_DECLARE_EXTERNAL_HOOK(ap,AP,ret,name,args)
    

* * *

APR_DECLARE_EXTERNAL_HOOK 宏定义如下，这个是Hook声明的核心处理代码

![](https://p3.ssl.qhimg.com/t011eb5bd72e80b44be.png)

我们来捋一捋其中都干了什么事，关于宏定义的分析需要点前置知识。

1.##宏主要用来连接它两边的字符串，形成一个新的字符串  
2.typedef 为类型取一个新的名字，但仅限于为类型定义符号名称，由编译器执行解释  
3.#define 给类型和数值起别名，由与编译器进行处理

首先对这段代码进行编译处理

![](https://p3.ssl.qhimg.com/t014a5c94f02dbcc373.png)

通过上述代码可以看出该代码的五个功能

**1\. 定义挂钩执行函数原型**

ap_HOOK_check_user_id_t 为挂钩在实际调用过程中的处理函数，我们所有的注册的函数都将会通过这个函数执行。

**2\. 定义挂钩注册函数原型**

如图中的ap_hook_check_user_id

    
    
    AP_DECLARE(void) ap_hook_check_user_id(ap_HOOK_check_user_id_t *pf,
                                          const char * const *aszPre, 
                                          const char * const *aszSucc, int nOrder);
    

简单解释下他的几个参数的含义：

  * ap_HOOK_check_user_id_t 为执行函数原型，为挂钩内部函数，最终会加入到在处理请求期间的指定调用列表中。
  * aszPre规定必须在这个函数之前调用的函数模块
  * aszSucc规定必须在这个函数之后调用的函数模块
  * nOrder 挂钩的综合排序参数，如果这个数值越低，那么这个挂钩函数在列表中排列将越靠前，因此也越早被调用。其定义如下图所示

![](https://p0.ssl.qhimg.com/t01482734fd62a0b9fc.png)

**3\. 声明挂钩调用函数**

    
    
    AP_DECLARE(int) ap_run_check_user_id args;
    

在声明这些挂钩后就要调用挂钩函数了，不同的挂钩函数对应的调用函数不同不过都长 **ap_run_xxx ，**
这写个挂钩调用函数会在request.c里调用

![](https://p3.ssl.qhimg.com/t01d048c9adff855cce.png)

**4\. 获取挂钩定义函数**

宏定义展开后如下图所示，生成挂钩访问函数原型，在模块外部可以调用该函数获得注册为该挂钩的所有函数。

![](https://p2.ssl.qhimg.com/t01992126b60d8fdb62.png)

**5\. 定义挂钩信息保存结构**

    
    
    typedef struct ap_LINK_check_user_id_t 
        { 
        ap_HOOK_check_user_id_t *pFunc; 
        const char *szName; 
        const char * const *aszPredecessors; 
        const char * const *aszSuccessors; 
        int nOrder; 
        } ap_LINK_check_user_id_t;
    

该宏定义了一个结构类型，用来保存挂钩的相关定义信息。由于同一个挂钩会有多个模块对其感兴趣并实现该挂钩，同一个挂钩所有的实现都保存在一个链表中，链表中的每一个元素都是
**ap_LINK_check_user_id_t** 结构

###  0x2 声明挂钩数组

对于同一挂钩，不同模块对应于它的处理函数各不相同，为了能够保存各个模块对同一挂钩的使用信息，Apache使用 **apr_array_header_t**
数组进行保存，该数组通过宏APR_HOOK_LINK声明，在request.c中的声明方式

![](https://p3.ssl.qhimg.com/t019efd6bafeb1b4ea0.png)

其宏定义如下，很简单针对每个挂钩声明了一个 **apr_array_header_t** 数组

    
    
    /** macro to link the hook structure */
    #define APR_HOOK_LINK(name) \
        apr_array_header_t *link_##name;
    

关于挂钩的大部分信息都由下面这个结构提供，这里就不展开讲了，我们只需要知道 apr_array_header_t 里面实现了动态数组结构，可以动态的插入查询
**ap_LINK_xxxx** 结构。

###  0x3 声明挂钩结构

为什么设计挂钩结构，主要是因为在Apache2.0中并不支持直接访问挂钩数组，目前的操作是将所有的数组通过宏定义实现一个统一的结构体。

![](https://p5.ssl.qhimg.com/t01ef9ba60e9be279a9.png)

![](https://p3.ssl.qhimg.com/t013bcb5229287c3747.png)

    
    
    ARP_HOOK_STRUCT()
    

该宏展开后实际上定义了一个限于模块内部的_hooks结构，该模块内所实现的所有挂钩的对应数组都保存为_hooks的成员。Apache
对挂钩数组的访问都要通过_hooks来实现。

###  0x4 注册挂钩函数

挂钩数组、挂钩结构声明过后，需要使用 AP _IMPLEMENT_HOOK_RUN_ (FIRST|ALL)
创建挂钩数组，并通过APR_IMPLEMENT_EXTERNAL_HOOK_BASE 宏实现了我们所需要的挂钩注册函数及挂钩信息获取函数。使用方法如下：

    
    
    AP_IMPLEMENT_HOOK_RUN_FIRST(int,check_user_id,(request_rec *r), (r), DECLINED)
    AP_IMPLEMENT_HOOK_RUN_ALL(int,fixups,(request_rec *r), (r), OK, DECLINED)
    

以 AP_IMPLEMENT_HOOK_RUN_ALL 为例进行分析，最终会在 APR_IMPLEMENT_EXTERNAL_HOOK_BASE
中实现核心功能。从宏定义中可以看出它实现了 **ap_hook_xxxx** 和 **ap_run_xxxx** 两个函数。

![](https://p0.ssl.qhimg.com/t0195dcb4425db4a6b7.png)

核心功能是使用apr_array_make创建每个挂钩对应的apr_array_header_t数组，并通过apr_array_push函数向_hooks结构体添加元素。

PS:  
RUN_FIRST：被调用的 hook函数的返回值为 OK 或者是DECLINE时，后面的hook是不被执行的。  
RUN_ALL：被调用的 hook函数的返回值不为 DECLINE时，已经加载的hook将被全部执行。

![](https://p1.ssl.qhimg.com/t011d0cf5b8ce2362e7.png)

###  0x5 编写挂钩处理函数

关于挂钩的声明和注册操作到这里就接近尾声了，下面就是如何使用挂钩的相关操作，步骤如下

  * 编写挂钩处理函数
  * 通过register_hooks 注册函数
  * 添加 AP_DECLARE_MODULE

    
    
    static void some_hook(request_rec *r){
        ap_rputs("some hook");
        return;
    }
    
    static void register_hooks(apr_pool_t *p)
    {
        ap_hook_check_authn(some_hook, NULL, NULL, APR_HOOK_MIDDLE,
                            AP_AUTH_INTERNAL_PER_CONF);
        ap_hook_fixups(authenticate_basic_fake, NULL, NULL, APR_HOOK_LAST);
        ap_hook_note_auth_failure(hook_note_basic_auth_failure, NULL, NULL,
                                  APR_HOOK_MIDDLE);
    }
    
    AP_DECLARE_MODULE(auth_basic) =
    {
        STANDARD20_MODULE_STUFF,
        create_auth_basic_dir_config,  /* dir config creater */
        merge_auth_basic_dir_config,   /* dir merger --- default is to override */
        NULL,                          /* server config */
        NULL,                          /* merge server config */
        auth_basic_cmds,               /* command apr_table_t */
        register_hooks                 /* register hooks */
    };
    

​  
查遍APACHE的所有文件，也不能找到ap_hook_header_parser和ap_hook_post_read_request等函数声明和实现，这是因为挂钩注册函数是通过宏AP_IMPLEMENT_HOOK_VOID/AP_IMPLEMENT_HOOK_RUN_ALL/AP_IMPLEMENT_HOOK_RUN_FIRST来实现的。

###  0x6 小结

通过对挂钩操作流程的了解，想必大家都想整出来个自己的hook链，为了增强动手实践能力，在接下来的两节内容里带着大家编写自己的挂钩处理函数以及一起调试Basic挂钩处理函数的相关流程。

## 0x04 编写自己的挂钩

    
    
    # 下载http源码
    wget http://archive.apache.org/dist/httpd/httpd-2.4.41.tar.gz
    

### **1\. 声明挂钩**

在http_request.h中声明自己设计的挂钩

    
    
    AP_DECLARE_HOOK(int,monkey_boy,(request_rec *r))
    

![](https://p4.ssl.qhimg.com/t013e56846ce7908806.png)

###  2\. 声明挂钩数组和结构

在request.c 中进行声明

    
    
    APR_HOOK_LINK(monkey_boy)
    

![](https://p1.ssl.qhimg.com/t014b6a900542d533b3.png)

###  3\. 注册挂钩

在request.c 中注册挂钩

    
    
    AP_IMPLEMENT_HOOK_RUN_FIRST(int,monkey_boy,
                                (request_rec *r), (r), DECLINED)
    

![](https://p0.ssl.qhimg.com/t01990254da2bd76d39.png)

###  4\. 编写挂钩处理函数

在mod_auth_basic.c模块中的register_hooks函数中添加

    
    
    ap_hook_monkey_boy(monkey_boy_founction,NULL, NULL, APR_HOOK_MIDDLE);
    

![](https://p3.ssl.qhimg.com/t010d628a25c8d9ab01.png)

###  5\. 注册挂钩处理函数

    
    
    static void monkey_boy_founction(request_rec *r){
        ap_rputs("Hello Monkey!!",r);
        return;
    }
    

![](https://p4.ssl.qhimg.com/t0153bd7eb2183126de.png)

后续直接进行编译即可使用

###  6\. 编译使用

>
> 使用apache扩展工具apxs可以为apache编译和安装扩展模块。新安装的模块将作为动态共享对象提供给apache，因此，apache运行的平台必须支持DSO特性，并且httpd必须内建mod_so模块。这样才能使用mod_so提供的LoadModule指令在运行时将模块加载到apache服务器中。

主要介绍为已运行的apache添加mod_proxy模块，先定位到apache源码中modules/proxy目录。然后使用apxs进行编译安装，编译指令为

    
    
    /usr/local/apache2/bin/apxs -i -c -a  mod_proxy.c proxy_util.c
    #-c表示进行编译
    #-i表示将生成的模块安装到apache的modules目录下
    #-a选项在httpd.conf中增加一条LoadModule指令以载入刚安装的模块，或者如果此指令已存在，则启用之
    #-n选项显式地指定模块名称
    

模块查询指令

    
    
    #查看apache支持的模块：
    httpd -l
    #查看apache载入的模块：
    httpd -t -D DUMP_MODULES
    

安装成功以后将在apache的modules目录下生成mod_proxy.so文件，并且在httpd.conf中加入了一行

    
    
    LoadModule proxy_module modules/mod_proxy.so
    

proxy只是核心模块，具体使用时还需要其它模块的支持，安装方法类似。

    
    
    /usr/local/apache2/bin/apxs -i -c -a mod_proxy_http.c
    /usr/local/apache2/bin/apxs -i -c -a mod_proxy_ftp.c
    /usr/local/apache2/bin/apxs -i -c -a mod_proxy_connect.c
    

同样，安装后在apache的modules目录中生成了mod_proxy_http.so, mod_proxy_ftp.so,
mod_proxy_connect.so文件。并且在httpd.conf中添加了如下行：

    
    
    LoadModule proxy_http_module  modules/mod_proxy_http.so
    LoadModule proxy_ftp_module   modules/mod_proxy_ftp.so
    LoadModule proxy_connect_module modules/mod_proxy_connect.so
    

这样，mod_proxy模块就安装好了，进行具体的应用配置，重启apache就可以了。

## 0x05 调试Basic挂钩处理函数

为了更好的理解钩子以及钩子处理函数在Apache运行过程的影响，打算调试下Basic挂钩处理函数在Apache程序中扮演的角色。

我们在mod_auth_basic.c 中注册了自己的hook处理函数，从Apache的Hook 执行函数作为调试的起点

###  0x1 调试准备工作

在调试机上安装了gdb、pwndbg等调试工具，查看httpd进程pid号（因为负载均衡的原因会有多个子进程），选择其中一个子进程进行attach

![](https://p0.ssl.qhimg.com/t01a3f60a77d2021e8a.png)

    
    
    gdb --pid 84370
    

因为在编译过程中添加了-g选项，所以可以对Apache及其模块进行源码调试。

###  0x2 调试hook执行函数

在Apache中hook执行函数在ap_process_request_internal函数中被调用，为了处理自己的钩子函数，我们在代码的开始部分添加自己的hook执行函数，如下图所示  
​  

在第296行，ap_run_check_user_id中进行了basic校验，结合basic的注册函数可能很多人产生了疑问，命名注册的是ap_hook_check_authn
为什么在执行的时候跑到了ap_run_check_user_id链中。

![](https://p3.ssl.qhimg.com/t01ac4b75d08860357d.png)

这是因为在ap_hook_check_authn 函数实现中调用了ap_hook_check_user_id 注册函数

![](https://p1.ssl.qhimg.com/t015f794d3bf6126c8b.png)

* * *

在gdb调试过程中有个比较有意思的现象，ap_run_check_user_id 找不到函数定义，在调试时一直显示下面状态

![](https://p5.ssl.qhimg.com/t01c95da0ae1568adc3.png)

通过汇编代码可以看出其调用逻辑，其实这个就是在挂钩声明时声明的挂钩执行函数，他的方法实现是在挂钩注册函数中进行的

![](https://p0.ssl.qhimg.com/t0167a5a88f67167285.png)

call qword ptr [rbx] 在动态调用链式函数地址，当前函数地址是 authenticate_basic_user
正好是Basic处理函数，其实这里可以通过ida查看 ap_run_check_user_id 函数反编译代码来进行分析

![](https://p0.ssl.qhimg.com/t014e7d72d2c73fc05d.png)

从ap_process_request_internal函数出来后的相关逻辑，因为access_status
返回值为-1所以没有执行ap_invoke_handler函数，从而报了401 Unauthorized 的错误

​

## 0x06 总结

通过阅读Apache源码的方式解决了一开始的很多疑问，在最后的总结部分我也打算换种方式去做，把我之前存在的问题和分析过源码后获得到的答案以问答的方式总结出来。

###  0x1 能否简单描述挂钩是如何构造的？

在Apache中构造个挂钩要经历， **声明** 、 **注册** 两个大阶段，声明主要是定义一些挂钩 **变量** 和 **函数，**
而注册可以理解为声明阶段注册的 **变量** 和 **函数** 进行 **赋值** 和 **实现** ，那么整体来讲声明和注册函数分为以下几种

**1\. 声明阶段**

宏定义

    
    
    AP_DECLARE_HOOK  //声明挂钩
    APR_HOOK_LINK    //声明挂钩数组
    ARP_HOOK_STRUCT  //声明挂钩结构
    

声明的变量和函数

    
    
    ap_hook_xxxx
    ap_run_xxxx
    ap_LINK_xxxx
    

**​2\. 注册阶段**

宏定义

    
    
    AP_IMPLEMENT_HOOK_RUN_(FIRST|ALL) //注册挂钩
    

### ​0x2 能否简单描述挂钩是如何使用的？

关于挂钩的使用就相对来说比较简单了，在 **声明** 和 **注册** 阶段之后预留了两个主要的功能函数 **ap_hook_xxxx** 和
**ap_run_xxxx，** 一个负责注册一个负责使用  
​  
在模块注册钩子的时候使用的ap_hook_xxxx函数

![](https://p3.ssl.qhimg.com/t01ce55ba1813df3e30.png)

在request.c 中有调用钩子的执行函数

![](https://p4.ssl.qhimg.com/t01a64ca480b374033f.png)

###  0x3 从逆向分析的角度讲，哪些方面更容易存在问题？

我们关注的是request.c
主程序的调用逻辑以及每个钩子的注册类型，重点关注在钩子处理函数中的代码逻辑，并综合判断它在主程序中对整个钩子执行链的影响，关于这一点可以参考对于CVE-2021-22986
漏洞的分析。其次本文也为分析Apache httpd mod_proxy SSRF漏洞CVE-2021-40438做了铺垫。下篇文章将详细分析httpd
mod_proxy中出现的漏洞。

## 参考文献

<https://wenku.baidu.com/view/2bfc9c07a6c30c2259019ee2.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/257539](/post/id/257539)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Apache](/tag/Apache)
  * [钩子](/tag/钩子)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

