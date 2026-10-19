# EOS节点远程执行代码漏洞

阅读量 **167188**

|评论 **1**

发布时间 : 2018-05-29 16:43:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 漏洞报告者

Yuki Chen of Qihoo 360 Vulcan Team

Zhiniang Peng of Qihoo 360 Core Security

## 漏洞描述

我们发现了EOS区块链系统在解析智能合约WASM文件时的一个越界写缓冲区溢出漏洞，并验证了该漏洞的完整攻击链。

使用该漏洞，攻击者可以上传恶意的智能合约至节点服务器，在节点服务器解析恶意合约后，攻击者就能够在节点服务器上执行任意代码并完全控制服务器。

在控制节点服务器后，攻击者可以将恶意合约打包进新的区块，进而攻击和控制其他新的节点，最终攻击和控制整个EOS网络。

## 漏洞报告时间线

2018-5-11 发现EOS越界写缓冲区溢出漏洞

2018-5-28 测试开发了完整攻破EOS超级节点的漏洞验证程序

2018-5-28 将漏洞细节报告给厂商

2018-5-29 厂商在Github托管代码库中修复漏洞，并关闭问题跟踪项

2018-5-29 提醒厂商漏洞未完全修复

一些在Telegram上与Daniel Larimer的沟通细节：

我们尝试和Daniel沟通并报告漏洞，Daniel回应我们在没有修复漏洞情况下不会发布新版EOS，同时请求我们在有人公开测试漏洞前，先将漏洞报告提交给他。

[](http://blogs.360.cn/wp-content/uploads/2018/05/001.jpg)

Daniel给了我们一个官方的邮件地址，让我们以邮件形式提交漏洞报告。  
[](http://blogs.360.cn/wp-content/uploads/2018/05/002.jpg)[](http://blogs.360.cn/wp-content/uploads/2018/05/004.jpg)

最后Daniel承诺在EOS的漏洞修复后，将给予我们公开致谢。

[](http://blogs.360.cn/wp-content/uploads/2018/05/003.jpg)

##

## 漏洞细节

这是一个缓冲区溢出越界写漏洞

漏洞存在于在 libraries/chain/webassembly/binaryen.cpp文件的78行,

Function binaryen_runtime::instantiate_module:

for (auto& segment : module->table.segments) {  
Address offset =
ConstantExpressionRunner<TrivialGlobalManager>(globals).visit(segment.offset).value.geti32();  
assert(offset + segment.data.size() <= module->table.initial);  
for (size_t i = 0; i != segment.data.size(); ++i) {  
table[offset + i] = segment.data[i]; **< = OOB write here !**  
}  
}

这里的table是一个std :: vector包含在函数表中的名称，在将元素存储到table中时，|offset|
字段没有被正确检查。注意在设置该值之前是有一个assert 断言的，它会检查偏移量，但不幸的是assert 仅适用于Debug版本，不适用于发布版本。

table.resize(module->table.initial);

|module->table.initial| 这个代码片段读取的值是根据函数表声明，在WASM文件中的读取的，该字段的有效值为0〜1024。

|offset| 字段的值是根据数据段从WASM文件中读取的，它是一个带符号的32位值。

所以通过这个漏洞，我们可以在table向量之后的内存，越界写入一定范围的内容。

## 重现漏洞过程

  1. **编译最新的EOS代码release版本**

`./eosio-build.sh`

  2. **启动EOS节点Start EOS node, 完成如下所有必要的配置**

<https://github.com/EOSIO/eos/wiki/Tutorial-Getting-Started-With-Contracts>

  3. **设置一个漏洞合约**

我们提供了一个会造成程序崩溃的WASM漏洞验证文件（POC）

在这个PoC中, 我们简单的设置了 |offset| 字段引用 0xfffffff地址，所以会触发越界写造成程序崩溃

开始测试 PoC:  
`cd poc  
cleos set contract eosio ../poc -p eosio`

顺利的话我们会看到 nodeos 进程出现 segment fault错误

崩溃信息:

> (gdb) c
>
> Continuing.
>
> Program received signal SIGSEGV, Segmentation fault.
>
> 0x0000000000a32f7c in
> eosio::chain::webassembly::binaryen::binaryen_runtime::instantiate_module(char
> const*, unsigned long, std::vector<unsigned char, std::allocator<unsigned
> char> >) ()
>
> (gdb) x/i $pc
>
> => 0xa32f7c
> <_ZN5eosio5chain11webassembly8binaryen16binaryen_runtime18instantiate_moduleEPKcmSt6vectorIhSaIhEE+2972>:
> mov %rcx,(%rdx,%rax,1)
>
> (gdb) p $rdx
>
> $1 = 59699184
>
> (gdb) p $rax
>
> $2 = 34359738360
>
> Here |rdx| points to the start of the |table| vector,
>
> And |rax| is 0x7FFFFFFF8, which holds the value of |offset| * 8.

##

##  利用漏洞实现远程代码执行

利用此漏洞可以在nodeos进程中实现远程代码执行，漏洞利用方法是将恶意合约上传到受害节点，并让节点解析恶意合约。而在真正的攻击中，攻击者可能会向EOS主网络发布恶意合约。

EOS超级节点解析恶意合约触发漏洞后，攻击者将可以完全控制这个节点。

攻击者可以窃取超级节点的私钥或控制新区块的内容，更重要的是攻击者可以将恶意合约打包成一个新块并发布进行攻击，最终整个网络中的所有节点都将受到攻击并被控制。

我们完成了概念性的漏洞验证程序，并在基于64位Ubuntu系统的nodeos上进行了测试。这个漏洞的攻击过程是这样的：

  1. 攻击者将恶意合约上传到nodeos服务器。
  2. 服务器nodeos进程解析引发漏洞的恶意合约。
  3. 使用越界写入的原生代码，我们可以覆盖WASM模块实例的WASM内存缓冲区，在恶意WASM代码的帮助下，最终可以在nodeos进程中实现了任意内存读/写操作，并绕过了64位操作系统上的DEP / ASLR等常见的攻击缓解技术。
  4. 漏洞利用一旦成功，会启动一个反向shell连接攻击者。

可以参考我们提供的视频，了解这个概念性的漏洞利用过程，稍后我们可能会提供完整的漏洞利用链。

## 漏洞修复

Bytemaster在EOS的Github托管项目中，为我们报告的漏洞建立了3498编号的issue跟进修复问题。

[](http://blogs.360.cn/wp-content/uploads/2018/05/1-2.png)

修复的相关代码

[](http://blogs.360.cn/wp-content/uploads/2018/05/2-2.png)

但是根据此次漏洞发现者Yuki所提交的评论，这个漏洞并没有完全被修复，在32位进程的处理过程中仍然存在问题。

[](http://blogs.360.cn/wp-content/uploads/2018/05/3-2.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360vulcan team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/146497](/post/id/146497)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [远程代码执行](/tag/远程代码执行)
  * [区块链安全](/tag/区块链安全)
  * [EOS漏洞](/tag/EOS漏洞)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t01cce7f410770758df.png) 360vulcan team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

