# 天价美元损失案Harmony事件分析

阅读量 **124348**

发布时间 : 2022-06-29 14:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t010d502ab2685bf3a3.jpg)

## 0x1 事件背景

零时科技区块链安全情报平台监控到消息，北京时间
2022年6月24日由Layer1公链Harmony开发的以太坊与Harmony间的资产跨链桥Horizon遭到攻击，损失金额约为1亿美元。零时科技安全团队及时对此安全事件进行分析。

## 0x2 攻击者信息

  * **攻击者钱包**

0x0d043128146654C7683Fbf30ac98D7B2285DeD00

0x9E91ae672E7f7330Fc6B9bAb9C259BD94Cd08715

0x58f4baccb411acef70a5f6dd174af7854fc48fa9

  * **MultiSigWallet**

0x715cdda5e9ad30a0ced14940f9997ee611496de6

  * **EthManager**

0xF9Fb1c508Ff49F78b60d3A96dea99Fa5d7F3A8A6

  * **ERC20EthManager**

0x2dccdb493827e15a5dc8f8b72147e6c4a5620857

## 0x3 攻击分析

攻击者获取 13,100 枚 ETH 和 5,000 枚 BNB 的合约调用相同，本篇主要分析这两笔交易。

两笔交易分别为

<https://etherscan.io/tx/0x27981c7289c372e601c9475e5b5466310be18ed10b59d1ac840145f6e7804c97>

<https://bscscan.com/tx/0xa72c7262340c25b9258b33dcad089cb3473ed048d1f808f436a96b8ed577cdb1>

**以上交易调用流程如下：**

**第一步：**

**0xf845a7ee8477ad1fb4446651e548901a2635a915 地址调用 MultiSigWallet 合约中
addTransaction 方法在交易映射中添加一笔新的交易。**

![](https://p0.ssl.qhimg.com/t01d857c151df700720.png)

![](https://p2.ssl.qhimg.com/t01e94e692e02286633.png)

**第二步：**

**0x812d8622c6f3c45959439e7ede3c580da06f8f25 地址调用 MultiSigWallet 合约中
confirmTransaction 方法传入映射的交易id。**

![](https://p0.ssl.qhimg.com/t01228366a88b9b11b6.png)

**注：confirmTransaction 只能由钱包管理员调用，通过分析，该管理员正是部署合约时已经确定的管理员地址。如下部署合约交易：**

![](https://p5.ssl.qhimg.com/t013cddcb82457693c0.png)

可以明确以上两个步骤操作均为管理员调用。

**第三步：**

**第二步中方法内部会最终调用 executeTransaction 方法，之后调用 isConfirmed 方法做判断。**

![](https://p5.ssl.qhimg.com/t012ec509873cadcd2b.png)

**isConfirmed 方法中判断事件是否通过是根据该值，需要两个管理员就可以成功执行。**

![](https://p5.ssl.qhimg.com/t01f5a27e37e60c70b0.png)

**通过方法内部调用 EthManager 合约 unlockEth 方法，最终将 ETH/BNB 资金发送至攻击者钱包。**

![](https://p2.ssl.qhimg.com/t018833bbb3cad4caab.png)

## 0x5 资金流向

攻击者在ETH链盗取的代币信息：

    
    
    13,100     Ether
    41,200,000 USDC
    592        WBTC
    9,981,000  USDT
    6,070,000  DAI
    5,530,000  BUSD
    84,620,000 AAG
    110,000    FXS
    415,000    SUSHI
    990        AAVE
    43         WETH
    5,620,000  FRAX
    

**攻击者通过一系列的兑换交易将获得到的一部分 Erc20 Token 兑换为 Ether。**

![](https://p1.ssl.qhimg.com/t013ffa2c930bc4e53e.png)

攻击者在 BSC 链盗取的代币信息：

    
    
    5,000   BNB
    640,000 BUSD
    

攻击者在两条链中总获利1亿美金。

## 0x6 总结

通过上述事件来看，攻击手法是控制多签合约中钱包私钥，由于转移资金只需要两个地址同意，所以当攻击者控制这两个地址钱包私钥，在跨链中同意了攻击者转移资金的交易，就会造成资金被盗。
**对于此类安全事件，我们给出以下安全建议：**

  * **建议增加资金转移时的多签地址数目，避免少量地址私钥被控制就可转移资金；**
  * **建议对多签地址私钥安全存储，避免将私钥存储在云端或者容易受攻击的服务器。**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/275387](/post/id/275387)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [区块链](/tag/区块链)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t01482eaf8414a7973c.png) 零时科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

