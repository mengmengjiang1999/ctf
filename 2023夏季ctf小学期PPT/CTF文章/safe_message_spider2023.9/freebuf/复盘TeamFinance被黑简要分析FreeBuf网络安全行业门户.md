By: Victory!

据慢雾区消息，2022 年 10 月 27 日 Team Finance 平台遭受攻击，损失价值约 1450
万美元的代币。慢雾安全团队现将简要复盘分析分享如下。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293578_6360e18aaf0e4ca30804b.jpg!small)

##  **相关信息**

攻击交易

0xb2e3ea72d353da43a2ac9a8f1670fd16463ab370e563b9b5b26119b2601277ce

攻击者地址

0x161cebB807Ac181d5303A4cCec2FC580CC5899Fd

攻击者部署的攻击合约地址

0xCFF07C4e6aa9E2fEc04DAaF5f41d1b10f3adAdF4

##  **攻击核心点**

合约并未对迁移的 token 和锁定的 token 进行一致性检查，并且在迁移的逻辑中会退还迁移剩余的代币，导致攻击者可以通过锁定一个任意 token
对合约中不属于攻击者的 LPtoken 进行迁移。

##  **攻击分析**

1、攻击者先通过交易 0xe8f17ee00906cd0cfb61671937f11bd3d26cdc47c1534fedc43163a7e89edc6f
构造了 4 个假 token 的 lockedToken 数据。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293582_6360e18eb4ecb2129ee65.jpg!small)

2、攻击者延长 lockedToken 的锁定时间。至此攻击者的准备工作已经完成，这些准备工作主要是为了绕过 migrate 的限制判断。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293607_6360e1a7d90e1356a5871.jpg!small)

3、攻击者通过攻击合约调用 Pool 的 migrate 函数。从传入的参数可以看出攻击者操作迁移的 token 与攻击者锁定的 token
并不一致，这是导致该合约被攻击的根本原因。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293611_6360e1ab809e517678155.jpg!small)

4、通过分析参数可以发现传入的 pair 与 token0 和 token1 并不匹配，并且由于传入的 noLiquidity 为 true，所以在
v3Migrator.createAndInitializePoolIfNecessary 的调用中还会创建一个假 token 对 WETH 的 V3
Pool。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293623_6360e1b77bd411d651998.jpg!small)

5、新创建的合约 Pool 价格 sqrtPriceX96 虽然由外部传入，但在此次攻击中并不是关键原因。此次攻击最重要的获利点是
v3Migrator.migrate(params) 的调用，此函数的作用是进行 Uni V2 往 Uni V3 迁移的逻辑。逻辑如下图所示：

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20200701/1593550745.png!small)

6、在 v3Migrator.migrate(params) 中会 burn 掉 V2 的 LP，根据迁移的比例往 V3
的池子继续添加流动性剩余的部分转回去给迁移者，攻击者传入的迁移比例是 1，所以在迁移完成后还剩余 99% 的 WETH 和 100%
FEG（因为添加流动性的是假 token 和 WETH），在之后的逻辑会把迁移剩下的代币转回去给执行迁移的用户。所以攻击者通过迁移不属于他的 LP
获得了非法收益。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293646_6360e1cecbc467e48b3f0.jpg!small)

7、在第二次攻击中，虽然从调用迁移的参数看出这次传入的 token0 跟 token1 与 Pair
是一致的，但由于此合约被攻击的根本原因是迁移函数中攻击者可以通过锁定任意 token 对合约中存有的 LP 进行迁移。虽然传入的 token 与 pair
参数是一致的，但攻击者还是同样通过 v3Migrator.migrate(params) 的调用，burn 掉了不属于他的 USDC-CAW 的
LPToken，并且在设置迁移的数量只有 1%，攻击者获得了迁移剩余的代币。

![复盘 | Team Finance
被黑简要分析](https://image.3001.net/images/20221101/1667293731_6360e223a66c323ba33e5.jpg!small)

8、最后，攻击者利用同样的手法将 USDC-TSUKA，WETH-KNDX 的 LP 套走获利离场。

#  **总结**

截止本文发布时，Team Finance 白帽黑客地址已返还 1340 万美元数字资产。

本次攻击事件最根本的原因是由于迁移函数并未对用户锁仓的 token 与迁移操作的 token 进行判断，导致只要任意锁仓一个 token
就可以对合约中存有的 LP
进行一个迁移操作并且迁移的数量还是由外部指定的。慢雾安全团队建议对于任何由外部传入的参数都需要做严格的检查，确保用户只能对自己资产进行操作。

