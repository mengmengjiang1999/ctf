**最近，朝鲜声名狼藉的APT组织Lazarus又开始活跃起来，先是入侵印度核电站，导致其紧急关闭一座反应堆，然后又向韩国、意大利等国发送大量钓鱼邮件进行攻击，加上今年年初的数字货币交易所入侵事件，Lazarus今年可谓是很“高产”了。鉴于我国也曾在Lazarus的攻击范围之内，下面就来了解下Lazarus组织的攻击手法，以及学习如何对其进行追踪。**

## APT组织概述

Lazarus别名APT38、Guardians of
Peace，是隶属于朝鲜的一个APT组织。据一位叛逃到韩国的朝鲜计算机科学教授透露，该组织的成员主要来源于朝鲜RGB海外情报机构的Unit
180部队，主要负责以获得外汇为目的的攻击。

![](https://image.3001.net/images/20191125/1574645187_5ddb2dc37cdf7.png!small)

Lazarus组织自2009年就已经开始有活动，不过早期主要是针对美国、韩国进行政治攻击，后续攻击目标渐渐扩大到印度、菲律宾、越南、孟加拉等亚洲及欧洲国家。

![](https://image.3001.net/images/20191125/1574645205_5ddb2dd517d7e.png!small)

然而，Lazarus真正映入我们眼帘的其实是2014年的索尼影业入侵事件，2014年，索尼影业在Youtube上首发了电影《刺杀金正恩》的预告片，引起了朝鲜人民强烈不满，仅仅10天之后，Lazarus就入侵了索尼影业，泄露了大量的还未发行的影片资料，以及高管间的秘密邮件和员工的隐私信息，逼得索尼影视娱乐公司不得不宣布取消了该电影的发行和放映计划。

自这次事件之后，Lazarus逐渐衍变成了一个全球性的黑客组织，先后导演了入侵孟加拉国央行账号、使用WannaCry大范围勒索、攻击5大数字货币交易所、破坏印度KNPP核电站的重大安全事件。安全界厂商认为，Lazarus的影响已经远非一般APT组织所能及。

![](https://image.3001.net/images/20191125/1574645222_5ddb2de6b196b.png!small)

## 攻击组件演变

### 2013 -- DarkSeoul

Lazarus早期的攻击组件，以DarkSeoul为代表的DDoS恶意软件为主，攻击对象为韩国的媒体、金融、基础设施行业。

### 2014 -- Destover

在索尼影业入侵事件中，攻击者使用了一系列的攻击组件进行信息窃取、主机擦除，其中，有一个MBR擦除组件（如下图）Destover的部分代码与之前Lazarus用到的攻击组件有大量重叠的地方，也基于此，安全厂商确定该次攻击样本来自于Lazarus之手。

![](https://image.3001.net/images/20191125/1574645259_5ddb2e0b2f49d.png!small)

### 2016 -- Alreay

在盗窃孟加拉国央行的行动中，Lazarus通过Alreay攻击组件篡改SWIFT软件，使得黑客能够操作银行账号任意进行转账，从而窃取了8100万美元。

![](https://image.3001.net/images/20191125/1574645278_5ddb2e1e80239.png!small)

### 2017 -- WannaCry

在最早版本的WannaCry病毒中，安全厂商发现了其中存在着Lazarus使用过的代码，从而判断该病毒是由Lazarus制作的。该细节被公布后，后续版本的WannaCry也将这段代码去除。

![](https://image.3001.net/images/20191125/1574645297_5ddb2e312bb85.png!small)

### 2019 -- Worldbit-bot

Worldbit-bot基于开源数字货币交易软件Qt Bitcoin Trader进行篡改，窃取账户敏感信息。

### 2019 -- Dtrack

Dtrack是Lazarus用来攻击印度核电站所使用的RAT，该攻击组件与ATMDtrack十分相似，后者曾被用来入侵某印度银行。该RAT会打包收集主机敏感信息并上传。

## APT追踪

对APT组织进行追踪需要一定的积累，只有熟悉了该组织的常用攻击手法（TTPs），才能在新型的攻击中将其辨识出来。其中，通过样本共用代码段进行关联是最高效的方式，这也突显了使用yara规则进行样本分析的好处。

首先，我们需要从已有的样本中筛选出相同的特征码，可以使用Bindiff来比较已有样本相似的代码片段，如下：找到相似度较高且不是系统API的函数。

![](https://image.3001.net/images/20191125/1574645338_5ddb2e5a9b012.png!small)

然后优先选取Blocks数较多、匹配指令数较多的函数。

![](https://image.3001.net/images/20191125/1574645352_5ddb2e68c7d74.png!small)

![](https://image.3001.net/images/20191125/1574645361_5ddb2e71ccc23.png!small)

可以重点挑选一些加密算法代码作为特征码，这样比较没那么容易误报。除此之外，也可以使用一些自动化提取yara规则的工具可以使用，比如yargen：<https://github.com/Neo23x0/yarGen>。

![](https://image.3001.net/images/20191125/1574645376_5ddb2e80a86a9.png!small)

如下，是提取出来的wannacry的特征码，可以在VT上进行关联，来追踪Lazarus的相似攻击组件。

![](https://image.3001.net/images/20191125/1574645392_5ddb2e9054108.png!small)

在VT搜索框中，输入：content:"{51 53 55 8B 6C 24 10 56 57 6A 20 8B 45 00 8D 75 04 24 01
0C 01 46 89 45 00 C6 46 FF 03 C6 06 01 46 56
E8}"，就能筛选出所有具有这个代码片段的样本，直到今年7月份，都还有相关的样本活跃。

![](https://image.3001.net/images/20191125/1574645407_5ddb2e9f64b35.png!small)

打开详细信息，发现这是Lazarus用于攻击孟加拉国的alreay攻击组件，那么也就说明，WannaCry和Alreay确实有共用的代码片段，通过这种方式，就可以关联出Lazarus所使用的攻击组件。

![](https://image.3001.net/images/20191125/1574645422_5ddb2eae41532.png!small)

将yara规则添加到hunting中，一旦VT捕获到新的样本符合这条规则，就会立刻通知我们。

![](https://image.3001.net/images/20191125/1574645437_5ddb2ebdca64e.png!small)

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

