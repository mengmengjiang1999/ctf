## **概要**

本月初，白帽安全研究员 Gerhard Wagner 在 Polygon 的 Plasma 桥中发现了一个严重的双花漏洞，并提交至 Immunefi
漏洞奖励平台。具体而言，用户可以将特定金额存入 Polygon 的 Plasma
桥，提取所有金额，然后再提交同样的提取交易（提交的次数最多是223次），每次都能收到之前存入的金额。就相当于存入100万美元，可以提取2.23亿美元。Plasma桥的
DepositManager 共持有8.5亿美元的资金，攻击者可以通过多次欺诈交易，耗尽所有的8.5亿美元。Immunefi平台将问题告知Polygon
区块链，后者在30分钟内证实漏洞存在并着手修复底层问题。评估风险后，Polygon
区块链向研究员发出200万美元的奖励，这是Polygon漏洞奖励计划设立的最高奖金。

## 什么是Plasma桥？

和以太坊、币安智能链和比特币一样，Polygon 也是领先的区块链。DeFi 的兴起使得很多资产都可以在这些链上创建并存在。但如何在各链之间转移 NFTs
或令牌？

这时就需要区块链桥了。区块链桥是连接两个独立区块链并使它们之间进行通信的方式。Polygon 通过 Plasma 和股份证明 (Proof of
Stake, PoS) 安全提供了一个无信任的双向交易渠道即Polygon 和以太坊之间的跨链桥。

Polygon 在文档中指出，“桥本质上是一系列合约，可以帮助资产从根链转移到子链。用于以太坊和Polygon 之间转移资产的桥主要有两个。”Polygon
提供的两种桥是Plasma 桥和PoS 桥。由于 Plasma桥具备退出机制，因而被认为更安全。

## Plasma 桥中的高级别资产流

![](https://image.3001.net/images/20211027/1635322736_61790b70c42c5ec651873.jpg!small)

1、用户将令牌存储在根链（以太坊）上的 Polygon 合约上。

2、以太坊确认令牌存储交易后，相应令牌将被铸造在 Polygon 链上。这些令牌做好了被用于 Polygon 网络的准备。

3、当用户准备从子链 (Polygon) 提取资金时，就可以通过Polygon 初始化进行提取。

3.1 需要通过一个检查点间隔（大概30分钟），验证自最近一个检查点以来的所有区块。

3.2 之后检查点被提交到根链合约。

4、EXIT NFT 令牌铸造的值是用户想要提取的值。

5、开始7天的资金提取等待期。

6、使用进程-退出程序， 一旦等待期结束，则用户可要求将资金收回自己的以太坊账户。

提取程序中包含一个漏洞。

## 提取

提取的流程始于子链的燃烧 (burning) 令牌。Polygon Plasma 客户端暴露 startWithdraw 方法，调用
getERC20TokenContract 的withdraw 函数。该函数 负责燃烧 (burn) 令牌。

确认燃烧后，用户可调用 erc20Predicate 合约的 startExitWithBurntTokens
函数，接着就是初始检查点（30分钟）。另外，需要将退出 payload传递给该函数。退出 payload 包含关于正从 L2 到L1
转移的资金的所有重要信息。

要继续进行退出，燃烧交易需要是成功且有效的。这里需要注意的一点是，只有当检查点和燃烧交易一起包含在根链之后才能调用退出，这一点很重要。用户应当调用
withdrawManager 合约的 processExits 函数并提交燃烧证明。

主要漏洞在于 Polygon 的 WithdrawManager 合约如何在之前的区块中验证燃烧交易的包含和唯一性。

## 漏洞分析

WithdrawManager.sol 实现 verifyInclusion() 函数。

![](https://image.3001.net/images/20211027/1635322756_61790b841ba1dfeaa9ce6.jpg!small)

该函数的目标是在检查点验证燃烧交易收据的包含性。它会检查收据和交易本身的默克尔证明 (Merkle Proof)。所有上述信息均包含在退出payload
内。

该退出证明的一个关键参数是默克尔证明为收据提供的branchMask。branchMask 是一个重要的安全保障，用于确保系统的安全性。这就是分支掩码
(branch mask) 为何必须是唯一的原因，因为它的作用是生成 “退出ID (Exit ID)“。需要持有的财产就是一次退出交易也就是一个
“退出ID”。但研究员发现事实并非如此。

该分支掩码是HP编码的，之后在 WithdrawManager.sol 内的 MerklePatriciaProof.verify 调用中解码。Verify
函数通过调用 _getNibbleArray 函数来解码已编码路径。除了在MerklePatriciaProof
中解码外，WithdrawManager.verifyInclusion 函数还将该路径解码为一个unit256。由于解码到 nibble
的数组忽略了某些值，而被忽略部分中的差异未遭unit256 解码拒绝，因此由MerklePatriciaProof 解码的同样值可能有很多解码是
unit256。该unit256解码用于避免重放；由于解码中存在差异，因此同样的证明可被重放。

我们可以深入研究MerklePatriciaProof 中的解码，查看为何一个语义值可能具有多个编码。由下可知，如果HP编码值的第一个nibble
是1或3，那么我们就可以解释第二个nibble。然而，如果第一个nibble
不是1或3，则整个第一个字节就被丢弃。除了解释第二个nibble的值外，我们发现解码同样路径的方法总共有14*16==224种。恶意人员可为同一个退出交易创建不同的退出id。

![](https://image.3001.net/images/20211027/1635322774_61790b961d9440011df03.png!small)

在这种情况下的利用步骤是什么？

1、通过 Plasma 桥在 Polygon 上存储大量 ETH/令牌。

2、确认 Polygon 上的资金后，开启 Withdrawal 进程。

3、等待7天期限，使退出合法。

4、重新提交退出payload，不过要修改分支掩码的第一个字节。

5、为HP编码的路径的第一个字节赋不同的值，再次提交相同的合法交易，共可提交223次。

6、 牟利

如上所述，该漏洞的影响非常大。在提交漏洞时，DepositManagerProxy 中共存在8.5亿美元的资金。那么Polygon
和研究员是如何进行修复的呢？

## 漏洞修复

事实证明，编码的分支掩码的第一个字节应该总是0x00。修复方法是检查所编码的分支掩码的第一个字节是否为0x00，而不是无视它为不正确的掩码。

修复方案的commit见：

https://github.com/maticnetwork/contracts/commit/283b8d2c1a9ff3dc88538820ffc4ea6a2459c040

WithdrawManager 的新实现见：

https://etherscan.io/address/0x4ef5123a30e4cfec02b3e2f5ce97f1328b29f7de#code

 **原文链接**

https://medium.com/immunefi/polygon-double-spend-bug-fix-postmortem-2m-bounty-5a1db09db7f1

 **本文由奇安信编译，不代表奇安信观点。转载请注明“转自奇安信代码卫士 https://codesafe.qianxin.com”。**

