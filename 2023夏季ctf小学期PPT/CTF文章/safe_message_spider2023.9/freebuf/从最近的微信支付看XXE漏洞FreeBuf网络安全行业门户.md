***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文作者：路上路人路过，属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

**先说下写这篇文章的初衷吧，最近微信支付java_sdk刚爆发了一次xxe漏洞，然后领导赶快用自家的静态代码审计工具做了审计（这里我就不报名字，本来可以帮公司推广下产品是很好的，但我怕本文过于基础会被各位大佬喷出翔来，到时候有辱“司”门就真是罪过罪过了）。**

发现能成功找出漏洞点，如下图。

![图片.png](https://image.3001.net/images/20180706/15308633532911.png!small)

到目前本来是件极好的事情，但是发现使用自己规则修复后依然能扫描出漏洞，这就很能说明问题，于是老大让我对微信支付漏洞做漏洞研究并找出产品出问题的原因。所以才有了这篇文章。由于本文的初衷是为了改进产品，所以本文并不是为了深入研究xxe漏洞，更加适合开发人员看。  

微信支付的sdk中提供了WXPayUtil这个工具类，该类中实现了xmltoMap和maptoXml这两个方法，而这次的微信支付的xxe漏洞爆发点就在xmltoMap方法中。

![图片.png](https://image.3001.net/images/20180706/15308626929190.png!small)  
![图片.png](https://image.3001.net/images/20180706/15308626999330.png!small)

该方法是为了将xml格式的字符串strXML转化为map。由于strXML可由攻击者控制，且程序未作任何防护措施（如禁止引用外部实体；过滤关键字符串等），导致恶意攻击者可利用外部实体注入读取服务器上的文件。当攻击者获取支付加密所用的安全密匙后，完全可以实现0元支付商品。

这里先以微信sdk中的xmlToMap方法为例，复现该xxe漏洞。（由于要完整的实现微信零元支付，需要写比较完整的程序对接微信支付接口，比较耗时间，暂时先不做）。

出现问题的代码是：

    
    
    DocumentBuilderFactory documentBuilderFactory = DocumentBuilderFactory.newInstance();
    
    org.w3c.dom.Document doc = documentBuilder.parse(stream);

生成documentBuilderFactory后直接去解析流。

构造xml格式的字符串如下:

    
    
    <?xml version='1.0' encoding='utf-8'?>
    
    <!DOCTYPE xdsec [
    
    <!ELEMENT methodname ANY>
    
    <!ENTITY xxe SYSTEM 'file:///c:/windows/win.ini'>]>
    
    <methodcall>
    
    <methodname>&ampxxe</methodname>
    
    </methodcall>

这样mapToXml中DOM解析器解析该字符串时，会访问外部实体中的SYSTEM属性中标识的URL，并将读取的文件内容放入methodccall节点中。然后取出放入map中（实际场景中map中的值最后会被攻击者所获取，我们这里以在控制台输出为例），能成功读取系统文件。

![图片.png](https://image.3001.net/images/20180706/15308627289061.png!small)

### 一、完全禁用DTDs，生成documentBuilderFactory后对feature进行设置

documentBuilderFactory.setFeature("<http://apache.org/xml/features/disallow-doctype-decl>",true);

效果如下：

![图片.png](https://image.3001.net/images/20180706/15308627401011.png!small)  

程序会报错，提示将该属性设为true。

### 二、生成documentBuilderFactory后对feature进行设置

    
    
    documentBuilderFactory.setXIncludeAware(false);          documentBuilderFactory.setExpandEntityReferences(false);                                        documentBuilderFactory.setFeature("<http://xml.org/sax/features/external-parameter-entities>",false);                                 documentBuilderFactory.setFeature("<http://xml.org/sax/features/external-general-entities>", false);

效果如下：

![图片.png](https://image.3001.net/images/20180706/15308627503619.png!small)

程序虽然不会报错，但是已经读取不出系统文件中的内容了。

### 三、对关键词做过滤，如ENTITY、 DOCTYPE

对以上三种防范方式做分析：推荐使用第一种，能处理掉绝大多数的xxe漏洞；当有需求不能全部禁用掉DTD时，使用第二种方法；不建议使用第三种方法，如果不然很容易被绕过，如使用ENTIENTITYTY等等情况来绕过。

微信支付sdk中使用的是原生的dom解析xml，接下里分别复现使用原生SAX解析xml、使用dom4j解析xml、使用jdom解析xml这三种实现方式的xxe漏洞以及修复方法（修复原理是一样的，方法都类似的，但为了方便之后产品规则的完善，这里全部列举出来）

使用原生SAX解析xml

![图片.png](https://image.3001.net/images/20180706/15308627634232.png!small)

问题在于生成SAXParserFactory后直接去解析xml了，修复方法添加属性

sf.setFeature("<http://apache.org/xml/features/disallow-doctype-decl>",true);

效果如下：

![图片.png](https://image.3001.net/images/20180706/15308627734795.png!small)

使用dom4j解析xml：

    
    
    SAXReader reader  = new SAXReader();
    
    InputStream stream = new ByteArrayInputStream(strXML.getBytes("UTF-8"));
    
    Document doc = reader.read(stream);

![图片.png](https://image.3001.net/images/20180706/15308628083349.png!small)

修复方法：

reader.setFeature("<http://apache.org/xml/features/disallow-doctype-decl>",true);

效果如下：

![图片.png](https://image.3001.net/images/20180706/1530862814472.png!small)

使用Jdom解析xml

    
    
    SAXBuilder  builder = new SAXBuilder();
    
    Document doc = builder.build(stream);

![图片.png](https://image.3001.net/images/20180706/15308628297286.png!small)

修复方法如下：

    
    
    builder.setFeature("<http://apache.org/xml/features/disallow-doctype-decl>",true);

效果如下：

![图片.png](https://image.3001.net/images/20180706/1530862835762.png!small)

最后是对SkyJava审计WxPayAPI结果的分析：

SkyJava是报了两个xxe漏洞，分别是WXpayUtil.java中的mapToXml和xmlToMap这两个方法。其中这次的微信支付xxe漏洞爆发点是在xmlToMap，所以两个中一个是正确的一个是误报。先分析误报：

![图片.png](https://image.3001.net/images/20180706/15308628487326.png!small)

该方法是实现将map中的键值对取出后生成xml的节点，并将其放在根节点<xml></xml>中，像这种情况，就算map是受攻击者控制的，生成xml的时候也不会构造出外部实体的引入。其实xxe漏洞都是解析的时候出现问题，单单只是生成有问题的xml，并不能确定是否存在xxe漏洞，关键还是得看程序去解析它的时候是否有安全措施（如上面所说的添加禁止外部实体引入的属性等）。

对于该种误报我的建议是：不能仅仅因为没有设置安全属性就判断存在漏洞，尽量是先判断存在解析xml的情况下再根据

> 1\. 是否有设置安全属性
>
> 2\. Source是否安全

来判断是否存在漏洞。（感觉不是很好实现，以上两段话主观性比较强，仅做参考.....）

再说下SkyJava报的另外一个点，爆发点确定的是正确的。

![图片.png](https://image.3001.net/images/20180706/15308628597964.png!small)

但头说修复之后还是会报xxe漏洞，所以我看了下修复之后的方法。

![图片.png](https://image.3001.net/images/20180706/1530862868351.png!small)

修复的方法中将<http://javax.xml.XMLConstants/feature/secure-processing>属性设为true。在本地测试效果如下，发现并不能防御xxe漏洞，所以不建议使用该方法。

![图片.png](https://image.3001.net/images/20180706/15308628773441.png!small)

再看官方微信支付sdk修复这个xxe漏洞之后的方法是怎么样的

![图片.png](https://image.3001.net/images/20180706/1530862886817.png!small)

是使用了一个专门的xml工具类来生成DocumentBuilder

![图片.png](https://image.3001.net/images/20180706/15308628926712.png!small)

该类中设置了一些安全属性，应该是微信支付为了保险起见吧，同时采用我上面所说的修复方法一和二（毕竟没有绝对的安全）。但在SkyJava的规则上，我认为审计的时候只要采举了其中的一种就可以认为不存在xxe漏洞，如果规则上认为两种措施都用才算不存在漏洞的话可能会导致误报率较高（毕竟很多程序都只采用第一种方法防范xxe）。

最后，我还是想说我第一次在FreeBuf上发表文章，望各位大佬站在培养新人的点上，轻喷轻喷！  

 ***本文作者：路上路人路过，属于FreeBuf原创奖励计划，未经许可禁止转载**

