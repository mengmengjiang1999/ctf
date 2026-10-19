# CodeQL

## 简介

官方文档：https://codeql.github.com/docs/

Semmle公司最早独创性的开创了一种QL语言，Semmle
QL，并且运行在自家[LGTM](https://lgtm.com/)平台上。LGTM平台上存放的就是一些开源项目，用户可以选择分析的语言，编写ql语句进行程序安全性查询2019年，GitHub收购了Semmle公司，开源了[CodeQL](https://github.com/github/codeql)分析引擎，来看引擎的概况图。  
![image.png](https://image.3001.net/images/20221208/1670490768_6391aa9094ea3632882c0.png!small)

可以看到CodeQL的整体思路是把源代码转化成一个可查询的数据库，然后用户可以使用QL语句进行查询，我们将其与Mysql进行对比，MySQL是一个数据库管理系统，可以用来存储、管理和分析数据；而CodeQL则可以看作是一个代码库管理系统，用于存储、管理和分析代码。为了分析数据，我们需要SQL语言来查询数据库；而为了分析代码，这里则需要利用QL语言来查询代码库。

  * 首先将源码通过Extractor模块进行代码信息分析&提取，构建一套自己的关系型数据库`Snapshot Database`

    * 编译型语言：Extractor观察编译器的编译过程，捕获编译器生成的AST，语义信息，控制流，数据流信息，外加一份源码来构成整个数据库

    * 解释型语言：Extractor直接分析源代码生成数据库

  * 接下来用户自定义QL语句，经过QL Compiler转换为Compiled Query，参与查询

  * 最终展示查询结果

这里需要说明的是CodeQL分析引擎是未开源的，只是开源了大量的QL查询样例。

CodeQL CLI(分析引擎)：https://github.com/github/codeql-cli-binaries
，此分析引擎是一个命令行工具，是和Mysql相似的，我们可以使用Navicat SQLyog 等工具对Mysql做图形化管理，同样的,CodeQL
CLI也可以图形化，不过其使用的是VS code插件的形式。

CodeQL ：https://github.com/github/codeql ，这是开源的大量查询样例来供我们进行学习。

## 作用

那么用CodeQL可以来干嘛呢?官方文档提到了`Code scanning with CodeQL`，也就是代码扫描，可用于分析 GitHub
存储库中的代码以查找安全漏洞和编码错误。代码扫描也就是代码审计，

代码审计，我们可以某种角度划分为人工和自动化，而自动化也就是自动化代码安全审计工具，例如`Fortify
SCA`，`FindBugs`，`JArchitect`等，而CodeQL和这些工具是相似的，也是进行自动化代码审计。

`Fortify SCA`这类产品原理是什么呢？`Static Program Analysis`，也就是静态程序分析

> 程序静态分析（Program Static
> Analysis）是指在不运行代码的方式下，通过词法分析、语法分析、控制流、数据流分析等技术对程序代码进行扫描，验证代码是否满足规范性、安全性、可靠性、可维护性等指标的一种代码分析技术
> ---百度百科

此时我们或许有这些许疑惑，感觉CodeQL和传统的扫描工具没有什么不同。

目前两种主流的静态程序分析:基于`AST`的，基于`IR/CFG`的，他们的区别只是技术基础不同，但分析的理论差异不大，我们可以粗略的将它们统一叫做`Data-flow Analysis`，也就是数据流分析（污点分析可以算作是数据流分析的变种）。

在基于数据流的扫描方案中，如果能够完整的支持各种语法充足的分析逻辑。我们就可以针对每一种漏洞分析相应的数据流挖掘漏洞。但是可惜事实是，问题比想象的还要多。这也印证了静态程序分析的一个著名的定理：Rice's
Theorem(莱斯定理)

> Any nontrivial property about the language recognized by a Turing machine is
> undecidable.
>
> 递归可枚举语言的任何非平凡的性质，都是不可判定的

这就像是扫描方案与开发人员的博弈一样，我们永远致力于降低误报率、漏报率却不能真正的解决，这样一来好像问题就变得又无解了起来……

而CodeQL也无法解决上面的问题，而是另辟蹊径，将静态代码扫描走到了新的路中，让我们不再拘泥于探讨如何处理流敏感、约束条件等等。将引擎的实现和规则开发、使用者分割开来，流分析等数据流相关的分析由引擎以及引擎的开发者来完成，使用者只需要关注规则的编写即可，当然，如何通过定义“谓词”来编写高级规则又或是不断通过多种高级规则来完善规则库体系，才是CodeQL真正的使用姿势。

# 环境搭建

## 环境准备

以Java为例，Java是编译型语言，所以你需要事先安装好项目编译所需的全部环境，例如：JDK、Maven

## CodeQL CLI

CodeQL CLI用来创建和分析数据库。也就是分析引擎

下载CodeQL压缩包并解压

<https://github.com/github/codeql-cli-binaries/releases>

将CodeQL CLI的可执行文件添加到环境变量，方便灵活调用

![image.png](https://image.3001.net/images/20221208/1670490823_6391aac79b5dff35cf94d.png!small)

![image.png](https://image.3001.net/images/20221208/1670490856_6391aae89f0abe98bb14e.png!small)

## CodeQL 标准库

包含了必须的一些标准库（内置库）和一些查询样例

<https://github.com/github/codeql>，下载后更改文件名为`ql`，此时目录结构为：  
![image.png](https://image.3001.net/images/20221208/1670490888_6391ab0815895c9680e5a.png!small)

注意：CodeQL解释器会按照某个规则（会查找CodeQL
CLI所在目录的兄弟目录以及其子目录）寻找CodeQL标准库的位置，若是没有找到，则需要你手动将CodeQL标准库添加到VSCode的工作区中。所以我们这里直接放在同一个文件夹下。

## 安装VS code插件并配置

官方提供了VSCode编写CodeQL的插件作为前端来使用Codeql  
![image.png](https://image.3001.net/images/20221208/1670490904_6391ab18cb0b7d7ad8d97.png!small)

这里的路径具体到`codeql.exe`，windows下也可以`codeql.cmd`

![image.png](https://image.3001.net/images/20221208/1670490922_6391ab2a62283102b8421.png!small)

# 使用

## 下载WebGoat

我这里以`WebGoat8.1.0`为例，此版本需要Java11环境，自行配置,

## 创建数据库

需要已经安装Maven，因为WebGoat项目是基于Maven构建的，CodeQL在创建数据库时，会自动探测并使用对应的编译方式。

在WebGoat根目录下面执行如下命令，会自动编译并且为该项目创建一个名为webgoat-qldb的QL数据库。

    
    
    codeql database create webgoat-ql -l java
    

因为要下载很多的依赖,生成比较慢  
![image.png](https://image.3001.net/images/20221208/1670490972_6391ab5c80109cedbef6a.png!small)

创建完该项目的数据库后，该项目的源码文件在后面几乎就用不到了（除非像更新QL数据库这种需求），CodeQL查询时主要使用的便是该项目的数据库文件

![image.png](https://image.3001.net/images/20221208/1670490986_6391ab6a68484f8f39107.png!small)

## 创建QL包

需要创建一个文件夹来存放后续编写的CodeQL脚本，CodeQL官方称这个文件夹为`QL Pack`。

例如名为`query`的文件夹，并在里面创建1个QL Pack的配置文件，名称固定为`qlpack.yml`；再创建一个ql后缀的文件，名称随意

![image.png](https://image.3001.net/images/20221208/1670491000_6391ab789ffb9cb8cd308.png!small)

在VSCode中打开这个文件夹

![image.png](https://image.3001.net/images/20221208/1670491010_6391ab82edce5227b7df2.png!small)

## 编写QL包的配置文件

将如下信息填入qlpack.yml文件

    
    
    name: query
    version: 0.0.0
    libraryPathDependencies: codeql-java
    

第一行表示这个QL包的名称为query，必选，如果你在VSCode中同时打开多个QL包时，要保证这个name的值唯一不重复；

第二行表示这个QL包的版本号，必选；

第三行表示这个QL包的依赖，必选，codeql-java表示需要Java语言的QL标准库依赖  
![image.png](https://image.3001.net/images/20221208/1670491025_6391ab91895e4846b60d1.png!small)

## VSCode工作区增加CodeQL标准库

为了让CodeQL解释器能够访问标准库，我们需要将标准库所在文件夹也加入到加入工作区中。

VSCode - 文件 - 将文件夹加入工作区 - 选择在【环境搭建-CodeQL标准库】章节中存放CodeQL标准库的文件夹。

![image.png](https://image.3001.net/images/20221208/1670491040_6391aba034e648957b975.png!small)

![image.png](https://image.3001.net/images/20221208/1670491051_6391ababe3fd253bf712c.png!small)

## 添加CodeQL数据库

在VSCode的CodeQL插件中添加之前用CodeQL创建的WebGoat的数据库。

![image.png](https://image.3001.net/images/20221208/1670491080_6391abc84d3831ddbc973.png!small)  
选择`webgoat-ql`那个文件夹。如下是添加成功后的页面

![image.png](https://image.3001.net/images/20221208/1670491109_6391abe518e4c7ef966f5.png!small)

## 编写一个简单查询

在`webgoat-queyr.ql`文件中编写如下代码，用来查找WebGoat项目中所有声明的方法

    
    
    import java
    
    from Method m
    select m
    

然后右键点击【CodeQL: Run Query 】来执行本次查询，执行完成后在右边可以看到多出一列用来显示查询结果

![image.png](https://image.3001.net/images/20221208/1670491211_6391ac4baf33e6ec7790c.png!small)  
点击结果里面的任意条目，可以跳到对应的文件中进行分析

![image.png](https://image.3001.net/images/20221208/1670491252_6391ac7483a0360f9e220.png!small)

# 总结

上面的环境搭建以及使用，应该是最简单的，我们只是初步使用了一下,对CodeQL有了一个简单的认识。下节，我们继续分享一些更深入的知识。

想要深入学习CodeQL，其学习成本是巨大的，首先是一门新的QL语言，由于QL是一种逻辑编程语言，类似于SQL语言，所以并不是难以理解，最重要的是关于静态程序分析的学习，目前好的学习资料并不多，主要还是高校开设的一些课程，个人看来南大的课程是更深入的。

> 南京大学 软件分析  
> https://www.bilibili.com/video/BV1b7411K7P4
>
> 北京大学 软件分析  
>
> https://www.bilibili.com/video/BV14X4y1N7nx?from=search&seid=9073392278546408847

由于笔者在学习中也是进行了大量资料的查阅，走了很多弯路，所以希望能站在一个初学者的角度进行一些讲解，来形成一份系统的学习笔记，而不是像网络上只是用简单的代码片段说明CodeQL的某个功能。

当然，详细阅读官方的文档永远是最好的方式。

因为难度较大，再加上时间问题，如果存在错误，希望指出，`WeChat：`KAC510

