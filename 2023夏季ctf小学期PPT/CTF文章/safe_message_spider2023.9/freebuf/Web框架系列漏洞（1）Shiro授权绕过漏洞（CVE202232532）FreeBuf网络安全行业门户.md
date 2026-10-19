# 漏洞介绍

和`Spring
Security`的[CVE-2022-22978](https://tanzu.vmware.com/security/cve-2022-22978)思路相同，通过`java`的正则缺陷绕过授权模块。  
此漏洞利用条件较为苛刻，且只能针对`shiro`的身份验证，无法绕过后端程序中的其他验证。

## 影响版本

Apache shiro < 1.9.1

# 基本原理

在`Java`中的正则默认情况下`.`并不包含`\r`和`\n`字符，因此某些情况下正则规则可以被绕过

    
    
    String regex = "a.*b";
    Pattern pattern = Pattern.compile(regex);
    boolean flag1 = pattern.matcher("aaabbb").matches();
    // true
    System.out.println(flag1);
    boolean flag2 = pattern.matcher("aa\nbb").matches();
    // false
    System.out.println(flag2);
    

# 漏洞复现

vulfocus镜像：vulfocus/shiro-CVE-2022-32532  
github地址：[Lay0us1/CVE-2022-32532](https://github.com/Lay0us1/CVE-2022-32532)

利用场景：

  * 配置了`/permit/{value}`这样从路径取参数的路由

  * 配置了`/permit/*`这样的通配路由

思路：`/permit/any`的目录访问需要token，根据漏洞原理在其中加入`\n`或`\r`的url编码字段`%0a`或`%0d`即可绕过shiro的鉴权

POC：`/permit/any%0d`

![image.png](https://image.3001.net/images/20221118/1668769098_6377654a7dc8012ce37f4.png!small)  
![image.png](https://image.3001.net/images/20221118/1668769108_6377655414a09a11b6ab6.png!small)

# 漏洞分析

`shiro`的`RegExPatternMatcher`存在正则绕过安全风险

    
    
    public class RegExPatternMatcher implements PatternMatcher {
        // ...
        public boolean matches(String pattern, String source) {
            if (pattern == null) {
                throw new IllegalArgumentException("pattern argument cannot be null.");
            }
            // no DOTALL flag
            Pattern p = Pattern.compile(pattern);
            Matcher m = p.matcher(source);
            return m.matches();
        }
    }
    

`RegExPatternMatcher`是`shiro`向开发者提供的一个`Matcher`实现，在整个`shiro`项目中都没有出现，需要用户自行配置  
![image.png](https://image.3001.net/images/20221118/1668769120_63776560ad95f783a43ba.png!small)

> 具体继承实现看参考链接

自行配置`Filter`使用`RegExPatternMatcher`的例子

    
    
    @Override
    protected AbstractShiroFilter createInstance() {
        SecurityManager securityManager = this.getSecurityManager();
        FilterChainManager manager = new DefaultFilterChainManager();
        manager.addFilter("myFilter",new MyFilter());
        // my filter
        manager.addToChain("/permit/.*", "myFilter");
        // todo: add other filters
    
        PathMatchingFilterChainResolver chainResolver = new PathMatchingFilterChainResolver();
        chainResolver.setFilterChainManager(manager);
        // set RegExPatternMatcher
        chainResolver.setPathMatcher(new RegExPatternMatcher());
        return new SpringShiroFilter((WebSecurityManager) securityManager, chainResolver);
    }
    
    
    
    public MyPermissionsAuthorizationFilter(boolean regexExp) {
        super();
        this.regexExpMatcher = regexExp;
        if (regexExp) {
            pathMatcher = new RegExPatternMatcher();
        }
    }
    protected boolean pathsMatch(String pattern, ServletRequest request) {
        String requestURI = getPathWithinApplication(request);
        if (request instanceof HttpServletRequest) {
            String queryString = ((HttpServletRequest) request).getQueryString();
            if (regexExpMatcher && !(queryString == null || queryString.length() == 0))
                requestURI += ("?" + queryString);
        }
        String regex = pattern;
        if (regexExpMatcher)
            regex = MyPathMatchingFilterChainResolver.replacePattern(pattern);
        return pathsMatch(regex, requestURI);
    }
    

# 漏洞总结

## 利用条件

shiro版本处于1.9.1以下  
 **目标配置了`RegExPatternMatcher`情况下且正则规则中包含了“.”则存在漏洞**

## DREAD评估

3(D)，3(R)，2(E)，1(A)，0(D)  
评估为 **中危** 漏洞

# 修复方案

  1. 升级到shiro 1.9.1版本及以上

  2. 使用`DOTALL`属性

    
    
    String regex = "a.*b";
    // add DOTALL flag
    Pattern pattern = Pattern.compile(regex,Pattern.DOTALL);
    boolean flag1 = pattern.matcher("aaabbb").matches();
    // true
    System.out.println(flag1);
    boolean flag2 = pattern.matcher("aa\nbb").matches();
    // true
    System.out.println(flag2);
    

# 参考链接

> [浅谈Shiro CVE-2022-32532--先知/4ra1n](https://xz.aliyun.com/t/11501#toc-0)  
> [Lay0us1/CVE-2022-32532](https://github.com/Lay0us1/CVE-2022-32532)  
> [NVD-CVE-2022-32532 Detail](https://nvd.nist.gov/vuln/detail/CVE-2022-32532)

