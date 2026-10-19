***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **** **今天我要分享的是，利用HackerOne平台的漏洞报告邮件转发（Security@email
forwarding）和项目退出功能（Leave
Program），无需与厂商的任何用户交互行为，即可实现反复对HackerOne平台私密项目邀请消息的获取。这是一个逻辑功能Bug，HackerOne的测试邀请获取设计存在缺陷。**

## 漏洞报告邮件转发功能（Security@email Forwarding）

这个[漏洞报告邮件转发功能（Security@email
Forwarding）](https://docs.hackerone.com/programs/email-forwarding.html)，需要厂商和HackerOne协商开通，并不是所有厂商的测试项目都会有这个功能，其原理是这样的，如果白帽子们在HackerOne上发现和某家厂商相关的漏洞，他可能会选择向HackerOne提供的相应厂商的安全团队邮箱security@companyname.com报告漏洞。与此同时，当白帽通过HackerOne平台报告了该漏洞之后，白帽子自己的
Inbox 里也会转发留存一份报告作为存档。

![email-forwarding-1-8d1b34ce232c12a9f558618e797f10da-c5529.jpg](https://image.3001.net/images/20181116/1542352876_5bee6fecde58a.jpg!small)在测试厂商收到报告之后，HackerOne系统会自动向白帽子的
Inbox 中发送一封私密测试邀请，以邀请白帽参加其组织的私密漏洞测试项目，以进一步提交漏洞。如下所示：

##
![1_Hg2fndjugS2tiZJSuRx0hw.png](https://image.3001.net/images/20181116/1542352911_5bee700f87ec8.png!small)项目退出功能（Leave
Program）

[项目退出功能](https://docs.hackerone.com/hackers/decline-invites-and-leave-programs.html)，简单地说就是在HackerOne平台中，白帽子们在加入某个漏洞测试项目之后，如果发现这个项目的测试范围或领域并不是你感兴趣或擅长的，那么，可以选择点击
“Leave Program”来退出该项目。在测试项目的主页（Security Page）中，可以找到“Leave Program”按钮。

![leaving-programs-1-a33d17157e4c9ecef34623e4eb558e4e-946ca.png](https://image.3001.net/images/20181116/1542352995_5bee7063a48ad.png!small)而在这个功能中，如果你选择退出了某个邀请项目，HackerOne会让你完成一份关于项目退出功能的调查表，之后，作为回报，系统还会在24小时之内继续向你发送另一个测试项目的邀请。如下：

![0_C2zR4B_ZPFrIxOJ9.jpg](https://image.3001.net/images/20181116/1542353034_5bee708a1f8b4.jpg!small)

> You helped out us by filling out a survey，in return you will be fast-tracked
> for invites, with the first one arriving in the next 24
> hours.（感谢你为我们完成了调查问卷，作为回报，我们会把你加入快速邀请行列，你将在24小时内收到一个邀请）  
>

那么，在这种设计逻辑下，能否存在一种可利用的空子呢？可以让 HackerOne 自动不断地向我发送测试项目邀请？答案是肯定的。

## 漏洞复现

假设你现在未收到任何测试项目邀请，也就是邀请数为0。那么可以用以下几步来进行漏洞复现：

1.首先，在HackerOne上找到开启漏洞报告邮件转发功能（Security@email
Forwarding）的测试项目，简单地说，可以通过HackerOne赏金项目链接 <https://hackerone.com/bug-bounty-programs>
来查找，如果确认其测试项目主页中有提供漏洞上报邮箱security@companyname.com，那么，说明该厂商的漏洞报告邮件转发功能（Security@email
Forwarding）是开启的。如下图所示：

![email.png](https://image.3001.net/images/20181116/1542353128_5bee70e8469c2.png!small)2.选取其中用来作漏洞报告邮件转发的邮箱，这里就用security@companyname.com来代替吧；

3.这个邮箱也就是你能收到HackerOne测试邀请的关键，所以我们就向其发送一封测试邮件；

4.之后，你会通过HackerOne平台，收到一封来自厂商安全团队的测试邀请，如下图所示：

![1_Hg2fndjugS2tiZJSuRx0hw.png](https://image.3001.net/images/20181116/1542353169_5bee7111119d0.png!small)5.点击上图中的
Submit Vulnerability Report 链接，你就成为了项目参与者了；

6.现在，选择项目退出（Leave Program），完成项目退出问卷调查并确认退出；

7.之后，你又被HackerOne加入快速邀请行列，在接下来的24小时之内，又可以接收到关于另一项目的测试邀请了；

8.重复以上第2步到第第7步，就会不断得到不同项目的漏洞测试邀请。

下图是这个过程的简单逻辑描述：

##
![1_ucSmqgAVCE_ltZcM7viszA.jpeg](https://image.3001.net/images/20181116/1542353220_5bee7144211fe.jpeg!small)漏洞影响

攻击者可以不需要与厂商进行任何交互，就可以得到各种漏洞测试项目的邀请，向上述我那样重复，几个月之内就能收到100多个测试邀请，从而得到你想要的邀请。

## 漏洞修复

现在，HackerOne已成功修复了这个逻辑Bug，退出项目的白帽再也不会再收到其它厂商的测试邀请了。

##
![1_Eqq3z7tO96pjJ1Li-F9rYw.png](https://image.3001.net/images/20181116/1542353263_5bee716fcf700.png!small)漏洞上报进程

> 2018.04.06 11:26:21 向HackerOne上报漏洞
>
> 2018.04.06 16:58:42 HackerOne确认并分级漏洞
>
> 2018.04.11 21:34:50 $2,500赏金发放
>
> 2018.04.17 19:53:34 漏洞修复

更多技术信息，请参考原HackerOne漏洞报告 - <https://hackerone.com/reports/334205>

***参考来源：[medium](https://medium.com/japzdivino/harvesting-all-private-invites-using-leave-program-fast-tracked-invitation-and-security-email-a01c8b3ce76f)，clouds编译，转载请注明来自FreeBuf.COM **  

