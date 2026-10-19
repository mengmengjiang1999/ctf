## 一、问题发现

**对于XXE问题，大家都不陌生。对于XXE的防御（修复），很多安全从业者也都知道，最安全的手段就是禁用DTD实体。文献【1】给出了各种语言下各类XML库的安全编码方式。在甲方环境下，笔者也曾参考此文档做了封装，供业务使用。读者可以思考这么做的好处与劣处（可以发散到其他场景）。**

笔者封装的编码（修复）方案一直工作良好，直到有一天，业务反馈代码抛出了Exception，并且不是因为安全Block导致的Exception。幸运的是，Exception在编码阶段就被发现了，没有将问题带到线上。

以下是抛出Exception的代码片段：

    
    
    public static void main(String[] args) throws IOException, TransformerException {
    
        TransformerFactory factory = TransformerFactory.newInstance();
        //禁用DTD（导致报错的代码）
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
        factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    
        //System.out.println(factory.getClass());
    
        InputStream is =  new FileInputStream("test/java/a.txt");
        StreamSource ss = new StreamSource(is);
        Transformer transformer = factory.newTransformer();
    
        transformer.transform(ss, new DOMResult());
        is.close();
    }

## 二、问题分析

### 2.1 问题复现

拿到给的代码片，运行了一下。发现并没有出现Exception，并且，上述代码片在写SDK就测试过，并没有异常抛出，也符合文献【1】给的修复建议。于是再次和RD确认，对factory的实例类打印处理，发现RD使用了xalan包，mvn坐标如下：

写SDK时的测试代码

    
    
    @RequestMapping("/xxe7")
    @ResponseBody
    public String testTransformerFactory(@RequestBody String xml) throws TransformerException {
        TransformerFactory tf = TransformerFactory.newInstance();
    
        XmlDtdSafeguard.disableDtd(tf); //禁用DTD
    
        StreamSource source = new StreamSource(new StringInputStream(xml));
        tf.newTransformer().transform(source, new DOMResult());
        return "testTransformerFactory";
    }
    
    
    
    <dependency>
        <groupId>xalan</groupId>
        <artifactId>xalan</artifactId>
        <!--最新的包-->
        <version>2.7.2</version>
    </dependency>
    

通过运行测试，发现：

当添加了上述jar包是，TransformerFactory的实现类是org.apache.xalan.processor.TransformerFactoryImpl，并且设置禁用DTD属性时报错。当不添加上述依赖，TransformerFactory的实现类是com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl，设置禁用DTD时不会报错。

### 2.2 JAVA SPI机制导致接口实现类被jar默认修改

从2.1的测试结果来看，添加一个jar包，就修改了接口的实现类。这必然需要JDK提供一定的扩展机制。处于自己太菜鸡，只是知道必然是有扩展机制，但是尚不知道是什么扩展机制导致。于是，两个方向来确定是什么扩展机制。

> 万能的搜索引擎：TransformerFactoryImpl，XXE，JDK，ServiceLoader mechanism（后来才知道）
>
> 观察jar包特征：jar包下/META-INF/services的正好定义了TransformerFactory接口文件

于是，发现TransformerFactory接口的实现类被修改是因为Java SPI的原因，参考【2】。我们也从源码层面看下：

![image.png](https://image.3001.net/images/20200527/1590587312_5ece6fb0aad67.png!small)  

可以看到，获取TransformerFactory接口实现类时：

首先从${java_home}/lib/jaxp.properties文件来确定实现类；

如果没有定义，则通过SPI机制来确定；

如果上述都没有，则使用硬编码的com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl作为实现类。

![image.png](https://image.3001.net/images/20200527/1590587361_5ece6fe1953b9.png!small)  

![image.png](https://image.3001.net/images/20200527/1590587386_5ece6ffabcad7.png!small)

在xalan包下确实定义了TransformerFactory实现类：![image.png](https://image.3001.net/images/20200527/1590587401_5ece7009defd5.png!small)

### 2.3 xalan TransformerFactoryImpl的报错原因及安全性

 **2.3.1 报错原因定位**

2.2就解释了为什么加了xalan包，TransformerFactory的就发生了改变。
这里还有个问题，为什么xalan的TransformerFactoryImpl类设置禁用DTD时会报错？

我们直接看xalan的TransformerFactoryImpl类的setFeature()和setAttribute()代码，可以看到这个类根本不支持XMLConstants.ACCESS_EXTERNAL_DTD
和XMLConstants.ACCESS_EXTERNAL_STYLESHEET属性，并抛出异常。
**![image.png](https://image.3001.net/images/20200527/1590587415_5ece70179052d.png!small)**

![image.png](https://image.3001.net/images/20200527/1590587430_5ece7026aed38.png!small)

看下JDK的实现类com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl，是支持这两个属性的，所以我们在测试时没有报错。

![image.png](https://image.3001.net/images/20200527/1590587454_5ece703e1b4dc.png!small)

综上，我们定位到了业务报错的原因。其实这个问题，老外还几年前就提出来了，但是Xalan官方并没有解决（xalan在2014年之后再没有发版），参考【3】【4】【5】【6】。

 **2.3.2 安全性分析**

既然，Xalan不支持设置上述属性，想必也是不安全的。我们猜测下证明我们的想法。注意，我们看到xalan支持另一个属性XMLConstants.FEATURE_SECURE_PROCESSING，我们将这个属性设置为true，进行测试，发现其
**不能有效阻止XXE漏洞** 。

    
    
    <!--测试payload-->
    <!DOCTYPE any [
    <!ELEMENT any ANY>
    <!ENTITY some SYSTEM "http://127.0.0.1:3344/nonexist">
    ]>
    <any>&ampsome</any>
    

## 三、问题解决  

看了下xalan的相关源码，发现没有好的方式可以禁用DTD（常规加固思路代价有点大）。其实，很多RD在使用xalan时，并不知道其使用了SPI机制。这也就说明，RD在做xml解析时，可能没有使用xalan对比jdk的额外属性（笔者在一天内解决此问题）。于是和RD确认了下，使用JDK自带的实现的能满足要求（一定要经过测试）。并且，TransformerFactoryImpl提供了不使用，使用指定实现类的方法，遂解决。

    
    
    TransformerFactory factory = TransformerFactory.newInstance(TransformerFactoryImpl.class.getName(),TransformerFactoryImpl.class.getClassLoader());
    factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    

* * *

****写在最后，以上仅是短期帮助业务快速定位和解决问题，此库是否有其他属性能够支持安全处理XML尚待研究。此外，此库设置不当还存在XSLT转换RCE漏洞，本文不多做介绍。笔者水平有限，欢迎指正。

 **参考文档**

>
> 【1】<https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#TransformerFactory>
>
> 【2】<https://juejin.im/post/5b9b1c115188255c5e66d18c>
>
> 【3】<https://github.com/find-sec-bugs/find-sec-bugs/issues/433>
>
> 【4】<https://access.redhat.com/solutions/1410603>
>
> 【5】<https://stackoverflow.com/questions/50000756/is-it-possible-to-avoid-> using-xalan-transformerfactory>
>
> 【6】<https://stackoverflow.com/questions/27128578/set-feature-> accessexternaldtd-in-transformerfactory/29021326#29021326>
>
> 【7】<http://xalan.apache.org/xalan-j/index.html>

 ***本文作者：Venscor，转载请注明来自FreeBuf.COM**  

