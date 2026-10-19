##  前言

 **2020年3月23号，Shiro开发者Brian Demers在[用户社区](http://shiro-user.582556.n2.nabble.com/Re-ANNOUNCE-CVE-2020-1957-Apache-Shiro-1-5-2-released-td7582136.html)发表帖子，提醒shiro用户进行安全更新，本次更新进行了三个修复，其中就包括了对编号为CVE-2020-1957的Shrio授权绕过漏洞的修复。漏洞影响shiro
1.5.2版本以下。**

![1.png](https://image.3001.net/images/20200330/15855529728296.png!small)

##  分析过程

###  SHIRO-682

根据Shiro开发者在1.5.2版本中提交的[commit](https://github.com/apache/shiro/commit/3708d7907016bf2fa12691dff6ff0def1249b8ce)中关于PathMatchingFilter类的测试用例，可以直接关联到JIRA
issue[SHIRO-682](https://issues.apache.org/jira/browse/SHIRO-682)，该issue在1.5.0版本中进行了修复。而1.5.2版本中更新则是对其绕过的修复。

![2.png](https://image.3001.net/images/20200330/15855531004235.png!small)

SHIRO-682的修复了spring框架下uri = uri + ‘/’ 绕过Shiro防护的问题。然后下面的描述则清晰得描述了造成改错误的原因。

在Spring web项目中，请求URI/resource/menus和/resource/menus/都可以访问到服务器的资源。

但在Shiro中的URL路径表达式pathPattern可以正确匹配/resource/menus，但不能正确匹配/resource/menus/，导致过滤链无法正确匹配，从而绕Shiro的防护机制。

![3.png](https://image.3001.net/images/20200330/15855531141523.png!small)

###  Shiro拦截器

Shiro框架通过拦截器功能来实现对用户访问权限的控制和拦截。Shiro中常见的拦截器有anon,authc等拦截器。

> 1.anon为匿名拦截器，不需要登录就能访问，一般用于静态资源,或者移动端接口
>
> 2.authc为登录拦截器，需要登录认证才能访问的资源。

用户可以在Shiro.ini编写匹配URL配置，将会拦截匹配的URL，并执行响应的拦截器。从而实现对URL的访问控制，URL路径表达式通常为ANT格式。如下配置，访问
/index.html主页的时候，Shiro将不会对其进行登录判断，anon拦截器不需要登录就能进行访问。而对于/user/xiaoming 等
/user/xiaogang等接口，authc拦截器将会对其进行登录判断，有登录认证才能访问资源。

    
    
    [urls]
    /index.html = anon
    /user/** = authc

Shiro的URL路径表达式为Ant 格式，路径通配符支持?***。

    
    
    ?：匹配一个字符
    *：匹配零个或多个字符串
    **：匹配路径中的零个或多个路径

其中*表示匹配零个或多个字符串，/*可以匹配/hello，但匹配不到/hello/因为*通配符无法匹配路径。假设/hello接口设置了authc拦截器，访问/hello将会被进行权限判断，如果请求的URI为/hello/呢，/*URL路径表达式将无法正确匹配，放行。然后进入到spring(Servlet)拦截器，spring中/hello形式和/hello/形式的URL访问的资源是一样的。

###  漏洞复现

明白上文的内容，漏洞复现就很容易了，复现环境代码主要参考网上的开源[demo](https://github.com/lenve/javaboy-code-samples/tree/master/shiro/shiro-basic)。

> 1.下载demo代码[shiro-basic](https://github.com/lenve/javaboy-code-> samples/tree/master/shiro/shiro-basic)。
>
> 2.导入idea
>
> 3.Shiro版本1.4.2
    
    
        <dependency>
            <groupId>org.apache.shiro</groupId>
            <artifactId>shiro-web</artifactId>
            <version>1.4.2</version>
        </dependency>
        <dependency>
            <groupId>org.apache.shiro</groupId>
            <artifactId>shiro-spring</artifactId>
            <version>1.4.2</version>
        </dependency>

4.修改ShiroConfig配置文件，添加authc拦截器的拦截正则

    
    
        @Bean
        ShiroFilterFactoryBean shiroFilterFactoryBean() {
            ShiroFilterFactoryBean bean = new ShiroFilterFactoryBean();
            ...
            ...
            //map.put("/*", "authc");
            map.put("/hello/*", "authc"); 
            bean.setFilterChainDefinitionMap(map);
            return bean;
        }

5.修改路由控制器方法

    
    
    @GetMapping("/hello/{currentPage}")
        public String hello(@PathVariable Integer currentPage) {
            return "hello";
    }

6.启动应用

访问/hello/1接口，可以看到被authc拦截器拦截了，将会跳转到登录接口进行登录。

![4.png](https://image.3001.net/images/20200330/15855531529677.png!small)

访问/hello/1/，成功绕过authc拦截器，获取到了资源。

![5.png](https://image.3001.net/images/20200330/15855531647767.png!small)

###  漏洞成因

漏洞初始成因可以定位到
PathMatchingFilterChainResolver的getChain函数下，该函数作用根据URL路径匹配中配置的url路径表达式来匹配输入的URL，判断是否匹配拦截器，匹配成功将会返回响应的拦截器执行链，让ShiroFither执行权限操作的。

其对于URL路径表达式和输入URL的匹配主要通过pathMathches函数进行匹配。

![6.png](https://image.3001.net/images/20200330/1585553173541.png!small)

pathMatches函数其最终会调用shiro.util.AntPathMatcher类中doMatch的对于ant格式的pathPattern和requestURI进行匹配。

    
    
    //pathMatches:135, PathMatchingFilterChainResolver (org.apache.shiro.web.filter.mgt)
    protected boolean pathMatches(String pattern, String path) {
            PatternMatcher pathMatcher = this.getPathMatcher();
            return pathMatcher.matches(pattern, path);
    }

doMatch:109, AntPathMatcher (org.apache.shiro.util)，当Shiro 的Ant格式的pathPattern
中的的*通配符是不支持匹配路径的，所以/hello/*不能成功匹配/hello/1/，也就不会触发authc拦截器进行权限拦截。从而成功绕过了Shiro拦截器，而后再进入到spring拦截器中，/hello/1/与/hello/1能获取到相同的资源。

![7.png](https://image.3001.net/images/20200330/15855531835042.png!small)

###  漏洞修复

该漏洞是由中国开发者在2019年3月25日在ShiroGitHub项目上提交的[issue](https://github.com/apache/shiro/pull/127)，并PR了分支代码[589f10](https://github.com/apache/shiro/commit/589f10d40414a815dbcaf1f1500a51f41258ef70)添加漏洞修复代码，最终分支代码在1.5.0版本进行了合并，合并时间为2019年11月20日。

###  1.5.0版本修复

1.5.0版本修复源自tomsun28提交的PR代码，代码修复位置为pathsMatch:125, PathMatchingFilter
(org.apache.shiro.web.filter)，该修复方式是通过判断requestURI是否以/为结尾，如果以/结尾的话，则去掉尾部的/符号在与URL表达式进行比较。

也就是当requestURI为/hello/1/等以/为结尾的URI的时候，都会被清除最后的/号，再进行URL路径匹配。

![8.png](https://image.3001.net/images/20200330/15855532071802.png!small)

###  ≤1.5.1版本绕过

观察1.5.2版本中新添加的[测试用例](https://github.com/apache/shiro/commit/3708d7907016bf2fa12691dff6ff0def1249b8ce)。

![9.png](https://image.3001.net/images/20200330/15855532183528.png!small)

切换测试版本到1.5.1中，然后从中上面的测试用例提取payload进行绕过。

在1.5.1版本中，添加/还是会直接跳转到登录。

![10.png](https://image.3001.net/images/20200330/1585553232642.png!small)  

绕过payload，/fdsf;/../hello/1，成功绕过。

![11.png](https://image.3001.net/images/20200330/15855532389426.png!small)

问题同样可以定位到getChain函数中对于requestURI的获取中，如下图所示，this.getPathWithinApplication(request)获取的requestURI为/fdsf，而不是我们输入的/fdsf;/../hello/1，从而导致后面的URI路径模式匹配返回False，从而再次绕过了shiro拦截器。

![12.png](https://image.3001.net/images/20200330/15855532467830.png!small)

getPathWithinApplication函数中会调用WebUtils
(org.apache.shiro.web.util)中的getRequestUri函数获取RequestUri。

    
    
    public static String getRequestUri(HttpServletRequest request) {
            String uri = (String)request.getAttribute("javax.servlet.include.request_uri");
            if (uri == null) {
                uri = request.getRequestURI();
            }
            return normalize(decodeAndCleanUriString(request, uri));
        }

RequestUri函数中最终调用decodeAndCleanUriString函数对URI进行清洗。

    
    
    private static String decodeAndCleanUriString(HttpServletRequest request, String uri) {
          uri = decodeRequestString(request, uri);
          int semicolonIndex = uri.indexOf(59);//获取;号的位置
          return semicolonIndex != -1 ? uri.substring(0, semicolonIndex) : uri;
      }

如果URI中存在;号的话，则会删除其后面的所有字符。/fdsf;/../hello/1/最终也就变成了/fdsf。

![13.png](https://image.3001.net/images/20200330/15855532548192.png!small)

###  1.5.2版本修复

再1.5.2版本中对其进行了[修复](https://github.com/apache/shiro/commit/3708d7907016bf2fa12691dff6ff0def1249b8ce#diff-98f7bc5c0391389e56531f8b3754081aR139)，获取requestURI的方式从request.getRequestUri直接获取的方式更改为获取request的ContextPath，ServletPath，PathInfo，然后再重新拼接而成。

![14.png](https://image.3001.net/images/20200330/15855532693817.png!small)

输入的/fdsf;/../hello/1/，将会被拼接为//hello/1/1再进行URI路径匹配，则无法绕过拦截器。

![15.png](https://image.3001.net/images/20200330/15855532764921.png!small)

##  总结

在web容器中，Shiro的拦截器是先与spring(Servlet)执行，两者拦截器对于URI模式匹配的差异，导致Shiro拦截器的绕过，而Shiro对其进行了两次修复，其一为删除requestURI后面的/号进行URL路径匹配，算是简单的修复了添加/号绕过的方式，而后在1.5.2版本中通过requestURI自主拼接的方式修复了/fdsf;/../hello/1/等使用了;号方式的绕过。

而后又会有什么形式的绕过，或者又有什么其它容器导致的差异化绕过。则未可知。

##  修复方案

> 1.升级1.5.2版本及以上
>
> 2.尽量避免使用*通配符作为动态路由拦截器的URL路径表达式。

##  参考链接

> 1.<https://github.com/apache/shiro/pull/127>
>
> 2.<https://blog.51cto.com/luchunli/1835108>
>
> 3.<https://issues.apache.org/jira/browse/SHIRO-682>
>
> 4.<https://www.syshlang.com/96db3174/>
>
> 5.<http://shiro-user.582556.n2.nabble.com/Re-ANNOUNCE-CVE-2020-1957-Apache-> Shiro-1-5-2-released-td7582136.html>

 ***本文作者： tbag@斗象能力中心TCC，转载请注明来自FreeBuf.COM**

  

