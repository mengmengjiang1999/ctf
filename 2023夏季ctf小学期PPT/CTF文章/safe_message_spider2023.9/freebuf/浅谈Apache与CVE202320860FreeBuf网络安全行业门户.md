# 一、前言

一般情况下，开发者配置鉴权时，可能都会遵循一个原则，就是"优先使用/**认证兜底，明确哪些接口无需认证，而不是明确哪些接口需要认证。

在Spring Controller中,以下两个路由访问是等价的（熟悉spring
framework源码的话，会知道其实都是在解析pattern前做了补全的处理（不论是AntPathMatcher还是高版本的PathPattern））：

    
    
    @GetMapping("/admin/*")
    @GetMapping("admin/*")
    

所以很多时候有的开发者会会直接认为`**`代表全路径，确实在某些鉴权框架中也生效了。

# 1.1 关于CVE-2023-20860

前段时间Spring官方发布了Spring Framework 身份认证绕过漏洞(CVE-2023-20860)，当Spring
Security使用mvcRequestMatcher配置并将**作为匹配模式时，在Spring Security 和 Spring MVC
之间会发生模式不匹配，最终可能导致身份认证绕过。首先简单回顾下漏洞的原理：

对比commit可以看到在调用PathPattern的match之前，首先判断pattern是否以`/`开头，如果不是的话进行补全（以修复版本spring-webmvc-5.3.26为例）：

  * PS： 下面代码块中的/admin/**就是pattern:

    
    
    httpSecurity.authorizeRequests().mvcMatchers("/admin/**").authenticated();
    

![wKg0C2QnsFSAThNqAAERs41afZo945.png](https://image.3001.net/images/20230707/1688714548_64a7bd34871d0a6ffe3b1.png!small)

结合漏洞描述以及对commit的分析，大致绕过的是如下的配置：

    
    
    httpSecurity.authorizeRequests().mvcMatchers("**").authenticated();
    

结合影响的版本可以确定对应的Spring应用使用的是PathPattern进行解析。而MvcRequestMatcher实际上使用Spring
MVC的HandlerMappingIntrospector来匹配路径并提取变量，对应的影响判断在匹配pattern跟请求的path时使用的也是PathPattern。根据PathPattern的解析方式，大致可以知道漏洞的成因了。

首先PathPattern会根据/将URL拆分成多个PathElement对象，然后根据其的链式节点中对应的PathElement的matches方法逐个进行匹配。正常情况下，`/**`这个Pattern对应的matches是WildcardTheRestPathElement。

因为PathPattern通配符只能定义在尾部(不能以/结尾)，所以当pathElements的元素个数大于PathPattern中的元素个数即可匹配：

![wKg0C2QnskSAGxdtAABZf2MEWQI945.png](https://image.3001.net/images/20230707/1688714549_64a7bd35142c842385fdc.png!small)

所以此时正常情况下访问/admin/page无法绕过。

但是如果此时使用的是`**`这个Pattern，因为漏洞版本缺少了补全`/`的操作（修复版本会判断pattern是否以`/`开头，如果不是的话进行补全），那么此时对应的matches是RegexPathElement：

就跟命名里的Regex一样，这个matches主要是通过java.util.regex.compile#matcher处理，看看当前pathElements的内容是否符合正则预期：

![wKg0C2QntAWAGe47AACpiTypOJc125.png](https://image.3001.net/images/20230707/1688714549_64a7bd35c389a3837a477.png!small)

此时获取textToMacth，对于`/admin/page`这个path第一个元素是`/`，此时会返回空字符串：

![wKg0C2QntG2ANJkVAAA1Win1LIk913.png](https://image.3001.net/images/20230707/1688714550_64a7bd36a39af0ec8df92.png!small)

虽然`*`能匹配到空字符串，但是这里还有一个逻辑，首先pathIndex+1后明显小于`matchingContext.pathLength`，此时matches为false，再往下的逻辑，pathIndex+1后对应的元素并不是`/`，而是admin，此时匹配失败，auth
Bypass：

    
    
    matches = pathIndex + 1 >= matchingContext.pathLength && (this.variableNames.isEmpty() || textToMatch.length() > 0);
    if (!matches && matchingContext.isMatchOptionalTrailingSeparator()) {
        matches = (this.variableNames.isEmpty() || textToMatch.length() > 0) && pathIndex + 2 >= matchingContext.pathLength && matchingContext.isSeparator(pathIndex + 1);
    }
    

![wKg0C2QnthKAQF27AABP1i8TnsI535.png](https://image.3001.net/images/20230707/1688714551_64a7bd3718fe95c9f1734.png!small)

![wKg0C2QntkOAPeMsAAB6y0MrZDI315.png](https://image.3001.net/images/20230707/1688714551_64a7bd3781213c8942d06.png!small)

在Java生态中，还有一个常用的鉴权组件shiro，那么shiro请求解析的过程又是怎么样处理的呢，是否也会有类似的问题。查看shiro的源码进行简单的分析：

![wKg0C2QntreAOQhZAAAk5q5p27s891.png](https://image.3001.net/images/20230707/1688714552_64a7bd383f60f12fb4349.png!small)

# 二、特殊场景下的shiro auth Bypass

结合上述背景，查看shiro能否按期我们的预期处理`**`：

## 2.1 相关场景

假设设置对应的url和过滤器匹配规则如下：

    
    
    @Bean
    ShiroFilterFactoryBean shiroFilterFactoryBean(){
        ShiroFilterConfiguration shiroFilterConfiguration = new ShiroFilterConfiguration();
        shiroFilterConfiguration.setStaticSecurityManagerEnabled(true);
        shiroFilterConfiguration.setFilterOncePerRequest(true);
    
        ShiroFilterFactoryBean bean = new ShiroFilterFactoryBean();
        bean.setShiroFilterConfiguration(shiroFilterConfiguration);
    
        bean.setSecurityManager(securityManager());
        bean.setLoginUrl("/login");
        bean.setSuccessUrl("/index");
        bean.setUnauthorizedUrl("/unauthorizedurl");
        Map<String, String> map = new LinkedHashMap<>();
        map.put("/**", "authc");
        map.put("/doLogin", "anon");
        bean.setFilterChainDefinitionMap(map);
        return  bean;
    }
    

按照预期的设定，按道理是能对以下Controller进行防护的：

    
    
    @GetMapping("/admin/page")
    public String admin() {
        return "admin page";
    }
    

实际上这个配置并不会生效，还是可以访问到对应的Controller：

![wKg0C2QnuMAfArhAABJlnDpfHM504.png](https://image.3001.net/images/20230707/1688714552_64a7bd38ad1ece0f375fe.png!small)

## 2.2 具体原理

以1.10.0版本的shiro为例，查看具体的原因：

当发起HTTP请求时，Shiro 的多个过滤器形成了一条链，所有请求都必须通过这些过滤器后才能成功访问到资源。简单看下Shiro拦截请求处理的过程。

查阅相关资料，shiro
发挥作用的入口是在`org.apache.shiro.spring.web.ShiroFilterFactoryBean.SpringShiroFilter`中，其中它继承自
OncePerRequestFilter，字面上看是每个请求执行一次。

在接收到请求时会先进入 OncePerRequestFilter.doFilter() ，在这里写一个断点：

![wKg0C2Qnuo2AG170AAB7mr12Ggc457.png](https://image.3001.net/images/20230707/1688714553_64a7bd392720acdb8103c.png!small)

这里会做一些简单的判断，然后org.apache.shiro.web.servlet.AbstractShiroFilter#doFilterInternal方法，首先会对request
和 response 对象进行包装，然后调用createSubject方法，这里会处理认证授权信息并进行封装:

![wKg0C2QnurCAfXorAAB2XxGTqws584.png](https://image.3001.net/images/20230707/1688714553_64a7bd39982411c311ce1.png!small)

接着在Callable修改了最近一次的访问时间，然后调用
FilterChain，实际上调用的是org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain来获取（会根据URL路径匹配，解析出ServletRequest请求过程中要执行的过滤器链）:

![wKg0C2QnutKAYBNPAAA3S40XwbU850.png](https://image.3001.net/images/20230707/1688714554_64a7bd3a97cbca2dc98bb.png!small)

根据前面的分析，在org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain来获取其会根据URL路径匹配，解析出ServletRequest请求过程中要执行的过滤器链：

![wKg0C2QnuQiAezRjAAAufuAy2HQ389.png](https://image.3001.net/images/20230707/1688714555_64a7bd3b166e8b06e7851.png!small)

首先调用getPathWithinApplication方法获取应用程序内的URI的相对路径，然后往下遍历filterChains，requestURI和pattern匹配的话会代理到
filterChainManager.proxy方法里去，如果不能匹配，会删除最后的"/" 再匹配一次：

![wKg0C2QnuSuAV47GAACSYvpaD0407.png](https://image.3001.net/images/20230707/1688714555_64a7bd3b7d594e6662195.png!small)

shiro使用的是AntPathMatcher进行匹配的，如果请求的path和pattern没有以/，就不再进行匹配了，
**与Spring不同的是，shiro在匹配前并不会对pattern进行检查，补全开头的/** ：

![wKg0C2QnuWCAM7F4AABwG9IAzhY357.png](https://image.3001.net/images/20230707/1688714556_64a7bd3c41a8f76ad7370.png!small)

根据AntPathMatcher的代码可以知道，如果pattern没有以`/`开头会直接匹配失败。会导致前面的对于`**`配置失效，可以看到filterChain仅仅返回了InvalidRequestFilter，并没有返回authc对应的Filter（权限控制失效）:

![wKg0C2QnuaCABNxOAABcwMkRFyM125.png](https://image.3001.net/images/20230707/1688714556_64a7bd3cb6168f709aeaa.png!small)

PS：实际上只要不以`/`开头的Pattern，Shiro都会找不到对应的Filter。所以类似`admin/*`的配置也是会auth Bypass的。

# 三、其他

相比CVE-2023-20860，`**`这个auth Bypass并不是由于shiro与Spring
Framework的解析不一致导致的。这个问题也第一时间反馈给了Apache，但是Apache认为这不能算一个漏洞：

![wKg0C2Qnu96AELGAAAtrtUDs287.png](https://image.3001.net/images/20230707/1688714557_64a7bd3d26adb46353727.png!small)

实际上在开发过程中由于各个框架间的差异导致的安全问题是十分常见的，如何正确的使用现有框架，规避不必要的安全风险是一个值得思考的问题。

