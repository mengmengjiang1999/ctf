## 前言

 **PHP-Casbin 是一个用 PHP 语言打造的轻量级开源访问控制框架（<https://github.com/php-casbin/php-casbin> )，目前在 GitHub 开源。PHP -Casbin 采用了元模型的设计思想，支持多种经典的访问控制方案，如基于角色的访问控制
RBAC、基于属性的访问控制 ABAC 等。**

![](https://image.3001.net/images/20181101/1541052921_5bda99f9d734e.png!small)

![](https://image.3001.net/images/20181101/1541052940_5bda9a0cc340e.png!small)

## 概述

### PHP-Casbin 的主要特性包括：

> 支持自定义请求的格式，默认的请求格式为{subject, object, action}；
>
> 具有访问控制模型 model 和策略 policy 两个核心概念；
>
> 支持 RBAC 中的多层角色继承，不止主体可以有角色，资源也可以具有角色；
>
> 支持超级用户，如 root 或 Administrator，超级用户可以不受授权策略的约束访问任意资源；
>
> 支持多种内置的操作符，如 keyMatch，方便对路径式的资源进行管理，如 /foo/bar 可以映射到 /foo*；

PHP-Casbin 不做的事情：

> 身份认证 authentication （即验证用户的用户名、密码），PHP-Casbin 只负责访问控制。应该有其他专门的组件负责身份认证，然后由
> PHP-Casbin 进行访问控制，二者是相互配合的关系；
>
> 管理用户列表或角色列表。PHP -Casbin 认为由项目自身来管理用户、角色列表更为合适，PHP -Casbin
> 假设所有策略和请求中出现的用户、角色、资源都是合法有效的。

## 安装

    
    
    composer require casbin/casbin

### HelloWorld 例子

1\. 初始化一个 enforcer，传入两个参数：模型文件路径和策略文件路径；

    
    
    $e = new Enforcer(__DIR__ . '/examples/modelandpolicy/basic_model.conf', __DIR__ . "/examples/modelandpolicy/basic_policy.csv");

2\. 在你的代码需要进行访问控制的位置，加入如下钩子；

    
    
    $sub = "alice"; // the user that wants to access a resource.
    $obj = "data1"; // the resource that is going to be accessed.
    $act = "read"; // the operation that the user performs on the resource.
    
    if ($e->enforce($sub, $obj, $act) === true) {
        // permit alice to read data1x
    } else {
        // deny the request, show an error
    }

3\. 采用管理 API 进行权限的管理，如获取一个用户所有的角色；  

    
    
    roles = $e->getRoles('alice');

请参考[test](https://github.com/php-casbin/php-casbin/tree/master/tests)
目录获得更多的使用方法。

## 社区进展

PHP-Casbin 目前正在积极向社区进行推送，目前通过插件的方式已经支持与Laravel 等 Web 框架进行集成，将来会推广到更多 Web
框架以及社区。Casbin 已经有 Golang 版本、Java 版本、PHP 版本和 Node.js 版本。有跨语言需求的开发者可以只用 Casbin
这一套框架就实现多个不同语言的项目的权限管理任务。

> Casbin (Go)： <https://github.com/casbin/casbin>
>
> jCasbin (Java)： <https://github.com/casbin/jcasbin>
>
> PHP-Casbin (PHP)： <https://github.com/php-casbin/php-casbin>
>
> Node-Casbin (Node.js): <https://github.com/casbin/node-casbin>

## 协议

PHP-Casbin 采用 Apache 2.0 开源协议发布。

## 联系作者

有问题请提交 Issues: <https://github.com/php-casbin/php-casbin/issues>

***本文作者：hsluoyz，转载请注明来自FreeBuf.COM**

