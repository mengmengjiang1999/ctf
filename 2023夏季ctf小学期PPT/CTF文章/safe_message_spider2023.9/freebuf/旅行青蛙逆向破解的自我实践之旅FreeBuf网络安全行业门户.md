> 本文作者：i春秋作家[aaaasss](https://bbs.ichunqiu.com/space-uid-189899.html)

## 第一阶段

下面就开始了此次的心路历程：  

首先是看到了[https://paper.seebug.org/519/](https://bbs.ichunqiu.com/thread-34154-1-1.html?from=beef)，参照其中

### 1.下载游戏安装包

修改后缀为zip可用解压工具打开，发现存在 assets\bin\Data\Managed
目录（判断游戏应该为Unity游戏的一个特征）。据说此类游戏主要逻辑代码在 Assembly-Csharp.dll 中，所以主要分析的就是这个。

![1.png](https://image.3001.net/images/20180227/151972468077.png!small)

![2.png](https://image.3001.net/images/20180227/1519724739916.png!small)  

### 2.逆向工具

得知此类游戏为unity3d开发后（好像和传统的安卓逆向有些不同），在代码未混淆加密的情况下可以用.net的逆向工具dnspy分析其中的dll文件。
很幸运这里没有加密。工具自行百度吧，从官网还是挺好下的。这里稍稍拯救下伸手党： **[点此下载。](https://github-production-release-asset-2e65be.s3.amazonaws.com/38380854/c98564a0-f630-11e7-8ea5-b4a518cdcb1a?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20180209%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20180209T095159Z&X-Amz-Expires=300&X-Amz-Signature=72ff1bee1384cf992bbb68f76d2c6dca7459f1eda5f495b4f28c0862696892ad&X-Amz-SignedHeaders=host&actor_id=0&response-content-disposition=attachment%3B%20filename%3DdnSpy.zip&response-content-type=application%2Foctet-stream)**

打开Assembly-Csharp.dll后大概长这样。 如果为英文看着比较费劲，可以在视图中切换成中文。

![3.png](https://image.3001.net/images/20180227/15197247732976.png!small)  

### 3.抽奖券修改

第一眼还是有点不知所措，现在参考前面的教程可发现，他的思路是从抽奖券开始的，首先发现在抽奖券不足时会提示一串文字，看不懂没关系，能看到其中有个“足”字就ok。

![4.png](https://image.3001.net/images/20180227/15197248342882.png!small)  

这时如果没有更改界面，可以在旁边看到搜索框，选中当前的dll文件，再选择搜索字符串，搜索“足”即可发现找到了两个匹配项。

![5.png](https://image.3001.net/images/20180227/15197248551859.png!small)  

这里可猜测第一个是和抽奖券有关（字都一样好嘛），

![6.png](https://image.3001.net/images/20180227/15197248694323.png!small)  

第二个猜测和三叶草的数量有关（别问我咋猜的）

![7.png](https://image.3001.net/images/20180227/15197248859294.png!small)  

可看到这里有和抽奖券类似的判断

![8.png](https://image.3001.net/images/20180227/15197248994137.png!small)  

![9.png](https://image.3001.net/images/20180227/15197249132260.png!small)  

所以这里参照各种大佬的教程先从抽奖券开始吧

由于这里可以看到是对TicketStock()进行的判断，

![10.png](https://image.3001.net/images/20180227/15197249292721.png!small)  

点击即可跳转到相关方法，猜测这里表示奖券的库存，

![11.png](https://image.3001.net/images/20180227/15197249565844.png!small)  

可看到是返回的

return SuperGameMaster.saveData.ticket; 再点击

![12.png](https://image.3001.net/images/20180227/15197250126144.png!small)  

搜索，然后一个一个找

![122.png](https://image.3001.net/images/20180227/15197252571593.png!small)

这里大概为对奖券数量的初始化

![13.png](https://image.3001.net/images/20180227/15197250266397.png!small)

这里可以修改奖券的初始值，参照开篇提到的教程，可改成一个比较大的值，但奖券终究有花完的一天，而且即使改成1000，花的也非常快，后面会讲到。
这里猜测还会限制奖券获得的数量，（所以那些玩正常版本的小伙伴们啊，有奖券赶紧花，最多就只能攒999个，手动滑稽）。

![14.png](https://image.3001.net/images/20180227/15197250559714.png!small)

但这里要说就要说骚玩法，那就是开篇教程的第二种修改方式，将数量写死在代码里，因为已知抽奖的时候奖券是从SuperGameMaster.TicketStock()获取的，令其返回值为固定的数值。这里找到该方法，右键选择编辑IL指令。  

![15.png](https://image.3001.net/images/20180227/15197250565428.png!small)

选中第一条，删除  

![16.png](https://image.3001.net/images/20180227/15197250565394.png!small)

操作码换成ldc.14，说人话就是这个操作码可以改成各种整数（也许太大会溢出吧）这几个操作码有啥区别见图，这里改个大于5的数，够抽就行了，反正不会变，低调些就改个20吧，改完确定。  

![17.png](https://image.3001.net/images/20180227/15197250561453.png!small)

![18.png](https://image.3001.net/images/20180227/15197254413100.png!small)

### 4.修改三叶草

同理改可改上方三叶草逻辑，一样的操作一样的方法，不赘述

![19.png](https://image.3001.net/images/20180227/15197254618436.png!small)  

截至目前，第一阶段完成，基本可以玩耍了，打包签名后就尝试了一下（后续会提到如何打包签名）。

人总是贪婪的！曾经我也以为到这里就可以开心的玩耍了，开心地玩了几天，花不完的钱，抽不完的奖券，开心。  
但是！！！随之而来的一些体验依旧让人感觉不爽：

##  **第二阶段 优化游玩体验**

首先，少了可玩性（虽然本来就没多少可玩的），如果把三叶草的值写死，采集三叶草就完全没有意义了，这里承接前文，再往上翻了翻，看到了这段代码：

![20.png](https://image.3001.net/images/20180227/1519725482985.png!small)  

接着猜测这里是采集三叶草的判断，修改为直接增加888，就可以在采集时直接增加888三叶草：

![21.png](https://image.3001.net/images/20180227/15197255658123.png!small)  

![22.png](https://image.3001.net/images/20180227/15197256544067.png!small)  

其次是抽奖券

 **1.无聊的重复性劳动：**

有了抽奖券只是可以去抽各种颜色的球，至于抽到什么颜色的球概率不同，比如黄球的概率极其低，这里如果像上文所说的把奖券改成一个大的数字，比如1000，可能抽完了也不一定能遇到黄球，青蛙还怎么能愉快的旅行！这就是为什么要改为一个固定值，可以无限抽。

那么虽然现在可以无限抽了，但是抽奖这种事，目的是为了获得奖品，有时候为了多抽几个黄球的车票需要抽很久，这种枯燥无聊的重复性劳动，肯定不是我们想要的。

有了这种需求，自己首先考虑了用自动化的方式去完成这种无聊的工作，此处借鉴了前段时间写的微信跳一跳外挂。用的安卓手机（苹果不了解），可以利用adb模拟点击来进行抽奖和随机的物品选择。写起来不难，大家可以自我尝试下，python实现还是挺容易的。这里承认自己代码写的比较糙，不够赏心悦目就不贴出来丢人了，实在有需要可以尝试留言或私信我啥的(虽然我不一定回，由于分辨率你的手机也不一定适用)。自己仅做了简单的实现和初步的不科学的统计，可能以后有空会考虑到球颜色精确识别和物品的精确选择吧，大致效果：

![23.png](https://image.3001.net/images/20180227/15197256112025.png!small)  
  

 **2.有用球的概率奇低：**

有了上述改进依旧不能解决很难抽到小概率球的问题，比如黄球和红球，有时候脚本跑了个把小时，蓝球都好几十个黄球却只有两三个。于是接着翻翻，看看有没有什么新发现。

这里游戏中对各种球的称呼为青玉黄玉啥的，这里尝试搜索一下“玉”，果然有发现。

![24.png](https://image.3001.net/images/20180227/15197257292364.png!small)  

往上翻发现了疑似各种球概率的定义（黄球1%……）：  

![25.png](https://image.3001.net/images/20180227/15197257606419.png!small)  

话不多说同样的方式尝试进行修改，  

![26.png](https://image.3001.net/images/20180227/15197258049640.png!small)  

0x3c是60，0x1b是27，然后是9，3，1,找到对应的即可修改为想要的值，这里改成了1，24，25，25，25：  

![27.png](https://image.3001.net/images/20180227/15197258194845.png!small)  

![28.png](https://image.3001.net/images/20180227/15197258339399.png!small)  

至此需求已经解决

其他：这里貌似是来看望伙伴给礼物的概率，一般伙伴和稀有伙伴:  
其实四叶草也还是有点用的，可以尝试改一改

![29.png](https://image.3001.net/images/20180227/15197258686968.png!small)

![30.png](https://image.3001.net/images/20180227/15197258866557.png!small)  

这里貌似定义了青蛙的休息时间之类的，也可以尝试尝试，但也许会出现不可预知的问题

![31.png](https://image.3001.net/images/20180227/15197259026604.png!small)  

  
血量，旅行时间拍摄时间啥的。。。。啧啧啧，改完你的蛙就是旅行达人了，不过逻辑复杂说不定会出现未知的状况就没继续探究了

![32.png](https://image.3001.net/images/20180227/1519725939561.png!small)  

然后是打包与签名：

解包和打包用的apktool.jar:

apktool.jar d apkfile.apkapktool.jar b
path签名用的signapk.jar，密钥找了个现成的，或者用别的工具也可以只要签名了就行:

    
    
    signapk.jar pubkey selfkey signapk.apk signed.apk

下载链接：
[](https://github.com/iBotPeaches/Apktool/releases/download/v2.3.1/apktool_2.3.1.jar)

[https://github.com/iBotPeaches/A ...
1/apktool_2.3.1.jar](https://bbs.ichunqiu.com/thread-34154-1-1.html?from=beef)

所以全程是解包--修改--打包--签名--安装，缺一不可，工具还有更详细用法还是自行百度吧，或者留言私信我啥的，虽然并不一定能及时看到，看到也并不一定回：）  
以上

###  **题外:**

如果遇到，路径\assets\bin\Data\Managed\没有Assembly-Csharp.dll这些的游戏，还能用这些方法吗？为什么同为unity游戏这个却没有？该如何入手？什么思路？感谢解答  

![33.png](https://image.3001.net/images/20180227/151972596450.png!small)  

### 参考：

[](https://link.jianshu.com/?t=http%3A%2F%2Fgslab.qq.com%2Farticle-396-1.html)

[http://gslab.qq.com/article-396-1.html](https://bbs.ichunqiu.com/thread-34154-1-1.html?from=beef)

[https://paper.seebug.org/519/](https://bbs.ichunqiu.com/thread-34154-1-1.html?from=beef)

