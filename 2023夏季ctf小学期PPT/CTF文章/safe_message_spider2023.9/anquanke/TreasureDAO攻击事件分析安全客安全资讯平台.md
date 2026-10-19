# TreasureDAO攻击事件分析

阅读量 **117251**

发布时间 : 2022-03-08 14:30:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t016553adbc5146eaae.png)

## 0x1 事件背景

Treasure 通过一种开放和可组合的方法，为日益增长的元宇宙架起了桥梁，使NFTs、DeFi和游戏融合在一起。

零时科技区块链安全情报平台监控到消息，北京时间2022年3月3日，TreasureDAO遭到黑客攻击，超过百枚NFT
Token被盗，价值约140万美元，零时科技安全团队及时对此安全事件进行分析。

![](https://p0.ssl.qhimg.com/t01a53521315c4903b7.png)

## 0x2 攻击信息

零时科技安全团队通过追踪分析，主要攻击信息如下：

  * 攻击者钱包地址

_<https://arbiscan.io/address/0x9b1acd4336ebf7656f49224d14a892566fd48e68>_

  * 攻击者交易

_<https://arbiscan.io/tx/0xb169e20b45c6a5b7e5726c812af73c0b48996a4db04b076d6ef484ca5a300d36>_

  * 出现漏洞的官方合约地址

**TreasureMarketplaceBuyer**

_<https://arbiscan.io/address/0x812cda2181ed7c45a35a691e0c85e231d218e273#code>_

**TreasureMarketplace**

_<https://arbiscan.io/address/0x2e3b85f85628301a0bce300dee3a6b04195a15ee#code>_

## 0x3 攻击分析

先来看一下攻击者获利的交易操作：

![](https://p5.ssl.qhimg.com/t016e5e229a86b64c95.png)

从攻击交易可以明确，攻击者调用TreasureMarketplaceBuyer合约中buyItem方法获取了NFT，并且攻击者提供的购买资金为0，这里需要注意buyItem方法中第四个参数_quantity传参为0。

下面直接来看TreasureMarketplaceBuyer合约buyItem方法。

![](https://p1.ssl.qhimg.com/t01b80ae37389a62d85.png)

分析buyItem方法可以明确，这里的_quantity参数，也就是购买数量由用户输入，但是在37行计算时，价格和购买数量零相乘，会得到最终价格也为零，之后的用户给合约转账也是零。也就是说用户完成了零资金购买，下面继续分析攻击者如何将零资金购买的NFT提到自己账上，转移资金后，这里调用了marketplace合约中buyItem方法，继续跟进：

![](https://p4.ssl.qhimg.com/t01295f9996560accb4.png)

上图buyItem方法中两个判断条件，首先对该NFT的所有者进行了异同判断，之后对该NFT进行了数量判断，由于攻击者传参为零，所以这里很轻易的可以绕过判断，最终零成本购买NFT成功，攻击者通过此漏洞，多次调用buyItem方法零成本获取了大量NFT
Token。

目前Treasure发布公告称已冻结交易，同时攻击者也在归还NFT。

![](https://p2.ssl.qhimg.com/t016ecf6395143143bd.png)

## 0x4 总结

攻击者虽然通过合约进行零资金购买NFT，但随后又逐步在归还获取的NFT
Token。暂时不能确定是否为测试人员所为，希望用户及官方不会有太大的资金损失。通过此次攻击事件来看，攻击者抓住了对合约对零资金购买NFT的限制缺失，导致通过该漏洞获取大量NFT
Token，所以对于以上合约漏洞，零时科技安全团队给出以下建议。

## 0x5 安全建议

  * 建议合约应严格判断用户输入购买数量的合理性
  * 建议合约限制零资金购买NFT的可能性
  * 建议对于ERC721及ERC1155协议的NFT Token进行严格区分，避免混淆情况发生

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/269124](/post/id/269124)

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

