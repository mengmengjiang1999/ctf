# Office文件格式基础知识（1）

阅读量 **962531**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-29 11:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01f25457e37ee9c490.jpg)

    
    
    本文系作者此前研究office文件格式解析及漏洞挖掘和分析时梳理的部分基础知识，文章部分内容可能会借鉴他人成果，由于时间久远所以无法一一考证。本文仅限于初学者作为参考，如有笔误，请见谅。
    

## Office文档格式简要介绍

OpenXML（OOXML）是微软在Office 2007中提出的一种新的文档格式，Office
2007中的Word、Excel、PowerPoint默认均采用OpenXML格式。OpenXML在2006年12月成为了ECMA规范的一部分，编号为ECMA376；并于2008年4月通过国际标准化组织的表决，并于两个月后公布为ISO／IEC
29500国际标准。

另一种结构是office 97-03的存储规范：OLE。它是一种对象链接和嵌入的技术，该技术可以包含文本，图形，电子表格甚至其他二进制数据。

###  Docx（Open XML）文档结构

Docx这种新的word 格式有三个主要的组成部分：部件、内容类型和关系。

**部件**

部件就是对应于office文档解压后的一个个文件。这些文件都是包中的文档部件。

Word2007的文档部件大致有以下几种：

> 注释；
>
> 格式定义；
>
> 列表定义；
>
> 页眉；
>
> 图表；
>
> 关系；
>
> 文档内容；
>
> 图片。

在word中，使用单独的文件（xml）来表示文档中的每个部分以及附加的内容。他们需要依赖于各部件之间的正确关系保证文件的完整和有效性，如果可以准确保持部件之间的关系，那么文件结构可以任意更改。

以docx文档为例，说明openxml文档内容的结构。随手建立一个docx文档，使用zip解压到文件夹中，他的目录结构如下：

![](https://p1.ssl.qhimg.com/t011e27a7ab3a6a702d.png)

事实上，在word2007及以上的版本当中，一个文档则是由一个文件夹（或者说容器），由内部的部件各自定义属性和数据，并相互依赖而产生的。一个文件可能会包含这些目录和组件：

**[Content_Types].xml**

这个文件描述的是整个文档内容的类型，把各个xml文件组合成一个整体。

**docProps文件夹**

这个文件夹中的xml记录了docx文档的主要属性信息

Core.xml：描述文件的创建时间，标题，主题和作者等给予open xml约定文档格式的通用文件属性

App.xml：描述文档的其他属性，文档类型，版本，只读信息，共享，安全属性等特定的文件属性

**rels 文件夹**

这个文件夹存放了所有指定的rels文件

**rels文件**

这些文件描述了文档结构中的起始关系，也可以叫做关系部件

**item1.xml**

包含了一些文档中出现的数据。例如自定义XML数据部件。

**内容类型**

每个文档部件都有一个特定的内容类型。一个部件的内容类型描述了这种文件类型的内容。例如，XML部件包含了Word
XML格式定义的标记，而内容类型可以用来分析文档的组成。

典型的内容类型是以word application开头，然后是厂商的名称。在内容类型中，word
vender被简写为vnd。所有内容类型都被指定为以application/vnd.ms-word开头。如果内容类型是一个XML文件，那么它的URI将以+xml结尾。其它的非XML内容的类型，例如图片，则没有这种结尾。下面是一些典型的内容类型：

1.application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml

它是一个描述Word文档中的尾注文档部件的内容类型。其中，+xml表示它是一个XML文件。

2.application/vnd.openxmlformats-package.core-properties+xml

它是一个描述核心文档属性部件的内容类型。其中，+xml表示它是一个XML文件。

3.image/png

图片的内容类型。其中没有+xml部分 － 表示内容类型不是XML文件。

**部件关系**

部件关系记录了文档部件之间的逻辑连接，比如根文档部件拥有一个`http://schemas.openxmlformats.org/package/2006/relationships/header`类型到application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml  
内容类型部件的关系。这表示部件之间的关系是，目标部件是源部件的页眉。而这个页眉部件可能也有自己的关系。在包中，可以通过_rels目录中的.rels文件进行关系定位。

构建关系的方法是：每一个关系中都有一个源一个目的，源是关系命名的部件。例如，document.xml.rels中所有的关系都将document.xml作为它们的源。每个.rels文件都包含一个<relationships>元素，每个元素都对应一个ID，包括目标部件的内容类型。

![](https://p1.ssl.qhimg.com/t0100c12dfbda0e0f77.png)

###  Doc文档结构

Word 97-03的后缀是doc，doc文件本身是一个ole类型文件。OLE (Object Linking and Embedding)文 件 主 要
由 storages 和 streams  
组成，而ole本身其实是一种面向对象的技术，该技术允许程序之间链接和嵌入对象数据，建立复合文档。

![](https://p3.ssl.qhimg.com/t01d6904e85bf964cda.png)

WordDocument stream 中保存的最重要的数据结构是 FIB（File InformationBlock），FIB 中除了保存
doc文件的一些基本信息（如格式版本）之外，大部分字段是指向其它结构的指针和标识其结构大小（见图2）。例如 fcClx 字段表示 Clx 结构在 Table
stream中的偏移，lcbClx 字段标识
Clx结构的大小。类似的，名称以“fc”开头的字段都表示对应结构在某个stream中的偏移，对应的以“lcb”开头的字段则表示其结构大小。

![](https://p1.ssl.qhimg.com/t01def8024c3d4e7905.png)

###  rtf文档结构

富文本格式（Rtf, rich text
format）是微软的文本和图像信息交换制定的格式。Rtf文件可以划分为文件头和文档区两个部分组成。文件头和文档区由文本、控制字和控制符组成，同时利用{…}来表明层级关系。

Rtf文件内容 | 控制字 | 解释  
---|---|---  
文件头 | rtfN | 版本号  
| fonttbl | 字体表  
| filetbl | 文件表  
| listtable | 编目表  
文档区 | info | 信息组  
| pict | 图片  
| object | 对象  
| sv | 绘图对象值  
| sn | 绘图对象名称  
| objupdate | 自动更新机制。  
  
( **objupdate很重要，攻击样本中经常使用，确保OLE对象自动加载、更新** )

## OLE简单说明

前面已经说到OLE的基本概念，现在我们先说说不同格式文档的OLE嵌入。OLE就其本质而言，是COM对象的子集，是一种基于组件对象模型（COM）的对象链接和嵌入技术。

###  不同嵌套控制字及对应的文件格式

OLE对象控制字和相应解释如下：

对象类型 | 解释  
---|---  
objemb | 嵌入图片、文档、音频等  
objlink | 嵌入链接文件  
objautlink | 嵌入自动链接对象类型。  
objsub | Macintosh版管理签署对象类型。  
objpub | Macintosh版管理发布对象类型。  
objicemb | MS Word for Macintosh可安装命令（IC）嵌入对象类型。  
objhtml | 超文本标记语言（HTML）控件对象类型。  
objocx | 嵌入ActiveX控件  
  
OLE对象数据控制字和对应解释如下：

对象数据 | 解释  
---|---  
objdata | 采用特定格式表示的对象数据；OLE对象采用OLESaveToStream结构。常见恶意文件样本关键字。  
objalias | Macintosh编辑管理器发行对象的别名记录。  
objsect | Macintosh编辑管理器发行对象的域记录。  
  
###  OLE对象数据结构解析

上面的表中，3个对象数据控制字都可以被对象类型引用。OLE对象数据包括头部（ObjectHeader）和数据流（ObjectStream），它们是通过D0CF11E0A1B11AE1  
标志符进行区分。其中头部由OLE 版本（4 字节）、格式ID（4
字节）、程序名长度（4字节）、程序名和数据流大小（4字节）组成。用一个CVE-2017-0199溢出文档中嵌入的OLE对象，可以对它做一下解析。对象内容如下：

![](https://p0.ssl.qhimg.com/t014a784fb57ba0f81d.png)

{*objdata  
0105000002000000090000004f4c45324c696e6b000000000000000000000a0000
**d0cf11e0a1b11ae1**
000000000000000000000000000000003e000300feff0900060000000000000000000000010000000100000000000000001000000200000001000000feffffff0000000000000000fffffffffffffffffffffffffffffffffffffff

上面数据流中加粗字符前面的是OLE对象的头部，各字段解析内容如下：

数据 | 解释  
---|---  
01050000 | OLE Version  
02000000 | Format ID  
09000000 | ProgName Size（0x09）  
4f4c45324c696e6b00 | ProgName (OLE2Link)  
000a0000 | Data Size  
  
**d0cf11e0a1b11ae1** 后面的数据就是ObjectStream的内容了，解析的时候需要将ascii  
转换成hex才可以识别。

![](https://p5.ssl.qhimg.com/t010c9498feba4bd05d.png)

###  部分office文档混淆免杀技术

**RTF文档格式混淆**

**文件头混淆**

Rtf文档正常的文件头是 **{rtf1** ，但解析器只识别前四个字节{rt}，所以可以通过修改文件头达到样本混淆的效果。

{rt{{{{info{authorismail-
{rtÈÐÏ

**无用字符混淆**

经过测试，rtf空格回车和不可见字符不会被解析器识别，所以可以通过在rtf样本中嵌入0x20以下和0x7f以上的字符完成混淆效果。

{rtf1object112objocx9912{*objdata54541 {{0……

**混淆objdata头部**

前文已经介绍过，objdata是OLE嵌入对象数据控制字，实际测试、objdata可以写成: bjdata (空格为0x00)这种形式

**大小写混淆**

Rtf解析器对大小写不敏感，而OLE data部分常用小写形式，所以OLE标识符可以写成 **D0cf11e0a1b11ae1** 或任意大小写组合。

**多重嵌套**

rtf中的组可以多重嵌套，但解释器会跳过无用的组和控制符，所以可以通过嵌套无用组达到混淆效果。

{{}{}{}{}ddd{}ddd}

**Bin混淆**

rtf  
binxx关键字表示后面的xx个字符将以二进制方式读取，实质上就是一段二进制的OLESS头部的数据。所以可以通过构造binxx后面的若干字节达到混淆的效果。

**利用OLE特性的免杀技术**

目前发现了一些通过插入OLE2Link达到免杀效果的样本，位置比较灵活：

  1. 页脚文件中有一个OLE2Link对象

![](https://p3.ssl.qhimg.com/t012cf53d8935b03ab9.png)

  1. rels文件中插入OLE2Link

![](https://p5.ssl.qhimg.com/t01a8592233455e84fd.png)

目前github已有类似的[开源项目](https://github.com/ryhanson/phishery)，可以生成插入OLE2Link对象的样本文档。将link指向的地址设为bit.ly等类似提供短链接生成的服务，可以增强免杀效果。

**构造特殊的OLE对象**

前面已经说到，正常RTF文档插入OLE时，首先是控制字“objdata”，然后是OLE 版本（4字节）、格式ID（4 字节）、程序名长度（4
字节）、程序名和数据流大小（4字节），而后是Compound File Binary Format（复合二进制文档）的标识符，也就是
**d0cf11e0a1b11ae1**
，后面是数据流（ObjectStream）。但是可以通过构造特殊的OLE对象，通过去掉部分结构上的关键字达到绕过杀软查杀的效果。

![](https://p5.ssl.qhimg.com/t019f565379b25816e6.png)

（360威胁情报中心-利用Office公式编辑器特殊处理逻辑的免杀技术分析（CVE-2017-11882））

这是上面是一个seebug发现的样本。我们可以看到objdata后面的头部没有问题，但是没有D0 CF 11
E0的标识符。至于为什么能够成功打开公式编辑器并利用漏洞，下面解析一下。

![](https://p1.ssl.qhimg.com/t01e2db9de9a1f4d12a.jpg)

（360威胁情报中心-利用Office公式编辑器特殊处理逻辑的免杀技术分析（CVE-2017-11882））

在这个过程当中需要注意的是，WINWORD.EXE在调用ole32!OleLoad函数前，会解析CFB文件将CFB文件的流对象写入剪切板并且将Embedded对象数据块（即d0cf11e0a1b11ae10对应的块）的Clsid值覆盖之前通过ProgID获取的Clsid，也就是最终以Embedded对象数据块内的clsid为准，
**所以CLSID仍然是Equation.3对应的CLSID** 。所以office 能够将公示对象传递给Equation处理。

Equation可以逻辑上可以处理Equation Native和Ole10Native两种流，在EquEdt32.exe打开Equation
Native流失败的情况，会处理OleNative流。

![](https://p1.ssl.qhimg.com/t011dcc9e37ff1126fa.png)

![](https://p4.ssl.qhimg.com/t0101e222d8f45375b5.png)

（360威胁情报中心-利用Office公式编辑器特殊处理逻辑的免杀技术分析（CVE-2017-11882））

然后就可以转入漏洞触发环节。根据上面的流的处理逻辑可以大致总结出免杀样本触发Equation漏洞的过程：

  1. 攻击者在objdata后附带非CFB格式的数据（只有公式数据的01Ole10Native流），迫使Office通过objdata  
header中的流名字（Equation.3）来查找对应处理的clsid，转入处理流程。

  2. 由于附带的是公式对象的01Ole10Native流（030101…部分数据），所以EquEdt32.exe进程打开Equation  
Native流失败，转而以objdata  
header中指定的数据长度直接处理01Ole10Native流，触发漏洞利用。

这种方式可以明显避过杀软对Equation.3 ProgID的检测，也可以通过去掉CFB标识符躲避杀软的检测。

## 深入理解OLE

为了深入理解OLE的原理，需要了解当含有OLE的文档打开时会有什么操作

![](https://p1.ssl.qhimg.com/t01ee06c1e573fd5d88.png)

####  关于OLE加载初始化

OLE加载初始化是依靠ole32!OleLoad() API完成的

![](https://p3.ssl.qhimg.com/t0157b6e9c3559d534d.png)

![](https://p1.ssl.qhimg.com/t01b40ab008e75f322c.png)

这个API的主要步骤：

步骤1：调用CoCreateInstance来初始化OLE对象

![](https://p3.ssl.qhimg.com/t01b42f089018bc1b14.png)

这里的CLSID在rtf和openxml文档中获取的方法不同：

> rtf是通过OLE对象头部的 _progID_ 进行转化得来的
>
> openxml是通过OLESS格式的二进制数据中读入的

步骤2：调用IPersistStorage来初始化OLE对象的初始状态(数据)

![](https://p3.ssl.qhimg.com/t01f66d6cd9aaf49ba0.png)

MSDN对该函数的定义是：允许容器应用程序将存储对象传递给其中一个包含的对象，并加载和保存存储对象。  
此接口支持结构化存储模型，其中每个包含的对象都有自己的存储，嵌套在容器的存储中。

![](https://p1.ssl.qhimg.com/t019f2b62ed0cf77783.png)

OLE初始化时，就是会用load()方法为OLE对象加载初始化的状态。

这里的Storage Data在rtf和openxml文档中获取的方法不同：

Rtf是OLE1 NativeData中获得的，

![](https://p1.ssl.qhimg.com/t012fd219a957999f4f.png)

Openxml格式的Storage Data在OleObject.bin文件中的Contents节中获得。

![](https://p2.ssl.qhimg.com/t0143c791f6056bfd0b.png)

###  关于OLE Verb动作

关于OLE Verb动作

![](https://p3.ssl.qhimg.com/t0190fbe7bf063e9644.png)

OLE  
Verb动作本质上是依靠调用IOleObject::DoVerb方法完成的。MSDN对该方法的定义如下：

![](https://p3.ssl.qhimg.com/t01fb770b0751f74560.png)

这里需要注意的是第一个参数，iVerb。这个参数的MSDN定义是：IOleObject
::EnumVerbs返回的OLEVERB结构中的verb动作的编号。

###  利用OLE可达的攻击面

**IPersistStorage::Load**

通过构造伪造的Storage数据，可能会在load数据时造成内存破坏。多数已发现的OLE漏洞都是利用IPersistStorage::Load方法。

**CVE-2012-0158**

调试过程：

Windbg加载winword打开poc.doc，访问违例，EIP指向0x41414141，查看函数调用栈发现没有任何内容。利用Immunity进行调试，查看栈的内容是这样的。

![](https://p1.ssl.qhimg.com/t01ed811287d9e9937c.png)

从栈结构看，0x275c8a0a很可能是崩溃函数的返回地址。

IDA查看静态代码是这样的。

![](https://p2.ssl.qhimg.com/t01b00e0b992cfd8d4e.png)

![](https://p2.ssl.qhimg.com/t018567c60bd79cc69a.png)

![](https://p4.ssl.qhimg.com/t01dfca77c54530ef72.png)

可以看到sub_275c876d是一个memcpy的代码，在这个函数里，两次完成memcpy，第一次是copy  
一个0xc字节的数据段，并判断dwBytes也就是第一次copy的最后四个字节是否大于等于8，如果条件成立则第二次复制。这里面有一个问题，sub_275c89c7只分配了0x14字节的栈空间，第一次copy利用了0xc字节空间，后面只有0x8字节空间可以利用，而第二次复制的数据大小是受第一次复制结构体的最后一个字节的成员控制的，如果它大于8，那么复制将会破坏sub_275c89c7的栈空间，造成栈溢出。事实上调试过程中也可以看到，函数处理数据时首先会匹配0x6A626F43地址中的内容。即验证读入的是否为Cobj对象的数据。而CVE-2012-0158溢出文档中查找Cobj对象可以看一下，Cobj对应的hex流为’
**436f626a** ‘

![](https://p0.ssl.qhimg.com/t01057b60e1334567fa.png)

Cobj对象的长度为0x8282，就一定会溢出的了。研究人员分析，这个漏洞本质上就发生在IPersistStorage::Load这个方法当中。

**IOleObject::DoVerb**

**这个攻击面主要代表是沙虫漏洞（CVE-2014-4114），如有必要的话会在后续中给出调试过程的信息**

**CLSID相关联的DLL加载**

注册表项HKEY_CLASSES_ROOTCLSID中存放着dll相关的CLSID，前面OLE初始化的内容已经说过，OLE对象由CLSID指定，CLSID在rtf和openxml文档中都可以被获取，也就是说可以
**由攻击者自由配置。** 这样就会导致很多后果：

  1. 可以在OLE容器中配置没有ALSR的dll，绕过ALSR（比如mscormmc.dll）
  2. 内存破坏，通过加载一个“未准备好的”dll，可以破坏内存（CVE-2015-1770）
  3. Dll劫持，可以通过控制工作目录去加载想要执行的dll（CVE-2015-2369）

## Office文档xml解析类的攻击面

Msxml库是office负责解析xml数据的动态链接库，漏洞通常发生在异构的标签数据，有的是因为标签不正确闭合，有的是通过精心构造数据混淆数据类型，如有必要，该部分内容将在后续中分享。

## 调试office漏洞的部分工具

  1. Windbg+符号文件
  2. IDA pro + bindiff工具
  3. Immunity debugger（崩溃的时候方便查看栈结构）
  4. Github oletools项目
  5. Offvis工具
  6. Olefileview工具
  7. 010 editor（支持ole格式）
  8. Msdn

## 部分参考链接

<https://www.blackhat.com/docs/us-15/materials/us-15-Li-Attacking-Interoperability-An-OLE-Edition.pdf>  
<http://hustlelabs.com/stuff/bh2009_dowd_smith_dewey.pdf>  
<https://docs.microsoft.com/en-us/office/open-xml/understanding-the-open-xml-file-formats>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **R0fM1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175548](/post/id/175548)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Office](/tag/Office)

 **+1** __9赞

 __收藏

![](https://p2.ssl.qhimg.com/t010f09718d00a0b6e4.png) R0fM1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

