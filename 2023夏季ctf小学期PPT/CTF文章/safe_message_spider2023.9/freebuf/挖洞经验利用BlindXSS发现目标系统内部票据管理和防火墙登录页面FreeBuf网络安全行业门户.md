***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**![01.png](https://image.3001.net/images/20190618/1560864313_5d08e639051fd.png!small)
*大家好，今天分享的Writeup是作者通过对某电子商务网站的Blind
XSS测试，发现了系统内部的票据管理系统和FortiGate防火墙管理系统，漏洞最终被定义为XSS导致的信息泄露，获得了厂商
$1,250的奖励，漏洞虽然简单，但这种姿势值得学习。以下是作者的分享，出于保密原因，其中描述的目标网站简称为seller.redacted.com。

## 漏洞发现端倪

刚开始在对seller.redacted.com的测试过程中，我尝试了各种方法但却一无所获，这种苦闷大家都能明白。于是，我尝试着变换思路寻找新的切口，这次我想看看XSS。在目标网站中我发现了一个比较有意思的登录页面，当在用户名密码区域中输入错误的凭据，输入失败后，就会出现一个“无法登录？”（Unable
to Login?）的选项按钮来，如下：

![02.jpg](https://image.3001.net/images/20190618/1560864135_5d08e587bbee6.jpg!small)好奇心促使我点击了这个选项按钮，之后，会跳出一个无法登录的信息反馈填写框，其中有无法登录相关的问题类型、注册的邮箱、个人手机号码和问题描述这几个填写项，我一一填写完后，在最后的问题描述区域内整上了我的Blind
XSS Payload，看看会出现什么结果。如下：

![03.png](https://image.3001.net/images/20190618/1560864147_5d08e593c532d.png!small)

## 获得系统内部票据管理系统登录页面

通过不停地变换Blind XSS Payload尝试，一小时后，我通过上述无法登录的信息反馈机制，在我填写的邮箱中收到了目标系统发给我的一条通知消息，其为
“XSS payload fired on
something.private.redacted.com/#app/secondLevelLead/my/incident/[ticket]/ticketjourny”：

![04.png](https://image.3001.net/images/20190618/1560864171_5d08e5ab4c50c.png!small)也就是说，那个问题描述区域确实存在XSS漏洞，且从通知消息中，我得到了目标系统的某个类似票据管理的服务端<http://something.private.redacted.com/#app/secondLevelLead/my/incident/>[ticket]/ticketjourny，可遗憾的是，我却不能有效地访问它，为什么呢？经过研究，我发现，这其实是一个内部管理系统，只能内部员工或通过VPN方式才能实现访问。

![05.png](https://image.3001.net/images/20190618/1560864184_5d08e5b853f13.png!small)

## 获得系统内部FortiGate防火墙登录页面

好吧，无法访问也就算了，但从上述通知消息的内容中，我又发现了另外一个IP地址，它是一个FortiGate防火墙登录页面，FortiGate是一种下一代防火墙NGFW系统。

![06.png](https://image.3001.net/images/20190618/1560864223_5d08e5df579db.png!small)用简单的用户名密码组合试试吧，admin/admin，哇，竟然可以成功登录！

![07.png](https://image.3001.net/images/20190618/1560864232_5d08e5e8c3fd3.png!small)登录之后，我就控制了这台防火墙，其中的功能更改也就完全不在话下了。

## 漏洞上报进程

> 2019.5.29 通过HackerOne向厂商上报
>
> 2019.5.29 HackerOne回复
>
> 2019.5.30 厂商对漏洞分类
>
> 2019.6.3 收获赏金$1,250

 ***参考来源：[pwnsec](https://pwnsec.ninja/2019/06/06/how-i-was-able-to-get-private-ticket-response-panel-and-fortigate-web-panel-via-blind-xss/)，clouds编译，转载请注明来自FreeBuf.COM**

