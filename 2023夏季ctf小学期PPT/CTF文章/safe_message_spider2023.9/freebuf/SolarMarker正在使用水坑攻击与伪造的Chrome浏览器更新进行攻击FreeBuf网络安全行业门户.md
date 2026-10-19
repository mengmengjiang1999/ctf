在过去的三个月里，eSentire 的安全研究团队发现信息窃密恶意软件 SolarMarker
都没有发动攻击，却在最近忽然重返舞台。此前，SolarMarker 的运营者使用 SEO
投毒或者垃圾邮件来引诱受害者，受害者试图下载一些文档的免费模板，就被攻击者盯上了。最新的攻击中，攻击者开始利用伪造的 Chrome
浏览器更新作为水坑攻击的一部分。

![image.png-114kB](https://image.3001.net/images/20221002/1664725715_6339b2d36d04d1c8b1bc4.png!small)SolarMarker
攻击时间线

SolarMarker 在长期休眠后，又忽然出现。SolarMarker
并不依赖大规模钓鱼邮件攻击，而是进行搜索引擎投毒。本次使用的虚假更新也不是首创的技术，此前 SocGholish 恶意软件就使用该方式进行攻击。

## 失陷 WordPress 网站被当作水坑

SolarMarker 的攻击者利用伪造的 Chrome 浏览器更新作为水坑攻击的一部分。黑客会选择那些对受害者有吸引力的网站，攻陷并部署恶意软件。

许多网站都是使用 CMS 搭建的，这些系统中包含的漏洞被攻击者利用。本次攻击行动中，SolarMarker 主要针对 WordPress
搭建的网站进行攻击。

![image.png-54.4kB](https://image.3001.net/images/20221002/1664725716_6339b2d421021f2230085.png!small)伪造的
Chrome 更新

典型的场景是：受害者为一家税务咨询公司的员工，在 Google 上搜索一家医疗设备制造商的名称，在访问 WordPress
部署的网站时，系统会提示用户下载伪造的 Chrome 更新。

## 与 SocGholish 恶意软件不同

SolarMarker 和 SocGholish 二者所使用的技术细节完全不同。由于只发现了 SolarMarker
为数不多的攻击，有可能是攻击者正在测试新的攻击方式。当然，这也有可能是 SolarMarker 一波新攻击的开始。

![image.png-151.6kB](https://image.3001.net/images/20221002/1664725716_6339b2d4b53d5d6c42dd2.png!small)嵌入式
Payload

虚假浏览器更新提醒是根据受害者访问网站时使用的浏览器联动的，除了 Chrome 攻击者也提供了 Firefox 与 Edge 浏览器的虚假更新。页面部署在
`hxxp://shortsaledamagereports[.]com`上，该页面包含 Payload 的嵌入式链接。

## 建议

SocGholish、SolarMarker 和 GootLoader 等恶意软件会通过浏览器来进行入侵，为减少影响：

>   *
> 提高员工意识。浏览器更新通常是自动进行的，可以开启浏览器的自动更新功能，而不是自行下载新版本。必须使员工了解，引诱用户下载浏览器更新是攻击者的常用手段。
>   *
> 不要从未知站点下载文件。看似无害的行为，例如寻找要使用的模板或者文档，都可能给攻击者带来可乘之机。搜索引擎提供的内容并不都是可信的，一定要从信任的来源进行下载。
>   * 监控端点。端点需要通过监控确保检测能力，为终端安全提供可见性和保护力。
>   * 威胁情报。充分利用威胁情报可以阻止最新的威胁，
>

## 参考来源

> [ESENTIRE](https://www.esentire.com/blog/popular-info-stealing-malware-> solarmarker-is-using-watering-hole-attacks-and-fake-chrome-browser-updates-> to-infect-business-professionals-warns-esentire)

