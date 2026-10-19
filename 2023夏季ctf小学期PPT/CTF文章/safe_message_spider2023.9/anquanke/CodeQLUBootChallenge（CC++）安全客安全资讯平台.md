# CodeQL U-Boot Challenge（C/C++）

阅读量 **146307**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-02-18 10:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01dfa2a598b29d9565.png)

## 背景

需要在U-Boot中寻找一组9个远程代码执行漏洞  
漏洞点位于memcpy函数  
但并非所有调用memcpy函数的都存在漏洞  
所以我们需要减少误报率，找到真正存在漏洞的memcpy调用

[放上题目链接](https://lab.github.com/githubtraining/codeql-u-boot-challenge-\(cc++)

关于环境搭建根据题目提示就可以顺利完成哦  
也可以参考我的文章”CodeQL for VSCode搭建流程”  
不出意外会放在我的[博客中](https://milkii0.github.io)

## Step 3 – our first query

在项目中寻找所有名为’strlen’的函数  
语法类似于sql语句  
`import cpp`: 导入c++规则库  
`From Function f1`: 声明一个Function类的变量为f1  
`where f1.getName() = "strlen"`:
Function.getName()顾名思义用于获取此声明的名称，也就是名称和”strlen”相等的声明会被挑选出来  
`select f1,"a function named strlen"`: select后接要在result中展示的项目，用逗号分隔  
3_function_definitions.ql

    
    
    import cpp
    
    from Function f1
    where f1.getName() = "strlen"
    select f1,"a function named strlen"
    

![](https://p0.ssl.qhimg.com/t012f49e693c5294e53.png)

直接在main提交

![](https://p4.ssl.qhimg.com/t0139d9da7eaa787c33.png)

commit中查看结果，通过

![](https://p5.ssl.qhimg.com/t01af31dd8eae01fe01.png)

## Step 4 – Anatomy of a query

仿照上一步，在项目中寻找所有名为’memcpy’的函数  
4_function_definitions.ql

    
    
    import cpp
    
    from Function f
    where f.getName() = "memcpy"
    select f,"a function named memcpy"
    

提交查看结果，通过

![](https://p1.ssl.qhimg.com/t0157f29812227e9411.png)

## Step 5 – Using different classes and their predicates

自定义规则，查找三个名为`ntohs`, `ntohl` or `ntohll`的宏定义  
需要一个紧凑的查询，而不是三个查找案例组合在一起  
给出以下两种方法

  1. 利用正则表达式  
`string`类有一个方法`regexpMatch`，接收器将参数与正则表达式匹配  
那我们需要先找到宏定义，再对该字符串进行正则匹配（使用的java的匹配模式）  
5_function_definitions.ql

    
    
    import cpp
    
    from Macro m
    where m.getName().regexpMatch("ntoh(s|l|ll)")
    select m,"macros named ntohs, ntohl or ntohll"
    

运行

![](https://p0.ssl.qhimg.com/t01efd712a775bd6a21.png)

  1. 使用集合表达式  
给出的格式：<your_variable_name> in [“bar”, “baz”, “quux”]

    
    
    import cpp
    
    from Macro m
    where m.getName() in ["ntohs","ntohl","ntohll"]
    select m,"macros named ntohs, ntohl or ntohll"
    

运行后和之前的结果相同，提交通过

PS：  
上学的时候为了过考试自学的c++，就是一些简单的语法  
看题目说明也没看明白ntoh 族函数到底是个啥  
后来看见了[swing的文章](https://bestwing.me/codeql.html)  
才知道ntoh族函数通常用来进行网络字节序到主机字节序的转换  
其实自己看到的时候就应该去查的，但是因为对题目影响不大就犯懒没去:-(  
以后不能这样了！看见没见过的看不懂的一定要去弄清楚

## Step 6 – Relating two variables

找到所有对`memcpy`函数的调用  
先看看给的例子  
`FunctionCall.getTarget()`查询该函数被调用的位置  
直接和`Function`类型的`fcn`对比值，说明他返回的值应该就是`Function`类型（这点在下面优化中会用到）

通过`Function.hasName()`获取方法名

    
    
    import cpp
    
    from FunctionCall call, Function fcn
    where
      call.getTarget() = fcn and
      fcn.getDeclaringType().getSimpleName() = "map" and
      fcn.getDeclaringType().getNamespace().getName() = "std" and
      fcn.hasName("find")
    select call
    

如果你想要省略中间变量`Function`，使查询的更加紧凑，可以参考以下两个对比  
`c1.getClass2()`返回的是Class2类型的值，因此可以直接调用Class2的方法

    
    
    from Class1 c1, Class2 c2
    where
      c1.getClass2() = c2 and
      c2.getProp() = "something"
    select c1
    
    
    from Class1 c1
    where c1.getClass2().getProp() = "something"
    select c1
    

根据以上案例思考  
我们需要找到`memcpy`函数被调用的位置，可以使用  
`FunctionCall.getTarget()`  
并希望查询更加紧凑，可以直接获取找到的函数的名称并进行判断  
`FunctionCall.getTarget().getName="memcpy"`

6_memcpy_calls.ql

    
    
    import cpp
    from FunctionCall functioncall
    where functioncall.getTarget().hasName("memcpy")
    select functioncall
    

提交通过

![](https://p4.ssl.qhimg.com/t0190d6d727cc30024d.png)

## Step 7 – Relating two variables, continued

寻找所有对`ntoh*`宏定义的调用

这里用到的是`MacroInvocation`这个类，顾名思义就是宏定义调用的类  
鼠标悬浮看其注释也能看出来

![](https://p4.ssl.qhimg.com/t0111123165b2670894.png)

那么我们就可以通过`getMacro()`寻找被调用的宏定义，并得到返回的`Macro`类型值  
再获得找到的`Macro`名称进行正则匹配，即可获得我们想要的结果

    
    
    import cpp
     from MacroInvocation macInvo
     where macInvo.getMacro().getName().regexpMatch("ntoh.*")
     select macInvo
    

（备注：关于正则表达式，不太会写，找的java正则api看的。  
`.`表示匹配除换行符 \n 之外的任何单字符，`*`表示零次或多次，  
我这里希望得到的结果是以`ntoh`开头的宏定义都会被选中。  
如果有不对的地方，还希望可以被提出指正◔ ‸◔）

提交通过

![](https://p5.ssl.qhimg.com/t013166420da066e36c.png)

## Step 8 – Changing the selected output

根据提示，使用`getExpr()`这个predicate  
先看看这个`getExpr()`的注释说明  
是用来获取宏定义表达式的  
如果顶级拓展元素不是表达式，它只是一条语句，将不会被选中列为结果

![](https://p5.ssl.qhimg.com/t01ec2f49b9b9431069.png)

使用`select macInvo.getExpr()`，就能获得宏定义调用相关的表达式  
8_macro_expressions.ql

    
    
    import cpp
     from MacroInvocation macInvo
     where macInvo.getMacro().getName().regexpMatch("ntoh.*")
     select macInvo.getExpr()
    

例如点击其中一个结果，就会跳转至下图位置

![](https://p0.ssl.qhimg.com/t012bb0e252c67269c4.png)

提交通过

![](https://p4.ssl.qhimg.com/t011ee6574205cdad6d.png)

那么查询表达式和查询调用的区别是啥？  
看注释说明，  
`getExpr()`：

_Gets a top-level expression associated with this macro invocation,if any.  
Note that this predicate will fail if the top-level expanded element is not an
expression (for example if it is a statement).  
This macro is intended to be used with macros that expand to a complete
expression.  
In other cases, it may have multiple results or no results._

获取关于宏调用的顶级表达式  
注意，如果顶级扩展元素不是一个表达式的话查询将失败（例如，它是一个语句）  
此宏用于扩展为完整表达式的宏，在其他情况下可能会有多个结果或没有结果

`getMacro()`：

_Gets the macro that is being accessed._  
获取正在访问的宏

即`getMacro()`会获取所有调用的宏，即使他只是一个语句  
而`getExpr()`只会获取宏调用的顶级表达式  
所以`getExpr()`得到的结果集应该包含于`getMacro()`的结果集  
这里放上[语句和表达式的区别讨论链接](https://www.zhihu.com/question/20750344)

## Step 9 – Write your own class

首先看看学习`exists`关键词给出的例子：  
这个规则只是为了获取不秃头的所有人

不秃头的人都会有头发，那么他们的头发都会对应一个或多个颜色  
其中`t.getHairColor()`会返回一个`string`类型的值，例如”red”  
如果我们需要获得不秃头的人，我们并不需要知道他们头发的具体颜色，只需要知道`t.getHairColor()`会返回`string`类型的值即可，因为秃头`getHairColor()`时，不会返回任何值

所以我们利用`string`类型的变量完成该操作  
更好的方式是使用`exists`关键词，因为我们只是在`where`中使用该变量  
例如，`exists(string c | t.getHairColor() =
c)`使用了string类型的临时变量，用于获取`t.getHairColor()`返回了`string`值的`t`，也就是查询了所有头发颜色的值为`string`类型的人

    
    
    from Person t
    where exists(string c | t.getHairColor() = c)
    select t
    
    /*在CodeQL中，以下代码功能同于以上代码，给出只是为了更好地理解*/
    from Person t, string c
    where t.getHairColor() = c
    select t
    

再来看看类定义中给出的案例

    
    
    class OneTwoThree extends int {
      OneTwoThree() { // characteristic predicate
        this = 1 or this = 2 or this = 3
      }
    
      string getAString() { // member predicate
        result = "One, two or three: " + this.toString()
      }
    
      predicate isEven() { // member predicate
        this = 2
      }
    }
    

以上代码定义了一个名为`OneTwoThree`的类，继承于int  
类似于构造函数的部分是`this = 1 or this = 2 or this = 3`  
文档中解释说明这个类中包括了1,2,3这三个值  
运行以下规则，可以发现ott中确实有1，2，3这三个值

    
    
    import cpp
     /*from MacroInvocation macInvo
     where macInvo.getMacro().getName().regexpMatch("ntoh.*")
     select macInvo.getExpr()*/
     class OneTwoThree extends int {
        OneTwoThree() { // characteristic predicate
          this = 1 or this = 2 or 3=this
        }
    
        string getAString() { // member predicate
          result = "One, two or three: " + this.toString()
        }
    
        predicate isEven() { // member predicate
          this = 2
        }
      }
    
      from OneTwoThree ott
      select ott
    

![](https://p2.ssl.qhimg.com/t010b5b5545e11dc759.png)

其中还有一个熟悉的单词`predicate`  
这个是在类的主体内定义的谓词，是使用变量来限制类中可能的值的逻辑属性  
举个例子，运行以下规则，就会得到值2

    
    
     class OneTwoThree extends int {
        OneTwoThree() { // characteristic predicate
          this = 1 or this = 2 or 3=this
        }
    
        string getAString() { // member predicate
          result = "One, two or three: " + this.toString()
        }
    
        predicate isEven() { // member predicate
          this = 2
        }
      }
    
      from OneTwoThree ott
      where ott.isEven()
      select ott
    

运行截图：

![](https://p2.ssl.qhimg.com/t0112786bc393aed9e1.png)

再更改规则如下：

    
    
     class OneTwoThree extends int {
        OneTwoThree() { // characteristic predicate
          this = 1 or this = 2 or 3=this
        }
    
        string getAString() { // member predicate
          result = "One, two or three: " + this.toString()
        }
    
        predicate isEven() { // member predicate
          this = 2
        }
      }
    
      from OneTwoThree ott
      where ott = 2
      select ott
    

他们会得到相同的结果

![](https://p1.ssl.qhimg.com/t01ea234ebc1788b62c.png)

也就是说`where ott.isEven()`和`where ott = 2`做出的是相同的限制  
那么我们也就能更好地理解，`predicate`特征是用于限制类中可能值的逻辑属性了

其中`string getAString()`就不必多说，返回一个字符串，其中包含对应值

![](https://p4.ssl.qhimg.com/t01e6047f182835e78d.png)

其中我发现一个很神奇事，不知该如何解释  
我将代码中`this=1`改成`1=this`也会得到一样的结果，没有任何不同或报错  
它和赋值语句不同，但好像又具有相似的功能  
在对变量做限制时，例如`where ott = 2`，它就变成了一个符号，用于对两个值进行比较，这里还好理解，因为sql语法类似  
但是同样在以下代码中

    
    
     predicate isEven() { // member predicate
          this = 2
        }
    

`this=2`也是用于对两个值进行比较  
我认为这是由于`predicate`带来的改变，使得其中的代码和`where`后的代码具有相同得到功能  
如果有更好的见解，还不忘赐教

最后来写题  
题目给了模板和提示  
按照step8中的规则进行编写，`exists`第二个参数放上step8中的where条件  
由于select由题目给出并为Expr的子类，所以我们需要增加一个条件获取宏调用相关表达式  
根据以上`exists`案例可知，我们需要在`mi.getExpr() =` 后面写出他返回值的类型，这样当`mi`为表达式时，就会被选中  
`NetworkByteSwap`是`Expr`的子类，因此

9_class_network_byteswap.ql

    
    
    import cpp
    
    class NetworkByteSwap extends Expr {
        NetworkByteSwap() { 
            exists(MacroInvocation mi | mi.getMacro().getName().regexpMatch("ntoh.*") | mi.getExpr() = this)
         }
    }
    
    from NetworkByteSwap n
    select n, "Network byte swap"
    

## Step 10 – Data flow and taint tracking analysis

最后一步，进行数据流分析

先了解以下我们需要查询的函数背景，`ntoh*`函数会返回一个数，并用于`memcpy`的第三个参数`size`，所以我们需要追踪的数据流就是从`ntoh*`到`memcpy`

> 在C/C++写网络程序的时候，往往会遇到字节的网络顺序和主机顺序的问题。 这时就可能用到htons(), ntohl(),
> ntohs()，htons()这4个网络字节顺序与本地字节顺序之间的转换函数
>
>
> memcpy指的是c和c++使用的内存拷贝函数，memcpy函数的功能是从源src所指的内存地址的起始位置开始拷贝n个字节到目标dest所指的内存地址的起始位置中

创建`Config`类，查找此类的数据流并进行污染点追踪分析  
进行数据流分析，我们需要用到，部分代码已经在给出的模板中

    
    
    import semmle.code.cpp.dataflow.TaintTracking
    import DataFlow::PathGraph
    

我们需要写两个`predicate`，一个是来源`isSource`，一个是接收器`isSink`

`isSource`中我们需要查询`ntoh*`宏定义调用的相关表达式，这一步我们已经在`NetworkByteSwap`中写过了  
`isSink`中我们需要查询调用`memcpy`函数时，传入的第三个参数`size`，这一步我们需要新增加的步骤是获取参数

弄清楚这些后，在编写规则时，根据提示完善代码  
我们就能获得10_taint_tracking.ql的答案

    
    
    /**
     * @kind path-problem
     */
    
    import cpp
    import semmle.code.cpp.dataflow.TaintTracking
    import DataFlow::PathGraph
    
    class NetworkByteSwap extends Expr {
        NetworkByteSwap() { 
            exists(MacroInvocation mi| mi.getMacro().getName().regexpMatch("ntoh(s|l|ll)") | this = mi.getExpr())
         }
    }
    
    class Config extends TaintTracking::Configuration {
      Config() { this = "NetworkToMemFuncLength" }
    
      override predicate isSource(DataFlow::Node source) {
        // TODO
        /*获取与此节点对应的表达式（如果有）。
        此谓词仅在表示表达式求值值的节点上具有结果。
        对于从表达式中流出的数据，例如通过引用传递参数时，请使用asDefiningArgument而不是asExpr。*/
        source.asExpr() instanceof NetworkByteSwap
      }
      override predicate isSink(DataFlow::Node sink) {
        // TODO
        exists(FunctionCall fc | fc.getTarget().hasName("memcpy") | sink.asExpr() = fc.getArgument(2))
      }
    }
    
    from Config cfg, DataFlow::PathNode source, DataFlow::PathNode sink
    where cfg.hasFlowPath(source, sink)
    select sink, source, sink, "Network byte swap flows to memcpy"
    

## 传送门

[cpp规则语法说明](https://lgtm.com/help/lgtm/console/ql-cpp-basic-example)  
[Java正则模式](https://docs.oracle.com/javase/7/docs/api/java/util/regex/Pattern.html)  
[给出的参考案例：CVE-2018-4259: MacOS NFS vulnerabilties lead to kernel
RCE](https://securitylab.github.com/research/cve-2018-4259-macos-nfs-vulnerability/)（知识点挺多的）  
[codeql-swing](https://bestwing.me/codeql.html)（swing的语言云淡风轻，条理清晰，如沐春风，我的的语言阿巴阿巴阿巴）  
[讨论区](https://github.com/github/securitylab/discussions)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **milkii0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266824](/post/id/266824)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CodeQL](/tag/CodeQL)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t0163b18c76935eb135.png) milkii0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

