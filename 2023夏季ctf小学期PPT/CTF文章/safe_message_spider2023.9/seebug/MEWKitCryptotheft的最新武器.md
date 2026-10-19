译者：[知道创宇安全服务团队、404区块链安全团队](http://scanv.com/ "知道创宇安全服务团队")  
[[PDF版本下载]](https://images.seebug.org/archive/MEWKit_Cryptotheft_%E7%9A%84%E6%9C%80%E6%96%B0%E6%AD%A6%E5%99%A8.pdf
"\[PDF版本下载\]")

#### 介绍

当谈到加密货币时，会联想到加密货币巨大的价格波动，交易违约、赎金勒索的情况以及许多不同种类的货币。虚拟货币自兴起以来，就一直受到罪犯无情地攻击，许多人都希望能从中获取利益。在此威胁报告中，我们将重点关注Ethereum，也称为“以太”，以及它与名为MyEtherWallet（MEW）的在线服务的关系，该服务是网络钓鱼自动传输系统（ATS）MEWKit的目标。

MEWkit的突出之处在于它远不止传统的网络钓鱼套件那样，除了是一个以窃取凭证为目的的模仿MyEtherWallet前端的网站以外，它也是一个客户端
，可以处理钓鱼页面捕获的付款细节以转出资金，将资金从钓鱼受害者以太坊钱包直接寄给攻击者控制的钱包。

本报告详细阐述了MEWKit功能，背景以及过去和现在的一系列行为活动，并对2018年4月24日发生的一件重大事件作一些说明。那就是在亚马逊DNS服务器上执行边界网关协议（BGP）劫持攻击，将用户从官方的MyEtherWallet网站重新路由到运行MEWKit的主机。

#### 理解犯罪：理解目标

MyEtherWallet不像其他加密货币交易所和交易平台，它没有内部账户。一个典型的交易所像银行一样运作 ，用户通过创建一个账户来实现资金转入和转出。
通过这种方式，交易所就有了添加了增加了额外安全措施的用户钱包的关键词。 这些银行和交易所也能够执行分析以查看什么设备正在用于登录，并知道从那里登录。

另一方面，MyEtherWallet取消了用户拥有账户的中间步骤，并为用户提供了一个钱包允许他们直接与以太坊网络进行互动。
这种访问使MyEtherWallet变得非常透明，但没有大多数银行和交易所的附加安全层面也造成一些重大风险问题，并使其成为攻击的主要目标。

一旦MEWKit受害者认为他们正在与官方互动，钓鱼攻击就成功了。MyEtherWallet网站的资金可直接转给攻击者。
因此，我们说MEWKit是专门为MyEtherWallet制作的网络钓鱼ATS。

#### MEWKit 技术分析

MEWKit由两部分组成：一个模仿MyEtherWallet站点的钓鱼页面和一个处理日志的服务器端，攻击者一旦进行网络钓鱼就会将受害者的钱包里面的资金转移至攻击者指定的地点。
典型的钓鱼网页通常会重定向到网站的合法版本，这样受害者可以再次登录，MEWKit只是通过受害者的浏览器，使用MyEtherWallet对以太坊的独特访问权限，在后台进行交易。

MEWKit被其开发者称为自动传输系统，因为它捕捉到的任何钓鱼信息都会立即用于从受害者的钱包中转移资金。ATS恶意软件运营的概念来源于它的恶意软件操作，它将脚本注入金融网站上的活动网络会话中，以便将资金从受害者账户中转出，并在被感染的电脑上利用受害者登陆的账户在短时间内无形地自动完成转帐。

一旦用户登录，MEWKit就会检查他们的钱包余额并从服务器端请求接收者地址。然后将攻击者的拥有的钱包设置为接收者地址，利用正常的MyEtherWallet功能转移受害者的全部余额。

#### MEWKit 钓鱼页面

由于MyEtherWallet完全在客户端运行，并且可以脱机运行，因此攻击者可以下载手动构建它，这正是MEWKit的开发者所做的。MyEtherWallet源代码可以从GitHub下载：<https://github.com/kvhnuke/etherwallet>

MEWKit是由一个添加多个脚本的MyEtherWallet组成。
它在页面中嵌入了两个额外的JavaScript资源文件，通常命名为：sm.js和wallet.js
。它们都从合法的MyEtherWallet脚本文件路径相同的目录中加载。

###### wallet.js - Configuration

该脚本充当MEWKit其余部分的配置文件。 它有两个选项来设置：

`js_stat`

这个变量是包含后端地址的字符串，开发者称其为'admin面板' ，此变量的值用于获取转帐资金的接收地址和发送页面上发生的所有事件的日志。

`user_in_page`

虽然变量名称有些模糊，但它只是用来标记启用或关闭日志记录的， 1表示启用日志记录，0表示无日志记录。

###### sm.js - Core

该脚本包含MEWKit的功能部分，并挂接到MyEtherWallet的源代码中。该脚本顶部包含一组全局变量：

`____pwd`

包含受害者的钱包中的助记符短语或密码/密钥库JSON文件内容。

`ikey`

目前尚未在我们观察到的任何MEWKit版本中使用。它会在所有的回调中发送到后端，但是除了初始值“none”以外，没有被设置其他值。

`txt_ua`

包含受害者的用户代理，并调用navigator.userAgent

`send_block_ﬂg`

包含一个二进制0或1标志。一旦受害者解密他们的钱包，ATS就会将`send_block_ﬂg`设置为0并开始将可用余额转账。标志位为1的话，不会启动任何交易而且会阻止任何正进行的交易。

`balance`

一旦用户登录到MEWKit钓鱼网站，将显用户钱包中的可用余额页面。

`eth_recipient`

包含攻击者控制的用来转移盗取资金的接收地址。

`balance_block_ﬂg`

包含一个二进制0或1标志。一旦受害者解密他们的钱包，ATS就会将balance_block_ﬂg设置为0，开始检查受害者钱包中的可用余额。

`count_ﬂg`

包含一个二进制0或1标志。标志设置为1，会触发假倒计时MEWKit页面。当MEWKit开始获取钱包凭证的时候开始转移可用余额。

在这些全局变量之后，该脚本包含一组用于进行钓鱼和自动化资金转账的功能。我们不会具体解释每一个功能，但我们会显示套件的执行流程。

###### MEWKit 挂钩在 MyEtherWallet 源码中

MEWKit挂钩了MyEtherWallet的正常功能，我们将逐个浏览它所放置的钩子。MEWKit首次出现在MyEtherWallet源码中主页的`<header>`部分。
已经添加了两个MEWKit脚本和一个jQuery脚本：

![](https://images.seebug.org/content/images/2018/05/ec50122f-0e42-4fa0-956d-f400d8148977.png-w331s)

下图，我们将在`<body>`标记中找到来自MEWKit的函数调用：

![](https://images.seebug.org/content/images/2018/05/dcd1fe0c-de37-470e-87dc-ad943cf4e471.png-w331s)

该功能禁用一个用户的常见功能，即查看他们的钱包信息和余额。它还确保启动事务按钮将禁用页面上的任何其他按钮，确保用户不能去其他地方。

下一个MEWKit函数调用可以在主体中看到：

![](https://images.seebug.org/content/images/2018/05/f7a39a8d-1b19-4154-99a9-67723754b403.png-w331s)

该功能保证欢迎消息能正确地更新，它通常显示的内容为“MyEtherWallet.com”
。因为钓鱼页面的域名不总是与MyEtherWallet.com近似，有时是Ethereum及其变种单词，这个函数调用确保窗口标题和页面信息与用户正在访问的网站相匹配。攻击者不必为他们设置的每个页面更改构建。

MEWKit的下一个函数被挂接到允许访问者看到钱包余额的按钮上：

![](https://images.seebug.org/content/images/2018/05/d053175d-2747-43dc-8745-8bc82b54cd3f.png-w331s)

此功能将在用户点击钱包余额按钮时执行，并重定向用到资金转移处，MyEtherWallet代码提供资金转移功能，这样MEWKit可以进行它所需要的交易。

另外，MEWKit将改变MyEtherWallet页面上的正常视觉效果。
通常情况下，用户所在页面的按钮会突出显示，但MEWKit会突出显示'查看电子钱包信息'按钮，当用户正在转账页面上时，“查看电子钱包信息”按钮也会将用户转到资金转移页面。
当我们访问MEWKit实例时，可以看到这种行为。注意禁用的可见性通常显示的Ether-sending头部：

![](https://images.seebug.org/content/images/2018/05/c16c4075-89d6-4ba0-93d8-689eff899edb.png-w331s)

从MEWKit到MyEtherWallet的最后一次插入不在HTML页面中，而是在官方源代码中文件：etherwallet-master.js。MyEtherWallet本身是使用AngularJS框架编写的，允许开发人员构建动态功能的网页而不是静态HTML页面。AngularJS允许他们对功能和元素进行模板化，从而更轻松地提供动态网站体验。

当用户为使用MyEtherWallet的钱包而解码的时候，MEWKit通过添加一个函数调用来挂钩到angular
JS。放置的函数叫做PrivateKey_decryptWallet，这将在下一章讨论ATS执行流程中详细介绍。我们可以看到很不好的是javascript源文件中的钩入函数是一个Angular
JS文件：

![](https://images.seebug.org/content/images/2018/05/3c3965ce-5016-4480-8c6b-5734f992c10c.png-w331s)

我们可以看到我们本应该查看我们的钱包信息的页面，但是实际却开始了一个事务，如前面的截图所示。 以下是MEWKit的入口获取解密的钱包的内容：

![](https://images.seebug.org/content/images/2018/05/2d7eb178-6da6-443e-bd0e-31dd15bcb115.png-w331s)

如图所示，这些功能不会自行开始传输。 上述功能只是准备对用户进行网络钓鱼攻击页面。

###### ATS Execution flow

当用户点击一个MEWKit页面时，它会为钓鱼和ATS功能做好准备，如上所示。后在准备工作中，每次都会执行一个函数，调出后端日志，这只会影响后端wallet.js中的user_in_page变量，将其设置为1（启用日志标注）时执行：

![](https://images.seebug.org/content/images/2018/05/9b31d9dd-c24b-44b8-bf33-aa4ca76a2f76.png-w331s)

`send_data_login_`函数在ATS的整个运行过程中使用，我们将解释它以下功能供以后参考。
MEWKit对后端执行标注的方式非常完美。有趣的是，它基于提供给函数和全局的参数构造一个URL变量。
然后将该URL作为新的脚本资源嵌入主浏览器的主页面中执行标注。 如下所示：

![](https://images.seebug.org/content/images/2018/05/3558d069-e65a-4cbb-beae-939190ab2000.png-w331s)

如图所示，`send_data_login_`函数构造一个URL，然后将其放入一个新的脚本元素中，附加到文档的`<head>`。
以下是执行该操作的MEWKit实例的示例：

![](https://images.seebug.org/content/images/2018/05/4a51245b-aafa-49c1-b3e0-d2d2db3ca61b.png-w331s)

有意思的是服务器返回一个小的JavaScript片段，它设置一个名为jsess_msg的全局变量，该变量稍后与ATS功能的其余部分相关。
这是后端根据日志消息返回的内容：

![](https://images.seebug.org/content/images/2018/05/436c6973-8b3a-4797-ade9-6cda13cb45bf.png-w331s)

这个函数有另一个版本叫做`send_data_login_pv`，因为它被修改为记录钱包到后端的私钥，这个版本的格式也可以编码和发送私钥。只有当用户上传私钥访问他们的钱包时，才会调用这个函数，密钥文件内容也被转发到后端。

当受害者通过使用MyEtherWallet提供的方法解密他们的钱包时，ATS功能开始实际运作，该方法触发`PrivateKey_decryptWallet`函数的onclick事件。
这个函数遍历用户可以使用的所有不同的身份验证选项并记录用户使用了什么方法，然后它开始自动传输代码。 下面是一个对每种认证方法重复的功能：

![](https://images.seebug.org/content/images/2018/05/8a4bdd5f-8520-4eed-ab50-597d5e5464a1.png-w331s)

您可以看到MEWKit记录用户使用的认证方法，设置余额并将标志位设置为0并调`check_send_block`函数。

在我们跳转到`check_send_block`函数之前，有一些重要的东西需要理解：这个特定的高亮示例使用`send_data_login_pv`函数，该函数还会发送钱包的私钥到后端。这意味着MEWKit进行攻击后仍然可以访问受害者的钱包。
如果受害者购买更多以太币，攻击者可以继续盗取受害者的资金。

这同样适用于另一种验证方法。 使用keyfile / JSON文件上传方法将文件上传到后端这也允许MEWKit攻击者继续访问受害者的钱包：

![](https://images.seebug.org/content/images/2018/05/5912f1a8-1613-4b33-9f39-79b15179b3b3.png-w331s)

函数会将上传的文件发送到后端脚本post.php中由后端路径的js_stat配置变量作为前缀。

函数将通过查看发送功能是否可用来检查受害者是否成功验证：

![](https://images.seebug.org/content/images/2018/05/719b3fe8-8c60-4aff-8531-1586182705f1.png-w331s)

这个函数会一直调用它自己，但会用标志阻塞，直到受害者可以启动交易。

然后代码跳转到`check_balance_block`函数：

![](https://images.seebug.org/content/images/2018/05/b532e874-3590-4f59-84cc-a4959aba0923.png-w331s)

虽然这个功能看起来很复杂，但它所做的只是通过手动解析HTML来检查钱包的余额，一旦它可以确定一个可用余额，就会将其记录到后端，并且调用`check_valid_balance`函数：

![](https://images.seebug.org/content/images/2018/05/21fa3a08-ab8f-44f2-9b13-979790b1c4a3.png-w331s)

`check_valid_balance`函数检查余额是否为正数。 如果不是，它会在后端记录一条消息，申明'Stop
ATS'。如果检查余额为正数，它将通过调用get_address函数来继续执行流程。
这个功能与日志功能类似，它会构建并嵌入一个脚本资源URL，以便将浏览器调用到后端。 这个用于获取收件人地址的URL是静态的，只添加当前时间戳到URL的末尾。

时间戳会附加到URL上，因为浏览器通常会很智能地使用它，并且如果相同的资源被追加两次，只会使用缓存的结果。
通过添加此时间戳会生成独一无二的URL，来确保后端服务器的更新响应：

![](https://images.seebug.org/content/images/2018/05/f7cd9a45-5bce-4e36-8dba-8f4093263bbd.png-w331s)

LoadScript函数创建一个新的脚本元素并将URL设置为由get_address生成的URL。一旦资源被加载，它将调用`get_state_address`函数继续执行流程。

`get_state_address`函数是jsess_msg变量中设置的值的解析器，该变量由后端通过LoadScript函数。 消息的解析如下所示：

![](https://images.seebug.org/content/images/2018/05/10aff813-3d35-4a7f-80dd-3777b9bc47ad.png-w331s)

`get_state_address`通过剪切和切分字符串值响应来解析变量内容，以解析出将被盗资金转移到的接收地址。
如果消息的响应中包含[EMPTY]，则MEWKit将停止处理并在日志中记录没有接收地址。
如果它能够从响应中获得地址，它将调用set_data函数，这是转移资金的最后一步。

set_data函数将通过设置接收地址来准备一个事务去触发输入。并在`set_get_trans`函数排队延误之前点击传输按钮。点击转移按钮将使用户进入交易概览页面。
然后，`set_get_trans`函数快速按下按钮以生成事务记录，之后它会对`set_yes_mk_trans`函数进行排队，然后再确认事务。
这将启动余额转移，从而窃取受害者钱包中的可用余额。

基本上，这些最后几项功能可以像合法用户那样只需按下按钮便可以自动创建，确认和开始转账。以下是我们上文提到过的MEWKit核心的所有功能：

![](https://images.seebug.org/content/images/2018/05/74674963-9d87-4b13-a3e5-7b3ab98aa606.png-w331s)

这种以自动方式窃取以太坊的功能，和我们之前在钓鱼工具包中看到过的不一样。

#### MEWKit服务器端

如上所示，MEWKit的主要功能，如部分ATS，能在JavaScrip客户端中完全运行。MEWKit的后端仅用于：

  * 日志存储：ATS中的每个步骤都会记录下每个受害者，并将其全部报告给后端
  * 私钥和密码存储：如果用户使用助记符或密码登录，则会记录和在C2上提取并存储以供以后访问。
  * 提供接收地址：将参与收件人的地址保留在后端和传送给被钓鱼的客户。

在大多数情况下，MEWKit实例的后端服务器为攻击者提供了他们正在从事的工作的概况。

#### MEWKit的限制：硬件钱包

虽然MyEtherWallet支持各种硬件钱包，如Trezor8，Ledger
Wallet9，Digital，Bitbox10和Secalot11，但却不支持从这些钱包中获取密钥。这意味着那些在使用硬件钱包时被MEWKit钓鱼的人不会受到MEWKit的ATS的影响，但仍然需要在处理之前确认其钱包上的交易。因为硬件钱包的私钥存储在内部，因此不会暴露于MEWKit。

突发的原因不明的的交易是打击MEWKit的一个标志，当然也不会接受交易所需要采取的措施。MEWKit会记录所有尝试使用硬件钱包的登录信息，它只是无法使用其ATS功能自动进行资金转账。

#### 活动的历史概述

以下部分概述了我们在RiskIQ数据库中集中观察到的所有数据攻击。以下各节中提到的AnyIOC也可以在本报告末尾的妥协指标（IOC）部分中找到。

请注意，我们没有描述观察到的每个MEWKit钓鱼网站，只列出了那些因各小节中描述的原因而可以进行钓鱼攻击的钓鱼网站。我们观察到的所有主机的完整列表可以在本报告结尾附近的“妥协指标”部分找到。

#### 权限边缘之亚马逊53

4月24日11:00
UTC过后的一会儿，针对与亚马逊路由5312相关的IP空间执行了边界网关协议（BGP）劫持，该路由是亚马逊DNS供应系统。这意味着未经授权的用户可以重新将路由一部分旨在AmazonRoute
53的流量传输到自身，并将域分辨率重新路由到他们自己选择的端点。

###### 重新路由MyEtherWallet访客

通常在亚马逊的AS16509下宣布（并维护）的以下IP块已由eNet在AS1029713下公布：

205.251.192.0/24  
205.251.193.0/24  
205.251.195.0/24  
205.251.197.0/24  
205.251.199.0/24

这些IP地址是Amazon Route
53为通过此服务维护的任何域执行DNS路由的一部分。驻留在AS10297中的上述IP块的新端点开始路由预定用于路由53的一些流量并回复来自用户的DNS查询。

实际上，我们可以看到这个AS宣布的前缀相对于它通常所宣称的非常固定的一组块而言：

![](https://images.seebug.org/content/images/2018/05/2de22fd4-c376-4f24-8103-2bd4383aeceb.png-w331s)
Source: <https://bgp.he.net/AS10297>

最终处理通常用于Route
53的流量的DNS服务器只设置了一个域来解决：myetherwallet.com。任何其他请求的域名都会被SERVFAIL响应，这是人们已经注意到的。新的DNS服务器响应一个新的IP地址MyEtherWallet，46.161.42.42，驻留在AS41995。根据地理位置，这台服务器来自俄罗斯。如果我们提供一些有关此AS的WHOIS信息，会发现它并不是一个好兆头。

![](https://images.seebug.org/content/images/2018/05/88155009-7777-4129-b0ff-1fc48d344cea.png-w331s)

在东欧分配一个AS，并在WHOIS中使用Gmail等免费服务的电子邮件地址通常是一个不好的迹象。我们可以从组织WHOISdetails中获得更多有关此地址的信息：

![](https://images.seebug.org/content/images/2018/05/de9a715e-5e7c-4c29-8bc3-dad9bbb573be.png-w331s)

根据WHOIS信息，自2014年底以来，电子邮件地址的域名一直存在，并且其详细信息始终存在于WHOIS隐私服务之后。目前，主网站onweb-shield.biz处于离线状态，但通过查看档案数据，我们可以找到一个旧的托管公司网站：

![](https://images.seebug.org/content/images/2018/05/68dc5659-21a4-48f9-8255-2713bd06bbb6.png-w331s)

Webshield对我们行业中的许多人来说都很熟悉，因为在他们的网站中有许多用于恶意目的的网站IP空间，其中一个例子是Rescator15。我们最感兴趣的是拥有这个AS的主机却已经关闭了它的网站托管网站，但仍然提供了托管机会。我们可以将Webshield定义为一个防弹主机。

###### 以太劫持：通过MEWKit实现资金转账自动化

虽然对亚马逊Route 53的攻击非常复杂，但攻击者用于托管在Webshield
AS上的服务器上的钓鱼站点的设置却不复杂。他们在服务器上放置的证书实际上并不是有效的证书，他们使用WHOIS隐私服务背后的myetherwallet
[.]com创建了自己的自签名证书。这里是以太钱包WHOIS：

![](https://images.seebug.org/content/images/2018/05/b0ca70f7-cc58-4d2b-a776-17b4ba5af4e7.png-w331s)

Source: <https://community.riskiq.com/search/myetherwallet.com>

以下是我们在使用MEWKit的Webshield主机上观察到的SSL证书：

![](https://images.seebug.org/content/images/2018/05/82007d77-e3e1-42d3-9230-e6696ebf700a.png-w331s)

Source:
<https://community.riskiq.com/search/certificate/sha1/4ee8ad8ef36d1e4461526997b78415b6dc306ee3>

攻击者只需根据WHOIS详细信息生成证书，该证书由几乎任何现代Web浏览器标记。然而，人们好像还是忽略了这些警告选择了点击，即使有人报告资金被MEWKit从他们的以太钱包中撤出。

MEWKit页面本身与任何正确构建钓鱼页面一样，看起来与正常的以太钱包网站完全相同：

![](https://images.seebug.org/content/images/2018/05/8805bb49-f275-4731-be5a-00bf77bec782.png-w331s)

然而，我们在这次攻击中看到的设置与我们在正常MEWKitinstall上看到的不同。如果我们看一下文档对象模型（DOM），我们会看到正常的MEWKit脚本（顶部MEWKit，底部MyEtherWallet.com）：

![](https://images.seebug.org/content/images/2018/05/37627f49-918d-4743-b9e2-8f8249de2d2a.png-w331s)

注意，脚本没有以任何方式混淆 ，看起来他们似乎是正确的。如果我们看看wallet.js，其中包含日志记录配置和后端位置，我们得到这个：

![](https://images.seebug.org/content/images/2018/05/5a270c16-d845-491e-8f2d-c7c070078749.png-w331s)

第一个变量将报告后端设置为`http://46.161.42.42/pind/`，第二个变量不可用日志记录。如果我们转到sm.js，我们已经可以在脚本的顶部看到添加了附加变量的一些更改：

![](https://images.seebug.org/content/images/2018/05/1e0979ed-c1b5-4f22-baae-0894035875e9.png-w331s)

正如上面MEWKit的功能所解释的，`eth_recipient`变量与被盗资金的接收者有关。如果我们检查`get_state_address`函数通常设置（单个）的`eth_recipient`变量值，我们看到开发者一直在实现多个收件人地址。该代码仍然包含注释部分，开发者忘记将添加的`eth_recipient_n`变量注释掉，因为它们没有被使用。

![](https://images.seebug.org/content/images/2018/05/9b607e25-7756-457c-aef7-4a8752be9098.png-w331s)

该函数还包含一个注释掉的console.log调用，该调用会将消息记录到控制台。这让我们更加确定开发者正在测试用于脚本攻击的新功能。

通过这个图表，我们可以找到更多俄文评论的证据。我们翻译了所有评论，并根据所用的措辞，很可能由熟悉财务条款的俄语母语人士撰写（有关下文的更多信息）。我们将逐个评论。在他们不直接翻译成英文的情况下，我们会做出解释。

![](https://images.seebug.org/content/images/2018/05/0ecc4022-4cf1-438f-b2bd-c4016511cf8f.png-w331s)

上面的文字‘проверяем доступность секции с
траншем’提到在代码段中检查‘траншем’的可用性，这是一个有趣的用词和重要的发现。
该注释是关于下面的代码将通过钱包地址来获得钱包中资金的总余额的事实。
‘траншем’这个词是‘ranche’的俄语，来自法语单词，表示交易的一部分或一部分。

![](https://images.seebug.org/content/images/2018/05/cb61d099-a843-4236-9d2f-fd3bf6c99ec9.png-w331s)

第一条注释‘получаем баланс’，即’得到平衡’，第二条注释’баланс’是平衡’一词，第三条注释，’стоп
работ’，意为’停止工作’，这能说得通是因为当程序检查到余额为0的时候来到了这条正确的分支，意味着ATS没有资金可以转移而程序可以停止工作了。

![](https://images.seebug.org/content/images/2018/05/a7e0528f-93ad-414e-aa7f-10ea78624aba.png-w331s)

第一条注释，’оставить кошелек
получателя’，翻译过来就是’设置收款人的钱包’，这与设置从钓鱼受害者的钱包中转移资金的交易收款人钱包地址的函数有关。第二条注释，’отправить
весь баланс в эмаунт ’，翻译过来就是’将全部余额转移’。这句话中的最后一个单词’эмаунт’是拼写为西里尔文的非俄语单词。

这些注释的出现意味着脚本的作者是一个以俄语为母语并至少拥有一定财务知识的人。

###### 结论

自事件发生以来，已经发布了很多关于这次具体攻击的具体细节，但我们决定更深入地了解到底发生了什么，并挖掘出与MEWKit相联系的额外见解。 亚马逊Route
53劫持（事件）只有一个目标。 虽然这次袭击的范围相对较小，但其范围可以更为巨大。

互联网是在几十年前创建的，并不是所有的构建模块都已经过时了 - BGP和DNS仍然是我们全球互联网中存在问题但至关重要的一部分。
与大多数网络安全问题一样，针对这些类型的攻击也有解决方案，但它们的效果取决于链中的每个人都加强安全性并部署解决方案。

#### IDN Phishery

几乎所有MEWKit实例都要注意的一点是攻击者利用国际化域名（IDNs）。 国际化域名攻击并不新鲜，但遗憾的是，它们在利用MEWKit的攻击中似乎非常有效。

浏览器正在迎头赶上去解决这个问题，Firefox和Chrome都实现了一个非常简单的算法来检查域名中的所有字符是否属于同一种语言。
如果不是，则显示以'xn--'开头的IDNA符号。
这个过滤器确实可以防止MEWKit的大量攻击，因为攻击者们使用来自西里尔文，希腊文，亚美尼亚文和希伯来文的特殊语言字符来替换带有特殊字符变体的字母。

当然，那些仍然会通过这些过滤器，我们希望在MyEtherWallet交易的每个人时保持小心。
请密切关注您打开的是哪个网址，最好是使用MyEtherWallet的书签页或自己输入域名。 不要使用来源于电子邮件，社交媒体的链接。

#### 不同之处

MEWKit战役中使用的大多数域和主机都使用非常特定的格式来模仿MyEtherWallet。
然而一个运行MEWKit的主机却不一样，经过仔细检查后发现其运行了一些令人好奇的脚本。
有问题的主机是tikkiepayment.info，托管在31.31.196.186。
4月9日，MEWKit实例被托管在`myyetherwallett.com/myether/`，它从以下位置加载它的MEWKit脚本：

    
    
     myyetherwallett.com/myether/js/wallet.js
     myyetherwallett.com/myether/js/sm.js

其后台地址在 wallet.js 脚本中被设置为 <https://tikkiepayment.info/showpanel/> ，wallet.js
中还包含着解释变量的注释：

![](https://images.seebug.org/content/images/2018/05/b2552ff1-7b0a-4e06-8d9e-997040975fba.png-w331s)

我们还发现位于同一主机上其他MEWKit的后台路径地址：

    
    
     https://tikkiepayment.info/pp/
     https://tikkiepayment.info/mycryptopanel/
     https://tikkiepayment.info/showpanel/

如果我们检查一下主机tikkiepayment.info，我们发现一些之前从来没有在其他MEWKit实例中见到过的奇怪的东西：它为攻击者运行着与MEWKit无关的基于web的工具。在
<https://tikkiepayment.info/pv/> 上，托管着一个允许攻击者使用MyEtherWallet API来批量检查Ethereum
keys的工具：

![](https://images.seebug.org/content/images/2018/05/a58c5f6b-3cdc-40d7-8e9e-3ad7b85a62ff.png-w331s)

尽管网络犯罪中窃贼之间通常不存在荣誉，但该工具是其他人可以使用的精简版MyEtherWallet，它检查帐户是否有效并且有一些余额。根据服务器上存在的工具以及它是我们曾经观察过MEWKit上的第一台主机的事实，我们认为这台主机是由MEWKit的创建者设置的。此外，根据本报告底部IOC部分显示的注册信息，域名会在任何MEWKit主机设置之前一个月进行登记。

#### 走出以太坊

尽管我们不能确切的说MEWKit操作是单一攻击者，但我们确实发现了MEWKit实例和其他加密货币和加密货币交易所的钓鱼页面之间的一些有趣链接。

4月17日，MEWKit实例在`www.xn--myetherwalle-occ.com`上正式运行，它的MEWKit脚本从以下位置加载：

    
    
     cdnsﬁles.com/js/wallet.js
     cdnsﬁles.com/js/sm.js

后端位置托管在，但另一个MEWKit实例直接托管在cdnsfiles.com上，其资源从上述同一位置加载，后端位置设置为cdns文件的.com / ADM
/。

我们看到另一个网站从cdnsfiles.com加载资源，这不是MEWKit实例，而是blockchain.info的钓鱼页面。
该页面本身是一个普通的钓鱼网站，并没有包含MEWKit所拥有的ATS组件 - 它只是收获了登录凭证。 然而，更有趣的是它从以下位置加载资源：

![](https://images.seebug.org/content/images/2018/05/21206310-beb6-4346-8583-7b0422554e68.png-w331s)

它在用于MEWKit的同时使用cdnfiles.com作为其钓鱼资源，这告诉我们MEWKit背后的攻击者拥有非常广泛的钓鱼页面组合。如果我们查看钓鱼页面的主机，185.207.205.16，我们发现另一大部分钓鱼域名主要关注blockchain.info。
然而，Coinbase也有一个IDN网络钓鱼：

![](https://images.seebug.org/content/images/2018/05/d53a041d-380b-4e11-aeaa-b3bd67a381e0.png-w331s)

资源: <https://community.riskiq.com/search/185.207.205.16>

综上所述，因为此报告仅关注MEWKit ，所以RiskIQ
PassiveTotal中的域名尚未添加到本报告的IOC部分。然而，由于它提供了MEWKit，因此在本报告IOC部分中提到的IP地址将提供足够的数据点来开始单独的调查。

#### 总结

MEWKit自今年年初就一直被广泛使用了，尽管我们在2018年以前都没见过它，但或许MEWKit在外界早已以不同的功能或形式活跃了。BGP劫持亚马逊Route
53的行为显示了它驱动的攻击者和活动的持续性，执行其攻击的成本表明MEWKit异常成功，技术虽然简单，但却有效地窃取了以太坊。

正如我们在MEWKit的技术分析中所解释的那样，我们无法估计攻击者的收益，因为我们无法知道攻击者控制了多少钱包和地址，这是由于MyEtherWallet的设置方式是以每个受害者为基础发放的地址的。区块链的架构，特别是以太坊允许每个人通过公簿洞察钱包地址余额，但它也维护了所有者的完全匿名性。直到攻击者被抓获或执法部门提供MEWKit攻击中使用的精确地址的见解前，我们永远不会知道其确切的运作。

我们确实知道，各种钱包已经在社交媒体和论坛上发布，表面上收入可能达数百万美元，但我们无法高度自信地将其与MEWKit联系起来。
然而，随着注册域名数量的增加，服务器维护的增多以及活动水平的提高，我们可以推测这次攻击的收入必须足够丰厚，不仅能够维持运营，而且还能盈利。

#### 妥协指标

以下部分包括我们观察到的所有直接属于MEWKit的IOC（控制反转）以及IOC的行为，这些IOC同样可以用于自动化的PassiveTotal项目：<https://community.riskiq.com/projects/27cddf0e-a912-1ca7-5a9e-6182d3674045>

以下IP地址被检测到正在执行MEWKit实例，并且与列表下方列举在表格中的一个或多个域名相关联。

    
    
     185.145.131.134
     185.207.205.16
     185.207.205.25
     185.61.137.36
     198.50.209.83
     31.31.196.186
     37.1.203.209
     46.161.42.42
     5.45.69.74

以下是包含注册日期及用于注册的电子邮件地址的详细域名列表。如果电子邮件地址丢失，这意味着该字段默认由隐私服务或注册商填写。由MEWKit建立和用于活动的域名的注册日期紧密重合。

![](https://images.seebug.org/content/images/2018/05/2a5a6ab1-49d0-4ca7-ab73-9d72b3b31da8.png-w331s)

![](https://images.seebug.org/content/images/2018/05/9ff8cb24-6d10-400f-ba60-78723b0da08c.png-w331s)

![](https://images.seebug.org/content/images/2018/05/414d012e-7eae-4503-8258-ff8fba0ae64d.png-w331s)

![](https://images.seebug.org/content/images/2018/05/6e340463-93e4-4888-ac39-0136611b1a69.png-w331s)

* * *

**高端渗透测试服务，请访问<http://www.scanv.com>  
招贤纳士：tiancy@knownsec.com**
![](https://images.seebug.org/content/images/2018/05/aba3ae0a-b9e6-495a-a395-89ef608742c0.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/608/>

