By：九九@慢雾安全团队

2022 年 03 月 13 日，据慢雾区消息，Paraluni 存在严重漏洞遭攻击，黑客获利约 170
万美元，慢雾安全团队第一时间介入分析，并将结果分享如下：

##  **相关信息**

Paraluni 是 BSC 链上的一个元宇宙金融（DeFi）项目。用户可以质押代币添加流动性获取收益。

以下是本次攻击涉及的相关地址：

攻击者地址：

<https://bscscan.com/address/0x94bc1d555e63eea23fe7fdbf937ef3f9ac5fcf8f>

攻击交易：

<https://bscscan.com/tx/0x70f367b9420ac2654a5223cc311c7f9c361736a39fd4e7dff9ed1b85bab7ad54>

攻击合约：

<https://bscscan.com/address/0x4770b5cb9d51ecb7ad5b14f0d4f2cee8e5563645>

UBT（ukraine bad token）代币合约：

<https://bscscan.com/address/0xca2ca459ec6e4f58ad88aeb7285d2e41747b9134>

UGT（russia good token）代币合约：

[https://bscscan.com/address/0xbc5db89ce5ab8035a71c6cd1cd0f0721ad28
8](https://bscscan.com/address/0xbc5db89ce5ab8035a71c6cd1cd0f0721ad28b508)

Masterchef 合约：

<https://bscscan.com/address/0xa386f30853a7eb7e6a25ec8389337a5c6973421d#code>

##  **攻击核心点**

在 MasterCheif 合约中的 depositByAddLiquidity 函数中，未校验传入的代币数组参数 _tokens 所构造的 LP
代币是否和指定的 _pid 参数对应和池子里的 LP 代币（USDT-BUSD
LP）是否一致，且在添加流动性计算时没有做重入限制，导致攻击者利用了恶意构造的代币合约进行了重入攻击。

##  **具体细节分析**

1\. 攻击者构造了改写了 transferFrom 函数的 ERC20 标准的 UBT 代币合约与另一个 ERC20 标准的 UGT 代币合约；

2\. 攻击者首先从 PancakeSwap 中闪电贷借出约 15.7 万枚 USDT 和 15.7 万枚 BUSD；

![分析](https://image.3001.net/images/20220313/1647177321_622dee697f3745d9b0443.jpg!small)

3\. 接着调用 ParaRouter 合约中的 addLiquidity 函数添加流动性，为所构造的 UBT 合约上 mint 约 15.5 万枚
Paraluni LPs 代币；

![分析](https://image.3001.net/images/20220313/1647177322_622dee6a1306a0f557c5c.jpg!small)

4\. 调用 MasterChef 合约中的 depositByAddLiquidity 函数，指定传入的 _pid 参数为 18，为该池子添加了 1 个
UBT 代币和 1 个 UGT 代币的流动性。该函数内部调用了 depositByAddLiquidityInternal 函数；

![分析](https://image.3001.net/images/20220313/1647177322_622dee6a98e288b77a12f.jpg!small)

在 depositByAddLiquidityInternal 函数中，会利用传入的 _tokens 代币通过调用 paraRouter 合约的
addLiquidity 函数去构造 LP 代币。而我们看到该函数没有校验 _pid 对应的池子代币（USDT-BUSD LP）和利用传入的 _tokens
所构造的 LP 代币是否相匹配；

![分析](https://image.3001.net/images/20220313/1647177323_622dee6b0747ece5d7888.jpg!small)

5\. depositByAddLiquidityInternal 函数又内部调用了 addLiquidityInternal 函数，而在
addLiquidityInternal 函数中，先获取合约地址中 LP 代币余额记录为 vars.oldBalance，接着调用了 paraRouter
合约的 addLiquidity 函数，然后再次获取合约地址中 LP 代币余额记录为 vars.newBalance，最后用 vars.newBalanc
- vars.oldBalance 计算需要 deposit 的数量，然后调用 _deposit 函数存入 LP 代币；

![分析](https://image.3001.net/images/20220313/1647177323_622dee6b7b18c2984a782.jpg!small)

而 paraRouter 合约的 addLiquidity 函数会调用攻击所构造的 UBT 代币合约中的 transferFrom
函数，该函数为攻击者恶意构造，会调用 deposit 函数转入 LP 代币记账到 UBT 合约中，而此时计算攻击合约 _deposit 的值时未能更新
vars.oldBalance 的值，造成了 UBT 代币合约与攻击合约均记账了 15.5 万枚的 LP 代币份额，形成了一次重入攻击；

6\. 攻击者分别调用 UBT 合约中的 withdrawAsset 函数和利用攻击合约调用 Mastechef 合约中的 withdraw 函数提取 LP
到攻击合约中；

![分析](https://image.3001.net/images/20220313/1647177324_622dee6c65cba3941ba0f.jpg!small)

7\. 攻击者移除流动性并总共得到了 31 万枚 USDT 和 31 万枚 BUSD，归还闪电贷后获利离场。

![分析](https://image.3001.net/images/20220313/1647177325_622dee6d4c588111cbc86.jpg!small)

##  **MistTrack**

据慢雾 AML 分析，黑客地址初始资金来源于从 Tornado.Cash 转入的 0.99785 BNB。

![分析](https://image.3001.net/images/20220313/1647177325_622dee6dd7ad6bda78f86.jpg!small)

在攻击获利后，黑客将部分 BNB 兑换为 ETH，并将 235.448 ETH 从 BSC 跨链到以太坊，同时将 230 ETH 分 5 笔转入
Tornado.Cash。

![分析](https://image.3001.net/images/20220313/1647177326_622dee6e3b2bc573b51c2.jpg!small)

截止目前，黑客在 BSC 上的地址余额为 3000.06 BNB，在以太坊上的地址余额为 5.243 ETH。慢雾 AML
将持续监控被盗资金的转移，拉黑攻击者控制的钱包地址。

在攻击发生后，Paraluni 项目方与黑客在链上发生了一系列对话：

Paraluni:

![分析](https://image.3001.net/images/20220313/1647177326_622dee6e8928a2d71c969.png!small)

黑客也很快给出了回复：

![分析](https://image.3001.net/images/20220313/1647177326_622dee6ed36276206fb12.jpg!small)

接着 Paraluni 项目方继续与黑客协商，如果黑客愿意退还部分资金，则作为白帽行为给予赏金：

![分析](https://image.3001.net/images/20220313/1647177327_622dee6f34b9028a7c9af.jpg!small)

而目前，黑客暂无回复。

##  **总结**

本次攻击事件是由于在 Mastechef 合约中的 depositByAddLiquidity 函数未对指定 _pid 对应的池子代币和传入的
_tokens 数组里的代币所构造的 LP 代币作一致性校验，并且在涉及流动性添加时未作重入锁的限制，导致了 LP
代币数量记账时被利用。慢雾安全团队建议在进行 deposit 存款等敏感操作时对指定 pid
对应的池子代币与所传入的代币做好一致性的判断，并且在添加流动性等涉及 LP 代币数量变动的函数需添加重入锁的限制，避免再次出现此类问题。

