***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、漏洞描述

 **2019年2月12日，Adobe官方发布了针对Adobe
ColdFusion的安全更新补丁，编号为APSB19-10。补丁中包含启明星辰ADLab发现并第一时间提交给官方的Critical（危急）反序列化漏洞，利用该漏洞攻击者可远程执行任意代码。**

漏洞编号为CVE-2019-7091，如下图所示：

![](https://image.3001.net/images/20190228/1551338047_5c778a3f886c6.png!small)

本次漏洞为AdobeColdFusion中FlashGateway服务中的漏洞。Adobe
ColdFusion的FlashGateway服务存在反序列化漏洞，未经身份验证的攻击者向目标AdobeColdFusion的FlashGateway服务发送精心构造的恶意数据，经反序列化后可远程执行任意代码。

## 二、漏洞时间轴

2018年9月21日：将漏洞详情提交给官方；

2018年12月05日：确认漏洞存在并开始修复；

2019年2月12日：官方发布正式补丁。

## 三、漏洞分析

Adobe
ColdFusion的FlashGateway服务允许flash连接到CFML和CFC模板。当攻击者通过HTTP协议向FlashGateway服务POST精心构造的ActionMessage信息后，FlashGateway服务依次通过各种类型的filter进行invoke()操作。在flashgateway.filter.SerializationFilter的invoke方法中，实例化MessageDeserializer类型的反序列工具deserializer并通过deserializer.readMessage(m)方法对精心构造的ActionMessage消息进行反序列化，同时将ActionMessage中的targetURI、data等值赋值给MessageBody。

完成序列化过程后，此时ActionContextcontext中的内容即为输入流中精心构造的ActionMessage信息。在flashgateway.filter.AdapterFilter的invoke方法中，读取ActionContext中的MessageBody信息赋值给serviceName、functionName、parameters等，通过adapter=locateAdapter(context,serviceName,
functionName, parameters,
serviceType)方法得到flashgateway.adapter.java.JavaBeanAdapter类型的adapter，然后执行JavaBeanAdapter的invokeFunction方法。关键代码如下：

    
    
    public ActionContext invoke(ActionContext context) throws  Throwable {
            ...
          //读取MessageBody信息
          MessageBody  requestMessageBody = context.getRequestMessageBody();
          String serviceName  = requestMessageBody.serviceName;
          String  functionName = requestMessageBody.functionName;
          List parameters = requestMessageBody.parameters;
            ...
         if  (context.isDescribeRequest()) {
          result = adapter.describeService(context,  serviceName);
         } else {
      //adapter为JavaBeanAdapter，执行flashgateway.adapter.java.JavaBeanAdapter的invokeFunction方法
        result =  adapter.invokeFunction(context, serviceName, functionName, parameters); }

在JavaBeanAdapter的invokeFunction方法中，看到关键代码：method.invoke(service,parameters.toArray())。

![](https://image.3001.net/images/20190228/1551338081_5c778a61a94f7.png!small)

其中，目标执行方法method通过Method method =this.getMethod(parameters, serviceName,
functionName, aClass)得到；

方法执行对象service 通过service = aClass.newInstance()得到；

方法执行参数parameters.toArray()通过MessageBody得到。

由此可见，method.invoke(service,parameters.toArray())的所用参数都可控，意味着可执行任意方法。

整个流程如下图所示：

![](https://image.3001.net/images/20190228/1551338115_5c778a8383fd4.png!small)

## 四、漏洞利用效果

![](https://image.3001.net/images/20190228/1551338155_5c778aab259f8.png!small)

## 五、影响版本

ColdFusion 11 Update 15及之前版本

ColdFusion 2016 Update 7及之前版本

ColdFusion 2018 Update 1及之前版本。

## 六、规避方案

> 1、修改gateway-config.xml文件的配置，禁止JavaBeanAdapter的使用。

>
> 2、升级最新补丁APSB19-10：<https://helpx.adobe.com/security/products/coldfusion/apsb19-10.html>。

 ***本文作者：ADLab，转载请注明来自FreeBuf.COM**

