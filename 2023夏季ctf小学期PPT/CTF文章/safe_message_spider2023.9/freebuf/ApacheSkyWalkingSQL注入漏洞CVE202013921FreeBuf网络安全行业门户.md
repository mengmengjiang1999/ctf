## ****Apache SkyWalking组件介绍****

SkyWalking 是观察性分析平台和应用性能管理系统。提供分布式追踪、服务网格遥测分析、度量聚合和可视化一体化解决方案。支持Java, .Net
Core, PHP, NodeJS, Golang, LUA语言探针。支持Envoy + Istio构建的Service
Mesh。其具有多种监控手段、语言探针和service
mesh；轻量高效不需要大数据；模块化设计，UI、存储、集群管理多种机制可选；六种语言自动探针；支持告警；提供优秀的可视化方案的特性，在国内互联网、银行、民航等领域有极其广泛的应用。

## ****漏洞描述****

近日Apache SkyWalking官方发布了最新的SkyWalking
8.1.0版本，修复了一个SQL注入漏洞（CVE-2020-13921）。在SkyWalking多个版本中，默认开放未授权GraphQL接口，当H2 /
MySQL / TiDB用作Apache SkyWalking存储时，攻击者可构造通配符查询语句进行SQL注入，从而导致用户的数据库敏感信息泄露。

## ****漏洞复现****

向有该漏洞的Apache Skywalking环境发送特殊构造的HTTP请求，可以看到数据库错误回显，效果如下：

****![](https://image.3001.net/images/20200807/1596796805.png!small)****

# ****影响范围****

目前受影响的Apache SkyWalking版本：

Apache SkyWalking 6.0.0~6.6.0

Apache SkyWalking 7.0.0

Apache SkyWalking 8.0.0~8.0.1

## ****修复建议****

目前厂商已在SkyWalking 8.1.0版本修复该漏洞，参考链接：

<https://github.com/apache/skywalking/releases>

##  ****时间轴****

2020/08/05 Apache SkyWalking官方发布新版本。

2020/08/07 深信服千里目安全实验室发布漏洞安全通告。

