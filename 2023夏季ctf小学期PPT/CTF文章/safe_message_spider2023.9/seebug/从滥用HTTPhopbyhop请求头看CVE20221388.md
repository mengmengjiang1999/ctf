**作者：Y4er**  
**原文链接：<https://y4er.com/post/from-hop-by-hop-to-cve-2022-1388/>**

## 前言

最近爆出来的bigip的CVE-2022-1388漏洞，涉及到一个知识点就是hop by hop，对这个东西没了解过，所以有了此文。

## 回顾CVE-2021-22986

CVE-2021-22986原理是因为apache和jetty之间的鉴权不当导致的权限绕过。

当不存在Authorization
basic认证头时，由apache做权限校验，判断basic认证头是否存在，此时response中的server头为apache

![1.png](https://images.seebug.org/content/images/2022/05/26/1653550334000-1vwzys.png-w331s)

当给一个错误的basic认证头时仍返回apache的401认证，注意这里给的是一个`admin:`空密码的admin用户。

![2.png](https://images.seebug.org/content/images/2022/05/26/1653550335000-2jymac.png-w331s)

当给一个空的X-F5-Auth-Token认证头时，由jetty处理返回401，报错信息为`Authorization failed: no user
authentication header or token detected.`

![3.png](https://images.seebug.org/content/images/2022/05/26/1653550341000-3xnipo.png-w331s)

当两个请求头都存在时，绕过了权限校验，rce。

![4.png](https://images.seebug.org/content/images/2022/05/26/1653550347000-4srlkd.png-w331s)

由此得出结论，当存在X-F5-Auth-Token头时apache不检查basic认证头，而jetty只会判断用户名，而不判断密码是否正确。

思考为什么权限校验不起作用？

查看apache的配置文件/config/httpd/conf/httpd.conf发现

![5.png](https://images.seebug.org/content/images/2022/05/26/1653550350000-5kkstu.png-w331s)

/mgmt/请求被转发到8100端口，并且启用了AuthPAM_Enabled，启用auth会调用/usr/lib/httpd/modules/mod_auth_pam.so判断鉴权，在这个so中

![6.png](https://images.seebug.org/content/images/2022/05/26/1653550351000-6siccn.png-w331s)

判断是否存在X-F5-Auth-Token头

![7.png](https://images.seebug.org/content/images/2022/05/26/1653550353000-7zqqzn.png-w331s)

然后接着拿一些其他的请求头

![8.png](https://images.seebug.org/content/images/2022/05/26/1653550354000-8pzsga.png-w331s)

最终逻辑就是如果存在转发给jetty处理。

而在jetty中 `f5.rest.jar`

    
    
    com.f5.rest.workers.authz.AuthzHelper#decodeBasicAuth

![9.png](https://images.seebug.org/content/images/2022/05/26/1653550356000-9hdrre.png-w331s)

从header中拿到basic认证的用户名和密码，在`com.f5.rest.common.RestOperationIdentifier#setIdentityFromBasicAuth`中设置用户身份

![10.png](https://images.seebug.org/content/images/2022/05/26/1653550357000-10oanuh.png-w331s)

因为basic不为空，所以进入`com.f5.rest.common.RestOperation#setIdentityData`

![11.png](https://images.seebug.org/content/images/2022/05/26/1653550359000-11rmkxe.png-w331s)

因为 `userName!=null && userReference==null`，所以处理完之后用户的身份变为

    
    
    identityData.userName = 'admin';
    identityData.userReference = 'http://localhost/mgmt/shared/authz/users/admin'
    identityData.groupReference = null;

接着在鉴权的地方 `com.f5.rest.workers.EvaluatePermissions#completeEvaluatePermission`

![12.png](https://images.seebug.org/content/images/2022/05/26/1653550365000-12pvtga.png-w331s)

setBasicAuthFromIdentity之后拿到userRef，此时userRef即上文处理完之后的用户身份。在判断`AuthzHelper.isDefaultAdminRef(userRef)`时

![13.png](https://images.seebug.org/content/images/2022/05/26/1653550365000-13vflwi.png-w331s)

先拿到默认的AdminReference和当前用户身份匹配，在getDefaultAdminReference()中拿到admin用户的身份new一个RestReference

![14.png](https://images.seebug.org/content/images/2022/05/26/1653550369000-14qsspp.png-w331s)

    
    
    UrlHelper.buildPublicUri(UrlHelper.buildUriPath(new String[]{WellKnownPorts.AUTHZ_USERS_WORKER_URI_PATH, DEFAULT_ADMIN_NAME}))`最终构建出来的url还是`http://localhost/mgmt/shared/authz/users/admin

所以此时我们在basic中将用户名设置为admin则可以满足`defaultReference != null &&
defaultReference.equals(userReference)`至此绕过权限认证。

然后就是找一个命令执行的点

![15.png](https://images.seebug.org/content/images/2022/05/26/1653550372000-15xhmmt.png-w331s)

对应的就是util下的路由功能点

![16.png](https://images.seebug.org/content/images/2022/05/26/1653550374000-16omabc.png-w331s)

调用bash执行命令即可

![17.png](https://images.seebug.org/content/images/2022/05/26/1653550377000-17wwkeo.png-w331s)

另外此处文档中也有提到

<https://f5-sdk.readthedocs.io/en/latest/_modules/f5/bigip/tm/util/bash.html>

## CVE-2021-22986的修复

在上文中，我们传递了一个X-F5-Auth-Token为空的header头，所以completeEvaluatePermission函数会赋给我们一个默认的用户身份。而修复补丁在mod_auth_pam.so判断当X-F5-Auth-Token为空直接返回401

![18.png](https://images.seebug.org/content/images/2022/05/26/1653550378000-18sveza.png-w331s)

所以我们无法传递给jetty一个空的X-F5-Auth-Token请求头。

那么CVE-2022-1388就是对其的绕过，这里引申出本文的重点hop by hop。

## hop by hop

先解释下这是什么东西。根据[RFC
2612](https://datatracker.ietf.org/doc/html/rfc2616#section-13.5.1)，HTTP/1.1
规范默认将以下标头视为逐跳：Keep-Alive、Transfer-Encoding、TE、Connection、Trailer、Upgrade、Proxy-Authorization和Proxy-Authenticate。当在请求中遇到这些标头时，代理服务器会处理这些标头，并且不会将其转发到下一个节点。

以推特[@jinonehk](https://twitter.com/jinonehk/status/1420413477521301507)的一张图来看

![19.png](https://images.seebug.org/content/images/2022/05/26/1653550381000-19griwk.png-w331s)

第一次尝试导出用户时返回403，因为不是环路ip，而当加上`Connection: close, X-Real-IP`时，导出用户成功，说明此时后端服务获取不到X-Real-IP请求头，认为是本地请求所以可以导出用户。

更具体一点，我在这里找到了一个ctf的题目 <https://github.com/ritsec/RITSEC-CTF-2019/tree/master/Web/hop-by-hop>

在verify函数中尝试获取xff头，如果获取不到则默认为direct。

![20.png](https://images.seebug.org/content/images/2022/05/26/1653550381000-20kgbov.png-w331s)

而前置服务为apache，根据逐跳原则，当Connection中加了其他标头X-Forwarded-For，那么在apache转发给下一跳时，会移除X-Forwarded-For头，导致在verify函数中`request.headers['X-Forwarded-For']`抛出异常，由此拿到flag。

![21.png](https://images.seebug.org/content/images/2022/05/26/1653550385000-21zvcjk.png-w331s)

可以自己本地搭一个反代试试，我这有一个springboot的项目，只有一个controller

![22.png](https://images.seebug.org/content/images/2022/05/26/1653550386000-22rdllm.png-w331s)

apache 80端口反代springboot 9091端口

先开启反代功能

    
    
    LoadModule proxy_module modules/mod_proxy.so

配置virtualhost

    
    
    <VirtualHost *:80>
        ProxyRequests Off
        ProxyPreserveHost On
        <Proxy>
            Order deny,allow
            Allow from all
        </Proxy>
        ProxyPass /  http://localhost:9091
        ProxyPassReverse /  http://localhost:9091
    </VirtualHost>

正常传token，springboot可以获取到token头

![23.png](https://images.seebug.org/content/images/2022/05/26/1653550388000-23bbfbr.png-w331s)

当connection加上Token时，springboot获取的token为null

![24.png](https://images.seebug.org/content/images/2022/05/26/1653550389000-24quabp.png-w331s)

由此可见CVE-2022-1388

## CVE-2022-1388

在CVE-2022-1388中使用Connection加上X-F5-Auth-Token让jetty接收到的X-F5-Auth-Token为null以此来绕过权限认证。

![25.png](https://images.seebug.org/content/images/2022/05/26/1653550393000-25iojlf.png-w331s)

另外需要注意的一个地方为host赋值为localhost，不然host为ip时报错

![26.png](https://images.seebug.org/content/images/2022/05/26/1653550398000-26mrmza.png-w331s)

因为CVE-2021-22986之后，在`com.f5.rest.common.RestOperationIdentifier#setIdentityFromBasicAuth`中

![27.png](https://images.seebug.org/content/images/2022/05/26/1653550404000-27xcgai.png-w331s)

当host为localhost或者127.0.0.1时，会赋予用户身份。另外这里还可以赋值host为127.4.2.1然后basic用户名为f5hubblelcdadmin，或者通过Connection加上X-Forwarded-Host也可以rce，就不截图了。

## hop by hop的适用面

我本地测试了apache、nginx、openresty、HAProxy，其中只有apache会消费掉Connection中的请求头，其他的要单独测试了。

## 参考链接

看了太多资料了，用到了但是没贴上来的请原作者见谅。

  1. [漏洞百出](https://articles.zsxq.com/id_rfsu4pm43qno.html)
  2. <https://twitter.com/jinonehk/status/1420413477521301507>
  3. <https://nathandavison.com/blog/abusing-http-hop-by-hop-request-headers>
  4. [RFC 2616](https://datatracker.ietf.org/doc/html/rfc2616#section-13.5.1)
  5. <https://y4y.space/2021/03/19/cve-2021-22986-f5-rest-unauthenticated-rce-analysis/>
  6. <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection>
  7. <https://nosec.org/home/detail/4722.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1908/>

