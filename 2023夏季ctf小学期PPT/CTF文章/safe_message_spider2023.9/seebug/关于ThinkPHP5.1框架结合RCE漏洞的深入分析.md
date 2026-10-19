**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/kwp5uxom7Amrj6S_-g8r4Q>**

### 前言

在前几个月，Thinkphp连续爆发了多个严重漏洞。由于框架应用的广泛性，漏洞影响非常大。为了之后更好地防御和应对此框架漏洞，阿尔法实验室对Thinkphp框架进行了详细地分析，并在此分享给大家共同学习。

本篇文章将从框架的流程讲起，让大家对Thinkphp有个大概的认识，接着讲述一些关于漏洞的相关知识，帮助大家在分析漏洞时能更好地理解漏洞原理，最后结合一个比较好的RCE漏洞(超链接)用一种反推的方式去进行分析，让大家将漏洞和框架知识相融合。体现一个从学习框架到熟悉漏洞原理的过程。

### 一、框架介绍

ThinkPHP是一个免费开源的，快速、简单的面向对象的轻量级PHP开发框架，是为了敏捷WEB应用开发和简化企业应用开发而诞生的。ThinkPHP从诞生以来一直秉承简洁实用的设计原则，在保持出色的性能和至简的代码的同时，也注重易用性。

### 二、环境搭建

#### 2.1 Thinkphp环境搭建

安装环境：Mac Os MAMP集成软件

PHP版本：5.6.10

Thinkphp版本：5.1.20

thinkphp安装包获取（Composer方式）：

首先需要安装composer。

curl -sS https://getcomposer.org/installer | php

下载后，检查Composer是否能正常工作，只需要通过 php 来执行 PHAR：

![img](https://images.seebug.org/content/images/2019/04/10/1554882464000-f9875e2e8c7504e93327da8c403b6234.png-w331s)

若返回信息如上图，则证明成功。

然后将composer.phar 移动到bin目录下并改名为composer

    
    
    mv composer.phar /usr/local/bin/composer

Composer安装好之后，打开命令行，切换到你的web根目录下面并执行下面的命令：

    
    
    composer create-project topthink/think=5.1.20 tp5.1.20  –prefer-dist

若需要其他版本，可通过修改版本号下载。

验证是否可以正常运行，在浏览器中输入地址：

http://localhost/tp5.1.20/public/

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-96114f3ea9a17b0237ebbc9f52f5310d.png-w331s)

如果出现上图所示，那么恭喜你安装成功。

#### 2.2 IDE环境搭建及xdebug配置

PHP IDE工具有很多，我推荐PhpStorm，因为它支持所有PHP语言功能， 提供最优秀的代码补全、重构、实时错误预防、快速导航功能。

PhpStorm下载地址：<https://www.jetbrains.com/phpstorm/>

Xdebug

Xdebug是一个开放源代码的PHP程序调试器，可以用来跟踪，调试和分析PHP程序的运行状况。在调试分析代码时，xdebug十分好用。

下面我们说一下xdebug怎么配置（MAMP+PHPstrom）

1.下载安装xdebug扩展(MAMP自带 ）。

2.打开php.ini文件，添加xdebug相关配置

[xdebug]

xdebug.remote_enable = 1

xdebug.remote_handler = dbgp

xdebug.remote_host = 127.0.0.1

xdebug.remote_port = 9000 #端口号可以修改，避免冲突

xdebug.idekey = PHPSTROM

然后重启服务器。

3.客户端phpstorm配置

3.1点击左上角phpstorm，选择preferences

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-7c215d91e766994c2352ce742e6f9343.png-w331s)

3.2 Languages & Frameworks -> PHP，选择PHP版本号，选择PHP执行文件。

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-6d4a042aed8a06b8adcbf7b9cdf7b574.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-61a6c3adbfc82b5b097b688ae8a88ce8.png-w331s)

在选择PHP执行文件的时候，会显示 “Debugger:Xdebug”，如果没有的话，点击open打开配置文件。

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-fa352ae753ff09e390de0ecb2a426021.png-w331s)

将注释去掉即可。

3.3配置php下的Debug

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-1052fe1888fb237f12c83eb53cf37a80.png-w331s)

Port和配置文件中的xdebug.remote_port要一致。

3.4配置Debug下的DBGp proxy

![img](https://images.seebug.org/content/images/2019/04/10/1554882465000-cbe1f04d817b2ad17eed76863dc3eee3.png-w331s)

填写的内容和上面php.ini内的相对应。

3.5配置servers

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-7cdc5ac91428a5bd2339d44bdba321a7.png-w331s)

点击+号添加

3.6配置debug模式

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-146eeb3b893dcb9143e745ea647c3588.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-49a9cf90178d630f525169f4119a79eb.png-w331s)

在Server下拉框中，选择我们在第4步设置的Server服务名称，Browser选择你要使用的浏览器。所有配置到此结束。

4.xdebug使用

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-f03395e0b11d6b36dfc5ec8d068fc08e.png-w331s)

开启xdeubg监听

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-d5d25dc082e6e26bcb6357f52efda1b7.png-w331s)

下一个断点，然后访问URL，成功在断点处停下。

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-31a98b56a250a46f1ec0cd5b6e5065cf.png-w331s)

### 三、框架流程浅析

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-5aad84823cf9fcec077b77e58d1f602c.png-w331s)

我们先看入口文件index.php，入口文件非常简洁，只有三行代码。

可以看到这里首先定义了一下命名空间，然后加载一些基础文件后，就开始执行应用。

第二行引入base.php基础文件，加载了Loader类，然后注册了一些机制–如自动加载功能、错误异常的机制、日志接口、注册类库别名。

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-cde641f08e7a5dd58d4c9ad84b2ea0c5.png-w331s)

这些机制中比较重要的一个是自动加载功能，系统会调用
Loader::register()方法注册自动加载，在这一步完成后，所有符合规范的类库（包括Composer依赖加载的第三方类库）都将自动加载。下面我详细介绍下这个自动加载功能。

首先需要注册自动加载功能，注册主要由以下几部分组成:

  1. 注册系统的自动加载方法 \think\Loader::autoload

  2. 注册系统命名空间定义

  3. 加载类库映射文件（如果存在）

  4. 如果存在Composer安装，则注册Composer自动加载

  5. 注册extend扩展目录

其中2.3.4.5是为自动加载时查找文件路径的时候做准备，提前将一些规则(类库映射、PSR-4、PSR-0)配置好。

然后再说下自动加载流程，看看程序是如何进行自动加载的？

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-464a7b5c5702e9816d905fc98fafb119.png-w331s)

spl_autoload_register()是个自动加载函数，当我们实例化一个未定义的类时就会触发此函数，然后再触发指定的方法，函数第一个参数就代表要触发的方法。

可以看到这里指定了think\Loader::autoload()这个方法。

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-9392e9b81da1fdec76fe6abdc80e5d29.png-w331s)

首先会判断要实例化的`$class`类是否在之前注册的类库别名`$classAlias`中，如果在就返回,不在就进入findFile()方法查找文件，

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-bbf301446f7edb4b974ed59e02cfe84d.png-w331s)

这里将用多种方式进行查找，以类库映射、PSR-4自动加载检测、PSR-0自动加载检测的顺序去查找(这些规则方式都是之前注册自动加载时配置好的)，最后会返回类文件的路径，然后include包含，进而成功加载并定义该类。

这就是自动加载方法，按需自动加载类，不需要一一手动加载。在面向对象中这种方法经常使用，可以避免书写过多的引用文件，同时也使整个系统更加灵活。

在加载完这些基础功能之后，程序就会开始执行应用，它首先会通过调用Container类里的静态方法get()去实例化app类，接着去调用app类中的run()方法。

![img](https://images.seebug.org/content/images/2019/04/10/1554882466000-263617ec3c77f0f27a6d3291ba4daf20.png-w331s)

在run()方法中，包含了应用执行的整个流程。

  1. `$this->initialize()`，首先会初始化一些应用。例如：加载配置文件、设置路径环境变量和注册应用命名空间等等。

  2. `this->hook->listen(‘app_init’);` 监听app_init应用初始化标签位。Thinkphp中有很多标签位置，也可以把这些标签位置称为钩子，在每个钩子处我们可以配置行为定义，通俗点讲，就是你可以往钩子里添加自己的业务逻辑，当程序执行到某些钩子位置时将自动触发你的业务逻辑。

  3. 模块\入口绑定

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-028ac665d62678becf04c81d1d6f6a4e.png-w331s)

进行一些绑定操作，这个需要配置才会执行。默认情况下，这两个判断条件均为false。

  4. `$this->hook->listen(‘app_dispatch’);`监听app_dispatch应用调度标签位。和2中的标签位同理，所有标签位作用都是一样的，都是定义一些行为，只不过位置不同，定义的一些行为的作用也有所区别。

  5. `$dispatch = $this->routeCheck()->init();` 开始路由检测，检测的同时会对路由进行解析，利用array_shift函数一一获取当前请求的相关信息（模块、控制器、操作等）。

  6. `$this->request->dispatch($dispatch);`记录当前的调度信息,保存到request对象中。

  7. 记录路由和请求信息

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-6d24351f02fce4d81bb5cd05ee9f307b.png-w331s)

如果配置开启了debug模式，会把当前的路由和请求信息记录到日志中。

  8. `$this->hook->listen(‘app_begin’);` 监听app_begin(应用开始标签位)。

  9. 根据获取的调度信息执行路由调度

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-35e39e1f2569786cb66881677b16e7bd.png-w331s)

期间会调用Dispatch类中的exec()方法对获取到的调度信息进行路由调度并最终获取到输出数据$response。

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-88fb318bc2af65e123982f7e9f782286.png-w331s)

然后将`$response`返回，最后调用Response类中send()方法，发送数据到客户端，将数据输出到浏览器页面上。

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-43f5008f87ad15fef43db3f9966ebe28.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-b3f5061c7f09d3e6d6904dc4e585b36e.png-w331s)

在应用的数据响应输出之后，系统会进行日志保存写入操作，并最终结束程序运行。

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-8ceb27f29fb1c1f397d41a97d106137d.png-w331s)

### 四、漏洞预备知识

这部分主要讲解与漏洞相关的知识点，有助于大家更好地理解漏洞形成原因。

#### 4.1命名空间特性

ThinkPHP5.1遵循PSR-4自动加载规范，只需要给类库正确定义所在的命名空间，并且命名空间的路径与类库文件的目录一致，那么就可以实现类的自动加载。

例如，\think\cache\driver\File类的定义为：

    
    
    namespace think\cache\driver;
    
    class File
    
    {
    
    }

如果我们实例化该类的话，应该是：

    
    
    $class = new \think\cache\driver\File();

系统会自动加载该类对应路径的类文件，其所在的路径是 thinkphp/library/think/cache/driver/File.php。

可是为什么路径是在thinkphp/library/think下呢？这就要涉及要另一个概念—根命名空间。

##### 4.1.1 根命名空间

根命名空间是一个关键的概念，以上面的\think\cache\driver\File类为例，think就是一个根命名空间，其对应的初始命名空间目录就是系统的类库目录（thinkphp/library/think），我们可以简单的理解一个根命名空间对应了一个类库包。

系统内置的几个根命名空间（类库包）如下：

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-9a5460d8e8a1ef8fb7355b1109a3420a.png-w331s)

#### 4.2 URL访问

在没有定义路由的情况下典型的URL访问规则（PATHINFO模式）是：

http://serverName/index.php（或者其它应用入口文件）/模块/控制器/操作/[参数名/参数值...]

如果不支持PATHINFO的服务器可以使用兼容模式访问如下

http://serverName/index.php（或者其它应用入口文件）?s=/模块/控制器/操作/[参数名/参数值...]

什么是pathinfo模式?

我们都知道一般正常的访问应该是

http://serverName/index.php?m=module&c=controller&a=action&var1=vaule1&var2=vaule2

而pathinfo模式是这样的

http://serverName/index.php/module/controller/action/var1/vaule1/var2/value2

在php中有一个全局变量`$_SERVER['PATH_INFO']`，我们可以通过它来获取index.php后面的内容。

什么是`$_SERVER['PATH_INFO']`?

官方是这样定义它的：包含由客户端提供的、跟在真实脚本名称之后并且在查询语句（query string）之前的路径信息。

什么意思呢？简单来讲就是获得访问的文件和查询?之间的内容。

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-8acb34a0d61fe4c23370242a7fc5ce9a.png-w331s)

强调一点，在通过`$_SERVER['PATH_INFO']`获取值时，系统会把’\'自动转换为’/'（这个特性我在Mac
Os(MAMP)、Windows(phpstudy)、Linux(php+apache)环境及php5.x、7.x中进行了测试，都会自动转换，所以系统及版本之间应该不会有所差异）。

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-b50971cf1cb65e8c5e59697ccb41422f.png-w331s)

下面再分别介绍下入口文件、模块、控制器、操作、参数名/参数值。

1.入口文件

文件地址：public\index.php

作用：负责处理请求

2.模块（以前台为例）

模块地址：application\index

作用：网站前台的相关部分

3.控制器

控制器目录：application\index\controller

作用：书写业务逻辑

  1. 操作（方法）

在控制器中定义的方法

  1. 参数名/参数值

方法中的参数及参数值

例如我们要访问index模块下的Test.php控制器文件中的hello()方法。

![img](https://images.seebug.org/content/images/2019/04/10/1554882467000-48acb8ba75619ee7d3a7bcb1379ab26a.png-w331s)

那么可以输入http://serverName/index.php/index(模块)/Test(控制器)/hello(方法)/name(参数名)/world(参数值)

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-bc8ec991e62fdb7e18d01b5acca157e6.png-w331s)

这样就访问到指定文件了。

另外再讲一下Thinkphp的几种传参方式及差别。

PATHINFO: index.php/index/Test/hello/name/world 只能以这种方式传参。

兼容模式:index.php?s=index/Test/hello/name/world

index.php?s=index/Test/hello&name=world

当我们有两个变量`$a`、`$b`时，在兼容模式下还可以将两者结合传参：

index.php?s=index/Test/hello/a/1&b=2

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-a6896418d9c1c1ac1423a1858f4c98fe.png-w331s)

这时，我们知道了URL访问规则，当然也要了解下程序是怎样对URL解析处理，最后将结果输出到页面上的。

#### 4.3 URL路由解析动态调试分析

URL路由解析及页面输出工作可以分为5部分。

  1. 路由定义：完成路由规则的定义和参数设置

  2. 路由检测：检查当前的URL请求是否有匹配的路由

  3. 路由解析：解析当前路由实际对应的操作。

  4. 路由调度：执行路由解析的结果调度。

  5. 响应输出及应用结束：将路由调度的结果数据输出至页面并结束程序运行。

我们通过动态调试来分析，这样能清楚明了的看到程序处理的整个流程，由于在Thinkphp中，配置不同其运行流程也会不同，所以我们采用默认配置来进行分析，并且由于在程序运行过程中会出现很多与之无关的流程，我也会将其略过。

##### 4.3.1 路由定义

通过配置route目录下的文件对路由进行定义，这里我们采取默认的路由定义，就是不做任何路由映射。

##### 4.3.2 路由检测

这部分内容主要是对当前的URL请求进行路由匹配。在路由匹配前先会获取URL中的pathinfo，然后再进行匹配，但如果没有定义路由，则会把当前pathinfo当作默认路由。

首先我们设置好IDE环境，并在路由检测功能处下断点。

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-e15610dc13d2b706bba0f03160c92584.png-w331s)

然后我们请求上面提到的Test.php文件。

http://127.0.0.1/tp5.1.20/public/index.php/index/test/hello/name/world

我这里是以pathinfo模式请求的，但是其实以不同的方式在请求时，程序处理过程是有稍稍不同的，主要是在获取参数时不同。在后面的分析中，我会进行说明。

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-ef5e48d50bfaad2fd6e383365b43842b.png-w331s)

F7跟进routeCheck()方法

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-75b17d36b7799eda56dc05abecfa0237.png-w331s)

route_check_cache路由缓存默认是不开启的。

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-19185c7ca263e4f5af97919e58eede1e.png-w331s)

然后我们进入path()方法

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-80302b5359356c17f38b3a0907f6f42a.png-w331s)

继续跟进pathinfo()方法

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-295c796e62e7f7b2a011b82c70da82cf.png-w331s)

这里会根据不同的请求方式获取当前URL的pathinfo信息，因为我们的请求方式是pathinfo,所以会调用`$this->server(‘PATH_INFO’)`去获取，获取之后会使用ltrim()函数对`$pathinfo`进行处理去掉左侧的’/’符号。Ps:如果以兼容模式请求，则会用`$_GET`方法获取。

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-b0c16f156988b4db2f5dc44deda8cf65.png-w331s)

然后返回赋值给`$path`并将该值带入check()方法对URL路由进行检测

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-3b4e1268a07275d2436e04b039335370.png-w331s)

这里主要是对我们定义的路由规则进行匹配，但是我们是以默认配置来运行程序的，没有定义路由规则，所以跳过中间对于路由检测匹配的过程，直接来看默认路由解析过程，使用默认路由对其进行解析。

##### 4.3.3 路由解析

接下来将会对路由地址进行了解析分割、验证、格式处理及赋值进而获取到相应的模块、控制器、操作名。

new UrlDispatch()
对UrlDispatch（实际上是think\route\dispatch\Url这个类）实例化，因为Url没有构造函数，所以会直接跳到它的父类Dispatch的构造函数，把一些信息传递（包括路由）给Url类对象，这么做的目的是为了后面在调用Url类中方法时方便调用其值。

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-7a2b6b470d937562e0adcb2a3d57537c.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882468000-c062499cd13efaabe7b9a20c38d92856.png-w331s)

赋值完成后回到routeCheck()方法，将实例化后的Url对象赋给`$dispatch`并return返回。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-62f3163369ea9299dba6b53743f88baa.png-w331s)

返回后会调用Url类中的init()方法，将`$dispatch`对象中的得到`$this->dispatch(路由)`传入parseUrl()方法中，开始解析URL路由地址。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-eddd2f248c6e401a034bd494751a1ae0.png-w331s)

跟进parseUrl()方法

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-e5ffe71990f002ad5766536d956e383e.png-w331s)

这里首先会进入parseUrlPath()方法，将路由进行解析分割。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-0caf928128a69b53f250530366249029.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-538b046b493889c850014cb15423d79d.png-w331s)

使用”/”进行分割，拿到 [模块/控制器/操作/参数/参数值]。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-4badd4e3741860e859e1f072e00e7de3.png-w331s)

紧接着使用array_shift()函数挨个从`$path`数组中取值对模块、控制器、操作、参数/参数值进行赋值。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-f2cf000b1c72792197a29fdb27ab64d2.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-dcc2d7819e2e9ed53351c54b31058c2f.png-w331s)

接着将参数/参数值保存在了Request类中的Route变量中，并进行路由封装将赋值后的`$module`、`$controller`、`$action`存到route数组中，然后将`$route`返回赋值给`$result`变量。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-1d2663a073cbf4bd880ec8b302313110.png-w331s)

`new Module($this->request, $this->rule, $result)`，实例化Module类。

在Module类中也没有构造方法，会直接调用Dispatch父类的构造方法。

![img](https://images.seebug.org/content/images/2019/04/10/1554882469000-f6a71095d6026eb20368d59a815e89b4.png-w331s)

然后将传入的值都赋值给Module类对象本身`$this`。此时，封装好的路由`$result`赋值给了`$this->dispatch`，这么做的目的同样是为了后面在调用Module类中方法时方便调用其值。

实例化赋值后会调用Module类中的init()方法，对封装后的路由(模块、控制器、操作)进行验证及格式处理。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-6173c9910a9be9f6807b78476f099999.png-w331s)

`$result =
$this->dispatch`，首先将封装好的路由`$this->dispatch`数组赋给`$result`，接着会从`$result`数组中获取到了模块`$module`的值并对模块进行大小写转换和html标签处理，接下来会对模块值进行检测是否合规，若不合规，则会直接HttpException报错并结束程序运行。检测合格之后，会再从`$result`中获取控制器、操作名并处理，同时会将处理后值再次赋值给`$this`(Module类对象)去替换之前的值。

Ps：从`$result`中获取值时，程序采用了三元运算符进行判断，如果相关值为空会一律采用默认的值index。这就是为什么我们输入http://127.0.0.1/tp5.1.20/public/index.php在不指定模块、控制器、操作值时会跳到程序默认的index模块的index控制器的index操作中去。

此时调度信息(模块、控制器、操作)都已经保存至Module类对象中，在之后的路由调度工作中会从中直接取出来用。

然后返回Module类对象`$this`，回到最开始的App类，赋值给`$dispatch`。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-9cc845da4762daee6a0c05ba851831f4.png-w331s)

至此，路由解析工作结束，到此我们获得了模块、控制器、操作，这些值将用于接下来的路由调度。

**接下来在路由调度前，需要另外说明一些东西**
：路由解析完成后，如果debug配置为True，则会对路由和请求信息进行记录，这里有个很重要的点param()方法, 该方法的作用是获取变量参数。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-c3709a811b230ace93ba6177afa554ed.png-w331s)

在这里，在确定了请求方式(GET)后，会将请求的参数进行合并，分别从`$_GET`、`$_POST`(这里为空)和Request类的route变量中进行获取。然后存入Request类的param变量中，接着会对其进行过滤，但是由于没有指定过滤器，所以这里并不会进行过滤操作。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-9d64557af7cd5afb7cefb8929c5d4e19.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-2d7ba7f2a141ed970c77ef8cb942496a.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-eb119f9cb8422f9300947c6e9549c4b7.png-w331s)

Ps：这里解释下为什么要分别从`$_GET`中和Request类的route变量中进行获取合并。上面我们说过传参有三种方法。

  1. index/Test/hello/name/world

  2. index/Test/hello&name=world

  3. index/Test/hello/a/1&b=2

当我们如果选择1进行请求时，在之前的路由检测和解析时，会将参数/参数值存入Request类中的route变量中。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-e3b5cb547ce5a2fd5f375a0081270ca3.png-w331s)

而当我们如果选择2进行请求时，程序会将&前面的值剔除，留下&后面的参数/参数值，保存到`$_GET`中。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-64202636fe552602b07a2aa5226a685f.png-w331s)

并且因为Thinkphp很灵活，我们还可以将这两种方式结合利用，如第3个。

这就是上面所说的在请求方式不同时，程序在处理传参时也会不同。

Ps：在debug未开启时,参数并不会获得，只是保存在route变量或`$_GET[]`中，不过没关系，因为在后面路由调度时还会调用一次param()方法。

继续调试，开始路由调度工作。

##### 4.3.4 路由调度

这一部分将会对路由解析得到的结果(模块、控制器、操作)进行调度，得到数据结果。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-02befa9cf8dc453f2bec0cac3c46b04c.png-w331s)

这里首先创建了一个闭包函数，并作为参数传入了add方法()中。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-629bfa35c186628924ff465c2da7eecd.png-w331s)

将闭包函数注册为中间件，然后存入了`$this->queue[‘route’]`数组中。

然后会返回到App类， `$response =
$this->middleware->dispatch($this->request);`执行middleware类中的dispatch()方法，开始调度中间件。

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-2bc86ec06b62c6e8829cbef910bb7b18.png-w331s)

使用`call_user_func()`回调`resolve()`方法，

![img](https://images.seebug.org/content/images/2019/04/10/1554882470000-91614c4a8dd02a42ed80386a592d107e.png-w331s)

使用`array_shift()`函数将中间件(闭包函数)赋值给了`$middleware`，最后赋值给了`$call`变量。

![img](https://images.seebug.org/content/images/2019/04/10/1554882471000-2b1c1c5045a16f6222b67102a7cb6b40.png-w331s)

当程序运行至`call_user_func_array()`函数继续回调，这个`$call`参数是刚刚那个闭包函数，所以这时就会调用之前App类中的闭包函数。

中间件的作用官方介绍说主要是用于拦截或过滤应用的HTTP请求，并进行必要的业务处理。所以可以推测这里是为了调用闭包函数中的run()方法，进行路由调度业务。

然后在闭包函数内调用了Dispatch类中的run()方法，开始执行路由调度。

![img](https://images.seebug.org/content/images/2019/04/10/1554882471000-9accf1fbd3637f952b070c2abdece87b.png-w331s)

跟进exec()方法

![img](https://images.seebug.org/content/images/2019/04/10/1554882471000-04f4ab0579b2a416a4b8e53a62872687.png-w331s)

可以看到，这里对我们要访问的控制器Test进行了实例化，我们来看下它的实例化过程。

![img](https://images.seebug.org/content/images/2019/04/10/1554882471000-c4dd432c1ccfde1ce2d75ae6e82d7481.png-w331s)

将控制器类名`$name`和控制层`$layer`传入了parseModuleAndClass()方法，对模块和类名进行解析，获取类的命名空间路径。

![img](https://images.seebug.org/content/images/2019/04/10/1554882471000-5ac7ae5d70228d71ad9eb260d5610258.png-w331s)

在这里如果`$name`类中以反斜线\开始时就会直接将其作为类的命名空间路径。此时`$name`是test，明显不满足，所以会进入到else中，从request封装中获取模块的值`$module`，然后程序将模块`$module`、控制器类名`$name`、控制层`$layer`再传入parseClass()方法。

![img](https://images.seebug.org/content/images/2019/04/10/1554882471000-cb524f46ae7945e2d05fa57b807faeea.png-w331s)

对`$name`进行了一些处理后赋值给`$class`，然后将`$this->namespace`、`$module`、`$layer`、`$path`、`$class`拼接在一起形成命名空间后返回。

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-46f576af662441878b9fcc30e9489a2e.png-w331s)

到这我们就得到了控制器Test的命名空间路径，根据Thinkphp命名空间的特性，获取到命名空间路径就可以对其Test类进行加载。

F7继续调试，返回到了刚刚的controller()方法，开始加载Test类。

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-a876050d49d070ca999b6eec0f5e01bf.png-w331s)

加载前，会先使用class_exists()函数检查Test类是否定义过，这时程序会调用自动加载功能去查找该类并加载。

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-5cf5d94934778bd378d5d9935f815248.png-w331s)

加载后调用__get()方法内的make()方法去实例化Test类。

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-f55795c5510a80983b16982cd17a63bc.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-7d2780ec042218074ab3356c0f80517b.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-0457af351582663ac9e9a5e6a9a45525.png-w331s)

这里使用反射调用的方法对Test类进行了实例化。先用ReflectionClass创建了Test反射类，然后 `return
$reflect->newInstanceArgs($args);`
返回了Test类的实例化对象。期间顺便判断了类中是否定义了__make方法、获取了构造函数中的绑定参数。

![img](https://images.seebug.org/content/images/2019/04/10/1554882472000-4706b69c1c205783f863a6fe9da83490.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882473000-f9758a67e89866ce5748154938876264.png-w331s)

然后将实例化对象赋值赋给`$object`变量，接着返回又赋给`$instance变`量。

继续往下看

这里又创建了一个闭包函数作为中间件，过程和上面一样，最后利用`call_user_func_array()`回调函数去调用了闭包函数。

![img](https://images.seebug.org/content/images/2019/04/10/1554882473000-eed697c0c27b4f7a8195efb8045ea4e4.png-w331s)

在这个闭包函数内，主要做了4步。

  1. 使用了is_callable()函数对操作方法和实例对象作了验证，验证操作方法是否能用进行调用。

  2. new ReflectionMethod()创建了Test的反射类`$reflect`。

  3. 紧接着由于url_param_type默认为0，所以会调用param()方法去请求变量，但是前面debug开启时已经获取到了并保存进了Request类对象中的param变量，所以此时只是从中将值取出来赋予`$var`变量。

  4. 调用invokeReflectMethod()方法，并将Test实例化对象`$instance`、反射类`$reflect`、请求参数`$vars`传入。

![img](https://images.seebug.org/content/images/2019/04/10/1554882473000-33429a2857c5498905d864360223b026.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882473000-c2db35fb1c401263d0c459b0d0463cea.png-w331s)

这里调用了`bindParams()`方法对`$var`参数数组进行处理，获取了Test反射类的绑定参数，获取到后将`$args`传入`invokeArgs()`方法，进行反射执行。

然后程序就成功运行到了我们访问的文件(Test)。

![img](https://images.seebug.org/content/images/2019/04/10/1554882473000-8b5adbec9509ba79f97262a822de1e2b.png-w331s)

运行之后返回数据结果，到这里路由调度的任务也就结束了，剩下的任务就是响应输出了，将得到数据结果输出到浏览器页面上。

##### 4.3.5 响应输出及应用结束

这一小节会对之前得到的数据结果进行响应输出并在输出之后进行扫尾工作结束应用程序运行。在响应输出之前首先会构建好响应对象，将相关输出的内容存进Response对象，然后调用Response::send()方法将最终的应用返回的数据输出到页面。

继续调试，来到autoResponse()方法，这个方法程序会来回调用两次，第一次主要是为了创建响应对象，第二次是进行验证。我们先来看第一次，

![img](https://images.seebug.org/content/images/2019/04/10/1554882473000-5ddd65425cec180dd3977648f7f2d980.png-w331s)

此时`$data`不是Response类的实例化对象，跳到了elseif分支中，调用Response类中的create()方法去获取响应输出的相关数据，构建Response对象。

![img](https://images.seebug.org/content/images/2019/04/10/1554882474000-60c81334cbe675874abbdf6ba75e9601.png-w331s)

执行`new static($data, $code, $header,
$options);`实例化自身Response类，调用`__construct()`构造方法。

![img](https://images.seebug.org/content/images/2019/04/10/1554882474000-83b1e3312e85be8bd7804913e7eded07.png-w331s)

可以看到这里将输出内容、页面的输出类型、响应状态码等数据都传递给了Response类对象，然后返回，回到刚才autoResponse()方法中

![img](https://images.seebug.org/content/images/2019/04/10/1554882474000-86443fdf9d4cbb3b74caa5dd513fcc94.png-w331s)

到此确认了具体的输出数据，其中包含了输出的内容、类型、状态码等。

上面主要做的就是构建响应对象，将要输出的数据全部封装到Response对象中，用于接下来的响应输出。

继续调试，会返回到之前Dispatch类中的run()方法中去，并将`$response`实例对象赋给`$data`。

![img](https://images.seebug.org/content/images/2019/04/10/1554882474000-f34c5faf64dde5a897abebfc9ded098e.png-w331s)

紧接着会进行autoResponse()方法的第二次调用，同时将`$data`传入，进行验证。

![img](https://images.seebug.org/content/images/2019/04/10/1554882474000-4e60439b88b63bb2009e706ff2b04162.png-w331s)

这回`$data`是Response类的实例化对象，所以将`$data`赋给了`$response`后返回。

然后就开始调用Response类中send()方法，向浏览器页面输送数据。

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-dbc2eec242030d2953d991208276a47e.png-w331s)

这里依次向浏览器发送了状态码、header头信息以及得到的内容结果。

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-dc371a35ce7650796993801595938faa.png-w331s)

输出完毕后，跳到了appShutdown()方法，保存日志并结束了整个程序运行。

#### 4.4 流程总结

上面通过动态调试一步一步地对URL解析的过程进行了分析，现在我们来简单总结下其过程：

首先发起请求->开始路由检测->获取pathinfo信息->路由匹配->开始路由解析->获得模块、控制器、操作方法调度信息->开始路由调度->解析模块和类名->组建命名空间>查找并加载类->实例化控制器并调用操作方法->构建响应对象->响应输出->日志保存->程序运行结束

### 五、漏洞分析及POC构建

相信大家在看了上述内容后，对Thinkphp这个框架应该有所了解了。接下来，我们结合最近一个思路比较好的RCE漏洞再来看下。为了更好地理解漏洞，我通过以POC构造为导引的方式对漏洞进行了分析，同时以下内容也体现了我在分析漏洞时的想法及思路。

在/thinkphp/library/think/Container.php 中340行：

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-965c4a51534be63fa0ba219131c404bd.png-w331s)

在Container类中有个`call_user_func_array()`回调函数，经常做代码审计的小伙伴都知道，这个函数非常危险，只要能控制`$function`和`$args`，就能造成代码执行漏洞。

如何利用此函数？

通过上面的URL路由分析，我们知道Thinkphp可由外界直接控制模块名、类名和其中的方法名以及参数/参数值，那么我们是不是可以将程序运行的方向引导至这里来。

如何引导呢？

要调用类肯定需要先将类实例化，类的实例化首先需要获取到模块、类名，然后解析模块和类名去组成命名空间，再根据命名空间的特性去自动加载类，然后才会实例化类和调用类中的方法。

我们先对比之前正常的URL试着构建下POC。

http://127.0.0.1/tp5.1.20/public/index.php/index/test/hello/name/world

http://127.0.0.1/tp5.1.20/public/index.php/模块?/Container/invokefunction

构建过程中，会发现几个问题。

  1. 模块应该指定什么，因为Container类并不在模块内。

  2. 模块和类没有联系，那么组建的命名空间，程序如何才能加载到类。

先别着急，我们先从最开始的相关值获取来看看（获取到模块、类名），此过程对应上面第四大节中的4.3.3路由解析中。

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-b39092379db0354a1ae1b746895e073f.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-e0d130687d4fcb9645a756b513161b3a.png-w331s)

app_multi_module为true，所以肯定进入if流程,获取了`$module`、`$bind`、`$available`的值。在红色框处如果不为true，则会直接报错结束运行，所以此处需要`$module`和`$available`都为True。而$available的值一开始就被定义为False，只有在后续的3个if条件中才会变为true。

来看下这3个if条件，在默认配置下，由于没有路由绑定，所以`$bind`为null。而empty_module默认模块也没有定义。所以第三个也不满足，那么只能寄托于第二个了。

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-3fff0cea09f294d36ccf079a6ba692f3.png-w331s)

在第二个中，1是判断`$module`是否在禁止访问模块的列表中，2是判断是否存在这个模块。

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-932650e94255813dafed3e27d4137d56.png-w331s)

![img](https://images.seebug.org/content/images/2019/04/10/1554882475000-8a4f6abc9d0c0bfcb478fc366849ac26.png-w331s)

所以，这就要求我们在构造POC时，需要保证模块名必须真实存在并且不能在禁用列表中。在默认配置中，我们可以指定index默认模块，但是在实际过程中，index模块并不一定存在，所以就需要大家去猜测或暴力破解了，不过一般模块名一般都很容易猜解。

获取到模块、类名后，就是对其进行解析组成命名空间了。此过程对应上面第四大节中的4.3.4路由调度中。

![img](https://images.seebug.org/content/images/2019/04/10/1554882476000-4b2e5a15f2b7b4e070fea85f269db7c9.png-w331s)

这里首先对`$name`(类名)进行判断，当`$name`以反斜线\开始时会直接将其作为类的命名空间路径。看到这里然后回想一下之前的分析，我们会发现这种命名空间路径获取的方式和之前获取的方式不一样(之前是进入了parseClass方法对模块、类名等进行拼接)，而且这种获取是不需要和模块有联系的，所以我们想是不是可以直接将类名以命名空间的形式传入，然后再以命名空间的特性去自动加载类？同时这样也脱离了模块这个条件的束缚。

那我们现在再试着构造下POC：

![img](https://images.seebug.org/content/images/2019/04/10/1554882476000-d3e4657c8a4dbff38b0025030fc4feb3.png-w331s)

http://127.0.0.1/tp5.1.20/public/index.php/index/think\Container/invokefunction

剩下就是指定`$function`参数和`$var`参数值了,根据传参特点，我们来构造下。

http://127.0.0.1/tp5.1.20/public/index.php/index/think\Container/invokefunction/function/call_user_func_array/vars[0]/phpinfo/vars[1][]/1

构造出来应该是这样的，但是由于在pathinfo模式下，`$_SERVER['PATH_INFO']`会自动将URL中的“\”替换为“/”，导致破坏掉命名空间格式，所以我们采用兼容模式。

默认配置中，`var_pathinfo`默认为s，所以我们可以用`$_GET[‘s’]`来传递路由信息。

http://127.0.0.1/tp5.1.20/public/index.php?s=index/think\Container/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

另外由于App类继承于Container类，所以POC也可以写成：

http://127.0.0.1/tp5.1.20/public/index.php?s=index/think\App/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

**漏洞利用扩大化**

  1. 以反斜线\开始时直接将其作为类的命名空间路径。

  2. thinkphp命名空间自动加载类的特性。

由于这两点，就会造成我们可以调用thinkphp框架中的任意类。所以在框架中，如果其他类方法中也有类似于invokefunction()方法中这样的危险函数，我们就可以随意利用。

例如：Request类中的input方法中就有一样的危险函数。

![img](https://images.seebug.org/content/images/2019/04/10/1554882476000-6bf873bdd34ac0695423c1c658936711.png-w331s)

跟入filterValue()方法

![img](https://images.seebug.org/content/images/2019/04/10/1554882477000-a551d3cdec646bd6b122a4b2447cebab.png-w331s)

POC:

![img](https://images.seebug.org/content/images/2019/04/10/1554882477000-dacd2916a83e58a12213fc03c9cb2fb8.png-w331s)

http://127.0.0.1/tp5.1.20/public/index.php?s=index/\think\Request/input&filter=phpinfo&data=1

### 六、结语

写这篇文章的其中一个目的是想让大家知道，通过框架分析，我们不仅可以在分析漏洞时变得更加容易，同时也可以对漏洞原理有一个更深的理解。所以，当我们在分析一个漏洞时，如果很吃力或者总有点小地方想不通的时候，不如从它的框架着手，一步一步来，或许在你学习完后就会豁然开朗，亦或者在过程中你就会明白为什么。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/888/>

