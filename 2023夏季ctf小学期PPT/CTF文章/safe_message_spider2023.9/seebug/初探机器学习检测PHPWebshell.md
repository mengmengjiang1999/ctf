作者：WenR0@n0tr00t Security Team

#### 简介

最近刷完了吴恩达（Andrew Ng）的Machine
Learning[课程](https://www.bilibili.com/video/av9912938/)，恰巧实验室有相关的需求，看了几个前辈的机器学习检测PHP
Webshell 的文章，便打算自己也抄起袖子，在实战中求真知。

本文会详细的介绍实现机器学习检测PHP Webshell的思路和过程，一步一步和大家一起完成这个检测的工具，文章末尾会放出已经写好的下载链接。

#### 可能需要的背景知识

  * php基础知识（PHP opcode）

  * php Webshell

  * Python（scikit-learn）

##### 背景知识简单介绍

PHP：世界上最好的编程语言，这个不多说了。

PHP opcode：PHP opcode 是脚本编译后的中间语言，就如同Java 的Bytecode、.NET 的MSL。

PHP Webshell：可以简单的理解为 网页后门。

Python scikit-learn：

![](https://images.seebug.org/content/images/2018/02/72374c26-0adc-477e-9c05-d2ea8f75b79b.png-w331s)

（翻译：用起来美滋滋的Python 机器学习包）

#### 可行性分析

PHP Webshell本质上也是一段PHP的代码，在没有深入研究前，也知道PHP Webshell
必然有一些规律，比如执行了某些操作（执行获取到的命令、列出目录文件、上传文件、查看文件等等）。如果直接用PHP
的源代码分析，会出现很多的噪音，比如注释内容、花操作等等。如果我们将PHP Webshell
的源代码转化成仅含执行语句操作的内容，就会一定程度上，过滤掉这些噪音。所以，我们使用PHP opcode 进行分析。

针对opcode这种类型的数据内容，我们可以采用词袋，词频等方法来进行提取关键特征。最后使用分类的算法来进行训练。

根据上面的简单“分析”，知道咱们在大体思路上，是可以行得通的。

#### 实战

##### 第一步：准备环境

要获取到PHP opcode，需要添加一个PHP 的插件 VLD，我们拿Windows环境来进行举例。

插件下载地址：[传送门](http://pecl.php.net/package/vld/0.14.0/windows)

选择对应版本进行下载

![](https://images.seebug.org/content/images/2018/02/ce18139d-b740-47ef-bd6b-9588023a025e.png-w331s)

下载好后，放入到PHP 安装目录下的ext文件夹内，我使用的是PHPstudy环境，

![](https://images.seebug.org/content/images/2018/02/0965007a-1c0d-4ce4-888d-cbcf01ab7378.png-w331s)

然后编辑php.ini文件，添加一行内容

    
    
    extension=php_vld.dll

测试是否安装成功：

测试文件1.php

    
    
    <?php
        echo "Hello World";
    ?>

执行命令：

    
    
    php -dvld.active=1 -dvld.execute=0 1.php

![](https://images.seebug.org/content/images/2018/02/7dd1d371-819a-4299-9d08-5bb84ab35679.png-w331s)

如果显示内容是差不多一样的，那我们的环境配置就成功了。

我们需要的就是这段输出中的

![](https://images.seebug.org/content/images/2018/02/180e8f93-db9b-453a-aee9-7d3d4ccf232d.png-w331s)

    
    
    ECHO 、RETURN

这样的opcode。

到这里，我们的PHP环境配置基本完成了。

##### 第二步：准备数据

进行机器学习前，我们很关键的一步是要准备数据，样本的数量和质量直接影响到了我们最后的成果。

###### 下载数据

这里需要准备的数据分为两类，【白名单数据】、【黑名单数据】。

白名单数据指我们正常的PHP程序，黑名单数据指的是PHP Webshell程序。数据源还是我们的老朋友 github.com

在github上搜索PHP，可以得到很多的PHP的项目，咱们筛选几个比较知名和常用的。

白名单列表（一小部分）：

  * <https://github.com/WordPress/WordPress>
  * <https://github.com/typecho/typecho>
  * <https://github.com/phpmyadmin/phpmyadmin>
  * <https://github.com/laravel/laravel>
  * <https://github.com/top-think/framework>
  * <https://github.com/symfony/symfony>
  * <https://github.com/bcit-ci/CodeIgniter>
  * <https://github.com/yiisoft/yii2>

再继续搜索一下 Webshell 关键字，也有很多收集 Webshell 的项目。

黑名单列表（一小部分）：

  * <https://github.com/tennc/webshell>
  * <https://github.com/ysrc/webshell-sample>
  * <https://github.com/xl7dev/WebShell>

###### 创建工程文件夹

创建工程文件夹【MLCheckWebshell】，并在目录下创建【black-list】【white-list】文件夹。用于存放黑名单文件和白名单文件。

###### 提取opcode

我们创建一个utils.py 文件，用来编写提取opcode的工具函数。

工具函数1：

    
    
    def load_php_opcode(phpfilename):
        """
        获取php opcode 信息
        :param phpfilename:
        :return:
        """
        try:
            output = subprocess.check_output(['php.exe', '-dvld.active=1', '-dvld.execute=0', phpfilename], stderr=subprocess.STDOUT)
            tokens = re.findall(r'\s(\b[A-Z_]+\b)\s', output)
            t = " ".join(tokens)
            return t
        except:
            return " "

方法`load_php_opcode` 解读：

用Python 的subprocess 模块来进行执行系统操作，获取其所有输出，并用正则提取opcode，再用空格来连接起来

工具函数2；

    
    
    def recursion_load_php_file_opcode(dir):
        """
        递归获取 php opcde
        :param dir: 目录文件
        :return:
        """
        files_list = []
        for root, dirs, files in os.walk(dir):
            for filename in files:
                if filename.endswith('.php'):
                    try:
                        full_path = os.path.join(root, filename)
                        file_content = load_php_opcode(full_path)
                        print "[Gen success] {}".format(full_path)
                        print '--' * 20
                        files_list.append(file_content)
                    except:
                        continue
        return files_list

工具方法2 recursion_load_php_file_opcode
的作用是遍历目标文件夹内的所有的PHP文件并生成opcode，最后生成一个列表，并返回。

然后我们在工程目录下，创建train.py文件。

编写 prepare_data() 函数

    
    
    def prepare_data():
        """
        生成需要使用的数据，写入文件后，以供后面应用
        :return:
        """
        # 生成数据并写入文件
        if os.path.exists('white_opcodes.txt') is False:
            print '[Info] White opcodes doesnt exists ... generating opcode ..'
            white_opcodes_list = recursion_load_php_file_opcode('.\\white-list\\')
            with open('white_opcodes.txt', 'w') as f:
                for line in white_opcodes_list:
                    f.write(line + '\n')
        else:
            print '[Info] White opcodes exists'
    
        if os.path.exists('black_opcodes.txt') is False:
            black_opcodes_list = recursion_load_php_file_opcode('.\\black-list\\')
            with open('black_opcodes.txt', 'w') as f:
                for line in black_opcodes_list:
                    f.write(line + '\n')
        else:
            print '[Info] black opcodes exists'
    
        # 使用数据
    
        white_file_list = []
        black_file_list = []
    
        with open('black_opcodes.txt', 'r') as f:
            for line in f:
                black_file_list.append(line.strip('\n'))
    
        with open('white_opcodes.txt', 'r') as f:
            for line in f:
                white_file_list.append(line.strip('\n'))
    
        len_white_file_list = len(white_file_list)
        len_black_file_list = len(black_file_list)
    
        y_white = [0] * len_white_file_list
        y_black = [1] * len_black_file_list
    
        X = white_file_list + black_file_list
        y = y_white + y_black
    
        print '[Data status] ... ↓'
        print '[Data status] X length : {}'.format(len_white_file_list + len_black_file_list)
        print '[Data status] White list length : {}'.format(len_white_file_list)
        print '[Data status] black list length : {}'.format(len_black_file_list)
        # X raw data
        # y label
        return X, y

prepare_data 做了以下几个事：

  * 把黑名单和白名单中的PHP opcode 统一生成并分别写入到两个不同的文件中。
  * 如果这两个文件已经存在，那就不再次生成了
  * 把白名单中的PHP opcode 贴上 【0】的标签
  * 把黑名单中的PHP opcode 贴上 【1】的标签
  * 最后返回所有PHP opcode 的集合数据 X（有序）
  * 返回所有PHP opcode 的标签 y（有序）

##### 第三步：编写训练函数

终于到了我们的重点节目了，编写训练函数。

在这里先简单的介绍一下[scikit-learn](http://scikit-learn.org/)中我们需要的一些使用起来很简单的对象和方法。

  * CountVectorizer
  * TfidfTransformer
  * train_test_split
  * GaussianNB

CountVectorizer 的作用是把一系列文档的集合转化成数值矩阵。

TfidfTransformer 的作用是把数值矩阵规范化为 tf 或 tf-idf 。

train_test_split的作用是“随机”分配训练集和测试集。这里的随机不是每次都随机，在参数确定的时候，每次随机的结果都是相同的。有时，为了增加训练结果的有效性，我们会用到交叉验证（cross
validations）。

GaussianNB ：Scikit-learn 对朴素贝叶斯算法的实现。朴素贝叶斯算法是常用的监督型算法。

先上写好的代码：

    
    
    def method1():
        """
        countVectorizer + TF-IDF 整理数据
        朴素贝叶斯算法生成
        :return: None
        """
        X, y = prepare_data()
    
        cv = CountVectorizer(ngram_range=(3, 3), decode_error="ignore", token_pattern=r'\b\w+\b')
        X = cv.fit_transform(X).toarray()
    
        transformer = TfidfTransformer(smooth_idf=False)
        X = transformer.fit_transform(X).toarray()
    
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
    
        gnb = GaussianNB()
        gnb.fit(x_train, y_train)
        joblib.dump(gnb, 'save/gnb.pkl')
        y_pred = gnb.predict(x_test)
    
        print 'Accuracy :{}'.format(metrics.accuracy_score(y_test, y_pred))
        print metrics.confusion_matrix(y_test, y_pred)

代码介绍：

首先，我们用了刚才写的prepare_data()函数来获取我们的数据集。然后，创建了一个CountVectorizer
对象，初始化的过程中，我们告诉CountVectorizer对象，ngram的上下限为(3,3)
【ngram_range=(3,3)】，当出现解码错误的时候，直接忽略【decode_error="ignore"】，匹配token的方式是【r"\b\w+\b"】，这样匹配我们之前用空格来隔离每个opcode
的值。

然后我们用 `cv.fit_transform(X).toarray()` 来“格式化”我们的结果，最终是一个矩阵。

接着创建一个TfidfTransformer对象，用同样的方式处理一次我们刚才得到的总数据值。

然后使用`train_test_split`函数来获取打乱的随机的测试集和训练集。这时候，黑名单中的文件和白名单中的文件排列顺序就被随机打乱了，但是X[i]
和 y[i] 的对应关系没有改变，训练集和测试集在总数聚集中分别占比60%和40%。

接下来，创建一个GaussianNB 对象，在Scikit-learn中，已经内置好的算法对象可以直接进行训练，输入内容为训练集的数据（X_train） 和
训练集的标签（y_train）。

    
    
    gnb.fit(X_train, y_train)

执行完上面这个语句以后，我们就会得到一个已经训练完成的gnb训练对象，我们用测试集(X_test) 去预测得到我们的y_pred 值（预测出来的类型）。

然后我们对比原本的 y_test 和 用训练算法得到的结果 y_pred。

    
    
    metrics.accuracy_score(y_test, y_pred)

结果即为在此训练集和测试集下的准确率。

![](https://images.seebug.org/content/images/2018/02/1ad48c33-842a-4baf-a76c-92e4a0ead885.png-w331s)

约为97.42%

还需要计算混淆矩阵来评估分类的准确性。

    
    
    metrics.confusion_matrix(y_test, y_pred)

输出结果见上图。

编写训练函数到这里已经初具雏形。并可以拿来简单的使用了。

##### 第四步：持久化&应用

编写完训练函数，现在我们可以拿新的Webshell来挑战一下我们刚才已经训练好的gnb。

但是，如果每次检测之前，都要重新训练一次，那速度就非常的慢了，我们需要持久化我们的训练结果。

在Scikit-learn 中，我们用joblib.dump() 方法来持久化我们的训练结果，细心的读者应该发现，在method1() 中有个被注释掉的语句

    
    
    joblib.dump(gnb, 'save/gnb.pkl')

这个操作就是把我们训练好的gnb保存到save文件夹内的gnb.pkl文件中。

方面下次使用。

创建check.py

理一下思路：先实例化我们之前保存的内容，然后将新的检测内容放到gnb中进行检测，判断类型并输出。

核心代码：

    
    
        gnb = joblib.load('save/gnb.pkl')
        y_p = gnb.predict(X[-1:])

最后根据标签来判断结果，0 为 正常程序， 1 为 Webshell。

我们来进行一个简单的测试。

![](https://images.seebug.org/content/images/2018/02/794c91b8-25fd-4a67-9f0f-38953471c4e0.png-w331s)
![](https://images.seebug.org/content/images/2018/02/12ca1a86-c5ad-44f9-b42f-f40852ff2804.png-w331s)

那么，一个简单的通过朴素贝叶斯训练算法判断Webshell的小程序就完成了。

#### 下一步？

这个小程序只是一个简单的应用，还有很多的地方可以根据需求去改进

如：

在准备数据时：

  1. 生成 opcode过程中，数据量太大无法全部放入内存中时，更换写入文件中的方式。

在编写训练方法时：

  1. 更换CountVectorizer的ngram参数，提高准确性。
  2. 增加cross validation 来增加可靠性
  3. 更换朴素贝叶斯算法为其他的算法，比如MLP、CNN（深度学习算法）等。
  4. 在训练后，得到数据与预期不符合时：

重复增量型训练，优化训练结果。

  1. 增大训练数据量
  2. 如果对PHP opcode 有深入研究的同学可以采用其他的提取特征的方法来进行训练。
  3. 选择多种训练方法，看看哪一种的效果最好，而且不会过度拟合（over fitting）。 

#### 结语

最后咱们总结一下机器学习在Webshell 检测过程中的思路和操作。

  1. 提取特征，准备数据
  2. 找到合适的算法，进行训练
  3. 检查是否符合心中预期，会不会出现过度拟合等常见的问题。
  4. 提供更多更精准的数据，或更换算法。
  5. 重复1~4

本人也是小菜鸡，在此分享一下简单的思路和方法。希望能抛砖引玉。

项目下载地址：

<https://github.com/hi-WenR0/MLCheckWebshell>

参考链接：

[基于机器学习的 Webshell 发现技术探索](https://mp.weixin.qq.com/s/1V0xcjH-6V5qJoJILP0pJQ
"基于机器学习的 Webshell 发现技术探索")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/526/>

