## 一、前言

**Harbor是一个用于存储和分发Docker镜像的企业级Registry服务器，通过添加一些企业必需的功能特性，例如安全、标识和管理等，扩展了开源Docker
Distribution。**

作为一个企业级私有Registry服务器，Harbor提供了更好的性能和安全。提升用户使用Registry构建和运行环境传输镜像的效率。Harbor支持安装在多个Registry节点的镜像资源复制，镜像全部保存在私有Registry中，
确保数据和知识产权在公司内部网络中管控。另外，Harbor也提供了高级的安全特性，诸如用户管理，访问控制和活动审计等。

**斗象智能安全平台CRS/ARS产品已全面支持该漏洞的检测与验证，斗象智能安全平台用户可直接登陆[www.riskivy.com](http://www.riskivy.com)进行验证。**

## 二、漏洞简介

近日Harbor曝出一个垂直越权漏洞，因注册模块对参数校验不严格，可导致任意管理员注册。

## 三、漏洞危害

经斗象安全应急响应团队分析，攻击者可以通过注册管理员账号来接管Harbor镜像仓库，从而写入恶意镜像，最终可以感染使用此仓库的客户端。

## 四、影响范围

### 产品

Harbor

### 版本

1.7.0-1.8.2

### 版本

Harbor

## 五、漏洞复现

经斗象安全应急响应团队分析，漏洞确实存在，可以越权注册管理员账号。

![微信图片_20190919162936.jpg](https://image.3001.net/images/20190919/15688817878704.jpg!small)

## 六、修复方案

1、升级Harbor版本到 1.7.6 和 1.8.3

## 七、参考

> <https://unit42.paloaltonetworks.com/critical-vulnerability-in-harbor-> enables-privilege-escalation-from-zero-to-admin-cve-2019-16097/>
>
> <https://github.com/goharbor/harbor/issues/8951>

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

> 联系电话：400-156-9866
>
> Email：help@tophant.com

