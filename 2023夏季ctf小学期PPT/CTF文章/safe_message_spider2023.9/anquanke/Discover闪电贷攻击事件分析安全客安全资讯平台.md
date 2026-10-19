# Discover 闪电贷攻击事件分析

阅读量 **136239**

发布时间 : 2022-06-09 10:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t010d502ab2685bf3a3.jpg)

## 0x1 事件背景

零时科技区块链安全情报平台监控到消息，北京时间 2022年6月6日 Binance 链上 Discover
智能合约遭到闪电贷攻击。零时科技安全团队及时对此安全事件进行分析。

## 0x2 攻击者信息

  * 攻击者钱包：

0x446247bb10B77D1BCa4D4A396E014526D1ABA277

  * 攻击者合约：

0x06b912354b167848a4a608a56bc26c680dad3d79

0xfa9c2157cf3d8cbfd54f6bef7388fbcd7dc90bd6

  * 攻击交易：

0x8a33a1f8c7af372a9c81ede9e442114f0aabb537e5c3a22c0fd7231c4820f1e9

0x1dd4989052f69cd388f4dfbeb1690a3f3a323ebb73df816e5ef2466dc98fa4a4

  * ETHpledge合约：

0xe732a7bD6706CBD6834B300D7c56a8D2096723A7

## 0x3 攻击分析

**攻击者主要的攻击交易流程：**

![](https://p2.ssl.qhimg.com/t01a8fb9bfbe4287e05.png)

  1. 通过PancakeSwap闪电贷分别借款 2100枚 USD 和 19810 枚 USD。
  2. 将 2000 枚 USD 转移至 ETHpledge 合约0xe732a。ETHpledge 合约返回 62,536 枚 Discover。
  3. 将 19,810 枚 USD 归还闪电贷至 BSC-USD-Discover。
  4. 将 62,536 枚 Discover 换取USD，获得 16,336 枚 USD。
  5. 归还 2,100 枚 闪电贷借款，将剩余的 USD 兑换为 BNB，获利离场。

## 0x4 漏洞细节

ETHpledge.team

![](https://p3.ssl.qhimg.com/t0145d6e5895c07d131.png)

ETHpledge.pledgein方法作用是，调用者转入USDT资金后收到一定比例的Discover代币，这里转入USDT资金在pledgein方法执行，接收Discover代币的逻辑在ETHpledge.team方法实现，获取价格逻辑在ETHpledge.getprice方法实现。

**漏洞解析**

**攻击者调用ETHpledge.pledgein方法之前通过闪电贷借到大量USDT资金，使得 usdt.balanceOf
资金变少，之后调用ETHpledge.pledgein方法将少量USDT转入，随后调用ETHpledge.getprice方法获取价格，由于usdt.balanceOf
减少，所以_price变小，_swapprice变小，最终转账数量的curTamount变量增大。从而兑换的Discover代币数量增加。**

在兑换了大量Discover代币后，攻击者随后迅速归还了数量较多的一笔USDT闪电贷借款。随后使用Discover代币正常兑换出较多的USDT。

## 0x5 资金流向

目前黑客已将获利的 49 枚 BNB 转移至 Tornado.Cash混币平台。

![](https://p4.ssl.qhimg.com/t01d1e92f729d7ec0ff.png)

## 0x6 总结

此次攻击事件主要通过闪电贷资金控制价格，导致兑换数量波动，对于此类安全事件，建议不要使用外部可控的资金数量来获取价格，避免闪电贷攻击影响官方及用户资产，此外合约上线前应进行全面安全审计，将可能发生的安全风险规避掉。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **零时科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/274003](/post/id/274003)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [区块链](/tag/区块链)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01482eaf8414a7973c.png) 零时科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

