## 1. **Xss漏洞攻击原理**

Cross Site Script（XSS），跨站脚本攻击。

攻击者利用应用程序的动态展示数据功能，在 html 页面里嵌入恶意代码。当用户浏览该页之时，这些嵌入在
html中的恶意代码会被执行，用户浏览器被攻击者控制，从而达到攻击者的特殊目的。

跨站脚本攻击有三种攻击形式

1、反射型跨站脚本攻击

通过 GET、POST、referer
等参数未加处理直接输出到页面执行。该类型是最为常见的，攻击者主要利用此类型通过email、热度非常大的论坛、或者有针对性的某一用户发送一个隐藏性的链接，让受害者进行点击触发。

2、存储型跨站脚本攻击

由攻击者输入恶意数据保存在数据库，再由服务器脚本程序从数据库中读取数据，然后显示在公共显示的固定页面上，那么所有浏览该页面的用户都会被攻击。该类型攻击性非常大，危险也非常大。

3、DOM 跨站攻击

由于 html 页面中，定义了一段 JS，根据用户的输入，显示一段 html 代码，攻击者可以在输入时，插入一段恶意脚本，最终展示时，会执行恶意脚本。

DOM 跨站和以上两个跨站攻击的差别是，DOM 跨站是纯页面脚本的输出，只有规范使用 JAVASCRIPT，才可以防御。

## 2.Xss攻击路径图

### 2.1. **反射型xss**

攻击方式：攻击者通过电子邮件等方式将包含XSS代码的恶意链接发送给目标用户。当目标用户访问该链接时，服务器接收该目标用户的请求并进行处理，然后服务器把带有XSS代码的数据发送给目标用户的浏览器，浏览器解析这段带有XSS代码的恶意脚本后，就会触发XSS漏洞。

![1688695887_64a7744f430b65dcdf6d2.png!small?1688695886765](https://image.3001.net/images/20230707/1688695887_64a7744f430b65dcdf6d2.png!small?1688695886765)

### 2.2. **存储型Xss**

攻击方式：这种攻击多见于论坛、博客和留言板，攻击者在发帖的过程中，将恶意脚本连同正常信息一起注入帖子的内容中。随着帖子被服务器存储下来，恶意脚本也永久地存放在服务器的后端存储器中。当其他用户浏览这个被注入了恶意脚本的贴子时，恶意脚本会在他们的浏览器中得到执行。

![1688695915_64a7746b6e984dae8806b.png!small?1688695915030](https://image.3001.net/images/20230707/1688695915_64a7746b6e984dae8806b.png!small?1688695915030)

###  **2.3.DOM型xss**

DOM(Document object model)，使用DOM能够使程序和脚本能够动态访问和更新文档的内容、结构和样式。

DOM型XSS其实是一种特殊类型的反射型XSS，它是基于DOM文档对象的一种漏洞。DOM型XSS是基于JS上的。不需要与服务器进行交互。

![1688695945_64a77489e8b1f5caed804.png!small?1688695945592](https://image.3001.net/images/20230707/1688695945_64a77489e8b1f5caed804.png!small?1688695945592)

## 3.Xss审计函数

代码审计需要注意的关键字：代码审计时可以全局搜索以下关键词，追踪参数来源，判断参数是否为用户可控，若为用户可控且未做有效过滤措施，则判定存在问题。

变量输出操作：

Response.write()

sendRedirect 重定向函数

getParameter 获取POST/GET传递的参数值

setAttribute 设置相关属性

getRequestDispatcher(). forward() 请求转发

getRequestDispatcher(). include() 请求包含

可能触发DOM型Xss的触发函数：

document.write(…)

document.writeln(…)

document.body.innerHtml=…

document.forms[0].action=…

document.attachEvent(…)

document.create…(…)

document.execCommand(…)

document.body. …

window.attachEvent(…)

document.location=…

document.location.hostname=…

document.location.replace(…)

##  **4.Xss危害**

1.网络钓鱼，包括获取各类用户账号；

2.窃取用户cookies资料，从而获取用户隐私信息，或利用用户身份进一步对网站执行操作；

3.劫持用户（浏览器）会话 从而执行任意操作，例如非法转账、强制发表日志、电子邮件等；

4.强制弹出广告页面、刷流量等；

5.网页挂马；

6.进行恶意操作，如任意篡改页面信息、删除文章等；

7.进行大量的客户端攻击，如DDoS等；

8.获取客户端信息，如用户的浏览历史、真实IP、开放端口等；

9.控制受害者机器向其他网站发起攻击；

10.结合其他漏洞，如CSRF,实施进一步危害；

11.提升用户权限，包括进一步渗透网站；

12.传播跨站脚本蠕虫等。

## 5. **Xss漏洞代码示例**

###  **5.1.反射型xss代码示例**

下面JSP代码片段的功能是从HTTP请求中读取用户的ID（uid），并将其显示给用户。

<% String uid = request.getParameter("uid"); %>

...

User ID: <%= uid%>  
  
---  
  
如果uid里有攻击者构造的恶意代码，那么浏览器就会执行该代码，应用程序将受到反射型XSS攻击。

### 5.2. **存储型xss代码示例**

下面JSP代码片段的功能是根据一个已知用用户ID（uid）从数据库中查询出该用户的年龄，并显示在JSP页面上。

<%...

Statement stmt = conn.createStatement();

ResultSet rs = stmt.executeQuery("select * from emp where id="+uid);

if (rs != null) {

rs.next();

String age= rs.getString("age");

%>

User age: <%= age%>  
  
---  
  
如果age的值是直接从用户输入的数据中获取的，且存入数据库时没有进行合理的校验，那么攻击者就可以利用上面的代码进行存储型XSS攻击。

###  **5.3.Dom型xss代码示例**

面的JavaScript代码片段可从URL中读取mesg信息，并将其显示给用户。

<script>

var url=document.URL;

document.write(url.substring(url.indexOf("name=")+11,url.length);

</script>  
  
---  
  
该段脚本解析URL，读取name参数的值，并将其写入页面。如果攻击者设计一个恶意的URL，并以JavaScript代码作为name参数，那么Web浏览器就会像显示HTTP响应那样执行该代码，应用程序将受到基于DOM的XSS攻击。

## 6.Xss实战案例-OFCMS XSS漏洞分析

漏洞点：ofcms-api/src/main/java/com/ofsoft/cms/api/v1/CommentApi.java

评论接口代码

public class CommentApi extends ApiBase {

/**

* 获取内容信息

*/

@ApiMapping(method = RequestMethod.GET)

@ParamsCheck(

{@ParamsCheckType(name = "comment_content"), @ParamsCheckType(name =
"content_id"),

@ParamsCheckType(name = "site_id")})

public void save() {

try {

Map params = getParamsMap();

params.put("comment_ip", IpKit.getRealIp(getRequest()));//获取值

Db.update(Db.getSqlPara("cms.comment.save", params));//写入数据库

rendSuccessJson();

} catch (Exception e) {

e.printStackTrace();

rendFailedJson();

}

}  
  
---  
  
通过打断点，发现在params.put获取到用户输入的值，并使用Db.update更新到数据库中，而写入过程中无任何过滤操作。

![1688696465_64a77691ca6af476b93ef.png!small?1688696465042](https://image.3001.net/images/20230707/1688696465_64a77691ca6af476b93ef.png!small?1688696465042)

前端代码

漏洞点：ofcms-admin/src/main/webapp/WEB-INF/page/default/article.html

<!-- 评论-->

<div class="of-crad" style="width: 900px;margin: 0 auto;">

  

<section class="comments">

<h1><span>用户评论</span></h1>

<form class="layui-form">

<textarea name="comment_content" maxlength="8000" required lay-verify="required" placeholder="发表你此时的观点 ……" class="comments-text"
id="comments-text"></textarea>

<div class="plfr1 clearfix">

<div class="down clearfix">

<input type="hidden" name="content_id" value="${params.content_id}">

<input type="hidden" name="site_id" value="${site.site_id}">

<input type="hidden" name="check_status" value="1">

<input type="submit" lay-submit value="提交评论" lay-filter="comment"
class="submit-on">

</div>

</div>

</form>

</section>

<section class="comments-list" style="margin-top:60px;">

<@of.comment site_id=site.site_id content_id=params.content_id limit="10">

<ul>

<#if comment ??>

<#list comment as data >

<li>

<span>评论时间：${data.comment_time} </span><br>

${data.comment_content}</li><!-- 前端也未做过滤等操作 --!>

</#list>

<#else>

<div class="zanwu">暂无相关评论！</div>

</#if>

</ul>

</@of.comment>

</section>

</div>

</div>  
  
---  
  
前端代码中也无过滤代码等其他防护措施，导致XSS漏洞存在。

## 7. **Xss漏洞防御**

###  **7.1.输出编码**

针对跨站脚本攻击，可以采用输出编码方式进行避免，下面是采用OWASP ESAPI对数据输出HTML上下文中不同位置所采用的不同编码方法。

//HTML编码

ESAPI.encoder().encodeForHTML("inputData");

//HTML属性编码

ESAPI.encoder().encodeForHTMLAttribute("inputData ");

//JavaScript编码

ESAPI.encoder().encodeForJavaScript("inputData ");

//CSS 编码

ESAPI.encoder().encodeForCSS(""inputData ");

//URL编码

ESAPI.encoder().encodeForURL("inputData ");  
  
---  
  
### 7.2. **请求头设置**

在给用户设置认证 COOKIE 时，加入
HTTPONLY。httponly无法完全的防御XSS漏洞，它只是规定了不能使用JS去获取cookie的内容，因此它只能防御利用XSS进行cookie劫持的问题。Httponly是在set-cookie时标记的，可对单独某个参数标记也可对全部参数标记。由于设置httponly的方法比较简单，使用也很灵活，并且对防御cookie劫持非常有用，因此已经渐渐成为一种默认的标准。

 ** **HttpOnly设置样例参考****

response.setHeader("Set-Cookie",
"cookiename=httponlyTest;Path=/;Domain=domainvalue;Max-Age=seconds;HTTPOnly");  
---  
  
### 7.3. **做输出数据做html转义处理，常见需要转义的字符如下：**

& \--> &

< \--> <

> \--> >

" --> "

' --> '  
  
---
