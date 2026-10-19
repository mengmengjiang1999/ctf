## 0x01 JSONP劫持简介

JSONP利用
script标签的跨域能力实现跨域数据的访问。请求动态生成的JS脚本同时带一个callback函数名作为参数。服务端收到请求后，动态生成脚本产生数据，并在代码中以产生的数据为参数调用callback函数。

![](https://image.3001.net/images/20190725/15640407598795.png!small)

JSONP劫持，就是在受害不知情的情况下，访问了攻击者的网站，攻击者通过JSONP接口获取用户在其它网站的敏感信息。

因此通常用做：

  * 敏感信息泄露引发的精准诈骗。

  * 防守方的溯源能力之一，如在蜜罐中获取攻击者画像。

## 0x02 AST简介

AST (Abstract Syntax Tree，抽象语法树)
是源代码语法结构的一种抽象表示。它以树状的形式表现编程语言的语法结构。因此相同含义的代码，即使在不同形式的实现方式下，在AST层面是统一的。

![](https://image.3001.net/images/20210110/1610258883_5ffa99c3a90728749cd18.png!small)

在 AST 层面的统一和一致，是传统的正则匹配所做不到的。使我们可以很轻易的解决下面几种情况：

    
    
    callback({"username":"xray"});
    callback({"data": {username:"xray"}});
    /*aa*/ window.cb && window.cb({"username":"xray"})
    callback([{"info": {"username": "array"}}])
    cb('  {"username":"xray"}  ')
    a={"username": "xray"}; cb({"s": a})

## 0x03 JSONP漏洞挖掘

Koalr师傅的分享非常好 <https://koalr.me/post/a-tour-of-xray/>。

手工挖掘JSONP漏洞时，主要分为以下几步：

  1. 找jsonp接口

  2. 检查响应是否包含敏感信息

  3. 绕referer

在做自动化挖掘时，我们应该主要考虑以下几个问题：

  1. 优秀的爬虫(使用crawlergo)

  2. 筛出js资源：通过content-type即可判断。参考chrome。<https://github.com/chromium/chromium/blob/fc262dcd403c74cf3e22896f32d9723ba463f0b6/third_party/blink/common/mime_util/mime_util.cc#L42>
    
        const char* const kSupportedJavascriptTypes[] = {
        "application/ecmascript",
        "application/javascript",
        "application/x-ecmascript",
        "application/x-javascript",
        "text/ecmascript",
        "text/javascript",
        "text/javascript1.0",
        "text/javascript1.1",
        "text/javascript1.2",
        "text/javascript1.3",
        "text/javascript1.4",
        "text/javascript1.5",
        "text/jscript",
        "text/livescript",
        "text/x-ecmascript",
        "text/x-javascript",
    };

  3. 解析js类型资源，检查query中的每个key，是否满足jsonp的特征。正则大法好：
    
        (?m)(?i)(callback)|(jsonp)|(^cb$)|(function)

  4. referer配置为同域，请求js获取响应。

  5. 将JSONP响应解析成AST，如果生成的AST满足以下条件即可认定存在JSONP漏洞。

一、Callee.Name == callback函数名

二、检查是否存在敏感信息：递归遍历AST
获取所key和value，是否满足满足正则(?m)(?i)(uid)|(userid)|(user_id)|(nin)|(name)|(username)|(nick)，且value不为空

  6. 替换Referer后再请求一次，重新验证步骤5。

## 0x04 工具使用方式

通过golang实现了以上逻辑：<https://github.com/jweny/check_jsonp_based_on_ast>

本组件未单独提供爬虫，须结合爬虫使用（推荐crawlergo），将爬虫的js资源直接用工具检测即可。

项目中提供了一个jsonp的漏洞环境，如需自取。

入参：js uri

返回：是否存在漏洞（bool型，true为存在漏洞），err

例：

    
    
    result, err := CheckSenseJsonp("http://127.0.0.1/jsonp_env/getUser.php?id=1&jsoncallback=callbackFunction")

## 0x05 参考链接

<https://www.codercto.com/a/65644.html>

<https://koalr.me/post/a-tour-of-xray/>

