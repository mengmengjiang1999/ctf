***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1_CmjmgiI3Sr6oByNZ81pkhQ.jpeg](https://image.3001.net/images/20190312/1552382427_5c8779db83bdb.jpeg!small)

**在做漏洞众测的时候，漏洞的定义其实是非常广泛的，就看你如何来看待它了，所以当目标项目相关的某项新功能新特点出现时，你可以仔细研究，结合实际进行一些安全分析。本文中，作者就针对GitHub
Repository Wiki Pages页面做了一次类似的综合分析，综合形成了漏洞隐患进行了上报。**

## GitHub Repository Wiki Pages介绍

依照 Wiki 的定义，它是一种可以多人共同编辑的网页，每个人都可以在上面任意的修改页面数据，像百度百科和维基百科一样。GitHub也有Wiki页面？是的。

GitHub 用户创建每一个项目都有一个独立完整的 Wiki 页面，我们可以用它来实现项目信息管理，为项目提供更加完善的文档。我们可以把 Wiki
作为项目文档的一个重要组成部分，将冗长、具体的文档整理成 Wiki，将精简概述性的内容，放到项目中或是 README.md 里。

GitHub 的 Wiki 页面在如图所示选项卡下，默认应该是开启的，而且新建时是空的，我们可以点击中间那个绿色的 Create the first
page 按钮创建一个页面。

## ![ 一次对GitHub
Wiki页面的把玩测试](https://image.3001.net/images/20190312/1552382503_5c877a2768458.jpg!small)

## 安全隐患

从GitHub Wiki页面的上述描述中，我们可以发现问题所在：只要拥有Github账户的人，都可以对那些开启Wiki页面的项目，进行Wiki
页面的任意创建编辑。如下：

![ 一次对GitHub
Wiki页面的把玩测试](https://image.3001.net/images/20190312/1552382555_5c877a5bae3ea.png!small)现实是，一些大公司的开发人员或工程师们可能根本不会在意这个默认设置，那么，这些大公司项目的Wiki页面就能被任意Github用户进行任意编辑修改了，不是吗？这难道不是一个安全问题吗？当然是......。比如以下随手搜的一些开启Wiki页面的Github项目：

> <https://github.com/phachon/mm-wiki/wiki>
>
> <https://github.com/gollum/gollum/wiki>
>
> <https://github.com/g0v/dev/wiki>
>
> <https://github.com/ndunning/testing123/wiki/>  
>

还有一些原因是，如果一些工程师们把某个项目从私有状态转为公开状态，但是这种情况下，原本应该禁止的Wiki页面仍然处于开启模式，那么，不仅仅是项目合作者或内部公司人员可以修改Wiki页面了，连任何Github用户都可以具备这样的操作权限。值得注意的是，项目所有者根本不会知道Wiki页面的任何修改操作，因为Github本身就没有这样的通知或告知配置。

## 漏洞影响

这种安全隐患的影响非常直观，可以总结为：

> 1、任意Github用户，可以对开启Wiki页面的项目，进行Wiki页面的任意修改；
>
> 2、恶意攻击者可以在这些可修改的Wiki页面中用markdown方式嵌入超链接、图片或其它内容；
>
> 3、这样很容易执行某些社工攻击，迷惑特定用户去安装某些恶意代码库，或是导航至攻击者控制的网络资源中去。
>
> 4、这种行为还可以导致某种程度上的名誉受损，恶意攻击者可以在Wiki页面中插入与公司规定不和谐的一些内容。  
>

## 缓解措施

对于一些大公司来说，他们在Github上部署有很多项目，貌似Github上没有能一键管理设置Wiki页面的功能，所以，只有通过勾选Github设置中的"Restrict
editing to collaborators only"（仅限项目合作者进行编辑），来进行限制了。（权限设置可参考： [Changing access
permissions for wikis](https://help.github.com/en/articles/changing-access-permissions-for-wikis)）

![ 一次对GitHub
Wiki页面的把玩测试](https://image.3001.net/images/20190312/1552382835_5c877b73bc3f1.png!small)其它方法还有：

> 除非需要，否则禁用Wiki页面；
>
> 提醒开发人员注意这个问题；
>
> 开发插件服务对Wiki页面的修改做出提醒；
>
> 用我开发的Wiki页面审计脚本进行审计 [github-wiki-> auditor.py](https://github.com/SmeegeSec/GitHub-Wiki-Auditor)  
>

禁用Wiki页面的方式为，去掉勾选的Wiki选项：  

## ![ 一次对GitHub
Wiki页面的把玩测试](https://image.3001.net/images/20190312/1552389428_5c879534304ee.jpg!small)

## Wiki页面审计脚本 [github-wiki-auditor.py](https://github.com/SmeegeSec/GitHub-Wiki-Auditor)

针对以上问题，我编写了一个python脚本，专门来用审计Github项目中的可编辑Wiki页面，它可以迭代查询相关Github账户上的所有项目，检查开启Wiki页面的状态，然后返回可编辑消息。它不会对Wiki页面做出修改，仅只是确认可编辑状态。

Usage: github-wiki-auditor.py [-h] --accounts_file ACCOUNTS_FILE [--username
USERNAME] [--password PASSWORD] [--output_file OUTPUT_FILE]

以下是对我个人Github项目的一个审计：（其中的account.txt包含了Github的账户密码）

![ 一次对GitHub
Wiki页面的把玩测试](https://image.3001.net/images/20190312/1552382853_5c877b85b22f2.png!small)

## 上报漏洞

这种问题当然不是Github的错了，但怎么报呢？我想很多大公司都存在类似问题，之后，我又对我的上述脚本进行了改进，尝试从开设漏洞众测的公司中来探测此类问题。最终，我从HackerOne、BugCrowd等开源渠道上收集了100多家存在此类问题的公司，从中选择一些影响力大的公司进行上报。

在向10多家公司上报了之后，反响并不太好，大部份的回复是说这种问题以前有人报过，而且不存在实际安全威胁。之后，我收到了两家公司安全团队的积极回应，他们没在第三方众测平台运行漏洞测试项目，所以，从这个层面上来说，这种公司不太会成为众多白帽的测试目标，而且对漏洞要求的门槛也相对较低。最终，我从其中一家公司收获了$500美金，从另外一家公司得到了致谢。

![ 一次对GitHub
Wiki页面的把玩测试](https://image.3001.net/images/20190312/1552383174_5c877cc681211.png!small)

 ***参考来源：[smeegesec](https://www.smeegesec.com/2019/03/auditing-github-repo-wikis-for-fun-and.html)，clouds编译，转载请注明来自FreeBuf.COM**

