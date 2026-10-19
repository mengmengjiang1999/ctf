**![](https://image.3001.net/images/20200401/1585732908_5e845d2c18e48.jpg!small)**

**该漏洞原因在于，当HackerOne注册用户在上传自己的头像图片时，由于在头像图片的文件名处（filename:unnamed.jpg）未设置有恰当的字符长度限制，因此，可以构造巨大冗长的文件名（filename:XXXXXXXXXXXXXXXXXXXXXXX....jpg）上传，之后可导致HackerOne网站的某些页面出现拒绝服务问题（DoS）。漏洞最终获得HackerOne奖励$2,500。**

当我在注册HackerOne用户时，发现在用户头像处的图片文件名处（filename:unnamed.jpg）未对默认图片文件unnamed.jpg设置字符长度限制，所以我首先想到的是在其中构造一个尽量尽量尽量长的文件名。以下为上传用户头像的请求：

![](https://image.3001.net/images/20200401/1585732555_5e845bcb634d5.png!small)刚开始看来，这看似并不是一个严重问题，所以我想是否能添加文件名的字符长度引起HackerOne服务端抛出500的服务端错误，但几经测试，没有效果。

接着，我发现，HackerOne的多个端点都会执行graphql方式的请求去查询获取注册用户的相关信息，并且，其响应的JSON消息中还包含了用户的头像图片URL地址，以及用户上传时命名的文件名。

所以，我马上想到的就是在用户图像处创建一个巨在冗长的文件名，因此，我直接构造了一个3.6M左右的随机字符串Payload：

![](https://image.3001.net/images/20200401/1585732653_5e845c2dd05d0.png!small)然后，在用户图像的上传请求中，用该字符串替换掉图片名称
unnamed（filename:unnamed.jpg），然后执行Request上传请求。当然，请求的成功执行还是花了些许时间，这其中我用的测试用户账户为@d3f4ul7_m4n。以下为加入Payload后的用户图像上传请求和响应截图：

![](https://image.3001.net/images/20200401/1585732675_5e845c433fde1.png!small)![](https://image.3001.net/images/20200401/1585732685_5e845c4dbfee5.png!small)接下来，我用我HackerOne的主账户@red_assassin创建了一份漏洞报告，并邀请上述测试用户@d3f4ul7_m4n共同加入该报告进行讨论，然后，我发现这个邀请动作对HackerOne服务端/reports/<report-id>/participants/发起了请求，由于其请求响应中会包含进对方账号的头像文件名，因此，响应将会耗时相当，甚至有时会导致超时或浏览器崩溃。

为了证明问题危害，我又注册了另外一个经过头像名Payload构造的用户@fossnow27，然后在上述同一份漏洞报告中邀请其参与。现在，在发起了同时邀请@d3f4ul7_m4n和@fossnow27这两个测试用户后，最终，由于其中需要获取冗长的用户头像名，最终服务端/reports/<report-id>/participants/的响应直接崩溃了。

![](https://image.3001.net/images/20200401/1585732725_5e845c75dc354.png!small)顺应地，我打开了一些显示注册用户个人信息的HackerOne页面，如用户配置页面、个人漏洞报告页面、邀请报告页面，我发现在打开这些页面时同样也遇到了上述的响应较慢，甚至是直接挂掉或页面崩溃的DoS问题。

![](https://image.3001.net/images/20200401/1585732748_5e845c8c51767.png!small)

##  漏洞复现

1、打开页面<https://hackerone.com/settings/profile/edit>

2、上传用户头像图片，开启抓包：

![](https://image.3001.net/images/20200401/1585732770_5e845ca2923de.png!small)

3、在请求中的头像图片名称处filename:unnamed.jpg，用准备好的长字符串Payload替换掉其中的unnamed，形成类似<payload>abcd.jpg的文件命名，执行上传。

##  漏洞危害

当某些恶意用户的上报漏洞发生重复（duplicate）争议时，那么在发起上报人漏洞报告参与协调时，他可以利用该漏洞方法，阻止其他上报人有效参与。漏洞参与者形成访问限制。

另外，在一些公司众测项目中，列出了一些致谢白帽，其中的碳同样涉及到用户头像名称获取（如下），因此，如果一些恶意白帽用上述漏洞方法，同样可导致公司众测项目出现DoS问题。

![](https://image.3001.net/images/20200401/1585732818_5e845cd285ea1.png!small)![](https://image.3001.net/images/20200401/1585732829_5e845cdd12ce5.png!small)

##  漏洞上报和处理

> 2019.12.25 漏洞初报
>
> 2020.3.2 漏洞修复
>
> 2020.3.25 漏洞公开

***参考来源：[hackerone](https://hackerone.com/reports/764434)，clouds 编译整理，转载请注明来自
FreeBuf.COM**

  

