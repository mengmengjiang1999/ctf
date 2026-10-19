## 简介

 **PhishProtect是一款Chrome插件。其主要用处是提醒并在需要时，阻止通过 IDN/Unicode
的方式进行钓鱼的web站点。目前发布的版本为Beta版。**

  *  **防止同形异义字攻击**
  * **基于云的零日网络钓鱼防御**

## 安装

你可以在[chrome](https://chrome.google.com/webstore/detail/phishprotect-beta/mikecfgnmakjomepfcghpbhfamjbjhid)，[firefox](https://addons.mozilla.org/en-US/firefox/addon/phish-ai-idn-protect/?src=search)，
[opera](https://addons.opera.com/en/extensions/details/phishai-idn-protect/)浏览器上安装。（Edge上即将推出）

零日网络钓鱼防御目前仅Chrome支持，并且仍处于Beta版。

## 截图

**![screenshot1.png](https://image.3001.net/images/20180404/15227997384662.png!small)  
**

**![screenshot3.png](https://image.3001.net/images/20180404/15227997504044.png!small)  
**

**![screenshot2.png](https://image.3001.net/images/20180404/15227997624429.png!small)  
**

## 隐私政策

你可以在插件中禁用zero-day phishing，并且我们不会收集你的任何信息。简而言之就是如果你启用了zero-day
phishing，我们将会把未知站点的截图发到云端进行分析。但我们不会保存任何的截图，除非它们是恶意的。完整的隐私政策在[这里](https://www.phish.ai/phish-ai-privacy-policy/)查看。

## AI和计算机视觉引擎

引擎如何工作的完整描述在[这里](https://www.phish.ai/product/)查看

我们有一个非常大的计算机视觉数据库，包含已知网站及其合法域名。该扩展程序会发送未知网站的屏幕截图，我们会将其与我们的数据库进行比较，如果我们检测到它与已知网站类似，但托管在不同的域上，则会发回响应和警报。

该引擎目前处于测试阶段，我们每天都会更新我们的数据库让它变得更加强大，如果你希望我们抓取相关的内容可以通过邮件向我们提交[yp@phish.ai](mailto:yp@phish.ai)

 ***参考来源：[GitHub](https://github.com/phishai/phish-protect)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

