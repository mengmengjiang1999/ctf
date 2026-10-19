**作者：Seaer@深信服千里目安全实验室  
原文链接：<https://mp.weixin.qq.com/s/j_gx9C_xL1LyrnuFFPFsfg>**

## 1 组件介绍

Apache
Shiro是一个功能强大且易于使用的Java安全框架，功能包括身份验证，授权，加密和会话管理。使用Shiro的API，可以轻松地快速地保护任何应用程序，范围包括小型的移动应用程序到大型的Web和企业应用程序。以下是Shiro的结构图。
![](https://images.seebug.org/content/images/2020/10/2ec5d8e4-7b44-4cc1-8d30-7297670c1301.png-w331s)

Shiro提供了应用安全API(被Shiro框架开发团队成为安全四大基石的Authentication（认证）, Authorization（授权）,
Session Management（会话管理）, Cryptography（加密）)

  * Authentication（认证）： 证明用户身份，通常称之为“登录”。
  * Authorization（授权） ： 访问控制。
  * Cryptography（加密） ： 保护或隐藏数据，防止数据被窃取。
  * Session Management（会话管理） ： 管理每一个用户的会话状态。

在概念层，Shiro 架构包含三个主要的理念：Subject,SecurityManager和 Realm。

  * Subject：当前用户，Subject 可以是一个人，但也可以是第三方服务、守护进程帐户、时钟守护任务或者其它–当前和软件交互的任何事件。
  * SecurityManager：管理所有Subject，SecurityManager 是 Shiro 架构的核心，配合内部安全组件共同组成安全伞。
  * Realms：用于进行权限信息的验证，我们自己实现。Realm 本质上是一个特定的安全 DAO：它封装与数据源连接的细节，得到Shiro 所需的相关的数据。在配置 Shiro 的时候，你必须指定至少一个Realm 来实现认证（authentication）和/或授权（authorization）。

![](https://images.seebug.org/content/images/2020/10/7ddc6bac-f9fb-464d-9e6c-90de73b36a3e.png-w331s)
（数据来源：[ZoomEye](https://www.zoomeye.org/))
上图是Shiro组件在国内的使用量统计图。通过网络空间搜索引擎的数据统计，绘制柱状图表。Shiro
在国内有着近5千个的站点分布，其中以浙江、北京、广东等为主要地区。

## 2 高危漏洞介绍

漏洞名称 | 漏洞ID | 影响版本 | CVSS  
---|---|---|---  
Apache Shiro 1.2.4反序列化远程代码执行漏洞 | CVE-2016-4437/SHIRO-550 | Apache Shiro <=
1.2.4 | 8.1  
Apache Shiro Padding Oracle Attack 远程代码执行漏洞 | CVE-2019-12422/SHIRO-721 |
Apache Shiro < 1.4.2 | 7.5  
Apache Shiro 身份验证绕过漏洞 | CVE-2020-1957/SHIRO-682 | Apache Shiro < 1.5.2 | 9.8  
Apache Shiro 身份验证绕过漏洞 | CVE-2020-11989/SHIRO-782 | Apache Shiro < 1.5.3 | 9.8  
Apache Shiro 身份验证绕过漏洞 | CVE-2020-13933 | Apache Shiro < 1.6.0 | 7.5  
Apache Shiro 身份验证绕过漏洞（AJP协议绕过） | SHIRO-760 | 基于Tomcat版本 | 无  
Apache Shiro < 1.2.3 身份验证绕过漏洞 | CVE-2014-0074/SHIRO-460 | Apache Shiro < 1.2.3
| 7.5  
  
Shiro组件漏洞主要分为两种类型，一种是java反序列化造成的远程代码执行漏洞，另一种是身份验证绕过漏洞。在官方对rememberMe字段反序列化进行秘钥随机化，AES加密模式更换后，暂无新型反序列化漏洞的出现。但是在身份验证绕过的补丁修复上，多次出现绕过情况，多是由于补丁修复过程中考虑不周全。Shiro在今年上半年爆出了三个较为严重的身份验证绕过的漏洞，且影响版本较新，用户需要重点关注。

## 3 漏洞利用链

### 3.1 组件风险梳理

根据Shiro组件的漏洞，结合敏感配置的梳理，得到如下风险梳理的思维导图。
![](https://images.seebug.org/content/images/2020/10/49e8911f-6936-4429-8213-5d369fafd193.png-w331s)

### 3.2 利用链总结

基于风险梳理思维导图，总结出2种可行的漏洞利用链。

#### 3.2.1 无权限 -> GetShell

![](https://images.seebug.org/content/images/2020/10/b8defc71-beac-4eb3-8a7b-78c4aefa4c86.png-w331s)

Apache Shiro
1.2.4反序列化远程代码执行漏洞单独使用，即可完成GetShell。此漏洞利用前提是获取AES加密秘钥。一般情况，Shiro组件默认没有被更换，可以直接利用此漏洞。如果出现秘钥被更换，此漏洞需要结合任意文件读取或者任意文件下载，先获取到AES加密秘钥，再进行漏洞利用。

#### 3.2.2 普通权限 -> GetShell

![](https://images.seebug.org/content/images/2020/10/da932f10-a64e-4c9d-ad5c-beaadcf24319.png-w331s)

Apache Shiro Padding Oracle Attack
远程代码执行漏洞单独使用，即可完成GetShell。此漏洞利用前提需要获得一个正确的用户Cookie值，利用此漏洞进行GetShell至少要获取一个普通用户权限。

## 4 高可利用漏洞分析

从高危漏洞列表中，针对部分近年高可利用漏洞进行漏洞深入分析。  
Shiro组件漏洞分为两个种类：java反序列化漏洞、身份验证绕过漏洞。本章节重点进行两个类别的漏洞分析。

### 4.1 java反序列化漏洞

**技术背景**

**Java反序列化漏洞原理：** Java
提供了一种对象序列化的机制，该机制中，一个对象可以被表示为一个字节序列，该字节序列包括该对象的数据、有关对象的类型的信息和存储在对象中数据的类型。Java反序列化则是从一个源输入流中读取字节序列，再把它们反序列化为一个对象，并将其返回。Java反序列化漏洞的成因是攻击者通过序列化函数将自己精心构造的恶意对象序列化，将序列化数据发送到目标服务器的反序列化接口，当服务器在没有对序列化数据进行有效的安全验证，直接对序列化数据进行反序列化处理，执行恶意对象中的代码，造成攻击。

**AES加密算法：** 使用Rijndael分组密码算法，属于对称加密。  
AES加密算法涉及4种操作：字节替代（SubBytes）、行移位（ShiftRows）、列混淆（MixColumns）和轮密钥加（AddRoundKey）。  
总体加密流程：
![](https://images.seebug.org/content/images/2020/10/916e27fe-67ae-466e-8794-b2a7ca64d2a4.png-w331s)

  * 字节替代（SubBytes）  
字节代替的主要功能是通过S盒完成一个字节到另外一个字节的映射。  
![](https://images.seebug.org/content/images/2020/10/8f51be5e-ec2a-4aa8-824d-baae7414df9b.png-w331s)
解密使用S盒的逆进行还原。  
![](https://images.seebug.org/content/images/2020/10/70c68efb-e822-4b34-b03f-97520f97d661.png-w331s)

  * 行移位（ShiftRows）  
行移位是一个4x4的矩阵内部字节之间的置换，用于提供算法的扩散性。  
正向行移位：正向行移位用于加密，其原理图如下。其中：第一行保持不变，第二行循环左移8比特，第三行循环左移16比特，第四行循环左移24比特。  
![](https://images.seebug.org/content/images/2020/10/f0e274ed-c46b-436e-8ead-d0733828b484.png-w331s)
解密使用逆向行移位：第一行保持不变，第二行循环右移8比特，第三行循环右移16比特，第四行循环右移24比特。  

  * 列混淆（MixColumns）  
将行移位得到的新的4x4矩阵，与另一个矩阵进行左乘运算，更改每一列的数值。
![](https://images.seebug.org/content/images/2020/10/27b40d42-da2e-4f24-8f16-2283e29e1396.png-w331s)

解密时，左乘与之前选取的中间矩阵的互逆矩阵，即可还原。  
![](https://images.seebug.org/content/images/2020/10/5e2c1b38-07e5-458c-8e9a-c0ad1d70f2ac.png-w331s)

  * 轮密钥加（AddRoundKey）  
加密过程中，每轮的输入与轮子密钥异或一次。  
解密过程，由于任何数和自身的异或结果为0，因此，解密时再异或上该轮的轮子密钥即可恢复。

**AES CBC模式**

  * 加密![](https://images.seebug.org/content/images/2020/10/5b2d4249-b6a5-441f-8fab-0ae9ff29f735.png-w331s)
  * 解密![](https://images.seebug.org/content/images/2020/10/5b93f1cf-6b47-49fd-be74-529629cd0f36.png-w331s)

#### 4.1.1 Apache Shiro 1.2.4反序列化远程代码执行漏洞

**1 漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：Apache Shiro 1.2.4 Deserialize Remote Code Execution Vulnerability
  * 漏洞编号：CVE-2016-4437
  * 漏洞类型：远程代码执行
  * CVSS评分：【CVSS v2.0：6.8】【CVSS v3.0：8.1】
  * 漏洞危害等级：高危

**1.2 漏洞概述**

Apache Shiro
1.2.5之前的版本在`org.apache.shiro.mgt.AbstractRememberMeManager`中存在AES默认秘钥`kPH+bIxk5D2deZiIxcaaaA==`，开启RememberMe功能的shiro组件将允许远程攻击者构造序列化数据，在目标服务器上执行任意命令。

**1.3 漏洞利用条件**

  * 已知 Shiro AES 解密密钥。
  * 开启RememberMe功能。

**1.4 漏洞影响**

影响版本：  
Apache Shiro <= 1.2.4

**1.5 漏洞修复**

获取Apache Shiro最新版本，下载链接：<https://shiro.apache.org/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/10/10c9095f-45e4-46eb-9161-68439e6966f0.png-w331s)

**2.2 应用协议**

8080/HTTP

**2.3 复现过程**

基于Windows平台，使用`环境`目录下的`shirodemo-1.0-SNAPSHOT.jar`环境，执行`java -jar
shirodemo-1.0-SNAPSHOT.jar`启动环境。效果如图
![](https://images.seebug.org/content/images/2020/10/a5622e57-5199-410c-86e7-8a9dab5ecb4c.png-w331s)

运行`sniper`工具箱，填写表单信息，输入`ipconfig`命令，点击Attack，效果如图。  

**有回显信息的exp插件**

![](https://images.seebug.org/content/images/2020/10/743a025a-1ab6-4757-8fc5-2db23b31d9b1.png-w331s)

**无回显信息的exp插件**

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 漏洞利用过程**

使用ysoserial生成存在恶意命令的反序列化payload。使用AES默认秘钥，生成的payload进行`AES/CBC/PKCS5Padding`模式加密，将加密后的结果传入到HTTP头部Cookie字段的rememberMe参数，通过HTTP协议发起请求。

注：由于Shiro重写了resolveClass方法，将原生方法中的forName方法替换为loadClass方法，由于loadClass无法加载数组类型的类，因此存在Transformer[]类的CommonCollections
gadget无法成功利用此漏洞，（例如ysoserial CommonCollections1、CommonCollections3）
![](https://images.seebug.org/content/images/2020/10/59663758-1c8e-4c2e-8f2e-b1b1bc6ebad4.png-w331s)
![](https://images.seebug.org/content/images/2020/10/2c871bd8-4925-4761-90b4-10c98e4e54d0.png-w331s)

**3.1.2 代码分析**

传入的payload首先被服务器接收，并传送给Shiro拦截器处理(org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter方法作为入口)  
![](https://images.seebug.org/content/images/2020/10/2672e9f5-3348-46d8-ac73-49ec8c87dbfb.png-w331s)

调用createSubject方法创建Subject  
![](https://images.seebug.org/content/images/2020/10/32d83ca0-33e5-4f0e-92a6-9a38444810f4.png-w331s)

在org.apache.shiro.mgt.DefaultSecurityManager#getRememberedIdentity方法调用getRememberedSerializedIdentity方法获取rememberMe认证的序列化数据。  
![](https://images.seebug.org/content/images/2020/10/986449f0-ecb8-43da-b899-36d871491cf2.png-w331s)
![](https://images.seebug.org/content/images/2020/10/8caf61c0-b679-4549-b6f3-ea90557d851e.png-w331s)

在此方法中可以获取传入的HTTP请求，响应数据，并解析获取http请求中的cookie字段值(payload所在字段)(base64形式)。
![](https://images.seebug.org/content/images/2020/10/d7b283ad-e06f-4b5e-a3ad-1f425bd7f02a.png-w331s)

并在后续的程序中进行base64解码，将解码后的byte流存储在decoded变量中，作为后续进行AES解密的密文。  
![](https://images.seebug.org/content/images/2020/10/76181e8f-be08-453b-9d67-f4b33bd4a922.png-w331s)

返回的密文数据流将会在org.apache.shiro.crypto.JcaCipherService#decrypt方法中完成AES解密操作。  
![](https://images.seebug.org/content/images/2020/10/e98bbc65-f265-453b-9772-c905fc05e04b.png-w331s)
![](https://images.seebug.org/content/images/2020/10/93e8fe68-f75b-4f4a-832f-2013ce362c57.png-w331s)
![](https://images.seebug.org/content/images/2020/10/24e19f6e-e45b-4020-9829-f2e960f29aff.png-w331s)

获得的AES解密后的明文将在org.apache.shiro.web.mgt.AbstractRememberMeManager#deserialize方法中反序列化，执行其中的恶意代码。  
![](https://images.seebug.org/content/images/2020/10/6b5e0251-5d71-4f4e-ba89-a67d7ba931d7.png-w331s)

**3.1.3 漏洞触发过程**

![](https://images.seebug.org/content/images/2020/10/51632744-8e2a-4225-94ce-897f743ccba2.png-w331s)

**3.1.4补丁分析**

对比Shiro
1.2.4与1.2.5版本的改动，在org.apache.shiro.mgt.AbstractRememberMeManager类中声明秘钥的方式，从原来的硬编码更改为自动生成秘钥。  
![](https://images.seebug.org/content/images/2020/10/01bb139c-4379-4f1e-89d3-21f3c0022642.png-w331s)
![](https://images.seebug.org/content/images/2020/10/7b8957cd-742c-475c-bdf0-9351690bb258.png-w331s)

新版本中调用generateNewKey方法进行秘钥生成，通过传入秘钥长度，根据传入的长度参数，返回对应长度的随机秘钥。  
![](https://images.seebug.org/content/images/2020/10/d4bb5723-63cb-4a03-b257-97185038db92.png-w331s)

由于秘钥的随机性，使攻击者无法轻易的通过使用秘钥加密恶意序列化数据的方式进行攻击，从而修复了此漏洞。

#### 4.1.2 Apache Shiro Padding Oracle Attack 远程代码执行漏洞

**1.漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：Apache Shiro Padding Oracle Attack Remote Code Execution Vulnerability
  * 漏洞编号：CVE-2019-12422
  * 漏洞类型：远程代码执行
  * CVSS评分：【CVSS v2.0：5.0】【CVSS v3.1：7.5】
  * 漏洞危害等级：高危

**1.2 漏洞概述**

Apache Shiro
1.4.2之前的版本默认使用AES/CBC/PKCS5Padding模式加密,开启RememberMe功能的Shiro组件将允许远程攻击者构造序列化数据，通过Padding
Oracle Attack进行爆破，即使在秘钥未知的条件下，也可以在目标服务器上执行任意命令。

**1.3 漏洞利用条件**

  * 使用AES CBC模式。
  * 开启RememberMe功能。
  * 密文可控。
  * 获取到正常Cookie。

**1.4 漏洞影响**

影响版本：  
Apache Shiro < 1.4.2

**1.5 漏洞修复**

获取Apache Shiro最新版本，下载链接：https://shiro.apache.org/download.html

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/10/dd6531c5-2551-4d7f-b906-17479155a9a5.png-w331s)

**2.2 应用协议**

8080/HTTP

**2.3 复现过程**

基于Windows平台，使用`环境`目录下的`apache-tomcat-8.5.2`环境，进入bin目录下运行`startup.bat`，linux环境运行`startup.sh`启动环境。效果如图  
![](https://images.seebug.org/content/images/2020/10/a741197e-1e38-4c8d-a858-6af315c00dc3.png-w331s)
![](https://images.seebug.org/content/images/2020/10/33ab2be6-1ae6-459b-b2bf-182f8726f86b.png-w331s)

运行`sniper`工具箱，填写表单信息，点击Attack，效果如图。  
![]![](https://images.seebug.org/content/images/2020/10/ad58d84a-8750-445c-ba71-63f8317dbef7.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

3.1.1 漏洞利用过程

使用ysoserial生成存在恶意命令的反序列化payload。获取一个用户的Cookie字段值(可以获取普通用户的Cookie)。取出rememberMe字段值，通过逐位爆破，构造正常padding数据，最终将每一块构造的block拼接在一起，形成任意构造的明文gadget加密后的密文。

注：由于Shiro重写了resolveClass方法，将原生方法中的forName方法替换为loadClass方法，由于loadClass无法加载数组类型的类，因此存在Transformer[]类的CommonCollections
gadget无法成功利用此漏洞，（例如ysoserial CommonCollections1、CommonCollections3）
![](https://images.seebug.org/content/images/2020/10/94b44ff5-e75f-4547-a9e3-1b918b52ad99.png-w331s)
![](https://images.seebug.org/content/images/2020/10/099ecb63-8e97-408e-b196-cdaa19fd6e91.png-w331s)

**3.1.2 代码分析**

CVE-2019-12422进行反序列化攻击的原理与CVE-2016-4437漏洞原理一致，而由于Shiro在1.2.4以上的版本已经将硬编码秘钥更换为随机生成的秘钥，因此无法获取到AES加密秘钥。CVE-2019-12422漏洞利用了AES
CBC模式加密的漏洞，绕过了使用AES秘钥加密明文gadget的前提条件。具体原理如下：  
在进行AES解密时，会对生成的明文进行padding校验，在com.sun.crypto.provider.CipherCore#doFinal中获取padding长度
![](https://images.seebug.org/content/images/2020/10/0324ed87-6199-47b0-8d92-d25a62539357.png-w331s)

com.sun.crypto.provider.PKCS5Padding#unpad方法进行padding检测，如果检测失败，返回-1状态码
![](https://images.seebug.org/content/images/2020/10/41e36d26-a32a-4f14-9bba-e73e1790ff38.png-w331s)

当校验失败时，com.sun.crypto.provider.CipherCore#doFinal方法抛出异常
![](https://images.seebug.org/content/images/2020/10/1ede914f-5215-43af-b4d4-75ce0b1cffa2.png-w331s)
最终程序走到org.apache.shiro.web.servlet#removeFrom方法中，构造响应信息，进行回显。在代码中可以看见padding失败后会回显rememberMe
deleteMe等特征字符串。可以作为padding oracle attack回显特征进行爆破。
![](https://images.seebug.org/content/images/2020/10/a4647666-7305-45c9-8585-e1f1282006d1.png-w331s)

攻击者可以凭借此特征，分组爆破。由于AES CBC模式解密时会将前一块的密文作为本轮解密的IV值，当密文可控时，可以逐位爆破前一块密文，根据padding
error的回显不同，获取padding字符为\x10*16的IV'值。  
IV ^ middle = 16 * \x10  
IV' ^ middle = 构造gadget密文块  
IV' = 构造gadget密文块 ^ 16 * \x10 ^IV  
根据公式，循环获取所有密文块。通过这种方式，获取任意明文对应的密文。

**3.1.3 漏洞触发过程**

![](https://images.seebug.org/content/images/2020/10/2b72fc70-fefa-4bf3-8925-adcc21744220.png-w331s)

**3.1.4补丁分析**

对比Shiro
1.4.1与1.4.2版本的改动，在org.apache.shiro.crypto.AesCipherService类中声明AES加密的模式，从原来的CBC模式更改为GCM模式。
![](https://images.seebug.org/content/images/2020/10/838c10be-e274-4725-856b-73eb3b036100.png-w331s)

由于AES加密模式更换，攻击者无法使用padding oracle attack进行攻击，从而修复了此漏洞。

### **4.2 身份验证绕过漏洞**

**技术背景**

**拦截器和过滤器的详细区别**

Filter | Interceptor | Summary  
---|---|---  
Filter 接口定义在 javax.servlet 包中 | 接口 HandlerInterceptor
定义在org.springframework.web.servlet 包中 |  
Filter 定义在 web.xml 中 |  |  
Filter在只在 Servlet 前后起作用。Filters 通常将 请求和响应（request/response） 当做黑盒子，Filter
通常不考虑servlet 的实现。 | 拦截器能够深入到方法前后、异常抛出前后等，因此拦截器的使用具有更大的弹性。允许用户介入（hook
into）请求的生命周期，在请求过程中获取信息，Interceptor 通常和请求更加耦合。 | 在Spring构架的程序中，要优先使用拦截器。几乎所有
Filter 能够做的事情， interceptor 都能够轻松的实现[
](http://einverne.github.io/post/2017/08/spring-interceptor-vs-filter.html#fn:top)  
Filter 是 Servlet 规范规定的。 | 而拦截器既可以用于Web程序，也可以用于Application、Swing程序中。 | 使用范围不同  
Filter 是在 Servlet 规范中定义的，是 Servlet 容器支持的。 | 而拦截器是在 Spring容器内的，是Spring框架支持的。 |
规范不同  
Filter 不能够使用 Spring 容器资源 |
拦截器是一个Spring的组件，归Spring管理，配置在Spring文件中，因此能使用Spring里的任何资源、对象，例如
Service对象、数据源、事务管理等，通过IoC注入到拦截器即可 | Spring 中使用 interceptor 更容易  
Filter 是被 Server(like Tomcat) 调用 | Interceptor 是被 Spring 调用 | 因此
Filter总是优先于interceptor执行  
  
**拦截器和过滤器的执行顺序**
![](https://images.seebug.org/content/images/2020/10/dba099b1-f01b-4ec9-90a3-04dad1b9c519.png-w331s)

**Shiro拦截器：**
![](https://images.seebug.org/content/images/2020/10/9b4a7ccc-0e49-4d8b-8b94-260558d5dbef.png-w331s)

NameableFilter: NameableFilter给Filter起个名字，如果没有设置默认就是`FilterName`

当我们组装拦截器链时会根据这个名字找到相应的拦截器实例  
OncePerRequestFilter:
用于防止多次执行Filter,一次请求只会走一次Filter链。`enabled`属性:是否开启该拦截器，默认`enabled=true`表示开启  
ShiroFilter: 整个Shiro的入口点，用于拦截需要安全控制的请求进行处理。  
AdviceFilter: 提供AOP风格的支持，类似于SpringMVC中的`Interceptor`。  
PathMatchingFilter:
提供基于Ant风格的请求路径匹配功能及拦截器参数解析的功能，如`roles[admin,user]`自动根据`,`分割解析到一个路径参数配置并绑定到相应的路径。  
AccessControlFilter:
提供访问控制的基础功能，比如是否允许访问/当访问拒绝时如何处理等。isAccessAllowed表示是否允许访问；mappedValue就是[urls]配置中拦截器参数部分，如果允许访问返回true，否则false。onAccessDenied
表当访问拒绝时是否已经处理，如果返回true表示需要继续处理，如果返回false表示该拦截器实例已经处理了，直接返回即可。
![](https://images.seebug.org/content/images/2020/10/4d5dde58-79fc-47a6-86f8-d12c02f29ff0.png-w331s)

#### 4.2.1 Apache Shiro 身份验证绕过漏洞

**1.漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：Apache Shiro Authentication Bypass Vulnerability
  * 漏洞编号：CVE-2020-1957
  * 漏洞类型：Authentication Bypass
  * CVSS评分：【CVSS v2.0：7.5】【CVSS v3.1：9.8】
  * 漏洞危害等级：高危

**1.2 漏洞概述**

Apache Shiro
1.5.2之前的版本，由于Shiro拦截器与requestURI的匹配流程与Web框架的拦截器的匹配流程有差异，攻击者构造一个特殊的http请求，可以绕过Shiro的认证，未授权访问敏感路径。此漏洞有两种攻击方式，第一种攻击方式适用于Shiro
< 1.5.0版本，由于Shiro 1.5.0版本修复补丁考虑不全面，导致补丁绕过，出现了第二种攻击方式，适用于Shiro < 1.5.2版本。

**1.3 漏洞利用条件**

  * 无

**1.4 漏洞影响**

影响版本：  
Apache Shiro < 1.6.0

**1.5 漏洞修复**

获取Apache Shiro最新版本，下载链接：<https://shiro.apache.org/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/10/bc68cafd-099e-43f9-93f1-f570de880eca.png-w331s)

**2.2 应用协议**

8080/HTTP

**2.3 复现过程**

基于Windows平台，使用`环境`目录下的`shiro-basic.zip`环境，解压后，用Idea打开shiro-basic文件夹，下载maven资源，运行ShiroBasicApplication类，即可启动环境。效果如图。  
![](https://images.seebug.org/content/images/2020/10/a3f85968-b6f5-4e90-90d8-2aa1edad9ea0.png-w331s)

**Shiro < 1.5.0**  
构造HTTP请求，发送到服务器，完成身份验证绕过，效果如图
![](https://images.seebug.org/content/images/2020/10/2d831c8e-5338-4fbe-923c-19a1c252a3be.png-w331s)
![](https://images.seebug.org/content/images/2020/10/c0f1d567-99fb-4831-a9df-7f14885bd790.png-w331s)

**Shiro < 1.5.2**
![](https://images.seebug.org/content/images/2020/10/328250cd-028a-4400-8291-a69b2445b567.png-w331s)
![](https://images.seebug.org/content/images/2020/10/a5ec2782-c9b1-4740-8fd7-bfcbfccf98e0.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 漏洞利用过程**

**Shiro < 1.5.0**  
获取到无权限访问的敏感路径，在路径的结尾添加`/`进行身份验证绕过。

**Shiro < 1.5.2**  
获取到无权限访问的敏感路径，在auth认证路径中的添加`;`进行身份验证绕过。

**3.1.2 代码分析**

**Shiro < 1.5.0**  
传入的payload首先被服务器接收，并传送给Shiro拦截器处理(org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter方法作为入口)。  
![](https://images.seebug.org/content/images/2020/10/f98890c8-62f2-4a1e-bd58-59190538fe3a.png-w331s)

调用createSubject方法创建Subject，并调用execute方法进入Shiro FilterChain中。
![](https://images.seebug.org/content/images/2020/10/2c0a6ef1-d599-4f65-b5dc-1158389c0c29.png-w331s)
![](https://images.seebug.org/content/images/2020/10/6a480c5a-7fea-4232-9b48-23f090639315.png-w331s)

进入org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain方法中，首先获取请求uri路径，之后迭代获取拦截器的表达式。
![](https://images.seebug.org/content/images/2020/10/962ed1e2-da6f-436f-9ada-56971d49ceca.png-w331s)
![](https://images.seebug.org/content/images/2020/10/a9aa93e9-23f7-4809-a3d6-dfc419b115bd.png-w331s)

这里我们重点关注`/hello/*`表达式。代码进入pathMatches方法，最终调用org.apache.shiro.util.AntPathMatcher#doMatch方法进行传入的requestURI与拦截器表达式进行匹配。
![](https://images.seebug.org/content/images/2020/10/7d4d8e23-3e9b-42b5-9582-11eedc12b556.png-w331s)
匹配过程中，分别将拦截器表达式与requestURI以`/`作为分隔符进行字符串到数组的转换，通过循环匹配数组中对应的元素，判断requestURI是否符合拦截器表达式匹配形式。
![](https://images.seebug.org/content/images/2020/10/5b4cf409-cbd7-47a1-ae17-cccd7b1ea833.png-w331s)

如果表达式中存在通配符`*`，会将containsStar标志位赋值为true，进入 `else if (patIdxEnd ==
0)`判断条件，返回true。
![](https://images.seebug.org/content/images/2020/10/1e131227-17e3-4da2-b95c-0501aa7be3fe.png-w331s)

继续跟进代码，在requestURI与拦截器表达式匹配结束后，还会进行一次判断，而漏洞产生的原因也是由于判断的条件。如果Shiro拦截器表达式不以`/`结尾，且requestURI以`/`结尾，判断代码将返回false表示匹配失败，从而绕过Shiro认证。
![](https://images.seebug.org/content/images/2020/10/508d7041-74ee-4b51-b434-9fb44639e34f.png-w331s)

跟进到Spring处理URI的代码，进入org.springframework.web.servlet.handler.AbstractHandlerMethodMapping#getHandlerInternal方法，获取requestURI。
![](https://images.seebug.org/content/images/2020/10/5175da18-c007-4515-8249-4a3aef8ecd78.png-w331s)

进入lookupHandlerMethod方法，调用addMatchingMappings方法，获取Spring拦截器。
![](https://images.seebug.org/content/images/2020/10/744d96da-a367-4510-8a9c-19bf19925f5d.png-w331s)
![](https://images.seebug.org/content/images/2020/10/4a36f7d2-4e3c-43b7-90f5-3c794b9c71e4.png-w331s)

进入org.springframework.web.servlet.mvc.condition.PatternsRequestCondition#getMatchingCondition方法调用doMatch方法进行requestURI和拦截器表达式的匹配。
![](https://images.seebug.org/content/images/2020/10/4fd403ae-3ae1-42d4-9823-fa6425013353.png-w331s)
![](https://images.seebug.org/content/images/2020/10/49d837fd-9b25-479f-850e-d14e2c23aee0.png-w331s)

Spring拦截器匹配流程和Shiro大致相同，都是将字符串转换为数组进行匹配。
![](https://images.seebug.org/content/images/2020/10/fea7d381-ad91-4be9-ac4f-f82864688d87.png-w331s)
![](https://images.seebug.org/content/images/2020/10/e88fc614-7f44-486c-9e3e-6cdd97e01e07.png-w331s)

由于Spring多了一个环节，在检测拦截器表达式与requestURI结尾是否为`/`之后，并没有直接返回false。而是将拦截器表达式结尾添加`/`，并继续进行`path.startsWith(this.pathSeparator)
!= pattern.startsWith(this.pathSeparator)`测试，从而完成了拦截器表达式与requestURI的匹配。
![](https://images.seebug.org/content/images/2020/10/bcb1bfb4-45ba-450c-9143-e5b805d92aff.png-w331s)
![](https://images.seebug.org/content/images/2020/10/2308e24b-269d-4bd8-a3ec-01488f3e3542.png-w331s)
上述攻击方式在Shiro 1.5.0版本中修复，但是被二次绕过，绕过分析如下。

**Shiro < 1.5.2**  
Shiro 1.5.0 -1.5.1在认证过程中基本没有变化，主要分析一下二次绕过的利用点。还是以org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain作为起点。![](https://images.seebug.org/content/images/2020/10/dccc0634-5703-4fdd-97e0-dc9bb523e3ae.png-w331s)

在获取requestURI时,依旧会在getPathWithinApplication方法中调用getRequestUri方法进行requestURI的解析并获取，但是在URI正规化处理时，先调用decodeAndCleanUriString方法进行路径的解码，并清理URI。
![](https://images.seebug.org/content/images/2020/10/4791b48a-496c-44e3-85ca-70905ce43288.png-w331s)
![](https://images.seebug.org/content/images/2020/10/2e40c388-7362-4b37-bb5b-edc4a78f8f6e.png-w331s)

进入decodeAndCleanUriString方法，发现此方法会以分号将传入的URI进行截断，并将分号以及分号后面的数据进行清空，返回分号前面的URI数据，从而让`/a/b;/c`变为/a/b。

继续跟进到Spring拦截器的decodeAndCleanUriString方法中
![](https://images.seebug.org/content/images/2020/10/572aa0bb-de2d-4b5d-9b98-79afa107fde4.png-w331s)
![](https://images.seebug.org/content/images/2020/10/a14ba9d6-d541-474e-8ece-a50a2aa2b326.png-w331s)

从代码中可以发现，Spring对于分号处理的方式与Shiro不同，Spring会先获取分号的位置，并检测分号后是否存在`/`，如果有，将`/`的位置记录在slashIndex变量中，并将分号前的数据与`/`之后的数据进行拼接，从而让`/a/b;/c`变为`/a/b/c`。返回处理后的requestURI。

由于Spring与Shiro的decodeAndCleanUriString方法不同，攻击者可以使用分号构造路径，绕过Shiro认证，并可以匹配Spring的动态控制器。

**3.1.3 漏洞触发过程**

**Shiro < 1.5.0**

![](https://images.seebug.org/content/images/2020/10/6c520efe-b4f0-430d-bd2e-4672595419c7.png-w331s)

**Shiro < 1.5.2**
![](https://images.seebug.org/content/images/2020/10/c68504dc-f12f-42e3-8a64-0a4fc1315788.png-w331s)

**3.1.4补丁分析**

对比Shiro 1.4.2与Shiro
1.5.0版本的改动，在org.apache.shiro.web.filter.PathMatchingFilter类中添加了删除requestURI结尾的`/`的代码。
![](https://images.seebug.org/content/images/2020/10/a3fc8828-e342-43f3-acfd-d1cad3772fcf.png-w331s)
![](https://images.seebug.org/content/images/2020/10/2f8e0fd8-7a04-45e6-95db-8f8a17c0e5ce.png-w331s)

由于requestURI和拦截器表达式结尾的`/`都会被清除，因此防御了此漏洞。

对比Shiro 1.5.1与Shiro 1.5.2版本的改动
![](https://images.seebug.org/content/images/2020/10/138bcc7e-f0fc-464f-a8dd-d939d30220df.png-w331s)
由于Shiro
1.5.2版本中，在进行decodeAndCleanUriString方法之前会先进行uri解析，调用request.getServletPath()和request.getPathInfo()获取ServletPath
和PathInfo 并进行路径拼接，避开了decodeAndCleanUriString对于分号的处理，从而修复了此漏洞。

#### 4.2.2 Apache Shiro 身份验证绕过漏洞

**1.漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：Apache Shiro Authentication Bypass Vulnerability
  * 漏洞编号：CVE-2020-11989
  * 漏洞类型：Authentication Bypass
  * CVSS评分：【CVSS v2.0：7.5】【CVSS v3.1：9.8】
  * 漏洞危害等级：高危

**1.2 漏洞概述**

Apache Shiro
1.5.3之前的版本，由于Shiro拦截器与requestURI的匹配流程与Web框架的拦截器的匹配流程有差异，攻击者构造一个特殊的http请求，可以绕过Shiro的认证，未授权访问敏感路径。此漏洞存在两种攻击方式。

**1.3 漏洞利用条件**

**First Attack**

  * 无

**Second Attack**

  * 应用不能部署在根目录（1.5.1 < Shiro < 1.5.3）

**1.4 漏洞影响**

影响版本：  
Apache Shiro < 1.5.3

**1.5 漏洞修复**

获取Apache Shiro最新版本，下载链接：<https://shiro.apache.org/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/10/1f8b6f65-a5b3-45f0-a26c-823389ca85b7.png-w331s)

**2.2 应用协议**

8080/HTTP

**2.3 复现过程**

基于Windows平台，使用`环境`目录下的`shiro-basic.zip`环境，解压后，用Idea打开shiro-basic文件夹，下载maven资源，运行ShiroBasicApplication类，即可启动环境。效果如图。
![](https://images.seebug.org/content/images/2020/10/8944d1c6-8ee7-4f24-8fb6-78e924c60a47.png-w331s)

**First Attack**  
构造HTTP请求，发送到服务器，完成身份验证绕过，效果如图
![](https://images.seebug.org/content/images/2020/10/a4f24518-ff6e-4f6e-aa44-8b387aed9455.png-w331s)
![](https://images.seebug.org/content/images/2020/10/840383e3-5258-498e-ac57-3fcf39c2814c.png-w331s)

**Second Attack**  
构造HTTP请求，发送到服务器，完成身份验证绕过，效果如图
![](https://images.seebug.org/content/images/2020/10/7f9400ea-b46d-4add-b830-7a15ad7e5ba6.png-w331s)
![](https://images.seebug.org/content/images/2020/10/b4bee920-cdd1-431d-85f6-bc960b64626e.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 漏洞利用过程**

**First Attack**  
获取到无权限访问的敏感路径，在authc认证路径后添加`%25%32%66`进行身份验证绕过。

**Second Attack**  
获取到无权限访问的敏感路径，在路径的头部添加`/;/`进行身份验证绕过。

**3.1.2 代码分析**

**First Attack**  
传入的payload首先被服务器接收，并传送给Shiro拦截器处理(org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter方法作为入口)。  
![](https://images.seebug.org/content/images/2020/10/f14a98d1-cee8-4441-8578-c7c11a982b58.png-w331s)

调用createSubject方法创建Subject，并调用execute方法进入Shiro FilterChain中。
![](https://images.seebug.org/content/images/2020/10/29873eb4-a37d-4158-bf65-7cd3fbb29931.png-w331s)
![](https://images.seebug.org/content/images/2020/10/008d3a4a-294f-4e9a-8360-fbb1bba3289c.png-w331s)

进入org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain方法中，首先获取请求uri路径。
![](https://images.seebug.org/content/images/2020/10/437c6cb0-8c1b-419b-9710-9feede30b381.png-w331s)
![](https://images.seebug.org/content/images/2020/10/b5d9d40a-7fc7-489b-9096-7864a28e9661.png-w331s)
在Shiro1.5.2版本中，对于requestURI处理的方式存在一些不同，此处也是漏洞触发点所在。Shiro1.5.2使用的是request.getContextPath()，request.getServletPath()，request.getPathInfo()拼接的方式。由于getServletPath()方法会对requestURI进行一次url解码，在之后的decodeAndCleanUriString方法中进行第二次url解码。
![](https://images.seebug.org/content/images/2020/10/cde1d78a-8780-4faf-ab75-35237b2c329e.png-w331s)

回到getChain方法中，迭代获取拦截器的表达式。
![](https://images.seebug.org/content/images/2020/10/7aa85bed-d63d-485c-b6b8-1a8c8ebc47d0.png-w331s)

这里重点关注`/hello/*`表达式。代码进入pathMatches方法，最终调用org.apache.shiro.util.AntPathMatcher#doMatch方法进行传入的requestURI与拦截器表达式进行匹配。
![](https://images.seebug.org/content/images/2020/10/acdb0af9-3830-4b41-81fd-9e3e49ce9e11.png-w331s)
匹配过程中，分别将拦截器表达式与requestURI以`/`作为分隔符进行字符串到数组的转换，通过循环匹配数组中对应的元素，判断requestURI是否符合拦截器表达式匹配形式。
![](https://images.seebug.org/content/images/2020/10/33c0c540-f554-4eac-9486-4d9c96297aa9.png-w331s)

如果表达式中存在通配符`*`，会将containsStar标志位赋值为true，进入 `else if (patIdxEnd ==
0)`判断条件，返回true。
![](https://images.seebug.org/content/images/2020/10/3a304de2-642b-474f-9030-e08716bf39a2.png-w331s)

最终回到doMatch方法中，通过判断表达式数组的元素个数与requestURI的元素个数，以及表达式中是否包含`**`，完成后续的匹配。
![](https://images.seebug.org/content/images/2020/10/4b26c791-898e-460c-9b72-b4838aa794fc.png-w331s)
跟进到Spring处理URI的代码，进入org.springframework.web.servlet.handler.AbstractHandlerMethodMapping#getHandlerInternal方法，获取requestURI。由于Spring获取requestURI时使用getRequestURI()方法，此方法不会进行URL解码。只会在decodeAndCleanUriString完成一次url解码。
![](https://images.seebug.org/content/images/2020/10/c29c5aea-1fe1-4a90-8031-596a1b69a87d.png-w331s)
进入lookupHandlerMethod方法，调用addMatchingMappings方法，获取Spring拦截器。
![](https://images.seebug.org/content/images/2020/10/506b7a66-603d-4934-b2e6-262a1ea91668.png-w331s)
![](https://images.seebug.org/content/images/2020/10/3f934b10-ba37-40cb-94b4-f85d1a9d2ba2.png-w331s)

进入org.springframework.web.servlet.mvc.condition.PatternsRequestCondition#getMatchingCondition方法调用doMatch方法进行requestURI和拦截器表达式的匹配。
![](https://images.seebug.org/content/images/2020/10/1c2b8521-4dc8-4bc8-b5cd-09f35a5a5554.png-w331s)
![](https://images.seebug.org/content/images/2020/10/19711086-a7a9-47f3-bfb8-eda46799e625.png-w331s)

Spring拦截器匹配流程和Shiro大致相同，同样是将字符串转换为数组进行匹配。
![](https://images.seebug.org/content/images/2020/10/faa06832-4c26-45d9-8f49-0080f8f83f15.png-w331s)

由于Spring只进行了一次URL解码，所以将未完全解码的部分作为一个整体，从而完成了拦截器表达式与requestURI的匹配。
![](https://images.seebug.org/content/images/2020/10/af9abb5f-a869-4062-be9c-f60702eb9fae.png-w331s)

**Second Attack**  

漏洞触发点同样是Shiro在修复CVE-2020-1957漏洞时，使用request.getContextPath()，request.getServletPath()，request.getPathInfo()拼接的方式，进行requestURI的获取。  
直接跟踪到`uri = valueOrEmpty(request.getContextPath()) + "/" +
valueOrEmpty(request.getServletPath()) + valueOrEmpty(request.getPathInfo());`
![](https://images.seebug.org/content/images/2020/10/bff9ad0d-4844-44f3-844c-4a036fda8686.png-w331s)

在调用getContextPath()方法获取context-path时，会调用removePathParameter方法清除掉分号以及分号到下一个/中间的数据。
![](https://images.seebug.org/content/images/2020/10/92248b04-71a5-4668-9541-78c95c099662.png-w331s)

接下来进入for循环中匹配candidate与conotext-path是否相同
![](https://images.seebug.org/content/images/2020/10/ea31b57a-b1a4-439c-a9fb-17e38dfd40e7.png-w331s)
如果不同，则从传入的URL中继续读取下一级目录，直到condidate与context-path相同，返回从URL截取的目录作为contextPath。由于context-path获取方式和removePathparameters方法对URL的处理，攻击者可以请求，让contextPath变量获取到带有分号的非预期值。

在进行requestURI拼接时，构造出根路径带有分号的requestURI。利用CVE-2020-1957漏洞原理，经过decodeAndCleanUriString方法时，截断reqeustURI中分号后的数据，并返回。从而绕过了shiro权限控制。

**3.1.3 漏洞触发过程**

**First Attack**
![](https://images.seebug.org/content/images/2020/10/790a62a2-3028-4d13-abf1-0196598a6917.png-w331s)

**Second Attack**
![](https://images.seebug.org/content/images/2020/10/c4978ab0-eeef-4ec9-9c59-23e30d57122e.png-w331s)

**3.2.4补丁分析**

对比Shiro 1.5.2与Shiro
1.5.3版本的改动，在org.apache.shiro.web.util.WebUtils类中添加了删除requestURI结尾的`/`的代码。
![](https://images.seebug.org/content/images/2020/10/2a1997ac-5a8c-40d4-8db2-cd97e8653df3.png-w331s)
![](https://images.seebug.org/content/images/2020/10/02690822-ba04-4f82-9a39-f263e63bd1d9.png-w331s)
![](https://images.seebug.org/content/images/2020/10/42a64364-f694-49d3-a337-c50786d83a13.png-w331s)

补丁主要优化了getPathWithinApplication方法，并单独定义了getServletPath方法，getPathInfo方法。补丁修复后，调用getPathWithinApplication方法获取requestURI只会在进行getServletPath方法中进行一次url解码，保持与Spring获取requestURI过程中相同的url解码次数。防御了双重url编码绕过。

获取requestURI直接调用getServletPath方法和getPathInfo方法进行拼接，由于不需要与contextpath拼接，从而防御了First
Attack攻击。

#### 4.2.3 Apache Shiro 身份验证绕过漏洞

**1.漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：Apache Shiro Authentication Bypass Vulnerability
  * 漏洞编号：CVE-2020-13933
  * 漏洞类型：身份验证绕过
  * CVSS评分：【CVSS v2.0：5.0】【CVSS v3.1：7.5】
  * 漏洞危害等级：高危

**1.2 漏洞概述**

Apache Shiro
1.6.0之前的版本，由于Shiro拦截器与requestURI的匹配流程与Web框架的拦截器的匹配流程有差异，攻击者构造一个特殊的http请求，可以绕过Shiro的认证，未授权访问敏感路径。

**1.3 漏洞利用条件**

  * 无

**1.4 漏洞影响**

影响版本：  
Apache Shiro < 1.6.0

**1.5 漏洞修复**

获取Apache Shiro最新版本，下载链接：<https://shiro.apache.org/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/10/468440ef-c753-4e68-a588-a7198d89d0e4.png-w331s)

**2.2 应用协议**

8080/HTTP

**2.3 复现过程**

基于Windows平台，使用`环境`目录下的`shiro-basic.zip`环境，解压后，用Idea打开shiro-basic文件夹，下载maven资源，运行ShiroBasicApplication类，即可启动环境。效果如图。
![](https://images.seebug.org/content/images/2020/10/c764302a-679c-4920-9bc2-1927a59ea759.png-w331s)
构造HTTP请求，发送到服务器，完成身份验证绕过，效果如图
![](https://images.seebug.org/content/images/2020/10/cc29620b-39f3-4d44-901b-938f81453a69.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 漏洞利用过程**

获取到无权限访问的敏感路径，在authc认证路径后添加%3b进行身份验证绕过。

**3.1.2 代码分析**

传入的payload首先被服务器接收，并传送给Shiro拦截器处理(org.apache.shiro.web.servlet.OncePerRequestFilter#doFilter方法作为入口)。  
![](https://images.seebug.org/content/images/2020/10/4350abd8-a9c1-40fc-9200-2517b4f2edfb.png-w331s)
![](https://images.seebug.org/content/images/2020/10/8e2e48ad-ae40-4c27-825a-a6e82c7e40fa.png-w331s)

调用createSubject方法创建Subject，并调用execute方法进入Shiro FilterChain中。
![](https://images.seebug.org/content/images/2020/10/85e18b9c-dbe2-4749-9c8e-653c5f0b7105.png-w331s)
![](https://images.seebug.org/content/images/2020/10/102bfa1f-96a9-459c-a111-29c2f002f3dd.png-w331s)

进入org.apache.shiro.web.filter.mgt.PathMatchingFilterChainResolver#getChain方法中，首先获取请求uri路径。
![](https://images.seebug.org/content/images/2020/10/a54df8b7-60fd-474a-877a-2a9bf0c0135c.png-w331s)

在Shiro1.5.3版本中，对于requestURI处理的方式存在一些不同，虽然Shiro官方在此处做了很多优化，但是依然存在与Spring处理方式不一致的请求，导致漏洞的产生。在Shiro1.5.3版本中，requestURI直接调用getServletPath方法和getPathInfo方法进行拼接。并清除解码后的requestURI中分号之后的数据。
![](https://images.seebug.org/content/images/2020/10/57ed615c-e19e-42d9-8ee3-38f47f794ded.png-w331s)

回到getChain方法中，迭代获取拦截器的表达式。
![](https://images.seebug.org/content/images/2020/10/e9090830-281a-48bf-bd4a-3601447c657a.png-w331s)
![](https://images.seebug.org/content/images/2020/10/dd178748-94c9-4165-9800-9d239596b7d5.png-w331s)

这里重点关注`/hello/*`表达式。代码进入pathMatches方法，最终调用org.apache.shiro.util.AntPathMatcher#doMatch方法进行传入的requestURI与拦截器表达式进行匹配。
![](https://images.seebug.org/content/images/2020/10/0f0b83cf-2c18-43aa-9558-a0c523f88dc8.png-w331s)

匹配过程中，分别将拦截器表达式与requestURI以`/`作为分隔符进行字符串到数组的转换，通过循环匹配数组中对应的元素，判断requestURI是否符合拦截器表达式匹配形式。
![](https://images.seebug.org/content/images/2020/10/9dc9096d-4843-4b79-9aff-0e79aea1d4a1.png-w331s)

由于解码后的requestURI被分号切割，导致pathDirs数组的元素个数少于pattDirs数组的元素个数。导致拦截器表达式与requestURI匹配失败，绕过认证
![](https://images.seebug.org/content/images/2020/10/b1d284bb-bdc5-4b9d-b109-5a712302055a.png-w331s)
![](https://images.seebug.org/content/images/2020/10/7563c864-65b9-4169-9478-f0be9dbe8ecc.png-w331s)

跟进到Spring处理URI的代码，进入org.springframework.web.servlet.handler.AbstractHandlerMethodMapping#getHandlerInternal方法，获取requestURI。由于Spring获取requestURI时使用getRequestURI()方法，此方法不会进行URL解码。
![](https://images.seebug.org/content/images/2020/10/433fdf1f-c4e5-4ab7-876d-a4c990a4d6ec.png-w331s)

进入decodeAndCleanUriString方法，对未进行url解码的requestURI调用removeSemicolonContent方法进行分号截断操作。由于此时的requestURI处于未解码状态，因此编码后的分号是无法被解析的。
![](https://images.seebug.org/content/images/2020/10/c50b385a-d9e9-42e2-a3fe-22dfb91c5b36.png-w331s)

进入lookupHandlerMethod方法，调用addMatchingMappings方法，获取Spring拦截器。
![](https://images.seebug.org/content/images/2020/10/1971d57c-264e-4e04-90ec-fc9000b52e52.png-w331s)
![](https://images.seebug.org/content/images/2020/10/1e3dbdb1-7155-4398-99ef-0b79c4205bf4.png-w331s)

进入org.springframework.web.servlet.mvc.condition.PatternsRequestCondition#getMatchingCondition方法调用doMatch方法进行requestURI和拦截器表达式的匹配。
![](https://images.seebug.org/content/images/2020/10/da62c653-9508-4348-bf89-79bd7ae10289.png-w331s)
![](https://images.seebug.org/content/images/2020/10/437ca461-2bb0-4cb4-9811-376fb807c533.png-w331s)

Spring拦截器匹配流程和Shiro大致相同，同样是将字符串转换为数组进行匹配。
![](https://images.seebug.org/content/images/2020/10/ac27049d-dab3-4eb9-9045-46b49eaef22f.png-w331s)

由于Spring对requestURI的先进行分号分割操作，再进行了一次URL解码。所以编码后分号之后的数据并不能被有效的分割，进行URL解码后，分号以及分号之后的数据成为了一个新的目录，从而完成了拦截器表达式与requestURI的匹配。
![](https://images.seebug.org/content/images/2020/10/67789a3c-473c-40f9-8861-e1f0a05e028a.png-w331s)

总结：Shiro对于requestURI的处理，先进行URL解码，再进行分号分割。Spring对于requestURI的处理，先进行分号分割，再进行URL解码。二者在解析requestURI时存在差异，因此导致漏洞出现。

**3.1.3 漏洞触发过程**

![](https://images.seebug.org/content/images/2020/10/6d346f26-ab44-401f-924a-f4ccfc332959.png-w331s)
**3.2.4补丁分析**

对比Shiro 1.5.3与Shiro 1.6.0版本的改动，在Shiro
1.6.0版本中新增org.apache.shiro.web.filter.InvalidRequestFilter类。
![](https://images.seebug.org/content/images/2020/10/c5294938-901c-4ca4-a0b1-a56d96f4844e.png-w331s)

在InvalidRequestFilter类中定义了SEMICOLON和BACKSLASH变量分别匹配路径中的`;`和`\`以及URL编码特征。调用isAccessAllowed方法，分别调用containsSemicolon，containsBackslash，containsNonAsciiCharacters方法进行`;`和`\`和不可见字符的检测。如果上述三个特征存在任意一个，则返回400状态。
![](https://images.seebug.org/content/images/2020/10/32fa873c-08b2-4ac4-bdb6-15882cad99f3.png-w331s)
![](https://images.seebug.org/content/images/2020/10/86da11e3-e149-491e-a58f-fea34d526741.png-w331s)

在org.apache.shiro.web.filter.mgt.DefaultFilter类中添加InvalidRequestFilter拦截器。在org.apache.shiro.web.config.IniFilterChainResolverFactory类中添加/**拦截器表达式，并为所有拦截器表达式赋予invalidRequest，目的是让所有传入的路径都可以经过InvalidRequestFilter检测。
![](https://images.seebug.org/content/images/2020/10/6aade67c-7fa1-41f5-a27a-296ce607c81c.png-w331s)
![](https://images.seebug.org/content/images/2020/10/27390bb7-e841-4e92-bd6e-5d6a5a4720a2.png-w331s)
![](https://images.seebug.org/content/images/2020/10/9ee4a5df-d700-4692-818e-54b0879f73f7.png-w331s)

## 参考链接

1.<https://www.infoq.com/articles/apache-shiro/>  
2.<https://zhuanlan.zhihu.com/p/54176956>  
3.<https://github.com/apache/shiro>  
4.<https://www.cnblogs.com/luop/p/4334160.html>  
5.[http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html<br](http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html<br) 6.<https://cloud.tencent.com/developer/article/1367702>  
7.<https://www.cnblogs.com/geektcp/p/10061908.html>  

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1378/>

