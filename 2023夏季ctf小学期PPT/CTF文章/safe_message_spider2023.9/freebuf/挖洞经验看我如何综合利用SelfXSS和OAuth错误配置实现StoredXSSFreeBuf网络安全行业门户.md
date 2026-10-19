***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![如何综合利用Self-XSS和OAuth错误配置实现Stored-XSS](https://image.3001.net/images/20190228/1551346720_5c77ac2092e98.png!small)**
**本文分享的作者是对Self-XSS和OAuth错误配置两个低危漏洞的组合利用，形成Stored
XSS的一个梳理过程，仅当思路拓展。由于测试保密原因，目标测试网站用redacted.com来代替描述。**

## 漏洞发现

在HackerOne平台参与的一个邀请测试项目中，我发现了一个AngularJS 客户端模板的Self
XSS漏洞和一个OAuth实现的错误配置漏洞，单独来看，这两个漏洞都属于低风险漏洞，形成不了严重的隐患影响。但经过我对它们的组合利用，就可以形成一个完美的Stored
XSS ！

目标测试网站redacted.com，它主要提供文件存储服务，有点像Google Drive 和
DropBox的样子，用户通过注册使用这个平台，可以实现文件的上传、下载和分享。

存在XSS的地方位于待上传文件的文件名处，如果把待上传文件的文件名改为
**{{constructor.constructor(‘alert(1)’)()}}.jpg**
这种样式，就会在上传文件管理面板中导致XSS，啊，可它却是一个Self XSS。

后经测试，有一种简单的方法可以让这个Self XSS转变为Stored
XSS，那就是向其它用户共享文件的上传链接，当文件被以相同的文件名从上传面板中导入时，就会导致Stored
XSS。但在这里，我还要展示另外一种转变为Stored XSS的有趣方式。

## OAuth错误配置

在设置菜单中，我发现了一个可以从DropBox导入文件的功能，使用这个功能，用户需要在OAuth机制下，把redacted.com的应用和Dropbox账户相关联。这里，来简单地介绍一下redacted.com应用的大致OAuth机制：

1、首先，用户点击Dropbox关联按钮，然后会产生一个GET发起请求：

>
> <https://dropbox.com/oauth2/authorize?client_id=>***********&response_type=code&state=****************&redirect_uri=https%3A%2F%2F[www.redacted.com%2Faccount%2Fsettings%2Fdropbox-> callback](http://www.redacted.com%2Faccount%2Fsettings%2Fdropbox-callback)

2、接下来，当前redacted.com应用的用户会跳转到Dropbox，进行一个相应的Dropbox登录和允许按钮点击：

![如何综合利用Self-XSS和OAuth错误配置实现Stored-XSS](https://image.3001.net/images/20190228/1551346505_5c77ab49e3a9b.png!small)3、点击允许Allow后，会产生一个发往redacted.com且包含
state 参数和验证码auth_code的GET请求，如下红框所示：

![如何综合利用Self-XSS和OAuth错误配置实现Stored-XSS](https://image.3001.net/images/20190228/1551346519_5c77ab57a29a6.png!small)4、redacted.com后端接收并处理这个GET请求后，用户的Dropbox账户就能与当前redacted.com应用同步了，所有Dropbox相关的文档都可导入到redacted.com应用中来；

我在测试这个OAuth机制的过程中，目的在于发现能否把我的Dropbox账户关联到其它redacted.com应用上，但却没什么发现。

其中涉及的redirect_uri是白名单化的，state参数方式也都合理，auth_code不能两次复用，等等，而且我还测试了state参数，也即redacted.com应用是否用当前用户会话对其进行验证，结果都没什么问题。

所以，基于以上这些测试来看，我肯定不能用来自Dropbox的链接
_<https://www.redacted.com/account/settings/dropbox-callback?state=>********code=**********_，去关联其他的redacted.com用户账户。

出于好奇，我删除了 _<https://www.redacted.com/account/settings/dropbox-callback?state=>********code=**********_链接中的state参数，变成了
_<https://www.redacted.com/account/settings/dropbox-callback?code=>**********_，并把它放到了redacted.com的其他用户账户中，惊喜的是，之后我的Dropbox账户就和其他用户账户关联起来了。

也就是说，只需要用一个GET请求，我就可以把我的Dropbox账户和其他任何人的redacted.com账户相关联。在这里，你可能会有疑问，我不用Dropbox账户来登录redacted.com应用，这就不能发生账号劫持了。但如前所述，在待上传文件的文件名处存在XSS，那么我们就可以考虑来充分利用利用它。

## 漏洞利用场景

1、在Dropbox中，上传一个名为{{constructor.constructor(‘alert(1)’)()}}.jpg的恶意文件，这是Dropbox允许的；

2、把Dropbox验证redacted.com应用且不包含state参数的最终OAuth链接<https://www.redacted.com/account/settings/dropbox-callback?code=>**********，发送给目标受害者；

3、当受害者的redacted.com应用和我们的Dropbox账户关联后，一旦他向redacted.com应用中导入那个恶意文件时，我们文件名方式的XSS
payload就会执行。

这里的问题在于，尽管redacted.com后端用当前的session会话对用户的state参数进行了验证，但却没验证它的存在性。redacted.com后端的验证逻辑大概是这样的：

    
    
    if(isset($_GET['state'])){
        if($_GET['state'] != current_user_state)
            ACCESS DENIED
            exit()
    }
    ACCESS GRANTED

所以，利用低危的OAuth错误配置和Self XSS，最终实现了具有危害性的Stored XSS。

## 漏洞上报进程

> 2019.1.1 漏洞初报
>
> 2019.1.8 漏洞分类
>
> 2019.1.8 漏洞修复
>
> 2019.1.15赏金发放

 ***参考来源：[medium](https://medium.com/@nahoragg/chaining-tricky-oauth-exploitation-to-stored-xss-b67eaea4aabd)，clouds编译，转载请注明来自FreeBuf.COM**  

