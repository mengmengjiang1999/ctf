**作者：Feynman@深信服千里目安全实验室  
原文链接：<https://mp.weixin.qq.com/s/OWi3G4ETrV-yBsnWgdU_Ew>**

## 一、组件介绍

### 1.1 基本信息

ThinkPHP是一个快速、兼容而且简单的轻量级国产PHP开发框架，诞生于2006年初，原名FCS，2007年元旦正式更名为ThinkPHP，遵循Apache
2开源协议发布，从Struts结构移植过来并做了改进和完善，同时也借鉴了国外很多优秀的框架和模式，使用面向对象的开发结构和MVC模式，融合了Struts的思想和TagLib（标签库）、RoR的ORM映射和ActiveRecord模式。

ThinkPHP可以支持windows/Unix/Linux等服务器环境，正式版需要PHP
5.0以上版本支持，支持MySql、PgSQL、Sqlite多种数据库以及PDO扩展，ThinkPHP框架本身没有什么特别模块要求，具体的应用系统运行环境要求视开发所涉及的模块决定。

### 1.2 版本介绍

ThinkPHP发展至今已有14年历史，其核心开发版本已有数十个之多。2009年10月，ThinkPHP
2.0版本完成了新的重构和飞跃，成就了这一划时代的版本，从此，ThinkPHP就基于此开始了长达十多年的演化与发展。ThinkPHP发展至今，核心版本主要有以下几个系列，即ThinkPHP
2系列、ThinkPHP 3系列、ThinkPHP 5系列、ThinkPHP 6系列，各个系列之间在代码实现及功能方面，有较大区别。其中ThinkPHP
2以及thinkPHP 3系列已经停止维护，ThinkPHP 5系列现使用最多，而ThinkPHP 3系列也积累了较多多的历史用户。版本细分如下图所示：
![](https://images.seebug.org/content/images/2020/10/952fbe1d-3739-4f3a-9706-04c8fda6774b.png-w331s)

### 1.3 使用量及使用分布

根据全网数据统计，使用ThinkPHP的网站多达15万余个，其中大部分集中在国内，约占使用量的75%以上。其中，浙江、北京、山东、广东四省市使用量最高，由此可见，ThinkPHP在国内被广泛应用。通过网络空间搜索引擎的数据统计和柱状图表，如下图所示。

![](https://images.seebug.org/content/images/2020/10/a2764432-1693-4fe1-8bed-15520ed0fb8e.png-w331s)
(数据来源：[Zoomeye](https://www.zoomeye.org/))

## 二、高危漏洞介绍

通过对ThinkPHP漏洞的收集和整理，过滤出其中的高危漏洞，可以得出如下列表。

漏洞名称 | 漏洞ID | 影响版本 | 漏洞披露日期  
---|---|---|---  
ThinkPHP 2.x/3.0 远程代码执行漏洞 |  | ThinkPHP 2.x,3.0 | 2012  
ThinkPHP 3.2.4 SQL注入漏洞 | CVE-2018-18546 | ThinkPHP <= 3.2.4 | 2018  
ThinkPHP 3.2.4 SQL注入漏洞 | CVE-2018-18529 | ThinkPHP <= 3.2.4 | 2018  
thinkphp 3.1.3 s parameter注入漏洞 | CVE-2018-10225 | ThinkPHP <= 3.1.3 | 2018  
ThinkPHP 3.x update方法 SQL注入漏洞 |  | ThinkPHP <3.2.4 | 2017  
ThinkPHP 3.x orderby方法 SQL注入漏洞 |  | ThinkPHP <3.2.4 | 2017  
ThinkPHP 3.x where SQL注入漏洞 |  | ThinkPHP <3.2.4 | 2018  
ThinkPHP 3.x exp SQL注入漏洞 |  | ThinkPHP <3.2.4 | 2018  
ThinkPHP 3.x bind SQL注入漏洞 |  | ThinkPHP <3.2.4 | 2018  
ThinkPHP SQL注入漏洞--paraData方法 |  | ThinkPHP 5.0.13-5.0.15 | 2018  
ThinkPHP SQL注入漏洞--paraArraryData方法 |  | ThinkPHP 5.1.6-5.1.7 | 2018  
ThinkPHP SQL注入漏洞--parseWhereItem方法 |  | ThinkPHP 5 | 2018  
ThinkPHP SQL注入漏洞--parseOrder方法 |  | ThinkPHP 5.1.16-5.1.22 | 2018  
ThinkPHP SQL注入漏洞--orderby方法 |  | ThinkPHP 5.0.0-5.0.21  
Thinkphp 5.1.3-5.1.25 | 2018  
ThinkPHP cacheFile变量文件包含漏洞 |  | ThinkPHP 5.0.0-5.0.18 | 2018  
ThinkPHP cache缓存函数远程代码执行漏洞 |  | ThinkPHP 5.0.0-5.0.10 | 2017  
**ThinkPHP 5远程代码执行漏洞** |  | ThinkPHP 5.0.7-5.0.22  
ThinkPHP 5.1.0-5.1.30 | 2018  
**ThinkPHP 5远程代码执行漏洞** |  | ThinkPHP 5.0.0-5.0.23  
ThinkPHP 5.1.0-5.1.30 | 2019  
ThinkPHP 6 任意文件操作漏洞 |  | ThinkPHP 6.0.0-6.0.1 | 2020  
ThinkPHP 6 反序列化漏洞 |  | ThinkPHP 6.0.0-6.0.1 | 2020  
  
中可以看出，ThinkPHP近年出现的高风险漏洞主要存在于框架中的函数，这些漏洞均需要在二次开发的过程中使用了这些风险函数方可利用，所以这些漏洞更应该被称为框架中的风险函数，且这些风险点大部分可导致SQL注入漏洞，所以，开发者在利用ThinkPHP进行Web开发的过程中，一定需要关注这些框架的历史风险点，尽量规避这些函数或者版本，则可保证web应用的安全性。

从上表数据来看，ThinkPHP 3系列版本的漏洞多是是2016/2017年被爆出，而ThinkPHP
5系列版本的漏洞基本为2017/2018年被爆出，从2020年开始，ThinkPHP 6系列的漏洞也开始被挖掘。

其中，2018年与2019年交替之际，ThinkPHP爆出了 **两枚重量级**
的远程代码执行漏洞，这两枚漏洞均不需要进行二次开发即可利用，攻击者可通过框架中已有逻辑，直接构造恶意流量，在服务器中执行任意代码，获取服务器的最高权限。时至今日，这两枚漏洞的利用在全网中仍非常活跃，且被誉为ThinkPHP框架中的“沙皇炸弹”。

## 三、漏洞利用链

### 3.1、暴露面梳理

根据ThinkPHP的历史高位漏洞，梳理出分版本的攻击风险点，开发人员可根据以下图标，来规避ThinkPHP的风险版本，如下ThinkPHP暴露面脑图。

![](https://images.seebug.org/content/images/2020/10/8b49686c-23ce-41ac-9787-462a00df5f8b.png-w331s)

### 3.2、利用链总结

基于暴露面脑图，我们可以得出几种可以直接利用的ThinkPHP框架漏洞利用链，不需要进行二次开发。

#### 3.2.1、ThinkPHP 2.x/3.0 GetShell

![](https://images.seebug.org/content/images/2020/10/e2252f53-8d8c-4bd4-b794-3316d80366e6.png-w331s)

**ThinkPHP低于3.0 - GetShell**

  * ThinkPHP 低版本可以使用以上漏洞执行任意系统命令，获取服务器权限。

#### 3.2.2、ThinkPHP 5.0 GetShell

![](https://images.seebug.org/content/images/2020/10/f5fad9f2-d7f0-445f-8234-33c2a2e60db2.png-w331s)

**ThinkPHP 5.0.x - GetShell**

  * 首先明确ThinkPHP框架系列版本。
  * 根据ThinkPHP版本，如是5.0.x版本，即可使用ThinkPHP 5.x远程代码执行漏洞，无需登录，即可执行任意命令，获取服务器最高权限。

#### 3.2.3、ThinkPHP 5.1 GetShell

![](https://images.seebug.org/content/images/2020/10/82318225-ff82-4cdc-bc15-599856b042bf.png-w331s)

  * **ThinkPHP 5.1.x - GetShell**
  * 首先明确ThinkPHP框架系列版本。
  * 根据ThinkPHP版本，如是5.1.x版本，即可使用ThinkPHP 5.x远程代码执行漏洞1，无需登录，即可执行任意命令，获取服务器最高权限。
  * 如需使用ThinkPHP 5.x远程代码执行漏洞2，则需要index.php文件中跳过报错提示，即 文件中有语句：“error_reporting(0);”，故该漏洞在5.1.x系列版本利用需要满足以上前提，利用较难。

## 四、高可利用漏洞分析

从高危漏洞列表中，针对ThinkPHP不需二次开发即可利用的高危漏洞进行深入分析。

### 4.1、ThinkPHP 2.x/3.0远程代码执行漏洞

#### 4.1.1、漏洞概要

  * 漏洞名称：ThinkPHP 2.x/3.0远程代码执行
  * 参考编号：无
  * 威胁等级：高危
  * 影响范围：ThinkPHP 2.x/3.0
  * 漏洞类型：远程代码执行
  * 利用难度：简单

#### 4.1.2、漏洞描述

ThinkPHP是为了简化企业级应用开发和敏捷WEB应用开发而诞生的开源MVC框架。Dispatcher.class.php中res参数中使用了preg_replace的/e危险参数，使得preg_replace第二个参数就会被当做php代码执行，导致存在一个代码执行漏洞，攻击者可以利用构造的恶意URL执行任意PHP代码。

#### 4.1.3、漏洞分析

漏洞存在在文件 `/ThinkPHP/Lib/Think/Util/Dispatcher.class.php` 中，ThinkPHP
2.x版本中使用preg_replace的/e模式匹配路由，我们都知道，preg_replace的/e模式，和php双引号都能导致代码执行的，即漏洞触发点在102行的解析url路径的preg_replace函数中。代码如下：

![](https://images.seebug.org/content/images/2020/10/092302d8-3324-48e2-80ef-e66159988e91.png-w331s)

该代码块首先检测路由规则，如果没有制定规则则按照默认规则进行URL调度，在preg_replace()函数中，正则表达式中使用了/e模式，将“替换字符串”作为PHP代码求值，并用其结果来替换所搜索的字符串。

正则表达式可以简化为“\w+/([\^\/])”，即搜索获取“/”前后的两个参数，{}里面可以执行函数，然后我们在thinkphp的url中的偶数位置使用${}格式的php代码，即可最终执行thinkphp任意代码执行漏洞，如下所示：

index.php?s=a/b/c/${code}

index.php?s=a/b/c/${code}/d/e/f

index.php?s=a/b/c/d/e/${code}

由于ThinkPHP存在两种路由规则，如下所示：

    
    
    http://serverName/index.php/模块/控制器/操作/[参数名/参数值...]
    如果不支持PATHINFO的服务器可以使用兼容模式访问如下：
    http://serverName/index.php?s=/模块/控制器/操作/[参数名/参数值...]

也可采用 index.php/a/b/c/${code}一下形式。

### 4.2、ThinkPHP 5.x 远程代码执行漏洞1

#### 4.2.1、漏洞概要

  * 漏洞名称：ThinkPHP 5.0.x-5.1.x 远程代码执行漏洞
  * 参考编号：无
  * 威胁等级：严重
  * 影响范围：ThinkPHP v5.0.x < 5.0.23,ThinkPHP v5.1.x < 5.0.31
  * 漏洞类型：远程代码执行
  * 利用难度：容易

#### 4.2.2、漏洞描述

2018年12月10日，ThinkPHPv5系列发布安全更新，修复了一处可导致远程代码执行的严重漏洞。此次漏洞由ThinkPHP
v5框架代码问题引起，其覆盖面广，且可直接远程执行任何代码和命令。电子商务行业、金融服务行业、互联网游戏行业等网站使用该ThinkPHP框架比较多，需要格外关注。由于ThinkPHP
v5框架对控制器名没有进行足够的安全检测，导致在没有开启强制路由的情况下，黑客构造特定的请求，可直接进行远程的代码执行，进而获得服务器权限。

#### 4.2.3、漏洞分析

本次ThinkPHP 5.0的安全更新主要是在`library/think/APP.php`文件中增加了对控制器名的限制，而ThinkPHP
5.1的安全更新主要是在`library/think/route/dispatch/Module.php`文件中增加了对控制器名的限制。
![](https://images.seebug.org/content/images/2020/10/29215029-90bf-485e-a235-7bd3963802e9.png-w331s)

![](https://images.seebug.org/content/images/2020/10/e78e62fe-cc72-4a7a-930d-f944ca0d7334.png-w331s)

从以上补丁更新可知，该漏洞的根源在于框架对控制器名没有进行足够的检测，从而会在未开启强制路由的情况下被引入恶意外部参数，造成远程代码执行漏洞。

由ThinkPHP的架构可知，控制器（controller）是通过url中的路由进行外部传入的，即/index.php?s=/模块/控制器/操作/[参数名/参数值...]，控制器作为可控参数，经过`library/think/APP.php`文件进行处理，我们跟踪路由处理的逻辑，来完整看一下该漏洞的整体调用链：

首先在run()主函数中，url传入后需要经过路由检查，如下代码所示：

![](https://images.seebug.org/content/images/2020/10/0c9bd39b-ff01-4f09-9d5c-4cdae2672062.png-w331s)

跟进 `self::routeCheck` 函数

![](https://images.seebug.org/content/images/2020/10/fceb8462-20e5-49ad-b992-fac5b5e22d63.png-w331s)

在 620行中调用 `$request->path()`
函数，该函数位于`thinkphp/library/think/Request.php`文件中,在该函数中跟进到本文件的`$this->pathinfo()`函数，在该函数中，就进行url解析，获取路由中的各个部分内容。

![](https://images.seebug.org/content/images/2020/10/1b134174-b1b0-4287-a55d-56b50892b8f3.png-w331s)

![](https://images.seebug.org/content/images/2020/10/66fd99c8-240d-4e35-b91a-2bd57dfc4a87.png-w331s)

其中var_pathinfo参数即为系统默认参数，默认值为`s`，通过GET方法将获取到的var_pathinfo的值，即s=/模块/控制器/操作/[参数名/参数值...]的内容送到`routeCheck()`函数中$path参数进行路由检查处理。

继续回到`routeCheck()`函数：

![](https://images.seebug.org/content/images/2020/10/05e15288-a7e8-4e89-a329-839508dc0629.png-w331s)

在初始化路由检查配置之后，就进行`Route::check`，由以上代码看出，若路由寻不到对应操作，即返回`$result=false`，且开启了强制路由`$must`的情况下，就会抛出异常，并最终进入`Route::parseUrl`函数，进行`$path`解析，
**以上就进入了我们的漏洞触发点** ：

![](https://images.seebug.org/content/images/2020/10/4c3faea1-b88e-4a76-89b6-27354fe78b72.png-w331s)

首先，在该函数中进行url解析，然后，进入到parseUrlPath函数，根据`/`进行路由地址切割，通过数组返回：

![](https://images.seebug.org/content/images/2020/10/118ed54d-169f-4bc6-8043-141c74328757.png-w331s)
最终在parseUrl函数中，将返回的route后返回：

![](https://images.seebug.org/content/images/2020/10/0fa6cc35-4ecc-4f3c-b05c-dd3e981f8a77.png-w331s)

回到`thinkphp/library/think/App.php`文件的run()函数：

![](https://images.seebug.org/content/images/2020/10/101e3cf3-fbdb-4138-a44e-8efb4d696570.png-w331s)

在完成RouteCheck后，进入到exec()函数中去：

![](https://images.seebug.org/content/images/2020/10/1b4f1e5b-d0a1-42cd-97c9-a098d342c701.png-w331s)

在该函数中，首先路由信息首先进入module()函数进行检验，该函数首先查看该路由中的模块信息是否存在且是否存在于禁止的模块类表中：

![](https://images.seebug.org/content/images/2020/10/bfb51548-e67b-422c-adfe-5eadb17bd048.png-w331s)

模块存在的话，继续往下跟踪，分别将模块中的controller、actionName经过处理后赋值到action，最终action被赋值给了$call参数。

![](https://images.seebug.org/content/images/2020/10/cb7a51a0-d54c-43b9-ba50-480afbd63a2b.png-w331s)

![](https://images.seebug.org/content/images/2020/10/0392f424-7c7b-4e2c-8e90-7f5ce38c15cf.png-w331s)

最终$call参数进入了`self::invokeMethod()`进行处理：

![](https://images.seebug.org/content/images/2020/10/73b1b154-8cd8-4460-a64f-7895997c4156.png-w331s)

在函数中，通过反射ReflectionMethod获取controller(method[0])和action(method[1])对象下的方法，然后通过`$args
= self::bindParams($reflect, $vars);`获取到传入参数。以上即为漏洞调用链。

**我们根据Payload来进行最终攻击链的总结：**

`siteserver/public/index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami`

根据上面的分析，我们将路由解析为：

`module：index`

`controller：think\app`

`action：invokefunction`

通过上述的利用链，最终通过反射ReflectionMethod进入到`Think/app`文件中的invokefunction方法中：

![](https://images.seebug.org/content/images/2020/10/10d54661-5271-4ea5-896e-fc287d8b7111.png-w331s)

通过构造参数，最终即可执行任意代码。

### 4.3、ThinkPHP 5.x 远程代码执行漏洞2

#### 4.3.1、漏洞概要

  * 漏洞名称：ThinkPHP 5.0.x-5.1.x远程代码执行漏洞
  * 参考编号：无
  * 威胁等级：严重
  * 影响范围：ThinkPHP v5.0.x < 5.0.23,ThinkPHP v5.1.x < 5.0.31
  * 漏洞类型：远程代码执行漏洞
  * 利用难度：容易

#### 4.3.2、漏洞描述

2019年1月11日，某安全团队公布了一篇ThinkPHP 5.0. _远程代码执行漏洞文档，公布了一个ThinkPHP 5.0._
远程代码执行漏洞。文章中的该漏洞与2018年12月的ThinkPHP
5.0.*远程代码执行漏洞原理相似，攻击者可利用该漏洞在一定条件下获取目标服务器的最高权限。后经研究，在一定条件下，ThinkPHP
5.1.x版本也存在该漏洞，在满足条件的情况下，攻击者可利用该漏洞执行任意代码。

#### 4.3.3、漏洞分析

该漏洞的漏洞关键点存在于`thinkphp/library/think/Request.php`文件中：

![](https://images.seebug.org/content/images/2020/10/429f1ecd-b55b-421c-b36e-c79fd0ab6c24.png-w331s)

从代码中可知：

![](https://images.seebug.org/content/images/2020/10/8649ccef-370c-43b7-9c0b-08e9aa7ed9a3.png-w331s)

method()函数主要用于请求方法的判断，var_method没有通过，为可控参数，通过外部传入，thinkphp支持配置“表单伪装变量”，var_method在在外部的可控参数表现为_method:

![](https://images.seebug.org/content/images/2020/10/7f164e37-45a0-4e71-9e0f-a202381f26dc.png-w331s)

由于var_method没有做任何过滤，我们可以通过控制`_method`参数的值来动态调用Request类中的任意方法，通过控制`$_POST`的值来向调用的方法传递参数。由上可知，漏洞存在于method()函数中，我们就需要寻找该函数的调用链，来构造POC。

第一个构造链在__construct()构造方法中，该方法如下：

![](https://images.seebug.org/content/images/2020/10/2b91533a-2156-496f-aae7-778047837d1d.png-w331s)

函数中对option的键名为该类属性时，则将该类同名的属性赋值为$options中该键的对应值。因此可以构造请求如下，来实现对Request类属性值的覆盖，例如覆盖filter属性。filter属性保存了用于全局过滤的函数。

再上一个漏洞分析过程中，我们跟踪到了路由检查`self::routeCheck`
函数，在过程中，会进入到`thinkphp/library/think/Route.php`文件中的check()函数，函数中调用了method()方法，并将函数执行结果转换为小写后保存在method
= strtolower(method最终的值就可以被控制了。

![](https://images.seebug.org/content/images/2020/10/324d2ce7-330c-4c71-90af-fd57558363b5.png-w331s)

在该函数中，调用了method()函数，在该函数中，就将进行变量覆盖：

通过调用构造函数__construct(),最终将请求参数保存到input参数。

![](https://images.seebug.org/content/images/2020/10/92f8e165-c728-4a9f-8e5c-6783400cc306.png-w331s)

在进行routecheck后，已完成了第一部分调用链，实现了变量覆盖，接下来就是要实现变量覆盖后的代码执行，具体调用链如下：

![](https://images.seebug.org/content/images/2020/10/864f4881-a118-4266-b2f2-9c97f194b42f.png-w331s)

返回到App.php文件中的run()函数，接着进入到exec()函数中，然后进入到module()函数中，最终进入到了invokeMethod()函数，

![](https://images.seebug.org/content/images/2020/10/d2cd649f-623e-46c1-9bf6-1039ae6269b6.png-w331s)

从invokeMethod()函数中进入到bindParams()函数，然后进入到param()函数：

![](https://images.seebug.org/content/images/2020/10/e0368204-b958-486c-896d-f8eafe81c765.png-w331s)

然后最终调用到input()函数：

![](https://images.seebug.org/content/images/2020/10/91b8c10b-f0a6-4bd9-abd8-affe1fdb9d10.png-w331s)

最终我们根据array_walk_recursive()函数，进入到了filterValue()函数：

![](https://images.seebug.org/content/images/2020/10/5b9e4774-b887-4e5c-9f6e-6f6c3281e35b.png-w331s)

最终，通过回调函数call_user_func执行了代码，整个调用链如上所示。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1377/>

