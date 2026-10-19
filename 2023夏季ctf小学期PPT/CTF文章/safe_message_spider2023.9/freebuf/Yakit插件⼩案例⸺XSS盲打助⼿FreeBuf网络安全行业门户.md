## 01 插件功能简单介绍

应key⼦哥要求，来分享点yakit的小小小姿势

![](https://image.3001.net/images/20220121/1642751045_61ea644518b76867090aa.jpg!small)![1642751072_61ea64602074e31399031.jpg!small](https://image.3001.net/images/20220121/1642751072_61ea64602074e31399031.jpg!small)

⽤yakit写mitm插件真的是比burp简单太太太多了，简化了很多繁琐的内容，⽐如画ui，可以真正做到让⽤户专注于插件的逻辑，⽽不是想着怎么画ui等⼀些与功能⽆关的东⻄。

⼀步⼀步来吧，⾸先我们创建⼀个新插件，依次点击插件商城->新插件

![1642751094_61ea64765010d8f95c247.jpg!small](https://image.3001.net/images/20220121/1642751094_61ea64765010d8f95c247.jpg!small)

接着选择MITM模块

![1642751128_61ea649854d127b401bc8.jpg!small](https://image.3001.net/images/20220121/1642751128_61ea649854d127b401bc8.jpg!small)

填好相关的表单后，点击创建新的Yak模块，因为我们这⾥是XSS盲打插件，需要⼀个盲打的 Payload，所以需要用户设置⼀个参数，可以在增加参数⾥⾯找到

![1642751142_61ea64a67bc429d08dbab.jpg!small](https://image.3001.net/images/20220121/1642751142_61ea64a67bc429d08dbab.jpg!small)

点击完创建新的Yak模块后到插件商店⻚⾯就可以看到新加的这个插件了，点击修改插件，然后再 点击⼤屏模式就可以开始开始写插件相关的代码逻辑了

![1642751164_61ea64bc93ef3d0bbba28.jpg!small](https://image.3001.net/images/20220121/1642751164_61ea64bc93ef3d0bbba28.jpg!small)

接下来就是本⽂的重点了。进入到内置的编辑器后可以看到作者给出了⼀个模板，其中`yakit_output(MITM_PARAMS)`代表打印插件参数，可以点右上角的调试按钮进行调试。

![1642751179_61ea64cbb6d31a3834456.jpg!small](https://image.3001.net/images/20220121/1642751179_61ea64cbb6d31a3834456.jpg!small)

填好参数后点击提交

可以看到插件给我们输出了⼀个日志信息，也就是说我们可以通过 MITM_PARAMS[key] （这⾥的
key取决于外面设置参数时所填写的值）来获取参数内容（以当前插件来说就是获取XSS盲打⽤的Payload）

![1642751268_61ea6524ac1064655f714.jpg!small](https://image.3001.net/images/20220121/1642751268_61ea6524ac1064655f714.jpg!small)

紧接着往下看，模板内定义了⼀个__test__函数，这个函数只会在调试的时候运⾏，也就是说这个插件在正式插⼊到MITM功能的时候是不会运⾏__test__函数的，那么我们就可以在这⾥⾯写测试⽤的逻辑

    
    
    __test__ = func() {results, err := yakit.GenerateYakitMITMHooksParams("GET", "https://example.com")if err != nil {return}isHttps, url, reqRaw, rspRaw, body = resultsmirrorHTTPFlow(results...)mirrorFilteredHTTPFlow(results...)mirrorNewWebsite(results...)mirrorNewWebsitePath(results...)mirrorNewWebsitePathParams(results...)}

`__test__`里面调用的`mirror*`函数（这里是模拟一下调用，在MITM中的话会自动hook到这些函数上）其实是一些钩子函数，分别对应了五种情况。具体会在什么时候被调用，作者的注释也写得非常完善。

    
    
      
    
    
    
    # mirrorHTTPFlow 会镜像所有的流量到这里，包括 .js / .css / .jpg 这类一般会被劫持程序过滤的请求
    mirrorHTTPFlow = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {
        
    }
    
    # mirrorFilteredHTTPFlow 劫持到的流量为 MITM 自动过滤出的可能和 "业务" 有关的流量，会自动过滤掉 js / css 等流量
    mirrorFilteredHTTPFlow = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {
        
    }
    
    # mirrorNewWebsite 每新出现一个网站，这个网站的第一个请求，将会在这里被调用！
    mirrorNewWebsite = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {
        
    }
    
    # mirrorNewWebsitePath 每新出现一个网站路径，关于这个网站路径的第一个请求，将会在这里被传入回调
    mirrorNewWebsitePath = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {
        
    }
    
    # mirrorNewWebsitePathParams 每新出现一个网站路径且带有一些参数，参数通过常见位置和参数名去重，去重的第一个 HTTPFlow 在这里被调用
    mirrorNewWebsitePathParams = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {
        
    }

了解得差不多了我们就可以写这个XSS盲打小助手插件相关的代码了。

## 02 XSS盲打小助手

我们的只需要用到最后一个钩子，也就是每当出现一个新的参数的时候，就会调用这个函数。

    
    
    mirrorNewWebsitePathParams = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {}

使用fuzz模块构造一个新请求

    
    
    freq, err := fuzz.HTTPRequest(req, fuzz.https(isHttps))die(err)

接着遍历一下所有的参数

    
    
    for _, param := range freq.GetCommonParams() {yakit_output(param.Name())}

然后我们写好一个`__test__`函数

    
    
    __test__ = func() {isHttps = false// 构建一个测试请求rspRaw, reqRaw, err := poc.HTTP(`POST /hello?test=a HTTP/1.1Host: 127.0.0.1:8080`, poc.https(isHttps))die(err)// 从响应报文里拿bodybody, _ := str.ExtractBodyFromHTTPResponseRaw(rspRaw)// 从请求报文里拿urlurl, _ := str.ExtractURLFromHTTPRequestRaw(reqRaw, isHttps)results = [isHttps, url, reqRaw, rspRaw, body]mirrorHTTPFlow(results...)mirrorFilteredHTTPFlow(results...)mirrorNewWebsite(results...)mirrorNewWebsitePath(results...)mirrorNewWebsitePathParams(results...)}

点击调试并输入插件参数后

![1642751517_61ea661d01d2af7f0503d.jpg!small](https://image.3001.net/images/20220121/1642751517_61ea661d01d2af7f0503d.jpg!small)

可以看到我们的url参数被输出了，并且这个参数是有一个`Fuzz`方法的([Yak
Fuzz库教程](https://www.yaklang.io/docs/buildinlibs/lib_fuzz))，我们试着把插件参数放入到`Fuzz`方法中，并且再调用`Show`方法看一下。

    
    
    for _, param := range freq.GetCommonParams() {param.Fuzz(MITM_PARAMS["payload"]).Show()}

![1642751576_61ea6658cf995aa96ce52.jpg!small](https://image.3001.net/images/20220121/1642751576_61ea6658cf995aa96ce52.jpg!small)

在终端里面可以看到请求的原文，yak的Fuzz库已经帮我们构造好请求了，我们只需要发送出去即可

    
    
    for _, param := range freq.GetCommonParams() {param.Fuzz(MITM_PARAMS["payload"]).Exec(httpool.https(isHttps))}

然后我们就完成了一个最最最简单的插件的编写了，是的你没听错就是这么方便。当然你还可以再加一些细节，比如记录一下测试了多少个参数了。

    
    
    testParamNum := 0# mirrorNewWebsitePathParams 每新出现一个网站路径且带有一些参数，参数通过常见位置和参数名去重，去重的第一个 HTTPFlow 在这里被调用mirrorNewWebsitePathParams = func(isHttps /*bool*/, url /*string*/, req /*[]byte*/, rsp /*[]byte*/, body /*[]byte*/) {freq, err := fuzz.HTTPRequest(req, fuzz.https(isHttps))die(err)for _, param := range freq.GetCommonParams() { testParamNum += 1yakit_status("已测试参数数量", testParamNum)param.Fuzz(MITM_PARAMS["payload"]).Exec(httpool.https(isHttps))}}

最后的效果：

![1642751656_61ea66a8881c5ca434e4e.jpg!small](https://image.3001.net/images/20220121/1642751656_61ea66a8881c5ca434e4e.jpg!small)

并且，`freq.GetCommonParams()`还帮忙把POST请求时`Content-Type`为JSON的情况也考虑到了。

![1642751672_61ea66b86e0cfb438f31b.jpg!small](https://image.3001.net/images/20220121/1642751672_61ea66b86e0cfb438f31b.jpg!small)

这意味着如果在MITM中遇到了JSON格式的POST正文，yak也会解析其中的参数（目前只会解析一层的数据，但是作者说将来会更新到可以解析更深的嵌套json格式！！），这一点是在burp不容易做到的。只能说`yaklang.io`牛皮！

## 03 END

感谢奶权大佬为我们提供插件小案例以及帮我们宣传~感兴趣的大佬们可以下载yakit感受一下，
稍后大佬会把插件更新，大家可以右上角“更新Yakit插件仓库”使用XSS盲打插件，或者根据以上介绍自建插件~

Yakit下载地址：https://github.com/yaklang/yakit

进群与大佬们交流请添加微信~

![1642752066_61ea6842ca14a66b9b3a2.jpg!small?1642752066324](https://image.3001.net/images/20220121/1642752066_61ea6842ca14a66b9b3a2.jpg!small?1642752066324)

