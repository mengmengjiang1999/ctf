***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **** **大家好，今天分享的writeup是关于outlook.live.com邮箱环境在iOS浏览器下的存储型XSS漏洞（Stored
XSS），由于测试范围隶属微软漏洞赏金项目，所以最终获得了微软官方$1000美金奖励。作者的感受是，一些基本的Payload有时候也能发挥意想不到的效果。**

 **
**![](https://image.3001.net/images/20190315/1552662547_5c8bc013462bf.jpg!small)****

## 漏洞情况

> 漏洞标题：用msoffice ppt文件触发iOS浏览器环境下的outlook.live.com网站存储型XSS漏洞
>
> 影响服务：访问了outlook.live.com网站且基于谷歌Chrome的iOS浏览器环境
>
> 上报渠道：secure@microsoft.com
>
> 其它说明：outlook.live.com为outlook.com版本升级后的网站，为微软早期推出的免费个人邮箱服务平台

## 漏洞复现

1、在苹果系列移动终端的iOS系统中，按照以下示例，创建一个MSoffice的PPT文件，其中包含一个指向地址为“javascript:prompt(document.cookie)”
的超链接，然后保存为“Powerpoint 97-2003演示文稿.ppt”格式，请注意，这点很重要，一定要保存为“Powerpoint
97-2003演示文稿.ppt”，如果不是这种格式，后续的XSS触发可能不会成功。

![](https://image.3001.net/images/20190315/1552662310_5c8bbf2678d1d.png!small)2、假想攻击者通过
​outlook.live.com 登录个人邮箱，向受害者通过邮件附件方式，发送上述制作的ppt文件；

3、假设受害者在苹果移动终端iOS系统下，使用谷歌Chrome iOS浏览器，通过 ​outlook.live.com
登录个人邮箱进行收件，打开攻击者发送的上述邮件，并点击其中的ppt附件下载。注意，此时下载操作并不会向电脑端那样直接保存到本地，而是由谷歌Chrome
iOS浏览器对ppt文件解析打开，而受害者在文件打开之后，一旦点击了ppt中的那个超链接，就会触发“javascript:prompt(document.cookie)”Palyload的XSS执行。

4、当然，如果直接通过iOS中的Chrome浏览器进行在线的ppt解析加载（Powerpoint online）或执行附件预览，如下：

![](https://image.3001.net/images/20190315/1552662338_5c8bbf4245feb.jpg!small)在线预览打开之后，点击其中“javascript:prompt(document.cookie)”的超链接，也能触发Payload实现XSS。当然了，只要在iOS系统中用outloook邮箱账户登录，预览打开这种经过构造的附件，XSS攻击一样也能在Safari,
Firefox, Chrome, Opera中实现。如下：

##
![](https://image.3001.net/images/20190315/1552662356_5c8bbf540ef8c.png!small)漏洞影响

恶意攻击者可以利用该漏洞嵌入恶意文件或脚本，发送给特定受害者，以XSS为切入利用方式，实现进一步的入侵渗透。

测试成功环境：

> iPhone 6 – iOS v11.2.5.
>
> ​Safari最新版
>
> Google Chrome最新版
>
> 我的outlook邮箱账户

## 漏洞上报进程

> 2018.2.21 通过secure@microsoft.com向MSRC上报漏洞
>
> 2018.2.21 微软团队回复并称已开展调查
>
> 2018.2.23 微软团队向我请求更多技术细节
>
> 2018.7.26 微软告知我还在处于技术分析调查过程
>
> 2018.11.7 微软告知我漏洞符合漏洞赏金政策
>
> 2018.11.26 微软通过支付平台向我发放赏金$1000
>
> 2019.3.4 我向微软申请漏洞公开
>
> 2019.3.14 微软同意漏洞公开

 ***参考来源：[omespino](https://omespino.com/write-up-1000-usd-in-5-minutes-xss-stored-in-outlook-com-ios-browsers/)，clouds编译，转载请注明来自FreeBuf.COM**  

 ****  

