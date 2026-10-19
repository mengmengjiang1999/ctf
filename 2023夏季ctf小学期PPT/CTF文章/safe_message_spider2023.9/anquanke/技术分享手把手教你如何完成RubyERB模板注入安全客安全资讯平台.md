# 【技术分享】手把手教你如何完成Ruby ERB模板注入

阅读量 **229879**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-18 14:34:45

 **x**

##### 译文声明

本文是翻译文章，文章来源：trustedsec.com

原文地址：<https://www.trustedsec.com/2017/09/rubyerb-template-injection/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**前言：现在Web应用的模板**

现在的Web应用中，许多客户端以及服务器端经常会用到模板。许多模板引擎提供了多种不同的编程语言实现，比如Smarty、Mako、Jinja2、Jade、Velocity、Freemaker以及Twig等模板。作为注入攻击大家族中的一员，模板注入这种攻击形式对不同的目标所造成的影响也有所不同。对于AngularJS而言，模板注入攻击可以达到
**XSS攻击** 效果，对于服务器端的注入攻击而言，模板注入攻击可以达到远程代码执行效果。

作为大名鼎鼎BurpSuite工具的开发商，Portswigger写了一篇[文章](http://blog.portswigger.net/2015/08/server-side-template-injection.html)详细介绍了服务器端的模板注入攻击。对攻击者而言，首先需要做的就是识别模板引擎、枚举可访问的类或方法，最终利用这些信息完成预期的操作，比如读取或写入文件、命令执行或其他操作等。攻击者具体能执行哪些操作取决于可访问的类方法或函数的能力范围。

  

**模板攻击：Ruby/ERB模板注入**

在本文中，我们会使用 **TrustedSec** 应用安全课程中的实验目标，演练一遍 **Ruby/ERB模板注入**
攻击。我们的实验对象是一个简单的应用，该应用可以模拟包含模板编辑功能的一种IT服务台（Helpdesk）报告工具。我们可以通过这个应用来编辑HTML及模板，也可以预览编辑效果，如下图所示：

使用预览（preview）按钮提交表格后，呈现在我们眼前是包含用户信息以及用户创建时间的一个页面：

观察代码中获取username以及tombstone时所使用的语法，根据其中的<%=语法以及其他一些Ruby技术，我们可以猜测这段代码属于Ruby/ERB代码。基于这个判断，我们可以编辑输入数据，测试我们是否可以进行模板注入。大致浏览ERB文档后，我们了解到<%=语法可以用来执行Ruby语句，并会尝试将结果转换为字符串，以附在最终的结果文本中。我们可以使用如下攻击载荷来尝试执行数学运算：

    
    
    ruby <%= 7 * 7 %>

运算结果为49，每个用户都会打印一次运算结果，如下所示：

可以肯定的是，这段代码存在模板注入漏洞。非常好，接下来我们可以试试看能否执行函数。我们可以先来测试自带的全局函数是否能用到这段代码中。比如，我们可以测试如下这种载荷：

    
    
    ruby <%= File.open(‘/etc/passwd’).read %>

由于不安全操作的原因，系统阻止我们访问 **File.open** 函数。Ruby的ERB模板引擎包含一个安全级别（safe
level）参数，当安全级别设置为0以上的某个值（比如3）时，我们无法在模板绑定（template
binding）中执行包括文件操作在内的某些函数。如果应用使用的安全级别为4，那么它会使用最为严格的隔离机制，只能执行标记为可信状态的那些代码。因此，看样子管理员在这个模板引擎中设置了安全级别。虽然我们的攻击不会像读写硬盘文件那样简单，但这里我们还可以尝试许多攻击面。比如，对于目前可用的这些小工具（gadget），我们还可以做什么操作？如果我们想分析self对象（self-object），我们可以尝试枚举该对象可用的属性及方法。比如，我们可以使用如下载荷：

    
    
    ruby <%= self %>

结果如下：

结果看起来就是Ruby的风格。现在我们可以试着获取self对象的类名：

    
    
    ruby <%= self.class.name %>

结果如下：

类名为“TemplateInjection”。现在我们已经可以“访问”这个控制接口，我们能用它来干啥？我们可以来枚举TemplateInjection类的可用方法：

    
    
    ruby <%= self.methods %>

结果如下：

接下来，我们可以观察这些函数，思考哪些数据可以传递给这些函数，以实现未授权访问目的。虽然我们并不清楚该应用具体使用的web框架，但由于我们正往服务器发送HTTP
POST请求，因此可以猜到我们很有可能处于handlePOST或者doPOST函数内部。也许我们可以借此访问某些局部变量。

如果大家不熟悉Ruby，这里我稍微介绍下。Ruby提供了强大的元编程（metaprogramming）以及内省（introspection）功能，读者可以访问[此链接](http://ruby-metaprogramming.rubylearning.com/)了解更多细节。作为攻击者，我们可以使用其中某些功能（如前面提到的类的.methods以及.name方法）来探索程序的内部结构。我们可以使用如下载荷获取目标所需的具体参数：

    
    
    ruby <%= self.method(:handle_POST).parameters %>

结果如下：

从结果中，我们可知handle_POST需要3个req参数，该参数可能代表的是某个请求（request）对象；rsp参数可能代表的是响应数据的引用；最后的session参数可能是某个id或者某个对象。我们可以继续探索，以确认session对象的具体含义，使用的载荷如下：

    
    
    ruby <%= session.class.name %>

结果如下：

上述结果中，我们首先可以观察到的是“WEBrick”，这是Ruby在标准库中实现的原生web服务器。我们当然可以继续探索这个session对象，但除此之外，还有其他一些目标更值得我们探索，比如，我们可以重点关注与当前会话有关的那些数据。简单翻阅WEBrick文档后，我们发现某些变量会传递给Servlet以处理客户端请求。我们可以使用某些内省（introspection）方法，以确认我们是否可以访问这些变量以及其他可用变量。

    
    
    ruby <%= self.instance_variables %>

结果如下：

当WEBrick被实例化以处理客户端请求时，它会将某个http服务器实例传递给servlet，这很有可能就是@server这个实例变量。接下来我们可以证实这个猜想，同时观察这个对象包含哪些成员变量。我们同样可以通过调用.instance_variables方法来证实这一点：

    
    
    ruby <%=@server.instance_variables %>

结果如下：

其中最为有趣的应该就是@ssl_context变量。这个变量可能会包含某些密钥或者其他有用的信息。需要注意的是，接下来我们会稍微改一下语法，使用<%来执行Ruby语句。通过这种语法，我们可以创建自己的局部变量，保存@sll_context的引用，使载荷可读性更好，方便随后在模板中加以引用。

    
    
    ruby <% ssl=@server.instance_variable_get(:@ssl_context) %><%= ssl.instance_variables %>

结果如下：

结果中，@key看起来非常有趣，我们可以提取这个值：

    
    
    ruby <% ssl = @server.instance_variable_get(:@ssl_context) %><%= ssl.instance_variable_get(:@key) %>

结果如下：

  

**总结：风险与检验**

在实际生活中，服务器私钥被泄露是非常严重的一件事情。作为应用安全测试员，我们的测试操作到此差不多就该停止了。开发人员可以采用多种方式来限制数据的读取范围，进一步沙箱化模板中运行的代码。我们会根据测试过程中对目标应用的了解来给出相应的建议。作为应用测试人员，我们需要全方位探索哪些模板代码会提交到服务端进行处理。虽然存在一定的安全风险，但是由用户提供模板的场景依然非常常见，特别是在某些应用中更是如此（比如用来生成报表以及发送邮件的那些应用）。希望读完这篇文章后，读者可以掌握一定的技巧来测试现在常用的那些模板引擎。

本文翻译自trustedsec.com [原文链接](https://www.trustedsec.com/2017/09/rubyerb-template-injection/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86867](/post/id/86867)

安全客 - 有思想的安全新媒体

本文转载自: [trustedsec.com](https://www.trustedsec.com/2017/09/rubyerb-template-injection/)

如若转载,请注明出处： <https://www.trustedsec.com/2017/09/rubyerb-template-injection/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

