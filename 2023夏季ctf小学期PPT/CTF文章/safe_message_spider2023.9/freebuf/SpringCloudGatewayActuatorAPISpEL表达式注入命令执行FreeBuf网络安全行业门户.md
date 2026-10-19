## I 漏洞前奏

昨天看到Vmware/security发布了安全告警，触发了强烈研究它的好奇心。说搞就搞！希望能抛砖引玉，大家可以多交流交流。

![1646474093_6223336d8c31a5f918cff.png!small?1646474093969](https://image.3001.net/images/20220305/1646474093_6223336d8c31a5f918cff.png!small?1646474093969)

![1646284919_62205077165204b012310.png!small?1646284918871](https://image.3001.net/images/20220303/1646284919_62205077165204b012310.png!small?1646284918871)

## II Spring Cloud Gateway 介绍

SpringCloud Gateway 是 Spring Cloud 的一个全新项目，该项目是基于 Spring 5.0，Spring Boot 2.0 和
Project Reactor 等技术开发的网关，它旨在为微服务架构提供一种简单有效的统一的 API 路由管理方式。

SpringCloud Gateway 作为 Spring Cloud 生态系统中的网关，目标是替代 Zuul，在Spring Cloud
2.0以上版本中，没有对新版本的Zuul 2.0以上最新高性能版本进行集成，仍然还是使用的Zuul
2.0之前的非Reactor模式的老版本。而为了提升网关的性能， **SpringCloud Gateway是基于WebFlux框架实现的，**
而WebFlux框架底层则使用了高性能的Reactor模式通信框架Netty。

Spring Cloud Gateway 的目标不仅提供统一的路由方式，并且基于 Filter
链的方式提供了网关基本的功能，例如：安全，监控/指标，和限流。

Note:由于此漏洞涉及到路由，就很有必要研究下路由规则。

## III Spring Cloud Gateway 路由匹配规则

Spring Cloud Gateway 的功能很强大，仅仅通过 Predicates 的设计就可以看出来，Spring Cloud Gateway 是
**通过 Spring WebFlux 的 HandlerMapping 做为底层支持来匹配到转发路由** ，Spring Cloud Gateway
内置了很多 Predicates 工厂，这些 Predicates 工厂通过不同的 HTTP 请求参数来匹配，多个 Predicates 工厂可以组合使用。

![1646470363_622324dbc0231568c642b.png!small?1646470364170](https://image.3001.net/images/20220305/1646470363_622324dbc0231568c642b.png!small?1646470364170)

## IV 漏洞介绍

Spring Cloud Gateway:是基于 Spring Framework 和 Spring Boot 构建的 API
网关，目的为微服务架构提供一种简单、有效、统一的 API 路由管理方式。

当启用和暴露 Gateway Actuator 端点时，使用 Spring Cloud Gateway
的应用程序可受到代码注入攻击。攻击者可以发送特制的恶意请求，从而远程执行任意代码。

## V 风险等级

高危：攻击者可利用该漏洞可RCE,发现漏洞已在野攻击。

## VI 影响范围

3.1.0 、3.0.0至3.0.6 3.0.0之前的版本

根据FOFA提供的数据显示全球范围内Spring Cloud Gateway共有 **1,106,595** 个相关服务对外开放。中国使用数量最多，共有
**513,580** 个；美国第二，共有 298,187 个；德国第三，共有 40,744 个；新加坡第四，共有 31,380 个；韩国第五，共有
29,936 个。

![1646468322_62231ce2cc73bee2aebd2.png!small?1646468323175](https://image.3001.net/images/20220305/1646468322_62231ce2cc73bee2aebd2.png!small?1646468323175)

全球范围内分布情况

中国大陆地区 **北京使用数量最多** ，共有 73,842 个；浙江第二，共有 62,239 个；广东第三，共有 51,794 个；上海第四，共有
45,121 个；山东第五，共有 14,285 个。

![1646468803_62231ec3061bcb1933c33.png!small?1646468803490](https://image.3001.net/images/20220305/1646468803_62231ec3061bcb1933c33.png!small?1646468803490)

## VII 漏洞环境搭建

![1646357648_62216c90f2ad8cdde130f.png!small?1646357650524](https://image.3001.net/images/20220304/1646357648_62216c90f2ad8cdde130f.png!small?1646357650524)

![1646358004_62216df4bb08462a1ad83.png!small?1646358006303](https://image.3001.net/images/20220304/1646358004_62216df4bb08462a1ad83.png!small?1646358006303)

漏洞环境搭建完成

## VIII 漏洞检测

![1646358469_62216fc5b17b683fe9737.png!small?1646358471400](https://image.3001.net/images/20220304/1646358469_62216fc5b17b683fe9737.png!small?1646358471400)

可添加一个包含恶意SpEL表达式的路由

![1646359024_622171f092e4e37abfc09.png!small?1646359026294](https://image.3001.net/images/20220304/1646359024_622171f092e4e37abfc09.png!small?1646359026294)

应用刚添加的路由，这个数据包将触发SpEL表达式的执行

![1646358967_622171b79ec7cc06174df.png!small?1646358969390](https://image.3001.net/images/20220304/1646358967_622171b79ec7cc06174df.png!small?1646358969390)

> GET /actuator/gateway/routes/hacktest HTTP/1.1  
> Host: xxxx:8080  
> Accept-Encoding: gzip, deflate  
> Accept: */*  
> Accept-Language: en  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36  
> Connection: close  
> Content-Type: application/x-www-form-urlencoded  
> Content-Length: 0

查看执行结果（uid=0(root) gid=0(root) gid=0(root) groups=0(root)）

![1646359379_62217353308002689be80.png!small?1646359380863](https://image.3001.net/images/20220304/1646359379_62217353308002689be80.png!small?1646359380863)

> DELETE /actuator/gateway/routes/hacktest HTTP/1.1  
> Host: localhost:8080  
> Accept-Encoding: gzip, deflate  
> Accept: */*  
> Accept-Language: en  
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36  
> Connection: close

删除所添加的路由，搞定！

## IX 漏洞修复

1>3.1.x用户应升级到3.1.1+、3.0.x用户应升级到3.0.7+

2>如果不需要Actuator端点，可以通过management.endpoint.gateway.enable:false配置将其禁用

3>如果需要Actuator端点，则应使用Spring Security对其进行保护

