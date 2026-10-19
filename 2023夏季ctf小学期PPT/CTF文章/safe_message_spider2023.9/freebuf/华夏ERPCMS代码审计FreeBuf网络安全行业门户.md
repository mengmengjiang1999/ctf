# 环境搭建

<https://github.com/jishenghua/jshERP/releases/tag/2.3>

创建数据库jsh_erp，导入sql文件

![](https://image.3001.net/images/20230630/1688107190_649e78b61c6395802db22.png!small)

修改数据库连接密码

![](https://image.3001.net/images/20230630/1688107203_649e78c3893278bd7bbad.png!small)

# 代码审计

首先，整个CMS是用Springboot加上静态的html开发的，数据库方面采用了mybatis的框架开发，其次看pom文件，fastjson的依赖是1.2.55，存在相应的漏洞

![](https://image.3001.net/images/20230630/1688107212_649e78ccd58be20a1bb10.png!small)

除此之外，还专门配置了一个filter，我们应该先来看看filter里面的逻辑

    
    
    package com.jsh.erp.filter;  
    ​  
    import org.springframework.util.StringUtils;  
    import javax.servlet.*;  
    import javax.servlet.annotation.WebFilter;  
    import javax.servlet.annotation.WebInitParam;  
    import javax.servlet.http.HttpServletRequest;  
    import javax.servlet.http.HttpServletResponse;  
    import java.io.IOException;  
    import java.util.ArrayList;  
    import java.util.List;  
    import java.util.regex.Matcher;  
    import java.util.regex.Pattern;  
    ​  
    @WebFilter(filterName = "LogCostFilter", urlPatterns = {"/*"},  
    initParams = {@WebInitParam(name = "ignoredUrl", value = ".css#.js#.jpg#.png#.gif#.ico"),  
    @WebInitParam(name = "filterPath",  
    value = "/user/login#/user/registerUser#/v2/api-docs")})  
    public class LogCostFilter implements Filter {  
    ​  
    private static final String FILTER_PATH = "filterPath";  
    private static final String IGNORED_PATH = "ignoredUrl";  
    ​  
    private static final List<String> ignoredList = new ArrayList<>();  
    private String[] allowUrls;  
    private String[] ignoredUrls;  
    ​  
    @Override  
    public void init(FilterConfig filterConfig) throws ServletException {  
    String filterPath = filterConfig.getInitParameter(FILTER_PATH);  
    if (!StringUtils.isEmpty(filterPath)) {  
    allowUrls = filterPath.contains("#") ? filterPath.split("#") : new String[]{filterPath};  
    }  
    ​  
    String ignoredPath = filterConfig.getInitParameter(IGNORED_PATH);  
    if (!StringUtils.isEmpty(ignoredPath)) {  
    ignoredUrls = ignoredPath.contains("#") ? ignoredPath.split("#") : new String[]{ignoredPath};  
    for (String ignoredUrl : ignoredUrls) {  
    ignoredList.add(ignoredUrl);  
    }  
    }  
    }  
    @Override  
    public void doFilter(ServletRequest request, ServletResponse response,  
    FilterChain chain) throws IOException, ServletException {  
    HttpServletRequest servletRequest = (HttpServletRequest) request;  
    HttpServletResponse servletResponse = (HttpServletResponse) response;  
    String requestUrl = servletRequest.getRequestURI();  
    //具体，比如：处理若用户未登录，则跳转到登录页  
    Object userInfo = servletRequest.getSession().getAttribute("user");  
    if(userInfo!=null) { //如果已登录，不阻止  
    chain.doFilter(request, response);  
    return;  
    }  
    if (requestUrl != null && (requestUrl.contains("/doc.html") ||  
    requestUrl.contains("/register.html") || requestUrl.contains("/login.html"))) {  
    chain.doFilter(request, response);  
    return;  
    }  
    if (verify(ignoredList, requestUrl)) {  
    chain.doFilter(servletRequest, response);  
    return;  
    }  
    if (null != allowUrls && allowUrls.length > 0) {  
    for (String url : allowUrls) {  
    if (requestUrl.startsWith(url)) {  
    chain.doFilter(request, response);  
    return;  
    }  
    }  
    }  
    servletResponse.sendRedirect("/login.html");  
    }  
    ​  
    private static String regexPrefix = "^.*";  
    private static String regexSuffix = ".*$";  
    ​  
    private static boolean verify(List<String> ignoredList, String url) {  
    for (String regex : ignoredList) {  
    Pattern pattern = Pattern.compile(regexPrefix + regex + regexSuffix);  
    Matcher matcher = pattern.matcher(url);  
    if (matcher.matches()) {  
    return true;  
    }  
    }  
    return false;  
    }  
    @Override  
    public void destroy() {  
    ​  
    }  
    }

这个filter是全局的，其次对于.css#.js#.jpg#.png#.gif#.ico和/user/login#/user/registerUser#/v2/api-docs等资源进行请求时不拦截（#是分隔符）

dofilter是具体的实现

    
    
    if(userInfo!=null) { //如果已登录，不阻止  
    chain.doFilter(request, response);  
    return;  
    }  
    if (requestUrl != null && (requestUrl.contains("/doc.html") ||  
    requestUrl.contains("/register.html") || requestUrl.contains("/login.html"))) {  
    chain.doFilter(request, response);  
    return;  
    }  
    if (verify(ignoredList, requestUrl)) {  
    chain.doFilter(servletRequest, response);  
    return;  
    }  
    if (null != allowUrls && allowUrls.length > 0) {  
    for (String url : allowUrls) {  
    if (requestUrl.startsWith(url)) {  
    chain.doFilter(request, response);  
    return;  
    }  
    }  
    }

如果登陆了会得到一个session，从session中取出的user字段，如果不为空，则代表已登陆，不拦截，继续调用下一个doFilter

如果未登陆，会判断url中是否含有doc.html，register.html，login.html，不拦截

ignoredList是css，js等字符串列表，通过正则表达式判断是否存在url中，如果存在则不拦截

    
    
    private static boolean verify(List<String> ignoredList, String url) {  
    for (String regex : ignoredList) {  
    Pattern pattern = Pattern.compile(regexPrefix + regex + regexSuffix);  
    Matcher matcher = pattern.matcher(url);  
    if (matcher.matches()) {  
    return true;  
    }  
    }  
    return false;  
    }

最后一个if，allowUrls是/user/login等url，判断url是否以这些开头，如果是则不拦截

如果这四个if都没进去，则重定向到login.html

读完这个filter我们可以明确几点：

  * 某些url是不会拦截的

  * 判断/user/login是通过开头来判断的，可能可以通过目录穿越符来欺骗，如`/user/login/../../`

  * 并没有对传入的参数处理的filter，对与sql注入和xss的恶意字符没有判断

读完了基本的pom和filter，接下来我们结合黑白盒来审计

## SQL注入

整个CMS用的是mybatis的框架，我们知道mybatis用#{}的方法传入参数是自动开启预编译的，但是用${}却不行，然后整个sql语句可以用注解或者写到xml文件里面去，这个cms的xml文件写到的是resource/mapper_xml下的，里面定义的sql语句

我们可以在这个文件夹全局搜索${}看有没有用${}传参的地方，不知道是开发炫技还是不同人协同开发的原因，里面有#{}也有${}

![](https://image.3001.net/images/20230630/1688107235_649e78e39b046d08319a0.png!small)![](https://image.3001.net/images/20230630/1688107244_649e78ecb6cf9d1bdb13d.png!small)

随便找到，一个，我们看到这里的`selectByConditionUser`，全局搜索找到定义的地方

![](https://image.3001.net/images/20230630/1688107280_649e7910c13a71a08a3b2.png!small)

向上走看调用的地方，在UserService.java

![](https://image.3001.net/images/20230630/1688107289_649e79191a35bb6769f09.png!small)

传入的userName等没做处理直接调用，继续向上走，找到UserComponent类的getUserList

![](https://image.3001.net/images/20230630/1688107297_649e7921b2c02fb0db9bd.png!small)

这里涉及到了userName和loginName的获取，是从一个map里面取出来的

![](https://image.3001.net/images/20230630/1688107305_649e7929056b07057b6c2.png!small)

看到是通过fastjson获取的，这里应该是一个json格式传入的参数`{"userName":"","loginName":""}`

我们找到关于参数获取的地方，接下来需要继续去找前端接口看能不能控制，向上走找到调用getUserList的地方

![](https://image.3001.net/images/20230630/1688107312_649e79300391f0ef09b4f.png!small)

继续找select

![](https://image.3001.net/images/20230630/1688107322_649e793a0c57c9adb9e56.png!small)

这里为什么可以调用到这里呢？

UserComponent实现了ICommonQuery接口

![](https://image.3001.net/images/20230630/1688107331_649e7943481f540ea9e14.png!small)

其实是调用到ICommonQuery接口的select方法

我们看刚才CommonQueryManager的select方法，通过apiName调用的container的getCommonQuery

![](https://image.3001.net/images/20230630/1688107340_649e794c5fcb97fba822d.png!small)

返回的是一个ICommonQuery类型的值

这里的先调用初始化init方法，遍历service下的组件（每个文件夹下的component类）压入configComponentMap中

![](https://image.3001.net/images/20230630/1688107347_649e7953e45ea050e065b.png!small)

后续调用getCommonQuery方法根据传进来的apiName获取对应的service组件（具体apiName跟对应的service组件映射如下：user->UserComponent）

![](https://image.3001.net/images/20230630/1688107356_649e795cb143b92f2443d.png!small)

即service下每个文件夹对应一个apiName

所以这里要调用UserComponent的select方法的话需要apiName为user

    
    
    return container.getCommonQuery(apiName).select(parameterMap);

继续往上，来到了ResourceController，终于找到了接口，由刚才的分析可以知道我们的apiName应该是user

![](https://image.3001.net/images/20230630/1688107377_649e797170288814dae9f.png!small)

所以访问的路由应该是user/list

这里接受了三个参数，pageSize，currentPage，search

![](https://image.3001.net/images/20230630/1688107385_649e79797fc5f2319bb03.png!small)

把search压入了parameterMap

然后传入了CommonQueryManager的select方法，整个过程没有任何过滤，然后刚才的分析可以知道，search应该为json格式的参数

    
    
    /user/list?search=%7b%22userName%22%3a%22%22%2c%22loginName%22%3a%22jsh'%20and%20sleep(3)--%2b%22%7d&ampcurrentPage=1&pageSize=10

  

![](https://image.3001.net/images/20230630/1688107397_649e798568d12b43d583c.png!small)可以看到sleep已经起作用了

![](https://image.3001.net/images/20230630/1688107409_649e7991006c74f33a9d8.png!small)

看到sql语句也拼接了，但是不知道为什么，睡眠时间是sleep的3倍

![](https://image.3001.net/images/20230630/1688107434_649e79aa3804ce3a8bb2f.png!small)

当然sql注入的地方不止这一个点，其他的思路大概也是这样的

## Fastjson

之前提到过，fastjson用的是1.2.55，这个版本存在漏洞，刚才看解析参数的时候用的是`JSONObject.parseObject`

![](https://image.3001.net/images/20230630/1688107443_649e79b3176538cbaf80e.png!small)

我们从/user/list的search打入一个fastjson的payload看看效果

![](https://image.3001.net/images/20230630/1688107456_649e79c032265da10c2df.png!small)![](https://image.3001.net/images/20230630/1688107468_649e79cc2ce0d13a38770.png!small)

收到啦dns请求，但是我看fastjson1.2.55虽然存在漏洞，但是基本上需要开启checkautoType，不过也有一些不需要autoType的

[GitHub - safe6Sec/Fastjson:
Fastjson姿势技巧集合](https://github.com/safe6Sec/Fastjson)

但是还是要依赖其他库

## 权限绕过

![](https://image.3001.net/images/20230630/1688107485_649e79dd00f123e2cf404.png!small)

在filter中定义了，url中包括了什么或者以什么开头的时候就不会拦截，但是并没有过于目录穿越符等

所以我们构造如下payload就能访问到其他资源

![](https://image.3001.net/images/20230630/1688107497_649e79e92ae9ed95b43e2.png!small)

但是得在burp里面才行

![](https://image.3001.net/images/20230630/1688107509_649e79f53eeb5f21f75c7.png!small)

这样就可以去访问任意接口拿到数据了

![](https://image.3001.net/images/20230630/1688107528_649e7a0844d355580249c.png!small)

最紧急的防御方式还是过滤掉目录穿越符，这两个白名单的地方都可以通过正则匹配的方式去过滤掉目录穿越符

## 存储型xss

之前提到过并没有对参数进行处理，随便找一个可以增加数据的地方看看有没有xss

![](https://image.3001.net/images/20230630/1688107540_649e7a14144f593e98534.png!small)![](https://image.3001.net/images/20230630/1688107553_649e7a21c8fda681d543a.png!small)

  

定位到路由/role/add

![](https://image.3001.net/images/20230630/1688107562_649e7a2acf326a829bf7c.png!small)

最终定位到了insertSelective方法定义的sql语句，虽然采用了预编译的方式，但是没有对参数进行过滤，就会对xss标签存储

但是这里的sql语句用的是#{}

因为这里增加的时候，对于账号需要JsesssionID，不然插入的时候找不到tenant_id导致最后不知道插入到哪里去啦

![](https://image.3001.net/images/20230630/1688107575_649e7a3793c506ab553b1.png!small)![](https://image.3001.net/images/20230630/1688107585_649e7a4133de8e6a45da1.png!small)

## 越权重置密码

![](https://image.3001.net/images/20230630/1688107605_649e7a55ea52a1c361cf5.png!small)

编辑的时候重置密码，抓包

![](https://image.3001.net/images/20230630/1688107626_649e7a6ab02752fa6f448.png!small)

通过id去重置密码，这里我们看到了这个id，可以登陆另外一个账户重置密码，修改id达到越权修改，因为这里是通过id判断账户的，所以，我们也可以结合之前的未授权来达到重置任意用户密码

![](https://image.3001.net/images/20230630/1688107643_649e7a7b6839b559e1bce.png!small)

定位路由/user/resetPwd，在UserController中

![](https://image.3001.net/images/20230630/1688107656_649e7a881af32d3c4af2c.png!small)

获取一个id参数，给定重置的密码为123456，把md5和id一起传入resetPwd

![](https://image.3001.net/images/20230630/1688107665_649e7a9160ed342e9f9bb.png!small)

通过id从数据库里面取出User，这里只有一个判断，就是loginName不为admin，对于其他用户没有判断，然后直接调用setter方法重置password，然后更新数据库

所以说我们这里只需要能够访问到这个路由，然后传入对应账户的id参数即可，可以遍历id

越权漏洞当然不只这一个，还有越权删除和修改用户信息的，这里都是通过id判断，就不再复现了

## 信息泄漏

华夏erp cms写了一个全局的filter用于身份验证

![](https://image.3001.net/images/20230630/1688107678_649e7a9e66f41d51d7d27.png!small)![](https://image.3001.net/images/20230630/1688107686_649e7aa6e0e271769b38e.png!small)

  

对于所有的url进行的判断是通过contains来实现的，如果包含doc.html，register.html，login.html等页面，不拦截，

![](https://image.3001.net/images/20230630/1688107699_649e7ab366f51780d59f5.png!small)

而verify函数也是通过pattern.match匹配的字符串

这也就成了绕过的关键，在spring中，我们用分号分割URL后，仍然可以进入到对应的controller

![](https://image.3001.net/images/20230630/1688107708_649e7abcca6de05d1daf1.png!small)

这样就能访问到对应的/user/hahaha路由，因此，就可以对erp中的路由进行身份绕过

![](https://image.3001.net/images/20230630/1688107716_649e7ac45fbc1f967efee.png!small)

payload：

    
    
    /user/getAllList;.js

分割符后面只要是ignoredUrl里面允许的后缀均可

# CodeQL

    
    
    codeql database create erpcms_demo  --language="java"  --command="mvn clean package -DskipTests" --source-root=/Users/DawnT0wn/代码审计/jshERP-2.3

## source

对于source点，这个CMS的传参全部写到了Controller里面的，所以对于传参我们可以先不看，明白了都是Controller下的方法获得参数，所以我们就把Controller下的所有方法作为我们的source点

    
    
    class AllControllerMethod extends Callable {  
    AllControllerMethod() {  
    exists(RefType i |  
    i.getName()  
    .substring(i.getName().indexOf("Controller"), i.getName().indexOf("Controller") + 10) =  
    "Controller" and  
    this = i.getACallable()  
    )  
    }  
    }

## SQL注入

对于sql注入，这个cms是通过mybatis作为数据库框架，我们还是要去找${}传参的地方

对于全局的codeql搜索，还没有想到很好的方法，不过，我们可以全局搜索${}的地方，来找到通过${}传参的sql方法

![](https://image.3001.net/images/20230630/1688107728_649e7ad0aa803fc3bdebe.png!small)

然后再通过codeql查找有没有到这里的一条链子

    
    
    /**  
    * @kind path-problem  
    */  
    import java  
    ​  
    class AllControllerMethod extends Callable {  
    AllControllerMethod() {  
    exists(RefType i |  
    i.getName()  
    .substring(i.getName().indexOf("Controller"), i.getName().indexOf("Controller") + 10) =  
    "Controller" and  
    this = i.getACallable()  
    )  
    }  
    }  
    ​  
    class SqlMethod extends Call{  
    SqlMethod(){  
    this.getCallee().hasName("selectByConditionUser") or  
    this.getCallee().hasName("selectByConditionUnit") or  
    this.getCallee().hasName("countsByUnit") or  
    this.getCallee().hasName("Example_Where_Clause")  
    }  
    }  
    ​  
    query predicate edges(Callable a, Callable b) { a.polyCalls(b) }  
    ​  
    from AllControllerMethod start, SqlMethod end, Callable c  
    where edges+(start, c)  
    select end.getCaller(), start, end.getCaller(), "jndi"

个人还是更喜欢edges谓词的方式找调用方法，而不是污点追踪参数，当然，污点追踪的话，对参数来说，会更明显

![](https://image.3001.net/images/20230630/1688107740_649e7adcd45646ee5cb91.png!small)

这就是我们上面分析的sql注入的点

另外的注入点

![](https://image.3001.net/images/20230630/1688107750_649e7ae602b5fae28898e.png!small)

也是成功的

## FastJson

虽然这里fastjson存在漏洞，利用性不高，但是我们可以来看看怎么去找到解析可控json的点

    
    
    /**  
    * @kind path-problem  
    */  
    import java  
    ​  
    class AllControllerMethod extends Callable {  
    AllControllerMethod() {  
    exists(RefType i |  
    i.getName()  
    .substring(i.getName().indexOf("Controller"), i.getName().indexOf("Controller") + 10) =  
    "Controller" and  
    this = i.getACallable()  
    )  
    }  
    }  
    ​  
    // class SqlMethod extends Call{  
    //     SqlMethod(){  
    //         this.getCallee().hasName("selectByConditionUser") or  
    //         this.getCallee().hasName("selectByConditionUnit") or  
    //         this.getCallee().hasName("countsByUnit") or  
    //         this.getCallee().hasName("Example_Where_Clause")  
    //     }  
    // }  
    ​  
    class FastJsonMethod extends Call{  
    FastJsonMethod(){  
    (this.getCallee().hasName("parse") or  
    this.getCallee().hasName("parseObject")) and  
    (this.getCallee().getDeclaringType().getASupertype*().hasQualifiedName("com.alibaba.fastjson","JSONObject") or  
    this.getCallee().getDeclaringType().getASupertype*().hasQualifiedName("com.alibaba.fastjson","JSON"))  
    }  
    }  
    ​  
    query predicate edges(Callable a, Callable b) { a.polyCalls(b) }  
    ​  
    from AllControllerMethod start, FastJsonMethod end, Callable c  
    where edges+(start, c)  
    select end.getCaller(), start, end.getCaller(), "jndi"

还是找到了很多

# 写在最后

这次的审计大概就到这里吧，对于一些文件操作类型的，基本上也只有两个导出excel的点，没什么其他地方，然后对于整个后台基本上功能点都很类似，都只能去测一点csrf和xss，以及sql，看晚上说还有信息泄漏，虽然是扫到的/v2/api-docs，但是还是要登陆才行，应该也算吧。

参考链接

<https://blog.csdn.net/Ananas_Orangey/article/details/120340010>

<https://www.freebuf.com/articles/web/347135.html>

<https://www.cnblogs.com/bmjoker/p/14856437.html>

