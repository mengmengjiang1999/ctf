# 【技术分享】API安全架构之抽丝剥茧

阅读量 **134090**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-26 11:14:02

 **x**

##### 译文声明

本文是翻译文章，文章来源：websec.io

原文地址：<https://websec.io/2017/05/01/Build_Secure-API-Part2.html>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[阿诺斯基](http://bobao.360.cn/member/contribute?uid=2826612711)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**传送门**

[**API架构之概念初探**](http://bobao.360.cn/learning/detail/4394.html)

**  
**

**前言**

这篇文章是构建安全API系列的第2部分。 [点击这里](https://websec.io/tagged/secureapi)查看更多的系列文章！

在本系列的[前一部分中](https://websec.io/2017/04/14/Build-Secure-API-Part1.html)，我花了一点时间，介绍了我们将要创建的安全API所需要实施的基本概念和过程。我还介绍了我们来创建API将要使用到的一些工具。如果你还没阅读本系列文章的第一部分，我一定会在你继续阅读本文前强烈推荐你去阅读一下第一部分。在本系列的第二部分中，我将从[
**Slim Framework**](http://slimframework.com/) 开始，深入挖掘这些工具。

我从框架作为开始的原因是因为它将成为我们构建一切的基础。我们的所有构建思路和功能将包含在整个框架的结构内。现在 **PHP生态系统**
中有很多框架可供选择。我选择使用Slim框架，是因为在我看来，它提供了最低限度的入门条件，并不需要太多的解释说明就可以快速上手，并且如果你需要一些功能的话，一切都可以放在一个文件中进行实现。

由于这是一个由多个部分组成的系列博文，我想确保在提供的代码方面能有更多的清晰度。所以，我[创建了一个](https://github.com/psecio/secure-api)[存储库](https://github.com/psecio/secure-api)可用于跟踪本系列文章每一部分发生的更改。存储库里包含了本系列每个部分的分支，每个部分都是基于了上一部分的功能。他们将显示本系列中每个教程的最终结果，以便你可以跟随每个教程，看看它是如何构建的，或者只是使用存储库来查看最终的结果。

另外我还会提到我们将要编写的代码 – 我将会使用几个PHP包，因此我们不会重新创建已经编写过和测试过的大量代码。所以，你需要熟悉[
**Composer**](https://getcomposer.org/)
依赖关系管理工具。我们将大量使用这些工具来提取软件包，并使得这些软件包易于使用到我们的应用程序中。

**  
**

**关于Web服务器？**

虽然你可以设置你所选择的Web服务器来处理进入Slim应用程序的请求，但我将在此保持一种简单的风格。PHP拥有自己的[内置Web服务器](http://php.net/manual/en/features.commandline.webserver.php)，非常适合这样的示例。它允许你定义并将index.php作为应用程序的“前端控制器”，同时在你选择的端口上提供服务。

有一件事需要注意 – 当我使用内置的PHP服务器作为我的示例中的Web服务时，它不应该被用来替代更强大的网络服务器，如 **Apache** 或
**Nginx** 。它非常适合测试和本地开发环境，但在性能质量部门肯定会希望你选择更可靠性能更好的Web服务器。如果你在生产环境中使用了内置的PHP
Web服务器，那么可能会给你带来麻烦。

让我们使用内置的服务器来获取一个简单的脚本并进行运行，以便你可以看到这个脚本的工作原理。你可以在系统的任何位置创建我们的测试文件，只要目录中有index.php这个文件就行。如果你要进行动手尝试，通常我建议你创建一个临时目录。在本教程中，我将在基于Unix的系统上执行命令，但在Windows上这个过程也是类似的。

创建文件只是一些比较简单的命令：

    
    
    mkdir www-tmp
    echo '<?php phpinfo(); ?>' test.php

然后，我们有一个PHP文件，test.php，其中包含了对[phpinfo](http://php.net/phpinfo)函数的调用，并且会显示我们的PHP实例的所有配置选项。

现在让我们启动内置的PHP服务器：

    
    
    > php -S test.php
    php -S localhost:8000 test.php
    PHP 7.0.12 Development Server started at Wed Apr 19 16:40:00 2017
    Listening on http://localhost:8000
    Document root is /path/to/script
    Press Ctrl-C to quit.

然后访问http://localhost:8000，你可以在浏览器中查看并可以看到正常的phpinfo输出。

需要注意的一点是，如果你的目录中有index.php文件，并且没有指定第二个参数，那么框架将使用index.php作为默认的执行脚本。

简单吧？现在我们知道如何使用内置的服务器了，我们可以继续安装Slim Framework然后用于构建我们的API。

**  
**

**安装Slim框架**

由于本系列文章的这一部分都是关于设置应用程序的初始部分，所以我们从基础开始：Slim框架。感谢[Composer](https://getcomposer.org/)，要将它使用到我们的应用程序，可以使用基本的require命令：

    
    
    > composer require slim/slim
     
    Using version ^3.8 for slim/slim
    ./composer.json has been updated
    Loading composer repositories with package information
    Updating dependencies (including require-dev)
    [...]
    Writing lock file
    Generating autoload files

如果你还不熟悉Composer软件包管理器，请参阅“
[入门](https://getcomposer.org/doc/00-intro.md)指南”了解更多信息。

执行上面的命令将安装基本的Slim框架及其相关组件，如nikic/fast-route请求路由组件和pimple/pimple依赖注入库。Slim框架大量使用了[Pimple](http://pimple.sensiolabs.org/)容器来处理应用程序中的依赖关系。大多数请求和响应处理围绕着这个容器。

如果Composer的安装过程一切顺利的话，它应该会生成自动加载的文件，并创建一个composer.lock文件，其中包含了有关于你安装的Slim版本的详细信息。如果有错误，你需要在继续操作之前对其进行调试
– 你必须先安装Slim及其依赖项，然后再尝试开发以下代码。

**  
**

**创建我们的第一个路由**

随着Slim的组件的全部安装完成，但由于Composer为我们设置了自动加载（PSR-0或PSR-4），我们可以直接在我们的脚本中使用它。Slim创建路由的过程非常简单，在我们的一个文件中定义路由
–
不需要创建任何目录或额外的文件。然而，这既具有有优点又有缺点。能够将东西全部保存在一个地方是很方便的做法，但是当整个项目开始变得复杂时，单个文件就使得维护更加困难。

不过，我们先从一些简单的代码开始，所以让我们创建第一个路由。首先创建一个index.php文件并将下面的代码放在其中：

    
    
    require_once 'vendor/autoload.php';
     
    $app = new SlimApp();
    $app->get('/', function() {
        echo 'It works!';
    });
    $app->run();

现在，如果我们启动PHP内置的服务器，并在浏览器中加载它，你应该可以看到在根目录的页面会打印出“It
works!”。在上面的代码中，我们已经在根路径/上定义了一个GET请求的路由。当我们开始添加其他路由类型时，事情会变得更加复杂，但是[Slim手册中](https://www.slimframework.com/docs/)有很多信息，所以我不会在这里重新进行整理说明。

现在，我们已经创建了一个基本的应用程序，我们可以继续改变一些关于它如何工作以满足我们的API需求。

**  
**

**使用配置**

Slim框架的一个主要功能是使用依赖注入容器定义配置值和你在应用程序中使用的其他资源。这还包括一些特殊的设置，Slim在内部重写了默认的错误处理程序。它也可以作为我们的控制器的存储库，使其更容易直接在我们的路由中使用它们。

我们先从这些自定义的设置开始，这样做有助于更好的构建我们的Slim
API。这些配置是针对Slim的处理程序的，但实现这些处理程序的思路是一样的，可以在任何框架内重新实现（有些甚至可以为你自动执行）。

**notFoundHandler**

当在定义的路由的列表中找不到被调用的URL时，Slim就会使用这个处理程序。有了这个错误处理程序，当客户端用户调用不正确时，我们可以设置一个友好的API响应。这里有一个例子：

    
    
    $app = new SlimApp();
    $container = $app->getContains();
     
    $container['notFoundHandler'] = function($container) {
        return function ($request, $response) use ($container) {
            return $container['response']
                ->withStatus(404)
                ->withHeader('Content-Type', 'application/json')
                ->write(json_encode(['error' => 'Resource not valid']));
        };
    };

如果你不习惯使用PSR-7结构，那么代码可能会有点复杂，但是当你将其拆下来后会发现它其实很简单。本质上，如果调用不存在的URL，我们将返回一个HTTP状态为404
的对象response和一个值为“资源无效” 的JSON消息error：

    
    
    {
        error: "Resource not valid"
    }

然后Slim在端点未定义时内部使用此处理程序 – 你无需做其他任何工作。

**notAllowedHandler**

Slim使用的另一个特殊设置就是notAllowedHandler。当不允许调用端点的方法时，框架会使用此处理程序，比如使用GET请求去调用一个POST端点：

    
    
    $container['notAllowedHandler'] = function($container) {
        return function ($request, $response) use ($container) {
            return $container['response']
                ->withStatus(401)
                ->withHeader('Content-Type', 'application/json')
                ->write(json_encode(['error' => 'Method not allowed']));
        };
    };

它与上面的notFoundHandler非常相似，只是在响应中有不同的内容：401和“不允许的方法”的错误消息。

**errorHandler**

我想在这里需要提到的最后一个特殊的选项就是使用errorHandler。在我选择的应用程序结构中，我们将利用PHP的异常处理特性在出现错误时停止执行，并向用户报告错误。这样可以防止我们在我们的控制器内部直接输出JSON并在一些奇怪的地方做任何其他比较诡异的事情。如果发现错误，就应该立即返回，而不是继续往下执行。

该errorHandler比前面的例子更详细一点。示例代码如下：

    
    
    $container['errorHandler'] = function($container) {
        return function ($request, $response, $exception = null) use ($container) {
            $code = 500;
            $message = 'There was an error';
     
            if ($exception !== null) {
                $code = $exception->getCode();
                $message = $exception->getMessage();
            }
     
            // Use this for debugging purposes
            /*error_log($exception->getMessage().' in '.$exception->getFile().' - ('
                .$exception->getLine().', '.get_class($exception).')');*/
     
            return $container['response']
                ->withStatus($code)
                ->withHeader('Content-Type', 'application/json')
                ->write(json_encode([
                    'success' => false,
                    'error' => $message
                ]));
        };
    };

现在，这个处理程序应该看起来很熟悉了，具有相同的功能签名和返回相同的响应对象。但有一些差异，主要是处理例外的情况。你会注意到$exception在内部闭包中有一个新的参数。这是通过Slim的内部功能传递给了错误处理程序，因此我们可以评估抛出的异常。在我们的例子中，我们设置了一个默认值$code，如果未设置异常（并非所有错误都是异常）则为$message，然后如果设置了异常，则会更新这些值。在我们的设置中，我们将使用异常的“代码”值作为我们返回的HTTP状态代码。这让我们控制了控制器内部的response对象然后使用此代码返回该对象，该异常中提供的消息和一个值为false的success对象。在我们的API中使用这个success对象值的返回结构都是一致的，并且将与每个响应一起返回（保存错误响应）。在我们的控制器中，我们可以抛出异常，这样errorHandler就可以正确地处理它们了：

    
    
    $app = new SlimApp();
    $app->get('/', function() {
        throw new Exception("You shouldn't have done that!", 418);
    });
    $app->run();

这将导致如下的响应内容：

    
    
    {
        success: false,
        error: "You shouldn't have done that!"
    }

响应中的HTTP状态码将在路由中的异常throw中指定。最后，你还可以使用自定义的异常，通过在类中定义它们，并使自定义的异常更具可重用性（例如CouldNotSaveRecord或InvalidInput异常）。

**最后一件事**

我想在转到本系列的下一部分之前，做最后一次更新。在我们目前的设置中，根路径/响应了一些纯文本的“工作”。这不是很友好的API，现在我们的其他错误处理程序是支持API构建的，当然你也可以改变这一点。Slim的请求/响应处理可以使这种改变变得很容易。我们只是返回一个Response对象作为一个新的实例这与错误处理程序的输出类似：

    
    
    $app->get('/', function() {
        return $response->withHeader('Content-Type', 'application/json')
            ->write(json_encode(['message' => 'It works!']));
    });

现在，当我们访问到根路径的路由/时，响应将返回一个内容类型为application/json的JSON内容：

    
    
    {
        message: "It works!"
    }

**现在，安装完成…**

在本文中，我介绍了一些设置Slim框架的基础知识，创建一个应用程序并配置几个处理程序，以帮助后续的事情变得更简单。还有其他我们将来会遇到的配置选项，但这就是你开始的地方。

为了帮助你更轻松地跟踪本系列的文章和每次创建的代码，我将为GitHub存储库中的每个部分添加一个分支。分支中的代码将是每篇文章的最终结果，所以希望到本系列文章的最后，我们将有一个完整的API示例，你将来可以使用它作为构建安全API的指导。

存储库位于此处：[https](https://github.com/psecio/secure-api):[//github.com/psecio/secure-api](https://github.com/psecio/secure-api)。

所以，让我们继续构建这个项目，并尝试一些请求示例和我们在本文中提到的例子。

**  
**

**资源**

[Slim 框架](http://slimframework.com/)

[第一部分](https://websec.io/2017/04/14/Build-Secure-API-Part1.html)

本文翻译自websec.io [原文链接](https://websec.io/2017/05/01/Build_Secure-API-Part2.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **phIshing** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86925](/post/id/86925)

安全客 - 有思想的安全新媒体

本文转载自: [websec.io](https://websec.io/2017/05/01/Build_Secure-API-Part2.html)

如若转载,请注明出处： <https://websec.io/2017/05/01/Build_Secure-API-Part2.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) phIshing

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

