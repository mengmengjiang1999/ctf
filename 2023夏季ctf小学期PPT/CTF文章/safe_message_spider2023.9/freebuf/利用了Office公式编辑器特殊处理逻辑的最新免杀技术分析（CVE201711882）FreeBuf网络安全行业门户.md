##  
背景  

2018年8月24日，360威胁情报中心捕获到一个专门为乌克兰语使用者设计的钓鱼文档：该文档为RTF文件格式，且有详细的文档内容。360威胁情报中心经过分析确认这是首次发现的针对Office公式编辑器特殊处理逻辑而专门设计的用于绕过杀毒软件查杀的漏洞利用样本，涉及的漏洞正是CVE-2018-11882。

由于漏洞触发后的Payload已失效，360威胁情报中心在本文中专门针对样本使用的特殊免杀技术进行详细分析，并提醒各杀毒软件厂商做好针对该利用方式的检测。由于该免杀技术已经出现在在野利用的样本中，后续可能会有大量实际攻击样本使用该免杀手段逃过杀软检测，形成新的威胁。

![image.png](https://image.3001.net/images/20180910/1536551499_5b95ea4bbfd9e.png!small)  

文档内容

  

![image.png](https://image.3001.net/images/20180910/1536551506_5b95ea526e707.png!small)

Google内容翻译

## 免杀效果及样本特点

### 免杀效果

捕获到的样本在VirusTotal上查杀效果如下，首次上传时仅有4家杀软可以查杀，且仅有两家杀软能正确识别漏洞，如果稍加改动几乎可以躲过所有杀软的查杀：

![image.png](https://image.3001.net/images/20180910/1536551514_5b95ea5a92a0e.png!small)

### 样本特点-特殊的公式对象OLE

捕获到的特殊样本在RTF控制字“\objdata”的header后面居然不是一个CompoundFile Binary
Format（复合二进制文档）流，其紧跟的直接就是公式对象的数据（MTEF data），甚至连公式对象的头部数据（Equation Native
Header）都没有：

![Image](https://ti.360.net/uploads/2018/09/07/49e14dcd8d302234c4be52b667f071c3.png)  

而这样一个“畸形”的CVE-2017-11882漏洞利用文档，竟然能成功触发漏洞利用。

我们先复习一下正常的RTF文档中利用Office公式编辑器漏洞的方式，以CVE-2017-11882为例：

首先，RTF文档中会被插入一个objdata，紧跟在RTF控制字“\objdata”后，随后的数据结构为4字节的版本标识、format_id（embed代表嵌入式）、OLE流名字（Equation.3）等等：

 **Header** **：**

01050000 // version

02000000 // format_id (embed)

0b000000

4571756174696f6e2e3300 // "Equation.3" could be anything

0000000000000000

410f0000 // data length

在“\objdata”的header后紧跟OLE对象流，可以看到其特殊的CompoundFile Binary Format（复合二进制文档）标识：D0
CF 11 E0 …

![image.png](https://ti.360.net/uploads/2018/09/07/7ffb8c44f046d1adb780de0ea37b6710.png)  

紧跟的OLE对象流是一个复合二进制文件（Compound File Binary Format），通过解析可以看到这是一个Office
公式3.0编辑器对象，RootEntry带有一个公式编辑器的CLSID {0002CE02-0000-0000-C000-000000000046}：

![image.png](https://ti.360.net/uploads/2018/09/07/55ec32af81848cfd4a4778219fb9306d.png)

包含的Office 公式3.0编辑器对象由公式头+公式数据组成：

![image.png](https://ti.360.net/uploads/2018/09/07/dffc5004e73cc6002e9cd306b81ad620.png)

360威胁情报中心针对该特殊的漏洞利用技术进行了详细分析，整个分析过程如下。

## Office处理RTF中\objdata对象的流程

带着Office为什么可以正确处理嵌入的非OLE对象（且该对象是一个没有公式头的公式对象）这一疑问，我们详细分析了Office处理RTF文档中嵌入的\objdata对象的过程，整个处理过程可以用以下流程图表示：

![蓝信图片_20180910112715.png](https://image.3001.net/images/20180910/1536551731_5b95eb33e23cb.png!small)  

从整个流程来看，当WINWORD.EXE加载RTF文件并解析RTF文件格式后会调用函数ole32!OleConvertOLESTREAMToIStorage将指定的对象从OLE
1存储模型转换为OLE 2结构化存储对象。其内部调用的ole32!wConvertOLESTREAMTOIStorage负责从RTF文件中解析、转换OLE
1对象到OLE 2存储对象，最后ole32!GenericObjectToIStorage函数负责将OLE
2存储对象通过剪切板的方式传送给EquEdt32.exe进程处理：

![image.png](https://ti.360.net/uploads/2018/09/07/2801b6e4868629e05ccaf3aed8632897.png)

首先ole32!wConvertOLESTREAMTOIStorage函数将具体事务交给Ole32!OLESTREAMToGenericObject：

![image.png](https://ti.360.net/uploads/2018/09/07/911381cbce5e2404d32c4c2dae5210ad.png)

Ole32! OLESTREAMToGenericObject函数会完成OLE
1对象读取及转换，内部会调用OLE1StreamToUL和OLE1StmToString（内部也调用OLE1StreamToUL函数）读取OLE1对象Version、format_id、ClassName(Prog
ID)、static object、linked nor an
embedde、topic、Item、NativeData等信息，也就是处理\objdata的header部分：

![image.png](https://ti.360.net/uploads/2018/09/07/9ba8156e41d8ab489e11972788eea792.png)

  

![image.png](https://ti.360.net/uploads/2018/09/07/78dd71eeb651ade0d0ee8be9c98938b7.png)

同样可以通过oletools的rtfobj工具查看对应的\objdata得到相同信息：

![image.png](https://image.3001.net/images/20180910/1536551810_5b95eb82c12a2.png!small)

进一步会判断format_id是否为FMTID_EMBED（linked nor
embedde），然后调用wCLSIDFromOle1Class函数读取Ole1对象的CLSID：

![image.png](https://image.3001.net/images/20180910/1536551836_5b95eb9c2c4ec.png!small)

  

![image.png](https://image.3001.net/images/20180910/1536551841_5b95eba1b9683.png!small)

wCLSIDFromOle1Class函数判断传入的szProgID是否是名字为“OLE2Link”的对象，如果是则返回CLSID_StdOleLink，否则交给代理函数CLSIDFromOle1Class转换Ole1的流名字到对应的CLSID（也就是转换流名称Equation.3到对应的clsid）：

![image.png](https://image.3001.net/images/20180910/1536551848_5b95eba822cb8.png!small)

CLSIDFromOle1Class交给代理函数wCLSIDFromOle1Class处理：

![image.png](https://image.3001.net/images/20180910/1536551854_5b95ebaeba56f.png!small)

wCLSIDFromOle1Class函数将打开注册表HKEY_CLASSES_ROOT\\[szProgID]（此处为HKEY_CLASSES_ROOT\Equation.3）查询其CLSID，如果查询成功则调用wGUIDFromString函数得到GUID返回：

![image.png](https://image.3001.net/images/20180910/1536551860_5b95ebb4e6b7a.png!small)

如果通过流名称查询不到CLSID则调用Ole10_CLSIDFromString函数遍历OLE32中内置的Object名称，发现相同则返回其CLSID：

![image.png](https://image.3001.net/images/20180910/1536551870_5b95ebbe536c8.png!small)

  

![image.png](https://image.3001.net/images/20180910/1536551876_5b95ebc485e50.png!small)

ole32! GenericObjectToIStorage函数根据返回的CLSID注册剪切板，并把OLE 2数据写入剪切板：

![image.png](https://image.3001.net/images/20180910/1536551883_5b95ebcb09cc7.png!small)

随后WINWORD.EXE会调用ole32!Load函数加载该CLSID对应的对象，最终定位到函数ole32!CoIsOle1Class，该函数判断CLSID是不是有效的Ole1Class对象，不是有效的Ole1Class对象则直接返回，是有效的Ole1Class对象则调用接口处理剪切板数据，以下是加载处理公式对象的过程：

![image.png](https://image.3001.net/images/20180910/1536551890_5b95ebd2e7440.png!small)

  

![image.png](https://image.3001.net/images/20180910/1536551898_5b95ebda982a7.png!small)

特别注意的是，WINWORD.EXE在调用ole32!OleLoad函数前，会解析CFB文件将CFB文件的流对象写入剪切板并且将Embedded对象数据块（即d0cf11e0a1b11ae10对应的块）的Clsid值覆盖之前通过ProgID获取的Clsid，也就是最终以Embedded对象数据块内的clsid为准：

  

![image.png](https://image.3001.net/images/20180910/1536551903_5b95ebdfc54c6.png!small)

## 公式编辑器（Equation）处理公式数据的特殊逻辑

最后，Office将公式对象数据传递给Equation处理：

EquEdt32.exe进程能够处理两种流，分别是Equation Native和01Ole10Native流，Equation
Native是较为常见的流格式，一般以0x1C开头。而01Ole10Native流在EquEdt32.exe打开Equation
Native流失败的情况下才使用：

  

![image.png](https://image.3001.net/images/20180910/1536551909_5b95ebe5d2c00.png!small)

随后会根据打开的流读取流内容，
如果是01Ole10Native流则先读取4字节流大小，如果不是则读取0x1C字节大小的EquationNative头，然后才从Equation
Native头解析流01Ole10Native大小，最后分配内存用于读取01Ole10Native流数据：

  

![image.png](https://image.3001.net/images/20180910/1536551914_5b95ebeabf9ba.png!small)

可以看到，本次捕获到的免杀样本在处理过程中，由于读取Equation
Native失败，所以Equation通过读取01Ole10Native流大小来直接处理后面附加的公式数据（03010103…）：

![image.png](https://image.3001.net/images/20180910/1536551921_5b95ebf16ee52.png!small)

随后再次调用IStream::Read(coml2!CExposedStream::Read)函数读取流数据：

![image.png](https://image.3001.net/images/20180910/1536551925_5b95ebf5ecbeb.png!small)

  

![image.png](https://image.3001.net/images/20180910/1536551990_5b95ec365a109.png!small)

  

![image.png](https://image.3001.net/images/20180910/1536551996_5b95ec3c2d783.png!small)

最后将流数据传入sub_42F8FF函数实现具体01Ole10Native流处理，最终成功触发漏洞：

  

![image.png](https://image.3001.net/images/20180910/1536552001_5b95ec41bdd74.png!small)

  

![image.png](https://image.3001.net/images/20180910/1536552008_5b95ec4840669.png!small)

## 总结免杀原理

我们回顾Office处理RTF中\objdata对象的流程可以总结出该免杀样本触发Equation漏洞的过程：

1、
攻击者在\objdata后附带非CFB格式的数据（只有公式数据的01Ole10Native流），迫使Office通过\objdataheader中的流名字（Equation.3）来查找对应处理的clsid，转入处理流程。

2、
由于附带的是公式对象的01Ole10Native流（030101…部分数据），所以EquEdt32.exe进程打开EquationNative流失败，转而以\objdata
header中指定的数据长度直接处理01Ole10Native流，触发漏洞利用。

由于该免杀样本\objdata后附带非CFB格式的数据（D0 CF
11…），而正常情况必然是携带的CFB数据，并且以CFB数据中获取的clsid为准寻找处理该对象的程序（如Equation），这直接导致绕过大部分杀软的检测逻辑。并且后续的公式数据没有公式对象头等特征，也使得部分杀软抓瞎，这是该样本绕过杀软检测的主要原因。

## IOC

**MD5**  
---  
0a8efb742ef488bcb8ccd6b616125eea  
  
## 参考

[1].<https://ti.360.net>

[2].<https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2017-11882>

[3].<https://github.com/Paolo-Maffei/OpenNT/blob/5c5b979ec08c17d3ca2eb70e8aad62d26515d01c/com/ole32/ole232/ole1/ostm2stg.cpp>

