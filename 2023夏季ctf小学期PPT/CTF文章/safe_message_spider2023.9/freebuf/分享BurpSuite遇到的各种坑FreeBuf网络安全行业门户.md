## 前言

上篇文章[《HTTP协议调试工具汇总，你心目中应该是什么样的？》](http://www.freebuf.com/sectool/184366.html)介绍了近40款抓包工具，本篇将单独吐槽一下Burp
Suite使用中经常遇到问题，及设想如何改进。

## 1、性质问题

### 价格昂贵

专业版高达399美元/每年，免费版有功能限制：<https://portswigger.net/buy/pro>，构想中的工具应该是免费开源的。

![构想中的工具应该是免费开源的](https://image.3001.net/images/20181008/1538960989_5bbaae5d1c452.png!small)

### 破解版存在安全隐患

> <https://www.0x00sec.org/t/malware-reversing-burpsuite-keygen/5167>
>
> <https://www.52pojie.cn/thread-691448-1-1.html>

![破解版存在安全隐患](https://image.3001.net/images/20181008/1538961078_5bbaaeb645e7c.png!small)

想起了XcodeGhost事件。

### 此类工具的敏感性

> <http://www.4hou.com/info/news/7656.html>

![此类工具的敏感性](https://image.3001.net/images/20181008/1538964317_5bbabb5dd9dea.png!small)

## 2、界面问题

### 不支持多语言，且无法汉化

![不支持多语言，且无法汉化](https://image.3001.net/images/20181008/1538961181_5bbaaf1d34f00.png!small)

构想中的应该支持 多语言菜单文件。

## 3、编码问题

### 中文显示乱码

![中文显示乱码](https://image.3001.net/images/20181008/1538961218_5bbaaf4291b2f.png!small)

![](https://image.3001.net/images/20181008/1538963719_5bbab9077a82d.png!small)

![中文显示乱码](https://image.3001.net/images/20181008/1538963732_5bbab914ec2f7.png!small)

### 请求无法输入中文

![请求无法输入中文](https://image.3001.net/images/20181008/1538963745_5bbab9217b732.png!small)

### 搜索不支持中文

![搜索不支持中文](https://image.3001.net/images/20181008/1538963753_5bbab92901161.png!small)

Decoder模块不支持中文

![Decoder模块不支持中文](https://image.3001.net/images/20181008/1538963760_5bbab930ce838.png!small)

中文编码一直很蛋疼，构想中的不存在此类问题。

## 3、资源占用问题

### 爆机是家常便饭

![爆机是家常便饭](https://image.3001.net/images/20181008/1538961984_5bbab2406a692.png!small)

![爆机是家常便饭](https://image.3001.net/images/20181008/1538963768_5bbab93899339.png!small)

理想中应该不超过100M吧。

## 4、性能问题

### 代理速度慢的可以用眼看出来

![代理速度慢的可以用眼看出来](https://image.3001.net/images/20181008/1538963777_5bbab94138a0a.png!small)

###  不支持长连接

![
不支持长连接](https://image.3001.net/images/20181008/1538963782_5bbab9467449b.png!small)

### Intruder模块只有多线程

![Intruder模块只有多线程](https://image.3001.net/images/20181008/1538963798_5bbab95619fca.png!small)

只用多线程未免有点慢，可以使用“连接池”技术，但XProxy采用了原理相似的 “连接复用”技术 ，由于没有“连接池”的资源调度消耗所以速度更快。

## 5、操作问题

### Urlcod处停留只显示5秒，来不及看完

![Urlcod处停留只显示5秒，来不及看完](https://image.3001.net/images/20181008/1538962183_5bbab30768074.png!small)

构想中的可以勾选关键字，使用右键菜单直接在界面里解码显示。

### 不支持Unicode编码

可通过插件<https://github.com/bit4woo/u2c>：

![不支持Unicode编码](https://image.3001.net/images/20181008/1538963818_5bbab96a39007.png!small)

构想中的可以 自动解码或手动右键菜单解码。

### Decode模块字符长的话看起来很蛋疼

![Decode模块字符长的话看起来很蛋疼](https://image.3001.net/images/20181008/1538962242_5bbab34207e6e.png!small)

构想中的可以 换行。

### 连续查看响应页面时如果中间存在响应缺失则会跑到请求页面去

![响应缺失](https://image.3001.net/images/20181008/1538963828_5bbab9743ea69.png!small)

这个Bug也很蛋疼。

### 请求地址过长需要鼠标左右拖动操作或挨个点击查看

![请求地址过长](https://image.3001.net/images/20181008/1538963833_5bbab979e52ca.png!small)

看不全URL，现在的抓包工具操作起来都有种“盲点”的感觉，构想中的自定义性更高，比如URL可以换行显示。

## 6、扩展问题

插件开发语言只支持Java，Jython，JRuby，代码量太大，sqlmap联动插件居然用了1500多行代码。

![](https://image.3001.net/images/20181008/1538962395_5bbab3dbd514d.png!small)

构想中的 前后端都使用Python API控制。

还有哪些问题及设想？欢迎补充。

 ***本文作者：mazekey，转载请注明来自FreeBuf.COM**

