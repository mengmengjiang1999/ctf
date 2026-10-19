##  **0x01 概要**

 **Apache Skywalking最近暴露了一个SQL注入漏洞：CVE-2020-9483。**

![](https://image.3001.net/images/20200622/1592809106_5ef0569261c9e.jpg!small)

Apache
SkyWalking是一个APM管理软件（应用性能监控），用于跟跑分析线上系统的性能，支持TCP、HTTP协议。这次出问题的Skywalking的软件版本号是6.0-6.6、7.0，升级官网版本8.0后，SQL注入漏洞问题被修复。

![](https://image.3001.net/images/20200622/1592809124_5ef056a4de547.png!small)

出问题的是Apache SkyWalking的Graph
QL协议接口。GraphQL是Facebook开源的数据查询规范。一用于API的查询语言，是对REST API的一种封装描述。原本REST
API的JSON协议下的接口，如果代码实现不注重安发规范也会存在安全隐患，Apache SkyWalking Graph
QL这次就出现SQL注入安全问题。SQL注入发生在Skywalking使用H2/MySQL/TiDB这三种数据库做存储的场景条件下，特定版本软件中可复现这个安全漏洞。

ElasticSearch也支持SQL查询，是通过插件实现支持的，ES不属于关系型数据库，如果Skywalking用的存储方案用是ES，这个SQL注入的问题可能会弱化一些。

##  **0x02 应急解决方案**

腾讯漏洞报告给出的应急对应方案：第一种方案：升级到官网网本的8.0版本。第二种方案：对Skywalking外网暴露的接口进行安全授权。第三种方案：最通用的方案，上WEB防火墙防护。

如果用户系统部署了WAF系统，可以用SQL注入的临时拦截策略进行处理，在请求没有到达Skywalking时，让WAF系统拦截过滤掉含有SQL注入请求。

##  **0x03 开源解决方案**

这篇重点是用开源方案解决问题，加入一层API网关，在Skywalking还没升级到8.0之前，将线上的老版本Skywalking的SQL注入的安全问题解决掉。将上面提到的第二、三方案，通过同一种软件系统实现落地，在Skywaling升级的过程中，也能保证本地对外网开放的Skywalking接口的安全性。

![](https://image.3001.net/images/20200622/1592809144_5ef056b81f22c.png!small)

APISIX网关和Skywalking同属于Apache的项目，APISIX本身支持Skywalking，有对应支持的插件，并且同时支持URL的鉴权（第二种方案）、URI的黑名单过滤（WAF的功能之一，SQL注入拦截）。

APISIX是开源的系统，在Nginx、OpenResty构建的应用网关产品，可以方便的实现上游管理，支持各种插件。APISIX的Skywalking插件与Skywalking配合，可以可视化的度量经过APISIX的请求，APISIX的同类开源网关产品，比如：Kong。

![](https://image.3001.net/images/20200622/1592809162_5ef056ca164ba.png!small)![](https://image.3001.net/images/20200622/1592809171_5ef056d35cf3c.png!small)

这是APISIX在Skywalking上的跟踪图。

最近出现CVE-2020-9483的问题，不升级Skywalking8.0的解决方案问题如下：

以前表过，不升级的方案：一种方案是对外网接口加鉴权认证，一种用防火墙拦截SQL注入。在APISIX当中，我们通过几个功能插件的添加，调整一下插件的执行顺序，就可不用升级Skywalking，解决这个安全问题。

**1.接口认证。**

为了避免外网可以直接访问接口Skywalking的接口，我们将Skywalking的请求，先转给APISIX网关，
由APISIX网关对请求进行认证，然后将通过认证请求转发给Skywalking。选用两个APISIX插件：Key-auth:通过加Key进行权限管理。Basic-auth:通过用户名密码对接进行加密权限管理。

**2.SQL注入拦截。**

一般的SQL注入，WAF系统会根据请求中存在的SQL子句特征进行拦截，APISIX同样有URI的过滤插件：

URI-Blocker：URI拦截黑名单。

##  **0x04 拦截SQL注入**

    
    
    local core = require("apisix.core")
    local re_compile = require("resty.core.regex").re_match_compile
    local re_find = ngx.re.find
    localipairs = ipairs
    local schema = {
       type = "object",
       properties = {
            block_rules = {
                type = "array",
                items = {
                    type = "string",
                    minLength = 1,
                    maxLength = 4096,
                },
               uniqueItems = true
            },
            rejected_code = {
                type = "integer",
                minimum = 200,
                default = 403
            },
       },
       required = {"block_rules"},
    }
    local plugin_name = "uri-blocker"
    local _M = {
       version = 0.1,
       priority = 2900,
       name = plugin_name,
       schema = schema,
    }
    function_M.check_schema(conf)
       local ok, err = core.schema.check(schema, conf)
       if not ok then
            return false, err
       end
       local block_rules = {}
       for i, re_rule in ipairs(conf.block_rules) do
            local ok, err = re_compile(re_rule,"j")
            -- core.log.warn("ok: ", tostring(ok), "err: ", tostring(err), " re_rule: ", re_rule)
            if not ok then
                return false, err
            end
            block_rules[i] = re_rule
       end
       conf.block_rules_concat = core.table.concat(block_rules, "|")
       core.log.info("concatblock_rules: ", conf.block_rules_concat)
       return true
    end
    function_M.rewrite(conf, ctx)
       core.log.info("uri: ", ctx.var.request_uri)
       local from = re_find(ctx.var.request_uri, conf.block_rules_concat,"jo")
       if from then
            core.response.exit(conf.rejected_code)
       end
    end
    return _M

上面是基本的黑名单过滤逻辑：用户准备若干SQL识别正则，可以识别正常的URI中存在可疑
的SQL文子句，对于这种URI直接进行拦截，或者将请求转发给蜜罐系统，这是另一个插件来实现的（动态上游）。

简单举例说明， 如何写SQL注入拦截正则，如下：

    
    
    1.“select.+(from|limit)”
    2.“(?:(union(.*?)select))”
    3.“having”

启用APISIX的URI-Blocker插件的方法，如下：

    
    
    curl -ihttp://127.0.0.1:9080/apisix/admin/routes/1 -H 'X-API-KEY:edd1c9f034335f136f87ad84b625c8f1' -X PUT -d '
    {
        "uri": "/*",
        "plugins": {
            "uri-blocker": {
                "block_rules":["root.exe", "root.m+"]
            }
        },
        "upstream": {
            "type":"roundrobin",
            "nodes": {
                "127.0.0.1:1980": 1
            }
        }
    }'

APISIX支持API调用的插件打开方式，我们将SQL注入识别的正则，通过这种方式在APISIX网关中注册生效各种插件。如果在Skywalking升级到8.0以后，可以快速的通过这种方式关闭插件。

    
    
    curl http://127.0.0.1:9080/apisix/admin/routes/1 -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' -X PUT -d '
    {
        "uri": "/*",
        "upstream": {
            "type": "roundrobin",
            "nodes": {
                "127.0.0.1:1980": 1
            }
        }
    }'

##  **0x05 总结**

如果您在Skywalking的使用过程中，或是某些开源软件的使用过程中，恰巧遇见类似的安全问题，想用一种低成本的方案解决CVE-2020-9483这种突发安全问题，可以考虑以上所说的开源解决方案，系统开源，即插即用。这次是Skywalking问题，以后也许会是其他软件，是需要一种敏捷的系统，速度的对应解决安全问题的。

##  **参考连接：**

> <https://mp.weixin.qq.com/s/tVJQa4so8nm0RYiWiKUYww>
>
> <https://github.com/apache/incubator-apisix>
>
> <https://shengyang.xyz/apisix/URI-blocker/>

***本文作者：糖果L5Q，转载请注明来自FreeBuf.COM**

