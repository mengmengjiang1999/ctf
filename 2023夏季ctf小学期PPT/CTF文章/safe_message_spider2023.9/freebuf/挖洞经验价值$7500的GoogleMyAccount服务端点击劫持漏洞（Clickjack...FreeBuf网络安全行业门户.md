***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![unnamed.jpg](https://image.3001.net/images/20181128/1543395947_5bfe5a6b034ae.jpg!small)
**最近，我发现了Google My
Account（myaccount.google.com）的一个点击劫持漏洞（Clickjacking），并最终收获了$
7,500的赏金。不可思议吧？其实我早在3月份的时候就发现了这个漏洞，但却被Google的内容安全策略（CSP）给拦截了，后来，在8月份的时候，我又研究了一番，终于绕过了CSP，成功实现Clickjacking。**

##  **最早发现**

****一开始，我关注研究的是business.google.com和其子域名，随便试试了它上面的各种功能，分析一下请求和响应内容，编辑请求参数，等等。但当我操作用户管理时，却又跳转到了myaccount.google.com。

用BurpSuite测试了一下，发现这个服务端并没有 X-Frame-Option 的头设置。X-Frame-Options
响应头是用来给浏览器指示允许一个页面可否在 <frame>, <iframe> 或者
<object>中展现的标记，网站可以使用此功能，来确保自己网站的内容没有被嵌到别人的网站中去，也从而避免了点击劫持 (clickjacking)
的攻击。X-Frame-Options有三种可配置值，分别是DENY、SAMEORIGIN和ALLOW-FROM。

看到了这里之后，我用Firefox
ESR浏览器，构造了一个包含iframe的html跳转页面cj.html，iframe中写入了我的myaccount.google.com和business.google.com账号。逻辑是没错的，但是最终却被Google自身的CSP策略给挡了。

##
![01.png](https://image.3001.net/images/20181128/1543395566_5bfe58eed2fe9.png!small)绕过CSP

这样我就放着一边了，后来到8月15日，我又坐下来慢慢研究，我在想触发CSP的难道是出在了其跳转源的origin参数上吗？所以，我把心思放到了origin参数的business.google.com之上。

由于构造的跳转页面中，其iframe片段中包含的链接为：

>
> [https://myaccount.google.com/u/0/brandaccounts/group/101656179839819660704/managers?originProduct=AC&origin=https://business.google.com](https://myaccount.google.com/u/0/brandaccounts/group/101656179839819660704/managers?originProduct=AC&origin=https://business.google.com)

响应情况为：

![02.png](https://image.3001.net/images/20181128/1543395580_5bfe58fc9ff0c.png!small)我意识到它会不会接收其它origin源主机呢？所以，我就随手一改，把origin源主机改为了<https://akugalau.business.google.com>，这一改，虽然请求可以通过，但是akugalau.business.google.com本来就是一个不存在的子域名网站，所以，这样一来，还是没有逃过CSP的魔爪。

![03.png](https://image.3001.net/images/20181128/1543395635_5bfe593395b8e.png!small)就这样放弃吗？Come
on，Google可是一家大公司啊，再想想办法吧！

没事，我有的是时间。所以，我又往origin参数里添加了一些其它字符，比如加了一个回车符%0d，变为URL编码后的<https://%0d.business.google.com>，最终iframe中的URL为：

>
> [https://myaccount.google.com/u/0/brandaccounts/group/101656179839819660704/managers?originProduct=AC&origin=https://%0d.business.google.com](https://myaccount.google.com/u/0/brandaccounts/group/101656179839819660704/managers?originProduct=AC&origin=https://%0d.business.google.com)  
>

这样一试，CSP竟然没跳出来了！t!!!!?!@?#!@?3!@?3?

**![04.png](https://image.3001.net/images/20181128/1543395676_5bfe595c3be46.png!small)**在构造的html页面中，我成功实现了点击劫持（Clickjacking）：
****

##
![05.png](https://image.3001.net/images/20181128/1543395702_5bfe597646632.png!small)PoC

如果你问我是怎么想到绕过CSP的方法的，其实我也不知道，就是乱试呗，看运气。上报Google之后，我估计赏金也就3,133.7 或
5,000美金左右，但是，Google最终给我的却是$ 7,500美金！

![06.png](https://image.3001.net/images/20181128/1543395730_5bfe5992eb725.png!small)PoC
Code :

> <iframe src=”<https://myaccount.google.com/u/0/brandaccounts/group/>{your-> group-> id}/managers?originProduct=AC&origin=<https://%0d.business.google.com>”
> width=”1000″ height=”1000″>

漏洞攻击适用场景：

> 1\. Google组用户基于group-id邀请新成员；
>
> 2\. 新成员接受邀请；
>
> 3\. 新成员知晓组ID号 {your-group-id} ；
>
> 4\. 新成员以此构造一个包含类似以上点击劫持的恶意页面，欺骗管理员，实现自身权限升级为组管理者；
>
> 5\. 新成员成功实现对组项目的接管。

## Poc视频：

> 8.11 : 向Google报告漏洞
>
> 8.15 : Google安全团队要求更多细节
>
> 8.15 : 上报更多漏洞细节
>
> 8.21 : Google暂时无法验证漏洞
>
> 8.21 : 给Google了PoC视频
>
> 8.28 : Google要求攻击场景补充
>
> 8.28 : 描述攻击场景
>
> 9.11 : Google认可
>
> 9.25 : 收到7,500$赏金
>
> 9.25 : 我差点喜极而泣

 ***参考来源：[apapedulime](https://apapedulimu.click/clickjacking-on-google-myaccount-worth-7500/)，clouds编译，转载请注明来自FreeBuf.COM**  

