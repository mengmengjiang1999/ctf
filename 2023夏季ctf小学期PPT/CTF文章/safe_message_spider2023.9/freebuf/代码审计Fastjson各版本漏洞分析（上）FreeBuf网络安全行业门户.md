## ****前言****

最先出现问题的Fastjson 1.2.24反序列化漏洞已经分析过了，产生漏洞的原理也差不多理解了

  * 在2.25之后的版本，以及所有的.sec01后缀版本中，autotype功能默认是受限的（黑白名单机制）
  * 在2.68之后的版本，fastjson增加了safeMode的支持。配置safeMode后，无论白名单和黑名单，都不支持autoType

##  ** **概念****

可能出现一些新的概念，给一些参考链接吧

  * [FastJSON为什么要有autoType功能](https://github.com/alibaba/fastjson/issues/3218)
  * [enable_autotype](https://github.com/alibaba/fastjson/wiki/enable_autotype)
  * [fastjson_safemode](https://github.com/alibaba/fastjson/wiki/fastjson_safemode)

##  ** **演示代码****

后面的分析代码都以此为基础修改

 ** **package**** org.example;  
  
 ** **import**** com.alibaba.fastjson.JSON;  
  
 ** **public**** ** **class**** App {  
 ** **public**** static void main(String[] args) {  
String json =
"{\"@type\":\"org.example.User\",\"age\":66,\"username\":\"test\"}";  
System.out.println(JSON.parseObject(json));  
}  
  
}  
  
 ** **class**** User {  
 ** **private**** String username;  
 ** **private**** int age;  
  
 ** **public**** void setUsername(String username) {  
 ** **this****.username = username;  
System.out.println("call setUsername");  
}  
  
 ** **public**** String getUsername() {  
System.out.println("call getUsername");  
 ** **return**** username;  
}  
  
 ** **public**** void setAge(int age) {  
 ** **this****.age = age;  
System.out.println("call setAge");  
}  
  
 ** **public**** int getAge() {  
 ** **return**** age;  
}  
}

##  ** **fastjson 1.2.24****

之前已经分析过了，就不在写了

##  ** **fastjson 1.2.41****

利用的前提是必须要手动开启autoTypeSupport，不然还是不能利用，所以说还是有一点鸡肋吧

从代码中开启autoTypeSupport

ParserConfig.getGlobalInstance().setAutoTypeSupport( ** **true**** );

在1.2.25之后的版本，以及所有的.sec01后缀版本中，增加了checkAutotype函数，autotype功能默认是受限的（黑白名单机制）

但在1.2.25到1.2.41之间，发生过一次checkAutotype的绕过。

Payload如下

{"@type":"Lorg.example.User;","age":66,"username":"test"}

我们用这个payload来分析一下如何绕过的（fastjson 1.2.41）

进入checkAutoType后，首先会对typeName的长度进行判断，很明显这个条件满足不了，所以不会抛出异常

![1649821167_625645ef40fe29a25660a.png!small?1649821167631](https://image.3001.net/images/20220413/1649821167_625645ef40fe29a25660a.png!small?1649821167631)

继续向下，开启autoTypeSupport时，会先通过黑白名单来判断，先白名单后黑名单

![1649821177_625645f9773c56f1d99f9.png!small?1649821177964](https://image.3001.net/images/20220413/1649821177_625645f9773c56f1d99f9.png!small?1649821177964)

很明显我们传入的typeName Lorg.example.User;肯定是不在黑名单内的，这是一个绕过的点

![1649821188_62564604ef3abeaf3aa22.png!small?1649821189316](https://image.3001.net/images/20220413/1649821188_62564604ef3abeaf3aa22.png!small?1649821189316)

继续向下，如果clazz==null，就会调用TypeUtils.getClassFromMapping(typeName);，跟一下其实就是从一个ConcurrentHashMap中看看存不存在这个类，很明显我们传入的L开头的类是不会存在的

![1649821197_6256460de1dce59b0baba.png!small?1649821198296](https://image.3001.net/images/20220413/1649821197_6256460de1dce59b0baba.png!small?1649821198296)

继续向下，和上面类似，我们这个类还是找不到的，所以clazz还是null

![1649821205_62564615e1db473aeb04a.png!small?1649821207076](https://image.3001.net/images/20220413/1649821205_62564615e1db473aeb04a.png!small?1649821207076)

没开启autoTypeSupport的情况下，依然会进行黑白名单检测，先黑名单后白名单，我们这里手动开启了所以这里不管，因为会跳过

![1649821218_62564622388e263968d39.png!small?1649821218578](https://image.3001.net/images/20220413/1649821218_62564622388e263968d39.png!small?1649821218578)

前面黑名单检测都没问题，就会开始加载这个类了

![1649821227_6256462b761032e20c123.png!small?1649821227774](https://image.3001.net/images/20220413/1649821227_6256462b761032e20c123.png!small?1649821227774)

跟进loadClass，如果第一个字符是[，就会去掉[再去解析，我们这里不满足就先不看，继续向下

![1649821236_6256463429f821dafe438.png!small?1649821236502](https://image.3001.net/images/20220413/1649821236_6256463429f821dafe438.png!small?1649821236502)

这个条件就是这次绕过的核心条件了

 ** **else**** ** **if**** (className.startsWith("L") &&
className.endsWith(";")) {  
String newClassName = className.substring(1, className.length() - 1);  
 ** **return**** loadClass(newClassName, classLoader);  
}

如果开头是L而且结尾是;，那么就会给前后这俩字符去掉，所以可以看到我们的newClassName就是我们想要的org.example.User

![1649821247_6256463f1a84b4cdea6b7.png!small?1649821247471](https://image.3001.net/images/20220413/1649821247_6256463f1a84b4cdea6b7.png!small?1649821247471)

后续就会加载我们的类实例化，达到我们绕过的目的

![1649821261_6256464d67548219588b5.png!small?1649821261907](https://image.3001.net/images/20220413/1649821261_6256464d67548219588b5.png!small?1649821261907)

debug过程中，可能大家注意到一个点，loadClass函数中，有一个条件，如果第一个字符是[，就会去掉[再去实例化，那这个地方是不是也能用来绕过呢？

答案是当然可以，这个绕过点就体现在1.2.43版本中

##  ** **fastjson 1.2.42****

1.2.41问题出现后，1.2.42中尝试了修复，修复方式

  * <https://github.com/alibaba/fastjson/commit/e701faa2da7cff6d94394061bbff06a166c2aaaf>

寻找历史commit技巧：

release里面找对应的版本的commit

直接搜索commit

直接搜索issue

可以明显的看到，给原来的denyList变成了denyHashCodes，让安全研究更难了，但是hashcode的方法是公开的，只要jar包够多还是可以碰撞出来的，感觉治标不治本。。。

![1649821279_6256465f380e20daf766f.png!small?1649821280014](https://image.3001.net/images/20220413/1649821279_6256465f380e20daf766f.png!small?1649821280014)

同时可以看到针对漏洞绕过的修复方式，很简单粗暴，如果发现开头是L而且结尾是;，就直接去掉

![1649821289_62564669bae1df955c2eb.png!small?1649821290222](https://image.3001.net/images/20220413/1649821289_62564669bae1df955c2eb.png!small?1649821290222)

所以绕过方式也很简单，直接用2个L和2个;就可以了，Payload如下

{"@type":"LLorg.example.User;;","age":66,"username":"test"}

##  ** **fastjson 1.2.43****

对LL;;可以绕过的情况做了过滤，如果只有一个L;，就去除了后再走黑名单去过滤看看是否允许反序列化，着实太恶心了看着

![1649821320_62564688dd9a27c52fc7c.png!small?1649821321244](https://image.3001.net/images/20220413/1649821320_62564688dd9a27c52fc7c.png!small?1649821321244)

所以2个LL;;是行不通了，但是别忘了我们在分析1.2.41的时候，发现还会去掉[然后实例化，这就是绕过点

初始payload

{"@type":"[org.example.User","age":66,"username":"test"}

报错exepct '[', but ,, pos 29, json :
{"@type":"[org.example.User","age":66,"username":"test"}，29那个位置，期望一个[，但是是,，所以我们加一个[

{"@type":"[org.example.User"[,"age" ** **:**** 66,"username" ** **:**** "test"
** **}****

报错syntax error, expect {, actual string, pos 30, fastjson-version
1.2.43，期望30的位置是一个{，加上

最终POC

{"@type":"[org.example.User"[{,"age":66,"username":"test"}

  

看着有点迷，为啥加上[{就可以了？

分析一下，通过checkAutoType后，返回class [Lorg.example.User;

![1649821330_625646929fde1a83df630.png!small?1649821330967](https://image.3001.net/images/20220413/1649821330_625646929fde1a83df630.png!small?1649821330967)

一直跟，发现调用了deserializer.deserialze，跟进去，发现使用了clazz.getComponentType()，是不是很眼熟？就是前面去掉[的那个地方

![1649821335_62564697bb65f74c609c1.png!small?1649821336072](https://image.3001.net/images/20220413/1649821335_62564697bb65f74c609c1.png!small?1649821336072)

这个函数是native的，所以看不到代码。。。不过根据结果来看，就是去掉[L和;拿到类

![1649821348_625646a448192d61e2179.png!small?1649821348668](https://image.3001.net/images/20220413/1649821348_625646a448192d61e2179.png!small?1649821348668)

再继续往下，跟进parseArray

![1649821360_625646b0130f1e6a16d30.png!small?1649821360657](https://image.3001.net/images/20220413/1649821360_625646b0130f1e6a16d30.png!small?1649821360657)

发现如果token != 14就会抛出错误，而没有[的时候，token是16，所以会报错，{也类似，可以下个异常断点来分析

![1649821370_625646ba40dd6dd834a10.png!small?1649821370919](https://image.3001.net/images/20220413/1649821370_625646ba40dd6dd834a10.png!small?1649821370919)

最后看下到setXXX的运行堆栈信息，结合堆栈来分析可以节约很多时间

setUsername:20, User (org.example)  
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
invoke:62, NativeMethodAccessorImpl (sun.reflect)  
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
invoke:498, Method (java.lang.reflect)  
setValue:110, FieldDeserializer (com.alibaba.fastjson.parser.deserializer)  
parseField:118, DefaultFieldDeserializer
(com.alibaba.fastjson.parser.deserializer)  
parseField:1061, JavaBeanDeserializer
(com.alibaba.fastjson.parser.deserializer)  
deserialze:756, JavaBeanDeserializer
(com.alibaba.fastjson.parser.deserializer)  
deserialze:271, JavaBeanDeserializer
(com.alibaba.fastjson.parser.deserializer)  
deserialze:267, JavaBeanDeserializer
(com.alibaba.fastjson.parser.deserializer)  
parseArray:729, DefaultJSONParser (com.alibaba.fastjson.parser)  
deserialze:183, ObjectArrayCodec (com.alibaba.fastjson.serializer)  
parseObject:373, DefaultJSONParser (com.alibaba.fastjson.parser)  
parse:1338, DefaultJSONParser (com.alibaba.fastjson.parser)  
parse:1304, DefaultJSONParser (com.alibaba.fastjson.parser)  
parse:152, JSON (com.alibaba.fastjson)  
parse:162, JSON (com.alibaba.fastjson)  
parse:131, JSON (com.alibaba.fastjson)  
parseObject:223, JSON (com.alibaba.fastjson)  
main:10, App (org.example)

