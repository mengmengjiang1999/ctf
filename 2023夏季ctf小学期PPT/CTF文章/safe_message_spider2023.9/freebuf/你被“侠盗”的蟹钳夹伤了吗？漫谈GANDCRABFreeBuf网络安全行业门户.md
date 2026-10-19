**还记得 2017 年 5 月，影响全球的 WannaCrypt 吗？在当时，全球超过 230,000
台计算机皆遭此病毒侵害，虽然此病毒要求支付价值等同于 300 美元的比特币才可解密所有遭加密的文档，但事实上，并无法通过付款的方式解密。WannaCrypt
是通过 Windows 操作系统的漏洞，以蠕虫方式进行传播扩散，微软也因为这个事件，破例对当时已停止技术支持的 WindowsXP
释出修补程序。这个事件是一个经典案例，也让许多人见识到了勒索软件的破坏力。**  

好一阵子，勒索软件的音量，似乎在各种流行的信息安全威胁中显得小了，勒索软件是否就此绝迹？抑或风险有趋缓的现象？观察 GandCrab
的演化史，或许能给出一些客观的答案。

##  GANDCRAB 简史

GandCrab 第一次被大众关注是在 2018 年 1 月，由罗马尼亚的安全公司
Bitdefender、罗马尼亚警政署、欧洲刑警组织连手揭露了这个恶意勒索软件，并且很快地，就由 Bitdefender 安全工程师根据 GandCrab
的加密缺陷，破解并释出了免费解密工具，这是 GandCrab1.0。

但这个勒索病毒的开发者十分积极，很快地在同年的 3 月 5 日、 5 月 3 日先后释出了 GandCrab 的 2.0 与 3.0 版本。2.0
版本增加了 QR code 功能，而 3.0
在感染后将病毒加为开机执行项目，并强制关机，下一次开机时会造成操作系统变慢或进不了操作系统，成功进入操作系统后则出现黑屏，并提示受害者已遭勒索软件感染。2018
年 7 月，GandCrab 进化至 4.0 版本，增加了许多提示受害人付钱的说明，以及 Tor 通道，并开始提供一个文档免费解密的验证服务。9
月时，5.0 版面世，GandCrab 开发团队与供应恶意软件加密工具（Crypter）的组织 NTCrypt 结盟，并举办折扣活动，提供购买解密
GandCrab 的客户。而 GandCrab 最新版是 2019 年 2 月 19 日左右所推出的 5.2 版。

GandCrab 在网络上还有一个轶闻，说是一个在叙利亚的父亲不幸感染了 GandCrab
后，再也不能看到他因战争而丧身的儿子照片，由于这个父亲在推特上发文说出了这个情况，GandCrab 的制造者看到随即发了道歉文，并释出解密密钥后，又更新了
GandCrab
版本，将叙利亚地区列为不受感染的白名单，因为这个事件，开始有人对此恶意软件心生好感，并称其为「侠盗」。事实上，该事件中的父亲本不该遭此一劫；而放过叙利亚，荼毒其他国家也非正义！去认同加害者的观点和想法，并不理性，这是典型的「斯德哥尔摩症候群」。

##  传播

事实上，GandCrab 每个版本间的变化并不是太大，但是它的传播渠道极为多元。在最初的版本，GandCrab 主要用 RIG ExploitKit 和
GandSoftExploitKit 两个开发工具包进行分发，进行水坑式攻击 ( Wateringhole ) 或路过式下载 ( Drive-bydownload )：攻击者尝试制作出网页乱码，以解决页面乱码之由，诱导受害者下载由 GandCrab
伪装的字体更新进行感染；或乔装成软件破解文件、正版商用软件之类，诱骗受害者执行 GandCrab。

后续版本则扩张到使用暴露于网络上的远程桌面、僵尸网络、渗透工具、经由木马程序挟带的做法。而 5.0.2 版，开始大量利用钓鱼邮件，触发后以
PowerShell 执行脚本，埋藏在内存内暗中运作，并会在受害者计算机中尝试利用 CVE-2018-8440 以及 CVE-2018-8120
漏洞进行提权。

![](https://image.3001.net/images/20190412/1555048753_5cb02931ba6da.jpg!small)

 _通过电子邮件发送 GandCrabv5.1 版的前导攻击恶意文件_

![](https://image.3001.net/images/20190412/1555048785_5cb029515d82d.jpg!small)
_日本地区常见的 GandCrab 恶意邮件攻击主题统计，除了图示外，还有许多女星的名字。引用自 Twitter@gorimpthon_

至于流行的地区，则可说全球都有其踪迹，亚洲地区受害者最多的国家是南韩，其次为中国。但某些操作系统虽触发了 GandCrab
这个勒索软件，但因为这个勒索软件内建操作系统语系白名单的缘故，只要是使用该白名单语系的操作系统，就不会进行后续的加密程序，这些白名单的操作系统语系分别为：俄罗斯、乌克兰、比利时、塔吉克、亚美尼亚、阿塞拜疆、乔治亚、吉尔吉斯坦、土库曼、乌兹别克、鞑靼斯坦、叙利亚、阿拉伯等。

##  感染的两三事

当 GandCrab 被触发后，首先它会将它自己复制到%AppData%\Microsoft\\[RANDOM
NAME]，接下来查找下列应用程序，并尝试将它们关闭：msftesql.exe、sqlagent.exe、sqlbrowser.exe、sqlservr.exe、sqlwriter.exe、oracle.exe、ocssd.exe、dbsnmp.exe、synctime.exe、mydesktopqos.exe、agntsvc.exeisqlplussvc.exe、xfssvccon.exe、mydesktopservice.exe、ocautoupds.exe、agntsvc.exeagntsvc.exe、agntsvc.exeencsvc.exe、firefoxconfig.exe、tbirdconfig.exe、ocomm.exe、mysqld.exe、mysqld-nt.exe、mysqld-opt.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、thebat.exe、thebat64.exe、thunderbird.exe、visio.exe、winword.exe、wordpad.exe。接着，它会尝试向外联机至内建的上千个独立主机列表，联机成功后，它会开始进行感染主机的加密。

勒索软件的目标是取财，未避免受害人的计算机完全不能用或无法联机付钱解锁的网页，GandCrab 会避开这些文件夹不加密： All
Users、LocalSettings、Program
Files、ProgramData、TorBrowser；会避开这些扩展名不加密：.bat、.cab、.cmd、.cpl、.cur、.diagcab、.diagpkg、.dll、.drv、.exe、.hlp、.icl、.icns、.ico、.ics、.idx、.key、.ldf、.lnk、.lock、.mod、.mpa.msc、.msp、.msstyles、.msu、.nomedia、.ocx、.prf、.rom、.rtp、.scr、.shs.spl、.sql、.sys、.theme、.themepack、autorun.inf、boot.ini、bootsect.bak、desktop.ini、iconcache.db、ntuser.dat、ntuser.dat.log、thumbs.db、.gandcrab；为避免受害人付了钱无法解密，
GandCrab 也会避免再次加密过去已被它加密的文档，因此会避开遭到感染的扩展名如：.CRAB、.KRAB。

完成加密后，会在每个遭到加密的数据，依不同的 GandCrab 版本，放置一个对应的说明文件，如：GDCB-DECRYPT.txt，或是 KRAB-DECRYPT.txt，文件的内容就是告诉受害者现在所遭遇的状况，以及提供可以付款解密的渠道。遭到加密的文档，依GandCrab
版本的不同，有不一样的扩展名：1.0 被加密的文档扩展名为.GDCB；v2.0、3.0 扩展名为.CRAB； 4.0 是.KRAB； 5.0
以后版本，其扩展名为 5-10 码随机字母。如同过去的勒索软件，勒索的有价目标多半是虚拟货币，GandCrab 也不例外，它要求的是Bitcoin、DASH
或其他虚拟货币。

##  解密

第一版 GandCrab 的开发较为青涩，因此，在很短的时间，即有安全工程师破解其中加密缺陷，而释出免费的解密工具；随着 GandCrab
每一版的演进，解密工具也都顺利地通过找到其中缺陷而推出。GandCrab 4.0 版几乎都可以被免费解密了，但 GandCrab
的开发者似乎也发现了这个问题，在安全工程师释出 5.0.4 及 5.1 的解密工具的 24 小时内， GandCrab
的开发者就修补了勒索软件的缺陷，造成修正后的 5.0.4、5.1 及最新的 5.2 版，目前还是无解的情况。

##  观点

根据 ASRC 与 Softnext 守内安安全团队观察，不仅是 GandCrab 这款勒索软件，所有的勒索软件的感染入侵渠道大约可分为下面几种：

> 通过暴露在防火墙外的服务，尤其是带有未修补漏洞，或可被滥用尝试登入的服务。
>
> 通过浏览器未修补漏洞入侵。
>
> 通过电子邮件寄送夹带前导攻击程序的恶意链接或文档，再以社交手段诱使受害人开启。
>
> 伪装为破解文件程序、修补软件、网页字体，诱使受害人执行安装。

知道了入侵的渠道与手段，我们建议可先盘点并以防火墙管控、封闭不必要暴露在网络上的服务，或至少，对于尝试登入失败的次数做限制并监控。再者，以安全的浏览器，并时时保持更新，尽可能减少浏览器的外挂的使用，以降低上网浏览及遭到入侵的风险，还有，别忽视搜索引擎或浏览器发出的安全警示。架构一个安全的邮件过滤机制，已是基本的信息安全防护措施，毕竟电子邮件是数年来黑客入侵的首选渠道！最后，操作系统本身会避免外来程序自动执行，但却无法避免人为允许的操作，社交手段主要攻击的对象是人，除了尽可能地隔离恶意程序与人接触外，基本的信息安全意识是必须的。

除了做好上述风险的控制措施外，面对勒索软件的侵害，建议您还是应该有定期脱机备份的策略。万一因意外造成重要数据被加密时，您还有从备份文件数据还原的选择。我们并不建议任何向黑客付赎以取回文档的行为，因为这样的行为，等于是变相鼓励了攻击者，支持他们的不义之举。

信息安全不是一个简单的单一层面的问题，也从未有单一特定产品可解决所有的安全问题。在依赖信息科技的时代，面对信息安全问题，没有谁能置身事外。信息安全防护是一个动态、持续建构与改善的防御工程，若能有好的产品、优秀的协防顾问团队，将使您面对信息安全问题能事半功倍。

 ***本文作者：softnext守内安，转载请注明来自FreeBuf.COM**

