本文原创作者：Yale

原创投稿详情：[重金悬赏 |
合天原创投稿等你](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652846451&idx=2&sn=2456db03a3a77d5ff8064449c34ffceb&chksm=bd5945be8a2ecca808f62ee5726223c16cab235d216c891df2dd114b8539001390dbad37bccd&scene=21#wechat_redirect)

 **  
**

本文译自Drozer官方文档，截图均为译者实际操作

（<https://labs.mwrinfosecurity.com/assets/BlogFiles/mwri-drozer-user-guide-2015-03-23.pdf>）

 **  
**

Drozer是Android领先的安全测试框架。

drozer允许您通过假设一个应用程序的作用，并与Dalvik虚拟机，其他应用的IPC端点和底层操作系统进行交互来搜索应用程序和设备的安全漏洞。

该drozer代理被设计为代表的Android设备上的任意无特权的应用程序运行，正因为如此，只要求一个单一的权限：INTERNET权限。因为代理需要打开套接字连接与控制台或服务器进行交互此权限是必需的。

drozer试图避免外部工具，如依ADB和AAPT，因为这些只会通过USB连接就可以让设备正常工作。

drozer功能全部模块化，即利用该代理的反射，加载功能来执行他们的测试。允许系统进行扩展，而无需过于频繁地更新代理。

3 **0×03安装**

使用adb将drozer代理apk装入我们的模拟器

  
![640.png](https://image.3001.net/images/20180620/15294621048527.png!small)  

在模拟器中可以看到一个名为drozeragent的app已经成功安装了

使用同样的方法我们来安装sieve.apk，这是我们这次要测试的应用

  
![640.jpg](https://image.3001.net/images/20180620/15294621122718.jpg!small)  

打开drozeragent

  
![640.png](https://image.3001.net/images/20180620/15294621257974.png!small)  

点击下方的embeddedserver

  
![640.jpg](https://image.3001.net/images/20180620/15294621321439.jpg!small)  

点击disabled，状态就会改变位enabled

  
![640.jpg](https://image.3001.net/images/20180620/15294621442439.jpg!small)  

接下来我们建立一个合适的端口用于转发来使得我们的pc可以和模拟器中drozeragent打开的tcp套接字进行连接。在上面的截图中我们可以看到agent默认的端口是31415，所以我们输入下图的命令即可

![640.png](https://image.3001.net/images/20180620/15294623548744.png!small)  

接下来再打开一个cmd，切换到drozer目录下

  
![640.png](https://image.3001.net/images/20180620/15294623619262.png!small)  

输入下图命令进行连接

  
![640.png](https://image.3001.net/images/20180620/15294623675119.png!small)  

如果是上图的回显说明连接成功了

4 **0×04使用**

接下来我们开始正式的学习drozer

前面我们安装了sieve，它是一款密码管理软件，专门被设计出来用于安卓应用常见漏洞的学习使用的。

打开sieve之后我们首先需要设置16位的masterpassword，点击右上角的+号即可设置。

这里为了方便，我设置的是rootrootrootroot

![640.png](https://image.3001.net/images/20180620/15294623759187.png!small)  

然后需要设置4位的pin码

  
![640.jpg](https://image.3001.net/images/20180620/15294623822844.jpg!small)  

点击save即可。

接下来我们开始在dz环境下实践。

测试sieve的第一步就是在安卓设备中找到它。安装在安卓设备上的应用会被他们的包名特定地识别出来。我们可以通过app.package.list找到sieve的标识符

  
![640.png](https://image.3001.net/images/20180620/15294623914006.png!small)  

然后通过app,package.info命令要求drozer提供一些关于包的基础信息

  
![640.png](https://image.3001.net/images/20180620/15294623983963.png!small)  

上图展示了一些app的细节。包括版本，app在设备中保存数据的地方，app安装的位置以及关于应用权限的大量细节

5 **0×05攻击**

接下来我们需要找到攻击面。我们这次关注android固有的IPC通信机制的脆弱性，这些特点导致了App泄漏敏感信息给同一台设备上的其它App。

首先我们使用下列命令来获得针对sieve的攻击面

  
![640.png](https://image.3001.net/images/20180620/15294624061478.png!small)  

上图展示了潜在的攻击向量。

我们注意到services下面提示isdebuggle,这意味着我们可以附加一个调试器到这个进程。

  
![640.png](https://image.3001.net/images/20180620/15294624144554.png!small)  

我们可以使用一些特殊的命令来深入研究攻击面。

比如使用runapp.activity.info –a com.mwr.example.sieve来查看哪些activities会被sieve导出

![640.png](https://image.3001.net/images/20180620/15294624258021.png!small)  

结果中的一个正是我们所期待的（mainloginactivity）。因为当我们第一次启动应用时将会被显示出来。

既然acticity被导出来了，而且不要求任何权限，我们就让drozer来加载它。

  
![640.png](https://image.3001.net/images/20180620/15294624334999.png!small)  

这条命令可以帮助我们成功绕过认证（没绕过的话，打开sieve时是需要我们输入密码才能登录到此界面的）

  
![640.png](https://image.3001.net/images/20180620/15294624392324.png!small)  

当调用‘app.activity.start’时很有可能会产生更多更复杂的intent.当然我们也可以使用dorzer其他模块，来获得更多的用法信息

![640.png](https://image.3001.net/images/20180620/15294624473377.png!small)  

  
![640.jpg](https://image.3001.net/images/20180620/15294624566897.jpg!small)  

接下来我们搜集从app中导出的关于contentproviders更多的信息。

我们使用下面的命令来获取额外的信息

  
![640.png](https://image.3001.net/images/20180620/15294624722118.png!small)  

上图告诉我们这些contentprovider不需要任何特定的权限就可以与之交互，除了DBContentProvider中的/Keys路径。

我们很容易会推测到名为DBContentProvider的contentproviderr在后端会有一些数据库。然而，由于不知道contentprovider是如何组织的，我们很难提取出任何信息。

因为我们知道目录URI必须以“content://”开头，所以我们可以尝试重构部分目录URI来进入DBContentProvider。但是，我们不知道将会被provider接收的所有的路径组成部分。

但是，我们的drozer提供一个扫描模块来猜测并验证一系列可以使用的目录URI。使用下列命令即可。

  
![640.png](https://image.3001.net/images/20180620/15294624794972.png!small)  

现在我们可以使用其他的drozer模块从目录URI中获得信息，甚至可以修改数据库中的数据。输入下列命令就可以获得我们在sieve初始化设置的密码

  
![640.png](https://image.3001.net/images/20180620/15294624878503.png!small)  

接下来我们看看SQL注入。

安卓平台推荐使用SQLite数据库存储用户数据。由于数据库使用SQL,那么就可能存在SQL注入的漏洞。使用projection参数和seleciton参数可以传递一些简单的SQL注入语句到Contentprovider

我们通过一个引号来简单的测试一下是否存在SQL注入

  
![640.png](https://image.3001.net/images/20180620/15294624968900.png!small)  

  
![640.png](https://image.3001.net/images/20180620/15294625037747.png!small)  

报错了，说明应该是存在SQL注入的

报错信息告诉我们整个查询是如何执行的。

现在我们完整地攻击这个漏洞，来列出数据库中的所有表。

  
![640.png](https://image.3001.net/images/20180620/1529462508729.png!small)  

使用SQL注入列出数据表的内容

  
![640.png](https://image.3001.net/images/20180620/15294625168489.png!small)  

上图中可以看出我们的密码和PIN码都被读出来了

File System-backedContent
Provider提供了访问底层文件系统的方法，Android沙盒会阻止App共享文件，而FileSystem-backed Content
Provider允许App共享文件。

对于sieve来说，我们可以推测出的FileBackupProvider就是一个filesystem-backed content
provider。这个路径代表了我们想要打开的文件的位置。因此我们可以猜测它的目录URIs并且使用drozer的app.provider.read模块查看某个文件

  
![640.png](https://image.3001.net/images/20180620/1529462523820.png!small)  

我们知道contentprovider存在SQL注入和目录遍历的风险。Drozer提供模块来自动测试这些类型的漏洞。

下图是测试注入的

  
![640.png](https://image.3001.net/images/20180620/15294625297353.png!small)  

下图是测试目录遍历的

  
![640.png](https://image.3001.net/images/20180620/15294625401894.png!small)  

至此我们几乎完全攻陷了sieve，我们提取出了用户的密码、pin，密文，也发现并利用了很多典型的漏洞，比如SQL注入、目录遍历等。

电商关注的是业务逻辑漏洞、越权。具体的就是价格篡改、订单便利、客户敏感信息泄露等等漏洞，并描述漏洞测试方法及测试点有哪些。

（注：本文属于合天原创投稿奖励，未经允许，禁止转载！）

