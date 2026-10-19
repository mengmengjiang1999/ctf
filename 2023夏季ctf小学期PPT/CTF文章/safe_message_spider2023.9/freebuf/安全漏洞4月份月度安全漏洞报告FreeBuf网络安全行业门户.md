近日，梆梆安全专家整理发布4月安全漏洞报告，主要涉及以下产品/组件：Spring Expression、VMware 、VMware Workspace
ONE Access、VMware Workspace ONE Access等组件，建议相关用户做好资产自查与预防工作。

###  **01** **VMware Workspace ONE Access**

###  **存在模版注入漏洞**

 **0** **1** **漏洞描述**

VMware Workspace ONE Access（以前称为VMware Identity
Manager）旨在通过多因素身份验证、条件访问和单点登录，让您的员工更快地访问SaaS、Web和本机移动应用程序。

近日VMware官网发布了VMware Workspace ONE
Access存在多个漏洞，其中CVE-2022-22954是一个由服务器模板注入导致的远程命令执行漏洞，未经身份验证的攻击者可以利用此漏洞进行远程任意代码执行。

 **02** **影响范围**

  * 5.3. VMware Workspace ONE Access Appliance （版本号：20.10.0.0 ，20.10.0.1 ，21.08.0.0 ，21.08.0.1 ）

  * VMware Identity Manager Appliance （版本号：3.3.3 ， 3.3.4 ， 3.3.5 ，3.3.6）

  * VMware Realize Automation （版本号：7.6）

 **03** **漏洞分析**

从补丁分析入手。漏洞爆出后，官方给出了一个修复脚本`HW-154129-applyWorkaround.py`：

![](https://image.3001.net/images/20220509/1652081074_6278c1b297d772688a459.png!small)

既然是模板渲染漏洞，那么我们首先关注对模板的修改。脚本删除了`endusercatalog-ui-1.0-SNAPSHOT-classes.jar`中自带的模板`customError.ftl`：

![](https://image.3001.net/images/20220519/1652955177_628618296ba095765c249.png!small)

在`customError.ftl`模板中调用了freemarker引擎的`eval`函数来渲染`errObj`：

![](https://image.3001.net/images/20220519/1652955187_62861833c4a5925afe5d9.png!small)

查看freemarker官方文档：

可以判断`customError.ftl`在模板渲染过程中导致出现了漏洞，找到渲染`customError.ftl`模板的相关代码位于

`com.vmware.endusercatalog.ui.web.UiErrorController#handleGenericError`：

![](https://image.3001.net/images/20220519/1652955197_6286183d2352d35ced758.png!small)

搜索调用关系：

![](https://image.3001.net/images/20220519/1652955218_62861852e30b204785e57.png!small)![](https://image.3001.net/images/20220519/1652955226_6286185a89d8633ec70b3.png!small)

继续寻找`/ui/view/error`的调用，因为这是一个API接口，所以直接构造URL请求当然可以达到，但是这样无法从请求中提取

`javax.servlet.error.message`，导致目标渲染的内容不可控。通过搜索找到另一处调用位于`UiApplicationExceptionResolver#resolveException`：

![](https://image.3001.net/images/20220509/1652081127_6278c1e73f1a6c5d6f48b.png!small)

存在`javax.servlet.error.message`赋值过程。继续搜索`resolveException`调用：

![](https://image.3001.net/images/20220509/1652081141_6278c1f580e7ba606d294.png!small)

如下图所示，

`handleHttpMediaTypeNotAcceptableException`和`handleAnyGenericException`对应的都是全局异常的处理过程：

![](https://image.3001.net/images/20220509/1652081159_6278c2070c8ea0f44270b.png!small)

![](https://image.3001.net/images/20220509/1652081177_6278c219ec121ac6ddc45.png!small)

显然`handleAnyGenericException`适配的异常更加通用。`UiApplicationExceptionResolver`类限定了全局异常处理适用的类型范围为`UIController`、`HubUIController`和`WorkspaceOauth2CodeVerificationController`：

![](https://image.3001.net/images/20220509/1652081195_6278c22b1550ef9263372.png!small)

分析到这里之后，经过不断尝试，但是一直也没有实现对变量`errObj`的完全控制。在深入分析其中的一些基础性定义之后，最终找到一个完美实现内容可控的利用方式。获取的`errorObj`变量如下：

![](https://image.3001.net/images/20220519/1652955247_6286186f5546470aecc3b.png!small)

最终通过freemarker模板渲染实现RCE：

![](https://image.3001.net/images/20220509/1652081213_6278c23df380b4c617d3f.png!small)

 **04** **修复建议**

下面列出的此修补程序解决了上述漏洞。部署前指南：

  * 建议在应用补丁之前将不支持版本的实例升级到更新的支持版本。此过程不适用于不受支持的版本。请参阅 VMware Lifecycle Matrix 以获取受支持的产品版本列表；

  * 建议在应用修补程序之前进行设备和数据库服务器的快照或备份；

  * 如果在先前应用了解决方法的节点上执行此处提到的修补程序安装程序，它们将自动恢复解决方法。或者，您可以使用 KB 88098 中提到的恢复解决方法手动执行此操作；

  * vRA 7.6 有一个单独的修补程序可用，部署它的步骤在 KB 70911 中注明。

  

详情参考：

https://kb.vmware.com/s/article/88099

  

###  **0** **2** **Spring Expression**

###  **存在拒绝服务漏洞**

 **0** **1** **漏洞描述**

Spring Framework是美国威睿（Vmware）公司的一套开源的Java、JavaEE应用程序框架。该框架可帮助开发人员构建高质量的应用。

近期Vmware官网发布Spring Expression存在拒绝服务漏洞，漏洞编号为：CVE-2022-22950，是Spring Framework
5.3.16 之前的 5.3 版本以及更老的不受支持的版本存在安全漏洞，该漏洞源于特定的 SpEL 表达式可能会导致拒绝服务。

 **02** **影响范围**

  * 5.3.0 <= Spring Framework <= 5.3.16

  * 5.2.0 <= Spring Framework <= 5.2.19

  * 较旧的、不受支持的版本也会受到影响

 **03** **漏洞分析**

该漏洞可能通过特定的的SpEL表达式，这可能会导致拒绝服务情况。

 **04** **修复建议**

受影响版本的用户应应用以下缓解措施：5.3.x用户应该升级到5.3.17+，5.2.x的用户应升级到5.2.20+。

###  **0** **3** **VMware**

###  **存在信息泄漏漏洞**

 **0** **1** **漏洞描述**

VMware Workspace ONE Access（以前称为VMware Identity
Manager）旨在通过多因素身份验证、条件访问和单点登录，让您的员工更快地访问SaaS、Web和本机移动应用程序。

近日VMware官网发布了VMware Workspace ONE
Access存在多个漏洞，其中CVE-2022-22961是一个信息泄露漏洞，攻击者利用该漏洞可以获取敏感信息。

 **02** **影响范围**

  * VMware Workspace ONE Access 21.08.0.1

  * VMware Workspace ONE Access 21.08.0.0

  * VMware Workspace ONE Access 20.10.0.1

  * VMware Workspace ONE Access 20.10.0.0

  * VMware Identity Manager 3.3.6

  * VMware Identity Manager 3.3.5

  * VMware Identity Manager 3.3.4

  * VMware Identity Manager 3.3.3

  * VMware Cloud Foundation (vIDM) 4.x

  * vRealize Suite Lifecycle Manager 8.x

 **03** **修复建议**

漏洞修复详情参考：

https://kb.vmware.com/s/article/88099

  

###  **0** **4** **VMware Workspace ONE Access**

###  **存在身份验证绕过漏洞**

 **0** **1** **漏洞描述**

VMware Workspace ONE Access（以前称为VMware Identity
Manager）旨在通过多因素身份验证、条件访问和单点登录，让您的员工更快地访问SaaS、Web和本机移动应用程序。

近日VMware官网发布了VMware Workspace ONE
Access存在多个漏洞，其中CVE-2022-22955和CVE-2022-22956是VMware Workspace ONE Access
存在OAuth2 ACS 身份验证绕过漏洞。未经身份验证的攻击者可以利用该漏洞绕过身份验证机制并对系统中存在的节点进行操作。

 **02** **影响范围**

  * VMware Workspace ONE Access 21.08.0.1

  * VMware Workspace ONE Access 21.08.0.0

  * VMware Workspace ONE Access 20.10.0.1

  * VMware Workspace ONE Access 20.10.0.0

  * VMware Identity Manager 3.3.6

  * VMware Identity Manager 3.3.5

  * VMware Identity Manager 3.3.4

  * VMware Identity Manager 3.3.3

  * VMware Cloud Foundation (vIDM) 7.6

 **03** **漏洞分析**

由于身份验证框架中暴露的端点，攻击者可能绕过身份验证机制并执行任何操作。

 **04** **修复建议**

修复建议参考：

https://kb.vmware.com/s/article/88099

