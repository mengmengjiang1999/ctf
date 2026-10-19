# 漏洞简介

Apache Kafka是一个分布式数据流处理平台，可以实时发布、订阅、存储和处理数据流。Kafka
Connect是一种用于在kafka和其他系统之间可扩展、可靠的流式传输数据的工具。攻击者可以利用基于SASLJAAS 配置和SASL
协议的任意Kafka客户端，对Kafka Connect worker 创建或修改连接器时，通过构造特殊的配置，进行JNDI 注入来实现远程代码执行。

# 影响版本

2.4.0<=Apache kafka<=3.3.2

# 修复方案

更新Apache Kafka至官方最新版本

# 环境搭建

通过[https://github.com/vulhub/vulhub搭建](https://github.com/vulhub/vulhub%E6%90%AD%E5%BB%BA)

# 漏洞复现

exp可参考：

<https://github.com/projectdiscovery/nuclei-templates/blob/5d90e8275084b0ae9166ec38cacd22e5a5a94fb8/http/vulnerabilities/apache/apache-druid-kafka-connect-rce.yaml>

发起攻击请求：

构造payload ,执行新建/tmp/test.txt文件

![1686306058_6482fd0aa605aa2ede112.png!small](https://image.3001.net/images/20230609/1686306058_6482fd0aa605aa2ede112.png!small)

验证漏洞存在，文件新建成功

![1686306072_6482fd1891d327fad8206.png!small](https://image.3001.net/images/20230609/1686306072_6482fd1891d327fad8206.png!small)

开启RASP后发起攻击：

在业务优先模式下，RASP会出现JNDI注入的告警，拦截最终的命令执行

![1686306081_6482fd2108f0a55a56c48.png!small](https://image.3001.net/images/20230609/1686306081_6482fd2108f0a55a56c48.png!small)

堆栈信息为

![1686306089_6482fd292f080e0af0f3d.png!small](https://image.3001.net/images/20230609/1686306089_6482fd292f080e0af0f3d.png!small)

在防护模式下将直接在JNDI注入处被拦截  
![1686306099_6482fd33a9ec8095f7fc5.png!small](https://image.3001.net/images/20230609/1686306099_6482fd33a9ec8095f7fc5.png!small)

堆栈信息为  
![1686306106_6482fd3aec6fdc7d9d31f.png!small](https://image.3001.net/images/20230609/1686306106_6482fd3aec6fdc7d9d31f.png!small)

# 漏洞分析

开始

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(java.util.Properties)

![1686306115_6482fd43626d65414f2ed.png!small](https://image.3001.net/images/20230609/1686306115_6482fd43626d65414f2ed.png!small)

跟进到

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(java.util.Properties

![1686306122_6482fd4aaa246b6b70e70.png!small](https://image.3001.net/images/20230609/1686306122_6482fd4aaa246b6b70e70.png!small)

调用

org.apache.kafka.common.utils.Utils#propsToMap  
对传入对象进行处理  
![1686306129_6482fd51dcce6562e1e27.png!small](https://image.3001.net/images/20230609/1686306129_6482fd51dcce6562e1e27.png!small)

将map型的对象传入

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(java.util.Map

![1686306136_6482fd58e2473bab27530.png!small](https://image.3001.net/images/20230609/1686306136_6482fd58e2473bab27530.png!small)

之后调用

org.apache.kafka.clients.producer.ProducerConfig#appendSerializerToConfig

![1686306144_6482fd6080b7ca40d1859.png!small](https://image.3001.net/images/20230609/1686306144_6482fd6080b7ca40d1859.png!small)

将返回的newConfigs传入

org.apache.kafka.clients.producer.ProducerConfig#ProducerConfig(java.util.Map)

![1686306151_6482fd679bd86c46b4eeb.png!small](https://image.3001.net/images/20230609/1686306151_6482fd679bd86c46b4eeb.png!small)

将配置参数传入

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(org.apache.kafka.clients.producer.ProducerConfig,org.apache.kafka.common.serialization.Serializer

![1686306159_6482fd6f140200f9ba1c7.png!small](https://image.3001.net/images/20230609/1686306159_6482fd6f140200f9ba1c7.png!small)

赋值后调用

org.apache.kafka.clients.producer.KafkaProducer#newSender

![1686306168_6482fd783d90a3ba56593.png!small](https://image.3001.net/images/20230609/1686306168_6482fd783d90a3ba56593.png!small)

![1686306176_6482fd8010c7072b54ad0.png!small](https://image.3001.net/images/20230609/1686306176_6482fd8010c7072b54ad0.png!small)

调用到

org.apache.kafka.clients.ClientUtils#createChannelBuilder

![1686306183_6482fd879a08891c3f5ac.png!small](https://image.3001.net/images/20230609/1686306183_6482fd879a08891c3f5ac.png!small)

赋值后调用

org.apache.kafka.common.network.ChannelBuilders#clientChannelBuilder

![1686306190_6482fd8eb4611292fa358.png!small](https://image.3001.net/images/20230609/1686306190_6482fd8eb4611292fa358.png!small)

这里对值做了一个判断后调用

org.apache.kafka.common.network.ChannelBuilders#create

![1686306198_6482fd96cc7cc8ae56121.png!small](https://image.3001.net/images/20230609/1686306198_6482fd96cc7cc8ae56121.png!small)

![1686306206_6482fd9e2c14e98e8c128.png!small](https://image.3001.net/images/20230609/1686306206_6482fd9e2c14e98e8c128.png!small)

![1686306213_6482fda5b24593dec41ae.png!small](https://image.3001.net/images/20230609/1686306213_6482fda5b24593dec41ae.png!small)

Create方法中得到map型的configs后进行switch，得到SaslChannelBuilder类型channelBuilder的对象，switch结束后调用了

org.apache.kafka.common.network.SaslChannelBuilder#configure

![1686306220_6482fdace241f5525573d.png!small](https://image.3001.net/images/20230609/1686306220_6482fdace241f5525573d.png!small)

![1686306228_6482fdb4500c152112d57.png!small](https://image.3001.net/images/20230609/1686306228_6482fdb4500c152112d57.png!small)

org.apache.kafka.common.network.SaslChannelBuilder#configure

进入循环后到

org.apache.kafka.common.security.authenticator.LoginManager#acquireLoginManager

![1686306236_6482fdbcb7a8c13120add.png!small](https://image.3001.net/images/20230609/1686306236_6482fdbcb7a8c13120add.png!small)

![1686306244_6482fdc40b30e903b2b09.png!small](https://image.3001.net/images/20230609/1686306244_6482fdc40b30e903b2b09.png!small)

![1686306250_6482fdcac8d2732804dea.png!small](https://image.3001.net/images/20230609/1686306250_6482fdcac8d2732804dea.png!small)

判断值后到

org.apache.kafka.common.security.authenticator.LoginManager#LoginManager

![1686306258_6482fdd20ebbd5f3e0743.png!small](https://image.3001.net/images/20230609/1686306258_6482fdd20ebbd5f3e0743.png!small)

![1686306264_6482fdd861a83c6bf72a5.png!small](https://image.3001.net/images/20230609/1686306264_6482fdd861a83c6bf72a5.png!small)

跟进到

org.apache.kafka.common.security.authenticator.AbstractLogin#login

![1686306271_6482fddfd8a3523d03a2b.png!small](https://image.3001.net/images/20230609/1686306271_6482fddfd8a3523d03a2b.png!small)

调用

javax.security.auth.login.LoginContext#login

![1686306279_6482fde797b4f7f5ddd4b.png!small](https://image.3001.net/images/20230609/1686306279_6482fde797b4f7f5ddd4b.png!small)

调用

javax.security.auth.login.LoginContext#invokePriv

![1686306288_6482fdf04e00cd71ef464.png!small](https://image.3001.net/images/20230609/1686306288_6482fdf04e00cd71ef464.png!small)

调用

javax.security.auth.login.LoginContext#invoke

进行逻辑判断后调用initialize方法

![1686306296_6482fdf8043605e3dfbd6.png!small](https://image.3001.net/images/20230609/1686306296_6482fdf8043605e3dfbd6.png!small)

![1686306304_6482fe000e4d00c9468c3.png!small](https://image.3001.net/images/20230609/1686306304_6482fe000e4d00c9468c3.png!small)

Initialize中得到userProvider

![1686306312_6482fe08827424a5d03d7.png!small](https://image.3001.net/images/20230609/1686306312_6482fe08827424a5d03d7.png!small)

user.provider.url通过jndi提供

![1686306319_6482fe0f66efd8a625d85.png!small](https://image.3001.net/images/20230609/1686306319_6482fe0f66efd8a625d85.png!small)

调用

com.sun.security.auth.module.JndiLoginModule#login

![1686306326_6482fe16b86bb63610aa9.png!small](https://image.3001.net/images/20230609/1686306326_6482fe16b86bb63610aa9.png!small)

调用

com.sun.security.auth.module.JndiLoginModule#attemptAuthentication

![1686306334_6482fe1ebec56dc03949c.png!small](https://image.3001.net/images/20230609/1686306334_6482fe1ebec56dc03949c.png!small)

通过

javax.naming.InitialContext#lookup(java.lang.String)

执行userProvider的值

![1686306344_6482fe287ce6929e9846f.png!small](https://image.3001.net/images/20230609/1686306344_6482fe287ce6929e9846f.png!small)

![1686306352_6482fe3014b5aa33174bd.png!small](https://image.3001.net/images/20230609/1686306352_6482fe3014b5aa33174bd.png!small)

由于RASP对javax.naming.InitialContext.lookup调用做了防护策略检测，所以会在此处拦截。

Reference

  * <https://github.com/luelueking/Java-CVE-Lists#cve-2023-25194>

  * <https://blog.snert.cn/index.php/2023/04/04/cve-2023-25194-kafka-jndi-injection-%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/>

