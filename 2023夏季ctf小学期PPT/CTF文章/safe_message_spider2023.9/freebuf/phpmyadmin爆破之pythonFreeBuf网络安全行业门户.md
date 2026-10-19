## **前言：**

在一个秋高气爽的上午，佛系的我在做着佛系的事，正喝着猫屎咖啡(wocao)，城里人真会玩，有没有鸡屎coffee。。。突然一个安服的美女给我发来一个微信，我来以为的约我看电影呢，上来一句就说原来的phpmyadmin后台登录爆破工具不行了。

还给我发来个工具的截图：

![1610437075_5ffd51d3c0da76c25cacd.png!small](https://image.3001.net/images/20210112/1610437075_5ffd51d3c0da76c25cacd.png!small)

想着闲着也是蛋疼，那既然美女开口了，那我就看看呗

这个工具是个老古董，现在都神马年代了。phpmyadmin早就更新了，爆破不了，那也是正常的。

##  **正式开始：**

废话不多说，我们先开始搭建测试环境，先是下载phpstudy集成环境。

这里需要注意：由于phpmyadmin4.8.5以上的版本，需要php7.5以上环境才能运行。

所以这里需要搭建两套环境。

我们这里分别运行两个虚拟机：

一个环境是php2016 + php7.0 + mysql + 自带的phpmyadmin(版本小于4.8.5)

![1610437091_5ffd51e3ecd93d7909afe.png!small](https://image.3001.net/images/20210112/1610437091_5ffd51e3ecd93d7909afe.png!small)

看看能否正常访问：

![1610437140_5ffd521423608c3c9536c.png!small](https://image.3001.net/images/20210112/1610437140_5ffd521423608c3c9536c.png!small)

另一个环境是最新版的phpstudy + phpmyadmin4.8.5

![1610437156_5ffd522442e63367c0f0c.png!small](https://image.3001.net/images/20210112/1610437156_5ffd522442e63367c0f0c.png!small)![1610437167_5ffd522f87e9d2854aac1.png!small](https://image.3001.net/images/20210112/1610437167_5ffd522f87e9d2854aac1.png!small)

首先，祭出我们的爆破神器，burp爆破看看：

先爆破phpmyadmin4.7版本：

先抓包：

![1610437179_5ffd523b03b162c32b865.png!small](https://image.3001.net/images/20210112/1610437179_5ffd523b03b162c32b865.png!small)

开始加载字典爆破：

![1610437186_5ffd5242a9f64e7f821c1.png!small](https://image.3001.net/images/20210112/1610437186_5ffd5242a9f64e7f821c1.png!small)

返回的长度好多。。。

再看看正确密码的返回值：

![1610437217_5ffd52615e57aa640d10e.png!small](https://image.3001.net/images/20210112/1610437217_5ffd52615e57aa640d10e.png!small)

正确的密码和错误的密码。返回的包和长度都是一样，无法分别。

同理，burp爆破最新版的也不行。。。

陷入了深深的沉思。

 **不放弃**

既然burp不行，那我们就上万能的python。以爬虫的思路，去构造包，看看正确密码和错误密码，有哪些不一样。

经过抓包分析：新老版本最大的变化就是4.8.5及以上版本会有一点差别：

新版本会多一个参数set_session

![1610437236_5ffd5274511f324720a40.png!small](https://image.3001.net/images/20210112/1610437236_5ffd5274511f324720a40.png!small)

![1610437244_5ffd527c1e5692abf641c.png!small](https://image.3001.net/images/20210112/1610437244_5ffd527c1e5692abf641c.png!small)

加下来就开始写破解的python脚本：

核心代码如下：

![1610437254_5ffd52865bbb905ce07f7.png!small](https://image.3001.net/images/20210112/1610437254_5ffd52865bbb905ce07f7.png!small)

![1610437262_5ffd528e71baa848834a1.png!small](https://image.3001.net/images/20210112/1610437262_5ffd528e71baa848834a1.png!small)

![1610437272_5ffd52986389851a0eebf.png!small](https://image.3001.net/images/20210112/1610437272_5ffd52986389851a0eebf.png!small)

先找token，再找是否有set_session参数，以此来判断新老版本，从而构造不同的paylaod。

新版本的构造的payload。

![1610437290_5ffd52aa6e70163d18d7d.png!small](https://image.3001.net/images/20210112/1610437290_5ffd52aa6e70163d18d7d.png!small)

准备就绪：

开始测试：

![1610437302_5ffd52b669492df37a116.png!small](https://image.3001.net/images/20210112/1610437302_5ffd52b669492df37a116.png!small)

收官。。。

兴奋的发给妹子呗。。。

妹子居然给我来一句，大哥哥(叫得我心痒痒)，这个我不会用，能不能搞成(我一直感觉搞子不是很好听，邪恶的我呀~~~)，那换成弄字。好像也不咋的。

言归正传，虽然我不好色，但是美女的力量还是无限的，既然美女发话了，那我就继续干~干干~~吧

进行python改造，引入 **import** tkinter **as** tk

![1610437312_5ffd52c0ec1ff056fe638.png!small](https://image.3001.net/images/20210112/1610437312_5ffd52c0ec1ff056fe638.png!small)

写到类里面：

![1610437320_5ffd52c8bd0a04e1b3af7.png!small](https://image.3001.net/images/20210112/1610437320_5ffd52c8bd0a04e1b3af7.png!small)

然后就是布局，不一一介绍了。

运行一下exe看看：

![1610437337_5ffd52d90c2b72ceb7e1c.png!small](https://image.3001.net/images/20210112/1610437337_5ffd52d90c2b72ceb7e1c.png!small)

这个就是个装逼的界面，啥用也没有，就是想在美女面前装下逼。

![1610437343_5ffd52df83799cd31c29b.png!small](https://image.3001.net/images/20210112/1610437343_5ffd52df83799cd31c29b.png!small)

本来是打算远程从VPS上加载用户名和密码的，怕泄露VPS地址，就不搞了。。。

输入用户名admin 密码：Jeffcheng

![1610437355_5ffd52ebb3d21e5bab0db.png!small](https://image.3001.net/images/20210112/1610437355_5ffd52ebb3d21e5bab0db.png!small)

不好意思，这个密码是大姐( J )开头，我写成了小姐。

登录进去后，输入待爆破的url

http://192.168.0.5/phpmyadmin4.8.5/

开始爆破：

![1610437364_5ffd52f4aee91afb5adfa.png!small](https://image.3001.net/images/20210112/1610437364_5ffd52f4aee91afb5adfa.png!small)

爆破成功后弹窗。

![1610437372_5ffd52fcd9345d83cac85.png!small](https://image.3001.net/images/20210112/1610437372_5ffd52fcd9345d83cac85.png!small)

字典要是跑完了，没成功的话，怎么办？

那就赶紧跑路吧，兄弟。。。

