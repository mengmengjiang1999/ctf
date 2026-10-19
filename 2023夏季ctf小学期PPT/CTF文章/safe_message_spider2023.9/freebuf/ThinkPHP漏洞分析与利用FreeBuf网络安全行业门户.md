## ****一、组件介绍****

###  ** **1.1 基本信息****

ThinkPHP是一个快速、兼容而且简单的轻量级国产PHP开发框架，遵循Apache
2开源协议发布，使用面向对象的开发结构和MVC模式，融合了Struts的思想和TagLib（标签库）、RoR的ORM映射和ActiveRecord模式。

ThinkPHP可以支持windows/Unix/Linux等服务器环境，正式版需要PHP
5.0以上版本，支持MySql、PgSQL、Sqlite多种数据库以及PDO扩展。

###  ** **1.2 版本介绍****

ThinkPHP发展至今，核心版本主要有以下几个系列，ThinkPHP 2系列、ThinkPHP 3系列、ThinkPHP 5系列、ThinkPHP
6系列，各个系列之间在代码实现及功能方面，有较大区别。其中ThinkPHP 2以及ThinkPHP 3系列已经停止维护，ThinkPHP
5系列现使用最多，而ThinkPHP 3系列也积累了较多的历史用户。版本细分如下图所示：

![](https://image.3001.net/images/20200908/1599567214.png!small)

##  ** **二、高危漏洞介绍****

通过对ThinkPHP漏洞的收集和整理，过滤出其中的高危漏洞，可以得出如下列表：

![](https://image.3001.net/images/20200908/1599567240.png!small)

从上表数据来看，ThinkPHP 3系列版本的漏洞多是2016/2017年被爆出，而ThinkPHP
5系列版本的漏洞基本为2017/2018年被爆出，从2020年开始，ThinkPHP 6系列的漏洞也开始被挖掘。

从中可以看出，ThinkPHP近年出现的高风险漏洞主要存在于框架中的函数，这些漏洞均需要在二次开发的过程中使用了这些风险函数方可利用，所以这些漏洞更应该被称为框架中的风险函数，且这些风险点大部分可导致SQL注入漏洞，所以，开发者在利用ThinkPHP进行Web开发的过程中，一定需要关注这些框架的历史风险点，尽量规避这些函数或者版本，则可保证web应用的安全性。

##  ** **三、漏洞利用链****

###  ** **3.1、暴露面梳理****

根据ThinkPHP的历史高危漏洞，梳理出分版本的攻击风险点，开发人员可根据以下图标，来规避ThinkPHP的风险版本，如下ThinkPHP暴露面脑图。

![](https://image.3001.net/images/20200908/1599567391.png!small)

###  ** **3.2、利用链总结****

基于暴露面脑图，我们可以得出几种可以直接利用的ThinkPHP框架漏洞利用链，不需要进行二次开发。

####  ** **3.2.1、ThinkPHP 2.x/3.0 GetShell****

![](https://image.3001.net/images/20200908/1599567500.png!small)

 ** **ThinkPHP低于3.0 - GetShell****

ThinkPHP 低版本可以使用以上漏洞执行任意系统命令，获取服务器权限。

####  ** **3.2.2、ThinkPHP 5.0 GetShell****

![](https://image.3001.net/images/20200908/1599567515.png!small)

 ** **ThinkPHP 5.0.x - GetShell****

首先明确ThinkPHP框架系列版本。

根据ThinkPHP版本，如是0.x版本，即可使用ThinkPHP 5.x远程代码执行漏洞，无需登录，即可执行任意命令，获取服务器最高权限。

####  ** **3.2.3、ThinkPHP 5.1 GetShell****

![](https://image.3001.net/images/20200908/1599567525.png!small)

 ** **ThinkPHP 5.1.x - GetShell****

首先明确ThinkPHP框架系列版本。

根据ThinkPHP版本，如是1.x版本，即可使用ThinkPHP 5.x远程代码执行漏洞1，无需登录，即可执行任意命令，获取服务器最高权限。

如需使用ThinkPHP 5.x远程代码执行漏洞2，则需要php文件中跳过报错提示，即
文件中有语句：“error_reporting(0);”，故该漏洞在5.1.x系列版本利用需要满足以上前提，利用较难。

##  ** **四、高可利用漏洞分析****

从高危漏洞列表中，针对ThinkPHP不需二次开发即可利用的高危漏洞进行深入分析。

###  ** **4.1、ThinkPHP 2.x/3.0远程代码执行漏洞****

 ** **4.1.1、漏洞概要****

> 漏洞名称：ThinkPHP 2.x/3.0远程代码执行
>
> 参考编号：无
>
> 威胁等级：高危
>
> 影响范围：ThinkPHP 2.x/3.0
>
> 漏洞类型：远程代码执行
>
> 利用难度：简单

 ** **4.1.2、漏洞描述****

ThinkPHP是为了简化企业级应用开发和敏捷WEB应用开发而诞生的开源MVC框架。Dispatcher.class.php中res参数中使用了preg_replace的/e危险参数，使得preg_replace第二个参数就会被当做php代码执行，导致存在一个代码执行漏洞，攻击者可以利用构造的恶意URL执行任意PHP代码。

 ** **4.1.3、漏洞分析****

漏洞存在在文件 /ThinkPHP/Lib/Think/Util/Dispatcher.class.php 中，ThinkPHP
2.x版本中使用preg_replace的/e模式匹配路由，我们都知道，preg_replace的/e模式，和php双引号都能导致代码执行的，即漏洞触发点在102行的解析url路径的preg_replace函数中。代码如下：

![](https://image.3001.net/images/20200909/1599616363.png!small)

该代码块首先检测路由规则，如果没有制定规则则按照默认规则进行URL调度，在preg_replace()函数中，正则表达式中使用了/e模式，将“替换字符串”作为PHP代码求值，并用其结果来替换所搜索的字符串。

正则表达式可以简化为“\w+/([\^\/])”，即搜索获取“/”前后的两个参数，$var[‘\1’]=”\2”;是对数组的操作，将之前搜索到的第一个值作为新数组的键，将第二个值作为新数组的值，我们发现可以构造搜索到的第二个值，即可执行任意PHP代码，在PHP中，我们可以使用${}里面可以执行函数，然后我们在thinkphp的url中的偶数位置使用${}格式的php代码，即可最终执行thinkphp任意代码执行漏洞，如下所示：

    
    
    index.php?s=a/b/c/${code}
    
    index.php?s=a/b/c/${code}/d/e/f
    
    index.php?s=a/b/c/d/e/${code}

由于ThinkPHP存在两种路由规则，如下所示：

  1. http://serverName/index.php/模块/控制器/操作/[参数名/参数值...]
  2. 如果不支持PATHINFO的服务器可以使用兼容模式访问如下：
  3. http://serverName/index.php?s=/模块/控制器/操作/[参数名/参数值...]

也可采用 index.php/a/b/c/${code}一下形式。

###  ** **4.2、ThinkPHP 5.x 远程代码执行漏洞1****

 ** **4.2.1、漏洞概要****

> 漏洞名称：ThinkPHP 5.0.x-5.1.x 远程代码执行漏洞
>
> 参考编号：无
>
> 威胁等级：严重
>
> 影响范围：ThinkPHP v5.0.x < 5.0.23,ThinkPHP v5.1.x < 5.0.31
>
> 漏洞类型：远程代码执行
>
> 利用难度：容易

 ** **4.2.2、漏洞描述****

2018年12月10日，ThinkPHPv5系列发布安全更新，修复了一处可导致远程代码执行的严重漏洞。此次漏洞由ThinkPHP
v5框架代码问题引起，其覆盖面广，且可直接远程执行任何代码和命令。电子商务行业、金融服务行业、互联网游戏行业等网站使用该ThinkPHP框架比较多，需要格外关注。由于ThinkPHP
v5框架对控制器名没有进行足够的安全检测，导致在没有开启强制路由的情况下，黑客构造特定的请求，可直接进行远程的代码执行，进而获得服务器权限。

 ** **4.2.3、漏洞分析****

本次ThinkPHP 5.0的安全更新主要是在library/think/APP.php文件中增加了对控制器名的限制，而ThinkPHP
5.1的安全更新主要是在library/think/route/dispatch/Module.php文件中增加了对控制器名的限制。

![](https://image.3001.net/images/20200909/1599616525.png!small)

![](https://image.3001.net/images/20200909/1599616555.png!small)

从以上补丁更新可知，该漏洞的根源在于框架对控制器名没有进行足够的检测，从而会在未开启强制路由的情况下被引入恶意外部参数，造成远程代码执行漏洞。

由ThinkPHP的架构可知，控制器（controller）是通过url中的路由进行外部传入的，即/index.php?s=/模块/控制器/操作/[参数名/参数值…]，控制器作为可控参数，经过library/think/APP.php文件进行处理，我们跟踪路由处理的逻辑，来完整看一下该漏洞的整体调用链：

首先在run()主函数中，url传入后需要经过路由检查，如下代码所示：

![](https://image.3001.net/images/20200909/1599618370.png!small)

跟进 self::routeCheck 函数

![](https://image.3001.net/images/20200909/1599620047.png!small)

在 620行中调用 $request->path()
函数，该函数位于thinkphp/library/think/Request.php文件中,在该函数中跟进到本文件的$this->pathinfo()函数，在该函数中，就进行url解析，获取路由中的各个部分内容。

![](https://image.3001.net/images/20200909/1599620072.png!small)

![](https://image.3001.net/images/20200909/1599620085.png!small)

其中var_pathinfo参数即为系统默认参数，默认值为s，通过GET方法将获取到的var_pathinfo的值，即s=/模块/控制器/操作/[参数名/参数值…]的内容送到routeCheck()函数中$path参数进行路由检查处理。

继续回到routeCheck()函数：

![](https://image.3001.net/images/20200909/1599620106.png!small)

在初始化路由检查配置之后，就进行Route::check，由以上代码看出，若路由寻不到对应操作，即返回$result=false，且开启了强制路由$must的情况下，就会抛出异常，并最终进入Route::parseUrl函数，进行$path解析，
** **以上就进入了我们的漏洞触发点**** ：

![](https://image.3001.net/images/20200909/1599620133.png!small)

首先，在该函数中进行url解析，然后，进入到parseUrlPath函数，根据/进行路由地址切割，通过数组返回：

![](https://image.3001.net/images/20200909/1599620156.png!small)

最终在parseUrl函数中，将返回的$path提取出路由，即module、controller、action，然后封装到$route后返回：

![](https://image.3001.net/images/20200909/1599620177.png!small)

回到thinkphp/library/think/App.php文件的run()函数：

![](https://image.3001.net/images/20200909/1599620206.png!small)

在完成RouteCheck后，进入到exec()函数中去：

![](https://image.3001.net/images/20200909/1599620229.png!small)

在该函数中，首先路由信息首先进入module()函数进行检验，该函数首先查看该路由中的模块信息是否存在且是否存在于禁止的模块类表中：

![](https://image.3001.net/images/20200909/1599620255.png!small)

模块存在的话，继续往下跟踪，分别将模块中的controller、actionName经过处理后赋值到$instance、$action，最终$instance、$action被赋值给了$call参数。

![](https://image.3001.net/images/20200909/1599620275.png!small)

![](https://image.3001.net/images/20200909/1599620290.png!small)

最终$call参数进入了self::invokeMethod()进行处理：

![](https://image.3001.net/images/20200909/1599620312.png!small)

在函数中，通过反射ReflectionMethod获取controller(method[0])和action(method[1])对象下的方法，然后通过$args
= self::bindParams($reflect, $vars);获取到传入参数。以上即为漏洞调用链。

 ** **我们根据Payload来进行最终攻击链的总结：****

siteserver/public/index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami

根据上面的分析，我们将路由解析为：

module：index

controller：think\app

action：invokefunction

通过上述的利用链，最终通过反射ReflectionMethod进入到Think/app文件中的invokefunction方法中：

![](https://image.3001.net/images/20200909/1599620343.png!small)

通过构造参数，最终即可执行任意代码。

###  ** **4.3、ThinkPHP 5.x 远程代码执行漏洞2****

 ** **4.3.1、漏洞概要****

> 漏洞名称：ThinkPHP 5.0.x-5.1.x远程代码执行漏洞
>
> 参考编号：无
>
> 威胁等级：严重
>
> 影响范围：ThinkPHP v5.0.x < 5.0.23,ThinkPHP v5.1.x < 5.0.31
>
> 漏洞类型：远程代码执行漏洞
>
> 利用难度：容易

 ** **4.3.2、漏洞描述****

2019年1月11日，某安全团队公布了一篇ThinkPHP 5.0.远程代码执行漏洞文档，公布了一个ThinkPHP
5.0.远程代码执行漏洞。文章中的该漏洞与2018年12月的ThinkPHP
5.0.*远程代码执行漏洞原理相似，攻击者可利用该漏洞在一定条件下获取目标服务器的最高权限。后经研究，在一定条件下，ThinkPHP
5.1.x版本也存在该漏洞，在满足条件的情况下，攻击者可利用该漏洞执行任意代码。

 ** **4.3.3、漏洞分析****

该漏洞的漏洞关键点存在于thinkphp/library/think/Request.php文件中：

![](https://image.3001.net/images/20200909/1599620448.png!small)

从代码中可知：

![](https://image.3001.net/images/20200909/1599620643.png!small)

method()函数主要用于请求方法的判断，var_method没有通过，为可控参数，通过外部传入，thinkphp支持配置“表单伪装变量”，var_method在在外部的可控参数表现为_method:

![](https://image.3001.net/images/20200909/1599620667.png!small)

由于var_method没有做任何过滤，我们可以通过控制_method参数的值来动态调用Request类中的任意方法，通过控制$_POST的值来向调用的方法传递参数。由上可知，漏洞存在于method()函数中，我们就需要寻找该函数的调用链，来构造POC。

第一个构造链在__construct()构造方法中，该方法如下：

![](https://image.3001.net/images/20200909/1599620694.png!small)

函数中对$option数组进行遍历，当$option的键名为该类属性时，则将该类同名的属性赋值为$options中该键的对应值。因此可以构造请求如下，来实现对Request类属性值的覆盖，例如覆盖filter属性。filter属性保存了用于全局过滤的函数。

再上一个漏洞分析过程中，我们跟踪到了路由检查self::routeCheck
函数，在过程中，会进入到thinkphp/library/think/Route.php文件中的check()函数，函数中调用了method()方法，并将函数执行结果转换为小写后保存在$method变量。在调用构造函数覆盖变量时，可以直接覆盖method，这样上面的$method
= strtolower($request->method()); 的$method最终的值就可以被控制了。

![](https://image.3001.net/images/20200909/1599620722.png!small)

在该函数中，调用了method()函数，在该函数中，就将进行变量覆盖：

![](https://image.3001.net/images/20200909/1599620743.png!small)

通过调用构造函数__construct(),最终将请求参数保存到input参数。

![](https://image.3001.net/images/20200909/1599620766.png!small)

在进行routecheck后，已完成了第一部分调用链，实现了变量覆盖，接下来就是要实现变量覆盖后的代码执行，具体调用链如下：

![](https://image.3001.net/images/20200909/1599620788.png!small)

返回到App.php文件中的run()函数，接着进入到exec()函数中，然后进入到module()函数中，最终进入到了invokeMethod()函数，

![](https://image.3001.net/images/20200909/1599620815.png!small)

从invokeMethod()函数中进入到bindParams()函数，然后进入到param()函数：

![](https://image.3001.net/images/20200909/1599620840.png!small)

然后最终调用到input()函数：

![](https://image.3001.net/images/20200909/1599620860.png!small)

最终我们根据array_walk_recursive()函数，进入到了filterValue()函数：

![](https://image.3001.net/images/20200909/1599620880.png!small)

最终，通过回调函数call_user_func执行了代码，整个调用链如上所示。

