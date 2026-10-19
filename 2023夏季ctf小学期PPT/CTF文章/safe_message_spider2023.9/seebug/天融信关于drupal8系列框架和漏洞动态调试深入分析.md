**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/_OAwkKMws9F-RP7lBwSmbw>**

### 前言

在drupal框架中，比较经典又离我们最近的莫过于18年的CVE-2018-7600这个漏洞了。但是通过本人阅读和学习过此漏洞分析文章的过程中，发现都是针对于此漏洞点的详细分析。相对于此框架运行流程不是很熟悉的人可能在阅读完后很难理解。

作为阿尔法实验室的一员，本人通过阅读框架相关文档与漏洞分析的相关文章和自己对框架源码的调试，对框架运行的流程有了进一步的了解。

在此把这些分享给大家，本文主要分为两大部分：

第一部分是对drupal框架流程的简介（这里主要针对8.x系列），让我们知道在symfony开源框架基础上的drupal框架是如何利用监听者模式支撑起整个繁杂的处理流程，并让我们对框架如何处理一个请求有基本的了解。

第二部分，结合框架对漏洞CVE-2018-7600的运行流程进行详细解读，在漏洞触发的起始点首先通过动态调试正常数据包来了解drupal框架对其的处理流程，借此利用正常包中的可控变量来构造POC包。让我们不仅能对开头和结果得以了解，更能让中间的过程透明化。得以触类旁通。

### 一、背景介绍

Drupal是使用PHP语言编写的开源内容管理框架（CMF），它由内容管理系统（CMS）和PHP开发框架（Framework）共同构成。连续多年荣获全球最佳CMS大奖，是基于PHP语言最著名的WEB应用程序。

Drupal架构由三大部分组成：内核、模块、主题。三者通过HOOK机制紧密的联系起来。其中，内核部分由世界上多位著名的WEB开发专家组成的团队负责开发和维护。

Drupal综合了强大并可自由配置的功能，能支持从个人博客（PersonalWeblog）到大型社区驱动（Community-Driven）的网站等各种不同应用的网站项目。Drupal最初是由DriesBuytaert所开发的一套社群讨论软件。之后，由于它的灵活的架构，方便的扩展等特性，使得世界上成千上万个程序员加入了Drupal的开发与应用中。今天，它已经发展成为一套强大的系统，很多大型机构都采用基于Drupal的框架建站，包括The
Onion，Ain’t ItCool
News，SpreadFirefox，Ourmedia，KernelTrap，NewsBusters等等。它特别常见于社区主导的网站。

### 二、准备工作

#### 2.1 源码下载

首先可以直接通过官网下载页面<https://www.drupal.org/download>
直接下载最新版本或者通过<https://www.drupal.org/project/drupal/releases/xxx>
xxx代表你想下载的版本号，来下载对应版本的源码文件。

你也可以用PHP包管理工具composer进行下载。

#### 2.2 drupal安装

安装环境：WIN7 32位  
集成环境：PHPSTUDY  
调试环境：PHPSTORM

安装中可能出现的问题和解决办法：

1.php版本问题：最好为PHP7.0以上  
2.datetime问题

![img](https://images.seebug.org/content/images/2019/02/25/1551063992000-fed6f8930a034ecadce67f4da6bc9125.png-w331s)

解决方法：

php.ini 中设置

![img](https://images.seebug.org/content/images/2019/02/25/1551063992000-b9ac6ed7138f510ac55457fdf0ee4080.png-w331s)

3.安装警告

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-6e24fe1af79b8f73dc79869029bdb924.png-w331s)

这两个问题（warning）可以不解决。

针对问题1解决方法：升级php版本为7.1及以上。

针对问题2解决办法：在php.ini中，找到[opcache]，在这个地下添加如下内容。

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-904efdd0a305e653af6c66a08cbbb024.png-w331s)

    
    
    zend_extension=”C:\xxx\xxx\php\php-7.0.12-nts\ext\php_opcache.dll”
    
    opcache.memory_consumption=128
    
    opcache.interned_strings_buffer=8
    
    opcache.max_accelerated_files=4000
    
    opcache.revalidate_freq=60
    
    opcache.fast_shutdown=1
    
    opcache.enable_cli=1

4.因为drupal处理有些请求过慢，有可能会导致超时出现异常，在Php.ini中max_execution_time选项设置大点即可。

### 三、框架浅析

#### 3.1目录结构

下面是drupal 8.5.7 源码解压后的目录:

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-eeef9367b7113d9b622ab75d74655244.png-w331s)

/core drupal的内核文件夹，详见后文说明

/modules 里存放 自定义或者下载的模块

/profiles 里存放 下载和安装的自定义配置文件

/sites 文件夹，在drupal 7 或者更早的版本中，主要存放站点使用的主题和模块活其他站点文件。

/themses 里存放 自定义或者下载的主题

/vendor 里存放 代码的依赖库

接下来我们来看核心文件夹core下的目录结构

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-dc63161b7bcaff9d412b659a401701b4.png-w331s)

/core/assets – drupal 所使用的各种扩展库，如jquery，ckeditor,backbone,normalizeCSS等

/core/config - drupal 中的核心配置文件

/core/includes – 模块化的底层功能函数，如模块化系统本身

/core/lib – drupal提供的原始核心类

/core/misc – 核心所需要的前端杂项文件，如JS,CSS,图片等。

/core/modules – 核心模块，大约80项左右

/core/profiles – 内置安装配置文件

/core/scripts – 开发人员使用的各种命里脚本

/tests – 测试相关用的文件

/core/themes – 内核主题

#### 3.2 框架运行逻辑

Drupal是建立在symfony开源框架之上的，在symfony的官网上可知sysmfony就是一个可复用的php组件集，可以将任何一个组件独立的运用到自己的应用程序中来，在symfony官网里每一个组件都有独立的文档，这些组件有些被drupal直接使用，有些根据drupal自己的特性进行了修改。

我们首先来看一下symfony的执行流程

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-60a78df5ee3a3229265ba7388616d280.png-w331s)

Drupal 与 symfony 在设计上也使用了相同的理念，它们都认为任何一个网站系统其实就是一个把请求转换为响应的系统。

在drupal的路由系统中，我们可以看到各个组件之间的关系：

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-1faa799825deb46aa0bbcd7ef30da8b5.png-w331s)

在此基础上，drupal对symfony的处理流程进行了细化，构成了现在这个庞大的drupal处理响应流程。

图片链接地址为<https://www.drupal.org/docs/8/api/render-api/the-drupal-8-render-pipeline> 如需要可自行下载高清版。

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-39a6d59d7c25ce5456eb6dbc0cf8c25e.png-w331s)

#### 3.3 从入口文件来看

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-1725fedfb8b370b2e4369ed5351f0d6f.png-w331s)

入口文件非常简洁，只有6行代码量，却贯穿了整个drupal，由于drupal的核心系统过于庞大，分析不可能面面俱到，我们将从入口文件一行行来看，分析下它的运行流程。首先是`$autoloader
= require_once ‘autoload.php’;`
表面上看单单的是包含了一个autoload.php的文件，实际上drupal会利用PHP自动加载机制创建一个自动加载器，并获取了一个自动加载的对象。下面从代码方面简略看下其流程：其根本是调用vendor/autoload.php
中的getLoader函数。

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-866108e4d63099a1cd321da1066c1633.png-w331s)

接着我们进入函数看看它做了什么：

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-a719ad3807c0ae380fda83df69fbbb5d.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-5f1d38be09023b8126b3ef9aec1e8e25.png-w331s)

ClassLoader对象就是利用里面定义的基本对应关系去查找函数和类定义文件。

函数最后返回实例化加载器，至此第一步完成，drupal以后就不需要手动的 include一大堆文件了，省去了大量工作。接着是 `$kernel = new
DrupalKernel(‘prod’, $autoloader);` drupal创建了一个新的drupal内核对象，为处理即将到来的请求对象做准备。

![img](https://images.seebug.org/content/images/2019/02/25/1551063993000-d3014020d13b116f4bb25d2fe551f971.png-w331s)

紧接着是入口文件中的`$request =
Request::createFromGlobals()`这一行代码。对于一个面向对象的系统来说，我们不应该直接使用`$_POST`,`$_GET`,`$_COOKIE`等这些全局变量。Drupal把它们全部封装进了`$request`对象。这样不仅简单方便，而且使用请求的对象可直接加入一些额外的功能和自定义的属性。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-a8b4e1b35921aacd92736d51f03572ba.png-w331s)

最终，会把相应的全局变量加到request对象中，并返回封装好的request对象。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-ec6d8f692c908edd0c58f1d4c0f035a4.png-w331s)

如果说上面的操作只是预备阶段，那么接下来`$response =
$kernel->handle($request);`这行代码将开始步入正题，由drupal内核对象kernel来处理request请求。

Drupal的处理核心是利用了设计模式里面的监听者模式。其中包括一个事件源，里面包含了不同的事件以及事件等级。另一部分就是需要执行事件的程序或者函数，我们叫它监听者。在请求处理的这个流程中，每到一个节点，会派发出相应的事件，监听者会根据获取的事件对象和等级来进行相应的操作。

其中系统核心事件还是继续沿用symfony框架中的事件，位于kernelevents.php中，其中包含八大核心：

  * Const REQUEST = ‘kernel.request’ 执行框架代码中的任何代码之前，请求分派的开始触发的。

  * Const EXCEPTION = ‘kernel.exception’ 出现未捕获的异常时触发的事件。

  * Const VIEW = ‘kernel.view’ 当控制器返回值不是response 实例时触发。此时控制器返回的是渲染数组，来进一步进行渲染工作。

  * Const CONTOLLER = ‘kernel.controller’ 解析request请求找到相对应的控制器时触发，并可以对此控制器进行修改。

  * Const CONTROLLER_ARGUMENTS = ‘kernel.controller_arguments’ 解析控制器的参数时触发，并可对参数进行更改。

  * Const RESPONSE = ‘kernel.response’ 创建响应回复请求时触发，并可修改或替换要回复的相应。

  * Const TERMINATE = ‘kernel.terminate’ 一旦发送响应，就会触发。这个事件会允许处理繁重的post-response任务。

  * Const FINISH_REQUEST = ‘kernel.finish_request’ 完成Request请求时触发，可在请求期间更改应用程序时重置应用程序的全局和环境状态。

除了这些核心的事件，drupal中的每个监听者也会派发它们自己的事件。这些文件的位置位于\core\lib\Drupal\Core\目录下相对应文件夹中。它们都是以events.php结尾，文件中定义了相应的静态事件变量。

我们接下来看下drupal 核心的请求流程：

开始请求request—》解析请求得到控制器并修正——》解析控制器参数—-》根据控制器调用其中的方法—–》观察控制器的返回情况：返回响应对象reponse或继续进行渲染——》发送响应。如果整个流程中途产生异常，会直接触发异常事件进行异常的分发。请求对象在整个流程中除了会对核心请求事件的响应，还会根据实际情况进入响应其他普通模块事件的分支，但是不管中途的过程如何崎岖坎坷，最终都会重新回归主流程返回响应对象response。

接下来从源代码中观察下上述具体行为：

从index.php中继续跟进便进入了drupalkernel.php文件，我们来看看做了那些操作。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-a1bc43cd2764bdba399bed9e1c44d83a.png-w331s)

接下来就是一系列的处理函数函数调用链，我们一直跟进handle函数即可，这样我们直接可跟进核心函数handleraw

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-2337cb9e2f85b97e6bd443bd32151f8c.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-4d79e630570ea23726d92aca7a45b06e.png-w331s)

这里我们继续跟进即将返回的filterResponse函数。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-455bffbc922b77696b81101288e6aafd.png-w331s)

这里的响应对象将一层一层的返回（需要注意的是不是所有的响应结果都会走这个流程），但是最终都会封装成respone响应对象，返回至index.php文件中的$response变量中。然后调用`$response->send()`发送封装好的响应对象。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-a46a846f5793fade48f0a1018add2a4e.png-w331s)

有时我们发送的请求操作的内容会过于繁琐，所以当上面的调用结束后，我们的drupal内核在关闭前会做最后的处理。流程进入Index.php文件的最后一行,调用`$kernel->terminate($request,$response)`，我们根据调用链跟进stackedhttpkernel.php文件。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-89497956dbbe32a1be7be98036a750e9.png-w331s)

至此，整个周期已经结束。

我们发现上面整个过程中出现最多的就是派发事件这个操作了，其实所有派发进行的流程是相同的，派发的具体过程在ContainerAwareEventDispatcher.php文件中，我们拿kernel.request事件来进行举例说明。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-d3beb51574cf232900940051ff9baf14.png-w331s)

系统中监听者总数有19个之多，每个监听者其中又会有与之相关的服务名，我们会根据传入的事件名称匹配相应的监听者，接着遍历挨个调用其中的服务名所对应的功能函数。我们这里是kernel.request事件，调用方式为回调调用。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-1aa8058ec89f9c3094a6235f75c25f59.png-w331s)

### 四、再看CVE-2018-7600

通过第三部分单纯的框架分析可能只对流程有一个模糊的概念，接下来我们结合漏洞实例，针对比较经典的drupal框架漏洞cve-2018-7600来仔细观察下此漏洞在框架中的详细运行流程。我们这里利用漏洞触发环境的版本为8.5.0，此版本漏洞触发更为直观，所以我们后面分析所用代码版本如不做说明皆为此版本。

#### 4.1 补丁对比

因为此漏洞在8.5.1版本中被修复，5.0 和5.1又只相差一个子版本，我们可以更清晰的在源码中对比出其中的差异。看官方是如何修复这个漏洞的。

在8.5.1版本的源码中，新增了一个RequestSanitizer.php文件，里面是对request请求部分进行过滤，在stripDangerousValues方法中过滤了以#开头且不再白名单里的所有键名的值。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-e502c2b1e50bf7a5703f9d04e318104b.png-w331s)

在prehandle方法中调用了上述文件新增的方法进行过滤，下图右边红色部分为8.5.1新增的过滤代码。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-949e1acab9acba7b158743f1fb78135f.png-w331s)

此处过滤代码的调用位置是在drupal内核处理请求之前。这样可以一劳永逸，彻底修复了这个漏洞。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-2d8db4b3fe1570298ead315147443d9a.png-w331s)

接着我们进入drupal官网查看官方文档发现了drupal render api对#开头有特殊处理，关键文档链接在下方

<https://www.drupal.org/docs/8/api/render-api/render-arrays>并根据checkpoint安全团队发布了一份关于此漏洞相关技术细节[报告](https://research.checkpoint.com/uncovering-drupalgeddon-2/)。

链接如下：<https://research.checkpoint.com/uncovering-drupalgeddon-2/>。我们发现漏洞触发的源头是8.5.0版本中注册用户功能中的头像上传功能。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-2dcca90f88d56e15dc518ad4f29821ba.png-w331s)

#### 4.2 数据包在框架中的运行流程

我们既然知道了漏洞的触发源头，那么首先随便上传一张图片，抓一个正常的初始包看看情况。

![img](https://images.seebug.org/content/images/2019/02/25/1551063994000-f71094b78893b15dcf6499def0a8b79f.png-w331s)

接着在入口文件index.php中，经过createfromglobals函数的包装，drupal把我们传入的参数全部封装进了request对象中。

![img](https://images.seebug.org/content/images/2019/02/25/1551063995000-1e2fe4a5bd6636126425e03313a79466.png-w331s)

##### 4.2.1 KernelEvents::REQUEST派发事件

由于上文中对框架流程做了介绍，下面就是drupal内核处理我们的request请求阶段了，我们这里直接把断点下在handleRaw上，并进入第一个KernelEvents::REQUEST派发事件，看看监听者们都对此次请求做了什么。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-68f09dd6dad3b422e49f7a1c92a06c32.png-w331s)

首先drupal尝试去处理Option请求，可惜我们这里是POST请求，所以不处理，直接放行。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-7b5de71af51643872485f3c271bddfe0.png-w331s)

接着会去处理URL路径上的斜杠问题，会把多个斜杠开头的路径转换成单个斜杠

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-9afd0b499e4a4b50f5c301a5c2948a30.png-w331s)

然后会根据请求验证身份，我们这里没有做登陆，是游客身份，所以这里也不做特殊处理。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-c53815feec29e57b971f1cfd29304c83.png-w331s)

接下来会清理含有`$ _GET ['destination']`和`$ _REQUEST ['destination']`目标参数，防止重定向攻击。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-af519d51a4995664f58ff1dc3ebab997.png-w331s)

紧接着会根据POST请求中的`_drupal_ajax`参数来判断此次请求是否为AJAX请求，并设置相关属性。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-a8f2d04cd98a5b4ed61ea0c6d92fdf01.png-w331s)

接下来就是根据请求中的URL部分来匹配相应的路由，这里drupal会先在路由缓存中查找相应的匹配项，如果没有则再进行全部的路由查表操作。（由于代码比较多，这里不做全部截取，只截取部分代码），处理函数在onKernelRequest
中，同时，我们也可以在user.routing.yml文件中找到相关信息。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-3819626176cde34661ebe40278aa82a1.png-w331s)

路由找到了，接下来就是去检查此路由是否可用

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-482ced20b17a2762f64dc3606434b129.png-w331s)

紧接着就是检查站点是否处于维护模式，如果是维护模式则退出账户，检查站点是否脱机，检查动态页面缓存，预先处理非路由设置，根据参数看是否禁用副本服务器。这些操作的相关函数，均截图在下方。

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-41398ad133f672d7a289e31e4903511d.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063997000-f7e18a81927f078ae9875b57e417ae55.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-124a38f3e982e4b001f50fb68c8efab7.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-642c9dcdd71ca291a34d7bb3a311090d.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-06da275cafe2ef19659315bb7d9b10ef.png-w331s)

至此，KernelEvents::REQUEST
的所有监听者的行为分析完毕，我们可以看到上面这些操作主要做的是一些额外的措施，我们可以忽略不看，但是从中我们也提炼出了一些有价值的信息，通过请求对象匹配到了相关的路由信息。

##### 4.2.2 KernelEvents::CONTROLLER与KernelEvents::CONTROLLER_ARGUMENTS事件

接下来在handleraw函数中，drupal通过刚刚匹配到的路由信息来找到真正的请求控制器和相应的参数。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-1336c0571638b9d33305157e965387ef.png-w331s)

我们先来看看`KernelEvents::CONTROLLER`的监听者们会做那些操作。

首先，为了以后不做冲突，在相应的管理器上设置了关键的KEY

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-66104d28593f9e4ac45b2a4717fda3c4.png-w331s)

紧接着为了确保后面处理数据时的完整性，这里利用闭包把回调处理控制器的函数存进$event对象中

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-f257b114a514288a65554723740227bd.png-w331s)

因为`KernelEvents::CONTROLLER_ARGUMENTS`并没有属于它自己的监听者，所以这里派发直接放行。

##### 4.2.3 调用控制器

在handleRaw中处理完了请求相关的事件派发，并从request中找到了相应的控制器后，就该根据控制器找到相应的处理函数了。下方`call_user_function`中的控制器已经被替换为上图中闭包回调函数了，这里的调用控制器相当于直接进入上图中的闭包函数中。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-da517cb714bd0f6138df20117bcefc5b.png-w331s)

在drupal中，控制器都会被加入渲染上下文，以保证每个控制器处理过程中如果有需要渲染的地方直接进行渲染操作。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-dbee45b7b1e7b41f738713133149d571.png-w331s)

根据控制器进入到了真正的调用方法，也就是getContenResult中，表单的构建正式开始。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-c1d14256044535515c2a74f57faa3c48.png-w331s)

##### 4.2.4 表单构建

在进入buildForm 函数后，我们首先会得到POST的信息并存入form_state。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-3c7c36178733027e1d0edbb8889164e2.png-w331s)

在buildForm函数的retrieveForm函数中，form表单开始初步组装，如果其中有元素需要渲染，drupal大部分会直接利用`\Drupal::service(‘renderer’)->renderPlain();`这个渲染服务对元素进行渲染操作，最终渲染函数的主要操作在doRender函数中。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-fb226f5f24f80e14bd199e6b4d0736dd.png-w331s)

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-5e276c6fe3643b9a21765fe6888a01e2.png-w331s)

根据rquest组装的form表单在组装完成之后，马上就要处理表单请求了，这里processForm这个函数进行了这个操作，在这个函数中，运用递归的操作来处理行为，我们是一个图片上传操作，在这里也会对此行为进行处理，处理完毕后会进行图片的移动。接着对每个元素和token进行检查校验，最后根据结果rebuild整个Form表单。

![img](https://images.seebug.org/content/images/2019/02/25/1551063998000-addace6d458925dfda99d138a65ec1fe.png-w331s)

如果想在processForm中跟踪对图片的处理流程，可直接对下方函数进行断点设置，并根据栈回溯来查找你关心的操作。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-d23013403b997fefaf370a7cdbcf37af.png-w331s)

在运行完processForm函数后这里给出rebuild后部分FORM表单截图

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-51df06283d0f7f17ea89127b37a1a244.png-w331s)

到这里整个表单的处理操作已经完成了。

##### 4.2.5 异常派发。

在上一步完成表单操作之后，不知不觉中已把request请求对象转换成了响应response对象。眼看就要逐层返回并进行send操作了，但是在接下来的流程中drupal发现这是一个ajax请求，这里主动把操作拦截了下来，并抛出AJAX异常来对此次请求做额外的处理。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-75fd44de24686eb04d495b3ecce2e54f.png-w331s)

捕获到异常之后再处理异常中进行对异常的派发操作。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-776f16c393a46d2dd022f124516577c5.png-w331s)

在这里的派发其实是一个遍历并匹配异常的过程，发生异常有很多种情况，匹配到正确的异常然后进行具体的处理。如果没有匹配到，放行即可。我们这里匹配到了AJAX的异常，如果还比较关心其他异常的处理流程，在kernel.exception数组中寻找即可。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-5dc1ecb6a556d59ad58e6fa954622ae4.png-w331s)

我们进一步跟进发现onException的buildResponse函数中，有对AJAX的具体处理方法。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-5ea4bc74c55b7ad12d9ee39ca0295d5c.png-w331s)

在uploadAjaxCallback函数中，我们从数据包的URL中获取element_parents参数的值，并以此为key从我们最终处理完成的FORM表单中获取出结果，接着对此结果进行渲染并呈现在HTML页面上。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-ec444931238c05e3423a339aceb11103.png-w331s)

根据我们POST包中URL得参数，我们这里取出了FORM表单中user_picture下widget数组中的第一项。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-31db9d729fcf6d6675004a9d42332a00.png-w331s)

最终在doRender中要被渲染的对象就是刚刚取出来的元素。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-4ac1ac22f394bc61823ffd4c9d6fb9bc.png-w331s)

渲染过后整个处理过程已即将步入尾声，开始构建response并逐层返回。

##### 4.2.6 kernel.response事件

既然到了response阶段，那么肯定就要开始触发response相应了，接下来我们来看看response 有哪些监听者

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-e4814f2c86bfe63182ffa4da17e44a0f.png-w331s)

在response的派发函数中，其根本是对response对象的添砖加瓦以及做一些相应的扩展操作。如
判断动态页面是否需要缓存，是否需要添加缓存上下文，处理占位符，在成功响应时设置额外标头等。上述所有的操作都会在listeners下的kernel.response数组中，这里不做详细展开介绍。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-46d7d8e028481334d8005e2e994e1db8.png-w331s)

##### 4.2.7 kernel.finish_request

当 request 和response 的操作都做完了之后，接下来会告诉drupal
内核所有已经完毕，会发送finish_request事件，这个事件的监听者只有一个：为了让URL生成器在正确的上下文中运行，我们需要把当前请求设置为父请求。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-cd0f05c9bedf1567dc03fcb77fad5fad.png-w331s)

##### 4.2.8 kernel.terminate事件

做完上述操作后，request请求从请求栈中弹出，并逐层返回至Index.php入口主页面进行reponse的发送。最后进行扫尾工作，触发kernel.terminate事件，判断相关换成是否需要写入文件。最终drupal内核关闭。整个流程结束。

#### 4.3 整个流程总结

通过上一个小节分解式的解析了整个流程，我们下面来简单概括下：

发送数据包–>根据URL匹配相关路由–>根据路由找到相应的控制器–>根据控制器得到处理方法（我们这里是表单相关操作）–>进行表单的构建与渲染–>处理表单请求–>处理完表单后判断是否为AJAX操作–>主动抛出异常利用AJAX回调来重新渲染URL中标注的FORM表单key–>完成相应构建响应对象–>发送相应–>扫尾结束。

### 五、漏洞POC构建

结合上面框架的分析与理解开始对POC进行构建。在checkpoint安全团队发布了一份关于此漏洞相关技术细节[报告](https://research.checkpoint.com/uncovering-drupalgeddon-2/)（上文有链接）中可知，漏洞触发点是在表单构建好之后，触发AJAX异常，从FROM表单提取出要渲染的对象，进行渲染时触发，也就是在最终的doRender函数中。我们在doRender中发现如下可利用点：

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-427780d45cadb653a496f38524afa2b3.png-w331s)

根据第四部分我们对一个正常上传包在框架中运行的流程的分析，我们可知想让我们自己构造的内容在doRender中成功触发漏洞，首先需要控制流程,让其进入AJAX回调部分。

在下方这个if判断中，我们可知需要同时满足三个条件，`$ajax_form_request`
，`$form_state->isProcessingInput()` 和`$request->request->get(‘form_id’) ==
$form_id`。`$ajax_form_request`的值从下图可知是由ajax_form这个变量控制，form_id 是表单的id。

![img](https://images.seebug.org/content/images/2019/02/25/1551063999000-782f53dcf6e1233bdf5c1043c6cdfa98.png-w331s)

接下来，利用url中的element_parents参数值来获取表单数组中的值。在第四部分4.2.5小节有所讲述，此处不再重复说明。

最后构造相应的变量利用doRender函数中的`call_user_func_array`来触发漏洞。

根据上述描述，我们利用mail参数构造了如下POC包

![img](https://images.seebug.org/content/images/2019/02/25/1551064000000-1844604dd4e3882ebd91780cd2e9c305.png-w331s)

除了上述mail参数可控外，在分析过程中同时发现form_build_id参数也可控，另一种POC如下。

![img](https://images.seebug.org/content/images/2019/02/25/1551064000000-f8583692bcfcf5be40fd25cd01fb8caf.png-w331s)

### 六、参考链接

<https://blog.csdn.net/u011474028/article/details/53021051>

<https://paper.seebug.org/567/>

<https://research.checkpoint.com/uncovering-drupalgeddon-2/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/823/>

