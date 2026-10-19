***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：TopScrew，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x01 前言

**前几天刚见人发了[一个登录框引发的血案](http://www.freebuf.com/web/174408.html)，而常规的爆破有风控和各种变态验证码，或者大型的电商都会用SSO实现登录，密码找回逻辑看似天衣无缝，又或者采用第三方的Oauth授权。往往这些常规的东西已经被人测了千万遍。怎么才能另寻奇辟，找寻新的大陆呢？分享一次SRC挖掘过程中，遇到一堆的登录框。通过对目录的fuzz发现了一些不正常的特征。通过这些不正常特性引发的思考（胡思乱想）和正确的防护措施。
**

## 0x02特征的发现

既然是登录的客户端欺骗方式，那么先请出我们的主角登录框！

![](https://image.3001.net/images/20180627/15300704801941.png!small)通过Fuzz后台目录，发现了一个神奇的现象，返回的状态码都为200。而且返回的Size不同说明了返回了不同的页面。

![](https://image.3001.net/images/20180627/15300704937125.png!small)当我对/system/user/index/页面进行访问时，又被弹到了首页。但是我的状态码明明是200呀。且还是Size不同的数据！从我的第六感来说，此处肯定存在猫腻。

## 0x03正常的场景

按照我以往的渗透经验,出现的应该是如下场景：

![](https://image.3001.net/images/20180627/15300705216213.png!small)

1\. 首先客户端向服务端发起一次请求。

2\. 进入服务端的全局过滤器，判断是否有权限对该url资源进行访问。

3\. 如果权限不够：

> 1) 状态码200，返回统一的错误友好界面。
>
> 2) 状态码302，直接跳转至登录页面。
>
> 3) 状态码403，提示没有权限
>
> 4) 状态码500，抛出越权异常

4\. 权限够的话，继续执行。访问后端的业务接口。

## 0x04结合分析

看似好像上面聊到的200的状态码是个正常现象，但是仔细一分析有很多矛盾的地方。

> 1\. 返回的状态码是200，但是每一次的访问跳到了登录页面。
>
> 2\. 返回的状态码是200，但是每个越权的url虽然都返回到了主页。但是Response 的Size都不相同。

由此可以猜想目前的流程：

![](https://image.3001.net/images/20180627/15300705422678.png!small)

> 1\. Client发起一次请求
>
> 2\. 请求直接被Server Interface接受，返回响应内容给Client.
>
> 3\. 浏览器再拿上Reponse去解析。（鉴权过程发生此处）
>
> 4\. 鉴权获取Cookie中的一些Flag,有则继续无则跳转登录页面。

## 0x05 脆弱点

1\.
从分析来看，没有正确实现全局的拦截器，而是依赖前端做权限判断。也就是说我们直接向业务接口post数据，业务接口就会拿上数据去调用其中的一些方法，只要想办法拿到接口的url和参数名即可。（获得一些增删改的垂直权限）

2\. 鉴权在前端利用JS去获取Cookie的一些Flag.大家都明白，前端的一切可更改。（此时的防护，已经晚了）

## 0x06 拉个实际的例子。

案例一：

![](https://image.3001.net/images/20180627/15300705598320.png!small)1）为了方便就不FUZZ了，直接F12看他的源码

![](https://image.3001.net/images/20180627/15300705727725.png!small)

2）发现前端js中使用的Ajax异步的方式访问后端接口去登陆。如果返回的json的data字段为success就跳转至Default.aspx。很明显可以猜到这就是后台的首页了。

3）尝试访问，不出意外的又回到了登录页面。但是他的response的状态码为200.且Size并不和登录页面的Size的大小一样。情况奇特抓包分析。

4）抓包分析，当请求这个页面时会返回一个html源码。发现了他跳去首页的原因。

![](https://image.3001.net/images/20180627/15300774606406.png!small)

5）还发现他的RoleID和 一些区域名都是通过JS来获取的。前端的一切都是扯淡。我们是不是可以直接篡改了呢？

![](https://image.3001.net/images/20180627/15300774767681.png!small)

案例二（截胡式）：

1）直接越权访问，会返回一个html源码。经过鉴权处理后，他的处理方式只是仅仅加了location.href。来进行首页的跳转。

![](https://image.3001.net/images/20180627/15300775042676.png!small)2）你想跳的话，就不让你跳。直接将其删除。在此我们就得到的接口的url和一些参数。

![](https://image.3001.net/images/20180627/15300775287531.png!small)3）既然他们返回状态200，并没有出现403等阻断行为，且Size不同。说明个站的业务接口你是可以直接触碰。很显然查出了所有的信息，可做增删改的操作。

## ![](https://image.3001.net/images/20180627/15300775414096.png!small)

案例三：

其实每个程序员写的代码都是千变万化，在此只简单的介绍两个案例。具体的环境还要根据具体的代码去调整。在此就不做过多的展示，只要抓住了思想，其实漏洞基本就已将摆出来了。聊了这么久的攻击思路下来聊聊防御。

##  
0x07如何做一个安全基于角色的权限控制呢

作为一个白帽子安全人员来说，当你发现漏洞后，交给客户安全建议是必不可少。怎样做一个非天马行空而是一个可落地的解决方案呢？

1）因为对java稍微熟悉那么一点点 ，就用java做一个简单的小例子。

项目结构

![](https://image.3001.net/images/20180627/15300787484415.png!small)

2）权限配置文件

路径中含有 admin 的需要管理员权限才可以访问

路径中含有 user 的需要 用户或者管理员 权限

路径中含有login的需要游客权限即可访问

![](https://image.3001.net/images/20180627/15300787641652.png!small)

3）过滤器设计

依赖servlet的Filter实现，所以需要先导入Servlet-api.jar

    
    
    package com.screw.util;
    
    import java.io.FileInputStream;
    
    import java.io.IOException;
    
    import java.util.Properties;
    
    import javax.servlet.Filter;
    
    import javax.servlet.FilterChain;
    
    import javax.servlet.FilterConfig;
    
    import javax.servlet.ServletException;
    
    import javax.servlet.ServletRequest;
    
    import javax.servlet.ServletResponse;
    
    import javax.servlet.http.HttpServletRequest;
    
    import javax.servlet.http.HttpServletResponse;
    
    public class PrivilegeFilter implements Filter{
    
    private Properties properties = new Properties();
    
    @Override
    
    public void destroy() {
    
    properties=null;
    
    }
    
    @Override
    
    public void init(FilterConfig filterConfig) throws ServletException {
    
    //获取privilegeFile配置文件的相对路径 ===》 fileName: /WEB-INF/privilege.properties
    
    String fileName=filterConfig.getInitParameter("privilegeFile");
    
    //获取配置文件的绝对路径  realPath: E:\code\Work2018\.metadata\.plugins\org.eclipse.wst.server.core\tmp0\wtpwebapps\AccessControl\WEB-INF\privilege.properties
    
    String realPath = filterConfig.getServletContext().getRealPath(fileName);
    
    try
    
    {
    
    properties.load(new FileInputStream(realPath));
    
    }
    
    catch(Exception e)
    
    {
    
    filterConfig.getServletContext().log("读取权限控制文件失败",e);
    
    }
    
    }
    
    @Override
    
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
    
    throws IOException, ServletException
    
    {
    
    HttpServletRequest request=(HttpServletRequest)req;
    
    HttpServletResponse response=(HttpServletResponse)res;
    
    //获取项目名后的路径  如：admin/index
    
    String requestUri=request.getRequestURI().replace(request.getContextPath()+"/", "");
    
    String role=(String)request.getSession().getAttribute("role");
    
    role=role==null?"guest":role;
    
    boolean authen=false;
    
    //properties.keySet()  配置文件中的key
    
    for(Object obj:properties.keySet())
    
    {
    
    String key=(String)obj;
    
    if(requestUri.indexOf(key)!=-1)
    
    {
    
    //查看对应路径权限是否正确
    
    if(((String) properties.get(key)).indexOf( role)!=-1)
    
    {
    
    authen=true;
    
    break;
    
    }
    
    }
    
    }
    
    if(!authen)
    
    {
    
    throw new RuntimeException("您无权访问该页面。");
    
    }
    
    chain.doFilter(request, response);
    
    }
    
    }

4） 将过滤器加入web.xml配置文件

![](https://image.3001.net/images/20180627/15300788173583.png!small)5
）测试用的Controller

    
    
    package com.screw.controller;
    
    import java.util.Map;
    
    import javax.servlet.http.HttpServletRequest;
    
    import javax.servlet.http.HttpSession;
    
    import org.springframework.stereotype.Controller;
    
    import org.springframework.web.bind.annotation.RequestMapping;
    
    import org.springframework.web.bind.annotation.RequestMethod;
    
    @Controller
    
    public class TestHello {
    
    @RequestMapping(value = "/login" ,method=RequestMethod.GET)
    
    public String login() {
    
    return "login";
    
    }
    
    @RequestMapping(value = "/login" ,method=RequestMethod.POST)
    
    public String login(String username,String passwd,HttpSession session) {
    
    if(username.equals("admin") && passwd.equals("123456")) {
    
    session.setAttribute("role", "admin");
    
    }else if (username.equals("user") && passwd.equals("123456")) {
    
    session.setAttribute("role", "user");
    
    }else {
    
    return "login";
    
    }
    
    return "index";
    
    }
    
    @RequestMapping("/admin/index")
    
    public String admin() {
    
    return "admin";
    
    }
    
    @RequestMapping("/user/add")
    
    public String add() {
    
    return "add";
    
    }
    
    }

6）测试

1-直接访问登录用户才有的编辑权限的地址 user/add

![](https://image.3001.net/images/20180627/15300788484797.png!small)2-访问login
以user的身份登录后，分别访问 user/add 和 admin/index

![](https://image.3001.net/images/20180627/15300788627300.png!small)登录成功

![](https://image.3001.net/images/20180627/15300788723802.png!small)访问用户

![](https://image.3001.net/images/20180627/15300788853009.png!small)访问超管权限

![](https://image.3001.net/images/20180627/15300788948157.png!small)

## 0x07总结

最后基于角色的权限控制的设计，鉴权放在全局拦截器中。也就是在你发其请求后，还有没路由到接口之前。对你的权限进行了判断。所以只要权限不够，甚至都无法fuzz真实的网站路径，更别说越权触碰业务接口了。这次的分享仅仅是我挖SRC过程中的胡思乱想，如果有任何错误，还希望大佬们多多指教。

 ***本文原创作者：TopScrew，本文属FreeBuf原创奖励计划，未经许可禁止转载**

