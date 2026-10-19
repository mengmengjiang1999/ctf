# 一、前言

前段时间Apache报告了CVE-2023-22602，由于 1.11.0 及之前版本的 Shiro 只兼容 Spring 的ant-style路径匹配模式（pattern matching），且 2.6 及之后版本的 Spring Boot 将 Spring MVC
处理请求的路径匹配模式从AntPathMatcher更改为了PathPatternParser，当 1.11.0 及之前版本的 Apache Shiro 和
2.6 及之后版本的 Spring Boot 使用不同的路径匹配模式时，攻击者访问可绕过 Shiro 的身份验证。

在Java生态中，还有一个常用的鉴权组件SpringSecurity，其中AntPathRequestMatcher是SpringSecurity中基于Ant风格模式进行匹配的实现类，那么是否也会有类似的问题。查看源码进行简单的分析:

![wKg0C2Qq5WqAPPYfAAAktHbm7U683.png](https://image.3001.net/images/20230630/1688104546_649e6e6216b960398c68b.png!small)

# 二、相关原理

按照前面的猜想，SpringSecurity某种条件下使用的是AntPathMatcher进行匹配，而高版本的Spring使用的是PathPatternParser，利用解析的差异在某些条件下可能会存在绕过鉴权的风险。

AntPathRequestMatcher是SpringSecurity中基于Ant风格模式进行匹配的实现类。一般使用如下：

    
    
    protected void configure(HttpSecurity httpSecurity) throws Exception{
         httpSecurity.authorizeRequests().antMatchers("/admin/*").authenticated();
    }
    

查看AntPathRequestMatcher以及PathPattern的具体实现：

## 2.1 AntPathRequestMatcher

主要的匹配在org.springframework.security.web.util.matcher.AntPathRequestMatcher#matches方法中进行。

首先判断请求方法是否一致，然后如果pattern是`/**`的话，说明是全路径匹配返回true。否则获取当前请求的url，然后调用当前matcher的matches方法进行进一步的匹配：

![wKg0C2Qq6FSALtkRAAA8yrdNIt8959.png](https://image.3001.net/images/20230630/1688104546_649e6e627fabe2f671cd9.png!small)

首先是当前请求url的获取方法，如果没有配置urlPathHelper的话，则通过请求的ServletPath和PathInfo进行拼接，获取归一化处理后的url，否则调用Spring中的
**UrlPathHelper**
(封装了有很多与URL路径处理有关的方法)的getPathWithinApplication方法（进行了URI解码、移除分号内容并清理斜线等进一步的处理）进行获取：

![wKg0C2Qq6IOAQjNtAACDvlWTI0A203.png](https://image.3001.net/images/20230630/1688104547_649e6e63d0d429a9e2bfd.png!small)

获取完url后，会调用当前matcher#matches方法进行匹配，从AntPathRequestMatcher的构造器可以看出，这里涉及到两个matcher(SubpathMatcher&SpringAntMatcher)：

![wKg0C2Qq6KKANX7tAABpoU5eJSc630.png](https://image.3001.net/images/20230630/1688104548_649e6e646739b1bdf92ad.png!small)

如果 pattern 的值以 `/**`结尾并且不包含路径变量(即通配符{})，会使用SubpathMatcher,否则 matcher 赋值为
SpringAntMatcher 类的对象。

  *  **SubpathMatcher**

例如Pattern为`/admin/**`，此时会使用SubpathMacher#matches进行解析。具体实现如下：

subpath从前面构造方法的调用可以知道主要是通过切割Pattern得到的(pattern.substring(0, pattern.length() -3)),例如/admin/**切割后的subPath就是/admin。

首先是统一转换成小写，然后如果请求的path以subpath开头，并且path的长度等于subpath的长度或者subpath长度后第一个字符是`/`则返回ture（满足/admin或者/admin/目录的访问方式）：

![wKg0C2Qq6VWATBb6AACAqb2M2iY905.png](https://image.3001.net/images/20230630/1688104548_649e6e64dceadd9f53209.png!small)

  *  **SpringAntMatcher**

例如Pattern为/admin/*，此时会使用SpringAntMatcher#matches进行解析。具体实现如下：

从构造方法可以看出实际上是调用的org.springframework.util.AntPathMatcher#match进行匹配：

![wKg0C2Qq6YiAAQwsAAC3W7sS6pQ861.png](https://image.3001.net/images/20230630/1688104549_649e6e6566ee2a380d954.png!small)

核心方法是org.springframework.util.AntPathMatcher#doMatch,首先会调用tokenizePattern()方法将pattern分割成String数组，如果是全路径并且区分大小写,那么就通过简单的字符串检查，看看path是否有潜在匹配的可能，没有的话返回false:

![wKg0C2Qq6baAEXQVAABGA3Y0BU579.png](https://image.3001.net/images/20230630/1688104549_649e6e65e723a62c68493.png!small)

然后调用tokenizePath()方法将需要匹配的path分割成string数组,主要是通过java.util
里面的StringTokenizer来处理字符串：

![wKg0C2Qq6eyAKj2mAAAmBYlIjk074.png](https://image.3001.net/images/20230630/1688104550_649e6e666f84672662917.png!small)

接着将pathDirs和pattDirs两个数组从左到右开始匹配，这里涉及一些正则的转换还有通配符的匹配。以`/admin/*`为例，首先会调用getStringMatcher方法：

![wKg0C2Qq6hiAdyVZAAAvjzAepDw002.png](https://image.3001.net/images/20230630/1688104550_649e6e66d3f2a79f81abd.png!small)

这里会调用AntPathStringMatcher的构造方法，实际上就是对Patten里的字符进行正则转换：

![wKg0C2Qq6kCAQh9gAACp7VsCdQs761.png](https://image.3001.net/images/20230630/1688104551_649e6e674b3dc273d78f8.png!small)

这里`*`最后会变成`.*`：

![wKg0C2Qq6oSAGu9qAAD78WTPEu4518.png](https://image.3001.net/images/20230630/1688104551_649e6e67bf5bf465e02ab.png!small)

最后封装java.util.regex.Pattern对象返回：

![wKg0C2Qq6qWATvkAAAmMnfty0085.png](https://image.3001.net/images/20230630/1688104552_649e6e6853c7c100a0b9b.png!small)

最后调用matchStrings方法调用java.util.regex.compile#matcher进行匹配:

![wKg0C2Qq6syADxYyAACPgj9akv8356.png](https://image.3001.net/images/20230630/1688104552_649e6e68b4b6ddfcd36a2.png!small)

## 2.2 PathPattern

Spring
Framework的逻辑中，org.springframework.web.servlet.handler.AbstractHandlerMapping#initLookupPath方法中会初始化请求映射的路径,因为高版本默认使用的是PathPattern进行解析，所以会执行this.usesPathPatterns()为true时的逻辑：

![wKg0C2Qq6waATeynAAB0bIcpQcY600.png](https://image.3001.net/images/20230630/1688104553_649e6e693bc45f83ab41b.png!small)

以spring-webmvc-5.3.22为例，查看具体的解析过程：

首先从request域中获取PATH_ATTRIBUTE属性的内容，然后使用defaultInstance对象进行处理：

![wKg0C2Qq6yeAYv7lAABBYWOgtwo083.png](https://image.3001.net/images/20230630/1688104553_649e6e69b06efa74a0aff.png!small)

这里会根据removeSemicolonContent的值（默认为true）确定是移除请求URI中的所有分号内容还是只移除jsessionid部分：

![wKg0C2Qq60KADIw7AAAs6DW1g8c468.png](https://image.3001.net/images/20230630/1688104554_649e6e6a71a0e1917fc97.png!small)

这里逻辑会比较简单， **缺少一些归一化的处理，例如并不会将`//`处理成`/`，也没有处理路径穿越**。

通过initLookupPath获取到路径后，会调用lookupHandlerMethod方法，根据请求的uri来找到对应的Controller和method。

直接查看PathPattern的核心实现，主要在org.springframework.web.util.pattern.PathPattern#matches方法：

![wKg0C2Qq63GAM0ASAABgFy03B6I049.png](https://image.3001.net/images/20230630/1688104554_649e6e6ad2b2915e6599e.png!small)

这里根据/将URL拆分成多个PathElement对象，然后根据PathPattern的链式节点中对应的PathElement的matches方法逐个进行匹配。举个例子：  
例如Pattern的第一个元素为/的话，会调用SeparatorPathElement的matches方法进行处理,结束后pathIndex++，继续遍历下一个元素进行处理：

![wKg0C2Qq66qAHrYkAABnzXqVqN8579.png](https://image.3001.net/images/20230630/1688104555_649e6e6b4ab2a7b65602c.png!small)

除此之外，根据不同Pattern的写法，还有很多PathElement：

  * WildcardPathElement（/api/*）
  * SingleCharWildcardedPathElement（/api/?）
  * WildcardTheRestPathElement（/api/**）
  * CaptureVariablePathElement（/api/{param}）
  * CaptureTheRestPathElement（/api/{*param}）
  * LiteralPathElement（/api/index）
  * RegexPathElement（/api/.*）

# 三、绕过场景

根据前面的分析，利用解析的差异在某些条件下可能会存在绕过鉴权的风险。

## 3.1 java.util.regex.Pattern模式差异

对于默认的Pattern模式，不开启DOTALL时候，在默认匹配的时候不会匹配\r \n 字符。

![wKg0C2Qq7UCAccbgAAA3VH9mi4219.png](https://image.3001.net/images/20230630/1688104555_649e6e6bc6f13c991d930.png!small)

根据前面的分析，AntPathRequestMatcher解析时，会调用AntPathStringMatcher的构造方法对Patten里的字符进行正则转换并封装成java.util.regex.Pattern对象返回，然后跟请求的Path进行匹配。不同版本间是存在差异的。

  * spring-core-5.3.21

![wKg0C2Qq7ZCAMjBrAABK6lgyqrU118.png](https://image.3001.net/images/20230630/1688104556_649e6e6c3a1db10e0e94a.png!small)

  * spring-core-5.3.22

![wKg0C2Qq7aSAUV2qAABOOCjhJvw176.png](https://image.3001.net/images/20230630/1688104556_649e6e6ca2280b2adf907.png!small)

可以看到，在5.3.22版本之前，Pattern并没有配置dotall模式，从5.3.22版本开始，配置了dotall模式，此时的表达式`.`匹配任何字符，包括行结束符。

结合前面的分析，结合实际场景进行Auth Bypass尝试。

假设SpringSecurity配置如下：

    
    
    protected void configure(HttpSecurity httpSecurity) throws Exception{
       httpSecurity.authorizeRequests().antMatchers("/admin/*").authenticated();
    }
    

访问的Controller如下：

    
    
    @GetMapping("/admin/*")
    public String Manage(){
        return "manage";
    }
    

正常情况下/admin/page接口应该是需要认证以后才可以访问的：

![wKg0C2Qq7gSAJs3yAABdV0wkgs106.png](https://image.3001.net/images/20230630/1688104557_649e6e6d218f38c34ad07.png!small)

当使用高版本的Spring时，在进行路由解析时使用的是PathPatternParser。且当这个版本低于5.3.22时，AntPathRequestMatcher是无法匹配行结束符的。

以5.3.21版本的Spring为例，使用\r或者\n（\r的URl编码为%0d,\n的URL编码为%0a）即可绕过当前的鉴权规则：

![wKg0C2Qq7lqAGVz5AABvAWCEiHI518.png](https://image.3001.net/images/20230630/1688104557_649e6e6dd1155e00b4ea2.png!small)

因为没有启用dotall模式，SpringSecurity匹配`/admin/page%0a`会失败，然后转由Spring的PathPattern进行解析，首先是admin字符匹配，当解析到`*`时会使用WildcardPathElement进行解析,若没有下一个Element元素的话，只要pathElements的元素个数和PathPattern中的元素个数一致都会返回true，也就是说page%0a跟`*`是可以成功匹配的：

![wKg0C2Qq7pmARJk1AACZADMYq84455.png](https://image.3001.net/images/20230630/1688104558_649e6e6e43a1313744945.png!small)

利用上述的差异即可达到auth Bypass的效果，当使用spring-core-5.3.22时，因为AntPathRequestMatcher在匹配时启用了dotall模式，此时的表达式`.`匹配任何字符，包括行结束符，无法auth
Bypass：

![wKg0C2Qq7r2AH2zPAABgx2MZfNo408.png](https://image.3001.net/images/20230630/1688104558_649e6e6eb06f7e8c86f1f.png!small)

同样是上面的SpringSecurity配置，当请求的Controllerr如下，也存在Auth Bypass的问题：

    
    
    @GetMapping("/admin/{param}")
    public String Manage(){
        /*return "Manage page";*/
        return "manage";
    }
    

当处理`{param}`时，PathPattern会使用CaptureVariablePathElement进行处理，因为通配符{}中没有正则，所以这里只需要pathElements的元素个数和PathPattern中的元素个数一致都会返回true:

![wKg0C2Qq7uiAWJA1AACkvxZWVU370.png](https://image.3001.net/images/20230630/1688104559_649e6e6f271b4cf3d848f.png!small)

![wKg0C2Qq7vaAGrr0AAByIBcRupY181.png](https://image.3001.net/images/20230630/1688104559_649e6e6fb4c8ca2d6221e.png!small)

PS：

  * 低版本的Spring使用的是AntPathMatcher，即使绕过了SpringSecurity也会因为解析差异找不到对应的Controller返回404。
  * SpringSecurity高版本的StrictHttpFirewall对\r或者\n（\r的URl编码为%0d，\n的URL编码为%0a）进行了拦截处理：

![wKg0C2Qq7xCAFxIwAAAlxg0fI8U848.png](https://image.3001.net/images/20230630/1688104560_649e6e703a2328039d069.png!small)

## 3.2 请求Path归一化差异

根据前面的分析，对于SpringSecurity来说，在获取当前请求url时会对请求的url进行一定的处理，例如`/admin/..`最终会处理为`/`：

![wKg0C2Qq71qARY0KAACDvlWTI0A938.png](https://image.3001.net/images/20230630/1688104560_649e6e70a758ea32746b6.png!small)

而在Spring
Framework的逻辑中，因为高版本默认使用的是PathPattern进行解析，所以会执行this.usesPathPatterns()为true时的逻辑，根据之前的分析，这里会根据主要是对请求URI中的所有分号内容进行处理，判断是移除全部部分还是只移除jsessionid部分，并没有处理编码，路径穿越符等内容：

![wKg0C2Qq73mAdciAAB0bIcpQcY117.png](https://image.3001.net/images/20230630/1688104561_649e6e7121a82d44d1a1e.png!small)

同样是前面的场景：

假设SpringSecurity配置如下：

    
    
    @Override
    protected void configure(HttpSecurity httpSecurity) throws Exception{
       httpSecurity.authorizeRequests().antMatchers("/admin/*").authenticated();
    }
    

访问的Controller如下：

    
    
    @GetMapping("/admin/*")
    public String Manage(){
        return "manage";
    }
    

当尝试访问`/admin/..`时，AntPathRequestMatcher在处理时会认为当前请求的path是`/`，在进行匹配的时候因为请求的path为`/`,在isPotentialMatch方法处理时会认为没有潜在匹配的可能返回false:

![wKg0C2Qq76mALNTkAABtq7YZC58270.png](https://image.3001.net/images/20230630/1688104561_649e6e7197e02d0a794bf.png!small)

但是对于PathPattern而言，WildcardPathElement解析时若没有下一个Element元素的话，只要pathElements的元素个数和PathPattern中的元素个数一致都会返回true，也就是说`..`跟`*`是可以成功匹配的。

![wKg0C2Qq8GOABBVCAAB7UqgejDs250.png](https://image.3001.net/images/20230630/1688104562_649e6e720bbd4eb91b9ac.png!small)

同样的，如下的场景也会有绕过的风险：

假设SpringSecurity配置如下：

    
    
    @Override
    protected void configure(HttpSecurity httpSecurity) throws Exception{
       httpSecurity.authorizeRequests().antMatchers("/admin/**").authenticated();
    }
    

访问的Controller如下：

    
    
    @GetMapping("/admin/**")
    public String Manage(){
        return "manage";
    }
    

如果 pattern 的值以
`/**`结尾并且不包含路径变量(即通配符{})，会使用SubpathMatcher。匹配逻辑也比较简单，若请求的path以subpath开头，并且path的长度等于subpath的长度或者subpath长度后第一个字符是`/`则返回ture（满足/admin或者/admin/目录的访问方式）。这里`/`跟`/admin`以及`/admin/`明显是不匹配的。

但是PathPattern在解析/admin/**时候，在解析/**时会调用WildcardTheRestPathElement进行处理，因为PathPattern通配符只能定义在尾部(不能以/结尾)，所以pathElements的元素个数大于PathPattern中的元素个数即可匹配，所以`..`是可以匹配上`/**`的，同样的由于SpringSecurity不能解析但是Spring
Framework的PathPattern可以解析导致了Auth Bypass问题。

PS:SpringSecurity高版本的StrictHttpFirewall对路径穿越符进行了拦截处理：

![wKg0C2Qq8COAMmOdAAAyYhI921A395.png](https://image.3001.net/images/20230630/1688104562_649e6e72795d9378b1821.png!small)

# 四、其他

实际上Spring官方很早就意识到解析差异带来的风险了。SpringSecurity还有一种匹配模式MvcRequestMatcher。

参考[https://docs.spring.io/spring-security/reference/servlet/integrations/mvc.html#mvc-requestmatcher](https://www.sec-in.com/outLinkPage/?target=https://docs.spring.io/spring-security/reference/servlet/integrations/mvc.html#mvc-requestmatcher)

其使用Spring
MVC的HandlerMappingIntrospector来匹配路径并提取变量。相比AntPathRequestMatcher会更严谨。在一定程度解决了差异的问题。避免了前面AntPathRequestMatcher的绕过一些问题。

同样是前面的例子，使用MvcRequestMatcher 后无法绕过鉴权逻辑：

![wKg0C2Qq8OWATF8MAABv94Ueoo982.png](https://image.3001.net/images/20230630/1688104562_649e6e72dfaa9a3221a64.png!small)

![wKg0C2Qq8NKAAuIAACAekbSgcU313.png](https://image.3001.net/images/20230630/1688104563_649e6e7371f3e82820103.png!small)

  

