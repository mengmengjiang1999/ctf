**程序员写在文章前：**

本周技术分享，程序员小星想以“php框架代码审计”为题，与大家分享一下小星对代码的审计思路。但由于内容较多，此次小星先从兼容模式和path_info模式、命名空间、tp5的正常调用流程等七大部分与大家进行讨论。

 **（一）内容**

1\. MVC基本的架构

2\. 漏洞挖掘

thinkphp、Yii、larevel

M 模块

V 界面

C 控制器

MVC设计模式的优点?

1）解耦合 2）多接口、降低开发成本 3）高复用

 **（二）使用方式**

application 应用目录（放自己的代码）

|---- admin 放后台文件

|________controller

|---- index 放前台文件

|________controller

public 入口文件

|---- index.php 网站的入口文件

thinkphp 核心文件

 **（三）访问方式**

 **thinkphp所有的都是用URL来实现。**

 **thinkphp的访问模式：**

1）http://localhost/index.php/模块名称/控制器的名/方法名/参数/vaulue

2）http://localhost/index.php/模块名称/控制器的名/方法名?参数=value

 **模块名称：** 在application下，例如index文件夹是模块名。

 **控制器的名：** 在index下有一controller,这个controller下有index.php，那他的控制器的名就是index。

 **方法名：** 方法就是index.php下的一些方法名称。

 **构造URL：**

http://localhost/index.php/index/Index/hello/name/11111

![image.png](https://image.3001.net/images/20220914/1663138594_63217b2250e5e00ae46ee.png!small)

 **（四）** **兼容模式和** **path_info** **模式**

 **1）tp使用兼容模式的写法：**

http://localhost/index.php?s=index/Index/hello&name=1111

 **2）pathinfo访问的模式：**

http://localhost/index.php/index/Index/hello/name/11111

 **3）可以得到：**

http://localhost/index.php?s=模块/控制器/方法&参数=value

 **（五）关于命名空间**

tp5遵循一个psr-4自动加载规范,他可以去自动加载类,需要合理的、正确的命名空间。

一组的健康的、合格的tp5代码需要一个合理的命名空间。

![image.png](https://image.3001.net/images/20220914/1663138595_63217b23a219cca71ab22.png!small)

创建一个核心包下的文件kk.php。

![image.png](https://image.3001.net/images/20220914/1663138596_63217b24ac23e660c25b9.png!small)

![image.png](https://image.3001.net/images/20220914/1663138597_63217b254108109a50df4.png!small)

![image.png](https://image.3001.net/images/20220914/1663138597_63217b25d7c94668cb35f.png!small)

 **得到一个关于命名空间的结论:**

1）如果你写在application下,那你命名空间的一个根路径是app；

2）如果thinkphp下的think,那你命名空间的一个根路径就think；

3）如果thinkphp下的traits,那你命名空间的一个根路径就是traits。

 **（六）问题根源**

TP处理URL的一个特性，他使用全局变量。

http://localhost/index.php/index/\Index/hello/name/11111

http://localhost/index.php/index//Index/hello/name/11111

 **（七）** **tp5** **的正常调用流程**

 **0** **1** **URL路由解析动态调试分析**

1）先看他这个入口文件的调用也就是public/index.php,根据他的入口文件去找相应的代码。

![image.png](https://image.3001.net/images/20220914/1663138598_63217b267f4f60b65e08a.png!small)

![image.png](https://image.3001.net/images/20220914/1663138599_63217b272767b556b1e8e.png!small)

2）正式进入路由检测的一个方法。

![image.png](https://image.3001.net/images/20220914/1663138599_63217b27d6e4a6f8650c9.png!small)

3）他会从下图中进一个path方法。

![image.png](https://image.3001.net/images/20220914/1663138600_63217b28ce15da0e28f8a.png!small)

4）他会从下图中进一个pathinfo方法。

![image.png](https://image.3001.net/images/20220914/1663138601_63217b29bb4031c7f004c.png!small)

5）要从这里进入一个server。

![image.png](https://image.3001.net/images/20220914/1663138603_63217b2bc8ab1fa72ad53.png!small)

6）ltrim()方法可以把/index/Index/hello//name/11111这一段字符串的最左边的'/'index/Index/hello//name/11111，以上就是路径解析的一个过程。

##  **0** **2** **路由解析动态调试**

1）接下来会调用check方法。

![image.png](https://image.3001.net/images/20220914/1663138604_63217b2ca6664ff5f1db4.png!small)

2）继续跟进check方法。

![image.png](https://image.3001.net/images/20220914/1663138605_63217b2daf56b9120dfef.png!small)

3）后续他会用str_replace()方法来把斜杠修改成|，调用"use think\route\dispatch\Url as UrlDispatch;
" 这个Url.php。

![image.png](https://image.3001.net/images/20220914/1663138607_63217b2f822edfdc2d3af.png!small)

4）跟进至paresUrl中。

![image.png](https://image.3001.net/images/20220914/1663138609_63217b31bc6108ce022f6.png!small)

![image.png](https://image.3001.net/images/20220914/1663138611_63217b33cd905fa452caa.png!small)

5）array_shift()取出第一个模块名，然后用同样的手法给控制器取出来并且赋值给$controller，再用同样的手法给$action赋值，最后他会把已经拆分的东西打包存放到这个route当中。

![image.png](https://image.3001.net/images/20220914/1663138613_63217b350215bb1faec5b.png!small)

6）后续把这一个route的内容返回到init中的$result中去。

![image.png](https://image.3001.net/images/20220914/1663138613_63217b35ecb0881bad086.png!small)

7）接下来他会去new一个module类,但是这个module中没构造方法,所以他会调用一次父类的无参构造,然后再调用module下的初始化方法init。

![image.png](https://image.3001.net/images/20220914/1663138615_63217b37f1a17bab60b62.png!small)

8）在进入这个初始化方法后他会用parent::init();再调用一次父类的初始化方法。

##  **0** **3** **开启debug后**

![image.png](https://image.3001.net/images/20220914/1663138616_63217b38dd4cc3373be27.png!small)

1）如果开启了debug,他就会对路由的信息进行记录。

![image.png](https://image.3001.net/images/20220914/1663138620_63217b3c272e7c2b43ddf.png!small)

2）这边会把请求的参数和URL地址进行参数合并,这边他会调用一次解析过滤器,但是这个过滤器他什么都没写, 所以相当于没有任何过滤。

![image.png](https://image.3001.net/images/20220914/1663138621_63217b3d05438cf7c3554.png!small)  
3）刚刚的一部分已先获取了一个字符串

/admin/index/hello

然后把上面的字符串处理成了以下的形式

admin/index/hello

最后他会把去掉'/'的字符串也就是路径会拆分赋值,如下：

    
    
    $module = admin -->模块
    $controller = index -->控制器
    $action = hello -->方法

下期，我们将就“路由动态测试”、“思路总结”两大部分与大家继续探讨，并附上小星在研究过程中的意外发现，请大家继续支持！

