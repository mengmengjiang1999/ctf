## **事件简介**

近期，深信服千里目高级威胁研究团队监测到“ **魔罗桫”组织针对南亚军工企业的攻击活动** 。该组织利用诱饵文档“China Cruise Missiles
Capabilities-Implications for the Indian
Army.docx”。经过深入追踪，文档内容摘抄自印度的orfonline站点， **里面包含了英文的导（隔开敏感词）弹技术报告，意在瞄准军工企业**
。受害者打开文档后，会触发office公式编辑器漏洞，进而下载执行恶意软件Warzone
RAT，实现长期控制主机和窃密敏感资料的目的。我们从技术等多维度对比了该组织上一次利用热门话题的攻击活动，本次攻击依然沿用了
**军事话题诱饵文档+漏洞利用+伪装微软域名+商业木马** 的攻击套路。

APT组织”魔罗桫”（又名为Confucius），是一个 **长期** **针** **对中国，巴基斯坦，尼泊尔等** 地区，主要瞄准
**政府机构，军工企业，核能行业** 等领域进行网络间谍活动的活跃组织。

##  **样本简介**

此类恶意文档主要通过钓鱼邮件进行传播，用户打开该恶意文档后，显示的是看似正常的相关报告，背后会通过office编辑器漏洞从黑客的服务端下载恶意文件并隐蔽执行，最终受害用户计算机被黑客组织控制，资料被窃取。恶意word文件打开后实际内容如下。

![](https://image.3001.net/images/20210206/1612600808_601e55e806f2a9c5714f1.png!small)涉及到一些公开的产品参数：

![](https://image.3001.net/images/20210206/1612600821_601e55f5648c937802b8b.png!small)

##  **攻击溯源**

从传播方式上此次攻击的载体为恶意文档，附带热点时事内容，对比前几次追踪到的攻击活动，存在一定的相似性。

最近的一次攻击事件采用的恶意文档内容来源于国外Bulletin（免费新闻与双月刊站点）2020年11月9日公开发布的一篇文章，标题是“Here's what
to expect from Biden on top nuclear weapons issues”。

![](https://image.3001.net/images/20210206/1612600835_601e5603dd45ad4d01525.png!small)

从利用手法上则使用同样的远程模板与office编辑器漏洞，请求服务端的地址msoffice.user-assist.site与前几次使用过的域名构成结构存在一定的相似性，以伪装微软或者office等连接域名绕过黑白名单限制。

![](https://image.3001.net/images/20210206/1612600846_601e560ec87943b36b785.png!small)

中间阶段释放的恶意dll文件整体架构与导出函数与之前捕获的样本基本功能是一致的，最终释放的远控也是之前攻击活动使用过的Warzone（Ave
Maria）RAT。依据本次攻击活动的TTPs以及落地的恶意文件特性与细节与IOC等相似性，我们可以判定这是”魔罗桫”（国外安全厂商命名为Confucius）APT的最新攻击活动。

##  **攻击总结**

根据以往几次攻击活动的方式与媒介，如利用引起媒体高度关注的最新消息来作为诱饵主题内容，最终的C&C存活的时间不长，每次被捕获的攻击活动存在细微差异，这也说明了该组织正在发展与适应，可以预见摩罗桫（Confucius）APT组织不仅是现在，未来依然会持续不断地针对特定的目标与机构发起网络攻击。

##  **详细分析**

对诱饵文件“China Cruise Missiles Capabilities-Implications for the Indian
Army.docx”的内容进行深入研究，发现该文档内容来源于印度的orfonline站点，发布于2020年12月4日，orfonline站点是允许不同观点与意见进行讨论的印度公众站点。

![](https://image.3001.net/images/20210206/1612600860_601e561cc5f4990853f27.png!small)

![](https://image.3001.net/images/20210206/1612600871_601e56278cdbfd5b849f6.png!small)

本次攻击流程图如下：

![](https://image.3001.net/images/20210206/1612600882_601e5632ad8694b355473.png!small)

受害用户无意打开恶意文件后，会直接从服务端下载模板文件（实际是携带office公式编辑器漏洞CVE-2017-11882的恶意RTF文档）。

![](https://image.3001.net/images/20210206/1612600893_601e563d19f4f580a235e.png!small)

该诱饵文件的最后一次修改时间为2020年12月10日，可以猜测本次攻击活动发生在该时间之后的某个时段。

![](https://image.3001.net/images/20210206/1612600902_601e5646277d402850297.png!small)

内嵌的远端模板地址，URL的目的是伪装成office更新，如下。

![](https://image.3001.net/images/20210206/1612600767_601e55bfb6d38f2e5badb.png!small)

下载的rtf文档在漏洞利用成功后，恶意代码会释放加载内嵌的bing.dll文件。

![](https://image.3001.net/images/20210206/1612600914_601e56529b9937fe2a7fc.png!small)

![](https://image.3001.net/images/20210206/1612600768_601e55c055e40c817e950.png!small)

该dll的导出函数为mark，原始文件名为linknew.dll，本次攻击活动的dll文件已经不存在pdb路径，而之前捕获的一次攻击活动攻击者采用了该pdb路径：C:\Users\admin\Documents\dll\linknew\Release\linknew.pdb，说明攻击者已经有意识地在进行痕迹地清理。

![](https://image.3001.net/images/20210206/1612600928_601e56602c145a4f8b49b.png!small)

![](https://image.3001.net/images/20210206/1612600938_601e566aedd0ce7c95e74.png!small)

编译时间为2020年11月26日

![](https://image.3001.net/images/20210206/1612600769_601e55c118e42931521ae.png!small)调用导出函数mark

![](https://image.3001.net/images/20210206/1612600974_601e568e4799c63597f94.png!small)后续该dll文件会通过URLDownloadToFile函数从<http://msoffice.user-assist.site/update/content>下载到本地命名为update.exe，接着创建快捷方式设置到启动目录为update.lnk文件，后续重启后启动。在32位系统环境下，恶意文件会首先注入到explorer.exe进程，之后该恶意文件会通过com功能复制自身并改名为update.exe至C:\ProgramData\Software\update.exe，并通过注册表HKCU\Software\Microsoft\Windows\CurrentVersion\Run为路径C:\Users\xxxx\AppData\Roaming\svchost.exe（svchost.exe是update.exe拷贝衍生）设置自启动，建立持久性。

利用pkgmgr.exe、dism.exe运行机制加com功能替换系统掉dismcore.dll文件提升自身程序权限后，恶意软件会使用powershell命令从Windows
Defender中排除整个C驱动器。执行的命令：powershell Add-MpPreference -ExclusionPath
C:\。然后释放programs.bat文件至目录C:\Users\xxxx\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup\（属于开始\启动菜单）下，后续重启后再次执行，programs.bat文件内容如下：

for /F "usebackq tokens=*" %%A in
("C:\Users\xxxx\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup\programs.bat:start") do %%A

在隐蔽性方面，programs.bat:start文件是母体为上述programs.bat采用ADS数据流生成的文件，接着执行后会通过wmic命令创建Roaming:ApplicationData进程，而Roaming:ApplicationData同样是自身母体程序通过ADS数据流产生的文件，实际内容如下：

wmic process call create '"C:\Users\xxxx\AppData\Roaming:ApplicationData"'

最终发现update.exe会在内存解密释放出Ave Maria远控木马，也被称为Warzone
RAT。经过分析为Warzone160版本的RAT，Warzone
RAT是一款以恶意软件即服务（MaaS）作为商业模式的远控工具，有多次已公开的进行攻击活动的记录。黑客使用它来远程控制受害者的PC，并从受感染的计算机中窃取信息，经过分析C&C地址为[syncronize.3utilities.com](http://syncronize.3utilities.com/)（45.147.231.232）。

![](https://image.3001.net/images/20210206/1612600988_601e569cdd58d2df66512.png!small)

##

##  **威胁情报**

 **MD5**

9f54962d644966cfad560cb606aeade2 （China Cruise Missiles Capabilities-Implications for the Indian Army.docx）

912141bb5b4020c2cc75a77c37928a3b （word）

e13134c8411557ce9c9e58d57b855a62 （content）

915F528202B036DC5D660F44C187F121 （bing.dll）

6b906764a35508a7fd266cdd512e46b1 （dismcore.dll）

7707871515E16C8E8461CED7AF1CACDD （Warzone RAT）

 **URL**

http[:]//msoffice.user-assist.site/refresh/word

http[:]//msoffice.user-assist.site/update/content

 **DOMAIN**

msoffice[.]user-assist.site

[syncronize[.]3utilities.com](http://syncronize.3utilities.com/)

 **IP**

45[.]84.204.148

45[.]147.231.232

