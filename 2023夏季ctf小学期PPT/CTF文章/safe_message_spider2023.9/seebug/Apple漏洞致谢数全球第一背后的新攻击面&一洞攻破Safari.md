**作者：光年  
公众号：[蚂蚁安全实验室](https://mp.weixin.qq.com/s/9dmQH4qIw95Gsx92wLSr6w)**

蚂蚁安全光年实验室从2020年4月份开始专注到 Apple 产品漏洞挖掘中，仅用了三个季度的时间，就累计拿下苹果47次致谢——
**致谢数排名2020年Apple漏洞致谢数全球第一** 。

47次漏洞致谢中，包含了系统库、浏览器、内核等多个维度层面，几乎都是高危漏洞，部分漏洞评分达到了“严重”级别，挖掘的数量和质量都处于全球领先位置。

![](https://images.seebug.org/content/images/2021/02/0b02dcb2-c93f-4584-8873-c7f40a88b47c.png-w331s)

2020年各大公司获得的苹果致谢次数排名

以往对苹果Safari浏览器的漏洞研究往往聚焦于DOM或者JS引擎，但是像Safari所使用的一些系统库，例如音频库，视频库，字体库等等很少受到关注，鲜有这些模块的漏洞在Safari中利用成功的案例。

部分原因是由于Safari内置一些缓解措施，导致这些模块中的漏洞很难单独利用，故而外界对这些模块的关注度较低。我们在对Safari的安全机制做了整体分析后判断，这些系统库中的洞是完全可以绕过Safari内置的缓解措施，从而控制Safari浏览器，攻击者进而可以在用户的机器上执行恶意代码，窃取浏览器cookie、历史记录、用户名密码等敏感信息。

我们在20年4月份左右开始投入到对这些系统库的漏洞挖掘当中，采用的是专家经验和Fuzz相结合的方式。光年实验室自研了AntFuzz引擎，该引擎是用rust语言编写，稳定性和性能与同类工具相比都有显著提升。

AntFuzz对当今主流的Fuzz方法体系进行了吸收融合，在易用性和接入能力上面也有很大的改善。在安全研究员筛选出一些可能的攻击面的基础上，AntFuzz会针对特定攻击面自动化生成高质量的Fuzz
Driver，再通过定制化的种子以及变异算法的选取，来进行高效漏洞挖掘。AntFuzz的这些关键特性支持我们取得了非常丰富的战果，挖掘出了大量高危漏洞。

在2020年天府杯中，光年实验室是全场唯一实现Safari full-chain
exploit的参赛团队（即从浏览器入口到获取用户目标机器上的最高权限）。在这个攻击中，我们仅依托发现的一个WebAudio漏洞就实现了Safari浏览器的远程代码执行，绕过了Safari的所有安全缓释措施。

该漏洞CVE编号为CVE-2021-1747，苹果官方已在最新的macOS系统、iOS系统中修复了该漏洞。这也是国内顶尖软硬件破解大赛中，首次通过系统库API来攻破Safari浏览器。下面我们会分享相关的漏洞利用技巧。

## 漏洞成因

漏洞存在于WebAudio模块当中，在解析CAF音频文件的时候会产生越界写。漏洞存在于ACOpusDecoder::AppendInputData函数中，(1)处有一个类似于边界检查的代码，但是最终被绕过了，(2)处调用memcpy函数，造成了越界写。

    
    
    __int64 __fastcall ACOpusDecoder::AppendInputData(ACOpusDecoder *this, const void *a2, unsigned int *a3, unsigned int *a4, const 
    AudioStreamPacketDescription *a5)
    {
      ...
    
      if ( a5 )
      {
        v8 = a5->mDataByteSize;
        if ( !a5->mDataByteSize || !*a4 || (v9 = a5->mStartOffset, (a5->mStartOffset + v8) > *a3) || this->buf_size ) // (1). 绕过这里的边界检查
        {
          result = 0LL;
          if ( !v8 )
          {
            this->buf_size = 0;
    LABEL_19:
            v13 = 1;
            v12 = 1;
            goto LABEL_20;
          }
          goto LABEL_16;
        }
        if ( v9 >= 0 )
        {
          memcpy(this->buf, a2 + v9, v8);   //（2）. 越界写发生的位置
          v14 = a5->mDataByteSize;
          this->buf_size = v14;
          result = (LODWORD(a5->mStartOffset) + v14);
          goto LABEL_19;
        }
        ...
    }

![](https://images.seebug.org/content/images/2021/02/92a3a858-2069-4e35-a811-5fcb40f6ca9c.png-w331s)

先简单介绍一下CAF文件格式，我这里画了一幅简化版的CAF文件格式图。CAF文件开头是File
Header，之后是由各种不同类型的Chunk组成，每个Chunk都有一个Chunk Header，记录了该Chunk的大小。

Desc Chunk主要存储了文件的一些元数据，Data Chunk里面存储了所有的Packet，Packet Table
Chunk则记录了每一个Packet的size。在解析的时候会先读取Packet Table Chunk，获取每一个Packet的大小，然后再去Data
Chunk里面读取。

为了分析这个漏洞，我特意编写了一个010 Editor模板来对CAF文件进行解析。

![](https://images.seebug.org/content/images/2021/02/c79cc38b-7991-468f-bb52-8bc9954bf5f7.png-w331s)

然后我们分析一下造成crash的CAF文件，用010 editor的模板文件跑一下，可以看到如下输出：

![](https://images.seebug.org/content/images/2021/02/14729be3-fce7-44f7-97a7-ec8eb1faeee1.png-w331s)

第一列是packet的序号，第二列是packet的size。可以看到，第114个packet的size是负数，可以推测程序在处理size为负的packet的时候出了问题。接下来就是如何利用这个漏洞了。

## 将越界写漏洞转化为任意地址写

这里我首先对相关代码做了逆向分析，被越界写的buffer是存在于ACOpusDecoder这个结构体的内部，这个结构体的字段如下所示：

![](https://images.seebug.org/content/images/2021/02/cbc2d428-42c5-4374-a9c8-8273a70e4d7e.png-w331s)

被越界写的是buf字段，共有1500个字节，后面的buf_size，controled_field, log_obj, controled
这几个字段都是我们可以控制的。通过一定的调试加逆向，可以发现log这个对象在后面有用到，而且可以造成任意地址写。

接下来我们的目标有两个，一是走到任意地址写的位置，并且写的值要满足一定的条件；二是在造成任意地址写之后程序不会立马崩溃。第一步的话我们通过控制一些变量的值就可以做到。

![](https://images.seebug.org/content/images/2021/02/5f97b21d-df90-4be9-8634-faa8d2a1591f.png-w331s)

![](https://images.seebug.org/content/images/2021/02/4fc740a7-2011-4788-8a88-7b0f0453ef7e.png-w331s)

第二步发生了点波折。任意地址写之后，会发现程序总会在opus_decode_frame中崩溃，按照常规的思路分析，如果造成了任意地址写就会导致崩溃，如果不崩溃，又没法造成任意地址写。但是我在逆向的过程中发现，opus_packet_parse_impl这个函数在解析packet的时候没有判断packet的长度，会越界解析到packet+4的位置。所以我构造了两个互相重叠的packet。

![](https://images.seebug.org/content/images/2021/02/23127e11-ebf4-42b2-934d-433b1ef9a286.png-w331s)

![](https://images.seebug.org/content/images/2021/02/98d1cb3a-c10f-4ee7-8691-2ae74c53da09.png-w331s)

Packet 1是两个字节， 在解析的时候会越界解析到Packet 2中，把Packet 2中的0xf8当成是Packet
1中的TOC字段，最后绕过opus_decode_frame中会导致崩溃的逻辑，具体细节不表。

## 堆喷，攻破ASLR！

通常即使有了任意地址写的能力，如果程序的ASLR防护做的比较好的话，想要利用该漏洞还得找一个信息泄漏。但是Safari的堆的实现上有些问题，导致我们可以通过堆喷的手段在某个固定的地址喷上我们控制的值。

有了任意地址写，首先想到的就是覆盖JSArray中的length字段，或者是ArrayBuffer中的length字段，ArrayBuffer由于Safari的Gigacage机制，即使覆盖了length字段也无法越界读写到有用的内容，所以我最后选择了JSArray。

Safari中JSArray使用了Butterfly来存储JSArray的长度以及内容，如果覆盖掉其中一个JSArray的长度，那么就可以越界读写到下一个JSArray的内容，就可以构造fakeobj以及addrof两个原语，用于后续的漏洞利用。

我先尝试喷了2个G的内存，发现我的Butterfly有时喷射在 0x800000000 - 0x1000000000 之间，有时喷射在
0x1800000000 - 0x1c00000000
之间。Safari由于堆隔离机制，不同类型的对象在不同的堆，Butterfly是在Safari中一个叫做Gigacage的堆里面的，对Gigacage堆做了一些研究发现，Gigacage的基地址是可以预测的，Gigacage的类型有两种，一种可以存储Bufferfly，一种可以存储ArrayBuffer。

对于这两种类型的堆，Gigacage做了一个小小的随机化，一种情况是Bufferfly在上面，另一种情况是ArrayBuffer在上面。如下图所示。情况一下，从0x800000000开始，会随机生成一块0-4G的未映射的区域，之后就是Bufferfly的堆了。第二种情况是从0x1800000000开始，会随机生成一块0-4G的未映射的区域，之后就是Bufferfly的堆。无论是哪种情况，基地址的随机化程度都很小。

![](https://images.seebug.org/content/images/2021/02/b6926a93-e482-4e2a-a9da-a0ddba87b435.png-w331s)

我一开始测试的时候是在16G内存的机器上，为了提高成功率，
喷了4个G，但是后来发现Safari对每个render进程占用的内存有监控，如果内存过大，会把他杀掉。所以最后我选择喷2.5个G，但是这会导致成功率有一定程度的下降。解决方法是多次触发任意地址写来提高成功率。

## 感谢多线程！在程序崩溃前让利用代码有足够的时间执行

下面这张时序图解释了整个漏洞利用过程，刚开始只有一个JS线程，我们先堆喷，并且在内存中构造音频文件，随后调用decodeAudioData函数，由于Safari是在单独的线程里解码音频的，所以这里会启动Audio
A线程，我们先假设堆喷后的内存布局是上面的情况1，那么Audio
A线程在解码音频文件的时候就会往0x80开头的地方写数据，JS线程在2s之后检测JSArray的length是否被改掉，如果被改掉，说明堆布局确实是情况1，接着就可以执行后续的exploit代码了，如果没有被改掉，说明堆布局是情况2，那么第二次调用decodeAudioData()函数，启动Audio
B线程解码音频，这次是往0x180开头的地址写数据。JS线程循环检查JSArray的length是否被改掉，如果成功，则调用执行后续的exploit，如果失败，说明整个利用失败。

![](https://images.seebug.org/content/images/2021/02/19840a6d-a5ca-4a40-b3ca-f92f7469a529.png-w331s)

此外还有一个问题需要解决，就是音频文件解码完之后，调用free函数对资源进行清理的时候，会触发崩溃。有几种方式可以解决这一问题，一种就是对损坏的堆进行修复，第二种就是让音频解码的时间非常非常的长，在解码结束之前我们的利用过程就结束了。

第一种由于需要对堆进行搜索，过于复杂，而且其实你要修复堆，其实也是需要一定的时间的，那其实还是要和第二种手段结合起来，那还不如直接粗暴一点，就选取第二种方法。我构造了一个600M的CAF文件，里面有七千多万个packet，要全部把这些packet解码完大概要花费50s左右的时间，完全足够我的漏洞利用了。

## Old school，任意地址读写原语到任意代码执行

当覆盖了JSArray的长度字段后，我们就可以构造fakeobj和addrof原语，然后就可以用这两个原语构造任意地址读写原语，再将shellcode写入JIT区域就可以任意代码执行了。这些都是属于浏览器利用的常规套路，对此感兴趣的读者可以阅读google的saelo写的文章《Attacking
JavaScript Engines》，在这里我们就不细细展开了。

## 尾声

光年实验室的 100 余处 Apple
漏洞（含47项致谢及50+项在途）的背后仅仅是两名安全研究员以及一台服务器。其中，高效高产的自动化漏洞挖掘平台AntFuzz居功至伟。

**蚂蚁安全光年实验室负责人曲和认为：自动化漏洞挖掘能力的建设与安全研究同学的培养同等重要。自动化能力通过实战不断加以演进，与安全研究同学两者相辅相成，实现漏洞挖掘的成果最大化，并在实战中加以证明。我们也将持续推进安全研究能力赋能变革，加速研究能力更好的连接基础业务。同时期待更多有志于从事漏洞研究、
Fuzzing 研究、程序分析方向的同学加入光年实验室，一起为基础设施提供更多安全保障。**

![](https://images.seebug.org/content/images/2021/02/407e9af8-ddd0-4d98-a435-3e8e8b92943c.jpg-w331s)

**蚂蚁安全光年实验室：**
隶属于蚂蚁安全实验室。通过对基础软件及设备的安全研究，达到全球顶尖破解能力，致力于保障蚂蚁集团及行业金融级基础设施安全。因发现并报告行业系统漏洞，上百次获得Google、Apple等国际厂商致谢。

扫码关注蚂蚁安全实验室微信公众号，干货不断！
![](https://images.seebug.org/content/images/2020/11/b7608072-36af-4d0b-b095-3ba93f757627.jpg-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1490/>

