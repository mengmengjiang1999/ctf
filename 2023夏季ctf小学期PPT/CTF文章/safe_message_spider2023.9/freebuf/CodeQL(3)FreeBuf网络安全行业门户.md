# 前言

上一篇通过官方文档给出的4个小故事，我们学习了QL语言的大概的使用，这篇来学习关于`CodeQL
queries`的相关知识，这部分是对`Java`语言进行介绍。也就是在CodeQL平台上对实际的项目进行分析的查询编写。

# Basic query

看以下`Java`代码：

    
    
    public class TestJava {
        void myJavaFun(String s) {
            boolean b = s.equals("");
        }
    }
    

或者`Kotlin`代码：

    
    
    void myKotlinFun(s: String) {
        var b = s.equals("")
    }
    

上面两种代码，站在安全编码的角度，我们应该将`s.equals("")`替换为`s.isEmpty()`

所以我们需要查找处项目中的此类代码，查询如下：

    
    
    from MethodAccess ma
    where
        ma.getMethod().hasName("equals") and
        ma.getArgument(0).(StringLiteral).getValue() = ""
    select ma, "This comparison to empty string is inefficient, use isEmpty() instead."
    

`MethodAccess：`方法调用类，获取的就是所有的方法调用

`ma.getMethod().hasName("equals")`限制调用方法名必须为`equals`，

`ma.getArgument(0).(StringLiteral).getValue() = ""`，限制调用方法的第一个参数字面量为`”“`

![image.png](https://image.3001.net/images/20221213/1670943521_63989321be9941cea5634.png!small)  
![image.png](https://image.3001.net/images/20221213/1670943534_6398932e7ab0534ad177c.png!small)

# CodeQL library for Java

CodeQL提供了一个专门针对Java项目做分析的库，这个库中的类以面向对象的形式呈现数据库中的数据，并提供大量谓词帮助分析。

该库作为一组QL模块实现，模块即具有`.qll`扩展名的文件，`java.qll`模块导入了所有的核心Java库模块。

    
    
    import java
    

接下来简要写一下此库中较为重要的类和谓词。

## Summary of the library classes

标准 Java 库中最重要的类可以分为五个主要类别：

  1. 用于表示程序元素（如类和方法）的类

  2. 用于表示 AST 节点（如语句和表达式）的类

  3. 用于表示元数据（如批注和注释）的类

  4. 用于计算指标(如复杂度和耦合）的类

  5. 用于对调用图进行操作的类

其中第一种最多也是最复杂，第四种不做讲解，有兴趣的自行学习

## Program elements

程序元素类包括程序中进行命名的元素：包(`Package`), 编译单元 (`CompilationUnit`), 类型(`Type`), 方法
(`Method`),构造器 (`Constructor`), 变量(`Variable`)。

上述几种的共同超类是`Element`，提供了一般成员谓词，来确定程序元素的名称并检查两个元素是否嵌套。

 **Types** 类有大量的子类来表示不同类型的类：

  * `PrimitiveType`表示基本类型，例如`boolean`,`byte`,`char`,`double`,`float`,`int`,`long`,`short`，QL还将`void`和`<nulltype>`也作为基本类型

  * `RefType`表示引用类型(非基本类型)，它有几个子类：

    * `Class`表示Java类

    * `Interface`表示Java接口

    * `EnumType`表示Java枚举类型.

    * `Array`表示Java数组类型

例如，下面的语句查找所有的`int`类型的变量

    
    
    import java
    
    from Variable v, PrimitiveType pt
    where pt = v.getType() and
        pt.hasName("int")
    select v
    

此查询会得到很多结果，因为大多数项目都包含许多`int`类型的变量

引用类型也可以根据其声明范围进行分类：

  * `TopLevelType`表示在编译单元的顶层声明的引用类型。

  * `NestedType`是在另一个类型中声明的类型。

例如，此查询查找名称与其编译单元名称不同的所有顶级类型：

    
    
    import java
    
    from TopLevelType tl
    where tl.getName() != tl.getCompilationUnit().getName()
    select tl
    

更多的专业类也很有用：

  * `TopLevelClass`：表示在编译单元的顶层声明的类。

  * `NestedClass`：表示在另一个类型中声明的类，

该库还具有许多单例类，它们包装了常用的Java标准类库：`TypeObject`,`TypeCloneable`,`TypeRuntime`,`TypeSerializable`,`TypeString`,`TypeSystem`和`TypeClass`。很明显，`TypeObject`包装了`Object`类

例如，我们可以编写一个查询来查找所有直接继承自Object的嵌套类：

    
    
    import java
    
    from NestedClass nc
    where nc.getASupertype() instanceof TypeObject
    select nc
    

![image.png](https://image.3001.net/images/20221213/1670943667_639893b3736867e49ed8d.png!small)

**Variables**

·`Variables`类表示Java中的变量，分为3种情况，一是类的成员字段(无论是否静态)，二是局部变量，三是一个参数，因此`Variables`有三个子类来满足上面的三种情况。

  * `Field`代表一个java字段

  * `LocalVariableDecl`代表一个本地变量

  * `Parameter`代表方法或构造器的参数

## Abstract syntax tree(AST)

这个类别中的类主要是为了表示抽象语法树上(`AST`)的节点(`nodes`),较为重要的是语句类 (class`Stmt`) 和表达式类
(class`Expr`)，后面会详细介绍AST这个类别。

`Expr`和`Stmt`两个类都提供了大量的谓词来帮助我们对程序的抽象语法树进行研究:

  * `Expr.getAChildExpr`:返回给定表达式的子表达式

  * `Stmt.getAChild`：返回给定语句中嵌套的语句或表达式

  * `Expr.getParent`和`Stmt.getParent`返回给定AST节点的父节点

例如，下面的查询查找父语句为`return语句`的所有表达式

    
    
    import java
    
    from Expr e
    where e.getParent() instanceof ReturnStmt
    select e
    

![image.png](https://image.3001.net/images/20221213/1670943730_639893f2ab0b5551eaea6.png!small)

![image.png](https://image.3001.net/images/20221213/1670943795_6398943376740b83ce2d3.png!small)

在AST中`return`后边语句是其子节点，这样就能理解了，如果程序包含一个语句`return x + y`，查询将会返回子表达式`x + y`

再举一个例子，下面这个查询查找父语句为`if语句`的所有表达式。

    
    
    import java
    
    from Stmt s
    where s.getParent() instanceof IfStmt
    select s
    

![image.png](https://image.3001.net/images/20221213/1670943814_6398944695c922be0ec36.png!small)

这个和上边的例子还是有所不同的，这个查询将返回`if`和`else`分支下的所有语句

接下来介绍一个语句用于发现方法体：

    
    
    import java
    
    from Stmt s
    where s.getParent() instanceof Method
    select s
    

![image.png](https://image.3001.net/images/20221213/1670944177_639895b125b52a178ac31.png!small)

当然上面只是较为简单的语句，我们需要结合自定义谓词以及类，来查询符合要求的表达式或语句，站在挖掘漏洞的角度，同时也需要我们需要很强的抽象能力，将已知的漏洞模式进行抽象形成查询，进而应用再实际的项目中。

上面的例子也说明了：表达式的父节点不总是表达式，也有可能是一个语句，同样的，语句的父节点不总是语句，也有可能是方法或构造函数，为了应对这一点，QL库提供了两个抽象类，`ExprParent`and`StmtParent`，前者表示可能是表达式父节点的任何节点，后者表示可能是语句父节点的任何节点。

## Metadata(元数据)

除了程序代码，Java中还有许多种元数据，特别是注释和Javadoc，Java底层的类其中存在大量的注释，CodeQL官方认为元数据，无论是帮助代码分析还是作为一个独立的分析主题，都是很有趣的，所以QL库定义了访问元数据的类

对于注释，`Annotatable`类是所有可以被注释的程序元素的超类(superclass)，子类对应Java程序中的元素，包括packages，reference
types， fields，methods，constructors和

本地变量声明，对应上述每个元素对应的类的`getAnAnnotation`，可以访问此元素的任何可能存在的注释，例如，下面的查询，查找构造器的所有注释：

    
    
    import java
    
    from Constructor c
    select c.getAnAnnotation()
    

![image.png](https://image.3001.net/images/20221213/1670944246_639895f663266a2ebf0a8.png!small)

这样会查询结果包含许多例子，这些注释是被用来禁止显示警告或标记代码被弃用。

注释是被`Annotation`类表示的，一个`annotation`是一个简单的表达式，其类型是`AnnotationType`例如我们可以修改此查询，使其仅报告已弃用的构造函数：

    
    
    import java
    
    from Constructor c, Annotation ann, AnnotationType anntp
    where ann = c.getAnAnnotation() and
        anntp = ann.getType() and
        anntp.hasQualifiedName("java.lang", "Deprecated")
    select ann
    

只有被`@Deprecated`标注的构造器被查询出来。

> Javadoc 是 Sun 公司提供的一种工具，它可以从程序源代码中抽取类、方法、成员等注释，然后形成一个和源代码配套的 API
> 帮助文档。也就是说，只要在编写程序时以一套特定的标签注释，在程序编写完成后，通过 Javadoc 就形成了程序的 API 帮助文档。

对于`javadoc`，`Element`类使用成员谓词`getDoc`来返回一个代理的`Documentable`对象，

接下来，我们可以查询此委托对象来获取`Javadoc`下面这个查询获取私有字段上的Javadoc注释：

    
    
    import java
    
    from Field f, Javadoc jdoc
    where f.isPrivate() and
        jdoc = f.getDoc().getJavadoc()
    select jdoc
    

![image.png](https://image.3001.net/images/20221213/1670944266_6398960a1e7cf74b774f4.png!small)

`Javadoc`类使用`JavadocElement`节点树来表示完整的javadoc文档，我们可以通过成员谓词``getAChild`and
`getParent`来对节点树进行遍历。例如，可以使用以下查询来查找私有字段的所有带有`@author`标签的Javadoc注释。

    
    
    import java
    
    from Field f, Javadoc jdoc, AuthorTag at
    where f.isPrivate() and
        jdoc = f.getDoc().getJavadoc() and
        at.getParent+() = jdoc
    select at
    

第5行可能比较难理解:使用了递归来查找嵌套在Javadoc注释中的任意深度的标签

## Call graph

Java代码库生成的CodeQL数据库包括关于`程序调用图`的一些预处理信息。

> Call
> graph是整个程序中方法（函数）之间调用关系的图，图中的节点是方法，边表示调用关系。例如方法foo()调用了方法bar()，则CG中应有一条从foo()到bar()的有向边，

CodeQL对应的类为`Callable`包括了`CG`中的方法或构造器，调用表达式可以抽象为`Call`类，此类包括方法调用，new表达式，或使用this或super显式的构造函数。

我们可以使用谓词`Call.getCallee`来查找特定调用特定方法或构造函数的表达式，例如，下面这个查询查找所有调用`println`方法的所有方法。

    
    
    import java
    
    from Call c, Method m
    where m = c.getCallee() and
        m.hasName("println")
    select c
    

相反的，谓词`Callable.getAReference`可以用来查找从未调用过指定方法或构造器的语句：

    
    
    import java
    
    from Callable c
    where not exists(c.getAReference())
    select c
    

# 小结

这部分只是简单的了解了一下Java QL库的一些较为重要的基础知识点。下一篇会介绍一些实际安全场景中的运用。

