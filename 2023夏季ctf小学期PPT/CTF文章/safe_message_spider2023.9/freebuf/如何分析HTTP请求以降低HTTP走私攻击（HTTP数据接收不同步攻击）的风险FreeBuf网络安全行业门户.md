![](https://image.3001.net/images/20220206/1644147894_61ffb4b645cb5f9caba25.png!small)  

## 写在前面的话

HTTP/1.1自1991年至2014年，已经走过了一段很长的发展历程：

  * [ _HTTP/0.9_](https://www.w3.org/Protocols/HTTP/AsImplemented.html)– 1991
  * [ _HTTP/1.0_](https://tools.ietf.org/html/rfc1945)– 1996
  * HTTP/1.1
  * [ _RFC 2068_](https://tools.ietf.org/html/rfc2068)– 1997
  * [ _RFC 2616_](https://tools.ietf.org/html/rfc2616)\- 1999
  * [ _RFC 7230_](https://tools.ietf.org/html/rfc7230)\- 2014

这也就意味着，互联网中各种各样的服务器和客户端，可能会存在很多安全问题，这也会给HTTP走私攻击（HTTP数据接收不同步攻击）创造了机会。

![](https://image.3001.net/images/20220206/1644147908_61ffb4c4d7923d35eca9f.png!small)  

遵循最新的RFC建议似乎很简单。然而，对于已经存在一段时间的大型系统，它可能会带来很多在系统可用性方面令人无法接受的影响。

http_desync_guardian这个工具库便应运而生，该工具可以帮助广大研究人员分析HTTP请求，以防止HTTP走私攻击（HTTP数据接收不同步攻击）的发生，同时还能够兼顾安全性和可用性。该工具可以将请求进行
_分类_，并并提供针对每一层的处理建议。

该工具既可以分析原始的HTTP请求Header，也可以对那些已经被HTTP引擎分析过的请求数据进行二次分析。

## 工具特性

> 1、服务的统一性是关键。这意味着请求分类、日志记录和度量必须在后台进行，并使用最少的可用设置（例如，日志文件目的地址）。
>
> 2、关注可审查性。测试套件不需要关于库/编程语言的知识，而只需要关于HTTP协议的知识即可。因此，它很容易审查、贡献代码和重复使用。
>
> 3、安全性对于用户来说是最重要的。
>
> 4、轻量级，开销非常小，并且处理请求不需要额外开销。

## 支持的HTTP版本

该工具主要针对的是HTTP/1.1，具体可以参考提供的覆盖测试用例。

HTTP/1.1的前身不支持连接重用，这限制了HTTP去同步的机会，但是一些代理可能会将此类请求升级到HTTP/1.1，并重新使用后端连接，这可能会导致恶意HTTP/1.0请求。这也就是为什么我们选择使用与HTTP/1.1相同的标准来分析它们。对于其他协议版本，可以参考这篇【[
_文档_](https://github.com/aws/http-desync-guardian/blob/main/docs%E3%80%81)】。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/aws/http-desync-guardian.git

## C代码使用

这个工具库主要使用的是C/C++开发的HTTP引擎，工具安装配置方法如下：

1、安装 _cbindgen_：

    
    
    cargo install --force cbindgen

2、生成Header文件：

 **C：**

    
    
    cbindgen --output http_desync_guardian.h --lang c

 **C++：**

    
    
    cbindgen --output http_desync_guardian.h --lang c++

3、运行下列命令，其中相关代码位于“./target/release/libhttp_desync_guardian.*”文件：

    
    
    cargo build --release
    
    
    #include "http_desync_guardian.h"
    
     
    
    /*
    
     * http_engine_request_t - already parsed by the HTTP engine
    
     */
    
    static int check_request(http_engine_request_t *req) {
    
        http_desync_guardian_request_t guardian_request = construct_http_desync_guardian_from(req);
    
        http_desync_guardian_verdict_t verdict = {0};
    
     
    
        http_desync_guardian_analyze_request(&guardian_request, &verdict);
    
     
    
        switch (verdict.tier) {
    
            case REQUEST_SAFETY_TIER_COMPLIANT:
    
                // The request is good. green light
    
                break;
    
            case REQUEST_SAFETY_TIER_ACCEPTABLE:
    
                // Reject, if mode == STRICTEST
    
                // Otherwise, OK
    
                break;
    
            case REQUEST_SAFETY_TIER_AMBIGUOUS:
    
                // The request is ambiguous.
    
                // Reject, if mode == STRICTEST
    
                // Otherwise send it, but don't reuse both FE/BE connections.
    
                break;
    
            case REQUEST_SAFETY_TIER_SEVERE:
    
                // Send 400 and close the FE connection.
    
                break;
    
            default:
    
                // unreachable code
    
                abort();
    
        }
    
    }

## 许可证协议

本项目的开发与发布遵循Apache-2.0开源许可证协议。

## 项目地址

 **http-desync-guardian：** 【[ _GitHub传送门_](https://github.com/aws/http-desync-guardian)】

## 参考资料

[ _https://github.com/aws/http-desync-guardian/blob/main/docs#request-classification_](https://github.com/aws/http-desync-guardian/blob/main/docs#request-classification)

[ _https://github.com/aws/http-desync-guardian#security-issue-notifications_](https://github.com/aws/http-desync-guardian#security-issue-notifications)

[ _https://github.com/aws/http-desync-guardian/blob/main/tests_](https://github.com/aws/http-desync-guardian/blob/main/tests)

[ _https://github.com/eqrion/cbindgen#cbindgen-----_](https://github.com/eqrion/cbindgen#cbindgen-----)

[ _https://github.com/aws/http-desync-guardian/blob/main/misc/demo-c_](https://github.com/aws/http-desync-guardian/blob/main/misc/demo-c)

[ _https://github.com/aws/http-desync-guardian/blob/main/misc/demo-nginx_](https://github.com/aws/http-desync-guardian/blob/main/misc/demo-nginx)

[ _http://aws.amazon.com/security/vulnerability-reporting/_](http://aws.amazon.com/security/vulnerability-reporting/)

