2022 年 03 月 16 日，据慢雾区消息，Hundred Finance 存在严重漏洞遭到攻击，黑客获利约 2,363
ETH，慢雾安全团队第一时间介入分析，并将结果分享如下：

##  **相关信息**

Hundred Finance 是一个去中心化应用程序（DApp），它支持加密货币的借贷。它是一种多链协议，与 Chainlink
预言机集成，以确保市场健康和稳定，同时专门为长尾资产提供市场。

以下是本次攻击涉及的相关地址：

攻击者地址：

<https://blockscout.com/xdai/mainnet/address/0xD041Ad9aaE5Cf96b21c3ffcB303a0Cb80779E358>

攻击交易：

<https://blockscout.com/xdai/mainnet/tx/0x534b84f657883ddc1b66a314e8b392feb35024afdec61dfe8e7c510cfac1a098>

攻击者合约：

<https://blockscout.com/xdai/mainnet/address/0xdbf225e3d626ec31f502d435b0f72d82b08e1bdd>

<https://blockscout.com/xdai/mainnet/address/0xbE8fe2aE087aeCcB1E46EF206368421c9212637B>

<https://blockscout.com/xdai/mainnet/address/0x09b4f2551e9f39fa021a99463e21d6044656a7b9>

<https://blockscout.com/xdai/mainnet/address/0xf07ac43678b408ff0c86efff99b8d21af3d38c51>

<https://blockscout.com/xdai/mainnet/address/0x9c4e6edbc45b16e4378b53cd3e261727e103f633>

被攻击合约：

[https://blockscout.com/xdai/mainnet/address/0x243E33aa7f6787154a8E59d3C27a66db3F8818ee
husdc](https://blockscout.com/xdai/mainnet/address/0x243E33aa7f6787154a8E59d3C27a66db3F8818ee%20husdc)

[https://blockscout.com/xdai/mainnet/address/0xe4e43864ea18d5e5211352a4b810383460ab7fcc
hwbtc](https://blockscout.com/xdai/mainnet/address/0xe4e43864ea18d5e5211352a4b810383460ab7fcc%20hwbtc)

[https://blockscout.com/xdai/mainnet/address/0x8e15a22853a0a60a0fbb0d875055a8e66cff0235
heth](https://blockscout.com/xdai/mainnet/address/0x8e15a22853a0a60a0fbb0d875055a8e66cff0235%20heth)

[https://blockscout.com/xdai/mainnet/address/0x090a00a2de0ea83def700b5e216f87a5d4f394fe
hxdai](https://blockscout.com/xdai/mainnet/address/0x090a00a2de0ea83def700b5e216f87a5d4f394fe%20hxdai)

##  **攻击核心点**

在 Hundred Finance 借贷协议的 borrowFresh 函数中，记账是在代币转账之后，但市场中 USDC、wBTC、wETH 使用的是
ERC677 类型 token 合约，它是 ERC20 合约的一个扩展，兼容 ERC20 协议标准。ERC677 在 token
进行转账之后，会回调到目标合约的 onTokenTransfer 方法，这就使攻击者构造的恶意合约能进行重入攻击。

##  **具体细节分析**

1\. 通过 SushiSwap 闪电贷借出 2,096,607.298 USDC、1,723,293.26 wXDAI、1,650,170.47
wXDAI。

![分析](https://image.3001.net/images/20220316/1647440237_6231f16d5b44c699fbf38.jpg!small)

2\. 攻击者通过攻击合约向 USDC 借贷合约抵押 1,200,000 枚 USDC，换取 59,999,789.075 枚 hUSDC。

![分析](https://image.3001.net/images/20220316/1647440237_6231f16da89a3ee4f71f2.jpg!small)

随后通过借贷合约借走 1,200,000 枚 USDC，但是由于借贷合约记账是在转账之后，因此攻击者能在转账的时候同时开始他的攻击。

![分析](https://image.3001.net/images/20220316/1647440238_6231f16e3aa2b448feefa.jpg!small)

因为 XDai 链上的 USDC、WBTC、WETH 是有转账后回调步骤，攻击者在转完 USDC 之后再次重入到 WBTC 的借贷合约。同时因为上一步借走
USDC 的数据还未记录，所以攻击者又顺利的借走 16.17030715 枚 WBTC， 此后再次重入到 WETH 的借贷合约，借走
24.715930916595319168 枚 WETH。

![分析](https://image.3001.net/images/20220316/1647440238_6231f16e9e3739ea4737e.jpg!small)

3\. 接着，攻击者继续往 USDC 借贷合约转入 1,964,607 枚 USDC，拿到 98,230,019.558 枚 hUSDC，然后从池子里面借出
1,748,500.495 枚 USDC，再重入到 xDai 的借贷合约；

随后，攻击者转入大量的 xDai 换出 234,304,737.048 枚 hxDAI，再借出大量的 xDai，再从 USDC 借贷合约借出
4,128,044.631 枚 USDC 之后，攻击者再一次往 USDC 借贷合约转入 1,358,759.278 枚 USDC，又获得
67,937,725.081枚 hUSDC，接着，继续从 USDC 的借贷合约借出 1,209,295.758 枚 USDC。

![分析](https://image.3001.net/images/20220316/1647440239_6231f16f079e15aa2979a.jpg!small)

4\. 最后攻击者归还从 SushiSwap 借出来的 xDai 和 USDC，剩余的非法获利转到攻击者账户上。

![分析](https://image.3001.net/images/20220316/1647440239_6231f16fc42da86650c93.jpg!small)

##  **MistTrack**

据慢雾 AML 分析，黑客地址将资金从 XDai 跨链到以太坊后，将代币均兑换为 ETH，且在以太坊上的黑客地址初始资金来源于 Tornado.Cash。

![分析](https://image.3001.net/images/20220316/1647440240_6231f1703d47ddd8c88ef.jpg!small)

最后将获利的 2,363 ETH 分成 32 次转入 Tornado.Cash，以躲避追踪。

![分析](https://image.3001.net/images/20220316/1647440240_6231f1709b8e77cc29236.jpg!small)

##  **总结**

本次攻击事件是由于在借贷合约中的 borrowFresh 函数没有在代币转账前进行记账并且使用的 token
是有回调机制造成的，进而导致攻击者可以在转账之后重入到其他借贷合约。 **建议使用非 ERC20 标准的 token
合约时，要注意兼容性，合约记账应在代币转账之前做好记录，遵循 Checks-Effects-Interactions 规则，避免再次出现此类安全问题。**

