**漏洞简介**

Apache Kafka是一个分布式数据流处理平台，可以实时发布、订阅、存储和处理数据流。Kafka
Connect是一种用于在kafka和其他系统之间可扩展、可靠的流式传输数据的工具。攻击者可以利用基于SASLJAAS 配置和SASL
协议的任意Kafka客户端，对Kafka Connect worker 创建或修改连接器时，通过构造特殊的配置，进行JNDI 注入来实现远程代码执行。

**影响版本**

2.4.0<=Apache kafka<=3.3.2

**修复方案**

更新Apache Kafka至官方最新版本

**环境搭建**

通过<https://github.com/vulhub/vulhub搭建>

**漏洞复现**

exp可参考：

<https://github.com/projectdiscovery/nuclei-templates/blob/5d90e8275084b0ae9166ec38cacd22e5a5a94fb8/http/vulnerabilities/apache/apache-druid-kafka-connect-rce.yaml>

发起攻击请求：

构造payload ,执行新建/tmp/test.txt文件

![](./img/6910302421597777036.png)

验证漏洞存在，文件新建成功

![](./img/3403865232086314811.png)

开启RASP后发起攻击：

在业务优先模式下，RASP会出现JNDI注入的告警，拦截最终的命令执行

![](./img/8251543397135122231.png)

堆栈信息为

![](./img/3735545357684822156.png)

在防护模式下将直接在JNDI注入处被拦截

![](./img/6878747253769887950.png)

堆栈信息为

![](./img/3934538533704873036.png)

**漏洞分析**

开始

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(java.util.Properties)

![](./img/8315011428291511027.png)

跟进到

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(java.util.Properties  
org.apache.kafka.common.serialization.Serializer<k>,org.apache.kafka.common.serialization.Serializer<v>)</v></k>

![](./img/4102536995713422311.png)

调用

org.apache.kafka.common.utils.Utils#propsToMap

对传入对象进行处理

![](./img/3980201886506357991.png)

将map型的对象传入

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(java.util.Map<java.lang.String,java.lang.Object>  
org.apache.kafka.common.serialization.Serializer<k>  
org.apache.kafka.common.serialization.Serializer<v>)</v></k>

![](./img/3389103808957138962.png)

之后调用

org.apache.kafka.clients.producer.ProducerConfig#appendSerializerToConfig

![](./img/648845851083740383.png)

将返回的newConfigs传入

org.apache.kafka.clients.producer.ProducerConfig#ProducerConfig(java.util.Map<java.lang.String,java.lang.Object>)

![](./img/2278224739159816805.png)

将配置参数传入

org.apache.kafka.clients.producer.KafkaProducer#KafkaProducer(org.apache.kafka.clients.producer.ProducerConfig,org.apache.kafka.common.serialization.Serializer<k>  
org.apache.kafka.common.serialization.Serializer<v>  
org.apache.kafka.clients.producer.internals.ProducerMetadata,org.apache.kafka.clients.KafkaClient  
org.apache.kafka.clients.producer.internals.ProducerInterceptors<K,V>  
org.apache.kafka.common.utils.Time)</v></k>

![](./img/665576465752458133.png)

赋值后调用

org.apache.kafka.clients.producer.KafkaProducer#newSender

![](./img/1943767652850739557.png)

![](./img/6744342647006680036.png)

调用到

org.apache.kafka.clients.ClientUtils#createChannelBuilder

![](./img/3844291821488956138.png)

赋值后调用

org.apache.kafka.common.network.ChannelBuilders#clientChannelBuilder

![](./img/6606038898370216614.png)

这里对值做了一个判断后调用

org.apache.kafka.common.network.ChannelBuilders#create

![](./img/3209413240503539767.png)

![](./img/761855077386698691.png)

![](./img/2241090771353556363.png)

Create方法中得到map型的configs后进行switch，得到SaslChannelBuilder类型channelBuilder的对象，switch结束后调用了

org.apache.kafka.common.network.SaslChannelBuilder#configure

![](./img/1661112109008575253.png)

![](./img/897493818244547892.png)

org.apache.kafka.common.network.SaslChannelBuilder#configure

进入循环后到

org.apache.kafka.common.security.authenticator.LoginManager#acquireLoginManager

![](./img/4076553792178713206.png)

![](./img/7365927234560830390.png)

![](./img/7246026854741363713.png)

判断值后到

org.apache.kafka.common.security.authenticator.LoginManager#LoginManager

![](./img/5666437199977910311.png)

![](./img/7767389856037859542.png)

跟进到

org.apache.kafka.common.security.authenticator.AbstractLogin#login

![](./img/3008540119122983554.png)

调用

javax.security.auth.login.LoginContext#login

![](./img/6779959842590543009.png)

调用

javax.security.auth.login.LoginContext#invokePriv

![](./img/8013078386933179518.png)

调用

javax.security.auth.login.LoginContext#invoke

进行逻辑判断后调用initialize方法

![](./img/5317625345732974832.png)

![](./img/862067315191580221.png)

Initialize中得到userProvider

![](./img/4049816124702826351.png)

user.provider.url通过jndi提供

![](./img/596251860117281144.png)

调用

com.sun.security.auth.module.JndiLoginModule#login

![](./img/4838858475347879655.png)

调用

com.sun.security.auth.module.JndiLoginModule#attemptAuthentication

![](./img/6932885292226839083.png)

通过

javax.naming.InitialContext#lookup(java.lang.String)

执行userProvider的值

![](./img/4884201183608162999.png)

![](./img/5282072904152270765.png)

由于RASP对javax.naming.InitialContext.lookup调用做了防护策略检测，所以会在此处拦截。

**Reference**

<https://github.com/luelueking/Java-CVE-Lists#cve-2023-25194>

<https://blog.snert.cn/index.php/2023/04/04/cve-2023-25194-kafka-jndi-injection-%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/>

