***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**近日，国家信息安全漏洞库（CNNVD）收到关于微信支付SDK XXE（XML External
Entity）漏洞（CNNVD-201807-083）情况的报送。成功利用该漏洞的攻击者可以远程读取服务器文件，获取商户服务器上的隐私数据，甚至可以支付任意金额购买商品。使用有漏洞的Java版本微信支付SDK进行支付交易的商家网站可能受此漏洞影响。目前，微信官方已经发布补丁修复该漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。**

##  **一、漏洞介绍**

微信支付官方SDK是微信支付官方的软件工具开发包，在使用微信支付时，商家需要向微信提供一个URL用来接收异步支付结果的通知，该接口接受XML格式的数据。XML语言标准支持了与外部进行实体数据交换的特性，如果程序在解析XML时没有限制或关闭该特性，同时外部又可以传入有恶意代码的XML数据就会触发漏洞。微信支付官方提供的SDK由于编码遗漏，未关闭该XML特性。商家在其系统中如果使用该版本SDK，系统便会受漏洞影响。

微信在支付过程中，其Java版本的SDK没有关闭该XML特性，导致攻击者在获取了接收通知的URL地址的前提下，可以通过构造恶意的XML数据包发送到该URL来窃取商家网站服务器上的隐私数据。

##  **二、危害影响**

成功利用该漏洞的攻击者可以远程读取服务器文件，获取商户服务器上的隐私数据，甚至可以支付任意金额购买商品。使用有漏洞的Java版本微信支付SDK进行支付交易的商家网站可能受此漏洞影响。

##  **三、修复建议**

目前，微信官方已经发布补丁修复该漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施，具体措施如下：

1.如果后台系统使用了官方SDK，请更新SDK到最新版本，链接如下:

> <https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=11_1>

2.如果有系统提供商，请联系提供商进行核查和升级修复；

3.如果是自研系统，请联系技术部门按以下指引核查和修复：

XXE漏洞需要在代码中进行相应的设置，不同语言设置的内容不同，下面提供了几种主流开发语言的设置指引：

【PHP】

    
    
    libxml_disable_entity_loader(true);

【JAVA】不同java组件修复方案不一样，请参考OWASP修复建议：

>
> <https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Prevention_Cheat_Sheet#Java>

【.Net】

    
    
    XmlResolver = null

【Python】

    
    
    from lxml import etree
    xmlData = etree.parse(xmlSource,etree.XMLParser(resolve_entities=False))

【c/c++(常用库为libxml2 libxerces-c)】

【libxml2】: 确保关闭配置选项：XML_PARSE_NOENT 和 XML_PARSE_DTDLOAD

2.9版本以上已修复xxe

【libxerces-c】：如果用的是XercesDOMParser:

    
    
    XercesDOMParser *parser = new XercesDOMParser;
    parser->setCreateEntityReferenceNodes(false);

如果是用SAXParser:

    
    
    SAXParser* parser = new SAXParser;
    parser->setDisableDefaultEntityResolution(true);

如果是用SAX2XMLReader:

    
    
    SAX2XMLReader* reader = XMLReaderFactory::createXMLReader();
    parser->setFeature(XMLUni::fgXercesDisableDefaultEntityResolution, true);

此外，针对使用XML进行数据交换的网络系统（如：第三方支付平台等），建议相关系统厂商对解析处理XML数据的功能代码进行安全检查，可参考上述方法修复漏洞，及时消除漏洞风险。

本通报由CNNVD技术支撑单位——深圳市腾讯计算机系统有限公司、北京长亭科技有限公司、北京华顺信安科技有限公司提供支持。

CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系，联系方式:cnnvd@itsec.gov.cn。

 ***本文作者：CNNVD，转载请注明来自FreeBuf.COM**

