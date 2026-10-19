# Brida入门

阅读量 **151623**

发布时间 : 2022-05-06 15:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01c2d9182c5248d888.jpg)

## Brida入门

###  前言

Brida是Burp中的一个插件，它可以把Burp和Frida结合起来使用，简化测试流程，通过Brida能在Burp中直接调用目标app中的加/解密函数，进行参数修改测试更多的输入点。

###  Brida及其依赖安装

Brida在Burp的插件商店中有下载。

![](https://p3.ssl.qhimg.com/t017a259a6e5c54a603.jpg)

因为Brida目前仅支持python2.7，你需要配置python2.7。  
然后是需要配置Frida，我这里用的12的，手机上注意对应版本，并启动Frida server。

![](https://p3.ssl.qhimg.com/t0176469961c1ff5281.jpg)

然后电脑还要安装两个依赖。  
Pyro4安装：

    
    
    pip install Pyro4
    

frida-compile安装，这里需要指定版本为9.x，大于9也行，但是会麻烦点。

    
    
    npm install frida-compile@9
    

安装好以后，页面如下：

![](https://p3.ssl.qhimg.com/t01ca93a61bc4cfd404.jpg)

简单看下他的配置：

![](https://p2.ssl.qhimg.com/t0100ac22b0eccb4deb.jpg)

###  简单实操

现在找个简单的app来测试（手头没有适合讲的app，挑了个有加密的，最后是有点问题的）。  
在手机启动app，先attach上对应的app。不知道进程名可以用frida-ps查看。

![](https://p4.ssl.qhimg.com/t01ca9510a9af2f674f.jpg)

hook成功不会报错，它有bug有时候（经常）报错，，kill server再启动，然后spawn attach几个多点，多试。  
然后在JS Editor中测试下js脚本能不能执行，模板用前面指定的Frida JS files folder目录下的Brida.js。  
这里写了个简单的输出脚本。

![](https://p0.ssl.qhimg.com/t01285aafcdf1c37c41.jpg)

然后去Debug export中进行调用，能正常输出就是好事。

![](https://p1.ssl.qhimg.com/t01651f3bd98718b553.jpg)

###  加解密

简单的会用了，来继续看这个app。  
数据包如下：发现都是加密的。

![](https://p1.ssl.qhimg.com/t01ba5713521ac5f82e.jpg)

先jadx打开，定位算法，他没有加壳（我之前测过，定位加密算法过程简化了）。  
直接通过encrypt之类的关键字定位到。

![](https://p5.ssl.qhimg.com/t013c9e196dd59c2950.jpg)

不放心，再用HttpDecrypt hook下看看，是否正确：

发现请求时，存在调用，不过他输入是bytes数组，后面写的时候要进行String转bytes的操作。

![](https://p1.ssl.qhimg.com/t017846c3beea210d7d.jpg)

将String转bytes：

![](https://p1.ssl.qhimg.com/t01bf50886e8fb07bf8.jpg)

这里多次测试发现密钥固定，a为加密，c为解密。

![](https://p1.ssl.qhimg.com/t01abdc632f551cbd15.jpg)

![](https://p4.ssl.qhimg.com/t01d199377b82e595c9.jpg)

这样就可以开始写hook了。  
时间问题写了个加密的，解密的差不多，就不重复写了。

![](https://p4.ssl.qhimg.com/t01ebcbddd381b1c06e.jpg)

在Debug export中输入明文，执行如下，能实现基本功能：

![](https://p4.ssl.qhimg.com/t0152fb9a91ae324ff5.jpg)

解密的hook调用也是大同小异，不重复了。

## 总结

这里只是简单尝试了下Brida的基础功能，比Frida直接操作只是多了图形化，Brida更强大的地方在于能和Burp的各模块进行联动。  
关于插件这块，下回分解。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/272868](/post/id/272868)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [brida](/tag/brida)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

