## 0x01 前言

之前写了一个burp插件，直接使用目标站点的加密js来解决用intruder模块爆破时的payload加密问题

地址：[https://www.freebuf.com/sectool/242363.html](../sectool/242363.html
"JSRainbow")

除了上面的情况外，有时还会遇到把burp当作代理，调用网站的js代码处理来自浏览器、sqlmap等工具的内容情况。

比如目标网站的参数调用了js加密算法，不管是手动访问也好，还是sqlmap注入也好，需要调用指定算法处理参数，用python或java重写算法的话呢，时间成本太高，有些算法还挺复杂……但，如果能够直接复用目标网站的js代码的话就太方便了。

因此，简单写了一个burp
suite插件，专门解决上述问题：下载地址：[JSFlash](https://github.com/thinkoaa/JSFlash/)

使用步骤是 可以参考我之前另一个插件的文章 [参考地址](../sectool/242363.html)：

  1. 1.把目标站点的相关js代码放到本地js文件中，调试可用；
  2. 2.把JSFlash插件导入到Burp Suite中，在插件中加载指定的js文件并填写对应的参数；
  3. 3.抓包发repeater做测试，如果效果符合预期，则该插件会根据指定的规则，调用js代码，处理指定的内容。

效果图：

![](https://image.3001.net/images/20200820/1597906902.png!small)

## 0x02 使用方法

### 1.从目标站点复制修改或者手动写好js代码，调试正确

![](https://image.3001.net/images/20200820/1597907220.png!small)

![](https://image.3001.net/images/20200820/1597907372.png!small)

因为插件是通过java调用js，因此window、document等对象及方法，还有一些很新的js特性可能在浏览器中执行正确，但插件调用时会报错，因此插件会把可能产生的错误信息弹出显示，方便根据实际逻辑修改，根据我的经历来看，不管多复杂，只要耐心点，没有改不了的情况，如图：

![](https://image.3001.net/images/20200820/1597907715.png!small)

![](https://image.3001.net/images/20200820/1597907771.png!small)再举一个例：![](https://image.3001.net/images/20200820/1597907855.png!small)

![](https://image.3001.net/images/20200820/1597907928.png!small)

### 2.导入插件，设置参数

![](https://image.3001.net/images/20200820/1597908057.png!small)

2.1 设置url，一定要用burp的Copy URL菜单复制，不要手动填写，以免出错：

![](https://image.3001.net/images/20200820/1597908207.png!small)

![](https://image.3001.net/images/20200820/1597908444.png!small)

2.2 设置处理指定内容的规则

GET方式:

![](https://image.3001.net/images/20200820/1597908851.png!small)

![](https://image.3001.net/images/20200820/1597909124.png!small)

php代码如图：

![](https://image.3001.net/images/20200820/1597909223.png!small)

处理结果：

![](https://image.3001.net/images/20200820/1597909441.png!small)

POST方式：

![](https://image.3001.net/images/20200820/1597911263.png!small)

![](https://image.3001.net/images/20200820/1597911342.png!small)

php代码如图：

![](https://image.3001.net/images/20200820/1597910298.png!small)

结果如图：

![](https://image.3001.net/images/20200820/1597910353.png!small)

一次调用多个方法，处理多个指定内容：

数据包：

![](https://image.3001.net/images/20200820/1597910765.png!small)规则：

![](https://image.3001.net/images/20200820/1597910846.png!small)

php代码：

![](https://image.3001.net/images/20200820/1597910946.png!small)结果：

![](https://image.3001.net/images/20200820/1597911053.png!small)

## 0x03 总结

这个插件用到的时候，需要具体情况具体分析，不过思路是这么个思路，目的就是复用js代码，提高工作效率。

有问题可以qq、邮箱、留言沟通，一般周末晚上有时间。

