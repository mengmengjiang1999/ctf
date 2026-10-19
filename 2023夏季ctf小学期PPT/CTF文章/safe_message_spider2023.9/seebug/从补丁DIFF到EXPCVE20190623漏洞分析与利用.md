**作者：ze0r @360A-TEAM  
公众号：[360ESG CERT](https://mp.weixin.qq.com/s/5KFEKs2jepivBSSdCsHefA "360ESG
CERT") **

在本篇文章中，我们将对CVE-2019-0623进行深入分析并得到利用EXP。

这个漏洞是微软在2019年2月份的补丁日中发布的（漏洞补丁），由腾讯的湛沪实验室提交给微软官方。该漏洞是一个存在于win32k.sys中的提权漏洞。分析后知道，这个漏洞居然异常简单！而且最早在1993年漏洞代码就已经被写出来了，所以至今已经存在了至少25年之久！下面我们来看看这个漏洞。

从微软的官方介绍上可知，此漏洞存在于win32k.sys中。在官方下载了补丁文件后解出更新后的win32k.sys后，与未更新的版本对比（win 7
32位系统）：

![
](https://images.seebug.org/content/images/2019/03/e04c8223-956a-45f0-aa74-0f85d1cfe456.jpg-w331s)

从图中可以看出，更改较大的有sfac_ReadGlyphHorMetrics和ReferenceClass。这里说一下，由于微软是在修补漏洞，而漏洞处的前后逻辑（比如漏洞函数本身的参数和之后返回的值）是不会改动的，一般漏洞都是没有校验XX或者没有检查XX参数造成XX超长，所以微软一般是在某处新增一段代码。看了sfac_ReadGlyphHorMetrics函数比较乱，便去查看ReferenceClass函数，查看流程图，发现是新增加了一段代码，差异如下：

![
](https://images.seebug.org/content/images/2019/03/81026421-1387-4648-aa4e-a231cffc1c94.jpg-w331s)

明显中间是新增加了中间粉红色的代码。所以很可能问题出在此函数上。拉近看看：

![ ](https://images.seebug.org/content/images/2019/03/6c1954ea-cd52-43c5-8aaf-5a362967e1fe.jpg-w331s)

中间能看到多了一次ExAllocatePoolWithQuotaTag函数的调用，图形看具体代码不方便，我们在IDA里看：

![
](https://images.seebug.org/content/images/2019/03/a8d301e3-e64a-4250-9baa-85b66fa66ea7.jpg-w331s)

![
](https://images.seebug.org/content/images/2019/03/6fd9847f-1fea-4fbe-84b9-049fc2429f58.jpg-w331s)

可以看到，都是在ClassAlloc返回的内存块赋值给一个变量（v4）,并且使用memcpy给整个v4结构体全部赋值。而差异在于，新版的是又多申请了一块内存（调用ExAllocatePoolWithQuotaTag在内核中申请），并且把申请到的内存赋值给了v4的一个成员。如果这里就是漏洞所在，那么应该就是v4的一个成员（
v4+0x50）和a1的成员指向了同一段内存，而指向同一段内存可能会导致内存值被另外改变、释放等。那么我们有必要弄清楚，这个V4和V4的这个成员到底是谁，又是什么作用。我们去翻看一下win2000的源代码尝试寻找答案：

![
](https://images.seebug.org/content/images/2019/03/81101845-9df5-4c1a-a7c0-c93673ea03cf.png-w331s)

很幸运，泄露的部分源代码中，包含此函数：

![
](https://images.seebug.org/content/images/2019/03/a8db5e34-5697-44dd-9256-544413d61917.jpg-w331s)

这里只截图了该函数中对应diff结果的代码部分，从代码和IDA
F5结果来看，这段代码完全一致。仔细看代码本身，1677行ClassAlloc函数是申请一个Class结构大小的内存，那么v4(pclsClone)其实是class结构，之后使用RtlCopyMemory给整个新申请的CLASS初始化，而赋值的来源则是调用该函数的第一个参数，所以该函数的功能基本就是根据参数传进来的CLASS再“克隆”出来一个CLASS，并且之后对克隆出来的新CLASS的成员进行一些设置。我们查看一下Class结构：

![
](https://images.seebug.org/content/images/2019/03/4b17cdd2-a23b-438c-a649-fa9879c082bf.jpg-w331s)

可以看到，在该结构中，0x50的地方是lpszMenuName，对应于用户态的WNDCLASS结构的lpszClassName成员。回头来看源代码，发现新申请的Class
pclsClone竟然没有被重新设置！也就正是补丁所做的：重新申请了一段内存给lpszMenuName！而新旧两个CLASS的menuname成员的值一样的话，则意味着，如果我们能想办法操纵一个CLASS释放掉这块内存，而另一个CLASS也销毁的时候，会引起double-free的问题！

那么漏洞位置找到了，现在需要触发漏洞。这存在如下问题：

  1. 哪里会调用漏洞函数？

  2. 如何通过操纵其中一个CLASS释放掉MenuName内存？

  3. 如何通过操纵另一个CLASS来再次释放这块内存？

我们先来看第一个问题，在IDA的交叉引用中，查看引用ReferenceClass函数的地方：

![
](https://images.seebug.org/content/images/2019/03/da210f90-bd1f-454e-9bd1-5b5a9040a872.png-w331s)

只有两处引用该函数，而其中一个就是xxxCreateWindowEx，该函数是在创建一个窗口的时候直接会被调用，而引用处：

![
](https://images.seebug.org/content/images/2019/03/a337621d-d54b-4cd8-bde4-fdc810d6fa33.png-w331s)

完全不需要任何条件！所以这里我们可以直接让流程调用进入到漏洞函数ReferenceClass。以下分析使用WIN 2008 R2 X64系统：

![
](https://images.seebug.org/content/images/2019/03/93238f11-1339-43e3-85c3-304c328131df.png-w331s)

![
](https://images.seebug.org/content/images/2019/03/c5bd16c9-3345-49f7-bb02-82792600927d.jpg-w331s)

可以看到，我们直接进入到了漏洞函数。回头再看一下WIN2000的源代码：

![
](https://images.seebug.org/content/images/2019/03/7455272c-37d5-43b3-868c-d6248b1a31bb.png-w331s)

在第1657行，我们看到如果是源CLASS(以下称baseCLS)的桌面和当前要创建的WINDOW所在的桌面一样的话，就会直接增加CLASS的引用计数后返回，也就是不需要再克隆一个新CLASS了。那么我们想要触发漏洞，就需要注册CLASS时和使用注册的CLASS创建窗口时处在不同的桌面中：

![
](https://images.seebug.org/content/images/2019/03/2cf0253f-59dd-4ff6-9b12-e260666a5165.png-w331s)

之后可直接进入到克隆新CLASS的流程：

![
](https://images.seebug.org/content/images/2019/03/aa9bcfc4-4650-4643-8928-713278b93976.jpg-w331s)
![
](https://images.seebug.org/content/images/2019/03/c6435fa6-2df8-4446-987c-85fbb96fe987.jpg-w331s)

这里说一下，在tagCLS结构中，存在一个pclsBase成员，这个成员会指向baseCLS，再注册一个窗口类时，CLASS结构的这个成员会被初始化为指向自己。而pclsClone成员则会指向自己复制出来的新CLASS：

![
](https://images.seebug.org/content/images/2019/03/3d2be169-8f55-45c3-92d8-c8b6dc202a77.png-w331s)

分别查看一下baseCLS和CloneCLS的MenuName成员：

![
](https://images.seebug.org/content/images/2019/03/16293782-5561-4fbc-b901-49610df152ea.jpg-w331s)

可以看到两个CLASS的MenuName成员指向了同一块内存：

![
](https://images.seebug.org/content/images/2019/03/374818a5-e9fd-4d0c-9089-c872e909ef10.png-w331s)

至此，我们已经得到了两个CLASS，接下来的问题是如何释放掉其中一个CLASS的lpszMenuName成员？也就是问题2。要解决这个问题，当然是往CLASS的MenuName方向考虑。熟悉WINDOWS
GUI编程的都知道，有一个API叫SetClassLongPtrA，该API可以完成更改一个窗口所使用的类的属性，当调用该API第二个参数为GCLP_MENUNAME时，可更改（替换）CLASS的menu
name：

![
](https://images.seebug.org/content/images/2019/03/bb2b09db-60a4-42a3-8b58-23089cfbfba2.png-w331s)

这里就透露了一个很重要的信息：既然是menu name
String，是个字符串，那么就是一段内存，那么如果新字符串比原字符串长呢？那肯定是要重新申请内存的，那么原内存肯定会释放！而泄露的源代码也印证了这一点：

![
](https://images.seebug.org/content/images/2019/03/556358df-b683-4640-b06f-1cecb43c841f.jpg-w331s)

可以看到，当为GCLP_MENUNAME时，会在1567行释放掉旧内存！所以我们就有了第2个问题的解决方案，让MenuName指向的内存块释放掉：

![
](https://images.seebug.org/content/images/2019/03/67b13f96-66f1-4cf6-be8b-3726ebc46c59.png-w331s)
![
](https://images.seebug.org/content/images/2019/03/77adf7e1-db76-4eea-9da9-3b85d6bbd7b6.jpg-w331s)
![
](https://images.seebug.org/content/images/2019/03/901be4f8-058b-4e3c-8c63-c4dcbbeec88a.jpg-w331s)

可以看到，释放了lpszMenuName成员指向的内存块：

![
](https://images.seebug.org/content/images/2019/03/2ca60bbe-d755-4263-a6c3-aa9e4813cf94.jpg-w331s)

然而，在baseCLS中的lpszMenuName成员，还是依然指向这块内存：

![
](https://images.seebug.org/content/images/2019/03/e4d9760d-d5f1-486e-bb73-bc072efded51.jpg-w331s)

可以看到，baseCLS中的MenuName成员指向的数据，已经不再是UNICODE的xxxxxx了！如何还剩下最后一个问题：如何让baseCLS的MenuName释放呢？也就是问题3。我们知道，tagCLS结构，在内核中就是一个内核结构，产生可以RegisterClassExA，那么销毁也自然简单：UnregisterClass就行！但在测试中，发现直接调用该API，在系统调用完成后，user32.dll中的代码会导致在用户态的某处内存错误，所以这里是直接调用了系统调用的销毁API：NtUserUnregisterClass

![
](https://images.seebug.org/content/images/2019/03/eb2e6df0-b95d-436d-ad4b-c8bb7f776f92.png-w331s)

调用即触发重复释放内存块：

![
](https://images.seebug.org/content/images/2019/03/c0f3f614-69d9-4498-94e2-424809b591d7.jpg-w331s)

![
](https://images.seebug.org/content/images/2019/03/bd592bad-61e3-4c55-90c0-600bfd2640d4.jpg-w331s)

![
](https://images.seebug.org/content/images/2019/03/bdf060e0-8f99-410e-a67c-ff32c82fd51d.jpg-w331s)

可以看到该内存被再次释放！继而引发BSOD（这里由于为了后补一张截图，重新运行了POC，所以RCX并不完全一样）：

![
](https://images.seebug.org/content/images/2019/03/6b78f5ea-6bcc-47a5-902d-2f6b81b73b28.jpg-w331s)
![
](https://images.seebug.org/content/images/2019/03/7cda29df-744f-4486-8946-d5596b7525fa.png-w331s)

至此，我们已经成功触发了漏洞！

接下来，就是如何利用此漏洞。我们经过上面的分析可知，该漏洞就是个double-free，所以利用流程如下：第一次释放->重新占用刚刚释放的内存->触发第二次释放->再次占用内存->使用第一次占用对象句柄来更改内存内容->获取一个损坏的对象！这个流程不再多说，有兴趣的可以参照本人之前的文章《从补丁diff到EXP
--CVE-2018-8453漏洞分析与利用》。这里仅贴出关键代码和简单流程说明：

  1. 创建触发环境：

![
](https://images.seebug.org/content/images/2019/03/4224bde7-dbae-4e77-a10a-4653e5425e53.png-w331s)

  2. 触发第一次释放：

![
](https://images.seebug.org/content/images/2019/03/ace62ce8-0b36-49b1-8d6a-260c484f7b88.png-w331s)

  3. 马上占用被释放的内存：

![
](https://images.seebug.org/content/images/2019/03/732419b0-77a2-4248-acc9-1bf9c06718a8.png-w331s)

  4. 触发第二次释放：

![
](https://images.seebug.org/content/images/2019/03/e742aa6e-e1f3-41c8-9eee-0dfe06786045.png-w331s)

  5. 创建palette对象，再次占用被释放的内存：

![
](https://images.seebug.org/content/images/2019/03/d992b1ff-b015-4549-94bf-b1b22d500293.png-w331s)

  6. 使用第4步中创建的DC对象来重写Palette结构，我们这里更改Palette结构中的大小，造成越界访问，从而更改紧临后面的Palette对象的地址指针等：

![
](https://images.seebug.org/content/images/2019/03/b1cdc575-af35-4d1e-8b56-f4a309fbabdc.png-w331s)

  7. 使用越界的Palette(Manger)来控制后面的Palette（worker）地址指针成员，完成获取token、替换token工作。然后创建CMD进程实现提权：

![
](https://images.seebug.org/content/images/2019/03/b3c22f1f-aed7-4635-a0c6-7547c249de04.png-w331s)

最后，由于上面第4步中，有一个DC对象的成员是被释放了的，如果退出EXP，则会导致释放这个DC对象的时候，导致系统BSOD（重复释放内存）。所以我们需要修正这个成员：只要把这个成员的值改为0即可，但获取该DC对象的地址却相当麻烦。

查看win32k的转换过程，发现如下：

![
](https://images.seebug.org/content/images/2019/03/da46378b-0a80-47b1-b88f-2236c4b3f80f.png-w331s)

所以重点是如何获取gpentHmgr表，win32k.sys+固定偏移的方式固然可以，但是兼容性太不好，只能是在本环境中可以，这是本人所不愿看到的。最后采用函数搜索的办法：

![
](https://images.seebug.org/content/images/2019/03/61d7d239-ddd5-4246-a620-4c1f31e2fdde.png-w331s)

Win32k.sys导出了EngCopyBits函数，该函数内引用了gGdiInPageErrors全局变量：

![
](https://images.seebug.org/content/images/2019/03/8e00597f-4c10-4200-9ea9-5aa29aa31b9d.png-w331s)

而该变量的附近就是gpentHmgr:

![
](https://images.seebug.org/content/images/2019/03/7afa79b6-9165-4ec1-846e-769fa90daf26.png-w331s)

所以只要从win32k.sys中，从导出表找到这个位置，然后减固定偏移就是gpentHmgr的指针！而寻找内存中win32k.sys模块的基址，本人从nt!PsLoadedModuleList中找到win32k.sys的基址，然后加上上面获取到的偏移获得gpentHmgr指针的地址，然后读取该地址通过换算即得到DC的地址，之后将目的成员值为0即可：

![
](https://images.seebug.org/content/images/2019/03/30d1d13b-10f7-4d49-a968-fb902d0b7d2a.png-w331s)

之后即可直接退出进程：

![
](https://images.seebug.org/content/images/2019/03/f6de48ec-d9dc-4cce-9a24-82613fa3c7fb.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/832/>

