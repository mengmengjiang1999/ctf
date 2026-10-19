最近30天左右，出现了若干个Java的漏洞，其中的一个是Spring Cloud Fuction的0Day，攻击主要隐藏在HTTP的Header里。

这种情况，在没有修复漏洞之前，最直接的缓解方式，是针对攻击请求中的Header信息进行过滤拦截。

`req-header("spring.cloud.function.routing-expression",
"spring.cloud.function.definition") => waf-mark-evil(message: "Spring Cloud
Function", level: "super");`

如果软件的服务资产过多，等官方修复再重新部署，时间来不及。
这个时候，用HIDS查主机的Java进程信息，不一定会覆盖所有的资产检查。如果没有对过去资产中，软件组件的资源进行信息管理，快速定位所受影响的服务器主机也比较难。  
如果不能快速评估，有多少软件服务资产受到威胁，最快速的应急缓解方式，是直接针对攻击进行拦截，最快的方式，就是在网络7层，针对HTTP协议中的敏感字段，进行过滤。  
从POC和各方给出的拦截方案中，有两个要在Header上进行拦截的字段：

`spring.cloud.function.routing-expression `

`spring.cloud.function.definition`

在传统的WAF上，就是创建一条拦截规则， 或者在网关上创建一个动态插件进行拦截，这个上篇文章就介绍。  
如果，WAF使用的是OpenResty Edge的WAF功能，只需要写一条DSL规则就可以对Header含有特定字段的攻击请求进行拦截。

这种拦截场景，是比较常见的WAF使用场景，在已经出版的一本书中《墨守之道-Web服务安全架构与实践》一书中对这种场景，有比较细节的介绍，其中包括使用网关的方式拦截，使用OpenResty Edge WAF系统的DSL语言，
编写EdgeLang的DSL规则进行拦截的案例。

 **引用：**

> [Spring Cloud(SPEL) RCE
> 0day漏洞临时修复建议](https://mp.weixin.qq.com/s/TGoXW64jKIzvxVr2u0lmfQ)
>
> [《墨守之道-Web服务安全架构与实践》](http://product.dangdang.com/29247206.html)``

