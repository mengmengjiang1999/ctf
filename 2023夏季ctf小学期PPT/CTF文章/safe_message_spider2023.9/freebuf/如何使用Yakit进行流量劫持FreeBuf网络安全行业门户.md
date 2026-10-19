## Yakit与 Burp在MITM上的对比

Yakit在使用代理监听端口劫持浏览器所有流量的场景下，已达到 **基本覆盖Burp基础功能**
的程度，虽然Yakit在MITM上仍有较多功能需要完善，但目前劫持流量、编解码数据包、web
fuzzer等功能已能满足正常使用。在爆破和流量转发时使用Yakit和Burp的操作状态和结果如下。

1.进行爆破枚举（burp）

![1641349431_61d50137ecf52404c0025.png!small?1641349433200](https://image.3001.net/images/20220105/1641349431_61d50137ecf52404c0025.png!small?1641349433200)

![1641349591_61d501d739c5f55828616.png!small?1641349592125](https://image.3001.net/images/20220105/1641349591_61d501d739c5f55828616.png!small?1641349592125)

![1641349634_61d50202108a982065750.png!small?1641349635231](https://image.3001.net/images/20220105/1641349634_61d50202108a982065750.png!small?1641349635231)

进行爆破枚举（yakit）

![1641349958_61d5034605f34ac2cc117.jpg!small?1641349958617](https://image.3001.net/images/20220105/1641349958_61d5034605f34ac2cc117.jpg!small?1641349958617)

![1641349962_61d5034abf42817c1625e.jpg!small?1641349963945](https://image.3001.net/images/20220105/1641349962_61d5034abf42817c1625e.jpg!small?1641349963945)

![1641349970_61d50352231416ffdc9ed.jpg!small?1641349971525](https://image.3001.net/images/20220105/1641349970_61d50352231416ffdc9ed.jpg!small?1641349971525)

2.进行流量转发（burp）

![1641350157_61d5040d9b4982243d3d2.jpg!small?1641350159426](https://image.3001.net/images/20220105/1641350157_61d5040d9b4982243d3d2.jpg!small?1641350159426)

![1641350172_61d5041c2036ac070d705.jpg!small?1641350174484](https://image.3001.net/images/20220105/1641350172_61d5041c2036ac070d705.jpg!small?1641350174484)

![1641350187_61d5042bae99070fa2e6b.png!small?1641350192706](https://image.3001.net/images/20220105/1641350187_61d5042bae99070fa2e6b.png!small?1641350192706)

![1641350198_61d50436ba10d1c4209f9.png!small?1641350201004](https://image.3001.net/images/20220105/1641350198_61d50436ba10d1c4209f9.png!small?1641350201004)

进行流量转发（yakit）

![1641351123_61d507d310462512a5997.jpg!small?1641351123953](https://image.3001.net/images/20220105/1641351123_61d507d310462512a5997.jpg!small?1641351123953)

![1641351127_61d507d767da088e5a9a6.png!small?1641351129991](https://image.3001.net/images/20220105/1641351127_61d507d767da088e5a9a6.png!small?1641351129991)

![1641351130_61d507daf0442364c311c.png!small?1641351133582](https://image.3001.net/images/20220105/1641351130_61d507daf0442364c311c.png!small?1641351133582)

可以看到在使用上，Yakit和Burp的差异不大，为了让用户能快速适应Yakit，在保留了Burp的常用操作基础上，对页面进行了人性化的优化，使交互更简洁流畅。从调试的结果来看，Yakit和Burp的结果是一致的，爆破和流量转发场景下，Yakit与Burp的功能性趋于一致。

## MITM功能介绍

### MITM

这个页面简单来说可以查看并编辑劫持数据包、查看最近历史请求数据，也可使用插件对数据包进行分析，目前插件仍在不断地完善中~如对插件有其他个性化的要求，可在“插件商店”对插件的源码进行修改，或自主添加新插件。

![1641351771_61d50a5b4fb40e9c1673b.jpg!small?1641351771436](https://image.3001.net/images/20220105/1641351771_61d50a5b4fb40e9c1673b.jpg!small?1641351771436)

### Http history

查看历史的请求响应数据包并对数据包进行编解码操作，了解请求的详细信息，如需对数据包进行编辑调试，可发送到web fuzzer进行操作。

![1641351791_61d50a6f5da3f23681eff.jpg!small?1641351791607](https://image.3001.net/images/20220105/1641351791_61d50a6f5da3f23681eff.jpg!small?1641351791607)

### 网站树视角

将历史请求以树结构的形式进行展示，选中域名，可查看该域名对应的数据信息与详情。

![1641351805_61d50a7d1f07b38aa65e4.jpg!small?1641351805227](https://image.3001.net/images/20220105/1641351805_61d50a7d1f07b38aa65e4.jpg!small?1641351805227)

### Web fuzzer

与Burp的repeater类似，可调试数据包进行漏洞检查。但Yakit提供yak.fuzz语法，在webfuzzer中使用来更灵活地调试数据，比如一次可发送多个请求包进行参数调试。

![1641351820_61d50a8c42d2864f743dd.jpg!small?1641351820793](https://image.3001.net/images/20220105/1641351820_61d50a8c42d2864f743dd.jpg!small?1641351820793)

## MITM持续升级

1、丰富MITM插件，涵盖指纹检测、参数爆破等场景

2、支持comparer对数据进行可视化差异对比

3、GUI的持续优化

## E N D

Yakit下载地址：https://github.com/yaklang/yakit

项目公众号：[Yak Project](https://mp.weixin.qq.com/cgi-bin/settingpage?t=setting/index&action=index&token=685964089&lang=zh_CN)

欢迎大家进交流群沟通~进群添加微信：Juzi19880818

期待收到大家在github issue / 微信公众号 / 微信用户群等渠道留下你的意见反馈或好评~~

