***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

### 一、漏洞介绍  

**2019年1月11日，ThinkPHP团队发布了一个补丁更新，修复了一处由于不安全的动态函数调用导致的远程代码执行漏洞。该漏洞危害程度非常高，默认条件下即可执行远程代码。启明星辰ADLab安全研究员对ThinkPHP的多个版本进行源码分析和验证后，确认具体受影响的版本为ThinkPHP5.0-5.0.23完整版。**

### 二、漏洞复现

本地环境采用ThinkPHP 5.0.22完整版+PHP5.5.38+Apache进行复现。安装环境后执行POC即可执行系统命令，如图：

![image.png](https://image.3001.net/images/20190228/1551336756_5c77853414a37.png!small)

### 三、漏洞分析

以官网下载的5.0.22完整版进行分析， **首先定位到漏洞关键点：**

    
    
    thinkphp/library/think/Request.php:518

在method函数的第二个if分支中，引入了一个外部可控的数据$_POST[Config::get[‘var_method’]。而var_method的值为_method。

![image.png](https://image.3001.net/images/20190228/1551336810_5c77856a8dea1.png!small)

Request类的__construct函数如下：

由于$options参数可控，攻击者可以覆盖该类的filter属性、method属性以及get属性的值。而在Request类的param函数中：

当$this->mergeParam为空时，这里会调用$this->get(false)。跟踪$this->get函数：

该函数末尾调用了$this->input函数，并将$this->get传入，而$this->get的值是攻击者可控的。跟踪$this->input函数：

该函数调用了$this->getFileter取得过滤器。函数体如下：

$this->filter的值是攻击者通过调用构造函数覆盖控制的，将该值返回后将进入到input函数:

查看filterValue函数如下：

在call_user_func函数的调用中，$filter可控，$value可控。因此，可致代码执行。

 **漏洞触发流程：**

从ThinkPHP5的入口点开始分析：

    
    
    thinkphp/library/think/App.php:77

run函数第一行便实例化了一个Request类，并赋值给了$request。然后调用routeCheck($request,$config)：

这里调用Route::check进行路由检测。函数如下：

注意红色字体部分。对应开头的第一个步骤，也就是调用method函数进行变量覆盖。这里需要覆盖的属性有$this->filter,$this->method,$this->get。因为$request->method()的返回值为$this->method，所以该值也需要被控制。这里返回值赋值给了$method，然后取出self::$rules[$method]的值给$rules。这里需要注意：THINKPHP5有自动类加载机制，会自动加载vendor目录下的一些文件。但是完整版跟核心版的vendor目录结构是不一样的。

完整版的目录结构如下：

![image.png](https://image.3001.net/images/20190228/1551337368_5c77879880de8.png!small)

而核心版的目录结构如下：

![image.png](https://image.3001.net/images/20190228/1551337383_5c7787a7194bb.png!small)

可以看到完整版比核心版多出了几个文件夹。特别需要注意的就是think-captcha/src这个文件夹里有一个helper.php文件：

![image.png](https://image.3001.net/images/20190228/1551337400_5c7787b8b4ba6.png!small)

这里调用\think\Route::get函数进行路由注册的操作。而这步操作的影响就是改变了上文提到的self::$rules的值。有了这个路由，才能进行RCE，否则不成功。这也就是为什么只影响完整版，而不影响核心版的原因。此时的self::$rules的值为:

![image.png](https://image.3001.net/images/20190228/1551337416_5c7787c8c13f7.png!small)

那么，当攻击者控制返回的$method的值为get的时候，$rules的值就是这条路由的规则。然后回到上文取到$rules之后，根据传入的URL取得$item的值，使得$rules[$item]的值为captcha路由数组，就可以进一步调用到self::parseRule函数。函数体略长，这里取关键点：

此时传递进来的$route的值为\think\captcha\CaptchaController@index。因此进入的是标注红色的if分支中。在这个分支中，$result的’type’键对应的值为‘method’。然后将$result层层返回到run函数中，并赋值给了$dispatch。

然后将$dispatch带入到self::exec函数中：

进入到红色标注的分支，该分支调用Request类的param方法。因此，满足了利用链的第三步，造成命令执行。

启明星辰ADLab安全研究员对ThinkPHP5.0-5.0.23每个版本都进行了分析，发现ThinkPHP5.0.2-5.0.23可以使用同一个POC，而ThinkPHP5.0-5.0.1需要更改一下POC，原因在于Route.php的rule函数的一个实现小差异。

ThinkPHP5.0-5.0.1版本的thinkphp/library/think/Route.php:235，将$type转换成了大写：

![image.png](https://image.3001.net/images/20190228/1551337576_5c77886896ff4.png!small)

在ThinkPHP5.0.2-5.0.23版本中，rule函数中却将$type转换成了小写：

![image.png](https://image.3001.net/images/20190228/1551337595_5c77887b6a892.png!small)

### 四、补丁分析

在ThinkPHP5.0.24中，增加了对$this->method的判断，不允许再自由调用类函数。

![image.png](https://image.3001.net/images/20190228/1551337618_5c778892c6053.png!small)

### 五、结论

强烈建议用户升级到ThinkPHP5.0.24版本，并且不要开启debug模式，以免遭受攻击。

 ***本文作者：ADLab，转载请注明来自FreeBuf.COM**

