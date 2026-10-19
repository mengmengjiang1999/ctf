> 原创 BlusKing 合天智汇  
>

邮件钓鱼老生常谈，攻击手段也并不新颖。但对于网络安全工程师来说,“懂原理”和“会使用”是两个概念。会用，用得好不好，又是不同的层次。红队攻击要讲究攻击的效率，人力投入的性价比，以及能获得的数据结果的重要性。钓鱼攻击原理不难，但找到可用性高的框架或平台难。网上的钓鱼平台很多，例如king-phisher或者PhishingFrenzy等，但总存在这样那样的问题，比如缺少维护或者不易操作。现在为大家带来Gophish这款开源钓鱼平台，至今仍在维护，安装和操作都很简单。便于网络安全人员进行红队攻击、企业内部安全检查、安全测试等等，它还为安全报告的撰写提供了非常不错的细节素材

国内对它的介绍不是很多，官网有简要的手册，但它的实际操作中也会有一些坑出现，本文以开展一次邮箱钓鱼攻击的方式来介绍该工具的详细使用方法。

## 01GoPhish安装简介  

<https://github.com/gophish/gophish/releases>

打开上述链接下载最新版，Centos7下安装可以参考：

<https://bloodzer0.github.io/ossa/infrastructure-security/network-security/office-network-security/gophish/>

为了方便使用或者演示，可以直接下载windwos系统版本。Windows版本解压后直接打开gophishing.exe即可运行服务。它会在本地80端口开启钓鱼网站，因此如果不是内网钓鱼环境，需要将其架设在公网服务器上。后台配置入口开放在3333端口，默认用户名密码为：admin/gophish。

![v2-e1e5d884b71b161564858b557e3d725e_hd.j](https://pic3.zhimg.com/80/v2-e1e5d884b71b161564858b557e3d725e_hd.jpg)

![v2-f3006d715b9c8e83034ef7dd433be1e9_hd.j](https://pic1.zhimg.com/80/v2-f3006d715b9c8e83034ef7dd433be1e9_hd.jpg)

在还未对其配置的情况下访问本地80端口会显示页面没找到，这是正常现象：

![v2-8d4d59746995ec437a114bebab592276_hd.j](https://pic2.zhimg.com/80/v2-8d4d59746995ec437a114bebab592276_hd.jpg)

> 后台登录页面：  
>

![v2-e3586dd1aa8bc64b7bec5bd65d81051b_hd.j](https://pic4.zhimg.com/80/v2-e3586dd1aa8bc64b7bec5bd65d81051b_hd.jpg)

> 后台：  
>

![v2-027aedd0e04c011cfc84da94bc9ea653_hd.j](https://pic2.zhimg.com/80/v2-027aedd0e04c011cfc84da94bc9ea653_hd.jpg)

> GoPhish后台主要包括这几大模块：  
>

Dashboard 仪表盘，展示已发动的攻击情况和受害者信息。

Campaigns 在此配置每次要发起的攻击

Users& Groups 在此设置目标受害者的邮箱**

EmailTemplates 在此设置钓鱼邮件的模板

LandingPages 要在此设置钓鱼页面模板

SendingProfiles 在此配置发送钓鱼邮件的邮箱

## 02实战配置GoPhish  

接下来，我们以展开一次邮箱钓鱼攻击的方式来展示GoPhish的具体使用及相关配置。

> 1.配置发送邮箱  
>

首先配置邮件发送的服务器（SendingProfiles），可以使用163邮箱或者QQ邮箱（需要设置开启“SMTP服务”）。

![v2-bac3a745b3149428369103a94c9e5cc0_hd.j](https://pic4.zhimg.com/80/v2-bac3a745b3149428369103a94c9e5cc0_hd.jpg)

> 2、设定攻击目标  
>

然后，在“Users&
Groups”设置发送钓鱼邮件的目标邮箱。邮箱需要通过前期搜集，msf有相关的邮件模块auxiliary/gather/search_email_collector。

![v2-0a219e5808a9e98d53fb4584ecb412a2_hd.j](https://pic4.zhimg.com/80/v2-0a219e5808a9e98d53fb4584ecb412a2_hd.jpg)

> 3.创建钓鱼邮件模板  
>

设置好钓鱼邮件的发送方和接收方之后，便该设置钓鱼邮件的模板了，我们进入EmailTemplates模块设置钓鱼邮件。GoPhish不但支持手动编辑生成钓鱼邮件，也支持导入现有邮件内容。我们尝试从QQ邮箱中导出一封邮件，并导入GoPhish。选择Google发来的提醒邮件，然后“导出为eml文件”

![v2-c3e6f75792cdf3f478900419d40a0c53_hd.j](https://pic2.zhimg.com/80/v2-c3e6f75792cdf3f478900419d40a0c53_hd.jpg)

之后以文本形式查看该导出文件的内容，然后将其复制到导入邮件模板处。同时勾选ChangeLinks to Point to
LandingPage，这样当钓鱼攻击开始时，邮件模板中的链接会被替换为钓鱼网站的链接，然后才被发送。当目标受害人点击邮件中的链接时，就会跳转到钓鱼页面。钓鱼页面的配置会在之后提到。

![v2-01881f94521fbb955089aedb94598f59_hd.j](https://pic4.zhimg.com/80/v2-01881f94521fbb955089aedb94598f59_hd.jpg)

点击Import后可以预览html视图，展示已经被导入的邮件，如果内容有误或者需要修改，可以点击source直接修改html源代码。

![v2-42bd0f567086a5222649df8c02af35e3_hd.j](https://pic2.zhimg.com/80/v2-42bd0f567086a5222649df8c02af35e3_hd.jpg)

可以勾选上AddTrackingImage，它会在源代码中插入一个图片标识来检测改邮件是否被打开。当邮件被打开时，邮件中的图片标识代码会自动向GoPhish服务器请求图片，由此，就可判断该邮件已经被目标人员打开。AddFiles则是给邮件添加附件。

![v2-85500caaa0cf478540c5bb99a2d056da_hd.j](https://pic3.zhimg.com/80/v2-85500caaa0cf478540c5bb99a2d056da_hd.jpg)

> 4.伪造钓鱼网页  
>

配置好钓鱼邮件后，就可以进入LandingPages模块来新建钓鱼网站页面。它同样支持导入网站功能，可以对目标网页进行克隆。但因为网页代码中通常会存在以相对位置定义路径的资源，因而无法真正的克隆出一个一模一样的网站。需要手动修改源代码来模仿真实的网站。下面以一个简单页面做演示，点击“Source”旁的按钮可以预览页面的显示效果。

![v2-14cda1c32ad0caffcd5a3e2c99aca4c2_hd.j](https://pic4.zhimg.com/80/v2-14cda1c32ad0caffcd5a3e2c99aca4c2_hd.jpg)

页面预览：

![v2-9733a725ca0b879457f10e6490e5423f_hd.j](https://pic3.zhimg.com/80/v2-9733a725ca0b879457f10e6490e5423f_hd.jpg)

勾选CaptureSubmitted
Data和CapturePasswords，这样当受害者在钓鱼页面尝试登陆并提交信息的时候，服务器会把相关数据保存下来。Redirectto
是指用户做完提交操作后，页面跳转的地址，可以指向真正的官网登录页面，这样能减少受害者发现自身被钓鱼的可能性。

> 5.攻击  
>

最后一步便是配置Campaigns。如下图，填写好攻击的名称，选择钓鱼邮件模板，选择相应的钓鱼页面，目标邮箱，和发送邮箱。需要填上GoPhish服务端的地址，在钓鱼攻击开始前，这个地址会将先前钓鱼邮件模板中的链接替换。这样当目标受害人收到邮件并点击邮件中的链接时，就会跳转到服务端展示的钓鱼页面。当然我们也可以不填写GoPhish服务端所在的地址，转而输入其他搭建的钓鱼服务器地址。

![v2-424d3f98a4329cfe6ecf9c4bc75dc461_hd.j](https://pic4.zhimg.com/80/v2-424d3f98a4329cfe6ecf9c4bc75dc461_hd.jpg)

开始功能攻击之后就可以在Dashboard监控进展，静静的等待鱼儿上钩了：

![v2-2e41f60ed86e1c691e451c31fb5e6bf9_hd.j](https://pic4.zhimg.com/80/v2-2e41f60ed86e1c691e451c31fb5e6bf9_hd.jpg)

## 03受害者视角展开  

接下来我们以受害者的视角来看这起钓鱼攻击事件，首先是查看邮件收件列表，收到了钓鱼邮件，并没有发现可疑的地方。

![v2-7c403f78dc21903fb07311bf6ab008cc_hd.j](https://pic4.zhimg.com/80/v2-7c403f78dc21903fb07311bf6ab008cc_hd.jpg)

接下来打开邮件，邮件内容很正常，但邮箱地址很明显是163邮箱，这会降低钓鱼攻击的成功率。实际攻击中，可以注册与受害者邮箱域名类似的域名，然后搭建邮件服务器，再以此服务器来发送钓鱼邮件。例如google的官方邮箱是xx@accounts.google.com，那么我们就可以注册g00gle.com这样的域名来发送邮件进行伪装。

接着点击邮件内容中的“查看活动”，便会跳转到GoPhish服务端配置好的钓鱼页面。随意输入数据然后提交，GoPhish服务端会抓取受害者提交的数据，并自动跳转到真正的谷歌官网（先前设置好的）。此时，一个完整的攻击链就完成了。

![v2-f693c0831a80976f8311dcad5f246697_hd.j](https://pic4.zhimg.com/80/v2-f693c0831a80976f8311dcad5f246697_hd.jpg)

![v2-7ed72d63a9309f90495c2de6b905fc64_hd.j](https://pic2.zhimg.com/80/v2-7ed72d63a9309f90495c2de6b905fc64_hd.jpg)

## 04结果展示  

再回到攻击者的后台，此时我们可以在Dashboard看到受害者打开了邮件，并点击了链接，而且提交了数据。

![v2-408df609b90fb04178cb11fb39737d1f_hd.j](https://pic1.zhimg.com/80/v2-408df609b90fb04178cb11fb39737d1f_hd.jpg)

除此以外，还能看到受害者提交的具体信息，他所使用的系统、浏览器版本等各种细节。方便相关安全人员撰写报告。

![v2-eccb8c05f3e6cc4e9b6265fa0ff1f97a_hd.j](https://pic4.zhimg.com/80/v2-eccb8c05f3e6cc4e9b6265fa0ff1f97a_hd.jpg)

项目地址：<https://github.com/gophish/gophish>

官网：<https://getgophish.com/>

引用：

<https://bloodzer0.github.io/ossa/infrastructure-security/network-security/office-network-security/gophish/>

合天网安实验室同款实验get实验：CobaltStrike之钓鱼攻击

[实验:CobaltStrike之钓鱼攻击(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECIDf4cc-5f6c-4683-b632-bc0abdb15462)（点击链接了解详情）

钓鱼攻击使用电子邮件或者恶意网站引诱人们提供个人信息(用户名、密码、金融信息等)。通过该实验了解使用cs进行钓鱼攻击。）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

