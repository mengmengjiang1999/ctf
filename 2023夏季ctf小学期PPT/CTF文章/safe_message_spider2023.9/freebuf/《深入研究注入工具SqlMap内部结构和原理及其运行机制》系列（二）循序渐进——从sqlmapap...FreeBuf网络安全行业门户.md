# **《深入研究注入工具SqlMap内部结构和原理及其运行机制》系列（二）：循序渐进——从sqlmapapi.py开始研究**

很多大佬开发的自动化工具都应用到了SQLMapApi，要控制sqlmapapi非常简单，只需要依靠Get/Post请求sqlmapapi所提供的接口即可完成启动sql注入扫描，检测扫描状态等等操作，国内已经有部分人对sqlmapapi有一定的了解了，很多大佬写的介绍sqlmapapi的文章也很不错，可惜就国内来说，了解的人还是不算特别多。其实我刚了解sqlmapapi的时候，觉得神器无疑，后面深入了解了sqlmapapi的底层运行逻辑，才发现，我的小可爱，原来就是通过调用系统命令行（那我还不如直接调用系统命令行来执行sqlmap命令，虽然少了优雅，不过方便快捷，工程量少）不过对于刚研究sqlmap内部结构的研究者来说，sqlmapapi绝对是个不错的选择，因为sqlmapapi工程量相对sqlmap主体来说较少，非常有利于对sqlmap整体架构意识的初步建立，同时由浅入深地了解整个sqlmap的思想。

## 研究环境

 **Python3.7**  
 **SQLMapApi**  
 **PyCharm 2021.3.2**  
 **sublimeText**  
![屏幕截图 2022-02-05
165056.png](https://image.3001.net/images/20220305/1646462983_622308077c020227f6c29.png!small)

* * *

### SqlMapApi源码分析(sqlmap/sqlmapapi.py)

#### 初始化部分

![屏幕截图 2022-02-05
165354.png](https://image.3001.net/images/20220305/1646462990_6223080e64f4c3bf722ed.png!small)

####  **Main部分**

![屏幕截图 2022-02-05
165545.png](https://image.3001.net/images/20220305/1646463010_62230822af052264cf64b.png!small)

#### 核心库：`from lib.utils.api import server `（32行）

* * *

### 初始化部分源码分析：

先从初始化部分开始分析（只分析该部分中的重点部分，很多是导入库不导入库的，没有值得探究的地方）：

`__import__`相当于动态引入类,如果一个模块经常变化就可以使用`__import__`来动态载入。  
则在第12行`__import__("lib.utils.versioncheck") # this has to be the first non-standard import`表示的是 **动态导入lib.utils.versioncheck库** ，该库是用来版本检查的.  
所以整行代码翻译成人话就是 **动态引入版本检查文件**

 **动态导入又是什么意思呢？**  
在运行状态中，对于任意一个类，都能够知道这个类的所有属性和方法；对于任意一个对象，都能够调用它的任意方法和属性；并且能改变它的属性。

### Main部分源码分析：

先看两个函数`dirtyPatches()`(45行)和`resolveCrossReferences()`（96行）  
emmmm......刚刚本来写了一些了，但是突然觉得这两个都不是重点，没必要逐行分析，我大概解释一下：  
 **dirtyPatches函数：提高对环境的兼容性，其实就是个Patches**

> 接受过长的结果行（例如 SQLi 导致 HTTP 标头响应）  
> 在 sqlmap 分块的情况下防止双重分块编码（注意：如果缺少 'Content-length'标头，Python3 会自动执行此操作）  
> 在python3环境下重新配置`from thirdparty.six.moves import http_client as
> _http_client`的HTTPConnection属性。  
> 在 Windows 操作系统上添加对 inet_pton() 的支持  
> 在response中不包含编码方式时就调用universaldetector第三方插件运用统计学来判断网页编码的方式

 **resolveCrossReferences函数：交叉引用解决方案的位置，换了一堆的函数**

然后回到Main函数，到49行的`logger.setLevel(logging.DEBUG)`大意是设置默认日志级别为调试，它这个是`from
lib.core.data import
logger`过来的，在这个logger库里，应该是先配置了`logging.getLogger()`，然后再通过logger.setLevel()设置logger的级别为DEBUG。![屏幕截图
2022-02-05
180136-16464625465232.png](https://image.3001.net/images/20220305/1646463029_62230835907dac8b9653d.png!small)

再来分析Main函数54行之后：通过optparse库来 **获取命令行参数** ，最后把这些参数选项 **赋值给args**  
![屏幕截图 2022-02-05
192451.png](https://image.3001.net/images/20220305/1646463050_6223084a2b2ae505a66af.png!small)

### 本文最最核心的部分

![屏幕截图 2022-02-05
195017.png](https://image.3001.net/images/20220305/1646463061_62230855ef8d6722a6c77.png!small)  
server和client函数都是由`from lib.utils.api import server`导入的。

不过平时我们其实用不到client部分，所以直入主题server函数。  
我们先打开sqlmap/lib/utils/api.py,跳转到677行`def server(host=RESTAPI_DEFAULT_ADDRESS,
port=RESTAPI_DEFAULT_PORT, adapter=RESTAPI_DEFAULT_ADAPTER, username=None,
password=None):`  
可以发现server函数的所有参数都是默认参数，我们再追到sqlmap/lib/core/settings.py文件里，这个文件存放了各种默认选项，包括sqlmap的版本号，项目地址等等。  
在settings文件中找到server函数的
**3个默认参数分别是RESTAPI_DEFAULT_ADDRESS，RESTAPI_DEFAULT_PORT，RESTAPI_DEFAULT_ADAPTER。**

在settings.py的811行可以找到 **RESTAPI_DEFAULT_ADDRESS变量的值为127.0.0.1**
,也就是说，在sqlmapapi没有-H或--host参数的情况下，**默认sqlmapapi的服务接口地址在127.0.0.1 **。

    
    
    # Default REST-JSON API server listen address
    RESTAPI_DEFAULT_ADDRESS = "127.0.0.1"
    

在settings.py的814行可以找到 **RESTAPI_DEFAULT_PORT变量的值为8775** ,也就是说，在sqlmapapi没有-p或
--port参数的情况下， **默认sqlmapapi的服务接口端口是8775** 。

    
    
    # Default REST-JSON API server listen port
    RESTAPI_DEFAULT_PORT = 8775
    

在settings.py的808行可以找到 **RESTAPI_DEFAULT_ADAPTER变量的值为wsgiref**
,也就是说，在sqlmapapi没有指定服务器适配器参数--adapter的情况下， **默认sqlmapapi使用的服务器适配器为wsgiref** 。

    
    
    # Default adapter to use for bottle server
    RESTAPI_DEFAULT_ADAPTER = "wsgiref"
    

