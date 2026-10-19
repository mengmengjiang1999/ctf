## **01** **概述：覆盖智能终端的A** **2** **PT** **样本拼图**

在过去二十多年的时间里，全球关键信息基础设施运营者、安全厂商、研究者所面临的重大考验是，如何应对以NSA等情报机构所发动的网络攻击活动，基于这种攻击活动应用了难以想象的技术与资源，安天CERT将这种攻击活动称之为A2PT（高级的高级持续性威胁）攻击，并发现其中多起攻击都来自于NSA下属的方程式组织。如何把A2PT攻击活动中的攻击样本与过程揭示出来，成为了一场比马拉松更艰苦的分析接力赛，这场接力至少已经完成了三次交接棒，第一阶段从2010年的“震网”事件触发，围绕“震网”-“火焰”-“毒曲”-“高斯”系列样本的攻击活动、样本同源性与关联展开，直到2013年的斯诺登事件出现，才发现这些只是冰山一角；第二阶段是从方程式组织（隶属于NSA）被曝光开始，围绕其硬盘固件攻击能力、载荷、通信加密机制特点、“原子化”作业模式等展开，并逐渐证明“震网”等攻击与方程式组织密切相关；第三阶段则是围绕“影子经纪人”所泄露的方程式组织的漏洞和攻击载荷，全球业界展开更深入的拼接分析和复盘。中国网络安全产业联盟在4月11日所发布的报告《美国情报机构网络攻击的历史回顾——基于全球网络安全界披露信息分析》[1]基本完整复现了这场漫长而艰难的斗争。

这场分析接力中两项比较重要的工作：一项是揭示从“震网”到方程式的复杂线索关联，这些信息可以参见卡巴斯基和安天相关的恶意代码家族的同源性分析报告[2][3]，也可以在[《震网事件的九年再复盘与思考》](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650173867&idx=1&sn=6b12446b10650f6c00784a63d3c486fb&chksm=beb9d29989ce5b8facbbad4c31886e98184461da5ced81e802a4f1c5e7c90f36c45d8e594de6&scene=21#wechat_redirect)[4]看到相关的恶意代码工程的关联图谱。另一项则是去验证一个逻辑上存在着必然性，但又需要大量工作来佐证的判断——即方程式组织的作业能力和恶意代码样本储备是覆盖全操作系统平台的。毫无疑问，国际安全厂商卡巴斯基为此做出了最大的贡献，安天CERT也有部分独创的工作，例如Linux、Solaris样本的最早曝光是来自安天的报告。安天CERT在2016年的报告[《从方程式到“方程组”——EQUATION攻击组织高级恶意代码的全平台能力解析》](https://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650170101&idx=1&sn=714546c757db8291d52b6a4332c364a4&chksm=beb9c1c789ce48d1d6a96ed51b2506feab47c344b50461e7a4f72b19d89879dc113669d47a33&scene=21&token=1730485739&lang=zh_CN#wechat_redirect)[5]中，汇聚了安天和卡巴斯基等的成果，统计了Windows、Linux、Solaris、FreeBSD和Mac
OS平台的样本情况。但彼时方程式组织针对iOS 、Android等移动平台的样本还没有正式浮出水面，尽管在2013年斯诺登事件中所曝光的NSA
ANT系列攻击装备中DROPOUTJEEP、TOTEGHOSTLY等代号给出了一些线索，但由于iOS平台取证的难度，和其攻击作业的高度定向性，业内一直没有样本级别的发现和实证——但这并不意味着，它们会永远沉寂于水面之下，持续的努力让我们能够在后续找到线索并进行了分析积累。

2023年6月1日，卡巴斯基[6]发布了《三角行动：iOS设备被以前未知的恶意软件攻击》，这让我们决定对我们原有分析成果进行补充分析，并正式发布。由于卡巴斯基尚未公开有关事件样本信息和分析结果，我们尚无法判定我们分析的这些历史样本是否是“三角行动”攻击样本的早期版本。但我们明确的判断是：我们所分析的样本，和卡巴斯基所曝光的攻击同样来自方程式组织。但与卡巴斯基所发现的样本是依托iMessage的漏洞投放不同的是，本报告的相关攻击样本来自方程式组织基于“量子”（QUANTUM）系统在网络侧针对上网终端浏览器漏洞利用投放。

##  **02** **样本分析**

相关样本并不是常规的iOS APP应用安装包，而是针对iOS底层的木马，木马分为执行载荷与后门程序，执行载荷是最初投放到系统的，它负责释放后门程序和持久化。

###  **2.1** **执行载荷**

表 2‑1 木马主体程序

![1686323263_6483403fdace15da4ec1d.jpg!small](https://image.3001.net/images/20230609/1686323263_6483403fdace15da4ec1d.jpg!small)

木马主体程序在投递过程中伪装的文件名是regquerystr.exe，但并非是一个PE格式文件，实际文件格式是ARM架构的Mach-O
可执行程序，利用漏洞或通过沙盒逃逸完成后门程序的释放和执行，其首先检测内核版本和用户权限。

![1686323300_64834064aff88e84eddb2.jpg!small](https://image.3001.net/images/20230609/1686323300_64834064aff88e84eddb2.jpg!small)

图 2‑1 对内核版本信息和当前的用户权限进行获取和判断

然后木马程序进行后门程序的释放，将其释放到/tmp/mvld，并执行/bin/launchctl的load命令完成后门服务的运行。

![1686323313_6483407193a6154159703.jpg!small](https://image.3001.net/images/20230609/1686323313_6483407193a6154159703.jpg!small)

图 2‑2 运行后门服务

![1686323325_6483407da21af203f734f.jpg!small](https://image.3001.net/images/20230609/1686323325_6483407da21af203f734f.jpg!small)

图 2‑3 正在运行的后门服务

木马主体采用了两种不同的加密算法来加密其明文字符串信息。

算法1：

![1686323349_648340956e4eb359f9e2f.jpg!small](https://image.3001.net/images/20230609/1686323349_648340956e4eb359f9e2f.jpg!small)

图 2‑4 字符串加密算法1

算法2：

![1686323371_648340ab7b00e2793ba42.jpg!small](https://image.3001.net/images/20230609/1686323371_648340ab7b00e2793ba42.jpg!small)

图 2‑5 字符串加密算法2

其使用的加密方法比较简单，配置数据只运用了异或和乘法运算，其使用的密钥有0x47[7]和0x1D，网络通讯部分则使用了标准的HTTPS加密协议。这种简单的加密与方程式组织在PC平台样本严格使用高强度加密算法并不一致，关于PC样本加密算法和密钥可以参见安天分析报告[《方程式（EQUATION）部分组件中的加密技巧分析》](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=206299704&idx=1&sn=64c8e787cf5199ce8613002e0300f3e6&chksm=2f04410a1873c81c9874355da75b8d05346a42e57c0899983a8c0911cb5bb1e43430d1bc7808&scene=21#wechat_redirect)[8]，但相对来看，可能是彼时的手机环境算力相对较低，同时没有较为成熟的安全对抗机制，因此攻击者并未使用强加密。

![1686323385_648340b9d457ff48d4de5.jpg!small](https://image.3001.net/images/20230609/1686323385_648340b9d457ff48d4de5.jpg!small)

图 2‑6 解密后的关键字符串信息

表 2‑2 Regquerystr木马解密出的配置信息

![1686323475_64834113f2d3ca544a90f.jpg!small](https://image.3001.net/images/20230609/1686323475_64834113f2d3ca544a90f.jpg!small)
**2.2** **后门程序**

在投放载荷执行后，会释放一个后门程序mvld。该木马是Regquerystr释放的子程序，主要用于收集设备信息，以及与远程服务器通信，程序运行后会生成日志文件/private/var/tmp/.swapfile.tmp，并删除自身文件(/tmp/mvld)，经分析，可将该木马合并入方程式组织的DoubleFantasy[9]攻击木马武器谱系。

表2‑2 后门程序信息

![1686323519_6483413f14e7ae519649a.jpg!small](https://image.3001.net/images/20230609/1686323519_6483413f14e7ae519649a.jpg!small)  
mvld后门程序路径如下：

![1686323539_64834153e938998c9627a.jpg!small](https://image.3001.net/images/20230609/1686323539_64834153e938998c9627a.jpg!small)

图 2‑7 后门程序路径

mvld后门程序会访问远程控制服务器发送http请求，当C2域名无法访问时直接访问硬编码IP： 图 2‑8 向远程服务器发送请求  
![1686323557_648341653bd6c8e208b2c.jpg!small](https://image.3001.net/images/20230609/1686323557_648341653bd6c8e208b2c.jpg!small)

mvld后门程序配置了代理设置，采用neno客户端http协议。

![1686323568_648341702acf93ac5bcdb.jpg!small](https://image.3001.net/images/20230609/1686323568_648341702acf93ac5bcdb.jpg!small)

图 2‑9 代理设置

mvld后门程序通过getuid、getpwuid获取设备帐号的用户名、密码、用户组等信息。

![1686323579_6483417b0ad143cbfb336.jpg!small](https://image.3001.net/images/20230609/1686323579_6483417b0ad143cbfb336.jpg!small)

图 2‑10 获取设备信息

mvld后门程序同时也会读取/etc/passwd文件，获取登录用户信息。

![1686323589_648341855339684f452c7.jpg!small](https://image.3001.net/images/20230609/1686323589_648341855339684f452c7.jpg!small)

图 2‑11 获取登录用户信息

修改环境变量DYLD_INSERT_LIBRARIES：

![1686323600_648341909ace7dd69a166.jpg!small](https://image.3001.net/images/20230609/1686323600_648341909ace7dd69a166.jpg!small)

图 2‑12 修改环境变量DYLD_INSERT_LIBRARIES内容

该样本有13个指令代码，功能与安天历史曝光过的方程式Windows和Solaris木马DoubleFantasy系列指令十分相似。

![1686323619_648341a373a524d8cc1f1.jpg!small](https://image.3001.net/images/20230609/1686323619_648341a373a524d8cc1f1.jpg!small)

图 2‑13 指令代码

样本各个指令功能简要描述如下：

表2‑3 指令代码及对应功能

![1686323658_648341ca8e324601b41af.jpg!small](https://image.3001.net/images/20230609/1686323658_648341ca8e324601b41af.jpg!small)样本获取配置环境等信息后进行回传：

图 2‑14 获取环境和配置信息回传

获取信息格式说明：

表 2‑4 获取环境和配置信息格式说明

![1686323706_648341fac6c7c16a2ffd9.jpg!small](https://image.3001.net/images/20230609/1686323706_648341fac6c7c16a2ffd9.jpg!small)

mvld木马内部解密出信息FAID，其中ace02468bdf13579[10]与之前曝光的NSA作业所需强制性的唯一标识代码一致，该标识也存在于“影子经纪人”泄露的方程式武器库中SecondDate武器中，种种信息都指向：该木马来自美方情报机构NSA下属的方程式组织。表
2‑5 mvld解密出的配置信息

![1686323737_64834219953cc1cfb6024.jpg!small](https://image.3001.net/images/20230609/1686323737_64834219953cc1cfb6024.jpg!small)

##  **03** **同源分析**

我们将该iOS木马与方程式组织的DoubleFantasy木马装备序列进行对比分析，可以得出如下结果：在功能、行为、算法、信息收集和指令控制集合上几乎相同；木马使用方程式组织加密算法中最常使用的数值0x47[7]、收集终端信息格式与DoubleFantasy一致，控制指令代码结构与DoubleFantasy基本一致。

###  **3.1** **配置数据解密算法、密钥对比**

本报告样本与其他方程式组织样本在加密算法、密钥上完全一致：

![1686323755_6483422bb599ef8df5f88.jpg!small](https://image.3001.net/images/20230609/1686323755_6483422bb599ef8df5f88.jpg!small)

图 3‑1 历史其他平台方程式样本（左）解密算法与iOS样本（右）解密算法

###  **3.2** **信息收集格式对比**

对比发现本报告样本与其他方程式样本在信息收集的数据格式基本一致：

![1686323776_648342403f11987f6d351.jpg!small](https://image.3001.net/images/20230609/1686323776_648342403f11987f6d351.jpg!small)

图 3‑2 历史其他平台方程式样本（左）信息收集与iOS样本（右）信息收集对比

###  **3.3** **控制指令代码对比**

本报告样本与其他方程式样本在控制指令格式上基本一致：

![1686323801_64834259c54bca0277f67.jpg!small](https://image.3001.net/images/20230609/1686323801_64834259c54bca0277f67.jpg!small)

图 3‑3 历史其他平台方程式样本（左）指令代码与iOS样本（右）指令代码对比

##  **04** **攻击投放分析**

通常认为iOS平台的安全强度比Android平台更高。但iOS平台本身依然有很多可攻击入口。针对iOS平台曾出现过的攻击方式包括，基于App
Store投毒、基于iMessage和FaceTime的漏洞、基于Wi-Fi在流量侧的攻击等。卡巴斯基所发布的报告，声明其所捕获的攻击入口为iMessage服务。iMessage漏洞确实是一个常用的攻击入口，加之其本身带有电信码号的指向性，适合发起指向明确目标的攻击。但同时我们也要指出的是，关闭iMessage和Facetime等服务，依然不能有效对抗方程式组织的攻击，这是因为：
**方程式组织所拥有专属的“上帝视角”攻击模式，** 是依托入侵和劫持各国运营商网络设备、和其他的信道介入能力构建流量劫持体系，在拟攻击目标人员上网过程中，
**基于“量子”（QUANTUM）系统** 插入攻击流量，利用浏览器等上网软件的漏洞，实现将恶意代码投放到设备当中运行。

“量子”（QUANTUM）系统项目于2013年首次被斯诺登曝光，由美国国家安全局（NSA）发起，并与英国政府通信总部（GCHQ）和瑞典国防无线局（FRA）联合执行，用于开发和运营承载实施网络攻击的工程体系和入侵工具集，以实现对网络空间中网络状态的干预和控制，由NSA下属的特别行动入侵行动办公室（TAO）开发并负责使用。而我们所说的方程式组织则是网络安全产业界基于分析工作中发现的装备特点对TAO所赋予的“别名”。“量子”（QUANTUM）系统的运行支点，是对网络通讯基础设施的关键路由和网关等设备的入侵和劫持，从而具备获取分析和劫持攻击目标上网过程的能力。其首先基于上网设备的相关IP、码号、链路、身份账号或其他标识依托X-KeyScore系统进行识别，看是是否复合攻击目标定义，以及是否是已经攻击成功设备，如果是尚未实施攻击过攻击的待攻击目标，则进一步判断是否存在可用漏洞，然后选用相应的工具执行秘密入侵。我们以假定目标登录雅虎账户为例，攻击过程如下：1、目标登录Yahoo邮箱或网站；2、特殊行动源（SSO:
Special Source
Operations）站点发现“量子”（QUANTUM）系统指定的雅虎分拣器筛选的数据包，会将其重定向到FOXACID服务器；3、该服务器将FOXACID
URL注入到选定的数据包并将其发回至目标计算机；4、雅虎服务器接收到请求邮件内容的数据包；5、FOXACID数据包先于雅虎数据包回到终端；6、目标机器加载雅虎页面，但在后台同时加载FOXACID
URL，将目标重定向到FOXACID刺探服务器；7、如果目标浏览器可用，且PSP（Personnel Security
Program）未能检测，则FOXACID将第一阶段植入程序部署到目标；8、“验证器”后门（美方称之为Validator，安全厂商命名为DoubleFantasy的木马）成功安装。

![1686323811_64834263c7509faa2f7bc.jpg!small](https://image.3001.net/images/20230609/1686323811_64834263c7509faa2f7bc.jpg!small)

图4‑1 NSA“量子”（QUANTUM）系统攻击原理

在针对iOS平台的攻击中，“量子”系统通过多个Safari浏览器的远程代码执行漏洞组合利用投放攻击样本。其中最早的攻击行为在2013年或更早的时间就出现。其早期运用的漏洞可能包括CVE-2014-1349、CVE-2014-4466等，漏洞利用代码则由“狐酸”FOXACID漏洞平台生成，“量子”系统所构造的流量可以实现先于正常网站返回流量抵达目标终端，触发漏洞执行该木马程序。在利用本报告样本的攻击过程中，攻击载荷在量子系统在插入的网络流量中伪装成GIF头部，命名为regquerystr.exe。

需要高度警惕的是，“量子”系统的攻击是上帝视角的，具体表现为：

  1. 其攻击流量是由被入侵或控制的网络路由设备发出，其甚至可能先于被访问的网站感知到被攻击方的网络访问。
  2. 其攻击对象是访问网站和网络资源的浏览器，或其他互联网客户端，因此其更难防御，也无法用传统收敛开放端口和暴露面的思路来防范。
  3. 其插入的攻击流量并不是和真实网站交互过程，且是加密的，因此即使数据包遭到了还原和留存，发现了其构造的域名，也不具备传统IP/域名意义的溯源价值。
  4. 在攻击得手后，其相关角色和设备被标定为攻击有效，后续不会再进行投放的动作，而攻击失手后，则可能不再继续攻击，或未来不会采用同一漏洞进行攻击。因此极难复现和验证。
  5. “量子”的能力并不仅可以部署于骨干网被A2PT组织渗透或控制的网络设备之中，也可以在入侵作业中，植入到政企机构网关和边界设备上，包括相关漏洞利用工具可以部署到类似企业WEBMail 服务器中，使之有别于一般的持久化，而采取反复打入+内存木马的方式，更好地对抗一般性的威胁猎杀。

“量子”的作业能力一方面来自于方程式组织对全球关键网络通讯设备的攻击控制程度，另一方面则来自其掌控的大量未公开漏洞资源和漏洞利用工具储备。

##  **05A** **2** **PT** **组织的漏洞储备、来源及资源运营和作业分析**

###  **5.1** **整体漏洞运营机制**

无论是攻击中东SWIFT对信息基础设施长驱直入[11]，还是“量子”之手实现上帝视角的攻击，方程式等A2PT作业组织都依赖极为丰富的漏洞储备[12][13]。

美方对零日漏洞（0day）的管理和储备有一套自身的管理机制。2017年美国白宫发布《漏洞公平裁决政策和程序》[14]，为漏洞公平裁决程序(Vulnerabilities
Equities
Process，VEP)制定了更多的规则和透明度要求，包括目的、背景、范围、参与主体、裁决过程和相关附件等内容，这个政策的主导机构就是NSA。VEP是美国政府在处理安全漏洞问题时所引入的一项裁决机制，当发现漏洞时，是选择将发现的漏洞向有关科技公司披露，告知其产品或服务中存在的网络安全漏洞以便开发者及时进行修复，还是选择将漏洞信息进行保留，以便今后用于网络入侵、情报搜集、军事活动或执法活动等目的。

为了实现对高价值零日漏洞（0day）的垄断利用，NSA还开发了一套NOBUS运营体系，NOBUS是Nobody But
Us的递归缩写，即“没有人可以（使用这些漏洞）除了我们”——这是NSA用来描述其认为只有其自身才能拥有和利用的安全漏洞的术语。他们在该系统中评估对手能够利用系统中已知漏洞的可能性，如果他们确定该漏洞只能由NSA出于计算资源、预算或技能组合等原因利用，就会将其标记为NOBUS，并且不会推动修补漏洞，而是让该漏洞继续存在以便针对当前或未来的目标进行利用[15]。NSA曾对外表示，它披露了发现的91%的漏洞，这就意味着剩下的9%的漏洞被NSA“私藏”了。而被NSA“私藏”的储备漏洞，才是让网络世界变得更加脆弱的独家命门。

当然更为严重的问题是，美方情报机构操纵预置漏洞和削弱产品安全性的行为，其中最为典型的是对加密算法标准的污染，如NIST 2006年正式发布的特别出版物SP
800-90（2012年后改称为SP
800-90A）《使用确定性随机位发生器的随机数产生算法推荐》中，推荐的4种“确定性随机位发生器”（DRBG）算法之一双椭圆曲线算法Dual_EC_DRBG其实存在后门[16]。以及瑞士Crypto
AG公司出品的加密机被美方控制，削弱其销往超过120个国家的通讯加密设备的密码强度，通过拦截并解码加密程序以窃取各国政府及企业用户的加密通讯内容[17]。

###  **5.2** **两类重点漏洞储备**

安天CERT认为方程式组织至少重点进行了两类漏洞和利用工具库的建设：一类是用于攻击开放端口和服务的，我们称之为漏洞集合（S），即Service，服务端；一类是用于攻击浏览器和互联网客户端的，我们暂称之为漏洞集合（C），即Client，客户端。这两个集合都用于实现对端点目标的突防，后续还可以与相关的提权、持久化等工具配合使用。但两个集合的运用方式有所差异。集合（S）被用于依托跳板，基于主动向特定端口或服务发送数据包的方式，攻击互联网开放目标，实现打入，或者在取得桥头堡后在网络纵深目标体系中横向移动。集合（S）中的漏洞储备相当丰富，以至于仅震网攻击中，就使用了超过5个0day，在方程式组织攻击中东最大SWIFT机构EastNets中，所使用的多个漏洞也属于此类。在2017年4月14日的Shadow
Brokers（影子经纪人）事件中，这个漏洞集合被彻底曝光。其中包括：Eternalblue（永恒之蓝）、Easybee（易之蜂针）、Easypi（易之远控）、Eclipsedwing（日食之翼）、Educatedscholar（文雅学者）、Emeraldthread（翡翠纤维）、Emphasismine（地域之雷）、Englishmansdentist（恐怖牙医）、Erraticgopher（古怪地鼠）、Eskimoroll
（爱斯基摩卷）、Esteemaudit（尊重审查）、Eternalromance（永恒浪漫）、Eternalsynergy（永恒协作）、Ewokfrenzy（星际流氓）、Explodingcan（爆炸之罐）、Zippybeer（夺命之酒）。
值得一提的是，相关漏洞和利用工具的泄露及其后被黑产集团所利用，最终导致了2017年5月12日的全球大规模的
[“WannaCry”（中文名称魔窟）](https://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650170534&idx=1&sn=dedc3ff25c3594b49bc4e6c53c9fd123&scene=21#wechat_redirect)勒索软件感染事件，给全球网络用户带来的空前的灾难影响。相关攻击者仅使用“永恒之蓝”（Eternalblue）一个漏洞就对全球网络安全造成了如此巨大的危害[18]。我们在[《安天关于系统化应对NSA网络军火装备的操作手册》](https://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650170743&idx=1&sn=4911fab3c2e2f0e97a4666e2d5e8da11&scene=21#wechat_redirect)[19]报告中对这批漏洞和所攻击的服务进行了图谱化梳理（图5-1）。可以肯定的是，在这次泄露事件后，相关组织会放弃这批效力大打折扣、且可能暴露行踪的漏洞利用，启用储备漏洞利用并加快漏洞挖掘采集储备的节奏。

![1686323854_6483428e87ff3688b63dc.jpg!small](https://image.3001.net/images/20230609/1686323854_6483428e87ff3688b63dc.jpg!small)

图 5‑1 NSA 攻击开放端口和服务的漏洞图谱

但长期以来，对于漏洞库（C），却一直了解甚少。基于“量子”系统的运行机理，其必然存在的一个重点针对IE、Edge、Chrome、Firefox等浏览器（含主要插件）的0day漏洞集合。我们有理由相信，由于漏洞库（S）的工具，更多要在手工作业中使用，导致其可以被更多人员接触到，也间接导致类似被“影子经纪人”泄露事件的发生。但由于漏洞库（C）更多的是配置到“量子”系统使用，因此其相对管控更为严格。这就使相关漏洞一直没有完整的浮出水面。但从另外一个层面，我们在对ANT工具集合和Vault7的分析中可以得出如下结论，A2PT组织的作业风格是，恶意代码覆盖全体系结构和操作系统平台、漏洞储备覆盖全系统和主流应用场景、中继运载工具覆盖全接口。基于漏洞库（C）配套量子系统的使用特点，我们完全可以有效猜测漏洞库（C）的覆盖能力。我们选取了一个非常具备场景清单价值的参照系。在NSA有间接参与和关联的相关活动中，类似Pwn2Own这样的安全大赛所提出的场景目标，高度匹配“量子”系统的需求。从2007-2013年的Pwn2Own的著名黑客成功攻击案例中，我们可以看到，对主流浏览器实现全覆盖是Pwn2Own的重点。这些场景较好地覆盖了“量子”所需要的漏洞需求频谱。因此我们就需要进一步细化分析A2PT组织的供给能力体系和资源运营。

![1686323914_648342ca7536ba0670a73.jpg!small](https://image.3001.net/images/20230609/1686323914_648342ca7536ba0670a73.jpg!small)

图 5‑2 2007-2013年的PWN2OWN的部分破解成功攻击案例[20]

我们可以PWN2OWN的破解场景作为一个参照系，来绘制“量子”系统的攻击能力频谱图，这个频谱完全覆盖全球所有主要终端和智能手机终端设备和浏览器。

![1686323922_648342d2be0a64e9ae118.jpg!small](https://image.3001.net/images/20230609/1686323922_648342d2be0a64e9ae118.jpg!small)

图 5‑3 量子系统可攻击场景图谱化分析

由于没有参照系作为分析支撑，我们在“量子”可攻击场景图谱上并未标注中国的基础信息产品和手机环境。但从我们历史分析成果中所呈现的相关攻击组织追求攻击能力覆盖全场景的一贯“调性”，其必然针对中国的基础信息产品和智能手机等环境持续进行全面的漏洞挖掘研究，进行攻击能力储备积累，随时准备运用。前火眼公司首席战略官Richard
Bejtlich的观点是[21]，修复漏洞提升安全性，还是藏匿漏洞用于网络入侵，对美国政府来说是一个“纠结”，“当外国目标运行其自己本土的软件时，这种纠结就不存在了”。可以想象，方程式等A2PT攻击组织既拥有深入了解美国出品软硬件产品脆弱性的非对称优势；同时在挖掘、分析、利用其他国家的信息产品与服务的脆弱性方面，也会更有恃无恐。

所以我们需要进一步梳理分析其攻击资源的来源。

###  **5.3 A** **2** **PT** **的0day漏洞和恶意代码工具的来源**

安天CERT尝试根据公开信息梳理方程式等A2PT攻击组织在除自身挖掘发现和预置外，可能用于直接和间接获取漏洞的资源来源。

 **5.3.1** **基于基础IT厂商安全生态获取漏洞**

信息化产品与服务的漏洞的发现、上报、修复和披露机制，是整个信息社会安全运营的重要基础环节，相关信息共享和联动响应机制也是全球产业链分工的基本信任基础。在全球化的历史演进中，相应的国际协同机制也已经形成。全球安全研究者对IT产品和开源代码进行分析研究，将这些漏洞上报给厂商和漏洞共享平台，以推动产品改进，大型IT厂商，自身也组建规模庞大的安全队伍，持续改善自身的安全性。当然这也就意味着，基础信息化软硬件产品、大规模互联网服务产品在这个机制中起到更举足轻重的作用。一旦这个机制被拥有IT产品垄断和支配力的霸权国家所把持，使相关机制单边化，就必然导致一种空前的不平衡和不平等。也更加重了全球用户对部分严重漏洞源自研发的失误还是合作预置的怀疑：2013
年 12月，原“洋葱路由器”( Tor) 项目核心程序员雅各·阿贝尔鲍姆( Jacob Appelbaum)在第 30 届通信大会上展示了一组泄露的 PPT
文档，其中包含 NSA
针对各种网络产品的可利用漏洞开发的程序与木马。产品覆盖服务器、路由器、防火墙和手机设备，囊括了DELL、HP、Sun、CISCO等知名品牌[22]。阿贝尔鲍姆表示，他怀疑NSA与其中一些企业存在合作关系，披露这此内容的初衷是“让相关企业在曝光的压力下，自己澄清是
NSA的同谋还是受害者。”2016年，美国哥伦比亚大学国际与公共事务学院的高级研究人员杰森·希利 ( Jason Healey)
在《国际事务杂志》发表“美国政府与零日漏洞”一文，深入分析了美国漏洞公平裁决程序(VEP)自2008到2016年的发展历程，并对当前（2016年）美国可能囤积的零日漏洞军火数量进行了谨慎的估算[23]。基于VEP的裁决机制，我们很难判断多少漏洞被打上了NOBUS的标签，成为A2PT用来攻击对手的网络军火。一些已经被公开披露的严重漏洞，从漏洞早期发现时点到修补和公开时点之间存在较长时间差。例如Google公司的Project
Zero等安全团队在2017年6月发现Intel
CPU的重大漏洞：Meltdown（熔毁，CVE-2017-5754）和Spectre漏洞（幽灵，CVE-2017-5715和CVE-2017-5753），这些漏洞对全球云基础设施带来重大威胁，但直到六个月后的2018年1月这些漏洞[24]才被公告。网络安全研究者有理由猜测，这六个月成为A2PT攻击全球云基础设施的独家作业窗口期。

 **5.3.2** **通过参与各类公开活动搜集漏洞信息**

RSA信息安全大会是全球网络安全领域一年一度的盛会，每年上半年在旧金山举行，来自世界各地的安全厂商代表和业界精英在大会期间聚集一堂，就全球面临的网络安全威胁和技术发展趋势进行广泛的沟通与交流。美国相关情报机构NSA、FBI等都例行“参展”，主要发展专业人员加入他们的队伍。包括发表演讲，号召“黑客”为美国服务。黑帽安全技术大会（Black
Hat
Conference）、DEFCON极客大会等黑客大会，也是美情报机构重点关注和参与的会议。Pwn2Own是全球最著名的黑客大赛之一，由美国五角大楼网络安全服务商、惠普旗下TippingPoint的ZDI（Zero
Day
Initiative）为主办项目组，谷歌、微软、苹果、Adobe等互联网和软件巨头都为比赛提供支持，通过黑客攻击挑战来完善自身产品。这种大会显然也是美情报机构搜集、储备漏洞和攻击技术的良机。目前并无线索来表明Pwn2Own活动与美方掌握的独家漏洞具有直接关联，但正如我们前文指出的，
从Pwn2Own所长期专注的科目来看，这个题目的场景设计基本完整映射了“量子”系统进行流量侧攻击作业的能力需求和价值偏好。而ZDI作为惠普旗下付费收购0day漏洞的平台，主要以明码标价、现金奖励的形式征集漏洞，全世界的黑客都可以把漏洞卖给ZDI。而ZDI作为美情报机构的代理人，则可能将征集到的高价值漏洞转卖给美情报机构。

 **5.3.3** **通过漏洞悬赏计划获取漏洞信息**

2016年起，美国防部就启动了“黑掉五角大楼”（Hack the
Pentagon）漏洞悬赏计划的试点。2023年1月13日，美国防部宣布将发起“黑掉五角大楼3.0”计划，旨在发现维持五角大楼和相关场地运行操作技术中的漏洞[25]。这些活动获取漏洞的真实用途值得怀疑。2019年1月，美国总统特朗普签署了一项法案，要求国土安全部在六个月内制定一个测试漏洞的赏金计划。除了政府部门自身的漏洞悬赏计划以外，美国本土还有一些知名的漏洞悬赏公司为美军方和情报机构提供服务，这些公司包括HackerOne、BugCrowd和Synack等。

 **5.3.4** **研发和采购商业恶意代码+漏洞利用工具**

基于安天CERT在[《震网事件的九年再复盘与思考》](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650173867&idx=1&sn=6b12446b10650f6c00784a63d3c486fb&chksm=beb9d29989ce5b8facbbad4c31886e98184461da5ced81e802a4f1c5e7c90f36c45d8e594de6&scene=21#wechat_redirect)中对方程式组织的恶意代码工程体系的关系梳理，可以看到其相当长的时间是基于超大规模恶意代码工程进行“滚动迭代”和积木式更新，安天CERT相对倾向认为NSA在核心行动中恶意代码体系是长期自研，或者由关系极为密切的承包商来长期承载。

美情报机构购买商用网络军火的历史已经被曝光。2021年7月19日，英国广播公司（BBC）报道，以色列软件监控公司NSO向一些国家售卖了一款名为“飞马”的手机间谍软件，用以监控各类重点人员甚至他国的相关政要。“飞马”软件可以轻而易举地入侵苹果和安卓系统，并轻松截取手机里的各类信息、图片、视频、电邮内容、通话记录，甚至可以秘密开启麦克风进行实时录音[26]。2022年，《纽约时报》的一项调查就揭露FBI曾购买过“飞马”软件，此后FBI局长克里斯托弗·雷也承认FBI确实购买了“飞马”软件[27]。据《纽约时报》2022年7月份报道，在获得美国情报部门默许下，美国军事承包商
L3 Harris的高管团队曾多次访问以色列，试图收购“飞马”软件的生产商NSO集团[28]。总部位于意大利的软件开发商Hacking
Team是一家向多国机构出售间谍软件工具的公司。美国FBI也是它的客户，据Wired报道，从2011年起，美国联邦调查局曾先后共支付了77万美元购买Hacking
Team公司的“伽利略”远程控制系统[29]。必须指出的是：无论是“飞马”，还是“伽利略”，都可以与“量子”系统的投放机制配合，作为突破得手后，实现持续作业。

###  **5.4 A** **2** **PT** **组织资源运营与作业关系分析**

美方情报机构通过公开安全活动、代理人模式、漏洞悬赏合作以及与网络军火商采购的模式在全球搜集、采购0day漏洞，并通过与网空防务承包商、电信基础设施公司和互联网公司构建网空项目、武器、基础设施和大数据支撑，依托在全球部署的项目和作业平台，利用植入、运载和中继装备，通过漏洞投放各类高级恶意代码，针对全球IT目标发起大量攻击行动，其组织运营和作业关系图谱推测如下：

![1686323942_648342e6781f34c558691.jpg!small](https://image.3001.net/images/20230609/1686323942_648342e6781f34c558691.jpg!small)

图 5‑4 A2PT组织的资源运营和作业关系图谱

##  **06** **小结：迎接智能终端设备面临的A** **2** **PT** **攻击挑战**

由于iOS环境特点，我们针对方程式组织针对iOS攻击的相关分析工作的展开，比我们之前分析方程式组织针对Windows、Linux、Solaris系统的攻击和硬盘持久化行为更加艰难。基于前文提到的分析工作：相关针对iOS移动设备木马样本系方程式组织所使用的网络攻击武器，与我们与Windows、Linux、Solaris所披露曝光的系列样本同属DoubleFantasy攻击装备谱系。该木马可以通过“量子”系统，基于iOS平台Safari浏览器0day漏洞进行远程植入和执行，并采用加密方法实现明文信息的隐藏，同时在运行之后删除自身达到内存作业，而无文件落地以对抗取证的目的。这些分析工作让方程式组织的攻击武器对操作系统平台覆盖能力的证据拼图得以进一步完善，对《从方程式到方程组》报告中所编制的图表进行更新。表
6‑1 方程式攻击组织多平台操作系统载荷的曝光过程

  

![1686906152_648c25281bc29bfc717f3.jpg!small?1686906152687](https://image.3001.net/images/20230616/1686906152_648c25281bc29bfc717f3.jpg!small?1686906152687)

我们在本篇报告所分析的相关样本及其必然存在的后续版本，不仅可以基于iMessage漏洞投放，更可通过“量子”系统，基于手机访问互联网的过程来实现更隐蔽的投放。我们对“量子”系统可攻击目标基于一个参照系进行了枚举，进行了可攻击目标图谱的绘制。本次相关事件和样本聚焦于iOS平台，但这并不代表其他平台和场景就是安全的。“量子”投放体系、面向浏览器和网络客户端的漏洞库，A2PT组织的这个能力体系，具备在几乎所有PC和移动设备访问网络过程中打击投放的能力。其将全球手机用户和网民都置于“量子”高悬的达摩克里斯之剑下。在实际作业中，A2PT组织可以针对高价值目标精确打点，而防御方找到受害者却犹如大海捞针，处于极为困难被动的境地。但这些都更说明，手机和智能终端的安全性需要进一步提升。手机等智能终端设备相对于传统PC节点来说具有更强的个人关联性，其设备上的数据资产与人本身、及其社交范围、行动轨迹、行为偏好等存在高度的关联性，例如定位数据、手机通讯录、文档文件、短信通话、照片。通过对设备上的数据资产的收集和分析，能够对目标人员的工作生活、人员画像以及周边环境进行定向精确的画像分析。近几年来，手机等智能终端设备不仅为人们提供了日常生活的信息化和智能化便利，也被国内大量政企机构、工业部门等引入作为移动办公环境（包括生产运营系统的远程管理）。特别是在广泛使用的双因子认证和零信任体系中，手机+SIM卡已经成为核心的令牌设备。一旦手机失陷，攻击者不仅能收集到与目标人员相关的更高价值的数据资产，更成为入侵政企机构内网的突破口和跳板。手机等智能终端设备具有远超传统PC节点的广泛感知能力，其带有多种传感器（包括带有GPS传感器用于获取高精度定位，加速度传感器、重力传感器、陀螺仪和旋转矢量传感器）可被用于获取当前设备的高精度即时动态。除了高精度传感器外，还有摄像头、麦克风这种输入输出的硬件采集装置，甚至是基于WiFi、蓝牙模块进行周边环境和设备的扫描和收集。这种特性使A2PT组织入侵智能手机后可以取得比PC或服务器更丰富的关联收获。

手机等智能终端设备有更多的暴露面和可攻击面，包括终端技术栈层面的攻击面，涉及硬件、固件、系统和应用，通信层面的攻击面，涉及WiFi、蓝牙、蜂窝网络、GPS等，供应链层面的攻击面以及系统和互联网生态下的攻击面。从设备使用和定位来看，手机等智能终端设备作为消费级的产品，其会基于产品体验来权衡安全性的设计，并且用户会通过手机设备从不同的渠道下载应用、浏览网站等，但从手机终端防御机制和体系来看，手机设备的安全性防御体系主要依赖于供应商和制造商引入的系统安全管控和缓解机制和应用的威胁检测防御，一旦突破某些单点安全策略，攻击和防御就不再对等。再者，由于移动互联网环境下，国际互联网厂商过量的信息攫取，经过“棱镜”等特权接口，也成为超高能力网空威胁行为体能准确定位攻击目标的来源。

在手机系统中，苹果安全机制设计长期是被称道的，其安全体系和封闭式应用生态等降低了系统和设备被一般性攻击的可能性和安全风险，但在卡巴斯基曝光的事件中，苹果手机反而成为一个难以有效进行环境分析和取证的“黑箱”。

也许比被APT攻击更危险的，是霸权主义和单边主义对世界的撕裂。

安天始终致力于为手机和智能终端、云和其他各种计算环境提供基础安全能力，这些能力包括了移动恶意代码检测、Wi-Fi接入安全、支付安全、扫码安全等。我们也一直努力支持手机和智能操作系统厂商研发改善安全设计，通过削减攻击面，增强安全缓解和管控策略，例如引入权限模型，应用生态管控，建立响应体系。我们尊重且敬畏自己的工作，但我们必须指出，手机是一种海量的消费级产品，其更多是面向便利性而设计，面向普通使用者，而非IT管理运营人员使用。手机厂商出厂的原生安全机制，是构建一个良性的基本面，支撑较好的运营和治理基础。但通用的安全机制，无论多么强劲，都很难对抗使用0day漏洞和专用样本的APT攻击，更不是简单靠安全意识和习惯就能解决的。而即使在消费级智能设备和系统上，寄希望于通过数据和运行环境隔离，设备入网管理和访问控制，容器级的应用管控等策略，很难完全对抗使用0day漏洞和先进样本的APT攻击。对有高安全需求场景的移动终端，需要以基于成熟的商业产品为基础，基于更专门的投入和保障体系，达成更强的安全防御能力。

与此同时，只有体系化和全生命周期的防御、溯源和猎杀机制，才能对抗体系化和全时间窗口的攻击，这个战场既在桌面终端、移动手机终端之上，也在网络设备和边界设备（包括安全设备）之上，更在内网和云计算等纵深资产之中。

让威胁检测、主动防御等更多安全能力基因化、底层化，从供应链层面构建原生融合的安全能力，实现“关口前移，防患于未然”，是我们的始终专注的工作，这些工作将持续塑造一个有利于防御攻击的供应链安全基本面；发现分析溯源曝光高级威胁，是我们始终奋战的战场，这些工作不仅持续检验和改善我们的核心安全能力，有助于公众了解网络空间的风险，有助于关键信息基础设施和政企机构以更真实客观的敌情想定改善网络安全能力。我们将继续为此付出努力。

参考资料：

[1] 美国情报机构网络攻击的历史回顾——基于全球网络安全界披露信息分析

https://www.china-cia.org.cn/home/WorkDetail?id=643368b50200340e00ff4fc7

[2] 探索Duqu木马身世之谜

https://antiy.cn/research/notice&report/research_report/261.html

[3] Equation: The Death Star of Malware Galaxy

http://securelist.com/blog/research/68750/equation-the-death-star-of-malware-galaxy/

[[4]
震网事件的九年再复盘与思考](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650173867&idx=1&sn=6b12446b10650f6c00784a63d3c486fb&chksm=beb9d29989ce5b8facbbad4c31886e98184461da5ced81e802a4f1c5e7c90f36c45d8e594de6&scene=21#wechat_redirect)

https://www.antiy.com/response/20190930.html

[[5]
从“方程式”到“方程组”EQUATION攻击组织高级恶意代码的全平台能力解析](https://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650170101&idx=1&sn=714546c757db8291d52b6a4332c364a4&chksm=beb9c1c789ce48d1d6a96ed51b2506feab47c344b50461e7a4f72b19d89879dc113669d47a33&scene=21&token=1730485739&lang=zh_CN#wechat_redirect)

https://www.antiy.com/response/EQUATIONS/EQUATIONS.html

[6] Operation Triangulation: iOS devices targeted with previously unknown
malware

https://securelist.com/operation-triangulation/109842/

[7] Bvp47 美国NSA方程式的顶级后门

[https://mp.weixin.qq.com/s/WTlRPzUv3npV8xd9KRJoQw](https://mp.weixin.qq.com/s?__biz=Mzk0MzMyOTE3MQ==&mid=2247483669&idx=1&sn=f24e32410b6cff8c0de9f4b90dc1e649&scene=21#wechat_redirect)

[[8]
方程式（EQUATION）部分组件中的加密技巧分析](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=206299704&idx=1&sn=64c8e787cf5199ce8613002e0300f3e6&chksm=2f04410a1873c81c9874355da75b8d05346a42e57c0899983a8c0911cb5bb1e43430d1bc7808&scene=21#wechat_redirect)

https://www.antiy.com/response/Equation_part_of_the_component_analysis_of_cryptographic_techniques.html

[[9] 修改硬盘固件的木马-探索方程式（EQUATION）组织的攻击组件](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=204971422&idx=1&sn=261bd60159aeb1a4881a9b24c78f1007&chksm=2f783eac180fb7baeed8ef195cbdb3c66275d8c6fb8745f5dc1eba71da1d71711a11ce79e2c5&scene=21#wechat_redirect)

https://www.antiy.com/response/EQUATION_ANTIY_REPORT.html

[[10]
美国国家安全局（NSA）“狐酸”漏洞攻击武器平台技术分析报告](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650189568&idx=1&sn=75d4ce44c281f16aa1a13f0916bd5600&chksm=beb90c3289ce8524bd08507c0aa0326062a5cc33137b0f123a9089779fc3e08a95cf83b12d82&scene=21#wechat_redirect)

https://www.cverc.org.cn/head/zhaiyao/news20220629-FoxAcid.htm

[[11]
“方程式组织”攻击SWIFT服务提供商EastNets事件复盘分析报告](http://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650173349&idx=1&sn=fbbf2624ce149edee2db05c8661e28fb&chksm=beb9cc9789ce45814b1b0fef8e80b09be3363e5b5b9e891bae53f46d033418494c4403d1bc61&scene=21#wechat_redirect)

https://www.antiy.com/response/20190601.html

[12] The nsa hacks other countries by buying millions of dollars worth of
computer vulnerabilities

https://www.washingtonpost.com/blogs/the-switch/wp/2013/08/31/the-nsa-hacks-other-countries-by-buying-millions-of-dollars-worth-of-computer-vulnerabilities/

[13] 10 Things You Need To Know About 'Wikileaks CIA Leak'

https://thehackernews.com/2017/03/wikileaks-cia-vault7-leak.html

[14] 美国NSA主导的VEP-《漏洞公平裁决政策和程序》的是是非非

https://www.ics-cert.org.cn/portal/page/122/e999bf92e06f42b89800faf420b45b14.html

[15] 维基百科：NOBUS

https://en.wikipedia.org/wiki/NOBUS

[16] Aris. Dual_EC_DRBG Backdoor: a Proof of Concept

https://blog.0xbadc0de.be/archives/155

[17] The intelligence coup of the century’For decades, the CIA read the
encrypted communications of allies and adversaries.

https://www.washingtonpost.com/graphics/2020/world/national-security/cia-crypto-encryption-machines-espionage/

[[18]
安天针对勒索蠕虫“魔窟”（WannaCry）的深度分析报告](https://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650170534&idx=1&sn=dedc3ff25c3594b49bc4e6c53c9fd123&scene=21#wechat_redirect)

https://www.antiy.com/response/wannacry.html

[[19]
《关于系统化应对NSA网络军火装备的操作手册》](https://mp.weixin.qq.com/s?__biz=MjM5MTA3Nzk4MQ==&mid=2650170743&idx=1&sn=4911fab3c2e2f0e97a4666e2d5e8da11&scene=21#wechat_redirect)

https://www.antiy.com/response/Antiy_Wannacry_NSA.html

[20] Pwn2Own list of notable hacks is incomplete

https://en.wikipedia.org/wiki/Pwn2Own

[21] Five Reasons I Want China Running Its Own Software

https://taosecurity.blogspot.com/2017/03/five-reasons-i-want-china-running-its.html

[22] NSA Surveillance Has No Boundaries, Expert Says

https://threatpost.com/nsa-surveillance-has-no-boundaries-expert-says/103355/

[23] The U.S. Government and Zero-Day Vulnerabilities.

https://jia.sipa.columia.edu/sites/default/files/attachments/Healey%20VEPpdf

[24] 6 months later, Spectre still haunts.

https://securityboulevard.com/2018/07/6-months-later-spectre-still-haunts/

[25] Hack the Pentagon 3.0 Bug Bounty Program to Focus on Facility Control
Systems

https://www.securityweek.com/hack-pentagon-30-bug-bounty-program-focus-facility-control-systems/

[26] REGULATING THE ZERO-DAY VULNERABILITY TRADE:A PRELIMINARY ANALYSIS

https://fsi-live.s3.us-west-1.amazonaws.com/s3fs-public/fidler-second-review-changes-made.pdf

[27] Pegasus: Spyware sold to governments 'targets activists'

https://www.bbc.co.uk/news/technology-57881364

[28] FBI acknowledges it tested NSO Group’s spyware

https://www.washingtonpost.com/technology/2022/02/02/pegasus-fbi-nso-test/

[29] L3 Harris in talks to buy Israeli spyware firm NSO

https://www.reuters.com/markets/deals/l3harris-talks-buy-israeli-spyware-firm-nso-reports-2022-06-15/

[30] The FBI Spent $775K on Hacking Team's Spy Tools Since 2011

https://www.wired.com/2015/07/fbi-spent-775k-hacking-teams-spy-tools-since-2011/

[31] Shadow Brokers reveals list of Servers Hacked by the NSA

https://thehackernews.com/2016/10/nsa-shadow-brokers-hacking.html

[32] A Fanny Equation: "I am your father, Stuxnet"

https://securelist.com/blog/research/68787/a-fanny-equation-i-am-your-father-stuxnet/

[33] Equation Group: from Houston with love

https://securelist.com/blog/research/68877/equation-group-from-houston-with-love/

[34] Equation_group_questions_and_answers

https://securelist.com/files/2015/02/Equation_group_questions_and_answers.pdf

  

