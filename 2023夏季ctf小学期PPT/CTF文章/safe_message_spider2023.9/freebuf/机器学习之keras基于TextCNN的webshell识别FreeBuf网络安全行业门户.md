本来想用zend直接解析PHP
opcode然后做xxoo的,然后看了一会zend源码，发现PHP真的是”动态”语言,,,比如eval(base64_encode(“xxxx”))
opcode只能看到eval base64_encode 其他的要动态执行才行~
那样就复杂了,需要追踪入口,加数据做流追踪等等,实在是太麻烦,所以还是换成了传统的语义分析

 **我们要做什么？**

我打算使用一个 TextCNN 与 一个普通的二分类网络来分别做。TextCNN主要是用来检测单词数组，普通二分类网络用于检测一些常规特征,比如
文件熵(aka 文件复杂度) 文件大小(某些一句话几KB)  
为了方便,我这边仅仅使用php,当然,任何都可以.样本数量是1W左右,自己写了一个一句话变种生成器(居然有部分过了主流防火墙,哈哈哈哈),生成了1000多个一句话。

## 准备

首先准备好几个文件夹 一个放好绿色文件:

![](https://image.3001.net/images/20210520/1621517558_60a664f6263218e689ee5.png!small)

一个是webshell

![](https://image.3001.net/images/20210520/1621517587_60a6651354e7f489deea9.png!small)下载安装好nltk,到时候做分词用

## 清洗数据

所谓清洗数据,我们不希望php的注释/**/ // #这种被机器学习解析,因此我们要清洗掉这些东西  
代码如下:

    
    
    def flush_file(pFile):  # 清洗php注释
        file = open(pFile, 'r', encoding='gb18030', errors='ignore')
        read_string = file.read()
        file.close()
        m = re.compile(r'/\*.*?\*/', re.S)
        result = re.sub(m, '', read_string)
        m = re.compile(r'//.*')
        result = re.sub(m, '', result)
        m = re.compile(r'#.*')
        result = re.sub(m, '', result)
        return result

效果:

![](https://image.3001.net/images/20210520/1621517655_60a66557513932a47e91a.png!small)

让我们得到data frame:

    
    
    # 得到webshell列表
        webshell_files = os_listdir_ex("Z:\\webshell", '.php')
        # 得到正常文件列表
        normal_files = os_listdir_ex("Z:\\noshell", '.php')
        label_webshell = []
        label_normal = []
        # 打上标注
        for i in range(0, len(webshell_files)):
            label_webshell.append(1)
        for i in range(0, len(normal_files)):
            label_normal.append(0)
        # 合并起来
        files_list = webshell_files + normal_files
        label_list = label_webshell + label_normal

记得打乱数据

    
    
    # 打乱数据,祖传代码
        state = np.random.get_state()
        np.random.shuffle(files_list)  # 训练集
        np.random.set_state(state)
        np.random.shuffle(label_list)  # 标签

合在一起,返回一个data_frame

    
    
    data_list = {'label': label_list, 'file': files_list}
        return pd.DataFrame(data_list, columns=['label', 'file'])

效果:

![](https://image.3001.net/images/20210520/1621517721_60a665998d2de81157ca5.png!small)

## 文件熵获取

文件熵,又叫做文件复杂度,文件越混乱,熵也越大,一般php文件不会很混乱,而webshell往往因为加密等东西搞的文件乱七八糟的,这是一个检测特征,这边使用网上抄来的方法计算文件熵

    
    
    # 得到文件熵 https://blog.csdn.net/jliang3/article/details/88359063
    def get_file_entropy(pFile):
        clean_string = flush_file(pFile)
        text_list = {}
        _sum = 0
        result = 0
        for word_iter in clean_string:
            if word_iter != '\n' and word_iter != ' ':
                if word_iter not in text_list.keys():
                    text_list[word_iter] = 1
                else:
                    text_list[word_iter] = text_list[word_iter] + 1
        for index in text_list.keys():
            _sum = _sum + text_list[index]
        for index in text_list.keys():
            result = result - float(text_list[index])/_sum * \
                math.log(float(text_list[index])/_sum, 2)
        return result

## 文件长度获取

针对一句话木马或者包含木马,他们长度就是很小的,所以文件长度也能作为一个特征:

    
    
    def get_file_length(pFile):  # 得到文件长度,祖传代码
        fsize = os.path.getsize(pFile)
        return int(fsize)
    

## 合并起来

现在常规特征已经搞好了,合并这些常规特征

    
    
    data_frame = get_data_frame()
    data_frame['length'] = data_frame['file'].map(
        lambda file_name: get_file_length(file_name)).astype(int)
    data_frame['entropy'] = data_frame['file'].map(
        lambda file_name: get_file_entropy(file_name)).astype(float)
    

归一化:  
我们要把他们变成-1 1之间区间的值,这样不会特别影响网络,如果不变,网络就会出现很大幅度的落差

    
    
    # 归一化这两个东西
    scaler = StandardScaler()
    data_frame['length_scaled'] = scaler.fit_transform(
        data_frame['length'].values.reshape(-1, 1), scaler.fit(data_frame['length'].values.reshape(-1, 1)))
    data_frame['entropy_scaled'] = scaler.fit_transform(
        data_frame['entropy'].values.reshape(-1, 1), scaler.fit(data_frame['entropy'].values.reshape(-1, 1)))
    

## 自然语言处理

由于我之前并不是特别专门学过自然语言处理,所以这里可能会有点错误.以后我发现有错误了再改:  
首先我们要通过nltk这个库分词:

    
    
    clean_string = flush_file(pFile)
        word_list = nltk.word_tokenize(clean_string)
    

请记住,nltk需要单独下载分词库,国内网络你懂的,我是手动下载了然后放到了nltk的支持目录  
然后我们得过滤掉不干净的词,避免影响数据库:

    
    
    # 过滤掉不干净的
        word_list = [
            word_iter for word_iter in word_list if word_iter not in english_punctuations]
    

这是我的不干净的词库:

    
    
    english_punctuations = [',', '.', ':', ';', '?',
                                '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', 'php', '<', '>', '\'']
    

然后初始化标注器,提取出文本字典

    
    
    keras_token = keras.preprocessing.text.Tokenizer()  # 初始化标注器
        keras_token.fit_on_texts(word_list)  # 学习出文本的字典

如果顺利,这些单词长这样:

![](https://image.3001.net/images/20210520/1621517769_60a665c9145f13b8822ce.png!small)

上面是一句话webshell,下面是正常文本  
通过texts_to_sequences 这个function可以将每个string的每个词转成数字

    
    
    sequences_data = keras_token.texts_to_sequences(word_list)
    

然后我们把它扁平化,别问我为什么要用C的写法,写惯了,,当时写的时候没有注意到,然后写出来了才发现python有封装了，

    
    
    word_bag = []
        for index in range(0, len(sequences_data)):
            if len(sequences_data[index]) != 0:
                for zeus in range(0, len(sequences_data[index])):
                    word_bag.append(sequences_data[index][zeus])
    

到此为止,自然语言处理函数已经完成,我们看看效果:

    
    
    # 导入词袋
    data_frame['word_bag'] = data_frame['file'].map(
        lambda file_name: get_file_word_bag(file_name))

![](https://image.3001.net/images/20210520/1621517828_60a6660477550d7f03df9.png!small)

由于keras要求固定长度,所以让我们填充他,固定长度为1337
超过1337截断(超过1337个字符的”单词”不用说肯定是某个骇客想把大马变免杀马),低于1337个字符用0填充:

    
    
    vectorize_sequences(data_frame['word_bag'].values)
    

让我们看看效果:

![](https://image.3001.net/images/20210520/1621517853_60a6661dd62924c581e77.png!small)

zzzz 全是0 还是别看了,反正数据就长这样

## 构造网络

重头戏来了,构造一个textCnn+二分类的混合网络:  
首先是构造textCNN  
长这样

![](https://image.3001.net/images/20210520/1621517877_60a66635d79243f93ea2f.png!small)

词嵌入层 -> 卷积层 + 池化层(我这边抄的只有3个) -> 全连接合并这三个  
首先是词嵌入,也叫做入口:

    
    
    input_1 = keras.layers.Input(shape=(1337,), dtype='int16', name='word_bag')
        # 词嵌入（使用预训练的词向量）
        embed = keras.layers.Embedding(
            len(g_word_dict) + 1, 300, input_length=1337)(input_1)
    

请注意,我输入的数据模型是1337个float,所以shape=1337  
然后生成三个卷积+池化层

    
    
    cnn1 = keras.layers.Conv1D(
            256, 3, padding='same', strides=1, activation='relu')(embed)
        cnn1 = keras.layers.MaxPooling1D(pool_size=48)(cnn1)
    

然后把这些拼接起来:

    
    
    cnn = keras.layers.concatenate([cnn1, cnn2, cnn3], axis=1)
        flat = keras.layers.Flatten()(cnn)
        drop = keras.layers.Dropout(0.2)(flat)
    

让他输出一个sigmoid

    
    
    model_1_output = keras.layers.Dense(
            1, activation='sigmoid', name='TextCNNoutPut')(drop)
    

第一层好了,连起来长这样:

    
    
    # 进来的file length_scaled entropy_scaled word_bag
        # 第一网络是一个TextCNN 词嵌入-卷积池化*3-拼接-全连接-dropout-全连接
        input_1 = keras.layers.Input(shape=(1337,), dtype='int16', name='word_bag')
        # 词嵌入（使用预训练的词向量）
        embed = keras.layers.Embedding(
            len(g_word_dict) + 1, 300, input_length=1337)(input_1)
        # 词窗大小分别为3,4,5
        cnn1 = keras.layers.Conv1D(
            256, 3, padding='same', strides=1, activation='relu')(embed)
        cnn1 = keras.layers.MaxPooling1D(pool_size=48)(cnn1)
    
        cnn2 = keras.layers.Conv1D(
            256, 4, padding='same', strides=1, activation='relu')(embed)
        cnn2 = keras.layers.MaxPooling1D(pool_size=47)(cnn2)
    
        cnn3 = keras.layers.Conv1D(
            256, 5, padding='same', strides=1, activation='relu')(embed)
        cnn3 = keras.layers.MaxPooling1D(pool_size=46)(cnn3)
        # 合并三个模型的输出向量
        cnn = keras.layers.concatenate([cnn1, cnn2, cnn3], axis=1)
        flat = keras.layers.Flatten()(cnn)
        drop = keras.layers.Dropout(0.2)(flat)
        model_1_output = keras.layers.Dense(
            1, activation='sigmoid', name='TextCNNoutPut')(drop)
        # 第一层好了
    

第二层,自己做的一个简易分类用来根据长度+熵做二分类  
输入shape为2(长度&熵)

    
    
    input_2 = keras.layers.Input(
            shape=(2,), dtype='float32', name='length_entropy')
        model_2 = keras.layers.Dense(
            128, input_shape=(2,), activation='relu')(input_2)
    

没什么特别的:

    
    
    model_2 = keras.layers.Dropout(0.4)(model_2)
        model_2 = keras.layers.Dense(64, activation='relu')(model_2)
        model_2 = keras.layers.Dropout(0.2)(model_2)
        model_2 = keras.layers.Dense(32, activation='relu')(model_2)
        model_2_output = keras.layers.Dense(
            1, activation='sigmoid', name='LengthEntropyOutPut')(model_2)
    

拼接两个网络:

    
    
    model_combined = keras.layers.concatenate([model_2_output, model_1_output])
        model_end = keras.layers.Dense(64, activation='relu')(model_combined)
        model_end = keras.layers.Dense(
            1, activation='sigmoid', name='main_output')(model_end)
    

不得不说keras是真的强大,,,  
我们希望输出是sigmoid而且只有一个值(是否是webshell),因此最后一层就是1  
别忘了定义输入输出

    
    
    # 定义这个具有两个输入和输出的模型
        model_end = keras.Model(inputs=[input_2, input_1],
                                outputs=model_end)
        model_end.compile(optimizer='adam',
                          loss='binary_crossentropy', metrics=['accuracy'])

总体网络架构如下:

![](https://image.3001.net/images/20210520/1621517906_60a666526dd73112f1b9b.png!small)

## 跑一下试试?

对于免杀样本,是有很好地检测率

![](https://image.3001.net/images/20210520/1621517928_60a66668caafc6f1bfc03.png!small)

正常文件误报率也很低  
个人认为 这个神经网络可以认为是跟人看写php法一样的,如果webshell的单词、熵写的跟正常文件差不多,就会没办法  
而且样本还是太少了,遇到一句话混合到正常文件的情况完全没有办法, 个人认为还是要增加样本+与传统检测引擎混合使用

## 源码下载

<https://github.com/huoji120/ai-webshell-detect>  
你可以随意使用,毕竟我们是知识付费时代的逆行者

