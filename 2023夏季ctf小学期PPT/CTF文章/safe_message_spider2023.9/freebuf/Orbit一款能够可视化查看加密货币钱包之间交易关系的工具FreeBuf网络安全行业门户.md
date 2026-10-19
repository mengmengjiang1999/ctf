**今天给大家介绍的是一款名叫Orbit的工具，Orbit采用递归爬取策略实现，大家可以使用该工具以可视化的方式查看加密货币钱包之间的交易关系。**

![31.png](https://image.3001.net/images/20180716/1531723323322.png!small)

## Orbit

你只需要给Orbit提供一个加密货币钱包地址，它就可以爬取到跟这个加密钱包有关的交易数据，层级为三层，并以图形化的方式显示出交易关系数据。

## 工具使用

首先你需要在设备上安装好Python 3，然后通过下列命令运行orbit.py：

    
    
    python3 orbit.py

接下来，输入目标钱包地址：

![32.png](https://image.3001.net/images/20180716/15317233411900.png!small)

输入之后，Orbit将会通过区块链API来抓取钱包信息，完成之后会生成一个JSON文件。接下来，Orbit需要以图形化的方式生成钱包的交易信息，这里Orbit使用的是[Quark框架](https://github.com/s0md3v/Quark)，这个框架也是我自己开发的。

克隆Quark项目源码，然后切换到Quark目录，使用下列命令将之前生成的JSON文件提供给quark.py：

    
    
    python quark.py /path/to/file.json

没错，就是这样，你要做的事情已经完成了，接下来打开quark.html看看你的查询结果吧！

### 注意事项

图形化结果中的节点大小和连线大小取决于目标钱包地址的交易数量以及范围，所以节点有时会非常的大，请不要被吓到，你只需要点击侧边栏的stabilize选项，剩下的就交给quark去完成吧！

![33.png](https://image.3001.net/images/20180716/1531723360808.png!small)

除此之外，如果节点标签显示错误的话，你可以点击Node Lables选项进行设置。

最后一点，如果目标钱包交易非常频繁的话，可能会出现非常多的节点，而有些节点可能并不是你所感兴趣的，此时你可以点击clean选项来清除那些没有意义的节点。

如果你对Quark框架感兴趣的话，可以查看项目的【[GitHub主页](https://github.com/s0md3v/Quark)】获取更多信息。

***参考来源：[Orbit](https://github.com/s0md3v/Orbit)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

