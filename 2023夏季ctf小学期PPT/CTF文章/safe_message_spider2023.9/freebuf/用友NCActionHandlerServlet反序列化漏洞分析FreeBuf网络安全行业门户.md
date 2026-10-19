## 前言

用友NC被披露过很多漏洞，其中反序列化漏洞尤为多，很多的接口都存在反序列化漏洞，网上披露的漏洞信息却很模糊，当自己把这些漏洞整合成工具时发现很多漏洞复现失败，只得回过头动手分析一探究竟。

## 分析

通过公开信息得知，用友NC 的ActionHandlerServlet接口存在反序列化漏洞。受影响的版本有NC6.3、NC6.5。

凭借对用友NC的历史反序列化漏洞了解，大多接口都是直接反序列化。便用同样方法测试，结果都是失败。

正好本地搭建有环境，那便直接找文件看源码。

已经知道了接口，通过接口 **ActionHandlerServlet** 找到对应的类。  
如下：  
![image](https://image.3001.net/images/20230818/1692338319_64df088f56eda611a10d6.png!small)

这里有三个方法 post和get接收到请求后调用了process()

查看process()  
可以看到 34行，将接收到的请求先用 **GZIPInputStream** 进行了 **Gzip解压缩**  
![image](https://image.3001.net/images/20230818/1692338348_64df08ac8ff5efe14e084.png!small)

然后紧接着就进行了反序列化，造成了反序列化漏洞。

看了代码获知 该接口请求的的序列化数据需要进行gzip压缩。

### 复现：

触发dnslog回显  
![image](https://image.3001.net/images/20230818/1692338358_64df08b6d19458b306760.jpg!small)

![image](https://image.3001.net/images/20230818/1692338368_64df08c06536c5bae9ac0.png!small)

写文件  
![image](https://image.3001.net/images/20230818/1692338378_64df08ca0adccf61c5200.png!small)

### poc编写问题：

在编写poc，对序列化数据进行gzip压缩时，出现了问题。

通过gzip库压缩后的数据与burp编码后的结果不同  
原始 序列化数据  
![image](https://image.3001.net/images/20230818/1692338399_64df08df36bd220377561.png!small)

用burp进行gzip解压看到的序列化数据`\xff变为了\xc3\xbf`  
![image](https://image.3001.net/images/20230818/1692338412_64df08eccf3db4c7ed479.png!small)

说明序列化数据经过gzip压缩时数据被改变了。

 **utf-8编码问题**  
经过查阅资料，找到一些信息，发现是UTF-8编码的问题：  
1.字节FF和FE在UTF-8编码中永远不会出现  
2.UTF-8是一种变长编码

修改编码为“ASCII”，问题解决  
![image](https://image.3001.net/images/20230818/1692338425_64df08f92fa52f00e9fff.png!small)

![image](https://image.3001.net/images/20230818/1692338433_64df0901bf7f2fbd12316.png!small)

![image](https://image.3001.net/images/20230818/1692338441_64df0909bb840a32eda20.png!small)

