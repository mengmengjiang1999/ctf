作者：[浮萍@猎户安全实验室](https://mp.weixin.qq.com/s/92z8oMpvvcDmp3vaqeD7mw
"浮萍@猎户安全实验室")

#### 0x01 前言

最近一款养蛙的游戏非常火，但是语言是日文的。下载了一个汉化的，结果广告一大堆。反编译之后查看是Unity游戏，之前没接触过，就想着跟着看一下。关于这类的破解，可以在52pojie上进行搜索。有很多类似的案例。

这里主要采用的工具为dnSpy，dnSpy 是一款针对 .NET 程序的逆向工程工具。反编译和打包采用的是apktool，当然也可以直接用改之理等工具。

虽然本文以一个小游戏为实例，但这个思路值得安全渗透人员借鉴。

#### 0x02 修改数据

下载app后重命名为zip文件，发现存在`assets\bin\Data\Managed`目录，那么该游戏应该为Unity游戏。

![](https://images.seebug.org/content/images/2018/01/b17faab0-fe78-4683-89c9-9c547d80a261.jpg-w331s)

那么需要分析的文件就是就是`Assembly-CSharp.dll`。

首先修改一下抽奖券的数量。安装游戏后，找到抽奖的地方。抽奖的时候提示券不足。

![](https://images.seebug.org/content/images/2018/01/2e0c2d5a-131f-4206-bb9a-750c62b80dfb.jpg-w331s)

使用dnSpy打开`Assembly-CSharp.dll`文件，然后搜索字符串”足”，可以发现有两个，打开后发现是第一个。

![](https://images.seebug.org/content/images/2018/01/dcf6eeea-05a3-4978-804b-2faa79ae12eb.jpg-w331s)

由此可以猜测TicketStock代表抽奖券库存。

![](https://images.seebug.org/content/images/2018/01/c91328fc-1f79-44a2-94dd-f5c37097c4c7.jpg-w331s)

ticket表示抽奖券数量。

![](https://images.seebug.org/content/images/2018/01/69907d83-6330-4e3f-9f09-4a1b7fbaa147.jpg-w331s)

当页查找ticket，发现有一个initialize方法进行初始化。我们将此处的数量改为1000.

![](https://images.seebug.org/content/images/2018/01/64fda4da-1893-47fb-af8e-f972e8654407.jpg-w331s)

快捷键Ctrl+E编辑IL指令。找到ticket变量后，将ldc.i4.0改为ldc.i4，然后将数值改为1000.

![](https://images.seebug.org/content/images/2018/01/fe240c5f-2c68-4501-9f0b-13fc95885cfd.jpg-w331s)

确定后，发现ticket数值已经改变。

![](https://images.seebug.org/content/images/2018/01/f81d81af-83e4-43b5-8452-229ca9be8eb7.jpg-w331s)

打包后并安装apk。

![](https://images.seebug.org/content/images/2018/01/d6183a50-1da4-4358-9259-fddf16fd9568.jpg-w331s)

打开抽奖界面发现数量已经改变为1000。

![](https://images.seebug.org/content/images/2018/01/6b47ded0-85a7-47f1-bada-6f8567520c52.jpg-w331s)

这样虽然达到了修改抽奖券的效果，但数量再大，总会被抽完的。那就换种方法，比如说抽奖的时候增加奖券，或者奖券一直不变。这里采用奖券数量固定的方法，使其不会变动。

    
    
    if (SuperGameMaster.TicketStock() < 5)
    
    {
    
       ConfilmPanel confilm = this.ConfilmUI.GetComponent<ConfilmPanel>();
    
       confilm.OpenPanel("ふくびき券が足りません");
    
       confilm.ResetOnClick_Screen();
    
       confilm.SetOnClick_Screen(delegate
    
       {
    
           confilm.ClosePanel();
    
       });
    
       return;
    
    }

已知抽奖的时候奖券是从`SuperGameMaster.TicketStock()`获取的，找到该方法。令其返回值为固定的数值。

![](https://images.seebug.org/content/images/2018/01/ccd663ea-7210-4129-9326-e5ad101ecba4.jpg-w331s)

右键编辑IL指令。

![](https://images.seebug.org/content/images/2018/01/a86308ec-a494-4b46-bb83-1a3b9c1295b8.jpg-w331s)

将其值修改为9000.

![](https://images.seebug.org/content/images/2018/01/a4ec85ec-df6b-401a-9c66-6a504e6da6e1.jpg-w331s)

然后保存后打包并重新安装。

![](https://images.seebug.org/content/images/2018/01/af6ce6f8-25bf-441e-b65d-170a5948c1ac.jpg-w331s)

此时无论抽多少次，奖券都不再变化。

另一个就是修改三叶草的数量了。三叶草是该游戏中流行的货币，买东西都是需要该物品。同理找到`CloverPointStock()`方法。

![](https://images.seebug.org/content/images/2018/01/ec2a1695-57eb-4480-bdf8-a3bef4062c18.jpg-w331s)

将其返回值修改为8888.之后就可以随便买买买了，三叶草的数量也不会发生变化了。

![](https://images.seebug.org/content/images/2018/01/6f0ee875-61af-47e7-b44e-664af758e566.jpg-w331s)

#### 0x03 汉化

然后就是进行汉化了。汉化的方法和上面的类似。首先搜索需要修改的文字。例如给小青蛙起名字的时候。直接进行字符串搜索。

![](https://images.seebug.org/content/images/2018/01/26c17031-7975-45ee-9807-08c28624a2b6.jpg-w331s)

然后修改为对应的中文就行了。

![](https://images.seebug.org/content/images/2018/01/81c2e604-2734-4ef6-b200-a6a50bce40d1.jpg-w331s)

进入游戏查看

![](https://images.seebug.org/content/images/2018/01/49740982-0db7-4927-8540-9fefae9559db.jpg-w331s)

修改其他处的文字也是这样操作即可。当然这种修改方法比较慢，还有另外一种，直接将他人汉化过的dll文件复制进来，可以快速达到汉化的目的，也没有广告的烦恼了。

#### 0x04 总结

这个游戏修改起来比较简单，首先判断为该游戏为Unity3d。然后使用dnSpy来对`Assembly-CSharp.dll`文件进行修改。根据特定的字符串找到需要修改的位置，修改后进行打包签名后即可。

#### 0x05 参考

[1]
[https://www.52pojie.cn/search.php?mod=forum&searchid=23262&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=unity3d](https://www.52pojie.cn/search.php?mod=forum&searchid=23262&orderby=lastpost&ascdesc=desc&searchsubmit=yes&kw=unity3d)

[2] <https://www.52pojie.cn/thread-647612-1-1.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/519/>

