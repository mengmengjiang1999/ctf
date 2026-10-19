## 使用场景

在我们渗透过程在，经常会发现没有验证码，也没有登录次数限制，但是用户名密码都是加密的，当然不限于账号密码，其他的fuzz测试加密也是可以使用，至于怎么用自己打开脑洞思考，在这里我就介绍下插件工具。

例如这样：

![](https://image.3001.net/images/20200902/1599029538.png!small)

这样：

![](https://image.3001.net/images/20200902/1599029547.png!small)【图片】

还有这种验证码可复用的：

![](https://image.3001.net/images/20200902/1599029554.png!small)

如果只是md5加密或者hash，burp的Intruder模块自带加密爆破功能，但是如果是自定义的加密方式，或者多层md5此时就没法直接爆破了，就需要用到插件。

## 插件简介

这里我们会提到两款插件，jsEncrypter与BurpCrypto。BurpCrypto跟jsEncrypter差不多，相当于是个升级版，不用依赖phantomjs。文末附GitHub下载地址。

 **jsEncrypter：**

此插件使用phantomjs启动前端加密函数对数据进行加密，phantomjs会返回加密结果传给burp。因此此插件需要启动phantomjs开启服务，burp去读取结果。

 **BurpCrypto** ：

不用单独启用phantomjs，直接在burp插件页面选择AES加密，传入AES key与AES
value即可。如果是其他的加密可直接把加密函数复制进去就可以了。

jsEncrypter使用:

jsEncrypter界面![](https://image.3001.net/images/20200902/1599029619.png!small)

打开jsEncrypter的练习环境![](https://image.3001.net/images/20200902/1599029626.png!small)

配置加密函数![](https://image.3001.net/images/20200902/1599029638.png!small)

phantomjs_server.js这个是配置文件，里面可以自定义一下东西。首先要配置加密js的函数路径，然后配置调用加密函数并把结果返回到newpayload，其它的默认就好不用管。

虽然环境里面都有现成的，但是我这里顺便提一下在前端找加密函数。毕竟不可能每次都是能有现成的用，授人鱼不如授人以渔。

![](https://image.3001.net/images/20200902/1599029646.png!small)![](https://image.3001.net/images/20200902/1599029654.png!small)

这是靶场前端源码，这里我们可以看到选择的md5对于的就是值为1，调用的是hex_md5()函数，上面加载了很多js，真实环境我们就在这些js里面去搜索这个函数，出现在哪个js里面就把整个js保存下来，当然也有多个js处理的，都给他保存下来。但是我们在phantomjs_server.js里面就需要引用多个js了。（^-^这里有点废话了^-^）

接下来就是启动phantomjs了。

    
    
    phantomjs.exe phantomjs_server.js

然后点击Test测试看生成加密结果对不。

![](https://image.3001.net/images/20200902/1599029670.gif!small)

最后在Intruder模块Payload Processing中选择此模块就可以使用了

位置：Payload Processing – Add – Invoke Burp extension – jsEncrypter

一个扩展小知识（多次md5及加其它字符加密）

直接在phantomjs_server.js中写出调用md5加密函数处理后再按需处理。

![](https://image.3001.net/images/20200902/1599029714.png!small)

## BurpCrypto使用

此插件可以快捷使用AES、RSA等加密，但由于RSA环境有问题，没法显示。还是拿md5环境来演示吧，

把整个加密js复制进插件，在Js Method
Name中填写需要调用的函数即可。然后保存即可。![](https://image.3001.net/images/20200902/1599029733.png!small)

在Intruder中选择BurpCrypto保存的对应加密模块。![](https://image.3001.net/images/20200902/1599029742.png!small)![](https://image.3001.net/images/20200902/1599029749.png!small)

## 总结

上面两个插件功能上都差不多，看个人爱好更喜欢使用哪一个。当然这里再说一次，这个工具不仅限于爆破账号密码，一些其他的fuzz测试也是可以使用，比如短信轰炸等。

下载地址

jsEncrypter：[https://github.com/c0ny1/jsEncrypter](https://github.com/c0ny1/jsEncrypte)

BurpCrypto：<https://github.com/topics/burpcrypto>

第一节jsEncrypter演示使用了作者Github的图片，本来我自己也有截图，但觉得作者的动图做得非常棒就直接使用了，如有侵权请见谅，联系本人会及时删除。

更多内容欢迎关注 微信公众号 **凌晨安全**

![](https://image.3001.net/images/20200903/1599125392.png!small)

