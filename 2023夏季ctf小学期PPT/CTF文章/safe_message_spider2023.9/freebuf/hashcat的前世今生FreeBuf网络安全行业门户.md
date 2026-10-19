Hashcat是一款基于GPU进行快速密码破译的开源软件。目前官网更新的最新版本是hashcat 4.1.0。我们可以在官网上找到3.00及之后的版本。

Hashcat是这世界上最快的报也是最先进的密码恢复工具。有一个好的密码字典的话，我们可以很容易的从一个大型密码列表中，破译出超过百分之九十的密码。Hashcat当前最新的版本是4.1.0，这一版本其实是把基于CPU的hashcat（现在叫hashcat-legacy）和基于GPU的oclHashcat结合起来，我们在安装的时候，它会根据机器硬件情况，自动生成多线程版本的hashcat或者是生成ocl版本的hashcat。如果大家想要安装hashcat可以在<https://hashcat.net/hashcat/>下载源码。

Hashcat是在2009年写出来的，在`hashcat`出现之前，已经有很多接近完美的工具了，比如“PasswordPro”，”John The
Ripper”。但是由于某些不为人知的原因，这两个工具都不支持多线程。于是就出现了利用现代CPU的多个内核进行运算的hashcat。

下面我们以4.1.0版本的hashcat为例，了解一下它的功能。

## Hashcat组件发展简史

### Hashcat

`Hashcat-legacy`是一个基于CPU的密码恢复工具。Hashcat是在2009年写出来的，在`hashcat`出现之前，已经有很多接近完美的工具了，比如“PasswordPro”，”John
The Ripper”。但是由于某些不为人知的原因，这两个工具都不支持多线程。于是就出现了利用现代CPU的多个内核进行运算的`hashcat`。

当然了，hashcat进行密码破译并不是百分百正确，`John the
Ripper`也可以通过补丁来支持MPI，只不过它只能用于暴力破解攻击，对于那些通过基于规则的攻击支持MPI的MD5，`John the
Ripper`并没有合适的方法进行破解。

Hashcat的第一个版本，叫做“atomcrack”。这个版本特别简单，功能也非常单一，但是最起码它的MD5内核是多线程的。atomcrack破解MD5只用到了最简单简单的字典攻击，但是`atomarack`的攻击速度非常快。发行`hashcat`第一版一段时间之后，逐渐增加了更多的算法类型，一个字典变种的规则引擎，还增加了一个windows版本和不同攻击模式。`Hashcat`的这些发展大概花费了半年时间，而且完全是非公开的。

在0.29版本中，“atomcrack”更名为“Dr.Hash”，直到2009年12月24日发布了第一版官方正式版 `hashcat`
0.30,才正式更名为“hashcat”。

2012年8月5日发布了`hashcat` 0.40,在这个版本中增加了Mac OXS二进制。也正是这样一点一点形成我们现在使用的`hashcat`。

### OclHahcat

Hashcat的另一个组成部分是`oclHashcat`，它是一个基于GPGPU的多哈希破解程序。它的功能包括暴力攻击，组合攻击，字典攻击，掩码攻击和基于规则的攻击等。这个GPU
cracker是`oclHashcat-plus`和`oclHashcat-lite`的融合版本，这两个工具都是很致命的组件，现在已经被弃用了。

oclHashcat的主要问题与它的体系结构有关。`oclHashcat`是专为Combinator攻击设计的，它对于高速算法很有效，但是和慢速算法结合就会变得低效。

正因为这一原因，人们仍然习惯使用基于CPU的`hashcat`，因为`hashcat`可以使用简单的字典攻击。要想在GPU上进行基于字典的攻击，首先要解决的问题就是oclHashcat的算法问题。而这一问题的解决方案是创造全新的方法`oclHashcat-plus`。在这一过程中oclHashcat开发者提出了一个非常专业化的GPU cracker即`oclHashcat-lite`，它专注于掩码攻击和强力攻击。这个工具专注于单个hash值的分析。为了让用户受到更少的限制，会与`oclHashcat-plus`并行存在。

GPU上的字典攻击确实会对MD4,MD5这样的快速算法很有效，但是效率并没有那么高，因为把单词表上传到GPU需要更多的时间，所以在CPU上攻击这些快速算法就可以了，但是像md5crypt，phpass这样的慢速算法，在GPU上的运行速度就非常快。这是因为这些算法在设计时候就会降低它的可碰撞性。

2013年12月6日，发布了oclHashcat1.00版本，开发人员宣称这一版本融合了`oclHashcat-lite`的优势，同时拥有`oclHashcat-plus`的一些功能。对于某些类型的hash值， `oclHashcat`
1.00的破解速度与`oclHashcat-lite`相当，甚至有可能更快。也正是从1.00版本开始，oclHashcat代替了`oclHashcat-lite`和`oclHashcat-plus`的功能。也就是说`oclHashcat`是这两个组件的合并版本。

oclHashcat的另一个主要特点是基于GPU的规则引擎。有了这个引擎就可以进行基于规则的攻击。

快速算法利用基于GPU的规则引擎来提高GPU利用率。使用这种策略，在GPU上的简单的字典攻击都会变得高效。
GPU上的规则引擎速度非常快。根据规则本身，您可以达到与`oclHashcat`中的combinator攻击几乎相同的速度。这是一个独一无二的功能，可以抵御其它的hash
cracker。

慢速算法利用基于CPU的规则引擎来增加单词表的大小。这样就可以用非常小的字典进行攻击。这些小字典其实是由规则引擎在内存中扩展出来的。这样我们就可以忽略把单词表存储到GPU的时间。

经过上述发展，`oclHashcat`变得有一点像基于CPU的`hashcat`。

## hashcat的基础命令及使用

### hashcat的基础命令

    
    
    -h/--help：显示联机帮助
    
    -m/--hash-type:Hash类型，比如：md4(900),md5(0),SAH-1(100),SHA-512(1700)等等。
    
    -v/--version:打印系统的版本信息
    
    --quite:
    
    -a/--attack-mode:破译模式，包括直接攻击模式（0），组合模式（1），大小写转换（2），暴力破解攻击（3）等等。(举例：-a 0)
    
    -o/--outfile:定义文件运行输出的文件
    
    -b/--benchmark：运行测试
    
    --remove:把破译出的密码从密码列表中移除。
    

关于命令的用法，后面的文章可以结合实例详细分析一下。

### Hashcat的使用（-a 0）

Kali里面有自带的hashcat，我们可以找一个小字典尝试一下密码匹配。来体验一下hashcat的功能。

![1.png](https://image.3001.net/images/20180523/15270709185180.png!small)

我们用Top109Million的字典，匹配密码.txt文件中的密码，并把匹配出的结果输出到outfile文件中。

![2.png](https://image.3001.net/images/20180523/15270709389597.png!small)

通过-o命令，破译出的密码和匹配到的明文会直接写入outfile文件中。而--remove命令会筛出还没有破译的密码，从密码表中移除已经破译的密码。

![3.png](https://image.3001.net/images/20180523/15270709828382.png!small)

### 实验过程中踩到的小水坑

正常情况下，-o
命令会把匹配出的密码输出到outfile文件，但是在我的实验过程中，出现了一个问题，即没有在路径下生成outfile文件。这是因为hashcat在破译密码的过程中，会把破译的结果缓存到potfile文件，当下次破译遇到同样的密码表，会从potfile文件中直接获取。破译结果就如下存储在potfile文件中。

![4.png](https://image.3001.net/images/20180523/15270709962600.png!small)

![5.png](https://image.3001.net/images/20180523/1527071011107.png!small)

potfile中会有本次破译出的密码和对应的结果。  

![6.png](https://image.3001.net/images/20180523/15270710514930.png!small)

通过--potfile-disable命令进行设置即可。

![7.png](https://image.3001.net/images/20180523/1527071038377.png!small)

除了使用单一字典进行密码破译，`hashcat`还可以进行字典间的组合攻击。尝试一下用多字典组合攻击,以及基于规则的攻击。但是由于虚拟机环境的限制，所以运行效果并不理想。

所以我在本机linux系统中配置了`hashcat`，利用GPU破译密码。大家感兴趣的话,下次可以分享一下hashcat安装过程中趟过哪些坑。

本文作者：EVA。本文属丁牛网安实验室原创出品，如需转载请标明作者及来源。  

