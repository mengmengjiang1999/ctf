## 背景

2018年5月15日，ESET发布文章“A tale of two zero-days”，该文章披露了今年3月ESET在恶意软件扫描引擎（VirusTotal）上捕获了一个用于攻击测试的
PDF文档。该PDF文档样本包含两枚0-day漏洞（CVE-2018-4990，CVE-2018-8120）以实现针对Adobe
Acrobat/Reader PDF阅读器的任意代码执行。其中CVE-2018-4990为Adobe
PDF阅读器的代码执行漏洞，而CVE-2018-8120则是Windows操作系统Win32k的内核提权漏洞，在获取代码执行权限后通过内核提权漏洞绕过Adobe
PDF阅读器的沙盒保护，实现任意代码执行。

## 漏洞利用回溯分析

360威胁情报中心分析确认披露的漏洞可被利用，在本文中我们试图通过公开的POC样本中针对Adobe
Acrobat/Reader代码执行的漏洞（CVE-2018-4990）利用过程进行详细分析，并记录整个分析过程。如有分析不当之处敬请谅解。

### 分析环境

操作系统：Windows 7 SP1

AdobeReader DC：1700920044

样本MD5：bd23ad33accef14684d42c32769092a0

### Payload功能解析

使用PDFStream打开漏洞样本，在尾部可以发现使用了JavaScript来触发利用漏洞：

![image.png](https://image.3001.net/images/20180528/15274878706963.png!small)  

通过分析可知，JavaScript中的前部分为PDF阅读器漏洞触发后加载运行的载荷，主要用于提权并执行恶意代码。而之后的JavaScript代码中则通过两个Array实例sprayarr及a1来实现内存Spray布局，这里需要注意的是a1对Array中奇数下标的element进行了释放，这是UAF类漏洞利用中常见的一种内存布局手法：

![image.png](https://image.3001.net/images/20180528/15274877813210.png!small)  

内存部署成功之后，接着在myfun1，myfun2中调用了两次触发double free的脚本，该脚本代码触发了double
free，从而导致后来的代码执行，触发double free的脚本：

varf1 = this.getField("Button1");  

最后对array实例sprayarr2进行赋值，每个element为一个长度为0x20000-0x24的ArrayBuffer，接着遍历sprayarr可以发现其对应的某一个sprayarr的element长度被修改为了0x20000-0x24（默认的长度为0x10000-0x24），此时通过超长的sprayarr[i1]即可修改相邻的sprayarr[i1+1]对象的len长度属性，从脚本代码中可以看到长度被修改为了0x66666666，最终通过该超长的sprayarr[i1+1]即可实现全内存的读写：

![image.png](https://image.3001.net/images/20180528/15274878155616.png!small)  

为此攻击者编写了专门的利用超长sprayarr对象实现全内存读写的函数：

![image.png](https://image.3001.net/images/20180528/15274878248238.png!small)  

获取全内存读写能力后，POC中通过伪造bookmarkRoot的对象实现代码执行：

![image.png](https://image.3001.net/images/20180528/15274878471834.png!small)  

POC运行之后会导致崩溃：

![image.png](https://image.3001.net/images/20180528/15274878856966.png!small)  

崩溃的原因为objecscript地址为硬编码，其中0x23A59BA4-0x23800000的地址并不适配测试的Adobe
Reader版本，从而导致崩溃：

![image.png](https://image.3001.net/images/20180528/15274878972791.png!small)  

通过对POC中的Payload功能解析，我们确定了POC中的几个需要分析的要点，这也是搞清楚整个漏洞利用的关键：

l sprayarr，a1在进行内存spray时的内存结构

l 触发double free的代码具体分析（var f1 = this.getField("Button1");）

l
sprayarr2初始化时的内存状态，其初始每个element长度正好是sprayarr中超长element的长度，这不禁让我们怀疑sprayarr2和某个sprayarr重合了（或许是第二点中的代码将sprayarr中的某个element释放了？然后被sprayarr2重用？）

### 脚本分析及调试

带着Payload功能解析中得出了漏洞利用关键点我们开始逐一进行调试分析。

####  **如何分析相关内存结构**

样本中具体的漏洞触发/利用部分都是JavaScript脚本，因此调试的时候我们可以依赖对应的三角函数实现具体的中断。为了获取对应的内存结构，我们可以直接修改对应POC，比如在POC中创建一个Array的实例myContent，将该Array中第0个element赋值为0x1a2c3d4f，以便于内存搜索，之后分别将我们感兴趣的变量赋值到该Array中即可很方便的定位内存
进行分析：

![image.png](https://image.3001.net/images/20180528/15274879091847.png!small)  

通过上述的三角函数断下后，此时通过搜索0x1a2c3d4f即可找到对应的myContent结构，如下所示地址0x062035f8开始的数据则为对应的tag（标记为0x1a2c3d4f），之后的四字节值0xffffff81标记该element的type类型，再往后依次为我们赋值的element，由于都是Array，所以type均为0xffffff87：

![image.png](https://image.3001.net/images/20180528/15274879346304.png!small)  

而为了获取sprayarr和a1的内存状态，我们可以在下图位置下三角函数断点来方便调试：

![image.png](https://image.3001.net/images/20180528/15274879252683.png!small)  

####  **sprayarr**

有了分析脚本中内存结构的方法，我们通过上述的办法定位到sprayarr的内存结构，可以看到element个数为0x1000，偏移c的位置包含指向具体内存element的指针0x07e94718：

![image.png](https://image.3001.net/images/20180528/15274879544404.png!small)  

进一步可以看到对应的每一个element对象的地址，由于sprayarr的element为ArrayBuffer，所以其对应的type为0xffffff87，从下标1开始全部都是type为0xffffff87的ArrayBuffer：

![image.png](https://image.3001.net/images/20180528/1527487958539.png!small)  

查看下标为1的element对象的内存结构如下所示，大的红框分别对应的sprayarr[1]和sprayarr[2]中的Arraybuffer对象，其内存为连续布局。每个Arraybuffer对象偏移+c的位置为具体的内存空间，下图中每个Arraybuffer对象的实际内存空间也是连续分布，而内存中的两个值相减则正好为Arraybuffer初始化时的长度（0x88dc760
- 0x88cc760=10000）：

![image.png](https://image.3001.net/images/20180528/15274879692588.png!small)  

进入到具体的Arraybuffer内存空间查看（0x88cc760），实际内存长度为ffe8（和分配的0x10000-0x24一致）：

![image.png](https://image.3001.net/images/20180528/15274879814715.png!small)  

而sprayarr连续布局的内存空间一直到延伸到地址0x18ce0038：

![image.png](https://image.3001.net/images/20180528/15274879934061.png!small)  

####  **al**

继续使用分析相关内存结构的方法查看此时的al array，同理偏移+c的地方指向了具体的element：

![image.png](https://image.3001.net/images/20180528/15274880118311.png!small)  

由于a1中的奇数下标的element在此时已经被释放，因此右侧element的内存都为0，此处选择al[2]进行查看，可以看到0x074926d8处保存了对应的长度，之后0x74926E0处指向脚本代码中对应的Uint32Array，起偏移+0xC的位置包含了指向具体内存的指针，而0x063008a0处即为对应的Uint32Array(252)，其长度为252*4=1008=0x3f0，而a1中有所Uint32Array最后都指向连续布局的内存空间：

![image.png](https://image.3001.net/images/20180528/15274880212575.png!small)  

对应的JavaScript脚本，其中a1i1，a1i1的值在此时分别为0x0d0e0048和0x0d0f0048：

![image.png](https://image.3001.net/images/20180528/15274880415660.png!small)  

Uint32Array(252)对应的内存布局（0x063008a0）：

![image.png](https://image.3001.net/images/20180528/15274880513371.png!small)  

释放的al[3]对象内存布局：

![image.png](https://image.3001.net/images/20180528/15274880602796.png!small)  

Uint32Array最终的内存布局（从0x06300890开始到0x88be180）：

![image.png](https://image.3001.net/images/20180528/15274880707786.png!small)  

####  **sprayarr2**

对sprayarr2的内存布局分析同样通过三角函数在sprayarr长度修改后断下：

![image.png](https://image.3001.net/images/20180528/15274880819630.png!small)  

sprayarr2的内存结构不过多展示，和sprayarr大致相同，此时sprayarr[i1]的长度已经被修改为0x1ffe8：

![image.png](https://image.3001.net/images/20180528/15274880982903.png!small)  

其后相邻element的len也被修改为0x66666666：

![image.png](https://image.3001.net/images/20180528/15274881103666.png!small)  

整个sprayarr的起始地址对应的内存数据：

![image.png](https://image.3001.net/images/20180528/1527488117522.png!small)  

检查sprayarr2内存，发现sprayarr中被修改的element和sprayarr2中的某个element指向同一片内存：

![image.png](https://image.3001.net/images/20180528/15274881424863.png!small)  

而sprayarr2中除了和sprayarr中一致的0x0d0e0058外可以发现，正常情况下，sprayarr2的element内存地址是从0x18d4a0d8开始的一片连续内存，而此处0x0d0e0058更像是漏洞利用中占坑的结果，这也肯定了我们之前的猜测，sprayarr中的内存被释放然后被sprayarr2占据，由于正好占据的长度为spayarr
element大小的两倍，因此可以猜测释放了两次，每次释放一个sprayarr element：

![image.png](https://image.3001.net/images/20180528/15274881649317.png!small)  

这里值得注意的是重用的内存地址0x0d0e0058似乎和POC中a1i1和a1i1的值非常接近，难道是通过这个地方控制的释放？

![image.png](https://image.3001.net/images/20180528/15274881699384.png!small)  

####  **释放函数定位**

为了验证到底是否是var f1 =
this.getField("Button1");相关代码导致了对应的a1i1和a1i1中的精确地址释放，通过以下windbg断点进行验证：

buMSVCR120!free ".if poi(esp+4)=0x0d0e0048{}.else{gc}"  

由于该函数在程序运行中会被大量调用，直接下断点会导致程序卡死，而且此处我们是为了验证var f1 =
this.getField("Button1");相关代码是否导致了sprayarr中的element被释放，因此可以在该代码前后加log函数，log被断下后再下对应的free断点并运行：

  
![image.png](https://image.3001.net/images/20180528/15274882213552.png!small)  
  

再次运行，调试器断下，可以看到此时正在释放地址0x0d0e0048中的内存，可以看到是JP2KLib!JP2kCopyRect+0xbae6调用了free释放函数：

![image.png](https://image.3001.net/images/20180528/1527488205894.png!small)  

查看JP2KLib!JP2kCopyRect+0xbae6即可定位到漏洞触发点（释放函数）：

![image.png](https://image.3001.net/images/20180528/15274882354427.png!small)  

动态调试分析可以发现漏洞函数运行到该loop前，其循环遍历的地址为eax，而eax的值为0x08AA2820（通过poi(poi(esi+0x48)+0x0c)获取）：

![image.png](https://image.3001.net/images/20180528/15274882455614.png!small)  

而0x08aa2820正好为脚本中的a1中某个释放的hole，即其大小为0x3f0：

![image.png](https://image.3001.net/images/20180528/15274882575537.png!small)  

而循环的校验值为0xff，0xfe*4 = 0x3f8，即可以访问到之后的a1i1和a1i1（0x0d0e0048，0x0d0f0048）：

![image.png](https://image.3001.net/images/20180528/15274882719177.png!small)  

之后继续访问并读取地址0x0d0e0048中的数据，并通过eax传入函数sub_10066FEA。

![image.png](https://image.3001.net/images/20180528/15274882817332.png!small)  

sub_10066FEA最终会调用MSVCR120!free释放该内存：

![image.png](https://image.3001.net/images/20180528/15274883413861.png!small)  

####  **精准的内存释放过程**

动态调试得知第一次调用var f1 =
this.getField("Button1");相关函数将导致0x0d0e0048对应的0x10000长度的内存被释放：

![image.png](https://image.3001.net/images/20180528/15274883542417.png!small)  

继续循环执行后，漏洞函数读取之后的地址0x0d0f0048中的数据，并释放对应大小为0x10000的内存，此时两次释放了总共0x20000长度的内存（两次释放由myfun1函数中的getField相关代码完成，myfun2中的getField删除不影响利用）：

![image.png](https://image.3001.net/images/20180528/15274883623776.png!small)  

通过对比hole被占据成buffer后的内存结构和正常a1的element就可以发现，该结构中寻址的起始地址要比之前的element低16个字节，因此获取a1i1和a1i1
element时的寻址编号分别是0xfd和0xfe：

![image.png](https://image.3001.net/images/20180528/15274883742310.png!small)  

最后通过sprayarra2赋值抢占该0x20000的内存，一旦分配成功，即变相的将sprayarr中0x0d0f0048位置的element的长度从0xffe8修改为0x11fe8：

![image.png](https://image.3001.net/images/20180528/1527488387864.png!small)  

####  ****

 **漏洞触发原理分析**  

分析到这还剩最后两个疑问。

1\. poi(poi(esi+0x48)+0x0c)这个被遍历的地址是如何被分配的？

2\. poi(poi(esi+0x48)+0x04)处的0xff来自何处？

 **第一个问题**

通过调试回溯，我们找到了具体的jp2h解析函数，如下所示：

![image.png](https://image.3001.net/images/20180528/15274884025663.png!small)  

其对应的参数如下：

参数1：getField("Button1")获取的图片的实际大小

参数2：poi(poi(esi+0x48)+0x0c)

参数3：图片的对象，可以看到包含的具体图片内容

函数调用前，poi(poi(esi+0x48)+0x0c)这个地址初始化为零：

![image.png](https://image.3001.net/images/20180528/15274884132005.png!small)  

继续跟踪调试可以看到，给poi(poi(esi+0x48)+0x0c)分配的内存地址大小为0x3f4，即一个a1中的hole：

![image.png](https://image.3001.net/images/20180528/15274884225049.png!small)  

而图片的实际大小则是0x3f4，正好用于填补a1的hole：

![image.png](https://image.3001.net/images/20180528/15274884314378.png!small)  

poi(poi(esi+0x48)+0x0c)为pg2h解析时分配，其实际大小和图片大小一致（0x3f4），正好填补a1中的hole，而在loop逻辑处理poi(poi(esi+0x48)+0x0c)时，由于长度为0xfe（0xfe*4
= 0x3f8），所以越界8字节刚好读到hole中残留的攻击者部署地址！

![image.png](https://image.3001.net/images/20180528/15274884485519.png!small)  

至此，可以清楚的知道漏洞触发的原因：越界读取，而我们也可以将漏洞触发的代码注释修改成越界读了：

![image.png](https://image.3001.net/images/20180528/15274884597488.png!small)  

 **0xff控制字**

其中控制loop循环次数的0xff，实际在poi(poi(esi+0x48)+0x4)的位置。

![image.png](https://image.3001.net/images/20180528/15274884665004.png!small)  

通过回溯分析，发现该值同样来自pg2h函数中的解析。

![image.png](https://image.3001.net/images/20180528/15274884715458.png!small)  

调试知道，其赋值来自于pg2h第三个参数，图片对象+10的位置。

![image.png](https://image.3001.net/images/20180528/15274884772263.png!small)  

067f4700这个变量主要用于标记解析图片时的指针，当解析图片时，该指针从图片的开始一直递加，直到图片尾部，如下图所示为扫描到图片中间时的值。

![image.png](https://image.3001.net/images/20180528/1527488485450.png!small)  

扫描完之后发现该指针指向后面的一片fffffff的内容，如下所示：

![image.png](https://image.3001.net/images/20180528/15274884949020.png!small)  

此时通过该指针给poi(poi(esi+0x48)+0x4)赋值时即为对应的0xff，从而导致之后的越界读（这个地方感觉应该是pclr后面应该还有字段，突然截断了导致了一个错误的残留指针）。

![image.png](https://image.3001.net/images/20180528/15274885023105.png!small)  

而打过补丁之后，poi(poi(esi+0x48)+0x0c)处的buffer被设置为零，不再指向之前a1中的某一个hole地址，从而无法通过释放函数前的校验：

![image.png](https://image.3001.net/images/20180528/15274885114391.png!small)  

### 遗留问题

脚本函数myfun1中
array2的赋值会导致部分a1里hole偏移249处，地址为0x0d0e0048的4字节数据被置空（因为其Uint32Array的大小为250，所以正好可以将偏移249的地址为0x0d0e0048处的4字节数据置空）。

![image.png](https://image.3001.net/images/20180528/15274885236516.png!small)  

如下所示，部分被填掉的a1 hole，可以看到对应的长度由0x3f0变成了0x3e8：

![image.png](https://image.3001.net/images/20180528/15274885343725.png!small)  

而直接删除后会影响漏洞触发，如下所示可以看到崩溃的原因在于漏洞函数释放的地址不合法导致，其遍历的buffer并不是我们分配的任何一个a1的element对象，因此猜测针对array2的循环遍历主要是用于将部分符合大小的脏
hole给填补上，这样var f1 = this.getField("Button1");相关代码调用的时候就能确保该buffer分配到我们指定的a1
hole中。通过调整array2的大小后发现，将大小值从0x200一直减少到0x70都能保证漏洞的稳定触发，但是低于0x70则会降低触发运行漏洞函数的几率，此处可以进一步研究：

![image.png](https://image.3001.net/images/20180528/15274885464169.png!small)  

## 整个漏洞利用过程

通过以上的分析过程可知漏洞函数JP2KLib!JP2kCopyRect+0xbae6中对访问的buffer检验有误，导致可以越界读取之后8字节的内容（0xff的获取有可能是pclr突然中断导致），所以该8字节的内容为攻击者可控，并在之后用于精确释放内存，最终通过精确释放，并重用该释放的地址，获取一个超长element，以实现全局内存读写，最终导致任意代码执行。

整个漏洞利用过程总结如下（编号和内存布局图中的编号对应）：

![image.png](https://image.3001.net/images/20180528/15274886351947.png!small)  

1、 通过heap spray
a1布置大量比buffer稍大的Uint32Array，将Uint32Array中249,250位置的element设置为需要释放的地址，之后将a1中奇数elemnt释放（以便于之后JP2KLib中解析图片时被分配到）。

2、 heap spray sprayarr布置之后需要释放的内存对象（即sprayarr）

3、
通过加载指定大小的jp2k图片，导致解析jp2k图片时分配的内存为之前某一个a1中的hole，之后运行到JP2KLib!JP2kCopyRect+0xbae6，漏洞触发越界读取249,250偏移处（即sprayarr中两个相连的elment）的内存并释放（合计0x20000），转化为类UAF的利用

4、 同上

5、 通过sprayarr2的赋值抢占释放的0x20000内存，一旦抢占成功，sprayarr中之前被释放的elment的长度就会被修改为0x20000

![image.png](https://image.3001.net/images/20180528/15274886683325.png!small)  

6、
最终通过精确释放，并重用该释放地址，获取一个超长element，以实现全局内存读写，再通过全局内存读写，伪造bookmarkRoot的对象实现任意代码执行！

## 参考

<https://srcincite.io/blog/2018/05/21/adobe-me-and-a-double-free.html>

<https://www.welivesecurity.com/2018/05/15/tale-two-zero-days/>

<https://twitter.com/klotxl404/status/998777393262166017>

  

