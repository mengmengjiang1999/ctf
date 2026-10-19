**作者：果胜**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

目前在威胁情报领域基于机器学习的数据分析技术已经的得到了很多应用,诸多安全厂商和团队都开始建立相关的机器学习模型用于威胁的检测和相关数据的分析。其中自然语言处理(NLP)相关技术在恶意代码检测,样本分析,威胁情报抽取与建模中有着重要的地位,本文主要梳理和介绍一些NLP技术在威胁情报中的应用场景与相关概念和技术,以供参考。

# 典型应用场景

NLP技术的安全应用多在于文本类数据的分析以及序列问题的处理,例如对HTTP协议传输数据的安全检测等,这里选取一些典型场景予以介绍。

## 恶意脚本代码检测

脚本代码(bash/powershell/sql/js等)不必编译即可执行,故而与二进制恶意代码分析不同,对脚本代码本身进行语义分析即可判定其性质。严格来说,对程序语言进行语义分析不属于NLP技术(自然语言处理)的范畴,但是NLP的相关技术可以有效的解决问题。例如,对HTTP协议参数进行语义分析,判断其文本是否符合sql/js语法,从而确认参数是否为sqli/xss
payload。与传统的基于规则的方法相比,基于机器学习NLP的方法对于未知数据的检测(机器学习有更好的泛化能力)和混淆后代码的检测(混淆本身不破坏语法结构)有更好的效果。不过NLP技术并不万能,分词技术的弱点和机器学习模型本身的不精确性会影响其最后的效果,仍需要结合规则使用。

## 二进制样本分析

对于二进制样本分析人员来说,反汇编后的程序某种程度可视为一个由汇编指令,以及指令块控制流构成的序列。目前一些安全研究者试图通过NLP技术解析反汇编序列,从而完成提取恶意代码的特征片段,检查二进制样本相似度和家族关系等工作。这方面的应用在AAAI-20大会上有精彩的分析,可以参考。

## 威胁情报生产与建模

对安全人员来说威胁情报可能存在多个来源,依据其格式不同,可划分为结构化数据(已经过表结构处理,便于机器识别)和非结构化数据(主要为自然语言等数据)。通过NLP技术对非结构化数据进行处理,可以提取出其中的关键知识,逻辑关系等信息并转化为结构化数据,从而用于生产可以被机器直接使用的机读情报或作为威胁建模的素材。例如semfuzz工具即通过对linux安全公告,git更新日志等信息进行NLP处理,提取其中的版本,API名称,变量名等关键信息,并以此构建精确的fuzz工程,提高发现漏洞的效率。

# 特征工程

计算机对文本数据进行处理,需要将文本序列转化为由数值构成的数据,这一把文本变为特征数据的过程称为特征工程。此处简要介绍一些NLP特征工程的关键概念。

## 分词

分词是指将文本内容转化为词序列的过程,只有通过分词计算机才能明确将文本数值化的最小处理单位,样例如下:

    
    
    import nltk
    text = nltk.word_tokenize("This is an exmaple.")
    print(text)
    ['This', 'is', 'an', 'exmaple', '.']

可见代码对目标以空格和标点符号为边界切割了整句话。分词是整个NLP技术的基础,分词的水平对最终的结果有很大影响。对于不同类型的文本需要设计独立的分词方式,例如对html文本的分词即需要以<>或html标签为边界进行切割，才可能得到可以被正确处理的词序列。

## 词袋模型

词袋模型是一种基于词汇出现次数将词序列数值化的方法，词袋模型通过计算单个词汇在文本中出现的次数来表示一个词序列，例如对以下文本:

> This is an apple.This is a banana.

可以形成一个如下的词空间

> ['This','is','an','a','apple','banana']

在这个词空间中，可以将两句话的词序列分别用词袋模型表示为如下数值:

> [1,1,1,0,1,0] #['This','is','an','apple']  
>  [1,1,0,1,0,1] #['This','is','a','banana']

词袋模型将每个词序列按照词汇出现次数表示，完成了文本向数据的转化。

## TF-IDF模型

简单的利用词汇出现次数表示词序列存在无法完全反映词汇重要程度的缺陷，例如’to‘，’and‘一类的词汇会具有很高的词频，为了修正这一缺陷，可以使用tf-idf模型，该模型对某一词汇计算数值的公式如下：

> TF（词频） = 词汇在文本中出现次数/文本总词数  
>  IDF（逆文件频率） = log(语料库文本总数/包含某个词的文本数+1)  
>  TF-IDF = TF * IDF

TF-IDF模型的核心思想在于以词汇在某个文本中的重要性来对词汇进行数值化，即由某个词在文本中出现的频率（TF）和该词汇在所有文本中出现的概率（IDF）共同决定，TF越高且同时IDF越低，说明某一词汇在某一文本中越重要。TF-IDF模型常常用于文本关键词提取和搜索引擎技术中。

## 词向量模型

词袋模型和TF-IDF模型本质上均为基于词频的模型，此类模型忽略了词序列中的先后关系，无法反映某个词汇的上下文对词汇意义的影响。为了修正这一缺陷，可以通过词向量的方式来表征一个词汇，词向量模型建立在一个基本假设上：具有相似上下文词汇的具有相似语义。以经典的词向量word2vec为例，通过训练一个以词汇的one-hot形式向量为输入（ont-hot编码是一种将词汇以字母为单位转化成定长数据的方法）的神经网络，可以得到文本的词向量，主要模型有如下两种：

![](https://images.seebug.org/content/images/2020/06/9ec60591-328c-4b4c-959b-f9ef1a137823.png-w331s)

**CBOW模型**

![](https://images.seebug.org/content/images/2020/06/2dd74e0d-7a42-4e09-ad46-efdbe1e6db46.png-w331s)

**Skip-Gram模型**

其中CBOW模型以某一词汇的上下文作为输入，预测上下问对应的词汇，而Skip-Gram模型以某一词汇作为输入，预测该词汇对应的上下文。在最终完成训练之后，神经网络隐藏层的矩阵权重（隐藏层可以参见深度学习的内容），即为所得的词向量。

由于在训练词向量的过程中使用了词汇的上下文信息，因而词向量本身即包含了词汇的语义信息，一个词向量在低维空间中的演示图如下：

![](https://images.seebug.org/content/images/2020/06/09d91070-0c92-4f87-89c9-1046206155ba.jpeg-w331s)

可以发现具有相似映射关系的词汇构成的向量几乎是平行的，这也是语义在词向量空间中具体的表现形式。因而通过词向量进行特征工程处理的文本，在需要上下文信息和相似度的场景下有更好的表现。在word2vec之后，还提出了fasttext，bert等模型，这些模型的基本思想都比较类似，在此不一一介绍。目前主流的NLP工具包中均提供了词向量API，可以方便的对文本进行处理。

    
    
    from gensim.models import Word2Vec
    from gensim.models.word2vec import LineSentence
    corpus = 'corpus.txt' #语料文本
    #对出现超过两次的词汇，以前后3个词汇为上下文训练次向量
    w2v_model = Word2Vec(LineSentence(corpus),window=3,min_count=2)
    wordvector = []
    for key in w2v_model.wv.vocab.keys():
        #逐一获取每个词汇的对应词向量
        wordvector.append(w2v_model[key])

# 关键词提取

文本挖掘是一个与NLP技术有交叉的领域，其目的是通过对文本数据进行挖掘，获取其中关键的知识和信息，在文本特征分析和安全情报提取中，关键词提取的一些算法有较好的表现。例如对反序列化或二进制数据应用关键词提取的方法进行分析，可以在缺少安全样本的情况下发现其中存在异常的payload和shellcode。在此简要介绍一些关键词提取技术。

## textrank

textrank算法来自与用于计算网页排名的pagerank算法，其思路是首先以N（N>0）为窗口，将文本转换为一个由词汇与前后N个词汇构成的网络（结构与由链接相互关联的网页相似），如图：

![](https://images.seebug.org/content/images/2020/06/09d9e741-d776-4d44-8a7d-5f836130f2c0.jpeg-w331s)

然后对每个节点计算计算权重，其思路为某个词汇的权重等于其相邻词汇的加权排名之和 ,公式为：

其中WS表示了某词汇的权重，In(Vi)表示该词汇之前相邻词汇，Out(Vj)表示该词汇之后相邻词汇，d用于平滑函数，W(ji)表示某一关系的权重。从公式可见，任何一个词汇的权重都由其上下文的权重决定，故而该算法需要从零开始，在网络中反复传播迭代以获取最终的结果。在各词汇权重均求出后，即可对词汇按权重排序，并将结果中相邻的词汇合并以获取关键词。
作为一种无监督算法，textrank的优势在于无需样本训练即可在目标上使用。且该算法适用于任意长度的文本。故而在分析一些中短长度的数据时，有不错的表现。

## LDA

LDA算法是一种依据概率求解文本中关键词的算法。其出发点是认为文本中的任意一个词汇都是根据一定概率从某个主题中选择的，而任意一个主题都是根据一定概率被文本选择的，即：

`$P(词汇|文档) = \sum_{主题}{p(词汇|主题)*p(主题|文档)}$`

LDA算法则从这一思路反向计算归于某一主题的关键词，LDA算法本身比较复杂，在此不做详述。目前主流的机器学习工具包也都提供了这一重要的算法。

    
    
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    from nltk.corpus import stopwords
    corpus = 'What are some of the real world uses topic modelling has? Historians can use LDA to identify important events in history by analysing text based on year. Web based libraries can use LDA to recommend books based on your past readings. News providers can use topic modelling to understand articles quickly or cluster similar articles. Another interesting application is unsupervised clustering of images, where each image is treated similar to a document.'
    #使用词袋模型对文本特征工程
    cntVector = CountVectorizer(stop_words=stopwords.words('english'))
    cntTf = cntVector.fit_transform([corpus]) 
    #假设目标文本有5个主题
    lda = LatentDirichletAllocation(n_components=1) 
    docres = lda.fit_transform(cntTf) #使用lda算法计算关键词
    
    def print_top_words(model, feature_names, n_top_words):
        #打印每个主题下权重较高的term
        for topic_idx, topic in enumerate(model.components_):
            print("Topic #%d:" % topic_idx)
            print(" ".join([feature_names[i]
                            for i in topic.argsort()[:-n_top_words - 1:-1]]))
    
    n_top_words=6
    tf_feature_names = cntVector.get_feature_names()
    print_top_words(lda, tf_feature_names, n_top_words)

结果：

    
    
    Topic #0:
    based use similar modelling topic lda

LDA算法也是一种无监督学习算法，无需样本训练即可在目标上使用。不过由于其需要对词频进行计算，故算法在较长的文本中会有更好的效果。

## 聚类提取

聚类算法是一类无监督学习算法，主要指自动将没有标记的数据划分为几类的方法。在前文中提到word2vec等词向量模型可以在向量空间中更好的反应语义信息。故可以通过对文本中的词向量进行聚类分析，将文本中的词汇划分为不同类别，并根据词频从不同的类别中选取关键词。目前主要的聚类算法分为基于划分、基于层次、基于密度、基于网格和基于模型等类型。在词向量聚类的场景下，词向量通过余弦相似度（即两个词向量的cos值）反映了语义的相似度，而由于归一化后的cos距离和欧式距离（即两个坐标点的直线距离）线性相关，故可以通过基于划分的方法对数据进行聚类（基于划分的方法主要依靠计算距离来评估两个数据间的相关性），在此对其中较知名的kmeans方法做介绍。

  1. 选取k个对象作为每一个簇的中心； 

  2. 计算其他对象与各簇中心的距离，并将其归类到最近的簇；

  3. 计算每个簇的距离平均值，更新簇中心； 

  4. 不断重复2、3

一个demo如下：

    
    
    from gensim.models import Word2Vec
    from sklearn.cluster import KMeans
    #语料
    sentences = [['this', 'is', 'a', 'pear'],
                ['this', 'is',  'a','banana'],
                ['this', 'is',  'an','apple'],
                ['this','is','a','lemon'],
                ['this','is','a','melon'],
                ['this','is','a','cherry']]
    #训练词向量
    model = Word2Vec(sentences, min_count=1)
    wordvector = []
    for key in model.wv.vocab.keys():
        #逐一获取每个词汇的对应词向量
        wordvector.append(model[key])
    #通过余弦相似度获取与apple最近义的词
    print (model.most_similar(positive=['apple'], negative=[], topn=2))
    #结果为[('is', 0.19642898440361023), ('pear', 0.15730774402618408)]
    #可见出现了pear，但仍有改善的余地
    
    #使用kmeans算法对语料进行聚类，共分为2类
    clf = KMeans(n_clusters=2)
    clf.fit(wordvector)
    labels = clf.labels_
    classCollects={}
    keys = model.wv.vocab.keys()
    for i in range(len(keys)):
        if labels[i] in list(classCollects.keys()):
            classCollects[labels[i]].append(list(keys)[i])
        else:
            classCollects={0:[],1:[]}
    
    print(classCollects[0])
    print(classCollects[1]))
    '''
    结果为：
    ['pear', 'banana', 'apple', 'lemon', 'melon']
    ['is', 'a', 'an', 'cherry']
    '''

对词向量聚类在理论上有很好的潜力，但在实践中也存在问题（在demo中也有体现）。其一是kmeans算法中初始选取的中心对最后的结果有一定影响;其二是词向量一般维度很高，而基于距离的聚类算法在高维空间的表现会有所下降（降维过度又会造成向量损失必要的信息）。故而词向量聚类在实际使用中需要根据具体场景做优化。

# 命名实体识别

命名实体识别是NLP技术中的重要组成部分，其目的是识别出文本当中的特定实体，并进而将其中的关键信息抽取出来，从而将非结构化的文本数据转换为结构化的可机读数据，为各类自动化任务提供数据支撑。在威胁建模或情报分析当中，命名实体识别可以快速的把关键信息从多个来源，不同格式的文本中抽取出来。

命名实体识别的方法基本可分为三类：

  * 基于规则/字典识别 

通过指定的字典或预先设定的正则表达式匹配文本中的实体，这一方法主要用于识别特定格式的数据，如版本号，CVE编号等。目前往往会将规则与其他方法一起使用进行实体识别工作。

  * 基于统计识别

通过对不同词性，不同特征的词汇进行统计，计算特定实体在其位置上出现的概率和上下文转换概率等。目前常用的方法有最大熵模型，隐式马尔科夫(HMM),支持向量机(SVM)等。

  * 基于深度学习识别 

深度学习方法本质也可归为统计识别的一种，实体识别本质上也可视为一个分类问题（即识别词汇是否属于特定的命名实体），故也可以使用图像识别领域常用的神经网络技术。通过使用人工标注了实体的文本对进行神经网络进行训练，即可获得一个用于识别命名实体的深度学习模型。目前常见的模型有CNN-CRF，RNN-CRF等。

![](https://images.seebug.org/content/images/2020/06/beca65d0-1526-4aca-9612-b3a85b40ec5c.png-w331s)

上图为一个demo，可见一个训练过的神经网络，可以从漏洞描述信息中识别出漏洞类型（VULN），产品名称（PRODUCT），产品版本（VERSION），漏洞危害（CAPIBILITY），漏洞处发点（SINK），payload（PAYLOAD）等，从而将文本转化为一份可机读的数据。这一技术也是试图通过NLP进行信息收集和数据分析的关键所在，高水平的命名实体识别可以对自动化威胁情报分析和威胁建模有很大帮助。

# 结语

NLP领域还有多个技术概念，如词性标注，词干分析，文本情感判定等，由于此类技术在安全领域应用有限，受限于篇幅，本文不做更多介绍，可以根据自身需求做更多了解。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1256/>

