**LookBack恶意软件在2019年7月至2019年8月之间针对美国公用事业部门发起了攻击，与此同时，Proofpoint研究人员发现了名为FlowCloud的恶意软件家族也出现在美国被攻击的目标中。攻击者可利用恶意软件完全控制受感染系统，木马（RAT）具有包括访问已安装的应用程序，键盘，鼠标，屏幕，文件，服务和进程的能力，并可以通过C
&C服务器获取敏感信息。**

研究人员分析了2019年7月至11月之间的网络钓鱼活动，确定LookBack和FlowCloud恶意软件都归属于称为TA410的攻击者。分析发现TA410和TA429（APT10）使用策略之间存在相似之处。下图1显示了LookBack和FlowCloud活动的时间表。

![1592554956_5eec75ccf1cc6.png!small](https://image.3001.net/images/20200619/1592554956_5eec75ccf1cc6.png!small)

## 传播方式

研究人员观察到在2019年7月10日的网络钓鱼活动中出现针对的美国的恶意可执行（PE）附件，其使用了诸如PowerSafe能源教育课程（30天试用期）之类的主题行，这些活动一直持续到2019年9月。

PE附件是模块化的恶意软件，开发人员在程序数据库路径中将其称为“
FlowCloud”。值得注意的是，FlowCloud活动与Proofpoint先前记录的LookBack活动同时发生。
FlowCloud和LookBack均针对美国的公用事业提供商，两者都使用了培训为主题的诱饵，都使用了攻击者控制的域进行传播。在某些情况下，FlowCloud和LookBack不仅针对相同的公司，而且针对相同的收件人。

2019年11月FlowCloud策略发生变化，美国公用事业公司目标保持不变，攻击者工具从PE附件变成恶意Microsoft
Word文档。攻击者在11月开始使用域asce
[.email]来传递这些附件。该域于2019年6月首次注册，IP为103.253.41[.]75。2019年10月29日该域名解析为134.209.99[.]169，此外还托管了多个能源认证和教育主题域名。这些域还与2019年7月和8月FlowCloud网络钓鱼活动中发现的域共享SSL证书（图2）。

![1592555574_5eec783663ddf.png!small](https://image.3001.net/images/20200619/1592555574_5eec783663ddf.png!small)

下表显示了首次观察到的TA410 IP、与其关联的注册域以及来自这些域的电子邮件中的恶意软件：

![1592555615_5eec785fa7d7c.png!small](https://image.3001.net/images/20200619/1592555615_5eec785fa7d7c.png!small)

2019年11月邮件中冒充了美国土木工程师学会，并伪装成合法域asce [.org]。
该电子邮件的结构与2019年7月模拟NCEES和全球能源认证构造的LookBack电子邮件非常相似。图3和图4为电子邮件的示例：

![1592555702_5eec78b636229.png!small](https://image.3001.net/images/20200619/1592555702_5eec78b636229.png!small)

![1593389797_5ef932e571d50.png!small](https://image.3001.net/images/20200629/1593389797_5ef932e571d50.png!small)

## 宏安装

攻击者在长时间使用PE附件传播FlowCloud后，于2019年11月开始使用恶意宏文档传播FlowCloud，在2019年7月和8月使用了LookBack。FlowCloud宏使用了
.pem文件，这些文件随后被重命名为“ pense1.txt”，随后被另存为“gup.exe”，并使用名为“
Temptcm.tmp”的certutil.exe执行该文件。

![1593390026_5ef933caceaf7.png!small](https://image.3001.net/images/20200629/1593390026_5ef933caceaf7.png!small)

![1593390037_5ef933d5ee5d1.png!small](https://image.3001.net/images/20200629/1593390037_5ef933d5ee5d1.png!small)

LookBack恶意软件针对目标为美国公用事业部门，其模仿工程许可委员会对目标进行攻击，FlowCloud使用完全相同的方法。两个宏版本的LookBack
Gup代理工具和FlowCloud恶意软件最终执行方法相同，但FlowCloud宏引入了一种新的恶意软件传递方法。

早期LookBack版本将有效负载包含在.pem文件中，这些文件在用户执行附件文件时被删除。FlowCloud从DropBox
URL下载有效负载，.pem格式的FlowCloud恶意软件存储为“ Pense1.txt”。

![1593390265_5ef934b9ae2ac.png!small](https://image.3001.net/images/20200629/1593390265_5ef934b9ae2ac.png!small)

FlowCloud宏还包含一组try ... catch语句，最初会尝试从DropBox
URL下载FlowCloud负载，如果无法检索有效负载，catch语句试图从[http://ffca.caibi379](http://ffca.caibi379/)[.]com/rwjh/qtinfo.txt检索恶意软件资源。

![1593390493_5ef9359df1c45.png!small](https://image.3001.net/images/20200629/1593390493_5ef9359df1c45.png!small)

## FlowCloud恶意软件

FlowCloud恶意软件是一个多阶段有效负载，其中包含用C
++编写的大型代码库。恶意软件能够根据命令（包括访问剪贴板，已安装的应用程序，键盘，鼠标，屏幕，文件，服务和进程）提供RAT功能，恶意软件至少从2016年7月以来就一直处于活动状态。

下图显示了FlowCloud加载程序功能流程图，简要说明了FlowCloud程序功能。

![1593390847_5ef936ff80a43.png!small](https://image.3001.net/images/20200629/1593390847_5ef936ff80a43.png!small)

> 1、恶意软件首先由恶意宏执行Gup.exe，然后由宏执行文件EhStorAuthn.exe。
>
>
> 2、EhStorAuthn.exe提取后续的有效负载文件组件，并将它们安装到目录C:\Windows\Media\SystemPCAXD\ado\fc，该文件还将设置注册表值“KEY_LOCAL_MACHINE\SYSTEM\Setup\PrintResponsor\<2-4>”。
>
>
> 3、EhStorAuthn.exe是QQ使用的合法可移植执行文件，其初始名称为QQSetupEx.exe。此文件用于加载dlcore.dll，作为其下载程序的一部分。
>
>
> 4、Dlcore.dll是攻击者精心制作的DLL，它会充当shellcode的作用，从名为rebare.dat的文件中提取shellcode。该文件模仿合法的QQ组件。当执行rebare.dat中的shellcode时，它将执行一个名为rescure.dat的RAT安装程序文件。
>
> 5、Rescure.dat是XOR加密的DLL文件，它安装了responsor.dat，该应用程序具有键盘记录和管理RAT功能。
>
>
> 6、Responsor.dat将几个模块（rescure86.dat或rescure64.dat）解压缩到%TEMP%\\{0d47c9bc-7b04-4d81-9ad8-b2e00681de8e}，并将解压缩的文件命名为“
> FSFilter Activity Monitor”或“ FltMgr”。
>
> 7、最后，当调用rescure.dat函数“ startModule”时，Responsor.dat启动RAT。
>
> 8、该恶意软件还使用了几个合法的Microsoft Windows文件进行线程注入。

恶意软件将其配置和键盘记录组件使用的驱动程序一起存储在注册表中，同时还会生成其他几个不同的注册表项。

![1593391203_5ef9386370359.png!small](https://image.3001.net/images/20200629/1593391203_5ef9386370359.png!small)

## FlowCloud配置

FlowCloud加载程序组件EhStorAuthn.exe在安装的早期会将恶意软件配置存储在注册表中。
注册表数据由多个加密头（使用XOR和ROR）组成，并且使用修改的AES算法对数据进行加密。 下图显示了FlowCloud配置示例：

![1593391284_5ef938b4b22cc.png!small](https://image.3001.net/images/20200629/1593391284_5ef938b4b22cc.png!small)

## 命令与控制

FlowCloud恶意软件利用自定义二进制C2协议，并会将配置更新，文件传递和命令执行作为独立线程处理。样本使用端口55555进行文件传递，确定了IP：188.131.233.
27。 请求和响应由多个加密头（使用XOR和ROR）和TEA加密数据组成，下图为解析初始信标示例。

![1593391438_5ef9394eb106a.png!small](https://image.3001.net/images/20200629/1593391438_5ef9394eb106a.png!small)

## 总结

LookBack和FlowCloud恶意软件在2019年11月针对美国公用事业提供商的持续活动中利用了多种工具。这两个恶意软件家族在概念和开发上都表现出成熟的水平，FlowCloud恶意软件的可扩展代码库表明，其早在2016年就已开始运营。其主要利用网络钓鱼策略提高攻击成功率，并非常有针对性进行社会工程学攻击。

## IOCs

![1593391683_5ef93a43dbe73.png!small](https://image.3001.net/images/20200629/1593391683_5ef93a43dbe73.png!small)

![1593391701_5ef93a5509391.png!small](https://image.3001.net/images/20200629/1593391701_5ef93a5509391.png!small)

![1593391739_5ef93a7b65563.png!small](https://image.3001.net/images/20200629/1593391739_5ef93a7b65563.png!small)

 **参考来源**

> [proofpoint](https://www.proofpoint.com/us/blog/threat-insight/ta410-group-> behind-lookback-attacks-against-us-utilities-sector-returns-new)

