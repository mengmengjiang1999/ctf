**作者：启明星辰ADLab  
公众号：<https://mp.weixin.qq.com/s/bXPmfp316WC6R0yHULU-jA>**

### 一 概述

近期，启明星辰ADLab接连捕获到大量针对全球制造、运输、能源等行业及部分医疗机构发起的鱼叉式钓鱼邮件定向攻击。从邮件的分析结果来看，受害者大多遍布于美国、加拿大、德国、中国、英国、法国、西班牙等国家和地区。攻击者以“装船通知单”、“装箱交货价单”、“紧急运输文件”等主题邮件作为诱饵向攻击目标植入信息窃密木马（Agent
Tesla、Formbook、Lokibot）和远程控制程序（NanoCore、Remcos）。我们通过对收集到的攻击工具进行去重并做分析，最终发现此次攻击活动关联着1362个攻击样本。通过同源分析，我们发现这批样本中有近80%是同一款恶意软件，对其分析判定后确定这正是近期被大范围传播且极为活跃的新型下载者病毒Guloader。Guloader是一款免杀能力很强的病毒，近期全球各大厂商均对其进行了预警，其具备沙盒逃逸、代码混淆、反调试、C&C/URL加密和有效载荷加密等多种能力。由于Guloader具有较强的免杀能力和对抗机制，因而受到大量黑客的青睐。本批攻击中，攻击者就广泛地利用Guloader下载者病毒结合云服务来分发窃密工具或远程控制程序（RAT）。

我们通过溯源分析确定此次攻击活动来自尼日利亚，并且关联出了大批量的黑恶意域名（攻击者使用境外的Duck
DNS注册动态域名）和IP地址。通过对攻击者使用的网络基础设施，追踪分析发现此次攻击活动最早可追溯到2020年1月。进一步分析我们发现，这批攻击者的攻击动机、攻击目标、作业风格与SWEED黑客组织极为相似，他们还有着相似的攻击习惯，并使用相同窃密木马程序，以及同样风格的C&C地址。因此，我们推断这批攻击背后应该就是SWEED黑客组织。SWEED是一个来自尼日利亚的以获取经济利益为主要目的的黑客组织，其最早出现于2017年，常利用公开披露的漏洞，借助鱼叉式钓鱼邮件来传播木马程序，如Agent
Tesla、Formbook和Lokibot等。该组织曾在早期被披露的攻击活动中，通过窃取被攻击目标用户和企业敏感信息实施中间人攻击，诱使财务人员将款项转至指定账户，是一个典型的网络诈骗团伙。

启明星辰ADLab对本次攻击活动的攻击过程和攻击手法进行了详细地分析和溯源，并对其所使用的新型恶意软件和C&C基础设施进行了深入研究。提醒各大企业单位做好安全防范工作，谨防后续可能出现的攻击。

### 二 攻击目标和受害者分布

截止到2020年6月，我们发现攻击者的重点目标为从事对外贸易的中小型企业，其目的是通过植入特定的后门以实现对目标计算机进行信息收集和长期监控，并为接下来的横向移动攻击提供基础。

#### 2.1 地域分布

通过对已知的SWEED组织攻击行动中受害者的国家和地区分布情况进行统计（如图2-1），我们可以看到该组织发起的攻击活动覆盖了很多国家和地区，由此猜测，攻击者在攻击目标地理位置的选择上并没有特定的指向性。

![
](https://images.seebug.org/content/images/2020/07/3a6ac607-6b62-484d-926c-e92411ea54ef.png-w331s)
图2-1 受害者国家地域分布图

#### 2.2 行业分布

统计结果显示（如图2-2），此次SWEED组织在面向全球的攻击中，运输、制造业和能源行业依然是其重点针对的目标对象。

![
](https://images.seebug.org/content/images/2020/07/4c983d53-89bd-4295-b9c5-8f8cc6290e19.png-w331s)
图2-2 受害者行业分布图

### 三 攻击事件分析

本小节总结了该组织在近些年的攻击活动时间点、此次行动中使用的攻击手法以及攻击流程。

#### 3.1 攻击活动时间线

为了对黑客组织在此次攻击活动使用的策略和技术进行全面的了解，启明星辰ADLab研究人员将目前关联到的该组织近几年的主要活动做了梳理和总结，并绘制了“SWEED组织”活动时间轴（如图3-1）。从时间轴可以看出，该组织的大部分活动都具有一致性——借助带有恶意附件的鱼叉式钓鱼邮件分发远控木马程序（RAT），并且行动中使用的木马程序主要是以Agent
Tesla为主。

![
](https://images.seebug.org/content/images/2020/07/b773c1ca-9ba8-4b32-93b9-5df198cfe053.png-w331s)
图3-1 SWEED组织相关活动时间轴

#### 3.2 攻击手法和特点

SWEED组织在初始环节主要以投递钓鱼邮件开始展开攻击，攻击者在前期对目标用户进行深入调研，选取与目标用户所属行业或领域相关的内容来构造邮件和恶意文档。随后将精心制作的主题如”采购订单”、“紧急运输文件”、”装船通知单“等文档添加在邮件附件中发送给目标用户，诱使其下载附件，目标用户一旦打开带有漏洞的恶意文档，触发漏洞的恶意代码就将会在后台静默下载和执行恶意软件，从而窃取目标用户的敏感信息并对其主机进行控制。

##### 3.2.1 鱼叉邮件

启明星辰ADLab通过对SWEED组织年初至今的攻击行动进行监测和关联分析后，梳理出几十起定向目标的攻击钓鱼邮件。部分相关邮件信息见表3-1。

![
](https://images.seebug.org/content/images/2020/07/7c160a62-1085-46e1-b419-83faaf91705a.png-w331s)

![](https://images.seebug.org/content/images/2020/07/ea903a58-adb5-4e30-b881-4f036f1bf191.png-w331s)

表3-1 部分钓鱼邮件案例信息

通过分析这些邮箱发件人所属公司的注册信息以及其官网信息，我们发现多数公司网站均为合法网站，由此猜测攻击者使用的这些邮箱，有可能来自被入侵和盗用的合法实体或个人。虽然收件人的信息很多无法看到，但是从邮件的主题以及正文内容不难看出，攻击者企图利用运输货物清单、装箱交货价单、物品到货通知单、海上新订单等邮件向运输商、制造商及其合作商进行有针对性的攻击活动。下面我们从以上邮件中列举一个做简单分析。

在此案例中，攻击者试图使用“VSL: MV FORTUNE TRADER”主题冒充“MV Fortune Trader”。船舶FORTUNE
TRADER是一艘建于1994年的集装箱船，该船舶的注册国家为韩国。

![
](https://images.seebug.org/content/images/2020/07/9b8627ac-c6fa-44b7-a10c-4329600ed15e.png-w331s)
图3-2 船舶FORTUNE TRADER相关信息

邮件正文与主题保持一致，显示该邮件是来自超捷国际物流公司。该公司总部位于台湾台北，主要提供海运、空运和中港运输等业务。

![
](https://images.seebug.org/content/images/2020/07/c53b2799-c35f-42c2-a192-069085bac6dd.png-w331s)
图3-3 超捷国际物流公司主页

邮件正文如图3-4：

![
](https://images.seebug.org/content/images/2020/07/33d184e3-7d72-4739-80d1-a3792e7d7285.png-w331s)
图3-4 邮件正文信息

对邮件信息进行解析后如图 3-5所示，发件人的邮件地址是印度尼西亚一家名为“PT.INTI PERSADA
NUSANTARA”电机设备公司的合法域，而该邮件实际上是由托管在us10.rumahweb.com上的Roundcube
Web邮件服务器发送。这里收件人地址之所以显示为“Undisclosed-Recipient”（导致无法看到收件人信息），猜测攻击者是在使用Roundcube
Webmail/1.3.8软件群发邮件时，为了不让收件人看到其他接收邮件人的地址，故将此处设置为Undisclosed-Recipient。

![
](https://images.seebug.org/content/images/2020/07/d6796e60-732f-490c-bafc-d9988e0ef59e.png-w331s)
图3-5 部分邮件头部信息

##### 3.2.2 诱饵文件

通过对该批截获的邮件进行分析所得，攻击者使用的攻击载荷类型总共有四种。下面将列举典型的攻击载荷及其所对应的钓鱼邮件。

(1) 携带漏洞文档

图3-6是一封攻击者冒名航空货运公司发送给客户的预约请求回复邮件，附件伪装成船舶详细信息表单。该文档使用微软Office经典漏洞CVE-2017-11882，当用户打开恶意文档时，嵌入到文档中的恶意程序则会自动加载。该漏洞的特点是在整个过程中用户完全无感知，且在断网的情况下仍然可达到有效攻击，所以成为各大APT组织必用漏洞利用库之一。

![
](https://images.seebug.org/content/images/2020/07/3fc47012-4a09-4d1b-b264-f8ba7527f75b.png-w331s)
图3-6 携带漏洞文档案例1—邮件截图

（2）携带GZ格式的压缩文档

图3-7是攻击者发送给总部位于比利时的一家多元化的工业制造商的邮件，该邮件使用热门的COVID-19为主题，并通过正文描述谎称恶意附件GZ压缩文档中包含采购单，诱使受害者下载。

![
](https://images.seebug.org/content/images/2020/07/c07b3a0b-f48c-481f-b173-54d72a4a06b3.png-w331s)
图3-7 携带GZ文档案例2—邮件截图

附件里面是伪装成bat文件的Guloader下载器。

![
](https://images.seebug.org/content/images/2020/07/9415eef9-36a3-409a-9c86-2cd1c4abd372.png-w331s)
图3-8 GZ压缩包里的文件

（3）携带ISO格式的文档

由图
3-9可见，攻击者将邮件附件伪装成系统镜像ISO文件（使用ISO文件可用于绕过垃圾邮件过滤器），将其命名为“COVID-19解决方案宣布”诱骗用户点击。嵌入在ISO恶意附件中的可执行文件为Guloader下载器。

![
](https://images.seebug.org/content/images/2020/07/05083637-6eaf-4d3a-8e75-b5accb284595.png-w331s)
图3-9 ISO压缩包里的文件

（4）携带html格式的文件

图3-10是攻击者冒充DHL Express国际快递公司发送给德国一家光学组件制造商的钓鱼邮件，邮件附件被命名为装船通知单并以html形式诱骗受害者点击。

![
](https://images.seebug.org/content/images/2020/07/ec4a71e6-6f7d-4bd8-83d4-095822e9322a.png-w331s)
图3-10 携带html文件案例3—邮件截图

##### 3.2.3 恶意软件托管位置

在攻击活动中，攻击者经常利用远程配置来控制恶意软件，而安全人员通过研究分析不同的恶意软件配置（例如主机地理位置和DNS信息），可以深入的了解和追踪攻击者使用的基础设施。我们在研究过程中将收集到的大量样本数据进行提取和整合，发现SWEED组织此次实施攻击行动所使用的恶意软件配置，主要应用了Guloader下载器配置选项中的利用云服务分发恶意软件的功能。攻击者之所以使用正规的云存储平台来托管恶意软件，是因为这些云平台多数是受信任的且有助于绕过商业威胁检测产品。虽然Google
Drive等云平台通常也会执行防病毒检测，但如果有效载荷是被加密后再存储，就可以躲过此类限制，并能有效的阻止安全人员对黑客组织的基础设施进行追踪。图3-11为恶意载荷样本托管平台的使用占比率。根据图中显示的数值可得，Google
Drive为恶意软件主要使用的托管平台。除此之外，还有部分恶意软件会托管在已被攻陷的合法网站上。

![
](https://images.seebug.org/content/images/2020/07/64ff6e33-0e09-4673-957b-636c3d028c31.png-w331s)
图3-11有效载荷托管平台的使用率

除了Google Drive和OneDrive，下面我们列举出几个攻击者使用的其他云托管平台。

files.fm是国外一家提供文件云存储平台的信息技术公司。图3-12是保存在该平台的加密的恶意文件。

![
](https://images.seebug.org/content/images/2020/07/bd11e56d-cadf-4e0f-94e8-e68e623f4a28.png-w331s)
图3-12 云托管平台例1

sendspace是一家免费文件托管平台。图3-13是攻击者上传到该平台进行托管的恶意软件。

![
](https://images.seebug.org/content/images/2020/07/237d471f-ac21-49d2-83f6-16bef4604c59.png-w331s)
图 3-13 云托管平台例2

dmca.gripe是一个免费的文件托管平台，其主页如图3-14所示。

![
](https://images.seebug.org/content/images/2020/07/f38afab2-9d2a-4dc5-b712-75fbb8b76df7.png-w331s)
图3-14 云托管平台例3

#### 3.3 攻击流程

我们对这批攻击活动进行归纳分析后发现绝大部分攻击具有相同的攻击流程，其攻击的流程如图3-15。

![
](https://images.seebug.org/content/images/2020/07/b0e1c1a6-1025-4052-b3aa-4f1ea6a568c6.png-w331s)

3-15 攻击流程图

攻击者伪装成物流或船舶等公司人员，向目标企业投递携带附件的钓鱼邮件，附件类型包括：包含漏洞的恶意文档、GZ格式的压缩包、ISO文件和HTML文件。在多数情况下，这些附件起初都会包含或下载Guloader下载器（其他情况下为远控木马）。Guloader开始执行时，先对储存在代码部分的shellcode进行解密，再将解密后的shellcode注入到RegAsm.exe系统文件中；接着RegAsm.exe中的shellcode再从指定的云平台地址下载加密的payload，并在内存中解密执行payload（远控木马），最后通过C2对目标主机进行信息窃取和远程控制。

此次攻击活动中使用到的窃密和远控木马包括：Agent
Tesla（是一款知名的商业窃取木马，主要用于浏览器、邮件客户端、FTP工具、下载器等用户账号密码和WiFi凭证的窃取。）；Formbook（是一款信息窃取木马，其主要以窃取用户电脑机密信息为主，包括键盘记录、剪贴板记录、cookie会话与本地密码等等。）；Lokibot（一款窃密木马，其通过从多种流行的网络浏览器、FTP、电子邮箱客户端、以及PuTTY等IT管理工具中获取凭证，来窃取用户的密码和加密货币钱包）；NanoCore（是一款.net编写的远控软件，其具有键盘监控、实时视频操作、语音、命令行控制等完全控制远程主机的功能。）；Remcos（一款远控软件，包括下载并执行命令、键盘记录、屏幕记录以及使用摄像头和麦克风进行录音录像等功能。）。

鉴于我们分析的这些木马在功能和技术上与旧版类似，并没有发现太多的变化点，所以在此我们仅对其主要功能做了简单的描述，本文后续便不再过多的详细描述其具体的技术细节，如有需要大家可查看文末的参考文献。在下个章节，我们主要对SWEED组织新引入的Guloader恶意代码进行完整详细地剖析。

### 四 技术分析

正如前文所述，我们目前收集到的电子邮件的附件主要分为四类。虽然其释放恶意软件的形式不同，但它们的主要功能行为都基本一致。在这里，我们选取一个典型案例进行详细分析。

#### 4.1 钓鱼邮件

图4-1为攻击者针对美国一家防滑产品制造商进行攻击的钓鱼邮件，此邮件于美国山地时区时间2020年4月29日（周三）02:31被发送到该公司。邮件标题为“Purchase
Order /APO-074787648”，正文描述为“请查看清单和确认商品库存”，并附有同名恶意文档“Purchase Order
/APO-074787648”。

![
](https://images.seebug.org/content/images/2020/07/672c99b2-43e7-4999-8d18-479759286be0.png-w331s)
图4-1 钓鱼邮件内容

#### 4.2 恶意文档

样本“Purchase Order
/APO-074787648.ppsx”利用了沙虫漏洞CVE-2014-4114的补丁（MS14-060）绕过漏洞CVE-2014-6352。沙虫漏洞是Windows
OLE任意代码执行漏洞，该漏洞出现在Microsoft
Windows服务器上的OLE包管理器上。攻击者通过利用该漏洞在OLE打包文件（packer.dll）中下载并执行类似的INF文件，来达到执行任意命令的目的。虽然微软为沙虫漏洞发布补丁（MS14-60），但攻击者还可通过构造特定的CLSID和OLE
Verb来绕过MS14-160补丁的限制（CVE-2014-6352）。下面我们以本次行动中使用的恶意文档为例，对该漏洞的实现原理做简单的分析。

图4-2为此案例中使用的ppsx漏洞攻击文档内容。 ![
](https://images.seebug.org/content/images/2020/07/c959f21d-dd5d-45d6-ac09-82aba98d0dd2.png-w331s)

图4-2 ppsx漏洞文档内容

我们解压PPXS文档可以看到，在“Purchase Order APO-074787648.ppsx\ppt\slides
\slides.xml”中，指定了嵌入的对象id=rld3。 ![
](https://images.seebug.org/content/images/2020/07/45237a6d-5c28-41df-adf4-18a7b55d0a3e.png-w331s)

图4-3 “slides.xml”文件内容

在“Purchase Order
APO-074787648\ppt\slides_rels\slide1.xml.rels”中指定了rld3对应“ppt\embeddings\”目录下的oleObject1.bin文件。
![
](https://images.seebug.org/content/images/2020/07/41f4cb46-7ea8-4adf-9922-2a31da848711.png-w331s)

图4-4 “slide1.xml.rels”文件内容

“Purchase Order
APO-074787648.ppsx\ppt\embeddings\”目录下的“oleObject1.bin”文件内嵌一个OLE
Package对象，嵌入文件为PE可执行程序。

![
](https://images.seebug.org/content/images/2020/07/675d5a37-b4ef-4788-8835-49a0d1e7c77d.png-w331s)

图4-5 “oleObject1.bin”文件内容

CVE-2014-4114漏洞的成因是packager.dll中CPackage::Load方法加载对应的OLE复合文档对象时，针对不同类型的复合文档进行不同的处理流程，但其中对某些复合文档中嵌入的不可信来源文件没有做处理。由此攻击者可使用伪造OLE复合文档的CLSID来达到执行特定文件的目的。微软在MS14-060补丁中，通过添加MarkFileUnsafe函数对文件进行MOTW处理，将其Security
Zone标记为“此文件来自其他计算机”，运行时会弹出安全警告窗口。

![
](https://images.seebug.org/content/images/2020/07/94d546b6-a118-494e-94dc-3d17ea06d666.png-w331s)
图4-6 “%TEMP%\NEW ORDER.exe”标记为不可信文件

但就算受害者已安装MS14-060的补丁，攻击者还是可以通过构造特定的CLSID和OLE
Verb来改变执行流程，从而绕过该补丁（CVE-2014-6352漏洞）。对于一个exe文件，即使被标记为URLZONE_INTERNET，右键点击以管理员权限执行该exe文件，那当程序运行时便不会再弹出“安全警告”（如图4-6）的提示，而是以（如图4-7）UAC
提示窗弹出。

![
](https://images.seebug.org/content/images/2020/07/f14b9d4c-4d5d-4509-b177-f49ae29e7873.png-w331s)
图4-7 弹出的UAC提示窗

由此可知，当受害者打开此PPSX恶意文档时，自动播放模式便会开启，同时“%TEMP%\NEW
ORDER.exe”将被释放在临时目录中。如果受害者选择“是”，恶意代码将会被执行。而如果受害者的系统处于UAC关闭状态或在获取了管理员权限的情况下，该UAC安全警告窗口则不会弹出，“NEW
ORDER.exe”会被静默地执行。

#### 4.3 GuLoader

如上文所述，最后被执行的“NEW ORDER.exe”可执行文件实际上便是文章开头提到的Guloader恶意软件（在后续对“NEW
ORDER.exe”的详细分析中，我们均使用“Guloader”来替代该文件名）。Guloader是一款新型的恶意软件下载器，其本身具有复杂的执行流程，通过采用各种代码混淆和随机化、反沙箱、反调试和数据加密等机制来对抗安全产品的检测。下面我们将对该GuLoader进行深入的挖掘分析。

##### 4.3.1 执行流程

如图4-8所示，
GuLoader首先将储存在代码部分的加密Shellcode解密并执行。这段Shellcode的主要功能为：以挂起方式创建一个系统子进程，之后将本段Shellcode自身注入到子进程并修改程序入口点为Shellcode处执行。最后从托管服务器上下载加密的BIN文件，成功下载后将其解密和运行。

![
](https://images.seebug.org/content/images/2020/07/522606ca-636d-43bd-995c-217d4a0762dd.png-w331s)
图4-8 Guloader执行流程图

##### 4.3.2 EXE可执行文件

（1）代码混淆

Guloader可执行文件是由Visual Basic
6语言编写的。使用工具查看后发现，其并未使用商业壳进行自身保护，而是使用混淆壳尝试对抗安全产品的查杀。由于杀软对商业壳比较敏感，并且商业壳检测和脱壳技术也比较成熟，所以混淆壳不失为一个不错的选择。混淆壳一般不存在通用的检测方法，并且静态脱壳相对较难，所以其恶意行为不易被发现，从而可长时间的存活在目标机器上。对于逆向分析人员来讲，分析这种带混淆壳的样本往往会花费大量的精力，无形的增加了人力和时间成本。

图4-9是一段混淆代码的截取，这部分代码使用了数据混淆中的常量拆分，主要目的是隐藏真实的代码逻辑，让分析者内心奔溃。

![
](https://images.seebug.org/content/images/2020/07/9f47a694-7a90-4d99-b9cb-006c2861b0ab.png-w331s)
图4-9 部分混淆代码

（2）代码解密

恶意软件首先计算出用于解密shellcode的密钥，其值为：0x24EBE470。

![
](https://images.seebug.org/content/images/2020/07/66880358-d589-4afb-a768-55519a6f1eb7.png-w331s)
图4-10 获取密钥的恶意代码

接着，为shellcode申请内存空间，再使用密钥进行XOR运算解密Shellcode并执行。

![
](https://images.seebug.org/content/images/2020/07/3ecfda7c-a888-4784-8b59-2247a9cf78ca.png-w331s)
图4-11 解密和执行shellcode

4.3.3 ShellCode

解密后的shellcode前期也采取了大量的对抗手段，使用各种代码混淆、沙箱检测、反调试等技术手段来规避安全产品的行为监测和查杀。仅当通过各种检查判断条件后，恶意代码才开始执行主功能行为。下面我们将对恶意代码做详细的分析。

（1）检测功能

  * 代码混淆

将解密后的shellcode从内存中dump出来并使用IDA反编译，可以看到shellcode中使用的混淆技术。恶意代码在执行过程中插入混淆函数，该函数的过程被分割成多个跳转流程，一直到最后再
jmp到原来的正常代码中继续执行下面的流程。图4-12是shellcode在入口处调用的此类混淆函数的代码片段，很显然通过该方法，能够有效的扰乱分析者对样本进行分析，严重降低了分析效率。

![
](https://images.seebug.org/content/images/2020/07/4276aa8c-480c-417e-91c3-0b4113d2764f.png-w331s)
图4-12 混淆后的代码片段

  * 动态获取API函数

接着，恶意代码通过访问PEB->LDR中的InMemoryOrderModuleList获取kernel32.dll的基址。遍历提取该模块导出表结构中存放函数名的数组，并依次将名称字符串作为参数传入到哈希算法函数中做运算，再将结果与硬编码数据做比较，以此方法来查找GetProcAddress函数。

![
](https://images.seebug.org/content/images/2020/07/cbb81390-d72c-499f-8a85-a5a898f1eefd.png-w331s)
图4-13 查找GetProcAddress函数

此处使用的是djb2的算法，
djb2是一个产生随机分布的哈希函数，与LCG的算法相似。由于该函数构造简单，使用移位和相加的操作，所以常被用来处理字符串。具体算法见图4-14。

![
](https://images.seebug.org/content/images/2020/07/6eafaea9-fad0-425a-825e-e731838e811b.png-w331s)
图4-14 djb2算法代码截图

由此我们可以看到，恶意代码在函数的获取方面是利用LoadLibrary和GetProcAddress这两个函数进行动态的获取。具体如图4-15所示。

![
](https://images.seebug.org/content/images/2020/07/de15eeeb-353d-4524-9ce8-e0d8288b304a.png-w331s)
图4-15 动态获取API函数

  * 沙箱检测

恶意代码枚举窗口数量，如果值小于12则退出进程，以此来检测自身是否运行在沙箱环境中。

![
](https://images.seebug.org/content/images/2020/07/6e0eb44c-9073-42f1-96ef-76ebb57b032e.png-w331s)
图4-16 沙箱检测代码

  * 反调试技术

方法1： 调用ZwProtectVirtualMemory函数修改ntdll.dll的“.text”节属性为可读可写可执行。

![
](https://images.seebug.org/content/images/2020/07/5a8e9061-67ce-4793-9450-4c05e87b25a6.png-w331s)
图4-17 修改ntdll.dll节属性

恶意代码通过修改DbgBreakPoint和
DbgUiRemoteBreakin函数代码，让调试器无法附加调试程序（如图4-18和图4-19）。给call调用后面指定一个未知地址，以此引发调试器崩溃退出。

![
](https://images.seebug.org/content/images/2020/07/ae9201ab-d558-4c46-9e06-931afa031775.png-w331s)
图4-18 DbgBreakPoint函数代码修改前后对比

![
](https://images.seebug.org/content/images/2020/07/9b8158fe-1c3f-40db-998c-7cd1be8b9d8a.png-w331s)
图4-19 DbgUiRemoteBreakin函数代码修改前后对比

方法2：

将ZwSetInformationThread函数的第二个参数设置为ThreadHideFromDebugger
（值为17），作用是在调试工具中隐藏线程。如果恶意软件处于被调试状态，那么该函数就会使当前线程（一般是主线程）脱离调试器，使调试器无法继续接收该线程的调试事件。效果就像是调试器崩溃了一样。

![
](https://images.seebug.org/content/images/2020/07/091d64a5-b545-462f-b5bd-6c6c7c2579de.png-w331s)
图4-20 隐藏线程达到反调试目的

方法3：

在使用ZwAllocateVirtualMemory函数申请内存空间时，为防止分析人员在调试时对关键函数下断点，恶意代码会提前将该函数的功能实现代码复制到本进程空闲空间中，使得后续在使用此函数时直接跳转到自身代码中执行。

![
](https://images.seebug.org/content/images/2020/07/58afdee8-870f-4cb9-a20d-410771189ad9.png-w331s)
图4-21 复制函数功能实现代码

方法4：

在调用部分敏感API函数时，会先调用自定义的检查函数做判断，以减少被安全产品检测的几率。

![
](https://images.seebug.org/content/images/2020/07/76344367-b5f2-4714-a5d7-cea5dbdbd6a5.png-w331s)
图4-22 检查函数是否被下断点或挂钩

该自定义的检查函数的主要功能：

① 将调用该函数前的shellcode代码（正序）按字节与0x4字节的返回地址做异或运算 进行加密处理；

② 调用ZwGetContectThread函数，通过检查_CONTEX结构中的Dr寄存器来判断是否 在调试环境中；

③ 判断此次要检查的关键API函数是否被下断点或挂钩。如果结果为否，则调用该API函数，否则程序直接崩溃退出；

④ 同“方法①”对shellcode代码（倒序）进行解密并跳转到返回地址处执行后续流程。

![
](https://images.seebug.org/content/images/2020/07/68143c27-3778-47f2-ac33-fd563c3ed4be.png-w331s)
图4-23 自定义检查函数代码

（2）恶意行为执行功能

如果以上一系列的沙箱以及反调试检测都通过，恶意代码则开始执行以下流程：

① 动态获取图4-24中的API函数，并将函数调用地址保存在堆栈中。

![
](https://images.seebug.org/content/images/2020/07/ba15e7c0-9ee8-4c56-a5e3-c2bba784d6fe.png-w331s)
图4-24 动态获取的API函数名称

② 根据指定地址处保存的数据内容特征（如果恶意代码未执行过创建子进程流程，那 么该地址处原数据为无效内容；否则，此处保存的是当前进程的全路径。）来判定是
否需要创建子进程。

![
](https://images.seebug.org/content/images/2020/07/7fd5f5ac-d5c0-46ca-8df1-0fc759c923cf.png-w331s)
图4-25 判断是否需要创建子进程

![
](https://images.seebug.org/content/images/2020/07/e481a500-666c-43ee-84ba-76820c4e89f9.png-w331s)
图4-26 对指定地址处保存的数据内容做判断

③ 调用CreateProcessInternal函数以挂起模式创建RegAsm.exe进程。

![
](https://images.seebug.org/content/images/2020/07/e9bbc607-ee01-4850-9313-d3ba290fbfde.png-w331s)
图4-27 创建系统子进程

④ 调用ZwOpenFile函数，获得映射文件mstsc.exe的句柄。

![
](https://images.seebug.org/content/images/2020/07/db778e3b-5f57-4467-a532-74f546c28bc0.png-w331s)
图4-28 获取mstsc.exe的句柄

⑤
使用ZwCreateSection和NtMapViewOfSection函数将“mstsc.exe”文件映射到RegAsm.exe内存中的0x00400000位置上。

![
](https://images.seebug.org/content/images/2020/07/698826e9-1723-4968-a9d1-3ba843e496fc.png-w331s)
图4-29 映射文件

⑥ 在傀儡进程中申请内存空间，并将我们正在调试的整个shellcode写入到目标内存中。

![
](https://images.seebug.org/content/images/2020/07/a0a2310e-c2a3-4caa-8348-6553937c3cf4.png-w331s)
图4-30 写入shellcode到系统子进程中

⑦ 使用ZwGetContextThread和ZwSetContextThread函数，获取和修改挂起的子
线程上下文中寄存器值，以实现重定向到shellcode入口处执行的目的。

![
](https://images.seebug.org/content/images/2020/07/0c7880d8-1441-441a-b823-b5471b005052.png-w331s)
图4-31 修改系统子进程的执行入口点

⑧ 若“步骤⑤”操作成功，则恢复执行子进程；否则结束当前程序。

![
](https://images.seebug.org/content/images/2020/07/50429c90-8d94-4550-aa3c-c2bb52f983bb.png-w331s)
图4-32 判断步骤⑤是否操作成功

（3）成功注入后恶意行为功能

我们在恶意代码调用NtResumeThread函数前，附加RegAsm.exe进程并在注入的shellcode执行处设置断点（如图4-33），然后再继续执行该函数来恢复线程运行。该shellcode前部分与之前的操作流程相同，将前文描述的各种检测重新执行一遍，直到在“判断是否创建子进程”处跳转到另外的分支流程。下面我们继续对后续功能进行详细地分析。

![
](https://images.seebug.org/content/images/2020/07/8d4adb27-6220-4069-84b2-318f297c4133.png-w331s)
图4-33 Shellcode执行处代码

判断开启RegAsm.exe程序的父进程是否为“C:\Users***\directory\filename.exe”。

如果不是，则将当前父进程文件复制到该目录中，将其命名为filename.exe并重新执行；

如果是，则在注册表HLM\Software\Microsoft\Windows\CurrentVersion\RunOnce目录里将该路径添加在“Startup
key”中，以实现长期驻留的目的。

![
](https://images.seebug.org/content/images/2020/07/5ab75fad-461f-4b3d-bf4a-cbd518e8e391.png-w331s)
图4-34 添加注册表信息代码

![
](https://images.seebug.org/content/images/2020/07/4747b7df-42a5-4a2c-a8de-43685a1329e6.png-w331s)
图4-35 添加注册表开机启动项

成功添加注册表项后，恶意代码则开始使用winnet.dll库中的Internet API函数从云托管服务器下载加密的payload。

![
](https://images.seebug.org/content/images/2020/07/d35feca2-b59f-49d0-a060-7a9e1f2adeb3.png-w331s)
图4-36 从云托管服务下载payload

下载完成后，恶意代码再将硬编码的值与将payload的大小做比较，以此来检查文件的完整性。如果大小不匹配，恶意代码则会重新下载文件，直到完全匹配为止。

![
](https://images.seebug.org/content/images/2020/07/02008fa6-024a-4a28-8867-972830989db7.png-w331s)
图4-37 检测payload大小

下载到的payload文件是由0x40个字节的HEX小写数字和加密的PE文件组成，具体如图4-38所示。

![
](https://images.seebug.org/content/images/2020/07/e3e5789a-3aba-412a-aecb-c16d444867d9.png-w331s)
图4-38 payload内容

接着，恶意代码再使用自定义解密函数对下载的payload进行异或解密。其密钥储存在shellcode代码0x2032偏移处，密钥长度为0x214。解密函数内容如图4-39所示。

![
](https://images.seebug.org/content/images/2020/07/0148beea-0afb-4754-99a3-a30cf4535b2b.png-w331s)
图4-39 payload解密函数

解密后的PE文件如图4-40所示。

![
](https://images.seebug.org/content/images/2020/07/57b0fe44-1b23-40c3-b926-4b0176165f74.png-w331s)
图4-40 解密后的文件内容

最后，恶意代码将解密后的PE文件覆盖0x00400000基址的内容，并跳转到入口点执行payload恶意程序。

![
](https://images.seebug.org/content/images/2020/07/45a6c8b0-c277-44d3-9e13-9db12f6e1354.png-w331s)
图4-41 执行payload

在此次分析的案例中，解密出的payload是Agent
Tesla。对于该恶意软件，在此我们就不再做过多的介绍和分析了。下面我们会对黑客组织的C&C服务器基础设施展开追踪溯源。

### 五 溯源追踪

#### 5.1 C&C基础设施

截止到目前为止，我们通过提取和整理所有关联样本中的IP地址和域名信息，可以看到此次攻击行动主要以动态域名为主，大部分域名都是通过境外的Duck
DNS注册。图5-1为SWEED黑客组织使用的部分域名、IP、样本的对应关系。

![
](https://images.seebug.org/content/images/2020/07/0a04c258-9192-402d-a074-e1ac17cf265c.png-w331s)
图5-1 部分域名、IP、样本的对应关系图

根据样本同源性分析的结果，我们发现大量的有效载荷被分别挂载在不同的动态域名中，以备包含漏洞的Office文档或恶意软件Guloader访问和下载。通过域名的查询记录所得，此次攻击活动最早可追溯到1月中下旬，同时也可以看到，它们最初均使用指向尼日利亚的基础设施。值得注意的是，这些域名解析使用的IP总不定期在常用的IP地址段来回切换。具体如图5-2所示。

![
](https://images.seebug.org/content/images/2020/07/06851d4d-892d-4b14-bb5a-e35c93d379eb.png-w331s)
图5-2 动态域名解析的IP地址

我们将C&C对应的IP地址所属国家和地区进行统计，并绘制其地理位置分布图（如图5-3所示）。整体来看，美国和法国占比率最高，其次为荷兰。

![
](https://images.seebug.org/content/images/2020/07/48058636-2e9f-4e3b-a829-ac238c184880.png-w331s)
图5-3 C&C对应的IP地理位置分布图

#### 5.2 关联性分析

启明星辰ADLab将本次捕获到的样本同以往SWEED活动做了全面的关联分析，得出以下几处重要的关联点：

（1）漏洞文档

在此次行动中攻击组织使用的漏洞文档有两类（CVE-2017-11882和CVE-2014-6357），其中以CVE-2017-11882漏洞利用文档为主要攻击载荷。而SWEED组织也曾在以往的攻击行动中频繁的使用过该漏洞文档。具体如图5-4所示。

![
](https://images.seebug.org/content/images/2020/07/85f01c32-1913-4415-b968-c201473ceaa3.png-w331s)
图5-4 漏洞文档案例

（2）攻击目标

根据公开报告可以得知，SWEED黑客组织的攻击目标主要针对全球从事对外贸易的中小型企业，并且所涉及的行业主要以制造业、航运、物流和运输为主。这与我们此次监测到的攻击行动中受害者的地理位置和行业分布具有较高的相似性。图5-5列举了几例在本次攻击活动中攻击者发送给目标用户的钓鱼邮件。

![
](https://images.seebug.org/content/images/2020/07/eaffe41f-35ef-460a-9d90-3304f4b5e74c.png-w331s)
图5-5 钓鱼邮件案例

（3）攻击武器

在目前观测到的行动中，攻击者最终投放的恶意软件包括Agent
Tesla、Remcos、NanoCore、Formbook和Lokibot。我们将捕获的所有恶意软件按家族分类和统计，根据结果显示，Agent
Tesla的占比率处于最高，是攻击者重点使用的攻击武器。而这种使用特征也曾反复出现在SWEED组织以前的攻击活动中。

![ ](https://images.seebug.org/content/images/2020/07/e73cb5fb-48ba-49c7-a2db-ee0966e2d76f.png-w331s) 图5-6 恶意软件家族占比率

（4）IP地址位置

我们通过Whois信息查询，发现在此次行动中的域名“mogs20.xxx.org”早期解析的IP（105.112.XXX.XXX）地理位置指向尼日利亚，该网段归属尼日利亚地区电信的105.112段。这与SWEED组织所属国家具有高度的一致性。

![ ](https://images.seebug.org/content/images/2020/07/95227e36-baea-4910-a3dc-cb0ee2fb98d7.png-w331s) 图5-7 Whois查询信息内容

结合SWEED组织一系列的攻击活动特点以及上面总结的四点可以看出，攻击者在攻击动机（窃取用户信息以牟利）、攻击目标（针对全球对外贸易的中小企业）、作业风格（投递定制型钓鱼邮件分发木马）、战术（规避检测、常驻、命令与控制）、技术（漏洞利用）、过程（发送携带恶意附件的邮件->漏洞文档->解密运行Agent
Tesla远控木马）以及其使用的网络基础设施等方面都十分符合SWEED组织的特征。由此我们推断，此次攻击活动幕后者很可能是来自尼日利亚的SWEED黑客组织。

### 六 总结

迄今为止SWEED黑客组织至少已活跃了4年的时间，从该组织近期的攻击可以发现，SWEED开始使用更具有针对性的邮件内容和更具迷惑性的文档标题，从而提高受害者中招的概率。启明星辰ADLab将该组织此次行动TTP的研究分析结果与以往跟进或披露的相关攻击行动特性做比对后，得到的相关证据都可表明这些样本来自SWEED黑客组织。

SWEED组织使用Guloader下载器传播的远程木马种类虽然多样化，但主要还是以其偏好的Agent
Tesla为主。从其所使用的TTP来看，该黑客组织目前并未具备很好的自研开发能力。在多数情况下，仅会从国外一些主流黑客网站上购买木马生成器和加密工具来作为攻击武器，例如曾使用的KazyCypter和此次使用的Guloader。不过，即便攻击者在技术能力上相对较弱，但其在社工技巧和多样化攻击方式的应用面上还是较为熟练的。在此，建议用户尽量避免打开不明来历的邮件以及附件文件（来自未知发送者的），及时安装系统补丁，提高风险意识，防范此类恶意软件攻击。

### 七 IOC

    
    
    MD5
    F97CFA6C3F1338B597768808FC1B2F00
    B1941921571C2B6ED0C3BDA77E402001    
    DD82B2E488811E64BB9C039C441DB19C
    EC4CF91427DAC3AD29CD2A52B0789DC6
    166FD7B0C74C60DCBC80BF335D712EA2
    BCBCC89F237B22F21BDAE9E6555404A
    60147B91AB7B64B9BE27BD3422147E60
    48408BBE8D9EE22D6BBB6820FCCC305F
    7DDA46F2D9008FAE016AFFF39E9C5801
    A22A37E699C20D42753D35A94A75B365
    C36C41EB6A34880459154334681C203A
    6BC92ACB050A2068EFF4842A1D360938
    FB7ED44C2BAAA6F011F7BF51DE721BC4
    58604AE63AEA84483C67980369958ACB
    312BFAFE6746645E72FCB84ECBFB023C
    779EB99965F1AAC12363632468DF7DCE
    DD49030C00EF3C2341BCBE4489DCEF63
    IP
    167.114.85.125
    URL
    https://drive.google.com:80/uc?export=download&id=1lmmu6kv5ep_wkm7hfyhdshru-y1n2pqv
    https://onedrive.live.com/download?cid=554BBD19BDD72613&resid=554BBD19BDD72613!156&authkey=AGIuaWEkkBxB_4o
    https://drive.google.com/uc?export=download&id=1W3ddZnmArVGhsecoWW5KcQAKPZ9OacLU
    https://share.dmca.gripe/iQakn267f3ZvpDN.bin
    http://167.114.85.125/go/Origin%20server%20ilyas_tTzYDNEGay108.bin

### 八 参考链接：

[1] <https://www.fortinet.com/blog/threat-research/new-agent-tesla-variant-spreading-by-phishing>  
[2] <https://www.fireeye.com/blog/threat-research/2017/10/formbook-malware-distribution-campaigns.html>  
[3] <https://www.fortinet.com/blog/threat-research/new-infostealer-attack-uses-lokibot>  
[4] <https://success.trendmicro.com/solution/1122912-nanocore-malware-information>  
[5] <https://www.fortinet.com/blog/threat-research/remcos-a-new-rat-in-the-wild-2>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1265/>

