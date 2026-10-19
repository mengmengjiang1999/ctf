本文会先介绍CodeQL是什么，基本语法和用法，最后是我在编写shiro反序列化漏洞提取规则的过程中遇到的问题，按照这三步来介绍CodeQL的使用方法

## CodeQL介绍

CodeQL是一个支持多种语言及框架的代码分析平台，由Semmle公司开发，现已被GitHub收购，它可以从代码中提取信息构成一个数据库，我们可以通过编写查询语句获得我们想要的信息，对于安全来说CodeQL可以用来做白盒代码审计，针对已知漏洞编写查询规则，整合之后可以就用这些规则来发现代码中类似的漏洞  
支持的语言和框架可以在官方文档查看  
https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/

### CodeQL安装

CodeQL主要分为引擎和库两部分，都可以在github上下载，核心的解析引擎部分是不开源的，用于解析数据库执行查询等操作，库是开源的，针对不同语言提供了很多函数和类型以方便我们编写自己的规则  
CodeQL提供了命令行工具和vscode插件两个选择，vscode插件底层也是调用命令行工具，但是有图形界面并且封装了一些功能，用起来会更加方便  
安装命令行版本需要下载安装包解压并配置环境变量，然后下载官方的CodeQL库放在软件包同级即可，CodeQL引擎会自动在上下级目录搜索库  
安装vscode版本需要搜索安装CodeQL插件，插件会在环境变量中搜索CodeQL引擎，如果没找到会自动下载引擎，安装插件后需要下载官方提供的工作区文件夹，使用vscode打开即可，其中已经包含了库文件  
具体过程可以参照官方文档：  
<https://codeql.github.com/docs/codeql-overview/>

###
工作流程![](https://image.3001.net/images/20211013/1634096361_616654e9c14a8fa07e5f6.png!small)

主要分两步，先提取数据库，然后我们就可以执行查询提取数据

提取数据库即图中的extraction部分，提取过程对编译语言和解释型语言有一定区别，解释型语言如python，数据库时会使用解释器来提取，像java这样的编译型语言需要调用编译器，在编译过程中提取需要的信息，最终CodeQL会获得源码的抽象语法树信息(AST)，和源码一起打包为数据库

查询包括上图查询编译部分和执行部分，我们的查询会和库一起交给编译器编译，编译成功后会进行查询，去数据库中提取数据

# 基本语法

具体请参考官方文档

https://codeql.github.com/docs/ql-language-reference/

## 基本数据类型

![](https://image.3001.net/images/20211013/1634096763_6166567b642cd35a4a4aa.png!small)

### 结构

    
    
    /**
     * @id java/examples/shiro
     * @name shiro
     * @description shiro
     * @kind path-problem
     * @problem.severity warning
     */
     //定义元数据
    
    import java // 导入使用的库
    
    predicate myfunc(Expr expSrc, Expr expDest) {
        //定义函数等
    }
    
    class myclass extends Class {
       //定义类型
    }
    
    from /* ... 变量声明... */
    where /* ... 逻辑公式 ... */
    select /* ... 表达式 ... */

## 函数

封装我们的逻辑，让我们的查询部分逻辑更简明清晰，CodeQL中的函数原名叫predicate，翻译是谓词

用函数前

    
    
    from int i
    where i in [1..9]
    select i

用函数后

    
    
    //声明函数，函数名必须小写字母开头
    predicate isSmall(int i) {
        i in [1 .. 9]
    }
    
    //进行查询
    from int i
    where isSmall(i)
    select i

### 类

CodeQL中，类用来代表符合某种逻辑的值，比如我们想要找到一个java方法，并且方法名叫main，我们可以用CodeQL库定义好的Method类，他代表所有java方法，然后定义一个Main类继承Method这个类，并加上我们的逻辑，只要名字是main的方法

    
    
    import java
    
    class Main extends Method {
        Main() {
            this.getName()="main"
        }    
    }
    
    from Main main
    select main

CodeQL语法规定声明的类必须是大写字母开头，其中和类名名称相同的方法为特征谓词，特征谓词中的this代表父类而不是和java一样代表本身，我们在特征谓词中加我们的逻辑，比如名字是main

每个类都必须继承一个父类，父类的值就是子类的初始值集，一般自定义的类都会根据需要继承库提供的类，比如例子中的Method类，一个类也可以同时继承多个类，代表同时满足父类逻辑的值

## 污点追踪

污点追踪是CodeQL提供的一个非常强大的功能，也是进行代码审计的基础，CodeQL会分析代码得到一张有向图，参数和表达式就是里面的节点，以下面一段代码为例子

    
    
    int func(int tainted) {
       int x = tainted;
       if (someCondition) {
         int y = x;
         callFoo(y);
       } else {
         return x;
       }
       return -1;
    }

![](https://image.3001.net/images/20211013/1634097163_6166580b9b9d08292d9eb.png!small)

有了这样的图我们可以借此分析代码参数的流向来寻找漏洞，库提供了TaintTracking::Configuration这个类，我们需要继承这个类，通过覆盖实现isSource方法和isSink方法来设置起始点和终点，方法会提供dataflow::node参数，我们通过把逻辑加在节点上来设置我们想要的起点和终点，这样CodeQL分析变量的流向，如果发现了有变量从source到sink，就可能会发现潜在的漏洞，比如从getParameter到query，这可能就是一个sql注入![](https://image.3001.net/images/20211013/1634097204_616658344f82367d72aae.png!small)

CodeQL还提供了更强大的功能，isSanitizer()方法可以让我们设置净化方法，设置一个节点，当流到达这个节点后中断，比如replace()这样的过滤函数，CodeQL并不知道他的作用，我们可以中断调用了这个方法的数据流来降低误报![](https://image.3001.net/images/20211013/1634097231_6166584f6c4747fe8fd14.png!small)

同样的，CodeQL并不能识别全部的变量传递，比如这次shiro的规则中遇到的cookie.getvalue()方法，CodeQL并不能把cookie和cookie.getvalue()连起来，这时候我们可以通过isAdditionalTaintStep()方法告诉污点追踪把这两个节点连起来![](https://image.3001.net/images/20211013/1634097261_6166586dcc54c38ab229e.png!small)

# 遇到的问题

### 获取数据库

写shiro规则的过程中遇到的第一个问题是我没想到的，shiro1.2.4非常有历史，而CodeQL获得java的数据库是要用maven编译的，所以环境搭建花了不少事件，也有不少问题，最后试出来以下环境可以成功，希望想做一遍的师傅能避开一些坑，当然也可以直接找我要数据库

> 1.整体环境，mvn3.1.1，java1.7，最新的svn，CodeQL 2.6.0
>
> 2.获得数据库的命令CodeQL database create shiro1.2.4 --language=java --overwrite
> --command="mvn package -Dmaven.test.skip"
>
> 3.mvn安装目录conf下的setting.xml中换阿里的源

### 污点追踪无法找到路径

刚开始的时候通过面的设置想找到路径，但是污点追踪一直没有结果

    
    
    class VulConfig extends TaintTracking::Configuration {
        VulConfig() { this = "shiroConfig" }
      
        override predicate isSource(DataFlow::Node source) { 
            exists(MethodAccess call | 
                call.getMethod().getName()="getCookie" and
                source.asExpr()=call
            )
        }
    
        override predicate isSink(DataFlow::Node sink) {
            exists(MethodAccess call | 
                call.getMethod().getName()="getValue" and
                sink.asExpr()=call
            )
        }
    }
    
    from VulConfig config, DataFlow::PathNode source, DataFlow::PathNode sink
    where config.hasFlowPath(source, sink)
    select sink.getNode(), source, sink, "source are"

后来发现问题在于上文讲污点追踪连接两个点时的那个例子，CodeQL不认为cookie和cookie.getvalue()是一个值，我们的source和sink设置的是两个方法的调用，CodeQL认为方法调用的值等于他的返回值，也就是a.getCookie()的值是cookie，cookie.getValue()的值是Value，所以这两个节点之间是断的，解决办法就是通过污点追踪的isAdditionalTaintStep()把这两个节点连起来，让cookie等于cookie.getValue()

### 连接CodeQL无法识别的节点

我们说过CodeQL并不能识别所有有关系的节点，所以在shiro这个例子中我在设置了getCookies和readObject这两个起点和终点后我还要找中间断的地方，我的方法是找了一篇分析shiro反序列化的文章，让我能知道变量在方法中的传递路径，然后设置source为getcookies，把sink沿着变量传递的链完后推，看断在哪里，最后找到需要连接的四个地方

### 最终代码

    
    
    /**
     * @id java/examples/shiro
     * @name shiro
     * @description shiro
     * @kind path-problem
     * @problem.severity warning
     */
    
    import java
    import semmle.code.java.dataflow.FlowSources
    import DataFlow::PathGraph
    
    predicate isCookiegetValue(Expr expSrc, Expr expDest) {
        exists(Method method, MethodAccess call| 
            expSrc.getType().toString()="Cookie" and 
            expDest=call and 
            call.getMethod() = method and 
            method.hasName("getValue") and 
            method.getDeclaringType().toString() = "Cookie"
        )
    }
    
    predicate isReadObject(Expr expSrc, Expr expDest) {
        exists(Method method, MethodAccess call| 
            expSrc.getType().toString()="ObjectInputStream" and 
            expDest=call and
            call.getMethod() = method and 
            method.hasName("readObject") and 
            method.getDeclaringType().toString() = "ObjectInputStream"
        )
    }
    
    predicate isBase64(Expr expSrc, Expr expDest) {
        exists(Method method, MethodAccess call| 
            expSrc.getType().toString()="String" and 
            expDest=call and
            call.getMethod() = method and 
            method.hasName("decode") and 
            method.getDeclaringType().toString() = "Base64"
        )
    }
    
    predicate isdecrypt(Expr expSrc, Expr expDest) {
        exists(Method method, MethodAccess call| 
            expSrc.getType().toString()="byte" and 
            expDest=call and
            call.getArgument(0)=expSrc and
            call.getMethod() = method and 
            method.hasName("decrypt") and 
            method.getDeclaringType().toString() = "CipherService"
        )
    }
    
    class VulConfig extends TaintTracking::Configuration {
        VulConfig() { this = "shiroConfig" }
      
        override predicate isSource(DataFlow::Node source) { 
            exists(MethodAccess call | 
                call.getMethod().getName()="getCookies" and
                source.asExpr()=call
            )
        }
    
        override predicate isSink(DataFlow::Node sink) {
            exists(MethodAccess call | 
                call.getMethod().getName()="readObject" and
                sink.asExpr()=call
            )
        }
    
        override predicate isAdditionalTaintStep(DataFlow::Node node1, DataFlow::Node node2) {
            isCookiegetValue(node1.asExpr(), node2.asExpr()) or
            isReadObject(node1.asExpr(), node2.asExpr()) or
            isBase64(node1.asExpr(), node2.asExpr()) or
            isdecrypt(node1.asExpr(), node2.asExpr())
        }
    }
    
    from VulConfig config, DataFlow::PathNode source, DataFlow::PathNode sink
    where config.hasFlowPath(source, sink)
    select sink.getNode(), source, sink, "source are"

###
效果![](https://image.3001.net/images/20211013/1634097862_61665ac681d9a6a855736.png!small)

## 参考

官方文档  
https://codeql.github.com/docs/codeql-overview/about-codeql/

  

