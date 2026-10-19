##  0x01：前言

**之前做内网渗透测试的时候，一直想要有一款能够格式化存储收集到的信息，并且可以方便的查找出重要信息的工具。前段时间看到了Leprechaun这个工具，给了我一些想法。由于，我对于这个工具有些不喜欢的地方。再加上好久没有写小程序练手了，于是决定自己定制一款类似的工具。**

有人肯定又会说是重复造轮子。其实，我觉得汽车的轮子再好用，也没办法装到自己的自行车上使用。对于使用者可能只是多了一个选择，而对于编写者，则可以学到很多东西。所以，“重复造轮子”至少对于开发者意义还是很大的。

先放一张成品图吧！

![](https://image.3001.net/images/20190824/1566657087_5d614a3fe6a62.png!small)

##  0x02：软件简述

本程序采用的是B/S结构开发，使用Go语言的[Gin](https://github.com/gin-gonic/gin)框架。考虑到经过处理后的连接记录不会太大和程序的便携性，数据库采用的sqllite。前端界面是不是看起来很熟悉？前端由于本人没有深入了学习过，所以就直接使用[LogonTracer](https://github.com/JPCERTCC/LogonTracer)
程序的界面做了一些修改。（最开始是想参考一下，它拓扑图实现的方式的，后来觉得有些复杂，依赖太多，就放弃了）。最后，拓扑图是由
[vis.js](https://visjs.org/)这个库实现的。

##  0x03：网络连接记录文件的处理

这里我们需要处理的主要是Windows主机通过netstat -ant命令所获取的结果。如下图所示：

![](https://image.3001.net/images/20190824/1566657374_5d614b5e90660.png!small)

所需要关注的部分主要是连接使用的协议，本地IP地址，外部IP地址和连接状态。

 **处理流程主要有四部分：**

1)过滤掉无意义的内容，如ip地址中为0.0.0.0以及未建立稳定连接的行。

![](https://image.3001.net/images/20190824/1566657402_5d614b7acc9a9.png!small)

2)比对每行数据，如果本地或外部地址中存在连向同一个IP的同一个端口的情况，那么该IP则确认为提供服务的IP。（经过处理，程序有可能会发现一些有趣的端口！）

![](https://image.3001.net/images/20190824/1566657420_5d614b8ca7310.png!small)![](https://image.3001.net/images/20190824/1566657428_5d614b9425155.png!small)

3）如果第二步没能确认出所有的服务IP,那么则通过常见的端口进行判断。（可以通过自定配置文件的方式，额外增加特殊端口。）

![](https://image.3001.net/images/20190824/1566657505_5d614be1b9c80.png!small)

4）如果经过第二步和第三步也未能识别出服务IP，则将所有IP和端口都存入数据库。（前两步只存储服务I端P，客户端IPI，服务端端口，以及客户端发起的连接数量。）

![](https://image.3001.net/images/20190824/1566657542_5d614c0618b1f.png!small)

处理后数据库中存放内容如下：

![](https://image.3001.net/images/20190824/1566657589_5d614c35db7ae.png!small)

##  0x04: 查询结果展示

这里我们会使用一个golang编写的一个解析DOT语言的库[Graphviz](http://github.com/awalterschulze/gographviz)。只需要将想要的节点从数据库中读出，并加入这些节点的关系，就可以自动生成DOT语言。最后将生成的DOT返回给前端界面，由vis.js处理后展示出来...

![](https://image.3001.net/images/20190824/1566657688_5d614c987190e.gif!small)

##  0x05:结束语

由于，很多东西都是第一次使用，需要一边查找文档，一边尝试着编写，最后勉强把自己想要的功能实现了。所以，程序的代码质量不是很高，有些地方也会比较混乱。实际使用测试过程中，如果一个ip的连接数量太多，最后生成的拓扑图基本没办法看了，之后我会试着看看还有没有更好生成拓扑图的方案改进一下。对于太大的网络，可能只能作为一个网络连接存储的功能。有时间的话，还想重造一个LogonTracer的轮子，侧重点可能更多在于用户和主机的定位。

> 代码地址：<https://github.com/Releasel0ck/NetTracer>

参考链接：

> <https://github.com/vonahisec/leprechaun>
>
> <https://github.com/JPCERTCC/LogonTracer>
>
> <https://github.com/awalterschulze/gographviz>
>
> <https://visjs.org/>
>
> <https://github.com/gin-gonic/gin>

***本文原创作者： releasel0ck，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
  
  

