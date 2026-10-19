# Shiro权限绕过漏洞详细分析

阅读量 **229882**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-12 10:00:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0175552f2250560322.jpg)

## 0x00 前言

上次讲了关于Jackson的相关漏洞，这次首先来分析一下shiro的权限绕过漏洞的原理。本文首先通过shiro<1.5.0版本引出shiro身份校验问题，再使用CVE-2020-1957也就是shiro-682存在的漏洞来详细分析shiro的权限绕过漏洞，并进一步来看看shiro这两个新的CVE-2020-11989和CVE-2020-13933。

## 0x01 关于shiro

shiro是做身份认证和权限管理的一款apache框架，可以和spring一起使用。这次的权限绕过漏洞就出在和spring boot搭配这里。

shiro框架通过拦截器来实现对用户访问权限的控制和拦截。Shiro常见的拦截器有anon,authc等。

  1. anon：匿名拦截器，不需登录就能访问，一般用于静态资源，或者移动端接口。
  2. authc：登录拦截器，需要登录认证才能访问的资源。

我们通过在配置文件中配置需要登录才可访问的url，实现对url的访问控制。其中，url的路径表达式为Ant格式。

## 0x02 shiro<1.5.0

在shiro1.5.0版本的修复中，可以看到会判断requestURI是否以“/”为结尾，如果以“/”结尾的话，则去掉尾部的“/”后，再与url表达式比较。

这样可以判断shiro<1.5.0中，可以通过构造127.0.0.1:8080/admin/password/绕过shiro认证。

（本段只作为引出内容，请继续向下看）

## 0x03 CVE-2020-1957详细分析（<1.5.2）

###  一、环境搭建

工具：IDEA  
步骤：  
1.首先创建spring boot项目，pox.xml添加依赖。

    
    
    <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
            </dependency>
            <dependency>
                <groupId>org.apache.shiro</groupId>
                <artifactId>shiro-web</artifactId>
                <version>1.5.0</version>
            </dependency>
            <dependency>
                <groupId>org.apache.shiro</groupId>
                <artifactId>shiro-spring</artifactId>
                <version>1.5.0</version>
    </dependency>
    

2.创建核心组件realm，用作简单的认证功能。

    
    
    //MyRealm.java
    package com.shiro;
    
    import org.apache.shiro.authc.*;
    import org.apache.shiro.authz.AuthorizationInfo;
    import org.apache.shiro.realm.AuthorizingRealm;
    import org.apache.shiro.subject.PrincipalCollection;
    
    public class MyRealm extends AuthorizingRealm {
        @Override
        protected AuthorizationInfo doGetAuthorizationInfo(PrincipalCollection principals) {
            return null;
        }
    
        @Override
        protected AuthenticationInfo doGetAuthenticationInfo(AuthenticationToken token) throws AuthenticationException {
            String username = (String) token.getPrincipal();
            if (!"lcecre4m".equals(username)) {
                throw new UnknownAccountException("账户不存在!");
            }
            return new SimpleAuthenticationInfo(username, "123456", getName());
        }
    }
    

3.创建ShiroConfig.java配置shiro，这里使用authc拦截器对访问“/admin/**”进行认证。

    
    
    //ShiroConfig.java
    package com.shiro;
    
    import org.apache.shiro.mgt.SecurityManager;
    import org.apache.shiro.spring.web.ShiroFilterFactoryBean;
    import org.apache.shiro.web.mgt.DefaultWebSecurityManager;
    import org.springframework.context.annotation.Bean;
    import org.springframework.context.annotation.Configuration;
    import java.util.LinkedHashMap;
    import java.util.Map;
    
    @Configuration
    public class ShiroConfig {
        @Bean
        MyRealm myRealm() {
            return new MyRealm();
        }
        @Bean
        SecurityManager securityManager() {
            DefaultWebSecurityManager manager = new DefaultWebSecurityManager();
            manager.setRealm(myRealm());
            return manager;
        }
        @Bean
        ShiroFilterFactoryBean shiroFilterFactoryBean() {
            ShiroFilterFactoryBean bean = new ShiroFilterFactoryBean();
            bean.setSecurityManager(securityManager());
            bean.setLoginUrl("/login");
            bean.setSuccessUrl("/index");
            bean.setUnauthorizedUrl("/unauthorizedurl");
            Map<String, String> map = new LinkedHashMap<>();
            map.put("/hello/**", "anon");
            map.put("/admin/**", "authc");
            bean.setFilterChainDefinitionMap(map);
            return bean;
        }
    }
    

4.LoginController.java用来创建相关使用接口。

    
    
    //LoginController.java
    package com.shiro;
    
    import org.apache.shiro.SecurityUtils;
    import org.apache.shiro.authc.AuthenticationException;
    import org.apache.shiro.authc.UsernamePasswordToken;
    import org.apache.shiro.subject.Subject;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.PostMapping;
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.RestController;
    
    @RestController
    public class LoginController {
        @PostMapping("/doLogin")
        public void doLogin(String username, String password) {
            Subject subject = SecurityUtils.getSubject();
            try {
                subject.login(new UsernamePasswordToken(username, password));
                System.out.println("登录成功!");
            } catch (AuthenticationException e) {
                e.printStackTrace();
                System.out.println("登录失败!");
            }
        }
        @GetMapping("/hello")
        public String hello() {
            return "hello";
        }
        @GetMapping("/admin/password")
        public String  index() {
            return "password";
        }
    }
    

5.启动测试。访问127.0.0.1:8080/hello正常；访问127.0.0.1:8080/admin/password会跳转到127.0.0.1:8080/login要求进行登录。简单实现了spring+shiro的身份认证功能。  
6.漏洞测试。访问127.0.0.1:8080/xxx/..;/admin/password成功绕过身份校验。

###  二、动态分析

首先在PathMatchingFilterChainResolver.class#getChain处下断点，进行调试，访问127.0.0.1:8080/xxx/..;/admin/password

![](https://p2.ssl.qhimg.com/t015e7a47babe45426a.png)

我们单步步入getPathWithinApplication(request)，在WebUtils#getPathWithinApplication()中，参数为ServletRequest对象，获取到上下文信息后，再用getRequestUri()获取具体的url

![](https://p1.ssl.qhimg.com/t0196f766494aa4e670.png)

我们步入getRequestUri()，可以看到已经获取到了我们访问的原始url

![](https://p3.ssl.qhimg.com/t01f32b0c0268d73396.png)

我们可以看到在返回之前做了相关处理，我们单步步入这个decodeAndCleanUriString(request,
uri)，可以看到在这个函数里以“;”截断后面的内容，并返回作为normalize(decodeAndCleanUriString(request,
uri))的参数

![](https://p5.ssl.qhimg.com/t019df891cc7c470ece.png)

继续步入normalize()，可以看到url已经变为“/xxx/..”了

![](https://p4.ssl.qhimg.com/t0148411be1450b19fb.png)

在normalize(String path, boolean
replaceBackSlash)内部对传入的路径进行标准化规范处理，相关操作包括替换反斜线、替换“//”为“/”等，最后得到返回的url

![](https://p0.ssl.qhimg.com/t012915fbdef5c1d082.png)

一路返回到PathMatchingFilterChainResolver.class#getChain，我们得到接下来shiro需要处理的url：/xxx/..

![](https://p4.ssl.qhimg.com/t011e013b8a5cabee0e.png)

接下来在while段里使用pathMatches(pathPattern, requestURI)进行权限校验

![](https://p5.ssl.qhimg.com/t01a40081b0ac06bac2.png)

我们单步步入pathMatches函数直到AntPathMatcher.java#doMatch，在里面与我们设置的shiro规则进行匹配，很显然，“/admin/**”不会与“/xxx/..”匹配成功

![](https://p5.ssl.qhimg.com/t011f9e3512dcf99652.png)

我们的url经过shiro的处理认证通过后，就会进入spring
boot中进行解析，我们在UrlPathHelper#getLookupPathForRequest下断点，并提前配置好使用getPathWithinServletMapping(request,
pathWithinApp)进行解析

![](https://p5.ssl.qhimg.com/t01a5e25734a2f6528b.png)

步入getPathWithinServletMapping()后，依次通过UrlPathHelper#getServletPath、HttpServletRequestWrapper#getServletPath、Request#getServletPath获取到我们实际访问的url：127.0.0.1:8080/admin/password后返回，最终实现绕过权限访问

![](https://p2.ssl.qhimg.com/t01b122254a8a4f53ff.png)

###  三、修复

在漏洞版本<=1.5.1，request.getRequestURI()直接返回请求的url，在1.5.2中修复为使用contextPath()+
servletPath()+ pathinfo()组合而成。

![](https://p1.ssl.qhimg.com/t0164f395797c140e74.png)

## 0x04 CVE-2020-11989 && CVE-2020-13933

CVE-2020-11989的shiro版本为<1.5.3和CVE-2020-13933的shiro版本为<1.6.0。他们原理类似，都是利用“;”或url编码进行绕过，比如127.0.0.1:8080/admin/%3bpassword等payload，这里就不详细跟踪分析了，过程跟shiro-682类似，原理都是利用shiro与spring
boot使用不同的url来绕过校验。

最后1.6.0版本中修复是添加一个InvalidRequestFilter类，从全局上对“；”和“\”和非ASCII字符进行过滤

![](https://p0.ssl.qhimg.com/t0147f276956db0fbc5.png)

## 0x05 shiro权限绕过小结

在shiro权限绕过漏洞中，利用的问题是shiro拦截器先于spring
boot执行，并且二者的匹配模式不同，最终导致：我们访问的url1和shiro处理的url2以及spring路由的url3不同，导致shiro拦截器起不到应有的作用，总被绕过。

## 0x06 结语

本文通过对shiro-682的详细分析，分析了shiro权限绕过的过程，同时也学习了后续的一些绕过姿势，shiro权限绕过就应该非常清晰了。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zzZ** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/226899](/post/id/226899)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t0177bde109b464d6d4.png) zzZ

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

