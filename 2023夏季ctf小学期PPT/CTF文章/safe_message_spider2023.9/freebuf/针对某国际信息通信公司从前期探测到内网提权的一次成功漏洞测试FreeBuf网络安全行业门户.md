![](https://image.3001.net/images/20200314/1584178869_5e6ca6b543666.jpg!small)

**本文记录的是作者针对某国际大型信通公司进行的一次漏洞测试，测试过程中，作者通过敏感信息泄露、错误配置、RCE等多种线索组合，最终成功实现了内网应用系统提权，可获取到目标公司内网系统的相关资料和应用数据，漏洞提交后收获了$9000的奖励。作为招式的分享学习，我们一起来看看。**

本文作者为印度尼西亚安全专家YoKo Kho，漏洞众测平台Bugcrowd MVP，具备12多年行业的资深信息安全Web漏洞挖掘和渗透测试经验，
拥有OSCP、SISE（iOS Application Security Expert）、道德黑客CEH等多项技能认证。《Bug Hunting
101》作者。

## 从Github发起探测侦察

前期，我已经收集了目标公司将近数千的子域名，但有了这些东西，我却有点无从下手，于是乎我只有从原始的目标公司个人信息收集入手。我尝试从Github上去发现一些目标公司开发人员留下的蛛丝马迹，这不这个视频-[Github
Recon and Sensitive Data
Exposure（从Github平台探测发现敏感数据）](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=l0YsEk_59fQ)给了我一些启发。

其中主要讲述的是如何从Github被上传代码库中发现凭据类敏感信息，然后去验证受影响公司的相关服务，测试是否有效，但是，从中我也得到另外的信息收集思路。我接下来做的是：

1、收集目标公司泄露在Github上的密码凭据（不管是否有效），然后尝试去发现密码规律，这样做的原因是从中或许能发现管理员在用户注册分配密码时预先会给定的一些默认密码，这种思路在后续我们会用到。非常不错，我幸运地在Github平台收集到了与目标公司相关的近50个密码凭据信息：

![](https://image.3001.net/images/20200314/1584177011_5e6c9f738c9ad.png!small)

2、收集目标公司相关的IP地址。这样做主要有几种考虑：一是我们可以从一些公开的Github漏洞报告中去发现目标公司相关的IP地址，因为白帽们提交的漏洞报告多少总会包括一些细节分析，才会被众测平台接收，虽然有些包含目标系统内部资产信息的漏洞有时候也会存在误报可能，但是我们可以从这些公开披露的漏洞中去寻找一些IP线索，总结规律，尝试从中发现一些开发代码库或系统信息。这不，我从bugcrowd平台就发现了自己提交的与目标公司Github相关的5个P1严重级漏洞：

![](https://image.3001.net/images/20200314/1584177043_5e6c9f937b0d6.png!small)

二是这样方便后续我们做内网探测时，可以更快地连接到内部网络相关的系统资产；三是通过目标公司泄露在Github上的信息，可以间接判断出目标公司的开发习惯和开发文化，比如我可以通过上述信息在两三个小时就能弄清其大概的开发框架和内网应用。最后，这样做也能从代码审计层面去发现目标公司在用服务的潜在问题。执行了以上几个前期步骤后，就可以针对目标公司收集到很多的线索信息。

## 利用Github进行密码探测

之前那个视频Github Recon and Sensitive Data
Exposure中，涉及到了密码安全问题，主要是：一些公司内部开发人员在使用类似Github的协同代码平台时犯下的错误，比如，会把包括相关密码信息的代码直接上传到Github上，这要么是太大意，要么是完全不知道Github有“隐私”功能，那么这种错误就有可能被恶意攻击者发现并利用。对于想要进行内网测试的攻击者来说，这种开发错误还是非常有用的。

接下来，我们需要做的就是登录我们自己的Github账号，用以下搜索请求进行搜索：

    
    
    password “.target.com”
    
    target.com “password_value_here”

target.com是目标公司的网站域名，当然“password”字段也可替换成telnet、ftp、ssh、mysql、jdbc、oracle等特定关键字。虽然我不太了解Github的查询机制，但利用这两个搜索语法我发现了很多有用的东西。

如果你通过上述语法发现某些项目代码存在密码泄露，那么，可以继续深挖，比如可以针对特定代码库和特定开发者用户进行搜索查询：

![](https://image.3001.net/images/20200314/1584177188_5e6ca0244d3a4.png!small)

![](https://image.3001.net/images/20200314/1584177194_5e6ca02ae254a.png!small)

或者再找找该开发者的其它代码库。如果这些搜索方式都没啥发现，那么我们可以去找找哪些与当前项目开发者或拥有者存在开发协作关系或互动，然后再针对这个用户再继续用上述语法搜索一遍。以下为我总结的Github信息收集（Recon）流程图：

![](https://image.3001.net/images/20200314/1584177210_5e6ca03a7d6f2.png!small)

## 活用Google Dork搜索语法收集信息

接下来，我尝试用Google
Dork搜索，这里我用到的语法关键字是目标公司的一个内部非公开子域名和相关密码模式，该内部子域名是我在第一阶段Github平台中发现的，当时通过它我又关联到了好几个子域名。由于这些子域名无法通过外网访问到，我猜想这些子域名是目标公司用于开发之用的。

虽然这些子域名是内部域名，但我还是想尝试看看Google大法的神奇，于是就用以下Google Dork语法进行了搜索：

    
    
    site:*.subx.target.tld AND intext:'one_of_password_pattern_value_here'

竟然真的有所发现！从中我发现了目标公司内部域名和服务端相关的大量密码凭据（如FTP/SSH）和内部IP地址等信息，尽管它们需要从内网才能访问或利用，但也算有所发现。

![](https://image.3001.net/images/20200314/1584177326_5e6ca0ae08ac6.png!small)

通过调整搜索关键字，如已知的IP地址、产品应用(如Oracle、MySQL、MSSQL等） 、服务名称 (FTP, SSH,
DB等）和其它登录键值字段（如password、pwd、pass、username、userid等），或与登录相关的dashboard、cms等内容。

![](https://image.3001.net/images/20200314/1584177344_5e6ca0c082ffd.png!small)

另外，通过Google大法，我还在某些众测平台披露的漏洞报告中发现了目标公司相关的4个账号，在披露漏洞中这4个账号都可以访问到顾客数据，而且这些账号都使用了我在Github中发现的密码模式。

![](https://image.3001.net/images/20200314/1584177370_5e6ca0da3be5c.png!small)

另外，我还发现了不在测试范围内的另一超级管理员账号（super
admin）,该账号信息涉及目标公司客户的多项交易数据，可惜它所属于的系统并不在于我渗透测试范围内，为了保密只放出具体漏洞报告示例，账号信息就不截图了。

## 通过旧版本Atlassian Crowd应用发现未授权RCE漏洞

手上有了一堆内网信息和其密码配置模式，但还缺少一个有效的内网访问渠道。为此，我又想从其子域名中发现更多线索，这次我用到了域名和主机可视化发现工具aquatone。之后我发现了目标公司在用的一个老版本服务端，从其显示线索中来看，只有一些带有类似
1st words、2nd words、3rd
words和crowd关键字的可点击链接，其中的“crowd”引起了我的注意，于是我点击了“crowd”的关键字链接，然后它跳转到了一个Atlassian
Crowd应用的子域名网站，从中注意到是2017年的版本。

![](https://image.3001.net/images/20200314/1584177489_5e6ca151803c3.png!small)

面对该Atlassian Crowd应用，我想有三种可利用方式：

> 可测试一些用过的账户密码；
>
> 可测试发现未修复的补丁；
>
> 可测试发现配置型漏洞。

当然，首先可用Google来搜索其漏洞利用方式：

![](https://image.3001.net/images/20200314/1584177520_5e6ca1709f19f.png!small)

经过一番查找，我发现了该版本的Atlassian
Crowd存在CVE-2019-11580漏洞，之后就是看看该漏洞是否存在公开的利用代码（exploit），然后我在Github中发现了这个远程代码执行（RCE）的exploit：

![](https://image.3001.net/images/20200314/1584177543_5e6ca187d58fc.png!small)

接下来的就是调试当前Atlassian
Crowd应用是否存在该漏洞了。可以在其/admin/路径下的上传操作端uploadplugin.action点击查看，如果当前Atlassian
Crowd应用回显了一个错误消息“HTTP Status 400 – Requires POST”
，那么这种情况说明它是存在该RCE漏洞的，也就是说其uploadplugin插件可以被未授权利用。

![](https://image.3001.net/images/20200314/1584177566_5e6ca19ede502.png!small)

## RCE代码执行

现在，我们从<https://github.com/jas502n/CVE-2019-11580>下载漏洞利用代码CVE-2019-11580.py，以当前Atlassian
Crowd应用为目标，它确实存在CVE-2019-11580漏洞，并反弹回了一个webshell，如下：

![](https://image.3001.net/images/20200314/1584177617_5e6ca1d1d729b.png!small)

接着，就可以通过浏览器浏览<http://xx.xx.xx.xx/crowd/plugins/servlet/exp?cmd=command_here>，访问到这个webshell了，当然其中的command_here可以替换成其它系统命令。如下：

![](https://image.3001.net/images/20200314/1584177637_5e6ca1e5470fc.png!small)

所以，总结来看，该漏洞利用有三个好处：

> 1、无需任何用户账户密码；
>
> 2、RCE是以root身份执行的；
>
> 3、该Atlassian Crowd应用无任何安全防护。

但这还不够，我们需要一个能与目标系统执行交互的Webshell！

这里，我的想法是通过我的Attacker主机，实现对目标应用系统的操控交互。通常我用的是PentestMonkey上提供的反弹Shell，但可惜的是，其中的交互命令在与我的Attacker主机连接执行时没有任何回连显示，很可能是目标Web应用过滤了如>
& 以及‘ “这些特殊字符。

为此，我只有在我的Attacker主机放置了一个回连python脚本reverse.py，然后通过之前的RCE命令迫使目标Web应用来对它执行下载，然后再通过我的Attacker主机连接它，实现控制。具体的python回连脚本reverse.py如下：

![](https://image.3001.net/images/20200314/1584177846_5e6ca2b60f254.png!small)

目标Web应用从我的Attacker主机中下载python回连脚本reverse.py：

![](https://image.3001.net/images/20200314/1584177861_5e6ca2c54ef10.png!small)

就这样，我们就向目标Web应用系统中植入了一个反弹脚本，之后，需要对该脚本文件进行chmod权限修改以便我们能访问执行，如可以把它修改为700:

![](https://image.3001.net/images/20200314/1584177878_5e6ca2d67206a.png!small)

![](https://image.3001.net/images/20200314/1584177989_5e6ca345e3867.png!small)

目标Web应用下载了reverse.py后，我们这边的Attacker主机需要设置一个监听端口：

    
    
    $ nc -lvp <our_port>

然后，用之前的RCE
shell使目标Web应用执行脚本reverse.py。但是，这还不算真正意义上的交互shell，如果把它设置为伪终端方式就更好了，所以，可以在终端窗口中执行以下python命令实现脚本的伪终端显示：

    
    
    python -c 'import pty;pty.spawn("/bin/bash")'

到此，我们就获得了目标Web应用系统的一个控制shell：

![](https://image.3001.net/images/20200314/1584178007_5e6ca357ddc88.png!small)

![](https://image.3001.net/images/20200314/1584178059_5e6ca38b5ff33.png!small)

通过运行reverse.py，我们就能无障碍地去连接目标Web应用系统中的数据库或其它运行服务了：

![](https://image.3001.net/images/20200314/1584178076_5e6ca39c5377a.png!small)

## 内部系统探测

这里我们获得的RCE，一个有利因素就是该服务器位于目标公司的内部网络中，当在上述交互webshell是去ping一些目标公司的公开系统时，返回响应中得到的是一些内部IP地址。也就是说，我们在这个全球知名大型信息通信技术公司的内部网络系统中实现了据点潜伏。之前阶段我们收集获得的大量内部网络信息，在这里就可派上用场了。但是，为了不造成严重影响破坏，不能再深入了，就点到为止吧。

> 声明：以上主要展示前期信息收集对后期渗透测试的重要性，最终说明问题即可收手，另外这些测试都是在允许授权之内开展的。

最终，尽管发现的该漏洞不在众测范围之内（out-scope），但确实是一次奇妙的渗透之旅。能以信息收集、目标分析和线索映证测试的方式，从知名信通公司的外部网络中打到内部系统，并实现RCE，已经非常不简单了。就像我们白帽平时开玩笑说的“要在漏洞测试中发现RCE漏洞，简单就是天方夜谭”。之后我及时上报了该漏洞，并收到目标公司的快速响应。

![](https://image.3001.net/images/20200314/1584178202_5e6ca41ae1089.png!small)

![](https://image.3001.net/images/20200314/1584178231_5e6ca437d88c8.png!small)

## 连接内部Crowd应用数据库

上述因为目标公司部署有Atlassian Crowd应用的系统存在漏洞，导致了最终我的RCE。那或许有人会问，能不能尝试登录其它的Atlassian
Crowd应用或相关数据库呢？

我们也来看看。经测试发现，为配合Atlassian
Crowd的使用，目标公司在该服务器上也安装了Atlassian协同办公组件Confluence，而我对Atlassian Crowd和Atlassian
Confluence的协同工作机制根本不懂，但我在netstat命令下观察到了数据库连接，所以我想其中肯定涉及到一些密码信息的存储。经过对Atlassian
Confluence的研究分析，我发现其密码信息存储在<confluence_home>/confluence.cfg.xml文件中。

![](https://image.3001.net/images/20200314/1584178279_5e6ca467daeeb.png!small)

使用locate命令，我在目标系统中发现了confluence.cfg.xml文件，更高兴的是，其中的密码信息完全是明文：

![](https://image.3001.net/images/20200314/1584178338_5e6ca4a2e7ce3.png!small)

就这样，利用其中的密码信息，我成功登录到了其相关数据库：

![](https://image.3001.net/images/20200314/1584178370_5e6ca4c276dc7.png!small)

登录了上述Crowd数据库之后，我就在想能不能把这个登录密码进行修改，换成我们自己的呢？我觉得应该是可行的，因为Atlassian在官方文档里有密码替换更改的说明，在如下介绍中，我们可以用哈希过的字符串去替换管理员原来的密码。

![](https://image.3001.net/images/20200314/1584178392_5e6ca4d8c686a.png!small)

由于这是一个漏洞测试项目，因为没有密码修改授权，所以我们不能擅自进行这种密码替换更改。但如果在真实的攻击场景下，攻击者完全可以实现这种操作，对系统造成影响。那如果不能修改替换密码，我们可以选择创建一个新账户的方法来测试。经过查找发现，只要知道管理员账号密码，就可以通过REST请求方式来创建Atlassian
Crowd的新账户：

![](https://image.3001.net/images/20200314/1584178437_5e6ca505ba6f3.png!small)

![](https://image.3001.net/images/20200314/1584178470_5e6ca52691c96.png!small)

![](https://image.3001.net/images/20200314/1584178523_5e6ca55b601ee.png!small)

上述操作的请求格式如下：

    
    
    curl -i -X POST<http://subdomain.target.com/crowd/rest/usermanagement/latest/user?username=your_new_user_here>-H 'Content-type: application/json' -H 'Accept: application/json' -u crowd_administrator_username_here:crowd_administrator_password_here -d'
    
    > {
    
    > "email": "your@email_here.tld",
    
    > "name": "your_new_user_here",
    
    > "password": {
    
    > "value": "your_new_user_password_here"
    
    > }
    
    > }
    
    > '

> your_new_user_here = 将要创建的账户名
>
> crowd_administrator_username_here = Crowd的管理员名称
>
> crowd_administrator_password_here = Crowd的管理员密码
>
> your@email_here.tld = 将要创建账户的绑定邮箱
>
> your_new_user_password_here =将要创建账户的密码

之后，进行账户激活，我们就可成功创建一个新的Crowd账户：

![](https://image.3001.net/images/20200314/1584178591_5e6ca59f7c999.png!small)

然后进行登录：

![](https://image.3001.net/images/20200314/1584178608_5e6ca5b0f111b.png!small)

## 经验总结

1、前期的信息收集（Recon）至关重要，通过其我们可以了解目标应用的API工作机制和开发环境等因素。在此借用大牛@Mongobug和@NahamSec对Recon的原话：

“前期信息收集（Recon）不仅可以发现目标系统的资产环境和过期版本信息，还可以掌握相关的应用架构，并获取到一些很难探测到的功能特性。因此，成功的测试需要在前期信息收集和实际渗透过程中保持一种平衡。”

![](https://image.3001.net/images/20200314/1584178652_5e6ca5dc46729.png!small)

2、不要丢掉任何你搜集到的数据和信息，说不定在之后的测试中可以发挥作用。该次测试中，我就是综合利用了前期收集的有用线索，最终成功在后续阶段实现了突破验证了RCE漏洞，收获了$9,000的奖励；

3、享受你的每次漏洞测试或渗透测试活动，不要太过于看重赏金（Bounty）。尽量去测试那些合法或官方的项目，多动手多思考多学习，这样才能快速地提高你的测试技能，扩展你的知识面；

4、可以多参与一些官方的漏洞责任披露项目，从中好好练手，储备经验；

5、高手和大牛都不是天生的，他们曾经也是菜鸟。

>
> NOTE：详细技术报告，请[点此下载](http://firstsight.me/fia07a53c4ec63d2b0d47fe27ea2645d82f8c98648/%5BENG%5D%20The%20Story%20about%20How%20I%20Finally%20could%20Got%20into%20an%20Internal%20Network%20v03.pdf)PDF版本。

**参考来源：[firstsight](http://www.firstsight.me/2020/02/from-recon-to-optimizing-rce-results-simple-story-with-one-of-the-biggest-ict-company-in-the-world/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

