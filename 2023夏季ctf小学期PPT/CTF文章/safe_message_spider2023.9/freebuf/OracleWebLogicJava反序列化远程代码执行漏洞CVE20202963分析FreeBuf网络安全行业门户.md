# **一、** ** **漏洞概要****

 ** **漏洞名称****

|

 ** **Oracle WebLogic 反序列化远程代码执行漏洞CVE-2020-2963****  
  
---|---  
  
 ** **威胁等级****

|

 ** **高危****  
  
 ** **影响范围****

|

 ** **Oracle WebLogic Server 10.3.6.0.0**** ** **  
**** ** **Oracle WebLogic Server 12.1.3.0.0**** ** **  
**** ** **Oracle WebLogic Server 12.2.1.3.0**** ** **  
**** ** **Oracle WebLogic Server 12.2.1.4.0****  
  
 ** **漏洞类型****

|

 ** **远程代码执行****  
  
 ** **利用难度****

|

 ** **中等****  
  
#  **二、** ** **漏洞分析****

###  ** **2.1 Weblogic组件介绍****

WebLogic是美国Oracle公司出品的一个Application
Server，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。

WebLogic将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中，是商业市场上主要的Java（J2EE）应用服务器软件（Application
Server）之一，是世界上第一个成功商业化的J2EE应用服务器，具有可扩展性，快速开发，灵活，可靠性等优势。

###  ** **2.2 漏洞描述****

2020年4月，Oracle官方发布了重要补丁更新，其中包括了漏洞CVE-2020-2963，漏洞等级定义为高危。
在SOAPInvokeState类中存在漏洞，未对序列化数据的安全性做检测，攻击者可以通过T3协议发送精心构造的序列化数据，从而达成远程代码执行的效果。

###  ** **2.3 漏洞分析****

首先通过补丁比较，发现漏洞点，在weblogic.wsee.async.SOAPInvokeState类中，使用了ObjectInputStream.readObject来反序列化对象，补丁是在反序列化方法执行之前，将原来的ObjectInputStream替换为FilteringObjectInputStream，而FilteringObjectInputStream方法的实现就是在resolveClass层添加了一层过滤，检查该类是否在黑名单之列。

![](https://image.3001.net/images/20201109/1604904639_5fa8e6bf64164e44ae935.png!small)

该漏洞点位于weblogic.wsee.async.SOAPInvokeState#readExternal方法，实现了Externalizable接口的类需要重写wirteExternal()方法和readExternal()方法，这样可以实现自定义方式的序列化和反序列化，而不受限于JVM。构造恶意的SOAPInvokeState对象，使其进入到readExternal方法，就可以执行攻击。

![](https://image.3001.net/images/20201109/1604905187_5fa8e8e3ec96d0616653c.png!small)

查看与readExternal对应的writeExternal方法，类似的使用了ObjectOutputStream.writeObject序列化了对象，但是首先需要使this.subject不为空，才能进入序列化的流程，而subject是SOAPInvokeState类的一个与认证有关的私有变量。

 ** **私有变量subject：****

![](https://image.3001.net/images/20201109/1604905754_5fa8eb1a4ab01a53e725a.png!small)

 ** **进入序列化流程的判断：****

![](https://image.3001.net/images/20201109/1604905766_5fa8eb2638c0797bfae5b.png!small)

SOAPInvokeState类有多个构造方法，由于在反序列化方法readExternal中，需要使用到私有变量msg，因此只有通过使用带形参的构造方法SOAPInvokeState(SOAPMessageContext
var1)构造的对象，才能成功被反序列化。

 ** **SOAPInvokeState类的构造方法：****

![](https://image.3001.net/images/20201109/1604905777_5fa8eb315f14a0ed95907.png!small)

 ** **反序列化中的msg：****

![](https://image.3001.net/images/20201109/1604905787_5fa8eb3bdf77715792f2c.png!small)

可以被序列化的对象，会进入readExternal方法，在反序列化过程中，发现还存在解密的过程，对应的writeExternal方法存在加密过程。

 ** **readExternal中的解密：****

![](https://image.3001.net/images/20201109/1604905803_5fa8eb4b525d9f0a25bfb.png!small)

 ** **writeExternal中的加密：****

![](https://image.3001.net/images/20201109/1604905814_5fa8eb56b64c6ae8d2a45.png!small)

跟进EncryptionUtil.encrypt

方法，在weblogic.security.internal.SerializedSystemIni#getExistingEncryptionService方法发现需要秘钥文件SerializedSystemIni.dat，因此需要将SerializedSystemIni.dat秘钥文件放在固定位置才能进行加密操作。

![](https://image.3001.net/images/20201109/1604905827_5fa8eb63249b2f85a0068.png!small)

攻击者通过writeExternal方法构造恶意SOAPInvokeState对象，并通过T3协议发送到存在漏洞的受害WebLogic服务器上，即可造成远程代码执行。

###  ** **2.4 漏洞复现****

搭建WebLogic环境，发送精心构造的序列化对象，在WebLogic服务器端成功执行了命令：

![](https://image.3001.net/images/20201109/1604905839_5fa8eb6fc7426f0e1afe1.png!small)

#  **三、** ** **影响范围****

目前受影响的WebLogic版本：

> Oracle WebLogic Server 10.3.6.0.0  
> Oracle WebLogic Server 12.1.3.0.0  
> Oracle WebLogic Server 12.2.1.3.0  
> Oracle WebLogic Server 12.2.1.4.0

#  **四、** ** **解决方案****

###  ** **修复建议****

目前厂商已发布升级补丁以修复漏洞，补丁获取链接：

<https://www.oracle.com/security-alerts/cpuapr2020.html>

#  **五、** ** **时间轴****

2020/04/16 Oracle 官方发布修复补丁。

2020/11/03 深信服千里目安全实验室发布漏洞通告。

#  **六、** ** **参考链接****

<https://www.oracle.com/security-alerts/cpuapr2020.html>

