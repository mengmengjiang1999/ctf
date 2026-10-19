***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  0x00 事件背景

 **2019 年 1 月 11 日，360CERT 发现某安全社区出现关于 ThinkPHP5 RCE 漏洞的威胁情报，不久之后 ThinkPHP5
官方与 GitHub 发布更新。该更新修复了一处严重漏洞，该漏洞可导致远程命令代码执行。**

![](https://image.3001.net/images/20190111/15472059798232.jpg!small)

##  0x01 影响范围

ThinkPHP 5.0.x：5.0.x ~ 5.0.23

##  0x02 修复建议

官方在 GitHub 中进行了更新：版本更新

![](https://image.3001.net/images/20190111/15472060119575.jpg!small)

升级代码到最新版本 5.0.24

同时建议用户在线上环境中关闭 debug 模式

##  0x03 修复建议

该漏洞危害高，影响严重：

![](https://image.3001.net/images/20190111/15472060586093.jpg!small)

##  0x04 漏洞分析

漏洞主要出现在 ThinkPHPRequest 类的 method 方法中 (thinkphp/library/think/Request.php)

Request 类可以实现对 HTTP 请求的一些设置，其中成员方法 method 用来获取当前请求类型，其定义如下：

![](https://image.3001.net/images/20190111/15472061073364.jpg!small)

当传入的参数为 false 的时候，会取配置项 var_method，其默认值为_method

![](https://image.3001.net/images/20190111/15472061355270.jpg!small)

$this->{$this->method}($_POST); 通过 post 参数_method 可以实现对当前类的任意方法进行调用。

通过调用当前类的构造方法可以覆盖任意成员属性的值：

![](https://image.3001.net/images/20190111/15472061669662.jpg!small)

这里通过覆盖 filter 属性，filter 属性保存了用于全局过滤的函数。

但是在 thinkphp5.0.23 中，会对 filter 值重新赋值为空，导致无法利用。

![](https://image.3001.net/images/20190111/15472061927277.jpg!small)在
thinkphp/library/think/App.php 中开启 debug 的时候会调用 Request 类的 param 方法。

![](https://image.3001.net/images/20190111/15472062862802.jpg!small)在
thinkphp/library/think/Request.php param 方法中会调用到 method 方法, 并将参数设置为 true。

![](https://image.3001.net/images/20190111/15472063572661.jpg!small)当参数为 true
的时候，会调用 server 方法

![](https://image.3001.net/images/20190111/15472063846370.jpg!small)![](https://image.3001.net/images/20190111/15472063895741.jpg!small)会走到
input 方法，通过之前方法覆盖 server 成员属性值为 array(),input 方法代码如下：

![](https://image.3001.net/images/20190111/15472064081298.jpg!small)最终会调用
filterValue 形成任意代码执行：

![](https://image.3001.net/images/20190111/15472064354037.jpg!small)

##  0x05 时间线

> 2019-01-11 360CERT 发现漏洞威胁情报
>
> 2019-01-11 ThinkPHP 发布补丁更新
>
> 2019-01-11 360CERT 发布预警分析

##  0x06 参考链接

ThinkPHP5 github 更新

<https://github.com/top-think/framework/commit/4a4b5e64fa4c46f851b4004005bff5f3196de003>

***本文作者：360安全卫士，转载请注明来自FreeBuf.COM**

