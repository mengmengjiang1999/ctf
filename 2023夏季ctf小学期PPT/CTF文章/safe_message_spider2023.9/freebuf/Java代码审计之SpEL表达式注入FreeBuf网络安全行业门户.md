***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：Lateink，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

##  SpEL 表达式注入

 **Spring Expression Language（简称 SpEL）是一种功能强大的表达式语言、用于在运行时查询和操作对象图；语法上类似于
Unified EL，但提供了更多的特性，特别是方法调用和基本字符串模板函数。SpEL 的诞生是为了给 Spring 社区提供一种能够与 Spring
生态系统所有产品无缝对接，能提供一站式支持的表达式语言。**

##  **SpEL 表达式**

### 基本表达式

字面量表达式、关系，逻辑与算数运算表达式、字符串链接及截取表达式、三目运算、正则表达式以及括号优先级表达式；

### 类相关表达式

类类型表达式、类实例化、instanceof 表达式、变量定义及引用、赋值表达式、自定义函数、对象属性存取及安全导航表达式、对象方法调用、Bean 引用；

### 集合相关表达式

内联 List、内联数组、集合、字典访问、列表、字典；

### 其他表达式

模版表达式

##  **SpEL 基础**

在 pom.xml 导入 maven
或是把"org.springframework.expression-3.0.5.RELEASE.jar"添加到类路径中

    
    
    <properties>
        <org.springframework.version>5.0.8.RELEASE</org.springframework.version>
    </properties>
    <dependency>
          <groupId>org.springframework</groupId>
          <artifactId>spring-expression</artifactId>
          <version>${org.springframework.version}</version>
    </dependency>

SpEL 使用方式

SpEL 在求表达式值时一般分为四步，其中第三步可选：首先构造一个解析器，其次解析器解析字符串表达式，在此构造上下文，最后根据上下文得到表达式运算后的值。

    
    
     ExpressionParser parser = new SpelExpressionParser();
     Expression expression = parser.parseExpression("('Hello' + ' freebuf').concat(#end)");
     EvaluationContext context = new StandardEvaluationContext();
     context.setVariable("end", "!");
     System.out.println(expression.getValue(context));  
    

1.创建解析器： **SpEL 使用 ExpressionParser 接口表示解析器，提供 SpelExpressionParser 默认实现；**

2.解析表达式：使用 ExpressionParser 的 parseExpression 来解析相应的表达式为 Expression 对象。

3.构造上下文：准备比如变量定义等等表达式需要的上下文数据。

4.求值：通过 Expression 接口的 getValue 方法根据上下文获得表达式值。

SpEL 主要接口

1. **ExpressionParser 接口** ：表示解析器，默认实现是 org.springframework.expression.spel.standard 包中的 SpelExpressionParser 类，使用 parseExpression 方法将字符串表达式转换为 Expression 对象，对于 ParserContext 接口用于定义字符串表达式是不是模板，及模板开始与结束字符；
    
    
    public interface ExpressionParser {  
        Expression parseExpression(String expressionString);  
        Expression parseExpression(String expressionString, ParserContext context);  
    }

事例 demo

    
    
    ExpressionParser parser = new SpelExpressionParser();
    ParserContext parserContext = new ParserContext() {
        @Override
        public boolean isTemplate() {
        return true;
        }
        @Override
        public String getExpressionPrefix() {
        return "#{";
        }
        @Override
        public String getExpressionSuffix() {
        return "}";
        }
    };
    String template = "#{'hello '}#{'freebuf!'}";
    Expression expression = parser.parseExpression(template, parserContext);
    System.out.println(expression.getValue());

演示的是使用 ParserContext 的情况，此处定义了 ParserContext 实现：定义表达式是模块，表达式前缀为「#{」，后缀为「}」；使用
parseExpression 解析时传入的模板必须以「#{」开头，以「}」结尾。

默认传入的字符串表达式不是模板形式，如之前演示的 Hello World。

 **EvaluationContext 接口** ：表示上下文环境，默认实现是
org.springframework.expression.spel.support 包中的 StandardEvaluationContext 类，使用
setRootObject 方法来设置根对象，使用 setVariable 方法来注册自定义变量，使用 registerFunction
来注册自定义函数等等。

 **Expression 接口** ：表示表达式对象，默认实现是 org.springframework.expression.spel.standard
包中的 SpelExpression，提供 getValue 方法用于获取表达式值，提供 setValue 方法用于设置对象值。

SpEL 语法 - 类相关表达式

类类型表达式： **使用"T(Type)"来表示 java.lang.Class
实例，"Type"必须是类全限定名，"java.lang"包除外，即该包下的类可以不指定包名；使用类类型表达式还可以进行访问类静态方法及类静态字段。**

具体使用方法

    
    
    ExpressionParser parser = new SpelExpressionParser();
            // java.lang 包类访问
    Class<String> result1 = parser.parseExpression("T(String)").getValue(Class.class);
    System.out.println(result1);
            //其他包类访问
    String expression2 = "T(java.lang.Runtime).getRuntime().exec('open /Applications/Calculator.app')";
    Class<Object> result2 = parser.parseExpression(expression2).getValue(Class.class);
    System.out.println(result2);
            //类静态字段访问
    int result3 = parser.parseExpression("T(Integer).MAX_VALUE").getValue(int.class);
    System.out.println(result3);
            //类静态方法调用
    int result4 = parser.parseExpression("T(Integer).parseInt('1')").getValue(int.class);
    System.out.println(result4);

> 类实例化：类实例化同样使用 java 关键字「new」，类名必须是全限定名，但 java.lang 包内的类型除外，如 String、Integer。
>
> instanceof 表达式：SpEL 支持 instanceof 运算符，跟 Java 内使用同义；如"'haha' instanceof
> T(String)"将返回 true。
>
> 变量定义以及引用：变量定义通过 EvaluationContext 接口的 setVariable(variableName, value)
> 方法定义；在表达式中使用"#variableName"引用；除了引用自定义变量，SpE
> 还允许引用根对象及当前上下文对象，使用"#root"引用根对象，使用"#this"引用当前上下文对象；
>
> 自定义函数：目前只支持类静态方法注册为自定义函数；SpEL 使用 StandardEvaluationContext 的
> registerFunction 方法进行注册自定义函数，其实完全可以使用 setVariable 代替，两者其实本质是一样的

##  审计过程

这里拿 Spring Message 远程命令执行漏洞来作为例子

环境搭建

    
    
    git clone https://github.com/spring-guides/gs-messaging-stomp-websocket
    git checkout 6958af0b02bf05282673826b73cd7a85e84c12d3

拿到项目代码，全局搜索一下 org.springframework.expression.spel.standard，发现
DefaultSubscriptionRegistry.java 文件处有导入。

![](https://image.3001.net/images/20190228/1551353029_5c77c4c5d8b3a.png!small)

再搜索一下 SpelExpressionParser

![](https://image.3001.net/images/20190228/1551353054_5c77c4de87b82.png!small)

往下跟进发现如下关键代码，具体分析看代码注释

    
    
    @Override
    protected void addSubscriptionInternal(
    String sessionId, String subsId, String destination, Message<?> message) {
    Expression expression = null;
    MessageHeaders headers = message.getHeaders();
            // 这里可以看出 SpEL 表达式 expression 是从 headers 中的 selector 字段中取出来
    String selector = SimpMessageHeaderAccessor.getFirstNativeHeader(getSelectorHeaderName(), headers);
    if (selector != null) {
    try {
                    //生成 expression 对象
    expression = this.expressionParser.parseExpression(selector);
    this.selectorHeaderInUse = true;
    if (logger.isTraceEnabled()) {
    logger.trace("Subscription selector: [" + selector + "]");
    }
    }
    catch (Throwable ex) {
    if (logger.isDebugEnabled()) {
    logger.debug("Failed to parse selector: " + selector, ex);
    }
    }
    }
            // expression 传入 addSubscription 这个函数里面，即存放在 this.subscriptionRegistry
    this.subscriptionRegistry.addSubscription(sessionId, subsId, destination, expression);
    this.destinationCache.updateAfterNewSubscription(destination, sessionId, subsId);
    }

再搜索一下 this.subscriptionRegistry，看看有没有调用传进去的 expression。

然后发现了！

![](https://image.3001.net/images/20190228/1551353085_5c77c4fd95c2f.png!small)

在这里调用了 this.subscriptionRegistry.getSubscriptions(sessionId) 并从中取出 info->sub->
expression。

最关键的是，这里直接调用了 expression.getValue()！这说明如果能控制 SpEL 的表达式，就能直接命令执行！

再来看看这个 filterSubscriptions 函数在哪里调用。从函数的调用回溯追踪调用链如下：

    
    
     filterSubscriptions -> findSubscriptionsInternal -> findSubscriptions -> sendMessageToSubscribers

sendMessageToSubscribers 即发送消息的功能

回顾一下整个流程，SpEL 表达式从 headers 中 selector 获取，即发送请求时添加 selector 到请求的 header
即可传入，然后生成 expression 对象传入 this.subscriptionRegistry，然后当发送消息的时候，最终会直接从
this.subscriptionRegistry 取出并调用 expression.getValue() 执行我们传入的 SpEL 表达式。

验证过程，在 expression.getValue() 这里打个断点，看看发送消息是否会拦截并查看调用链是否如上述分析一样。

![](https://image.3001.net/images/20190228/1551353103_5c77c50fae53d.png!small)

Bingo！

简单总结一下 SpEL 表达式注入的分析思路，可以先全局搜索 org.springframework.expression.spel.standard,
或是
expression.getValue()、expression.setValue()，定位到具体漏洞代码，再分析传入的参数能不能利用，最后再追踪参数来源，看看是否可控。Spring
Data Commons Remote Code Execution 的 SpEL 注入导致的代码执行同样可以用类似的思路分析。

##  漏洞修复

SimpleEvaluationContext、StandardEvaluationContext 是 SpEL 提供的两个
EvaluationContext

> SimpleEvaluationContext - 针对不需要 SpEL 语言语法的全部范围并且应该受到有意限制的表达式类别，公开 Spal
> 语言特性和配置选项的子集。
>
> StandardEvaluationContext - 公开全套 SpEL
> 语言功能和配置选项。您可以使用它来指定默认的根对象并配置每个可用的评估相关策略。

SimpleEvaluationContext 旨在仅支持 SpEL 语言语法的一个子集。它不包括 Java 类型引用，构造函数和 bean
引用；所以最直接的修复方式是使用 SimpleEvaluationContext 替换 StandardEvaluationContext。

这是我个人学习代码审计过程中的小总结，可能逻辑性相对来说没那么严谨，但是个人觉得这是一个比较通俗易懂的分析方法，不喜勿喷。

###  参考文章：

> [spring-messaging Remote Code Execution 分析](https://xz.aliyun.com/t/2252)
>
> [SpEL 表达式注入](http://rui0.cn/archives/1043)

 ***本文原创作者：Lateink，本文属FreeBuf原创奖励计划，未经许可禁止转载**

