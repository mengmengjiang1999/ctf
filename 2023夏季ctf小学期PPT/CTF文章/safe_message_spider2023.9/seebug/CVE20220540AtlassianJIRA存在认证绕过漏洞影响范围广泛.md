**作者：且听安全  
原文链接：<https://mp.weixin.qq.com/s/3EWju-IdsTfK7COKOK-c-w>**

## 漏洞信息

JIRA 存在 Seraph 组件认证绕过漏洞，影响范围广泛：

![](https://images.seebug.org/content/images/2022/06/3d4220a8-56c5-4d5f-ad19-877493a8e69c.png-w331s)

根据官方描述，大批量的默认和第三方插件受到影响：

![](https://images.seebug.org/content/images/2022/06/fd636095-0e6d-4944-b8a8-d03e5b4a04fe.png-w331s)

## 关于Seraph Filter

对于认证绕过，猜测问题可能出现在 Filter 过滤上，JIRA 内部封装了数量较为庞大的 Filter 列表：

![](https://images.seebug.org/content/images/2022/06/5092ad2a-11a1-40da-b817-321495cfd21b.png-w331s)

由于漏洞出现在`Seraph`模块，挨个查看 Filter
类，发现`JiraSecurityFilter`引用了`com.atlassian.seraph`包：

![](https://images.seebug.org/content/images/2022/06/a9c70e8c-8334-44a3-8de2-45de5dfadf30.png-w331s)

在`doFilter`中调用`super.doFilter`，即`SecurityFilter.doFilter`：

![](https://images.seebug.org/content/images/2022/06/f6820724-57fc-4209-a8a6-209143b01f68.png-w331s)

`Security.doFilter`根据客户端请求用户权限进行检查，进一步判定是否需要认证，`needAuth`变量很容易引起注意：
![](https://images.seebug.org/content/images/2022/06/22c02ea0-374f-4f63-b838-08b8c56fa806.png-w331s)

通过动态调试可知有 3
种服务进行检查，即`JiraPathService`、`WebworkService`和`JiraSeraphSecurityService`：

![](https://images.seebug.org/content/images/2022/06/f1bdec71-be66-4d6d-9b27-db567376a86c.png-w331s)

`JiraPathService`用于处理`/secure/admin/`请求，需要管理员访问：

![](https://images.seebug.org/content/images/2022/06/376a8e60-c39a-41dc-9501-6f81ee9a8b3f.png-w331s)

`WebworkService`从`actions.xml`文件`webwork`中读取权限定义：

![](https://images.seebug.org/content/images/2022/06/ad3f1a8a-241f-4780-9301-d5280f69a96e.png-w331s)

其`getRequiredRoles`函数代码如下：

![](https://images.seebug.org/content/images/2022/06/cf97c92a-03c5-4a69-a2f8-718a9daa02e3.png-w331s)

最后是`JiraSeraphSecurityService`，从插件`Atlassian-plugin.xml`文件中读取`webwork`接口权限定义：

![](https://images.seebug.org/content/images/2022/06/afcd2c15-4943-4fec-9cb8-56be79321177.png-w331s)

动态调试可知经过多次`getRequiredRoles`函数执行，最后调用了`WebworkPluginSecurityServiceHelper.getRequiredRoles`函数，而且这个函数代码与`WebworkService.getRequiredRoles`相同：

![](https://images.seebug.org/content/images/2022/06/3bbe2a0d-915b-4274-be95-297f75044d63.png-w331s)

该函数从`request`请求中提取 URI ，搜索最后一个`/`所在的位置，提取接口名称得到`targetURL`。如果 URL
输入为`/secure/PerformOAuth2Authorization.jspa`，那么`targetURL`为`PerformOAuth2Authorization.jspa`：

![](https://images.seebug.org/content/images/2022/06/f5340583-e54d-4ed8-9949-db5c43a654b1.png-w331s)

在`actionMapper`中搜索对应的`Action`名称，这里得到为`PerformOAuth2Authorization`：

![](https://images.seebug.org/content/images/2022/06/df388274-60c0-4cf5-b9a9-f741e1c761db.png-w331s)

根据`rolesMap`得到接口的权限为`admin`，接口需要管理员登录：

![](https://images.seebug.org/content/images/2022/06/558fce0d-32ff-4999-8cc2-a37839f53245.png-w331s)

介绍完功能代码，最后还要重点 Mark 一下，`getRequiredRoles`中获取 URL 的方式为`getRequestURI`：

![](https://images.seebug.org/content/images/2022/06/1a4949e4-a81f-482a-94ee-dd08bf8becf8.png-w331s)

### *.jspa的处理

查看`atlassian-jira/WEB-INF/web.xml`文件`Servlet`定义，`*.jspa`由`com.atlassian.jira.web.dispatcher.JiraWebworkActionDispatcher`处理：

![](https://images.seebug.org/content/images/2022/06/c5529b0b-b3b5-41a0-883f-d114f84bdd99.png-w331s)

`JiraWebworkActionDispatcher.service`函数从请求中获取`Action`名称：

![](https://images.seebug.org/content/images/2022/06/656fb37b-c224-4b26-8fcb-5293b52e36f0.png-w331s)

使用`/`和`.jspa`切割字符串获取`ActionName`，如果 URL
输入`/secure/PerformOAuth2Authorization.jspa`，那么 Action
为`PerformOAuth2Authorization`，注意到使用`getServletPath`函数：

![](https://images.seebug.org/content/images/2022/06/f47f721a-12d2-490e-b182-d0267bdb9869.png-w331s)

在`executeAction`函数中进行`Action`检查：

![](https://images.seebug.org/content/images/2022/06/18365a0e-abaf-4369-aa1d-eb6dbacc262c.png-w331s)

`Action`工厂列表如下：

![](https://images.seebug.org/content/images/2022/06/13eebca5-2481-4e3a-8bca-d63303c6e900.png-w331s)

再一次 Mark ，`GetActionName`中使用了`getServletPath`函数。

### Seraph Filter认证绕过

通过前边的分析，我们能够得知`Seraph`组件在 Filter 中使用`getRequestURI`提取 URL ，而 Servlet
中使用`getServletPath`，有经验的小伙伴应该很快意识到存在一个典型的认证绕过场景。

简单的来说就是如果 URL
中包含`;`，`getServletURI`结果会将分号保留，但`getServletPath`会自动将分号删除。以发送`/secure/PerformOAuth2Authorization.jspa;`为例，
`Seraph` 组件 Filter 中调用显然找不到`PerformOAuth2Authorization.jspa;`对应的 Action ，从而进入
Servlet 处理，相当于完成了 Filter 层面的认证绕过：

![](https://images.seebug.org/content/images/2022/06/f22226fe-fcc9-4b86-8133-92a678d52f03.png-w331s)

`getActionName`获取的结果示例如下：

![](https://images.seebug.org/content/images/2022/06/31424ca8-75e2-44cc-8579-52548b485548.png-w331s)

### 利用WebWork绕过插件认证

绕过`Seraph`组件`Filter`后，可以看到回复报文存在差异，但是还是需要认证：

![](https://images.seebug.org/content/images/2022/06/a310c33c-f9e1-4252-b279-259f2503581c.png-w331s)

调试后发现在执行`LookupAliasActionFactoryProxy`时同样读取了`PerformOAuth2Authorization`权限并进行检查：

![](https://images.seebug.org/content/images/2022/06/e0538119-50a1-4e53-b18e-47fd72d40ded.png-w331s)

同时其他`Factory`可能检查`Xsrf`、`checkWebSudoStatus`等要素：

![](https://images.seebug.org/content/images/2022/06/b1088cce-ac29-4697-9269-be4f1165229c.png-w331s)

直接查找官方文档，在编写插件时可以使用`webwork1`元素添加`roles-required`属性：

![](https://images.seebug.org/content/images/2022/06/e84223ba-60e2-4c14-90ed-d9da9ddbc7d6.png-w331s)

Atlassian 插件通常为 jar 或者 ocr 格式，为了验证绕过，根据官方发布的插件影响列表下载 Insight 8.9.10
版本，找到一个`webwork1`元素：

![](https://images.seebug.org/content/images/2022/06/25ed09c4-f86e-48d6-bfdc-22fcac5801a8.png-w331s)
成功绕过后台限制：

![](https://images.seebug.org/content/images/2022/06/3eaf344c-67d7-47cd-8825-e84e05918e4e.jpg-w331s)

### 受影响的其他页面

JIRA 默认组件中一些可能绕过的功能，（尚未调试分析每个接口功能）：
![](https://images.seebug.org/content/images/2022/06/82c75532-e934-469d-8bd6-64242adbcbe0.png-w331s)

![](https://images.seebug.org/content/images/2022/06/b1968817-2d92-49e2-93de-ab49f8bb1a06.png-w331s)

![](https://images.seebug.org/content/images/2022/06/96b8ca92-9a61-493d-bf45-3b72b6f46e64.png-w331s)

![](https://images.seebug.org/content/images/2022/06/ef0da8ab-6f66-4dbd-9f61-30d16e2a1a97.png-w331s)

还有很多其他 URL ，需要绕过 XSRF：

![](https://images.seebug.org/content/images/2022/06/ace3c216-6cd1-4ee0-84f5-5d9437e97705.png-w331s)

部分接口可通过请求直接返回错误栈：

![](https://images.seebug.org/content/images/2022/06/6d8b69ca-4019-4fdd-aefb-a60393de6a35.png-w331s)

### 修复方式

典型的插件修补过程：
![](https://images.seebug.org/content/images/2022/06/08e4b35e-6be8-4df1-b800-1d2bac44275e.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1896/>

