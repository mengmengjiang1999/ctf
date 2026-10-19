***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **ThinkPHP是一个免费开源的，快速、简单的面向对象的轻量级PHP开发框架，是为了敏捷WEB应用开发和简化企
业应用开发而诞生的。由于其简单易用，国内用户众多。**

2019年1月11日ThinkPHP团队发布了版本更新，本次更新包含了一个可能GetShell的安全更新，具体内容为改进Request类的method方法。

## 漏洞描述

Thinphp团队在实现框架中的核心类Requests的method方法实现了表单请求类型伪装，默认为$_POST[‘_method’]变量，却没有对$_POST[‘_method’]属性进行严格校验，可以通过变量覆盖掉Requets类的属性并结合框架特性实现对任意函数的调用达到任意代码执行的效果。

## 漏洞危害

在未经授权的情况下远程攻击者构造特殊的请求可以在PHP上下文环境中执行任意系统命令，甚至完全控制网站，造成数据泄露，网站内容被修改。

## 影响范围

受影响版本：ThinkPHP 5.0.x

不受影响版本：ThinkPHP 5.0.24

## 漏洞分析

本次更新的关键commit如下：

![图片1.png](https://image.3001.net/images/20190112/15472235175706.png!small)  

文件路径为：library/think/Request.php ,在修复前的文件526行中，当存在$_POST[‘_method’]变量是将会执行
$this->{$this->method}($_POST)，当$_POST[‘_method’]为__construct时及等价于调用$this->_construct($_POST)_construct函数实现如下：

在该函数中，当传入的参数中的key为该Requests属性，将value赋值给该属性，由于key可控制，可以到达属性覆盖的效果。

![图片2.png](https://image.3001.net/images/20190112/15472235608511.png!small)

## 漏洞复现

通过git 可以快速搭建环境

> git clone <https://github.com/top-think/think>
>
> git checkout v5.0.23
>
> cd think
>
> git clone <https://github.com/top-think/framework> thinkphp
>
> cd thinkphp
>
> git checkout v5.0.23

通过覆盖filter属性即可达到调用任意函数的效果。

5.0.23且设置了app_debug=true复现截图如下：

![图片3.png](https://image.3001.net/images/20190112/15472237021997.png!small)  

Payload如下

> _method=__construct&filter[]=system&server[REQUEST_METHOD]=whoami

在早期5.0的版本过滤器的调用有差别payload也会不同

## 修复方案

1.升级到5.0.24版本

2.或通过修改以下代码来缓解漏洞：

编辑 library/think/Request.php 文件， 查找:

> $this->method = strtoupper($_POST[Config::get('var_method')]);
>
> $this->{$this->method}($_POST);

修改为如下

> $method = strtoupper($_POST[Config::get('var_method')]);
>
> if (in_array($method, ['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])) {
>
> $this->method = $method;
>
> $this->{$this->method}($_POST);
>
> } else {
>
> $this->method = 'POST';
>
> }
>
> unset($_POST[Config::get('var_method')]);

## 参考

<http://www.thinkphp.cn/topic/60992.html>

<https://github.com/top-think/framework/commit/4a4b5e64fa4c46f851b4004005bff5f3196de003>

