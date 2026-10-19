差分隐私（Differential
Privacy，DP）是密码学中的一种手段，可以提高从统计数据库进行数据查询的准确性，同时帮助最大限度减少识别其具体记录的机会。DP
一般分为：CDP（Centralized Differential Privacy）、LDP（Local Differential Privacy）。

# 一、CDP

## 1.1 基本定义

![996b702b18990aca4186d62b24a37d46.png](https://image.3001.net/images/20230612/1686533572_648675c437a8f7267e57b.png!small)

 **保护效果：查询者无法判断特定样本是否在一个数据集当中。**

## 1.2 应用举例

![14fa77a87782053c77ee29dfc4969547.png](https://image.3001.net/images/20230612/1686533573_648675c57e0265a8578cf.png!small)

## 1.3 全局敏感度

![76ad152377688392112ea0fcaa6f98e1.png](https://image.3001.net/images/20230612/1686533574_648675c682c4229d52397.png!small)

## 1.4 数据裁剪

COUNT 函数的 GS 始终为 1，但是 SUM 函数的 GS 就不好说了，因为这要看 SUM 作用于哪个属性列，如：年龄和收入应用 SUM
就有很大差异。如 1.2 所述，我们应用 Laplace 扰动机制时需要 f(x)（此处为 SUM）的有界全局敏感度，但 SUM
显然不容易做到，因此需要对待处理的列进行裁剪处理，以得到 f(x)的有界全局敏感度。有两点需要特别注意：

• 在裁剪造成的信息损失与满足差分隐私所需要的噪声间进行 trade off，一般裁剪后要尽可能保留 100%的信息。

• 不能通过查看数据集来确定裁剪边界，这可能会泄露信息，同时也不满足差分隐私的定义。

那我们应该如何对属性列进行裁剪动作，一般有如下两个做法：

• 根据数据集先天满足的一些性质来确定裁剪办界。如人的年龄一般在 0~125 岁之间。

• 采用差分隐私问询估计选择的边界是否合理。先通过数据变换把属性列映射为非负值，然后将裁剪下界置 0，逐渐增加上界，直至问询输出不变。

![fc2eef31cfd7cafa256b5f9b6b2cb02d.png](https://image.3001.net/images/20230612/1686533575_648675c756f03187a28f3.png!small)

## 1.5 向量值函数及其敏感度

![23d4480c2e75fc2488e53eec39f85334.png](https://image.3001.net/images/20230612/1686533576_648675c8629d71a58acbb.png!small)

## 1.6 Laplace 机制

![d84deea1d5a4dfd759b6ca96a0125c90.png](https://image.3001.net/images/20230612/1686533577_648675c9809d48b17f0c7.png!small)

## 1.7 Gaussian 机制

![d2439553686d498f49242af17434f2e5.png](https://image.3001.net/images/20230612/1686533578_648675ca766615ef93ede.png!small)

## 1.8 Laplace vs Gaussian

向量值 Laplace 机制需要使用 L1 敏感度，而向量值 Gaussian 机制 L1 和 L2 敏感度都可以使用。在 L2 敏感度远低于 L1
敏感度的场景下，Gaussian 机制添加的噪声要小得多。向量值 Laplace 和 Gaussian 的发布规则为：

![2a7454b99dcdf715a1f9e4a1c47c39f8.png](https://image.3001.net/images/20230612/1686533579_648675cb564ee38530962.png!small)

## 1.9 指数机制

前述 Laplace 和 Gaussian
机制的回复都是数值型的，只需要直接在回复的数值结果上添加噪声即可。如果我们想从一个备选回复集合中选出最佳结果，同时又保证回复过程满足差分隐私，那应该怎么办呢？
**一种可行的方法是使用指数机制。**
首先，定义一个备选回复集合；然后，再定义评分函数，评分函数输出备选集合中每个回复的分数；分数最高的回复就是最大回复。指数机制通过返回分数近似最大的回复来实现差分隐私保护。

![b8c9a4f170a56e572be6d475a2d81fa1.png](https://image.3001.net/images/20230612/1686533580_648675cc608129f9812f1.png!small)

 **报告噪声最大值**

![0bced5ac07ce691fea77df5434b4ce65.png](https://image.3001.net/images/20230612/1686533582_648675ce593050c5a292b.png!small)

## 1.10 组合性与后处理性

![8b51934171b2a4f8c815e542ce9b8d9d.png](https://image.3001.net/images/20230612/1686533583_648675cfeee0ab8d4a9e1.png!small)

# 二、LDP

## 2.1 LDP 基本定义

![833b0c77757dd0ae454cbd23afa3c0dd.png](https://image.3001.net/images/20230612/1686533585_648675d13548c1175605c.png!small)

## 2.2 LDP 经典算法

![47d1355b4f5f32c922fbcfc2c1fee862.png](https://image.3001.net/images/20230612/1686533586_648675d2687c15ed16b86.png!small)

## 2.3 LDP 举例-随机应答

有 n 个用户，假设 X 病患者的真实比例为Π﻿，我们希望对这个比例进行统计。于是我们发起一个敏感问题：“你是否为 X 病患者？”，每个用户的答案是 yes
or no。出于隐私性考虑，用户可能不会给出正确答案[5]。

我们可以对每位用户的回答加一些数据扰动。比如：用户正确回答的概率为
p，错误回答概率为(1-p)。这样就不会准确知道每位用户的真实答案，相当于保护了用户隐私。按此规则我们统计回答 yes 与 no 的用户占比。

![f71d4ea0a6157b210da77e1baae31075.png](https://image.3001.net/images/20230612/1686533587_648675d360f59fd66502a.png!small)

DP 在机器学习领域的应用、基于 Gaussian 机制实现 LDP 的原理请听下回分享。

# 参考资料

1.Balle B, Wang Y X. Improving the gaussian mechanism for differential
privacy: Analytical calibration and optimal denoising[C]//International
Conference on Machine Learning. PMLR, 2018: 394-403.

2\. [https://programming-dp.com/](https://xie.infoq.cn/link?target=https%3A%2F%2Fprogramming-dp.com%2F)

3.Cynthia Dwork, Aaron Roth, and others. The algorithmic foundations of
differential privacy. Foundations and Trends® in Theoretical Computer Science,
9(3–4):211–407, 2014.

4.Xiong X, Liu S, Li D, et al. A comprehensive survey on local differential
privacy[J]. Security and Communication Networks, 2020, 2020: 1-29.

5.LDP 随机响应技术举例：
[https://zhuanlan.zhihu.com/p/472032115](https://xie.infoq.cn/link?target=https%3A%2F%2Fzhuanlan.zhihu.com%2Fp%2F472032115)

作者：京东科技 李杰

内容来源：京东云开发者社区

