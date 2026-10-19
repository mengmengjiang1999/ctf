*****本文原创作者：黑鸟，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

**WordPress主题供应商Pipdig被发现利用客户的服务器对竞争对手的网站发动DDoS攻击。安全研究人员jem分析了他们的代码后，找到了实锤进行了DDoS攻击的证据。**

然而Pipdig官方博客居然发表了一份声明称，其并没有发动DDoS攻击，声称代码是用来检查主题的许可密钥。并且它还迅速从其bitbucket库里删除了证据，然而证据已经永世留存，且广大网友和Wordfence公司给出了打脸证据。

![图片 1.png](https://image.3001.net/images/20190404/15543452242775.png!small)

下面为针对本次事件的分析过程。

## 事前分析

事件起因在于某位用户与安全分析人员Jem进行接触，称她的网站运行了一个她从WordPress主题提供商处购买的主题，表现得很奇怪：网站变得越来越慢。

经过分析人员的研究了pipdig Power Pack插件的源代码后，发现了pipdig以下行为：

> 1.正在使用其他博主的服务器对竞争对手执行DDoS；
>
> 2.正在操纵博主的内容，以更改指向竞争对手WordPress迁移服务的链接，以指向pipdig网站；
>
> 3.未经许可从博客网站收集数据，直接违反GDPR的各个部分；
>
> 4.正在使用收集的数据，通过更改管理员密码来访问博主的网站；
>
> 5.包含一个“kill switch”，它会删除所有数据库表；
>
> 6.在未经许可的情况下，故意禁用pipdig认为不必要的其他插件；
>
> 7.将管理通知和元框隐藏在WordPress core和仪表板中的其他插件中，这些插件可能包含重要信息。

下面将逐条进行代码分析。

## pipdig p3插件对竞争对手执行DDoS攻击

在/p3/inc/cron.php中，我们将以下代码块嵌套在WP Cron每小时运行一次的函数中：

![image.png](https://image.3001.net/images/20190404/1554345387617.png!small)

代码注释告诉我们这是“检查CDN（内容传送网络）缓存”。

然而这是在pipdigz.co.uk上的一个文件（id39dqm3c0_license_h.txt）上执行GET请求，该文件昨天早上在响应正文中返回了“<https://kotrynabassdesign.com/wp-admin/admin-ajax.php>”。

当响应主体不为空时，即当它包含该URL时，以下代码使用伪造的用户代理向响应中的admin-ajax.php URL发送第二个GET请求：

![image.png](https://image.3001.net/images/20190404/15543454311948.png!small)

所以，每天一个小时，没有任何人工干预，任何运行pipdig插件的博主都会向伪造的用户代理发送请求到'<https://kotrynabassdesign.com/wp-admin/admin-ajax.php>' 并附加一个随机数字符串。

 **这有效地在kotrynabassdesign.com的服务器上执行小规模DDoS（分布式拒绝服务）。**

Kotrynabassdesign是一个和pipdig类似的wordpress主题提供商：

![图片 1.png](https://image.3001.net/images/20190404/15543454757276.png!small)

我和Kotryna谈到了这些要求，以排除与pipdig的某种共同安排，她说：

在分析人员为了和Kotryna联系以排除是否和pipdig有合作之后，负责人说了下面的话：

“我的网络主机实际上遇到了很大麻烦，他们解释说我的admin-ajax.php文件受到了某种攻击[...]我可以确认我从来没有给过pipdig任何向我的服务器发出请求的权限。我也没有与他们建立伙伴关系或任何形式的联系。”

下图为详细对话，其中提及了有大量不同的IP访问了他们的网站。

![图片 1.png](https://image.3001.net/images/20190404/15543455387235.png!small)

请注意她的服务器日志文件中的引号，特别是pipdig插件中记录的确切用户代理字符串（'Mozilla / 5.0（Windows NT 10.0;
Win64; x64）AppleWebKit / 537.36（KHTML，如Gecko）Chrome / 60.0.3112.113 Safari
/537.36'）和admin-ajax.php的请求，和上面代码中提及的使用请求PHP的随机生成的编号字符串。

这个DDoSing的唯一例外是pipdig自己托管的客户 - 因为每小时cron首先运行此检查：

![image.png](https://image.3001.net/images/20190404/15543455846460.png!small)

大概是为了不减慢pipdig服务器的速度，并防止客户举报。

在Once Daily cron中还有第二个与此相同的请求，尽管目前还没发获取响应正文中的URL

![image.png](https://image.3001.net/images/20190404/15543456108278.png!small)

不知道这个txt指向的又是那家公司呢？

## pipdig操纵博客内容的链接，替换竞争对手的网址

在/p3/inc/functions.php中，307行以后：

![image.png](https://image.3001.net/images/20190404/15543456407316.png!small)

在这里，我们有pipdig的插件搜索提及“ blogerize.com ”的字符串，字符串分为两部分并重新加入。

当插件在博客的内容（帖子，页面）中找到指向blogerize.com的链接时，它们会被转换为“pipdig.co/shop/blogger-to-wordpress-migration/”的链接，即pipdig自己的博客迁移服务。

交换这些链接可以提高对pipdig的SEO好处，并且绝大多数博客都不会注意到切换器（特别是如果页面/帖子被编辑，blogerize的链接将像正常一样出现在后端）。

## pipdig收集数据和更改管理员密码（留后门）

/p3/inc/cron.php中：

![image.png](https://image.3001.net/images/20190404/15543456951484.png!small)

![image.png](https://image.3001.net/images/20190404/1554345713897.png!small)

这里的代码注释告诉我们这段代码将“检查要添加到导航栏等的新社交渠道”。

然而，此代码会在<https://pipdigz.co.uk/p3/socialz.txt>上执行GET请求，该请求需要响应中的电子邮件地址。

**当在GET请求正文中“收到”电子邮件地址时，该函数会检查Users表中是否存在该电子邮件地址，对其运行自己的“p3_check_social_links”函数，然后使用它来记录站点URL（包含在$
me中）在<https://pipdigz.co.uk/p3/socialz.php>的一个脚本。**

p3_check_social_links（）是/p3/inc/functions.php第195行中函数的包装器，它将用户密码更改为'p3_safe_styles'。

简单来说：当cron运行时，它会检查socialz.txt中的电子邮件地址。如果该电子邮件地址存在，它会将密码更改为该帐户，并将您的URL记录在socialz.php中，以允许访问任何有权访问该文件的人。

如果您的管理员电子邮件地址是由socialz.txt返回的，那么您将被从管理员帐户中删除。一位博主认为，这可以用来为pipdig用户提供博客支持。虽然这是可行的情况，但由于以下任何原因，这是一种完全令人讨厌的方式：

> 1.它是一个可以随时激活的后门（不仅仅是在需要支持时）。
>
> 2.我们不知道谁可以访问这些数据：大公司不能保密用户密码，我们为什么要信任pipdig？有一些方法和手段可以支持WordPress用户而无需重置密码。
>
> 3.这可能很容易被恶意手段劫持。
>
> 4.密码就是明文; 我可以监控socialz.txt文件以获得响应，并通过一些谷歌搜索轻松找到相应的博客到电子邮件地址并使用不安全的密码获取访问权限。

而cron.php种下面有一个函数是用来收集另一个竞争对手lyricalhost.com的客户URL列表：

![image.png](https://image.3001.net/images/20190404/15543457964573.png!small)![image.png](https://image.3001.net/images/20190404/15543458073108.png!small)

同样，该网站的域名做了分割处理。

## pipdig包含一个擦除博客的kill开关

在/p3/inc/cron.php中有以下内容：

![image.png](https://image.3001.net/images/20190404/15543458365250.png!small)

此代码在“<https://pipdigz.co.uk/p3/id39dqm3c0.txt>”上执行GET请求。如果它返回与您的博客URL匹配的博客URL，它将查找具有WordPress前缀的所有的表并逐个删除它们。

换句话说，如果您的网站位于他的杀戮名单上，您可以与每个帖子，页面，插件/常规设置，小部件内容，主题自定义，任何表单数据或其他内容亲吻然后说再见。

 **你最后一次完整备份你的WordPress数据库是什么时候？**

## pipdig禁用它认为不必要的插件

这里非常粗暴，在插件激活后的/p3/p3.php中，插件会停用一大堆插件而不会询问：

![image.png](https://image.3001.net/images/20190404/15543458748300.png!small)

![image.png](https://image.3001.net/images/20190404/1554345883731.png!small)

再往下，另一堆被停用，但这次是在admin_init上，每次加载后端面板时都会运行，这样就可以在运行pipdig的插件时重新启用它们：

![image.png](https://image.3001.net/images/20190404/15543459084032.png!small)

这已经是涉及基本道德问题了。

若有同学还想再次复现代码分析场景，可以下载下面这个压缩包。

    
    
    https://www.jemjabella.co.uk/wp-content/uploads/2019/03/p3_v4.7.3.zip

因为pipdig正在使用第三方更新程序而不是通过WordPress分发他的插件/主题，所以他可以在任何时候重新实现已经删除的代码，更糟糕的是，其可以推送更新。

如果您受此影响，即您有一个pipdig主题/插件，特别是如果您运行的是4.7.3或更早版本的p3 power pack，我建议您执行以下步骤：

> 1.备份您的WordPress文件和数据库；
>
> 2.激活备用主题；
>
> 3.取消激活并删除p3 power pack插件及其捆绑的任何补充插件；
>
> 4.检查您无法识别的任何用户并将其删除；
>
> 5.重置您的管理员密码；
>
> 6.安装WP Crontrol或类似的cron管理插件，并删除任何名为p3_的cron作业；
>
> 7.再次备份WordPress文件和数据库。

## 事后分析

上述便是涉及的关键恶意代码的分析，下面将是在事件爆发的后续发展。

开头的Pipdig的官方回应(<https://www.pipdig.co/blog/sad-times/>)，在这篇代码分析中来看，简直不堪一击，理由苍白。单一条，你为什么连人网站，你就已经解释不清了。

![图片 1.png](https://image.3001.net/images/20190404/15543460026794.png!small)

他是这么回应的：

我们现在正在研究为什么这个函数返回这个url。但是，它似乎表明某些“作者URL”已设置为“kotrynabassdesign.com”。
**我们目前不知道为什么会这样，或者网站所有者是否故意改变了这种情况。**

我们不知道，不要怪我，我不清楚，我甩锅给天！

![图片 1.png](https://image.3001.net/images/20190404/15543460321491.png!small)

然后，看见这些毫无诚意的声明的twitter网友以及wordfence彻底怒了，毕竟使用Pipdig的用户还是很多的，因此开始更进一步的扒皮和打脸，
**包括什么时候上传，什么时候删库，什么时候修改代码，都一一列举了出来。**

由于篇幅原因，感兴趣的同学请直接跳转该网站继续围观，毕竟这文章也一个很好的取证教学。

<https://www.wordfence.com/blog/2019/04/pipdig-update-dishonest-denials-erased-evidence-and-ongoing-offenses/>

![图片 1.png](https://image.3001.net/images/20190404/15543460608063.png!small)

而在这篇文章中还有一个关键证据，这个证据表明了，Pigdig不仅将使用了他们插件pipdig Power
Pack的用户用于ddos攻击，而且还将调用了他们的一些Blogger主题的JS代码的网站同样用于ddos攻击，关键证据分析如下。

在调查过程中，还发现了一些与他们的Blogger主题相关的可疑代码。此代码是Pipdig针对其竞争对手的可疑DDoS活动的一部分，并且在Pipdig否认任何此类行为四天之后一直有效，直到4月1日。

Pipdig的一些Blogger主题已被确认为对Pipdig的服务器进行外部JavaScript调用，特别是对脚本
hXXps://pipdigz[.]co[.]uk/js/zeplin1.js 调用：

![图片 1.png](https://image.3001.net/images/20190404/15543460881886.png!small)

上图显示了使用Pipdig的Blogger主题之一在网站的实时源中调用zeplin1.js。

该文件包含两行混淆的JavaScript代码。

![图片 1.png](https://image.3001.net/images/20190404/15543461133487.png!small)

当代码的第二行被反混淆并且可读时，可以得到以下内容：

![图片 1.png](https://image.3001.net/images/20190404/15543461323608.png!small)

从上述代码可以看出，其会设置实际目标地址值：

    
    
    hXXps://nullrefer[.]com/?hXXps://www.{competitor's domain}[.]com/{random endpoint}

NullRefer是一种服务，用于从请求中去除引用者数据到路径中的第二个链接。这意味着，Pipdig使用NullRefer隐藏请求的实际源页面到竞争对手的网站。这是可以理解的，因为所有这些引用都是运行Pipdig主题的网站。

每当访问者使用此脚本从Pipdig到达运行Blogger主题的任何站点时，他们的浏览器都会向其竞争对手的站点发出额外请求。此请求隐藏它来自的位置，在竞争对手的服务器上命中一个字面上随机的文件，并且对数据不执行任何操作。此行为不仅隐藏在这些网站的访问者中，也隐藏在这些网站的所有者中。

为了隐藏上述证据，Pipdig已经做出了额外的努力来隐藏这种行为的证据” zeplin1.js” 。

4月1日，Pipdig在他们的服务器上删除了该脚本的第二行。幸运的是webarchive上证据都存着。

![图片 1.png](https://image.3001.net/images/20190404/15543461721115.png!small)

这个脚本的编辑在接下来的几周里来了。有时，代码被删除了。而在一些时候，一个 **不同的竞争对手的域名** 出现了。

然而，最近报道的竞争对手的域名被添加的最近时间表明Pipdig 即使在被曝光后仍然存在可疑行为 。

3月13日，存在可疑的DDoS代码。

    
    
    http://web.archive.org/web/20190313140004/https://pipdigz.co.uk/js/zeplin1.js

请注意，此快照的目标与常见报告的竞争对手不同。

3月31日，代码不存在。

    
    
    http://web.archive.org/web/20190330081856/https://pipdigz.co.uk/js/zeplin1.js

4月1日，代码WAS出现。

    
    
    http://web.archive.org/web/20190401162700/https://pipdigz.co.uk/js/zeplin1.js

在4月1日的后续快照中，代码已被删除。

    
    
    http://web.archive.org/web/20190401185426/https://pipdigz.co.uk/js/zeplin1.js

如果Pipdig也取消了这些证据，目前已通过其他受信任的第三方制作了此代码的其他可验证副本。

而在4月2日，在此次更新时，Pipdig仍在托管滥用客户访问者的JavaScript。

![图片 1.png](https://image.3001.net/images/20190404/15543462455387.png!small)

该文件hXXps://pipdigz[.]co[.]uk/js/jquery.menu.min.js目前正在托管类似的混淆JavaScript，它正在针对他们的另一个竞争对手发出可疑的DDoS攻击。

存档：

    
    
    https://web.archive.org/web/20190402173508/https://pipdigz.co.uk/js/jquery.menu.min.js

可谓是屡教不改的经典模范了。

## 总结

所以不管是开源的还是付费的软件，我们都得小心谨慎。流氓到处都有，发现异常请及时排查举报，避免更多人受害。

更多详情请看参考链接：

[1] <https://www.jemjabella.co.uk/2019/security-alert-pipdig-insecure-ddosing-competitors>/

[2] <https://www.jemjabella.co.uk/2019/pipdig-your-questions-answered/>

[3] <https://www.wordfence.com/blog/2019/03/peculiar-php-present-in-popular-pipdig-power-pack-plugin/>

[4] <https://www.wordfence.com/blog/2019/04/pipdig-update-dishonest-denials-erased-evidence-and-ongoing-offenses/>

[5] <https://www.pipdig.co/blog/sad-times/>

***本文原创作者：黑鸟，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

