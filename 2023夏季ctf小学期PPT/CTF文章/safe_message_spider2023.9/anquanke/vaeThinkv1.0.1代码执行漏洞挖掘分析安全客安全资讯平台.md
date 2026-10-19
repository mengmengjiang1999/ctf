# vaeThink v1.0.1 代码执行漏洞挖掘分析

阅读量 **279460**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-16 16:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t017f860c1a965b3b1b.png)

## 0x01 引言

本文是对一个小众CMS（vaeThink
v1.0.1）进行分析、代码执行漏洞挖掘和审计过程的记录，该CMS基于ThinkPHP5开发。作为一名代码审计的入门菜鸟，也希望能够将实践和学习的过程记录和分享，以期能够与大家共同交流进步。

![](https://user-images.githubusercontent.com/18137763/57710705-04453480-76a0-11e9-87ef-bae03d338352.png)

## 0x02 分析

通过`git`将项目源码下载到本地，首先对项目源码目录结构进行了解：

    
    
    www  WEB部署目录（或者子目录）
    ├─app                   应用目录
    │  ├─common             公共模块目录
    │  │  ├─model           公共模型目录
    │  ├─admin              后台模块目录
    │  │  ├─controller      模块控制器目录
    │  │  ├─model           模块模型目录
    │  │  ├─validate        模块验证器目录
    │  ├─port               API接口模块目录
    │  │  ├─controller      模块控制器目录
    │  │  ├─model           模块模型目录
    │  │  ├─validate        模块验证器目录
    │  ├─common.php         公共函数文件
    │
    ├─data                  数据目录
    │  ├─conf               配置目录
    │  │  ├─module_name     模块配置目录
    │  │  ├─extra           额外配置目录
    │  │  ├─command.php        命令行工具配置文件
    │  │  ├─config.php         公共配置文件
    │  │  ├─route.php          路由配置文件
    │  │  ├─tags.php           应用行为扩展定义文件
    │  │  └─database.php       数据库配置文件
    │  ├─runtime            应用的运行时目录
    │  └─install.lock       用于系统鉴定是否完成安装
    │ 
    ├─public                WEB目录（对外访问目录）
    │  ├─plugin              插件目录
    │  ├─themes              模板文件目录
    │  └─admin_themes       admin模块模板文件目录
    │  ├─index.php          入口文件
    │  ├─router.php         快速测试文件
    │  └─.htaccess          用于apache的重写
    │
    ├─listenrain            系统核心引擎目录
    │  ├─thinkphp           ThinkPHP5框架文件目录
    │  ├─vae                vaeThink框架核心类库目录
    │
    ├─extend                扩展类库目录
    ├─vendor                第三方类库目录（Composer依赖库）
    ├─build.php             自动生成定义文件（参考）
    ├─composer.json         composer 定义文件
    ├─LICENSE.txt           授权说明文件
    ├─README.md             README 文件
    ├─think                 命令行入口文件
    

得到CMS的项目源码后，不着急进行源码的白盒审计，可以先将CMS部署和运行起来，认识和了解其功能点，同时进行黑盒测试。

该CMS的部署比较简单，只要有`LAMP`的环境，并且将网站根目录指向`public`目录即可，接着根据提示安装。安装完成之后，访问该CMS直接出现登录页面：

![](https://user-images.githubusercontent.com/18137763/57740394-3f6c5580-76ea-11e9-9e42-46285d17ffee.png)

**需要注意的是，一般在登录功能处可能存在SQL注入漏洞，但是本文着重挖掘代码执行漏洞的挖掘，因此其他类型会略过**
，我们继续通过安装时设置的管理员账号登入后台，进一步了解后台的其他功能点：

![](https://user-images.githubusercontent.com/18137763/57740505-cde0d700-76ea-11e9-9548-3dee953a7db9.png)

一般存在代码执行漏洞的地方，可能在如下这些功能模块：

    
    
    1、网站配置文件写入
    2、缓存cache文件写入
    3、日志文件写入
    4、文件上传
    5、代码执行函数参数可控
    

从这5点出发，我们继续对该CMS进行挖掘。

## 0x03 配置、日志和缓存文件

在`系统/配置`菜单中，存在与网站信息、邮件和短信配置相关的功能页面。在不进行源码审计的情况下，首先查看数据库中的数据表和字段，发现没有存储和这些配置相关的信息，可以猜测这些信息可能直接经过处理后存储在某个配置文件中，经过对项目目录的大致了解，应该是在`data/conf`下。

我们输入特定的测试数据进行提交，并且通过`grep`过滤包含特定数据的文件：

![](https://user-images.githubusercontent.com/18137763/57740799-2795d100-76ec-11e9-8954-bbb57d59ba3f.png)

![](https://user-images.githubusercontent.com/18137763/57741019-49dc1e80-76ed-11e9-80e3-ba3852c017c4.png)

欣喜地发现，输入的配置内容写入了`data/conf/extra/webconfig.php`中，并且同时注意到，输入的配置内容同样写入了日志文件`data/runtime/log/201905/1557823231-14.log`。

我们继续构造可控内容`'];phpinfo();//`，可以通过闭合前面的数组逃逸出来：

![](https://user-images.githubusercontent.com/18137763/57741092-a9d2c500-76ed-11e9-86c2-eeaf1b4d58a0.png)

但是测试发现，可控内容前的`return`会直接返回，注入的代码并没有被执行。另外，注意一下配置文件的路径可以发现，`data`目录不是一个可以直接访问到的网站路径，
**除非能够配合其他的路径穿越或者文件包含漏洞才有更进一步的可能** ，这里的日志文件也是同理。

注意到`data`目录下还存在`cache`和`temp`目录，其中存储了一些缓存文件

![](https://user-images.githubusercontent.com/18137763/57741251-9116df00-76ee-11e9-9bc8-e001ae6132a7.png)

除了和上面配置、日志文件存在同样的限制，这些缓存文件还通过`exit()`进行了安全处理：

![](https://user-images.githubusercontent.com/18137763/57741291-c7ecf500-76ee-11e9-818b-77cb1bda007b.png)

## 0x04 文件上传

几条路暂时被堵死了不要慌，继续观察CMS的其他功能点。在管理员的`修改个人信息`页面，发现存在一个头像上传功能，简单选择一个`t.php`上传，页面提示文件类型错误，不排除这只是一个前端校验的可能，我们通过抓包修改文件后缀继续进行上传：

![](https://user-images.githubusercontent.com/18137763/57741460-83ae2480-76ef-11e9-84e1-126bbd34d18e.png)

![](https://user-images.githubusercontent.com/18137763/57741486-a2142000-76ef-11e9-9fbe-40deec971c02.png)

![](https://user-images.githubusercontent.com/18137763/57741509-b7894a00-76ef-11e9-8fb2-884e08ce14a0.png)

测试后发现这里的上传点果然只对文件后缀进行了前端校验，直接了当上传`.php`后缀的文件：

![](https://user-images.githubusercontent.com/18137763/57741564-f3bcaa80-76ef-11e9-8c94-40e746770c1c.png)

## 0x05 代码执行函数参数可控

该CMS除了头像功能点直接暴力的文件上传之外（过于简单。。），还有没有可能存在其他角度的漏洞点呢？
**比如用户输入可以直接作为某些代码执行函数的参数，导致任意代码执行**
。怀着疑问我们继续对CMS开始进一步的挖掘，`PHPStorm`启动！`XDebug`配置！

在PHP中常见的代码执行函数有`eval、system`等等，通过`command+shift+f`进行全局搜索这些函数名关键词来找到切入点。经过一番排查，最终定位到了一个比较可疑的地方`listenrain/vae/lib/Auth.php第194行中的getAuthList函数`：

![](https://user-images.githubusercontent.com/18137763/57741965-a9d4c400-76f1-11e9-9e8d-f635a2b802d1.png)

我们继续从此处逆向回溯分析，查看该`污点`是否可被用户控制。

在`eval`函数中的参数存在一个变量`$command`：

![](https://user-images.githubusercontent.com/18137763/57742021-f02a2300-76f1-11e9-92eb-88fddeb81714.png)

该变量来自上一行的`$rule['condition']`，并且替换了`{(w*?)}`，但是没有进行其他的过滤操作：

`$command = preg_replace('/{(w*?)}/', '$user['\1']', $rule['condition']);`

`$rule`是从`186行 $rules =
Db::name($this->config['auth_rule'])->where($map)->field('condition,name')->select();`数据库中查询得到的数据的一部分。从作者的注释可以看到，读取的是`用户组所有权限规则`。

![](https://user-images.githubusercontent.com/18137763/57742599-54e67d00-76f4-11e9-825a-a2bf46bacc29.png)

我们通过分析和函数名可以大致对该函数作用有了解，是对通过用户id获得用户组权限，并且返回权限列表。

继续查看`getAuthList`的调用情况，是在`check`函数中：

![](https://user-images.githubusercontent.com/18137763/57742712-ddfdb400-76f4-11e9-8615-98bb5c92ee7f.png)

回溯`check`函数，发现调用在：

![](https://user-images.githubusercontent.com/18137763/57742767-071e4480-76f5-11e9-9e5f-fb9818e24bb9.png)

到此，基本可以确定在`管理员访问鉴权`功能模块中会触发此流程。接着下断点进行动态调试，便于对变量值的查看，我们选择菜单中的任何一个选项进行访问，执行流程会经过上述我们分析过的检查函数中：

![](https://user-images.githubusercontent.com/18137763/57743038-0df98700-76f6-11e9-9ad9-1e30981d1870.png)

![](https://user-images.githubusercontent.com/18137763/57743072-341f2700-76f6-11e9-98a3-f8329cefeffd.png)

![](https://user-images.githubusercontent.com/18137763/57743299-10101580-76f7-11e9-9368-f0feb6e6508a.png)

**分析后可以确定，数据库中用户拥有的权限对应的规则的`condition`字段将会作为`eval()`的参数被执行**

![](https://user-images.githubusercontent.com/18137763/57743483-ca078180-76f7-11e9-8edc-881bd18d09b4.png)

接着继续确定数据表中的`condition`字段是否为用户可控，分析后可以发现，在后台的`系统/节点
http://127.0.0.1/index.php/admin/rule/index.html`页面中存在对该数据表的操作功能，而`附加规则`对应数据表中的`condition`字段：

![](https://user-images.githubusercontent.com/18137763/57743578-34b8bd00-76f8-11e9-9c85-e9f7df9f6ebc.png)

尝试修改`附加规则`内容后，访问任意一个菜单中的页面，并动态调试观察:

![](https://user-images.githubusercontent.com/18137763/57743677-9a0cae00-76f8-11e9-8d1d-7da014d4bf4e.png)

![](https://user-images.githubusercontent.com/18137763/57743782-0b4c6100-76f9-11e9-973b-a0a4c0cdf533.png)

可以看到，可控内容没有经过过滤，成功触发该`污点`：

![](https://user-images.githubusercontent.com/18137763/57743856-654d2680-76f9-11e9-9ce7-7371b58c3c79.png)

![](https://user-images.githubusercontent.com/18137763/57743866-726a1580-76f9-11e9-9c86-9116a7925180.png)

## 0x06 结尾

本文针对`代码执行漏洞`，从配置文件、日志文件和缓存文件的写入，文件上传以及函数执行参数可控的角度对vaeThink
v1.0.1进行简单地挖掘和分析。全文内容比较简单，目的是记录和分享交流，请大佬轻喷。

最后，感谢阅读！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yunsle** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/178297](/post/id/178297)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [代码审计](/tag/代码审计)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t018d078a0ca4861591.jpg) yunsle

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

