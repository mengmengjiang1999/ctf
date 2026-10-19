**作者：启明星辰ADLab  
公众号：<https://mp.weixin.qq.com/s/UPu6cE20l24T6fkYOlSUJw>**

### **漏洞介绍**

2020年1月10日，ThinkPHP团队发布一个补丁更新，修复了一处由不安全的SessionId导致的任意文件操作漏洞。该漏洞允许攻击者在目标环境启用session的条件下创建任意文件以及删除任意文件，在特定情况下还可以getshell。

具体受影响版本为ThinkPHP6.0.0-6.0.1。

### **漏洞复现**

本地环境采用ThinkPHP 6.0.1+PHP7.1.20+Apache进行复现。在特定情况下执行测试验证程序即可写入一个webshell，如下图：

![](https://images.seebug.org/content/images/2020/01/f59eae5c-0fe4-4885-ac63-ae013a96be53.png-w331s)

![](https://images.seebug.org/content/images/2020/01/63687a0a-de0a-4bcf-82f8-89831c2ec45d.png-w331s)

### **漏洞分析**

根据官方github的commit:

![](https://images.seebug.org/content/images/2020/01/ca8751d0-1251-4b41-bb2b-812e6013a6c6.png-w331s)

<https://github.com/topthink/framework/commit/1bbe75019ce6c8e0101a6ef73706217e406439f2>

因而推测，可能是在存储session时导致的文件写入。然后，跟踪：`vendor/topthink/framework/src/think/session/Store.php:254`。

![](https://images.seebug.org/content/images/2020/01/5b78be80-74db-45b4-afa8-fc7085b0874f.png-w331s)

这里调用了一个write函数，跟进一下：`vendor/topthink/framework/src/think/session/driver/File.php:210`。

![](https://images.seebug.org/content/images/2020/01/a792ebec-c07c-4efb-9e7e-76e53df09270.png-w331s)

调用writeFile函数，跟入：

![](https://images.seebug.org/content/images/2020/01/a27bf742-7d6c-4e76-aa41-fdb180926128.png-w331s)

果然是写入文件的操作。

继续反向看一下文件名是否可控，该文件名来自于最开始的getId()得到的`$sessionId`的值。既然有getId，就会有setId，看一下函数内容：

![](https://images.seebug.org/content/images/2020/01/066b632d-145f-4bfe-ab4a-8b8497c7e76a.png-w331s)

当传入的参数`$id`满足32位的长度时，就将该值设为`$this->id`。看一下调用setId的地方：`vendor/topthink/framework/src/think/middleware/SessionInit.php:46`。

![](https://images.seebug.org/content/images/2020/01/03a933e9-f13a-4d9b-85a5-9b0e273db9eb.png-w331s)

这里的`$cookieName`的值是PHPSESSID。

![](https://images.seebug.org/content/images/2020/01/f57ac045-93f0-4765-b306-313edb555841.png-w331s)

而`$sessionId`是cookie中名为PHPSESSID的值，因此是攻击者可控的，从而导致写入的文件名可控。

写入的文件名可控，那么写入的内容是否可控呢？分析发现，写入的内容就是创建session使用的内容。但是session的创建是由实际的后端业务逻辑来决定的，而默认环境下并没有创建session。因此，默认环境下无法做到任意文件写入。

在对该漏洞的深入分析过程中，我们发现该漏洞还可以实现任意文件删除，且文件删除对后端业务逻辑依赖较低。

还是在`vendor/topthink/framework/src/think/session/Store.php:254`中：

![](https://images.seebug.org/content/images/2020/01/f7ae3de8-9db2-434a-814e-9d64913f939c.png-w331s)

通过分析验证，我们发现漏洞（如上图）还能导致任意文件删除。

### **总结**

在目标环境为Windows且开启session的情况下，容易遭受任意文件删除攻击。

在目标环境开启session且写入的session可控的情况下，容易遭受任意文件写入攻击。

建议相关用户及时升级到ThinkPHP6.0.2版本，以免遭受攻击。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1114/>

