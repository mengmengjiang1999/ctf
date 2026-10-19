# CVE-2018-0296 Cisco ASA 拒绝服务漏洞分析

阅读量 **443747**

发布时间 : 2019-02-27 15:00:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0167804a26ab415dad.jpg)

作者：陈千

## 漏洞简介

CVE-2018-0296是思科ASA设备Web服务中存在的一个拒绝服务漏洞，远程未认证的攻击者利用该漏洞可造成设备崩溃重启。该漏洞最初由来自Securitum的安全研究人员Michal
Bentkowski发现，其在[博客](https://sekurak.pl/opis-bledu-cve-2018-0296-ominiecie-uwierzytelnienia-w-webinterfejsie-cisco-asa/)中提到该漏洞最初是一个认证绕过漏洞，上报给思科后，最终被归类为拒绝服务漏洞。据思科发布的[安全公告](https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180606-asaftd)显示：针对部分型号的设备，该漏洞可造成设备崩溃重启；而针对其他型号的设备，利用该漏洞可获取设备的敏感信息，造成信息泄露。

针对该漏洞，目前已有公开的PoC脚本，可用于获取设备的敏感信息如用户名，或造成设备崩溃重启。经过实际测试，在公开PoC中造成该漏洞的关键url如下。

https://<ip>:<port>/+CSCOU+/../+CSCOE+/files/file_list.json?path=/

下面利用思科ASA设备和已有的PoC脚本，对该漏洞的形成原因进行分析。

## 背景知识

在实际对漏洞进行分析的过程中，发现思科ASA设备的lina程序中，存在大量的Lua脚本以及对Lua
api的调用。为了便于理解，下面对Lua脚本的相关知识进行简单介绍。

###  Lua脚本和C/C++交互

Lua是一个小巧的脚本语言，其设计目的是为了嵌入应用程序中，从而为应用程序提供灵活的扩展和定制功能。Lua脚本可以很容易被C/C++代码调用，也可以反过来调用C/C++的函数，这使得Lua在应用程序中可以被广泛使用。不仅可作为扩展脚本，也可以作为普通的配置文件，代替XML、ini等文件格式，并且更容易理解和维护。

Lua和C/C++通信的主要方式是一个虚拟栈，其特点是后进先出。在Lua中，Lua栈就是一个struct，栈的索引可以是正数也可以是负数，其中正数索引1永远表示栈底，负数索引-1永远表示栈顶，如下图所示。

![](https://p0.ssl.qhimg.com/t01e9f1507a9beeb964.png)

Lua中的栈在stack_init()函数中创建，其类似于下面的定义。

    
    
    TObject stack[BASIC_STACK_SIZE + EXTRA_STACK]

在Lua中，可以往栈上压入字符串、数值、表和闭包等类型，最后统一用Tobject这种数据结构进行保存，如下。TObject结构对应于Lua中所有的数据类型，是一个{值，类型}结构，它将值和类型绑在一起。其中用tt表示value的类型，value是一个联合体，共有4个域，说明如下。

  * p：可以保存一个指针，实际上指向Lua中的light userdata结构
  * n：保存数值，包括int、float等类型
  * b：保存布尔值
  * gc：保存需要内存管理垃圾回收的类型如string、table、closure等

![](https://p4.ssl.qhimg.com/t011f13835cd9527529.png)

    
    
    // lua 数据类型
    #define LUA_TNONE        (-1)
    
    #define LUA_TNIL         0   // 空值
    #define LUA_TBOOLEAN     1
    #define LUA_TLIGHTUSERDATA  2
    #define LUA_TNUMBER         3
    #define LUA_TSTRING         4
    #define LUA_TTABLE          5
    #define LUA_TFUNCTION       6
    #define LUA_TUSERDATA       7
    #define LUA_TTHREAD         8

###  Lua 栈操作常用api

Lua中提供了一系列与栈操作相关的api，常用的api如下。

    
    
    // 压入元素
    void lua_pushnil (lua_State *L);
    void lua_pushboolean (lua_State *L, int bool);
    void lua_pushnumber (lua_State *L, double n);
    void lua_pushlstring (lua_State *L, const char *s, size_t length);
    void lua_pushstring (lua_State *L, const char *s);
    
    // 检查一个元素是否是一个指定的类型
    int lua_is* (lua_State *L, int index); // *可以是任何类型
    
    // 获取元素
    int           lua_toboolean (lua_State *L, int index);
    double        lua_tonumber (lua_State *L, int index);
    const char *  lua_tostring (lua_State *L, int index);
    size_t        lua_strlen (lua_State *L, int index);

## 环境准备

###  调试环境搭建

由于该漏洞在不同型号设备上表现的行为不一致，这里分别选取了32位的设备和64位的设备，相关信息如下。其中，前面2个设备用于漏洞分析，设备asav9101用于补丁分析。

  * 真实设备ASA 5505，镜像为asa924-k8.bin ，32bit
  * GNS3仿真设备，镜像为asav962.qcow2，64bit
  * GNS3仿真设备，镜像为asav9101.qcow2，64bit

ASA设备中内置了gdbsever，但默认不启动。为了对设备进行调试，需要修改镜像文件以启动gdbserver。同时，由于ASA设备会对镜像文件进行完整性校验，所以修改后的镜像文件无法直接通过tftp或ASDM工具传入设备。ASA使用CF卡作为存储设备，可以通过用CF卡读卡器直接将镜像写入CF卡中的方式绕过校验，因为ASA没有对CF中的镜像进行校验。

详细的调试环境搭建和镜像修改等内容可以参考nccgroup的系列[博客](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/september/cisco-asa-series-part-one-intro-to-the-cisco-asa/).

###  设备配置

思科ASA设备会在443端口提供Web服务。笔者在进行测试时，对设备的WebVPN功能(Clientless SSL
VPN)进行了配置，使得可以访问Web服务，进而触发该漏洞。详细的配置操作可参考思科[相关文档](https://www.cisco.com/c/en/us/support/docs/security-vpn/webvpn-ssl-vpn/119417-config-asa-00.html)。

## 漏洞分析

环境搭建好后，运行已有的PoC脚本，针对asa924设备，会造成敏感信息泄露，而针对asav962设备，会造成设备崩溃重启。下面基于asav962设备，重点对拒绝服务漏洞进行分析。

###  崩溃分析

运行PoC脚本，在gdb中捕获到如下错误。可以看到，崩溃点在libc.so.6库中的strlen()函数里，由于在0x7ffff497699a处尝试访问一个非法的内存地址0x13，故产生Segmentation
fault错误，而rax的值来源于strlen()函数的参数。

    
    
    Thread 2 received signal SIGSEGV, Segmentation fault.
    [Switching to Thread 1677]
    0x00007ffff497699a in strlen () from ***/_asav962.qcow2.extracted/rootfs/lib64/libc.so.6
    (gdb) x/10i $rip
    => 0x7ffff497699a <strlen+42>:  movdqu xmm12,XMMWORD PTR [rax]
       0x7ffff497699f <strlen+47>:  pcmpeqb xmm12,xmm8
       0x7ffff49769a4 <strlen+52>:  pmovmskb edx,xmm12
       0x7ffff49769a9 <strlen+57>:  test   edx,edx
       0x7ffff49769ab <strlen+59>:  je     0x7ffff49769b1 <strlen+65>
       0x7ffff49769ad <strlen+61>:  bsf    eax,edx
       0x7ffff49769b0 <strlen+64>:  ret
       0x7ffff49769b1 <strlen+65>:  and    rax,0xfffffffffffffff0
       0x7ffff49769b5 <strlen+69>:  pcmpeqb xmm9,XMMWORD PTR [rax+0x10]
       0x7ffff49769bb <strlen+75>:  pcmpeqb xmm10,XMMWORD PTR [rax+0x20]
    (gdb) i r $rax
    rax            0x13     19
    (gdb) bt
    #0  0x00007ffff497699a in strlen () from ***/_asav962.qcow2.extracted/rootfs/lib64/libc.so.6
    #1  0x0000555557ee51ce in lua_pushstring ()
    #2  0x00005555583c87d2 in webvpn_file_name ()
    #3  0x0000555557eec43b in luaD_precall ()
    #4  0x0000555557efc258 in luaV_execute ()
    #5  0x0000555557eeced0 in luaD_call ()
    #6  0x0000555557eebeda in luaD_rawrunprotected ()
    #7  0x0000555557eed323 in luaD_pcall ()
    #8  0x0000555557ee5de6 in lua_pcall ()
    #9  0x0000555557f00821 in lua_dofile ()
    #10 0x000055555822053b in aware_run_lua_script_ns ()
    #11 0x0000555557dc6e3d in ak47_new_stack_call ()
    Backtrace stopped: previous frame inner to this frame (corrupt stack?)

根据栈回溯信息，查看函数lua_pushstring()和webvpn_file_name()，其部分伪代码片段如下。在函数webvpn_file_name()中，将v1
+
0x13这个指针作为参数传递给lua_pushstring()，最终传递给strlen()函数。崩溃点处访问的非法内存地址为0x13，说明v1=0，即在webvpn_file_name()中lua_touserdata()返回值为NULL(也就是0)。

    
    
    _DWORD *__fastcall lua_pushstring(__int64 a1, const char *a2)
    {
      size_t v2; // r14
      __int64 v3; // r13
      _DWORD *result; // rax
    
      if ( a2 )
      {
        v2 = _wrap_strlen(a2);
        // ...
    }
    
    signed __int64 __fastcall webvpn_file_name(_QWORD *a1)
    {
      signed __int64 v1; // rax
    
      v1 = lua_touserdata(a1, 1);
      lua_pushstring((__int64)a1, (const char *)(v1 + 0x13));
      return 1LL;
    }

由前面lua的相关知识可知，函数lua_touserdata()用于获取栈底数据。因此，很自然的想法就是分析这个NULL值是从哪里来的，即在什么地方通过调用lua_pushnil()往栈上压入了NULL值。

###  静态分析

通过查找字符串/+CSCOE+/files/file_list.json的交叉引用定位到aware_webvpn_content()函数。在该函数中可以看到有很多请求url的字符串，同时还包含很多lua脚本的名称，猜测该函数应该是负责对这些请求进行处理，根据不同的请求url执行对应的lua脚本。示例如下。

![](https://p2.ssl.qhimg.com/t01ac6d4e4366a0b5e1.png)

查看files_list_json_lua脚本的内容，其主要功能是列出当前路径下的目录或文件，依次调用了Lua中的OPEN_DIR()、READ_DIR()、FILE_NAME()、FILE_IS_DIR()等函数。而在aware_addlib_netfs()函数中，建立了Lua函数和C函数之间的对应关系，示例如下。

![](https://p1.ssl.qhimg.com/t01083a6dddbd09827f.png)

    
    
    // Lua函数与C函数对应关系
    OPEN_DIR()    <--->      webvpn_open_dir()
    READ_DIR()    <--->      webvpn_read_dir()
    FILE_NAME()       <--->      webvpn_file_name()
    FILE_IS_DIR() <--->      webvpn_file_is_dir()

在查看对应的C函数时，在webvpn_read_dir()函数中，有一个对lua_pushnil()函数的调用。根据函数的调用顺序，猜测webvpn_file_name()函数中获取到的NULL值来自于这里。

![](https://p5.ssl.qhimg.com/t01be1b0d57cf6c146c.png)

###  动态分析

根据之前的猜测，尝试在调用lua_pushnil()处下断点，然后查看Lua栈上的数据，如下。

![](https://p0.ssl.qhimg.com/t017ccbe28a5055f840.png)

其中，rdi指向的数据结构的定义大致如下，这里主要关注其中的lua_stack_top_ptr和lua_stack_base_ptr两个指针，分别指向Lua栈的栈顶和栈底，栈中的元素就是前面提到的{类型，值}结构。

    
    
    struct {
        uint64 xxx;
        uint64 xxx;   
        uint64 lua_stack_top_ptr;    // 指向栈顶   (空栈，即始终指向刚入栈元素的下一个位置)
        uint64 lua_stack_base_ptr;   // 指向栈底   (栈地址由低向高增长)
        uint64 xxx;
        uint64 xxx;
        uint64 xxx;
        uint64 xxx;
        ... 
    }

之后在webvpn_file_name()中调用lua_touserdata()函数前下断点，查看此时Lua栈上的内容，如下。此时，lua_touserdata()函数的第2个参数为1，即获取Lua栈底的数据，而此时栈底的数据为NULL。

![](https://p2.ssl.qhimg.com/t01bf944f1c0bf8f5a5.png)

继续单步执行程序，查看函数lua_touserdata()的返回值。可以看到，其返回值确实为NULL，之后将一个非法内存地址0x13作为参数传入了lua_pushstring()，最终导致Segmentation
fault错误。

![](https://p5.ssl.qhimg.com/t01f3626a3c65e18049.png)

但是，这里的NULL值并不是来自之前lua_pushnil()压入的nil值，而是位于其下面的栈元素。在下断点调试的过程中，发现设置的2个断点均只命中一次就触发了问题，极大地缩小了调试的范围。同时，在2个断点处Lua栈的地址是一样的，因此可以在第1个断点命中后，对相应的Lua栈地址设置硬件断点，看在哪个地方对其值进行了修改。

在gdb中设置硬件断点后，继续执行时提示如下错误。网上查找相应的解决方案，建议使用set can-use-hw-watchpoints
0，但实际测试时貌似也存在问题。最后采用hook-stop的方式来观察指定地址处的内容。

![](https://p5.ssl.qhimg.com/t01746457d4280eeaf3.png)

    
    
    define hook-stop
        x/2gx <addr>
    end

通过设置断点并查看相应地址处的内容，最终定位到修改内容的地方位于luaV_execute()中。对照lua-5.0源码，luaV_execute()函数是Lua
VM执行字节码的入口，修改内容的地方位于OP_GETGLOBAL操作码的处理流程中。

![](https://p5.ssl.qhimg.com/t0134bf51616da953d2.png)

###  asav962与asa924执行流程对比

前面的分析定位到了luaV_execute()函数中，而该函数属于Lua
VM的一部分，难道是因为files_list_json_lua脚本存在问题，而导致Lua
VM执行字节码时出现错误？由于该拒绝服务漏洞对型号为asa924的设备没有影响，下面对asa924设备上对应的执行流程进行分析。

根据前面的分析思路，在webvpn_file_name()中设置断点，发现其流程与asav962类似，lua_touserdata()函数的返回值同样会为NULL，而asa924设备却不会发生崩溃。2个webvpn_file_name()的对比如下。

![](https://p5.ssl.qhimg.com/t0120b9b062d8dc6f72.png)

通过调试可知，针对32位程序(asa924)，lua_touserdata()函数的返回值为指向字符串的指针。当该指针为空时，其直接作为参数传入lua_pushstring()，而在lua_pushstring()中会对参数是否为空进行判断。而针对64位程序(asav962)，lua_touserdata()函数的返回值为指向某个结构体的指针。当该指针为空时，传入lua_pushstring()的参数为0x13，从而”绕过“了lua_pushstring()中的校验，最终造成非法内存地址访问。

至此，分析清楚了该拒绝服务漏洞产生的原因，主要是由于32位程序和64位程序中lua_touserdata()函数的返回值代表的结构不一致造成的。

## 补丁分析

在镜像asav9101.qcow2中该漏洞被修复了。基于前面对漏洞形成原因的分析，下面以asav9101.qcow2镜像为例，对漏洞的修复情况进行简单分析。

###  目录遍历漏洞补丁分析

通过动态调试分析，对请求url的解析在UrlSniff_cb()函数中完成，其中增加了对./和../的处理逻辑，部分代码如下。

    
    
    v16 = *v5;    // v5 指向请求url
    v17 = v5;
    v18 = v5;
    LABEL_45:
    while ( v16 )
    {
    if ( v16 == '.' )
    {
        v20 = v18[1];
        switch ( v20 )
        {
        case '.':
            v9 = (unsigned __int8)v18[2];
            if ( !(_BYTE)v9 )
            goto LABEL_75;
            if ( (_BYTE)v9 == '/' )
            {
            v20 = v18[3]; // 匹配到"../"
            v18 += 2;
    LABEL_75:
            ++v18;
            v16 = v20;
            goto LABEL_45;
            }
            break;
        case '/':
            v16 = v18[2]; // 匹配到"./"
            v18 += 2;
            goto LABEL_45;
        case '\0':
            ++v18;
            goto LABEL_60;
        }
        do
        {
    LABEL_48:

###  拒绝服务漏洞补丁分析

根据前面的分析可知，拒绝服务漏洞的触发位置在函数webvpn_file_name()中。在镜像asav9101.qcow2中，该函数内容如下，可以看到并没有对该函数进行更改。

    
    
    webvpn_file_name proc near
    ; __unwind {
    push    rbp
    mov     esi, 1
    mov     rbp, rsp
    push    rbx
    mov     rbx, rdi
    sub     rsp, 8
    call    lua_touserdata
    mov     rdi, rbx
    lea     rsi, [rax+13h]
    call    lua_pushstring
    add     rsp, 8
    mov     eax, 1
    pop     rbx
    pop     rbp
    retn
    ; }

在字符串列表中查找/+CSCOE+/files/file_list.json显示没有结果，表明在该镜像中将这个接口去掉了。同时根据之前files_list_json_lua脚本的内容进行查找，在该镜像中仍然可以找到对应的lua脚本内容，但是找不到对该脚本的交叉引用，进一步证实该接口/+CSCOE+/files/file_list.json被去掉了。

## 小结

  * 利用CVE-2018-0296漏洞，远程未认证的攻击者可以对目标设备实施拒绝服务攻击，或从设备获取敏感信息。
  * 拒绝服务漏洞的形成原因是由于32位程序和64位程序中lua_touserdata()函数的返回值代表的结构不一致造成。
  * 在镜像asav9101.qcow2中已经修复了该漏洞，其中拒绝服务漏洞的修复方式是去掉了触发了该漏洞的请求url接口。

## 相关链接

  * [Cisco Adaptive Security Appliance Web Services Denial of Service Vulnerability](https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180606-asaftd)
  * [Error description CVE-2018-0296 – bypassing authentication in the Cisco ASA web interface](https://sekurak.pl/opis-bledu-cve-2018-0296-ominiecie-uwierzytelnienia-w-webinterfejsie-cisco-asa/)
  * [Cisco Adaptive Security Appliance – Path Traversal](https://www.exploit-db.com/exploits/44956)
  * [Test CVE-2018-0296 and extract usernames](https://github.com/milo2012/CVE-2018-0296)
  * [Lua和C++交互详细总结](http://www.cnblogs.com/sevenyuan/p/4511808.html)
  * [网络设备漏洞分析技术研究](https://www.freebuf.com/articles/system/114741.html)
  * [Cisco ASA series part one: Intro to the Cisco ASA](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/september/cisco-asa-series-part-one-intro-to-the-cisco-asa/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360信安-涅槃团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/171916](/post/id/171916)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [cisco](/tag/cisco)
  * [CVE-2018-0296](/tag/CVE-2018-0296)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t018799f60cb7058aec.png) 360信安-涅槃团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

