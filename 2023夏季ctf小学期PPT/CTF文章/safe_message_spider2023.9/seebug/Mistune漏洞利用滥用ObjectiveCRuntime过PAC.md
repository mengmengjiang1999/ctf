**作者：0xcc  
原文链接：<https://mp.weixin.qq.com/s/HdsgTK4mNremDeV8TnO7iw>**

## 前情提要

[CVE-2021-1748：从客户端 XSS 到弹计算器](https://paper.seebug.org/1659/)

[CVE-2021-1864：访问控制的蝴蝶效应](https://paper.seebug.org/1661/)

在前文中介绍了天府杯 2020 上远程攻破 iPhone 11 的一套漏洞。首先由一个客户端的 XSS
绕过浏览器沙箱并打开额外的攻击面，接下来一个访问控制的逻辑漏洞来让 js 直接可以调用对象的 dealloc 方法，造成 Use-After-Free。

这是本系列的最终篇，介绍如何在最高 iOS 14.3 和 A14 芯片上利用以上漏洞，完全绕过用户态 PAC 和 APRR 执行任意 shellcode。

* * *

## SeLector-Oriented Programming

在前文中已经[构造了 fakeobj
原语](http://mp.weixin.qq.com/s?__biz=Mzk0NDE3MTkzNQ==&mid=2247483981&idx=1&sn=b0b8abbd404bea339b10416f02b38125&chksm=c329fcbdf45e75ab7e2001a704fbc64f4e3d8fa53583c746c55ff81742edfb7d78e277786a6f&scene=21#wechat_redirect)，让
objc_msgSend 将一块完全可控的内存当作 Objective-C 对象处理。

![](https://images.seebug.org/content/images/2021/08/33d485e6-f325-4ef5-9a74-8da4c2c1ecd5.jpg-w331s)

在 A12 以前，可以通过构造一些 runtime 的结构体（注：近期版本的 iOS 针对伪造 isa 做了加固）来控制 pc 寄存器，然后通过
return-oriented programming 执行任意代码。PAC 引入后，通过 objc_msgSend 控制 pc 寄存器就不可行，更不要说
ROP。

但是在 iOS 14.4 和之前的系统上有一个已知的弱点。

Objective-C 的对象结构中第一个指针为 isa，之后才是对象的私有属性等成员。由于 Objective-C runtime 本身用到了 isa
指针的高位存储信息，这就和 PAC 的实现有了冲突——PAC 使用密码学算法给指针添加的校验签名也保存到高位上。

所以在 iOS 14 之前，isa 指针没有签名保护。PAC 确保不能伪造 selector 对应的 IMP 函数指针，但可以通过指向已有的
objc_class 结构来调用合法的 selector 方法。结合特殊的 gadget，Project Zero 在 iMessage 的 0click
攻击演示中使用一种被称之为 SeLector-Oriented Programming 的技术来绕过 PAC，执行一连串 NSInvocation 调用任意
Objective-C 方法。

经过对 ABI 的调整（例如减少引用计数存储用的长度），在 iOS 14 beta 上，运行时已经开始对 isa
指针做签名。不过当时加上签名之后并没有开始校验，而是直接用 xpacd 指令移除签名位。

![](https://images.seebug.org/content/images/2021/08/86dae23b-5e94-428e-b8c4-c28b8114355d.jpg-w331s)

![](https://images.seebug.org/content/images/2021/08/96f23254-b3e8-4e13-a556-aa15f4d52d7e.jpg-w331s)

直到 2021 年发布的 iOS 14.5，终于上线了强制校验 isa 的 PAC 的运行时。关于这个改动，请参考之前发布的文章 [iOS 14.5 如何用
PAC 保护 Objective-C
对象](http://mp.weixin.qq.com/s?__biz=Mzk0NDE3MTkzNQ==&mid=2247483893&idx=1&sn=e2d16817ddbe155e8405c4a35cb3ca56&chksm=c329ff05f45e7613db4598a240294edc7525783f0d2d41f81d99a7cf0a16226d5075b6bfcaf0&scene=21#wechat_redirect)。

不过侥幸的是，在天府杯对应的 iOS 14.2，SLOP 还可以用。大胆猜测，新防御的迅速转正应该也是比赛被打起了一定的催化作用。

SLOP 的核心思路如下：

  1. 找到一个符合条件的类。这个类需要在 dealloc 方法中解引用 self 指针，将固定偏移上的成员当作 _UIAsyncInvocation，调用其 invoke 方法
  2. 这里隐藏了一个类型混淆，就是把 _UIAsyncInvocation 当作 NSInvocation。由于 Objective-C 是根据具体的 isa 指针和 selector 来确定具体调用的方法，这种 NSObject 之前的类型混淆只要存在对应的 selector，就不会产生异常，而是会顺利调用查找到的方法
  3. 于是对象被当作 NSInvocation 处理，调用其 invoke 方法
  4. NSInvocation 具有调用任意运行时方法的能力，这一步作为自举 gadget，来调用一系列 NSInvocation
  5. 一串的 NSInvocation 保存在 NSArray（数组）对象中。而 NSArray 正好有一个 makeOobjectsPerformSelector: 方法
  6. 给 makeObjectsPerformSelector: 传入 @selector(invoke) 作为参数，就会按顺序遍历数组内所有的 NSInvocation 并执行 ![](https://images.seebug.org/content/images/2021/08/deb4c533-fb47-4bf7-b402-aa97fcb2c231.jpg-w331s)

在这次的目标 iTunes Store 里正好有一个 SKStoreReviewViewController 满足要求。但在正式开启 SLOP
执行代码之前，我们还需要准备很多工作。

* * *

## 内存任意读

虽然在 iOS 14.2 上 PAC 还没有加到 isa 指针，但在 Project Zero 的 iMessage
利用演示之后加入了一个新的防御措施。Apple 意识到 NSInvocation 过于强大，需要针对内存伪造对象的检查。

于是 NSInvocation 引入了一个 32 位的随机数。随机数在单个进程内全局共享，每次启动进程时初始化。随机数保存的地址有一个符号
_magic_cookie.oValue。当 NSInvocation 被调用时，runtime 就会检查 NSInvocation 的 cookie
是否和全局变量相等。

这样一来，如果不能读内存，单纯用 fakeobj，是不能通过检查的。

接下来看看如何读内存。

WebScripting 将 js 的调用映射到 Objective-C 的函数调用。有一个隐藏的转换就是，js 里的 toString
函数，最终会调用对象的 description 方法，将得到的 NSString 转换回 js 的字符串返回。

NSData 正好有一个 hex dump 的特性。调用 -[NSData description] 会将其内存内容的十六进制打印出来。如果数据长度超过
24，则会用省略号截断内容：

{length=4096, bytes=0x23230a23 1025ff00 7224bfbf … 6e2f4142 5c732510}

那么可以构造如下结构：

![](https://images.seebug.org/content/images/2021/08/40fcd339-06e0-473a-b92c-7a4ae56fa943.jpg-w331s)

通过 ASLR 漏洞获得 NSConcreteData 的 isa 地址。接下来的字段是 buffer 的长度和指针，可以获得任意内存读。最后的
callback 成员必须用 0 填充，否则将会被当作一个函数指针，并将 NSData 标记为 freeWhenDone。这样可能造成不必要的崩溃。

这个函数可以复用，稳定性取决于 UAF 抢占内存的概率。虽然一次限制了 24 个字节，实际上可以转储整个内存空间的内容。

* * *

## 使用 ArrayBuffer 伪造对象

在前文中让 objc_msgSend 在可控的内存上做了消息发送，实现伪造任意 Objective-C 对象并调用其部分方法的效果。但这时候 fakeobj
用的内存分配原语来自前文的一个解码 data URI 的业务逻辑，获得的 NSData 对于 js 是只读的。

这意味着在需要重复使用对象解引用时，需要触发多次 Use-After-Free。如果能将内存指向一个 js 的
ArrayBuffer，并能在利用当中动态修改就好了。

要达到这个效果，有两种思路：用 heap spray 让 ArrayBuffer 到达一个硬编码的地址，或者使用内存任意读直接获取 ArrayBuffer
的 backing store。Heap Spray 是一个不太优雅的方案，稳定性相对后者低很多，不过比赛的时候用到了。

两个方案都用到了一种思路，就是 Objective-C 当中存在一类"容器"（或者"集合"）对象，例如 NSSet, NSArray
等。这类对象的特点是嵌套结构，在容器中会保存一个或多个元素的地址。这样就造成了在 fakeobj 上的二次地址解引用，可以再次定向到我们需要的地方。而且
Objective-C 的 dealloc 方法一般有递归调用的特点，即集合被释放时会依次尝试释放子元素。即使包上一层容器，也不影响代码执行等 gadget
的使用。

首先是最简单暴力的堆喷。

iPhone 物理内存很小，堆喷还是很有效的。用 js 创建多个 ArrayBuffer，确保其中一个能落到固定的地址上。在 UAF 创建的假对象上伪造一个
NSArray，只有一个元素，元素的地址指向固定的堆喷目标地址。

![](https://images.seebug.org/content/images/2021/08/00981017-c7e9-4f4a-94bb-a7ef6eb1ea6f.jpg-w331s)

为了区分具体落到目标的 ArrayBuffer，在 ArrayBuffer 里再创建一个嵌套的 NSArray，元素为 NSNumber，用来标记序号。

当调用最外部的对象的 toString 方法时，就会返回类似如下的字符串：

@[[@1234]]

这个 NSNumber 可以继续用 isa 和内存结构伪造，不过在比赛时直接伪造了 tagged pointer 用来加速内存喷射。有 iOS
开发背景的开发者一般知道，为了节省内存，一部分数字、字符串、日期等对象可以通过指针本身的 bits 保存。

在当前版本的 iOS 上，tagged pointer 被混淆处理。例如之前的

0xb000000000000012，混淆之后看上去完全变成了随机数

0x93b027f3768c6a51。

这也是 iOS 为了防止远程攻击引入的防御。在每个进程初始化时，生成一个随机数保存到全局变量
objc_debug_taggedpointer_obfuscator。之后的 tagged pointer 会和这个随机数 xor
处理。在缺乏信息泄露漏洞时，就很难伪造 tagged pointer。

不过还记得之前的 addrof 原语吗？这个原语可以直接泄露出 js 数字对应的 NSNumber 的地址，也就是一个 tagged pointer。已知
xor 的算法和一对(数字,混淆值)之后，就可以算出任意数字的 tagged pointer：

    
    
    const tagf64 = (() => {  const mask = 0x800000000000002Bn;  const float64_obfuscator = ((1n << 7n) | mask) ^ addrof(1);  const objc_debug_taggedpointer_obfuscator = float64_obfuscator & (!(7n));  iTunes.log('tagged pointer obfuscator: ' + objc_debug_taggedpointer_obfuscator);  return n => ((BigInt(n) << 7) | mask) ^ float64_obfuscator;})();

使用 tagged pointer 伪造对象可以减少一半以上的内存写入操作。而 addrof 原语会抛出一次异常，并产生 syslog 输出。如果直接用
addrof 生成所有的数字 id，程序从毫秒级拖慢到几秒，性能差距在千倍以上。通过这个伪造 tagged pointer 的算法，极大地提升了堆喷的效率。

不过比赛结束之后我又鼓捣了不用堆喷的方案，稳定性极大提升了，也不需要伪造 tagged pointer。

这一个思路其实更简单。

WebScripting 会为 js 运行时里的对象创建一个 WebScriptObject。当用 addrof 原语获取一个 ArrayBuffer
的地址时得到的就是这个对象的地址。在WebScriptObject 里有一个 jsObject 指针，指向 JavaScriptCore 里的对象结构。

ArrayBuffer 的 jsObject 指向 jsc 的 Int8Array，也就是保存 ArrayBuffer 内容的地方。在新版的 WebKit
里 VectorPtr 指针被 PAC 加上了保护，用来防止伪造指针来获取内存读写的利用技术。这便是 PAC-cage。

![](https://images.seebug.org/content/images/2021/08/94b8741e-a293-4b7c-b10a-84a00af55240.jpg-w331s)

我们的目的是用 ArrayBuffer 的二进制数据被 Objective-C 当作对象来处理，不会修改 VectorPtr。而 Objective-C
也不管 jsc 里的 PAC 签名。因此只需要用逻辑 and 运算简单地移除掉高位即可得到一个 fakeobj 的指针。把这个指针作为 UAF 的之后伪造的
NSArray 的唯一元素即可。

* * *

## 构造 Double Free

SLOP 技术有一个关键 gadget 就是调用 dealloc 方法。Project Zero 在实现 iMessage
攻击的时候利用了一个条件，即数据序列化之后创建出来的对象会隐式调用 dealloc 方法。

在前面一系列步骤之后，我们伪造了一个SKStoreReviewViewController 对象，并在 0x358 偏移处放了一个 bootstrap 用的
NSInvocation。既然第二篇文章说到，Use-After-Free 的核心问题在于 dealloc 可以被 js 调用，那么是不是再调用一次
dealloc 就行了？

并没有这么简单。

之所以 dealloc 能被 js 访问，是 SUScriptObject 在实现 isSelectorExcludedFromWebScript:
方法时返回了 NO。不过 SKStoreReviewViewController 并不是 SUScriptObject 的子类，最后会执行到
+[NSObject isSelectorExcludedFromWebScript:]，而默认的实现是一律 YES 拒绝。

要让伪造的对象再调用一次 dealloc，我们需要找到一个满足如下条件的类：

  * SUScriptObject 的子类
  * 提供一个 setter 方法，可以将其他对象赋值到这个类的属性上
  * 在 dealloc 时递归释放成员属性

SUScriptSegmentedControlItem 便满足需求。

首先用 js 分配该对象到变量 A：

    
    
    iTunes.makeSegmentedControl().createSegment()

然后调用 setUserInfo_ 将对象 B 关联上去。调用对象 B 的 dealloc 释放后占位，准备好 SLOP 所需的数据结构。这时候调用 A 的
dealloc，就会递归调用到 B 的 dealloc 方法。

    
    
    const deallocator = iTunes.makeSegmentedControl();const seg = deallocator.createSegment(); // for double freeiTunes.log(`dangling pointer: ${addrof(x)}`);window.x = x; // avoid GCseg.setUserInfo_(x);x.dealloc(); // first free// ... exploit the UAFseg.dealloc(); // double free to kickstart the chain

![](https://images.seebug.org/content/images/2021/08/ae7147b7-e24e-4261-b713-99d6a44bb1c1.jpg-w331s)

* * *

## 调用任意 C 函数

到这一步已经可以串联多个 Objective-C 方法，实现相当多功能了。

Project Zero 的 iMessage 攻击演示用到了两个特殊的 gadget，可以配合起来调用任意被导出的 C 函数。

-[CNFileServices dlsym::]

-[NSInvocation invokeUsingIMP:]

第一个正如它的名字，等价于 dlsym。在 PAC 环境下，dlsym 返回的函数指针使用进程内共享的 IA key 和 0
作为上下文来签名，通常用作将函数指针当作 callback 的场景。

而另一个则是 NSInvocation 的私有用法，可以自定义 IMP 指针，也就是函数指针，实现参数可控的函数调用。这个方法利用到的 IMP 正是使用
IA key 和 0 context 签名。

两个方法结合起来，就可以调用任意能被 dlsym 找到的函数。

但是 saelo 留下了一个问题没有解决。NSInvocation 要求函数的第一个参数，也就是 self 指针不能为
nil（0）。在接下来的漏洞利用中，我们需要以 0 为参数调用一些函数。

这个缺陷可以用 CoreFoundation 里的回调函数解决。

例如这个：

void CFSetApplyFunction(CFSetRef theSet, CFSetApplierFunction applier, void
*context);

第二个参数的 applier 是一个 IA key 和 0 context 签名过的函数指针。CFSetApplyFunction 将遍历 CFSet
所有的元素，将元素和 context 作为参数传给 applier。

这样便可以通过如下代码（对应的 SLOP 链）绕过限制：

    
    
    void *fake[2] = {(__bridge void *)NSClassFromString(@"__NSSingleObjectSetI"), NULL};CFSetApplyFunction((void *)&fake[0], (void*)exit, (void*)0x41414141);

首先创建一个只有一个元素的 __NSSingleObjectSetI，元素指针就是 0（applier 的第一个参数）。接下来调用
CFSetApplyFunction，加上 void *context 一共可以完全控制两个参数。

另外我没有实测过一个想法，由于 arm64 使用通用寄存器传递参数，如果上层的 CFSetApplyFunction
没有污染后续的寄存器，那么有可能还可以控制更多的参数。

反正之后的利用链条两个参数够用了。

* * *

## 绕过 APRR 载入任意 shellcode

JavaScriptCore 用到了 APRR 来动态切换 JIT
代码页的权限。对于一个线程而言，页面的属性要么可写要么可执行；而不同线程（编译线程、执行线程）看到的内存页属性可以是不一样的。

虽然浏览器的 just-in-time
允许加载动态的机器码，漏洞利用程序在获得内存读写之后却没办法简单将代码写入。写入代码必须调用特殊的指令切换内存属性，复制代码之后再恢复权限为可执行。而
PAC 又将代码重用攻击（ROP）阻断了，使攻击者不能简单复用浏览器已有的指令。

在 APRR 和 PAC 的协作下，很难单纯用内存读写载入任意代码。而绕过技术更是见光死，修一个少一个。不得不说 Apple
使用私有的硬件极大提高了漏洞利用的门槛。

当然凡事无绝对，以下介绍一个已被修复的绕过。

具体来说，WebKit 在生成即时编译的机器码会用到一个总是内联的 performJITMemcpy 函数。这个函数内部流程大致如下：

    
    
    pthread_jit_write_protect_np(0); // set writablememcpy(jit_function, code, size); // write shellcodepthread_jit_write_protect_np(1); // set executable

pthread_jit_write_protect_np 本该被展开成为 内联汇编指令。但是 iOS 14.3 之前犯了一个低级错误，在
libpthread 里把这个函数设置成了公开导出。这样结合前文的 SLOP 技术，我们直接构造以上三个函数调用，就可以轻而易举地绕过
APRR，写入任意的机器码。

* * *

## 又一个 PAC 绕过：CVE-2021-1769

这一步在漏洞利用中不是必要的，有些炫技的成分。

前面的步骤中实现了任意 shellcode 的写入，还差最后一步 pc control，把控制流重定向到 shellcode 上。

可以使用经典的做法，利用 JIT 生成一个足够大的函数体，用上面的 APRR 绕过覆盖函数的机器码。最后在 js 里调用该函数时就会执行被修改过的
shellcode。

在这里使用了另一种思路。可以看到 SLOP 本身就可以实现复杂的功能，即使不写 shellcode 也能完成很多效果。我的想法是找到一些未被 PAC
保护的间接跳转指令，由某个函数从已知的内存地址中读取一个指针，然后不加验证地跳转过去。只要使用 SLOP
将指针修改掉，再调用这个具有间接跳转的函数，就可以控制 PC 运行 shellcode。

通过 IDA Pro 对整个 dyld_shared_cache 搜索，找到了这个 Swift 的运行库函数：

![](https://images.seebug.org/content/images/2021/08/0d26784a-bed8-4002-994d-c861368e7ea6.jpg-w331s)

其中第二条 ldr 指令读取的就是一个 GOT 表项目，也就是没有 PAC 保护的函数指针。接下来函数走到 jn( _:_ :)，再继续看汇编指令：

![](https://images.seebug.org/content/images/2021/08/66f16862-7175-49f0-ba96-e6f470e02db2.jpg-w331s)

最后一行 br x1 即是跳转到函数的第二个参数，也就是前文 ldr 读取出来的指针。

以上函数位于 /usr/lib/swift/libswiftDarwin.dylib，默认没有被 iTunes Store 链接到，可以用 SLOP 调用
dlopen 加载之。接着修改 _jn_ptr@PAGE 的值为shellcode 的地址，然后直接调用 dlsym 出来的_
$s6Darwin2jnySdSi_SdtF 函数即可。

这个 PAC 绕过在 iOS 14.4 修复，通过升级编译工具链移除了所有无保护的 GOT 指针。

* * *

最终 shellcode 执行结果如下：

![](https://images.seebug.org/content/images/2021/08/9950b674-c3a9-4d7b-af54-e1fb069868c8.jpg-w331s)

第一篇文章里提到了，这个 App 非常特殊，可能是目前 shellcode 能在 iOS 上获取的最高权限。所有基于 App
能实现的越狱都可以无缝串联到这里。iTunes Store 还通过 entitlement 加入了例如摄像头、通讯录、Apple Wallet、Apple
ID 等敏感信息等访问权限，直接调用对应的 API 即可。

本研究大量参考了 Samuel Groß 的 iMessage hack 和 JITSploitation
系列文章，强烈推荐阅读，也在此表示感谢。可以看到阅读历史漏洞利用的报告对展开新的研究具有极大的推动作用。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1671/>

