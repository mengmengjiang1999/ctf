![图片](https://image.3001.net/images/20230824/1692857354_64e6f40a1d715b22ca8e4.gif!small)

**0x01 概述**

Hutool 是一个 **Java工具库** ，提供了丰富的工具和方法，方便开发者在Java应用程序中进行各种常见任务的处理。它具有
**简单易用、功能丰富、性能优越** 等特点，被广泛用于Java开发中。

笔者通过对数百个真实项目引入组件的分析选出了该组件的常见漏洞进行分析。本次分析的是 **CVE-2022-22885** ，Hutool-http执行HttpRequest操作时的 **证书验证漏洞**

 **0x02 组件使用场景**

Hutool-http组件是基于HttpUrlConnection的Http客户端封装 。其中的HttpRequest类有发送Http请求的功能。

 **0x03 漏洞信息**

 **3.1 漏洞简介**

 **漏洞名称：** 证书验证漏洞

 **漏洞编号：** CVE-2022-22885

 **漏洞类型：** CWE-295 证书验证不正确

 **CVSS评分：** CVSS v3.1：9.8

 **漏洞危害等级：** 超危

 **3.2 漏洞概述**

该库的HttpRequest类默认的HostnameVerifier信任所有的hostname，并不对服务器证书进行校验。

 **3.3 漏洞利用条件**

使用Hutool默认的HostnameVerifier。

 **3.4 影响版本**

Hutool < 5.7.19

 **3.5 漏洞分析**

该漏洞是证书验证漏洞，该漏洞会导致服务器遭受中间人攻击从而造成信息泄露等问题。若泄露的信息涉及密钥等可供验证的内容，会导致密钥对应设备被入侵。

该漏洞产生的原因在于Hutool
HttpUtil的setInfo函数传入的hostNameVerfier默认的为TRUST_ANY_HOSTNAME_VERIFIER。![1692857379_64e6f423395489d729f47.png!small](https://image.3001.net/images/20230824/1692857379_64e6f423395489d729f47.png!small)

其恒返回true。

![1692857385_64e6f429b399c53389284.png!small](https://image.3001.net/images/20230824/1692857385_64e6f429b399c53389284.png!small)

HostnameVerifier是一种fallback机制，当要连接的host与服务端证书server
name不匹配进行调用。Hutool默认放行所有这类请求。故而服务器易遭受不安全站点的攻击。

 **3.6 漏洞复现**

 **1.使用未封装的Java函数请求不安全页面**

Java自带HttpsURLConnection访问hostname与证书不匹配时报错。

![1692857391_64e6f42f6f7baa4f04790.png!small](https://image.3001.net/images/20230824/1692857391_64e6f42f6f7baa4f04790.png!small)

 **2.使用Hutool的HttpRequest类访问不安全页面**

成功返回页面内容。

![1692857395_64e6f433f28d2750751a9.png!small](https://image.3001.net/images/20230824/1692857395_64e6f433f28d2750751a9.png!small)

 **3.7 漏洞修复**

 **使用自定义的HostnameVerifier**

使用自定义的HostnameVerifier对证书主体名称和hostname进行校验。

![1692857400_64e6f4386455e5be1f323.png!small](https://image.3001.net/images/20230824/1692857400_64e6f4386455e5be1f323.png!small)

修复后，如下图所示，在执行Https请求时，程序会自动校验hostname和从证书获取的主体名称。具体需要根据请求URL改变传入hostname.equals()，principalName.equals()。如此就不会遭受证书域名不匹配的不安全站点的攻击。

![1692857406_64e6f43e9b666df942e2b.png!small](https://image.3001.net/images/20230824/1692857406_64e6f43e9b666df942e2b.png!small)

该修复方案需要根据请求URL的hostname和证书信息配置verify代码。

