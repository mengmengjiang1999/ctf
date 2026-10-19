> 几周前，Apache
> HTTPD服务器的2.4.54版本发布了。它包括了一个修复CVE-2022-31813漏洞的补丁，我们在mod_proxy中发现了这个漏洞，它可能影响由Apache的反向代理提供服务的无意识的应用程序。
>
> 然而在软件更改日志危害评估中将其评为低级别漏洞，但是不妨碍它仍然很重要。
>
> 简而言之：如果你的版本存在问题，请打上补丁！

翻译感受：本篇文章水平很高，包含了网络请求知识和C语言代码知识，是一篇典型的好的分析文章。

[TOC]

## 基本概念阐述

如果您已经熟悉HTTP代理链，特别是从客户端到应用程序传输请求信息的过程，那么您可以跳到“文章mod_proxy有什么问题？”一部分。如果您只想了解故事的要点，请跳到“文章总结”一部分。

## 好的应用程序，坏的IP地址和邪恶的代理

所有Web应用程序都直接暴露在互联网上的时代已经过去了。现在，我们很少看到不包含反向代理、负载均衡器或两者都有的Web基础架构来面对应用程序的情况。造成这种情况的原因很多，包括性能、成本、IPv4耗尽等等。这种标准架构的演变带来了一系列新问题和技术挑战。

其中一个问题是源IP地址管理。当使用反向代理（或其他前置组件）时，发送到应用程序容器的HTTP请求是从该设备的IP地址而不是真实客户端的IP地址发出的。当应用程序需要这些信息（通常是用于日志记录或过滤）时，这就是一个问题。

为了解决这个挑战，反向代理开始在转发到应用程序的标头中注入有关原始HTTP请求的信息。这些包括客户端的IP地址、最初请求的主机、协议等条目。直到最近，HTTP规范中不存在用于存储这些信息的标准字段。因此，非标准标头已被创建：

  * X-Forwarded-{Host,For,Proto}
  * X-Real-IP
  * Client-IP

因此，X-Forwarded-For、X-Forwarded-Host和X-Forwarded-Proto已成为事实上的标准。尽管2014年发布了RFC
7239，标准化了一个名为Forwarded的标头字段，但这仍然是正确的。

这些标头的操作非常简单。它们中的值表示与原始客户端请求相关的信息：

  * X-Forwarded-Proto：包含原始请求协议（即HTTP/HTTPS）。
  * X-Forwarded-Host：包含代理接收到的Host标头的原始值。
  * X-Forwarded-For：包含原始客户端的IP地址以及所有先前中间代理的IP地址。

实质上，这就是转发标头的全部内容。

## 跳转，跳转，逐级跳转问题

http中的HOP HOP HOP-BY-HOP 逐级跳转标头是一种HTTP机制，允许指示代理哪些标头应沿请求（端到端）转发，哪些应立即处理和删除（逐跳）。

其中有几个标头始终被视为逐跳。它们是：

  * Connection 
  * Keep-Alive
  * Proxy-Authenticate 
  * Proxy-Authorization 
  * TE Trailers 
  * Transfer-Encoding 
  * Upgrade  
虽然所有其他标头都被视为端到端的，但可能会将其中一些添加到前面的集合中，方法是在Connection标头中列出它们，紧接着是经典的Close或Keep-Alive关键字。这样做，所有列出的标头都应该被第一个接收到它们的代理处理和删除。

正如Nathan Davison在他2019年的一篇文章中所解释的那样，这种机制暴露了一个非常有趣的攻击面。

## 那么，mod_proxy有什么问题？?

像所有反向代理一样，Apache HTTPD与mod_proxy一起尽最大努力遵循真正的和事实上的标准。这意味着代理组件将添加X-Forwarded标头，如文档中所述。

> 在反向代理模式下操作（例如使用ProxyPass指令），mod_proxy_http会添加多个请求标头，以便将信息传递到目标服务器。这些标头包括：

  1. X-Forwarded-For：客户端的IP地址。 
  2. X-Forwarded-Host：客户端在Host HTTP请求标头中请求的原始主机。 
  3. X-Forwarded-Server：代理服务器的主机名。

同时，代理还遵循逐跳标头指示，并从转发的请求中删除它们。

问题是，如果将X-Forwarded标头列为逐跳，则Apache在将它们转发到上游基础架构时失败。在正常情况下，当接收到合法请求时，例如从此curl调用中：

    
    
    $ curl myhost.local/test
    

在 _Apache mod_proxy_ 反向代理后面的应用程序收到以下HTTP请求：

    
    
    GET / HTTP/1.1
    Host: localhost:5000
    User-Agent: curl/7.74.0
    Accept: */*
    X-Forwarded-For: 192.168.42.42
    X-Forwarded-Host: myhost.local
    X-Forwarded-Server: 127.0.1.1
    Connection: Keep-Alive
    

但是，如果发送相同的请求，并将X-Forwarded标头包含在逐跳列表中：

    
    
    $ curl -H "Connection: close, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Server" myhost.local/test
    

接收到的请求将不同：

    
    
    GET / HTTP/1.1
    Host: localhost:5000
    User-Agent: curl/7.74.0
    Accept: */*
    Connection: Keep-Alive
    

最后，接收到的请求与直接从应用程序服务器上的回环接口发送的请求完全相同。

## 这不是本末倒置吗？

这种奇怪的行为可以在mod_proxy
HTTPD模块的源代码中快速跟踪到。所有相关的内容都打包在proxy_util.c文件（modules/proxy/proxy_util.c）中。

处理逐跳标头的函数是`ap_proxy_clear_connection`。它甚至在代码中包含了很好的注释与说明。

    
    
    /**
     * Remove all headers referred to by the Connection header.
     * Returns -1 on error. Otherwise, returns 1 if 'Close' was seen in
     * the Connection header tokens, and 0 if not.
     */
    static int ap_proxy_clear_connection(request_rec *r, apr_table_t *headers)
    {
        int closed = 0;
        header_connection x;
    
        x.pool = r->pool;
        x.array = NULL;
        x.error = NULL;
        x.is_req = (headers == r->headers_in);
    
        apr_table_unset(headers, "Proxy-Connection");
    
        apr_table_do(find_conn_headers, &x, headers, "Connection", NULL);
        apr_table_unset(headers, "Connection");
    
        //Skipped
    
        if (x.array) {
            int i;
            for (i = 0; i < x.array->nelts; i++) {
                const char *name = APR_ARRAY_IDX(x.array, i, const char *);
                ap_log_rerror(APLOG_MARK, APLOG_DEBUG, 0, r, APLOGNO(02807)
                              "Removing header '%s' listed in Connection header",
                              name);
                if (!ap_cstr_casecmp(name, "close")) {
                    closed = 1;
                }
                apr_table_unset(headers, name);
            }
        }
    
        return closed;
    }
    

负责添加X-Forwarded标头的代码片段位于`ap_proxy_create_hdrbrgd`函数中。同时，一个很好的代码文档注释同样标注了该功能。

    
    
    PROXY_DECLARE(int) ap_proxy_create_hdrbrgd(apr_pool_t *p,
                                            apr_bucket_brigade *header_brigade,
                                            request_rec *r,
                                            proxy_conn_rec *p_conn,
                                            proxy_worker *worker,
                                            proxy_server_conf *conf,
                                            apr_uri_t *uri,
                                            char *url, char *server_portstr,
                                            char **old_cl_val,
                                            char **old_te_val)
    {
    //Skipped
    /* X-Forwarded-*: handling
     *
     * SKIPPED
     */
    if (dconf->add_forwarded_headers) {
        if (PROXYREQ_REVERSE == r->proxyreq) {
            const char *buf;
    
            /* Add X-Forwarded-For: so that the upstream has a chance to
             * determine, where the original request came from.
             */
            apr_table_mergen(request_headers, "X-Forwarded-For",
                             r->useragent_ip);
    
            /* Add X-Forwarded-Host: so that upstream knows what the
             * original request hostname was.
             */
            if ((buf = apr_table_get(r->headers_in, "Host"))) {
                apr_table_mergen(request_headers, "X-Forwarded-Host", buf);
            }
    
            /* Add X-Forwarded-Server: so that upstream knows what the
             * name of this proxy server is (if there are more than one)
             * XXX: This duplicates Via: - do we strictly need it?
             */
            apr_table_mergen(request_headers, "X-Forwarded-Server",
                             r->server->server_hostname);
        }
    }
    

重要的是，尽管X-Forwarded添加代码在第4050行（左右）调用，但`ap_proxy_clear_connection`函数在此之后调用，大约在第4083行左右。

现在已经可以明白了，mod_proxy作为捆绑在Apache HTTPD版本2.4.53，首先填充X-Forwarded标头，然后立即删除它们。这是一个错误的处理流程。

这个问题是在官方软件的2.2.1版本中引入的，更确切地说是在2006年4月1日的第377053个修订版本中引入的（就像一个愚人节玩笑）。这使得这个漏洞存在有16年的历史了。

## 这有多糟糕？

也可能不会用这个问题来危害Apache服务器。但事实上，这个问题属于“影响应用程序”的类别。其影响的后果将取决于应用程序和基础架构的设置。

虽然几乎没有通用的、长期有效的攻击场景。但是，根据上下文可以找到多个用法。

### 流行的Web框架

根据应用程序使用的框架，这个问题可能是可利用的或不可利用的。实际上，所有利用方案都取决于框架使用和信任X-Forwarded标头的意愿。因为X-Forwarded标头有时可以被欺骗并用于攻击应用程序，所以Web框架开发了防御措施来保护其用户。它们主要分为两类：

  * **代理信任设置** ：当用户需要定义一个设置告诉应用程序在代理后面，并且哪些地址应该被视为可信的转发者时。
  * **什么也不做** ：当应用程序不提供利用X-Forwarded标头的方法时。在这种情况下，通常存在插件或其他中间件来处理该情况。

让我们看看常见的例子。

#### ExpressJS框架处理

在使用ExpressJS时，存在一个设置来考虑X-Forwarded标头。它的名称是trust proxy，并且根据要实现的目标接受多个参数类型。

Express文档[[EXPRIP]](https://www.synacktiv.com/en/publications/cve-2022-31813-forwarding-addresses-is-hard#references)指出，proxy_addr包用于管理标头的处理。有趣的是，当接收到的请求不包括X-Forwarded标头时，请求的值将保持为合法值。

这意味着客户端地址将设置为远程地址（代理服务器的地址），虚拟主机名将设置为Host标头值（可能与客户端请求的不同），等等。

#### Flask框架处理

Flask文档[[FLASKIP]](https://www.synacktiv.com/en/publications/cve-2022-31813-forwarding-addresses-is-hard#references) 声明，框架本身不信任或使用X-Forwarded标头，但它提出使用Werkzeug中间件来处理该任务。

X-Forwarded-For Proxy Fix组件确实旨在接收和处理传入的X-Forwarded标头。它接受一个配置，告诉它从每个标头类型（对应于受信任代理添加的）信任多少个值（下一个是要使用的实际值）。

行为与Express非常相似。当未设置X-Forwarded标头时，将保留实际请求的值。

#### Django框架处理

自2009年1.1版本以来，Django已删除对X-Forwarded-For标头的支持[[DJANIP]](https://www.synacktiv.com/en/publications/cve-2022-31813-forwarding-addresses-is-hard#references)。

> 删除SetRemoteAddrFromForwardedFor中间件¶
>
>
> [...]已经证明，这种机制不能够可靠地用于通用目的，并且（尽管有相反的文档）它被包括在Django中可能会导致应用程序开发人员认为REMOTE_ADDR的值是“安全的”或某种方式可靠作为身份验证来源。

更改日志中的方法是绝对正确的。但是，这使得使用该框架的用户没有简单的解决方案来处理传入的地址，他们会错误地实现自定义解决方法。

广大互联网（例如stackoverflow）倾向于推荐使用django-ipware方法。这个允许高度可配置，与ExpressJS和Flask不同，如果在数据链中配置了受信任的代理但未找到，那么可以接受不返回地址。但是，由于具有如此高的可配置性，也有可能完全搞砸。其后果超出了本文章所讨论的范围。

### Tomcat容器处理

Tomcat关于X-Forwarded标头的行为有点像django-ipware和Flask或Express的混合。
Tomcat本身不考虑标头。但是，它提供了一些可以配置以处理这些标头的Valve。

RemoteIPValve与django-ipware一样可配置。但是，即使在正确配置的情况下，也很明显可能会对其进行错误配置，即使远程IP阀门被正确配置，它仍将保留请求值，当没有提供X-Forwarded标头时。

例如，该阀门可以配置为将单个IP视为受信任的代理。 在这种情况下，转发包含X-Forwarded-For标头的请求会产生预期的合法结果。
如果没有提供此类标头，则保留受信任的代理地址。

    
    
    <Valve className="org.apache.catalina.valves.RemoteIpValve" hostHeader="x-forwarded-host"  trustedProxies="192.168.122.1" />
    

在这种情况下，转发包含 _X-Forwarded-For_ 标头的请求会得到预期的合法结果：

    
    
    $ curl http://srv.local:8080/ipinfo.jsp -H "X-Forwarded-For: 1.0.0.0" # request sent from the proxy
    <html>
    <body>
        <h2>Client IP is: 1.0.0.0</h2>
    </body>
    </html>
    

如果没有提供这样的报头，则会保留可信的代理地址。

    
    
    $ curl http://srv.local:8080/ipinfo.jsp # request sent from the proxy
    <html>
    <body>
        <h2>Client IP is: 192.168.122.1</h2>
    </body>
    </html>
    

## 实际攻击场景和供给面有哪些？

既然我们知道大多数应用程序框架将只接受直接来自反向代理请求，那么让我们看看我们实际上能实现什么攻击。

### IP代理欺骗问题

现在我们知道大多数应用程序框架将仅接受直接来自反向代理的请求，让我们看看实际可以实现什么。

代理IP地址欺骗
这很明显。只要您可以代表Apache反向代理发送请求，您就自动伪造了其IP地址。当应用程序和Apache反向代理都托管在同一台机器上时，这尤其有趣。在这种情况下，对应用程序的请求将显示为来自本地主机。

进行基于IP的访问控制，同时将localhost列入可信任的地址列表是很常见的。这甚至是我们在入侵测试期间首先发现mod_proxy问题的原因所在。

通过开源项目进行快速的愚蠢搜索就可以导致某些设置在Apache反向代理后面的应用程序受到影响。

>
> [https://grep.app/search?q=%5C.remote_addr%20%3F%3D%3D%20%3F%5B%27%22%5D127&regexp=true&filter[lang][0]=Python](https://grep.app/search?q=%5C.remote_addr%20%3F%3D%3D%20%3F%5B%27%22%5D127&regexp=true&filter\[lang\]\[0\]=Python)

您要查找的典型代码片段，例如在Ziconius/FudgeC2项目中返回的先前搜索中演示。

    
    
    def shutdown_listener():
        if request.remote_addr == "127.0.0.1":
            shutdown_hook = request.environ.get('werkzeug.server.shutdown')
            if shutdown_hook is not None:
                shutdown_hook()
    

在这种情况下，在应用程序前面有一个Apache反向代理将导致身份验证绕过。

### 任意地址欺问题

在某些情况下，可能会稍微扩展先前的攻击。特别是，如果应用程序或框架接受其他来源的IP地址作为X-Forwarded-For的备用来源。在这种情况下，强制删除X-Forwarded-For标头并添加替代方案可能允许欺骗任意IP地址。

当IPWARE_META_PRECEDENCE_ORDER设置保持不变时，django-ipware默认配置就是这种情况。根据其他设置，删除X-Forwarded-For标头可能会导致组件返回没有IP地址或代理地址的返回。

    
    
    $ curl -i 192.168.122.225/test/ip/
    HTTP/1.1 200 OK
    [SKIPPED]
    
    Hello 192.168.122.1
    $ curl -H "Connection: close, X-Forwarded-For" -i 192.168.122.225/test/ip/
    HTTP/1.1 200 OK
    [SKIPPED]
    
    Hello 127.0.0.1
    

但在这种情况下，通过向请求添加Client-IP标头，可以实现欺骗任意IP。

    
    
    $ curl -H "Client-IP: 10.10.10.10" -H "Connection: close, X-Forwarded-For" -i 192.168.122.225/test/ip/
    HTTP/1.1 200 OK
    Date: Thu, 07 Jul 2022 14:34:50 GMT
    Server: WSGIServer/0.2 CPython/3.9.2
    Content-Type: text/html; charset=utf-8
    X-Frame-Options: DENY
    Content-Length: 17
    X-Content-Type-Options: nosniff
    Referrer-Policy: same-origin
    Cross-Origin-Opener-Policy: same-origin
    Connection: close
    
    Hello 10.10.10.10
    

### 主机注入/主机过滤器绕过问题

到目前为止，我们只使用X-Forwarded-For标头来实现某种IP地址欺骗。 X-Forwarded-Host也可以是一个很好的攻击选项。特别是在复杂的架构中，可能会访问后端服务器或应用程序的默认虚拟主机，而这些虚拟主机并不打算从公共访问中访问。

实际上，有趣的是，这种利用场景已经被用于在野攻击，并且是作为更大的利用链的一部分。相关漏洞是CVE-2022-1388，在F5 BIG-IP中进行身份验证绕过以进行远程代码执行。

如果您阅读有关此问题的详细说明[[F5VULN]](https://www.synacktiv.com/en/publications/cve-2022-31813-forwarding-addresses-is-hard#references)，则可能会注意到以下声明：

>   * Connection: X-F5-Auth-Token, X-Forwarded-Host
>

>
> 这使Jetty无法知道该请求是由Apache提供的，并将该请求视为本地完成。

实际上，这就是我们正在讨论的问题。通过删除X-Forwarded-Host标头，Jetty服务器被欺骗成将请求视为本地，从而允许访问管理应用程序。

### 拒绝服务漏洞

因为我们可以代表反向代理发送请求，所以我们可以尝试滥用速率限制或反暴力破解机制。例如，想象一下在IP地址上设置了失败的身份验证的 _fail2ban_
保护。这种保护可能被滥用以强制应用程序服务器将反向代理的IP地址列入黑名单。

## 文章总结

_Apache HTTPD mod_proxy_ 在版本2.2.1和2.4.53之间，当这些标头以跳跃的方式列出时，不会填充X-Forwarded标头。在其后面托管的应用程序可能会错误使用真实客户端的IP地址或请求的主机名。

根据应用程序和架构，这可能会导致身份验证或过滤器绕过，IP地址欺骗或拒绝服务。漏洞CVE-2022-1388说明了这一点，利用mod_proxy的问题来访问私有应用程序。

该漏洞已在Apache HTTPD 2.4.54版本中修复。

## CVE时间线

Time | Event  
---|---  
05/10 | 向HTTPD安全团队报告问题。  
05/18 | HTTPD安全团队拒绝了该问题  
05/18 | 进一步的详细信息添加到详情中。  
05/30 | 问题采纳。  
06/08 | 发布了补丁。  
06/09 | CVE已发布。  
  
> 参考链接：
>
> 1.滥用HTTP跳跃请求标头：<https://nathandavison.com/blog/abusing-http-hop-by-hop-> request-headers>
>
>   1. 在代理后的ExpressJS：<https://expressjs.com/en/guide/behind-proxies.html>
>

>
>
> 3.告诉Flask它在代理后面：<https://flask.palletsprojects.com/en/2.1.x/deploying/proxy_fix/>
>
> 4.Django 1.1发布代理说明：<https://docs.djangoproject.com/en/4.0/releases/1.1/>
>
> 5.F5 BIG-IP远程代码执行漏洞CVE-2022-138:<https://blog.cyble.com/2022/05/12/f5-big-> ip-remote-code-execution-vulnerability-cve-2022-1388/>

