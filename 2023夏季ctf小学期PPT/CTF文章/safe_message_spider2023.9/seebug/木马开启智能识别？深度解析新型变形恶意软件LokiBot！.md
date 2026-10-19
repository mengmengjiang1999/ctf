作者：钱盾反诈实验室

#### 0x1.木马介绍

近期，Client-Side
Detection披露“LokiBot”木马，钱盾反诈实验室快速响应分析，发现“LokiBot”木马前身是由“BankBot”演变而来。与其他银行劫持木马相比“LokiBot”具备其独特功能，可以根据不同目标环境发起相应攻击，比如主动向用户设备发起界面劫持、加密用户设备数据，勒索欺诈用户钱财、建立socks5代理和SSH隧道，进行企业内网数据渗透。

“LokiBot”传播途径通过恶意网站推送虚假的“Adobe Flash Playe”、“APK Installer”、“System
Update”、“Adblock”、“Security Certificate”等应用更新，诱导用户安装。运行截图如下：

![](https://images.seebug.org/content/images/2017/11/60c5aa58-e7a6-4358-991e-a3f81ff931f5.png-w331s)
![](https://images.seebug.org/content/images/2017/11/0be76690-8c62-4e88-873e-e34be653ff52.png-w331s)

#### 0x2.样本分析

##### 2.1 恶意代码解析

LokiBot关键组件和代码块如下：

![](https://images.seebug.org/content/images/2017/11/e0a7a60a-5293-42fc-adbe-f38216fcb361.png-w331s)

MainActivity：恶意代码执行入口。模拟器检查［1］、图标隐藏、引导激活设备管理、启动CommandService和InjectProcess。
Boot：Receiver组件，恶意代码执行入口。核心服务CommandService保活。

CommandService：核心服务，根据远程控制指令执行恶意代码。

InjectProcess：界面劫持服务。

Crypt模块：加密文件、锁定设备实施勒索。

Socks模块：实现Socks5协议和SSH隧道，使受控设备所在内网服务器和攻击者主机之间能进行流量转发。

##### 2.2 远程控制

首先上传设备deviceId、锁屏状态、网络类型至控制端（ **92500503912** :Loki:1:wifi）。
控制端以用户deviceId作为肉鸡ID，并下发指令数据，触发恶意行为。指令包括：

![](https://images.seebug.org/content/images/2017/11/61efba76-7fcd-4402-bbf0-402824e9eb37.png-w331s)

LokiBot会根据采集到的用户数据，发起相应的攻击。攻击手段主要包括以下三种方式：

  1. 用户设备安装有银行或社交类app会发起应用劫持攻击；
  2. 用户网络环境属于某企业，会进行内网渗透；
  3. 直接发送DeleteApp或Go_Crypt指令，实施勒索敲诈。

##### 2.3 应用劫持

劫持过程与“BankBot”木马［2］相似，都是上传用户安装列表，在云端配置劫持界面，后台监视应用，一旦用户开启劫持列表内的应用，就弹出钓鱼界面覆盖真实应用，诱导用户输入账户和密码。由于此类木马生命周期短，“LokiBot”则采取主动发起应用劫持。方式包括：

  1. 通过远程指令启动待劫持应用；
  2. 主动弹出伪造的app Notification，一旦用户点击就弹出钓鱼界面

![](https://images.seebug.org/content/images/2017/11/3d401eef-43d6-45c5-81c7-412df82ff4cd.png-w331s)

##### 2.4 内网渗透

若受控设备处于内网环境，“LokiBot”下发startSocks命令，建立Socks5代理和SSH安全隧道[3]，攻击者这样以移动设备为跳板，入侵内网，窃取企业数据资产。

“LokiBot”木马内网渗透过程：

  1. 木马（SSH客户端）主动连接攻击者主机（SSH服务端），建立SSH连接，并设置端口转发方式为远程端口转发，这样完成SSH Client端至SSH Server端之间的安全数据通讯，并能突破防火墙的限制完成一些之前无法建立的TCP连接。
  2. 木马作为socks服务端创建一个socket，等待本机的SSH客户端（木马）连接，连接成功后就可以通过SSH安全隧道进行内网数据渗透。

![](https://images.seebug.org/content/images/2017/11/74672b44-9228-45ba-83be-6ec5a0660f9d.png-w331s)

###### 建立SSH安全传输隧道

控制端下发的”startSocks”数据指令还包括：攻击者主机IP、木马作为socks服务器要监听的端口、木马连接攻击者主机（SSH服务器）的用户名、密码信息。木马创建一个异步任务，内部使用JSch包提供的接口实现攻击端主机连接，端口转发设置。

![](https://images.seebug.org/content/images/2017/11/74f278ad-8e88-4cb7-9288-0698f066424b.png-w331s)

###### socks代理

木马实现了一套socks5协议，在内网服务器和攻击者之间转发数据流量。这样木马设备（SSH客户端）会将访问的内网数据，通过SSH隧道安全传输到攻击者。

![](https://images.seebug.org/content/images/2017/11/a5f132a8-041a-44d5-bde1-44485b1feef6.png-w331s)

##### 2.5 锁屏勒索

LokiBot成功诱导用户激活设备管理后，隐藏在后台，执行恶意代码。若用户检测到恶意软件，尝试卸载、控制端下发DeleteApp或Go_Crypt指令，都会触发设备锁定，加密用户设备文件代码。下图取消设备管理权限，触发执行CriptActivity$mainActivity，实施锁屏勒索。

![](https://images.seebug.org/content/images/2017/11/8d4f1ca4-f6b2-4da6-9c17-036e38c455d3.png-w331s)

AES加密设备SD目录下所有文件，并将原文件删除。

![](https://images.seebug.org/content/images/2017/11/9db7e300-7db8-4e52-a919-29467979d9b9.png-w331s)

通过向设备Window添加flag＝FLAG_WATCH_OUTSIDE_TOUCH｜FLAG_LAYOUT_IN_SCREEN｜FLAG_NOT_FOCUSABLE
的View，使用户无法使用手机，恐吓用户设备文件被加密，必须通过比特币支付$70。BTC支付地址硬编码在资源文件里，根据交易地址可查询到，该账户2015年7月份发生第一笔交易，今年2月开始交易频繁，近期交易呈下降趋势，账户共发生1341笔交易，共计收入48.821BTC。

![](https://images.seebug.org/content/images/2017/11/79f2bab0-1308-40cf-8fd2-f789b00ece5e.png-w331s)

##### Sample sha256

    
    
    97343643ed13e3aa680aaf6604ca63f447cdfc886b6692be6620d4b7cddb2a35
    00d8b0b6676a3225bd184202649b4c1d66cd61237cfad4451a10397858c92fd3
    b28252734dd6cbd2b9c43b84ec69865c5ee6daea25b521387cf241f6326f14a3
    6fbecc9ecf39b0a5c1bc549f2690a0948c50f7228679af852546a1b2e9d80de6
    b3c653d323a59645c30d756a36a5dd69eb36042fc17107e8b4985c813deabaf5
    b2cc3b288d4bb855e64343317cf1560cb09f22322618c5ff9bdc9d9e70c8f335
    f5a5f931e11af31fa22ef24ba0e4fff2600359498673d18b5eb321da1d5b31e0
    bf13ee6be6e13e8a924ca9b85ad5078eafabf5b444b56fab2d5adcf3f8025891
    fea63f4b85b4fd094a761cd10069d813c68428121b087f58db2ea273250ec39b
    ab51dcd0629758743ed1aa48531a71852a49454cc9c90f37fbedb8c02547d258
    a912166eaf2c8e0c3c87f17bb208f622a0b51bfa1124e5ba84f42a4adf7a96b4
    1979d60ba17434d7b4b5403c7fd005d303831b1a584ea2bed89cfec0b45bd5c2
    97d7c975ceb7f7478d521b0f35fdb4a14bd26c6dfde65e29533fdaf6d1ac9db6
    1d828d3a89242513048546769f3c1394ff134b76ed08c7d8d9ec07e495cd14f5
    1902424d09c9ddce312c84d166353199c5e6da97918b61616ec38431bdaa1359
    b89892fe9fd306636cb79225ab260320b26b2313d1f415f885b8d6843fcc6919
    e8714558ba46b2e44f1167baf0e427ed408c6946a045be245061f1a914869a27
    418bdfa331cba37b1185645c71ee2cf31eb01cfcc949569f1addbff79f73be66
    a9899519a45f4c5dc5029d39317d0e583cd04eb7d7fa88723b46e14227809c26
    3c258581214d4321875218ed716d684d75e21d6fa5dc95c6109d6c76de513aca
    a1f7498c8ae20452e25bb1731ab79f8226ed93713990496009cd9060954cea3c
    3136fd5a06ad5b1cdc48ade31fe5fdce6c050e514f028db18230d31801592995
    7ebebd2b83ea29668e14d29e89e96cf58665e01603b970823b2f4f97e7a2c159
    e46aee4b737d1328b7811d5d6158a6e1629dc3b08d802378eaba7c63d47de78b
    1e4795407db5f3084fcdc8ebb3a1486af4720495d85c5ebe6b8489fc9f20e372
    1a18fc5f117c8240dce9379390fe5da27e6b135246dcb7ac37abb1acf47db0fe
    92229e3b0c95ad4aee3cf9f0a2270aeb62cedd35869d726399fe980154782019
    0f7fc30cc701bea7e6ffa541665670ff126a9b3bc0c55ea9bc51c461d8d629a8
    b280c4b1954abc1979a67ee9c60fd8d8690921aa92ce217592a3b0653a7694c1
    93c229c459fb13890bafc4fed2f1974948940d0cbc81ed64b4817a2c6619036e
    0b5c854fceaccad3516ebb1a424d935d393fa2f2246f1704e36e8084e29949c8
    c260e60567723af1dddc717a87cf2c24e1fdc7981ea379dd8f11f5a8f272e63c
    a09d9d09090ea23cbfe202a159aba717c71bf2f0f1d6eed36da4de1d42f91c74
    84136b96ee1487a3f763436c5e60591be321ac4dd953d2b9a03dbec908d1962a
    c6acdb6a3df9522b688a7bb38e175b332639121d840305394f05f7f594b2917c
    2bad6d8530601a8ab67dbc581184138b87d2c7cb3a63a1d15d7f774b3f4f9cd0
    bc93d1c1dea582e039f9bcb99d506842c2c2a757b57ff7fda299eac079019bd8
    7f4bbe3e6ba3a35e7a187369f5ed280de557e93121c85f2a9e4a8bb63ac8f7f2
    77c149c2892adbf2e5c69374ccf24de22788afbc5800b3d3fcd332e3d2042de2
    6eb92722e16840495363bb3f3e6bba6f2c6f30ad9eb8e891b90eb455dc5e3e91
    794d79a549711e2eba0ebbf1d2720948295b3c5e21c5c3c39064abaa632e902e
    09bad7c39020c29d68f9357812f2fb355750d3980c32c02f920f54ba42bb8726
    8ef0edca1822d0460a34f59d564458ee3cc420afc7166612cb1a16eab01583e0
    fb188fcd914e891f26985c0b19935ce5e5ca0c96a977e6c04df2a3c6c86d9ea8
    7ed19d67d7ab8934aac1a125446d3132f1f4ccfb0c2419f333bdc90f8aef09c0
    ce0c24d3c856e8f1c05f238aa5222fb11dbdfc562becdc0ff9ba2c7152860008
    18da21d688317ba1eb704b9127757d1c9feeac362537fccd7e68ecb7e06adeb9
    83497ac340f6e38b54395eacd8e02405fb5b28125b8537e74dbce1de3bef79d5
    2e6b667076dec035e5ca19823697eb64b190a9009a2d21bfd5ed7374d32c21f0

##### C&C

    
    
    http://updddatererb1.gdn/sfdsdfsdf/
    http://tyfgbjyf.xyz/sfdsdfsdf/
    http://dghooghel.com/sfdsdfsdf/
    http://sdtyoty.gdn/sfdsdfsdf/
    http://rthrew.gdn/sfdsdfsdf/
    http://spirit7a.pw/sfdsdfsdf/
    http://cofonderot.top/sfdsdfsdf/
    http://sdfsdfsf.today/sfdsdfsdf/
    http://sdfsdfsf.gdn/sfdsdfsdf/
    http://dgdfgdfg.top/sfdsdfsdf
    http://profitino365.com/sfdsdfsdf/
    http://sdfsdgfsdfsdfsd.info/sfdsdfsdf/
    http://showtopik.gdn/tosskd/
    http://showtopik.xyz/kdlhoi/
    http://showtopics.biz/saddasd/
    http://tescoy.com/asffar929/
    http://pornohab24.com/dklska/
    http://185.209.20.28/sdfsdfdsf/
    http://185.206.145.22/sfdsdfsdf/
    http://185.165.29.29/dover/
    http://185.110.132.60/sfdsdfsdf/
    http://217.172.172.10/adminlod/
    http://217.23.6.14/adminlod/
    http://94.75.237.86/sfdsdfsdf/
    http://85.93.6.104/sfdsdfsdfhfghf/
    http://77.72.84.48/gslrmgt/

#### 0x3 安全建议

“LokiBot”为例，黑客以移动设备作为跳板入侵企业内网以多次出现，因此企业应加强防范措施，严格限制不可信设备连接内网，加强员工网络安全意识。而对于普通用户，下载应用请到官方网站或安全应用市场，切勿点击任何色情链接，尤其是短信、QQ、微信等聊天工具中不熟识的“朋友”发来的链接，安装安全防护软件，定期进行病毒查杀。

#### 参考

  * [模拟器检测](https://github.com/strazzere/anti-emulator "模拟器检测")
  * [新型BankBot木马解析](https://jaq.alibaba.com/community/art/show?articleid=783 "新型BankBot木马解析")
  * [BankBot AvPass分析](https://jaq.alibaba.com/community/art/show?spm=a313e.7916648.0.0.3775bb8euvWFHg&articleid=1028 "BankBot AvPass分析")
  * [实战SSH端口转发](https://www.ibm.com/developerworks/cn/linux/l-cn-sshforward/ "实战SSH端口转发")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/441/>

