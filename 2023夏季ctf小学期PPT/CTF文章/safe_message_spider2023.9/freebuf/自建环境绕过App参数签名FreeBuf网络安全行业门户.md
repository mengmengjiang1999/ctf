*** 本文作者：海带头，本文属FreeBuf原创奖励计划，未经许可禁止转载，** **声明：本文仅限于技术讨论，严禁用于非法目的**

## 概述

**随着智能终端的不断发展，应用数量和app应用种类不断扩大的同时，各类应用安全问题也不断涌现，例如恶意代码注入、发送虚假坐标、刷屏、刷票、用户敏感信息泄露。app在设计开发阶段，需要根据业务场景考虑多种安全策略。比如在数据传输方面，很多app为保证数据的机密性和完整性，会对发送的请求数据做加密和签名处理。那么，作为一名白帽子，又如何绕过这些安全策略呢？今天我们自己搭建坏境测试下。**

## 环境搭建

为了便于演示和测试，我们需要自己搭建一个测试环境，主要分为客户端和服务端的搭建。

### app客户端

首先，我们需发一个app的demo，在点击按钮后会发送一个加密请求到服务端，如下图所示：

![image.png](https://image.3001.net/images/20180514/15262828336478.png!small)  

在MainActivity中，监听到Button按钮点击后，使用子线程执行http请求。返回信息回调给主进程的webview组件。http请求函数sendRequestWithHttpClient()如下图所示。这里先将原始`xml字符串`使用aes对称加密，作为post数据。再将加密结果hash运算后与时间戳等因子生成签名`signature`，signature和因子放在url中供后台服务器校验使用。

![image.png](https://image.3001.net/images/20180514/15262828507650.png!small)  

### 服务端

服务端获取因子和post数据后会重新hash校验，校验通过再使用对称解密获取数据，（这里我将解密后的xml数据重新加密发送给客服端）：

![image.png](https://image.3001.net/images/20180514/15262828604325.png!small)

### 请求

安装demo后，使用burpsuit抓取客户端发送的请求，可以看到post的是AES加密的数据，url中是因子和signature，如下：

![image.png](https://image.3001.net/images/20180514/15262828698951.png!small)

下图是request body和url中参数的逻辑图形。body是由明文数据aes加密得到，参数l由body
hash运算生成，参数s由时间戳和token等因子生成。若改变body或相关参数，服务端将验签失效。

![image.png](https://image.3001.net/images/20180516/152645863760.png!small)

## 解密绕过

其实很早之前我写过一篇xposed
hook加密函数的方法，请参考<https://mp.weixin.qq.com/s/zCGkfrDfCNjBA9qht4MiiQ>  
所以我们这次使用frida的工具尝试下。

### frida

这里我们使用frida去hook app中的加密函数，让其直接post明文数据。  
1.首先，需要下载对应版本的fridaserver，建议放在/data/local/tmp目录下，给与权限后执行。（在此之前建议关闭selinux防火墙，使用命令`setenforce
0`）  
2.端口转发  
adb forward tcp:27042 tcp:27042  
adb forward tcp:27043 tcp:27043  
使用`frida-ps -R`出现进程列表则表示没有问题。  
3.frida提供了丰富的js
api接口，供我们对需要调试的进程进行hook。我们查看需要hook的函数（可以修改该函数接受的参数、函数输出值、覆盖重新定义该函数）：

![image.png](https://image.3001.net/images/20180514/15262828914310.png!small)  

函数的参数为String类型的明文和String类型的key，我们hook类AESTool中的函数Encrypt()，让其直接输出明文，绕过其加密过程,如下图所示：

![image.png](https://image.3001.net/images/20180515/15263846434398.png!small)  

将该js注入到进程中：

![image.png](https://image.3001.net/images/20180514/15262829684980.png!small)

点击app发送请求的按钮，可以看到加密的函数已经被绕过，request body明文显示。但是由于request
body被改动，服务端验签将会失败。在安全测试的时候，不能改动请求参数那便如咸鱼一样，xss、sql、越权等漏洞仿佛与你隔着一层难以逾越的鸿沟。所以，我们需要重新构造请求给服务端，最简单的办法就是编写burpsuit的插件。

![image.png](https://image.3001.net/images/20180516/15264591075104.png!small)

### burp插件

我们可以利用burpsuit提供的接口实现插件的开发。新建项目，将burpsuit提供的api导入后，新建BurpExtender.java类，重写processHttpMessage()方法。我们将app客户端使用的加密和签名使用的类也导入，根据客户端的加密和签名逻辑，重新构造请求，并将构造的请求打印在后台:

![image.png](https://image.3001.net/images/20180516/15264628942040.png!small)

![image.png](https://image.3001.net/images/20180516/1526462916372.png!small)

使用fat jar
exporter将项目导出jar文件，burpsiut中添加插件并勾选插件，重新抓包，查看插件打印的输出，可以看到所又经过burp的请求将被插件重新以app客户端的逻辑构造：

![image.png](https://image.3001.net/images/20180516/15264615834700.png!small)

关闭插件，单独发送该请求验证burp插件构造的请求是否可以通过，成功：

![image.png](https://image.3001.net/images/20180516/15264622633615.png!small)

这样测试人员便可以随意修改抓取的数据。同理，服务端返回的数据是加密的，同样可以在插件中解密，不做赘述。

## 总结

Frida提供的api有很多，这里只是简单的介绍，还值得我们去深入了解。app安全策略还有很多，比如https证书检验、root环境检测等等，同样的道理，很多业务场景需要我们去发挥想象去做一些有趣的事情。

 *** 本文作者：海带头，本文属FreeBuf原创奖励计划，未经许可禁止转载**

