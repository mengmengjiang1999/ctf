## 前言

**近期，有一群研究人员设计出了一种智能灰盒模糊测试模型，他们声称这种Fuzzer模型在搜寻代码库（解析复杂文件）漏洞方面跟现有Fuzzer相比，新模型的漏洞挖掘效率会更高。**

![](https://image.3001.net/images/20181206/1544075037_5c08b71dafd5c.png!small)

## 简介

[模糊测试](https://www.securityweek.com/fuzzing-reveals-over-30-web-browser-engine-flaws)是一种寻找软件漏洞的技术，这种技术需要向待测目标发送恶意构造的输入数据，如果程序发生崩溃或没有执行预期行为，这就表明这里有可能存在安全漏洞。目前，模糊测试技术主要有三种类型：黑盒模糊测试，这种情况下测试人员对待测目标的情况一无所知；白盒模糊测试，这种情况下测试人员需要对待测目标的情况了如指掌，测试主要针对的是程序的源代码；灰盒模糊测试，这种情况下测试人员手上只有部分待测目标信息。

此前，五名分别来自新加坡国立大学、澳大利亚莫纳什大学和罗马尼亚布加勒斯特波利特尼卡大学的安全研究人员一直在寻找一种能够有效提升灰盒模糊测试效率的方法，而现在他们表示研究已经取得了显著成果。

这群研究专家基于American Fuzzy
Lop（[AFL](http://lcamtuf.coredump.cx/afl/)，一款由安全专家MichalZalewski开发的模糊测试工具）开发出了一款名叫AFLsmart的工具，而这款工具采用了一种他们称之为智能灰盒模糊测试（SGF）的技术。

根据专家的介绍，目前社区有大量专门用于解析复杂文件结构的代码库，比如说解析音频、视频、图片、文档和数据库文件等等，而AFLsmart在分析这类代码库方面的效率非常的高。

在基于代码覆盖的灰盒模糊测试技术中，测试人员需要向fuzzer提供一个种子文件，并通过随机翻转、删除、拷贝或添加比特位的形式生成新的文件，然后让待测目标（代码库）去解析这些文件以发现潜在的安全漏洞。但问题就在于，对于复杂的文件结构（格式），比特位翻转并不一定能生成有效的文件。

不过，研究人员通过定义一种“新型变异操作”来克服了这种困难，这种技术是在虚拟文件结构上实现的，而不是在比特位层，这样就可以确保文件的有效性了。研究人员在白皮书上写到：“我们引入了一种新颖的基于有效性的电源调度方式，它可以让SGF花费更多的时间来生成更容易通过程序解析阶段的文件，从而挖掘到隐藏得更深的业务处理逻辑漏洞。”

在他们的实验过程中，他们对目前十一款热门的用于处理二进制可执行文件（ELF）、图片、音频和视频文件的开源代码库进行了测试，测试名单中包括Binutils、LibPNG、ImageMagick、LibJPEG-turbo、LibJasper、FFmpeg、LibAV、WavPack和OpenJPEG。

研究人员使用AFLsmart对这些代码库进行了测试，并与AFL、AFLfast和Peach
Fuzzer等模糊测试工具的结果进行了对比。AFLsmart发现了33个漏洞，是AFL和AFLfast挖到漏洞数量的一倍，而Peach一个漏洞都没找到。

![](https://image.3001.net/images/20181206/1544075050_5c08b72a0d4f7.png!small)

实验结果表明，这款新型模糊测试工具总共发现了42个安全漏洞，其中的17个已经标记了CVE编号。挖掘到的漏洞类型包括断言失败、堆栈缓冲区溢出、空指针引用和除零错误等等。

## 项目地址

目前，研究人员已经将AFLsmart Fuzzer开源了，感兴趣的同学可以fork一下。

> AFLsmartFuzzer：【[GitHub传送门](https://github.com/aflsmart/aflsmart)】

 *** 参考来源：[securityweek](https://www.securityweek.com/researchers-introduce-smart-greybox-fuzzing?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Securityweek+%28SecurityWeek+RSS+Feed%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

