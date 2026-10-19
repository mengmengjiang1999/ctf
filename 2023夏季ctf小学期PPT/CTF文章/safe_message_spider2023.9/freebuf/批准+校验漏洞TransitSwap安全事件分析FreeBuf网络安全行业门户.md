# ****一、事件描述****

2022年10月2日，Transit Swap项目在Twitter上发布消息称项目遭受到黑客的攻击，被盗取了约2100万美元。

![1665140589_6340076db1546f88428f7.png!small](https://image.3001.net/images/20221007/1665140589_6340076db1546f88428f7.png!small)

SharkTeam对此事件进行了技术分析，并总结了安全防范手段，希望后续项目可以引以为戒，共筑区块链行业的安全防线。

#  ** **二、事件分析****

攻击者账户地址：

攻击发起地址：0x5f0b31aa37bce387a8b21554a8360c6b8698fbef，简记为0x5f0b

代币接收地址：0x75f2aba6a44580d7be2c4e42885d4a1917bffd46，简记为0x75f2

Ethereum攻击合约：0x17ff6c94ba3a49c72ef2f10782de8a6152f204ea，简记为0x17ff

Ethereum攻击交易如下：

![1665140599_63400777c1221aa9e30f1.png!small](https://image.3001.net/images/20221007/1665140599_63400777c1221aa9e30f1.png!small)

BSC攻击合约：0x8ca8fd9c7641849a14cbf72faf05c305b0c68a34，简记为0x8ca8

BSC攻击交易如下：

![1665140609_6340078153b8072ca73ae.png!small](https://image.3001.net/images/20221007/1665140609_6340078153b8072ca73ae.png!small)

我们以BSC上的第一笔攻击交易为例，对攻击进行分析。

TxHash：0xb25c24e787d750925bd80fd4bf2c0a24e3b18cc73f695b49470e41d913201567

![1665140628_634007944dd8fad4e2cd5.png!small](https://image.3001.net/images/20221007/1665140628_634007944dd8fad4e2cd5.png!small)

该交易包含了4笔转账，从4个账户中将不同数量的WBNB转入账户0x75f2中。从整个交易的详细过程中发现，每一笔转账的执行过程都包含了4部分，以第一笔转账为例：

![1665140634_6340079ab42f1371963bf.png!small](https://image.3001.net/images/20221007/1665140634_6340079ab42f1371963bf.png!small)

（1）调用allowance函数查询代币批准，如下：

![1665140825_63400859b8cca60ce621e.png!small](https://image.3001.net/images/20221007/1665140825_63400859b8cca60ce621e.png!small)

账户0xcfbc将所有的WBNB批准给了合约0xed1a。

（2）调用balanceOf函数查询余额，如下：

![1665140832_63400860cad28abd8ed1f.png!small](https://image.3001.net/images/20221007/1665140832_63400860cad28abd8ed1f.png!small)

账户0xcfbc的WBNB余额为18.7

（3）调用balanceOf函数查询余额，与（2）中的查询余额相同。

（4）访问合约0x8785bb8deae13783b24d7afe250d42ea7d7e9d72，简记为0x8785

![1665140843_6340086b6204a77601a76.png!small](https://image.3001.net/images/20221007/1665140843_6340086b6204a77601a76.png!small)

由合约0x8ca8调用合约0x8785中签名值为0x006de4df的函数

![1665140851_63400873c9414c1401d8b.png!small](https://image.3001.net/images/20221007/1665140851_63400873c9414c1401d8b.png!small)

然后，由合约0x8785调用合约0x0b47中签名值为0xd9c45357的函数。

![1665140860_6340087c21a4d7a161ed0.png!small](https://image.3001.net/images/20221007/1665140860_6340087c21a4d7a161ed0.png!small)

![1665140870_63400886000e8cd0a7212.png!small](https://image.3001.net/images/20221007/1665140870_63400886000e8cd0a7212.png!small)

进而，由合约0x0b47调用合约0xed1a中签名值为0x0a5ea466的函数，即claimTokens函数。

![1665140889_6340089930f16d103ebc4.png!small](https://image.3001.net/images/20221007/1665140889_6340089930f16d103ebc4.png!small)

其中，inputdata如下：

![1665140895_6340089fb9a40f7282110.png!small](https://image.3001.net/images/20221007/1665140895_6340089fb9a40f7282110.png!small)

最后，合约0xed1a中的claimTokens函数会调用WBNB合约中的transferFrom函数。

![1665140901_634008a55e9a87ff7f477.png!small](https://image.3001.net/images/20221007/1665140901_634008a55e9a87ff7f477.png!small)

将账户0xcfbc持有的所有的18.7WBNB转移给账户0x75f2，即攻击交易中第一笔转账。

通过以上过程，攻击者利用合约漏洞以及账户0xcfbc的批准，自定义inputdata，调用transferFrom函数将账户0xcfbc的所有WBNB转移到攻击者自己的账户中。

 **为什么** **攻击者** **可以转走用户批准的代币呢？**

整个攻击过程中，攻击合约访问了3个合约，即0x8785、0x0b47和0xed1a。我们知道，Solidity合约中的函数调用属于动态调用类型，可以通过传递的参数来指定访问的合约、调用的函数以及相关的参数。明显这3个合约缺少对访问的合约、调用的函数以及相关的参数这3个方面的校验，使得攻击者可以利用用户对合约的代币批转调用代币的转账函数（transferFrom）调用用户的代币。

#  ** **三、安全建议****

攻击者利用了合约校验漏洞将用户批准的代币转移到了自己的账户中。被攻击合约本身存在校验漏洞是此次攻击发生的根本原因，对于Solidity中的call函数，尤其是在实际业务应用中，建议根据实际业务限定调用的合约以及函数，推荐使用白名单机制。

其次，用户对合约的无限额代币的批准也是引发攻击的原因之一，若每一次批准都是限量的，至少可以保证未批准的代币是安全的。因此，建议项目在获取用户批准的时候可以定量批准，即使这种做法可能会影响一些用户体验。

对于用户来说，批准交易需要谨慎，尤其是全部批准的情况。

