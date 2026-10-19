**![delete-facebook-1.jpg](https://image.3001.net/images/20190906/1567758557_5d7218dd0c9b8.jpg!small)**

**该漏洞能让攻击者在Facebook的tapprd.legal.thefacebook.com服务端（Server-Side）执行HTML代码，如此实现远程代码执行（RCE）。原因在于漏洞页面中用于填充输入的HTML标签未经转义，就被直接传递给了“HTML至PDF转化器”（HTML
to PDF Converter）进行下一步文件转化。以下为作者的分享思路。**

## HTML转PDF过程中存在的漏洞

1、Workplace by
Facebook为Facebook旗下办公通讯软件，通过公司或群组模式实现内部团队交流沟通。当属于公司或群组的个人创建Workplace by
Facebook账号时，会从Facebook官方邮箱legal_noreply@fb.com收到一封确认邮件，该邮件中包含一个需由帐号所有者签署的在线协议URL，而该URL中包含一个特殊的token，如下：

>
> <https://legal.tapprd.thefacebook.com/tapprd/Portal/ShowWorkFlow/AnonymousShowStage?token=>

打开以上URL页面后，其中包括需由用户输入的姓名、地址、电邮、职业等区域。如果我尝试向这些区域中注入HTML代码后，会发现其Web应用会对所有的文本执行HTML编码。首先，我想到的是抓包拦截请求，但是行不通，被阻挡
了。接下来，我注意到，Web应用是先对文本执行HTML编码，然后当在服务端（Server-Side）进行PDF格式转化时，会对其进行HTML解码；

2、所以我想到了进一步提权的可能，由于前述的Javascript脚本不在“HTML至PDF转化器”的内部解析范围，因此，我想到了用 “file://”
这种IFRAME中的URL格式，来尝试读取本地文件；

然后，我通过转化后的PDF文档中的IFRAME元素扫描查看到了Web应用的内部网络，从中可以区分出一些现有IP和开放/关闭端口。通过这点，可以有多种提权至RCE的方法：

1、由于Web应用服务器中还存在另一个漏洞，我可以通过它获取到Web应用的内部系统路径，然后由此提取出web.config文件，进而得到关于Web应用的更多敏感配置信息；

2、在扫描查看了Web应用的内部网络后，我发现其中一些仅限内部访问的WebLogic服务器系统存在可利用漏洞；

3、在捣鼓测试了一番不同的URL方法后，我发现用“about://”格式方法后，在PDF文件中的一个IE页面列出了所有的菜单选项和IE版本。因为我对ASP.NET不熟，但我当时猜想，是否Web应用打开IE中的HTML页面用到了某种Windows
API接口？还有在那个HTML页面中是否包含了一个用于截屏或文档转化的Javascript代码，如类似于开源PDF文档生成工具
jsPDF一样？基于这样的假设，我尝试向其中嵌入一些针对IE的Payload攻击载荷（出于保密原因，抱歉在此不能做太多细节公布）。

有了以上三种实现RCE的方法后，最后一步就是如何来执行攻击了，恰巧，我发现该Web应用系统中存在[我之前公布的一个Facebook电子邮件伪造漏洞](https://ysamm.com/?p=308)，那么两者结合就能形成最大程度威力了。

## 以legal_noreply@fb.com伪造发送电子邮件漏洞

该漏洞在于，可以用Facebook官方的无需回复邮箱legal_noreply@fb.com，以Facebook雇员或合作伙伴身份，伪造电邮正文并发送给任意用户邮箱地址。漏洞原因在于以下链接：

>
> <https://legal.tapprd.thefacebook.com/tapprd/Portal/ShowWorkFlow/AnonymousEmbed/XXXXXXXXXXXXX>

该链接是一个邮件处理模板，存在的问题是：除其中的邮件生成模板不可更改外，却可以任意指定收件人邮箱地址和收件人姓名，然而，由于收件人姓名字段没有对HTML注入做出限制过滤，因此我可以对邮件正文执行编辑修改，并对其它部分添加文字说明（具体[参见writeup](https://ysamm.com/?p=308)）。如下：

![POC_email.png](https://image.3001.net/images/20190906/1567758245_5d7217a5a1677.png!small)

## 漏洞测试被叫停

由于Facebook漏洞众测政策原因，还没待我把所有方法步骤完全实施完成，就收到了Facebook安全团队停止测试的通知。

Facebook给我的回复是，该Web应用是由某第三方合作伙伴开发的，为了避免深入的测试威胁，他们会及时通知第三方修复漏洞并发布补丁。而我也因此没得到一个理想的赏金奖励，但明白人都知道，该系统负责处理的具体业务，以及发现高危入侵漏洞后的价值。

## 漏洞报送处理进程

> 2019.4.7 漏洞初报
>
> 2019.4.10 Facebook确认
>
> 2019.5.1 Facebook需要更多验证性资料
>
> 2019.5.21 Facebook确认漏洞有效性
>
> 20.19.6.18 Facebook修复漏洞
>
> 2019.7.3 Facebook发放1000$赏金

 ***参考来源：[ysamm](https://ysamm.com/?p=280)，clouds编译整理，转载请注明来自FreeBuf.COM**  

