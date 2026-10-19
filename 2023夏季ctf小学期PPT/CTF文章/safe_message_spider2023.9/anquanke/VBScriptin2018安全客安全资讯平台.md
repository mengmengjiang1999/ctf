# VBScript in 2018

阅读量 **365650**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-14 17:15:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01cd5ec5a5e5a162bf.png)

## 0x00 背景

VBScript是微软开发的一款脚本语言，是Visual
Basic的轻量级的版本。使用VBScript可以快速高效地开发出一些浏览器客户端和服务端的应用程序。然而随着DVE技术的公布以及在CVE-2014-6332、CVE-2016-0189中的稳定利用，VBScript开始被认为并不是那么安全了。很快微软在Windows
10 Fall Creators Update版本中对于Internet Explorer(IE)浏览器的Internet Zone和Restricted
Sites
Zone默认禁用了VBScript。但是这似乎并未减缓关于VBScript的在野漏洞利用攻击，相反，随着Adobe宣布2020年Flash正式退役，Hacker们似乎开始把重点转向了VBScript这个几乎被遗弃的脚本引擎。于是在2018年我们看到了CVE-2018-8174，CVE-2018-8373
这类0Day攻击事件以及相当数量的关于VBScript的CVE和研究报告。

笔者在学习了部分研究报告和调试了部分PoC后，决定对2018年VBScript的漏洞做个简单的归类总结，与大家分享，希望对关于VBScript的漏洞挖掘和分析有所帮助。但水平有限，文中错误之处恳请斧正。

## 0x01 分析

2018年关于VBScript的CVE不少，这里笔者筛选了6个比较有代表性的CVE分两类进行分析。

###  Type 1: Class_Terminate Callback

VBScript存在类的概念，VBScript类支持两个事件：Class_Initialize和Class_Terminate。在类实例化的时候会触发Class_Initialize事件，同样在类实例被销毁的时候会触发Class_Terminate事件。VBScript支持在脚本中通过添加自定义Class_Initialize或Class_Terminate事件的方法在脚本中手动做一些初始化或者释放的操作。也就是说自定义Class_Terminate给了VBScript引擎执行过程一次脚本回调的机会，如果在脚本回调过程中手动修改了一些数据，就可能触发一些未知的情形。

####  CASE 1：CVE-2018-1004

**1.PoC**

![](https://p4.ssl.qhimg.com/t01684f227b7669756c.png)

PoC执行流程：

1） 创建一个动态数组arr

2） 创建一个MyClass对象实例并保存到arr的第一个元素

3） 调用Erase函数逐个删除arr里的元素

4） 因为arr的第一个元素保存了MyClass对象实例，MyClass对象实例在析构的时候会调用脚本里的Class_Terminate函数

5） Class_Terminate重新定义的arr

**2.Debug**

1）Set arr(0) = new MyClass

![](https://p1.ssl.qhimg.com/t01f4627f6fe5cfb66c.png)

2）Erase a -> Class_Terminate -> ReDim Preserve a(1)

![](https://p1.ssl.qhimg.com/t0194f504ad2496b482.png)

3) Erase a -> OLEAUT32!VariantClear-> crash

![](https://p4.ssl.qhimg.com/t0187d92e55a5705113.png)

**3.Root Cause**

关于PoC的关键代码，VBScript引擎的执行过程如下图所示：

![](https://p5.ssl.qhimg.com/t011e13748d495ac866.png)

VBScript中的数组是由OLEAUT32的SAFEARRAY结构体定义的。

VbsErase通过调用OLEAUT32!_SafeArrayDestroyData释放数组元素，OLEAUT32!_SafeArrayDestroyData会遍历数组元素并将每个数组元素的地址传给OLEAUT32!VariantClear逐个清除数组元素：

![](https://p2.ssl.qhimg.com/t01619c1b37b6694e62.png)

OLEAUT32!VariantClear中如果元素是对象，且对象的引用计数为0，则调用该对象的析构函数，从而触发脚本函数Class_Terminate的回调。在Class_Terminate重新定义了arr的大小，导致原始arr
buffer被释放，但是OLEAUT32!VariantClear中依然保留了原始arr buffer地址，当再次访问该地址时触发crash。

####  CASE 2：CVE-2018-8174

CVE-2018-8174是360发现的一个在野0Day攻击样本。关于其具体利用代码分析可以参考360的Blog。

**1.PoC**

![](https://p2.ssl.qhimg.com/t01ac63342729c0c4ec.png)

PoC执行流程：

1） 创建一个数组arr

2） 创建一个MyClass对象实例并保存到arr的第一个元素

3） 调用Erase函数逐个删除arr里的元素

4） 因为arr的第一个元素保存了MyClass对象实例，MyClass对象实例在析构的时候会调用脚本里的Class_Terminate函数

5） Class_Terminate里将MyClass对象实例的引用保存到变量o，并释放自身引

6） 访问变量o

**2.Debug**

1）Set arr(0) = new MyClass

![](https://p1.ssl.qhimg.com/t01c6c0e6f84dd00c92.png)

2）Erase a -> Class_Terminate （转移MyClass对象实例的引用到变量o）

![](https://p5.ssl.qhimg.com/t011b2b58acd0dc7088.png)

3) msgbox o (通过变量o访问MyClass对象实例)

![](https://p1.ssl.qhimg.com/t011a5b6c9402eb08b6.png)

**3.Root Cause**  
关于PoC的关键代码，VBScript引擎的执行过程如下图所示：

![](https://p5.ssl.qhimg.com/t01237d0c4d85a849dc.png)

可以看到漏洞触发的流程和CVE-2018-1004较为相似，不同的是
CVE-2018-1004是在脚本回调函数Class_Terminate中释放了原始arr的buffer，而CVE-2018-8174则是在MyClass对象实例被析构前转移（读取）了MyClass对象实例的引用。

####  CASE 3：CVE-2018-8242

CVE-2018-8242是古河师傅分析了微软对CVE-2018-8174的补丁后，发现的一个新的漏洞。简单地说就是CVE-2018-8174的补丁只是禁止了在Class_Terminate中对VT_DISPATCH(Object)变量的读操作，但是并没有禁止在Class_Terminate中对VT_DISPATCH(Object)变量的写操作，然而写操作依然存在漏洞：

**1.PoC**

![](https://p4.ssl.qhimg.com/t0100ecbd96bd51e099.png)

PoC执行流程：

1） 创建一个数组arr

2） 创建一个MyClass对象实例并保存到arr的第一个元素

3） 调用Erase函数逐个删除arr里的元素

4） 因为arr的第一个元素保存了MyClass对象实例，MyClass对象实例在析构的时候会调用脚本里的Class_Terminate函数

5） Class_Terminate里再次调用Erase清除数组元素

**2.Debug**

1）Set arr(0) = new MyClass

![](https://p4.ssl.qhimg.com/t0115d04447dd305a78.png)

2）Erase a(1st) -> Class_Terminate -> Erase a(2nd)

![](https://p3.ssl.qhimg.com/t01c0179862b86ecfe7.png)

3) Class_Terminate -> Erase a(1st)

![](https://p3.ssl.qhimg.com/t0112f3768dad40ddc6.png)

**3.Root Cause**

关于PoC的关键代码，VBScript引擎的执行过程如下图所示：

![](https://p4.ssl.qhimg.com/t01a474bdd9c5558c74.png)

与CVE-2018-8174类似，这次在Class_Terminate再次尝试释放正在处于半释放状态下的VBScriptClass，最终触发Double
Free。

####  CASE 4：CVE-2018-8544

上面的3个case都与Class_Terminate中的array操作相关，而微软在7月的补丁中直接禁止了Class_Terminate操作array，但是依然可以考虑用其他的容器代替array，实现类似的效果，比如Dictionary。

**1.PoC**

![](https://p3.ssl.qhimg.com/t01e8980decac3c96e5.png)

PoC执行流程：

1） 创建一个Dictionary对象

2） 创建一个MyClass对象实例实例并保存到Dictionary容器，其key为“foo“

3） 重新给key-“foo“赋值，导致MyClass对象实例被释放

4）
因为PoC中定义了MyClass的Class_Terminate函数，故MyClass对象实例在析构的时候会调用脚本里的Class_Terminate回调函数

5） Class_Terminate里调用Dictionary的RemoveAll函数，清空所有key-value

**2.Debug**

1）Set dict.Item(“foo”) = new MyClass

![](https://p5.ssl.qhimg.com/t014b890d11a58b48ac.png)

2）dict.Item(“foo”) = 0 -> Class_Terminate -> dict.RemoveAll

![](https://p3.ssl.qhimg.com/t01aab290b8395724c9.png)

3) End Class_Terminate

![](https://p5.ssl.qhimg.com/t01284e313111be38b5.png)

**3.Root Cause**

关于PoC的关键代码，VBScript引擎的执行过程如下图所示：

![](https://p1.ssl.qhimg.com/t01ab3c40dc218cccc9.png)

虽然微软在CVE-2018-8242的补丁中彻底禁止了在Class_Terminate脚本回调中对数组的操作：

![](https://p4.ssl.qhimg.com/t0155e79a5fe4f21b6c.png)

![](https://p2.ssl.qhimg.com/t01d2cce5d60619b6fd.png)

但是仍然可以找到其他可以替代arr的容器，比如这里的Dictionary。其漏洞原理和CVE-2018-8242相似，同样是在Class_Terminate再次尝试释放（dict.RemoveAll）正在处于半释放状态下的VBScriptClass，最终触发Double
Free。

###  Type 2: Default Property Get Callback

Default Property Get用来获取类实例的缺省属性，当尝试将一个类实例转换成一个字符串对象时，如果脚本中定义了Default Property
Get函数，则会触发该函数的脚本回调。与Class_Terminate回调原理类似，如果在脚本回调Default Property
Get过程中手动修改了一些数据，亦可能触发一些未知的执行过程。

####  CASE 5：CVE-2018-8373

CVE-2018-8373是Trend Micro发现的另一个在野0Day攻击样本。关于其具体利用代码分析可以参考Trend的Blog。

**1.PoC**

![](https://p5.ssl.qhimg.com/t017e1702b8a8755ad7.png)

PoC执行流程：

1） 创建一个数组arr

2） 创建一个MyClass对象实例并将对象的值保存到arr的第三个元素arr(2)

3） 取MyClass对象实例的值时会触发脚本函数Default Property Get的调用

4） 回调函数Default Property Get中重新定义的arr，导致原arr buffer被释放

5） MyClass对象的值保存到原arr(2)地址中

**2.Debug**

1）arr(2) = new MyClass: 先计算左值arr(2)地址

![](https://p5.ssl.qhimg.com/t01480652796cb3e5c9.png)

2）arr(2) = new MyClass: 再计算右值，触发Default Property Get回调，修改了arr大小

![](https://p2.ssl.qhimg.com/t010bc6e1b06b4788fc.png)

3) arr(2) = new MyClass：右值保存到左值

![](https://p2.ssl.qhimg.com/t01291ec34df2c5dfbe.png)

**3.Root Cause**

关于PoC的关键代码，VBScript引擎的执行过程如下图所示：

![](https://p4.ssl.qhimg.com/t017c9b70dd87969444.png)

这次的回调利用的是Default Property
Get，可以发现其触发流程与CVE-2018-1004类似，不同的是CVE-2018-1004是在Class_Terminate回调中修改了arr的buffer，而CVE-2018-8373则是在Default
Property Get回调中修改了arr的buffer。

####  CASE 6：CVE-2018-8552

CVE-2018-8552是Google Project Zero Fuzz出来的一个漏洞，通过分析可以发现其与CVE-2018-8373相似之处。

**1.PoC**

![](https://p2.ssl.qhimg.com/t01cb1b8dbc9a7fb7da.png)

PoC执行流程：

1） 创建一个数组arr，其中一个元素为MyClass对象实例

2） Filter函数用来返回一个以特定过滤条件为基础的字符串数组的子集

3） Filter函数内遍历到MyClass对象实例时，触发脚本函数Default Property Get的调用

4） 回调函数Default Property Get中重新定义的arr，导致原arr buffer被释放

**2.Debug**

1）arr = Array(“b”, “b”, “a”, “a”, new MyClass)

![](https://p0.ssl.qhimg.com/t011a324ebc143a6df5.png)

2）Call Filter(arr, “a”) -> Default Property Get -> ReDim Preserve arr(1)

![](https://p2.ssl.qhimg.com/t01d50805d615e226d2.png)

3) Back Call Filter(arr, “a”)

![](https://p4.ssl.qhimg.com/t0193df228eb538d301.png)

**3.Root Cause**

关于PoC的关键代码，VBScript引擎的执行过程如下图所示：

![](https://p5.ssl.qhimg.com/t011b4c608aff155d43.png)

微软在CVE-2018-8373的补丁中通过给数组加锁的方式禁止在类似arr(2) = new MyClass的回调函数Default Property
Get中修改数组的大小：

![](https://p0.ssl.qhimg.com/t013d3412e6372778a7.png)

![](https://p3.ssl.qhimg.com/t01a1245c4922330248.png)

但是仍然可以找到其他替代方法在回调函数Default Property Get中修改数组的大小来触发漏洞，比如这里的Filter函数。

## 0x02 思考

###  1\. 脚本中的回调可能会导致未知的执行流程

通过上面的分析可以知道，脚本中的回调函数Class_Terminate，Default Property
Get会打乱脚本解析引擎的顺序执行流程，并且在脚本回到解析引擎之前执行一些非常规操作，比如修改正在访问的数组大小导致原数组buffer被释放，转移即将被释放的对象实例，释放即将被释放的对象实例等等。这就容易触发一些非预期的结果，比如UAF，OOB等等。如果能够发现一些新的回调方式或者触发回调的函数，就可能会有新的漏洞被发现。

###  2\. 补丁分析可能会有意外的收获

古河师傅的文章启发我们微软的补丁并非完美，比如有时候修复了一个数据类型的读漏洞（CVE-2018-8174）但是可能就忽略了写漏洞（CVE-2018-8242）。所以补丁分析对于发现一些新的漏洞是有帮助的。

这里笔者可以给坚持阅读到这的同学一个小彩蛋：通过对CVE-2018-8242的补丁分析知道微软对于在Class_Terminate中操作数组引发漏洞的修补方法是在进入OLEAUT32!_SafeArrayDestroyData前将数组的类型临时修改为VT_EMPTY，这样在Class_Terminate就不能操作数组了（此时数组类型是VT_EMPTY，尝试进行数组的操作会触发类型不匹配的运行时异常），最后在OLEAUT32!_SafeArrayDestroyData返回后恢复数组的类型：

![](https://p1.ssl.qhimg.com/t0155e79a5fe4f21b6c.png)

虽然不能再次在回调函数Class_Terminate里操作数组，但是被设置为VT_EMPTY类型的变量是否有可能被其他VARIANT再次占用呢？如果可以被占用，在OLEAUT32!_SafeArrayDestroyData返回后该VARIANT的类型又会被修改成数组类型，这里是不是就是一处类型混淆呢？：）

经试验在笔者最新打补丁的系统是可以触发crash的，感兴趣的话也可以尝试一下。

###  3\. GC相关的问题仍有待发现

GC是脚本中重要的一个特性，VBScript中主要通过引用计数方法来垃圾回收。如果引用计数错误的话就可能触发引用计数的泄露问题，比如文中未提到的CVE-2018-8625。同样可以注意到最近的两个在野0Day:
Flash CVE-2018-15982，Jscript CVE-2018-8653都是和GC相关。所以GC相关问题可能也会是后面发现漏洞的一个方向。

## 0x03 结论

2018年是VBScript漏洞挖掘与利用非常活跃的一年。两个被发现的在野0Day和相当数量的CVE说明Hacker们开始关注这个即将被微软淘汰的脚本引擎。有理由相信，只要VBScript不被微软从Windows中移除，接下来可能会有更多的漏洞甚至在野0Day攻击出现。

## 0x04 参考文献

  1. <http://blogs.360.cn/post/cve-2018-8174-en.html>
  2. <http://blogs.360.cn/post/from-a-patched-itw-0day-to-remote-code-execution-part-i-from-patch-to-new-0day.html>
  3. <https://blog.trendmicro.com/trendlabs-security-intelligence/use-after-free-uaf-vulnerability-cve-2018-8373-in-vbscript-engine-affects-internet-explorer-to-run-shellcode/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **iamelli0t** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170727](/post/id/170727)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [VBScript](/tag/VBScript)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t01be4b7fa9ae1425b6.png) iamelli0t

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

