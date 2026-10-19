【密钥泄漏】CVE-2022-29266 Apache Apisix jwt插件

[ H_00c8](https://www.jianshu.com/u/3cf70976a08b)关注赞赏支持

# 【密钥泄漏】CVE-2022-29266 Apache Apisix jwt插件

# 漏洞描述

在2.13.1版本之前的APache APISIX中，攻击者可以通过向受 jwt-auth 插件保护的路由发送不正确的 JSON Web
令牌来通过错误消息响应获取插件配置的机密。依赖库 lua-resty-jwt 中的错误逻辑允许将 RS256 令牌发送到需要 HS256
令牌的端点，错误响应中包含原始密钥值。

# 漏洞版本

Apache Apisix < 2.13.1

# 插件开启

在这里给大家演示的是Dashboard页面开启jwt插件。

1、当我们环境搭建完毕后、通过访问http://127.0.0.1:9000 登陆页 默认账号密码 admin admin

image.png

jwt-auth 是一个认证插件，它需要与 consumer 一起配合<typo id="typo-332" data-origin="才能"
ignoretag="true">才能</typo>工作。  
添加 JWT Authentication 到一个 service 或 route。 然后 consumer 将其密钥添加到查询字符串参数、请求头或
cookie 中以验证其请求。

2、我们先创建一个consumer 名称的话 随便写。

image.png

3、点击下一步、启用jwt-auth插件。

image.png

将{ "key": "Vul_test", "secret": "admin_admin" } 填写到编辑器里，值的话可以随便写。  
算法的默认配置是HS256 。

image.png

> 【
> **[相关技术文档】](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.qq.com%2Fdoc%2FDVExrc2JqUU1DWWd5)**  
>  1、网络安全学习路线  
>  2、电子书籍（白帽子）  
>  3、安全大厂内部视频  
>  4、100份src文档  
>  5、常见安全面试题  
>  6、ctf大赛经典题目解析  
>  7、全套工具包  
>  8、应急响应笔记

4、接下来让我们创建<typo id="typo-580" data-origin="路由" ignoretag="true">路由</typo>。

image.png

5、在设置路由这项里、名称需要添加、路径需要添加。路径的话、因为后面需要用、可以写个简单易记的。接着点击下一步。

image.png

image.png

6、在设置上游服务里，只需要修改目标节点就行(有配置上游服务的不用写)。然后点击下一步

image.png

7、在插件配置里，只需启用jwt-auth ，不需要配置。然后点击提交下一步。

image.png

image.png

8、最后将全部配置进行提交，点开路由，有我们新增路由表示创建成功。

image.png

9、为了保险起见我们通过命令行测试一下。  
当我们启用了jwt-auth插件后，会增加 /apisix/plugin/jwt/sign 这个接口。  
在命令行输入以下命令，参数key的值就是我们刚刚在consumer 配置的key值，访问了这个api，我们可以获取到认证token。

    
    
    curl http://127.0.0.1:9080/apisix/plugin/jwt/sign?key=Vul_test -i
    

image.png

然后再使用我们获取到的token值，尝试进行请求。返回的502，就可以做下一步的漏洞测试了。

注意：路由地址是我们在上面配置好的。token 是上一步请求回来的，将jwt参数值修改为获取到的token。

在官网中有三种认证方式：

  * 在url参数中；
  * 在头部信息的cookie中；
  * 请求头Authorization 中。

这里参与的是<typo id="typo-1153" data-origin="在" ignoretag="true">在</typo>参数中

    
    
    curl http://127.0.0.1:9080/Vul_test?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJWdWxfdGVzdCIsImV4cCI6MTY1MDk1NTEzM30.JEzqCqEFe0M1MVLioRRWHl2yuxrpN3rL29rpR7N6UOI -i
    

image.png

到此为止，整个环境就搭建完毕了。下面有些关于json web token的知识，可以了解了解。

# 什么是 JSON Web 令牌？

JSON Web Token （JWT） 是一种开放标准 （RFC 7519），它定义了一种紧凑且独立的方式，用于将信息作为 JSON
对象在各方之间安全地传输。此信息可以进行验证和信任，因为它是经过数字签名的。JWT 可以使用密钥（使用 HMAC 算法）或使用 RSA 或 ECDSA
的公钥/私钥对进行签名。

# JWT 获取 及访问 API 或资源流出：

image.png

  1. 应用程序或客户端请求对授权服务器进行授权。这是通过不同的授权流<typo id="typo-1614" data-origin="之一" ignoretag="true">之一</typo>执行的。例如，典型的 OpenID Connect 兼容 Web 应用程序将使用授权代码流通过终结点。/oauth/authorize
  2. 授予授权后，授权服务器将向应用程序返回访问令牌。
  3. 应用程序使用访问令牌访问受保护的资源（如 API）。

# JSON Web 令牌的使用

授权：这是使用 JWT 的最常见方案。  
信息交换：JSON Web令牌在各方之间安全传输信息。

# JSON Web 令牌格式

    
    
    三部分组成
         Header Payload  Signature
    
      通常如下所示:
         header.payload.Signature
    

Header 是由 令牌类型(jwt) 和签名算法组成(HS256) ，格式是JSON，会进行Base64Url 编码

Payload 是由注册声明、公共声明组成、私人声明组成，格式是JSON，会进行Base64Url 编码

Signature 是签名部分、创建签名部分，您必须获取编码的Header、编码的Payload、中指定的算法，并对其进行签名。

    
    
    例如，如果要使用 HMAC SHA256 算法，将按以下方式创建签名：
            HMACSHA256(
            base64UrlEncode(header) + "." +
            base64UrlEncode(payload),
            secret)
    

最后输出的部分是三个Base64-URL字符串 由点分割。  
下面显示了一个 JWT，它具有编码的Header和Payload，并使用密钥对其进行签名。

image.png

# 漏洞复现

通过diff记录，可以看到漏洞不复杂，是在返回的message中将报错输出，输出的内容包含敏感数据。在漏洞描述中已经讲明白了，依赖库 lua-resty-
jwt 中的错误逻辑允许将 RS256 令牌发送到需要 HS256 令牌的端点，错误响应中包含原始密钥值。  
看了描述，下一步就是构建RS256令牌、然后发送到接受HS256令牌的路由上。

image.png

开始构建RS256令牌。与HS256有些区别。在构建的时候需要一组私钥、公钥。

# RS256令牌构建

JSON Web Tokens 网站中有个Debugger 可以帮助我们去快速构建。  
我们需要填写三个部分、Header Payload VERIFY SIGNATURE

1、先将 Algorithm 修改为RS256

image.png

image.png

2、Header 可以保持不变。

3、Payload 填写：{ "key": "Vul_test" } 。此时的key值是我们在注册 consumer 填写的key值。

image.png

4、VERIFY SIGNATURE 公钥、私钥不用改，可以使用。

5、最后在左边文本框里会帮我们自动生成 RS256令牌。前提是格式不能错，前两部分都是JSON格式。

image.png

OK！准备完毕。  
还记得我们上边的token测试嘛，将jwt的参数换成获取到的RS256令牌。

    
    
    curl http://127.0.0.1:9080/Vul_test?jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJWdWxfdGVzdCJ9.Q-psC9EqmVdjSSQW4gjNl_pcBt_vKoQbWz6j_YI-yHXOurShJIkceShVSHU2XZfH1E5g5pwOQ_JizDC_mp95_3FTv6j6ECcRdUOsXrMP8L5CJhNJhNh-UddrpBfep4WWn-bZsJV2mYyp4fLAXwMVH2JsOPRi9nkuR4_F8ZJzU-2KwrIRBDGo8NsgVpYhuQcjIDRBOmKloBzqdPKXbVPFetkDgqJgN0jLSuYV7mKJSN2R6XLF62gtZilf03pIf9UQFs7XE5kY2H4BSOBIZlD3ET6pvpo1PJRVmvxBU9_y7DfMkUzkq9S3gihsabHGuybKOUbQ_GqOGv_knule8wTimg -i
    

命令行发起请求。命令行发起请求。在messages信息中能够获取到我们刚开始在 consumer 插件配置中填写的 secret

image.png

# 浅析

/apisix/plugins/jwt-auth.lua#_M.rewrite() 判断 令牌、及令牌的 Header、Payload、user-
key。未通过会返回401及message信息。可以看到有两个会输出报错信息：一个是判断token、一个是判断secret。

image.png

image.png

我构建了很多RS256令牌，Payload的配置各种尝试更改。在看源码的时候，考虑绕过各种固定报错信息，才能够往下走。

有一个错误一直不理解，Invalid user key in JWT token 。尝试修改Key值。

image.png

在分析CVE描述的时候认为从该漏洞中泄漏的是Key值，然而实际是 secret值。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [使用auth0构建JWT](https://www.jianshu.com/p/0fed399c2561)

写于2019年年底，2020年春，新年好！ JWT 全称 Json Web Token 用于用户认证 用于前后端分...

[_Youarethehero](https://www.jianshu.com/u/8a578974927d)阅读 13,838评论 3赞 6

  * [JWT 学习](https://www.jianshu.com/p/60dbcaea510c)

前言 在实际测试网站时多次遇到JWT认证，赶紧把这块知识点通过CTF题目的方式补上。 JWT 定义 JWT 全称是...

[CSeroad](https://www.jianshu.com/u/859a42ec7c8f)阅读 1,423评论 1赞 3

  * [java-jwt ReadMe 文件中文翻译 （ R3.8.1 ）](https://www.jianshu.com/p/e80eabfd0dea)

说明：本翻译仅仅作为个人笔记使用（因为每次看英文文档，看了第一遍，下次再去看又得慢慢翻译一遍，很反感，所以本人决定...

[执着的小子](https://www.jianshu.com/u/22e369dcabdf)阅读 1,214评论 1赞 1

  * [SpringBoot-JWT 概述与代码实现](https://www.jianshu.com/p/1539b2f49abd)

一、什么是JSON Web Token？ JSON Web Token（JWT）是一个开放标准（RFC7519），...

[帅大叔的简书](https://www.jianshu.com/u/651c15a1758a)阅读 1,209评论 2赞 14

  * [JWT认证机制笔记](https://www.jianshu.com/p/223b9112fc5e)

0x01 什么是JWT JWT 全称为 JSON Web Tokens，是为了在网络应用环境间传递声明而执...

[Your7Maxx](https://www.jianshu.com/u/95058f4bbac0)阅读 1,888评论 0赞 1

 