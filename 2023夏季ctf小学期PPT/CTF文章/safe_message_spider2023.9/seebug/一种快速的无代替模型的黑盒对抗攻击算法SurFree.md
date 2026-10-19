**作者：seven010@墨云科技VLab Team  
原文链接：<https://mp.weixin.qq.com/s/XYpeT7tdVD7l-LfFrhDm-g>**

今天笔者给大家推荐一篇高效的基于决策的黑盒对抗攻击算法的文章—— **SurFree: a fast surrogate-free black-box
attack** ，目前该工作已被CVPR2021录用。

![图片](https://images.seebug.org/content/images/2022/09/06/1662433991000-1ddbct.png-w331s)

论文地址：<https://arxiv.org/abs/2011.12807v1>

## **黑盒攻击**

![图片](https://images.seebug.org/content/images/2022/09/06/1662433992000-2oczzc.png-w331s)

**基于分数的黑盒攻击算法** 是根据目标模型对输入样本的输出，即 **各个类别的概率分数**
来估计目标模型损失函数的梯度，进而构造相应的对抗样本。整个过程既不需要知道目标模型的内部信息，也不需要训练额外的替代模型。

**基于决策的黑盒攻击算法** 的特点是仅仅依靠目标模型返回的 **最终标签类别**
来生成对抗样本。相比其他两类攻击方法，基于决策的黑盒攻击算法既不需要训练替代模型，也不需要知道每个输入样本归属于各个类别的概率分数，但往往需要向目标模型进行更多次的查询以达到最优的攻击性能。该类型攻击又称为hard-label attack。

**基于可迁移性的黑盒攻击，**
针对某一种机器学习模型的对抗样本常常也会被其它的机器学习模型错误分类。为了攻击目标模型，攻击者首先会训练一个与目标模型尽可能相似的 **替代模型**
。对于攻击者而言，替代模型的全部信息都是已知的，因此可以使用已有的白盒对抗攻击算法来生成能够成功欺骗替代模型的对抗样本，根据对抗样本的可迁移性，这些对抗样本大概率也能成功欺骗攻击者真正想要攻击的目标模型。

## **SurFree攻击**

**算法概要**

机器学习分类器极易受到对抗样本的攻击。所谓对抗样本，是指在数据集中通过故意添加细微的干扰所形成的输入样本，并导致模型给出一个高置信度的错误输出，同时在人类视觉感知上保持与原始样本的高度一致。在过去几年中，为了伪造对抗样本，黑盒攻击向目标分类器提交的查询数量显著减少，这方面研究的进展主要集中于基于分数的黑盒攻击，即攻击者通过获得的分类预测概率实现攻击，将其查询量从数百万次减少到不足一千次。

本文介绍的SurFree是一种基于几何原理的对抗攻击算法，可以在最苛刻的条件下，即基于黑盒决策的攻击，仅依赖最终的分类标签来大幅减少查询花销。在苛刻条件下实现优秀的对抗攻击，HSJA、QEBA
和 GeoDA
都执行了代价高昂的梯度代理估计，而SurFree避免了代价高昂的梯度代理估计，基于分类器决策边界的几何特性制导，专注于沿着不同方向的探索。在与其他最新的攻击算法进行正面比较之前，笔者对SurFree进行了实验，并重点关注查询量，SurFree在低查询量（几百到一千）的情况下表现出更快的失真衰减，而在更高的查询预算下保持更强竞争力。

**算法介绍**

作者认为之前做梯度估计的方法会在估计梯度时采样B个样本，从而浪费了大量的查询。下图展示了随着查询数量的增多，其扰动导致的失真情况。通过对350多幅图像求平均值可知，其他攻击的失真情况表现出明显的阶梯形状。

![图片](https://images.seebug.org/content/images/2022/09/06/1662433992000-3ljjwc.png-w331s)

图一

为了避免冗余的梯度估计，作者提出了一种有效的随机搜索方法，即将原始样本![](https://images.seebug.org/content/images/2022/09/73bddf43-b796-4fcd-bc76-30bd5c877d40.png-w331s)与当前在边界上的对抗样本![](https://images.seebug.org/content/images/2022/09/24907707-9fb6-4aec-b1bc-082c2fa9861a.png-w331s)起来，通过施密特正交化产生一个随机正交向量，保证与连接的向量以及之前采样过的向量都正交，然后在该正交向量与连接向量构成的超平面内搜索，代替其在整个高维空间内搜索。

**插值方法**

如下图所示，受watermark攻击的启发，边界面具有小曲率的凸曲面，从给定角度![](https://images.seebug.org/content/images/2022/09/4944fec5-03bc-4ec0-acd3-00627a5970b6.png-w331s)，距离为d的点![](https://images.seebug.org/content/images/2022/09/223684de-e94b-4369-981b-1d050fd73317.png-w331s)开始，给出角度![](https://images.seebug.org/content/images/2022/09/4d24fd63-2d04-40c9-8715-f98d244a9041.png-w331s)距离![](https://images.seebug.org/content/images/2022/09/94542a99-91e8-4386-a585-38fc2c0f9605.png-w331s)，在边界上以角度找到第三个点。当![](https://images.seebug.org/content/images/2022/09/d88fa597-a1e6-4ff5-9924-5d6eef15272a.png-w331s)为0，![](https://images.seebug.org/content/images/2022/09/2f2bca5e-4aa7-4099-b5dc-c1acbe1d447b.png-w331s)/2和![](https://images.seebug.org/content/images/2022/09/88b4ed23-77ed-4603-8c38-bb88e49dc6c5.png-w331s)，通过二阶多项式插值从角度到距离并在以下位置找到其最小值：

![](https://images.seebug.org/content/images/2022/09/1c0323ba-d0bc-4f68-8470-8aac50b12737.png-w331s)
利用二分搜索法找到了![](https://images.seebug.org/content/images/2022/09/42e1cbeb-c062-4c35-8fc3-cbf845139df5.png-w331s)和![](https://images.seebug.org/content/images/2022/09/f1fa5cde-9817-400c-bba4-7ff1835d05aa.png-w331s)之间的边界点，点![](https://images.seebug.org/content/images/2022/09/6cd5e824-073c-4867-899a-b8a97430c1a0.png-w331s)在边界上找到的最近的点。

![图片](https://images.seebug.org/content/images/2022/09/06/1662433995000-17ratcq.png-w331s)

图二

**算法流程图**

![图片](https://images.seebug.org/content/images/2022/09/06/1662433995000-18yvglx.png-w331s)

图三

**基本流程：**
首先构建超平面，通过旋转角度搜索更近的对抗样本，再通过二分法细化角度。如果第二步找不到更近的对抗样本，则重新采样方向构建另一个超平面去寻找。

**1.初始化：** 该算法需要一个初始化的点，通过目标攻击或非目标攻击生成对抗样本点。

**2.搜索新方向：**
第k次迭代中，原始样本和当前对抗样本连线向量![](https://images.seebug.org/content/images/2022/09/53001997-2a83-4305-869e-34ba97352f43.png-w331s)，使用DCT基产生一个伪随机向量![](https://images.seebug.org/content/images/2022/09/11e26552-14e5-4b53-9326-6833728daea2.png-w331s)，将![](https://images.seebug.org/content/images/2022/09/87b10fd4-bd75-4137-8b1d-c4597bf39c67.png-w331s)与![](https://images.seebug.org/content/images/2022/09/903c500e-f2f3-4b42-a675-9febb22c27f3.png-w331s)和前![](https://images.seebug.org/content/images/2022/09/bb46ceb2-2e2d-419e-8a6c-14f7f6d74341.png-w331s)次产生的方向做施密特正交化，正交后的方向向量为![](https://images.seebug.org/content/images/2022/09/052de1e8-343c-4e67-b300-401330eea717.png-w331s)，即本次产生的新方向。

**3.搜索：**
在当前方向![](https://images.seebug.org/content/images/2022/09/52d3e3ad-9f1c-45a1-8a9d-cf0fd387d55d.png-w331s)和![](https://images.seebug.org/content/images/2022/09/2c763dfe-69c0-4776-8e3a-4975dcb9e403.png-w331s)所构成的平面内，由当前给定的最大角度![](https://images.seebug.org/content/images/2022/09/44b7b192-e550-4ea2-aba7-638c8e1ce94b.png-w331s)，乘以系数![](https://images.seebug.org/content/images/2022/09/249f73b2-aaba-497d-8b05-97d130ec5882.png-w331s)来试探点![](https://images.seebug.org/content/images/2022/09/119e2268-c722-47ca-83da-7bce4f1f3206.png-w331s)是否为对抗样本，一旦发现对抗样本图片搜索立即停止。否则缩小![](https://images.seebug.org/content/images/2022/09/6008d77d-dc61-4596-8561-1fcac39f739a.png-w331s)重新生成一个![](https://images.seebug.org/content/images/2022/09/53f97449-123e-44cd-a675-fa86b1af1d78.png-w331s)进行上述搜索。

**4.二分法搜索：**
找到角度以及符号![](https://images.seebug.org/content/images/2022/09/8b624a2d-4008-4abd-9038-8c1d0f21d5ab.png-w331s)后，用二分法搜索在![](https://images.seebug.org/content/images/2022/09/748a5d5f-4079-43f1-81f8-be3bd05f93ae.png-w331s)细化![](https://images.seebug.org/content/images/2022/09/152da640-8cd8-4689-9f39-d62c67093205.png-w331s)步，最后增大![](https://images.seebug.org/content/images/2022/09/2a5bda41-8e03-444e-8681-4b22b197fffe.png-w331s)。

## **实验结果**

**评估指标**

论文中的评估指标是查询的数量，以及受攻击图像的对抗扰动。对抗扰动是用空间![](https://images.seebug.org/content/images/2022/09/b6f069bf-d23f-41f4-bd67-1a447830347b.png-w331s)上的范数来进行测量的（用像素的数量乘以颜色通道的数量）。对于给定的![](https://images.seebug.org/content/images/2022/09/c98cfa66-ff4b-4e45-8a47-836c931eede0.png-w331s)，它是在查询序列上获得的最小扰动，具体表达式为：

![](https://images.seebug.org/content/images/2022/09/1ecfe838-17fe-46c3-acca-0e30f3235301.png-w331s)
N张原始图像上的平均值给出了攻击效率的特征，揭示了其找到接近原始图像的对抗样本的能力，具体的表达式为：

![](https://images.seebug.org/content/images/2022/09/5aa675f3-c487-46aa-bee4-f5d5401cb741.png-w331s)

作者将成功率定义为在查询预算内获得低于目标数据的失真概率，具体的表达式为：

![](https://images.seebug.org/content/images/2022/09/6a3f081b-0249-4533-bbe7-64ca993574be.png-w331s)

**实验分析**

本论文中的攻击方向的产生是高度随机的，这可能会产生不稳定的结果，产生分散扰动的对抗图像。下面两幅图分别展示了100幅图像的平均失真情况和一幅图像被攻击20次的标准偏差。这两幅图展示了一次迭代在查询数量方面的复杂性与失真率下降的增益之间的权衡，并且可以发现，SurFree攻击算法很好地权衡了平均失真和标准偏差这两方面。

![图片](https://images.seebug.org/content/images/2022/09/06/1662434000000-41jsvqt.png-w331s)

图四

![图片](https://images.seebug.org/content/images/2022/09/06/1662434001000-42jkaqa.png-w331s)

图五

如下表所示，在最初的一千个查询中，全像素域的失真更大。对于相同的查询代价，将扰动约束在用全离散余弦变换定义的较小低频子空间中是更加有益的。

![图片](https://images.seebug.org/content/images/2022/09/06/1662434001000-43frjcz.png-w331s)

图六

下表显示了三个被攻击图像的视觉展示，这三个被攻击图像分别是容易攻击、中等攻击和难以攻击。虽然这三种攻击对图像的影响不同，可以很明显的发现SurFree攻击生成的对抗样本非常有针对性，并且生成的对抗扰动不是漫无目的。

![图片](https://images.seebug.org/content/images/2022/09/06/1662434002000-44xwemn.png-w331s)

图七

参考文献：

Maho T, Furon T, Le Merrer E. SurFree: a fast surrogate-free black-box
attack[C]//Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition. 2021: 10430-10439.

注：本文图片图一至图七均来源于以上论文

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1958/>

