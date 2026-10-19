**漏洞简介**

Oracle WebLogic Server是一个统一的可扩展平台，用于在本地和云端开发、部署和运行企业应用程序，例如 Java。WebLogic
Server提供了Java Enterprise Edition (EE)和Jakarta EE的可靠、成熟和可扩展的实现。

WebLogic是美商Oracle的主要产品之一，是商业市场上主要的Java应用服务器软件之一，是世界上第一个成功商业化的J2EE应用服务器，目前已推出到14c版。而此产品也延伸出WebLogic
Portal, WebLogic Integration等企业用的中间件，以及OEPE开发工具。

近日，Oracle WebLogic
Server被检测到远程代码执行漏洞(CVE-2023-21839)，该漏洞允许未经身份验证的远程攻击者通过T3/IIOP协议网络访问并破坏WebLogic服务器，成功利用此漏洞可导致关键数据的未授权访问或直接获取WebLogic服务器权限。

 **影响版本**

WebLogic_Server = 12.2.1.3.0

WebLogic_Server = 12.2.1.4.0

WebLogic_Server = 14.1.1.0.0

 **修复方案**

更新Oracle WebLogic Server官方最新补丁：

https://www.oracle.com/security-alerts/cpujan2023.html

 **环境搭建**

下载地址:

  * https://www.oracle.com/middleware/technologies/weblogic-server-downloads.html（根据官方安装说明安装即可）

  * https://github.com/vulhub/vulhub一键搭建

 **漏洞复现**

使用以下工具进行复现

  * https://github.com/4ra1n/CVE-2023-21839

  * https://github.com/WhiteHSBG/JNDIExploit

发起攻击请求：新建/tmp/1.txt文件

![](https://image.3001.net/images/20230518/1684408040_646606e80da7b7362f1dd.png!small)

![1684408046_646606ee1b1bb10e95eef.png!small](https://image.3001.net/images/20230518/1684408046_646606ee1b1bb10e95eef.png!small)

新建成功

![1684408089_64660719496cd0eb2d779.png!small](https://image.3001.net/images/20230518/1684408089_64660719496cd0eb2d779.png!small)

开启rasp后发起攻击：请求被拦截

![1684408103_646607275e80d1b72e1e3.png!small](https://image.3001.net/images/20230518/1684408103_646607275e80d1b72e1e3.png!small)

![1684408106_6466072ab8b01e67771b5.png!small](https://image.3001.net/images/20230518/1684408106_6466072ab8b01e67771b5.png!small)

堆栈信息为：

![1684408114_64660732c3f6db7c9f6b6.png!small](https://image.3001.net/images/20230518/1684408114_64660732c3f6db7c9f6b6.png!small)

 **漏洞分析**

在../wlserver/server/lib下执行java -jar wljarbuilder.jar生成wlfullclient.jar

![1684408226_646607a233499ed6d7366.png!small](https://image.3001.net/images/20230518/1684408226_646607a233499ed6d7366.png!small)

![1684408228_646607a4281105ec12a08.png!small](https://image.3001.net/images/20230518/1684408228_646607a4281105ec12a08.png!small)

![1684408232_646607a84850e45ed310c.png!small](https://image.3001.net/images/20230518/1684408232_646607a84850e45ed310c.png!small)

OpaqueReference接口的对象从 WLContext 中检索时，由 getReferent()
返回对象![1684408248_646607b84e935cf0dc0a3.png!small](https://image.3001.net/images/20230518/1684408248_646607b84e935cf0dc0a3.png!small)

当远程对象继承自OpaqueReference时，客户端在对该对象进行JNDI查找并获取的时候，服务器端实际上是通过调用远程对象的getReferent()方法来获取该对象的实际引用。

由于ForeignOpaqueReference继承OpaqueReference，所以在远程查询该对象的时候，调用的将会是ForeignOpaqueReference.getReferent方法

![1684408312_646607f8dbc04da44190f.png!small](https://image.3001.net/images/20230518/1684408312_646607f8dbc04da44190f.png!small)

在后续的进行lookup操作之前会检查 JNDI
环境是否已正确配置后访问远程资源，主要是对jndiEnvironment和remoteJNDIName进行逻辑判断。

![1684408321_64660801207cb63710624.png!small](https://image.3001.net/images/20230518/1684408321_64660801207cb63710624.png!small)

由于this.remoteJNDIName为private类可利用反射来赋值

![1684408330_6466080aa9811fe828915.png!small](https://image.3001.net/images/20230518/1684408330_6466080aa9811fe828915.png!small)

而this.jndiEnvironment只要不空，就能对InitialContext进行初始化，所以this.jndiEnvironment也可以使用反射的方式进行赋值.将jndiEnvironment和remoteJNDIName修改为期望值即可实现攻击。![1684408350_6466081e7d2430f8e49be.png!small](https://image.3001.net/images/20230518/1684408350_6466081e7d2430f8e49be.png!small)

之后即可通过retVal=context.lookup(evalMacros(this.remoteJNDIName))的实现jndi注入攻击。

![1684408362_6466082a908c53e886f82.png!small](https://image.3001.net/images/20230518/1684408362_6466082a908c53e886f82.png!small)

由于rasp探针hook了javax.naming.InitialContext.lookup的方法，当进行lookup查找jndi地址时便会直接触发拦截。

![1684408373_64660835abb7f936bdc1f.png!small](https://image.3001.net/images/20230518/1684408373_64660835abb7f936bdc1f.png!small)

 **云鲨方案**

使用云鲨RASP，无需额外配置规则，即可实现对该漏洞的天然免疫防护。

![1684408382_6466083e35c5eb7e59906.png!small](https://image.3001.net/images/20230518/1684408382_6466083e35c5eb7e59906.png!small)

 **Refrence**

https://xz.aliyun.com/t/12297

https://github.com/4ra1n/CVE-2023-21839

https://docs.oracle.com/html/E80373_03/weblogic/jndi/OpaqueReference.html

https://www.anquanke.com/post/id/287753

* * *

 **关于云鲨RASP**

悬镜云鲨RASP助力企业构建应用安全保护体系、搭建应用安全研运闭环，将积极防御能力注入业务应用中，实现应用安全自免疫。详情欢迎访问云鲨RASP官网https://rasp.xmirror.cn/

