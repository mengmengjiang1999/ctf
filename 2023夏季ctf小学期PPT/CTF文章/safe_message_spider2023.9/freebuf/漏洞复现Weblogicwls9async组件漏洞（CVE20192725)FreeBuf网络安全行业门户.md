## **漏洞描述**

该漏洞是由wls9-async组件导致，在反序列化处理输入信息时存在缺陷，攻击者可以在/_async/AsyncResponseService路径下传入恶意的XML格式的数据，传入的数据在服务器端反序列化时，执行其中的恶意代码，实现远程命令执行，进而攻击者可以获得整台服务器的权限。

##  **影响版本**

WebLogic 10.X

WebLogic 12.1.3

##  **复现步骤**

注：因10.X版本都受影响，所以本次复现使用的是SSRF漏洞版本环境

###  **01** 测试漏洞是否存在

方法如下：访问[http://youip:7001/_async/](https://link.zhihu.com/?target=http%3A//youip%3A7001/_async/)（返回403说明存在，返回404说明不存在）

![v2-67e50dc3cd00c7116555c8e70016470c_720w.jpg](https://image.3001.net/images/20200903/1599098759.jpg!small)

访问[http://youip:7001/_async/AsyncResponseService](https://link.zhihu.com/?target=http%3A//youip%3A7001/_async/AsyncResponseService)，（返回200说明存在，返回404说明不存在）

###
**![preview](https://image.3001.net/images/20200904/1599211192.jpg!small)02**
利用poc反弹shell

![preview](https://image.3001.net/images/20200904/1599212521.jpg!small)![preview](https://image.3001.net/images/20200904/1599211193.jpg!small)

![preview](https://image.3001.net/images/20200911/1599794422.jpg!small)

 **03** 在Windows这台主机上开启监听，反弹成功

![preview](https://image.3001.net/images/20200904/1599211194.jpg!small)

##  **产品解决与支持**

华云安灵洞®威胁与漏洞管理平台（Ai.Vul）已经支持一键检测该漏洞。

![preview](https://image.3001.net/images/20200904/1599212521.jpg!small)

![preview](https://image.3001.net/images/20200904/1599212522.jpg!small)

