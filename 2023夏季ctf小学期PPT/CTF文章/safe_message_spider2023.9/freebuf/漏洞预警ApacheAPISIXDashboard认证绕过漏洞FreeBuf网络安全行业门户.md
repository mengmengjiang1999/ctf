近日，网络上出现 Apache APISIX Dashboard 身份验证绕过漏洞，攻击者可通过该漏洞绕过身份验证过程并通过某些 API
端点未经授权访问应用程序。

##  **项目介绍**

Apache APISIX 是一个动态、实时、高性能的开源 API
网关，提供负载均衡、动态上游、灰度发布、服务熔断、身份认证、可观测性等丰富的流量管理功能。Apache APISIX 可以帮忙企业快速、安全的处理 API
和微服务流量，包括网关、Kubernetes Ingress 和服务网格等。

Apache APISIX Dashboard设计的目的是让用户通过前端界面尽可能轻松地操作Apache APISIX。APISIX Dashboard
架构图如下：

![1640932434_61cea45251355e9794e47.png!small?1640932434778](https://image.3001.net/images/20211231/1640932434_61cea45251355e9794e47.png!small?1640932434778)

全球已有数百家企业使用 Apache APISIX
处理关键业务流量，涵盖金融、互联网、制造、零售、运营商等等，比如美国航空航天局（NASA）、欧盟的数字工厂、中国航信、中国移动、腾讯、华为、微博、网易、贝壳找房、360、泰康、奈雪的茶等。

##  **项目地址**

https://apisix.apache.org/

##  **漏洞概述**

在2.10.1版本之前的Apache APISIX Dashboard中，Manager
API使用了两个框架，并在框架‘gin’的基础上引入了框架‘droplet’，所有的API和认证中间件都是基于框架‘droplet’开发的，但有些API直接使用框架‘gin’的接口，从而绕过了认证。

CVE编号：CVE-2021-45232

漏洞危害等级：高危

##  **影响版本**

Apache APISIX Dashboard < 2.10.1

##  **漏洞复现**

![1640932557_61cea4cd332e03b2b4fb3.png!small?1640932557606](https://image.3001.net/images/20211231/1640932557_61cea4cd332e03b2b4fb3.png!small?1640932557606)

##  **漏洞分** **析**

对比apisix-dashboard
2.10.0版本和2.10.1版本，排除非核心文件的变化，发现官方通过修改route.go文件，全部接口都必须经过认证，修复了漏洞。

![1640932575_61cea4df706da0191565f.png!small?1640932575735](https://image.3001.net/images/20211231/1640932575_61cea4df706da0191565f.png!small?1640932575735)

在2.10.0版本中，authentication.go主要完成认证功能。所有以/apisix开头，排除/apisix/admin/tool/version、/apisix/admin/user/login两个接口，全部都会检查请求头中的Authorization字段进行认证。

![1640932591_61cea4ef057866af1c35f.png!small?1640932591223](https://image.3001.net/images/20211231/1640932591_61cea4ef057866af1c35f.png!small?1640932591223)

在2.11.0版本中，authentication.go文件作用相同，但全部采用了gin-gonic。这个改动并不是漏洞产生的主要原因。

![1640932604_61cea4fc1c6b765a8210a.png!small?1640932604601](https://image.3001.net/images/20211231/1640932604_61cea4fc1c6b765a8210a.png!small?1640932604601)

分析发现，2.10.0版本大部分接口都进行了认证

![1640932616_61cea5081054b71b60f89.png!small?1640932616482](https://image.3001.net/images/20211231/1640932616_61cea5081054b71b60f89.png!small?1640932616482)

漏洞产生的原因在于部分handler接口没有使用wgin.Wraps进行认证因此产生了未授权访问漏洞。

![1640932636_61cea51cb7e55fdbc6aa4.png!small?1640932636950](https://image.3001.net/images/20211231/1640932636_61cea51cb7e55fdbc6aa4.png!small?1640932636950)

由于该接口可以导入api six 配置文件，因此可以完全控制api
six，存在极大安全隐患。翻阅官方文档，route路由存在script参数，可以执行任意lua脚本，攻击通过导入恶意配置可以完全控制服务器权限。

![1640932651_61cea52b79d654b4c1224.png!small?1640932654732](https://image.3001.net/images/20211231/1640932651_61cea52b79d654b4c1224.png!small?1640932654732)

目前网上已经出现相关漏洞利用工具：

![1640932670_61cea53ee1352b7330323.png!small?1640932671396](https://image.3001.net/images/20211231/1640932670_61cea53ee1352b7330323.png!small?1640932671396)

##  **漏洞修复**

目前官方已经在2.10.1版本中修复此漏洞，请尽快升级。最新版下载地址：

https://github.com/apache/apisix-dashboard/releases/tag/v2.10.1

##  **参考链接**

https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-45232

https://apisix.apache.org/zh/docs/apisix/admin-api

