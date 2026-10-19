## 前言

此次演练来源于使用谷歌搜索引擎偶然得到的站点。本人萌新一枚，大佬勿喷。

## 实战过程

1\. 谷歌语法 ’inurl:php?id=’，找到此站点。

![1622788061_60b9c7dd1ac3689b5d043.png!small?1622788061366](https://image.3001.net/images/20210604/1622788061_60b9c7dd1ac3689b5d043.png!small?1622788061366)

2\. 通过参数判断为数字型，接着开始构造SQL语句，得到列数为9。

![](https://image.3001.net/images/20210604/1622788397_60b9c92daf1cf98b8153c.png!small)3\.
先判断显示位在哪里。

![](https://image.3001.net/images/20210604/1622788568_60b9c9d8d4230fdc1e72f.png!small)

4\. 接着查出数据库和当前用户。

![](https://image.3001.net/images/20210604/1622788774_60b9caa6d712bf6c44e6a.png!small)5\.
这里的第一个表直接爆出了admin表。

![](https://image.3001.net/images/20210604/1622789036_60b9cbac026cebd846915.png!small)6\.
接着爆出表中的主要字段。

![](https://image.3001.net/images/20210604/1622789176_60b9cc381fcf233c218b9.png!small)![](https://image.3001.net/images/20210604/1622789227_60b9cc6bdef06305555fb.png!small)

## 总结

站点应加强防护，程序员应进行黑白名单过滤。

