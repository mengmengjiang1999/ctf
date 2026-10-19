![](https://image.3001.net/images/20210823/1629715907_61237dc35b28bf715c649.png!small)

## 关于OpenAttack

OpenAttack是一款专为文本对抗攻击设计的开源工具套件，该工具基于Python开发，可以处理文本对抗攻击的整个过程，包括预处理文本、访问目标用户模型、生成对抗示例和评估攻击模型等等。

## 功能&使用

 **OpenAttack支持以下几种功能：**

高可用性：OpenAttack提供了易于使用的API，可以支持文本对抗攻击的整个过程；

全面覆盖攻击模型类型：OpenAttack支持句子/单词/字符级扰动和梯度/分数/基于决策/盲攻击模型；

灵活性强&可扩展：我们可以轻松攻击定制目标用户模型，或开发和评估定制的攻击模型；

综合评估：OpenAttack可以从攻击有效性、对抗示例质量和攻击效率等方面全面评估攻击模型；

 **OpenAttack的使用范围非常广，其中包括但不限于：**

为攻击模型提供各种评估基线；

使用其全面评估指标综合评估攻击模型；

借助通用攻击组件，协助快速开发新的攻击模型；

评估机器学习模型对各种对抗攻击的鲁棒性；

通过使用生成的对抗示例丰富训练数据，进行对抗训练以提高机器学习模型的鲁棒性；

## 工具模块

![](https://image.3001.net/images/20210823/1629715926_61237dd6b81137424b642.png!small)

## 工具安装

我们可以使用pip安装，或者克隆该项目源码来安装OpenAttack。

### 使用pip安装（推荐）

    
    
    pip install OpenAttack

### 克隆代码库

    
    
    git clone https://github.com/thunlp/OpenAttack.git
    
    cd OpenAttack
    
    python setup.py install

安装完成之后，我们可以尝试运行“demo.py”来检测OpenAttack是否能够正常工作：

![](https://image.3001.net/images/20210823/1629715959_61237df7ead21357cd483.gif!small)

## 使用样例

### 基础使用：使用内置攻击模型

OpenAttack内置了一些常用的文本分类模型，如LSTM和BERT，以及用于情感分析的SST和用于自然语言推理的SNLI等数据集。

以下代码段显示了如何使用基于遗传算法的攻击模型攻击SST数据集上的BERT：

    
    
    import OpenAttack as oa
    
    # choose a trained victim classification model
    
    victim = oa.DataManager.load("Victim.BERT.SST")
    
    # choose an evaluation dataset
    
    dataset = oa.DataManager.load("Dataset.SST.sample")
    
    # choose Genetic as the attacker and initialize it with default parameters
    
    attacker = oa.attackers.GeneticAttacker()
    
    # prepare for attacking
    
    attack_eval = oa.attack_evals.DefaultAttackEval(attacker, victim)
    
    # launch attacks and print attack results
    
    attack_eval.eval(dataset, visualize=True)

### 高级使用：攻击自定义目标用户模型

下面的代码段显示了如何使用基于遗传算法的攻击模型攻击SST上的自定义情绪分析模型：

    
    
    import OpenAttack as oa
    
    import numpy as np
    
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    
     
    
    # configure access interface of the customized victim model
    
    class MyClassifier(oa.Classifier):
    
        def __init__(self):
    
            self.model = SentimentIntensityAnalyzer()
    
        # access to the classification probability scores with respect input sentences
    
        def get_prob(self, input_):
    
            rt = []
    
            for sent in input_:
    
                rs = self.model.polarity_scores(sent)
    
                prob = rs["pos"] / (rs["neg"] + rs["pos"])
    
                rt.append(np.array([1 - prob, prob]))
    
            return np.array(rt)
    
    # choose the costomized classifier as the victim model
    
    victim = MyClassifier()
    
    # choose an evaluation dataset
    
    dataset = oa.DataManager.load("Dataset.SST.sample")
    
    # choose Genetic as the attacker and initialize it with default parameters
    
    attacker = oa.attackers.GeneticAttacker()
    
    # prepare for attacking
    
    attack_eval = oa.attack_evals.DefaultAttackEval(attacker, victim)
    
    # launch attacks and print attack results
    
    attack_eval.eval(dataset, visualize=True)

## 项目地址

 **OpenAttack：** 【[ _GitHub传送门_](https://github.com/thunlp/OpenAttack)】

