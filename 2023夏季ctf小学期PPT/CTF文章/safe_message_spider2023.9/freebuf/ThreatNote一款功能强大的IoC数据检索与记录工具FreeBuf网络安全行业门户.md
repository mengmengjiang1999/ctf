**Threat_Note是一款一个轻量级的调查笔记，它允许安全研究人员注册和检索他们所需要的入侵威胁指标IoC数据。**

![](https://image.3001.net/images/20191113/1573580893_5dcaf05d1d45b.png!small)

##  注意事项

threat_note目前仍处于开发测试阶段，因此在使用过程中可能会出现很多问题。该工具目前已在Yosemite
10.10.4平台上进行了测试，测试环境为Chrome，其他浏览器或操作系统平台可能会出现显示格式错误等等，大家可以在issues页面提交bug。

##  工具介绍

threat_note本质上是一个Web应用程序，该工具基于Defense Point
Security开发，允许研究人员添加或检索相关研究的入侵威胁指标IoC。目前该工具版本支持添加IP地址、域名和攻击者等等，未来将添加更多支持。

该工具是一个轻量级工具，并且易于安装，并且不会添加任何额外的信息。该工具的出现填补了目前该领域解决方案的研究空白。在使用该工具之前，用户需要创建一个新的指标器，我们只需要提供对象本身（域名、IP地址或攻击者信息），并修改相应的类型即可。

###  工具需求分析

> 1、难以安装/配置/域名；
>
> 2、需要为更多其他的功能付费（企业许可证）；
>
> 3、信息过多：数据拥塞情况太过复杂。

##  工具安装

该工具目前使用的是SQLite，我们只需要通过pip安装相关依赖并启动服务器即可：

> cd threat_note
>
> pip install -r requirements.txt
>
> honcho start

服务器运行之后，我们可以访问[http://localhost:5000](http://localhost:5000/)，并注册一个新的threat_note账号即可。

###  Docker安装

目前该工具提供了可开发的docker文件，构建命令如下：

> sudo docker build -t threat_note .
>
> sudo docker run -itd -p 8888:8888 threat_note

当服务器运行之后，我们可以访问[http://localhost:8888](http://localhost:8888/)，并注册一个新的账号来使用threat_note。

##  工具使用

首先打开仪表盘，其中显示了最新的入侵威胁指标、以及星标信息：

![](https://image.3001.net/images/20191113/1573580941_5dcaf08dd2fea.png!small)

网络入侵威胁指标界面，这里我们可以看到所有的入侵威胁指标：

![](https://image.3001.net/images/20191113/1573580950_5dcaf096d6423.png!small)

我们还可以编辑或移除指标信息：

![](https://image.3001.net/images/20191113/1573580958_5dcaf09e2f894.png!small)

点击其中一个网络指标符，将可以查看详细的信息：

![](https://image.3001.net/images/20191113/1573580966_5dcaf0a66b952.png!small)

点击“新指标符”按钮，即可根据需求创建新的指标符：

![](https://image.3001.net/images/20191113/1573580973_5dcaf0ad48dc8.png!small)

在设置页面中，我们还可以删除threat_note数据库，并控制相关数据：

![](https://image.3001.net/images/20191113/1573580981_5dcaf0b5dc7a0.png!small)

##  项目地址

>
> threat_note：【[GitHub传送门](https://github.com/DefensePointSecurity/threat_note)】

***参考来源：[DefensePointSecurity](https://github.com/DefensePointSecurity/threat_note)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

