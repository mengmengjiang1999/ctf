## 准备工作

因为目标站点只能用微信打开，微信又不能调试看代码。这里推荐可以使用pc端旧版微信3.2.1，具体方法放链接里：

> <https://blog.csdn.net/qq_45863248/article/details/127688137>

![](https://image.3001.net/images/20230713/1689212756_64af5754dfa6e49247b8a.jpg!small)

需要注意的是，如果作者方法未生效，可以把pak文件放微信安装目录再重启试试。

看到Show DevTools就说明成功啦！

![](https://image.3001.net/images/20230713/1689213443_64af5a037d963da7ef726.png!small)

## 开始测试

首先看到微信小游戏先游戏流程先走一遍抓个包。在手机微信上点击开始游戏：

![1689216059_64af643bb24a47d6a584d.png!small?1689216060822](https://image.3001.net/images/20230713/1689216059_64af643bb24a47d6a584d.png!small?1689216060822)

把上面的图形对应滑到下面的棒冰上制作成功棒冰+1

![1689218943_64af6f7fb7e59d6bb14ac.png!small?1689218944809](https://image.3001.net/images/20230713/1689218943_64af6f7fb7e59d6bb14ac.png!small?1689218944809)

每制作一根棒冰发送一个包（我这里制作了两个）：

![1689215942_64af63c672f38c2ec34f8.jpg!small?1689215942794](https://image.3001.net/images/20230713/1689215942_64af63c672f38c2ec34f8.jpg!small?1689215942794)

![1689216184_64af64b8afa3619675eba.png!small?1689216185183](https://image.3001.net/images/20230713/1689216184_64af64b8afa3619675eba.png!small?1689216185183)

页面倒计时结束后，变量boxNum统计制作了多少根棒冰，然后发送

![1689216208_64af64d02fbf2d60436b3.png!small?1689216208469](https://image.3001.net/images/20230713/1689216208_64af64d02fbf2d60436b3.png!small?1689216208469)

这里我们看到boxNum参数是加密了的，有理由怀疑最终制作个数就是由boxNum来控制的

打开pc端旧版微信调试工具，全局搜索，发现并未找到这个变量![1689215817_64af6349106457fb5c80e.png!small?1689215818443](https://image.3001.net/images/20230713/1689215817_64af6349106457fb5c80e.png!small?1689215818443)

懵了，我还以为出了什么问题，反复找了半天，发现也并没有游戏相关的js。在旧版pc端微信点开始游戏抓包，终于是发现了game.js，全局搜索boxNum，居然在这里。与之前不同的是，它不会一次性加载显示所有js，游戏开始后才加载的。

![1689217218_64af68c25cfb394dde921.png!small?1689217219427](https://image.3001.net/images/20230713/1689217218_64af68c25cfb394dde921.png!small?1689217219427)

  

分析加密逻辑，直接找f函数，搜索function f：

![1689218316_64af6d0c00919925f7b6a.png!small?1689218316379](https://image.3001.net/images/20230713/1689218316_64af6d0c00919925f7b6a.png!small?1689218316379)

发现是AES加密，自定义了icon1，icon2两个未知变量，需要加密就必须知道这两个变量，同样，在这个game.js和之前的js里均未搜到这两个变量。于是游戏里继续抓包，发现rem.js，看到icon1、icon2均是固定的。

![1689218413_64af6d6de0c652a56cd7a.png!small?1689218414274](https://image.3001.net/images/20230713/1689218413_64af6d6de0c652a56cd7a.png!small?1689218414274)

这下好办了，直接本地环境搭起来，先试试开头的我制作的棒冰数量2加密与数据包对比一下。

![1689218675_64af6e73c88810b4bf3b8.png!small?1689218676689](https://image.3001.net/images/20230713/1689218675_64af6e73c88810b4bf3b8.png!small?1689218676689)

![1689218627_64af6e43e4d24c52fab3d.png!small?1689218628235](https://image.3001.net/images/20230713/1689218627_64af6e43e4d24c52fab3d.png!small?1689218628235)

完全一样！测试结束。

