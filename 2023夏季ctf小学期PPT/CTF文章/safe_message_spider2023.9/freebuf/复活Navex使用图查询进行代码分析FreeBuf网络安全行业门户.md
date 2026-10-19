**从了解到修复[Navex](http://zeroyu.xyz/2019/03/11/NAVEX-Precise-and-Scalable-Exploit-Generation-for-Dynamic-Web-Applications/?utm_source=tuicool&utm_medium=referral), 其中花了一年多,
从对自动化代码审计一无所知到学习`PL/Static Analysis`, 翻阅十几年前的文档, 补全`Gremlin Step`, 理解`AST`,
`CFG`, `DDG`, `PDG`, `CPG`,
也感谢[`z3r0yu`](http://zeroyu.xyz/)师傅和[Gaba](https://github.com/AlkenePan)哥的的交流指导.**

本文重点在于静态分析 Joern-图查询部分, 后面的动态分析自动生成EXP部分是剪枝的过程, 也相对好实现, 各位有兴趣的话, 我会在下一篇文章继续谈论.

这里不得不说的Navex实际的效果没有描述的那么优秀, 以及作者故意在代码里埋坑, 毕竟人家也研究了快十年, 留一手也是正常的.

这里不是说一定非要完成/使用Navex, 而是借鉴新鲜的学术思想, 结合实际环境实现相关功能来降低排查漏洞成本.

* * *

### Navex 是什么

下面这段摘自`z3r0yu`师傅的博文 [Navex](http://zeroyu.xyz/2019/03/11/NAVEX-Precise-and-Scalable-Exploit-Generation-for-Dynamic-Web-Applications/?utm_source=tuicool&utm_medium=referral)

> NAVEX->Precise and Scalable Exploit Generation for Dynamic Web Applications
>
> 出处：27th USENIX Security Symposium  
> 作者：Abeer Alhuzali, Rigel Gjomemo, Birhanu Eshete, and V.N.  
> 单位：Venkatakrishnan University of Illinois at Chicago  
>
> 资料：[Paper](https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-alhuzali.pdf)
> | [Github](https://github.com/aalhuz/navex)
>
> 作者在本文中提出了一种以静态分析作为指导，结合动态分析自动验证漏洞并构造可用exploit的工具NAVEX。
>
> 研究问题：
>
>   1. 解决以往自动化审计的误报以及必须结合人工参与构造Exp的问题；
>   2. 静态分析虽然覆盖率高，但是对于具有动态特性的语言其建模困难。
>
> 解决方案：
>
>   3. 静态分析阶段：使用符号执行创建Web应用程序的各个模块的行为模型。标记出包含潜在漏洞点的模块；
>
>   4.
> 动态分析阶段：使用Web爬虫和concolic执行器去发现可能导致攻击者进入易受攻击模块的可能的HTTP导航路径，之后使用约束求解器生成一组对漏洞进行利用的HTTP输入序列。
>
> 方案优点：.
>
>   5. 动态分析与静态分析相结合提升了性能，可以应用于大型应用程序；
>
>   6. 是一种多类型漏洞的Exp生成框架。
>
>
> NAVEX分析了320万行PHP代码，自动构建并利用204个漏洞，其中有195个与SQLI和XSS相关，而9个与逻辑漏洞相关。此外NAVEX是第一个可以自动发现并利用EAR漏洞的方案。
>
>

### Joern 静态分析核心模块

`Joern` 是`ShiftLeft`公司开发的用于`C/C++`代码健壮性分析的平台. 其核心思想:
将代码分析问题转化为用`Gremlin`去遍历存储在`Neo4j`中的`CPG`(代码属性图). 其商业产品
[Ocular](https://go.shiftleft.io/ocular-free-trial) 支持多种语言, 也侧面证明 `CPG` 作为一种
`IR`, 是可以解决大部分语言的审计问题.

PS. 静态分析这部分其实可以使用`Codeql`代替.

### CPG 代码属性图

`CPG` (代码属性图) 的论文可以参考

[Modeling and Discovering Vulnerabilities with Code Property
Graphs](https://fabs.codeminers.org/papers/2014-ieeesp.pdf)

这里用几张图简要描述一下

原始代码

![6f014ba20ec8a2724c2ee07c47fc73a8.png](https://image.3001.net/images/20200518/15897703694590.png!small)

代码对应的`AST`(抽象语法树)

![9344f170a4e964d6522be074d57ab6ad.png](https://image.3001.net/images/20200518/1589770353195.png!small)

代码对应的`CFG`(控制流程图)

![6830130f98d190a5dcb6f203c993b1ee.png](https://image.3001.net/images/20200518/15897703371668.png!small)

代码对应的`PDG`(程序依赖图)![446fc809296a504d72988643c8b5d2da
\(1\).png](https://image.3001.net/images/20200518/15897703065736.png!small)

](<https://blog.riskivy.com/wp-content/uploads/2020/05/4afab12ab74238d1b09a90517beabf9e.png>)

代码对应的`CPG`(代码属性图)

![446fc809296a504d72988643c8b5d2da.png](https://image.3001.net/images/20200518/1589770276530.png!small)  

其实以上的信息都可以从AST中获取, 只是后续的操作提高了单位节点的信息密集度, 对分析过程更友好

### TinkerPop 2.x Gremlin 图查询语言

由于Navex作者是2012年开始研究这个方向, 所以大部分依赖都是远古版本, 我尽可能的修复了一些, 其中`TinkerPop 2.x
Gremlin`由于官方已经更新 `TinkerPop 3.x`, `2.x` 已经不再维护了, 全网只有一个github上面的历史文档

[spmallette/GremlinDocs: Gremlin Documentation and
Samples](https://github.com/spmallette/GremlinDocs)

或者阅读`TinkerPop 2.x Gremlin`的实现源码

[tinkerpop/gremlin: A Graph Traversal Language (no longer active – see Apache
TinkerPop)](https://github.com/tinkerpop/gremlin).

其实更新为最新版的`TP3`(文档, 性能和语法都更好), 我也尝试过, 但是整个框架的`Gremlin step`需要重写, 不利于前期探索,
`TP2`目前还够用, 所以如果后续有需要, 可以考虑整体重构.

目前的`python-joern`的实现方式是通过`HTTP请求`发送`Gremlin查询语言(Groovy实现)`到`Neo4j`的`Gremlin插件`

> 为什么不用`Neo4j`自带的`Cypher`, 因为`Gremlin`支持`Groovy语法`, 有更强的操作性, 也兼容其他图数据库

## Tinkerpop 2.x Gremlin 基础知识

首先得了解`Groovy`的相关语法

[精通
Groovy](https://www.ibm.com/developerworks/cn/education/java/j-groovy/j-groovy.html)

`TinkerPop 2.x Gremlin` 文档查看这个

[tinkerpop/gremlin: A Graph Traversal Language (no longer active – see Apache
TinkerPop)](https://github.com/tinkerpop/gremlin).

下面是我添加了一些注释, 方便理解

### it

`it` 是groovy闭包中的默认参数

    
    
    list.each {
        println it
    }
    
    //等于
    
    list.each { obj ->
        println obj 
    }
    

### id

Gets the unique identifier of the element.

每个节点/边都有唯一的`id`

    
    
    gremlin> v = g.V("name", "marko").next()
    ==>v[1]
    gremlin> v.id
    ==>1
    gremlin> g.v(1).id
    ==>1
    

### V

The vertex iterator for the graph. Utilize this to iterate through all the
vertices in the graph. Use with care on large graphs unless used in
combination with a key index lookup.

在 `TP2`中

`g.V()` 代表所有节点

`g.v(1)` 注意这里是小写的`v`, 可以用`node_id`取值

`g.V("name", "marko")` 返回 `v.name=="marko"` 的节点

    
    
    gremlin> g.V
    ==>v[3]
    ==>v[2]
    ==>v[1]
    ==>v[6]
    ==>v[5]
    ==>v[4]
    gremlin> g.V("name", "marko")
    ==>v[1]
    gremlin> g.V("name", "marko").name
    ==>marko
    

### E

The edge iterator for the graph. Utilize this to iterate through all the edges
in the graph. Use with care on large graphs.

返回节点的所有边

    
    
    gremlin> g.E
    ==>e[10][4-created->5]
    ==>e[7][1-knows->2]
    ==>e[9][1-created->3]
    ==>e[8][1-knows->4]
    ==>e[11][4-created->3]
    ==>e[12][6-created->3]
    gremlin> g.E.weight
    ==>1.0
    ==>0.5
    ==>0.4
    ==>1.0
    ==>0.4
    ==>0.2
    

### in

Gets the adjacent vertices to the vertex.

返回当前`node`的父节点

参数的调用可以不写 ()

  1. 没有参数的调用可以不写 `()`
  2. 这个技巧在后面存储路径信息的时候会用到

`g.v(4).inE.outV == g.v(4).in`

`g.v(4).outE.inV == g.v(4).out`

    
    
    gremlin> v = g.v(4)
    ==>v[4]
    gremlin> v.inE.outV
    ==>v[1]
    gremlin> v.in
    ==>v[1]
    gremlin> v = g.v(3)
    ==>v[3]
    gremlin> v.in("created")
    ==>v[1]
    ==>v[4]
    ==>v[6]
    gremlin> v.in(2,'created')
    ==>v[1]
    ==>v[4]
    gremlin> v.inE("created").outV
    ==>v[1]
    ==>v[4]
    ==>v[6]
    gremlin> v.inE(2,'created').outV[0]
    ==>v[1]
    

### out

Gets the out adjacent vertices to the vertex.

返回当前`node`的子节点

    
    
    gremlin> v = g.v(1)
    ==>v[1]
    gremlin> v.outE.inV
    ==>v[2]
    ==>v[4]
    ==>v[3]
    gremlin> v.out
    ==>v[2]
    ==>v[4]
    ==>v[3]
    gremlin> v.outE('knows').inV
    ==>v[2]
    ==>v[4]
    gremlin> v.out('knows')
    ==>v[2]
    ==>v[4]
    gremlin> v.out(1,'knows')
    ==>v[2]
    

### both

Get both adjacent vertices of the vertex, the in and the out.

`both` 操作表示`node` 的相邻节点, 也就有有`edge` 存在, 且忽略 `edge` 的方向

    
    
    gremlin> v = g.v(4)
    ==>v[4]
    gremlin> v.both
    ==>v[1]
    ==>v[5]
    ==>v[3]
    gremlin> v.both('knows')
    ==>v[1]
    gremlin> v.both('knows', 'created')
    ==>v[1]
    ==>v[5]
    ==>v[3]
    gremlin> v.both(1, 'knows', 'created')
    ==>v[1]
    

### Transform

Transform steps take an object and emit a transformation of it.

`Transform` 操作可以返回其后面闭包里面的值

Identity turns an arbitrary object into a “pipeline”.

    
    
    gremlin> x = [1,2,3]
    ==>1
    ==>2
    ==>3
    gremlin> x._().transform{it+1}
    ==>2
    ==>3
    ==>4
    gremlin> x = g.E.has('weight', T.gt, 0.5f).toList()
    ==>e[10][4-created->5]
    ==>e[8][1-knows->4]
    gremlin> x.inV
    ==>[StartPipe, InPipe]
    ==>[StartPipe, InPipe]
    gremlin> x._().inV
    ==>v[5]
    ==>v[4]
    

### has

使用has可以做一些简单的属性判断

Allows an element if it has a particular property. Utilizes several options
for comparisons through `T`:

  * T.gt – greater than
  * T.gte – greater than or equal to
  * T.eq – equal to
  * T.neq – not equal to
  * T.lte – less than or equal to
  * T.lt – less than
  * T.in – contained in a list
  * T.notin – not contained in a list

It is worth noting that the syntax of `has` is similar to `g.V("name",
"marko")`, which has the difference of being a [key
index](https://github.com/tinkerpop/blueprints/wiki/Graph-Indices) lookup and
as such will perform faster. In contrast, this line, `g.V.has("name",
"marko")`, will iterate over all vertices checking the `name` property of each
vertex for a match and will be significantly slower than the key index
approach. All that said, the behavior of `has` is dependent upon the
underlying implementation and the above description is representative of most
Blueprints implementations. For instance, Titan will actually try to use
indices where it sees the opportunity to do so. It is therefore important to
understand the functionality of the underlying database when writing
traversals.

    
    
    gremlin> g.V.has("name", "marko").name
    ==>marko
    gremlin> g.v(1).outE.has("weight", T.gte, 0.5f).weight
    ==>0.5
    ==>1.0
    gremlin> g.V.has('age').name
    ==>vadas
    ==>marko
    ==>peter
    ==>josh
    gremlin> g.V.has('age',T.in,[29,32])
    ==>v[1]
    ==>v[4]
    gremlin> g.V.has('age').has('age',T.notin, [27,35]).name
    ==>marko
    ==>josh
    

### [i]

A index filter that emits the particular indexed object.

通过下标可以进行取值, 跟Python的数组相似

    
    
    gremlin> g.V[0].name
    ==>lop
    

* * *

### [i..j]

A range filter that emits the objects within a range.

下标也可以取范围. 前闭后开, `[0,2)`

    
    
    gremlin> g.V[0..2].name
    ==>lop
    ==>vadas
    ==>marko
    gremlin> g.V[0..<2].name
    ==>lop
    ==>vadas
    

### filter

Decide whether to allow an object to pass. Return true from the closure to
allow an object to pass.

filter操作就是通过一个闭包函数来过滤输入

    
    
    //filter有时会失效,最好用has()
    g.v(1).outE.has('label','created')
    //g.v(1).outE.filter{it.label=='created'}
    

> groovy  
> in `filter{}`  
> `it.xxx()` 可能返回 `pipe` 对象  
> 可以使用  
> `it.xxx().next()`  
> 来获取第一个节点
    
    
    gremlin> g.V.filter{it.age > 29}.name
    ==>peter
    

### dedup

Emit only incoming objects that have not been seen before with an optional
closure being the object to check on.

用于去除重复元素

    
    
    gremlin> g.v(1).out.in
    ==>v[1]
    ==>v[1]
    ==>v[1]
    ==>v[4]
    ==>v[6]
    gremlin> g.v(1).out.in.dedup()
    ==>v[1]
    ==>v[4]
    ==>v[6]
    

### as

Emits input, but names the previous step.

给一个操作设置一个别名, 配合`select`, `loop`

`g.v(1).as('sloop').outE.inV.loop('sloop'){it.loops < 2}`

循环体为 `.outE.inV.` 等价

`g.v(1).outE.inV.loop(2){it.loops < 2}`

    
    
    gremlin> g.V.as('x').outE('knows').inV.has('age', T.gt, 30).back('x').age
    ==>29
    

### select

Select the named steps to emit after select with post-processing closures.

`select` 一般配合`as`一起使用

    
    
    gremlin> g.v(1).as('x').out('knows').as('y').select
    ==>[x:v[1], y:v[2]]
    ==>[x:v[1], y:v[4]]
    gremlin> g.v(1).as('x').out('knows').as('y').select(["y"])
    ==>[y:v[2]]
    ==>[y:v[4]]
    gremlin> g.v(1).as('x').out('knows').as('y').select(["y"]){it.name}
    ==>[y:vadas]
    ==>[y:josh]
    gremlin>  g.v(1).as('x').out('knows').as('y').select{it.id}{it.name}
    ==>[x:1, y:vadas]
    ==>[x:1, y:josh]
    

### sideEffect

Emits input, but calls a side effect closure on each input.

官方示例中的是交互console, 可以延伸到下一条语句

    
    
    gremlin> youngest = Integer.MAX_VALUE
    ==>2147483647
    gremlin> g.V.has('age').sideEffect{youngest=youngest>it.age?it.age:youngest}
    ==>v[2]
    ==>v[1]
    ==>v[6]
    ==>v[4]
    gremlin> youngest
    ==>27
    

`sideEffect`可以在运行过程中执行指定操作, 但是不会影响遍历过程, 主要用于收集信息, 尽量不要用于改变节点信息

在`python-joern`中, `sideEffect`的作用域只在当前遍历过程/语句, 这里比较坑人, 大家注意

`g.V.has('age').sideEffect{youngest=youngest>it.age?it.age:youngest}.transform{youngest}`

### ifThenElse

Allows for if-then-else conditional logic.

    
    
    gremlin> g.v(1).out.ifThenElse{it.name=='josh'}{it.age}{it.name}
    ==>vadas
    ==>32
    ==>lop
    

判断条件选择分支执行, 这边倾向于单独使用`groovy`的 `if`语句来处理, 逻辑更清晰

### loop

Loop over a particular set of steps in the pipeline. The first argument is
either the number of steps back in the pipeline to go or a named step. The
second argument is a while closure evaluating the current object. The `it`
component of the loop step closure has three properties that are accessible.
These properties can be used to reason about when to break out of the loop.

  * `it.object`: the current object of the traverser.
  * `it.path`: the current path of the traverser.
  * `it.loops`: the number of times the traverser has looped through the loop section.

The final argument is known as the “emit” closure. This boolean-based closure
will determine wether the current object in the loop structure is emitted or
not. As such, it is possible to emit intermediate objects, not simply those at
the end of the loop.

    
    
    gremlin> g.v(1).out.out
    ==>v[5]
    ==>v[3]
    gremlin> g.v(1).out.loop(1){it.loops<3}
    ==>v[5]
    ==>v[3]
    gremlin> g.v(1).out.loop(1){it.loops<3}{it.object.name=='josh'} 
    ==>v[4]
    

`loop`应该这里最关键的操作, 可以参考

[Loop Pattern · tinkerpop/gremlin
Wiki](https://github.com/tinkerpop/gremlin/wiki/Loop-Pattern)

大部分的查询操作都需要`loop`进行配合

`g.v(1).out.loop(1){it.loops<3}{it.object.name=='josh'}`

大概等价于

    
    
    arr = []
    for (i=1; i<3; i++){
        if(it.object.name=='josh'){
            arr.add(it.object)
        }
    }
    return arr
    

结合后面的`enablePath`, 可以在遍历的过程中获取当前所在的完整路径信息

`g.v(1).out.loop(1){it.loops<3}{it.object.name=='josh' &&
it.path.contains(g.v(4))}.enablePath`

大概等价于

    
    
    arr = []
    for (i=1; i<3; i++){
        if(it.object.name=='josh' && it.path.contains(g.v(4))){
            arr.add(it.object)
        }
    }
    return arr
    

### Pipe.enablePath

If the path information is required internal to a closure, Gremlin doesn’t
know that as it can not interpret what is in a closure. As such, be sure to
use `GremlinPipeline.enablePath()` if path information will be required by the
expression.

主要是保存路径信息

    
    
    gremlin> g.v(1).out.loop(1){it.loops < 3}{it.path.contains(g.v(4))}
    Cannot invoke method contains() on null object
    Display stack trace? [yN] 
    gremlin> g.v(1).out.loop(1){it.loops < 3}{it.path.contains(g.v(4))}.enablePath()
    ==>v[5]
    ==>v[
    

### Pipe.next

Gets the next object in the pipe or the next n objects. This is an important
notion to follow when considering the behavior of the Gremlin Console. The
Gremlin Console iterates through the pipeline automatically and outputs the
results. Outside of the Gremlin Console or if more than one statement is
present on a single line of the Gremlin Console, iterating the pipe must be
done manually. Read more about this topic in the Gremlin Wiki [Troubleshooting
Page](https://github.com/tinkerpop/gremlin/wiki/Troubleshooting).

There are some important things to note in the example below. Had the the
first line of Gremlin been executed separately, as opposed to being placed on
the same line separated by a semi-colon, the name of the vertex would have
changed because the Gremlin Console would have automatically iterated the pipe
and processed the side-effect.

    
    
    gremlin> g.v(1).sideEffect{it.name="same"};g.v(1).name
    ==>marko
    gremlin> g.v(1).sideEffect{it.name="same"}.next();g.v(1).name
    ==>same
    gremlin> g.V.sideEffect{it.name="same-again"}.next(3);g.V.name
    ==>same-again
    ==>same-again
    ==>same-again
    ==>peter
    ==>ripple
    ==>josh
    

`next` 操作可以从`pipe`中取出对象 // `pipe`返回的一般都是生成器对象

### path

Gets the path through the pipeline up to this point, where closures are post-processing for each object in the path. If the path step is provided closures
then, in a round robin fashion, the closures are evaluated over each object of
the path and that post-processed path is returned.

    
    
    gremlin> g.v(1).out.path
    ==>[v[1], v[2]]
    ==>[v[1], v[4]]
    ==>[v[1], v[3]]
    gremlin> g.v(1).out.path{it.id}
    ==>[1, 2]
    ==>[1, 4]
    ==>[1, 3]
    gremlin> g.v(1).out.path{it.id}{it.name}
    ==>[1, vadas]
    ==>[1, josh]
    ==>[1, lop]
    gremlin> g.v(1).outE.inV.name.path
    ==>[v[1], e[7][1-knows->2], v[2], vadas]
    ==>[v[1], e[8][1-knows->4], v[4], josh]
    

`path`操作返回遍历的所有路径

### simplePath

Emit the object only if the current path has no repeated elements.

    
    
    gremlin> g.v(1).out.in
    ==>v[1]
    ==>v[1]
    ==>v[1]
    ==>v[4]
    ==>v[6]
    gremlin> g.v(1).out.in.simplePath
    ==>v[4]
    ==>v[6]
    

`simplePath`返回没有环路的`path`

### toList

    
    
    g.v(1).out //返回生成器
    g.v(1).out.toList() //返回一个列表, 已经把数据都读出来了, 可以随便操作
    

### intersect

返回交集

    
    
    [1,2,3].intersect([1]) 
    => [1]
    
    [].intersect([1]) 
    => []
    

## Navex 排坑

### 被删除的查询语句

当你信心满满的解决了前面的各种古老依赖, 奇怪版本号问题时, 在最关键的查询语句是丢失的

如果你真的尝试运行了, 大概会这样

    
    
    #python static-main.py 
    
    the query is 
    xss_funcs = [
                    "print", "echo"
                    ]
    sql_query_funcs = [
                    "mysql_query", "mysqli_query", "pg_query", "sqlite_query"
                    ]
    os_command_funcs = [
                   "backticks", "exec" , "expect_popen","passthru","pcntl_exec",
                   "popen","proc_open","shell_exec","system", "mail"     
                   ]
      m =[];  queryMapList =[]; g.V().filter{sql_query_funcs.contains(it.code)  && isCallExpression(it.nameToCall().next()) }.callexpressions()
                                .sideEffect{m = start(it, [], 0, 'sql', false, queryMapList)}
                                .sideEffect{ warnmessage = warning(it.toFileAbs().next().name, it.lineno, it.id, 'sql', '1')}
                                .sideEffect{ reportmessage = report(it.toFileAbs().next().name, it.lineno, it.id)}
                                .ifThenElse{m.isEmpty()}
                                  {it.transform{reportmessage}}
                                  {it.transform{findSinkLocation(m, warnmessage, 'sql', queryMapList, it)}}
    Caught exception: <class 'py2neo.error.BadInputException'> groovy.lang.MissingMethodException: No signature of method: com.tinkerpop.gremlin.groovy.jsr223.GremlinGroovyScriptEngine.start() is applicable for argument types: (com.tinkerpop.blueprints.impls.neo4j2.Neo4j2Vertex, java.util.ArrayList, java.lang.Integer, java.lang.String, java.lang.Boolean, java.util.ArrayList) values: [v[721], [], 0, sql, false, []]
    Possible solutions: wait(), any(), every()
    None
    

很显然是作者删除了关键函数

`m = start(it, [], 0, 'sql', false, queryMapList)` # 筛选sql注入节点

`findSinkLocation(m, warnmessage, 'sql', queryMapList, it)` # 查找Sink

所以你不可能直接复现论文里的静态分析结果, 世界上除了作者应该没人知道写的是啥了, issue中也有人反馈这样的问题

[python-joern/Analysis.py at e5f651511143938511ae572b7986bfa92c6c4936 ·
aalhuz/python-joern](https://github.com/aalhuz/python-joern/blob/e5f651511143938511ae572b7986bfa92c6c4936/Analysis.py#L45:9)

![3a12a2b4908cbb9d546c9dcbc43341be.png](https://image.3001.net/images/20200518/158977020186.png!small)

大部分想尝试的人, 面对这样未知的领域, 未知的语言, 未知的代码, 都会就此止步, 可惜了, 我不信邪, 哪怕重新写一个.

> 之后的时间, 去寻找“Tinkerpop Gremlin`的教程,
> 然后学完百度的`HugeGraph教程`才发现市面上的文档都是针对`Tinkerpop 3.x`, 甚至又学习了一个宝藏博主的`Tinkerpop
> 3.x`教程
>
> [PRACTICAL GREMLIN: An Apache TinkerPop
> Tutorial](http://kelvinlawrence.net/book/Gremlin-Graph-Guide.html)
>
> 想着触类旁通, 修复`Tinkerpop 2.x` 的 Navex, 在一个完全陌生的领域探索必然是缓慢而痛苦的, 又过了很久, 找到
> github上面的一份古老文档
>
> [spmallette/GremlinDocs: Gremlin Documentation and
> Samples](https://github.com/spmallette/GremlinDocs)
>
> 这是一份 2012-2015 年的Tinkerpop 2.x文档, 然后勉强把Tinkerpop 2.x文档扣了一遍, 中间穿插学习了编译原理,
> 离散数学, 南大的静态分析课程, 也算是知道了什么是静态分析, 大概的原理和目的也算是清楚了些.
>
> 在浏览器相关收藏快100个了的时候, 前后知识点终于打通了, 被迫完成了作者删除的代码, 回过头来看, 也不是特别难, 硬着头皮写Gremlin遍历,
> 边查边写就是了.

### CPG – Vertex, Edge , Property

`CPG`的`节点`, `边`和`属性`信息都记录在下面这个文件中

`joern/phpjoernsteps/_constants.groovy`

    
    
    // AST node property keys
    
    Object.metaClass.NODE_INDEX = 'id'  // 每个node都有自己的id
    Object.metaClass.NODE_TYPE = 'type' // 节点的类型, 后面`AST node types`有具体描述
    Object.metaClass.NODE_FLAGS = 'flags'   // 参考`AST node flags`, 赋值, 二元操作,判断, 文件包含, 目录信息
    Object.metaClass.NODE_LINENO = 'lineno' // 当前节点所处源文件的行数
    Object.metaClass.NODE_CODE = 'code'     // 引用的函数或者变量的名称
    Object.metaClass.NODE_FUNCID = 'funcid' // 所处文件的文件id
    Object.metaClass.NODE_ENDLINENO = 'endlineno'   // 所处文件的总行数
    Object.metaClass.NODE_NAME = 'name'             // 函数声明的函数名称, 文件的文件名
    Object.metaClass.NODE_DOCCOMMENT = 'doccomment'     // 注释
    
    
    // AST node types
    //g.V().has('type', TYPE_STMT_LIST)
    Object.metaClass.TYPE_STMT_LIST = 'AST_STMT_LIST' // ...; ...; ...;
    Object.metaClass.TYPE_CALL = 'AST_CALL' // foo()
    Object.metaClass.TYPE_STATIC_CALL = 'AST_STATIC_CALL' // bla::foo()
    Object.metaClass.TYPE_METHOD_CALL = 'AST_METHOD_CALL' // $bla->foo()
    Object.metaClass.TYPE_PROP = 'AST_PROP' // e.g., $bla->foo
    Object.metaClass.TYPE_FUNC_DECL = 'AST_FUNC_DECL' // function foo() {}
    Object.metaClass.TYPE_METHOD = 'AST_METHOD' // class bla { ... function foo() {} ... }
    Object.metaClass.TYPE_ARG_LIST = 'AST_ARG_LIST' // foo( $a1, $a2, $a3)
    Object.metaClass.TYPE_PARAM_LIST = 'AST_PARAM_LIST' // function foo( $p1, $p2, $p3) {}
    Object.metaClass.TYPE_PARAM = 'AST_PARAM' // $p1
    Object.metaClass.TYPE_ASSIGN = 'AST_ASSIGN' // $buzz = true
    Object.metaClass.TYPE_ASSIGN_REF = 'AST_ASSIGN_REF' // $b = &$a
    Object.metaClass.TYPE_ASSIGN_OP = 'AST_ASSIGN_OP' // $x += 3
    Object.metaClass.TYPE_NAME = 'AST_NAME' // names (e.g., name of a called function in call expressions)
    Object.metaClass.TYPE_VAR = 'AST_VAR' // $v
    Object.metaClass.TYPE_BINARY_OP = 'AST_BINARY_OP' // e.g., "foo"."bar" or 3+4
    Object.metaClass.TYPE_ENCAPS_LIST = 'AST_ENCAPS_LIST' // e.g., "blah{$var1}buzz $var2 beep"
    Object.metaClass.TYPE_INCLUDE_OR_EVAL = 'AST_INCLUDE_OR_EVAL' // eval, include, require
    //Abeer
    Object.metaClass.TYPE_CALLEE = 'Callee'
    Object.metaClass.TYPE_FUNCTION = 'Function'
    Object.metaClass.TYPE_ECHO = 'AST_ECHO' // echo
    Object.metaClass.TYPE_PRINT = 'AST_PRINT' // PRINT
    
    //ABEER
    Object.metaClass.TYPE_IF_ELEM = 'AST_IF_ELEM' // HOLDES THE COND INSIDE IF 
    Object.metaClass.TYPE_DIM = 'AST_DIM' // _POST[x]
    Object.metaClass.TYPE_ISSET = 'AST_ISSET' // is_set()
    // TODO and many more...
    
    
    // AST node flags
    // of AST_ASSIGN.*
    Object.metaClass.FLAG_ASSIGN_CONCAT = 'ASSIGN_CONCAT' // $v .= "foo"
    // of AST_BINARY_OP
    Object.metaClass.FLAG_BINARY_CONCAT = 'BINARY_CONCAT' // "foo"."bar"
    //Abeer
    Object.metaClass.FLAG_BINARY_EQUAL = 'BINARY_IS_EQUAL' // x==y
    Object.metaClass.FLAG_BINARY_NOT_EQUAL = 'BINARY_IS_NOT_EQUAL'  // x != y
    Object.metaClass.FLAG_BINARY_IS_IDENTICAL = 'BINARY_IS_IDENTICAL'   // 1 === 1
    Object.metaClass.FLAG_BINARY_IS_NOT_IDENTICAL = 'BINARY_IS_NOT_IDENTICAL' // 1 !== 1
    // of AST_INCLUDE_OR_EVAL
    Object.metaClass.FLAG_EXEC_EVAL = 'EXEC_EVAL' // eval("...")
    Object.metaClass.FLAG_EXEC_INCLUDE = 'EXEC_INCLUDE' // include "..."
    Object.metaClass.FLAG_EXEC_INCLUDE_ONCE = 'EXEC_INCLUDE_ONCE' // include_once "..."
    Object.metaClass.FLAG_EXEC_REQUIRE = 'EXEC_REQUIRE' // require "..."
    Object.metaClass.FLAG_EXEC_REQUIRE_ONCE = 'EXEC_REQUIRE_ONCE' // require_once "..."
    
    // TODO and many more...
    
    
    // Other (non-AST) node types
    // 目录结构信息
    Object.metaClass.TYPE_DIRECTORY = 'Directory'
    Object.metaClass.TYPE_FILE = 'File'
    
    Object.metaClass.TYPE_STRING = 'string'
    
    
    // Edge types
    
    Object.metaClass.DIRECTORY_EDGE = 'DIRECTORY_OF'
    Object.metaClass.FILE_EDGE = 'FILE_OF'
    Object.metaClass.AST_EDGE = 'PARENT_OF'
    
    // 不清楚, dvwa里面没有这种边
    Object.metaClass.TYPE_IDENTIFIER_DECL_STMT = 'IdentifierDeclStatement'
    Object.metaClass.TYPE_PARAMETER = 'Parameter'
    
    Object.metaClass.TYPE_FILE = 'File'
    
    // Edge types
    
    
    Object.metaClass.CALLS_EDGE = 'CALLS'  // 类中的函数定义
    Object.metaClass.CFG_EDGE = 'FLOWS_TO' // 用来描述 ControlFlow
    
    Object.metaClass.USES_EDGE = 'USE'
    Object.metaClass.DEFINES_EDGE = 'DEF'
    Object.metaClass.DATA_FLOW_EDGE = 'REACHES'  // 用来描述 DataFlow
    
    Object.metaClass.FUNCTION_TO_AST_EDGE = 'IS_FUNCTION_OF_AST'
    Object.metaClass.FILE_TO_FUNCTION_EDGE = 'IS_FILE_OF'
    
    // Edge keys
    
    Object.metaClass.DATA_FLOW_SYMBOL = 'var' // 如果这是一条`REACHES`的边, 就会有`var`这个key, 其值代表上一个节点流出到下一个节点的变量名
    
    //Abeer
    // phpjoern 自带的过滤函数检测, 这里我们不用
    Object.metaClass.DATA_FLOW_TAINT_SRC = 'taint_src'
    Object.metaClass.DATA_FLOW_TAINT_DST = 'taint_dst'
    

## 漏洞查询代码补全分析

### 参考`Navex`中的算法描述

![](https://blog.riskivy.com/wp-content/uploads/2020/05/c777be916bb8859d2732c3da877fb5be.png)

### 定义sink

`sql_query_funcs = ["mysql_query", "mysqli_query", "pg_query",
"sqlite_query"]`

### 定义repair

`repairs = ["md5", "addslashes", "mysqli_real_escape_string",
"mysql_escape_string"]`

### 寻找 source 可控的 sink

    
    
    VulnerablePaths = g.V().filter{sql_query_funcs.contains(it.code)  && isCallExpression(it.nameToCall().next())}.as('sink')
    .callexpressions().as('sloop').statements().inE('REACHES').outV.loop('sloop')
    { it.loops < 10  }{ it.object.containsLowSource().toList() != []}.path().toList()
    

这里拆开来讲讲

`g.V().filter{sql_query_funcs.contains(it.code) &&
isCallExpression(it.nameToCall().next())}.as('sink')`

`sql_query_funcs.contains(it.code)`

表示节点的`code` 为 `["mysql_query", "mysqli_query", "pg_query", "sqlite_query"]`
其中之一

`isCallExpression(it.nameToCall().next())` 这里涉及2个函数

`isCallExpression` 判断当前节点是不是函数调用

    
    
    // checks whether a given node represents a call expression
    Object.metaClass.isCallExpression = { it ->
        it.type == TYPE_CALL ||
                it.type == TYPE_STATIC_CALL ||
                it.type == TYPE_METHOD_CALL
    }
    
    Object.metaClass.TYPE_CALL = 'AST_CALL' // foo()
    Object.metaClass.TYPE_STATIC_CALL = 'AST_STATIC_CALL' // bla::foo()
    Object.metaClass.TYPE_METHOD_CALL = 'AST_METHOD_CALL' // $bla->foo()
    

`nameToCall` `code`节点的父节点的父节点就是`call节点`

![09c528d95df77735c46b17e7360137b1.png](https://image.3001.net/images/20200518/15897701587845.png!small)

![1c9136149459ef6a63508a649b332a99.png](https://image.3001.net/images/20200518/15897701524871.png!small)

    
    
    /**
     Traverse to enclosing call expression.
     */
    Gremlin.defineStep('nameToCall', [Vertex, Pipe], { i ->
        _().parents().parents()
    })
    
    /**
     Traverse to parent-node of AST nodes.
     */
    Gremlin.defineStep('parents', [Vertex, Pipe], {
        _().in(AST_EDGE)
    })
    
    Object.metaClass.AST_EDGE = 'PARENT_OF'
    

第二部分, 向前遍历查找该`sink`的`source`是否可控

    
    
    .callexpressions()
    .as('sloop') 
    .statements().inE('REACHES').outV
    .loop('sloop'){ it.loops < 10  }{ it.object.containsLowSource().toList() != []}
    .path() //这里一定要保存路径信息
    .toList()   //把路径信息从生成器里读出来, 保存成List方便后续操作
    

`callexpressions`

从上一步返回的满足条件的`code`节点中, 获取他们的`AST_CALL`节点

    
    
    /**
     Traverse to enclosing call expression.
     */
    Gremlin.defineStep('callexpressions', [Vertex, Pipe], { i ->
        _().matchParents { isCallExpression(it) }
    })
    
    /**
     Walk the tree into the direction of the root stopping at the
     enclosing statement and output all parents that match the supplied
     predicate. Note that this may include the enclosing statement node.
     */
    Gremlin.defineStep('matchParents', [Vertex, Pipe], { p ->
        _().parents().loop(1) { !isStatement(it.object) } { p(it.object) }
    })
    
    // A node is a statement node iff its parent is of type TYPE_STMT_LIST
    // Note that each node except for the root node has exactly one
    // parent, so count() is either 0 or 1
    // TODO: we want something more here. In particular, we would also
    // like to return 'true' for if/while/for/foreach/... guards (called
    // "predicates" in the CFG), and we have to think about what we want
    // for statements that enclose other full-fledged statements, e.g., an
    // if-statement node which has a body consisting of many other
    // statements.
    Object.metaClass.isStatement = { it ->
        it.parents().filter { it.type == TYPE_STMT_LIST }.count() == 1
    }
    
    Object.metaClass.TYPE_STMT_LIST = 'AST_STMT_LIST' // ...; ...; ...;
    

`loop`循环体为

`.statements().inE('REACHES').outV`

`statements` 寻找该节点的父节点中的 `TYPE_STMT_LIST` -> `AST_STMT_LIST`

    
    
    /**
     Traverse to statements enclosing supplied AST nodes. This may be
     the node itself.
     */
    Gremlin.defineStep('statements', [Vertex, Pipe], {
        _().ifThenElse { isStatement(it) }
        { it }
                { it.parents().loop(1) { !isStatement(it.object) } }
    });
    
    // A node is a statement node iff its parent is of type TYPE_STMT_LIST
    // Note that each node except for the root node has exactly one
    // parent, so count() is either 0 or 1
    // TODO: we want something more here. In particular, we would also
    // like to return 'true' for if/while/for/foreach/... guards (called
    // "predicates" in the CFG), and we have to think about what we want
    // for statements that enclose other full-fledged statements, e.g., an
    // if-statement node which has a body consisting of many other
    // statements.
    Object.metaClass.isStatement = { it ->
        it.parents().filter { it.type == TYPE_STMT_LIST }.count() == 1
    }
    
    Object.metaClass.TYPE_STMT_LIST = 'AST_STMT_LIST' // ...; ...; ...;
    

`.inE('REACHES').outV`

`REACHES` 是`DataFlow`的数据流向边, 代表了变量的传递

`loop`的条件为

    
    
    .loop('sloop'){ it.loops < 10  }{ it.object.containsLowSource().toList() != []}
    ==>
    arr = []
    for (i=1;i<10;i++){
        if (it.object.containsLowSource().toList() != []){
            arr.add(it.object)   
        }
    }
    return arr
    

`containsLowSource` 查找该节点是否包含来自如下可控输入的变量

`["_GET", "_POST", "_COOKIE", "_REQUEST", "_ENV", "HTTP_ENV_VARS",
"HTTP_POST_VARS", "HTTP_GET_VARS"]`

    
    
    Gremlin.defineStep('containsLowSource', [Vertex, Pipe], {
        def attacker_sources2 = ["_GET", "_POST", "_COOKIE", "_REQUEST", "_ENV", "HTTP_ENV_VARS", "HTTP_POST_VARS", "HTTP_GET_VARS"]
        _().ifThenElse { isAssignment(it) }
        {
            it
                    .as('assign')
                    .as('assign')
                    .rval()
                    .children()
                    .loop('assign') { it.object != null } { true }
                    .match { it.type == "AST_VAR" }
                    .filter { attacker_sources2.contains(it.varToName().next()) }
        }
    
        {
            it
                    .astNodes()
                    .match { it.type == 'AST_VAR' }
                    .filter { attacker_sources2.contains(it.varToName().next()) }
                    .in('PARENT_OF')
        }
                .dedup()
    
    
    });
    
    // checks whether a given node represents an assignment
    Object.metaClass.isAssignment = { it ->
        it.type == TYPE_ASSIGN ||
                it.type == TYPE_ASSIGN_REF ||
                it.type == TYPE_ASSIGN_OP
    }
    
    Object.metaClass.TYPE_ASSIGN = 'AST_ASSIGN' // $buzz = true
    Object.metaClass.TYPE_ASSIGN_REF = 'AST_ASSIGN_REF' // $b = &$a
    Object.metaClass.TYPE_ASSIGN_OP = 'AST_ASSIGN_OP' // $x += 3
    
    /**
     Traverse to right side of an assignment.
     */
    Gremlin.defineStep('rval', [Vertex, Pipe], {
        _().filter { isAssignment(it) }.ithChildren(1)
    });
    
    /**
     Traverse to i'th children.
    
     @param i The child index
     */
    Gremlin.defineStep('ithChildren', [Vertex, Pipe], { i ->
        _().children().filter { it.childnum == i }
    })
    
    /**
     Return all nodes in the subtrees rooted in the current vertices and
     filter them according to a predicate p.
    
     @param p The predicate
     */
    Gremlin.defineStep('match', [Vertex, Pipe], { p ->
        _().astNodes().filter(p)
    })
    
    /**
     Traverse from an AST_VAR node to the name of the variable
     */
    Gremlin.defineStep('varToName', [Vertex, Pipe], {
        _().filter { it.type == TYPE_VAR }.ithChildren(0).code
    })
    
    

### 路径查询返回结果

    
    
    ('len:', 26)
    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/4832' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 4802, u'type': u'AST_CALL', u'id': 4832, u'lineno': 9}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/4829' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 4802, u'type': u'AST_ASSIGN', u'id': 4829, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123318' start=u'node/4821' end=u'node/4829' type=u'REACHES' properties={u'var': u'getid'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/4821' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 4802, u'type': u'AST_ASSIGN', u'id': 4821, u'lineno': 8}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123319' start=u'node/4814' end=u'node/4821' type=u'REACHES' properties={u'var': u'id'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/4814' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 4802, u'type': u'AST_ASSIGN', u'id': 4814, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/5097' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 5028, u'type': u'AST_CALL', u'id': 5097, u'lineno': 10}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5094' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 5028, u'type': u'AST_ASSIGN', u'id': 5094, u'lineno': 10}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123357' start=u'node/5086' end=u'node/5094' type=u'REACHES' properties={u'var': u'getid'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5086' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 5028, u'type': u'AST_ASSIGN', u'id': 5086, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123359' start=u'node/5047' end=u'node/5086' type=u'REACHES' properties={u'var': u'id'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5047' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 5028, u'type': u'AST_ASSIGN', u'id': 5047, u'lineno': 6}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123358' start=u'node/5040' end=u'node/5047' type=u'REACHES' properties={u'var': u'id'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5040' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 5028, u'type': u'AST_ASSIGN', u'id': 5040, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/5167' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 5137, u'type': u'AST_CALL', u'id': 5167, u'lineno': 9}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5164' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 5137, u'type': u'AST_ASSIGN', u'id': 5164, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123376' start=u'node/5156' end=u'node/5164' type=u'REACHES' properties={u'var': u'getid'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5156' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 5137, u'type': u'AST_ASSIGN', u'id': 5156, u'lineno': 8}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123377' start=u'node/5149' end=u'node/5156' type=u'REACHES' properties={u'var': u'id'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5149' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 5137, u'type': u'AST_ASSIGN', u'id': 5149, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/5997' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 5953, u'type': u'AST_CALL', u'id': 5997, u'lineno': 10}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5993' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 10, u'type': u'AST_BINARY_OP', u'id': 5993, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123581' start=u'node/5985' end=u'node/5993' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5985' labels=set([u'AST']) properties={u'id': 5985, u'childnum': 2, u'type': u'AST_ASSIGN', u'lineno': 9, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123588' start=u'node/5972' end=u'node/5985' type=u'REACHES' properties={u'var': u'id', u'taint_src': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5972' labels=set([u'AST']) properties={u'id': 5972, u'childnum': 1, u'type': u'AST_ASSIGN', u'lineno': 7, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123587' start=u'node/5965' end=u'node/5972' type=u'REACHES' properties={u'var': u'id', u'taint_dst': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5965' labels=set([u'AST']) properties={u'id': 5965, u'childnum': 0, u'type': u'AST_ASSIGN', u'lineno': 5, u'funcid': 5953}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/6067' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 5953, u'type': u'AST_CALL', u'id': 6067, u'lineno': 27}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6063' labels=set([u'AST']) properties={u'childnum': 2, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 27, u'type': u'AST_BINARY_OP', u'id': 6063, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123584' start=u'node/5993' end=u'node/6063' type=u'REACHES' properties={u'var': u'result'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5993' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 10, u'type': u'AST_BINARY_OP', u'id': 5993, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123581' start=u'node/5985' end=u'node/5993' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5985' labels=set([u'AST']) properties={u'id': 5985, u'childnum': 2, u'type': u'AST_ASSIGN', u'lineno': 9, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123588' start=u'node/5972' end=u'node/5985' type=u'REACHES' properties={u'var': u'id', u'taint_src': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5972' labels=set([u'AST']) properties={u'id': 5972, u'childnum': 1, u'type': u'AST_ASSIGN', u'lineno': 7, u'funcid': 5953}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123587' start=u'node/5965' end=u'node/5972' type=u'REACHES' properties={u'var': u'id', u'taint_dst': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/5965' labels=set([u'AST']) properties={u'id': 5965, u'childnum': 0, u'type': u'AST_ASSIGN', u'lineno': 5, u'funcid': 5953}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/6164' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 6133, u'type': u'AST_CALL', u'id': 6164, u'lineno': 9}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6160' labels=set([u'AST']) properties={u'childnum': 2, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 9, u'type': u'AST_BINARY_OP', u'id': 6160, u'funcid': 6133}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123608' start=u'node/6152' end=u'node/6160' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6152' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 6133, u'type': u'AST_ASSIGN', u'id': 6152, u'lineno': 8}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123610' start=u'node/6145' end=u'node/6152' type=u'REACHES' properties={u'var': u'id'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6145' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 6133, u'type': u'AST_ASSIGN', u'id': 6145, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/6725' labels=set([u'AST']) properties={u'id': 6725, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 19, u'funcid': 6565}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6721' labels=set([u'AST']) properties={u'childnum': 8, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 19, u'type': u'AST_BINARY_OP', u'id': 6721, u'funcid': 6565}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123686' start=u'node/6710' end=u'node/6721' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6710' labels=set([u'AST']) properties={u'id': 6710, u'childnum': 7, u'type': u'AST_ASSIGN', u'lineno': 18, u'funcid': 6565}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123689' start=u'node/6671' end=u'node/6710' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6671' labels=set([u'AST']) properties={u'childnum': 6, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6671, u'lineno': 15}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123688' start=u'node/6660' end=u'node/6671' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6660' labels=set([u'AST']) properties={u'childnum': 5, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6660, u'lineno': 14}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123687' start=u'node/6588' end=u'node/6660' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6588' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6588, u'lineno': 6}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/6725' labels=set([u'AST']) properties={u'id': 6725, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 19, u'funcid': 6565}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6721' labels=set([u'AST']) properties={u'childnum': 8, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 19, u'type': u'AST_BINARY_OP', u'id': 6721, u'funcid': 6565}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123686' start=u'node/6710' end=u'node/6721' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6710' labels=set([u'AST']) properties={u'id': 6710, u'childnum': 7, u'type': u'AST_ASSIGN', u'lineno': 18, u'funcid': 6565}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123693' start=u'node/6651' end=u'node/6710' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6651' labels=set([u'AST']) properties={u'childnum': 4, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6651, u'lineno': 11}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123692' start=u'node/6612' end=u'node/6651' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6612' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6612, u'lineno': 10}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123691' start=u'node/6599' end=u'node/6612' type=u'REACHES' properties={u'var': u'message', u'taint_src': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6599' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6599, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123690' start=u'node/6577' end=u'node/6599' type=u'REACHES' properties={u'var': u'message', u'taint_dst': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6577' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 6565, u'type': u'AST_ASSIGN', u'id': 6577, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/7137' labels=set([u'AST']) properties={u'id': 7137, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 19, u'funcid': 6977}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7133' labels=set([u'AST']) properties={u'childnum': 8, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 19, u'type': u'AST_BINARY_OP', u'id': 7133, u'funcid': 6977}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123736' start=u'node/7122' end=u'node/7133' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7122' labels=set([u'AST']) properties={u'id': 7122, u'childnum': 7, u'type': u'AST_ASSIGN', u'lineno': 18, u'funcid': 6977}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123739' start=u'node/7083' end=u'node/7122' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7083' labels=set([u'AST']) properties={u'childnum': 6, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 7083, u'lineno': 15}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123738' start=u'node/7072' end=u'node/7083' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7072' labels=set([u'AST']) properties={u'childnum': 5, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 7072, u'lineno': 14}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123737' start=u'node/7000' end=u'node/7072' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7000' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 7000, u'lineno': 6}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/7137' labels=set([u'AST']) properties={u'id': 7137, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 19, u'funcid': 6977}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7133' labels=set([u'AST']) properties={u'childnum': 8, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 19, u'type': u'AST_BINARY_OP', u'id': 7133, u'funcid': 6977}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123736' start=u'node/7122' end=u'node/7133' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7122' labels=set([u'AST']) properties={u'id': 7122, u'childnum': 7, u'type': u'AST_ASSIGN', u'lineno': 18, u'funcid': 6977}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123743' start=u'node/7063' end=u'node/7122' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7063' labels=set([u'AST']) properties={u'childnum': 4, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 7063, u'lineno': 11}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123742' start=u'node/7024' end=u'node/7063' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7024' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 7024, u'lineno': 10}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123741' start=u'node/7011' end=u'node/7024' type=u'REACHES' properties={u'var': u'message', u'taint_src': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7011' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 7011, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123740' start=u'node/6989' end=u'node/7011' type=u'REACHES' properties={u'var': u'message', u'taint_dst': u'san-sql:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/6989' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 6977, u'type': u'AST_ASSIGN', u'id': 6989, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/7320' labels=set([u'AST']) properties={u'id': 7320, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 17, u'funcid': 7184}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7316' labels=set([u'AST']) properties={u'childnum': 6, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 17, u'type': u'AST_BINARY_OP', u'id': 7316, u'funcid': 7184}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123755' start=u'node/7305' end=u'node/7316' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7305' labels=set([u'AST']) properties={u'id': 7305, u'childnum': 5, u'type': u'AST_ASSIGN', u'lineno': 16, u'funcid': 7184}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123757' start=u'node/7266' end=u'node/7305' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7266' labels=set([u'AST']) properties={u'childnum': 4, u'funcid': 7184, u'type': u'AST_ASSIGN', u'id': 7266, u'lineno': 13}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123756' start=u'node/7207' end=u'node/7266' type=u'REACHES' properties={u'var': u'name'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7207' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 7184, u'type': u'AST_ASSIGN', u'id': 7207, u'lineno': 6}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/7320' labels=set([u'AST']) properties={u'id': 7320, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 17, u'funcid': 7184}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7316' labels=set([u'AST']) properties={u'childnum': 6, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 17, u'type': u'AST_BINARY_OP', u'id': 7316, u'funcid': 7184}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123755' start=u'node/7305' end=u'node/7316' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7305' labels=set([u'AST']) properties={u'id': 7305, u'childnum': 5, u'type': u'AST_ASSIGN', u'lineno': 16, u'funcid': 7184}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123760' start=u'node/7227' end=u'node/7305' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7227' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 7184, u'type': u'AST_ASSIGN', u'id': 7227, u'lineno': 10}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123759' start=u'node/7218' end=u'node/7227' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7218' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 7184, u'type': u'AST_ASSIGN', u'id': 7218, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/123758' start=u'node/7196' end=u'node/7218' type=u'REACHES' properties={u'var': u'message'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/7196' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 7184, u'type': u'AST_ASSIGN', u'id': 7196, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/8770' labels=set([u'AST']) properties={u'id': 8770, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 20, u'funcid': 8611}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8766' labels=set([u'AST']) properties={u'childnum': 9, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 20, u'type': u'AST_BINARY_OP', u'id': 8766, u'funcid': 8611}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124065' start=u'node/8755' end=u'node/8766' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8755' labels=set([u'AST']) properties={u'id': 8755, u'childnum': 8, u'type': u'AST_ASSIGN', u'lineno': 19, u'funcid': 8611}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124074' start=u'node/8652' end=u'node/8755' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8652' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8652, u'lineno': 10}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124073' start=u'node/8643' end=u'node/8652' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8643' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8643, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124072' start=u'node/8636' end=u'node/8643' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8636' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8636, u'lineno': 8}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/8770' labels=set([u'AST']) properties={u'id': 8770, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 20, u'funcid': 8611}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8766' labels=set([u'AST']) properties={u'childnum': 9, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 20, u'type': u'AST_BINARY_OP', u'id': 8766, u'funcid': 8611}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124065' start=u'node/8755' end=u'node/8766' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8755' labels=set([u'AST']) properties={u'id': 8755, u'childnum': 8, u'type': u'AST_ASSIGN', u'lineno': 19, u'funcid': 8611}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124064' start=u'node/8746' end=u'node/8755' type=u'REACHES' properties={u'var': u'pass', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8746' labels=set([u'AST']) properties={u'childnum': 7, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8746, u'lineno': 16}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124063' start=u'node/8707' end=u'node/8746' type=u'REACHES' properties={u'var': u'pass', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8707' labels=set([u'AST']) properties={u'childnum': 6, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8707, u'lineno': 15}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124062' start=u'node/8698' end=u'node/8707' type=u'REACHES' properties={u'var': u'pass'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8698' labels=set([u'AST']) properties={u'childnum': 5, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8698, u'lineno': 14}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124061' start=u'node/8691' end=u'node/8698' type=u'REACHES' properties={u'var': u'pass'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/8691' labels=set([u'AST']) properties={u'childnum': 4, u'funcid': 8611, u'type': u'AST_ASSIGN', u'id': 8691, u'lineno': 13}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/9525' labels=set([u'AST']) properties={u'id': 9525, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 15, u'funcid': 9397}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9521' labels=set([u'AST']) properties={u'childnum': 6, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 15, u'type': u'AST_BINARY_OP', u'id': 9521, u'funcid': 9397}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124202' start=u'node/9510' end=u'node/9521' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9510' labels=set([u'AST']) properties={u'id': 9510, u'childnum': 5, u'type': u'AST_ASSIGN', u'lineno': 14, u'funcid': 9397}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124210' start=u'node/9416' end=u'node/9510' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9416' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 9397, u'type': u'AST_ASSIGN', u'id': 9416, u'lineno': 6}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124209' start=u'node/9409' end=u'node/9416' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9409' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 9397, u'type': u'AST_ASSIGN', u'id': 9409, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/9525' labels=set([u'AST']) properties={u'id': 9525, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 15, u'funcid': 9397}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9521' labels=set([u'AST']) properties={u'childnum': 6, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 15, u'type': u'AST_BINARY_OP', u'id': 9521, u'funcid': 9397}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124202' start=u'node/9510' end=u'node/9521' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9510' labels=set([u'AST']) properties={u'id': 9510, u'childnum': 5, u'type': u'AST_ASSIGN', u'lineno': 14, u'funcid': 9397}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124201' start=u'node/9501' end=u'node/9510' type=u'REACHES' properties={u'var': u'pass', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9501' labels=set([u'AST']) properties={u'childnum': 4, u'funcid': 9397, u'type': u'AST_ASSIGN', u'id': 9501, u'lineno': 11}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124200' start=u'node/9462' end=u'node/9501' type=u'REACHES' properties={u'var': u'pass', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9462' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 9397, u'type': u'AST_ASSIGN', u'id': 9462, u'lineno': 10}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124199' start=u'node/9455' end=u'node/9462' type=u'REACHES' properties={u'var': u'pass'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9455' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 9397, u'type': u'AST_ASSIGN', u'id': 9455, u'lineno': 9}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/9701' labels=set([u'AST']) properties={u'id': 9701, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 13, u'funcid': 9651}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9697' labels=set([u'AST']) properties={u'childnum': 4, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 13, u'type': u'AST_BINARY_OP', u'id': 9697, u'funcid': 9651}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124233' start=u'node/9686' end=u'node/9697' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9686' labels=set([u'AST']) properties={u'id': 9686, u'childnum': 3, u'type': u'AST_ASSIGN', u'lineno': 12, u'funcid': 9651}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124238' start=u'node/9663' end=u'node/9686' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9663' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 9651, u'type': u'AST_ASSIGN', u'id': 9663, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/9701' labels=set([u'AST']) properties={u'id': 9701, u'childnum': 1, u'type': u'AST_CALL', u'lineno': 13, u'funcid': 9651}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9697' labels=set([u'AST']) properties={u'childnum': 4, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 13, u'type': u'AST_BINARY_OP', u'id': 9697, u'funcid': 9651}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124233' start=u'node/9686' end=u'node/9697' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9686' labels=set([u'AST']) properties={u'id': 9686, u'childnum': 3, u'type': u'AST_ASSIGN', u'lineno': 12, u'funcid': 9651}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124232' start=u'node/9677' end=u'node/9686' type=u'REACHES' properties={u'var': u'pass', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9677' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 9651, u'type': u'AST_ASSIGN', u'id': 9677, u'lineno': 9}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124231' start=u'node/9670' end=u'node/9677' type=u'REACHES' properties={u'var': u'pass', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/9670' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 9651, u'type': u'AST_ASSIGN', u'id': 9670, u'lineno': 8}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/13369' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13255, u'type': u'AST_CALL', u'id': 13369, u'lineno': 19}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13365' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 19, u'type': u'AST_BINARY_OP', u'id': 13365, u'funcid': 13255}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124975' start=u'node/13350' end=u'node/13365' type=u'REACHES' properties={u'var': u'insert'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13350' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 13255, u'type': u'AST_ASSIGN', u'id': 13350, u'lineno': 18}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124980' start=u'node/13341' end=u'node/13350' type=u'REACHES' properties={u'var': u'pass_new', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13341' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13255, u'type': u'AST_ASSIGN', u'id': 13341, u'lineno': 15}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124979' start=u'node/13302' end=u'node/13341' type=u'REACHES' properties={u'var': u'pass_new', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13302' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 13255, u'type': u'AST_ASSIGN', u'id': 13302, u'lineno': 14}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/124978' start=u'node/13280' end=u'node/13302' type=u'REACHES' properties={u'var': u'pass_new'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13280' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13255, u'type': u'AST_ASSIGN', u'id': 13280, u'lineno': 8}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/13845' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13725, u'type': u'AST_CALL', u'id': 13845, u'lineno': 18}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13841' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 18, u'type': u'AST_BINARY_OP', u'id': 13841, u'funcid': 13725}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125044' start=u'node/13826' end=u'node/13841' type=u'REACHES' properties={u'var': u'insert'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13826' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 13725, u'type': u'AST_ASSIGN', u'id': 13826, u'lineno': 17}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125049' start=u'node/13817' end=u'node/13826' type=u'REACHES' properties={u'var': u'pass_new', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13817' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13725, u'type': u'AST_ASSIGN', u'id': 13817, u'lineno': 14}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125048' start=u'node/13778' end=u'node/13817' type=u'REACHES' properties={u'var': u'pass_new', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13778' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 13725, u'type': u'AST_ASSIGN', u'id': 13778, u'lineno': 13}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125047' start=u'node/13756' end=u'node/13778' type=u'REACHES' properties={u'var': u'pass_new'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13756' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 13725, u'type': u'AST_ASSIGN', u'id': 13756, u'lineno': 7}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/14032' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13931, u'type': u'AST_CALL', u'id': 14032, u'lineno': 16}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/14028' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 16, u'type': u'AST_BINARY_OP', u'id': 14028, u'funcid': 13931}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125066' start=u'node/14013' end=u'node/14028' type=u'REACHES' properties={u'var': u'insert'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/14013' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 13931, u'type': u'AST_ASSIGN', u'id': 14013, u'lineno': 15}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125071' start=u'node/14004' end=u'node/14013' type=u'REACHES' properties={u'var': u'pass_new', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/14004' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 13931, u'type': u'AST_ASSIGN', u'id': 14004, u'lineno': 12}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125070' start=u'node/13965' end=u'node/14004' type=u'REACHES' properties={u'var': u'pass_new', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13965' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 13931, u'type': u'AST_ASSIGN', u'id': 13965, u'lineno': 11}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125069' start=u'node/13943' end=u'node/13965' type=u'REACHES' properties={u'var': u'pass_new'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/13943' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 13931, u'type': u'AST_ASSIGN', u'id': 13943, u'lineno': 5}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/15558' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 15417, u'type': u'AST_CALL', u'id': 15558, u'lineno': 31}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/15554' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 31, u'type': u'AST_BINARY_OP', u'id': 15554, u'funcid': 15417}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125405' start=u'node/15539' end=u'node/15554' type=u'REACHES' properties={u'var': u'insert'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/15539' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 15417, u'type': u'AST_ASSIGN', u'id': 15539, u'lineno': 30}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125410' start=u'node/15530' end=u'node/15539' type=u'REACHES' properties={u'var': u'pass_new', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/15530' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 15417, u'type': u'AST_ASSIGN', u'id': 15530, u'lineno': 27}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125409' start=u'node/15491' end=u'node/15530' type=u'REACHES' properties={u'var': u'pass_new', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/15491' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 15417, u'type': u'AST_ASSIGN', u'id': 15491, u'lineno': 26}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125408' start=u'node/15435' end=u'node/15491' type=u'REACHES' properties={u'var': u'pass_new'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/15435' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 15417, u'type': u'AST_ASSIGN', u'id': 15435, u'lineno': 8}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/16277' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 16040, u'type': u'AST_CALL', u'id': 16277, u'lineno': 69}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16273' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 69, u'type': u'AST_BINARY_OP', u'id': 16273, u'funcid': 16040}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125512' start=u'node/16258' end=u'node/16273' type=u'REACHES' properties={u'var': u'insert'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16258' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 16040, u'type': u'AST_ASSIGN', u'id': 16258, u'lineno': 68}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125519' start=u'node/16249' end=u'node/16258' type=u'REACHES' properties={u'var': u'pass_new', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16249' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 16040, u'type': u'AST_ASSIGN', u'id': 16249, u'lineno': 65}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125518' start=u'node/16210' end=u'node/16249' type=u'REACHES' properties={u'var': u'pass_new', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16210' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 16040, u'type': u'AST_ASSIGN', u'id': 16210, u'lineno': 64}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125517' start=u'node/16168' end=u'node/16210' type=u'REACHES' properties={u'var': u'pass_new'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16168' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 16040, u'type': u'AST_ASSIGN', u'id': 16168, u'lineno': 51}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/16579' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 16362, u'type': u'AST_CALL', u'id': 16579, u'lineno': 61}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16575' labels=set([u'AST']) properties={u'childnum': 3, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 61, u'type': u'AST_BINARY_OP', u'id': 16575, u'funcid': 16362}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125563' start=u'node/16560' end=u'node/16575' type=u'REACHES' properties={u'var': u'insert'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16560' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 16362, u'type': u'AST_ASSIGN', u'id': 16560, u'lineno': 60}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125570' start=u'node/16551' end=u'node/16560' type=u'REACHES' properties={u'var': u'pass_new', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16551' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 16362, u'type': u'AST_ASSIGN', u'id': 16551, u'lineno': 57}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125569' start=u'node/16512' end=u'node/16551' type=u'REACHES' properties={u'var': u'pass_new', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16512' labels=set([u'AST']) properties={u'childnum': 0, u'funcid': 16362, u'type': u'AST_ASSIGN', u'id': 16512, u'lineno': 56}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/125568' start=u'node/16490' end=u'node/16512' type=u'REACHES' properties={u'var': u'pass_new'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/16490' labels=set([u'AST']) properties={u'childnum': 1, u'funcid': 16362, u'type': u'AST_ASSIGN', u'id': 16490, u'lineno': 50}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/122239' labels=set([u'AST']) properties={u'id': 122239, u'childnum': 0, u'type': u'AST_CALL', u'lineno': 40, u'funcid': 121984}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122234' labels=set([u'AST']) properties={u'childnum': 13, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 40, u'type': u'AST_BINARY_OP', u'id': 122234, u'funcid': 121984}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149605' start=u'node/122223' end=u'node/122234' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122223' labels=set([u'AST']) properties={u'id': 122223, u'childnum': 12, u'type': u'AST_ASSIGN', u'lineno': 39, u'funcid': 121984}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149614' start=u'node/122071' end=u'node/122223' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122071' labels=set([u'AST']) properties={u'childnum': 4, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122071, u'lineno': 22}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149613' start=u'node/122062' end=u'node/122071' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122062' labels=set([u'AST']) properties={u'childnum': 3, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122062, u'lineno': 21}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149612' start=u'node/122055' end=u'node/122062' type=u'REACHES' properties={u'var': u'user'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122055' labels=set([u'AST']) properties={u'childnum': 2, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122055, u'lineno': 20}>]
    --------------------------------------------------    [<Node graph=u'http://localhost:7474/db/data/' ref=u'node/122239' labels=set([u'AST']) properties={u'id': 122239, u'childnum': 0, u'type': u'AST_CALL', u'lineno': 40, u'funcid': 121984}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122234' labels=set([u'AST']) properties={u'childnum': 13, u'flags': [u'BINARY_BOOL_OR'], u'lineno': 40, u'type': u'AST_BINARY_OP', u'id': 122234, u'funcid': 121984}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149605' start=u'node/122223' end=u'node/122234' type=u'REACHES' properties={u'var': u'query'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122223' labels=set([u'AST']) properties={u'id': 122223, u'childnum': 12, u'type': u'AST_ASSIGN', u'lineno': 39, u'funcid': 121984}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149603' start=u'node/122165' end=u'node/122223' type=u'REACHES' properties={u'var': u'pass', u'taint_src': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122165' labels=set([u'AST']) properties={u'childnum': 8, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122165, u'lineno': 27}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149602' start=u'node/122126' end=u'node/122165' type=u'REACHES' properties={u'var': u'pass', u'taint_dst': u'san-string:'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122126' labels=set([u'AST']) properties={u'childnum': 7, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122126, u'lineno': 26}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149601' start=u'node/122117' end=u'node/122126' type=u'REACHES' properties={u'var': u'pass'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122117' labels=set([u'AST']) properties={u'childnum': 6, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122117, u'lineno': 25}>,
     <Relationship graph=u'http://localhost:7474/db/data/' ref=u'relationship/149600' start=u'node/122110' end=u'node/122117' type=u'REACHES' properties={u'var': u'pass'}>,
     <Node graph=u'http://localhost:7474/db/data/' ref=u'node/122110' labels=set([u'AST']) properties={u'childnum': 5, u'funcid': 121984, u'type': u'AST_ASSIGN', u'id': 122110, u'lineno': 24}>]
    --------------------------------------------------    

### 遍历已有路径查询`repair`

    
    
    Paths = []
    
    // 向下遍历筛选未经过滤的 VulnerablePath
    for ( vpaths in VulnerablePaths){   //遍历所有存在分析风险的路径, 循环取出每一个path进行分析
        vlen = vpaths.size()            
        p = []
    
        for (int i = 1; i < vlen ; i+=2) {  // path结构是 [v_call,v,e,v,e,v] 这种格式的, 所以1+=2, 遍历节点
            node = vpaths[i];
            if ( i+1 < vlen){   // 因为[v_call,v,e,v,e,v]的形式, 最后一个节点是没有边信息的, 所要边界检查一下
                source_var = vpaths[i+1].var;   // 取出DataFlow边(`REACHES`)上传递的变量名, 给后面做变量筛查
            }
            else{           //最后一个var可能来自于 `$var_id = repair($_POST['id'])` 所以要特殊处理
                source_var = vpaths[i].match {
                            it.type == "AST_VAR" &&
                            it.containsLowSource().toList().size() > 0 }.varToName().toList()[0]
            }
            // 这里要筛选变量, 满足以下条件
            // 首先该节点是 "AST_VAR" 类型的, 也就是个变量
            // 该变量会从当前节点流出到下一个DataFlow节点
            // 该变量没有被过滤:
            //      1.这个变量没有被函数处理
            //      2.这个变量被函数处理了, 但处理函数不是repairs中的函数
            // 输出所有变量名
            alive_vars = node.match{isAssignment(it)}.rval().match {
                        it.type == "AST_VAR" &&
                        it.varToName().toList().contains(source_var) &&
                        it.argToCall().transform{getFuncName(it)}.toList().intersect(repairs) == [] 
                        }.varToName().toList()
    
            // 如果alive_vars中包含了传递出去的变量名, 也就是这个点的变量存活下来, 就添加到p
            if (alive_vars.contains(source_var)){
                  p.add(node);
            }else{      // 否则p=[], i=vlen, 循环结束
                p = []
                i = vlen
            }
        }
        // 如果p=[], 该path被过滤, 不考虑
        if(p.isEmpty()){
            continue
        }
        else{       // 如果p != [], 该path存在风险, 添加该路径到结果`Paths`中
            Paths.add(vpaths)
            p =[]
        }
    
    }
    

上述代码中引用的`getFuncName`

    
    
    // gets the function name of a call expression
    Object.metaClass.getFuncName = { it ->
        if (it.type == TYPE_CALL) {
            // have to call .next() because the calls to ithChildren()
            // implictly convert the vertex 'it' into a Gremlin pipeline, but
            // we know that only one vertex is spit out at the end and we want
            // its 'code' property
            it.ithChildren(0).ithChildren(0).next().code
        } else if (it.type == TYPE_STATIC_CALL ||
                it.type == TYPE_METHOD_CALL) {
            it.ithChildren(1).next().code
        } else {
            null
        }
    }
    

## 完整代码

    
    
    import json
    from pprint import pprint
    
    from Analysis import Analysis
    
    attackType = "sql"
    sa = Analysis(7474)
    query = sa.prepareQueryStatic(attackType)
    
    query = """
    sql_query_funcs = ["mysql_query", "mysqli_query", "pg_query", "sqlite_query"]
    
    repairs = ["md5", "addslashes", "mysqli_real_escape_string", "mysql_escape_string"]
    
    Paths = []
    
    VulnerablePaths = g.V().filter{sql_query_funcs.contains(it.code)  && isCallExpression(it.nameToCall().next())}.as('sink')
    .callexpressions().as('sloop').statements().inE('REACHES').outV.loop('sloop')
    { it.loops < 10  }{ it.object.containsLowSource().toList() != []}.path().toList()
    
    
    for ( vpaths in VulnerablePaths){
        vlen = vpaths.size()
        p = []
    
        for (int i = 1; i < vlen ; i+=2) {
            node = vpaths[i];
            if ( i+1 < vlen){
                source_var = vpaths[i+1].var;
            }
            else{
                source_var = vpaths[i].match {
                            it.type == "AST_VAR" &&
                            it.containsLowSource().toList().size() > 0 }.varToName().toList()[0]
            }
    
            alive_vars = node.match{isAssignment(it)}.rval().match {
                        it.type == "AST_VAR" &&
                        it.varToName().toList().contains(source_var) &&
                        it.argToCall().transform{getFuncName(it)}.toList().intersect(repairs) == [] 
                        }.varToName().toList()
    
    
            if (alive_vars.contains(source_var)){
                  p.add(node);
            }else{
                p = []
                i = vlen
            }
        }
    
        if(p.isEmpty()){
            continue
        }
        else{
            Paths.add(vpaths)
            p =[]
        }
    
    }
    
    
    result = []
    for (x in Paths){
        result.add([x[0].toFileAbs().next().name, x[0].lineno, getFuncName(x[0])])
        for (int i = 1; i < x.size() ; i+=2){
            result.add([x[i].toFileAbs().next().name, x[i].lineno, x[i].match{it.type == 'AST_VAR'}.resolveCallArgsNew3()])
        }
        result.add("------------------")
    }
    
    result
    
    """
    
    result, elapsed_time = sa.runTimedQuery(query)
    print(query)
    print("result:")
    # print (result)
    # exit()
    if type(result) == list:
        print("len:", len(result))
        for x in result:
            # print(type(x), type("AST_CALL"))
            print(x)
        exit()
    try:
        print (json.dumps(result, indent=2))
    except:
        print (result)
    
    

## 安装与使用

### 安装 Navex -> `python-joern for php`

如果按照论文作者的github来安装, 最多到 `python-joern` 查询这一步就走不下去了,

如上文, 作者删除最关键的`漏洞查询语句`

这边我整理一下资源, 上传到github, 因为有些资源不是很好找, 而且代码不全, 我花费了了大量的业余时间修补填坑

<https://github.com/UUUUnotfound/Navex_fixed>

  1. 目录结构

    
    
    ubuntu@ubuntu:~/Navex$ tree  -L 2
    .
    ├── batch-import        # 批量数据导入Neo4j
    │   ├── batch_importer_21.zip
    │   ├── import.bat
    │   ├── import.sh
    │   ├── lib
    │   └── readme.md
    ├── joern               # joern, 这里主要使用 `phpast2cpg`
    │   ├── AUTHORS
    │   ├── build
    │   ├── build.gradle
    │   ├── build.sh
    │   ├── docs
    │   ├── eclipse
    │   ├── gremtest
    │   ├── joern-parse
    │   ├── joern-server.sh
    │   ├── LICENSE
    │   ├── phpast2cpg
    │   ├── projects
    │   ├── python
    │   ├── README.md
    │   ├── RELEASE_NOTES
    │   └── settings.gradle
    ├── neo4j-community-2.1.8  # Neo4j图数据库, 默认数据库文件存放位置`data/graph.db`
    │   ├── bin
    │   ├── CHANGES.txt
    │   ├── conf
    │   ├── data
    │   ├── lib
    │   ├── LICENSES.txt
    │   ├── LICENSE.txt
    │   ├── NOTICE.txt
    │   ├── plugins
    │   ├── README.txt
    │   ├── system
    │   └── UPGRADE.txt
    ├── phpjoern            # 主要用`php2ast`来生成`nodes.csv`, `rels.csv`
    │   ├── 1.php
    │   ├── AUTHORS
    │   ├── conf
    │   ├── LICENSE
    │   ├── php2ast
    │   ├── README.md
    │   └── src
    ├── php_src             # 这里存放测试文件源码, 我这里准备的是`dvwa`, `graph.db`是我生成好的Neo4j数据
    │   ├── dvwa
    │   └── graph.db
    └── python-joern        # 用来连接`localhost:7474`进行图查询, `main_test.py`是demo文件, 可以查询sql注入
        ├── Analysis.py
        ├── docs
        ├── exploitFinding.py
        ├── ExploitSeed.py
        ├── joern
        ├── LICENSE
        ├── main_test.py
        ├── README.md
        ├── setup.py
        ├── static-main.py
        ├── staticResults.py
        └── testing
    

  1. 安装依赖

    
    
    git clone https://github.com/UUUUnotfound/Navex_fixed
    cd Navex_fixed
    sudo apt install php7.0 php-ast python-dev graphviz libgraphviz-dev pkg-config python-setuptools python-pip openjdk-8-jdk groovy -y
    sudo pip install py2neo==2.0.7 -i https://pypi.tuna.tsinghua.edu.cn/simple 
    grape install commons-net commons-net 3.3
    grape install com.github.jsqlparser jsqlparser 1.1
    

### 运行Navex -> `python-joern for php`

  1. 生成`CPG`数据并导入`Neo4j`

    
    
    APP_NAME=dvwa
    mkdir workspace && cd $_
    ../phpjoern/php2ast ../php_src/$APP_NAME
    ../joern/phpast2cpg nodes.csv rels.csv
    
    HEAP=3G
    JEXP_HOME=../batch-import/
    PHPJOERN_HOME=../phpjoern/
    java -classpath "$JEXP_HOME/lib/*" -Dfile.encoding=UTF-8 org.neo4j.batchimport.Importer $PHPJOERN_HOME/conf/batch.properties graph.db nodes.csv rels.csv,cpg_edges.csv
    
    cp -R  graph.db ../neo4j-community-2.1.8/data/
    

  1. 启动`Neo4j`

    
    
    cd neo4j-community-2.1.8/bin
    ./neo4j console
    

浏览器访问`<http://localhost:7474/browser/>`, 选择左侧`labels`->`Filesystem`可以看到如下界面,
数据库已经加载成功

![8fc64b6aeda5f3a4766f497f8beaf906.png](https://image.3001.net/images/20200518/15897700673488.png!small)  

  1. 使用`python-joern`进行查询

    
    
    cd python-joern
    python main_test.py
    

## 查询结果分析

### 查询结果

    
    
    ('len:', 20)
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/high.php', 9, u'mysqli_query']
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/high.php', 9, [u'$result', u'$getid', u'$GLOBALS']]
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/high.php', 8, [u'$getid', u'$id']]
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/high.php', 5, [u'$id', u'$_COOKIE']]
    ------------------    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/low.php', 9, u'mysqli_query']
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/low.php', 9, [u'$result', u'$getid', u'$GLOBALS']]
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/low.php', 8, [u'$getid', u'$id']]
    [u'../php_src/dvwa/vulnerabilities/sqli_blind/source/low.php', 5, [u'$id', u'$_GET']]
    ------------------    [u'../php_src/dvwa/vulnerabilities/sqli/source/low.php', 9, u'mysqli_query']
    [u'../php_src/dvwa/vulnerabilities/sqli/source/low.php', 9, [u'$result', u'$query', u'$GLOBALS', u'$___mysqli_res']]
    [u'../php_src/dvwa/vulnerabilities/sqli/source/low.php', 8, [u'$query', u'$id']]
    [u'../php_src/dvwa/vulnerabilities/sqli/source/low.php', 5, [u'$id', u'$_REQUEST']]
    ------------------    [u'../php_src/dvwa/vulnerabilities/brute/source/low.php', 13, u'mysqli_query']
    [u'../php_src/dvwa/vulnerabilities/brute/source/low.php', 13, [u'$result', u'$query', u'$GLOBALS', u'$___mysqli_res']]
    [u'../php_src/dvwa/vulnerabilities/brute/source/low.php', 12, [u'$query', u'$pass', u'$user']]
    [u'../php_src/dvwa/vulnerabilities/brute/source/low.php', 5, [u'$user', u'$_GET']]
    ------------------    

### 漏洞所在文件

`dvwa/vulnerabilities/sqli_blind/source/high.php`

    
    
    <?php
    
    if( isset( $_COOKIE[ 'id' ] ) ) {
        // Get input
        $id = $_COOKIE[ 'id' ];
    
        // Check database
        $getid  = "SELECT first_name, last_name FROM users WHERE user_id = '$id' LIMIT 1;";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $getid ); // Removed 'or die' to suppress mysql errors
    
        // Get results
        $num = @mysqli_num_rows( $result ); // The '@' character suppresses errors
        if( $num > 0 ) {
            // Feedback for end user
            $html .= '<pre>User ID exists in the database.</pre>';
        }
        else {
            // Might sleep a random amount
            if( rand( 0, 5 ) == 3 ) {
                sleep( rand( 2, 4 ) );
            }
    
            // User wasn't found, so the page wasn't!
            header( $_SERVER[ 'SERVER_PROTOCOL' ] . ' 404 Not Found' );
    
            // Feedback for end user
            $html .= '<pre>User ID is MISSING from the database.</pre>';
        }
    
        ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);
    }
    
    ?>
    
    

`dvwa/vulnerabilities/sqli_blind/source/low.php`

    
    
    <?php
    
    if( isset( $_GET[ 'Submit' ] ) ) {
        // Get input
        $id = $_GET[ 'id' ];
    
        // Check database
        $getid  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $getid ); // Removed 'or die' to suppress mysql errors
    
        // Get results
        $num = @mysqli_num_rows( $result ); // The '@' character suppresses errors
        if( $num > 0 ) {
            // Feedback for end user
            $html .= '<pre>User ID exists in the database.</pre>';
        }
        else {
            // User wasn't found, so the page wasn't!
            header( $_SERVER[ 'SERVER_PROTOCOL' ] . ' 404 Not Found' );
    
            // Feedback for end user
            $html .= '<pre>User ID is MISSING from the database.</pre>';
        }
    
        ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);
    }
    
    ?>
    

`dvwa/vulnerabilities/sqli/source/low.php`

    
    
    <?php
    
    if( isset( $_REQUEST[ 'Submit' ] ) ) {
        // Get input
        $id = $_REQUEST[ 'id' ];
    
        // Check database
        $query  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    
        // Get results
        while( $row = mysqli_fetch_assoc( $result ) ) {
            // Get values
            $first = $row["first_name"];
            $last  = $row["last_name"];
    
            // Feedback for end user
            $html .= "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
        }
    
        mysqli_close($GLOBALS["___mysqli_ston"]);
    }
    
    ?>
    

`dvwa/vulnerabilities/brute/source/low.php`

    
    
    <?php
    
    if( isset( $_GET[ 'Login' ] ) ) {
        // Get username
        $user = $_GET[ 'username' ];
    
        // Get password
        $pass = $_GET[ 'password' ];
        $pass = md5( $pass );
    
        // Check the database
        $query  = "SELECT * FROM `users` WHERE user = '$user' AND password = '$pass';";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    
        if( $result && mysqli_num_rows( $result ) == 1 ) {
            // Get users details
            $row    = mysqli_fetch_assoc( $result );
            $avatar = $row["avatar"];
    
            // Login successful
            $html .= "<p>Welcome to the password protected area {$user}</p>";
            $html .= "<img src=\"{$avatar}\" />";
        }
        else {
            // Login failed
            $html .= "<pre><br />Username and/or password incorrect.</pre>";
        }
    
        ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);
    }
    
    ?>
    

虽说存在一些误报, 但是基本实现了漏洞分析查询的功能

### 漏报原因分析

  1. `dvwa/vulnerabilities/sqli/source/medium.php`

    
    
    <?php
    
    <?php
    
    if( isset( $_POST[ 'Submit' ] ) ) {
        // Get input
        $id = $_POST[ 'id' ];
    
        $id = mysqli_real_escape_string($GLOBALS["___mysqli_ston"], $id);
    
        $query  = "SELECT first_name, last_name FROM users WHERE user_id = $id;";
        $result = mysqli_query($GLOBALS["___mysqli_ston"], $query) or die( '<pre>' . mysqli_error($GLOBALS["___mysqli_ston"]) . '</pre>' );
    
        // Get results
        while( $row = mysqli_fetch_assoc( $result ) ) {
            // Display values
            $first = $row["first_name"];
            $last  = $row["last_name"];
    
            // Feedback for end user
            $html .= "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
        }
    
    }
    
    // This is used later on in the index.php page
    // Setting it here so we can close the database connection in here like in the rest of the source scripts
    $query  = "SELECT COUNT(*) FROM users;";
    $result = mysqli_query($GLOBALS["___mysqli_ston"],  $query ) or die( '<pre>' . ((is_object($GLOBALS["___mysqli_ston"])) ? mysqli_error($GLOBALS["___mysqli_ston"]) : (($___mysqli_res = mysqli_connect_error()) ? $___mysqli_res : false)) . '</pre>' );
    $number_of_rows = mysqli_fetch_row( $result )[0];
    
    mysqli_close($GLOBALS["___mysqli_ston"]);
    ?>
    

Medium级别的代码利用`mysql_real_escape_string`函数对以下特殊符号进行转义

  * `\x00`
  * `\n`
  * `\r`
  * `\`
  * `'`
  * `"`
  * `\x1a`

但是此处为数字型注入不需要单引号, 可以绕过

`$query = "SELECT first_name, last_name FROM users WHERE user_id = $id;";`

所以这里还有优化空间, 比如多一步判断`注入类型`, 然后忽略`无效的过滤`

  1. `dvwa/vulnerabilities/sqli/source/high.php`

    
    
    <?php
    
    if( isset( $_SESSION [ 'id' ] ) ) {
        // Get input
        $id = $_SESSION[ 'id' ];
    
        // Check database
        $query  = "SELECT first_name, last_name FROM users WHERE user_id = '$id' LIMIT 1;";
        $result = mysqli_query($GLOBALS["___mysqli_ston"], $query ) or die( '<pre>Something went wrong.</pre>' );
    
        // Get results
        while( $row = mysqli_fetch_assoc( $result ) ) {
            // Get values
            $first = $row["first_name"];
            $last  = $row["last_name"];
    
            // Feedback for end user
            $html .= "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
        }
    
        ((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);        
    }
    
    ?>
    

这里使用的是`$_SESSION [ 'id' ]`注入, 通过访问

`dvwa/vulnerabilities/sqli/session-input.php`

其实该点可控 `$_SESSION[ 'id' ] = $_POST[ 'id' ];`

    
    
    <?php
    
    define( 'DVWA_WEB_PAGE_TO_ROOT', '../../' );
    require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';
    
    dvwaPageStartup( array( 'authenticated', 'phpids' ) );
    
    $page = dvwaPageNewGrab();
    $page[ 'title' ] = 'SQL Injection Session Input' . $page[ 'title_separator' ].$page[ 'title' ];
    
    if( isset( $_POST[ 'id' ] ) ) {
        $_SESSION[ 'id' ] =  $_POST[ 'id' ];
        //$page[ 'body' ] .= "Session ID set!<br /><br /><br />";
        $page[ 'body' ] .= "Session ID: {$_SESSION[ 'id' ]}<br /><br /><br />";
        $page[ 'body' ] .= "<script>window.opener.location.reload(true);</script>";
    }
    
    $page[ 'body' ] .= "
    <form action=\"#\" method=\"POST\">
        <input type=\"text\" size=\"15\" name=\"id\">
        <input type=\"submit\" name=\"Submit\" value=\"Submit\">
    </form>
    <hr />
    <br />
    
    <button onclick=\"self.close();\">Close</button>";
    
    dvwaSourceHtmlEcho( $page );
    
    ?>
    

但是从单文件来看, 该输入点不可控, 所以产生了漏报, 如果优化需要解析 `include`等节点进行跨文件判断

  1. `dvwa/vulnerabilities/sqli_blind/source/medium.php`

    
    
    <?php
    
    if( isset( $_POST[ 'Submit' ]  ) ) {
        // Get input
        $id = $_POST[ 'id' ];
        $id = ((isset($GLOBALS["___mysqli_ston"]) && is_object($GLOBALS["___mysqli_ston"])) ? mysqli_real_escape_string($GLOBALS["___mysqli_ston"],  $id ) : ((trigger_error("[MySQLConverterToo] Fix the mysql_escape_string() call! This code does not work.", E_USER_ERROR)) ? "" : ""));
    
        // Check database
        $getid  = "SELECT first_name, last_name FROM users WHERE user_id = $id;";
        $result = mysqli_query($GLOBALS["___mysqli_ston"],  $getid ); // Removed 'or die' to suppress mysql errors
    
        // Get results
        $num = @mysqli_num_rows( $result ); // The '@' character suppresses errors
        if( $num > 0 ) {
            // Feedback for end user
            $html .= '<pre>User ID exists in the database.</pre>';
        }
        else {
            // Feedback for end user
            $html .= '<pre>User ID is MISSING from the database.</pre>';
        }
    
        //mysql_close();
    }
    
    ?>
    

这里也是数字型注入的问题, 不再赘述

## 总结

本文重点在于静态分析部分的修复, 动态分析部分其实相对简单一些, 也就是剪枝的过程, 后续也可以实现.

我的想法是:

  1. 静态分析使用`Joern`, `Codeql`等工具来实现, 然后生成导航图
  2. exp使用固定`poc`\+ 动态变异 fuzzing 的思想
  3. 动态爬虫使用论文中所使用的`crawler4j` 或者最近比较火的`crawlergo`
  4. 然后后端使用`Baidu Rasp`, `prvd`来实现监控是否执行成功

> PS.也可以实现一种类似动态跃点的标记, 比如挖掘反序列化的利用链, 具有某些特性的的节点,
>
> 比如 `$a=$this->$ppp; $a->arr($b);`
>
> 那么这个点只是`L1级别`的信息, 但是配合`unserialize`, 配合其他的类的`__call`,
>
> 将这些`L1`的标记组合起来,就能组合成存在风险的`L2级别`的安全风险.

最近对`自动化审计`, `AEG`这方面比较感兴趣, 欢迎讨论.

## 参考

<https://github.com/UUUUnotfound/Navex_fixed>

