**作者：ACce1er4t0r@知道创宇404区块链安全研究团队  
时间：2020年7月22日 **

在7月15号，v2ex上突然出现了一个这样标题的帖子：[三行代码就赚走 4000w
RMB，还能这么玩？](https://s.v2ex.com/t/690286)

帖子内容里，攻击者仅仅只用了短短的几行代码，就成功的获利千万RMB，那么他是怎么做到的呢？

让我们来回顾一下这次事件。

### 事件回顾

2020年1月16日，开源项目`Ravencoin`接到这么一则`pull request`

![image.png](https://images.seebug.org/content/images/2020/07/23/1595472711000-1gdjji.png-w331s)

代码中，提交者将原本定义模糊的报错细分，让人们能够更直观的了解究竟出了什么错误，看起来是在优化项目，但是，事实真是这样么？

2020年6月29日，Solus Explorer开发团队一位程序员在修bug后同步数据时发现了一个`suspected transactions with
unbalanced
VOUTs`被Explorer标记出，之后他检查RVN时发现RVN大约被增发了约275,000,000，并发现了大量可疑地`reissue asset
Transaction`，这些交易不仅仅有`Asset
Amount`，而且获得了RVN。在他发现这一事件后，马上和他的团队一起将事件报告给`Ravencoin`团队。

2020年7月3日，`Ravencoin`团队向社区发布紧急更新

2020年7月4日，13:26:27 (UTC)，`Ravencoin`团队对区块强制更新了新协议，并确认总增发量为 301,804,400
RVN，即为3.01亿RVN.

2020年7月5月，`Ravencoin`团队宣布紧急事件结束

2020年7月8日，`Ravencoin`团队公布事件

![image.png](https://images.seebug.org/content/images/2020/07/23/1595472716000-2wtldd.png-w331s)

### 事件原理

在解释原理前，我们不妨先重新看看`WindowsCryptoDev`提交的代码

![
](https://images.seebug.org/content/images/2020/07/899b3a14-4e7d-4368-a96d-0e5349bb5727.png-w331s)

这是一段`Ravencoin`中用于验证的逻辑代码。

简单来说，提交者改变了`CheckTransaction`对Asset验证的判断，将原本`isAsset && txout.nValue !=
0`的条件更改为下面的条件：

  1. `isAsset && nType == TX_TRANSFER_ASSET && txout.nValue != 0`
  2. `isAsset && nType == TX_NEW_ASSET && txout.nValue != 0`

这段代码本身利用了开源社区PR的风格(在开源社区中，如果开发者发现提交的PR无关实际逻辑，则不会过度关注代码影响)，
**看似只是细化了交易过程中返回的报错，使得正常使用功能的交易者更容易定位到错误** ，实则，通过忽略`else`语句，导致一个通用的限制条件被细化到了
**nType的两种常见情况下** 。

而代码中`nTypt`可能的值有如下：

    
    
    enum txnouttype
    {
        TX_NONSTANDARD = 0,
        // 'standard' transaction types:
        TX_PUBKEY = 1,
        TX_PUBKEYHASH = 2,
        TX_SCRIPTHASH = 3,
        TX_MULTISIG = 4,
        TX_NULL_DATA = 5, //!< unspendable OP_RETURN script that carries data
        TX_WITNESS_V0_SCRIPTHASH = 6,
        TX_WITNESS_V0_KEYHASH = 7,
        /** RVN START */
        TX_NEW_ASSET = 8,
        TX_REISSUE_ASSET = 9,
        TX_TRANSFER_ASSET = 10,
        TX_RESTRICTED_ASSET_DATA = 11, //!< unspendable OP_RAVEN_ASSET script that carries data
        /** RVN END */
    };

由于代码的改变，当`nType == TX_REISSUE_ASSET`时，`txout.nValue`可以不为0。

通过对比正常的交易和存在问题的交易，我们也能验证这一观点。

![image.png](https://images.seebug.org/content/images/2020/07/23/1595472719000-3yqxnn.png-w331s)

在正常的Reissue操作中，我们需要向 Address
[RXReissueAssetXXXXXXXXXXXXXXVEFAWu](https://rvn.cryptoscope.io/address/?address=RXReissueAssetXXXXXXXXXXXXXXVEFAWu)支付`100RVN`，之后我们可以得到一个新的Amount为0的Address，如果新的Address的Amount不为0，那么将会返回`bad-txns-asset-tx-amount-isn't-zero`的错误信息（代码被更改前，修复后会返回`bad-txns-asset-reissued-amount-isn't-zero`的错误信息）

![image.png](https://images.seebug.org/content/images/2020/07/23/1595472729000-4ucfuj.png-w331s)

而攻击者修改了判断条件，导致了在`CheckTransaction`时并不会检测`TX_REISSUE_ASSET`，所以能够在Address的Amount不为0的情况下通过判断，最终实现增发RVN。

看完代码后，我们点开这位叫做`WindowsCryptoDev`的用户的GitHub主页

![
](https://images.seebug.org/content/images/2020/07/4e97e0f1-b1e9-441d-aa69-c483d2b36fcd.png-w331s)

这是个在2020年1月15日新建的账号，为了伪造身份，起了个`WindowsCryptoDev`的id，并且同天建了个叫`Windows`的repo，最后的活动便是在1月16号向`Ravencoin`提交PR。

而对于这个PR，项目团队的反馈也能印证我们的猜测。

![ ](https://images.seebug.org/content/images/2020/07/6e5dddc5-a9b9-4bff-ad5c-ae24e9199d3f.png-w331s)

* * *

整个攻击流程如下：

  1. 2020年1月15日，攻击者伪造身份
  2. 1月16日，攻击者提交pull request
  3. 1月16日，当天pull request被合并
  4. 5月9日，攻击者开始通过持续制造非法Reissue Asset操作增发RVN，并通过多个平台转卖换为其他虚拟货币
  5. 6月29日，`Solus Explorer`开发团队一位程序员发现问题并上报
  6. 7月3日，`Ravencoin`团队向社区发布紧急更新，攻击者停止增发RVN
  7. 7月4日，13:26:27 (UTC)，`Ravencoin`团队对区块强制更新了新协议
  8. 7月5月，`Ravencoin`团队宣布紧急事件结束
  9. 7月8日，`Ravencoin`团队公布事件

至此，事件结束，最终，攻击者增发了近3亿的RVN。

### 总结

随着互联网时代的发展，开源文化逐渐从小众文化慢慢走向人们的视野中，人们渐渐开始认为开源社区给项目带来源源不断的活力，开源使得人人都可以提交请求、人人都可以提出想法，可以一定层度上提高代码的质量、增加社区的活跃度，形成一种正反馈，这使开源社区活力无限。

但也因此，无数不怀好意的目光也随之投向了开源社区，或是因为攻击者蓄谋已久，抑或是因为贡献者无心之举，一些存在问题的代码被加入到开源项目中，他们有的直接被曝光被发现被修复，也有的甚至还隐藏在核心代码中深远着影响着各种依赖开源项目生存着的软件、硬件安全。

开源有利亦有弊，攻击者也在渗透着越来越多开发过程中的不同维度，在经历了这次事件之后，你还能随意的接受开源项目中的PR吗？

### REF

[1] 三行代码就赚走 4000w RMB，还能这么玩？

<https://s.v2ex.com/t/690286>

[2] commit

<https://github.com/RavenProject/Ravencoin/commit/d23f862a6afc17092ae31b67d96bc2738fe917d2>

[3] Solus Explorer - Address: Illegal Supply

<https://rvn.cryptoscope.io/address/?address=Illegal%20Supply>

[4] Ravencoin — Emergency Update

<https://medium.com/@tronblack/ravencoin-emergency-update-dece62255fd9>[/https://medium.com/@tronblack/ravencoin-emergency-update-dece62255fd9](mailto:/https://medium.com/@tronblack/ravencoin-emergency-update-dece62255fd9)

[5] Ravencoin — Emergency Ended

<https://medium.com/@tronblack/ravencoin-emergency-ended-3f3181a0f6d2>[/https://medium.com/@tronblack/ravencoin-emergency-ended-3f3181a0f6d2](mailto:/https://medium.com/@tronblack/ravencoin-emergency-ended-3f3181a0f6d2)

[6] The anatomy of Ravencoin exploit finding

<https://medium.com/@cryproscope/the-anatomy-of-ravencoin-exploit-finding-8fa4fe7547a9>[/https://medium.com/@cryproscope/the-anatomy-of-ravencoin-exploit-finding-8fa4fe7547a9](mailto:/https://medium.com/@cryproscope/the-anatomy-of-ravencoin-exploit-finding-8fa4fe7547a9)

[7] RavencoinVulnerability — WTF Happened?

<https://medium.com/@tronblack/ravencoin-post-vulnerability-fix-fb3a4bd70b7b>[/https://medium.com/@tronblack/ravencoin-post-vulnerability-fix-fb3a4bd70b7b](mailto:/https://medium.com/@tronblack/ravencoin-post-vulnerability-fix-fb3a4bd70b7b)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1275/>

