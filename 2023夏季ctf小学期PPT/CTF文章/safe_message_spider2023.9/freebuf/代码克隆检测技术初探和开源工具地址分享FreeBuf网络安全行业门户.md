## 一、前言

 **代码克隆（Code
clone），是指存在于代码库中两个及两个以上相同或者相似的源代码片段，是软件开发中的常见现象。代码克隆能够提高效率，但也可能意外引入外部漏洞。下文是对代码克隆检测技术的简单整理。**

## 二、克隆的类型

代码克隆的类型主要分为两大类，句法克隆(syntactic clones)和语义克隆(semantic clones)。句法克隆指文本相似的代码片段,
语义克隆则是指功能相似的代码片段。基于这两大类，代码克隆可以被划分为四小类，其中前三种为句法克隆，第四种为语义克隆。

![](https://image.3001.net/images/20200415/1586933170_5e96adb2c247c.jpg!small)

当前，学术界对Type1,2,3类克隆的检测已颇为成熟，尤其是对Java和C++语言的克隆检测；而对Type4类克隆的检测准确率仍不高，无法达到工业界应用标准。

四类的代码示例可参照下图——

其中s1,s2,s3,s4 分别对照Type-1，2，3，4类的代码形式，加粗部分为修改部分。

![](https://image.3001.net/images/20200415/1586933217_5e96ade116416.png!small)

## 三、克隆检测的通用流程

通览代码克隆检测领域的相关论文，可以发现代码克隆检测通常分三步走。

![](https://image.3001.net/images/20200415/1586933429_5e96aeb59bef6.jpg!small)

将源码拆分为对比单元（comparison units, 如class，function，block，statement）

将对比单元转化为中间表达（IR, Intermediate Representation，如token，AST, PDG）

再对这些对比单元的IR进行match detection（对比），通常是将对比单元组成clone pair的形式：一次对比两个（c1,
c2）或是多个（c1, c2, c3）

## 四、克隆检测算法的分类

代码克隆检测发展至今，主要分为五大类检测思想: Textual, Token, Syntactic, Semantic,
Learning。其具体分类见下图。

![](https://image.3001.net/images/20200415/1586933517_5e96af0d7437a.jpg!small)

> Textual：代码片段以文本/字符串/词法的形式相互比较，并且只有在两个代码片段在文本内容方面确实相同时才被发现被克隆。
>
> Token：在编译器的词法分析阶段，所有源代码行都被划分为一系列Token。 然后将所有Token转换回Token序列。
>
> Syntactic（句法分析）： 基于树: 提取的AST用于子树比较以识别相似区域。
> 基于度量：通过源代码收集度量，然后使用这些度量为每个代码片段生成向量。然后使用向量对代码的相似度进行对比。
>
> Semantic：主要检测代码片段不同，但功能相同的函数（Type4）
>
> Learning : 通过机器学习和统计分析的方式来进行克隆检测

这几类对应的具体算法见下——

### 4.1 Textual

图中的oss指open source software

![](https://image.3001.net/images/20200415/1586933726_5e96afdeb7bed.jpg!small)

### 4.2 Token

![](https://image.3001.net/images/20200415/1586933741_5e96afed36722.jpg!small)

### 4.3 Syntactic

4.3.1 Tree

![](https://image.3001.net/images/20200415/1586933855_5e96b05fcde59.jpg!small)

4.3.2 Metric

![](https://image.3001.net/images/20200415/1586933781_5e96b0154864b.jpg!small)

### 4.4 Semantic

4.4.1 PDG

![](https://image.3001.net/images/20200415/1586933795_5e96b023e668f.jpg!small)

4.4.2 Other

![](https://image.3001.net/images/20200415/1586933808_5e96b030866b6.jpg!small)

### 4.5 Learning

4.5.1 ML

![](https://image.3001.net/images/20200415/1586933825_5e96b0412a5e8.jpg!small)

4.5.2 Other Learning

![](https://image.3001.net/images/20200415/1586933836_5e96b04c9f909.jpg!small)

## 五、克隆检测的历史趋势

有关代码克隆检测的最早和最开创性的工作是在1990年代初期完成的，如下表所示。可以看出除了近年兴起的ML方法以外，代码克隆检测的开创性工作均在90年代和00年代就已完成，这也是笔者说该领域已颇为成熟的原因。

名称 | 算法思想 | 检测级别  
---|---|---  
Baker,1992 | line-by-line comparison | Type-1,2  
Dup,1995 | parameterization | Type-1,2  
CloneDR，1998 | AST | Type-1,2  
CCFinder，2002 | token stream, a preﬁx tree and a novel matching algorithm, |
Type-1,2 支持在分钟内实现百万行代码的检测。支持代码类型：C，C++，Java，COBOL  
CP-Miner,2004 | 类CCFinder | bug-detection  
Deckard, 2007 | tree-based | 在大型数据集上有很好的表现，如Linux Kernel。可以检测 Type-1,2,3类的代码克隆  
  
## 六、Benchmarks 基准

除工具本身之外，代码克隆检测工具的基准测试和有效性测试领域也有许多发展。其中比较有名的基准数据集是Bellon’s benchmark（2007）和
BigCloneBench（2015）。

基准 | 发布时间 | 描述  
---|---|---  
Bellon’s benchmark | 2007 | 在两个小型C程序和两个小型Java程序上运行六个不同的代码克隆工具，并收集克隆结果。
将这些结果与真实代码克隆的主体进行比较，创建出代码克隆数据集。  
BigCloneBench | 2015 |
BigCloneBench是IJaDataset-2.0（一个包含25,000个开源Java系统的大数据软件存储库）中800万个经过验证的克隆代码段。包含项目内和项目间的全部四种主要克隆类型。  
  
## 七、开源工具

笔者整理了部分已开源的学术成果，地址见下。

Classification | **Tool** | Languages | Link  
---|---|---|---  
Token | **SHINOBI2009** | Any | <https://sdlab.naist.jp/projects/shinobi.html>  
AST | **Clone Merge** | C/C++ | <https://krishnanm86.wixsite.com/clonerge>  
Learning | **CloneCognition2019** | Java |
<https://github.com/pseudoPixels/CloneCognition>  
Token | **CtCompare2012** | Unspecified |
<https://github.com/awakecoding/ctcompare>  
Token | **CloneWorks2017** | Java |
<https://github.com/jeffsvajlenko/CloneWorks>  
Token | **CodeEase2017** | Unspecified | <https://github.com/shamsa-abid/CodeEase>  
Token | **SourcererCC2016** | Java | <https://github.com/Mondego/SourcererCC>  
Token | **CCFinderSW2017** | Any |
<https://github.com/YuichiSemura/CCFinderSW>  
Token | **Nicad2011** | C / C# / Java / Python / WSDL |
<https://www.txl.ca/txl-nicaddownload.html>  
PDG | **Clone-Diﬀerentiator2011** | Java等 |
<https://sites.google.com/site/yinxingxue/home/projects/clonedifferentiator>  
ML | **Agec2013** | Java | <https://github.com/tos-kamiya/agec>  
ML | **LICCA2018** | Java / C / JavaScript |
<https://github.com/tvislavski/licca>  
Learning | **Mostaeen2018** | C/Java |
<https://github.com/pseudoPixels/ML_CloneValidationFramework>  
Text | **BCFinder2018** | Binary |
<http://www.imm.dtu.dk/~sljo/bcfinder/gettingstarted.html>  
Text | **CCCD2013** | C | <http://www.se.rit.edu/~dkrutz/CCCD/index.html>  
  
## 八、References

> [1] Walker A, Cerny T, Song E. Open-source tools and benchmarks for code-> clone detection: past, present, and future trends[J]. ACM SIGAPP Applied
> Computing Review, 2020, 19(4): 28-39.
>
> [2] Roy C K, Cordy J R, Koschke R. Comparison and evaluation of code clone
> detection techniques and tools: A qualitative approach[J]. Science of
> computer programming, 2009, 74(7): 470-495.

 ***本文作者： 薇拉vera，转载请注明来自FreeBuf.COM**

