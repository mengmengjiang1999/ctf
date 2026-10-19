众所周知，BurpSuite几乎成为全球WEB安全从业者必用的安全测试工具，然而十余年来尚无一个可替代的解决方案。破解版被投毒风险高、商业版太贵、插件难写、依赖java…等等问题逐渐显露。

与我个人而言，经常会遇到的一种情况就是，有的网站BurpSuite一打开就会被WAF拦掉，这也是我从Burp转到Yakit的契机和原因之一吧。

在经过一段时间的使用与体验后，想着针对两个工具之间的功能性模块，来一个正面对决，1V1分析一番。

![](https://image.3001.net/images/20221104/1667543421_6364b17ddc3561be384d4.png!small)

  

##  
BurpSuite-Proxy模块

先看熟悉的Burp抓包，打开抓包

  

![](https://image.3001.net/images/20221104/1667543440_6364b19066580b4083586.png!small)  
所有的流量都会拦下来,包括一些没用的"心跳"，如下图  
比如付款的页面，会不断发送数据包进行检测是否付款成功

![](https://image.3001.net/images/20221104/1667543453_6364b19d01474082a0528.png!small)

尽管这里可以设置要拦截的流量,但是设置还是比较麻烦，  
比如你要对一个网站进行测试，设置好了过滤的策略，这时候，突然电脑关机了，你打开Burp又要设置一遍过滤的策略。

![](https://image.3001.net/images/20221104/1667543465_6364b1a9c0ef2b7da7cee.png!small)

在还没遇到并使用Yakit之前,我的解决办法是装一个插件 knife，对于没用且频繁发送的数据包dismiss。

![](https://image.3001.net/images/20221104/1667543478_6364b1b61afe59e09933b.png!small)

它根据url或host可以选择drop或者forward

  

![](https://image.3001.net/images/20221104/1667543490_6364b1c2e8bd8918815e8.png!small)  
但是，我们在实际测试中还会有个问题  
比如你测试的是[http://a.com](https://link.zhihu.com/?target=http%3A//a.com)  
有一个"心跳"为a.com?log=nkebsfks(随机数)  
这个时候如果你选择dismissed整个host，那你测试这个站的流量全部会被放过，如果你选择dismissed这个url，下一个"心跳"仍然会被拦截(因为含有随机数)。  
所以又不得不回到这里设置拦截的规则，而且对于不懂正则的人来说，这里可能又会碰上难题。

![](https://image.3001.net/images/20221104/1667543505_6364b1d18605bed5412fe.png!small)

## Yakit Proxy取代模块MITM

  

![](https://image.3001.net/images/20221104/1667543528_6364b1e81c1b81dabb8e0.png!small)

我们先看过滤模块：

![](https://image.3001.net/images/20221104/1667543540_6364b1f46e0c0eae57ca8.png!small)

首先这个界面和Burp比起来，很简洁有没有？  
而且就操作而言，Yakit也相对方便很多(不需要你点击那么多次)，Burp设置一条过滤要点击8、9次，而Yakit只需要2次。

![](https://image.3001.net/images/20221104/1667543557_6364b20536c7fa86c04ab.png!small)

接下来看标记和替换规则

![](https://image.3001.net/images/20221104/1667543572_6364b21484da63671454e.png!small)

新增规则

![](https://image.3001.net/images/20221104/1667543584_6364b220eb32474e1b451.png!small)

添加规则后可以在该规则设置对哪些流量生效

![](https://image.3001.net/images/20221104/1667543599_6364b22f0302bbee5fda4.png!small)

然后发送一个请求参数为wifi的数据包看标记效果

![](https://image.3001.net/images/20221104/1667543610_6364b23acf2868676dcb3.png!small)

我发送的wifi也被替换成了WIFI

![](https://image.3001.net/images/20221104/1667543622_6364b246abf49c32a3023.png!small)

Yakit这些流量替换、标记的功能Burp虽然也有，不过相比起来，个人觉得Yakit的实现方式会更加方便使用.

接下来说一下Burp没有的功能— **热加载**

在Burp中如果你想自定义处理经过代理的流量，就需要自己开发插件，在懂java的基础上学个一两天差不多就可以开发插件了。

![](https://image.3001.net/images/20221104/1667543638_6364b256a6e5ca89b17eb.png!small)

当然插件也可以用Python开发，不过需要下载Jython，麻烦事也挺多的…  
而对于Yakit，自定义处理流量就很简单了。

![](https://image.3001.net/images/20221104/1667543650_6364b262df6b62df24a51.png!small)

demo里第一个if是如果请求包含/products/plugins/plugin_11就替换内容后发送；  
第二个if是如果请求包含/products/plugins/plugin_12直接丢弃；  
即便你不懂java、python、go…这几行代码也没有压力吧  
如果Yakit自带的规则满足不了你，那就使用热加载，想怎样就怎样！  
之前提到过a.com?log=sevse(随机数)也可以使用热加载过滤掉。

![](https://image.3001.net/images/20221104/1667543666_6364b272bad2b8c964da7.png!small)

## BurpSuite-Repeter模块

这个相信大家都已经很熟悉了。

![](https://image.3001.net/images/20221104/1667543681_6364b28150a2b7562a00f.png!small)

## Yakit Repeter取代模块Web Fuzzer

效果上和Burp是差不多的

![](https://image.3001.net/images/20221104/1667543693_6364b28dac16d1a85aa77.png!small)

## Burpsuite Decoder模块

说实话这个模块我基本上没有用过，因为它不支持中文解码。  
还有一点就是有点麻烦，你需要找Decoder模块，在插件多的情况下，一眼看不到Decoder模块。

![](https://image.3001.net/images/20221104/1667543708_6364b29cc740116af07d0.png!small)

关于中文解码，插件knife可以解决，  
不过knife默认编码好像不是GBK，需要点点点进行切换…我修改了knife的源码优化了这点，需要的可以自取[https://github.com/VVeakee/knife](https://link.zhihu.com/?target=https%3A//github.com/VVeakee/knife)

![](https://image.3001.net/images/20221104/1667543723_6364b2abe3e0e1e3373f9.png!small)

## Yakit Decoder取代模块Codec

包含编码以及加解密算法

![](https://image.3001.net/images/20221104/1667543736_6364b2b8d6b148fa9af06.png!small)

此外，Codec不单单是个模块，在代码中是有这个全局变量的，后面会在热加载中用来生成自定义的payload

![](https://image.3001.net/images/20221104/1667543749_6364b2c56bb9029a9528a.png!small)

当然，最方便的用法还是右键即可，这个不需要解释吧，Yakit yyds！

![](https://image.3001.net/images/20221104/1667543762_6364b2d29f1c483f762e9.png!small)

## BurpSuite Intruder模块

对于Intruder模块最重要的无非两点  
1.payload位置

![](https://image.3001.net/images/20221104/1667543776_6364b2e0b2a9104ab2256.png!small)

2.payload(字典)

![](https://image.3001.net/images/20221104/1667544003_6364b3c3397d679a02809.png!small)

在以往的使用经验中，大概率是要你先生成payload然后load  
比如你需要6位随机字符，很遗憾，Burp里并没有适合的生成该payload的type

![](https://image.3001.net/images/20221104/1667544016_6364b3d0a49a7aada6d63.png!small)

你可能会用python写一段代码或者crunch生成payload  
有时候甚至会想，偌大的Burp就没有一个好用的插件可以自动生成payload吗？

## Yakit Intruder取代模块

![](https://image.3001.net/images/20221104/1667544031_6364b3dfecc5b627cb489.png!small)

下面是自带的生成payload的规则

![](https://image.3001.net/images/20221104/1667544044_6364b3ec3620e68d897e7.png!small)

如果不存在符合你需要的payload可以直接用代码生成，  
如下，生成6位数字爆破手机验证码的payload为`{{int(0-100000|6)}}`

  

![](https://image.3001.net/images/20221104/1667544060_6364b3fc2b8346b7a948f.png!small)  
除了代码生成的payload也可以使用定义好的payload

![](https://image.3001.net/images/20221104/1667544174_6364b46ee13d21aae02c2.png!small)

把你定义好的payload上传云端，调用就是`{{x(字典名)}}`  
比如我要使用user_top10这个字典

![](https://image.3001.net/images/20221104/1667544192_6364b4809aac18b344823.png!small)

如果插入两个位置就是对应Burp里的Cluster bomb模式，请求总数为payload1的个数 乘 payload2的个数。

  

![](https://image.3001.net/images/20221104/1667544205_6364b48d8232d2fd4bf2d.png!small)  
如果仍然没有你想要的payload也没关系，咱们可以自己直接造。  
这里有两种方式造payload，强烈推荐第一种！  
1.热加载

  

![](https://image.3001.net/images/20221104/1667544229_6364b4a51cec865afbfbd.png!small)

示例1:转小写

  

![](https://image.3001.net/images/20221104/1667544242_6364b4b2d99ccaf4bbd8b.png!small)  
示例2:base编码

![](https://image.3001.net/images/20221104/1667544253_6364b4bd03d8f85dd6602.png!small)

保存后直接粘贴payload就可以

![](https://image.3001.net/images/20221104/1667544264_6364b4c89d9ae429b894d.png!small)

这个地方的payload可以说是即用即生成，超级方便！  
2.常规写脚本  
下图是用字符集`abc123!@#`生成10个6位的随机字符串

![](https://image.3001.net/images/20221104/1667544276_6364b4d4bb2452e182fa8.png!small)

然后在payload管理里面专门生成一个字典temp放临时字典

![](https://image.3001.net/images/20221104/1667544290_6364b4e2ec4a12fbbe44d.png!small)

## BurpSuite turbo intruder 并发插件

一般是用来测试并发

![](https://image.3001.net/images/20221104/1667544303_6364b4ef9fa6bd5e9721e.png!small)

## Yakit并发取代模块

Yakit的并发集成在Web Fuzzer中

![](https://image.3001.net/images/20221104/1667544314_6364b4fa345370fa940a4.png!small)

## BurpSuite target模块

![](https://image.3001.net/images/20221104/1667544326_6364b506e4925db1c7cd4.png!small)

## Yakit target取代模块 网站树

![](https://image.3001.net/images/20221104/1667544338_6364b512753a88b9b731a.png!small)

## 一点点建议

在网站树状图的地方,大概是我喜欢一眼能看到数据包的布局吧，如下图：

![](https://image.3001.net/images/20221104/1667544357_6364b5250d3a56477a7ba.png!small)

## 总结

综上所述，Yakit作为后起之秀，已经把Burp经常用的功能全实现了，并且用起来更加方便快捷。  
而且相比于Burp的插件，Yakit的插件更容易开发，还有一点算是大势所趋吧，Yakit的数据会上传到云端，你的个人习惯、使用的工具都会保存在云端(如果字典也可以上云那可就太妙了)，可谓是拿来就用，但是Burp的话，换个设备就是又要从0开始了。

