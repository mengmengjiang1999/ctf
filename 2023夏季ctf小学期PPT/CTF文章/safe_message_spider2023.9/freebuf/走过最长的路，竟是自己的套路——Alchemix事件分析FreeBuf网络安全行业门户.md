By：yudan@慢雾安全团队

![](https://image.3001.net/images/20210618/1623984837_60cc0ac549c2acf7f8261.png!small)

据慢雾区消息， **2021 年 06 月 16 日，以太坊 DeFi 项目 Alchemix 的 alETH 合约疑似出现安全问题。** 17
日，Alchemix 发布了事故分析报告，慢雾安全团队迅速介入分析，并在官方分析报告的基础上梳理了本次事件的整个脉络和核心关键点，供大家参考。

##  **太长不看系列**

本次分析文章很长。这里先说结论，方便大家有个大概的理解。 **本次事故的主要原因在于 Alchemix 通过 transmuter 添加了 3次
vault，导致收益信息记录在了一个错误的元素上，而在调用 transmuter 的 harvest 函数时也没有传入正确的 index
值，导致通过错误的元素获取了错误的收益，将错误的 4300 ETH 的收益发送到 adapter 合约，帮助用户偿还了 alETH
的贷款，造成收益增多的问题，导致了悲剧。**

##  **核心分析——Round 1**

![](https://image.3001.net/images/20210618/1623984867_60cc0ae3a17b393f91d77.jpg!small)

根据官方发布的事故分析报告，本次事故的原因是官方的 alETH 的部署脚本意外地创建了额外的 vaults，导致 Alchemix 使用了 vaults
数组中错误的索引并计算出了错误的奖励，导致 transmuter
把所有的奖励用于偿还了用户的所有负债。我知道单单是这句简短的分析让人有点云里雾里，摸不着头脑，所以我们只能把目标放在官方给出的交易中，看看能不能找到真相。

根据官方给出的交易，通过 ethtx.info 分析工具进行分析，我们不难发现，这笔交易调用了 AlchemistEth 合约的 harvest
函数，并且传入了 _vaultId=0 这个参数，最后返回了 "4308144937764982868765" 和
"4308144937764982866415" 这两个值。

![](https://image.3001.net/images/20210618/1623984904_60cc0b08ad2c98c11e703.jpg!small)

为了更加了解 harvest
函数的作用，我们需要对整个函数进行分析：![](https://image.3001.net/images/20210618/1623984919_60cc0b171af866d069b7c.jpg!small)

不难发现，harvest 函数其实包含两个重要的操作，分别是收获奖励和将奖励分发给 transmuter 合约。其中 vault 是一个 library
库合约，其中的 harvest 逻辑实现如下：

![](https://image.3001.net/images/20210618/1623984935_60cc0b277eea45861a18c.jpg!small)

通过代码分析不难发现，vault 库合约的 harvest 函数其实是检查了外部的 adapter 的总的资金量，然后根据 adapter
中的资金量减去用户的充值数量计算出收益的部分。

这里我们可以将这个 adapter 理解为一个 **策略池** ，用于管理用户的资金和收益。然后我们回到用户一开始的 AlchemistEth 合约中的
harvest 函数,发现返回的 "4308144937764982868765" 和

"4308144937764982866415" 这两个值其实对应的就是 vault 库合约的 harvest 函数计算出的需要提现的代币数量和从
adapter (策略池) 中取回的代币的数量。由于这个 adapter 对应的收益代币是 WETH，精度为 18 位，那么
"4308144937764982866415" 这个数值换算过来就是 "4308.144937764982866415" 个 WETH。

也就是说，本次 harvest 操作，收益了超过 4300 个 ETH 的收益，然后这个收益在下一步中通过 _distributeToTransmuter
函数给到了 transmuter 合约进行分发，我们看下分发过程中的逻辑是怎样的：

![](https://image.3001.net/images/20210618/1623984980_60cc0b54ddb5023815fb4.jpg!small)

_distributeToTransmuter 函数的逻辑只有简单的 3 行，我们主要关注的是最后的外部调用 —— lowerHashMinted
函数。该函数所对应的 xtoken 在这里指的是 alETH 本身。因为 alETH 本身是用户通过借贷借出来的，所以 lowerHashMinted
这里的操作其实是使用 harvest 的收益将 alETH 总的贷出数量减少了，从而减少了每个用户的贷款。总结来说就是用 harvest 4300 ETH
的收益偿还用户的 alETH 贷款。

![](https://image.3001.net/images/20210618/1623985015_60cc0b776d0a8cb5909f3.jpg!small)

###  **打个小总结**

这里先总结下这个流程，就是 AlchemistEth 合约通过 harvest 函数，得到了 4300 ETH
的收益，并将这个收益分发出去了，用于偿还用户的 alETH 贷款，导致了我们看到的情况 —— 已经贷出 alETH
的用户在不需要还款的情况下就可以拿回他们质押的 ETH。那究竟是为什么，会有这 4300 ETH 的收益呢？这多出来的 4300 ETH
的收益是怎么来的？针对这个问题，我们开始下一轮的分析。

##  **核心分析——Round 2**

要了解为什么会多出来 4300 ETH，就必须了解 AlchemistEth 的资金存储过程。在 AlchemistEth 合约中，合约总的充值情况是使用
Vault library 库的 Data 结构体进行记录的，然后通过 flushActiveVault
函数更新对应的充值数量(totalDeposit)。

![](https://image.3001.net/images/20210618/1623985048_60cc0b988db5166ef4894.jpg!small)![](https://image.3001.net/images/20210618/1623985057_60cc0ba125365684bd03b.jpg!small)

然后 depositAll 函数会将充值的代币金额打到对应的 adapter(策略池) 中，那么在下一次 harvest 的时候，通过
adapter(策略池) 获取的 totalValue，就会是用户的本金加上策略池的收益。为了计算收益过程中的本金部分，我们对官方给出的交易进行
debug，发现本金仅为 9000 ETH，从 adapter 获取的收益加上本金共有 13000 ETH，也就是说 9000 ETH 的本金产生了
4300 ETH
的收益。![](https://image.3001.net/images/20210618/1623985083_60cc0bbbcfc576760063c.jpg!small)

但是，按照上面分析的逻辑，用户的本金是不会产生那么大的收益的，问题肯定是出在了 adapter 获取的 totalValue。也就是说 adapter
不止只有 AlchemistEth 充值代币，还存在其他的收益渠道。为了验证我们的想法， **慢雾安全团队** 分析了 adapter 的所有代币收入，果然
**发现了一笔异常的转入行为** ，并且金额也能刚好对上多出的 4300 ETH 的收益。也就是说，问题就在这里了。

![](https://image.3001.net/images/20210618/1623985097_60cc0bc98a1467b8300c2.jpg!small)

通过查看交易数据，发现这是一笔调用 harvest 操作的交易，调用的合约是 transmuter 合约：

![](https://image.3001.net/images/20210618/1623985143_60cc0bf719703be7d53d5.jpg!small)

也就是说，是这个 harvest 函数出问题了，harvest 函数的逻辑如下：

![](https://image.3001.net/images/20210618/1623985154_60cc0c02e7fddf8129ca4.jpg!small)

同样是调用了 vault 的 harvest 函数，熟悉的配方，熟悉的味道。我们再次进行 debug，发现一个惊人的事实 ——
**在进行收益的时候，vault 的 totalDeposit 竟然为 0** ，导致 4300 ETH 的收益直接分发给了 adapter，导致了
adapter 获取的 totalValue 错误了，多了 4300 个
ETH，原因就是在这里。![](https://image.3001.net/images/20210618/1623985173_60cc0c1532908705dd9c5.jpg!small)

到了这里，我们已经很接近真相了，剩下要解决的就是为什么 totalDeposit 会为 0？我们查询了transmuter 合约中能改变
totalDeposit 的地方，发现只有 _plantOrRecallExcessFunds 函数可以改变这个值，而这个函数上层调用的又是
distribute 函数。而 transmuter 合约的 distribute 函数是 AlchemistEth 合约在收益的时候进行调用的。也就是说
**本身的流程** 应该是：

1\. AlchemistEth 合约调用 harvest 进行收益

2\. AlchemistEth 合约调用 transmuter 合约的 distribute 函数记录收益情况，并把收益部分给 adapter

3\. adapter 收到了 transmuter 的收益，根据收益偿还用户的 alETH 的贷款

但是问题就出在了 _plantOrRecallExcessFunds 函数中。由于在记录充值信息的时候，用的是 _vaults.last() 来获取最新的
vault，所以其实充值信息叠加在了最后一个元素上。但是项目方调用了三次 setActiveVault 函数，所以其实充值信息是叠加到了 _vaults
数组的 3 号元素，也就是 index 为 2 的 vault 元素上。但是在 transmuter 合约在 harvest 的时候传入的 _vaultId
却是 0，0 号元素是没有任何充值记录的，所以 transmuter 合约就误将所有的收益都给了 adapter
了。导致了悲剧的发生。![](https://image.3001.net/images/20210618/1623985199_60cc0c2fc6d3c113500fd.jpg!small)![](https://image.3001.net/images/20210618/1623985213_60cc0c3d6703014807e9a.jpg!small)

##  **总结**

到这里，整个事情已经变得很清晰了，Alchemix 项目方由于某种原因，通过 transmuter 添加了 3 次
vault，导致收益信息记录在了一个错误的元素上，而在调用 transmuter 的 harvest 函数时也没有传入正确的 index
值，导致通过错误的元素获取了错误的收益，错误收益被发送到 adapter 合约，造成收益增多，导致了悲剧。

慢雾安全团队在此提醒，DeFi 是一个复杂的系统，在进行 DeFi
操作的时候，要记得检查好业务逻辑中的每一个流程，防止意外的发生，在必要的时候可以联系专业的安全团队进行专业的安全审计，防止事故的发生。

## 参考链接

> 官方事故分析报告：
>
> <https://forum.alchemix.fi/public/d/137-incident-report-06162021>
>
> 收益计算错误交易：
>
>
> <https://etherscan.io/tx/0x3cc071f9f40294bb250fc7b9aa6b2d7e6ca5707ce4d6d222157d7a0feef618b3>

