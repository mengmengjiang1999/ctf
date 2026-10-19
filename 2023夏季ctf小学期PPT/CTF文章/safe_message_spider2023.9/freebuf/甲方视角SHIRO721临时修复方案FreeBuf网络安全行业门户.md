## 0x00 问题简介

14日晚上，发现了一个公开的Shiro的RCE漏洞，作为在甲方工作了挺久的人，一听Shiro立马虎躯一震，来不及分析poc，立马先得确认公司业务是否受到影响。确定了影响后，立马看怎么修复漏洞。结果悲催的时候出现了，这个漏洞官方居然没有升级修复。这让笔者想起差不多半年前给Shiro官方推的一个加固，结果一直没有收到官方回复，直接杳无音讯。

### 受影响的组件漏洞版本

以下组件的全量版本均收到漏洞影响，当然这个这个漏洞需要可以登录才能利用。

    
    
    <dependency>
        <groupId>org.apache.shiro</groupId>
        <artifactId>shiro-core</artifactId>
    </dependency>
    

## 0x01 问题分析

参考[https://www.anquanke.com/post/id/192819。](https://www.anquanke.com/post/id/192819%E3%80%82)

笔者看漏洞分析，大致清楚了漏洞原理及其触发条件，但来不及分析更多细节。也更加聚焦于怎么让业务修复这个漏洞。大致想了下几种常见的漏洞处理办法：

> （1）升级：上面说了官方没有解决，pass
>
> （2）下线业务：除非业务真的没有用了，否则面谈，pass
>
> （3）WAF拦截EXP：Shiro的EXP是加密值，特征不够明显（这里先不谈绕过），而且有些甲方的有些业务还没接WAF，pass。

如此看来，似乎只能希望攻击者没有账号不来搞事情了。但是想想，这么搞也太不负责任，并且业务还在等着方案，通知了业务有没有修复方案难免有点有损安全部门门脸。是在没有办法，只能想着自己出修复方案了。

经过和业务沟通，发现有些业务虽然用了Shiro框架，但是并不需要rememberMe这个功能，于是想着，能不能找到个配置方法，把这个功能直接干掉，经过分析，在极短的时间内没有发现。于是又想，Shiro这个漏洞不是从Filter触发的吗，能不能在Filter做点事情，把rememberMe这个功能干掉。于是，有两个思路来干掉rememberMe功能。

> 思路（1）：提供一个Filter，在Shiro的Filter被调用前就调用，然后将cookie里的rememberMe直接置空。
>
> 思路（2）：覆盖Shiro Filter的一些行为，然后去掉rememberMe功能。
>
> 思路（1）实现起来很简单，但是有个问题，就怕业务配置filer的顺序错误，导致问题没有修复。所有想着用思路（2）。

于是问题聚焦于怎么找到Shiro的Filter，以及怎么覆盖其行为。

### 1.1 寻找Shiro的Filter

用poc直接大断点，发现Filter是ShiroFilterFactoryBean$SpringShiroFilter。

![](https://image.3001.net/images/20191114/1573739053_5dcd5a2d952de.png!small)

但是发现这个内部类是个final Class，因此是没有办法被继承的。

    
    
    private static final class SpringShiroFilter extends AbstractShiroFilter {
    
            protected SpringShiroFilter(WebSecurityManager webSecurityManager, FilterChainResolver resolver) {
                super();
                if (webSecurityManager == null) {
                    throw new IllegalArgumentException("WebSecurityManager property cannot be null.");
                }
                setSecurityManager(webSecurityManager);
                if (resolver != null) {
                    setFilterChainResolver(resolver);
                }
            }
        }
    

### 1.2 覆盖默认的Filter

由于这个内部类是个final Class，只能去更底一级覆盖。我们看下Shiro的配置：

    
    
    <filter>
            <!--filter 配置-->
            <filter-name>shiroFilter</filter-name>
            <filter-class>org.springframework.web.filter.DelegatingFilterProxy</filter-class>
            <init-param>
                <param-name>targetFilterLifecycle</param-name>
                <param-value>true</param-value>
            </init-param>
    </filter>
    
    <bean id="shiroFilter" class="org.apache.shiro.spring.web.ShiroFilterFactoryBean">
        <!--省略-->
    </bean>
    

于是，我们发现可以复写ShiroFilterFactoryBean类，然后让业务使用我们配置的类，从而覆盖Shiro
Filter默认的行为，去除rememberMe功能。于是得到以下的临时pactch方案。

这里强调几个注意点：（1）复写的类出得request是ServletRequest实例，没有操作cookie的方法。实际上在tomcat下，这个类是RequestFacade实例。（2）RequestFacade实例写代码时需要加额外的provided
maven依赖。由于这个类和tomcat版本有关，因此需要测兼容性，不通用，可以用反射方式解决。

## 0x02 临时patch

（1）在源码中添加以下类

    
    
    import org.apache.shiro.mgt.SecurityManager;
    import org.apache.shiro.spring.web.ShiroFilterFactoryBean;
    import org.apache.shiro.web.filter.mgt.FilterChainManager;
    import org.apache.shiro.web.filter.mgt.FilterChainResolver;
    import org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver;
    import org.apache.shiro.web.mgt.WebSecurityManager;
    import org.apache.shiro.web.servlet.AbstractShiroFilter;
    import org.springframework.beans.factory.BeanInitializationException;
    
    import javax.servlet.FilterChain;
    import javax.servlet.ServletException;
    import javax.servlet.ServletRequest;
    import javax.servlet.ServletResponse;
    import javax.servlet.http.Cookie;
    import javax.servlet.http.HttpServletRequest;
    import java.io.IOException;
    import java.lang.reflect.Field;
    
    /**
     * @author: Venscor
     * @date: 2019/11/14
     * @description
     */
    public class SafeShiroFilterFactoryBean extends ShiroFilterFactoryBean {
        @Override
        protected AbstractShiroFilter createInstance() throws Exception {
            SecurityManager securityManager = getSecurityManager();
            if (securityManager == null) {
                String msg = "SecurityManager property must be set.";
                throw new BeanInitializationException(msg);
            }
    
            if (!(securityManager instanceof WebSecurityManager)) {
                String msg = "The security manager does not implement the WebSecurityManager interface.";
                throw new BeanInitializationException(msg);
            }
    
            FilterChainManager manager = createFilterChainManager();
    
            //Expose the constructed FilterChainManager by first wrapping it in a
            // FilterChainResolver implementation. The AbstractShiroFilter implementations
            // do not know about FilterChainManagers - only resolvers:
            PathMatchingFilterChainResolver chainResolver = new PathMatchingFilterChainResolver();
            chainResolver.setFilterChainManager(manager);
    
            //Now create a concrete ShiroFilter instance and apply the acquired SecurityManager and built
            //FilterChainResolver.  It doesn't matter that the instance is an anonymous inner class
            //here - we're just using it because it is a concrete AbstractShiroFilter instance that accepts
            //injection of the SecurityManager and FilterChainResolver:
            return new SafeShiroFilterFactoryBean.SpringShiroFilter((WebSecurityManager) securityManager, chainResolver);
        }
    
        private static final class SpringShiroFilter extends AbstractShiroFilter {
            protected SpringShiroFilter(WebSecurityManager webSecurityManager, FilterChainResolver resolver) {
                if (webSecurityManager == null) {
                    throw new IllegalArgumentException("WebSecurityManager property cannot be null.");
                } else {
                    this.setSecurityManager(webSecurityManager);
                    if (resolver != null) {
                        this.setFilterChainResolver(resolver);
                    }
    
                }
            }
    
            @Override
            protected void doFilterInternal(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain chain) throws ServletException, IOException {
                HttpServletRequest request = (HttpServletRequest) servletRequest;
                Cookie[] cookies = request.getCookies();
                boolean needResetCookie = false;
                if (cookies != null && cookies.length > 0) {
                    for (Cookie cookie : cookies) {
                        if (cookie.getName().equalsIgnoreCase("rememberMe")) {
                            cookie.setValue("");
                            needResetCookie = true;
                            break;
                        }
                    }
                }
                if (needResetCookie) {
                    Object innerReq = getField(request, "request");
                    setField(innerReq, "cookies", cookies);
                    setField(request, "request", innerReq);
                }
    
                super.doFilterInternal(servletRequest, servletResponse, chain);
            }
    
            public void setField(Object instance, String fieldName, Object fieldValue) {
                try {
                    Field field = instance.getClass().getDeclaredField(fieldName);
                    field.setAccessible(true);
                    field.set(instance, fieldValue);
                } catch (Exception e) {
                    throw new RuntimeException();
                }
            }
    
            public static Object getField(Object instance, String fieldName) {
                try {
                    Field field = instance.getClass().getDeclaredField(fieldName);
                    field.setAccessible(true);
                    return field.get(instance);
                } catch (Exception e) {
                    throw new RuntimeException();
                }
            }
        }
    
    }
    

（2）替换原始的ShiroFilter Bean

SpringMVC中配置示例：

    
    
    <filter>
            <!--filter 配置-->
            <filter-name>shiroFilter</filter-name>
            <filter-class>org.springframework.web.filter.DelegatingFilterProxy</filter-class>
            <init-param>
                <param-name>targetFilterLifecycle</param-name>
                <param-value>true</param-value>
            </init-param>
    </filter>
    
    <!--替换原始的Shiro Bean配置-->
    <bean id="shiroFilter" class="[包名].SafeShiroFilterFactoryBean">
        <!--中间的配置不需要做任何改变-->
    </bean>

SpringBoot配置示例：在原来配置Shiro的Config类中修改

    
    
    @Bean(name = "shiroFilter")
    //返回值修改：ShiroFilterFactoryBean改为SafeShiroFilterFactoryBean
    public SafeShiroFilterFactoryBean getShiroFilterFactoryBean(DefaultWebSecurityManager securityManager,
                                                            CasFilter casFilter) {
        //这个地方改成SafeShiroFilterFactoryBean
        //ShiroFilterFactoryBean shiroFilterFactoryBean = new ShiroFilterFactoryBean(); // 这个地方替换掉
        SafeShiroFilterFactoryBean shiroFilterFactoryBean = new SafeShiroFilterFactoryBean(); // 这个地方替换掉
        shiroFilterFactoryBean.setSecurityManager(securityManager);
        String loginUrl = cas.getServerUrlPrefix() + "/login?service=" + cas.getClientHostUrl() + cas.getCasFilterUrlPattern();
        shiroFilterFactoryBean.setLoginUrl(loginUrl);
        shiroFilterFactoryBean.setSuccessUrl("/");
        // 未授权 url
        shiroFilterFactoryBean.setUnauthorizedUrl(markProperties.getShiro().getUnauthorizedUrl());
        Map<String, Filter> filters = new HashMap<>();
        filters.put("casFilter", casFilter);
        LogoutFilter logoutFilter = new LogoutFilter();
        logoutFilter.setRedirectUrl(cas.getServerUrlPrefix() + "/logout?");
        filters.put("logout", logoutFilter);
        shiroFilterFactoryBean.setFilters(filters);
    
        loadShiroFilterChain(shiroFilterFactoryBean);
        return shiroFilterFactoryBean;
    }
    

## 0x03 写在最后

Shiro还有其他配置方式，可以类似处理。笔者水平有限，如果不当之处，还望不吝指正。

