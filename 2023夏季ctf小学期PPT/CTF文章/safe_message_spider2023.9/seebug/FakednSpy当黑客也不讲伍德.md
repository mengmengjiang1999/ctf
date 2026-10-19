**作者：liuchuang@360高级攻防实验室  
原文链接：<http://blog.noah.360.net/fake-dnspy-when-hackers-have-no-martial-ethics/>**

## 前景提要

dnSpy是一款流行的用于调试，修改和。反编译.NET程序的工具。网络安全研究人员在分析 .NET 程序或恶意软件时经常使用。

2022 年1月8日， [BLEEPING
COMPUTER](https://www.bleepingcomputer.com/news/security/trojanized-dnspy-app-drops-malware-cocktail-on-researchers-devs/) 发文称，
有攻击者利用恶意的dnSpy针对网络安全研究人员和开发人员发起了一次攻击活动。[@MalwareHunterTeam](https://twitter.com/malwrhunterteam/status/1479767752885874688)
发布推文披露了分发恶意dnSpy编译版本的Github仓库地址，该版本的dnSpy后续会安装剪切板劫持器， Quasar RAT， 挖矿木马等。

![image](https://images.seebug.org/content/images/2022/01/13/1642054509000-1bqryr.png-w331s)

![image_1](https://images.seebug.org/content/images/2022/01/13/1642054510000-2nsiql.png-w331s)

查看 dnSpy 官方版的 Git，发现该工具处于Archived状态，在2020年就已经停止更新，并且没有官方站点。
![2022-01-11-19-15-52](https://images.seebug.org/content/images/2022/01/13/1642054510000-3ixwof.png-w331s)

攻击者正是借助这一点，通过注册 dnspy[.]net 域名， 设计一个非常精美的网站， 来分发恶意的dnSpy 程序。
![image_2](https://images.seebug.org/content/images/2022/01/13/1642054511000-4ykpny.png-w331s)
同时购买Google搜索广告， 使该站点在搜索引擎的结果排名前列，以加深影响范围。
![2022-01-11-19-19-54](https://images.seebug.org/content/images/2022/01/13/1642054511000-5cqxtz.png-w331s)

截止 2022 年 1 月 9 日， 该网站已下线

## 样本分析

dnspy[.]net 下发的为 dnSpy 6.1.8 的修改版，该版本也是官方发布的最后一个版本。

通过修改dnSpy核心模块之一的dnSpy.dll入口代码来完成感染。

dnSpy.dll正常的入口函数如下:

![image_3](https://images.seebug.org/content/images/2022/01/13/1642054511000-6ttybq.png-w331s)

修改的入口添加了一个内存加载的可执行程序

![image_4-1](https://images.seebug.org/content/images/2022/01/13/1642054512000-7wrrwh.png-w331s)

该程序名为dnSpy Reader

![image_5](https://images.seebug.org/content/images/2022/01/13/1642054512000-8fuenc.png-w331s)

并经过混淆

![image_6](https://images.seebug.org/content/images/2022/01/13/1642054512000-9mpzvq.png-w331s)

后续会通过mshta下发一些挖矿，剪切板劫持器，RAT等
![2022-01-11-19-27-48](https://images.seebug.org/content/images/2022/01/13/1642054512000-10ufokz.png-w331s)

#### Github

攻击者创建的两个 github 分别为:

  * https[:]//github[.]com/carbonblackz/dnSpy
  * https[:]//github[.]com/isharpdev/dnSpy

其中使用的用户名为:isharpdev 和 `carbonblackz`，请记住这个名字待会儿我们还会看到它

## 资产拓线

通过对dnspy[.]net的分析，我们发现一些有趣的痕迹进而可对攻击者进行资产拓线：

#### dnspy.net

域名 dnspy[.]net 注册时间为2021年4月14日。

![image_7](https://images.seebug.org/content/images/2022/01/13/1642054512000-11drllf.png-w331s)

该域名存在多个解析记录， 多数为 Cloudflare 提供的 cdn 服务， 然而在查看具体历史解析记录时，我们发现在12月13日-01月03日该域名使用的IP为`45.32.253[.]0` ， 与其他几个Cloudflare CDN服务的IP不同，该IP仅有少量的映射记录。

![image_8](https://images.seebug.org/content/images/2022/01/13/1642054513000-12rggst.png-w331s)

查询该IP的PDNS记录， 可以发现该IP映射的域名大多数都疑似为伪造的域名， 且大部分域名已经下线。

![image_9](https://images.seebug.org/content/images/2022/01/13/1642054513000-13pnxfy.png-w331s)

这批域名部分为黑客工具/办公软件等下载站点，且均疑似为某些正常网站的伪造域名。

![2022-01-11-20-02-22](https://images.seebug.org/content/images/2022/01/13/1642054513000-14kvivh.png-w331s)

以及披露事件中的dnspy.net域名， 基于此行为模式，我们怀疑这些域名均为攻击者所拥有的资产，于是对这批域名进行了进一步的分析。

#### 关联域名分析

以 **toolbase[.]co** 为例， 该域名历史为黑客工具下载站点， 该网站首页的黑客工具解压密码为 “`CarbonBlackz`”，
与上传恶意 dnspy 的 Github 用户之一的名字相同。

![image_10](https://images.seebug.org/content/images/2022/01/13/1642054514000-15klcvi.png-w331s)

该站点后续更新页面标题为 Combolist-Cloud ， 与`45.32.253[.]0`解析记录中存在的 **combolist.cloud**
域名记录相同， 部分文件使用 mediafire 或 gofile 进行分发。

![image_11](https://images.seebug.org/content/images/2022/01/13/1642054514000-16bupyu.png-w331s)

该域名疑似为combolist[.]top的伪造站点， combolist[.]top 是一个提供泄露数据的论坛。

![image_12](https://images.seebug.org/content/images/2022/01/13/1642054514000-17juynt.png-w331s)

**torfiles[.]net** 也同样为一个软件下载站。

![image_13](https://images.seebug.org/content/images/2022/01/13/1642054514000-18bjwul.png-w331s)

**Windows-software[.]co** 以及 **windows-softeware[.]net** 均为同一套模板创建的下载站。

![image_14](https://images.seebug.org/content/images/2022/01/13/1642054514000-19hmant.png-w331s)

![image_15](https://images.seebug.org/content/images/2022/01/13/1642054514000-20nyexd.png-w331s)

**shortbase[.]net** 拥有同 **dnspy[.]net** 一样的CyberPanel安装页面.且日期均为2021年12月19日。

![image_16](https://images.seebug.org/content/images/2022/01/13/1642054515000-21xjqxx.png-w331s)

下图为 **dnspy[.]net** 在WaybackMachine记录中的CyberPanel的历史安装页面。

![image_17](https://images.seebug.org/content/images/2022/01/13/1642054515000-22boxma.png-w331s)

**coolmint[.]net** 同样为下载站， 截止 2022 年1月12日依然可以访问.但下载链接仅仅是跳转到 **mega[.]nz**

![image_18](https://images.seebug.org/content/images/2022/01/13/1642054515000-23viytb.png-w331s)

**filesr[.]net** 与 **toolbase[.]co** 为同一套模板

![image_19](https://images.seebug.org/content/images/2022/01/13/1642054515000-24xvyah.png-w331s)

此站点的`About us` 都未做修改，

![image_20](https://images.seebug.org/content/images/2022/01/13/1642054516000-25tasoi.png-w331s)

该页面的内容则是从FileCR[.]com的About us页面修改而来

![2022-01-11-19-57-10](https://images.seebug.org/content/images/2022/01/13/1642054516000-26irafp.png-w331s)

**filesr[.]net** 的软件使用dropbox进行分发，但当前链接均已失效

最后是 **zippyfiles[.]net** ， 该站点为黑客工具下载站
![2022-01-11-19-53-30](https://images.seebug.org/content/images/2022/01/13/1642054516000-27eohwq.png-w331s)
我们还在reddit上发现了一个名为`tuki1986`的用户两个月前一直在推广 **toolbase[.]co** 及
**zippyfiles[.]net** 站点。

![2022-01-11-20-41-21](https://images.seebug.org/content/images/2022/01/13/1642054516000-28coeod.png-w331s)
该用户在一年前推广的网站为 **bigwarez[.]net**

![2022-01-11-20-58-43-1](https://images.seebug.org/content/images/2022/01/13/1642054517000-29lblts.png-w331s)
查看该网站的历史记录发现同样为一个工具下载站点，且关联有多个社交媒体账号。

![2022-01-12-21-03-15](https://images.seebug.org/content/images/2022/01/13/1642054517000-30oulgu.png-w331s)
推特[@Bigwarez2](https://twitter.com/bigwarez2)

![2022-01-11-21-05-11](https://images.seebug.org/content/images/2022/01/13/1642054517000-31oeuqz.png-w331s)
Facebook[@software.download.free.mana](http://noahblog.360.cn/content/images/2022/01/https://www.facebook.com/software.download.free.mana)

![2022-01-11-21-06-54](https://images.seebug.org/content/images/2022/01/13/1642054517000-32ygxzb.png-w331s)

该账号现在推广的网站为 **itools[.]digital** ，是一个浏览器插件的下载站。
![2022-01-11-21-18-54](https://images.seebug.org/content/images/2022/01/13/1642054517000-33voxbl.png-w331s)

Facebook组[@free.software.bigwarez](https://www.facebook.com/groups/free.software.bigwarez)

![2022-01-11-21-14-23](https://images.seebug.org/content/images/2022/01/13/1642054518000-34vbrhc.png-w331s)

领英 - 当前已经无法访问 [@free-software-1055261b9](http://noahblog.360.cn/fake-dnspy-when-hackers-have-no-martial-ethics/www.linkedin.com/in/free-software-1055261b9)

tumblr[@bigwarez](https://www.tumblr.com/blog/view/bigwarez)

![2022-01-11-21-12-50](https://images.seebug.org/content/images/2022/01/13/1642054518000-35qioht.png-w331s)

继续分析tuki1986的记录发现了另一个网站 **blackos[.]net**

![2022-01-11-21-24-33](https://images.seebug.org/content/images/2022/01/13/1642054518000-36lmkku.png-w331s)

该网站同样为黑客工具下载站点

![2022-01-11-21-27-38](https://images.seebug.org/content/images/2022/01/13/1642054518000-37vvrbd.png-w331s)

且在威胁情报平台标注有后门软件

![2022-01-12-01-33-08](https://images.seebug.org/content/images/2022/01/13/1642054518000-38zvtrw.png-w331s)

通过该网站发现有一个名为`sadoutlook1992`的用户，从18年即开始在各种黑客论坛里发布挂马的黑客工具。

![2022-01-12-01-39-59](https://images.seebug.org/content/images/2022/01/13/1642054519000-39qosyh.png-w331s)
![2022-01-12-01-40-42](https://images.seebug.org/content/images/2022/01/13/1642054519000-40dmrni.png-w331s)
![2022-01-12-01-41-27](https://images.seebug.org/content/images/2022/01/13/1642054519000-41qebac.png-w331s)

在其最新的活动中，下载链接为 **zippyfiles[.]net**

![2022-01-12-01-43-26](https://images.seebug.org/content/images/2022/01/13/1642054519000-42kzucf.png-w331s)

从恶意的Gihubt仓库及解压密码可知有一个用户名为”CarbonBlackz”， 使用搜索引擎检索该字符串，
发现在知名的数据泄露网站raidforums[.]com有名为“Carbonblackz”的用户。

![image_23](https://images.seebug.org/content/images/2022/01/13/1642054519000-43nystm.png-w331s)

同样的在俄语的黑灰产论坛里也注册有账号，这两个账号均未发布任何帖子和回复，疑似还未投入使用。

![image_24](https://images.seebug.org/content/images/2022/01/13/1642054519000-44jqyyf.png-w331s)

其还在越南最大的论坛中[发布](https://tinhte.vn/profile/2883781/)软件下载链接：

![image_25](https://images.seebug.org/content/images/2022/01/13/1642054520000-45ftbvd.png-w331s)

![image_26](https://images.seebug.org/content/images/2022/01/13/1642054520000-46gxkez.png-w331s)

#### 归因分析

通过查看这些域名的WHOIS信息发现， filesr[.]net的联系邮箱为carbon1986@protonmail.com

![image_22](https://images.seebug.org/content/images/2022/01/13/1642054520000-47nlkum.png-w331s)

查询该邮箱的信息关联到一位35岁，疑似来自俄罗斯的人员。

![2022-01-12-00-40-11](https://images.seebug.org/content/images/2022/01/13/1642054520000-48ndvda.png-w331s)

从`carbon1986`和`tuki1986`这两个ID来看，1986疑似为其出生年份，同时也符合35岁的年龄。

根据这些域名的关联性，行为模式与类似的推广方式，我们认为这些域名与dnspy[.]net的攻击者属于同一批人。

![2022-01-12-02-45-11](https://images.seebug.org/content/images/2022/01/13/1642054520000-49agamg.png-w331s)

这是一个经过精心构建的恶意组织，其至少从2018年10月即开始行动，通过注册大量的网站，提供挂马的黑客工具/破解软件下载，并在多个社交媒体上进行推广，从而感染黑客，安全研究人员，软件开发者等用户，后续进行挖矿，窃取加密货币或通过RAT软件窃取数据等恶意行为。

## 结论

破解软件挂马已经屡见不鲜，但对于安全研究人员的攻击则更容易中招，因为一些黑客工具，分析工具的敏感行为更容易被杀软查杀，所以部分安全研究人员可能会关闭防病毒软件来避免烦人的警告。

虽然目前该组织相关的恶意网站，gihub仓库以及用于分发恶意软件的链接大部分已经失效.但安全研究人员和开发人员还是要时刻保持警惕。对于各种破解/泄露的黑客工具建议在虚拟环境下运行，开发类软件，办公软件要从官网或正规渠道下载，且建议使用正版.以避免造成不必要的损失。

## IOCs

    
    
    dnSpy.dll - f00e0affede6e0a533fd0f4f6c71264d

  * ip

    
    
    ip:
    45.32.253.0

  * domain

    
    
    zippyfiles.net
    windows-software.net
    filesr.net
    coolmint.net
    windows-software.co
    dnspy.net
    torfiles.net
    combolist.cloud
    toolbase.co
    shortbase.net
    blackos.net
    bigwarez.net
    buysixes.com
    itools.digital
    4api.net

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1812/>

