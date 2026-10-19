# Flurry Finance 攻击事件分析

阅读量 **157849**

|评论 **1**

发布时间 : 2022-03-31 10:30:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t016553adbc5146eaae.png)

## 0x1 事件背景

Flurry 协议使用 rhoToken 自动化了收益耕作过程，使用户免去了在不同链上切换 DeFi 产品以通过存款产生收益的所有繁琐任务。作为回报，将获得
rhotokens（rhoUSDC、rhoUSDT、rhoBUSD），可以将其作为交换媒介进行持有、交易和消费， 同时自动赚取利息。

零时科技区块链安全情报平台监控到消息，北京时间 2022 年 2 月 23 日，Flurry Finance
称遭到黑客攻击，零时科技安全团队及时对此安全事件进行分析。

![](https://p2.ssl.qhimg.com/t01d918745cd1a0ddce.jpg)

## 0x2 攻击者信息

零时科技安全团队通过初步追踪分析，此次攻击发生在 Binance Smart Chain 链，主要攻击信息如下:

**攻击者钱包地址:**

-0x2A1F4cB6746C259943f7A01a55d38CCBb4629B8E

-0x0F3C0c6277BA049B6c3f4F3e71d677b923298B35

**攻击者创建的相关合约地址:**

• 0xB7A740d67C78bbb81741eA588Db99fBB1c22dFb7

**攻击交易流程：**

-0x969002ea247f3f242ccfb64fecd3bd70b23e443e411e2a65c786e585aef8544c

-0xe737e1e9cd2ee2c535d1304883e958ed2f7b4b8d9c10c0aec12acbf888665789

-0x646890dd8569f6a5728e637e0a5704b9ce8b5251e0c486df3c8d52005bec52df

**官方漏洞合约:**

_-StrategyLiquidate:_ 0x5085c49828B0B8e69bAe99d96a8e0FCf0A033369

_-FlurryRebaseUpkeep:_ 0x10f2c0d32803c03fc5d792ad3c19e17cd72ad68b

_-Vault:_

0xeC7FA7A14887C9Cac12f9a16256C50C15DaDa5C4

## 0x3 攻击分析

先来看看攻击者获利的一组交易操作：

步骤1: 在 PancakeSwap
上创建流动资金池：<https://bscscan.com/tx/0xb6e1e0f1bfccbc332a195f4974989bc9d1a00fe3f9b0ccd4ebabe885383e6fa4#eventlog>

![](https://p3.ssl.qhimg.com/t014580605b0a7220f3.png)

如上述日志所示：黑客创建了 Exploiter2-BUSD 令牌对。

步骤2: 攻击者从 Rabbit Bank 合约闪贷并触发了 StrategyLiquidate 的 execute 方法。execute
方法将输入数据解码为 LP 代币地址，攻击者能够执行恶意代币合约中实现的代码。

![](https://p1.ssl.qhimg.com/t012158757251bb900a.png)

恶意代币合约调用了 FlurryRebaseUpkeep.performUpkeep() 方法，重新设置了所有 vault 并更新了 rhoTokens
的乘数。(更新基于所有策略的余额)

![](https://p3.ssl.qhimg.com/t012fceab43ca75f988.jpg)

![](https://p3.ssl.qhimg.com/t018f1a93283e836d66.jpg)

更新是在闪贷过程中触发的，从银行合约借来的代币还没有归还，余额低导致乘数低。

![](https://p3.ssl.qhimg.com/t0171d7bb1d9c4b5981.png)

步骤3: 发币到 EOA 地址，并将 EOA 切换到合约地址来操纵 rhoToken
数量：<https://bscscan.com/address/0x32e0c08617e84b9568541db969b79cefd6ef2e44#tokentxns>

![](https://p0.ssl.qhimg.com/t01e2ac444e58334969.png)

至此，攻击者利用此攻击流程，通过对官方 StrategyLiquidate、FlurryRebaseUpkeep 和 Vault 合约进行了 9
次攻击共获利约二十五万美元。

## 0x4 总结

通过此次攻击事件来看，攻击成功最重要的因素是 Flurry Finance 官方的 StrategyLiquidate、FlurryRebaseUpkeep
和 Vault 合约中：没有对利息的乘数做监控，没有为 rebase 做安全层的效验，也没有任何机制防止 EOA
地址转换为合约地址。攻击者可以通过提取流动性，操纵计算利息的乘数铸币并发送到账户地址，并将账户地址转换为合约地址使乘数失效对项目造成威胁。对于此类安全事件，零时科技安全团队给出下述安全建议。

## 0x5 安全建议

  * 建立监控系统，监控利息计算乘数上的任何异常活动。
  * 在敏感操作前，增加额外的安全层来增强函数调用的授权权限。
  * 实施新机制，防止人为操纵将 EOA 地址转换为合约地址。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/271195](/post/id/271195)

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

