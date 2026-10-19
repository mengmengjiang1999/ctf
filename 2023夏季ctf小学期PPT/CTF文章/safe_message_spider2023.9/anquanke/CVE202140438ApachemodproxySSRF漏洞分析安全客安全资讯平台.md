# CVE-2021-40438 Apache mod_proxy SSRF 漏洞分析

阅读量 **399235**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-24 10:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01874facfe256de95d.png)

## 0x00 前言

复现这个漏洞的过程中觉得很有分析的必要，而作者源码结合 log 调试分析的[这篇文章](https://firzen.de/building-a-poc-for-cve-2021-40438)已经写得比较详尽了，就想自己纯从审计的角度写一下分析巩固一下。

总之，如有不当，烦请评论捉虫，我会在第一时间响应并评论提示，谢谢。

## 0x01 简介

###  漏洞成因

![](https://p0.ssl.qhimg.com/t013487448c54895670.png)

可构造 uri 使 mod_proxy 请求转发给内部服务器造成 SSRF 。

###  影响版本

![](https://p3.ssl.qhimg.com/t01b26aa7bbf5030ba2.png)

###  实验环境

代审环节个人建议是亲手编译调试 Apache 跟进，可以参照 P 神的教程：

[编译调试 Apache](https://wx.zsxq.com/dweb2/index/topic_detail/418885442584848)

[调试补充事项](https://wx.zsxq.com/dweb2/index/topic_detail/218882521544551)

不一定要 Ubantu，Kali 上笔者也调试成功了，最好用 VS，另外如果你想尝试用 CLion，可以参照下面的链接进行 SSH
远程调试，其余步骤都同上一样：

[Stay local, let your IDE do remote work for you! | The CLion Blog
(jetbrains.com)](https://blog.jetbrains.com/clion/2018/09/initial-remote-dev-support-clion/)

CLion 调试需要注意有 cmake 和 gdb 版本限制，最好不要下载最新版本避免还要用软链接重新下载某一指定版本，或者更新 CLion 也是可以的。

## 0x02 前置学习

为了理解漏洞原理，笔者个人认为是需要 Apache 和 PHP
一些前置知识学习的，就简单概括了并使之递进加深理解，很多点都会在分析过程中用到，行文结合了许多官方文档和自身理解整理以确保准确，如有缺漏不当之处，还请指出。

###  Apache 部署 php

众所周知，php 有五种运行模式，其中最常见的三种 CGI、FastCGI、Module 加载或者说 apache2handler 更为恰当（linux
下）。

Module 加载这种模式一般对于 Apache 而言，简单来说，就是把 PHP 作为 Apache 的一个子模块来运行，用 LoadModule
加载模块，最主要的模块就是 mod_php，漏洞实验环境配置调试也是以 LoadModule 加载 mod_proxy 的。

而 FastCGI 这个模式下会用到 PHP-FPM 这个进程管理器进行 FastCGI 管理，而非 CGI 的用 Web 服务器管理，其中的子进程叫做
PHP-CGI ， **这次漏洞的突破点 mod_proxy 就与 PHP-FPM 有关，它从 PHP 5.3.3 就成为了 PHP
的内置管理器，所以配合这个从 Apache httpd 2.4.x 推出了使用 mod_proxy 的子模块 mod_proxy_fcgi 和 PHP-FPM 部署更高性能的 PHP 运行环境。**

虽然现在明显用 Nginx+PHP-FPM 是更好的选择 🙂

###  mod_proxy 反向代理

顾名思义，这个模块与其相关模块为 Apache HTTP Server 实现代理 / 网关。

前面有说到 High-performance PHP on apache httpd 2.4.x using mod_proxy_fcgi and php-fpm 这种方式，本质就是 Apache 作为反代服务器用 mod_proxy_fcgi 这个子模块请求转发给 PHP-FPM ，而 PHP-FPM
监听的方式，也就是接收 Apache 转过去时处理 PHP 的请求的方式，有两种：

  1. TCP Socket（ip and port） 
    
        ProxyPass / http://www.example.com:port
    

  2. UDS （Unix Domain Socket） **只在Apache 2.4.7 及更高版本中支持。** 可以通过使用位于 `unix:/path/app.sock|` 前面的目标来支持使用 UDS 。例如，要代理 HTTP 并将 UDS 定位于 /home/www.socket ，应使用 `unix:/home/www.socket|http://localhost/whatever/` 。 
    
        ProxyPass / unix:/path/to/app.sock|http://example.com/app/name
    

对于反向代理而言， Apache 转发代理，也就是 Apache 发送请求给 PHP-FPM 的方式有三种，其中一种叫 ProxyPass
，这是指令，允许将远程服务器 Map 到本地服务器（反向代理 / 网关）的空间，对于不同监听方式的指令例子如上所示。

###  Apache hook 机制

说起 Apache Module 不能不提起 Apache hook，想要处理请求，要做的第一件事就是在请求处理过程中创建一个
hook，所有处理程序，就比如我们上面说到的 mod_proxy
，都会被挂接到请求过程的特定部分。服务器本身是不知道哪个模块负责处理特定请求的，所以会询问每个模块是否对给定请求感兴趣。然后，由每个模块决定是否像身份验证
/ 授权模块那样拒绝服务请求，接受服务请求或拒绝服务请求，就像下图一样。

![](https://p5.ssl.qhimg.com/t010bc527ef00965901.png)

为了使诸如 mod_example 之类的处理程序更容易知道 Client
端是否在请求我们应处理的内容，服务器具有用于向模块提示是否需要其协助的指令。其中两个是
[AddHandler](https://www.docs4dev.com/docs/zh/apache/2.4/reference/mod-mod_mime.html#addhandler) 和
[SetHandler](https://www.docs4dev.com/docs/zh/apache/2.4/reference/mod-core.html#sethandler)。

为此可以看一个例子理解，比如我们想通过创建合适的 Handler 传递，将请求强制处理为反向代理请求：

    
    
    <FilesMatch "\.php$">
        # Unix sockets require 2.4.7 or later
        SetHandler  "proxy:unix:/path/to/app.sock|fcgi://localhost/"
    </FilesMatch>
    

这个例子是使用反向代理将对 PHP 脚本的所有请求传递到指定的 FastCGI 服务器，是不是和之前 UDS 的例子很像？

一个 Module 通常是在 Handler 中创建一个 hook，例如：

    
    
    static void register_hooks(apr_pool_t *pool)
    {
        /* Create a hook in the request handler, so we get called when a request arrives */
        ap_hook_handler(example_handler, NULL, NULL, APR_HOOK_LAST);
    }
    

如上，继而就会在 example_handler 这个函数中处理请求，mod_proxy 也有这样的 Handler 。

另外还要提到的就是 request_rec 结构。

任何请求中最重要的部分是 request record 。在对处理程序函数的调用中，这由与进行的每次调用一起传递的 `request_rec*`
结构表示。该结构在模块中通常简称为 `r` ，包含模块完全处理任何 HTTP 请求并相应做出响应所需的所有信息。

![](https://p3.ssl.qhimg.com/t010148ccd01ac685da.png)

其中这个 `r->filename` 还有其他几个我们就会在分析过程中接触到。

## 0x03 分析

###  代码审计

以 Apache 2.4.48 源代码审计， **不同版本会有些出入** 。

**注意审计这部分着重看代码中的注释，笔者所写的有很大一部分解释和分析都在其中，修复的部分会标 * ，一定要看注释配合理解！**

[[Apache-SVN] Revision
1892814](https://svn.apache.org/viewvc?view=revision&revision=1892814)

直接来看修复前后的对比分析缺陷在哪，还有漏洞本质上是什么问题。

官方的函数解释看这个文档：

[Apache2: HTTP Daemon
Routine](https://ci.apache.org/projects/httpd/trunk/doxygen/group__APACHE__CORE__DAEMON.html#gaa6a7169f7d3801b11d3b113b27284dbd)

    
    
    --- httpd/httpd/trunk/modules/proxy/proxy_util.c    2021/09/02 12:33:49 1892813
    +++ httpd/httpd/trunk/modules/proxy/proxy_util.c    2021/09/02 12:37:02 1892814
    @@ -2274,8 +2274,8 @@ static void fix_uds_filename(request_rec *r, char **url){
         char *ptr, *ptr2;
         if (!r || !r->filename) return;
    
         // COND1：r->filename 前 6 个字符必须是 proxy:
         if (!strncmp(r->filename, "proxy:", 6) &&
                 // COND2：r->filename 必须有 unix: 这个字符串，但不区分大小写，这不同于 strstr
    -            (ptr2 = ap_strcasestr(r->filename, "unix:")) &&
                 // COND3：COND2 对 r->filename 进行了截取，这条是判断 unix: 这个字符串后的部分是否有 | 
    -            (ptr = ap_strchr(ptr2, '|'))) {
                  // *COND2：不区分大小写对两个字符串进行比较，也就是这里 r->filename 必须以 proxy:unix: 开头
    +            !ap_cstr_casecmpn(r->filename + 6, "unix:", 5) &&
                 // *COND3：ptr2 指 proxy:unix: 后的部分，这里判断字符串中那个是否有 | ，与 COND3 要求一致
    +            (ptr2 = r->filename + 6 + 5, ptr = ap_strchr(ptr2, '|'))) {
    
             apr_uri_t urisock;
             apr_status_t rv;
             *ptr = '\0';
    
             // 举例：ProxyPass / unix:/path/to/app.sock|http://example.com/app/name 我们来看这些参数的值
             // 这里解析给定的 uri ，填写 apr_uri_t 结构的一些字段，避免重复提取主机端口、路径这些
             rv = apr_uri_parse(r->pool, ptr2, &urisock);
             // 如果解析成功（apr_uri_parse Returns APR_SUCCESS for success or error code）
             if (rv == APR_SUCCESS) {
                 // 这里 rurl 即 redirect url 在例子中就是 http://example.com/app/name，需要重定向到的地址
                 char *rurl = ptr+1;
                 // 返回相对路径，在例子中 uds_path 就是 /path/to/app.sock
                 char *sockpath = ap_runtime_dir_relative(r->pool, urisock.path);
                 // 将 uds_path 键值对添加到 r->notes
                 apr_table_setn(r->notes, "uds_path", sockpath);
                 *url = apr_pstrdup(r->pool, rurl); /* so we get the scheme for the uds */
                 /* r->filename starts w/ "proxy:", so add after that */
                 memmove(r->filename+6, rurl, strlen(rurl)+1);
                 // 记录信息
                 ap_log_rerror(APLOG_MARK, APLOG_TRACE2, 0, r,
                         "*: rewrite of url due to UDS(%s): %s (%s)",
                         sockpath, *url, r->filename);
             }
    
             else {
                 *ptr = '|';
             }
    
         }
    }
    

结合注解，可以看出 `fix_uds_filename` 这个函数本身就是用于解析并填写 uri ，文件名标识 UDS ，然后通过管道符 `|`
后面的内容重定向到它。

对比 COND2 和 *COND2 ，我们知道这个漏洞的修复就是单纯强制要求 `proxy:unix:` 开头，COND2 我们也能看出只要是有
`unix:` 字样而且不论大小写都能被解析，显然是判定宽松出了问题，为了更好理解我们先来看 [remy🐀 在 Twitter:
“CVE-2021-40438 Apache SSRF as a one-liner./
Twitter](https://twitter.com/_mattata/status/1449020783989297167) 上的一个 poc ：

![](https://p4.ssl.qhimg.com/t014fa50f6bd09ba75c.png)

可以看到 `unix:` 后它拼接了共 7701 个字符的 A
，可以猜想这其中一定有缓冲区或者错误处理的问题，来看修复前拼接的效果，假设我们发送的请求如下，显然是让代理一个 http 请求：

    
    
    http://localhost/?unix:$(python3 -c 'print("A"*7701, end="")')|http://backend_server1:8085/
    

代理请求拼接后：

    
    
    proxy:http://localhost/?unix:$(python3 -c 'print("A"*7701, end="")')|http://backend_server1:8085/
    

这里就又因为包含 `unix:` ，满足 COND2 ， **就从 http 请求变成了有效的 UDS 代理重定向请求。**

解释到这，我们明白问题本质后，先来分析什么是我们可控的，再来从 UDS 解析过程上分析为什么要拼接将 7000 个字符才能攻击成功。

####  哪部分是可控的？

之前在前置知识学习中，笔者有提到过 mod_proxy 有它处理请求的
Handler，我们从这个函数来看哪些是我们可控的，当然，认真看了上部分内容的你，一定知道 `r->filename` 是关键。

modules/proxy/mod_proxy_http.c

    
    
    static void ap_proxy_http_register_hook(apr_pool_t *p)
    {
        ap_hook_post_config(proxy_http_post_config, NULL, NULL, APR_HOOK_MIDDLE);
        proxy_hook_scheme_handler(proxy_http_handler, NULL, NULL, APR_HOOK_FIRST);
        proxy_hook_canon_handler(proxy_http_canon, NULL, NULL, APR_HOOK_FIRST);
        warn_rx = ap_pregcomp(p, "[0-9]{3}[ \t]+[^ \t]+[ \t]+\"[^\"]*\"([ \t]+\"([^\"]+)\")?", 0);
    }
    

可以看到有两个 hook，我们来看 `proxy_http_canon` 这个 Handler，是用于处理反代请求的。

    
    
    static int proxy_http_canon(request_rec *r, char *url)
    {
    
        ...
    
        // get_url_scheme 是检查该请求是否是（h / H 开头） 再判断是否是 http / https，也就是该不该由 mod_proxy_http 处理
        // schema pass
        scheme = get_url_scheme((const char **)&url, &is_ssl);
        if (!scheme) {
            return DECLINED;
        }
        port = def_port = (is_ssl) ? DEFAULT_HTTPS_PORT : DEFAULT_HTTP_PORT;
    
        ...
    
        switch (r->proxyreq) {
        default: /* wtf are we doing here? */
        case PROXYREQ_REVERSE:
            if (apr_table_get(r->notes, "proxy-nocanon")) {
                path = url;   /* this is the raw path */
            }
            else {
                path = ap_proxy_canonenc(r->pool, url, strlen(url),
                                         enc_path, 0, r->proxyreq);
                search = r->args;
            }
            break;
        case PROXYREQ_PROXY:
            path = url;
            break;
        }
    
        if (path == NULL)
            return HTTP_BAD_REQUEST;
    
        if (port != def_port)
            apr_snprintf(sport, sizeof(sport), ":%d", port);
        else
            sport[0] = '\0';
    
        // host pass
        if (ap_strchr_c(host, ':')) { /* if literal IPv6 address */
            host = apr_pstrcat(r->pool, "[", host, "]", NULL);
        }
    
        // 最终拼接赋值给 r->filename
        r->filename = apr_pstrcat(r->pool, "proxy:", scheme, "://", host, sport,
                                  "/", path, (search) ? "?" : "", search, NULL);
        return OK;
    }
    

结合注释，可以看到最终只有 `path` 和 `search` 是我们可控的，`r->filename` 后半部分可控也恰恰是 `|` 后的后端地址。

####  UDS 解析过程

之前在代码注释中也提到过，`uds_path` 就是 `unix:` 与 `|` 之间的部分，在 poc 中就是那近 7000 的字符。

    
    
    char *sockpath = ap_runtime_dir_relative(r->pool, urisock.path);
    // 将 uds_path 键值对添加到 r->notes
    apr_table_setn(r->notes, "uds_path", sockpath);
    

先来看 `ap_runtime_dir_relative` 做了什么。

server/config.c

    
    
    // ap_runtime_dir_relative(r->pool, urisock.path)
    AP_DECLARE(char *) ap_runtime_dir_relative(apr_pool_t *p, const char *file)
    {
        char *newpath = NULL;
        apr_status_t rv;
        const char *runtime_dir = ap_runtime_dir ? ap_runtime_dir : ap_server_root_relative(p, DEFAULT_REL_RUNTIMEDIR);
    
        rv = apr_filepath_merge(&newpath, runtime_dir, file,
                                APR_FILEPATH_TRUENAME, p);
        if (newpath && (rv == APR_SUCCESS || APR_STATUS_IS_EPATHWILD(rv)
                                          || APR_STATUS_IS_ENOENT(rv)
                                          || APR_STATUS_IS_ENOTDIR(rv))) {
            return newpath;
        }
        else {
            return NULL;
        }
    }
    

可以看到调用了 apr 库的 `apr_filepath_merge` 这个函数。

apr/file_io/unix/filepath.c

    
    
    // apr_filepath_merge(&newpath, runtime_dir, file,APR_FILEPATH_TRUENAME, p)
    APR_DECLARE(apr_status_t) apr_filepath_merge(char **newpath,
                                                 const char *rootpath,
                                                 const char *addpath,
                                                 apr_int32_t flags,
                                                 apr_pool_t *p)
    {
        ...
    
        rootlen = strlen(rootpath);
        maxlen = rootlen + strlen(addpath) + 4; /* 4 for slashes at start, after
                                                 * root, and at end, plus trailing
                                                 * null */
        if (maxlen > APR_PATH_MAX) {
            return APR_ENAMETOOLONG;
        }
    
        ...
    
    }
    

`apr_filepath_merge` 这个函数简单描述就是将 `addpath` 合并到预先处理的 `rootpath` 上，在这里就是 `file`
合并到 `runtime_dir` 。

对省略的部分解释一下，这里的 `flags` 因为是 `APR_FILEPATH_TRUENAME`（这是合并的规则），流程大概就是检查 `file` 这个
`addpath` 是否包含一些平台不支持的通配符（ `*` 、`?`），其他情况是处理绝对 / 相对路径的一些规则。

可以看到我们截取出来的部分，如果 `maxlen` 也就是 `rootpath` 和 `addpath` 长度 + 4 如果大于
`APR_PATH_MAX`（ linux 与 win 不同，是4096），就会返回一个 `APR_ENAMETOOLONG` 的错误，这个错误赋值给
`rv` ，在 `ap_runtime_dir_relative` 中是最后会进入 else 分支 **return NULL** 的。

之后在 modules/proxy/proxy_util.c 中 `ap_proxy_determine_connection` 确定后端主机名和端口。

    
    
    PROXY_DECLARE(int)
    ap_proxy_determine_connection(apr_pool_t *p, request_rec *r,
                                  proxy_server_conf *conf,
                                  proxy_worker *worker,
                                  proxy_conn_rec *conn,
                                  apr_uri_t *uri,
                                  char **url,
                                  const char *proxyname,
                                  apr_port_t proxyport,
                                  char *server_portstr,
                                  int server_portstr_size)
    {
    
        ...
    
        // 这里是不是很熟悉？
        // 还记得之前有这句 apr_table_setn(r->notes, "uds_path", sockpath); 将 uds_path 键值对添加到 r->notes 吗？
        // 这里就是在检验 uds_path 的值
        uds_path = (*worker->s->uds_path ? worker->s->uds_path : apr_table_get(r->notes, "uds_path"));
        if (uds_path) {
            if (conn->uds_path == NULL) {
                /* use (*conn)->pool instead of worker->cp->pool to match lifetime */
                conn->uds_path = apr_pstrdup(conn->pool, uds_path);
            }
            if (conn->uds_path) {
                ap_log_rerror(APLOG_MARK, APLOG_DEBUG, 0, r, APLOGNO(02545)
                             "%s: has determined UDS as %s",
                             uri->scheme, conn->uds_path);
            }
            else {
                /* should never happen */
                ap_log_rerror(APLOG_MARK, APLOG_DEBUG, 0, r, APLOGNO(02546)
                             "%s: cannot determine UDS (%s)",
                             uri->scheme, uds_path);
    
            }
            /*
             * In UDS cases, some structs are NULL. Protect from de-refs
             * and provide info for logging at the same time.
             */
            if (!conn->addr) {
                apr_sockaddr_t *sa;
                apr_sockaddr_info_get(&sa, NULL, APR_UNSPEC, 0, 0, conn->pool);
                conn->addr = sa;
            }
            conn->hostname = "httpd-UDS";
            conn->port = 0;
        }
        else{
    
            ...
    
        }
    
        ...
    
    }
    

对照注释，如果我们发送超长字符，导致 `uds_path` 为 `NULL` 的话，就会进入 else 分支，它们具体处理大致是这样一个情况：

    
    
    if (uds_path) { 
        // Prepare UDS request…
        // 用 UDS 继续通信
    }
    else {
        // Prepare standard proxy request…
        // 转而用 TCP 通信
    }
    

这里结合所有内容就可以看出来了，进入 else 分支把请求最终解释成了标准代理请求如 http://<SSRF_TARGET> ，就导致了可以向内部网络任意
Apache 服务器发送请求，请求执行成功，SSRF 触发。

###  漏洞利用

有时会报 503 的错误，多试几次就行了。

![](https://p0.ssl.qhimg.com/t0185c0a7e857122241.png)

## 0x04 参考

[Building a POC for CVE-2021-40438 – Firzens Blog](https://firzen.de/building-a-poc-for-cve-2021-40438)

[Apache SSRF: an all-you-can-eat reverse proxy > Cydrill Software
Security](https://cydrill.com/owasp/apache-ssrf-an-all-you-can-eat-reverse-proxy/)

[Apache mod_proxy SSRF（CVE-2021-40438）的一点分析和延伸 | 离别歌
(leavesongs.com)](https://www.leavesongs.com/PENETRATION/apache-mod-proxy-ssrf-cve-2021-40438.html#)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **snovving** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263175](/post/id/263175)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE](/tag/CVE)
  * [代码审计](/tag/代码审计)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d65b2fc371a68f8.png) snovving

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

