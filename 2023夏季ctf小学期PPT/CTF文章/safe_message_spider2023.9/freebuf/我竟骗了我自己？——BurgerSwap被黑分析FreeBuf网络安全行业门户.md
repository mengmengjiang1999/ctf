![](https://image.3001.net/images/20210528/1622198033_60b0c711835812d88bb33.png!small)

据慢雾区消息， **2021 年 05 月 28 日， 币安智能链 (BSC) DeFi 项目 BurgerSwap 被黑，损失达 330 万美元。**
慢雾安全团队第一时间介入分析，并将结果分享如下：

##  **攻击细节分析**

BurgerSwap 是一个仿 Uniswap AMM 项目，但是和 Uniswap 架构有所区别。BurgerSwap 架构总体分成【Delegate
-> lpPlatForm -> Pair】。其中 Delegate 层管理了所有的 Pair 的信息，并负责创建 lpPlatForm 层。然后
lpPlatForm 层再往下创建对应的 Pair 合约。在整个架构中，lpPlatForm 层充当了 Uniswap 中 Router
的角色，负责将计算交易数据和要兑换的代币转发到 Pair 合约中，完成兑换。

![](https://image.3001.net/images/20210528/1622198068_60b0c73452628dd4820a0.jpg!small)

本次事件的根本正是出在这种架构的问题上。通过一步步分析攻击者的交易行为，我们来还原整个攻击过程的核心：

![](https://image.3001.net/images/20210528/1622198086_60b0c74671a73276dff33.jpg!small)

 **本次攻击开始于 Pancake 的闪电贷** ，攻击者从 Pancake 中借出了大量的 WBNB，然后将这些 WBNB 通过 BurgerSwap
兑换成 Burger 代币。在完成以上的操作后，攻击者使用自己控制的代币(攻击合约本身) 和 Burger 代币通过 Delegate
层创建了一个交易对并添加流动性，为后续攻击做准备。

![](https://image.3001.net/images/20210528/1622198101_60b0c75514ced354f0005.jpg!small)

在完成代币的创建和准备之后，攻击者立马通过 PaltForm 层的 swapExactTokensForTokens
函数发起了兑换，兑换路径为【攻击者自己控制的代币 -> Burger -> WBNB】

![](https://image.3001.net/images/20210528/1622198133_60b0c775ce416f632bf60.jpg!small)

接下来进行了最关键的一次操作。

由于先前攻击者在创建交易对的时候使用的是自己控制的代币，在代币兑换过程中， _innerTransferFrom
函数会调用攻击者控制的代币合约，于是攻击者可以 _innerTransferFrom 函数中重入 swapExactTokensForTokens
函数。为什么攻击者要这样做呢？

![](https://image.3001.net/images/20210528/1622198159_60b0c78fc28f7b2e040f1.jpg!small)

通过对 PlatForm 层的 swapExactTokensForTokens 函数进行代码分析，我们不难发现，合约在调用
_innerTransferFrom 函数时首先计算了用户的兑换数据，然后在 _innerTransferFrom
函数的操作后使用预先计算的数据来转发到底层进行真正的代币兑换。从这个函数层面来看，就算攻击者重入了 swapExactTokensForTokens
函数，底层调用的 swap 函数也是独立的，咋一看并没有什么问题，但是链上的一个行为引起了慢雾安全团队的注意：

![](https://image.3001.net/images/20210528/1622198172_60b0c79ca5c7acfc881cf.jpg!small)

我们惊讶地发现， **在重入的兑换过程中，兑换的数量竟然没有因为滑点的关系而导致兑换数量的减少。** 这究竟是什么原因呢？看来关键是底层的 Pair
合约的问题了。我们又进一步分析了底层调用的 Pair 合约，代码如下：

![](https://image.3001.net/images/20210528/1622198185_60b0c7a9be74b3c0de332.jpg!small)

通过分析 Pair 的代码，我们再次惊讶地发现在 swap 的过程中，合约竟然没有在兑换后根据恒定乘积公式检查兑换后的数值！！也就是说， **Pair
合约完全依赖了 PlatForm 层的数据进行兑换，导致了本次事件的发生。** 由于 Pair 层本身并不做恒定乘积的检查，在重入的过程中，PlatForm
层的兑换数据预先进行了计算，在 _innerTransferFrom 函数完成后，Pair 的更新数据也没有反映到 PlatForm
层中，导致重入交易中的兑换产生的滑点并不影响下一次的兑换，从而造成了损失。用图来看的话大概如下：

![](https://image.3001.net/images/20210528/1622198198_60b0c7b623a2231a1342d.jpg!small)

##  **总结**

 **本次攻击属于 BurgerSwap 架构上的问题，由于 Pair 层完全信任 PaltForm 层的数据，并没有自己再做一次检查，导致攻击的发生。最近
DeFi 安全事件频发，针对越来越密集的 DApp 攻击事件，慢雾安全团队建议 DApp
开发者在移植其他协议的代码时，需充分了解移植协议的架构，并充分考虑移植协议和自身项目的兼容性，且需通过专业安全审计机构的审计后才上线，防止资金损失情况的发生。**

攻击交易参考：

<https://bscscan.com/tx/0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333>

作者：yudan@慢雾安全团队

