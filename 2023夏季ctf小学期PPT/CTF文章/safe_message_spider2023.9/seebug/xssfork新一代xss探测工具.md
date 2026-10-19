作者：[bsmali4](http://www.codersec.net/2017/07/xssfork%E4%B8%80%E6%AC%BExss%E6%8E%A2%E6%B5%8B%E5%B7%A5%E5%85%B7/)

#### xssfork简介

xssfork 作为 sicklescan 的一个功能模块，其开发主要目的是用于检测 xss 漏洞。

传统的 xss 探测工具，一般都是采用 payload in response 的方式，即在发送一次带有 payload 的 http
请求后，通过检测响应包中 payload 的完整性来判断，这种方式缺陷，很多。

第一：不能准确地检测 dom 类 xss  
第二：用类似于 requests 之类的库不能真正的模拟浏览器  
第三：网页 js 无法交互

怎么解决？如果能够用浏览器代替这个模块，去自动hook是最好的。所幸，我了解到 phantomjs，当然现在 google 浏览器也支持 headless
模式，类似的，你也可以采用 google 浏览器去做检测。

#### 原理

对于这类 fuzz 过程,基本都是预先准备好一些 payload,然后加载执行。对于这类 io 型密集的扫描模型，后端使用多线程就比较适用，但是由于
phantomjs 你可以理解为一个无界面的浏览器，在加载的时候，其缺陷也比较明显，比较吃内存，用它来发包自然不像 requests 库轻量。

#### 编码脚本

由于基础的 payload 模块，我收集了71个。

![](https://images.seebug.org/content/images/2017/07/1.jpg-w331s)

基础 payload 会在现有的基础上，会添加上各种闭合的情况。

![](https://images.seebug.org/content/images/2017/07/2.jpg-w331s)

除了这些基础的 payload,xssfork 还提供了几个编码脚本，查看脚本，可以看 help

![](https://images.seebug.org/content/images/2017/07/3.jpg-w331s)

现阶段提供了10进制，16进制，随机大小写，关键字叠加四个脚本。

###### 10hex_encode

将 html 标签内部字符10进制化

    
    
    <a href=&#x6a&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3a&#x61&#x6c&#x65&#x72&#x74&#x28&#x36&#x35&#x35&#x33&#x34&#x29&#x3b>aaa</a>

![](https://images.seebug.org/content/images/2017/07/4.jpg-w331s)

其效果如下

![](https://images.seebug.org/content/images/2017/07/5.jpg-w331s)

###### 16hex_encode

将 html 标签内部字符16进制化

###### uppercase

随机大小写将 `<script>alert(65534);</script>` 转换成 `<ScRIPt>alert(65534);</ScRIpT>`

###### addkeywords

主要是应对过滤为 `replace('keyword>s','')` 的情况，`<script>alert(65534);</script>` 变成
`<<script>script>alert(65534);</script>`当然默认开启的是轻量模式，即只返回一个payload，开启重量模式，可以生成更加丰富的pyaload，效果如下

    
    
    <script>alert(65534);</script>  
    <script>alert(65534);</ScrIpt>  
    <ScrIpt>alert(65534);</sCrIpt>  
    <scRiPt>alert(65534);</script>  
    <ScrIpt>alert(65534);</script>

#### 演示

场景1.反射型xss
![](https://images.seebug.org/content/images/2017/07/---xss.gif-w331s)

场景2.大小写绕过  
![](https://images.seebug.org/content/images/2017/07/-----1-xss.gif-w331s)
![](https://images.seebug.org/content/images/2017/07/-----2-xss.gif-w331s)

场景3.dom型xss  
![](https://images.seebug.org/content/images/2017/07/dom-xss1.gif-w331s)
![](https://images.seebug.org/content/images/2017/07/dom-xss2.gif-w331s)

场景3.post类型 ![](https://images.seebug.org/content/images/2017/07/post-xss1.gif-w331s)

场景4.需要验证cookie ![](https://images.seebug.org/content/images/2017/07/cookie-xss.gif-w331s)
![](https://images.seebug.org/content/images/2017/07/2017-07-24-at---4-23.gif-w331s)
![](https://images.seebug.org/content/images/2017/07/2017-07-24-at---4-27.gif-w331s)

post类型  
python xssfork.py -u "xx" -d "xx" 存储型  
python xssfork.py -u "xx" -d "xxx" -D "输出位置" 带cookie python xssfork.py -u "xx"
-c "xx"

#### 说明

开源只为分享，请勿将本脚本做任何商业性质的集成。开发的时候，有可能很多情况没有考虑到，如果你有更好的建议或者发现bug，可以联系我邮箱root@codersec.net
，xssfork.codersec.net网站还在建设中，github不要吝啬你的star。

开源地址 https://github.com/bsmali4/xssfork ，记得不要吝啬你的star

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/359/>

