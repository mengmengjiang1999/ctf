# Shiro权限绕过漏洞分析

阅读量 **139780**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-13 16:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01ad3398286611c591.jpg)

## 前言

前段时间遇到通过分号绕过nginx层屏蔽并顺利访问到Springboot项目actuator端点的问题，修复过程中偶然发现当项目使用shiro组件时，若将shiro升级到1.6.0可间接修复分号绕过的问题，当请求url中包含分号时响应状态码为400；

考虑到shiro主要用来执行身份验证授权等，理论上不适合直接阻断存在分号的请求；

为搞明白此问题，决定对shiro的权限校验问题进行整理学习，下面为常见的shiro权限绕过漏洞分析修复过程。

## Shiro Filter

学习shiro权限绕过漏洞之前，有必要了解下shiro filter的过滤过程；

一个http请求过来，首先经过web容器的处理（这里默认为tomcat）被投放到相应的web应用，web应用会通过过滤器Filter链式的对http请求进行预处理，这里将会经过shiro的Filter（SpringShiroFilter）处理：

    
    
    org.apache.catalina.core.ApplicationFilterChain#internalDoFilter --> org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter        -->    
    org.apache.shiro.web.servlet.AbstractShiroFilter#doFilterInternal  -->
    org.apache.shiro.web.servlet.AbstractShiroFilter#executeChain
    

![](https://p3.ssl.qhimg.com/t01a86e77715c725d1e.png)

![](https://p5.ssl.qhimg.com/t0163372e685cc998f7.png)

![](https://p4.ssl.qhimg.com/t018475eec4d165c26d.png)

shiro的Filter执行过会通过getExecutionChain()获取执行链并执行对应的doFilter函数：

![](https://p2.ssl.qhimg.com/t01da9b265277441f81.png)

重点在获取chain的org.apache.shiro.web.servlet.AbstractShiroFilter#getExecutionChain中；

首先会尝试获取到在springboot启动时加载的shiro配置文件中配置的Shiro
filterChains（resolver）并判断是否为null，当为null则返回原始过滤器链origChain，当不为空时则尝试通过org.apache.shiro.web.filter.mgt.FilterChainResolver#getChain方法根据当前请求的url使用Ant模式获取相应的拦截器链
FilterChain代理（resolved），否则返回原始过滤器链origChain：

    
    
        protected FilterChain getExecutionChain(ServletRequest request, ServletResponse response, FilterChain origChain) {
            FilterChain chain = origChain;
    
            FilterChainResolver resolver = getFilterChainResolver();
            if (resolver == null) {
                log.debug("No FilterChainResolver configured.  Returning original FilterChain.");
                return origChain;
            }
    
            FilterChain resolved = resolver.getChain(request, response, origChain);
            if (resolved != null) {
                log.trace("Resolved a configured FilterChain for the current request.");
                chain = resolved;
            } else {
                log.trace("No FilterChain configured for the current request.  Using the default.");
            }
    
            return chain;
        }
    

![](https://p3.ssl.qhimg.com/t014d05932af4191d27.png)

其中获取shiro对应的FilterChain代理是在org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain中完成，主要通过获取所有的filter链（filterChainManager）及requestURI，并循环遍历filterChainManager进行匹配，当匹配时则直接返回相对应的FilterChain代理，否则返回null：

![](https://p1.ssl.qhimg.com/t01957729c1acc8c936.png)

附上filterChainManager接口说明：

    
    
    public interface FilterChainManager {
        // 得到注册的拦截器
        Map<String, Filter> getFilters();
           // 获取拦截器链
        NamedFilterList getChain(String chainName);
        // 是否有拦截器链
        boolean hasChains();
        // 得到所有拦截器链的名字
        Set<String> getChainNames();
        // 使用指定的拦截器链代理原始拦截器链
        FilterChain proxy(FilterChain original, String chainName);
        // 注册拦截器
        void addFilter(String name, Filter filter);
        // 注册拦截器
        void addFilter(String name, Filter filter, boolean init);
        // 根据拦截器链定义创建拦截器链
        void createChain(String chainName, String chainDefinition);
        // 添加拦截器到指定的拦截器链
        void addToChain(String chainName, String filterName);
        // 添加拦截器（带有配置的）到指定的拦截器链
        void addToChain(String chainName, String filterName, String chainSpecificFilterConfig) throws ConfigurationException;
    }
    

最终链式执行过滤器：

    
    
    org.apache.catalina.core.ApplicationFilterChain#doFilter        -->        org.apache.catalina.core.ApplicationFilterChain#internalDoFilter
    

![](https://p5.ssl.qhimg.com/t01af4a394b10339adb.png)

执行完过滤器后将调用servlet.service，进而执行controller解析及service等：

![](https://p4.ssl.qhimg.com/t0138fc348520eb89eb.png)

javax.servlet.http.HttpServlet#service(javax.servlet.ServletRequest,
javax.servlet.ServletResponse)：

![](https://p5.ssl.qhimg.com/t01e92807cd6f8d7bcf.png)

接下来的SpringMVC controller解析部分详情可参见下面CVE-2020-1957漏洞分析部分。

## 漏洞环境

可参考：

<https://github.com/apache/shiro/releases>

或

<https://github.com/ttestoo/java-sec-study/tree/main/sec-shiro/java-shiro-bypass>

## shiro权限绕过 CVE-2020-1957

###  利用条件

Apache Shiro < 1.5.2

###  利用过程

1、正常情况下访问/hello/a会进行跳转：<http://127.0.0.1:9091/hello/a>

![](https://p5.ssl.qhimg.com/t01c6c646cb4419bec9.png)

2、可通过分号进行绕过：

<http://127.0.0.1:9091/;/hello/a>

<http://127.0.0.1:9091/aa/..;test=123/admin/index>

…

![](https://p0.ssl.qhimg.com/t015c80bf789f2f049a.png)

###  漏洞分析

shiro
filter主要过程上述部分已简单介绍，其中根据分号绕过可初步判断问题可能出现在获取requestURI处，毕竟是拿requestURI和shiro配置的FilterChain进行匹配的，也就是说通过分号使得shiro
filter过程的requestURI能绕过shiro的Ant格式的规则匹配；

可以直接在org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain中的String
requestURI = getPathWithinApplication(request); 处下断点进行调试：

![](https://p0.ssl.qhimg.com/t01f5ba5eb5cc8e70e6.png)

注意这里测试过程中URL为：<http://127.0.0.1:9091/aa/..;test=123/admin/index>

跟进getPathWithinApplication函数，将通过WebUtils.getPathWithinApplication —>
WebUtils.getRequestUri 获取requestURI：

![](https://p3.ssl.qhimg.com/t019a39b7e39fa34267.png)

![](https://p4.ssl.qhimg.com/t012ec185baaafe9b6d.png)

最终还是通过request.getRequestURI获取请求中的URI，即：/aa/..;test=123/admin/index

![](https://p1.ssl.qhimg.com/t01babcf3045ef59040.png)

获取到请求中的URI后，将通过org.apache.shiro.web.util.WebUtils#normalize进行标准化处理，其中参数调用了decodeAndCleanUriString函数处理，在decodeAndCleanUriString中可以清晰的看到根据
; 对uri进行了分割，并获取到 ; 之前的部分，即/aa/..

![](https://p5.ssl.qhimg.com/t01c28b4316fe13a94c.png)

且在normalize函数中，主要标准化处理内容如下：

  * \ —> /
  * // —> /
  * /./ —> /
  * /../ —> /

    
    
    private static String normalize(String path, boolean replaceBackSlash) {
    
            if (path == null)
                return null;
    
            // Create a place for the normalized path
            String normalized = path;
    
            if (replaceBackSlash && normalized.indexOf('\\') >= 0)
                normalized = normalized.replace('\\', '/');
    
            if (normalized.equals("/."))
                return "/";
    
            // Add a leading "/" if necessary
            if (!normalized.startsWith("/"))
                normalized = "/" + normalized;
    
            // Resolve occurrences of "//" in the normalized path
            while (true) {
                int index = normalized.indexOf("//");
                if (index < 0)
                    break;
                normalized = normalized.substring(0, index) +
                        normalized.substring(index + 1);
            }
    
            // Resolve occurrences of "/./" in the normalized path
            while (true) {
                int index = normalized.indexOf("/./");
                if (index < 0)
                    break;
                normalized = normalized.substring(0, index) +
                        normalized.substring(index + 2);
            }
    
            // Resolve occurrences of "/../" in the normalized path
            while (true) {
                int index = normalized.indexOf("/../");
                if (index < 0)
                    break;
                if (index == 0)
                    return (null);  // Trying to go outside our context
                int index2 = normalized.lastIndexOf('/', index - 1);
                normalized = normalized.substring(0, index2) +
                        normalized.substring(index + 3);
            }
    
            // Return the normalized path that we have completed
            return (normalized);
    
        }
    

由于此时传入的为经过decodeAndCleanUriString处理后的值（/aa/..），所以这里经过normalize处理后结果不变：

![](https://p0.ssl.qhimg.com/t014ec543f15695fc83.png)

也就是说此时通过WebUtils.getRequestUri获取到的requestUri的值为/aa/..

![](https://p0.ssl.qhimg.com/t01f57dadcb6bad3c34.png)

且getPathWithinApplication后的值也为/aa/..

![](https://p3.ssl.qhimg.com/t017a23ab3433b80676.png)

接下来将对requestURI和在shiro配置文件中配置的过滤规则filterChains进行匹配，则/aa/..不会和任何规则匹配成功，返回null：

![](https://p0.ssl.qhimg.com/t0195be0cfd13b825ef.png)

至此，我们通过在请求url中添加 ; 成功绕过了shiro的filter过滤匹配，并成功进入SpringMVC
controller解析过程，其中入口为SpringMVC的DispatcherServlet.doService()：

    
    
    org.apache.catalina.core.ApplicationFilterChain#internalDoFilter -->  javax.servlet.Servlet#service --> javax.servlet.http.HttpServlet#service --> javax.servlet.http.HttpServlet#doGet --> org.springframework.web.servlet.FrameworkServlet#processRequest --> 
    org.springframework.web.servlet.DispatcherServlet#doService  -->
    

![](https://p3.ssl.qhimg.com/t01162b3abcd6cbaa90.png)

![](https://p4.ssl.qhimg.com/t01686c98245c179041.png)

![](https://p2.ssl.qhimg.com/t01dbac55c979f4a5e2.png)

![](https://p0.ssl.qhimg.com/t01ef2abc8d633bb378.png)

![](https://p3.ssl.qhimg.com/t010862d62e0b2c7084.png)

在DispatcherServlet.doService中将调用核心的doDispatch方法进行下一步处理：

![](https://p2.ssl.qhimg.com/t016b79ef9171cc62f4.png)

其中doDispatch主要处理逻辑如下：

  1. checkMultipart 检查是不是文件上传请求，如果是，则对当前 request 重新进行包装，如果不是，则直接将参数返回；
  2. 根据当前请求，调用 getHandler 方法获取请求处理器，如果没找到对应的请求处理器，则调用 noHandlerFound 方法抛出异常或者给出 404；
  3. getHandlerAdapter 方法，根据当前的处理器找到处理器适配器；
  4. 然后处理 GET 和 HEAD 请求头的 Last_Modified 字段。当浏览器第一次发起 GET 或者 HEAD 请求时，请求的响应头中包含一个 Last-Modified 字段，这个字段表示该资源最后一次修改时间，以后浏览器再次发送 GET、HEAD 请求时，都会携带上该字段，服务端收到该字段之后，和资源的最后一次修改时间进行对比，如果资源还没有过期，则直接返回 304 告诉浏览器之前的资源还是可以继续用的，如果资源已经过期，则服务端会返回新的资源以及新的 Last-Modified；
  5. 接下来调用拦截器的 preHandle 方法，如果该方法返回 false，则直接 return 掉当前请求；
  6. 接下来执行 ha.handle 去调用真正的请求，获取到返回结果 mv；
  7. 接下来判断当前请求是否需要异步处理，如果需要，则直接 return 掉；如果不需要异步处理，则执行 applyDefaultViewName 方法，检查当前 mv 是否没有视图，如果没有（例如方法返回值为 void），则给一个默认的视图名；
  8. processDispatchResult 方法对执行结果进行处理，包括异常处理、渲染页面以及执行拦截器的 afterCompletion 方法都在这里完成；
  9. 最后在 finally 代码块中判断是否开启了异步处理，如果开启了，则调用相应的拦截器；如果请求是文件上传请求，则再调用 cleanupMultipart 方法清除文件上传过程产生的一些临时文件。

其中我们关心的是获取请求处理器的过程，即getHandler方法实现细节：

首先Spring会循环所有注册的HandlerMapping并返回第一个匹配的HandlerExecutionChain：

![](https://p5.ssl.qhimg.com/t018f28b554a5d1517c.png)

对于mapping为RequestMappingHandlerMapping时，则会调用org.springframework.web.servlet.handler.AbstractHandlerMapping#getHandler进行获取对应的handler，

在getHandler中调用getHandlerInternal方法，并在其中进行调用getLookupPathForRequest—>getPathWithinServletMapping解析请求路径lookupPath：

![](https://p1.ssl.qhimg.com/t01b1974d68b8c2c530.png)

对于getPathWithinServletMapping中首先通过getPathWithinApplication获取请求URI在web应用中的路径，其中经过如下调用链：

![](https://p2.ssl.qhimg.com/t018a578c3d352a9d3b.png)

最终在org.springframework.web.util.UrlPathHelper#getRequestUri中通过request.getRequestURI()获取请求的uri,即/aa/..;test=123/admin/index，并通过decodeAndCleanUriString方法对uri进行处理：

![](https://p3.ssl.qhimg.com/t01f10a0552f9d1f2e4.png)

![](https://p5.ssl.qhimg.com/t017c4698a16d7b2161.png)

decodeAndCleanUriString方法中主要做了三件事：

1、调用removeSemicolonContent方法对uri进行处理，其中将分号及后面的key-value进行了去除得到新的requestUri为/aa/../admin/index：

![](https://p4.ssl.qhimg.com/t014cbdc8a48fe73476.png)

2、通过调用decodeRequestString进行URL解码：

![](https://p0.ssl.qhimg.com/t015b7e6f98b8c524f1.png)

3、通过调用getSanitizedPath将//替换为/：

![](https://p0.ssl.qhimg.com/t016f1e590e43ebf4f4.png)

至此经过decodeAndCleanUriString方法处理后最终获取到的uri为/aa/../admin/index，即getPathWithinApplication返回的结果pathWithinApp的值也为/aa/../admin/index：

![](https://p2.ssl.qhimg.com/t010bd117ead6b6e7d5.png)

![](https://p3.ssl.qhimg.com/t01e5565b1ede5a3d09.png)

接下来回到getPathWithinServletMapping中，此时pathWithinApp值为/aa/../admin/index，servletPath为/admin/index，正常情况下将通过getRemainingPath方法将pathWithinApp中servletPath给截取掉，但此时由于两者值无法截取成功返回为null：

![](https://p1.ssl.qhimg.com/t0142a7c63258acae2a.png)

![](https://p1.ssl.qhimg.com/t01eaea8847111d2c82.png)

由于path为null，则进入else这种特殊情况，最终返回servletPath，即/admin/index：

![](https://p1.ssl.qhimg.com/t01e8aa983af4aa38fd.png)

即最终获取到的lookupPath值为/admin/index，并根据lookupPath的值寻找相对应的handlerMethod为com.ttestoo.bypass.controller.LoginController#admin_index()：

![](https://p1.ssl.qhimg.com/t01380444d1a6def1a2.png)

至此，SpringMVC中获取handler的过程已结束，成功获取到/admin/index相对应的handler方法，并将继续获取HandlerAdapter，并执行HandlerAdapter的handle方法利用反射机制执行/admin/index相对应的controller方法com.ttestoo.bypass.controller.LoginController#admin_index()：

![](https://p0.ssl.qhimg.com/t01a9db85d0f9d07a47.png)

**总结：**

当我们发起请求[http://127.0.0.1:9091/aa/..;test=123/admin/index时，经过shiro](http://127.0.0.1:9091/aa/..;test=123/admin/index%E6%97%B6%EF%BC%8C%E7%BB%8F%E8%BF%87shiro)
filter进行权限校验，此时shiro解析到的路径为/aa/..不会和任何规则匹配成功，从而通过了shiro的权限校验；

接下来会由springmvc进行controller解析，此时springmvc解析到的路径为/admin/index，并获取到/admin/index对应的handler方法admin_index，从而正常的执行service并得到最终的响应。

**漏洞本质：**

当路径中包含特殊字符时，shiro解析得到的路径和SpringMVC解析得到的路径不一致，导致可正常通过shiro的权限校验并正常的完成service的执行获取执行结果。

###  利用场景

在实际场景中每个API会通过网关层统一校验或[@RequiresPermissions](https://github.com/RequiresPermissions
"@RequiresPermissions")注解等方式校验所需访问权限，此漏洞仅能绕过shiro全局的Filter校验，无法绕过API配置的访问权限；

个人理解此问题在实战中利用场景相对有限。

###  修复方式

根据官方commit记录，可知在1.5.2开始，在org.apache.shiro.web.util.WebUtils#getRequestUri中获取uri的方式从request.getRequestURI()换成了request.getContextPath()+request.getServletPath()+request.getPathInfo()组合的方式：

![](https://p3.ssl.qhimg.com/t015b2f0200c46f9a46.png)

此时请求[http://127.0.0.1:9091/aa/..;test=123/admin/index获取到的url为/admin/index，无法绕过shiro的权限校验：](http://127.0.0.1:9091/aa/..;test=123/admin/index%E8%8E%B7%E5%8F%96%E5%88%B0%E7%9A%84url%E4%B8%BA/admin/index%EF%BC%8C%E6%97%A0%E6%B3%95%E7%BB%95%E8%BF%87shiro%E7%9A%84%E6%9D%83%E9%99%90%E6%A0%A1%E9%AA%8C%EF%BC%9A)

![](https://p1.ssl.qhimg.com/t01b0b06c619511dc52.png)

## shiro权限绕过 CVE-2020-11989

###  利用条件

主要是针对CVE-2020-1957修复后的绕过探索，主要两种方式：

  * URL双编码：Apache Shiro = 1.5.2 & controller需为类似”/hello/{page}”的方式
  * 分号绕过：Apache Shiro < 1.5.3 & server.servlet.context-path不为根/

###  利用过程

**URL双编码**

shiro版本需为1.5.2，访问[http://127.0.0.1:9091/hello/test，被shiro权限校验拦截：](http://127.0.0.1:9091/hello/test%EF%BC%8C%E8%A2%ABshiro%E6%9D%83%E9%99%90%E6%A0%A1%E9%AA%8C%E6%8B%A6%E6%88%AA%EF%BC%9A)

![](https://p2.ssl.qhimg.com/t01bd8e4d00b6345041.png)

访问[http://127.0.0.1:9091/hello/te%25%32%66st](http://127.0.0.1:9091/hello/te%2fst)可直接绕过权限校验：

![](https://p5.ssl.qhimg.com/t01731534cb19b55208.png)

**分号绕过**

需要配置server.servlet.context-path：

    
    
    server.servlet.context-path=/test
    

<http://127.0.0.1:9091/test/hello/test>

![](https://p4.ssl.qhimg.com/t016c1fff00bbe4b648.png)

<http://127.0.0.1:9091/a/..;a=1/test/hello/test>

![](https://p1.ssl.qhimg.com/t01ee8618490b436174.png)

###  漏洞分析

**URL双编码分析**

首先发起http请求时，若url中存在URL编码字符，则会被容器进行一次URL解码，此时/hello/te%25%32%66st —>
/hello/te%2fst，接下来则同CVE-2020-1957过程一样，在shiro处理过程中会在org.apache.shiro.web.util.WebUtils#getPathWithinApplication中通过getRequestUri函数获取uri：

![](https://p0.ssl.qhimg.com/t01c6997c063991f290.png)

在org.apache.shiro.web.util.WebUtils#getRequestUri中首先通过request.getContextPath()+request.getServletPath()+request.getPathInfo()组合的方式获取uri为：//hello/te%2fst

![](https://p4.ssl.qhimg.com/t017d2b8fc0a9e3a9c7.png)

接着在进入normalize函数进行格式化处理时，传入的参数经过了decodeAndCleanUriString方法的处理，其中通过调用org.apache.shiro.web.util.WebUtils#decodeRequestString方法，利用URLDecoder.decode进行了URL解码为：//hello/te/st

![](https://p0.ssl.qhimg.com/t01d8995de128e7df83.png)

![](https://p0.ssl.qhimg.com/t01bd04816702fe9943.png)

继续进入normalize函数，将//替换为/，最终获取到的uri为：/hello/te/st

![](https://p2.ssl.qhimg.com/t01ac29a3a89f8eb774.png)

接下来就同上面shiro过程一致了，/hello/te/st不会和任何的规则匹配，成功解析controller并执行相对应的service获取响应结果：

![](https://p1.ssl.qhimg.com/t01e35848ae26ddc41c.png)

补充，在1.5.1及之前版本中，获取uri采用request.getRequestURI方式，获取到的为URL双编码的值，shiro进行一次解码并格式化处理后为/hello/te%2fst，则会和/hello/*进行匹配：

![](https://p0.ssl.qhimg.com/t0113a011b2c268b254.png)

**分号绕过分析**

当请求为[http://127.0.0.1:9091/a/..;a=1/test/hello/test时，](http://127.0.0.1:9091/a/..;a=1/test/hello/test%E6%97%B6%EF%BC%8C)

同URL双编码主要区别在经过request.getContextPath()+request.getServletPath()+request.getPathInfo()组合获取到的uri为：/a/..;a=1/test//hello/test

    
    
    request.getContextPath() --> /a/..;a=1/test
    request.getServletPath() --> /hello/test
    request.getPathInfo() --> null
    

![](https://p2.ssl.qhimg.com/t01ec81f0a360a9337c.png)

接着经过org.apache.shiro.web.util.WebUtils#decodeAndCleanUriString处理后，会根据 ;
进行分割，最终uri结果为：/a/..

![](https://p4.ssl.qhimg.com/t01f390d97d9cd147ab.png)

从而绕过shiro的权限校验，而接下来则和cve-2020-1957流程一致，springmvc会将 ;
进行剔除，最终根据/a/../test/hello/test，即/test/hello/test成功解析controller并执行service获取响应结果：

![](https://p1.ssl.qhimg.com/t013e0a2de894ebefce.png)

###  修复方式

在1.5.3中，获取uri方式改成了getServletPath(request) +
getPathInfo(request)组合的方式，且去除了解码过程：

![](https://p5.ssl.qhimg.com/t01d7870e9d75f705ff.png)

此时，同样的请求[http://127.0.0.1:9091/a/..;a=1/test/hello/test，获取到的requestURI为：/hello/test](http://127.0.0.1:9091/a/..;a=1/test/hello/test%EF%BC%8C%E8%8E%B7%E5%8F%96%E5%88%B0%E7%9A%84requestURI%E4%B8%BA%EF%BC%9A/hello/test)

请求[http://127.0.0.1:9091/hello/te%25%32%66st](http://127.0.0.1:9091/hello/te%2fst)获取到的requestURI为：/hello/te%27st

![](https://p4.ssl.qhimg.com/t01708702606648e576.png)

## shiro权限绕过 CVE-2020-13933

###  利用条件

Apache shiro<=1.5.3 即 Apache Shiro < 1.6.0

controller需为类似”/hello/{page}”的方式利用过程

###  利用过程

<http://127.0.0.1:9091/hello/test>

![](https://p4.ssl.qhimg.com/t01721a78fbfe68e213.png)

<http://127.0.0.1:9091/hello/%3btest>

![](https://p1.ssl.qhimg.com/t01fdb812290cbff400.png)

###  漏洞分析

当发起请求[http://127.0.0.1:9091/hello/%3btest时，](http://127.0.0.1:9091/hello/%3btest%E6%97%B6%EF%BC%8C)

首先容器会进行URL解码，/hello/%3btest —> /hello/;test

进入shiro处理，org.apache.shiro.web.util.WebUtils#getPathWithinApplication中最终结果即requestURI为/hello/：

![](https://p4.ssl.qhimg.com/t01a6fb1817e1ac03e3.png)

    
    
    getServletPath(request) --> /hello/;test
    getPathInfo(request) --> ""
    
    removeSemicolon中根据;进行分割
    

![](https://p1.ssl.qhimg.com/t01fcbb88d0a4ce9ad7.png)

而/hello/不会和/hello/*匹配，顺利进入controller解析并执行service获取响应结果：

![](https://p1.ssl.qhimg.com/t0147db6e3859d8198d.png)

###  修复方式

在1.6.0中，执行shiro过滤器时增加了preHandle方法进行判断是否继续执行：

![](https://p3.ssl.qhimg.com/t012414f7366b99669f.png)

判断内容主要为：若请求URI中包含分号、反斜杠、非ASCII字符（均可配置），则直接响应400

![](https://p1.ssl.qhimg.com/t01236d2b095ec9ecb9.png)

![](https://p4.ssl.qhimg.com/t0122843c39297f59be.png)

核心逻辑均在新增的类org.apache.shiro.web.filter.InvalidRequestFilter中：<https://shiro.apache.org/static/1.6.0/apidocs/org/apache/shiro/web/filter/InvalidRequestFilter.html>

![](https://p2.ssl.qhimg.com/t01a98b401c2e2e7ad5.png)

## shiro权限绕过 CVE-2020-17523

###  利用条件

Apache Shiro < 1.7.1

controller需为类似”/hello/{page}”的方式

###  利用过程

**空格绕过**

1、<http://127.0.0.1:9091/hello/test>

![](https://p3.ssl.qhimg.com/t01d9c70f05dd40254d.png)

2、[http://127.0.0.1:9091/hello/%20](http://127.0.0.1:9091/hello/)

![](https://p0.ssl.qhimg.com/t01b8c88bf88e370559.png)

**西式句号 全路径绕过**

需配置开启全路径匹配：

1、<http://127.0.0.1:9091/hello/>.

![](https://p3.ssl.qhimg.com/t0111fc7fa50fa9d8af.png)

###  漏洞分析

**空格绕过**

当发起[http://127.0.0.1:9091/hello/%20](http://127.0.0.1:9091/hello/)请求时，

首先经过容器URL解码，/hello/%20 —> /hello/空格

发现在shiro进行匹配过程中，/hello/* 和 /hello/空格 不匹配：

![](https://p2.ssl.qhimg.com/t014d366395fb778ef2.png)

在org.apache.shiro.util.AntPathMatcher#doMatch函数中，/hello/* 和 /hello/空格
经过tokenizeToStringArray函数处理后的结果中/hello空格仅剩/hello：

![](https://p1.ssl.qhimg.com/t01683d13ff5b15b049.png)

跟进tokenizeToStringArray方法可知，调用过程中，trimTokens参数值为true：

![](https://p3.ssl.qhimg.com/t0168f8c8ae21a9edfd.png)

而当trimTokens为true时，则会调用trim()，此时/hello/后面的空格将会被丢弃：

![](https://p5.ssl.qhimg.com/t010014f8042f9cbad8.png)

在接下来的判断过程中，匹配结果为false，即/hello/* 和 /hello/空格 不匹配从而导致shiro的权限绕过：

![](https://p2.ssl.qhimg.com/t0131b2576d454c4f3a.png)

**西式句号 全路径绕过**

当请求[http://127.0.0.1:9091/hello/.时，首先经过org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getPathWithinApplication处理时，会被normalize函数将/hello/.最后面的](http://127.0.0.1:9091/hello/.%E6%97%B6%EF%BC%8C%E9%A6%96%E5%85%88%E7%BB%8F%E8%BF%87org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getPathWithinApplication%E5%A4%84%E7%90%86%E6%97%B6%EF%BC%8C%E4%BC%9A%E8%A2%ABnormalize%E5%87%BD%E6%95%B0%E5%B0%86/hello/.%E6%9C%80%E5%90%8E%E9%9D%A2%E7%9A%84)
. 删除掉，最终requestURI为/hello/：

![](https://p4.ssl.qhimg.com/t01e2591684a2cf256b.png)

在org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain处理过程中，由于此时requestURI以/结尾，则将会把最后一个/删除，变成/hello：

![](https://p5.ssl.qhimg.com/t01951c954290b37ad1.png)

而/hello和/hello/*不匹配导致shiro权限绕过：

![](https://p5.ssl.qhimg.com/t01fa0cccecfdf1b1b9.png)

但是，此时SpringMVC进行controller解析时，请求路径为/hello/%2e，spring中.和/默认是作为路径分割符的，不会参与到路径匹配，此时将解析controller失败，返回404:

![](https://p5.ssl.qhimg.com/t01971ad858a6bb4050.png)

即，虽然绕过了shiro的权限校验，但默认无法解析到controller，也就无法执行想要的service；

特殊情况：

当手工配置开启springboot的全路径匹配时，可成功执行：

    
    
    //开启全路径匹配
    @ServletComponentScan
    @SpringBootApplication
    public class Application extends SpringBootServletInitializer implements BeanPostProcessor {
        public static void main(String[] args) {
    
            SpringApplication.run(Application.class, args);
        }
    
        @Override
        protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
            return builder.sources(Application.class);
        }
    
    
        @Override
        public Object postProcessBeforeInitialization(Object bean, String beanName)
                throws BeansException {
            if (bean instanceof RequestMappingHandlerMapping) {
                ((RequestMappingHandlerMapping) bean).setAlwaysUseFullPath(true);
            }
            return bean;
        }
    
        @Override
        public Object postProcessAfterInitialization(Object bean, String beanName)
                throws BeansException {
            return bean;
        }
    }
    

![](https://p2.ssl.qhimg.com/t01705f7ec72ee7eb32.png)

###  修复方式

1、将tokenizeToStringArray函数的trimTokens参数设置为false，防止空格被抛弃：

![](https://p1.ssl.qhimg.com/t01ef1defa7d32334b6.png)

2、将剔除结尾/的过程移到匹配的下方：

![](https://p4.ssl.qhimg.com/t01cfc95f644f6e54ef.png)

![](https://p5.ssl.qhimg.com/t01b2445bf547f53485.png)

## 总结

开头所说的利用分号绕过了nginx的403屏蔽，请求到springboot项目后携带分号解析成功，而当使用了shiro
1.6.0后，url中携带分号则直接报错400，原因就很清晰了，因为在1.6.0中增加了org.apache.shiro.web.filter.InvalidRequestFilter类，其中会判断请求中包含分号时响应400状态码；

shiro的权限绕过，本质还是shiro对uri的解析规则和后端开发框架的解析规则不一样所导致。

## 巨人的肩膀

<https://github.com/apache/shiro/commit/3708d7907016bf2fa12691dff6ff0def1249b8ce>

<https://shiro.apache.org/static/1.6.0/apidocs/org/apache/shiro/web/filter/InvalidRequestFilter.html>

<https://github.com/apache/shiro/commit/0842c27fa72d0da5de0c5723a66d402fe20903df>

<https://shiro.apache.org/security-reports.html>

<https://xlab.tencent.com/cn/2020/06/30/xlab-20-002/>

<https://mp.weixin.qq.com/s/yb6Tb7zSTKKmBlcNVz0MBA>

<https://github.com/jweny/shiro-cve-2020-17523>

<https://segmentfault.com/a/1190000039703198>

……

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ttestoo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253749](/post/id/253749)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [shiro](/tag/shiro)
  * [权限绕过](/tag/权限绕过)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t019adae1145cd57009.png) ttestoo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

