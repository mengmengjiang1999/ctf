**原文链接：<https://mp.weixin.qq.com/s/EqEyEDKpzxS5BYA_t74p9A>  
作者：Phith0n**

> 事先声明：本次测试过程完全处于本地或授权环境，仅供学习与参考，不存在未授权测试过程，请读者勿使用该漏洞进行未授权测试，否则作者不承担任何责任

一次日常测试中，偶然遇到了一个Flarum搭建的论坛，并获得了其管理员账号。本来到这里已经可以算完成了任务，将漏洞报给具体负责的人就结束了，但是既然已经拿到了管理员账号，何不尝试一下RCE呢？

首先，我在管理员后台看到当前Flarum版本是1.3，PHP版本是7.4。Flarum以前没有遇到过，于是问下师傅们有没有历史漏洞，没准就不用费事了：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151436000-1vsrws.png-w331s)

结果显然是没有，否则也不会有这篇文章了??。

Flarum是一个PHP开源的论坛社区系统，以前有听说过，主要是国外用户较多，所以我也是出国以后才遇到。简单搜了下网上公开的漏洞，确实很少，而且以XSS和越权为主。

我对前后台进行了一系列观察，发现这个论坛CMS默认的功能较少，大部分扩展性由插件实现，但安装插件却只能通过命令行composer。浏览了一遍后台所有的功能，基本都是针对帖子和用户进行管理的：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151437000-2cylif.png-w331s)

黑盒没有进展，那么下载源码进行代码审计吧。

## 0x01 代码通读与逻辑梳理

漏洞挖掘前，我阅读了Flarum的代码和扩展开发文档，来进一步了解整个项目的架构与各个部分的使用方法。

接着，我在本地安装好Flarum，完成后有三个目录：

• public：Web根目录，里面只有index.php  
• storage：储存runtime文件的目录，里面有session、cache、logs等  
• vendor：库文件目录，使用composer安装

所有代码都在vendor中。它使用了很多Laravel和Laminas框架的components，但主体的MVC架构是自己实现的，并大量使用了依赖注入和事件机制（这一点和我之前分析的Cachet有点像，但Cachet是使用的标准Laravel结构，更简单一些），导致我熟悉目录文件结构和数据流转方式就花了很长时间。

现代PHP项目想要getshell，常见的方法有下面几个：

• 文件上传漏洞  
• 路由错误导致的函数执行漏洞，比如ThinkPHP 5的两个RCE  
• 模板注入漏洞，比如Cachet这个后台getshell  
• 反序列化漏洞

文件上传漏洞是传统漏洞了，但如果规范使用Web框架是不太会出现的，特别是现代的Laravel等框架；路由错误导致的函数执行漏洞多出现于上一代的MVC框架，这类框架会将用户输入解析成class
name和method
name再动态调用，而现在的框架路由多是定义一个完整的路由，Flarum也是这样；模板注入漏洞在后台功能中相对较多，有时候甚至直接就是PHP代码（Wordpress）；反序列化漏洞多出现在数据库、session、缓存之类的位置，如果能控制这些地方，可以着重找这相关的功能。

我按照这个思路逐一进行测试。

### 文件上传

首先是文件上传功能，Flarum仅有三处支持文件上传的逻辑，分别是网站Logo、Favicon和用户头像……是的，作为一个论坛社区，发帖默认不支持上传附件和图片，需要安装扩展来实现，而目标站点并没有这类扩展。

看了一下三处图片上传的代码，文件名无法控制，后缀写死成.png，文件内容也会使用GD库转换成png格式保存，可谓是水泄不通了。比如这是上传用户头像的部分代码：

    
    
    /**
     * @param User $user
     * @param Image $image
     */
    public function upload(User $user, Image $image)
    {
        if (extension_loaded('exif')) {
            $image->orientate();
        }
    
        $encodedImage = $image->fit(100, 100)->encode('png');
    
        $avatarPath = Str::random().'.png';
    
        $this->removeFileAfterSave($user);
        $user->changeAvatarPath($avatarPath);
    
        $this->uploadDir->put($avatarPath, $encodedImage);
    }

这条路堵死，甚至给我后面的漏洞利用也造成了很大困扰。

### 路由问题

Flarum没有动态执行用户传入的类和函数，而是通过router的方式分发路由，比如：

    
    
    return function (RouteCollection $map, RouteHandlerFactory $route) {
        // Get forum information
        $map->get(
            '/',
            'forum.show',
            $route->toController(Controller\ShowForumController::class)
        );
    
        //...
    }

所以我判断路由出问题的可能性较小，就没有细看。

### 模板注入漏洞

我翻了后台页面，并没有发现存在任何有关编辑模板的功能，所以这条路也作罢。

### 反序列化漏洞

经过分析，Flarum中存在反序列化的有两个地方，一是session，二是缓存，但这两个都储存在文件系统中，而我并不能控制文件内容。

终上所述，经过前面的分析，已经大致排除了一些常见的可能导致RCE漏洞的点。

## 0x02 利用CSS渲染读取任意文件

这是我第一次被卡住，但很快我看到了后台的一个功能： **自定义CSS样式** 。

![图片](https://images.seebug.org/content/images/2022/08/22/1661151437000-3jzojl.png-w331s)

很多CMS都有类似的功能，但Flarum有个有趣的地方是其支持Less语法。

Less是一个完全兼容CSS的语言，并在CSS的基础上提供了很多高级语法与功能，比如CSS中不支持的条件判断与循环，相当于是CSS语言的超集。前端开发者使用Less编写的程序，可以通过编译器转换成合法的CSS语法，提供给浏览器进行渲染。

那么就有趣了，这里支持Less语法，说明这其中存在代码编译的过程，这让我有两个思路：

• 编译过程本身是否存在漏洞，可以用于执行任意代码或命令  
• Less语言中是否有一些高危的函数，可以执行代码或命令

Flarum使用了less.php这个第三方库来编译Less，在其README页面可以看到下面这段警告：

> **Security**
>
> The LESS processor language is powerful and including features that can read
> or embed arbitrary files that the web server has access to, and features
> that may be computationally exensive if misused.  
>  In general you should treat LESS files as being in the same trust domain as
> other server-side executables, such as Node.js or PHP code. In particular,
> it is not recommended to allow people that use your web service to provide
> arbitrary LESS code for server-side processing.

看起来less.php自己也知道在渲染的过程中可能存在一些安全隐患。

我很快在Less语言的文档中找到了这样一个函数：data-uri

![图片](https://images.seebug.org/content/images/2022/08/22/1661151437000-4oiqpq.png-w331s)

在Less中，data-uri函数用于读取文件并转换成data协议输出在css中。看下less.php中相关的实现：

    
    
    public function datauri( $mimetypeNode, $filePathNode = null ) {
        $filePath = ( $filePathNode ? $filePathNode->value : null );
        // ...
    
        if ( file_exists( $filePath ) ) {
            $buf = @file_get_contents( $filePath );
        } else {
            $buf = false;
        }
        // ...
    }

一个可以控制完整路径的文件读取漏洞。

尝试在后台修改CSS，读取/etc/passwd：

    
    
    .test {
      content: data-uri('/etc/passwd');
    }

![图片](https://images.seebug.org/content/images/2022/08/22/1661151437000-5agbjq.png-w331s)

然后，在页面源码中找到CSS的地址，搜索`.test`这个样式：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151438000-6aynhr.png-w331s)

对其中的base64进行解码，可见读取`/etc/passwd`成功：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151439000-7cckli.png-w331s)

OK，我现在有了一个任意文件读取漏洞。

## 0x03 phar://反序列化尝试

通过对刚才代码的分析就可以发现，`file_exists`和`file_get_contents`的完整路径可以被控制，也就是说这里可以使用任意协议。幸运的是，目标系统是PHP
7.4，支持使用phar://来构造反序列化，相比起来，PHP 8.0以上就不再支持phar反序列化了。

关于phar://反序列化，可以参考Blackhat 2018的这个议题《It’s a PHP unserialization vulnerability
Jim, but not as we know it》。

phar是PHP中类似于Jar的包格式，而其中保存的metadata信息在读取的时候会被自动反序列化。这样，如果攻击者可以控制文件操作的完整路径，并能够在服务器上上传一个文件，将可以利用phar://协议指向这个文件进而执行反序列化操作。

所以接下来还需要找一个服务器上可控内容的文件（不需要控制文件名或后缀）。这个问题有点像我这篇文章里介绍的“裸文件包含”，但又不完全一样，phar反序列化对文件内容的要求相比起来会更加苛刻。

对于文件包含漏洞来讲，攻击者只需要控制任意一个文件中的一部分即可，对于文件格式、是否有脏字符等没有要求；而phar反序列化场景下，需要这个文件内容满足一定的格式才能成功被加载，进行反序列化。

phar文件可以是下面三种格式：

• zip  
• tar  
• phar

这三者都是archive格式，可以使用phpgcc这款工具来生成一个phar文件，并将反序列化利用链插入其中：

    
    
    php phpggc -o evil.phar Monolog/RCE6 system id

因为Flarum使用了monolog，我选择了Monolog/RCE6这条利用链，本地测试可以正常触发反序列化执行命令：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151439000-8oielm.png-w331s)

那么现在就需要想办法将这个phar文件上传到服务器上。

Flarum前面分析过，存在三处图片上传的功能，而phar是可以伪造成图片文件格式的，phpggc也贴心地提供了这个功能，`-pj`参数：

    
    
    php phpggc -pj example.jpg -o evil.jpg Monolog/RCE6 system whoami

使用该参数即可将phar文件和example.jpg图片制作成一个“图片马”，在上传时可以被识别成图片，但使用PHP解析时又可以识别成phar文件。

于是我尝试将payload使用上面的三个接口上传，但试了很多次才想起了之前那段代码：

    
    
    $encodedImage = $image->fit(100, 100)->encode('png');

寄了，这三个接口都使用GD库调整了图片大小，图片一处理就会把其中附带的phar内容给去掉。虽然之前有过通过GD库处理保留Webshell的图片马构造方法，但那个方法仅限于保留Webshell这样的代码片段，对于phar这种文件格式却无能为力。

还需要找到其他方法可以上传恶意phar文件。

## 0x04 恶意phar文件的构造与写入

这是第二次卡了我很久的点，一直感觉离RCE只差一层窗户纸，但很多时候就是被一层窗户纸给彻底堵死了所有路。

是否可以利用Session或PHP、Nginx的临时文件呢？这些方法要不就是对环境有要求，要不就是需要条件竞争，都不算理想的利用方式，我将其尝试的优先级降到很低，只有在彻底无望的情况下才会去考虑。

去冰箱里拿出vida气泡水喝一口，思考一下我这一步的目标是什么：
**我需要控制一个服务器上的文件，写入我需要的Payload，而且知道文件名，但对文件名和后缀没有要求。**

这时候我想到，前面进行代码审计的时候我阅读了Less生成CSS的过程，发现管理员在后台输入自定义CSS代码的时候将会把渲染完成后的CSS文件写入Web目录的assets/forum.css文件中：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151440000-9lfhay.png-w331s)

通过这个方法能够控制一个文件中的部分内容了，但好像还差点意思，因为实际思考下来，我遇到了两个难点：

• 用户自定义CSS会被插入到其他内置Less脚本中间，导致编译出的代码前后还会有不可控的其他字符（如上图）  
• 用户输入的内容会先校验是否满足Less或CSS的格式，完成后才会被编译成forum.css，且编译过程可能导致字符变化破坏phar文件格式结构

第一点，经过分析发现，Flarum生成的CSS是分成三部分，分别是内置CSS、用户自定义CSS、扩展插件中带的CSS：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151441000-10qcusj.png-w331s)

也就是说，虽然内置CSS我是完全无法控制的，但我可以通过将所有扩展都禁用来去除第三部分CSS。

禁用所有扩展以后，用户输入的CSS就输出在文件末尾了：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151442000-11awrss.png-w331s)

我研究用户自定义内容的输出位置，目的是了解是否可控文件头和文件尾。PHP在解析phar的时候支持三种文件格式，分别是zip、tar和phar。

**对于zip格式**
，我曾在知识星球里介绍过，它的文件头尾都可以有脏字符，通过对偏移量的修复就可以重新获得一个合法的zip文件。但是否遵守这个规则，仍然取决于zip解析器，经过测试，phar解析器如果发现文件头不是zip格式，即使后面偏移量修复完成，也将触发错误：

> internal corruption of phar (truncated manifest header)

当然，这也可能是我修复偏移方式有错误，可以后面再深入研究，暂时认为zip格式无法满足要求。

**对于tar格式** ，如果能控制文件头，即可构造合法的tar文件，即使文件尾有垃圾字符。

**对于phar格式** ，必须控制文件尾，但不需要控制文件头。PHP在解析时会在文件内查找`<?php __HALT_COMPILER();
?>`这个标签，这个标签前面的内容可以为任意值，但后面的内容必须是phar格式，并以该文件的sha1签名与字符串`GBMB`结尾。

可见，因为这里可以控制文件尾，我首先想到使用phar来构造一个恶意文件。但我很快发现了问题：用户输入的内容会先校验是否满足Less或CSS的格式。如果传入一个phar格式的文件，将会直接导致保存出错，无法正常写入文件。

## 0x05 @import的妙用

这个问题我想了很久也没有解决，就在即将放弃之时，我在阅读less.php代码的时候发现另一个有趣的方法，`@import`。

在CSS或Less中，`@import`用于导入外部CSS，类似于PHP中的include：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151442000-12hekfh.png-w331s)

在Less.php底层，`@import`时有如下判断逻辑：

• 如果发现包含的文件是less，则对其进行编译解析，并将结果输出在当前文件中  
• 如果发现包含的文件是css，则不对其进行处理，直接将`@import`这个语句输出在页面最前面

这就比较有趣了，第二种情况居然可以“控制”到文件头，虽然可控的内容只是一个`@import`语句。

于是我继续深入阅读这一部分代码，在解析`@import`语句的代码中，我看到了这样一段if语句：

    
    
    if ( $this->options['inline'] ) {
        // todo needs to reference css file not import
        //$contents = new Less_Tree_Anonymous($this->root, 0, array('filename'=>$this->importedFilename), true );
    
        Less_Parser::AddParsedFile( $full_path );
        $contents = new Less_Tree_Anonymous( file_get_contents( $full_path ), 0, array(), true );
    
        if ( $this->features ) {
            return new Less_Tree_Media( array( $contents ), $this->features->value );
        }
    
        return array( $contents );
    }

当`$this->options['inline']`为`true`时进入if语句，并使用`file_get_contents`读取此时的URL，直接作为结果返回。而众所周知的是，`file_get_contents`支持`data:`协议，所以我可以通过`data:`协议来控制读取的文件内容。

让`$this->options['inline']`为`true`的条件也很简单，文档中有相关说明：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151442000-13lmpli.png-w331s)

在`@import`语句后面指定`inline`选项即可。于是，我使用下面这段CSS进行测试：

    
    
    .test {
      width: 1337px;
    }
    
    @import (inline) 'data:,testtest';

![图片](https://images.seebug.org/content/images/2022/08/22/1661151443000-14srbtu.png-w331s)

哈，成功地将`testtest`这串字符串输出在了CSS文件的最开头。

那么，整个利用链就可以串起来了： **通过`@import
(inline)`和`data:`协议的方式可以向assets/forum.css文件的开头写入任意字符，再通过`data-uri('phar://...')`的方式包含这个文件，触发反序列化漏洞，最后执行任意命令。**

## 0x06 漏洞利用成功

因为可控文件头，我选择直接使用phpggc来生成tar格式包：

    
    
    php phpggc -p tar -b Monolog/RCE6 system "id>success.txt"

![图片](https://images.seebug.org/content/images/2022/08/22/1661151443000-15dufct.png-w331s)

然后构造成`@import`的Payload，在后台修改：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151443000-16fgooc.png-w331s)

此时访问forum.css即可发现文件头已经被控制：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151444000-17oluph.png-w331s)

再修改自定义CSS，使用phar协议包含这个文件（可以使用相对路径）：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151445000-18gfrly.png-w331s)

成功触发反序列化，执行命令`id`写入web目录，完成RCE：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151445000-19vdtln.png-w331s)

## 0x07 总结

这次漏洞挖掘开始于一次对Flarum后台的测试，通过阅读Flarum与less.php的代码，找到less.php的两个有趣的函数`data-uri`和`@import`，最后通过Phar反序列化执行任意命令。

整个测试过程克服了不少困难，也有一些运气，运气好的点在于，目标PHP版本是7.4，而这是最后一个支持使用phar进行序列化的PHP版本（PHP已安全??）。由于需要管理员权限，所以漏洞并无通用影响，但仅从有趣程度来看，是今年我挖过的最有趣的漏洞之一吧。

最后，打完收工，通知群友，有始有终：

![图片](https://images.seebug.org/content/images/2022/08/22/1661151445000-20zlaqb.png-w331s)

一看时间已4点，天都快亮了……

![图片](https://images.seebug.org/content/images/2022/08/22/1661151445000-21bcibg.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1946/>

