原创：h0x合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

![v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.w](https://pic2.zhimg.com/80/v2-b6ac4acb391e97c8ef3bf1f3f5fe9a62_hd.webp)

##  前言  

上次记录过一篇提权到内网初探，但感觉收尾有些仓促，最近刚好遇到了很好的实战过程，故本篇为过程记录复现，着重围绕着目标进行测试。希望看完本篇能给您带来一些思路或启发。

假设本次测试前提为：仅知道刘书源为某学校的学生，目的是尽可能的收集刘书源的信息，以此进行展开。

PS：截至投稿前，已将漏洞提交eduSRC平台并验证已完成修复。

![v2-10e6c58b4c92b5f2d2a2997f12a5aa98_hd.w](https://pic4.zhimg.com/80/v2-10e6c58b4c92b5f2d2a2997f12a5aa98_hd.webp)

![v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.w](https://pic4.zhimg.com/80/v2-a17f39b0263ccd7b5082f9456ca34bcd_hd.webp)

##  内网资产嗅探  

首先通过谷歌语法搜索该学校的学号。这是个众人皆知的小技巧，通过收集的学号，可以生成学号字典去爆破弱口令用户。如下获得了该校的学号格式。

![v2-4b0a348804e67ab7f38347cfb69c34f8_hd.w](https://pic1.zhimg.com/80/v2-4b0a348804e67ab7f38347cfb69c34f8_hd.webp)

通过以下公告通知，获取到默认的密码为身份证号的某段构成，故此处获得了学号之后，可以考虑如何获取学号对应的身份证号码。

![v2-ce3ab6cf8329c10502a6ea9db99546ce_hd.w](https://pic2.zhimg.com/80/v2-ce3ab6cf8329c10502a6ea9db99546ce_hd.webp)

![v2-c437bd72ffdd984df8cd0f803db0316c_hd.p](https://pic3.zhimg.com/80/v2-c437bd72ffdd984df8cd0f803db0316c_hd.png)

弱口令爆破

通过上述获取到的学号生成字典，找到一处无验证码的学生系统进行爆破。

![v2-c30bb144d76f3d07a9a0fdc76fcde808_hd.w](https://pic1.zhimg.com/80/v2-c30bb144d76f3d07a9a0fdc76fcde808_hd.webp)

![v2-65897d474bb41fe5024dcc7a6a742c8c_hd.w](https://pic1.zhimg.com/80/v2-65897d474bb41fe5024dcc7a6a742c8c_hd.webp)

![v2-e68d359313b3f33a10a0ff47f787c2ff_hd.w](https://pic1.zhimg.com/80/v2-e68d359313b3f33a10a0ff47f787c2ff_hd.webp)

如上成功爆破出尾数50的学号存在弱口令，通过弱口令可以登录该系统，登录后可以获取到该学生的身份证号码。此时，我们掌握了一个学号、姓名及身份证号，如果时间足够可以多去爆破几个。

但此时并不知道刘书源的学号，若能得到刘书源的学号应能获取更多的信息。

通过对该学校网站继续浏览，发现网站存在VPN系统，此处为突破口。

![v2-8eca10306f15d37895c9e4a1e29a2feb_hd.w](https://pic4.zhimg.com/80/v2-8eca10306f15d37895c9e4a1e29a2feb_hd.webp)

内网资产嗅探

通过上述获取到的学号+身份证后6位成功登录VPN系统，若登录不成功，则可以多爆破几个学号，尝试通过他们的身份证号进行登录，总有学生没有改默认密码的。

![v2-8042fc55ce812ff66b48a80aa667b4c8_hd.w](https://pic4.zhimg.com/80/v2-8042fc55ce812ff66b48a80aa667b4c8_hd.webp)

![v2-64ed375cede9132e0b352bee71c6bcaa_hd.w](https://pic2.zhimg.com/80/v2-64ed375cede9132e0b352bee71c6bcaa_hd.webp)

如上成功登录VPN系统，进入学校内网。通过对内网的资产进行了大概的浏览及信息收集，发现存在以下IP段：

192.168.25x.0

192.168.4.0

192.168.5.0

扫描该网段开放WEB服务的服务器，同时后台扫描SQLServer及MySQL的弱口令。如下，内网还是存在很多的网站服务器。

![v2-4ddc69475b238fdc2eafe832d36d3575_hd.w](https://pic1.zhimg.com/80/v2-4ddc69475b238fdc2eafe832d36d3575_hd.webp)

通过对几个网段的Web系统的逐个浏览测试，发现主要存在以下漏洞：

1、在线考试管理系统存在SQL注入

此系统最有可能存在刘书源的学号信息，故对此系统进行检测。

![v2-9b297801a28169baf6be2a3cd96eca10_hd.w](https://pic4.zhimg.com/80/v2-9b297801a28169baf6be2a3cd96eca10_hd.webp)

抓包使用Sqlmap进行测试，一片红证明存在安全防护软件。

![v2-03752269e9e50667d92e882cf6c2b738_hd.w](https://pic1.zhimg.com/80/v2-03752269e9e50667d92e882cf6c2b738_hd.webp)

![v2-c3c3ccf2074ab51c47624f7f383b31e5_hd.w](https://pic1.zhimg.com/80/v2-c3c3ccf2074ab51c47624f7f383b31e5_hd.webp)

![v2-8d9169f34c52f8aa3cd9d7d0386e46ec_hd.w](https://pic4.zhimg.com/80/v2-8d9169f34c52f8aa3cd9d7d0386e46ec_hd.webp)

2、资产管理系统存在SQL注入

用户名处加单引号报错

![v2-1ed49bf74e1c9f8f1bc2fc767f6943e8_hd.w](https://pic2.zhimg.com/80/v2-1ed49bf74e1c9f8f1bc2fc767f6943e8_hd.webp)

![v2-eabdf8b836095a2d61652632d9c13885_hd.w](https://pic2.zhimg.com/80/v2-eabdf8b836095a2d61652632d9c13885_hd.webp)

抓包使用Sqlmap进行测试

![v2-d9a9064d1aea27e1a14dafc1e79f5a6c_hd.w](https://pic4.zhimg.com/80/v2-d9a9064d1aea27e1a14dafc1e79f5a6c_hd.webp)

![v2-eabc42c39d3bb627b1f5c5cecfc4c0c8_hd.w](https://pic3.zhimg.com/80/v2-eabc42c39d3bb627b1f5c5cecfc4c0c8_hd.webp)

同样抓包使用Sqlmap进行测试，但此处未被拦截。

分析后发现该站点和上面站点不是一个网段，考试管理系统的是192.168.25x.0网段，而当前系统是192.168.4.0网段，可能是WAF的部署位置缺陷导致未防护到192.168.4.0网段。推测其大概网络拓扑图如下：

![v2-85f728a167cead67b5d5e2c016445c50_hd.w](https://pic4.zhimg.com/80/v2-85f728a167cead67b5d5e2c016445c50_hd.webp)

虽然当前注入点为SA权限，但不支持os-shell，也未找到后台管理页面，且该系统很大可能不存在我们需要的信息。此处暂且先放一边。

3、后台弱口令

发现一系统后台弱口令，成功登录后，并未有可以利用的功能点，且该站点有WAF进行防护。

![v2-5cfe3de1a72536d52449564bdb1e2ad4_hd.w](https://pic2.zhimg.com/80/v2-5cfe3de1a72536d52449564bdb1e2ad4_hd.webp)

此时服务扫描那一块已经扫描完成，扫到存在sa弱口令的服务。

4、SA弱口令

如下，发现两台存在弱口令的服务器，且为192.168.25x.0网段。可以通过获取该服务器权限建立代理，然后去跑同网段考试系统的注入点，即可绕过WAF的防护，进而可获取数据库的信息。

![v2-32ff8009035204df89e81be3b9960239_hd.w](https://pic2.zhimg.com/80/v2-32ff8009035204df89e81be3b9960239_hd.webp)

通过SQL工具连接后可以执行cmd，且当前权限为system权限。

![v2-dc87d776ae8f04236b91bc46377e1976_hd.w](https://pic2.zhimg.com/80/v2-dc87d776ae8f04236b91bc46377e1976_hd.webp)

通过以下命令查找RDP服务的端口号

tasklist/svc | find "TermService"

netstat-nao | find "3220"

发现当前RDP服务的端口号为8080

![v2-55f45e0d0326a7f8efa57c6ebbc2e517_hd.w](https://pic2.zhimg.com/80/v2-55f45e0d0326a7f8efa57c6ebbc2e517_hd.webp)

![v2-da721f0308ee789666ee99ab8ab47ae7_hd.w](https://pic2.zhimg.com/80/v2-da721f0308ee789666ee99ab8ab47ae7_hd.webp)

![v2-c6c16026f275fa46a57e69904b3faf61_hd.w](https://pic3.zhimg.com/80/v2-c6c16026f275fa46a57e69904b3faf61_hd.webp)

直接远程内网IP:8080，提示访问拒绝，表示VPN并未对外开放8080端口的访问。本想通过reGeorg脚本建立代理，但是80端口访问为报错，测试默认网站路径写入文件也404。测试本服务器为纯内网环境，不可访问互联网。

![v2-bf6d294526f12eab48e6dc3b64acae96_hd.w](https://pic3.zhimg.com/80/v2-bf6d294526f12eab48e6dc3b64acae96_hd.webp)

端口复用及Socks代理

通过对当前环境的分析，目前已经获取了25x的服务器的system权限cmd，想通过这台服务器建立代理，及登录服务器，在服务器上进行同网段的扫描探测，以此来绕过安全设备的防护。

1、端口复用

但当前是通过VPN连接到内网，且VPN仅对外开放了某些特定端口。此时我首先想到的是利用端口复用，正好当前的80端口的网站为报错页面，于是上传了利用工具。

![v2-1316a22bfb86e0b24312a4ad1144e1ce_hd.w](https://pic3.zhimg.com/80/v2-1316a22bfb86e0b24312a4ad1144e1ce_hd.webp)

在目标服务器上执行以下两条命令，此时相当于把本地的8080端口映射到80端口上。

c:\wmpub\drivers.exe

c:\wmpub\Changeport.exelocalhost 8080

执行上述两条命令后，在本地nc目标IP80

发送chkroot2007

即开启端口复用，80端口的web服务会无法访问。

![v2-6c08fd00f64623a993f77aa3c8d81796_hd.w](https://pic1.zhimg.com/80/v2-6c08fd00f64623a993f77aa3c8d81796_hd.webp)

此时远程目标IP:80端口，即可访问服务器RDP

![v2-7ea36d262498acc0af3c20d433f17cdf_hd.w](https://pic2.zhimg.com/80/v2-7ea36d262498acc0af3c20d433f17cdf_hd.webp)

![v2-be32dbaf2afa3576fe038056f7b23ff3_hd.w](https://pic3.zhimg.com/80/v2-be32dbaf2afa3576fe038056f7b23ff3_hd.webp)

![v2-649d0cbf384de371dc59c796a5cc7117_hd.w](https://pic3.zhimg.com/80/v2-649d0cbf384de371dc59c796a5cc7117_hd.webp)

如上，成功登录该服务器，通过该服务器即可当跳板登录内网更多的服务器，且可以对内网进行扫描。

![v2-9c670128bc6882fb3c9093edfb5b7ac2_hd.w](https://pic1.zhimg.com/80/v2-9c670128bc6882fb3c9093edfb5b7ac2_hd.webp)

但在测试过程中发现端口复用并不稳定，不时就会断开，有可能是安全设备防护的原因。于是对目标IP进行了全端口扫描，看看开放了哪些端口，扫描后发现被封了访问20多分钟。待解封后对端口逐个访问测试，发现存在9527存在web服务。

![v2-179f9aa9d7e4970a7032abf61620b8b4_hd.w](https://pic3.zhimg.com/80/v2-179f9aa9d7e4970a7032abf61620b8b4_hd.webp)

![v2-85589261e4f5739030b2dfef50d2f549_hd.w](https://pic2.zhimg.com/80/v2-85589261e4f5739030b2dfef50d2f549_hd.webp)

此时需要找网站的物理路径写shell，以下两种方式即可：

dirf:\2013103011494215.jpg /s

typeC:\WINDOWS\system32\inetsrv\MetaBase.xml | findstr "Path"

![v2-6c7969b421ccbef6dd61dc6f242ed981_hd.w](https://pic4.zhimg.com/80/v2-6c7969b421ccbef6dd61dc6f242ed981_hd.webp)

找到路径后写入菜刀一句话shell

![v2-11dc1d052de5959fab76b20748e28d1f_hd.w](https://pic3.zhimg.com/80/v2-11dc1d052de5959fab76b20748e28d1f_hd.webp)

如上连接被重置证明存在安全设备，直接上传reGeorg代理脚本访问也是连接被重置。此处用到神器冰蝎，上传后成功连接。

![v2-2708d0d4c945d03dbfb8f7e1abc47a17_hd.w](https://pic3.zhimg.com/80/v2-2708d0d4c945d03dbfb8f7e1abc47a17_hd.webp)

![v2-3d7575bf3c1d3b2a44f33378a9e89597_hd.w](https://pic1.zhimg.com/80/v2-3d7575bf3c1d3b2a44f33378a9e89597_hd.webp)

2、开始Socks代理

开启Socks代理，sqlmap挂上代理进行考试系统注入测试

![v2-2bca56f48ace034d66b15b137bad433f_hd.w](https://pic3.zhimg.com/80/v2-2bca56f48ace034d66b15b137bad433f_hd.webp)

sqlmap.py--proxy=socks5://192.168.0.110:10086

![v2-797e64bbd0e8284630e68bd89ac9de6f_hd.w](https://pic2.zhimg.com/80/v2-797e64bbd0e8284630e68bd89ac9de6f_hd.webp)

如上没有报一片红，当前注入点权限为root，绕过了安全设备的防护

![v2-51e3e1110c7517898817bfd98c762ea0_hd.w](https://pic1.zhimg.com/80/v2-51e3e1110c7517898817bfd98c762ea0_hd.webp)

![v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.w](https://pic3.zhimg.com/80/v2-a79f3ccfcdcddcfccf8d8e039e539803_hd.webp)

##  学生信息获取  

通过对数据库的浏览，发现存在member表，且数量为近5w，可以估计此约为全校学生信息，包含学号，姓名，身份证号等。

![v2-98995e1248178d3fef9a469e79c09a4a_hd.w](https://pic1.zhimg.com/80/v2-98995e1248178d3fef9a469e79c09a4a_hd.webp)

通过以下SQL语句即可获取刘书源的信息:

selectusername,name,idcard from user_data where name='刘书源';

![v2-a1384e98e9f33ae88c6f6cbc78061868_hd.w](https://pic4.zhimg.com/80/v2-a1384e98e9f33ae88c6f6cbc78061868_hd.webp)

如上，即可获取刘书源的学号及身份证号码，通过身份证号码后六位即可登录大部分系统。

![v2-08407aef5a6bdd509035cecb7d9302ac_hd.w](https://pic4.zhimg.com/80/v2-08407aef5a6bdd509035cecb7d9302ac_hd.webp)

![v2-ef91cb889dda27621a520f870e4a54dd_hd.w](https://pic3.zhimg.com/80/v2-ef91cb889dda27621a520f870e4a54dd_hd.webp)

如上达成此次测试的目的，成功获取刘书源的相关信息。

![v2-a8ab9696f562e16261e9d0cd503f046b_hd.w](https://pic3.zhimg.com/80/v2-a8ab9696f562e16261e9d0cd503f046b_hd.webp)

总结

本文主要通过信息收集加弱口令扫描，到最后获取信息，并没有太多的亮点，更多的是测试过程中遇到问题的解决思路的分享。若后续要继续测试，可以围绕以下的系统作为突破点。

1、通过爆破教师弱口令，登录门户系统进行测试。

![v2-565fdf45c734c28654fe2b6cfd738f45_hd.w](https://pic1.zhimg.com/80/v2-565fdf45c734c28654fe2b6cfd738f45_hd.webp)

![v2-b44074c4cdf0064a0d5e2e366b3b8f4f_hd.w](https://pic4.zhimg.com/80/v2-b44074c4cdf0064a0d5e2e366b3b8f4f_hd.webp)

2、OA系统

![v2-334b7856c3bb1feade87915e7bcc6cc0_hd.w](https://pic3.zhimg.com/80/v2-334b7856c3bb1feade87915e7bcc6cc0_hd.webp)

3、教学平台

![v2-789c84c6a759602321f1dd020b05c2db_hd.w](https://pic4.zhimg.com/80/v2-789c84c6a759602321f1dd020b05c2db_hd.webp)

4、科研系统

![v2-7f7f87c8bee9c676231667b903040257_hd.w](https://pic1.zhimg.com/80/v2-7f7f87c8bee9c676231667b903040257_hd.webp)

5、财务系统

![v2-1476f8995a2030fabaec797b5db4ba3e_hd.w](https://pic4.zhimg.com/80/v2-1476f8995a2030fabaec797b5db4ba3e_hd.webp)

6、资产管理系统

![v2-53325e80549b66a1a0f679b723088cad_hd.w](https://pic1.zhimg.com/80/v2-53325e80549b66a1a0f679b723088cad_hd.webp)

7、抓取已经获取服务器的账号密码，收集服务器的数据库相关信息等继续进行横向渗透测试。

至此，本篇完。

声明：作者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关。

![v2-391128842e3e21d144f46d1464f30a5c_hd.w](https://pic3.zhimg.com/80/v2-391128842e3e21d144f46d1464f30a5c_hd.webp)

实操推荐

Sqlmap教程：sqlmap是一款开源、功能强大的自动化SQL注入工具，支持多种数据库和多种注入方式

点击“[课程:sqlmap教程(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182015011916013600001)”，可预览学习（PC端操作最佳哟）

![v2-1796f0875af6f90700b3bff3d917266a_hd.w](https://pic3.zhimg.com/80/v2-1796f0875af6f90700b3bff3d917266a_hd.webp)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  

