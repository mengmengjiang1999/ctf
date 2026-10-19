***本文作者：m0nst3r@丁牛网安实验室，转载请注明来源。**  

传送门：

[透过Autoruns看持久化绕过姿势的分享（一）](http://www.freebuf.com/column/164252.html)

## 4个未公开的绕过方法

### Service DLL Bug

首先认识一下两种`Service`：`Standalone Service`和`sss service`

#### Standalone Service

iPod Service
是随iTunes安装的Service类型的自启动项，用来管理硬件的一个Service，当它启动时，会运行一个自己的进程。当系统启动时，会调用`iPodService.exe`。这就是一个典型的Standalone
Service的运行方式。来看下这样的Service在注册表中的样子：

![56.png](https://image.3001.net/images/20180307/15203886422490.png!small)

在Autoruns中的，这个Service是一个由Apple Inc签名的合法启动项：

![57.png](https://image.3001.net/images/20180307/15203886867778.png!small)

  

#### Shared Service

`DcomLaunch`是Shared
Service的一个很好的例子。它是微软自带的一个Service启动项，启动的是非常常见的`svchost.exe`程序，当它启动时，它会加载`rpcss.dll`。  
在注册表中是这样的：

![59.png](https://image.3001.net/images/20180307/15203888074690.png!small)

  

对于绕过非常重要的键是`Parameters`键，它用来指定它当启动时要加载的DLL文件，这是就是这个`rpcss.dll`，如下图：

![60.png](https://image.3001.net/images/20180307/15203889826345.png!small)

在Autoruns里面的检测结果是一个Microsoft签名的Service：

![61.png](https://image.3001.net/images/20180307/15203890274377.png!small)  

  

如果我们的iPod Service里面手工添加一个`Parameters`键，会是什么样呢？

![63.png](https://image.3001.net/images/20180307/15203890602862.png!small)

![64.png](https://image.3001.net/images/20180307/15203890804050.png!small)

当我们进行如上修改后，在Autoruns中，会被显示为一个Microsoft签名的合法启动项。

#### 利用方法

经过上面的演示，估计大家都知道如何隐藏自己的启动项了。

添加一个启动项，类型为Standalone Service，然后指定启动时运行的程序。

![65.png](https://image.3001.net/images/20180307/15203891774212.png!small)

然后新建一个`Parameters`键，然后随便挑一个合法的微软DLL，写进去。

![66.png](https://image.3001.net/images/20180307/15203892054064.png!small)

  

在Autoruns中就会被当作一个Microsoft签名的合法启动项了：

![67.png](https://image.3001.net/images/20180307/15203892355959.png!small)

  

### Extension Search Order Bug (扩展名的搜索顺序利用漏洞)

`搜索路径`这里不再展开，直奔主题：比如我们要运行计算器，一般我们会输入`calc.exe`，这里程序会去`搜索路径`中去找这个程序。但是如果我们只输入`calc`，也就是不带`.exe`后缀，会好发生什么呢？

![73.png](https://image.3001.net/images/20180307/15203892756260.png!small)

为什么这样呢？

![74.png](https://image.3001.net/images/20180307/15203893156220.png!small)

当我们不指定扩展名时，Windows会根据默认的扩展名的搜索顺序在搜索目录中进行查找，但不幸的是，它会选查找`.com`扩展的文件，然后才是`.exe`扩展的文件。

#### 利用方法

找一个自启动的Windows签名的启动项：

![76.png](https://image.3001.net/images/20180307/1520389351437.png!small)

它在Autoruns检测结果如下：

![77.png](https://image.3001.net/images/20180307/15203893788005.png!small)  

  

我们把注册表中的键值进行一下修改，把程序扩展名删掉：

然后，将我们的恶意程序复制到相应目录下，并将扩展名改为`.com`：

当机器重启时，我们的程序就会自动运行：

在Autoruns中检测，会发现它并没有什么异常，因为Autoruns并不检测扩展名，而是直接解析`.exe`文件：

### SIP Hijacking (SIP劫持)

#### 工具

[PoCSubjectInterfacePackage](https://github.com/mattifestation/PoCSubjectInterfacePackage)

#### 利用方法

我们将一个合法程序的电子授权证书偷过来，然后添加到自己的恶意程序中，那么在Autoruns中就会显示为Microsoft验证过的启动项：

![85.png](https://image.3001.net/images/20180307/1520389571151.png!small)

### .INF Scriptlets

提到这种技术的时候，我们一般会想到Casey给出的一个使用`regsvr32.exe`的例子：

![88.png](https://image.3001.net/images/20180307/1520389612255.png!small)

我们使用这个合法的Microsoft可执行程序来静默注册或卸载一个二进制程序或对象文件。上面这个例子中，我们告诉Windows我们想要卸载`scrobj.dll`，当卸载这个dll时，会给我们机会来提交或下载一个`脚本文件`，这个脚本文件是`XML`格式的。这使得我们能利利用一个合法的程序调用一个合法的dll去下载我们的payload。这种方法自从公开之后就变得不好用了，因为各种防护开始针对这种方法时行封堵。比如在Autoruns当中，会显示出`regsvr32.exe`：

![90.png](https://image.3001.net/images/20180307/15203896401291.png!small)

那么我们就没有办法了吗？当然不是。

在MSDN中有一个`INF UnregisterDlls`命令：

![92.png](https://image.3001.net/images/20180307/15203896701585.png!small)

我们新建一个`inf`文件，使用合适的程序去调用它，那么它就会跟我们上文中提到的相似，程序会像regsvr32一样，调用`scrobj.dll`去下载我们指定的`脚本文件`。如果通过社会工程学的攻击方法，可诱导用户右击并安装我们指定的程序，如下图。

![93.png](https://image.3001.net/images/20180307/15203896963410.png!small)

#### 利用方法

利用`rundll32.exe`去调用`setupapi.dll`，然后指定我们新建的`inf`文件，就可以达到我们的目的，执行流程如下：

![94.png](https://image.3001.net/images/20180307/15203897238868.png!small)

安装完成全，Autoruns的检测结果如下：

![95.png](https://image.3001.net/images/20180307/1520389764942.png!small)

很不幸的是，被新版本的Autoruns检测出来了。

这里，我们的绕过方法是使用`InfDefaultInstall.exe`。这是一个本地签名的微软程序：

![96.png](https://image.3001.net/images/20180307/1520389792974.png!small)

这个可执行程序一样会去加载你的inf文件，下载并执行你指定的`脚本文件`。

## 结语

持久化越来越已成为攻击者所关注的事，希望通过这篇文章的分析，能够提高防御者的视野。毕竟，攻击者的招数不止这些！

  

 ***本文作者：m0nst3r@丁牛网安实验室，转载请注明来源。**  

