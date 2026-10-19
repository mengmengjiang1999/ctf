## 背景

Burp⾥有match extract，⽽在Yakit⾥可以通过"预加载参数⽣成器" 来获取token插⼊。

## 进入正题

要提取token，⾸先得找到提取token的正则，这⾥使⽤Fuzzer巧妙获取⼀下即可。

![](https://image.3001.net/images/20221118/1668762524_63774b9cdeb3bb377bdd8.png!small)

像这样随便插⼊⼀个Fuzztag获取response，就可以⽤提取响应数据的功能来获取正则。

![](https://image.3001.net/images/20221118/1668762539_63774babaf3d766bcfd1e.png!small)

![](https://image.3001.net/images/20221118/1668762555_63774bbb2a2e01b2e24c3.png!small)

然后前后缀之间插⼊`(.*?) `，因为可能涉及多⾏匹配，所以建议前⾯加个`(?s)`，格式就是：

![](https://image.3001.net/images/20221118/1668762650_63774c1a6c3d122853124.png!small)

替换成上⾯的例⼦就是 ：

![](https://image.3001.net/images/20221118/1668762664_63774c28d00d3c8f05079.png!small)

原本是想使用它的单正则提取，发现有bug，无法提取分组值 ，然后代码如下 ：

![](https://image.3001.net/images/20221118/1668762679_63774c37138e63bd6b9e6.png!small)

热加载，插⼊到预加载参数⽣成器，将提取的结果放到"token"这个参数中，后续就会渲染给`{{params(token)}} `

  
![](https://image.3001.net/images/20221118/1668762696_63774c48d5d435605de03.png!small)

这个函数是⼀个全局函数，就是每次发包都会调⽤这个函数，进⾏参数预处理，如果没有这种场景，就别去改它。

###
![](https://image.3001.net/images/20221118/1668762714_63774c5aa1ff35e2228ac.png!small)

下⾯就是最后⼀步，插⼊Fuzztag`{{params(token)}}`,发包后可以看到payloads⾥已经被渲染了。

![](https://image.3001.net/images/20221118/1668762730_63774c6a5745f2d2aa31e.png!small)

打开请求详情查看，进⼀步确认渲染成功了。

![](https://image.3001.net/images/20221118/1668762745_63774c7980765e65c8ece.png!small)

参考文章：https://mp.weixin.qq.com/s/ePogLxU5SPkNNPiCMb3QTw、

## 结语

感谢来自@520师傅的投稿分享，在Yakit的进阶过程中，已经陪很多师傅完成了大量的工作内容，未来团队也会继续沉淀与强化Yakit的各个功能模块，希望能逐步脱离大家对
BurpSuite的依赖，更高效便捷地完成工作！

