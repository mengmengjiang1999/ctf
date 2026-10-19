作者：fenix@知道创宇404区块链安全研究团队  
时间：2018年6月22日

#### 一、漏洞概述

以太坊智能合约的含义就是一组代码（函数）和数据（合约的状态），它们位于以太坊区块链的一个特定地址上。智能合约一般使用solidity语言编写。

[Morpheus Network](https://morpheus.network/ "Morpheus
Network")与世界上一些大型航运、海关和银行公司协商，通过利用区块链的智能合约技术建立一个全面服务的、全球性的、自动化的、开放的供应链平台和一个集成的加密货币支付系统
，发布基于以太坊的
[MorphToken](https://etherscan.io/token/0x2ef27bf41236bd859a95209e17a43fbd26851f92
"MorphToken")。

2018年6月22日，Morpheus Network 发[公告](https://medium.com/@themorpheus/new-morpheus-network-token-smart-contract-91b80dbc7655
"公告")称将发布新的智能合约，以更新目前含有漏洞的合约代码。新的Token名称为MRPH，新旧Token以1:1兑换。

随后，知道创宇404区块链安全研究团队开始漏洞应急，通过分析MorphToken合约代码和交易历史，确定该漏洞是由于大小写编码问题，错误的将Owned合约的构造函数Owned的首字母小写，使之成为了一个普通函数owned，任何以太坊账户均可调用该函数夺取合约的所有权，进一步实现盗币等系列非法操作。随即我们发布了相关应急报告，同时我们也注意到BCSEC安全团队发布了相关的[分析文档](https://bcsec.org/index/detail?id=157&tag=1
"分析文档")。

在后续的研究中，我们发现早在2017年8月29日，[Github](https://github.com/trailofbits/not-so-smart-contracts/blob/master/missing_constructor/Missing.sol
"Github")上就有人提到了这种因构造函数缺失导致的合约安全漏洞问题。该漏洞目前影响包括MorphToken、B2X、DoubleOrNothingImpl等多个智能合约。

#### 二、漏洞原理

在MorphToken的合约代码里：<https://etherscan.io/address/0x2ef27bf41236bd859a95209e17a43fbd26851f92#code>
可以明显的看到相关大小写编写错误：

![](https://images.seebug.org/content/images/2018/06/29a666c8-1ce4-4b1d-be09-292ce4aed7cb.png-w331s)

以太坊智能合约中的构造函数主要用于初始化，如：确定合约的所有者，并且只会在合约部署时运行。在小于0.4.22版本的solidify编译器语法要求中，构造函数的名称应该和合约名称保持一致。如果程序员在编写合约时将构造函数名称写错，那么原本的构造函数将成为任何人都可以调用的普通函数。漏洞示例代码及在Remix-ide中的复现结果如下：

##### 0x01 漏洞合约部署

下图中，Bank合约继承自Owned合约。在Owned合约中，由于错误的编码，将构造函数名称写错，owned函数成为了一个普通函数。可以看到，Bank合约部署后，由于缺少构造函数，初始化时owner为0x0000000000000000000000000000000000000000。

![](https://images.seebug.org/content/images/2018/06/d666f0b0-a307-4ab3-99ef-8a841f579c09.png-w331s)

##### 0x02 漏洞现场还原

任何以太坊账户都可以调用Bank合约继承自Owned合约的owned函数，更改Bank合约的owner变量，从而使合约所有权发生转移。

如下如所示，0x14723a09acff6d2a60dcdf7aa4aff308fddc160c这个账户调用了Bank合约的owned函数后，可以看到Bank合约的owner变成了0x14723a09acff6d2a60dcdf7aa4aff308fddc160c。同理，攻击者也可以利用这个漏洞提权，实施一系列恶意操作。

![](https://images.seebug.org/content/images/2018/06/4d0c0dac-797d-4452-b10f-94319e15af3e.png-w331s)

#### 三、漏洞影响评估

我们使用内部的以太坊智能合约审计系统对[以太坊主链上](https://etherscan.io/contractsVerified
"以太坊主链上")所有30000+公开智能合约进行了自动化审计，确认受该大小写编码漏洞影响的共计16个，以下为统计结果：

（受漏洞影响程度取决于合约的逻辑，具体代码审计结果可联系知道创宇404区块链安全研究团队）

![](https://images.seebug.org/content/images/2018/06/ffc4c4a2-6b3f-4a01-a723-62cd64772d34.png-w331s)

理论上在合约部署后，由于编码错误引起的构造函数缺失，owner默认值会变为0x0000000000000000000000000000000000000000，这样合约中涉及到owner的函数调用都会异常，合约所有者应该能及时发现漏洞才是。然而MorphToken这种市值几百万美金的代币，因为合约存在这个编码漏洞而被盗币。通过分析Morph
Token源代码，我们得到了答案。MorphToken继承了Owned合约，但是自己实现了构造函数。就是说，是父合约向外留了一个“后门”。

![](https://images.seebug.org/content/images/2018/06/d2c38d79-ddaa-4520-8526-6ab0c5ad5046.png-w331s)

另一种情况，如果合约中没有涉及owner权限的函数调用，那么即使攻击者盗取了合约所有权，也没有任何用处。上表B2X合约中就是这种情况。

总体来说，受漏洞影响的合约数量不多，属于被MorphToken带着“火”了一把的漏洞。

事实上，很多安全漏洞都来源于程序员的粗心编码，智能合约这种部署后即不可更改的更应加强代码审计。

#### 四、防护方案

1、0.4.22版本以后的solidity编译器引入了constructors关键字，以替代低版本的将合约名作为构造函数名的语法，从而避免程序员编码错误。强烈建议采用最新版本编译器。

![](https://images.seebug.org/content/images/2018/06/619b4663-7ace-4148-8821-65448221c4b9.png-w331s)
![](https://images.seebug.org/content/images/2018/06/4e35d514-2dab-42c4-a38c-c3e584cb8064.png-w331s)

2、技术业务咨询

知道创宇404区块链安全研究团队：<http://www.scanv.com/lca/index.html>  
联系电话：(086) 136 8133 5016（沈经理，工作日:10:00-18:00）

欢迎扫码咨询：
![](https://images.seebug.org/content/images/2018/06/95677dc3-cb3e-474e-832e-8b79ec73bfa9.png-w331s)

#### 五、相关链接

[1] Morpheus 官网  
<https://morpheus.network/>  
[2] 官方公告  
<https://medium.com/@themorpheus/new-morpheus-network-token-smart-contract-91b80dbc7655>  
[3] 以太坊主链智能合约  
<https://etherscan.io/contractsVerified>  
[4] 合约构造函数缺失漏洞示例  
<https://github.com/trailofbits/not-so-smart-contracts/blob/master/missing_constructor/Missing.sol>  
[5] 漏洞详情参考  
[https://bcsec.org/index/detail?id=157&tag=1](https://bcsec.org/index/detail?id=157&tag=1)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/630/>

