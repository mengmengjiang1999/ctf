## 0x01 背景

**最近HackerOne公布了Nginx内存内容泄漏的问题，如果说内存内容泄漏的问题是个Bug的话，那这个Bug是个比较典型的程序没有对输入异常数据做适当的过滤处理而形成的。**

现实中程序对有限正常系用例的数据处理是定量的，对无线的异常数据会出现处理的盲点，如果什么数据都可以作为一个可接受输入程序的输入数据，那一个程序没有处理好异常系的非业务数据，就可能造成逻辑Bug，或是漏洞。

这篇文章的重点，不局限于Bug问题的代码是如何在异常数据之前出现问题，如何复现Bug，我们还要通过社区给出的防护方案，学习如何构建安全的代码，去过滤那些非法的数据输入。

## 0x02 安全测试

安全测试很多时候，是构造一个被测程序意料之外的异常输入数据，让程序出错，或产生超出正常用户预期的结果。

一个程序功能是为了实现用户某些用例场景的处理，而安全测试很多时候，提供给程序输入的数据，并不一定是用户正常业务使用的正常数据。安全测试提供的数据，目的并不是让程序完成正常用户功能作处理，而是让程序暴露安全问题。

测试人员：测试的是程序是否能按功能需求实现功能。

安全测试人员：测试的是程序在收到异常系数据时，是否出错，是否可以利用程序出错，取得系统更大的权限。

这次问题的产生，一种在有问题的Nginx的配置基础，构造有问题的访问请求，造成Nginx的Rewrite功能出问题。另一种是，安全测试人员在构造一个HTTP请求时，在Header部分注入一些非法的字符，正常的浏览器HTTP请求一般不会有这些奇怪的数据。

### Nginx

Nginx的问题和%00有关系，在请求当中加入%00，造成内存内容泄漏。

    
    
    curl localhost:8337 -d "url=%00asdfasdfasdfasdfasdfasdfasdfasdf" -vv
    

在静态的rewrite配置中加特殊符号，^@是空字节。

    
    
    location ~ /memleak {
        rewrite ^.*$ "^@asdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdasdf";
    }
    
    
    
    curl localhost:8337/memleak -vv
    
    ...Location: [http://localhost:8337/WjWj](http://localhost:8337/WjWj)...
    

WjWj就是随机的内存数据。

### OR

OR的问题是，Lua程序员在写Lua相关的URI设置逻辑，或是有设定头数据动作时，不考虑过滤用户请求Header中异常数据，这个数据的会被传递给低层的Nginx
C代码，最直接相关的代码就是调用的ngx.req.set_uri()这个函数，如果这个函数也不做Header数据的判断，继续执行下面的逻辑，就会出现问题。

    
    
    location ~ /memleak { rewrite_by_lua_block { ngx.req.read_body(); local args, err = ngx.req.get_post_args(); ngx.req.set_uri( args["url"], true ); }}
    
    location / { root html; index index.html index.htm;}
    

## 0x03 复现问题

从朋友那得到漏洞消息后，测试了一些低版本的Nginx，发现问题的确是可以复现的，从漏洞公开时间表，最后公开这个问题的时间节点是3.18号，发现者已经告知的了Nginx和OR的厂商相关信息，并公布了这个问题。

新的版本Nginx修复了如果没有问题的话，但如果企业单位还在用老版本Nginx就会出现问题，对于正常的Nginx服务中用到Rewirte功能的机率还是很高的。

如果你的Nginx服务中用了有问题的Rewrite的配置，或是在Nginx中对应使用的Nginx
Lua服务代码中调用了ngx.req.set_uri()这个函数，会触发的这个问题逻辑代码的执行，如果没有相关问题Rewrite的配置和API的调用，或是过滤过异常Header数据，不一定能复现问题的。

给这个漏洞定位是中低危漏洞。一般的Lua在设置URI时大多数不会还考虑过滤Header数据，但如果Lua程序是一个
WAF程序，其实应该有对非法Header数据的检查。

### Nginx问题

Bug问题原理，主要还是对应的函数没有对非法的HTTP数据做过滤, Hacker One给出了Nginx的问题代码的。

看参考连接：<https://hackerone.com/reports/513236>

漏洞Bug复现的条件：

这个Bug的被归为中低危漏洞，原因也是因为想利用漏洞需要前提条件成立。

> A).低版本Nginx或Openresty系统服务，在nginx.conf中配置有问题的Rewrite的。
>
> B).低版本Nginx或Openresty系统服务，在nginx.conf中配置的Lua代码，并且代码调用了ngx.req.set_uri()函数。

## 0x04 测试漏洞

HackerOne给出复现例子。

Nginx 目录遍历

    
    
    location ~ /rewrite { rewrite ^.*$ $arg_x;}
    
    location / { root html; index index.html index.htm;}
    

^.*$匹配所有的路径映射到入口文件，$arg_x取变量x的值，这种静态的rewrite设定，就会出现目录遍历，如果老版本Nginx中配置文件中有这种代码就有问题。

    
    
    curl localhost:80/rewrite?x=/../../../../../../../etc/passwd
    

测试：

如果可以显示出系统文件/etc/passwd中的内容，实现目录遍历达成。

    
    
    location ~ /memleak { rewrite ^.*$ "^@asdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdasdf";}
    
    location / { root html; index index.html index.htm;}
    

测试：

    
    
    curl localhost:8337/memleak -vv...Location: [http://localhost:8337/WjWj](http://localhost:8337/WjWj)...
    

WjWj是随机的泄漏的内存内容数据， /WjWj这种路由也不是用户提前正常设置的。

## 0x05 修复方案发布

OR社区今天发布新版本，修复了这个问题。相对造成这个问题的代码，也比较关注这个问题的修复方案。对于安全测试来说的，理论和URI相关的函数，其实都可以关注一下，如果是WAF系统，这些地方处理的是否全面，会决定WAF是否可能被绕过。

Nginx
C级别的这些与URI、HTTP输入数据直接相关的代码，最应该被关注，因为这些函数和对请求中异常数据的过滤息息相关，一旦没有过滤充分就可能会引起问题。

WAF某些时候是在给，被保护的生产业务做过滤，让生产业务专注于自己的功能，由WAF处理攻击者的业务数据。一旦，业务和WAF都没有对非法数据做检查，这些数据就会交给低层的Nginx
C来处理，如果C也没有检查，再向后执行，原本期待正常业务数据的C代码，面对异常输入时，没有过滤好就会出错。

### 修复方案

之前的漏洞解析，更多的关注的造成问题的代码，而作为一个代码开发人员来说，还应该关注，如果写出可靠的安全代码，我们学习回顾一下，最新发布的OR是如何安全过滤攻击者注入数据的处理。

经老师提醒，代码方案有初期版和终期版，经历了最开始没安全检查，到有安全检查的过程，代码如下：

    
    
    static ngx_inline size_t  ngx_int_t ngx_http_lua_check_header_safe(ngx_http_request_t *r, u_char *str,
    ngx_http_lua_safe_header_value_len(u_char *str, size_t len)      size_t len);
    {  
        size_t i;
    
        for (i = 0; i < len; i++, str++) {  
            if (*str == '\r' || *str == '\n') {  
                return i;  
            }  
        }
    
        return len;  
    }
    

被删除的一个版本的安全处理函数，在计算头值长度的时候，遇到换行回车就停止长度计数。

新发布的代码中加入安全检查函数，代码如下。

    
    
    ngx_inline ngx_int_t
    ngx_http_lua_check_header_safe(ngx_http_request_t *r, u_char *str, size_t len)
    {
        size_t           i, buf_len;
        u_char           c;
        u_char          *buf, *src = str;
    
                         /* %00-%1F, %7F */
    
        static uint32_t  unsafe[] = {
            0xffffffff, /* 1111 1111 1111 1111  1111 1111 1111 1111 */
    
                        /* ?>=< ;:98 7654 3210  /.-, +*)( '&%$ #"!  */
            0x00000000, /* 0000 0000 0000 0000  0000 0000 0000 0000 */
    
                        /* _^]\ [ZYX WVUT SRQP  ONML KJIH GFED CBA@ */
            0x00000000, /* 0000 0000 0000 0000  0000 0000 0000 0000 */
    
                        /*  ~}| {zyx wvut srqp  onml kjih gfed cba` */
            0x80000000, /* 1000 0000 0000 0000  0000 0000 0000 0000 */
    
            0x00000000, /* 0000 0000 0000 0000  0000 0000 0000 0000 */
            0x00000000, /* 0000 0000 0000 0000  0000 0000 0000 0000 */
            0x00000000, /* 0000 0000 0000 0000  0000 0000 0000 0000 */
            0x00000000  /* 0000 0000 0000 0000  0000 0000 0000 0000 */
        };
    
        for (i = 0; i < len; i++, str++) {
            c = *str;
            if (unsafe[c >> 5] & (1 << (c & 0x1f))) {
                buf_len = ngx_http_lua_escape_log(NULL, src, len);
                buf = ngx_palloc(r->pool, buf_len);
                if (buf == NULL) {
                    return NGX_ERROR;
                }
    
                ngx_http_lua_escape_log(buf, src, len);
    
                ngx_log_error(NGX_LOG_ERR, r->connection->log, 0,
                              "unsafe byte \"0x%uxd\" in header \"%*s\"",
                              (unsigned) c, buf_len, buf);
    
                ngx_pfree(r->pool, buf);
    
                return NGX_ERROR;
            }
        }
    
        return NGX_OK;
    }
    

最新的防护方案是，当发现请求中有非法数据，释放空间然后抛出错误异常。检查也从过去的没到检查，判断回车换行计算头长度，变成直接抛出异常错误。

WAF系统一个主要的功能就是过滤用户非法请求数据，特别是基于Nginx +
Lua的WAF方案更是这样，而如果只是单纯检查过滤请求Header中的数据，其实小语言DSL，更简洁，比Lua还简洁。

    
    
    req-header(“Content-Type”) contains “multipart/form-data”,
    req-header(“Content-Type”) !contains rx{^multipart/form-data[\s\S]+} =>
    

## 0x06 总结

在Nginx过去历史发展过程，不只是这一次出现过类似%00的问题，以后安全测试人员和黑客，还会通过构建类似这种的异常数据输入，敲开系统的门。安全生态中的人和系统，也会在不断发生的威胁事件中，演进彼此的技法，在存量和增加的代码中，发现安全问题，解决安全问题，动态的变化。

最新OR版本发行，解决了文中提到的问题：<https://openresty.org/en/ann-1015008003.html>

 ***本文原创作者：糖果L5Q，本文属FreeBuf原创奖励计划，未经许可禁止转载**

