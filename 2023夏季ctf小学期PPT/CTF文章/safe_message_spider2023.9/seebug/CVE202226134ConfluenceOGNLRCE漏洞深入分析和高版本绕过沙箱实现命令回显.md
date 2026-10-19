**作者：且听安全  
原文链接：<https://mp.weixin.qq.com/s/nCMtSD7QH8ai6fpurJBXTg>**

## 漏洞信息

最近 Confluence 官方通报了一个严重漏洞 CVE-2022-26134 ：

![](https://images.seebug.org/content/images/2022/06/065bce52-07fd-46f5-8246-4e3aa3218de7.png-w331s)

从漏洞描述来看，这仍然是一个 OGNL 表达式注入漏洞。影响版本如下：

  * from 1.3.0 before 7.4.17
  * from 7.13.0 before 7.13.7
  * from 7.14.0 before 7.14.3
  * from 7.15.0 before 7.15.2
  * from 7.16.0 before 7.16.4
  * from 7.17.0 before 7.17.4,
  * from 7.18.0 before 7.18.1

补丁描述：

![](https://images.seebug.org/content/images/2022/06/0df03991-7abe-4d7d-b32e-2b5adb56936a.png-w331s)

主要是修改了 `xwork-1.0.3-atlassian-10.jar` 。下面将深入分析漏洞原理，并尝试绕过沙箱构造命令执行结果回显。

## 漏洞分析

新版本主要是修改了 `xwork-1.0.3-atlassian-10.jar` 。首先简单进行一下补丁对比：

![](https://images.seebug.org/content/images/2022/06/fc35df27-c2e8-4add-a2da-6bed4e3efef7.png-w331s)

改动的地方很多，但是最关键的地方位于 `ActionChainResult#execute` 函数，对提取 `finalNamespace` 和
`finalActionName` 的过程进行了更新。

Confluence 基于 Struts 架构进行开发。我们首先以登录请求为例，对 Confluence 请求处理的流程进行动态调试。访问
`/login.action` ，经过一系列 `Filter` 处理后，将进入Servlet 的分发器 `ServletDispatcher`
（本质上是其子类 `ConfluenceServletDispatcher` 对象）：

![](https://images.seebug.org/content/images/2022/06/f2eb0262-c174-4043-aefd-141650102c88.png-w331s)

![](https://images.seebug.org/content/images/2022/06/32dfff62-e182-46d6-a89e-a18268c07247.png-w331s)

![](https://images.seebug.org/content/images/2022/06/5d2cafb0-849e-453d-897a-dde18ea6467f.png-w331s)

分别通过函数 `getNameSpace` 、 `getActionName` 、 `getRequestMap` 、 `getSessionMap` 、
`getApplicationMap` 提取相应参数，对应关系如下：

  * `getNameSpace(request)` -> `namespace`
  * `getActionName(request)` -> `actionName`
  * `getRequestMap(request)` -> `requestMap`
  * `getParameterMap(request)` -> `parameterMap`
  * `getSessionMap(request)` -> `sessionMap`
  * `getApplicationMap()` -> `applicationMap`

然后调用 `serviceAction` 函数，进入子类 `ConfluenceServletDispatcher` 的 `serviceAction`
函数：

![](https://images.seebug.org/content/images/2022/06/d4a7fba1-09e0-4856-850b-7bf549997a77.png-w331s)

实例化 `DefaultActionProxy` 对象，调用其 `execute` 函数：

![](https://images.seebug.org/content/images/2022/06/192fc329-1600-4d47-88ae-d152b60bdeaa.png-w331s)

进入 `DefaultActionInvocation#invoke` ：

![](https://images.seebug.org/content/images/2022/06/8d46f115-2b77-43eb-b76d-fb2acd069b86.png-w331s)

这里开始调用 Struts Interceptor 拦截器对象对请求进行处理， `DefaultActionInvocation` 对象拦截器集合
`interceptors` 一共有 32 个：

![](https://images.seebug.org/content/images/2022/06/229e0864-c55f-4396-af44-2293f4b2c816.png-w331s)

函数 `invoke` 尝试通过 `next` 获取下一个拦截器对象，然后调用其 `intercept` 方法，大部分 `Interceptor` 对象的
`intercept` 函数格式如下所示：
![](https://images.seebug.org/content/images/2022/06/a39cafdc-dbbe-4b48-b99f-45a6c7a9bb23.png-w331s)

继续调用 `DefaultActionInvocation#invoke` ，从而形成迭代循环。但是在调试中我们发现也有特殊的一些
`Interceptor` ，比如 `ConfluenceAccessInterceptor` ：
![](https://images.seebug.org/content/images/2022/06/8bde45e6-3845-4dfd-8144-0f9c945b2f91.png-w331s)

当满足一定条件时并不会继续调用 `DefaultActionInvocation#invoke` ，而是返回字符串 `notpermitted`
，我们分析一下 `isAccessPermitted` 函数：
![](https://images.seebug.org/content/images/2022/06/ebfced5f-b051-48dc-a8cf-80b3fedf9553.png-w331s)

主要是通过请求的 `*.action` 和 `methdName` ，来判断当前用户 `currentUser`
是否有访问权限。也就是说，当访问一个无权访问的 `*.action` 时，`DefaultActionInvocation#invoke` 在迭代调用到
`ConfluenceAccessInterceptor#intercept` 后，将返回 `notpermitted` 并赋值给
`resultCode`，从而跳出迭代。我们替换测试请求为 `/index.action`：

![](https://images.seebug.org/content/images/2022/06/8c8e0044-a5d6-459d-aa15-347d16fd201f.png-w331s)

当处理到 `ConfluenceAccessInterceptor` 拦截器时，将不会继续迭代调用下一个拦截器，而是继续往下走，进入
`executeResult` 函数：

![](https://images.seebug.org/content/images/2022/06/6df629c4-bca6-41f8-8a53-dfd9574d54c8.png-w331s)

进入 `ActionChainResult#execute` ：

![](https://images.seebug.org/content/images/2022/06/45e40fd1-0384-44e4-bb28-c8bf781ce25c.png-w331s)

提取 `namespace` 参数，并调用 `translateVariables` 函数，进入：
![](https://images.seebug.org/content/images/2022/06/b038f161-5ab8-4a89-9cf6-c8b01cce4330.png-w331s)

典型的 OGNL 表达式解析过程，前面分析中可知， `namespace` 参数通过 `ServletDispatcher#getNameSpace`
函数获取，查看定义：

![](https://images.seebug.org/content/images/2022/06/86756480-b097-4db7-888d-63bc5ff556b5.png-w331s)
![](https://images.seebug.org/content/images/2022/06/cfeb94b9-50e2-4fe8-8470-9f59755b60c9.png-w331s)

可见 `namespace` 取值为请求 `servletPath` 最后一个 `/` 之前的部分。

根据上面正则表达式规则，要想触发 OGNL 解析，我们很容易构造出相应的 URL ：

![](https://images.seebug.org/content/images/2022/06/b4d25d23-1a56-47e3-b6fe-0803a13193c4.png-w331s)

成功触发 OGNL 表达式注入。

## 沙箱绕过与命令执行

网上现在已经公开的一些利用方式简单粗暴，只能针对 v7.14 及以下系列有效，因为从 v7.15 系列开始，Confluence 在 OGNL
表达式解析时加入了沙箱设置：
![](https://images.seebug.org/content/images/2022/06/78e6e6b3-8c96-4191-a416-75e604206f04.png-w331s)

进入 `isSafeExpression` 函数：

![](https://images.seebug.org/content/images/2022/06/519e4905-367a-4123-a727-00cba3855e26.png-w331s)

主要的黑名单如下： （1） `unsafePropertyNames`
![](https://images.seebug.org/content/images/2022/06/f2524ddf-7312-4af3-8e0e-c1a76cebf13a.png-w331s)

（2） `unsafePackageNames`
![](https://images.seebug.org/content/images/2022/06/76dbb3f8-26c8-43a4-87a3-f1b83940cc1a.png-w331s)
![](https://images.seebug.org/content/images/2022/06/04d5f073-013d-4bfa-8080-e0895693763e.png-w331s)
![](https://images.seebug.org/content/images/2022/06/0ca05ced-5fda-49e0-9b39-f086d061d33f.png-w331s)

（3） `unsafeMethodNames`

    
    
    0 = "getClass"
    1 = "getClassLoader"

白名单 `allowedClassNames` 如下：
![](https://images.seebug.org/content/images/2022/06/a8ff1891-3dbe-4f9c-b89f-ef6c98d7e245.png-w331s)

此外，对成员函数等也进行了检查（ `containsUnsafeExpression` 函数 ）：
![](https://images.seebug.org/content/images/2022/06/75813bd8-cec1-430b-bc47-0111525e31d7.png-w331s)

小伙伴看到这里，应该很容易想到多种绕过的方法，感兴趣的小伙伴可以进入漏洞空间站进行交流。其中一种实现命令执行结果回显的方式如下（适用全部受影响的版本）：

![](https://images.seebug.org/content/images/2022/06/c01baa81-97a5-4843-8978-c5c15fceeb30.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1912/>

